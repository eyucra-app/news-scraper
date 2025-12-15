"""
Cliente Redis para caché y message queue.

Proporciona funciones para caché de datos y cola de mensajes.
"""

import json
from typing import Optional, Any
import redis.asyncio as redis

from core.config import settings
from core.logging import logger


class RedisClient:
    """
    Cliente Redis asíncrono para caché y queue.
    """
    
    def __init__(self):
        """Inicializa el cliente Redis."""
        self.redis: Optional[redis.Redis] = None
        self.enabled = settings.CACHE_ENABLED
    
    async def connect(self):
        """Conecta al servidor Redis."""
        if not self.enabled:
            logger.warning("Caché Redis deshabilitado")
            return
        
        try:
            self.redis = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            # Test de conexión
            await self.redis.ping()
            logger.info("Conectado a Redis exitosamente")
        except Exception as e:
            logger.error(f"Error conectando a Redis: {e}")
            self.enabled = False
    
    async def disconnect(self):
        """Desconecta del servidor Redis."""
        if self.redis:
            await self.redis.close()
            logger.info("Desconectado de Redis")
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Obtiene un valor del caché.
        
        Args:
            key: Clave del caché
        
        Returns:
            Valor deserializado o None si no existe
        """
        if not self.enabled or not self.redis:
            return None
        
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Error obteniendo de Redis: {e}")
        
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Guarda un valor en el caché.
        
        Args:
            key: Clave del caché
            value: Valor a guardar (será serializado a JSON)
            ttl: Tiempo de vida en segundos (usa TTL por defecto si no se especifica)
        
        Returns:
            True si exitoso, False en caso contrario
        """
        if not self.enabled or not self.redis:
            return False
        
        ttl = ttl or settings.CACHE_TTL
        
        try:
            serialized = json.dumps(value)
            await self.redis.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Error guardando en Redis: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Elimina una clave del caché.
        
        Args:
            key: Clave a eliminar
        
        Returns:
            True si se eliminó, False en caso contrario
        """
        if not self.enabled or not self.redis:
            return False
        
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error eliminando de Redis: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """
        Verifica si una clave existe.
        
        Args:
            key: Clave a verificar
        
        Returns:
            True si existe, False en caso contrario
        """
        if not self.enabled or not self.redis:
            return False
        
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Error verificando existencia en Redis: {e}")
            return False
    
    async def acquire_lock(
        self,
        lock_name: str,
        timeout: int = 300
    ) -> Optional[redis.client.Lock]:
        """
        Adquiere un lock distribuido.
        
        Args:
            lock_name: Nombre del lock
            timeout: Timeout en segundos
        
        Returns:
            Lock object o None si no se pudo adquirir
        """
        if not self.enabled or not self.redis:
            return None
        
        try:
            lock = self.redis.lock(lock_name, timeout=timeout)
            acquired = await lock.acquire(blocking=False)
            if acquired:
                return lock
        except Exception as e:
            logger.error(f"Error adquiriendo lock: {e}")
        
        return None


# Instancia global del cliente Redis
redis_client = RedisClient()


async def get_redis() -> RedisClient:
    """
    Dependency para obtener cliente Redis.
    
    Returns:
        RedisClient: Cliente Redis global
    """
    return redis_client
