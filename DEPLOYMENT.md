# Deployment Instructions para News Scraper

## ⚠️ IMPORTANTE: Configuración Correcta de Vercel

El error que viste es porque falta configurar el **Root Directory** en Vercel.

## Pasos CORREGIDOS para Deploy en Vercel

### 1. Preparar Repositorio Git

```bash
# Commitear los cambios actualizados
git add .
git commit -m "Fix vercel.json configuration"
git push origin main
```

### 2. Configurar en Vercel Dashboard

1. Ve a tu proyecto en https://vercel.com/dashboard
2. Click en **Settings** (⚙️)
3. Ve a **General** en el sidebar
4. Busca la sección **Build & Development Settings**
5. Configura lo siguiente:

   **Framework Preset:** Next.js
   
   **Root Directory:** 
   - Click en **Edit**
   - Ingresa: `frontend` ← IMPORTANTE
   - Click en **Save**
   
   **Build Command:** `npm run build` (automático)
   
   **Output Directory:** `out` (automático)
   
   **Install Command:** `npm install` (automático)

6. Guarda los cambios

### 3. Re-Deploy

**Opción A: Desde Dashboard**
1. Ve a **Deployments**
2. Click en el último deployment fallido
3. Click en el botón **⋯** (tres puntos)
4. Selecciona **Redeploy**

**Opción B: Nuevo Push**
```bash
git commit --allow-empty -m "Trigger redeploy"
git push
```

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
