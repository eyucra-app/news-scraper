# 🚀 Inicio Rápido - News Scraper

## Opción 1: Docker (Recomendado)

```bash
# 1. Navegar al proyecto
cd c:\Users\eyucr\Desktop\app.v.2\news-scrapper

# 2. Configurar credenciales
cp .env.example .env
notepad .env  # Editar SINGULAR_APP_INSTANCE_ID y SINGULAR_SHARED_TOKEN

# 3. Iniciar todo
docker-compose up -d

# 4. Verificar
curl http://localhost:8000/health
```

## Opción 2: Sin Docker

```bash
# 1. Instalar PostgreSQL y Redis
# 2. Crear base de datos newscrapper
# 3. Configurar .env con URLs locales
# 4. Instalar dependencias
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 5. Iniciar backend
python app.py
```

## Acceder a la Aplicación

- **API**: http://localhost:8000
- **Documentación Interactiva**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Primeros Pasos

### 1. Testear Singular.live

```bash
curl -X POST http://localhost:8000/api/config/test-singular
```

### 2. Agregar Fuente

```bash
curl -X POST http://localhost:8000/api/sources/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CNN",
    "url": "https://cnnespanol.cnn.com/seccion/mundo/",
    "container": "module__content row--container",
    "holder": "news__title",
    "category": "mundo",
    "is_active": true
  }'
```

### 3. Scrapear

```bash
curl -X POST http://localhost:8000/api/scraping/start
```

### 4. Ver Titulares

```bash
curl http://localhost:8000/api/headlines/
```

### 5. Iniciar Automático

```bash
curl -X POST "http://localhost:8000/api/scraping/scheduler/start?interval_minutes=5"
```

## Documentación Completa

Ver [docs/INSTALLATION.md](docs/INSTALLATION.md) para guía completa.

## Problemas Comunes

### No puede conectar a PostgreSQL
```bash
# Ver logs
docker-compose logs db

# Verificar estado
docker-compose ps
```

### Error de Singular.live
Verifica credenciales en `.env` y revisa la [guía de credenciales](../../../.gemini/antigravity/brain/101c271c-32f8-49d2-adab-d80ab49266d7/guia_credenciales_singular.md).
