"""
Servicio para rastrear el estado actual del ticker.

Mantiene en memoria el último estado conocido del ticker (In/Out).
"""

from typing import Optional
from core.logging import logger


class TickerStateTracker:
    """
    Rastrea el estado actual del ticker de Singular.live.
    
    Como Singular.live API no expone el estado directamente,
    rastreamos cada operación show/hide para mantener sincronizado.
    """
    
    def __init__(self):
        self._current_state: Optional[str] = None  # 'In', 'Out', or None
        self._last_category: Optional[str] = None
    
    def set_state(self, state: str, category: Optional[str] = None):
        """
        Actualiza el estado del ticker.
        
        Args:
            state: Nuevo estado ('In' o 'Out')
            category: Categoría actual si está visible
        """
        self._current_state = state
        if state == 'In' and category:
            self._last_category = category
        elif state == 'Out':
            self._last_category = None
            
        logger.debug(f"Estado del ticker actualizado: {state}" + 
                    (f" - Categoría: {category}" if category else ""))
    
    def get_state(self) -> dict:
        """
        Obtiene el estado actual del ticker.
        
        Returns:
            dict con 'state' y 'category'
        """
        return {
            "state": self._current_state,
            "category": self._last_category
        }
    
    @property
    def is_visible(self) -> bool:
        """Retorna True si el ticker está visible."""
        return self._current_state == 'In'
    
    @property
    def is_hidden(self) -> bool:
        """Retorna True si el ticker está oculto."""
        return self._current_state == 'Out'


# Instancia global del tracker
ticker_state_tracker = TickerStateTracker()
