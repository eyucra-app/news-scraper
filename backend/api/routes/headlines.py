"""
Routers de API para gestión de titulares.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime

from api.deps import get_database
from db.models import Headline, NewsSource, CategoryEnum
from services.singular_client import SingularLiveClient
from core.logging import logger


router = APIRouter(prefix="/headlines", tags=["headlines"])


# Schemas
class HeadlineResponse(BaseModel):
    """Schema de respuesta de titular."""
    id: int
    title: str
    category: CategoryEnum | None
    extracted_data: str | None
    source_id: int
    source_name: str | None
    sent_to_singular: bool
    sent_at: str | None
    created_at: str
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[HeadlineResponse])
async def list_headlines(
    limit: int = Query(50, le=200),
    offset: int = 0,
    category: CategoryEnum | None = None,
    source_id: int | None = None,
    unsent_only: bool = False,
    db: AsyncSession = Depends(get_database)
):
    """
    Lista titulares con filtros y paginación.
    
    Args:
        limit: Número máximo de resultados (máx 200)
        offset: Offset para paginación
        category: Filtrar por categoría
        source_id: Filtrar por fuente
        unsent_only: Solo titulares no enviados a Singular
        db: Sesión de base de datos
    
    Returns:
        List[HeadlineResponse]: Lista de titulares
    """
    stmt = select(
        Headline,
        NewsSource.name.label("source_name")
    ).join(NewsSource).order_by(desc(Headline.created_at))
    
    if category:
        stmt = stmt.where(Headline.category == category)
    
    if source_id:
        stmt = stmt.where(Headline.source_id == source_id)
    
    if unsent_only:
        stmt = stmt.where(Headline.sent_to_singular == False)
    
    stmt = stmt.limit(limit).offset(offset)
    
    result = await db.execute(stmt)
    rows = result.all()
    
    headlines = []
    for headline, source_name in rows:
        headline_dict = {
            "id": headline.id,
            "title": headline.title,
            "category": headline.category,
            "extracted_data": headline.extracted_data,
            "source_id": headline.source_id,
            "source_name": source_name,
            "sent_to_singular": headline.sent_to_singular,
            "sent_at": headline.sent_at.isoformat() if headline.sent_at else None,
            "created_at": headline.created_at.isoformat()
        }
        headlines.append(HeadlineResponse(**headline_dict))
    
    return headlines


@router.get("/stats")
async def get_headlines_stats(db: AsyncSession = Depends(get_database)):
    """
    Obtiene estadísticas de titulares.
    
    Returns:
        dict: Estadísticas
    """
    # Total de titulares
    total_stmt = select(func.count(Headline.id))
    total_result = await db.execute(total_stmt)
    total = total_result.scalar()
    
    # Titulares no enviados
    unsent_stmt = select(func.count(Headline.id)).where(Headline.sent_to_singular == False)
    unsent_result = await db.execute(unsent_stmt)
    unsent = unsent_result.scalar()
    
    # Por categoría
    category_stmt = select(
        Headline.category,
        func.count(Headline.id).label("count")
    ).group_by(Headline.category)
    category_result = await db.execute(category_stmt)
    by_category = {row[0].value: row[1] for row in category_result.all() if row[0]}
    
    return {
        "total": total,
        "sent": total - unsent,
        "unsent": unsent,
        "by_category": by_category
    }


@router.post("/send")
async def send_headlines_to_singular(
    headline_ids: List[int],
    db: AsyncSession = Depends(get_database)
):
    """
    Envía titulares seleccionados a Singular.live.
    
    Args:
        headline_ids: IDs de titulares a enviar
        db: Sesión de base de datos
    
    Returns:
        dict: Resultado del envío
    """
    # Obtener titulares
    stmt = select(Headline, NewsSource.name).join(NewsSource).where(
        Headline.id.in_(headline_ids)
    )
    result = await db.execute(stmt)
    rows = result.all()
    
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontraron titulares con los IDs proporcionados"
        )
    
    # Preparar datos para Singular
    headlines_data = []
    headline_objects = []
    
    for headline, source_name in rows:
        headlines_data.append({
            "title": headline.title,
            "source": source_name,
            "category": headline.category.value if headline.category else "otro",
            "data": headline.extracted_data or ""
        })
        headline_objects.append(headline)
    
    # Enviar a Singular.live
    async with SingularLiveClient() as client:
        success = await client.send_headlines(headlines_data)
    
    if success:
        # Marcar como enviados
        now = datetime.utcnow()
        for headline in headline_objects:
            headline.sent_to_singular = True
            headline.sent_at = now
        
        await db.commit()
        
        logger.info(f"Enviados {len(headline_ids)} titulares a Singular.live")
        
        return {
            "status": "success",
            "sent": len(headline_ids)
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error enviando titulares a Singular.live"
        )


@router.delete("/{headline_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_headline(
    headline_id: int,
    db: AsyncSession = Depends(get_database)
):
    """
    Elimina un titular.
    
    Args:
        headline_id: ID del titular
        db: Sesión de base de datos
    """
    stmt = select(Headline).where(Headline.id == headline_id)
    result = await db.execute(stmt)
    headline = result.scalar_one_or_none()
    
    if not headline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Titular con ID {headline_id} no encontrado"
        )
    
    await db.delete(headline)
    await db.commit()
