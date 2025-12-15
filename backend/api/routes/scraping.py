"""
Routers de API para control de scraping.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field

from api.deps import get_database
from services.scraper import NewsScraper
from services.scheduler import scraping_scheduler
from services.singular_client import SingularLiveClient
from services.ticker_rotation import ticker_rotation_service
from services.ticker_state_tracker import ticker_state_tracker
from db.models import Headline, NewsSource
from db.redis_client import redis_client
from core.logging import logger


router = APIRouter(prefix="/scraping", tags=["scraping"])


class TickerControlRequest(BaseModel):
    """Schema para controlar el ticker."""
    state: str  # "In" o "Out"
    category: str = "mundo"
    max_headlines: int = 10
    separator_url: str = "https://assets.singular.live/7072b13f9e20b98034f48d6202400ff9/svgs/7esb5NbN8cQxcCk7X0szej_w24h24.svg"
    show_source_name: bool = True  # Si False, envía Custom Credit vacío
    auto_scrape: bool = False  # Si True, hace scraping antes de mostrar
    scraping_interval: int = 10  # Intervalo de scraping automático en minutos (modo manual)


@router.post("/start")
async def start_manual_scraping(
    send_to_ticker: bool = False,
    ticker_category: str = "mundo",
    db: AsyncSession = Depends(get_database)
):
    """
    Inicia scraping manual de todas las fuentes activas.
    
    Args:
        send_to_ticker: Si True, envía titulares al ticker de Singular.live
        ticker_category: Categoría para mostrar en el ticker
        db: Sesión de base de datos
    
    Returns:
        dict: Estadísticas del scraping
    """
    logger.info(f"Iniciando scraping manual (send_to_ticker={send_to_ticker})")
    
    async with NewsScraper(db, redis_client) as scraper:
        stats = await scraper.scrape_all(active_only=True)
    
    # Si se solicita, enviar titulares al ticker
    if send_to_ticker and stats.get("headlines_new", 0) > 0:
        try:
            # Obtener últimos titulares de la categoría
            result = await db.execute(
                select(Headline)
                .where(Headline.category == ticker_category)
                .order_by(Headline.created_at.desc())
                .limit(10)
            )
            headlines = result.scalars().all()
            
            if headlines:
                async with SingularLiveClient() as client:
                    headline_texts = [h.title for h in headlines]
                    await client.show_ticker(
                        headlines=headline_texts,
                        category=ticker_category
                    )
                    logger.info(f"✓ Titulares enviados al ticker ({len(headlines)} items)")
                    stats["ticker_updated"] = True
            else:
                stats["ticker_updated"] = False
                logger.warning("No hay titulares de la categoría para enviar al ticker")
        except Exception as e:
            logger.error(f"Error enviando titulares al ticker: {e}")
            stats["ticker_error"] = str(e)
    
    return {
        "status": "completed",
        "stats": stats
    }


@router.post("/ticker/control")
async def control_ticker(
    request: TickerControlRequest,
    db: AsyncSession = Depends(get_database)
):
    """
    Controla la visibilidad y contenido del ticker de Singular.live.
    
    Args:
        request: Configuración del ticker (state: In/Out, category, max_headlines)
        db: Sesión de base de datos
    
    Returns:
        dict: Estado actualflé después del cambio
    """
    logger.info(f"Controlando ticker: state={request.state}, category={request.category}")
    
    try:
        async with SingularLiveClient() as client:
            if request.state == "Out":
                # Ocultar ticker
                await client.hide_ticker()
                logger.info("✓ Ticker ocultado")
                
                # MODO MANUAL: Pausar scheduler de scraping
                logger.info("Pausando scheduler de scraping (modo manual)")
                scraping_scheduler.pause()
                
                # Actualizar tracker
                ticker_state_tracker.set_state("Out")
                
                return {
                    "status": "success",
                    "ticker_state": "Out",
                    "message": "Ticker ocultado y scraping automático pausado"
                }
            else:
                # Auto-scraping si está activado
                if request.auto_scrape:
                    logger.info(f"🔄 Ejecutando scraping automático para categoría '{request.category}'...")
                    
                    # Obtener fuentes activas de esta categoría
                    sources_result = await db.execute(
                        select(NewsSource)
                        .where(NewsSource.category == request.category)
                        .where(NewsSource.is_active == True)
                    )
                    sources = sources_result.scalars().all()
                    
                    if sources:
                        # Scrapear cada fuente
                        async with NewsScraper(db, redis_client) as scraper:
                            for source in sources:
                                try:
                                    await scraper.scrape_source(source.id)
                                    logger.info(f"  ✓ Scrapeado: {source.name}")
                                except Exception as e:
                                    logger.warning(f"  ⚠️ Error scrapeando {source.name}: {e}")
                        logger.info(f"✓ Auto-scraping completado para {len(sources)} fuentes")
                    else:
                        logger.warning(f"No hay fuentes activas para categoría '{request.category}'")
                
                # Mostrar ticker con titulares de la categoría
                # JOIN con NewsSource para obtener el nombre de la fuente
                result = await db.execute(
                    select(Headline, NewsSource.name)
                    .join(NewsSource, Headline.source_id == NewsSource.id)
                    .where(Headline.category == request.category)
                    .order_by(Headline.created_at.desc())
                    .limit(request.max_headlines)
                )
                rows = result.all()
                
                if not rows:
                    return {
                        "status": "warning",
                        "ticker_state": "Out",
                        "message": f"No hay titulares de categoría '{request.category}'"
                    }
                
                # Extraer titulares y nombre de la fuente más común
                headlines = [row[0] for row in rows]
                source_names = [row[1] for row in rows]
                
                # Usar la fuente más común o la primera
                from collections import Counter
                most_common_source = Counter(source_names).most_common(1)[0][0] if source_names else ""
                
                # Si show_source_name es False, enviar string vacío
                source_to_send = most_common_source if request.show_source_name else ""
                
                headline_texts = [h.title for h in headlines]
                success = await client.show_ticker(
                    headlines=headline_texts,
                    category=request.category,
                    source_name=source_to_send,
                    separator_url=request.separator_url
                )
                
                
                # Marcar titulares como enviados si fue exitoso
                if success:
                    from datetime import datetime
                    for headline in headlines:
                        headline.sent_to_singular = True
                        headline.sent_at = datetime.utcnow()
                    await db.commit()
                    logger.info(f"✓ {len(headlines)} titulares marcados como enviados")
                
                logger.info(f"✓ Ticker mostrado con {len(headlines)} titulares" + 
                           (f" de fuente: {most_common_source}" if request.show_source_name else " (sin nombre de fuente)"))
                
                # MODO MANUAL: Iniciar/reanudar scheduler de scraping en background
                logger.info(f"Iniciando scheduler de scraping (intervalo: {request.scraping_interval}min)")
                
                # Si el scheduler está pausado, reanudarlo primero
                if scraping_scheduler.is_running:
                    logger.info("Scheduler ya corriendo, reanudando...")
                    scraping_scheduler.resume()
                
                # Luego iniciar/actualizar con nuevo intervalo
                scraping_scheduler.start(interval_minutes=request.scraping_interval)
                
                # Actualizar tracker
                ticker_state_tracker.set_state("In", request.category)
                
                return {
                    "status": "success",
                    "ticker_state": "In",
                    "category": request.category,
                    "source_name": most_common_source if request.show_source_name else None,
                    "headlines_count": len(headlines),
                    "message": f"Ticker mostrado con {len(headlines)} titulares" + 
                              (f" de {most_common_source}" if request.show_source_name else "")
                }
                
    except Exception as e:
        logger.error(f"Error controlando ticker: {e}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }


class SeparatorUpdateRequest(BaseModel):
    """Schema para actualizar solo el separador del ticker."""
    separator_url: str = Field(..., description="URL del icono separador")


@router.patch("/ticker/separator")
async def update_ticker_separator(
    request: SeparatorUpdateRequest,
    db: AsyncSession = Depends(get_database)
):
    """
    Actualiza SOLO el separador del ticker visible, sin afectar contenido ni estado.
    Endpoint completamente independiente de los modos manual/automático.
    
    Args:
        request: URL del nuevo separador
        db: Sesión de base de datos
    
    Returns:
        dict: Estado de la actualización
    """
    logger.info(f"Actualizando separador del ticker: {request.separator_url}")
    
    try:
        # Obtener estado actual del ticker
        current_state = ticker_state_tracker.get_state()
        
        if current_state.get("state") != "In":
            return {
                "status": "warning",
                "message": "El ticker está oculto, el separador se aplicará cuando se muestre",
                "separator_url": request.separator_url
            }
        
        # Obtener última categoría y headlines actuales para re-enviar con nuevo separador
        current_category = current_state.get("category", "mundo")
        
        result = await db.execute(
            select(Headline, NewsSource.name)
            .join(NewsSource, Headline.source_id == NewsSource.id)
            .where(Headline.category == current_category)
            .where(Headline.sent_to_singular == True)  # Solo los que ya están en el ticker
            .order_by(Headline.sent_at.desc())
            .limit(10)
        )
        rows = result.all()
        
        if not rows:
            return {
                "status": "warning",
                "message": "No hay contenido en el ticker para actualizar",
                "separator_url": request.separator_url
            }
        
        headlines = [row[0] for row in rows]
        source_names = [row[1] for row in rows]
        
        # Fuente más común
        from collections import Counter
        most_common_source = Counter(source_names).most_common(1)[0][0] if source_names else ""
        
        headline_texts = [h.title for h in headlines]
        
        # Re-enviar ticker con mismo contenido pero nuevo separador
        async with SingularLiveClient() as client:
            success = await client.show_ticker(
                headlines=headline_texts,
                category=current_category,
                source_name=most_common_source,
                separator_url=request.separator_url
            )
            
            if success:
                logger.info(f"✓ Separador actualizado en ticker visible")
                return {
                    "status": "success",
                    "message": "Separador actualizado correctamente",
                    "separator_url": request.separator_url,
                    "headlines_count": len(headlines)
                }
            else:
                return {
                    "status": "error",
                    "message": "Error actualizando separador en Singular.live"
                }
                
    except Exception as e:
        logger.error(f"Error actualizando separador: {e}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }


@router.get("/status")
async def get_scraping_status():
    """
    Obtiene el estado del scheduler de scraping.
    
    Returns:
        dict: Estado actual del scheduler
    """
    return scraping_scheduler.get_status()


@router.post("/scheduler/start")
async def start_scheduler(interval_minutes: int = None):
    """
    Inicia el scheduler de scraping automático.
    
    Args:
        interval_minutes: Intervalo en minutos (opcional)
    
    Returns:
        dict: Confirmación
    """
    scraping_scheduler.start(interval_minutes=interval_minutes)
    
    return {
        "status": "started",
        "scheduler": scraping_scheduler.get_status()
    }


@router.post("/scheduler/stop")
async def stop_scheduler():
    """
    Detiene el scheduler de scraping.
    
    Returns:
        dict: Confirmación
    """
    scraping_scheduler.stop()
    
    return {"status": "stopped"}


@router.post("/scheduler/pause")
async def pause_scheduler():
    """
    Pausa el scheduler de scraping.
    
    Returns:
        dict: Confirmación
    """
    scraping_scheduler.pause()
    
    return {"status": "paused"}


@router.post("/scheduler/resume")
async def resume_scheduler():
    """
    Reanuda el scheduler de scraping.
    
    Returns:
        dict: Confirmación
    """
    scraping_scheduler.resume()
    
    return {"status": "resumed"}


@router.put("/scheduler/interval")
async def update_scheduler_interval(interval_minutes: int):
    """
    Actualiza el intervalo de scraping del scheduler.
    
    Args:
        interval_minutes: Nuevo intervalo en minutos (mínimo 1)
    
    Returns:
        dict: Confirmación con nuevo intervalo
    """
    try:
        if interval_minutes < 1:
            return {
                "status": "error",
                "message": "El intervalo debe ser al menos 1 minuto"
            }
        
        await scraping_scheduler.update_interval(interval_minutes)
        
        return {
            "status": "success",
            "message": f"Intervalo actualizado a {interval_minutes} minutos",
            "interval_minutes": interval_minutes
        }
    except Exception as e:
        logger.error(f"Error actualizando intervalo: {e}")
        return {
            "status": "error",
            "message": str(e)
        }



# ==================== ENDPOINTS DE ROTACIÓN AUTOMÁTICA ====================

class TickerRotationStart(BaseModel):
    """Schema para iniciar rotación automática."""
    interval_seconds: int = 60
    separator_url: str = "https://assets.singular.live/7072b13f9e20b98034f48d6202400ff9/svgs/7esb5NbN8cQxcCk7X0szej_w24h24.svg"
    show_source_name: bool = True


@router.post("/ticker/rotation/start")
async def start_ticker_rotation(request: TickerRotationStart):
    """
    Inicia rotación automática de categorías del ticker.
    
    Args:
        request: Configuración de rotación (intervalo, separator, etc.)
    
    Returns:
        dict: Estado de rotación iniciada
    """
    try:
        await ticker_rotation_service.start_rotation(
            interval_seconds=request.interval_seconds,
            separator_url=request.separator_url,
            show_source_name=request.show_source_name
        )
        
        return {
            "status": "success",
            "message": f"Rotación automática iniciada (intervalo: {request.interval_seconds}s)",
            "rotation_status": ticker_rotation_service.get_status()
        }
    except Exception as e:
        logger.error(f"Error iniciando rotación: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


@router.post("/ticker/rotation/stop")
async def stop_ticker_rotation():
    """
    Detiene la rotación automática del ticker.
    
    Returns:
        dict: Confirmación de detención
    """
    try:
        await ticker_rotation_service.stop_rotation()
        
        return {
            "status": "success",
            "message": "Rotación automática detenida",
            "rotation_status": ticker_rotation_service.get_status()
        }
    except Exception as e:
        logger.error(f"Error deteniendo rotación: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


@router.get("/ticker/rotation/status")
async def get_ticker_rotation_status():
    """
    Obtiene el estado actual de la rotación automática.
    
    Returns:
        dict: Estado de rotación (activa/inactiva, intervalo, categoría actual)
    """
    return {
        "status": "success",
        "rotation_status": ticker_rotation_service.get_status()
    }


# ==========================================
# ENDPOINTS DE MODO AUTOMÁTICO
# ==========================================

class AutoModeStartRequest(BaseModel):
    """Schema para iniciar modo automático."""
    rotation_interval: int = Field(default=60, ge=10, le=300, description="Segundos entre rotaciones")
    scraping_interval: int = Field(default=10, ge=1, le=60, description="Minutos entre scraping")
    separator_url: str = Field(default="", description="URL del separador SVG")
    show_source_name: bool = Field(default=True, description="Mostrar nombre de fuente")


@router.post("/ticker/auto/start")
async def start_auto_mode(request: AutoModeStartRequest):
    """
    Inicia el modo automático completo del ticker.
    
    Activa:
    - Scheduler de scraping automático
    - Rotación automática de categorías
    - Envío automático a Singular.live
    - Marcado de headlines como enviados
    
    Args:
        request: Configuración del modo automático
        
    Returns:
        dict: Estado del modo automático
    """
    from services.auto_mode import auto_mode_service
    
    result = await auto_mode_service.start(
        rotation_interval=request.rotation_interval,
        scraping_interval=request.scraping_interval,
        separator_url=request.separator_url,
        show_source_name=request.show_source_name
    )
    
    return result


@router.post("/ticker/auto/stop")
async def stop_auto_mode():
    """
    Detiene el modo automático completo del ticker.
    
    Desactiva:
    - Scheduler de scraping
    - Rotación automática
    
    El ticker permanece en su estado actual (In/Out).
    El usuario retoma el control manual.
    
    Returns:
        dict: Confirmación de detención
    """
    from services.auto_mode import auto_mode_service
    
    result = await auto_mode_service.stop()
    return result


@router.get("/ticker/auto/status")
async def get_auto_mode_status():
    """
    Obtiene el estado actual del modo automático.
    
    Returns:
        dict: Estado detallado incluyendo:
            - auto_mode_active: Si el modo está activo
            - scheduler_running: Si el scheduler está corriendo
            - rotation_running: Si la rotación está activa
            - current_category: Categoría actual en rotación
            - next_rotation_in: Segundos hasta próxima rotación
            - next_scraping_in: Segundos hasta próximo scraping
    """
    from services.auto_mode import auto_mode_service
    
    status = await auto_mode_service.get_status()
    return {
        "status": "success",
        **status
    }


@router.get("/ticker/state")
async def get_ticker_state():
    """
    Obtiene el estado actual del ticker desde Singular.live en tiempo real.
    
    Retorna si el ticker está visible (In) u oculto (Out).
    Útil para sincronizar el frontend con el estado real de Singular.
    
    Returns:
        dict: Estado del ticker
            - state: 'In' si visible, 'Out' si oculto, None si error
            - message: Mensaje descriptivo del estado
    """
    try:
        async with SingularLiveClient() as client:
            # Obtener info del Control App que incluye el estado actual
            info = await client.get_control_app_info()
            
            if not info:
                return {
                    "status": "error",
                    "message": "No se pudo obtener información de Singular.live",
                    "state": None
                }
            
            # Obtener estado rastreado
            tracked_state = ticker_state_tracker.get_state()
            
            return {
                "status": "success",
                "message": "Estado obtenido del tracker interno",
                "state": tracked_state.get("state", "Out"),  # Default a Out si no hay estado
                "category": tracked_state.get("category"),
                "info": {
                    "output_url": info.get("outputUrl"),
                    "has_config": bool(info)
                }
            }
            
    except Exception as e:
        logger.error(f"Error obteniendo estado del ticker: {e}")
        return {
            "status": "error",
            "message": str(e),
            "state": None
        }
