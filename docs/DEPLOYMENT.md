# RecallRadar AI Deployment Notes

## 1. Deployment Goal

RecallRadar should run as a real hosted portfolio app.

Recommended target: Vercel frontend, Vercel FastAPI function, Neon PostgreSQL.

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
- `MAX_UPLOAD_MB`
- `MAX_CSV_ROWS`
- `MAX_UPLOAD_ERRORS`
- `RATE_LIMIT_WINDOW_SECONDS`
- `RATE_LIMIT_READ_PER_WINDOW`
- `RATE_LIMIT_ACTION_PER_WINDOW`
- `RATE_LIMIT_UPLOAD_PER_WINDOW`

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
- Vercel Python runtime for `backend/`.
- Neon Free PostgreSQL.

Vercel backend:

```text
Project: backend
Framework: FastAPI
Entrypoint: backend/app/main.py
```

Backend environment:

```text
APP_ENV=production
DATABASE_URL=<Neon pooled database URL>
CORS_ALLOWED_ORIGINS=<comma-separated allowed origins>
OPENFDA_REFRESH_MINUTES=30
ENABLE_DEMO_RECALL_SEED=false
```

`backend/app/config.py` always includes the deployed portfolio origin (`https://recallradar-ai.vercel.app`) in the allowed CORS origins, while still honoring additional local or custom origins from `CORS_ALLOWED_ORIGINS`.

Free-tier availability checks:

- `.github/workflows/keep-render-warm.yml` sends read-only requests to the API and frontend every 10 minutes.
- This surfaces availability problems and may reduce API cold starts without changing application data.
- GitHub scheduled workflows are best effort and can be delayed or disabled after long repository inactivity.
- The workflow can also be started manually from GitHub Actions.

Vercel frontend:

```text
Root directory: frontend
NEXT_PUBLIC_API_BASE_URL=https://backend-inky-rho-68.vercel.app
```

## 5. Production Considerations

Before production use, add:

- Authentication.
- Organization or tenant isolation.
- File scanning.
- Background job queue.
- Robust logging.
- Monitoring and alerting.
- Data retention controls.
- Formal safety disclaimers.

The public demo now includes best-effort in-memory rate limits, bounded CSV uploads, safe production error responses, security headers, and disabled API documentation when `APP_ENV=production`. The limiter is intentionally dependency-free and resets when the free-tier process restarts; it is not a substitute for authentication or distributed abuse protection.

## 6. Portfolio Demo Flow

The portfolio deployment should:

- Auto-refresh live openFDA recalls when stale.
- Show live import status in the command bar.
- Let the user select fictional company inventory.
- Runs matching.
- Allows review actions.
- Keep demo recall seeding disabled unless `ENABLE_DEMO_RECALL_SEED=true`.
