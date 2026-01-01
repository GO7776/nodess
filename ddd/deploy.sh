#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

printf '
🚀 Starting deployment...
'

git pull --ff-only || true

docker compose pull

docker compose build --no-cache

docker compose down

docker compose up -d

printf '
🗃️ Running migrations...
'
docker compose exec app npm run init-db || true

printf '
🧹 Cleaning unused Docker data...
'
docker system prune -f

printf '
✅ Deployment finished!
'
docker compose ps
