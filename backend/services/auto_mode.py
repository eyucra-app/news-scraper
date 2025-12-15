"""
Servicio para coordinar el modo automático del ticker.

Gestiona scheduler y rotación de forma unificada para evitar conflictos.
"""

from datetime import datetime
from typing import Optional, Dict
from core.logging import logger
from services.scheduler import scraping_scheduler
from services.ticker_rotation import ticker_rotation_service


class AutoModeService:
    """
    Servicio centralizado para gestionar el modo automático del ticker.
    
    Coordina:
    - Scheduler de scraping automático
    - Rotación automática de categorías
    """
    
    def __init__(self):
        self._is_active = False
        self._started_at: Optional[datetime] = None
    
    async def start(
        self,
        rotation_interval: int = 60,
        scraping_interval: int = 10,
        separator_url: str = "",
        show_source_name: bool = True
    ) -> Dict:
        """
        Inicia el modo automático completo.
        
        Args:
            rotation_interval: Segundos entre rotaciones de categoría
            scraping_interval: Minutos entre scraping automáticos
            separator_url: URL del separador para el ticker
            show_source_name: Si mostrar nombre de fuente
            
        Returns:
            Dict con estado del sistema
        """
        if self._is_active:
            logger.warning("Modo automático ya está activo")
            return {
                "status": "warning",
                "message": "Modo automático ya está activo",
                "auto_mode_active": True
            }
        
        try:
            # 1. Iniciar/reanudar scheduler de scraping
            logger.info(f"Iniciando scheduler (intervalo: {scraping_interval}min)")
            
            # Si el scheduler está pausado, reanudarlo primero
            if scraping_scheduler.is_running:
                logger.info("Scheduler ya está corriendo, reanudando...")
                scraping_scheduler.resume()
            
            # Luego iniciar/actualizar con nuevo intervalo
            scraping_scheduler.start(interval_minutes=scraping_interval)
            
            # 2. Iniciar rotación automática
            logger.info(f"Iniciando rotación (intervalo: {rotation_interval}s)")
            result = await ticker_rotation_service.start_rotation(
                interval_seconds=rotation_interval,
                separator_url=separator_url,
                show_source_name=show_source_name
            )
            
            if result and result.get('status') == 'success':
                self._is_active = True
                self._started_at = datetime.utcnow()
                
                logger.info("✅ Modo automático iniciado exitosamente")
                
                return {
                    "status": "success",
                    "message": "Modo automático iniciado: scraping + rotación activos",
                    "auto_mode_active": True,
                    "scheduler_running": True,
                    "rotation_running": True,
                    "started_at": self._started_at.isoformat()
                }
            else:
                # Rollback: detener scheduler si rotación falló
                scraping_scheduler.pause()
                error_msg = result.get('message') if result else "Rotación retornó None"
                raise Exception(f"Error iniciando rotación: {error_msg}")
                
        except Exception as e:
            logger.error(f"Error iniciando modo automático: {e}")
            self._is_active = False
            return {
                "status": "error",
                "message": f"Error: {str(e)}",
                "auto_mode_active": False
            }
    
    async def stop(self) -> Dict:
        """
        Detiene el modo automático completo.
        
        Returns:
            Dict con estado del sistema
        """
        if not self._is_active:
            logger.warning("Intentando detener modo automático inactivo (limpieza forzada)")
            # Continuamos para asegurar limpieza de scheduler/rotación
        
        try:
            # 1. Ocultar ticker automáticamente
            logger.info("Ocultando ticker automáticamente")
            try:
                from services.singular_client import SingularLiveClient
                async with SingularLiveClient() as client:
                    await client.hide_ticker()
                logger.info("✓ Ticker ocultado")
            except Exception as e:
                logger.warning(f"No se pudo ocultar ticker: {e}")
                # Continuamos con la detención aunque falle
            
            # 2. Pausar scheduler (NO detener, solo pausar)
            logger.info("Pausando scheduler de scraping")
            scraping_scheduler.pause()
            
            # 3. Detener rotación
            logger.info("Deteniendo rotación automática")
            result = await ticker_rotation_service.stop_rotation()
            
            self._is_active = False
            self._started_at = None
            
            logger.info("✅ Modo automático detenido exitosamente")
            
            return {
                "status": "success",
                "message": "Modo automático detenido: ticker ocultado y usuario tiene control manual",
                "auto_mode_active": False,
                "scheduler_running": False,
                "rotation_running": False
            }
            
        except Exception as e:
            logger.error(f"Error deteniendo modo automático: {e}")
            return {
                "status": "error",
                "message": f"Error: {str(e)}",
                "auto_mode_active": self._is_active
            }
    
    async def get_status(self) -> Dict:
        """
        Obtiene el estado actual del modo automático.
        
        Returns:
            Dict con estado detallado del sistema
        """
        try:
            # Obtener estado de rotación (get_status() NO es async, pero funciona con await)
            rotation_status = ticker_rotation_service.get_status()
            
            # Obtener estado de scheduler
            scheduler_running = scraping_scheduler.is_running
            
            # Calcular próximas ejecuciones
            next_rotation_in = None
            current_category = None
            
            if rotation_status.get('is_running'):
                # TODO: Implementar cálculo de tiempo restante
                current_category = rotation_status.get('current_category', 'local')
                next_rotation_in = rotation_status.get('interval_seconds', 60)
            
            return {
                "auto_mode_active": self._is_active,
                "scheduler_running": scheduler_running,
                "rotation_running": rotation_status.get('is_running', False),
                "current_category": current_category,
                "next_rotation_in": next_rotation_in,
                "next_scraping_in": None,  # TODO: Implementar
                "started_at": self._started_at.isoformat() if self._started_at else None,
                "scraping_interval_minutes": scraping_scheduler.interval_minutes,
                "rotation_interval_seconds": rotation_status.get('interval_seconds', 60)
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estado de modo automático: {e}")
            return {
                "auto_mode_active": False,
                "error": str(e)
            }


# Instancia global del servicio
auto_mode_service = AutoModeService()
