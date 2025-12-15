# 📦 Guía de Instalación - News Scraper

Esta guía cubre la instalación y configuración inicial de News Scraper.

## Índice

1. [Instalación con Docker (Recomendado)](#instalación-con-docker)
2. [Instalación Manual](#instalación-manual)
3. [Configuración Inicial](#configuración-inicial)
4. [Verificación](#verificación)
5. [Troubleshooting](#troubleshooting)

---

## Instalación con Docker

### Prerequisitos

- **Docker** 20.10+ ([Instalar Docker](https://docs.docker.com/get-docker/))
- **Docker Compose** 2.0+ (incluido con Docker Desktop)
- **Git** (para clonar el repositorio)

### Pasos

#### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd news-scrapper
```

#### 2. Configurar Variables de Entorno

```bash
# Copiar el template
cp .env.example .env

# Editar con tu editor favorito
notepad .env  # Windows
nano .env     # Linux/Mac
```

**Variables críticas a configurar**:

```env
# Credenciales de Singular.live (obligatorio)
SINGULAR_APP_INSTANCE_ID=tu-app-instance-id
SINGULAR_SHARED_TOKEN=tu-shared-token

# Base de datos (ya configurado por defecto para Docker)
DATABASE_URL=postgresql+asyncpg://newscrapper:newscrapper_password@db:5432/newscrapper

# Redis (ya configurado por defecto para Docker)
REDIS_URL=redis://redis:6379/0
```

Ver [Guía de Credenciales de Singular.live](../../../.gemini/antigravity/brain/101c271c-32f8-49d2-adab-d80ab49266d7/guia_credenciales_singular.md) para obtener las credenciales.

#### 3. Construir e Iniciar Servicios

```bash
# Construir imágenes e iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f
```

#### 4. Verificar que Todo Funciona

```bash
# Verificar estado de contenedores
docker-compose ps

# Debería mostrar:
# newscrapper_db       Up (healthy)
# newscrapper_redis    Up (healthy)
# newscrapper_backend  Up
```

#### 5. Acceder a la Aplicación

- **Backend API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## Instalación Manual

### Prerequisitos

- **Python** 3.11+ ([Descargar Python](https://www.python.org/downloads/))
- **PostgreSQL** 14+ ([Descargar PostgreSQL](https://www.postgresql.org/download/))
- **Redis** 7+ ([Descargar Redis](https://redis.io/download))
- **Git**

### Pasos

#### 1. Clonar y Preparar

```bash
git clone <repository-url>
cd news-scrapper
```

#### 2. Configurar PostgreSQL

```bash
# Conectar a PostgreSQL
psql -U postgres

# Crear base de datos y usuario
CREATE DATABASE newscrapper;
CREATE USER newscrapper WITH ENCRYPTED PASSWORD 'newscrapper_password';
GRANT ALL PRIVILEGES ON DATABASE newscrapper TO newscrapper;
\q
```

#### 3. Instalar Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

#### 4. Configurar Variables de Entorno

```bash
# Crear archivo .env en la raíz del proyecto
cp .env.example .env

# Editar .env con configuraciones locales
# Importante: usar localhost en lugar de nombres de contenedores
```

**Ejemplo para instalación local**:

```env
# Singular.live
SINGULAR_APP_INSTANCE_ID=tu-app-instance-id
SINGULAR_SHARED_TOKEN=tu-shared-token

# Base de datos LOCAL
DATABASE_URL=postgresql+asyncpg://newscrapper:newscrapper_password@localhost:5432/newscrapper

# Redis LOCAL
REDIS_URL=redis://localhost:6379/0
```

#### 5. Iniciar Redis

```bash
# Windows (si instalaste Redis con chocolatey):
redis-server

# Linux/Mac:
redis-server
```

#### 6. Iniciar Backend

```bash
cd backend

# Asegúrate de que el entorno virtual está activado
python app.py
```

El backend estará disponible en: http://localhost:8000

---

## Configuración Inicial

### 1. Verificar Conexión con Singular.live

```bash
curl -X POST http://localhost:8000/api/config/test-singular
```

**Respuesta esperada**:
```json
{
  "status": "success",
  "message": "Conexión con Singular.live exitosa"
}
```

### 2. Agregar Primera Fuente de Noticias

Usar la API o Swagger UI (http://localhost:8000/docs):

```bash
curl -X POST http://localhost:8000/api/sources/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CNN Español",
    "url": "https://cnnespanol.cnn.com/seccion/mundo/",
    "container": "module__content row--container",
    "holder": "news__title",
    "category": "mundo",
    "is_active": true
  }'
```

### 3. Probar Scraping Manual

```bash
curl -X POST http://localhost:8000/api/scraping/start
```

### 4. Iniciar Scraping Automático

```bash
# Iniciar scheduler con intervalo de 5 minutos
curl -X POST "http://localhost:8000/api/scraping/scheduler/start?interval_minutes=5"
```

---

## Verificación

### Checklist de Verificación

- [ ] **PostgreSQL**: Base de datos creada y accesible
- [ ] **Redis**: Servidor Redis corriendo
- [ ] **Backend**: API responde en puerto 8000
- [ ] **Health Check**: `/health` retorna status "healthy"
- [ ] **Singular.live**: Test de conexión exitoso
- [ ] **Fuentes**: Al menos una fuente configurada
- [ ] **Scraping**: Scraping manual funciona
- [ ] **Titulares**: Se pueden ver titulares extraídos

### Comandos de Verificación

```bash
# 1. Health check
curl http://localhost:8000/health

# 2. Listar fuentes
curl http://localhost:8000/api/sources/

# 3. Ver titulares
curl http://localhost:8000/api/headlines/?limit=10

# 4. Estadísticas
curl http://localhost:8000/api/headlines/stats
```

---

## Troubleshooting

### Problema: "Connection refused" al base de datos

**Causa**: PostgreSQL no está corriendo o configuración incorrecta.

**Solución**:
```bash
# Verificar que PostgreSQL está corriendo
# Windows:
sc query postgresql-x64-14

# Linux/Mac:
sudo systemctl status postgresql

# Verificar que la URL de conexión es correcta en .env
```

### Problema: "Connection refused" a Redis

**Causa**: Redis no está corriendo.

**Solución**:
```bash
# Iniciar Redis
# Windows:
redis-server

# Linux/Mac:
sudo systemctl start redis

# Verificar conexión
redis-cli ping
# Debe responder: PONG
```

### Problema: Error en Singular.live

**Causa**: Credenciales incorrectas o no configuradas.

**Solución**:
1. Verificar que `SINGULAR_APP_INSTANCE_ID` y `SINGULAR_SHARED_TOKEN` están en `.env`
2. Verificar que las credenciales son correctas
3. Ver [Guía de Credenciales](../../../.gemini/antigravity/brain/101c271c-32f8-49d2-adab-d80ab49266d7/guia_credenciales_singular.md)

### Problema: No se extraen titulares

**Causa**: Configuración incorrecta de contenedor/holder o sitio cambió estructura.

**Solución**:
1. Probar una fuente con el endpoint `/api/sources/{id}/test`
2. Revisar logs: `docker-compose logs backend`
3. Ajustar `container` y `holder` según la estructura actual del sitio

### Problema: Docker no inicia

**Causa**: Puertos ya en uso o permisos insuficientes.

**Solución**:
```bash
# Ver qué está usando el puerto 8000
# Windows:
netstat -ano | findstr :8000

# Linux/Mac:
lsof -i :8000

# Detener servicios en conflicto o cambiar puerto en docker-compose.yml
```

### Logs y Debugging

```bash
# Ver logs en tiempo real (Docker)
docker-compose logs -f backend

# Ver logs de un servicio específico
docker-compose logs db
docker-compose logs redis

# Entrar al contenedor para debugging
docker-compose exec backend bash

# Ver logs de PostgreSQL
docker-compose exec db psql -U newscrapper -d newscrapper
```

---

## Próximos Pasos

Una vez instalado y verificado:

1. Lee el [Manual de Usuario](USER_GUIDE.md)
2. Configura más fuentes de noticias
3. Ajusta el intervalo de scraping según necesites
4. Revisa la [Documentación de API](API_DOCUMENTATION.md)

---

**¿Necesitas ayuda?** Consulta la documentación completa o reporta un issue.
