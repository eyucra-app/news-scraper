"""
News Scraper - Aplicación con ventana nativa.

Características:
- Consola visible solo durante arranque
- Ventana nativa con pywebview
- Minimizar oculta de taskbar y envía a bandeja
- Auto-instalación de Playwright
"""

import os
import sys
import platform
import threading
import time
from pathlib import Path
import uvicorn
import pystray
import webview
from PIL import Image, ImageDraw

import logging
from pathlib import Path

# Configurar UTF-8 y logging solo si hay consola  
if platform.system() == "Windows":
    try:
        import io
        # Solo reconfigurar si hay un buffer (consola existe)
        if hasattr(sys.stdout, 'buffer') and sys.stdout.buffer is not None:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        # En builds sin consola, esto fallará - está bien
        pass

# Configurar logging a archivo
log_file = Path.home() / "news_scraper.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
    ]
)
logger = logging.getLogger('news_scraper')


# Función para ocultar consola en Windows
def hide_console():
    """Oculta la ventana de consola (solo Windows).
    Safe para builds con console=False."""
    if platform.system() == "Windows":
        try:
            import ctypes
            console_window = ctypes.windll.kernel32.GetConsoleWindow()
            # Solo ocultar si realmente hay una consola
            if console_window != 0:
                ctypes.windll.user32.ShowWindow(console_window, 0)
        except Exception as e:
            # Silenciar errores - normal en builds sin consola
            pass


def safe_print(*args, **kwargs):
    """Print que usa logging en vez de stdout"""
    message = ' '.join(str(arg) for arg in args)
    logger.info(message)
    # También intentar print si hay consola
    try:
        print(*args, **kwargs)
    except:
        pass


class NativeAPI:
    """API JavaScript para el frontend - permite usar diálogos nativos"""
    
    def save_file_dialog(self, default_filename, file_content):
        """Mostrar diálogo para guardar archivo"""
        try:
            result = webview.windows[0].create_file_dialog(
                webview.SAVE_DIALOG,
                save_filename=default_filename,
                file_types=('JSON Files (*.json)', 'All Files (*.*)')
            )
            
            if result:
                save_path = result[0] if isinstance(result, tuple) else result
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(file_content)
                logger.info(f"Archivo guardado en: {save_path}")
                return {'success': True, 'path': save_path}
            else:
                return {'success': False, 'cancelled': True}
        except Exception as e:
            logger.error(f"Error guardando archivo: {e}")
            return {'success': False, 'error': str(e)}
    
    def open_file_dialog(self):
        """Mostrar diálogo para abrir archivo"""
        try:
            result = webview.windows[0].create_file_dialog(
                webview.OPEN_DIALOG,
                file_types=('JSON Files (*.json)', 'All Files (*.*)')
            )
            
            if result:
                file_path = result[0] if isinstance(result, tuple) else result
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                logger.info(f"Archivo abierto desde: {file_path}")
                return {'success': True, 'content': content, 'path': file_path}
            else:
                return {'success': False, 'cancelled': True}
        except Exception as e:
            logger.error(f"Error abriendo archivo: {e}")
            return {'success': False, 'error': str(e)}


class NewsScraperApp:
    """Aplicación con ventana nativa."""
    
    def __init__(self):
        self.icon = None
        self.window = None
        self.server_thread = None
        self.server_running = False
        self.backend_ready = False
        self.os_name = platform.system()
        self.window_visible = True
        
    def create_icon_image(self):
        """Crea icono para la bandeja."""
        icon_path = Path(__file__).parent.parent / "icon.png"
        if icon_path.exists():
            try:
                return Image.open(icon_path)
            except:
                pass
        
        # Icono por defecto
        image = Image.new('RGB', (64, 64), color='white')
        draw = ImageDraw.Draw(image)
        draw.ellipse([4, 4, 60, 60], fill='#4A90E2', outline='#2E5C8A')
        draw.text((20, 15), "N", fill='white')
        return image
    
    def run_server(self):
        """Inicia el servidor FastAPI."""
        try:
            safe_print("🚀 Iniciando servidor...")
            
            backend_dir = Path(__file__).parent
            os.chdir(backend_dir)
            
            self.server_running = True
            
            # Configurar logging de uvicorn para usar archivo
            log_config = {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "default": {
                        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    },
                },
                "handlers": {
                    "file": {
                        "formatter": "default",
                        "class": "logging.FileHandler",
                        "filename": str(log_file),
                        "encoding": "utf-8",
                    },
                },
                "loggers": {
                    "uvicorn": {"handlers": ["file"], "level": "INFO"},
                    "uvicorn.error": {"handlers": ["file"], "level": "INFO"},
                    "uvicorn.access": {"handlers": ["file"], "level": "INFO"},
                },
            }
            
            # Iniciar uvicorn
            uvicorn.run(
                "app:app",
                host="127.0.0.1",
                port=8000,
                log_config=log_config,
                access_log=False
            )
        except Exception as e:
            safe_print(f"❌ Error: {e}")
            # No usar input() en producción sin consola
            self.server_running = False
    
    def check_backend_ready(self):
        """Verifica si el backend está listo."""
        import requests
        max_attempts = 30
        for i in range(max_attempts):
            try:
                response = requests.get("http://localhost:8000/health", timeout=1)
                if response.status_code == 200:
                    safe_print("✅ Backend listo")
                    self.backend_ready = True
                    return True
            except:
                pass
            time.sleep(0.5)
        return False
    
    def start_server(self):
        """Inicia servidor y espera que esté listo."""
        self.server_thread = threading.Thread(target=self.run_server, daemon=True)
        self.server_thread.start()
        
        # Solo mostrar mensajes si hay consola visible
        try:
            safe_print("⏳ Esperando backend...")
        except:
            pass
            
        if self.check_backend_ready():
            try:
                safe_print("✅ Backend listo")
                # Intentar ocultar consola si existe
                hide_console()
            except:
                pass
            return True
        else:
            return False
    
    def on_closing(self):
        """Maneja el evento de cerrar ventana - minimiza a bandeja en lugar de cerrar."""
        # En lugar de cerrar, ocultar la ventana
        if self.window:
            self.window.hide()
            self.window_visible = False
        return True  # Retornar True previene el cierre
    
    def on_minimized(self):
        """Cuando se minimiza, ocultar de taskbar."""
        if self.window:
            self.window.hide()
            self.window_visible = False
    
    def create_window(self):
        """Crea ventana nativa."""
        try:
            # Crear instancia de la API nativa
            native_api = NativeAPI()
            
            self.window = webview.create_window(
                'News Scraper',
                'http://localhost:8000',
                width=1200,
                height=800,
                resizable=True,
                fullscreen=False,
                min_size=(800, 600),
                on_top=False,
                confirm_close=False,
                js_api=native_api  # Exponer API al JavaScript
            )
            
            # Configurar eventos DESPUÉS de crear la ventana
            self.window.events.closing += self.on_closing
            self.window.events.minimized += self.on_minimized
            
            self.window_visible = True
            return True
        except Exception as e:
            safe_print(f"Error creando ventana: {e}")
            return False
    
    def show_window(self, icon=None, item=None):
        """Muestra la ventana."""
        if self.window:
            try:
                self.window.show()
                self.window_visible = True
            except Exception as e:
                safe_print(f"Error mostrando ventana: {e}")
    
    def open_docs(self, icon=None, item=None):
        """Abre documentación."""
        import webbrowser
        webbrowser.open("http://localhost:8000/docs")
    
    def setup_autostart(self, icon=None, item=None):
        """Configura auto-inicio."""
        try:
            if self.os_name == "Windows":
                import winreg
                key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, "NewsScraper", 0, winreg.REG_SZ, sys.executable)
                winreg.CloseKey(key)
                safe_print("✓ Auto-inicio configurado")
        except Exception as e:
            safe_print(f"Error: {e}")
    
    def quit_app(self, icon=None, item=None):
        """Cierra la aplicación completamente."""
        if self.icon:
            self.icon.stop()
        if self.window:
            try:
                self.window.destroy()
            except:
                pass
        sys.exit(0)
    
    def run(self):
        """Ejecuta la aplicación."""
        safe_print("=" * 60)
        safe_print("📰 News Scraper")
        safe_print("=" * 60)
        safe_print()
        
        # Iniciar servidor y esperar
        if not self.start_server():
            sys.exit(1)
        
        # Crear ventana nativa
        safe_print("🪟 Creando ventana...")
        if not self.create_window():
            safe_print("Error creando ventana")
            sys.exit(1)
        
        # Crear menú de bandeja
        menu = pystray.Menu(
            pystray.MenuItem("Mostrar News Scraper", self.show_window, default=True),
            pystray.MenuItem("Documentación", self.open_docs),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Auto-inicio", self.setup_autostart),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Salir", self.quit_app)
        )
        
        # Crear icono de bandeja en thread
        image = self.create_icon_image()
        self.icon = pystray.Icon("newsscraper", image, "News Scraper", menu)
        threading.Thread(target=self.icon.run, daemon=True).start()
        
        # Iniciar webview en hilo principal
        safe_print("✅ Aplicación lista")
        safe_print()
        webview.start()


def main():
    try:
        app = NewsScraperApp()
        app.run()
    except Exception as e:
        import traceback
        print("=" * 60)
        print("ERROR FATAL:")
        print("=" * 60)
        print(f"Tipo: {type(e).__name__}")
        print(f"Mensaje: {e}")
        print("\nTraceback completo:")
        traceback.print_exc()
        print("=" * 60)
        input("\nPresiona Enter para cerrar...")
        sys.exit(1)


if __name__ == "__main__":
    main()

