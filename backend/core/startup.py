"""
Funciones de inicialización de la aplicación.

Carga configuraciones desde la base de datos al arrancar.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import AsyncSessionLocal
from db.models import AppConfig
from core.config import settings
from core.logging import logger


async def load_config_from_database():
    """
    Carga configuración guardada desde la base de datos.
    
    Se ejecuta al iniciar la aplicación para restaurar la configuración
    de Singular.live que el usuario guardó previamente.
    """
    try:
        async with AsyncSessionLocal() as db:
            # Cargar Control App ID
            result = await db.execute(
                select(AppConfig).where(AppConfig.key == "singular_control_app_id")
            )
            config_entry = result.scalar_one_or_none()
            
            if config_entry:
                settings.SINGULAR_CONTROL_APP_ID = config_entry.value
                logger.info(f"✓ Control App ID cargado desde BD: {config_entry.value[:10]}...")
            
            # Cargar Output URL
            result = await db.execute(
                select(AppConfig).where(AppConfig.key == "singular_output_url")
            )
            output_entry = result.scalar_one_or_none()
            
            if output_entry:
                settings.SINGULAR_OUTPUT_URL = output_entry.value
                logger.info(f"✓ Output URL cargado desde BD")
            
            # Cargar Scraping Interval
            result = await db.execute(
                select(AppConfig).where(AppConfig.key == "scraping_interval")
            )
            interval_entry = result.scalar_one_or_none()
            
            if interval_entry:
                try:
                    settings.SCRAPING_INTERVAL = int(interval_entry.value)
                    logger.info(f"✓ Intervalo de scraping cargado desde BD: {settings.SCRAPING_INTERVAL} min")
                except ValueError:
                    logger.warning(f"Valor inválido para scraping_interval: {interval_entry.value}")
            
    except Exception as e:
        logger.warning(f"No se pudo cargar configuración desde BD (puede ser la primera ejecución): {e}")
