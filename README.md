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
  capture/     tier 1 — six bots, one primitive, autonomy level 3 always
  triage/      OPS-SOP-004, executed: the procedure, eight read-only estate
               probes, and the condition predicates behind each branch
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
make capture              # run tier 1 over the sources -> the review queue
```

`make capture` drafts; it never commits. Rows leave the queue through
`POST /api/capture/drafts/{id}/accept|edit|reject` and nowhere else.

Then two terminals:

```bash
make api                  # http://127.0.0.1:8000  (docs at /docs)
make web                  # http://localhost:5173
```

Postgres is published on host port **5433**, so a local Postgres on 5432 does not clash.

## Google Sheets

The customer's registers are seven live Google Sheets, one per workbook. An agent
reaches them as a service account that a human invited to each file — so access is per
register, and revoking it is unsharing a file.

Two things are not in the repository and never will be: the service-account JSON key,
and the filled-in `.env`. Keep the key outside the repo and point
`REGISTER_SHEETS_CREDENTIALS` at it.

An `.xlsx` uploaded to Drive is **not** a Google Sheet — Drive keeps it as an Excel blob
the API refuses to write to. Registers must be native sheets.

Read [`plan/SHEETS.md`](plan/SHEETS.md) before writing anything that touches them: it
covers what an agent is allowed to write, and the three constraints that will otherwise
cost an hour each (RAW values, the 60 reads/min quota, the Office-file trap).

## Build order

From [`plan/ARCHITECTURE.md`](plan/ARCHITECTURE.md) §Build order. Three built properly
beats five half-wired.

1. ~~**Outage watch** — telemetry → incident log. The strongest single demo.~~
   **Built.** 44 rows recovered, 559 completions, 100% field accuracy against
   ground truth, coverage 53% → 93% if the queue is worked as drafted.
   **The capture queue screen it feeds is built** — `make web`, then
   http://localhost:5173/capture.
2. ~~**Field triage** — OPS-SOP-004 → troubleshooting log. *Why*, not just *what*.~~
   **Built.** 288 episodes triaged against the ops team's own procedure, 281
   diagnoses matching what was actually wrong, 59 escalated as inconclusive
   rather than guessed, 2,074 read-only checks and no device touched. The
   procedure walk renders on the review panel, transcripts and all.
3. **Inbox triage** — mail → comms log + complaint recommendation.
4. **Meeting scribe** — transcript → comms log.
5. **Tier 2**, all five workflows. Lands ALERT-FALSE / SW 1.1.0.
6. **Tier 3**, one CAPA recommendation. BATT / H1.
7. RMA capture and field-check nudge, as stubs of the same primitive.

Ship the capture queue if you ship one screen.

## The rules that are not negotiable

- A capture bot never commits a row. It drafts; a human accepts, edits or rejects.
- A bot fills only fields its source evidences. Unknown stays blank, never a guess.
- Every drafted row points back to its raw artifact. If it doesn't, that's a bug.
- Capture never edits a human row — it proposes a separate completion suggestion.
- Capture is autonomy level 3, always. No promotion, however good the accept rate.
- A rejection, a declined complaint, a signal closed as no action — each is a
  permanent record with a named reviewer and a rationale. Never a deletion.
- Estate access is read-only. The triage agent diagnoses, records and
  recommends; nothing in it restarts, reconfigures or flashes anything.
- The agent follows a controlled procedure, not a prompt. Every diagnosis cites
  the clause that produced it and the revision in force at the time —
  [`plan/TRIAGE.md`](plan/TRIAGE.md).
