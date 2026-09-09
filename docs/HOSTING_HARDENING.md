# Free Hosting Hardening

RecallRadar uses Vercel for both the frontend and FastAPI API, with Neon Free PostgreSQL for persistent hosted data.

> Use synthetic portfolio data only. This unauthenticated MVP is not safe for real customer data.

## Hosted architecture

```text
Vercel frontend
        |
        v
Vercel FastAPI function
        |
        v
Neon Free PostgreSQL
```

This removes the Render web-service and Render database failure modes. Vercel functions can still cold-start and free-tier quotas or policies can change, so this is a durable portfolio setup, not an uptime guarantee.

## Vercel API setup

The backend is deployed as the Vercel project `backend` and exposes:

- API: `https://backend-inky-rho-68.vercel.app`
- Health check: `https://backend-inky-rho-68.vercel.app/health`

In the backend Vercel project, configure this variable as a **Secret** for Production:

```text
DATABASE_URL=<Neon pooled connection string>
```

Never commit or paste the connection string into GitHub, documentation, screenshots, chat, or issue comments.

In the frontend Vercel project, configure this variable as **Config** for Production and Preview:

```text
NEXT_PUBLIC_API_BASE_URL=https://backend-inky-rho-68.vercel.app
```

The frontend value is intentionally public because browsers must call the API. Redeploy the frontend after changing it.

## Verification

Run the read-only smoke check from the repository root:

```bash
python scripts/smoke.py \
  --api https://backend-inky-rho-68.vercel.app \
  --frontend https://recallradar-ai.vercel.app
```

Then open the frontend, select **Portfolio Demo**, and confirm the synthetic recall and review workflow. The deterministic demo can recreate its records in Neon when needed.

## Automated checks and monitoring

- GitHub Actions runs CI on pushes and pull requests.
- A scheduled workflow checks the Vercel API health endpoint.
- Dependabot proposes monthly dependency updates.
- Add independent monitors for:
  - `https://recallradar-ai.vercel.app`
  - `https://backend-inky-rho-68.vercel.app/health`

Monitoring detects failures but cannot repair a broken deployment. GitHub scheduled workflows may also be disabled after long repository inactivity.

## What remains best-effort

- Vercel functions may cold-start after inactivity.
- Neon may scale idle compute to zero.
- Free quotas and provider policies can change.
- openFDA may be unavailable or change its schema.
- The hosted app has no production authentication, tenant isolation, backup policy, or SLA.

The local SQLite quick start and deterministic Portfolio Demo remain the recovery path if hosted services need repair.

## Monthly check

```bash
git pull --ff-only
python scripts/smoke.py \
  --api https://backend-inky-rho-68.vercel.app \
  --frontend https://recallradar-ai.vercel.app
```

Then check Vercel, Neon, GitHub Actions, and independent-monitor dashboards for failed deployments, quota warnings, or paused services.

## References

- [Getting Started](GETTING_STARTED.md)
- [Maintenance and longevity](MAINTENANCE.md)
- [Vercel FastAPI deployment](https://vercel.com/docs/frameworks/backend/fastapi)
- [Vercel Hobby plan](https://vercel.com/docs/plans/hobby)
- [Neon Free plan](https://neon.com/faqs/managed-postgres-databases-free-tier)
