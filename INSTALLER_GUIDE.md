# Guía para Crear Instalador con Inno Setup

## Paso 1: Descargar e Instalar Inno Setup

1. Descarga Inno Setup desde: https://jrsoftware.org/isdl.php
2. Descarga la versión más reciente (recomendada: con QuickStart Pack)
3. Ejecuta el instalador y sigue las instrucciones
4. Instala en la ubicación por defecto

## Paso 2: Compilar el Instalador

### Opción A: Desde la GUI de Inno Setup (Más fácil)

1. Abre **Inno Setup Compiler**
2. File → Open → Selecciona `installer.iss`
3. Build → Compile (o presiona F9)
4. Espera ~30 segundos
5. ✅ El instalador se creará en: `installer_output/NewsScraperSetup.exe`

### Opción B: Desde Línea de Comandos

```powershell
# Ubicación típica de Inno Setup
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

## Paso 3: Probar el Instalador

1. Ejecuta `installer_output/NewsScraperSetup.exe`
2. Sigue el wizard de instalación:
   - Acepta ubicación (sugerida: `C:\Program Files\News Scraper`)
   - ✅ Marca "Iniciar automáticamente con Windows" (opcional)
   - ✅ Marca "Crear icono en escritorio" (opcional)
3. Click "Instalar"
4. Al finalizar:
   - ✅ Click "Iniciar News Scraper ahora"
   - ✅ Click "Abrir News Scraper en el navegador"

## Lo que hace el Instalador

### Durante la Instalación

1. ✅ Copia `NewsScraperBackend.exe` a `C:\Program Files\News Scraper\`
2. ✅ Crea acceso directo en Menú Inicio → "News Scraper"
3. ✅ Crea acceso directo en Escritorio (si se seleccionó)
4. ✅ Configura auto-inicio con Windows (si se seleccionó)
5. ✅ Crea entrada en "Programas y características" para desinstalar

### Accesos Directos Creados

**Menú Inicio → News Scraper:**
- **"News Scraper"** → Abre https://news-scraper-v1.vercel.app en navegador
- **"News Scraper Backend"** → Ejecuta el servidor (muestra consola con logs)
- **"Desinstalar News Scraper"** → Desinstala la aplicación

**Escritorio (opcional):**
- **"News Scraper"** → Abre el frontend directamente

### Registro de Windows

Si se seleccionó auto-inicio:
```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
Valor: NewsScraperBackend
Datos: "C:\Program Files\News Scraper\NewsScraperBackend.exe"
```

## Uso para el Usuario Final

### Primera Vez

1. Doble-click en `NewsScraperSetup.exe`
2. Siguiente → Siguiente → Instalar
3. El instalador abre automáticamente:
   - El backend (consola)
   - El navegador con https://news-scraper-v1.vercel.app

### Uso Diario

**Si configuró auto-inicio:**
- ✅ Al encender la PC, el backend inicia automáticamente
- Doble-click en acceso directo "News Scraper" (escritorio o menú)
- El navegador abre el frontend y conecta con el backend local

**Si NO configuró auto-inicio:**
1. Abrir "News Scraper Backend" desde menú inicio (inicia el servidor)
2. Abrir "News Scraper" desde menú inicio o escritorio (abre frontend)

## Desinstalar

1. Panel de Control → Programas y características
2. Buscar "News Scraper"
3. Click derecho → Desinstalar
4. O usar: Menú Inicio → News Scraper → "Desinstalar News Scraper"

✅ Desinstala completamente:
- Ejecutable
- Accesos directos
- Entrada de auto-inicio (si existe)
- Entrada en registro

❌ NO elimina (se preservan):
- `news_scraper.db` (datos del usuario)
- Configuraciones en AppData

## Tamaños Aproximados

- `NewsScraperBackend.exe`: ~150 MB
- `NewsScraperSetup.exe`: ~150 MB (comprimido con LZMA)
- Una vez instalado: ~200 MB (con archivos temporales)

## Personalización Opcional

### Agregar Icono

1. Crea o descarga un ícono `.ico` (256x256 recomendado)
2. Guárdalo como `icon.ico` en el directorio raíz
3. Edita `installer.iss`:
   ```ini
   SetupIconFile=icon.ico
   ```
4. Recompila

### Cambiar Idioma

El instalador soporta Español e Inglés. Para otros idiomas:
1. Descarga archivos `.isl` de Inno Setup
2. Agrégalos en la sección `[Languages]`

### Agregar Licencia

1. Crea archivo `LICENSE.txt`
2. Edita `installer.iss`:
   ```ini
   LicenseFile=LICENSE.txt
   ```

## Distribución

El archivo `NewsScraperSetup.exe` es todo lo que necesitas distribuir:
- ✅ Portable (no requiere otros archivos)
- ✅ Incluye todo el backend
- ✅ Firmado digitalmente (si tienes certificado)
- ✅ Compatible con Windows 10/11

---

**¡Listo!** Ahora tienes un instalador profesional de News Scraper 🚀
