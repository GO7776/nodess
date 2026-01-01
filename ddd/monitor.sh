#!/bin/bash
set -euo pipefail

APP_URL=${APP_URL:-http://localhost:3000/health}
STATUS=$(curl -s -o /dev/null -w '%{http_code}' "$APP_URL")

if [[ "$STATUS" != "200" ]]; then
  MSG="🚨 Service health check failed (${STATUS})"
  echo "$MSG"
  if [[ -n "${TELEGRAM_BOT_TOKEN:-}" && -n "${TELEGRAM_CHAT_ID:-}" ]]; then
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage"       -d chat_id="${TELEGRAM_CHAT_ID}"       -d text="$MSG" >/dev/null || true
  fi
else
  echo "✅ Service is healthy ($STATUS)"
fi

DISK=$(df / | awk 'NR==2 {print $5}' | tr -d '%')
if (( DISK > 80 )); then
  echo "⚠️ Disk usage is ${DISK}%"
fi

RUNNING=$(docker ps -q | wc -l)
if (( RUNNING < 3 )); then
  echo '⚠️ Less than 3 containers are running'
fi
