"""
Test rápido de migración a SQLite.
Verifica que la base de datos se crea correctamente y las tablas se generan.
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from db.database import init_db, engine
from db.models import Base
from core.config import settings
from sqlalchemy import text


async def test_sqlite_migration():
    """Prueba la migración a SQLite."""
    print("=" * 60)
    print("Test de Migracion a SQLite")
    print("=" * 60)
    
    # Verificar configuración
    print(f"\nConfiguracion:")
    print(f"   DATABASE_URL: {settings.DATABASE_URL}")
    print(f"   REDIS_ENABLED: {settings.REDIS_ENABLED}")
    print(f"   CORS_ORIGINS: {settings.CORS_ORIGINS}")
    
    # Inicializar base de datos
    print(f"\nInicializando base de datos...")
    try:
        await init_db()
        print("   [OK] Base de datos inicializada correctamente")
    except Exception as e:
        print(f"   [ERROR] Error al inicializar BD: {e}")
        return False
    
    # Verificar que el archivo se creó
    db_file = Path("news_scraper.db")
    if db_file.exists():
        size = db_file.stat().st_size
        print(f"   [OK] Archivo SQLite creado: {db_file.name} ({size} bytes)")
    else:
        print(f"   [ERROR] Archivo SQLite no encontrado")
        return False
    
    # Verificar tablas creadas
    print(f"\nVerificando tablas:")
    async with engine.begin() as conn:
        def get_tables(connection):
            # Para SQLite, obtener nombres de tablas usando text()
            result = connection.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            )
            return [row[0] for row in result]
        
        tables = await conn.run_sync(get_tables)
        
        expected_tables = ['news_sources', 'headlines', 'scrape_logs', 'app_config']
        for table in expected_tables:
            if table in tables:
                print(f"   [OK] Tabla '{table}' creada")
            else:
                print(f"   [ERROR] Tabla '{table}' NO encontrada")
    
    print(f"\nTest completado exitosamente!")
    print(f"=" * 60)
    return True


if __name__ == "__main__":
    result = asyncio.run(test_sqlite_migration())
    sys.exit(0 if result else 1)
