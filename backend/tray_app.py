"""
News Scraper - Aplicación de bandeja del sistema multi-plataforma.

Ejecuta el backend FastAPI y proporciona un icono en la bandeja del sistema
para controlar la aplicación.
"""

import os
import sys
import platform
import threading
import webbrowser
import time
from pathlib import Path
import uvicorn
import pystray
from PIL import Image, ImageDraw


class NewsScraperTrayApp:
    """Aplicación de bandeja del sistema para News Scraper."""
    
    def __init__(self):
        self.icon = None
        self.server_thread = None
        self.server_running = False
        self.os_name = platform.system()
        
    def create_icon_image(self):
        """Crea un icono simple para la bandeja del sistema."""
        # Crear imagen de 64x64
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Dibujar un círculo azul con "N" en el centro
        draw.ellipse([4, 4, 60, 60], fill='#4A90E2', outline='#2E5C8A')
        
        # Dibujar "N" (aproximado)
        draw.text((20, 15), "N", fill='white')
        
        return image
    
    def run_server(self):
        """Inicia el servidor FastAPI."""
        try:
            self.server_running = True
            print("🚀 Iniciando servidor News Scraper...")
            
            # Cambiar al directorio del backend
            backend_dir = Path(__file__).parent
            os.chdir(backend_dir)
            
            # Configurar uvicorn
            uvicorn.run(
                "app:app",
                host="0.0.0.0",
                port=8000,
                log_level="info",
                access_log=True
            )
        except Exception as e:
            print(f"❌ Error al iniciar servidor: {e}")
            self.server_running = False
    
    def start_server(self):
        """Inicia el servidor en un thread separado."""
        if not self.server_running:
            self.server_thread = threading.Thread(target=self.run_server, daemon=True)
            self.server_thread.start()
            time.sleep(2)  # Esperar a que el servidor inicie
            print("✓ Servidor iniciado")
    
    def open_app(self, icon=None, item=None):
        """Abre la aplicación en el navegador."""
        print("Abriendo aplicacion en el navegador...")
        webbrowser.open("http://localhost:8000")
    
    def open_local_docs(self, icon=None, item=None):
        """Abre la documentación de la API local."""
        if self.server_running:
            webbrowser.open("http://localhost:8000/docs")
        else:
            print("⚠ El servidor no está corriendo")
    
    def setup_autostart(self, icon=None, item=None):
        """Configura el auto-inicio según el sistema operativo."""
        try:
            if self.os_name == "Windows":
                self._setup_autostart_windows()
            elif self.os_name == "Darwin":  # macOS
                self._setup_autostart_macos()
            else:  # Linux
                self._setup_autostart_linux()
            
            print("✓ Auto-inicio configurado")
        except Exception as e:
            print(f"❌ Error al configurar auto-inicio: {e}")
    
    def _setup_autostart_windows(self):
        """Configura auto-inicio en Windows."""
        import winreg
        
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "NewsScraper"
        app_path = sys.executable
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, app_path)
            winreg.CloseKey(key)
        except Exception as e:
            raise Exception(f"No se pudo configurar auto-inicio en Windows: {e}")
    
    def _setup_autostart_macos(self):
        """Configura auto-inicio en macOS."""
        import plistlib
        
        plist_path = Path.home() / "Library" / "LaunchAgents" / "com.newsscraper.plist"
        
        plist_content = {
            "Label": "com.newsscraper",
            "ProgramArguments": [sys.executable],
            "RunAtLoad": True,
            "KeepAlive": False
        }
        
        plist_path.parent.mkdir(parents=True, exist_ok=True)
        with open(plist_path, 'wb') as f:
            plistlib.dump(plist_content, f)
    
    def _setup_autostart_linux(self):
        """Configura auto-inicio en Linux."""
        autostart_dir = Path.home() / ".config" / "autostart"
        autostart_dir.mkdir(parents=True, exist_ok=True)
        
        desktop_file = autostart_dir / "newsscraper.desktop"
        
        content = f"""[Desktop Entry]
Type=Application
Name=News Scraper
Exec={sys.executable}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
"""
        
        with open(desktop_file, 'w') as f:
            f.write(content)
        
        # Hacer ejecutable
        os.chmod(desktop_file, 0o755)
    
    def quit_app(self, icon=None, item=None):
        """Cierra la aplicación."""
        print("👋 Cerrando News Scraper...")
        if self.icon:
            self.icon.stop()
        sys.exit(0)
    
    def run(self):
        """Ejecuta la aplicación de bandeja del sistema."""
        # Iniciar servidor
        self.start_server()
        
        # Abrir navegador automáticamente al inicio
        time.sleep(1)
        self.open_app()
        
        # Crear menú
        menu = pystray.Menu(
            pystray.MenuItem("🌐 Abrir Aplicación", self.open_app, default=True),
            pystray.MenuItem("📚 Documentación API", self.open_local_docs),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("⚙️ Configurar Auto-inicio", self.setup_autostart),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("❌ Salir", self.quit_app)
        )
        
        # Crear icono
        image = self.create_icon_image()
        self.icon = pystray.Icon(
            "newsscraper",
            image,
            "News Scraper",
            menu
        )
        
        # Ejecutar
        print("✓ News Scraper ejecutándose en la bandeja del sistema")
        print(f"📍 Sistema operativo: {self.os_name}")
        print(f"🌐 Aplicación: http://localhost:8000")
        print(f"🔧 API Backend: http://localhost:8000/api")
        print(f"📚 Documentación: http://localhost:8000/docs")
        
        self.icon.run()


def main():
    """Punto de entrada principal."""
    print("=" * 60)
    print("📰 News Scraper - Sistema de Extracción de Noticias")
    print("=" * 60)
    
    app = NewsScraperTrayApp()
    app.run()


if __name__ == "__main__":
    main()
