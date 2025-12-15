"""
Demo del Motor de Scraping - News Scraper
Prueba las funcionalidades principales sin necesidad de servidor completo.
"""

import asyncio
from datetime import datetime
from bs4 import BeautifulSoup
import hashlib


class SimpleScraper:
    """Motor de scraping simplificado para demostración."""
    
    @staticmethod
    def calculate_hash(text: str) -> str:
        """Calcula hash MD5 para deduplicación."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Limpia texto eliminando espacios extra."""
        return ' '.join(text.split()).strip()
    
    def parse_headlines(self, html: str, container_class: str, holder_tag: str):
        """
        Parsea HTML y extrae titulares.
        
        Args:
            html: HTML a parsear
            container_class: Clase CSS del contenedor
            holder_tag: Etiqueta HTML de los títulos
        
        Returns:
            Lista de titulares extraídos
        """
        soup = BeautifulSoup(html, 'html.parser')
        headlines = []
        
        try:
            # Buscar contenedor
            container = soup.find(class_=container_class)
            
            if not container:
                print(f"❌ No se encontró contenedor: {container_class}")
                return headlines
            
            print(f"✓ Contenedor encontrado: {container_class}")
            
            # Buscar holders
            holders = container.find_all(holder_tag)
            print(f"✓ Encontrados {len(holders)} elementos con tag: {holder_tag}")
            
            for holder in holders:
                title = holder.get_text(strip=True)
                if not title:
                    continue
                
                title = self.clean_text(title)
                content_hash = self.calculate_hash(title)
                
                headlines.append({
                    "title": title,
                    "hash": content_hash[:8],  # Primeros 8 caracteres
                    "length": len(title)
                })
            
            print(f"✓ Extraídos {len(headlines)} titulares\n")
            
        except Exception as e:
            print(f"❌ Error parseando HTML: {e}")
        
        return headlines


# HTML de ejemplo simulado de un sitio de noticias
SAMPLE_HTML = """
<html>
<head><title>Noticias de Ejemplo</title></head>
<body>
    <div class="news-container">
        <h2>Primera noticia importante del día de hoy</h2>
        <h2>Segunda noticia sobre tecnología y avances</h2>
        <h2>Tercera noticia relacionada con deportes</h2>
        <h2>Cuarta noticia de última hora internacional</h2>
        <h2>Quinta noticia sobre economía global</h2>
    </div>
</body>
</html>
"""


def main():
    """Función principal de demostración."""
    print("=" * 70)
    print("DEMO: Motor de Scraping de Noticias - News Scraper")
    print("=" * 70)
    print()
    
    # Crear scraper
    scraper = SimpleScraper()
    
    print("📰 PRUEBA 1: Parsing de HTML\n")
    print("Configuración:")
    print("  - Contenedor: 'news-container'")
    print("  - Holder: 'h2'\n")
    
    # Parsear titulares
    headlines = scraper.parse_headlines(
        SAMPLE_HTML,
        "news-container",
        "h2"
    )
    
    # Mostrar resultados
    print("📋 TITULARES EXTRAÍDOS:")
    print("-" * 70)
    for i, headline in enumerate(headlines, 1):
        print(f"\n{i}. {headline['title']}")
        print(f"   Hash: {headline['hash']}  |  Longitud: {headline['length']} caracteres")
    
    print("\n" + "=" * 70)
    print("✅ FUNCIONALIDADES DEMOSTRADAS:")
    print("=" * 70)
    print("✓ Parsing de HTML con BeautifulSoup4")
    print("✓ Extracción de titulares por contenedor y holder")
    print("✓ Limpieza de texto")
    print("✓ Cálculo de hash para deduplicación")
    print("✓ Contador de titulares")
    
    print("\n" + "=" * 70)
    print("📊 ESTADÍSTICAS:")
    print("=" * 70)
    print(f"Total de titulares encontrados: {len(headlines)}")
    print(f"Promedio de longitud: {sum(h['length'] for h in headlines) // len(headlines)} caracteres")
    
    print("\n" + "=" * 70)
    print("🔍 CARACTERÍSTICAS DEL SISTEMA COMPLETO:")
    print("=" * 70)
    print("""
    Backend Implementado:
    ✓ Motor de scraping asíncrono con aiohttp
    ✓ Base de datos SQLAlchemy (PostgreSQL/SQLite)
    ✓ Cliente de Singular.live API con retry logic
    ✓ Scheduler automático con APScheduler
    ✓ API REST completa con FastAPI
    ✓ Sistema de caché con Redis
    ✓ Deduplicación automática por hash
    ✓ Manejo robusto de errores
    ✓ Logging estructurado
    ✓ Docker Compose para deployment
    
    Endpoints API:
    • GET  /api/sources/          - Listar fuentes
    • POST /api/sources/          - Crear fuente
    • POST /api/sources/{id}/test - Testear fuente
    • POST /api/scraping/start    - Scraping manual
    • GET  /api/headlines/        - Ver titulares
    • POST /api/headlines/send    - Enviar a Singular.live
    • GET  /api/config/           - Configuración
    """)
    
    print("\n" + "=" * 70)
    print("📚 DOCUMENTACIÓN CREADA:")
    print("=" * 70)
    print("""
    ✓ docs/INSTALLATION.md     - Guía de instalación
    ✓ docs/USER_GUIDE.md       - Manual de usuario
    ✓ docs/API_DOCUMENTATION.md - Documentación de API
    ✓ docs/MAINTENANCE.md      - Guía de mantenimiento
    ✓ README.md                - Documentación principal
    ✓ QUICKSTART.md            - Inicio rápido
    """)
    
    print("\n" + "=" * 70)
    print("🎯 PRÓXIMOS PASOS:")
    print("=" * 70)
    print("""
    1. Configurar credenciales reales de Singular.live en .env
    2. Instalar PostgreSQL y Redis (o usar Docker)
    3. Ejecutar: docker-compose up -d
    4. Acceder a: http://localhost:8000/docs
    5. Agregar fuentes de noticias reales
    6. Iniciar scraping automático
    """)
    
    print("\n" + "=" * 70)
    print("✨ DEMO COMPLETADA EXITOSAMENTE")
    print("=" * 70)


if __name__ == "__main__":
    main()
