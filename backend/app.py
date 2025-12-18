"""
Aplicación principal de FastAPI - News Scraper Backend.

Este es el punto de entrada del backend de la aplicación.
"""

from contextlib import asynccontextmanager
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

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
    
    # Auto-setup de dependencias en primer arranque
    try:
        from core.auto_setup import setup_dependencies
        await setup_dependencies()
    except Exception as e:
        logger.warning(f"Auto-setup no disponible: {e}")
    
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

# Servir frontend estático
# Buscar directorio del frontend build
# En PyInstaller, usar sys._MEIPASS para encontrar recursos
if getattr(sys, 'frozen', False):
    # Ejecutándose como ejecutable PyInstaller
    base_path = Path(sys._MEIPASS)
else:
    # Ejecutándose como script Python normal
    base_path = Path(__file__).parent.parent

frontend_path = base_path / "frontend" / "out"

if frontend_path.exists():
    # Montar archivos estáticos
    app.mount("/_next", StaticFiles(directory=str(frontend_path / "_next")), name="next_static")
    
    # Servir otros assets estáticos
    try:
        app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
    except:
        pass  # Si no hay directorio static, ignorar
    
    logger.info(f"✓ Frontend estático montado desde: {frontend_path}")
else:
    logger.warning(f"⚠ Frontend build no encontrado en: {frontend_path}")

# Registrar routers
app.include_router(sources.router, prefix="/api")
app.include_router(scraping.router, prefix="/api")
app.include_router(headlines.router, prefix="/api")
app.include_router(config.router, prefix="/api")


@app.get("/api")
async def api_root():
    """
    API root endpoint - Health check.
    
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


# Catch-all route para SPA (debe ser la última)
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """
    Sirve el frontend de Next.js.
    Para cualquier ruta que no sea API, sirve index.html (SPA).
    """
    # Usar el mismo base_path que arriba
    if getattr(sys, 'frozen', False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent.parent
    
    frontend_path = base_path / "frontend" / "out"
    
    # Si la ruta es para un archivo específico que existe, servirlo
    file_path = frontend_path / full_path
    if file_path.is_file():
        return FileResponse(file_path)
    
    # Para rutas de la SPA (/, /config, /headlines, etc.), servir index.html
    index_path = frontend_path / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    
    # Si no hay frontend, retornar mensaje
    return {
        "error": "Frontend not found",
        "message": f"Frontend path checked: {frontend_path}",
        "frozen": getattr(sys, 'frozen', False),
        "api_docs":"/docs"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG
    )
