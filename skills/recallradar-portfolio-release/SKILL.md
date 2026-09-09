---
name: recallradar-portfolio-release
description: Verify RecallRadar portfolio releases end to end.
version: 0.1.0
author: Con (connorpaps), Hermes Agent
license: MIT
platforms: [windows, macos, linux]
metadata:
  hermes:
    tags: [RecallRadar, portfolio, release, verification]
    related_skills: []
---
# RecallRadar Portfolio Release Skill

Use this project-local workflow when preparing RecallRadar for a portfolio or resume release. It keeps live FDA data separate from deterministic evidence, requires matching-quality evidence, and treats the app as a single-workspace demo rather than production SaaS.

## When to Use

- Use before presenting RecallRadar in a portfolio, resume, interview, or demo.
- Use after changes to matching, imports, review actions, deployment, or the frontend shell.
- Do not use this workflow to claim authentication, tenant isolation, or production readiness that the repository does not provide.

## Prerequisites

- Run from the repository root.
- Backend dependencies are installed in `backend/.venv`, and that environment is activated before running Python commands.
- Frontend dependencies are installed in `frontend/node_modules`.
- Do not place credentials, real inventory, or personal data in fixtures or logs.

## Quick Reference

```text
python -m pytest -q                                                 # workdir: backend, activated venv
python -m ruff check app tests scripts                               # workdir: backend, activated venv
python -m scripts.evaluate_matching                                  # workdir: backend, activated venv
npm run lint                                                       # workdir: frontend
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8100 npm run build       # Bash, workdir: frontend
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8100 npm run test:e2e   # Bash, workdir: frontend
python scripts/smoke.py --api <api-url> --frontend <frontend-url> # workdir: repository root
```

Activate the backend environment with `source .venv/Scripts/activate` in Git Bash on Windows or `source .venv/bin/activate` on macOS/Linux. On Windows Command Prompt, set the build-time API with `set NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8100 && npm run build` and run the E2E suite with `set NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8100 && npm run test:e2e`.

## Procedure

1. Run the backend tests and Ruff checks. Completion means both exit successfully.
2. Run `python -m scripts.evaluate_matching` from `backend`. Completion means precision and recall are at least `0.95`, with at least three high-confidence and five total known matches. The command exits nonzero if the release gate regresses.
3. Build the frontend with `NEXT_PUBLIC_API_BASE_URL` set before the build. Completion means the generated bundle points at the intended API.
4. Run the browser suite against a clean backend and frontend process. Completion means live routes, CSV upload, explicit matching, review actions, portfolio demo mode, and mobile navigation pass.
5. Open Portfolio Demo mode and confirm the page labels synthetic recalls and distinguishes match confidence from operational exposure.
6. Run the read-only smoke script against any hosted deployment. Completion means backend health, dashboard summary, and frontend home each return HTTP 200.
7. Review README and release documentation. Completion means claims match verified behavior and known limitations remain visible.

## Pitfalls

- `NEXT_PUBLIC_API_BASE_URL` is embedded at build time. Starting Next.js with a new value after `next build` does not change the bundle.
- Live openFDA tests are opt-in with `RUN_LIVE_OPENFDA=1`; release CI uses synthetic Portfolio Demo fixtures and does not depend on the upstream service.
- Portfolio Demo is non-destructive: it refuses to replace customer-uploaded inventory or another demo company. Start from the MetroMart demo workspace or an empty workspace.
- Do not rebuild `.next` under a running production server. Restart the server after every build.
- Live FDA data is intentionally noisy. Low-confidence candidates are not confirmed exposure.
- Portfolio Demo mode is deterministic synthetic evidence, not FDA data.
- CSV upload validates and stores inventory first. Matching is an explicit human-controlled next step.

## Verification

Record the exact test counts, evaluation metrics, smoke endpoints, and current limitations in the release notes. A release is not complete if only the unit tests pass while the browser workflow or hosted smoke check is unverified.
