"""
Scheduler para tareas automáticas de scraping.

Programa y ejecuta scraping periódico de noticias y actualiza el ticker.
"""

from datetime import datetime
from typing import List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select, func, update

from core.logging import logger
from core.config import settings
from db.database import AsyncSessionLocal
from db.models import Headline
from .scraper import NewsScraper
from .singular_client import SingularLiveClient
from db.redis_client import redis_client


class ScrapingScheduler:
    """
    Scheduler para ejecutar scraping automático y rotación de ticker.
    """
    
    def __init__(self):
        """Inicializa el scheduler."""
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        self.current_category_index = 0
        self.interval_minutes = settings.SCRAPING_INTERVAL  # Intervalo configurado
        self.categories = [
            "local", "nacional", "mundo", 
            "deportes", "economia", "tecnologia", 
            "entretenimiento"
        ]
    
    async def _scrape_job(self):
        """
        Job de scraping que se ejecuta periódicamente.
        
        - Scrapea fuentes y guarda headlines en BD
        - En MODO MANUAL: actualiza ticker con categoría actual
        - En MODO AUTO: NO toca ticker (rotación lo maneja)
        """
        logger.info("=== Ejecutando job de scraping automático ===")
        
        async with AsyncSessionLocal() as db:
            async with NewsScraper(db, redis_client) as scraper:
                stats = await scraper.scrape_all(active_only=True)
                logger.info(f"✓ Scraping completado: {stats}")
            
            # MODO MANUAL: Actualizar ticker si está visible
            # Verificar si hay modo automático activo
            from services.auto_mode import auto_mode_service
            
            if not auto_mode_service._is_active:
                # Estamos en MODO MANUAL - actualizar ticker con categoría actual
                from services.ticker_state_tracker import ticker_state_tracker
                current_state = ticker_state_tracker.get_state()
                
                if current_state.get("state") == "In":
                    # Ticker está visible, actualizar con nuevos headlines
                    current_category = current_state.get("category", "mundo")
                    logger.info(f"📝 Modo manual: actualizando ticker con categoría '{current_category}'")
                    
                    # Obtener headlines frescos de la categoría actual
                    from db.models import Headline, NewsSource
                    from sqlalchemy import select
                    
                    result = await db.execute(
                        select(Headline, NewsSource.name)
                        .join(NewsSource, Headline.source_id == NewsSource.id)
                        .where(Headline.category == current_category)
                        .order_by(Headline.created_at.desc())
                        .limit(10)
                    )
                    rows = result.all()
                    
                    if rows:
                        headlines = [row[0] for row in rows]
                        source_names = [row[1] for row in rows]
                        
                        # Fuente más común
                        from collections import Counter
                        most_common_source = Counter(source_names).most_common(1)[0][0] if source_names else ""
                        
                        headline_texts = [h.title for h in headlines]
                        
                        # Actualizar ticker (sin transición OUT/IN para modo manual)
                        from services.singular_client import SingularLiveClient
                        async with SingularLiveClient() as client:
                            # Obtener separator_url desde AppConfig o usar default
                            separator_url = "https://assets.singular.live/7072b13f9e20b98034f48d6202400ff9/svgs/7esb5NbN8cQxcCk7X0szej_w24h24.svg"
                            
                            success = await client.show_ticker(
                                headlines=headline_texts,
                                category=current_category,
                                source_name=most_common_source,
                                separator_url=separator_url
                            )
                            
                            if success:
                                # Marcar headlines como enviados
                                from datetime import datetime
                                for headline in headlines:
                                    headline.sent_to_singular = True
                                    headline.sent_at = datetime.utcnow()
                                await db.commit()
                                
                                logger.info(f"✅ Ticker actualizado en modo manual: {len(headlines)} headlines de {most_common_source}")
                    else:
                        logger.warning(f"No hay headlines para categoría '{current_category}' después del scraping")
                else:
                    logger.info("Ticker no está visible, no se actualiza")
            else:
                logger.info("Modo automático activo, rotación maneja el ticker")
    
    # Método _update_ticker_with_rotation() ELIMINADO
    # La rotación del ticker ahora se maneja exclusivamente por TickerRotationService
    # para evitar conflictos y duplicación de lógica
    
    def start(self, interval_minutes: int = None):
        """
        Inicia el scheduler.
        
        Args:
            interval_minutes: Intervalo en minutos (usa settings si no se especifica)
        """
        interval = interval_minutes or settings.SCRAPING_INTERVAL
        self.interval_minutes = interval  # Guardar intervalo configurado
        
        # Si ya está corriendo, solo actualizar el job con nuevo intervalo
        if self.is_running:
            logger.info(f"Scheduler ya corriendo, actualizando intervalo de {self.interval_minutes}min a {interval}min")
            # Remover job anterior y agregar nuevo con nuevo intervalo
            # APScheduler permite replace_existing=True para esto
        
        # Agregar job de scraping con actualización de ticker
        # replace_existing=True permite actualizar si ya existe
        self.scheduler.add_job(
            self._scrape_job,
            trigger=IntervalTrigger(minutes=interval),
            id="scraping_job",
            name="Scraping Automático de Noticias",
            replace_existing=True
        )
        
        # Solo hacer start() si el scheduler no está corriendo
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
        
        logger.info(f"✓ Scheduler configurado - Scraping cada {interval} minutos")
    
    def stop(self):
        """Detiene el scheduler."""
        if not self.is_running:
            logger.warning("Scheduler no está en ejecución")
            return
        
        self.scheduler.shutdown(wait=False)
        self.is_running = False
        logger.info("✓ Scheduler detenido")
    
    def pause(self):
        """Pausa el scheduler."""
        if not self.is_running:
            logger.warning("Scheduler no está en ejecución")
            return
        
        self.scheduler.pause()
        logger.info("Scheduler pausado")
    
    def resume(self):
        """Reanuda el scheduler."""
        if not self.is_running:
            logger.warning("Scheduler no está en ejecución")
            return
        
        self.scheduler.resume()
        logger.info("Scheduler reanudado")
    
    async def update_interval(self, new_interval: int):
        """
        Actualiza el intervalo de scraping dinámicamente.
        
        Args:
            new_interval: Nuevo intervalo en minutos
        """
        if new_interval < 1:
            raise ValueError("El intervalo debe ser al menos 1 minuto")
        
        # Actualizar settings
        settings.SCRAPING_INTERVAL = new_interval
        
        # Si está corriendo, reiniciar con nuevo intervalo
        if self.is_running:
            was_paused = self.scheduler.state == 2
            
            # Eliminar job anterior
            try:
                self.scheduler.remove_job("scraping_job")
            except:
                pass
            
            # Agregar nuevo job con nuevo intervalo
            self.scheduler.add_job(
                self._scrape_job,
                trigger=IntervalTrigger(minutes=new_interval),
                id="scraping_job",
                name="Scraping Automático de Noticias",
                replace_existing=True
            )
            
            if was_paused:
                self.scheduler.pause()
            
            logger.info(f"✓ Intervalo de scraping actualizado a {new_interval} minutos")
        
        # Guardar en BD
        from db.models import AppConfig
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(AppConfig).where(AppConfig.key == "scraping_interval")
            )
            entry = result.scalar_one_or_none()
            
            if entry:
                entry.value = str(new_interval)
                entry.updated_at = datetime.utcnow()
            else:
                entry = AppConfig(
                    key="scraping_interval",
                    value=str(new_interval),
                    description="Intervalo de scraping automático en minutos"
                )
                db.add(entry)
            
            await db.commit()
            logger.info(f"✓ Intervalo guardado en BD: {new_interval} min")
    
    def get_status(self) -> dict:
        """
        Obtiene el estado del scheduler.
        
        Returns:
            dict: Estado del scheduler
        """
        if not self.is_running:
            return {
                "running": False,
                "next_run": None,
                "interval_minutes": self.interval_minutes,
                "current_category": None
            }
        
        job = self.scheduler.get_job("scraping_job")
        
        return {
            "running": True,
            "paused": self.scheduler.state == 2,  # STATE_PAUSED
            "next_run": job.next_run_time.isoformat() if job and job.next_run_time else None,
            "interval_minutes": self.interval_minutes,
            "current_category": self.categories[self.current_category_index - 1] if self.current_category_index > 0 else None
        }


# Instancia global del scheduler
scraping_scheduler = ScrapingScheduler()
