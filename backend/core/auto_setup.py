"""
Utilidades para configuración automática de dependencias.
"""

import os
import sys
import subprocess
from pathlib import Path


def install_playwright_browsers():
    """
    Instala los navegadores de Playwright automáticamente.
    
    Returns:
        bool: True si la instalación fue exitosa
    """
    try:
        print("=" * 60)
        print("🔧 Instalando Playwright (requerido)...")
        print("=" * 60)
        print()
        print("Descargando navegador Chromium (~150MB)...")
        print("Esto puede tomar unos minutos...")
        print()
        
        # Ejecutar playwright install chromium - mostrar output en tiempo real
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            timeout=600  # 10 minutos máximo
        )
        
        if result.returncode == 0:
            print()
            print("=" * 60)
            print("✅ Playwright instalado correctamente")
            print("=" * 60)
            print()
            return True
        else:
            print()
            print("⚠️ Error instalando Playwright")
            print("La aplicación funcionará con scraping básico")
            print()
            return False
            
    except subprocess.TimeoutExpired:
        print("⏱️ Timeout instalando Playwright")
        return False
    except Exception as e:
        print(f"⚠️ Error: {e}")
        return False


async def setup_dependencies():
    """
    Configura dependencias en el primer arranque.
    Solo crea el directorio de datos, NO instala Playwright automáticamente.
    """
    if os.name == 'nt':  # Windows
        app_data = Path(os.getenv('APPDATA')) / 'NewsScraper'
    else:
        app_data = Path.home() / '.newsscraper'
    
    setup_marker = app_data / '.setup_complete'
    app_data.mkdir(parents=True, exist_ok=True)
    
    # Si ya se ejecutó, saltar
    if setup_marker.exists():
        return True
    
    # Solo marcar como completado, sin instalar Playwright
    # El usuario debe instalar Playwright manualmente: playwright install chromium
    setup_marker.touch()
    
    return True
