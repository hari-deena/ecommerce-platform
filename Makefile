.PHONY: up down logs migrate revision test lint format shell

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f backend

migrate:
	docker compose exec backend alembic upgrade head

revision:
	docker compose exec backend alembic revision --autogenerate -m "$(m)"

test:
	cd backend && uv run pytest

lint:
	cd backend && uv run ruff check . && uv run mypy app

format:
	cd backend && uv run ruff format .

shell:
	docker compose exec backend /bin/sh
