#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

echo '🔁 Checking certificates via certbot...'
docker compose run --rm certbot renew --quiet

echo '♻️ Reloading nginx'
docker compose exec nginx nginx -s reload || docker compose restart nginx

echo '✅ SSL certificates refreshed'
