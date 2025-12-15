"""
Dependencias compartidas para endpoints de FastAPI.
"""

from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from db.redis_client import get_redis, RedisClient


async def get_database() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency para obtener sesión de base de datos.
    
    Yields:
        AsyncSession: Sesión de base de datos
    """
    async for session in get_db():
        yield session


async def get_redis_client() -> RedisClient:
    """
    Dependency para obtener cliente Redis.
    
    Returns:
        RedisClient: Cliente Redis
    """
    return await get_redis()
