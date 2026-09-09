# Keeping RecallRadar Available Over Time

RecallRadar is a portfolio deployment, not an unattended production service. The application code is versioned and tested, but free hosting plans and external data sources have lifecycle limits.

## What is already automated

- GitHub Actions runs CI on pushes to `main` and pull requests.
- A scheduled GitHub Actions workflow pings the Vercel API health endpoint every 10 minutes.
- The frontend is deployed as a Vercel project from the GitHub repository.
- The hosted backend uses Neon PostgreSQL rather than an ephemeral SQLite file.
- Backend and frontend dependencies are pinned through `requirements.txt` and `package-lock.json`.
- Dependabot opens monthly update pull requests for Python, npm, GitHub Actions, and Docker dependencies.

## Important free-tier limits

These are hosting-plan constraints, not bugs in RecallRadar:

1. **Vercel Function cold starts:** Vercel can scale inactive functions down. The frontend is CDN-served, while the API may have a first-request delay. No free platform guarantees zero cold starts.
2. **Neon Free limits:** Neon keeps the database available but can scale idle compute to zero and may change free-tier quotas or policies. Check the current plan limits periodically.
3. **GitHub scheduled workflow suspension:** GitHub automatically disables scheduled workflows in public repositories after 60 days without repository activity. Re-enable the keep-warm workflow after returning from a long absence, or use an independent uptime monitor.
4. **Free usage quotas:** Neon, Vercel, and GitHub can restrict services or workflows if plan limits are exceeded. Check their dashboards before a public presentation.
5. **openFDA dependency:** Live mode depends on the availability, schema, rate limits, and content of the public openFDA API. Portfolio Demo remains deterministic and does not depend on that service.

## Before leaving the project unattended

- Confirm the Neon project and Vercel API/frontend projects are active and within quota.
- Confirm the `Keep Vercel API warm` workflow is enabled in GitHub Actions.
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
python scripts/smoke.py --api https://backend-inky-rho-68.vercel.app --frontend https://recallradar-ai.vercel.app
```

Only describe the hosted deployment as available when that command succeeds. A Vercel function cold start may require one bounded retry, but do not hide repeated failures.

## If the hosted app is no longer worth maintaining

The repository remains runnable locally with synthetic data. The lowest-cost fallback is to use the SQLite quick start in [Getting Started](GETTING_STARTED.md) and present the local Portfolio Demo. The hosted deployment can be recreated from the Vercel project settings and Neon connection configuration.

## References

- [Getting Started](GETTING_STARTED.md)
- [Portfolio release guide](PORTFOLIO_RELEASE.md)
- [Vercel Hobby plan](https://vercel.com/docs/plans/hobby)
- [Neon Free plan](https://neon.com/faqs/managed-postgres-databases-free-tier)
- [GitHub scheduled workflows](https://docs.github.com/actions/using-workflows/events-that-trigger-workflows)
