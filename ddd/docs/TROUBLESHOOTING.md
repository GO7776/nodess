# Troubleshooting
- **PostgreSQL unhealthy**: проверьте переменные `DB_*`, выполните `docker compose logs postgres`.
- **SSL не обновляется**: убедитесь, что порт 80 открыт и cron запускает `renew-certs.sh`.
- **Память закончилась**: ограничьте ресурсы в `docker-compose.yml` и запустите `docker system prune`.
