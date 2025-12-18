# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file para News Scraper Backend
Crea un ejecutable Windows standalone con todas las dependencias
"""

import os
import sys
from pathlib import Path

# Obtener el directorio raíz del proyecto
project_root = os.path.abspath('.')
backend_dir = os.path.join(project_root, 'backend')

# Obtener ruta de Playwright browsers
playwright_browsers = Path.home() / 'AppData' / 'Local' / 'ms-playwright'

block_cipher = None

a = Analysis(
    [os.path.join(backend_dir, 'main_wrapper.py')],  # Entry point wrapper
    pathex=[backend_dir],  # Agregar backend al path
    binaries=[],
    datas=[
        (os.path.join(backend_dir, 'app.py'), '.'),  # Incluir app.py en raíz
        (os.path.join(backend_dir, 'db'), 'db'),
        (os.path.join(backend_dir, 'api'), 'api'),
        (os.path.join(backend_dir, 'services'), 'services'),
        (os.path.join(backend_dir, 'core'), 'core'),
        (os.path.join(project_root, 'frontend', 'out'), 'frontend/out'),  # Frontend build
        (os.path.join(project_root, 'icon.png'), '.'),  # Icono
        (os.path.join(project_root, '.env.example'), '.'),
        (os.path.join(project_root, 'setup_playwright.py'), '.'),  # Script de instalación Playwright
        (str(playwright_browsers), 'ms-playwright'),  # Playwright browsers
    ],
    hiddenimports=[
        # Uvicorn y FastAPI
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        # FastAPI
        'fastapi',
        'fastapi.responses',
        'fastapi.routing',
        # Backend modules
        'app',
        'api',
        'api.routes',
        'api.routes.sources',
        'api.routes.scraping',
        'api.routes.headlines',
        'api.routes.config',
        'db',
        'db.database',
        'db.models',
        'services',
        'services.scraper',
        'services.scheduler',
        'core',
        'core.config',
        # Pydantic
        'pydantic',
        'pydantic_settings',
        # SQLAlchemy
        'sqlalchemy',
        'sqlalchemy.ext.asyncio',
        'aiosqlite',
        # Web scraping
        'playwright',
        'beautifulsoup4',
        'bs4',
        'lxml',
        'lxml.etree',
        # Tray
        'pystray',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        # Native window
        'pywebview',
        'webview',
        'webview.window',
        # Scheduler
        'apscheduler',
        'apscheduler.schedulers',
        'apscheduler.schedulers.asyncio',
        # HTTP
        'tenacity',
        'aiohttp',
        'requests',
        # Windows specific  
        'winreg',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[os.path.join(project_root, 'pyi_rth_playwright.py')],
    excludes=[
        'matplotlib',
        'pandas',
        'numpy',
        'scipy',
        'pytest',
        'tkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='NewsScraperBackend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sin consola en producción
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(project_root, 'icon.png'),  # Icono de la app
)
