"""
Routers de API para configuración de la aplicación.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime

from core.config import settings
from services.singular_client import SingularLiveClient
from api.deps import get_database
from core.logging import logger


router = APIRouter(prefix="/config", tags=["config"])


class SingularConfig(BaseModel):
    """Schema de configuración de Singular.live."""
    control_app_id: str
    output_url: str
    has_config: bool


class SingularConfigUpdate(BaseModel):
    """Schema para actualizar configuración de Singular.live."""
    control_app_id: str


class AppConfigResponse(BaseModel):
    """Schema de respuesta de configuración."""
    singular: SingularConfig
    scraping_interval: int
    environment: str
    debug: bool


@router.get("/", response_model=AppConfigResponse)
async def get_config():
    """
    Obtiene la configuración actual de la aplicación.
    
    Returns:
        AppConfigResponse: Configuración actual
    """
    return AppConfigResponse(
        singular=SingularConfig(
            control_app_id=settings.SINGULAR_CONTROL_APP_ID,
            output_url=settings.SINGULAR_OUTPUT_URL,
            has_config=bool(settings.SINGULAR_CONTROL_APP_ID)
        ),
        scraping_interval=settings.SCRAPING_INTERVAL,
        environment=settings.ENVIRONMENT,
        debug=settings.DEBUG
    )


@router.put("/singular")
async def update_singular_config(config: SingularConfigUpdate, db: AsyncSession = Depends(get_database)):
    """
    Actualiza la configuración de Singular.live.
    
    Hace GET al Control App para obtener outputUrl automáticamente.
    Guarda la configuración en la base de datos para persistencia.
    
    Args:
        config: Nueva configuración con control_app_id
        db: Sesión de base de datos
    
    Returns:
        dict: Mensaje de confirmación con outputUrl
    """
    logger.info(f"Actualizando Control App ID de Singular.live: {config.control_app_id[:10]}...")
    
    # Actualizar settings en runtime
    settings.SINGULAR_CONTROL_APP_ID = config.control_app_id
    
    # Obtener información del Control App (incluyendo outputUrl)
    try:
        async with SingularLiveClient(control_app_id=config.control_app_id) as client:
            info = await client.get_control_app_info()
            
        if info and info.get('outputUrl'):
            # Guardar Output URL obtenido automáticamente
            settings.SINGULAR_OUTPUT_URL = info['outputUrl']
            
            # Persistir en base de datos
            from db.models import AppConfig
            
            # Guardar Control App ID
            result = await db.execute(
                select(AppConfig).where(AppConfig.key == "singular_control_app_id")
            )
            config_entry = result.scalar_one_or_none()
            
            if config_entry:
                config_entry.value = config.control_app_id
                config_entry.updated_at = datetime.utcnow()
            else:
                config_entry = AppConfig(
                    key="singular_control_app_id",
                    value=config.control_app_id,
                    description="ID de la Control App de Singular.live"
                )
                db.add(config_entry)
            
            # Guardar Output URL
            result = await db.execute(
                select(AppConfig).where(AppConfig.key == "singular_output_url")
            )
            output_entry = result.scalar_one_or_none()
            
            if output_entry:
                output_entry.value = info['outputUrl']
                output_entry.updated_at = datetime.utcnow()
            else:
                output_entry = AppConfig(
                    key="singular_output_url",
                    value=info['outputUrl'],
                    description="URL del Output de Singular.live"
                )
                db.add(output_entry)
            
            await db.commit()
            
            logger.info(f"✓ Control App ID verificado y guardado en BD - Output URL: {info['outputUrl']}")
            return {
                "status": "success",
                "message": "Control App ID verificado, guardado en BD y Output URL obtenido automáticamente",
                "output_url": info['outputUrl'],
                "connection_test": "passed"
            }
        else:
            logger.warning("No se pudo obtener información del Control App")
            return {
                "status": "warning",
                "message": "Control App ID guardado pero no se pudo verificar. Verifica el ID.",
                "connection_test": "failed"
            }
    except Exception as e:
        logger.error(f"Error verificando Control App: {e}")
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")


@router.post("/test-singular")
async def test_singular_connection():
    """
    Prueba la conexión con Singular.live obteniendo info del Control App.
    
    Returns:
        dict: Resultado del test con outputUrl si es exitoso
    """
    logger.info("Probando conexión con Singular.live")
    
    async with SingularLiveClient() as client:
        info = await client.get_control_app_info()
    
    if info and info.get('outputUrl'):
        return {
            "status": "success",
            "message": "Conexión con Singular.live exitosa",
            "output_url": info['outputUrl']
        }
    else:
        return {
            "status": "error",
            "message": "Fallo en conexión con Singular.live. Verifica tu Control App ID."
        }
