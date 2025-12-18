"""
Script para construir el ejecutable de News Scraper con PyInstaller
"""

import os
import subprocess
import sys
from pathlib import Path

def install_pyinstaller():
    """Instala PyInstaller si no está disponible"""
    try:
        import PyInstaller
        print("[OK] PyInstaller ya esta instalado")
    except ImportError:
        print("Instalando PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("[OK] PyInstaller instalado")

def build_executable():
    """Construye el ejecutable usando PyInstaller"""
    print("=" * 60)
    print("Construyendo ejecutable de News Scraper Backend")
    print("=" * 60)
    
    # Verificar que estamos en el directorio correcto
    if not Path("backend").exists():
        print("ERROR: No se encuentra el directorio 'backend'")
        print("Ejecuta este script desde el directorio raiz del proyecto")
        return False
    
    # Construir con PyInstaller
    spec_file = "news_scraper.spec"
    
    if not Path(spec_file).exists():
        print(f"ERROR: No se encuentra {spec_file}")
        return False
    
    print(f"\nConstruyendo desde {spec_file}...")
    print("Esto puede tomar varios minutos...\n")
    
    try:
        subprocess.check_call([
            "pyinstaller",
            "--clean",
            "--noconfirm",
            spec_file
        ])
        
        print("\n" + "=" * 60)
        print("[OK] Build exitoso!")
        print("=" * 60)
        print(f"\nEjecutable creado en: dist/NewsScraperBackend.exe")
        print("\nPuedes probarlo ejecutando:")
        print("  dist\\NewsScraperBackend.exe")
        print("\nEl ejecutable incluye:")
        print("  - Backend FastAPI")
        print("  - Base de datos SQLite")
        print("  - Tray icon")
        print("  - Todas las dependencias")
        print("\nAbre automaticamente: https://news-scraper-v1.vercel.app")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\nERROR durante el build: {e}")
        return False

def main():
    """Función principal"""
    # Cambiar al directorio del script
    os.chdir(Path(__file__).parent)
    
    # Instalar PyInstaller si es necesario
    install_pyinstaller()
    
    # Construir ejecutable
    success = build_executable()
    
    if success:
        print("\nTodo listo! El backend esta empaquetado.")
        return 0
    else:
        print("\nEl build fallo. Revisa los errores arriba.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
