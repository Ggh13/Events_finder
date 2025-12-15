.PHONY:
.SILENT:

up:
	docker compose -f docker-compose-local.yaml up -d --build

down-v:
	docker compose down -v

down:
	docker compose down -v