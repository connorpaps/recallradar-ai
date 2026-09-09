# Keeping RecallRadar Available Over Time

RecallRadar is a portfolio deployment, not an unattended production service. The application code is versioned and tested, but free hosting plans and external data sources have lifecycle limits.

## What is already automated

- GitHub Actions runs CI on pushes to `main` and pull requests.
- A scheduled GitHub Actions workflow pings the Render API health endpoint every 10 minutes.
- The frontend is deployed as a Vercel project from the GitHub repository.
- The backend uses Render Postgres rather than an ephemeral SQLite file.
- Backend and frontend dependencies are pinned through `requirements.txt` and `package-lock.json`.
- Dependabot opens monthly update pull requests for Python, npm, GitHub Actions, and Docker dependencies.

## Important free-tier limits

These are hosting-plan constraints, not bugs in RecallRadar:

1. **Render Free web service sleep:** Render can spin down an idle free web service after 15 minutes. The next request can take about a minute while it starts again. The keep-warm workflow reduces this risk but cannot guarantee zero cold starts.
2. **Render Free Postgres expiry:** Render documents that free Postgres databases expire 30 days after creation. After expiry, the database is inaccessible until upgraded, with a limited grace period before deletion. Upgrade the database or move it to another persistent provider before treating the hosted app as a long-term demo.
3. **GitHub scheduled workflow suspension:** GitHub automatically disables scheduled workflows in public repositories after 60 days without repository activity. Re-enable the keep-warm workflow after returning from a long absence, or use an independent uptime monitor.
4. **Free usage quotas:** Render and Vercel can restrict or suspend services if plan limits are exceeded. Check both dashboards before a public presentation.
5. **openFDA dependency:** Live mode depends on the availability, schema, rate limits, and content of the public openFDA API. Portfolio Demo remains deterministic and does not depend on that service.

## Before leaving the project unattended

- Confirm the Render database is not on an expiring free plan, or record its expiry date in a private reminder.
- Confirm the Render service and Vercel project are not paused or over quota.
- Confirm the `Keep Render API warm` workflow is enabled in GitHub Actions.
- Confirm the latest `CI` workflow is green.
- Do not rely on the keep-warm workflow as the only monitor. An independent monitor such as UptimeRobot, Better Uptime, or a similar service is more reliable because GitHub can suspend scheduled workflows.
- Do not store important business data in this deployment. It is an unauthenticated synthetic portfolio demo.

## Monthly maintenance check

Run this from a fresh checkout or the maintained local clone:

```bash
git pull --ff-only
cd backend
.venv/Scripts/python -m pytest -q
.venv/Scripts/ruff check app tests scripts
.venv/Scripts/python -m scripts.evaluate_matching
cd ../frontend
npm ci
npm run lint
npx tsc --noEmit
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8100 npm run build
npm audit --omit=dev --audit-level=high
```

Then run the read-only hosted smoke check from the repository root:

```bash
python scripts/smoke.py --api https://recallradar-api.onrender.com --frontend https://recallradar-ai.vercel.app
```

Only describe the hosted deployment as available when that command succeeds. A Render cold start may require one bounded retry, but do not hide repeated failures.

## If the hosted app is no longer worth maintaining

The repository remains runnable locally with synthetic data. The lowest-cost fallback is to use the SQLite quick start in [Getting Started](GETTING_STARTED.md) and present the local Portfolio Demo. The hosted deployment can be recreated from `render.yaml` and the Vercel project settings, but database contents should not be assumed recoverable after a free database expires.

## References

- [Getting Started](GETTING_STARTED.md)
- [Portfolio release guide](PORTFOLIO_RELEASE.md)
- [Render free plans](https://render.com/docs/free)
- [GitHub scheduled workflows](https://docs.github.com/actions/using-workflows/events-that-trigger-workflows)
