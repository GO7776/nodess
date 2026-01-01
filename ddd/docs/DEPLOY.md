# Deploy Guide
1. Заполните `.env`.
2. `docker compose build --pull`.
3. `docker compose up -d`.
4. `docker compose exec app npm run init-db`.
5. Настройте SSL через `certbot` и запланируйте `renew-certs.sh`.
