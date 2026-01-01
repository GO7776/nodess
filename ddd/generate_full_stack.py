#!/usr/bin/env python3
"""Generate the deployment skeleton described in `1ndex copy.html`.

The HTML document stored in this repository acts as a long-form tutorial that
covers every phase of a production-ready Node.js + PostgreSQL stack on a Beget
VPS. Working with that document behind a VPN can be inconvenient, so this
script materialises the entire directory structure, sample configuration and
helper scripts that the course references.

Usage
-----
python generate_full_stack.py                 # creates ./myapp
python generate_full_stack.py -o infra       # creates ./infra
python generate_full_stack.py -o ./ops --force

The script is idempotent: by default it skips files that already exist. Use
"--force" to overwrite everything.
"""

from __future__ import annotations

import argparse
import textwrap
from pathlib import Path
from typing import Dict, Union

FileTree = Dict[str, Union[str, "FileTree"]]

PHASES_SUMMARY = """
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
"""

PROJECT_README = f"""# Node.js + PostgreSQL Production Stack

Эта директория создана скриптом `generate_full_stack.py` и повторяет структуру,
описанную в `1ndex copy.html`. Ниже собрана краткая логика всех фаз курса.

{PHASES_SUMMARY}

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
"""

DOCKER_COMPOSE = """version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: myapp_postgres
    restart: always
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app_network
    healthcheck:
      test: ['CMD-SHELL', 'pg_isready -U ${DB_USER}']
      interval: 10s
      timeout: 5s
      retries: 5

  app:
    build:
      context: ./app
      dockerfile: Dockerfile
    container_name: myapp_app
    restart: always
    env_file:
      - .env
    environment:
      NODE_ENV: ${NODE_ENV:-production}
      PORT: 3000
      DB_HOST: postgres
      DB_PORT: 5432
      JWT_SECRET: ${JWT_SECRET}
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - app_network
    ports:
      - '3000:3000'
    volumes:
      - ./app/logs:/app/logs

  nginx:
    image: nginx:alpine
    container_name: myapp_nginx
    restart: always
    ports:
      - '80:80'
      - '443:443'
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl-params.conf:/etc/nginx/snippets/ssl-params.conf:ro
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    depends_on:
      - app
    networks:
      - app_network

  certbot:
    image: certbot/certbot
    container_name: myapp_certbot
    volumes:
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    entrypoint: >-
      sh -c "trap exit TERM; while :; do certbot renew --webroot -w /var/www/certbot; sleep 12h & wait $${!}; done"
    networks:
      - app_network

  redis:
    image: redis:7-alpine
    container_name: myapp_redis
    restart: always
    volumes:
      - redis_data:/data
    networks:
      - app_network

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: myapp_cadvisor
    restart: always
    ports:
      - '8080:8080'
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
    networks:
      - app_network

  loki:
    image: grafana/loki:2.9.3
    container_name: myapp_loki
    restart: always
    ports:
      - '3100:3100'
    command: -config.file=/etc/loki/local-config.yaml
    volumes:
      - loki_data:/loki
    networks:
      - app_network

  promtail:
    image: grafana/promtail:2.9.3
    container_name: myapp_promtail
    restart: always
    volumes:
      - /var/log:/var/log
      - ./promtail-config.yaml:/etc/promtail/config.yaml:ro
    command: -config.file=/etc/promtail/config.yaml
    networks:
      - app_network

  adminer:
    image: adminer:latest
    container_name: myapp_adminer
    restart: always
    ports:
      - '8081:8080'
    networks:
      - app_network
    depends_on:
      - postgres

  portainer:
    image: portainer/portainer-ce:latest
    container_name: myapp_portainer
    restart: always
    ports:
      - '9000:9000'
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - portainer_data:/data
    networks:
      - app_network

volumes:
  postgres_data:
  redis_data:
  loki_data:
  portainer_data:

networks:
  app_network:
    driver: bridge
"""

DOCKER_COMPOSE_PROD = """version: '3.8'

services:
  app:
    image: ghcr.io/example/myapp:latest
    container_name: myapp_app
    restart: always
    env_file:
      - .env
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - app_network

  postgres:
    image: postgres:15-alpine
    container_name: myapp_postgres
    restart: always
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app_network

  nginx:
    image: nginx:alpine
    container_name: myapp_nginx
    restart: always
    ports:
      - '80:80'
      - '443:443'
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    depends_on:
      - app
    networks:
      - app_network

networks:
  app_network:
    driver: bridge

volumes:
  postgres_data:
"""

DEFAULT_ENV = """# Database
DB_NAME=myapp_db
DB_USER=myapp_user
DB_PASSWORD=change_me_now
DB_ROOT_PASSWORD=super_secret_root

# Application
NODE_ENV=production
JWT_SECRET=replace_with_openssl_rand
APP_NAME=myapp
APP_ENV=production

# Domains / SSL
DOMAIN=example.com
EMAIL=admin@example.com

# Monitoring / Alerts
TELEGRAM_BOT_TOKEN=000000000:sample
TELEGRAM_CHAT_ID=123456789
"""

ENV_EXAMPLE = """# Copy this file to .env and fill out secrets.
DB_NAME=myapp_db
DB_USER=myapp_user
DB_PASSWORD=please_change
DB_ROOT_PASSWORD=postgres_root
NODE_ENV=production
JWT_SECRET=$(openssl rand -base64 32)
DOMAIN=example.com
EMAIL=admin@example.com
TELEGRAM_BOT_TOKEN=bot_token_here
TELEGRAM_CHAT_ID=chat_id_here
"""

MAKEFILE = """SHELL := /bin/bash

PROJECT_NAME ?= myapp

bootstrap:
	@echo 'No bootstrap steps yet. Customize as needed.'

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f app

ps:
	docker compose ps

reload-nginx:
	docker compose exec nginx nginx -s reload

init-db:
	docker compose exec app npm run init-db

backup:
	./backup-db.sh

renew-ssl:
	./renew-certs.sh

monitor:
	./monitor.sh
"""

DEPLOY_SH = """#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

printf '\n🚀 Starting deployment...\n'

git pull --ff-only || true

docker compose pull

docker compose build --no-cache

docker compose down

docker compose up -d

printf '\n🗃️ Running migrations...\n'
docker compose exec app npm run init-db || true

printf '\n🧹 Cleaning unused Docker data...\n'
docker system prune -f

printf '\n✅ Deployment finished!\n'
docker compose ps
"""

BACKUP_DB_SH = """#!/bin/bash
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
"""

RENEW_CERTS_SH = """#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

echo '🔁 Checking certificates via certbot...'
docker compose run --rm certbot renew --quiet

echo '♻️ Reloading nginx'
docker compose exec nginx nginx -s reload || docker compose restart nginx

echo '✅ SSL certificates refreshed'
"""

MONITOR_SH = """#!/bin/bash
set -euo pipefail

APP_URL=${APP_URL:-http://localhost:3000/health}
STATUS=$(curl -s -o /dev/null -w '%{http_code}' "$APP_URL")

if [[ "$STATUS" != "200" ]]; then
  MSG="🚨 Service health check failed (${STATUS})"
  echo "$MSG"
  if [[ -n "${TELEGRAM_BOT_TOKEN:-}" && -n "${TELEGRAM_CHAT_ID:-}" ]]; then
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
      -d chat_id="${TELEGRAM_CHAT_ID}" \
      -d text="$MSG" >/dev/null || true
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
"""

PROMTAIL_CONFIG = """server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: app-logs
    static_configs:
      - targets:
          - localhost
        labels:
          job: myapp
          __path__: /var/log/*.log
      - targets:
          - localhost
        labels:
          job: node-app
          __path__: /app/logs/*.log
"""

NGINX_CONF = """events {
    worker_connections 2048;
}

http {
    map $http_upgrade $connection_upgrade {
        default upgrade;
        '' close;
    }

    upstream app_backend {
        server app:3000;
    }

    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

    server {
        listen 80;
        server_name ${DOMAIN} www.${DOMAIN};

        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        location / {
            proxy_pass http://app_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection $connection_upgrade;
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            proxy_pass http://app_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }

    server {
        listen 443 ssl http2;
        server_name ${DOMAIN} www.${DOMAIN};

        ssl_certificate /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;
        include /etc/nginx/snippets/ssl-params.conf;

        location / {
            proxy_pass http://app_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            proxy_pass http://app_backend;
        }
    }
}
"""

SSL_PARAMS = """ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers on;
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384';
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:10m;
ssl_session_tickets off;
ssl_stapling on;
ssl_stapling_verify on;
add_header Strict-Transport-Security "max-age=63072000" always;
"""

SITE_CONF = """server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        proxy_pass http://app:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
"""

PACKAGE_JSON = """{
  "name": "myapp",
  "version": "1.0.0",
  "description": "Node.js + PostgreSQL stack from 1ndex copy.html",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "dev": "nodemon src/index.js",
    "init-db": "node src/init-db.js",
    "lint": "eslint src --ext .js",
    "test": "echo 'Add tests' && exit 0"
  },
  "dependencies": {
    "bcrypt": "^5.1.1",
    "cors": "^2.8.5",
    "dotenv": "^16.3.1",
    "express": "^4.18.2",
    "express-validator": "^7.0.1",
    "helmet": "^7.1.0",
    "jsonwebtoken": "^9.0.2",
    "pg": "^8.11.3",
    "redis": "^4.6.10",
    "winston": "^3.11.0"
  },
  "devDependencies": {
    "eslint": "^8.57.0",
    "nodemon": "^3.0.2"
  }
}
"""

DOCKERFILE = """# syntax=docker/dockerfile:1

FROM node:18-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

FROM node:18-alpine
WORKDIR /app
ENV NODE_ENV=production

COPY --from=builder /app .

RUN addgroup -g 1001 nodejs && adduser -S nodejs -u 1001
USER nodejs

EXPOSE 3000
CMD ["node", "src/index.js"]
"""

DOCKERFILE_PROD = """FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
CMD ["node", "src/index.js"]
"""

DOCKERIGNORE = """node_modules
npm-debug.log
.env
.git
.gitignore
.vscode
.idea
logs
"""

GITIGNORE = """node_modules/
dist/
coverage/
.env
logs/
"""

ECOSYSTEM = """module.exports = {
  apps: [
    {
      name: 'myapp',
      script: 'src/index.js',
      instances: 1,
      exec_mode: 'fork',
      env: {
        NODE_ENV: 'production',
      },
    },
  ],
};
"""

INDEX_JS = """require('dotenv').config();
const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const { json, urlencoded } = express;
const logger = require('./config/logger');
const pool = require('./config/database');
const redis = require('./config/redis');

const apiRoutes = require('./routes/api');
const authRoutes = require('./routes/auth');
const userRoutes = require('./routes/users');
const errorHandler = require('./middlewares/errorHandler');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(helmet());
app.use(cors());
app.use(json());
app.use(urlencoded({ extended: true }));

app.get('/health', async (_req, res) => {
  try {
    await pool.query('SELECT 1');
    res.json({ status: 'healthy', db: 'connected' });
  } catch (error) {
    logger.error('Healthcheck failed', { error });
    res.status(500).json({ status: 'unhealthy', error: error.message });
  }
});

app.use('/api', apiRoutes);
app.use('/auth', authRoutes);
app.use('/users', userRoutes);

app.use(errorHandler);

app.listen(PORT, '0.0.0.0', () => {
  logger.info(`🚀 Server listening on port ${PORT}`, { env: process.env.NODE_ENV });
});
"""

INIT_DB = """const { Pool } = require('pg');
const { readFile } = require('fs/promises');
const path = require('path');

async function initDatabase() {
  const pool = new Pool({
    host: process.env.DB_HOST,
    port: process.env.DB_PORT,
    database: process.env.DB_NAME,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
  });

  try {
    const migrationPath = path.join(__dirname, '../migrations/001_initial.sql');
    const sql = await readFile(migrationPath, 'utf8');
    await pool.query(sql);
    await pool.query(`
      INSERT INTO users (username, email, password_hash)
      VALUES ('admin', 'admin@example.com', '$2b$10$ExampleHash')
      ON CONFLICT (email) DO NOTHING;
    `);
    console.log('✅ Database initialised');
  } catch (error) {
    console.error('❌ Migration error', error);
    process.exit(1);
  } finally {
    await pool.end();
  }
}

initDatabase();
"""

DATABASE_JS = """const { Pool } = require('pg');
const logger = require('./logger');

const pool = new Pool({
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
});

pool.on('error', (err) => {
  logger.error('Unexpected PG error', { err });
});

module.exports = pool;
"""

REDIS_JS = """const { createClient } = require('redis');
const logger = require('./logger');

const client = createClient({ url: process.env.REDIS_URL || 'redis://redis:6379' });

client.on('error', (err) => logger.error('Redis error', { err }));
client.on('ready', () => logger.info('Redis connected')); 

client.connect();

module.exports = client;
"""

LOGGER_JS = """const { createLogger, format, transports } = require('winston');

const logger = createLogger({
  level: process.env.NODE_ENV === 'production' ? 'info' : 'debug',
  format: format.combine(
    format.timestamp(),
    format.errors({ stack: true }),
    format.json()
  ),
  transports: [
    new transports.File({ filename: 'logs/error.log', level: 'error' }),
    new transports.File({ filename: 'logs/combined.log' }),
  ],
});

if (process.env.NODE_ENV !== 'production') {
  logger.add(new transports.Console({
    format: format.combine(format.colorize(), format.simple()),
  }));
}

module.exports = logger;
"""

API_ROUTES = """const { Router } = require('express');
const pool = require('../config/database');
const logger = require('../config/logger');

const router = Router();

router.get('/users', async (_req, res, next) => {
  try {
    const result = await pool.query('SELECT id, username, email, created_at FROM users LIMIT 20');
    res.json(result.rows);
  } catch (error) {
    logger.error('Failed to list users', { error });
    next(error);
  }
});

module.exports = router;
"""

AUTH_ROUTES = """const { Router } = require('express');
const { body } = require('express-validator');
const authController = require('../controllers/authController');
const validators = [
  body('email').isEmail(),
  body('password').isLength({ min: 8 }),
];

const router = Router();

router.post('/login', validators, authController.login);
router.post('/register', validators, authController.register);

module.exports = router;
"""

USERS_ROUTES = """const { Router } = require('express');
const userController = require('../controllers/userController');
const auth = require('../middlewares/auth');

const router = Router();

router.get('/me', auth, userController.me);
router.get('/', auth, userController.list);

module.exports = router;
"""

AUTH_CONTROLLER = """const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const { validationResult } = require('express-validator');
const pool = require('../config/database');
const logger = require('../config/logger');

exports.register = async (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }

  try {
    const { email, password, username } = req.body;
    const hashed = await bcrypt.hash(password, 10);
    await pool.query(
      'INSERT INTO users (email, password_hash, username) VALUES ($1, $2, $3) ON CONFLICT (email) DO NOTHING',
      [email, hashed, username]
    );
    res.status(201).json({ message: 'User created' });
  } catch (error) {
    logger.error('Register failed', { error });
    next(error);
  }
};

exports.login = async (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }

  try {
    const { email, password } = req.body;
    const { rows } = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
    const user = rows[0];

    if (!user) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const match = await bcrypt.compare(password, user.password_hash);
    if (!match) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const token = jwt.sign({ id: user.id, email: user.email }, process.env.JWT_SECRET, {
      expiresIn: '12h',
    });

    res.json({ token });
  } catch (error) {
    logger.error('Login failed', { error });
    next(error);
  }
};
"""

USER_CONTROLLER = """const pool = require('../config/database');

exports.me = async (req, res, next) => {
  try {
    const { rows } = await pool.query('SELECT id, email, username, created_at FROM users WHERE id = $1', [req.user.id]);
    res.json(rows[0]);
  } catch (error) {
    next(error);
  }
};

exports.list = async (_req, res, next) => {
  try {
    const { rows } = await pool.query('SELECT id, email, username FROM users ORDER BY created_at DESC LIMIT 50');
    res.json(rows);
  } catch (error) {
    next(error);
  }
};
"""

AUTH_MIDDLEWARE = """const jwt = require('jsonwebtoken');

module.exports = (req, res, next) => {
  const authHeader = req.headers.authorization;
  if (!authHeader) {
    return res.status(401).json({ error: 'Missing token' });
  }

  const [, token] = authHeader.split(' ');
  try {
    req.user = jwt.verify(token, process.env.JWT_SECRET);
    next();
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
};
"""

ERROR_HANDLER = """const logger = require('../config/logger');

module.exports = (err, _req, res, _next) => {
  logger.error('Unhandled error', { err });
  res.status(500).json({ error: 'Something went wrong' });
};
"""

VALIDATORS_JS = """const { body } = require('express-validator');

exports.registerRules = [
  body('username').isLength({ min: 3 }),
  body('email').isEmail(),
  body('password').isLength({ min: 8 }),
];
"""

HELPERS_JS = """exports.sanitizeFilename = (name) =>
  name.replace(/[<>:"/\\|?*]/g, '_').replace(/\.+$/, '').slice(0, 200);
"""

USER_MODEL = """class User {
  constructor(row) {
    this.id = row.id;
    this.username = row.username;
    this.email = row.email;
    this.createdAt = row.created_at;
  }
}

module.exports = User;
"""

POST_MODEL = """class Post {
  constructor(row) {
    this.id = row.id;
    this.userId = row.user_id;
    this.title = row.title;
    this.content = row.content;
  }
}

module.exports = Post;
"""

MODELS_INDEX = """module.exports = {
  User: require('./User'),
  Post: require('./Post'),
};
"""

MIGRATION_ONE = """-- Users and posts tables
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id);
"""

MIGRATION_TWO = """ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;
ALTER TABLE posts ADD COLUMN IF NOT EXISTS published BOOLEAN DEFAULT true;
"""

MIGRATE_JS = """const { readdir, readFile } = require('fs/promises');
const path = require('path');
const pool = require('../src/config/database');

async function runMigrations() {
  const migrationsDir = path.join(__dirname);
  const files = (await readdir(migrationsDir))
    .filter((file) => file.endsWith('.sql'))
    .sort();

  for (const file of files) {
    const sql = await readFile(path.join(migrationsDir, file), 'utf8');
    await pool.query(sql);
    console.log(`Applied ${file}`);
  }

  await pool.end();
}

runMigrations().catch((error) => {
  console.error(error);
  process.exit(1);
});
"""

DOC_API = """# API Overview
- `GET /` — статус сервиса.
- `GET /health` — проверка подключения к БД.
- `GET /api/users` — список пользователей.
- `POST /auth/register` — регистрация.
- `POST /auth/login` — получение JWT.
"""

DOC_DEPLOY = """# Deploy Guide
1. Заполните `.env`.
2. `docker compose build --pull`.
3. `docker compose up -d`.
4. `docker compose exec app npm run init-db`.
5. Настройте SSL через `certbot` и запланируйте `renew-certs.sh`.
"""

DOC_TROUBLE = """# Troubleshooting
- **PostgreSQL unhealthy**: проверьте переменные `DB_*`, выполните `docker compose logs postgres`.
- **SSL не обновляется**: убедитесь, что порт 80 открыт и cron запускает `renew-certs.sh`.
- **Память закончилась**: ограничьте ресурсы в `docker-compose.yml` и запустите `docker system prune`.
"""

BACKUPS_README = """# Backups
- Скрипт `backup-db.sh` создаёт сжатые дампы и хранит их 30 дней.
- Восстановление: `gunzip < backup.sql.gz | docker compose exec -T postgres psql -U myapp_user myapp_db`.
"""

DOCS_API = DOC_API
DOCS_DEPLOY = DOC_DEPLOY
DOCS_TROUBLE = DOC_TROUBLE

WORKFLOW_DEPLOY = """name: Deploy to VPS

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up SSH
        uses: webfactory/ssh-agent@v0.9.0
        with:
          ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
      - name: Deploy
        run: |
          ssh -o StrictHostKeyChecking=no ${{ secrets.SERVER_USER }}@${{ secrets.SERVER_IP }} \
            'cd /var/www/myapp && git pull && docker compose build && docker compose up -d'
"""

WORKFLOW_TESTS = """name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      - run: cd app && npm ci
      - run: cd app && npm test
"""

WORKFLOW_SECURITY = """name: Security Scan

on:
  schedule:
    - cron: '0 3 * * 1'

jobs:
  trivy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Trivy
        uses: aquasecurity/trivy-action@v0.11.2
        with:
          scan-type: fs
          format: table
          exit-code: '1'
          ignore-unfixed: true
          severity: CRITICAL,HIGH
"""

SCRIPTS_INIT = """#!/bin/bash
set -euo pipefail

PROJECT_ROOT=${1:-myapp}
python generate_full_stack.py -o "$PROJECT_ROOT"
"""

SCRIPTS_DEPLOY = """#!/bin/bash
set -euo pipefail

../deploy.sh
"""

SCRIPTS_BACKUP = """#!/bin/bash
set -euo pipefail

../backup-db.sh
"""

TEMPLATE_STRUCTURE: FileTree = {
    'docker-compose.yml': DOCKER_COMPOSE,
    'docker-compose.prod.yml': DOCKER_COMPOSE_PROD,
    '.env': DEFAULT_ENV,
    '.env.example': ENV_EXAMPLE,
    'README.md': PROJECT_README,
    'Makefile': MAKEFILE,
    'deploy.sh': DEPLOY_SH,
    'backup-db.sh': BACKUP_DB_SH,
    'renew-certs.sh': RENEW_CERTS_SH,
    'monitor.sh': MONITOR_SH,
    'promtail-config.yaml': PROMTAIL_CONFIG,
    'nginx': {
        'nginx.conf': NGINX_CONF,
        'ssl-params.conf': SSL_PARAMS,
        'sites-available': {
            'myapp.conf': SITE_CONF,
        },
    },
    'certbot': {
        'conf': {'.gitkeep': ''},
        'www': {'.gitkeep': ''},
    },
    'app': {
        'Dockerfile': DOCKERFILE,
        'Dockerfile.prod': DOCKERFILE_PROD,
        '.dockerignore': DOCKERIGNORE,
        '.gitignore': GITIGNORE,
        'package.json': PACKAGE_JSON,
        'ecosystem.config.js': ECOSYSTEM,
        'src': {
            'index.js': INDEX_JS,
            'init-db.js': INIT_DB,
            'config': {
                'database.js': DATABASE_JS,
                'redis.js': REDIS_JS,
                'logger.js': LOGGER_JS,
            },
            'routes': {
                'api.js': API_ROUTES,
                'auth.js': AUTH_ROUTES,
                'users.js': USERS_ROUTES,
            },
            'controllers': {
                'authController.js': AUTH_CONTROLLER,
                'userController.js': USER_CONTROLLER,
            },
            'models': {
                'User.js': USER_MODEL,
                'Post.js': POST_MODEL,
                'index.js': MODELS_INDEX,
            },
            'middlewares': {
                'auth.js': AUTH_MIDDLEWARE,
                'errorHandler.js': ERROR_HANDLER,
            },
            'utils': {
                'validators.js': VALIDATORS_JS,
                'helpers.js': HELPERS_JS,
            },
            'tests': {
                'integration': {'.gitkeep': ''},
                'unit': {'.gitkeep': ''},
            },
        },
        'migrations': {
            '001_initial.sql': MIGRATION_ONE,
            '002_add_users_table.sql': MIGRATION_TWO,
            'migrate.js': MIGRATE_JS,
        },
        'logs': {
            'error.log': '',
            'combined.log': '',
            'access.log': '',
        },
        'public': {
            'css': {'.gitkeep': ''},
            'js': {'.gitkeep': ''},
            'images': {'.gitkeep': ''},
        },
    },
    'backups': {
        'README.md': BACKUPS_README,
    },
    '.github': {
        'workflows': {
            'deploy.yml': WORKFLOW_DEPLOY,
            'tests.yml': WORKFLOW_TESTS,
            'security-scan.yml': WORKFLOW_SECURITY,
        },
    },
    'monitoring': {
        'grafana': {'.gitkeep': ''},
        'prometheus': {'.gitkeep': ''},
        'alertmanager': {'.gitkeep': ''},
    },
    'docs': {
        'API.md': DOCS_API,
        'DEPLOY.md': DOCS_DEPLOY,
        'TROUBLESHOOTING.md': DOCS_TROUBLE,
    },
    'scripts': {
        'init.sh': SCRIPTS_INIT,
        'deploy.sh': SCRIPTS_DEPLOY,
        'backup.sh': SCRIPTS_BACKUP,
    },
}


def normalize(content: str) -> str:
    if not content:
        return ''
    return textwrap.dedent(content).lstrip('\n') + ('\n' if not content.endswith('\n') else '')


def write_tree(base: Path, tree: FileTree, overwrite: bool = False) -> None:
    for name, payload in tree.items():
        destination = base / name
        if isinstance(payload, dict):
            destination.mkdir(parents=True, exist_ok=True)
            write_tree(destination, payload, overwrite)
            continue
        if destination.exists() and not overwrite:
            print(f'Skip existing file: {destination}')
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(normalize(payload), encoding='utf-8')
        print(f'Wrote {destination}')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Create the VPS project stack described in 1ndex copy.html')
    parser.add_argument('-o', '--output', default='myapp', help='Target directory (default: myapp)')
    parser.add_argument('--force', action='store_true', help='Overwrite existing files')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    target = Path(args.output).expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)
    write_tree(target, TEMPLATE_STRUCTURE, overwrite=args.force)
    print('\n🎉 Structure ready at', target)


if __name__ == '__main__':
    main()
