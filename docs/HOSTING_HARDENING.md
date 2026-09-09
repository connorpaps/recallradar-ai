# Free Hosting Hardening

This guide replaces the expiring Render Free Postgres database with a non-expiring free PostgreSQL provider while keeping the existing Render backend and Vercel frontend.

> Use synthetic portfolio data only. Do not migrate real customer data into this unauthenticated MVP.

## Recommended target

```text
Vercel frontend
        |
        v
Render FastAPI backend
        |
        v
Neon Free PostgreSQL
```

Neon Free is preferable here because its current plan is not time-limited. Compute scales to zero while the database and data remain available. Verify current limits before relying on the service:

<https://neon.com/faqs/managed-postgres-databases-free-tier>

## One-time provider setup

1. Create a Neon project in the same broad region as the Render backend.
2. Copy the pooled PostgreSQL connection string from Neon. Keep it private.
3. In Render, open the `recallradar-api` service and set `DATABASE_URL` to the Neon connection string.
4. Redeploy the backend. The Render start command runs `alembic upgrade head` before starting FastAPI.
5. Run the read-only smoke check:

```bash
python scripts/smoke.py \
  --api https://recallradar-api.onrender.com \
  --frontend https://recallradar-ai.vercel.app
```

6. Open the frontend and select **Portfolio demo**. Confirm the synthetic recall and review workflow works.
7. Only after the new database is verified, remove or cancel the expiring Render Postgres database. Do not delete it first.

Never put the Neon connection string in Git, README files, screenshots, chat, or issue comments. Store it only in Render's environment settings and a password manager.

## Add independent uptime monitoring

Create a free monitor with UptimeRobot, Better Uptime, or another independent provider:

- Monitor 1: `https://recallradar-ai.vercel.app`
- Monitor 2: `https://recallradar-api.onrender.com/health`
- Interval: five minutes, or the provider's closest free interval
- Alert: email notification

This is more reliable than GitHub Actions alone because GitHub can disable scheduled workflows after 60 days without repository activity.

The monitor may wake the Render backend from sleep. A first request can still be slow on the free Render plan, so use a timeout of at least 90 seconds if the monitor supports it.

## What remains best-effort

- Render Free web services can still cold-start after inactivity.
- Free providers can change quotas or policies.
- openFDA can be unavailable or change its public data.
- The app has no production authentication, tenant isolation, backup policy, or SLA.
- Uptime monitoring detects failure; it does not repair a broken deployment.

The deterministic Portfolio Demo and local SQLite quick start ensure that the project remains demonstrable even if the hosted service needs repair.

## Monthly check

```bash
git pull --ff-only
python scripts/smoke.py \
  --api https://recallradar-api.onrender.com \
  --frontend https://recallradar-ai.vercel.app
```

Then check the Render, Neon, Vercel, and monitor dashboards for paused services, quota warnings, failed deploys, or database expiry notices.

## References

- [Getting Started](GETTING_STARTED.md)
- [Maintenance and longevity](MAINTENANCE.md)
- [Render free plans](https://render.com/docs/free)
- [GitHub scheduled workflows](https://docs.github.com/actions/using-workflows/events-that-trigger-workflows)
