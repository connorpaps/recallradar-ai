# RecallRadar AI

RecallRadar AI is a food-safety operations app that helps a team answer a simple question quickly: "Do we have recalled product in our inventory right now?"

It pulls live food recall data from openFDA, provides a deterministic Portfolio Demo mode, lets a user load fictional company inventory, runs explainable recall-to-inventory matching, and gives staff a clean review workflow for confirming, dismissing, or resolving possible exposure.

Live deployment:

- [Open the frontend demo](https://recallradar-ai.vercel.app)
- [Check API health](https://backend-inky-rho-68.vercel.app/health)

> **Safety boundary:** This is a no-login, single-workspace portfolio MVP. Use the hosted instance with synthetic demo data only. Do not upload real customer inventory or rely on it for regulatory action until authentication, tenant isolation, access control, retention, and production monitoring are added.

## What It Does

Most public recall notices are messy to work with in real life. Product names vary, UPCs are incomplete, lot details are inconsistent, and smaller organizations often manage stock with spreadsheets or lightweight internal tools instead of enterprise systems.

RecallRadar AI turns that into a practical workflow:

1. Pull the latest FDA recall data.
2. Load a company inventory profile.
3. Match recalled products against local stock.
4. Show why each match was flagged.
5. Let a human reviewer decide what is real and what is noise.

## Why This Feels Real

This is not just a static dashboard with fake charts.

- Recalls come from the live openFDA food enforcement API.
- The app auto-refreshes live recall data on launch when the last successful refresh is stale.
- Matching is explainable and reviewable instead of being a black-box score.
- Inventory stays intentionally fictional so the demo is repeatable and safe to show.
- The deployed app uses a real hosted frontend, backend, and Postgres database.

## AI and Hugging Face Integration

The project was designed around practical Hugging Face inference tasks rather than adding a model as decoration. The release path is deterministic first, with an optional Hugging Face semantic signal available when configured:

- **Feature Extraction:** generate embeddings for recall and inventory text.
- **Sentence Similarity:** compare those embeddings with cosine similarity.
- **Human-gated decision support:** use the model score as supporting evidence alongside product, brand, UPC, lot, and distribution signals.
- **Optional summarization:** generate concise recall summaries when an inference provider and model are configured.

The hosted Portfolio Demo disables external model calls so its results remain repeatable, free to run, and available even when an inference provider is unavailable. The current implementation covers optional semantic similarity and summarization; document QA, entity extraction, and image analysis remain documented roadmap work rather than completed features. See the [Hugging Face task reference](https://huggingface.co/docs/inference-providers/en/tasks/index) and the [AI matching specification](docs/AI_MATCHING_SPEC.md).

### Hugging Face task alignment

| Hugging Face task | RecallRadar use | Status |
| --- | --- | --- |
| Feature Extraction | Create embeddings for recall and inventory text | Implemented, optional |
| Sentence Similarity | Add semantic similarity as supporting match evidence | Implemented, optional |
| Summarization | Produce concise recall summaries | Implemented, optional |
| Token Classification | Extract brands, products, lot codes, allergens, and regions | Roadmap |
| Document Question Answering and Visual Document Retrieval | Read invoices, packing slips, and recall notices | Roadmap |
| Image-to-Text, Object Detection, and Image Feature Extraction | Analyze labels, shelf photos, and package similarity | Roadmap |

The project does not claim to implement the full Hugging Face task catalog. It applies a small, relevant set of NLP tasks to a concrete operations problem, with multimodal extensions identified as future work.

## Data modes and product flow

For the user-facing experience:

- Live FDA mode uses public openFDA data and labels weak matches as possible candidates.
- Portfolio Demo mode uses bundled synthetic recalls and inventory with repeatable labeled results.
- Inventory comes from fictional company profiles or CSV upload.
- CSV upload validates and stores rows first; matching is an explicit next step.
- Matching uses a release threshold of `0.50` to avoid surfacing weak lexical coincidences.

Live FDA flow:

1. Open the app.
2. Let live FDA recalls load automatically.
3. Choose a company inventory.
4. Click `Run matching`.
5. Review the dashboard, recall queue, and evidence.

Portfolio Demo flow:

1. Open the app.
2. Choose `Portfolio demo` in the command bar.
3. Show the deterministic five high-confidence and three medium-confidence examples.
4. Open the review queue and inspect the evidence trail.

The modes remain visibly separate. Portfolio Demo is not live FDA data.

## Main Features

- Live openFDA food recall import.
- Auto-refresh status with throttling.
- Fictional demo company inventory profiles.
- Inventory CSV upload support.
- Explainable recall-to-inventory matching.
- Deterministic Portfolio Demo mode with labeled evaluation fixtures.
- Repeatable precision/recall evaluation harness.
- Optional Hugging Face embedding-based semantic similarity.
- Match confidence and review states.
- Dashboard with exposure and workload views.
- Recall case file and review queue workflow.
- Production-minded deployment on Vercel + Neon PostgreSQL.
- Free-tier Vercel health workflow with a read-only scheduled health check.

## Deployed Demo Walkthrough

Use this flow when showing the project:

1. Open `https://recallradar-ai.vercel.app`.
2. Choose `Portfolio demo` for the deterministic walkthrough.
3. Show the five high-confidence and three medium-confidence examples.
4. Explain that match confidence and operational exposure are separate signals.
5. Open the recalls worklist and pick a case.
6. Open the review queue and confirm, dismiss, resolve, or reopen a match.
7. Optionally switch back to Live FDA mode and explain why real source data is noisier.

Good companies to use in a demo:

- `Campus Table Dining`
- `MetroMart Grocery`
- `Oak & Ember Steakhouse`

## Screenshots

### Dashboard

![RecallRadar AI dashboard](docs/screenshots/dashboard.png)

### Recall case file

![RecallRadar AI recall case file](docs/screenshots/recall-case-file.png)

### Review queue

![RecallRadar AI review queue](docs/screenshots/review-queue.png)

## Engineering Hardening and Verification

Completed before deployment:

- Deployed frontend to Vercel.
- Deployed backend as a Vercel FastAPI function.
- Moved production persistence to Postgres.
- Added import status tracking in the database.
- Added `GET /recalls/imports/status`.
- Throttled auto-refresh to once every 30 minutes unless manually forced.
- Added a free GitHub Actions health check every 10 minutes to surface API availability issues.
- Moved backend CORS to environment configuration.
- Kept demo recall seeding disabled by default.
- Added best-effort in-memory rate limits and bounded CSV uploads for the public no-login demo.
- Added safe production error responses, security headers, and disabled API docs in production.
- Added a read-only smoke script; rerun it immediately before claiming hosted availability.

The local release candidate was verified with backend tests, Ruff, frontend lint/build, Playwright browser coverage, and the deterministic matching evaluator. Hosted availability remains an operational check, not a permanent claim. Run `python scripts/smoke.py --api <api-url> --frontend <frontend-url>` before a public demonstration.

For long-term availability, read the [maintenance guide](docs/MAINTENANCE.md). Vercel Functions and Neon can still scale idle compute down, and GitHub can disable scheduled workflows after 60 days without repository activity. An independent uptime monitor remains useful for an unattended hosted demo over multiple months.

For the current Vercel plus Neon deployment and maintenance notes, see [Free Hosting Hardening](docs/HOSTING_HARDENING.md). Independent uptime monitoring is optional redundancy; the repository already includes a model-free GitHub health workflow.

## Stack

- Frontend: Next.js, TypeScript, Tailwind CSS
- Backend: FastAPI, Python
- Database: PostgreSQL
- ORM: SQLAlchemy
- Migrations: Alembic
- Testing: pytest, Playwright
- Hosting: Vercel + Neon

## Local Development

For the shortest fresh-clone path, follow the [Getting Started guide](docs/GETTING_STARTED.md). It includes the SQLite quick start, optional PostgreSQL setup, Portfolio Demo walkthrough, troubleshooting, and verification commands.

Start PostgreSQL:

```bash
docker compose up -d
```

Install backend dependencies:

```bash
cd backend
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
```

Run migrations:

```bash
cd backend
.venv/Scripts/alembic upgrade head
```

Start backend:

```bash
cd backend
.venv/Scripts/python -m uvicorn app.main:app --reload
```

Install frontend dependencies:

```bash
cd frontend
npm install
```

Start frontend:

```bash
cd frontend
npm run dev
```

Open:

```text
http://localhost:3000
```

## Environment

Backend:

```text
APP_ENV=production
DATABASE_URL=<database url>
CORS_ALLOWED_ORIGINS=<comma separated frontend origins>
OPENFDA_REFRESH_MINUTES=30
OPENFDA_API_KEY=<optional>
ENABLE_DEMO_RECALL_SEED=false
MAX_UPLOAD_MB=2
MAX_CSV_ROWS=5000
RATE_LIMIT_WINDOW_SECONDS=60
RATE_LIMIT_READ_PER_WINDOW=120
RATE_LIMIT_ACTION_PER_WINDOW=12
RATE_LIMIT_UPLOAD_PER_WINDOW=5
```

Frontend:

```text
NEXT_PUBLIC_API_BASE_URL=<backend base url>
```

## Testing

Backend:

```bash
cd backend
.venv/Scripts/python -m pytest
.venv/Scripts/ruff check app tests scripts
.venv/Scripts/python -m scripts.evaluate_matching
```

Frontend build:

```bash
cd frontend
npm run lint
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8100 npm run build
```

Frontend e2e:

```bash
cd frontend
npm run test:e2e
```

See [the portfolio release guide](docs/PORTFOLIO_RELEASE.md) and [matching evaluation](docs/MATCHING_EVALUATION.md) for the release gate, demo script, measured metrics, and production limitations.

## Project Structure

```text
frontend/
backend/
docs/
docker-compose.yml
render.yaml (legacy deployment reference, not used by the current host)
README.md
```

## Documentation

- [Deployment notes](docs/DEPLOYMENT.md)
- [Getting started](docs/GETTING_STARTED.md)
- [Maintenance and longevity](docs/MAINTENANCE.md)
- [Free hosting hardening](docs/HOSTING_HARDENING.md)
- [Architecture](docs/ARCHITECTURE.md)
- [API design](docs/API_DESIGN.md)
- [Data model](docs/DATA_MODEL.md)
- [AI matching spec](docs/AI_MATCHING_SPEC.md)
- [UX spec](docs/UX_SPEC.md)
- [Test plan](docs/TEST_PLAN.md)

## Resume-Ready Summary

Built and deployed a food-safety intelligence platform that ingests live FDA recall data, matches recalls against inventory, explains evidence behind potential exposure, and supports human-in-the-loop review with a production-style full-stack architecture.
