"""
Sistema de logging configurado para la aplicación.

Proporciona loggers configurados según las especificaciones del settings.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from .config import settings


def setup_logging(
    level: Optional[str] = None,
    log_format: Optional[str] = None
) -> logging.Logger:
    """
    Configura el sistema de logging de la aplicación.
    
    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Formato del log (text o json)
    
    Returns:
        logging.Logger: Logger configurado
    """
    level = level or settings.LOG_LEVEL
    log_format = log_format or settings.LOG_FORMAT
    
    # Configurar nivel
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Configurar formato
    if log_format == "json":
        formatter = logging.Formatter(
            '{"time":"%(asctime)s", "level":"%(levelname)s", "module":"%(module)s", "message":"%(message)s"}'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # Configurar handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Configurar logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.addHandler(console_handler)
    
    # Logger específico de la aplicación
    logger = logging.getLogger("news_scraper")
    logger.setLevel(numeric_level)
    
    return logger


# Logger global de la aplicación
logger = setup_logging()
