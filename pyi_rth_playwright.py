"""
Runtime hook para Playwright.
Configura la variable de entorno para que Playwright use los navegadores bundleados.
"""

import os
import sys
from pathlib import Path

# Cuando el ejecutable esté corriendo, configurar PLAYWRIGHT_BROWSERS_PATH
if getattr(sys, 'frozen', False):
    # Estamos en el ejecutable PyInstaller
    base_path = Path(sys._MEIPASS)
    playwright_path = base_path / 'ms-playwright'
    
    if playwright_path.exists():
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(playwright_path)
        print(f"✓ Playwright browsers: {playwright_path}")
