.PHONY: db api web install migrate seed fmt test

install:
	cd backend && uv sync --extra dev
	cd frontend && npm install

db:
	docker compose up -d db

migrate: db
	cd backend && uv run alembic upgrade head

api:
	cd backend && uv run uvicorn asteria.main:app --reload --port 8000

web:
	cd frontend && npm run dev

ingest:
	cd backend && uv run python -m asteria.ingest

test:
	cd backend && uv run pytest

fmt:
	cd backend && uv run ruff format . && uv run ruff check --fix .
