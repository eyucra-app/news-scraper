"""
Motor de scraping de noticias.

Extrae titulares de sitios web configurados de forma asíncrona.
"""

import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import aiohttp
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

from core.logging import logger
from core.config import settings
from db.models import NewsSource, Headline, ScrapeLog, StatusEnum
from db.redis_client import RedisClient

# Límite máximo de titulares por fuente
MAX_HEADLINES_PER_SOURCE = 10


class NewsScraper:
    """
    Motor de scraping asíncrono de noticias.
    
    Extrae titulares de fuentes configuradas y los almacena en base de datos.
    """
    
    def __init__(
        self,
        db_session: AsyncSession,
        redis_client: Optional[RedisClient] = None
    ):
        """
        Inicializa el scraper.
        
        Args:
            db_session: Sesión de base de datos
            redis_client: Cliente Redis para caché (opcional)
        """
        self.db = db_session
        self.redis = redis_client
        self.settings = settings
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
            timeout = aiohttp.ClientTimeout(total=settings.REQUEST_TIMEOUT)
            self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def disconnect(self):
        """Cierra sesión HTTP."""
        if self.session:
            await self.session.close()
            self.session = None
    
    @staticmethod
    def _calculate_hash(text: str) -> str:
        """
        Calcula hash MD5 de un texto para deduplicación.
        
        Args:
            text: Texto a hashear
        
        Returns:
            str: Hash MD5 en hexadecimal
        """
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Limpia un texto eliminando espacios extra y caracteres especiales.
        
        Args:
            text: Texto a limpiar
        
        Returns:
            str: Texto limpio
        """
        # Eliminar espacios múltiples
        text = ' '.join(text.split())
        # Eliminar saltos de línea
        text = text.replace('\n', ' ').replace('\r', '')
        # Trim
        text = text.strip()
        return text
    
    @staticmethod
    def _is_css_selector(selector: str) -> bool:
        """
        Detecta si un selector es un selector CSS complejo.
        
        Selectores CSS complejos incluyen:
        - Selectores de atributos: a[href*="value"], input[type="text"]
        - Combinadores: div > p, h1 + h2, ul ~ p
        - Pseudo-clases: :nth-child, :first-child, :not()
        - Selectores de clase múltiple: .class1.class2
        
        Args:
            selector: String del selector a verificar
        
        Returns:
            bool: True si es un selector CSS complejo, False si es simple
        """
        if not selector:
            return False
        
        # Indicadores de selectores CSS complejos
        css_indicators = [
            '[',   # Selector de atributo
            '>',   # Combinador hijo directo
            '+',   # Combinador hermano adyacente
            '~',   # Combinador hermano general
            ':',   # Pseudo-clases
            '*=',  # Atributo contiene
            '^=',  # Atributo empieza con
            '$=',  # Atributo termina con
        ]
        
        return any(indicator in selector for indicator in css_indicators)
    
    async def _fetch_html(self, url: str) -> Optional[str]:
        """
        Descarga el HTML de una URL.
        
        Args:
            url: URL a descargar
        
        Returns:
            str: HTML descargado o None si falla
        """
        if not self.session:
            await self.connect()
        
        headers = {
            "User-Agent": settings.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        }
        
        try:
            logger.debug(f"Descargando HTML de: {url}")
            async with self.session.get(url, headers=headers) as response:
                response.raise_for_status()
                html = await response.text()
                logger.debug(f"HTML descargado: {len(html)} caracteres")
                return html
        except aiohttp.ClientError as e:
            logger.error(f"Error descargando {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado descargando {url}: {e}")
            return None
    
    async def _fetch_html_playwright(self, url: str) -> Optional[str]:
        """
        Obtiene HTML renderizado con JavaScript usando Playwright.
        
        Usado para sitios que requieren JavaScript para cargar contenido
        (SPAs, frameworks modernos como React, Vue, Astro, etc).
        
        Args:
            url: URL a descargar
            
        Returns:
            Optional[str]: HTML renderizado o None si hay error
        """
        try:
            logger.info(f"Usando Playwright para renderizar: {url}")
            
            async with async_playwright() as p:
                # Lanzar navegador Chromium en modo headless
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )
                
                page = await browser.new_page()
                
                # Configurar timeout y user agent
                page.set_default_timeout(self.settings.REQUEST_TIMEOUT * 1000)
                await page.set_extra_http_headers({
                    'User-Agent': self.settings.USER_AGENT
                })
                
                # Navegar y esperar a que la red esté inactiva
                logger.debug(f"Navegando con navegador headless a: {url}")
                await page.goto(url, wait_until='networkidle')
                
                # Espera adicional para frameworks que renderizan después de networkidle
                # Esto ayuda con Vue, React, Astro y otros frameworks modernos
                await page.wait_for_timeout(2000)
                
                # Hacer scroll para trigger lazy loading si existe
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(500)
                
                # Volver arriba
                await page.evaluate("window.scrollTo(0, 0)")
                
                # Obtener HTML completamente renderizado
                html = await page.content()
                
                await browser.close()
                
                logger.info(f"HTML renderizado obtenido: {len(html)} caracteres")
                return html
                
        except PlaywrightTimeoutError:
            logger.error(f"Timeout al cargar {url} con Playwright")
            return None
        except Exception as e:
            logger.error(f"Error con Playwright para {url}: {e}")
            return None
    
    def _parse_headlines(
        self,
        html: str,
        container_class: str,
        holder_tag: str,
        data_class: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Parsea HTML y extrae titulares.
        
        Soporta tanto selectores simples (para retrocompatibilidad) como
        selectores CSS complejos.
        
        Ejemplos de selectores soportados:
        - Selectores simples: "h2", ".article", "uk-container"
        - Selectores CSS: "a[href*='/local/']", "div.class1.class2", "div > h2"
        
        Args:
            html: HTML a parsear
            container_class: Selector CSS o clase del contenedor principal
            holder_tag: Selector CSS o etiqueta HTML que contiene el título
            data_class: Selector CSS o clase para datos adicionales (opcional)
        
        Returns:
            List[Dict]: Lista de titulares extraídos
        """
        soup = BeautifulSoup(html, 'lxml')
        headlines = []
        
        try:
            # Buscar contenedor usando selector CSS o método antiguo
            container = None
            
            if self._is_css_selector(container_class):
                # Selector CSS complejo - usar select()
                logger.debug(f"Usando selector CSS para contenedor: {container_class}")
                containers = soup.select(container_class)
                container = containers[0] if containers else None
            else:
                # Método antiguo para retrocompatibilidad
                logger.debug(f"Usando búsqueda simple para contenedor: {container_class}")
                
                # Primero intentar como etiqueta HTML (body, main, div, etc)
                container = soup.find(container_class)
                
                # Si no se encuentra, intentar como clase
                if not container:
                    container = soup.find(class_=container_class)
                
                # Si aún no se encuentra, intentar como id
                if not container:
                    container = soup.find(id=container_class)
            
            if not container:
                logger.warning(f"No se encontró contenedor: {container_class}")
                return headlines
            
            # Buscar todos los holders dentro del contenedor
            holders = []
            
            if self._is_css_selector(holder_tag):
                # Selector CSS complejo - usar select()
                logger.debug(f"Usando selector CSS para holders: {holder_tag}")
                holders = container.select(holder_tag)
            else:
                # Método antiguo para retrocompatibilidad
                logger.debug(f"Usando búsqueda simple para holders: {holder_tag}")
                if holder_tag.startswith('.'):
                    # Es una clase
                    holders = container.find_all(class_=holder_tag[1:])
                else:
                    # Es una etiqueta
                    holders = container.find_all(holder_tag)
            
            logger.debug(f"Encontrados {len(holders)} elementos con selector: {holder_tag}")
            
            # Si no se encontraron holders con el método tradicional,
            # intentar buscar en atributos (para frameworks modernos como Vue/Astro/React)
            if len(holders) == 0:
                logger.debug("No se encontraron holders tradicionales, buscando en atributos...")
                
                # Buscar elementos con atributo 'title' o 'data-title'
                # Esto es común en componentes de frameworks modernos
                elements_with_title = container.find_all(attrs={'title': True})
                
                if elements_with_title:
                    logger.debug(f"Encontrados {len(elements_with_title)} elementos con atributo 'title'")
                    
                    for element in elements_with_title:
                        # Limitar durante la extracción
                        if len(headlines) >= MAX_HEADLINES_PER_SOURCE:
                            logger.debug(f"Alcanzado el límite de {MAX_HEADLINES_PER_SOURCE} titulares en atributos")
                            break
                        
                        title = element.get('title', '').strip()
                        
                        if not title or len(title) < 10:  # Filtrar títulos muy cortos
                            continue
                        
                        # Limpiar título y convertir a mayúsculas
                        title = self._clean_text(title).upper()
                        
                        headlines.append({
                            "title": title,
                            "data": ""
                        })
                    
                    logger.info(f"Extraídos {len(headlines)} titulares de atributos")
                    return headlines
            
            # Procesamiento tradicional de holders
            for holder in holders:
                # Limitar durante la extracción
                if len(headlines) >= MAX_HEADLINES_PER_SOURCE:
                    logger.debug(f"Alcanzado el límite de {MAX_HEADLINES_PER_SOURCE} titulares")
                    break
                
                # Extraer título
                title = holder.get_text(strip=True)
                
                if not title:
                    continue
                
                # Limpiar título y convertir a mayúsculas
                title = self._clean_text(title).upper()
                
                # Extraer datos adicionales si se especificó
                extra_data = ""
                if data_class:
                    data_element = None
                    
                    if self._is_css_selector(data_class):
                        # Selector CSS complejo
                        data_elements = holder.select(data_class)
                        data_element = data_elements[0] if data_elements else None
                    else:
                        # Método antiguo
                        data_element = holder.find(class_=data_class)
                    
                    if data_element:
                        extra_data = self._clean_text(data_element.get_text(strip=True))
                
                headlines.append({
                    "title": title,
                    "data": extra_data
                })
            
            logger.info(f"Extraídos {len(headlines)} titulares")
            
        except Exception as e:
            logger.error(f"Error parseando HTML: {e}")
        
        
        # Aplicar límite final de MAX_HEADLINES_PER_SOURCE
        limited_headlines = headlines[:MAX_HEADLINES_PER_SOURCE]
        
        if len(headlines) > MAX_HEADLINES_PER_SOURCE:
            logger.info(f"Limitando de {len(headlines)} a {MAX_HEADLINES_PER_SOURCE} titulares")
        else:
            logger.info(f"Extraídos {len(limited_headlines)} titulares (dentro del límite)")
        
        return limited_headlines
    
    async def _check_duplicate(self, content_hash: str) -> bool:
        """
        Verifica si un titular ya existe (por hash).
        
        Args:
            content_hash: Hash del contenido
        
        Returns:
            bool: True si es duplicado, False si es nuevo
        """
        # Primero verificar en caché si está disponible
        if self.redis and self.redis.enabled:
            cache_key = f"headline:hash:{content_hash}"
            exists = await self.redis.exists(cache_key)
            if exists:
                return True
        
        # Verificar en base de datos
        stmt = select(Headline).where(Headline.content_hash == content_hash).limit(1)
        result = await self.db.execute(stmt)
        headline = result.scalar_one_or_none()
        
        is_duplicate = headline is not None
        
        # Cachear el resultado
        if self.redis and self.redis.enabled and not is_duplicate:
            cache_key = f"headline:hash:{content_hash}"
            await self.redis.set(cache_key, True, ttl=86400)  # 24 horas
        
        return is_duplicate
    
    async def scrape_source(
        self,
        source: NewsSource,
        save_to_db: bool = True
    ) -> Tuple[List[Headline], ScrapeLog]:
        """
        Scrapea una fuente específica.
        
        Args:
            source: Objeto NewsSource a scrapear
            save_to_db: Si se deben guardar los titulares en BD
        
        Returns:
            Tuple[List[Headline], ScrapeLog]: Titulares extraídos y log
        """
        logger.info(f"Iniciando scraping de fuente: {source.name}")
        
        # Crear log
        log = ScrapeLog(
            source_id=source.id,
            status=StatusEnum.RUNNING,
            started_at=datetime.utcnow()
        )
        
        headlines_new = []
        
        try:
            # Descargar HTML usando el método apropiado
            if source.requires_js:
                html = await self._fetch_html_playwright(source.url)
            else:
                html = await self._fetch_html(source.url)
            
            if not html:
                log.status = StatusEnum.FAILED
                log.error_message = "No se pudo descargar el HTML"
                log.completed_at = datetime.utcnow()
                if save_to_db:
                    self.db.add(log)
                    await self.db.commit()
                return headlines_new, log
            
            # Parsear titulares
            parsed = self._parse_headlines(
                html,
                source.container,
                source.holder,
                source.data_field
            )
            
            log.headlines_found = len(parsed)
            
            # Procesar cada titular
            for item in parsed:
                title = item["title"]
                content_hash = self._calculate_hash(title)
                
                # Verificar duplicados
                is_duplicate = await self._check_duplicate(content_hash)
                
                if is_duplicate:
                    logger.debug(f"Titular duplicado, omitiendo: {title[:50]}...")
                    continue
                
                # Crear nuevo titular
                headline = Headline(
                    title=title,
                    category=source.category,
                    extracted_data=item.get("data", ""),
                    source_id=source.id,
                    content_hash=content_hash,
                    created_at=datetime.utcnow()
                )
                
                headlines_new.append(headline)
                
                if save_to_db:
                    self.db.add(headline)
            
            # Actualizar log
            log.headlines_new = len(headlines_new)
            log.status = StatusEnum.COMPLETED
            log.completed_at = datetime.utcnow()
            log.duration_seconds = int((log.completed_at - log.started_at).total_seconds())
            
            # Actualizar fuente
            source.last_scraped_at = datetime.utcnow()
            source.scrape_count += 1
            
            logger.info(
                f"Scraping completado: {source.name} - "
                f"{log.headlines_found} encontrados, {log.headlines_new} nuevos"
            )
            
        except Exception as e:
            logger.error(f"Error scrapeando {source.name}: {e}")
            log.status = StatusEnum.FAILED
            log.error_message = str(e)
            log.completed_at = datetime.utcnow()
            source.error_count += 1
        
        if save_to_db:
            self.db.add(log)
            await self.db.commit()
            await self.db.refresh(source)
        
        return headlines_new, log
    
    async def scrape_all(self, active_only: bool = True) -> Dict[str, any]:
        """
        Scrapea todas las fuentes configuradas.
        
        Args:
            active_only: Si solo scrapear fuentes activas
        
        Returns:
            Dict: Estadísticas del scraping
        """
        logger.info("Iniciando scraping de todas las fuentes")
        
        # Obtener fuentes
        stmt = select(NewsSource)
        if active_only:
            stmt = stmt.where(NewsSource.is_active == True)
        
        result = await self.db.execute(stmt)
        sources = result.scalars().all()
        
        if not sources:
            logger.warning("No hay fuentes configuradas para scrapear")
            return {
                "sources_scraped": 0,
                "headlines_found": 0,
                "headlines_new": 0,
                "errors": 0
            }
        
        stats = {
            "sources_scraped": len(sources),
            "headlines_found": 0,
            "headlines_new": 0,
            "errors": 0
        }
        
        # Scrapear cada fuente
        for source in sources:
            headlines, log = await self.scrape_source(source, save_to_db=True)
            
            stats["headlines_found"] += log.headlines_found
            stats["headlines_new"] += log.headlines_new
            
            if log.status == StatusEnum.FAILED:
                stats["errors"] += 1
        
        logger.info(f"Scraping completado: {stats}")
        return stats
