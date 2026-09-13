.PHONY: db api web install migrate seed fmt test capture sop fleet live reset-live

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

capture:
	cd backend && uv run python -m asteria.capture

# The simulated PulseOne fleet, on its own port. It is the device cloud, not
# part of Asteria — the backend reaches it over HTTP like it would a real one.
# FLEET_SPEED=60 is one simulated minute per wall second. FLEET_INTENSITY is how
# much hotter than a real fleet it runs — 1.0 is PMS-PLAN-001's own rates, which
# is almost entirely silence. See plan/TELEMETRY-API.md.
fleet:
	cd backend && uv run python -m asteria.fleet

# Asteria consuming that fleet: poll, draft, triage, score, repeat. Needs
# `make fleet` running. Commits nothing, at any speed.
live:
	cd backend && uv run python -m asteria.capture.live

# Takes the simulated fleet back out of the database, leaving the frozen twenty
# months. Run it before `make test` — the test suite reads the same database,
# and a rate computed across real and simulated rows is meaningless.
reset-live:
	cd backend && uv run python -m asteria.fleet.reset

# Reissues the controlled SOP PDF from reference-data/sop/ and pins its checksum.
# Move `revision` in the YAML first — regenerating is a document reissue.
sop:
	cd backend && uv run --extra docs python tools/sop_pdf.py

test:
	cd backend && uv run pytest

fmt:
	cd backend && uv run ruff format . && uv run ruff check --fix .
