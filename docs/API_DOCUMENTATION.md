# 📚 Documentación de API - News Scraper

Referencia completa de endpoints REST.

## Base URL

```
http://localhost:8000/api
```

## Autenticación

Actualmente no requiere autenticación (planificado para v2.0).

---

## Endpoints

### Sources (Fuentes)

#### Listar Fuentes
```http
GET /sources/
```

**Query Parameters**:
- `active_only` (bool): Solo fuentes activas

**Response 200**:
```json
[
  {
    "id": 1,
    "name": "CNN Español",
    "url": "https://cnnespanol.cnn.com/seccion/mundo/",
    "container": "module__content",
    "holder": "news__title",
    "data_field": null,
    "category": "mundo",
    "is_active": true,
    "scrape_count": 45,
    "error_count": 2,
    "last_scraped_at": "2024-12-05T19:30:00"
  }
]
```

#### Crear Fuente
```http
POST /sources/
```

**Body**:
```json
{
  "name": "Nueva Fuente",
  "url": "https://sitio.com/noticias",
  "container": "main-content",
  "holder": "h2",
  "data_field": "subtitle",
  "category": "local",
  "is_active": true
}
```

**Response 201**: Fuente creada

#### Obtener Fuente
```http
GET /sources/{id}
```

**Response 200**: Objeto de fuente  
**Response 404**: Fuente no encontrada

#### Actualizar Fuente
```http
PUT /sources/{id}
```

**Body**: Campos a actualizar (parcial)

#### Eliminar Fuente
```http
DELETE /sources/{id}
```

**Response 204**: Eliminado exitosamente

#### Testear Fuente
```http
POST /sources/{id}/test
```

**Response 200**:
```json
{
  "source": "CNN Español",
  "status": "completed",
  "headlines_found": 12,
  "headlines_new": 8,
  "sample_headlines": ["Titular 1", "Titular 2", ...],
  "error_message": null
}
```

---

### Scraping

#### Iniciar Scraping Manual
```http
POST /scraping/start
```

**Response 200**:
```json
{
  "status": "completed",
  "stats": {
    "sources_scraped": 5,
    "headlines_found": 67,
    "headlines_new": 23,
    "errors": 0
  }
}
```

#### Estado del Scraping
```http
GET /scraping/status
```

**Response 200**:
```json
{
  "running": true,
  "paused": false,
  "next_run": "2024-12-05T20:00:00",
  "interval_minutes": 5
}
```

#### Iniciar Scheduler
```http
POST /scraping/scheduler/start?interval_minutes=5
```

#### Detener Scheduler
```http
POST /scraping/scheduler/stop
```

#### Pausar Scheduler
```http
POST /scraping/scheduler/pause
```

#### Reanudar Scheduler
```http
POST /scraping/scheduler/resume
```

---

### Headlines (Titulares)

#### Listar Titulares
```http
GET /headlines/?limit=50&offset=0
```

**Query Parameters**:
- `limit` (int): Máximo de resultados (máx 200)
- `offset` (int): Paginación
- `category` (string): Filtrar por categoría
- `source_id` (int): Filtrar por fuente
- `unsent_only` (bool): Solo no enviados

**Response 200**: Array de titulares

#### Estadísticas
```http
GET /headlines/stats
```

**Response 200**:
```json
{
  "total": 1234,
  "sent": 980,
  "unsent": 254,
  "by_category": {
    "mundo": 456,
    "local": 234,
    "deportes": 123
  }
}
```

#### Enviar a Singular.live
```http
POST /headlines/send
```

**Body**:
```json
{
  "headline_ids": [1, 2, 3, 4, 5]
}
```

**Response 200**:
```json
{
  "status": "success",
  "sent": 5
}
```

**Response 500**: Error enviando

#### Eliminar Titular
```http
DELETE /headlines/{id}
```

**Response 204**: Eliminado

---

### Config (Configuración)

#### Obtener Configuración
```http
GET /config/
```

**Response 200**:
```json
{
  "singular": {
    "app_instance_id": "app-123...",
    "has_token": true
  },
  "scraping_interval": 5,
  "environment": "production",
  "debug": false
}
```

#### Testear Singular.live
```http
POST /config/test-singular
```

**Response 200**:
```json
{
  "status": "success",
  "message": "Conexión con Singular.live exitosa"
}
```

---

## Códigos de Error

| Código | Significado |
|--------|-------------|
| 200 | OK |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request (datos inválidos) |
| 404 | Not Found |
| 500 | Internal Server Error |

---

## Rate Limiting

Actualmente sin límites. Planificado para v2.0.

---

## Ejemplos con curl

```bash
# Listar fuentes
curl http://localhost:8000/api/sources/

# Crear fuente
curl -X POST http://localhost:8000/api/sources/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","url":"https://test.com","container":"main","holder":"h2","category":"mundo"}'

# Iniciar scraping
curl -X POST http://localhost:8000/api/scraping/start

# Ver titulares
curl "http://localhost:8000/api/headlines/?limit=10"

# Estadísticas
curl http://localhost:8000/api/headlines/stats
```

---

Ver [USER_GUIDE.md](USER_GUIDE.md) para casos de uso prácticos.
