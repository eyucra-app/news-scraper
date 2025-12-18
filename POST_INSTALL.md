# Configuración Post-Instalación de News Scraper

## Problema 1: Base de Datos se Borra ✅ SOLUCIONADO

**Causa:** La base de datos se guardaba en un directorio temporal.

**Solución Implementada:**
La base de datos ahora se guarda en:
- **Windows:** `C:\Users\[TuUsuario]\AppData\Roaming\NewsScraper\news_scraper.db`
- **macOS:** `~/.newsscraper/news_scraper.db`
- **Linux:** `~/.newsscraper/news_scraper.db`

Estos son directorios persistentes que NO se borran al cerrar la aplicación.

---

## Problema 2: Playwright No Funciona (Páginas con JavaScript)

**Causa:** Playwright requiere navegadores (Chromium) que no se incluyen en el ejecutable.

### Solución: Instalar Chromium (Una Sola Vez)

**En Windows:**

1. Abre **PowerShell** o **CMD**
2. Ejecuta:
   ```bash
   playwright install chromium
   ```
3. Espera a que descargue (~150MB)
4. ✅ ¡Listo! Ahora funcionará Playwright

**Alternativa (si no funciona el comando anterior):**

```bash
python -m playwright install chromium
```

### ¿Qué Pasa Si NO Instalo Chromium?

La aplicación funcionará perfectamente EXCEPTO:
- ❌ Páginas que requieren JavaScript para cargar contenido (marcadas con "Requiere JS")
- ✅ Páginas HTML normales SEGUIRÁN funcionando sin problemas

### Cómo Verificar Si Funciona

1. En la aplicación, ve a "Sources"
2. Crea una fuente que tenga "Requires JavaScript" marcado
3. Haz scraping
4. Si ves los titulares → ✅ Funcionó
5. Si no hay titulares y ves error en logs → Chromium no instalado

---

## Ubicación de Archivos Importantes

### Base de Datos
- **Windows:** `%APPDATA%\NewsScraper\news_scraper.db`
- **macOS/Linux:** `~/.newsscraper/news_scraper.db`

### Logs (si los hay)
- Misma ubicación que la base de datos

### ¿Cómo Hacer Backup?

Simplemente copia el archivo `news_scraper.db` a otro lugar seguro.

Para restaurar: copia el archivo de vuelta a su ubicación original.

---

## Resumen

**✅ Ya NO necesitas hacer nada** - La base de datos ahora persiste automáticamente

**⚠️ Opcional (para scraping avanzado):** Ejecuta `playwright install chromium`

**🎯 Todo lo demás funciona out-of-the-box!**
