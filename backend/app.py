"""
Aplicación principal de FastAPI - News Scraper Backend.

Este es el punto de entrada del backend de la aplicación.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.logging import logger
from db.database import init_db
from db.redis_client import redis_client
from api.routes import sources, scraping, headlines, config


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager de la aplicación.
    
    Ejecuta código al inicio y al cierre de la aplicación.
    """
    # Startup
    logger.info("=== Iniciando News Scraper Backend ===")
    logger.info(f"Entorno: {settings.ENVIRONMENT}")
    logger.info(f"Debug: {settings.DEBUG}")
    
    # Inicializar base de datos
    logger.info("Inicializando base de datos...")
    await init_db()
    logger.info("✓ Base de datos inicializada")
    
    # Cargar configuración guardada desde BD
    logger.info("Cargando configuración desde base de datos...")
    from core.startup import load_config_from_database
    await load_config_from_database()
    
    # Cargar y restaurar rotación automática si estaba activa
    logger.info("Verificando rotación automática...")
    from services.ticker_rotation import ticker_rotation_service
    await ticker_rotation_service.load_rotation_config()
    
    # Conectar a Redis (opcional)
    if settings.REDIS_ENABLED:
        logger.info("Conectando a Redis...")
        await redis_client.connect()
        logger.info("✓ Redis conectado")
    else:
        logger.info("⚠ Redis deshabilitado - usando cache en memoria")
    
    # Iniciar scheduler automático de scraping
    logger.info("Iniciando scheduler automático...")
    from services.scheduler import scraping_scheduler
    scraping_scheduler.start()
    logger.info(f"✓ Scheduler iniciado (intervalo: {settings.SCRAPING_INTERVAL} minutos)")
    
    logger.info("✓ Backend iniciado exitosamente")
    
    yield
    
    # Shutdown
    logger.info("=== Cerrando News Scraper Backend ===")
    if settings.REDIS_ENABLED:
        await redis_client.disconnect()
    logger.info("✓ Backend cerrado")


# Crear aplicación FastAPI
app = FastAPI(
    title="News Scraper API",
    description="API para scraping de noticias e integración con Singular.live",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS con orígenes desde settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(sources.router, prefix="/api")
app.include_router(scraping.router, prefix="/api")
app.include_router(headlines.router, prefix="/api")
app.include_router(config.router, prefix="/api")


@app.get("/")
async def root():
    """
    Endpoint raíz - Health check.
    
    Returns:
        dict: Información básica de la API
    """
    return {
        "name": "News Scraper API",
        "version": "1.0.0",
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: Estado de salud de la aplicación
    """
    # Verificar Redis
    redis_status = "connected" if redis_client.enabled and redis_client.redis else "disconnected"
    
    return {
        "status": "healthy",
        "redis": redis_status,
        "environment": settings.ENVIRONMENT
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG
    )
