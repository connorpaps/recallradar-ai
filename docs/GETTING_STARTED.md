# Getting Started with RecallRadar AI

This guide is the shortest path from a fresh clone to a working Portfolio Demo. It is written for a recruiter, reviewer, or developer who has not seen the project before.

> **Safety boundary:** RecallRadar AI is an unauthenticated, single-workspace portfolio MVP. Use synthetic data only. Do not upload real customer inventory or use the hosted app for regulatory decisions.

## What you will run

- **Backend:** FastAPI on `http://127.0.0.1:8100`
- **Frontend:** Next.js on `http://localhost:3000`
- **Database:** SQLite for the fastest local start, or PostgreSQL through Docker for a production-like setup

## Prerequisites

- Git
- Python 3.11 or newer
- Node.js 18.18 or newer and npm
- Optional: Docker Desktop, only if you want PostgreSQL locally

## 1. Clone the repository

```bash
git clone https://github.com/connorpaps/recallradar-ai.git
cd recallradar-ai
```

## 2. Start the backend with SQLite

SQLite is the recommended first run. The backend creates its local tables at startup, so Docker and a database migration are not required for the Portfolio Demo.

### Windows, Git Bash

```bash
cd backend
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m uvicorn app.main:app --host 127.0.0.1 --port 8100
```

### macOS or Linux

```bash
cd backend
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8100
```

Leave this terminal running. Verify the API in a second terminal from the repository root:

```bash
python scripts/smoke.py --api http://127.0.0.1:8100
```

The expected result includes `backend_health: ok HTTP 200`.

## 3. Start the frontend

Open a second terminal at the repository root:

### Windows, Git Bash

```bash
cd frontend
npm ci
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8100 npm run dev
```

### macOS or Linux

```bash
cd frontend
npm ci
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8100 npm run dev
```

Open:

<http://localhost:3000>

The API URL is embedded into the Next.js client at startup or build time. Set it before running `npm run dev`, `npm run build`, or `npm run start`.

## 4. Run the Portfolio Demo

1. Open the dashboard.
2. Select **Portfolio demo** in the command bar.
3. Choose a fictional company if prompted, such as **MetroMart Grocery**.
4. Show the deterministic evidence set:
   - 10 synthetic recalls
   - 5 high-confidence matches
   - 3 medium-confidence matches
5. Open **Review Queue**.
6. Open a candidate to inspect source facts and matching signals.
7. Confirm, dismiss, resolve, or reopen a candidate.
8. Open **Inventory**, upload a small CSV, and click **Run matching for uploaded inventory**.
9. Open the **Recalls** worklist and inspect a recall case file.

Matching suggestions are not confirmed exposure. Human review and official recall notices remain authoritative.

## 5. Optional: use PostgreSQL

The SQLite path is enough for evaluation and the Portfolio Demo. To run the production-like local stack instead:

```bash
docker compose up -d
```

Set `DATABASE_URL` in the repository-root `.env` to the local PostgreSQL database, then run migrations:

### Windows, Git Bash

```bash
cd backend
.venv/Scripts/alembic upgrade head
```

### macOS or Linux

```bash
cd backend
.venv/bin/alembic upgrade head
```

Then start the backend as shown above. Never commit `.env` or credentials.

## 6. Run the verification suite

Backend tests and evaluation:

```bash
cd backend
.venv/Scripts/python -m pytest -q
.venv/Scripts/ruff check app tests scripts
.venv/Scripts/python -m scripts.evaluate_matching
```

On macOS or Linux, replace `.venv/Scripts/...` with `.venv/bin/...`.

Frontend checks:

```bash
cd frontend
npm run lint
npx tsc --noEmit
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8100 npm run build
npm audit --omit=dev --audit-level=high
```

Browser workflow, using the running backend and frontend:

```bash
cd frontend
npm run test:e2e
```

The browser suite uses synthetic fixtures and covers the dashboard, source modes, navigation, filters, CSV upload, matching, review actions, and mobile layout.

## Troubleshooting

### The frontend cannot reach the API

Make sure the backend is running on port `8100`, and start the frontend with:

```bash
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8100 npm run dev
```

If you changed the API URL after a production build, rebuild before running `npm run start`.

### Portfolio Demo refuses to load

This is intentional. Portfolio Demo does not delete uploaded inventory, reviewed decisions, or another company's records. Use a fresh SQLite database, or finish the current review workspace before trying the demo again.

### Port already in use

Stop the existing process using port `8100` or `3000`, then restart the corresponding service. Do not run two copies of the app against the same workspace while testing.

### Live FDA tests

Live openFDA tests are opt-in and are not required for the normal release suite:

```bash
RUN_LIVE_OPENFDA=1 .venv/Scripts/python -m pytest tests/test_openfda_live.py -q
```

## Where to go next

- [Portfolio release guide](PORTFOLIO_RELEASE.md): demo script, release gates, and honest limitations
- [Architecture](ARCHITECTURE.md): system boundaries and data flow
- [API design](API_DESIGN.md): endpoint behavior and source routing
- [Matching evaluation](MATCHING_EVALUATION.md): methodology and measured results
- [Test plan](TEST_PLAN.md): automated coverage and CI behavior
