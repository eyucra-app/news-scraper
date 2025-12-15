"""
Script de inicio para News Scraper Backend.
Prepara el entorno e inicia el servidor FastAPI.
"""

import os
import sys
import webbrowser
import time
from pathlib import Path

# Configurar paths
ROOT_DIR = Path(__file__).parent
BACKEND_DIR = ROOT_DIR / "backend"
VENV_PYTHON = BACKEND_DIR / "venv" / "Scripts" / "python.exe"

# Banner
print("\n" + "=" * 70)
print("🚀 NEWS SCRAPER - Iniciando Backend")
print("=" * 70)

# Verificar que existe el venv
if not VENV_PYTHON.exists():
    print("\n❌ Error: No se encontró el entorno virtual")
    print(f"Expected: {VENV_PYTHON}")
    print("\nEjecuta primero:")
    print("  cd backend")
    print("  python -m venv venv")
    print("  venv\\Scripts\\pip install -r requirements.txt")
    sys.exit(1)

print("\n✅ Entorno virtual encontrado")
print(f"📁 Directorio: {BACKEND_DIR}")

# Cambiar al directorio backend
os.chdir(BACKEND_DIR)
print(f"✅ Cambiado a directorio: {os.getcwd()}")

# Configurar PYTHONPATH
sys.path.insert(0, str(BACKEND_DIR))
os.environ['PYTHONPATH'] = str(BACKEND_DIR)

print("\n" + "=" * 70)
print("📡 INFORMACIÓN DEL SERVIDOR")
print("=" * 70)
print("\n  🌐 URL Base:    http://localhost:8000")
print("  📚 API Docs:    http://localhost:8000/docs")
print("  💚 Health:      http://localhost:8000/health")
print("  🔍 ReDoc:       http://localhost:8000/redoc")

print("\n" + "=" * 70)
print("⏳ Iniciando servidor...")
print("=" * 70)
print("\n💡 Tip: El navegador se abrirá automáticamente con la documentación")
print("💡 Presiona Ctrl+C para detener el servidor\n")

# Esperar un momento antes de iniciar
time.sleep(2)

# Importar e iniciar uvicorn
try:
    import uvicorn
    
    # Abrir navegador después de 3 segundos
    def open_browser():
        time.sleep(3)
        webbrowser.open('http://localhost:8000/docs')
    
    import threading
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Iniciar servidor
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
    
except KeyboardInterrupt:
    print("\n\n" + "=" * 70)
    print("✅ Servidor detenido correctamente")
    print("=" * 70)
    
except ModuleNotFoundError as e:
    print(f"\n❌ Error: Módulo no encontrado - {e}")
    print("\nAsegúrate de haber instalado todas las dependencias:")
    print("  cd backend")
    print("  venv\\Scripts\\pip install -r requirements.txt")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ Error inesperado: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
