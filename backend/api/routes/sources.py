"""
Routers de API para gestión de fuentes de noticias.
"""

from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, field_serializer

from api.deps import get_database
from db.models import NewsSource, CategoryEnum
from services.scraper import NewsScraper
from db.redis_client import redis_client
from core.logging import logger


router = APIRouter(prefix="/sources", tags=["sources"])


# Schemas Pydantic
class NewsSourceCreate(BaseModel):
    """Schema para crear fuente de noticias."""
    name: str
    url: str
    container: str
    holder: str
    data_field: str | None = None
    requires_js: bool = False
    category: CategoryEnum
    is_active: bool = True


class NewsSourceUpdate(BaseModel):
    """Schema para actualizar fuente de noticias."""
    name: str | None = None
    url: str | None = None
    container: str | None = None
    holder: str | None = None
    data_field: str | None = None
    requires_js: bool | None = None
    category: CategoryEnum | None = None
    is_active: bool | None = None


class NewsSourceResponse(BaseModel):
    """Schema de respuesta de fuente de noticias."""
    id: int
    name: str
    url: str
    container: str
    holder: str
    data_field: str | None
    requires_js: bool
    category: CategoryEnum
    is_active: bool
    scrape_count: int
    error_count: int
    last_scraped_at: datetime | None = None
    
    @field_serializer('last_scraped_at')
    def serialize_datetime(self, dt: datetime | None, _info):
        if dt is None:
            return None
        return dt.isoformat()
    
    class Config:
        from_attributes = True


# Endpoints
@router.get("/", response_model=List[NewsSourceResponse])
async def list_sources(
    active_only: bool = False,
    db: AsyncSession = Depends(get_database)
):
    """
    Lista todas las fuentes de noticias.
    
    Args:
        active_only: Si solo listar fuentes activas
        db: Sesión de base de datos
    
    Returns:
        List[NewsSourceResponse]: Lista de fuentes
    """
    stmt = select(NewsSource)
    if active_only:
        stmt = stmt.where(NewsSource.is_active == True)
    
    result = await db.execute(stmt)
    sources = result.scalars().all()
    
    return sources


@router.post("/", response_model=NewsSourceResponse, status_code=status.HTTP_201_CREATED)
async def create_source(
    source_data: NewsSourceCreate,
    db: AsyncSession = Depends(get_database)
):
    """
    Crea una nueva fuente de noticias.
    
    Args:
        source_data: Datos de la fuente
        db: Sesión de base de datos
    
    Returns:
        NewsSourceResponse: Fuente creada
    """
    # Verificar si ya existe una fuente con ese nombre
    stmt = select(NewsSource).where(NewsSource.name == source_data.name)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una fuente con el nombre '{source_data.name}'"
        )
    
    # Crear fuente
    source = NewsSource(**source_data.model_dump())
    db.add(source)
    await db.commit()
    await db.refresh(source)
    
    logger.info(f"Fuente creada: {source.name}")
    return source


@router.get("/{source_id}", response_model=NewsSourceResponse)
async def get_source(
    source_id: int,
    db: AsyncSession = Depends(get_database)
):
    """
    Obtiene una fuente específica por ID.
    
    Args:
        source_id: ID de la fuente
        db: Sesión de base de datos
    
    Returns:
        NewsSourceResponse: Fuente solicitada
    """
    stmt = select(NewsSource).where(NewsSource.id == source_id)
    result = await db.execute(stmt)
    source = result.scalar_one_or_none()
    
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fuente con ID {source_id} no encontrada"
        )
    
    return source


@router.put("/{source_id}", response_model=NewsSourceResponse)
async def update_source(
    source_id: int,
    source_data: NewsSourceUpdate,
    db: AsyncSession = Depends(get_database)
):
    """
    Actualiza una fuente existente.
    
    Args:
        source_id: ID de la fuente
        source_data: Datos a actualizar
        db: Sesión de base de datos
    
    Returns:
        NewsSourceResponse: Fuente actualizada
    """
    stmt = select(NewsSource).where(NewsSource.id == source_id)
    result = await db.execute(stmt)
    source = result.scalar_one_or_none()
    
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fuente con ID {source_id} no encontrada"
        )
    
    # Actualizar campos
    update_data = source_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(source, field, value)
    
    await db.commit()
    await db.refresh(source)
    
    logger.info(f"Fuente actualizada: {source.name}")
    return source


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(
    source_id: int,
    db: AsyncSession = Depends(get_database)
):
    """
    Elimina una fuente y todos sus titulares asociados.
    
    Args:
        source_id: ID de la fuente
        db: Sesión de base de datos
    """
    stmt = select(NewsSource).where(NewsSource.id == source_id)
    result = await db.execute(stmt)
    source = result.scalar_one_or_none()
    
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fuente con ID {source_id} no encontrada"
        )
    
    await db.delete(source)
    await db.commit()
    
    logger.info(f"Fuente eliminada: {source.name}")


@router.post("/{source_id}/test")
async def test_source(
    source_id: int,
    db: AsyncSession = Depends(get_database)
):
    """
    Testea una fuente realizando un scraping de prueba.
    
    Args:
        source_id: ID de la fuente
        db: Sesión de base de datos
    
    Returns:
        dict: Resultados del test
    """
    stmt = select(NewsSource).where(NewsSource.id == source_id)
    result = await db.execute(stmt)
    source = result.scalar_one_or_none()
    
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fuente con ID {source_id} no encontrada"
        )
    
    # Realizar scraping de prueba (sin guardar)
    async with NewsScraper(db, redis_client) as scraper:
        headlines, log = await scraper.scrape_source(source, save_to_db=False)
    
    return {
        "source": source.name,
        "status": log.status.value,
        "stats": {
            "headlines_found": log.headlines_found,
            "headlines_new": len(headlines)
        },
        "sample_headlines": [h.title for h in headlines[:5]],
        "error_message": log.error_message
    }

