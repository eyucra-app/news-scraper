# Solución para Playwright en Ejecutable

## Problema

Playwright requiere navegadores (Chromium) que no se incluyen automáticamente con PyInstaller.

## Soluciones

### Opción 1: Instalar Playwright browsers en el sistema (RECOMENDADA)

El usuario debe ejecutar una sola vez después de instalar:

```bash
playwright install chromium
```

**Ventajas:**
- Funciona inmediatamente
- Navegadores actualizados
- Menor tamaño del ejecutable

**Desventajas:**
- Requiere paso adicional de instalación

### Opción 2: Usar Selenium en lugar de Playwright

Más compatible con PyInstaller, pero requiere chromedriver.

### Opción 3: Bundlear Playwright con PyInstaller (COMPLEJO)

Requiere copiar manualmente los binarios de chromium al ejecutable.

## Implementación Actual

Por ahora, el ejecutable funcionará para scraping HTML simple (sin JavaScript).

Para páginas que requieren JavaScript, el usuario necesita:
1. Instalar Playwright browsers una sola vez
2. O las páginas fallarán silenciosamente y usarán scraping HTML básico

## Mensaje para el Usuario

Cuando detectemos que Playwright no funciona, podemos mostrar:
"Para scraping avanzado de páginas con JavaScript, ejecuta: `playwright install chromium`"
