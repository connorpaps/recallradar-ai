# Portfolio release guide

## Product position

RecallRadar AI is a full-stack food-recall decision desk. It imports public openFDA enforcement records, loads fictional inventory, scores explainable recall-to-inventory candidates, prioritizes operational exposure, and keeps final decisions human-gated.

This release has two explicit data modes:

1. **Live FDA mode** uses current openFDA records. The data can be noisy, and low-confidence candidates are only possible matches.
2. **Portfolio Demo mode** loads bundled synthetic recalls and MetroMart Grocery inventory. It is deterministic, labeled, and designed to show five high-confidence and three medium-confidence examples with no false positives under the release evaluator.

The modes are intentionally separate. The demo does not manipulate live FDA records to make the product look better.
Portfolio Demo also refuses to replace customer-uploaded inventory or another demo company; it returns `409 Conflict` instead.

> **Hosted-use boundary:** The public no-login deployment is for synthetic portfolio demonstrations only. It is not safe for real customer inventory or shared operational use because the current MVP has no authentication or tenant isolation.

## Fast local verification

Backend:

```text
cd backend
.venv/Scripts/python -m pytest -q
.venv/Scripts/ruff check app tests scripts
.venv/Scripts/python -m scripts.evaluate_matching
CORS_ALLOWED_ORIGINS=http://127.0.0.1:3000 RATE_LIMIT_ACTION_PER_WINDOW=100 RATE_LIMIT_READ_PER_WINDOW=500 RATE_LIMIT_UPLOAD_PER_WINDOW=20 .venv/Scripts/python -m uvicorn app.main:app --host 127.0.0.1 --port 8100
```

Frontend, in a second terminal:

```text
cd frontend
npm ci
npm run lint
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8100 npm run build
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8100 npm run start -- --hostname 127.0.0.1 --port 3000
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8100 npm run test:e2e
```

Open `http://localhost:3000`, choose **Portfolio demo** in the command bar, and follow the labeled review queue.

## Primary demo script

1. Open the dashboard and explain that the default mode is live FDA data.
2. Select **Portfolio demo**.
3. Show the banner with ten synthetic recalls, five high-confidence matches, and three medium-confidence matches.
4. Open the review queue and explain the difference between match confidence and operational exposure.
5. Open a recall case file and inspect source facts, signal traces, and human review controls.
6. Open Inventory, upload a small CSV, and show that upload validation is separate from matching.
7. Click **Run matching for uploaded inventory** and show the generated reviewable candidates.
8. Confirm or dismiss one candidate, then point to the audit evidence.
9. On a narrow viewport, open the mobile navigation and show the same core routes remain reachable.

## Release gate

A portfolio release is ready when all of the following are true:

- Backend tests pass.
- Ruff passes.
- Frontend ESLint passes without interactive setup.
- Frontend production build passes with the intended API URL embedded before build.
- Browser tests pass for routes, CSS, upload, matching, review actions, Portfolio Demo mode, and mobile navigation.
- Matching evaluation reports at least `0.95` precision and recall, at least three high-confidence predictions, and at least five known matches.
- Live FDA and Portfolio Demo labels remain visibly distinct.
- Confidence and exposure are described as separate concepts.
- The hosted read-only smoke test passes for backend health, dashboard summary, and frontend home.
- README, screenshots, and resume claims match the verified implementation.

## Honest limitations

This is a polished single-workspace portfolio MVP, not a production food-safety platform. It currently does not provide authentication, tenant isolation, real actor identity, malware scanning, a background job queue, distributed rate limiting, formal monitoring, retention/deletion controls, or automated regulatory action. Human review remains mandatory, and the system does not replace official food-safety guidance.

## Hosted smoke test

The smoke test is read-only and does not import records or change review state:

```text
python scripts/smoke.py --api https://backend-inky-rho-68.vercel.app --frontend https://recallradar-ai.vercel.app
```

Run it immediately before a public demonstration. Free-tier cold starts may require a generous timeout or a second bounded attempt outside the release claim, but never report a deployment as healthy without a successful response.
