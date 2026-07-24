# RecallRadar AI Deployment Notes

## 1. Deployment Goal

RecallRadar should run as a real hosted portfolio app.

Recommended target: Vercel frontend, Render FastAPI backend, Render managed PostgreSQL.

## 2. Local Development

Recommended local services:

- Frontend dev server.
- FastAPI backend.
- PostgreSQL database.

Optional V2 services:

- Redis.
- Object storage.
- pgvector.

## 3. Environment Variables

See `.env.example` for required configuration.

Key variables:

- `DATABASE_URL`
- `OPENFDA_API_KEY`
- `OPENFDA_FOOD_ENFORCEMENT_URL`
- `NEXT_PUBLIC_API_BASE_URL`
- `AI_PROVIDER`
- `HF_API_TOKEN`
- `ENABLE_SEMANTIC_MATCHING`
- `ENABLE_AI_SUMMARIES`

PostgreSQL local validation:

```bash
docker compose down -v
docker compose up -d

cd backend
$env:DATABASE_URL="postgresql+asyncpg://recallradar:recallradar@localhost:5432/recallradar"
.venv/Scripts/alembic upgrade head
.venv/Scripts/python scripts/validate_postgres_workflow.py
.venv/Scripts/python -m uvicorn app.main:app --reload
```

SQLite fallback remains supported:

```bash
DATABASE_URL=sqlite+aiosqlite:///./recallradar.db
```

openFDA can be used without an API key for light development, but an API key is recommended for more reliable usage.

## 4. Recommended Deployment Targets

Chosen portfolio path:

- Vercel for `frontend/`.
- Render web service for `backend/`.
- Render managed PostgreSQL.

Render backend:

```text
Build command: cd backend && pip install -r requirements.txt
Start command: cd backend && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Backend environment:

```text
DATABASE_URL=<Render Postgres internal database URL>
CORS_ALLOWED_ORIGINS=<Vercel frontend URL>
OPENFDA_REFRESH_MINUTES=30
ENABLE_DEMO_RECALL_SEED=false
```

Vercel frontend:

```text
Root directory: frontend
NEXT_PUBLIC_API_BASE_URL=<Render backend URL>
```

## 5. Production Considerations

Before production use, add:

- Authentication.
- Organization or tenant isolation.
- File scanning.
- Rate limiting.
- Background job queue.
- Robust logging.
- Monitoring and alerting.
- Data retention controls.
- Formal safety disclaimers.

## 6. Portfolio Demo Flow

The portfolio deployment should:

- Auto-refresh live openFDA recalls when stale.
- Show live import status in the command bar.
- Let the user select fictional company inventory.
- Runs matching.
- Allows review actions.
- Keep demo recall seeding disabled unless `ENABLE_DEMO_RECALL_SEED=true`.
