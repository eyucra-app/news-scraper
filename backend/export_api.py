"""
API JavaScript para pywebview - Permite diálogos nativos desde el frontend
"""
import os
import json
from pathlib import Path
from datetime import datetime


class ExportAPI:
    """API para operaciones de exportación con diálogos nativos"""
    
    def __init__(self, window=None):
        self.window = window
        
    def export_sources_to_file(self, sources_json):
        """Exportar fuentes a archivo con diálogo de guardado"""
        try:
            import webview
            
            # Generar nombre de archivo con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"news_sources_backup_{timestamp}.json"
            
            # Mostrar diálogo de guardado
            result = webview.windows[0].create_file_dialog(
                webview.SAVE_DIALOG,
                save_filename=default_filename,
                file_types=('JSON Files (*.json)', 'All Files (*.*)')
            )
            
            if result:
                # Guardar archivo
                save_path = result[0] if isinstance(result, tuple) else result
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(sources_json)
                return {'success': True, 'path': save_path}
            else:
                return {'success': False, 'cancelled': True}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def export_config_to_file(self, config_json):
        """Exportar configuración a archivo con diálogo de guardado"""
        try:
            import webview
            
            # Generar nombre de archivo con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"app_config_backup_{timestamp}.json"
            
            # Mostrar diálogo de guardado
            result = webview.windows[0].create_file_dialog(
                webview.SAVE_DIALOG,
                save_filename=default_filename,
                file_types=('JSON Files (*.json)', 'All Files (*.*)')
            )
            
            if result:
                # Guardar archivo
                save_path = result[0] if isinstance(result, tuple) else result
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(config_json)
                return {'success': True, 'path': save_path}
            else:
                return {'success': False, 'cancelled': True}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def select_import_file(self):
        """Abrir diálogo para seleccionar archivo a importar"""
        try:
            import webview
            
            result = webview.windows[0].create_file_dialog(
                webview.OPEN_DIALOG,
                file_types=('JSON Files (*.json)', 'All Files (*.*)')
            )
            
            if result:
                file_path = result[0] if isinstance(result, tuple) else result
                # Leer contenido del archivo
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {'success': True, 'content': content, 'path': file_path}
            else:
                return {'success': False, 'cancelled': True}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
