# Guía Rápida: Crear Ejecutable de News Scraper

## Paso 1: Preparar Entorno

```bash
# Asegúrate de tener todas las dependencias
cd backend
pip install -r requirements.txt
cd ..
```

## Paso 2: Construir Ejecutable

```bash
# Ejecutar script de build
python build_exe.py
```

Esto:
- Instala PyInstaller si es necesario
- Empaqueta todo el backend en un solo .exe
- Tarda ~3-5 minutos

## Paso 3: Probar Ejecutable

```bash
# Ejecutar el .exe generado
.\dist\NewsScraperBackend.exe
```

Debería:
1. Mostrar consola con logs del backend
2. Iniciar servidor en localhost:8000
3. Crear icono en bandeja del sistema
4. Abrir navegador con https://news-scraper-v1.vercel.app

## Ubicación del Ejecutable

```
dist/
└── NewsScraperBackend.exe  ← Este es el ejecutable final
```

## Tamaño Aproximado

- Ejecutable: ~150-200 MB (incluye Python + todas las dependencias)
- Primera ejecución crea: news_scraper.db (~50 KB)

## Distribución

El archivo `NewsScraperBackend.exe` es **portable**:
- No requiere instalación de Python
- No requiere pip install
- Incluye todas las dependencias
- El usuario solo necesita ejecutarlo

---

## Siguiente Paso (Opcional)

Para crear un **instalador profesional** con Inno Setup:
1. Instala Inno Setup: https://jrsoftware.org/isdl.php
2. Usa el script `installer.iss` (próximo paso)
3. Genera `NewsScraperSetup.exe`

El instalador profesional permite:
- Elegir ubicación de instalación
- Configurar auto-inicio
- Crear acceso directo
- Desinstalador automático
