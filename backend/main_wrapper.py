"""
Wrapper para ejecutar native_app con el working directory correcto
"""
import os
import sys
from pathlib import Path
import traceback
from datetime import datetime

# Crear archivo de log para debugging
log_file = Path.home() / "news_scraper_debug.log"

def log(message):
    """Escribir mensaje al log"""
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")
            f.flush()
    except:
        pass


log("="*60)
log("INICIO DEL WRAPPER")
log(f"Python version: {sys.version}")
log(f"Frozen: {getattr(sys, 'frozen', False)}")
log(f"Executable: {sys.executable}")

try:
    # Configurar working directory al directorio del ejecutable
    if getattr(sys, 'frozen', False):
        # Ejecutando como ejecutable de PyInstaller
        application_path = Path(sys.executable).parent
        log(f"Modo: PyInstaller frozen")
        log(f"Application path: {application_path}")
    else:
        # Ejecutando como script Python
        application_path = Path(__file__).parent
        log(f"Modo: Python script")
        log(f"Application path: {application_path}")

    log(f"Cambiando a directorio: {application_path}")
    os.chdir(application_path)
    log(f"Working directory actual: {os.getcwd()}")
    
    # Listar archivos en el directorio
    log("Archivos en directorio:")
    for item in os.listdir(application_path):
        log(f"  - {item}")
    
    # Intentar importar native_app
    log("Intentando importar native_app...")
    import native_app
    log("✓ native_app importado correctamente")
    
    # Ejecutar main
    log("Ejecutando native_app.main()...")
    native_app.main()
    log("✓ native_app.main() completado")
    
except Exception as e:
    log(f"ERROR FATAL: {type(e).__name__}: {e}")
    log("Traceback completo:")
    log(traceback.format_exc())
    
finally:
    log("FIN DEL WRAPPER")
    log("="*60)
