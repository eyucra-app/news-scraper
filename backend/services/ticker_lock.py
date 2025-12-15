"""
Sistema de lock para coordinar acceso al ticker de Singular.live.

Previene race conditions cuando múltiples servicios (scheduler, rotación, manual)
intentan actualizar el ticker simultáneamente.
"""

import asyncio
from core.logging import logger


class TickerLock:
    """
    Lock asíncrono para coordinar acceso exclusivo al ticker.
    
    Uso:
        async with ticker_lock:
            await singular_client.show_ticker(...)
    """
    
    def __init__(self):
        self._lock = asyncio.Lock()
        self._owner = None
    
    async def __aenter__(self):
        """Adquiere el lock indicando quién lo tiene."""
        await self._lock.acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Libera el lock."""
        self._owner = None
        self._lock.release()
    
    def set_owner(self, owner: str):
        """Establece quién está usando el lock (para debugging)."""
        self._owner = owner
        logger.debug(f"Ticker lock adquirido por: {owner}")
    
    @property
    def is_locked(self) -> bool:
        """Verifica si el lock está actualmente adquirido."""
        return self._lock.locked()
    
    @property
    def owner(self) -> str:
        """Retorna el dueño actual del lock."""
        return self._owner


# Instancia global del lock
ticker_lock = TickerLock()
