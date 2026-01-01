# Backups
- Скрипт `backup-db.sh` создаёт сжатые дампы и хранит их 30 дней.
- Восстановление: `gunzip < backup.sql.gz | docker compose exec -T postgres psql -U myapp_user myapp_db`.
