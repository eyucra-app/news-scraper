# 🛠️ Guía de Mantenimiento - News Scraper

## Tareas de Mantenimiento Regular

### Diarias
- [ ] Revisar logs de errores
- [ ] Verificar que scheduler está activo
- [ ] Monitorear cantidad de titulares nuevos

### Semanales
- [ ] Verificar todas las fuentes funcionan correctamente
- [ ] Limpiar titulares antiguos (>30 días)
- [ ] Revisar uso de recursos (CPU, RAM, disco)

### Mensuales
- [ ] Actualizar dependencias de Python
- [ ] Backup de base de datos
- [ ] Revisar y optimizar queries lentas
- [ ] Rotarcredenciales si es necesario

## Comandos Útiles

### Logs

```bash
# Ver logs del backend (Docker)
docker-compose logs -f backend

# Ver logs de PostgreSQL
docker-compose logs db

# Ver logs de Redis
docker-compose logs redis

# Ver últimas 100 líneas
docker-compose logs --tail=100 backend
```

### Base de Datos

```bash
# Backup de PostgreSQL
docker-compose exec db pg_dump -U newscrapper newscrapper > backup_$(date +%Y%m%d).sql

# Restaurar backup
docker-compose exec -T db psql -U newscrapper newscrapper < backup_20241205.sql

# Conectar a PostgreSQL
docker-compose exec db psql -U newscrapper
```

### Limpieza

```bash
# Limpiar titulares antiguos (SQL)
DELETE FROM headlines WHERE created_at < NOW() - INTERVAL '30 days';

# Limpiar logs antiguos
DELETE FROM scrape_logs WHERE started_at < NOW() - INTERVAL '60 days';

# Vacuum de PostgreSQL (optimizar espacio)
docker-compose exec db psql -U newscrapper -c "VACUUM FULL;"
```

### Actualización de Dependencias

```bash
# Ver dependencias desactualizadas
pip list --outdated

# Actualizar requirements.txt
pip freeze > requirements.txt

# Reconstruir imagen Docker
docker-compose build backend
docker-compose up -d
```

## Monitoring

### Métricas a Monitorear

1. **Scraping Success Rate**: `headlines_new / headlines_found`
2. **Error Rate**: `error_count / scrape_count` por fuente
3. **Uso de Disco**: PostgreSQL y logs
4. **Memoria**: Backend container
5. **Latencia**: Tiempo de respuesta de API

### Health Checks

```bash
# API Health
curl http://localhost:8000/health

# PostgreSQL
docker-compose exec db pg_isready -U newscrapper

# Redis
docker-compose exec redis redis-cli ping
```

## Troubleshooting

### Fuente deja de funcionar

```sql
-- Ver errores recientes de una fuente
SELECT * FROM scrape_logs 
WHERE source_id = 1 
ORDER BY started_at DESC 
LIMIT 10;

-- Probar fuente
curl -X POST http://localhost:8000/api/sources/1/test
```

### Performance Issues

```sql
-- Ver queries lentas (si tienes pg_stat_statements)
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;

-- Ver tamaño de tablas
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(tablename::text)) 
FROM pg_tables 
WHERE schemaname = 'public';
```

## Seguridad

### Rotación de Credenciales

1. Generar nuevas credenciales en Singular.live
2. Actualizar `.env`
3. Reiniciar servicios: `docker-compose restart backend`

### Backups

**Automatizar con cron**:
```bash
# Agregar a crontab (Linux/Mac)
0 2 * * * cd /path/to/news-scrapper && docker-compose exec -T db pg_dump -U newscrapper newscrapper > backups/backup_$(date +\%Y\%m\%d).sql
```

---

Para más información, consulta [INSTALLATION.md](INSTALLATION.md) y [USER_GUIDE.md](USER_GUIDE.md).
