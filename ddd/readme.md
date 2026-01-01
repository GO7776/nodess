# Node.js + PostgreSQL Production Stack

Эта директория создана скриптом `generate_full_stack.py` и повторяет структуру,
описанную в `1ndex copy.html`. Ниже собрана краткая логика всех фаз курса.


## Phase 0 – Подготовка окружения
- Устанавливаем Node.js 18+, Termius, Git, VS Code и Docker Desktop.
- Заказываем VPS в Beget (Ubuntu 22.04 LTS, ≥2 GB RAM, 2 vCPU) и фиксируем IP, логин, пароль и SSH порт.

## Phase 1 – Подключение к серверу
- Создаём подключение в Termius, проверяем `uname -a` и `/etc/os-release`.
- Генерируем SSH-ключи, подключаем их к серверу и отключаем парольную аутентификацию.

## Phase 2 – Базовая настройка сервера
- Выполняем `apt update && apt upgrade`, ставим полезные пакеты.
- Настраиваем UFW (22, 80, 443), создаём пользователя `deploy`, копируем SSH ключи.

## Phase 3 – Docker и Compose
- Ставим Docker Engine и Compose plugin из официального репозитория.
- Добавляем пользователя в группу docker, включаем автозапуск и проверяем `docker run hello-world`.

## Phase 4 – Структура проекта
- Выстраиваем корневую папку `myapp/` с Docker Compose, .env, скриптами и документацией.
- Подготавливаем конфиги для Nginx, Certbot, логирования и мониторинга.

## Phase 5 – Node.js приложение
- Пишем многоступенчатый Dockerfile, `package.json`, `src/index.js`, `init-db.js` и MVC-модули.
- Добавляем `.dockerignore`, `.gitignore`, `migrations/`, `logs/`, `public/` и тестовые каталоги.

## Phase 6 – Nginx
- Настраиваем reverse proxy, rate limiting, отдельные upstream и конфиг для HTTP→HTTPS редиректов.

## Phase 7 – Запуск и деплой
- `docker compose build && docker compose up -d`, проверка `docker compose ps` и логов.
- Входим в PostgreSQL контейнер, применяем миграции и добавляем стартовые данные.

## Phase 8 – SSL и автоматизация
- Поднимаем Certbot, получаем сертификаты Let's Encrypt, пишем `renew-certs.sh` и cron-задачи.

## Phase 9 – База данных и миграции
- Создаём SQL миграции, `init-db.js`, cron для бэкапов (`backup-db.sh`).

## Phase 10 – CI/CD
- Готовим GitHub Actions workflow (`tests` + `deploy`), секреты и публикацию Docker образов.

## Phase 11 – Мониторинг и логирование
- Добавляем cAdvisor, Loki, Promtail, настраиваем Winston, Telegram оповещения и `monitor.sh`.

## Phase 12 – Оптимизация и безопасность
- Оптимизируем Dockerfile, ограничиваем ресурсы, включаем fail2ban и составляем production checklist.

## Phase 13 – Эксплуатация
- Скрипт `deploy.sh`, шпаргалка по Docker, PG и бэкапам.

## Phase 14–17 – Расширения
- Готовые рецепты для jQuery/Vue/React/Angular, Laravel/Yii2/Django/Flask, универсальный compose и bare-metal PostgreSQL.


## Как пользоваться шаблоном
- Скопируйте `.env.example` в `.env` и заполните значения.
- Запустите `make bootstrap` для установки git submodules/подготовки (опционально).
- Выполните `docker compose up -d` и отслеживайте логи `docker compose logs -f app`.
- Для первичной миграции выполните `docker compose exec app npm run init-db`.
- Настройте cron для `backup-db.sh`, `renew-certs.sh` и `monitor.sh`.

## Сервисы
- `app`: Express API, соединяется с PostgreSQL, Redis и пишет логи через Winston.
- `postgres`: хранилище данных, backup скрипт в `backup-db.sh`.
- `nginx` + `certbot`: reverse proxy и SSL.
- `redis`: кэш и брокер задач (по желанию).
- `cadvisor`, `loki`, `promtail`: мониторинг и сбор логов.
- `adminer`, `portainer`: обслуживание БД и Docker.

## Скрипты
- `deploy.sh`: полный цикл сборки и перезапуска контейнеров.
- `backup-db.sh`: ежедневный дамп БД и очистка старых архивов.
- `renew-certs.sh`: автоматическое продление SSL.
- `monitor.sh`: проверка health endpoint и отправка оповещений.
