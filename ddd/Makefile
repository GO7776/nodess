SHELL := /bin/bash

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
