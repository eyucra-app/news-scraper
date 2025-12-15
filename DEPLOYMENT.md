# Deployment Instructions para News Scraper

## Pasos Rápidos para Deploy en Vercel

### 1. Preparar Repositorio Git

```bash
# Si no tienes git inicializado
git init
git add .
git commit -m "Ready for Vercel deployment"
```

### 2. Subir a GitHub

1. Crea un nuevo repositorio en https://github.com/new
2. Nombre sugerido: `news-scraper`
3. No inicialices con README

```bash
git remote add origin https://github.com/TU-USUARIO/news-scraper.git
git branch -M main
git push -u origin main
```

### 3. Deploy en Vercel

**Opción A: Desde Dashboard (Más fácil)**

1. Ve a https://vercel.com
2. Sign up / Login con GitHub
3. Click "Add New" → "Project"
4. Selecciona tu repositorio `news-scraper`
5. Configuración:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `out`
6. Click "Deploy"
7. Espera 2-3 minutos ✨

**Opción B: Con CLI**

```bash
# Instalar Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
cd c:/Users/eyucr/Desktop/React/news-scrapper
vercel

# Respuestas:
# Setup and deploy? Y
# Which scope? [tu cuenta]
# Link to existing project? N
# Project name? news-scraper
# Directory? frontend

# Deploy a producción
vercel --prod
```

### 4. Obtener tu URL

Vercel te dará una URL como:
- `news-scraper-xxx.vercel.app` (temporal)
- O configura: `news-scraper.vercel.app` (en Settings → Domains)

### 5. Verificar

Visita tu URL y deberías ver:
- 🔴 "Backend no disponible" ← Esto es CORRECTO
- El frontend funciona, solo falta el backend local

---

## Archivos Preparados

- ✅ `vercel.json` - Configuración de Vercel
- ✅ `frontend/next.config.ts` - Export estático configurado
- ✅ `frontend/out/` - Build listo (generado con npm run build)

---

## Próximo Paso

Una vez tengas tu URL de Vercel:
1. Anótala (ej: `https://news-scraper.vercel.app`)
2. Continúa con Fase 4: Crear instaladores
3. Los instaladores abrirán automáticamente esa URL

---

## Troubleshooting

**Build falla en Vercel:**
- Verifica que Root Directory = `frontend`
- Revisa logs en Vercel Dashboard

**404 en rutas:**
- Ya está configurado con `trailingSlash: true`
- Debería funcionar automáticamente

**Quieres cambiar el dominio:**
- Ve a Settings → Domains en Vercel
- Agrega tu dominio personalizado o cambia el subdominio

---

¿Listo para desplegar? 🚀
