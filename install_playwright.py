"""
Script de instalación post-install para Playwright.

Este script se ejecuta como paso del instalador para instalar
Playwright en el sistema del usuario (no en el ejecutable).
"""

import subprocess
import sys

def main():
    print("=" * 60)
    print("Instalando Playwright...")
    print("=" * 60)
    print()
    
    try:
        # Instalar playwright en el sistema
        result = subprocess.run(
            ["playwright", "install", "chromium"],
            capture_output=False,
            timeout=600
        )
        
        if result.returncode == 0:
            print()
            print("✅ Playwright instalado correctamente")
            return 0
        else:
            print("⚠️ Error instalando Playwright")
            return 1
            
    except FileNotFoundError:
        # Si playwright no está en PATH, usar python -m
        try:
            result = subprocess.run(
                [sys.executable, "-m", "playwright", "install", "chromium"],
                capture_output=False,
                timeout=600
            )
            
            if result.returncode == 0:
                print()
                print("✅ Playwright instalado correctamente")
                return 0
        except Exception as e:
            print(f"Error: {e}")
            return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
