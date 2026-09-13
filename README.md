# Asteria PMS

Three tiers of agent working alongside a post-market surveillance specialist at a
medical-device company. Forward hackathon, Track 1.

**The one line:** the registers are not the input, they are the output. In the dataset
this is built against, 369 indicator events happened, 307 reached the incident log, and
197 of those carry a correct event code — the register correctly identifies **53%** of
what happened. That is the number the product attacks.

Design docs live in [`plan/`](plan/). Read [`plan/ARCHITECTURE.md`](plan/ARCHITECTURE.md)
before anything else. This README covers only how to run the thing.

## Layout

```
backend/asteria/
  ingest/      mock-company/ -> Postgres (registers, telemetry, mail, meetings,
               service, ward rounds; ground truth into a separate schema)
  resolve/     entity resolution — plumbing, never a screen
  capture/     tier 1 — five bots, one primitive, autonomy level 3 always
  analysis/    tier 2 — indicators, denominators, the five workflows
  capa/        tier 3 — failure-mode matching and the sweep
  agent/       model client, autonomy levels, the append-only action log
  api/routes/  one router per dashboard screen
  models/      the eleven registers + the capture layer
frontend/src/
  screens/     the five screens of plan/DASHBOARD.md
```

## Running it

Prereqs: Docker, Python 3.11+ with [uv](https://docs.astral.sh/uv/), Node 20+.

```bash
cp .env.example .env      # add your ANTHROPIC_API_KEY
make install
make migrate              # starts Postgres in Docker, runs alembic
make ingest               # mock-company/ -> database
```

Then two terminals:

```bash
make api                  # http://127.0.0.1:8000  (docs at /docs)
make web                  # http://localhost:5173
```

Postgres is published on host port **5433**, so a local Postgres on 5432 does not clash.

## Build order

From [`plan/ARCHITECTURE.md`](plan/ARCHITECTURE.md) §Build order. Three built properly
beats five half-wired.

1. **Outage watch** — telemetry → incident log. The strongest single demo.
2. **Inbox triage** — mail → comms log + complaint recommendation.
3. **Meeting scribe** — transcript → comms log.
4. **Tier 2**, all five workflows. Lands ALERT-FALSE / SW 1.1.0.
5. **Tier 3**, one CAPA recommendation. BATT / H1.
6. RMA capture and field-check nudge, as stubs of the same primitive.

Ship the capture queue if you ship one screen.

## The rules that are not negotiable

- A capture bot never commits a row. It drafts; a human accepts, edits or rejects.
- A bot fills only fields its source evidences. Unknown stays blank, never a guess.
- Every drafted row points back to its raw artifact. If it doesn't, that's a bug.
- Capture never edits a human row — it proposes a separate completion suggestion.
- Capture is autonomy level 3, always. No promotion, however good the accept rate.
- A rejection, a declined complaint, a signal closed as no action — each is a
  permanent record with a named reviewer and a rationale. Never a deletion.
