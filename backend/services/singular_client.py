"""
Cliente para la API de Singular.live Control App (API v2).

Maneja la comunicación con Singular.live para actualizar el RSS Ticker.
"""

import asyncio
from typing import List, Dict, Any, Optional
import aiohttp
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from core.config import settings
from core.logging import logger


class SingularLiveClient:
    """
    Cliente asíncrono para la API v2 de Singular.live Control App.
    
    Actualiza el RSS Ticker enviando payloads al endpoint de control.
    """
    
    def __init__(self, control_app_id: Optional[str] = None):
        """
        Inicializa el cliente de Singular.live.
        
        Args:
            control_app_id: ID del Control App (usa settings si no se proporciona)
        """
        self.control_app_id = control_app_id or settings.SINGULAR_CONTROL_APP_ID
        self.base_url = settings.SINGULAR_BASE_URL
        self.ticker_subcomp_id = settings.SINGULAR_TICKER_SUBCOMP_ID
        
        if not self.control_app_id:
            logger.warning("Control App ID de Singular.live no configurado")
        
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.disconnect()
    
    async def connect(self):
        """Crea sesión HTTP."""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def disconnect(self):
        """Cierra sesión HTTP."""
        if self.session:
            await self.session.close()
            self.session = None
    
    def _build_control_url(self) -> str:
        """
        Construye la URL del endpoint de control.
        
        Returns:
            str: URL completa del endpoint
        """
        return f"{self.base_url}/controlapps/{self.control_app_id}/control"
    
    def _build_info_url(self) -> str:
        """
        Construye la URL para obtener información del Control App.
        
        Returns:
            str: URL completa del endpoint de info
        """
        return f"{self.base_url}/controlapps/{self.control_app_id}"
    
    async def get_control_app_info(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene la información del Control App desde Singular.live.
        
        Incluye outputUrl, publicControlApiUrl, etc.
        
        Returns:
            dict: Información del Control App o None si falla
            
        Example response:
            {
                "outputUrl": "https://app.singular.live/output/7HyLhxQeykALXaeTzhjFj3/Output?aspect=16:9",
                "publicControlApiUrl": "https://app.singular.live/apiv2/controlapps/243pPuk6OSMKYixCEz5Qzj/control",
                ...
            }
        """
        if not self.control_app_id:
            logger.error("No se puede obtener info: Control App ID no configurado")
            return None
        
        if not self.session:
            await self.connect()
        
        url = self._build_info_url()
        
        try:
            logger.debug(f"Obteniendo info de Control App: {url}")
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    info = await response.json()
                    logger.info(f"✓ Info de Control App obtenida exitosamente")
                    logger.debug(f"Output URL: {info.get('outputUrl')}")
                    return info
                else:
                    error_text = await response.text()
                    logger.error(f"Error obteniendo info: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error obteniendo info del Control App: {type(e).__name__} - {e}")
            return None
    
    @retry(
        stop=stop_after_attempt(settings.MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(aiohttp.ClientError),
        reraise=True
    )
    async def send_control_payload(self, payload: List[Dict[str, Any]]) -> bool:
        """
        Envía payload al endpoint de control de Singular.live.
        
        Incluye retry automático con backoff exponencial.
        
        Args:
            payload: Lista de payloads para sub-compositions
        
        Returns:
            bool: True si exitoso, False en caso contrario
        
        Raises:
            aiohttp.ClientError: Si falla después de todos los reintentos
        """
        if not self.control_app_id:
            logger.error("No se puede enviar: Control App ID no configurado")
            return False
        
        if not self.session:
            await self.connect()
        
        url = self._build_control_url()
        headers = {
            "Content-Type": "application/json",
            "User-Agent": settings.USER_AGENT
        }
        
        try:
            logger.debug(f"Enviando a Singular.live: {url}")
            logger.debug(f"Payload: {payload}")
            
            # Usar PATCH en lugar de POST según especificación de Singular.live API
            async with self.session.patch(url, json=payload, headers=headers) as response:
                response_text = await response.text()
                logger.debug(f"Response status: {response.status}")
                logger.debug(f"Response body: {response_text}")
                
                if response.status >= 400:
                    logger.error(f"Singular.live returned error {response.status}: {response_text}")
                    return False
                    
                logger.info(f"Datos enviados exitosamente a Singular.live (status: {response.status})")
                return True
                
        except aiohttp.ClientError as e:
            logger.error(f"Error de conexión con Singular.live: {type(e).__name__} - {e}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado enviando datos: {type(e).__name__} - {e}")
            return False
    
    async def update_ticker(
        self,
        headlines: List[str],
        category: str = "MUNDO",
        source_name: str = "",
        state: str = "In",
        speed: str = "7",
        direction: str = "RightToLeft",
        separator_url: str = "https://assets.singular.live/7072b13f9e20b98034f48d6202400ff9/svgs/7esb5NbN8cQxcCk7X0szej_w24h24.svg"
    ) -> bool:
        """
        Actualiza el RSS Ticker en Singular.live.
        
        Args:
            headlines: Lista de titulares (se unirán con saltos de línea)
            category: Categoría para mostrar (ej: "MUNDO", "DEPORTES")
            source_name: Nombre de la fuente de noticias (ej: "RNN", "CORREO DEL SUR")
            state: "In" (mostrar ticker) o "Out" (ocultar ticker)
            speed: Velocidad del ticker como string (default: "7")
            direction: "RightToLeft" o "LeftToRight"
            separator_url: URL del icono separador entre titulares
        
        Returns:
            bool: True si exitoso
        
        Example:
            await client.update_ticker(
                headlines=["Titular 1", "Titular 2"],
                category="MUNDO",
                source_name="RNN",
                state="In"
            ... )
        """
        if not headlines:
            logger.warning("No hay titulares para actualizar en el ticker")
            return False
        
        # Unir titulares con salto de línea (formato requerido por Singular)
        news_text = "\n".join(headlines)
        
        # Construir payload según nueva estructura del usuario
        payload = [{
            "subCompositionId": self.ticker_subcomp_id,
            "subCompositionName": "RSS Ticker",
            "mainComposition": False,
            "state": state,
            "payload": {
                "Custom Category": category.upper(),
                "Custom Credit": source_name.upper(),
                "Direction": direction,
                "Message Seperator": separator_url,  # URL string
                "Speed": speed,
                "Text": news_text,
                "customRssFeedUrl": "",
                "numMessages": "10",
                "requestInterval": "10",
                "rssFeed": "manualFeed",
                "tickerMessages": ""
            }
        }]
        
        logger.info(f"Actualizando ticker: categoría={category}, fuente={source_name}, state={state}, {len(headlines)} titulares")
        return await self.send_control_payload(payload)
    
    async def show_ticker(
        self,
        headlines: List[str],
        category: str = "MUNDO",
        source_name: str = "",
        separator_url: str = "https://assets.singular.live/7072b13f9e20b98034f48d6202400ff9/svgs/7esb5NbN8cQxcCk7X0szej_w24h24.svg"
    ) -> bool:
        """
        Muestra el ticker con titulares (state: In).
        
        Args:
            headlines: Lista de titulares
            category: Categoría de noticias
            source_name: Nombre de la fuente
            separator_url: URL del icono separador
        
        Returns:
            bool: True si exitoso
        """
        return await self.update_ticker(headlines, category, source_name, state="In", separator_url=separator_url)
    
    async def hide_ticker(self) -> bool:
        """
        Oculta el ticker (state: Out).
        
        Solo cambia el estado a "Out" sin modificar otros campos como
        Custom Category o Custom Credit para evitar parpadeo de valores.
        
        Returns:
            bool: True si exitoso
        """
        # Enviar payload mínimo que solo cambie el state
        payload = [{
            "subCompositionId": self.ticker_subcomp_id,
            "subCompositionName": "RSS Ticker",
            "mainComposition": False,
            "state": "Out"
            # NO incluimos payload.Custom Category ni Custom Credit
            # para evitar que cambien durante la transición
        }]
        
        logger.info("Ocultando ticker (state: Out)")
        return await self.send_control_payload(payload)
    
    async def test_connection(self) -> bool:
        """
        Prueba la conexión con Singular.live.
        
        Envía un payload de prueba al ticker (state: Out para no interferir).
        
        Returns:
            bool: True si la conexión es exitosa, False en caso contrario
        """
        test_headlines = ["Conexión de prueba desde News Scraper"]
        
        try:
            result = await self.update_ticker(
                headlines=test_headlines,
                category="TEST",
                state="Out"  # No mostrar en pantalla
            )
            if result:
                logger.info("✓ Conexión con Singular.live exitosa")
            else:
                logger.error("✗ Fallo en conexión con Singular.live")
            return result
        except Exception as e:
            logger.error(f"✗ Error probando conexión: {e}")
            return False
