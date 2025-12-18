"""
Script de instalación de Playwright que usa el Python del ejecutable.
Este script se ejecuta dentro del contexto del ejecutable PyInstaller.
"""

import subprocess
import sys
import os

def main():
    print("=" * 60)
    print("Instalación de Playwright para News Scraper")
    print("=" * 60)
    print()
    print("Descargando navegador Chromium (~150MB)...")
    print("Esto puede tomar unos minutos...")
    print()
    
    try:
        # Usar el Python del ejecutable
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            capture_output=False,
            timeout=600
        )
        
        if result.returncode == 0:
            print()
            print("=" * 60)
            print("✅ Playwright instalado correctamente")
            print("=" * 60)
            print()
            print("El scraping avanzado con JavaScript ahora está disponible.")
            print()
        else:
            print()
            print("=" * 60)
            print("⚠️ Error en la instalación")
            print("=" * 60)
            print()
            print("La aplicación funcionará con scraping básico HTML.")
            print()
        
        input("Presiona Enter para continuar...")
        return result.returncode
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ Error: {e}")
        print("=" * 60)
        print()
        print("La aplicación funcionará con scraping básico HTML.")
        print()
        input("Presiona Enter para continuar...")
        return 1

if __name__ == "__main__":
    sys.exit(main())
