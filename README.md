# RecallRadar AI

RecallRadar AI is a multimodal food-safety intelligence platform that helps grocery stores, restaurants, campus dining teams, food banks, and small retailers identify recalled products in their inventory before they reach customers.

The app ingests public FDA recall data, accepts local inventory uploads, matches recalls against inventory items, explains why products may be affected, and gives staff a review workflow for confirming, dismissing, or resolving recall risks.

## Why This Project Exists

Food recalls are operationally messy. Public notices often use inconsistent product names, vague distribution regions, incomplete UPCs, and long free-text descriptions. Smaller organizations may track inventory through spreadsheets, supplier invoices, receipts, and staff knowledge instead of enterprise recall systems.

RecallRadar AI turns that fragmented information into an evidence-based workflow:

1. Import recent food recalls.
2. Upload local inventory.
3. Score likely recall matches.
4. Explain the evidence behind each match.
5. Let a human reviewer confirm, dismiss, or resolve the case.

## Portfolio Goal

This project is designed to stand out as a 2025 software engineering portfolio project by combining:

- Real-world public APIs.
- Backend data modeling.
- AI-assisted matching.
- Human-in-the-loop review.
- Production-minded UX.
- Auditability and confidence scoring.
- Clear V1/V2 architecture.

The first version focuses on a complete end-to-end workflow instead of trying to integrate every possible AI model immediately.

## MVP Scope

V1 includes:

- openFDA food recall ingestion.
- Inventory CSV upload.
- Recall-to-inventory matching.
- Match confidence scoring.
- Human-readable match explanations.
- Recall inbox.
- Recall detail/action page.
- Review queue.
- Basic dashboard metrics.
- Seed data for demos.

V2 adds:

- Persisted operational exposure scores separate from match confidence.
- Explainable exposure factors for quantity, recall class, location criticality, supplier overlap, and review status.
- Richer location-aware demo inventory.
- A meaningful Risk Radar where ring, sector, color, and size encode exposure data.

V1 intentionally excludes:

- Shelf image analysis.
- Invoice/document question answering.
- USDA FSIS integration.
- Barcode scanning.
- Multi-location permissions.
- Email/SMS alerting.
- Time-series forecasting.

Those are planned V2 extensions.

## Recommended Stack

- Frontend: Next.js, TypeScript, Tailwind CSS.
- Backend: FastAPI, Python.
- Database: PostgreSQL.
- ORM: SQLAlchemy or SQLModel.
- Migrations: Alembic.
- Background jobs: FastAPI background tasks for V1, Redis/RQ or Celery later.
- AI/matching: deterministic scoring plus semantic similarity.
- Vector search: pgvector in V2.
- Testing: pytest for backend, Playwright for frontend flows.
- Deployment: Docker Compose locally, Render/Railway/Fly.io or cloud containers later.

## Local Development

Start PostgreSQL:

```bash
docker compose up -d
```

For a clean production-like validation pass:

```bash
docker compose down -v
docker compose up -d
cd backend
$env:DATABASE_URL="postgresql+asyncpg://recallradar:recallradar@localhost:5432/recallradar"
.venv/Scripts/alembic upgrade head
```

Install backend dependencies:

```bash
cd backend
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
```

Start the backend:

```bash
cd backend
.venv/Scripts/python -m uvicorn app.main:app --reload
```

Install frontend dependencies:

```bash
cd frontend
npm install
```

Start the frontend:

```bash
cd frontend
npm run dev
```

Open:

```text
http://localhost:3000
```

Recommended demo sequence:

1. Open the app; live openFDA recall data refreshes automatically.
2. Pick a company inventory profile from the top command bar.
3. Click `Run matching`.
4. Open the review queue.
5. Confirm, dismiss, or resolve matches.

## Deployment

Production deployment target:

- Frontend: Vercel, root directory `frontend`.
- Backend: Render web service from this repo.
- Database: Render managed PostgreSQL.

Render backend:

```text
Build command: cd backend && pip install -r requirements.txt
Start command: cd backend && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Render backend env:

```text
DATABASE_URL=<Render Postgres internal database URL>
CORS_ALLOWED_ORIGINS=<Vercel frontend URL>
OPENFDA_REFRESH_MINUTES=30
ENABLE_DEMO_RECALL_SEED=false
AI_PROVIDER=local
ENABLE_SEMANTIC_MATCHING=false
ENABLE_AI_SUMMARIES=false
```

Vercel frontend env:

```text
NEXT_PUBLIC_API_BASE_URL=<Render backend URL>
```

Final deployed smoke:

1. Open the Vercel URL.
2. Confirm FDA refresh status appears in the command bar.
3. Select a company in the command bar.
4. Click `Run matching`.
5. Confirm the radar and review queue populate.

Run checks:

```bash
cd backend
.venv/Scripts/python -m pytest

cd ../frontend
npm run build

# Requires backend and frontend dev servers to already be running.
npm run test:e2e
```

Apply migrations when using an existing local database:

```bash
cd backend
.venv/Scripts/alembic upgrade head
```

## Project Structure

Recommended structure:

```text
RecallRadar_Project/
  frontend/
  backend/
  docs/
  docker-compose.yml
  README.md
  .env.example
```

## Core User Flow

1. User opens the dashboard.
2. App shows active recalls and unresolved match counts.
3. User imports recent openFDA recalls.
4. User uploads an inventory CSV.
5. System scores recall-to-inventory matches.
6. User opens a recall detail page.
7. App shows affected product details, matched inventory, confidence, and evidence.
8. User marks each match as `confirmed`, `dismissed`, or `resolved`.
9. Dashboard and review queue update.

## Hugging Face Task Roadmap

V1 uses AI-ready architecture and can support:

- Text classification.
- Token classification.
- Summarization.
- Sentence similarity.
- Text ranking.
- Question answering.

V2 can add:

- Document question answering.
- Image-to-text.
- Visual question answering.
- Object detection.
- Image feature extraction.
- Translation.
- Automatic speech recognition.

Implemented AI extension points:

- Feature-flagged Hugging Face semantic similarity for recall-to-inventory matching.
- Feature-flagged Hugging Face recall summaries.
- Deterministic fallback when flags are disabled, token is absent, or the provider fails.
- Model activity recorded in `model_runs`.

## Demo Script

1. Open the Imports console.
2. Let live openFDA data auto-refresh, or click `Live FDA import`.
3. Pick a demo company inventory profile such as `MetroMart Grocery` or `Oak & Ember Steakhouse`.
4. Click `Run matching`.
5. Open the dashboard to inspect exposure.
6. Open the review queue and confirm, dismiss, resolve, or reopen a case.
7. Use the recalls filters to narrow live openFDA records by class and exposure.

## Screenshots

- [Dashboard](docs/screenshots/dashboard.png)
- [Recall case file](docs/screenshots/recall-case-file.png)
- [Review queue](docs/screenshots/review-queue.png)
- [Imports console](docs/screenshots/imports-console.png)
- [Inventory company profiles](docs/screenshots/inventory-companies.png)
- [Live/demo recall filters](docs/screenshots/recalls-live-demo.png)

## Documentation

- [MVP_SPEC.md](docs/MVP_SPEC.md)
- [DATA_MODEL.md](docs/DATA_MODEL.md)
- [API_DESIGN.md](docs/API_DESIGN.md)
- [AI_MATCHING_SPEC.md](docs/AI_MATCHING_SPEC.md)
- [DEVELOPMENT_PLAN.md](docs/DEVELOPMENT_PLAN.md)
- [UX_SPEC.md](docs/UX_SPEC.md)
- [TEST_PLAN.md](docs/TEST_PLAN.md)
- [DEPLOYMENT.md](docs/DEPLOYMENT.md)
- [AGENT_SKILLS.md](docs/AGENT_SKILLS.md)
- [ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Resume-Ready Summary

Built a food-safety intelligence platform that ingests FDA recall data, matches recalls against uploaded inventory, generates explainable confidence scores, and provides an auditable human review workflow for resolving potentially affected products.

- Validated a production-like Docker/PostgreSQL workflow with Alembic migrations and async SQLAlchemy.
- Added Playwright e2e coverage for core routes, CSS loading, and human review actions.
- Integrated optional Hugging Face inference for semantic matching and summaries with safe deterministic fallbacks.
