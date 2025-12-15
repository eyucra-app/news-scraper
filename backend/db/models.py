"""
Modelos de base de datos usando SQLAlchemy.

Define todas las tablas y relaciones de la base de datos.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, 
    DateTime, ForeignKey, JSON, Enum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum


Base = declarative_base()


class CategoryEnum(str, enum.Enum):
    """Categorías de noticias disponibles."""
    LOCAL = "local"
    NACIONAL = "nacional"
    MUNDO = "mundo"
    DEPORTES = "deportes"
    ECONOMIA = "economia"
    TECNOLOGIA = "tecnologia"
    ENTRETENIMIENTO = "entretenimiento"
    OTRO = "otro"


class StatusEnum(str, enum.Enum):
    """Estados de scraping."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class NewsSource(Base):
    """
    Modelo para fuentes de noticias.
    
    Representa un sitio web del cual se extraen noticias.
    """
    __tablename__ = "news_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, comment="Nombre de la fuente")
    url = Column(String(512), nullable=False, comment="URL del sitio a scrapear")
    
    # Configuración de scraping
    container = Column(String(255), nullable=False, comment="Clase CSS del contenedor principal")
    holder = Column(String(255), nullable=False, comment="Etiqueta HTML que contiene el título")
    data_field = Column(String(255), nullable=True, comment="Campo adicional para metadatos")
    requires_js = Column(Boolean, default=False, nullable=False, comment="Si el sitio requiere JavaScript para cargar contenido")
    
    # Metadatos
    category = Column(Enum(CategoryEnum), default=CategoryEnum.OTRO, comment="Categoría de noticias")
    is_active = Column(Boolean, default=True, comment="Si la fuente está activa")
    
    # Tiempos
    created_at = Column(DateTime, default=datetime.utcnow, comment="Fecha de creación")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="Última actualización")
    last_scraped_at = Column(DateTime, nullable=True, comment="Último scraping exitoso")
    
    # Estadísticas
    scrape_count = Column(Integer, default=0, comment="Número total de scrapes")
    error_count = Column(Integer, default=0, comment="Número de errores")
    
    # Relaciones
    headlines = relationship("Headline", back_populates="source", cascade="all, delete-orphan")
    logs = relationship("ScrapeLog", back_populates="source", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<NewsSource(id={self.id}, name='{self.name}', category='{self.category}')>"


class Headline(Base):
    """
    Modelo para titulares extraídos.
    
    Representa un titular de noticia extraído de una fuente.
    """
    __tablename__ = "headlines"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False, comment="Texto del titular")
    
    # Metadatos
    category = Column(Enum(CategoryEnum), comment="Categoría del titular")
    extracted_data = Column(String(512), nullable=True, comment="Datos adicionales extraídos")
    
    # Relación con fuente
    source_id = Column(Integer, ForeignKey("news_sources.id"), nullable=False)
    source = relationship("NewsSource", back_populates="headlines")
    
    # Estado de envío
    sent_to_singular = Column(Boolean, default=False, comment="Si fue enviado a Singular.live")
    sent_at = Column(DateTime, nullable=True, comment="Cuándo fue enviado")
    
    # Tiempo
    created_at = Column(DateTime, default=datetime.utcnow, index=True, comment="Cuándo se extrajo")
    
    # Hash para detectar duplicados
    content_hash = Column(String(64), index=True, comment="Hash MD5 del contenido para deduplicación")
    
    def __repr__(self):
        return f"<Headline(id={self.id}, title='{self.title[:50]}...', source_id={self.source_id})>"


class ScrapeLog(Base):
    """
    Modelo para logs de scraping.
    
    Registra cada ejecución de scraping con su resultado.
    """
    __tablename__ = "scrape_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relación con fuente
    source_id = Column(Integer, ForeignKey("news_sources.id"), nullable=True)
    source = relationship("NewsSource", back_populates="logs")
    
    # Información del scrape
    status = Column(Enum(StatusEnum), default=StatusEnum.PENDING, comment="Estado del scrape")
    headlines_found = Column(Integer, default=0, comment="Número de titulares encontrados")
    headlines_new = Column(Integer, default=0, comment="Número de titulares nuevos")
    
    # Tiempos
    started_at = Column(DateTime, default=datetime.utcnow, comment="Inicio del scrape")
    completed_at = Column(DateTime, nullable=True, comment="Fin del scrape")
    duration_seconds = Column(Integer, nullable=True, comment="Duración en segundos")
    
    # Errores
    error_message = Column(Text, nullable=True, comment="Mensaje de error si falló")
    
    def __repr__(self):
        return f"<ScrapeLog(id={self.id}, source_id={self.source_id}, status='{self.status}')>"


class AppConfig(Base):
    """
    Modelo para configuración de la aplicación.
    
    Almacena configuraciones que pueden cambiar en runtime.
    """
    __tablename__ = "app_config"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, nullable=False, index=True, comment="Clave de configuración")
    value = Column(Text, nullable=False, comment="Valor de configuración")
    description = Column(Text, nullable=True, comment="Descripción de la configuración")
    
    # Tiempos
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<AppConfig(key='{self.key}', value='{self.value[:20]}...')>"
