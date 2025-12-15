"""
Servicio de Rotación Automática del Ticker de Singular.live.

Permite rotar automáticamente entre categorías cada cierto intervalo de tiempo.
"""

import asyncio
from typing import Optional, List
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import AsyncSessionLocal
from db.models import Headline, NewsSource, AppConfig
from services.singular_client import SingularLiveClient
from core.logging import logger


class TickerRotationService:
    """
    Servicio para rotación automática de categorías del ticker.
    
    Cambia automáticamente entre categorías cada N segundos,
    mostrando solo categorías que tienen titulares disponibles.
    """
    
    def __init__(self):
        self.categories = ["local", "nacional", "mundo", "deportes", 
                          "economia", "tecnologia", "entretenimiento"]
        self.current_index = 0
        self.rotation_task: Optional[asyncio.Task] = None
        self.is_running = False
        self.interval_seconds = 60  # Default 60 segundos
        
    async def start_rotation(
        self, 
        interval_seconds: int = 60,
        separator_url: str = "https://assets.singular.live/7072b13f9e20b98034f48d6202400ff9/svgs/7esb5NbN8cQxcCk7X0szej_w24h24.svg",
        show_source_name: bool = True
    ):
        """
        Inicia la rotación automática de categorías.
        
        Args:
            interval_seconds: Segundos entre cada rotación
            separator_url: URL del icono separador
            show_source_name: Si mostrar nombre de fuente
        """
        # Si ya está corriendo, cancelar tarea actual y crear nueva con nuevos valores
        if self.is_running and self.rotation_task:
            logger.info(f"Rotación ya activa ({self.interval_seconds}s), actualizando a ({interval_seconds}s)")
            self.rotation_task.cancel()
            try:
                await self.rotation_task
            except asyncio.CancelledError:
                pass
        
        self.interval_seconds = interval_seconds
        self.is_running = True
        
        # Guardar configuración en BD
        # TODO: Descomentar cuando AppConfig.singular_config esté disponible
        # await self._save_rotation_config(interval_seconds, separator_url, show_source_name)
        
        # Iniciar tarea de rotación con nuevos parámetros
        self.rotation_task = asyncio.create_task(
            self._rotation_loop(separator_url, show_source_name)
        )
        
        logger.info(f"✓ Rotación automática iniciada (intervalo: {interval_seconds}s)")
        
        return {
            "status": "success",
            "message": f"Rotación iniciada correctamente ({interval_seconds}s)",
            "rotation_status": self.get_rotation_status()
        }
        
    async def stop_rotation(self):
        """Detiene la rotación automática."""
        if not self.is_running:
            logger.warning("La rotación no está activa (ya detenida)")
            return {
                "status": "success",
                "message": "Rotación ya estaba detenida"
            }
            
        self.is_running = False
        
        if self.rotation_task:
            self.rotation_task.cancel()
            try:
                await self.rotation_task
            except asyncio.CancelledError:
                pass
                
        # Actualizar BD
        # TODO: Descomentar cuando AppConfig.singular_config esté disponible
        # await self._save_rotation_config(0, "", True)  # interval=0 indica desactivado
        
        logger.info("✓ Rotación automática detenida")
        
        return {
            "status": "success",
            "message": "Rotación detenida correctamente"
        }
        
    def get_status(self) -> dict:
        """
        Obtiene el estado actual de la rotación.
        
        Returns:
            dict: Estado de rotación con is_running, interval, current_category
        """
        current_category = self.categories[self.current_index] if self.is_running else None
        
        return {
            "is_running": self.is_running,
            "interval_seconds": self.interval_seconds,  # Siempre devolver intervalo configurado
            "current_category": current_category,
            "categories": self.categories
        }
        
    async def load_rotation_config(self):
        """Carga la configuración de rotación guardada al iniciar."""
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(AppConfig).limit(1))
                config = result.scalar_one_or_none()
                
                if config and config.singular_config:
                    rot_config = config.singular_config
                    rotation_interval = rot_config.get("rotation_interval", 0)
                    
                    if rotation_interval > 0:
                        separator_url = rot_config.get("separator_url", "")
                        show_source_name = rot_config.get("show_source_name", True)
                        
                        logger.info(f"Restaurando rotación automática (intervalo: {rotation_interval}s)")
                        
                        self.interval_seconds = rotation_interval
                        self.is_running = True
                        self.rotation_task = asyncio.create_task(
                            self._rotation_loop(separator_url, show_source_name)
                        )
        except Exception as e:
            logger.error(f"Error cargando config de rotación: {e}")

    async def _rotation_loop(self, separator_url: str, show_source_name: bool):
        """Loop principal de rotación."""
        try:
            while self.is_running:
                # Esperar intervalo
                await asyncio.sleep(self.interval_seconds)
                
                if not self.is_running:
                    break
                    
                # Rotar a siguiente categoría
                await self._rotate_to_next_category(separator_url, show_source_name)
                
        except asyncio.CancelledError:
            logger.info("Loop de rotación cancelado")
        except Exception as e:
            logger.error(f"Error en loop de rotación: {e}")
            self.is_running = False
            
    async def _rotate_to_next_category(self, separator_url: str, show_source_name: bool):
        """Cambia a la siguiente categoría con titulares."""
        max_attempts = len(self.categories)
        attempts = 0
        
        async with AsyncSessionLocal() as db:
            while attempts < max_attempts:
                # Siguiente categoría
                self.current_index = (self.current_index + 1) % len(self.categories)
                next_category = self.categories[self.current_index]
                
                # Verificar si tiene titulares
                result = await db.execute(
                    select(Headline, NewsSource.name)
                    .join(NewsSource, Headline.source_id == NewsSource.id)
                    .where(Headline.category == next_category)
                    .order_by(Headline.created_at.desc())
                    .limit(10)
                )
                rows = result.all()
                
                if rows:
                    # Encontrado! Enviar a Singular
                    headlines = [row[0] for row in rows]
                    source_names = [row[1] for row in rows]
                    
                    # Fuente más común
                    from collections import Counter
                    most_common_source = Counter(source_names).most_common(1)[0][0] if source_names else ""
                    
                    headline_texts = [h.title for h in headlines]
                    
                    async with SingularLiveClient() as client:
                        # TRANSICIÓN: Primero ocultar ticker de categoría anterior
                        logger.info(f"🔄 Iniciando transición a {next_category}")
                        await client.hide_ticker()
                        
                        # Pausa breve para transición visual (1 segundo)
                        await asyncio.sleep(1)
                        
                        # Luego mostrar ticker con nueva categoría
                        success = await client.show_ticker(
                            headlines=headline_texts,
                            category=next_category,
                            source_name=most_common_source if show_source_name else "",
                            separator_url=separator_url
                        )
                        
                        if success:
                            # Marcar como enviados
                            for headline in headlines:
                                headline.sent_to_singular = True
                                headline.sent_at = datetime.utcnow()
                            await db.commit()
                            
                            logger.info(f"✅ Rotación completada: {next_category} ({len(headlines)} items)")
                            
                            # Actualizar tracker (Opcional, importar tracker causaría ciclo circular)
                            # Para un diseño limpio, ticker_rotation debería emitir evento o tracker suscribirse,
                            # pero por ahora lo dejamos así ya que Singular es la fuente de verdad.
                            return
                
                attempts += 1
                
            logger.warning("No se encontraron categorías con titulares para rotar")

    async def get_rotation_status(self) -> dict:
        """Alias para get_status para compatibilidad."""
        return self.get_status()

    async def _save_rotation_config(self, interval: int, separator: str, show_source: bool):
        """Guarda configuración en BD."""
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(AppConfig).limit(1))
                config = result.scalar_one_or_none()
                
                if config:
                    if config.singular_config:
                        config.singular_config["rotation_interval"] = interval
                        config.singular_config["separator_url"] = separator
                        config.singular_config["show_source_name"] = show_source
                    else:
                        config.singular_config = {
                            "rotation_interval": interval,
                            "separator_url": separator,
                            "show_source_name": show_source
                        }
                    await db.commit()
        except Exception as e:
            logger.error(f"Error guardando config de rotación: {e}")


# Instancia global
ticker_rotation_service = TickerRotationService()
