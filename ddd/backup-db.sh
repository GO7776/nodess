#!/bin/bash
set -euo pipefail

BACKUP_DIR="$(pwd)/backups"
DATE=$(date +%Y%m%d_%H%M%S)
CONTAINER=myapp_postgres
DB_NAME=myapp_db
DB_USER=myapp_user

mkdir -p "$BACKUP_DIR"

echo "Creating backup $BACKUP_DIR/backup_$DATE.sql.gz"
docker exec "$CONTAINER" pg_dump -U "$DB_USER" "$DB_NAME" > "$BACKUP_DIR/backup_$DATE.sql"

gzip "$BACKUP_DIR/backup_$DATE.sql"

find "$BACKUP_DIR" -name '*.gz' -mtime +30 -delete

echo "✅ Backup complete"
