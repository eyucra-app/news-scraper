"""
Configuración central de la aplicación News Scraper.

Este módulo contiene todas las configuraciones de la aplicación,
cargadas desde variables de entorno para mayor seguridad.
"""

import os
from typing import List
from pydantic import validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuración de la aplicación usando Pydantic Settings.
    
    Las variables se cargan desde el archivo .env o variables de entorno del sistema.
    """
    
    # =================================
    # Configuración de Singular.live
    # =================================
    SINGULAR_APP_INSTANCE_ID: str = ""
    SINGULAR_SHARED_TOKEN: str = ""
    SINGULAR_API_KEY: str = ""
    SINGULAR_BASE_URL: str = "https://app.singular.live/apiv2"
    
    # =================================
    # Base de datos (SQLite para deployment local)
    # =================================
    @property
    def DATABASE_URL(self) -> str:
        """Obtiene la URL de la base de datos con ruta persistente."""
        import os
        from pathlib import Path
        
        # Usar AppData en Windows, home en otros sistemas
        if os.name == 'nt':  # Windows
            app_data = Path(os.getenv('APPDATA')) / 'NewsScraper'
        else:  # Linux/Mac
            app_data = Path.home() / '.newsscraper'
        
        # Crear directorio si no existe
        app_data.mkdir(parents=True, exist_ok=True)
        
        db_path = app_data / 'news_scraper.db'
        return f"sqlite+aiosqlite:///{db_path}"
    
    # =================================
    # Redis (Opcional - usar cache en memoria si no está disponible)
    # =================================
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_ENABLED: bool = False  # Deshabilitado por defecto para deployment local
    
    # =================================
    # Aplicación
    # =================================
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    
    FRONTEND_HOST: str = "0.0.0.0"
    FRONTEND_PORT: int = 3000
    
    # URL del backend para el frontend
    NEXT_PUBLIC_API_URL: str = "http://localhost:8000"
    
    # =================================
    # Singular.live Integration
    # =================================
    SINGULAR_CONTROL_APP_ID: str = ""
    SINGULAR_BASE_URL: str = "https://app.singular.live/apiv2"
    SINGULAR_TICKER_SUBCOMP_ID: str = "7bb6ec7f-1b21-44af-8026-1acdcf4e59d4"
    SINGULAR_OUTPUT_URL: str = ""  # Se obtiene automáticamente del Control App API
    
    # Deprecated (API v1 - mantenido para compatibilidad)
    SINGULAR_APP_INSTANCE_ID: str = ""
    SINGULAR_SHARED_TOKEN: str = ""
    
    # =================================
    # Scraping
    # =================================
    SCRAPING_INTERVAL: int = 10  # minutos (configurable desde BD)
    REQUEST_TIMEOUT: int = 30  # segundos
    MAX_RETRIES: int = 3
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # =================================
    # Logging
    # =================================
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "text"  # json o text
    
    # =================================
    # CORS
    # =================================
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000", 
        "http://127.0.0.1:3000",
        "https://news-scraper-v1.vercel.app",  # Dominio de producción (actual)
        "https://news-scraper.vercel.app",     # Dominio alternativo
        "https://*.vercel.app"  # Dominios de preview
    ]
    
    # =================================
    # Caché
    # =================================
    CACHE_TTL: int = 300  # segundos
    CACHE_ENABLED: bool = True
    
    class Config:
        """Configuración de Pydantic Settings."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Instancia global de configuración
settings = Settings()


def get_settings() -> Settings:
    """
    Obtiene la instancia de configuración.
    
    Returns:
        Settings: Instancia de configuración de la aplicación
    """
    return settings
