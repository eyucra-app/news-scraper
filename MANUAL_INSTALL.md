# Instalación Manual de News Scraper

## Problema Actual

La aplicación tiene dos issues que requieren pasos manuales:

### 1. Playwright
El instalador automático de Playwright no funciona correctamente en el ejecutable.

**Solución:** Instalar manualmente DESPUÉS de instalar la app:

```bash
playwright install chromium
```

O si no funciona:

```bash
python -m playwright install chromium
```

### 2. Minimizar a Bandeja
Los eventos de pywebview pueden no ocultar la ventana de la taskbar correctamente.

**Comportamiento actual:**
- Al minimizar → va a taskbar (como ventana normal)
- Al cerrar (X) → cierra completamente

**Solución temporal:**
- Usar el ícono de la bandeja para controlar la app
- No minimizar, solo cerrar y abrir desde bandeja

---

## Instalación Recomendada

1. **Instalar la aplicación:**
   ```bash
   NewsScraperSetup.exe
   ```

2. **Instalar Playwright (REQUERIDO para scraping con JavaScript):**
   ```bash
   playwright install chromium
   ```
   
   Esto descarga ~150MB. Es necesario solo una vez.

3. **Ejecutar la aplicación:**
   - Click en el ícono de escritorio
   - O buscar "News Scraper" en el menú inicio

4. **Primera ejecución:**
   - Se abrirá consola brevemente
   - Luego se abrirá ventana de la aplicación
   - Consola se ocultará automáticamente

---

## Alternativa: Ejecutable Portable

Si prefieres no usar el instalador:

1. Copiar `dist/NewsScraperBackend.exe` a cualquier carpeta
2. Ejecutar directamente
3. Instalar Playwright manualmente (paso 2 de arriba)

---

## Verificar que Playwright Funciona

1. Abre la app
2. Ve a "Sources"
3. Crea una fuente con "Requires JavaScript" marcado
4. Haz scraping
5. Si ves titulares → ✅ Playwright funciona
6. Si no → instala Playwright con el comando de arriba
