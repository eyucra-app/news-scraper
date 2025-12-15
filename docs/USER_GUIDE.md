# 👤 Manual de Usuario - News Scraper

Guía práctica para usar News Scraper en el día a día.

## Dashboard Principal

Accede a la API docs en: **http://localhost:8000/docs**

## Tareas Comunes

### 1. Agregar una Fuente de Noticias

**Endpoint**: `POST /api/sources/`

**Ejemplo**:
```json
{
  "name": "Ejemplo Noticias",
  "url": "https://sitio.com/noticias",
  "container": "clase-contenedor",
  "holder": "h2",
  "category": "nacional",
  "is_active": true
}
```

**¿Cómo encontrar container y holder?**
1. Abre la página de noticias en el navegador
2. Click derecho > Inspeccionar elemento
3. Encuentra el contenedor principal (div con clase)
4. Encuentra la etiqueta que contiene los títulos (h1, h2, a, etc.)

### 2. Testear una Fuente

**Endpoint**: `POST /api/sources/{id}/test`

Esto scrapea la fuente SIN guardar los titulares, perfecto para verificar configuración.

### 3. Iniciar Scraping Manual

**Endpoint**: `POST /api/scraping/start`

Scrapea TODAS las fuentes activas inmediatamente.

### 4. Programar Scraping Automático

**Endpoint**: `POST /api/scraping/scheduler/start?interval_minutes=10`

Programa scraping cada X minutos.

### 5. Ver Titulares Extraídos

**Endpoint**: `GET /api/headlines/?limit=50`

**Parámetros**:
- `limit`: Cantidad de titulares (máx 200)
- `category`: Filtrar por categoría
- `unsent_only=true`: Solo no enviados a Singular

### 6. Enviar Titulares a Singular.live

**Endpoint**: `POST /api/headlines/send`

**Body**:
```json
{
  "headline_ids": [1, 2, 3, 4, 5]
}
```

### 7. Ver Estadísticas

**Endpoint**: `GET /api/headlines/stats`

Muestra total de titulares, enviados, no enviados, por categoría.

## Casos de Uso

### Caso 1: Ticker de Noticias 24/7

```bash
# 1. Agregar múltiples fuentes variadas
# 2. Iniciar scheduler cada 5 minutos
curl -X POST "http://localhost:8000/api/scraping/scheduler/start?interval_minutes=5"

# 3. Enviar titulares periódicamente
# (Puedes automatizar esto con un cron job o script)
```

### Caso 2: Scraping On-Demand

```bash
# 1. Configurar fuentes pero desactivar auto-scraping
# 2. Ejecutar manualmente cuando necesites:
curl -X POST http://localhost:8000/api/scraping/start

# 3. Revisar titulares y enviar seleccionados
```

### Caso 3: Noticias de Última Hora

```bash
# 1. Filtrar titulares recientes no enviados
curl "http://localhost:8000/api/headlines/?unsent_only=true&limit=10"

# 2. Enviar inmediatamente a Singular
curl -X POST http://localhost:8000/api/headlines/send \
  -H "Content-Type: application/json" \
  -d '{"headline_ids": [...]}'
```

## Tips y Mejores Prácticas

### Configuración de Fuentes

✅ **DO**:
- Probar cada fuente con `/test` antes de activarla
- Usar nombres descriptivos
- Configurar categorías apropiadas

❌ **DON'T**:
- Scrapear sitios que prohíben scraping (revisar robots.txt)
- Usar intervalos muy cortos (< 3 minutos)
- Dejar fuentes con errores activas

### Scraping

✅ **DO**:
- Iniciar con intervalos conservadores (10-15 min)
- Monitorear logs para errores
- Revisar titulares antes de enviar a producción

❌ **DON'T**:
- Scrapear demasiado frecuentemente
- Ignorar errores en logs
- Enviar titulares duplicados

### Mantenimiento

- Revisar fuentes semanalmente (sitios cambian estructura)
- Limpiar titulares antiguos periódicamente
- Rotar credenciales de Singular.live cada 3 meses

---

Ver [API_DOCUMENTATION.md](API_DOCUMENTATION.md) para referencia completa de endpoints.
