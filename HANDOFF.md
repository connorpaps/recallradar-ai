# RecallRadar AI Handoff

Last updated: July 24, 2026

## Latest Live-Only Recall Data Update

Implemented live-only recall workflow:
- User-facing recall data now defaults to live openFDA records.
- Added client-side live data bootstrap in the app shell: `POST /recalls/import/openfda` with `{ "limit": 50 }` on full page load/refresh.
- Removed user-facing demo recall action/copy from the dashboard/imports/recall filters.
- Dashboard and review/match lists now count and show openFDA recall matches by default.
- `POST /matches/run` now honors `recall_source`, defaulting to `openfda`.
- `POST /recalls/seed` is now disabled unless `ENABLE_DEMO_RECALL_SEED=true`.
- Fictional company inventories remain available through `/inventory/demo-companies`, `/inventory/seed`, and `/inventory/seed-company`.

Verification:
- Backend tests: `15 passed` with real openFDA import coverage.
- Frontend build: passed.
- Playwright e2e: `10 passed` against live openFDA import path.

Current running servers:
- Backend: `http://127.0.0.1:8000` with network-enabled process.
- Frontend: `http://localhost:3000`.

## Latest Deployment-Ready Update

Implemented deploy-prep for Vercel + Render:
- Added import status persistence in `import_statuses`.
- Added Alembic migration `20260724_0003_import_statuses`.
- Added `GET /recalls/imports/status`.
- Live FDA auto-refresh is now throttled by `OPENFDA_REFRESH_MINUTES`, default `30`.
- Command bar shows FDA refresh status/last success/failure.
- Manual `Live FDA import` still force-refreshes.
- Backend CORS now reads `CORS_ALLOWED_ORIGINS`.
- Database URL normalization supports Render-style `postgres://` / `postgresql://` by converting to `postgresql+asyncpg://`.
- Added `render.yaml` for Render backend + Postgres.
- Updated README and deployment docs for Vercel frontend + Render backend/Postgres.

Verification:
- Backend tests: `16 passed`.
- Frontend build: passed.
- Playwright e2e: `12 passed`.

Current running servers:
- Backend: `http://127.0.0.1:8000`.
- Frontend: `http://localhost:3000`.

## Crash Recovery Current Status

Codex crashed after the previous work session before this handoff was fully refreshed. The current workspace has now been re-read from source files and verified against the implemented backend/frontend setup.

Confirmed current app setup:
- Backend: FastAPI app in `backend/app/main.py`, async SQLAlchemy models, Alembic migrations, SQLite default via `.env.example`, and PostgreSQL support through `docker-compose.yml`.
- Frontend: Next.js App Router app in `frontend/app`, TypeScript API types in `frontend/types/api.ts`, Tailwind/lucide UI, and Playwright e2e tests.
- API base URL defaults:
  - Backend local URL: `http://127.0.0.1:8000` or `http://localhost:8000`.
  - Frontend local URL: `http://localhost:3000`.
  - Frontend reads `NEXT_PUBLIC_API_BASE_URL`, defaulting to `http://localhost:8000`.
- `.git` currently appears nonfunctional/empty from this environment. `git -C G:\Hug_Test status` reports `fatal: not a git repository`, so do not rely on git history until that is repaired or reinitialized.

Verification rerun after recovery:
- Backend tests: `13 passed` with `backend\.venv\Scripts\python.exe -m pytest backend\tests`.
- Frontend build: passed with `npm run build` from `frontend/`.
- Playwright is installed in `frontend/node_modules`, but e2e was not rerun during recovery because it expects backend and frontend dev servers to already be running.

## Latest Completed Work

Implemented the post-V2 completion pass and extra live/demo functionality:
- Validated Docker Desktop and clean Docker/PostgreSQL workflow.
- Added reusable Postgres workflow validator at `backend/scripts/validate_postgres_workflow.py`.
- Added Hugging Face API-backed provider support through `huggingface_hub.InferenceClient`.
- Added feature flags for semantic matching and AI summaries with deterministic fallback.
- Records semantic/summarization model activity in existing `model_runs`.
- Added Playwright e2e config and route/action/CSS tests.
- Improved `/imports` to clearly distinguish demo data, live openFDA import, inventory seed/upload flow, and matching.
- Added live FDA import action in the frontend action bar: `POST /recalls/import/openfda` with `{ "limit": 50 }`.
- Added live/demo recall source filtering and match-state filtering on `/recalls`.
- Added portfolio screenshots under `docs/screenshots/`.
- Added `docs/ARCHITECTURE.md` and updated README/test/deployment docs.

Verification from latest saved session:
- Backend tests reached `13 passed`.
- Frontend build passed.
- Docker/Postgres clean validation migrated to `20260722_0002`, seeded 10 recalls and 42 inventory items, created 23 matches, and verified exposure JSON as dict.
- Postgres workflow validator with non-default company `oak_ember_steakhouse` created 24 inventory rows and 15 matches.
- Playwright e2e reached `10 passed`.

Known notes:
- `npm audit` previously reported 1 moderate and 2 high vulnerabilities; forced fixes were not applied because they may introduce breaking dependency changes.
- `npm run test:e2e` expects backend and frontend dev servers to already be running.

## Latest Live Recall + Demo Company Inventory Update

Implemented the live/demo realism pass:
- Added 8 fictional demo company inventory profiles:
  - MetroMart Grocery
  - Oak & Ember Steakhouse
  - Campus Table Dining
  - Northside Hospital Cafeteria
  - Harvest Hope Food Bank
  - QuickBasket Convenience
  - BrightPath Childcare Kitchen
  - Summit Events Catering
- Added `GET /inventory/demo-companies`.
- Added `POST /inventory/seed-company` with `{ "company_id": "..." }`.
- Existing `POST /inventory/seed` now loads the default MetroMart Grocery profile.
- Selecting a company replaces current inventory and clears matches.
- Inventory rows include `demo_company_id`, `demo_company_name`, and `inventory_source` in `raw_row`.
- Added source labels for `Live openFDA` vs `Demo recall`.
- Added recall filters for source, class, and match state.
- Added company selector to `/imports` and `/inventory`.
- Added dashboard current-company and live/demo recall source counts.
- Added recall-detail AI support/fallback panel and clearer AI semantic signal labels.
- Updated screenshots for dashboard, imports, inventory profiles, recall filters, and case file.

Verification:
- Backend tests: `13 passed`.
- Frontend build: passed.
- Postgres workflow validator with non-default company `oak_ember_steakhouse`: created 24 inventory rows and 15 matches.
- Playwright e2e: `10 passed`.

## Latest V2 Update

Implemented the core V2 exposure layer:
- Created checkpoint `.checkpoints/pre-v2-risk-policy`.
- Added persisted match exposure fields and inventory location metadata.
- Added Alembic migration `20260722_0002_v2_exposure_fields`.
- Added `risk_policy` service for exposure score, level, and explainable factors.
- Recomputed existing local SQLite matches after migration.
- Upgraded dashboard/review/detail UI to show exposure separate from match confidence.
- Upgraded Risk Radar semantics: exposure level/ring, location type/sector, quantity/node size, exposure label.
- Added richer V2 seed inventory metadata and `demo-data/inventory_sample.csv`.
- Updated API/data/model docs and README.

Verification:
- Backend tests: `9 passed`.
- Frontend build: passed.
- Local SQLite Alembic revision: `20260722_0002 (head)`.

Later passes completed the previously deferred Docker/PostgreSQL validation, Playwright route/action tests, and Hugging Face semantic matching/summarization feature flags.

## Current Next Steps

Steps 1-5 from the old handoff are now complete. Recommended next work:

1. Repair or reinitialize git metadata.
   - `.git` exists but Git does not recognize `G:\Hug_Test` as a repository.
   - Do this before any serious checkpointing or commits.

2. Run full local app smoke after restarting servers.
   - Backend: `cd backend; .venv/Scripts/python -m uvicorn app.main:app --reload`.
   - Frontend: `cd frontend; npm run dev`.
   - Then run `npm run test:e2e` from `frontend/`.

3. Portfolio final pass.
   - Make README/demo script concise and recruiter-friendly.
   - Confirm screenshots still match current UI.
   - Add resume bullets and deployment notes if needed.

4. Optional next product features.
   - Auth/roles, alert routing, USDA FSIS integration, import job status, document/image AI workflows, or organization risk-policy UI.

## Project Snapshot

RecallRadar AI is a portfolio-ready food-safety operations platform. It imports or seeds recall data, uploads/seeds inventory, runs explainable recall-to-inventory matching, and lets a user review, confirm, dismiss, resolve, or reopen possible exposure with an audit trail.

Current stack:
- Frontend: Next.js App Router, TypeScript, Tailwind CSS, lucide-react.
- Backend: FastAPI, Pydantic, SQLAlchemy async, Alembic-ready structure.
- Database: SQLite is the default local fallback; PostgreSQL is supported and has been validated through Docker Compose.
- AI strategy: deterministic explainable scoring remains the base path; Hugging Face semantic matching and recall summaries are implemented behind feature flags with deterministic fallback.
- Auth: intentionally skipped for V1.

Primary local app URLs:
- Frontend default: `http://localhost:3000`
- Backend default: `http://127.0.0.1:8000`

Important docs:
- `docs/MVP_SPEC.md`
- `docs/API_DESIGN.md`
- `docs/DATA_MODEL.md`
- `docs/AI_MATCHING_SPEC.md`
- `docs/UX_SPEC.md`
- `docs/TEST_PLAN.md`
- `docs/DEVELOPMENT_PLAN.md`
- `docs/UI_REDESIGN_OPTIONS.md`
- `docs/AGENT_SKILLS.md`
- `docs/DEPLOYMENT.md`

Manual checkpoints:
- `.checkpoints/pre-redesign`: state before the first visual redesign.
- `.checkpoints/v2-redesign`: state before the deeper command-center redesign pass.

## Current Implementation State

Backend V2 core is implemented and working:
- Health endpoint.
- Recall seed/import structure, including live openFDA import through `POST /recalls/import/openfda`.
- Recall list filters for source, class, and match presence.
- Inventory seed/upload structure, including demo company profiles and CSV upload.
- `GET /inventory/demo-companies` and `POST /inventory/seed-company`.
- Loading a demo company replaces current inventory, clears matches, and records company metadata in inventory `raw_row`.
- Matching run and match retrieval.
- Match review status updates.
- Dashboard summary.
- Audit events.
- Deterministic matching with explainable signal scoring.
- Feature-flagged Hugging Face semantic similarity as supporting evidence only.
- Feature-flagged Hugging Face recall summaries with deterministic fallback.
- AI/model activity recorded in `model_runs`.
- Persisted operational exposure scoring separate from match confidence.
- Inventory location metadata for V2 risk context.

Frontend V2 core is implemented and working:
- `/`: operational dashboard with action bar, command header, meaningful risk radar, exposure score, review progress, priority queue, and case log.
- `/recalls`: active recall worklist with live/demo source filters, class filters, and match-state filters.
- `/recalls/[id]`: case-file detail page with source intelligence, matched inventory evidence, exposure factors, signal meters, review actions, decision dock, and audit timeline.
- `/review`: triage-lane review queue with exposure-aware confirm/dismiss/resolve/reopen actions.
- `/inventory`: company selector, inventory upload, source labels, and stock ledger.
- `/imports`: guided data/demo operations console with live FDA import, default company load, demo recalls, and matching actions.

Reusable frontend components added:
- `CommandHeader`
- `RiskRadar`
- `ExposureScoreCard`
- `ReviewProgress`
- `RiskWorklistRow`
- `DecisionDock`
- `AuditTimeline`
- `SignalMeter`
- `EvidenceChip`
- `EmptyCommandState`
- `ActionBar`
- `CompanySelector`
- `InventoryUpload`
- `RecallFilters`

Recent UI direction:
- The app now uses a lighter professional instrument-panel style for the command header and risk radar instead of full dark/black blocks.
- The sidebar remains dark to preserve product identity and operational contrast.
- The main workspace remains warm, readable, and table/workflow friendly.

## What Was Done This Recovery Session

- Re-read `HANDOFF.md` after the Codex crash.
- Inspected current backend routes, schemas, models, services, config, tests, and seed data behavior.
- Inspected current frontend API client, pages, components, TypeScript types, package scripts, and Playwright config.
- Confirmed the extra live functionality: frontend live FDA import action, backend openFDA import/update path, live/demo recall filters, company inventory selector, inventory upload, and match clearing on demo company changes.
- Confirmed Playwright is installed and configured.
- Confirmed `.git` is currently not usable from this environment.
- Updated this handoff so the completed Steps 1-5 are no longer listed as pending.

Verification completed during recovery:
- Backend tests passed: `13 passed`.
- Frontend build passed: `npm run build`.
- E2E was not rerun because backend/frontend dev servers were not started in this recovery pass.

## Current Running Notes

Backend:
- Expected URL: `http://127.0.0.1:8000`
- Start from `backend/` with `.venv/Scripts/python -m uvicorn app.main:app --reload`.

Frontend:
- Expected URL: `http://localhost:3000`
- Start from `frontend/` with `npm run dev`.
- If the browser looks stale/plain, hard refresh and confirm CSS assets load with HTTP `200`.

## Product/UX Notes

The V2 Risk Radar is now meaningful rather than decorative:
- Ring/radius represents exposure level.
- Sector represents location type.
- Node size represents affected quantity.
- Node label represents exposure score.
- Dashboard/review/detail pages distinguish match score from operational exposure score.

## Suggested Next Development Steps

Use `Current Next Steps` near the top of this file. The immediate practical next action is to repair git metadata, then start backend/frontend dev servers and rerun Playwright e2e.

## Detailed V2 Roadmap

This section is historical V2 planning context. The core V2 risk/exposure, radar, demo-data, AI-flag, Docker/Postgres, and Playwright work has now been implemented; use `Current Next Steps` for the active queue.

### V2 Goal

Turn RecallRadar from a polished V1 demo into a more real operational risk product by adding:
- A configurable organization risk policy.
- A meaningful exposure scoring model.
- A Risk Radar that encodes real business meaning.
- Better demo data that proves the model.
- Optional Hugging Face semantic matching and summarization behind feature flags.
- Stronger tests and portfolio proof.

The original project goals still apply:
- Stand out in the 2025 job market.
- Be portfolio-worthy for a software engineer.
- Use Hugging Face tasks from the original screenshot where practical.
- Use real-world data APIs and practical food-safety scenarios.
- Go beyond a basic demo with architecture, UX, scalability, and explainability.

### V2 Phase 1: Configurable Risk Policy

Problem:
- V1 treats "high exposure" mostly as match confidence plus unresolved review pressure.
- In a real company, exposure depends on business context: location type, quantity, recall class, supplier, public-serving risk, and company priorities.

Implementation intent:
- Add a default policy that computes an `exposure_score` separate from `match.score`.
- Keep `match.score` as "how likely this inventory item matches the recall."
- Add `exposure_score` as "how operationally risky this possible match is."

Recommended scoring inputs:
- Match confidence score.
- FDA recall classification: Class I should weigh highest.
- Inventory quantity.
- Number of affected locations.
- Location type, such as grocery floor, school cafeteria, hospital, food bank distribution, storage-only.
- Supplier or distributor overlap.
- Lot code match strength.
- UPC match strength.
- Purchase date / active inventory relevance.
- Current review status.
- Whether item has already been confirmed, dismissed, resolved, or reopened.

Recommended default policy weights:
- `match_confidence`: 35
- `recall_class`: 20
- `lot_or_upc_exactness`: 15
- `quantity`: 10
- `location_criticality`: 10
- `supplier_overlap`: 5
- `review_status_pressure`: 5

Suggested exposure levels:
- `critical`: `>= 85`
- `high`: `70-84`
- `medium`: `45-69`
- `low`: `< 45`

Backend changes:
- Add a policy service, likely `backend/app/services/risk_policy.py`.
- Add a scoring function that accepts recall, inventory item, match signals, and optional policy config.
- Store risk output on each match or compute it in response DTOs.
- Prefer persistence if the value is used for sorting/auditing.

Potential schema additions:
- Add columns to `recall_matches`:
  - `exposure_score` numeric.
  - `exposure_level` string.
  - `exposure_factors` JSON.
- Optional new table:
  - `risk_policies`
    - `id`
    - `name`
    - `description`
    - `weights` JSON
    - `thresholds` JSON
    - `is_default`
    - `created_at`
    - `updated_at`

If avoiding schema complexity for first V2 pass:
- Implement a default policy in code.
- Include computed fields in API responses.
- Persist later once UI/logic is validated.

API changes:
- Add exposure fields to match DTOs:
  - `exposure_score`
  - `exposure_level`
  - `exposure_factors`
- Optional endpoints:
  - `GET /risk-policy`
  - `PATCH /risk-policy`
  - `POST /risk-policy/reset`
- Dashboard summary should include:
  - exposure counts by level.
  - top exposed locations.
  - top exposed suppliers.
  - highest exposure matches.

Frontend changes:
- Update match cards to show both:
  - Match score: "Does this item match the recall?"
  - Exposure score: "How urgent is this for the organization?"
- Add an "Exposure Factors" panel on recall detail.
- Add a compact policy explanation: "High because Class I + exact lot + public-serving location + 24 units."
- Add a risk policy settings view later if time allows.

Tests:
- Unit tests for scoring weights.
- Tests for Class I vs Class III difference.
- Tests for exact lot/UPC boosting exposure.
- Tests for storage-only location reducing exposure.
- Tests for resolved/dismissed status reducing urgency.
- Tests for explanation/factors output.

Done criteria:
- A user can understand why a case is operationally high risk beyond simple match confidence.
- Dashboard and review queue sort by exposure, not only match score.
- Exposure score is explainable and test-covered.

### V2 Phase 2: Meaningful Risk Radar

Problem:
- Current Risk Radar looks good, but node positions are mostly decorative.
- User feedback confirmed that a number in a random spot is not meaningful enough.

Goal:
- Make the radar encode real operational meaning while staying visually memorable.

Recommended radar semantics:
- Ring distance from center:
  - Center ring: `critical`
  - Middle ring: `high`
  - Outer ring: `medium/low`
- Sectors:
  - Option A: location type.
  - Option B: supplier.
  - Option C: recall class.
  - Recommended first implementation: location type, because it is easier to understand visually.
- Node color:
  - Red: critical/high unresolved.
  - Amber: medium needs review.
  - Green: resolved.
  - Slate: dismissed/watchlist.
- Node size:
  - Quantity affected or number of affected locations.
- Node label:
  - Exposure score.
- Hover/click:
  - Product name.
  - Recall class.
  - Location.
  - Quantity.
  - Match score.
  - Exposure score.
  - Link to case file.

Required UI additions:
- Radar legend explaining rings, sectors, color, and node size.
- Accessible labels or visible tooltip-like summary cards.
- "Top exposure" list next to radar should align with radar nodes.

Possible implementation approach:
- Keep pure React/Tailwind/CSS; no chart dependency needed.
- Calculate polar coordinates in `RiskRadar`.
- Define sector angle per location type.
- Define radius per exposure level.
- Define node size from quantity buckets.
- Render nodes with absolute positioning.

Data needed:
- `exposure_score`
- `exposure_level`
- `inventory_item.location`
- Future: `inventory_item.location_type`
- `quantity`
- `status`
- `confidence`

Tests/verification:
- Unit-test coordinate helpers if extracted.
- Frontend build.
- Route smoke.
- Manual visual QA on desktop/tablet/mobile.

Done criteria:
- A user can look at the radar and answer:
  - How many urgent exposures exist?
  - Which operational sector they belong to?
  - Which one is most urgent?
  - What action to take next?

### V2 Phase 3: Demo Data Upgrade

Problem:
- V1 demo data works, but V2 needs richer business context to prove risk policy and radar meaning.

Recommended additions:
- Locations:
  - `Downtown Grocery - Aisle 3`
  - `Campus Dining - Main Kitchen`
  - `Hospital Cafeteria - Cold Storage`
  - `Food Bank - Distribution Dock`
  - `Warehouse - Dry Storage`
- Location metadata:
  - `location_type`
  - `public_serving`
  - `criticality`
  - `region`
- Suppliers:
  - Multiple suppliers with some overlapping recall firms.
- Quantities:
  - Use varied quantities so node sizes matter.
- Lot/UPC:
  - Include exact, partial, missing, and conflicting examples.

Potential schema changes:
- Add fields to `inventory_items`:
  - `location_type`
  - `location_criticality`
  - `public_serving`
  - `region`
- Or keep these inside `raw_row`/metadata initially if minimizing migrations.

Sample CSV:
- Add `demo-data/inventory_sample.csv`.
- Include realistic headers:
  - `product_name,brand,upc,lot_code,quantity,location,location_type,public_serving,supplier,purchase_date`

Done criteria:
- Demo data makes the risk policy visibly useful.
- Radar sectors/rings have enough variety to demonstrate meaning.
- Portfolio screenshots tell a real story.

### V2 Phase 4: Hugging Face AI Integration

Use Hugging Face only after deterministic workflow remains stable.

Primary HF tasks from the original screenshot:
- Sentence Similarity.
- Feature Extraction.
- Summarization.

Recommended first AI feature:
- Semantic recall-to-inventory similarity.
- Use sentence-transformers or transformers behind an `AI_ENABLED` feature flag.
- Compare recall product/reason text with normalized inventory product/brand text.
- Add semantic score as one matching signal, not the only decision driver.

Recommended second AI feature:
- Recall action summary.
- Generate concise "what to do next" text from recall reason, distribution, classification, and matched inventory.
- Keep deterministic fallback summary.

Backend boundaries:
- Add or complete `backend/app/services/ai/`.
- Feature flags:
  - `AI_ENABLED=false`
  - `HF_SEMANTIC_MODEL=...`
  - `HF_SUMMARY_MODEL=...`
- Record all AI runs in `model_runs`.
- Store:
  - model name
  - task type
  - input hash or metadata
  - output summary/scores
  - latency
  - fallback status

Important architecture rule:
- AI is decision support only.
- UI must always show evidence, source data, and human review status.

Tests:
- Mock model calls.
- Test deterministic fallback.
- Test semantic score is blended safely.
- Test AI failure does not break matching.

Done criteria:
- Hugging Face integration improves matching/summaries but the app still works offline or with AI disabled.
- Portfolio story clearly references HF tasks and human-in-the-loop explainability.

### V2 Phase 5: Verification And Portfolio Polish

Testing:
- Playwright has been added.
- Route smoke tests exist for:
  - `/`
  - `/recalls`
  - `/recalls/[id]`
  - `/review`
  - `/inventory`
  - `/imports`
- Review action tests exist for:
  - confirm
  - dismiss
  - resolve
  - reopen
- Remaining visual QA ideas:
  - desktop
  - tablet
  - mobile
  - no text overflow
  - CSS asset loading

Developer experience:
- `.env.example` exists at the project root.
- Root README startup instructions exist.
- Add one-command scripts if practical:
  - `scripts/start-backend`
  - `scripts/start-frontend`
  - or documented commands.

Portfolio README:
- Add project problem statement.
- Add architecture diagram or description.
- Add screenshots.
- Add "AI tasks used" section.
- Add "Why this is not a toy demo" section.
- Add "Future work" section.

Done criteria:
- Project can be launched reliably.
- User can demo it in under five minutes.
- README makes it clear why this is resume-worthy.

### Recommended V2 Implementation Order

When next session begins, follow this order unless the user redirects:
1. Read `HANDOFF.md`.
2. Verify backend and frontend current state.
3. Create a new checkpoint before V2 changes, such as `.checkpoints/pre-v2-risk-policy`.
4. Inspect backend models/schemas/services for match fields and dashboard response.
5. Implement computed risk policy service first.
6. Add exposure fields to match response DTOs without schema migration if feasible.
7. Update dashboard/review/detail UI to display exposure score and factors.
8. Upgrade Risk Radar semantics using exposure level, sectors, and quantity.
9. Add tests for risk policy.
10. Run backend tests, frontend build, and route smoke.
11. Update `HANDOFF.md` with results.

If schema changes are clearly cleaner than computed-only fields:
1. Add migration/columns for exposure fields.
2. Recompute exposure during match generation and review status updates.
3. Continue with UI and tests.

### V2 Risks And Decisions To Watch

Risk:
- Adding too much policy/settings UI could slow progress.

Preferred choice:
- Implement a strong default policy first.
- Add editable settings later.

Risk:
- Radar can become visually busy.

Preferred choice:
- Keep one clear encoding per visual property:
  - ring = exposure level
  - sector = location type
  - size = quantity
  - color = status

Risk:
- Hugging Face dependencies may be heavy.

Preferred choice:
- Add AI behind feature flags.
- Mock tests.
- Keep deterministic fallback.

Risk:
- SQLite fallback and PostgreSQL target may diverge.

Preferred choice:
- Keep schema/data types simple.
- Use JSON-compatible structures.
- Keep SQLite fallback and PostgreSQL validation paths in sync.

### V2 Completion Definition

V2 should be considered complete when:
- Exposure risk is distinct from match confidence.
- The system can explain both match score and exposure score.
- Risk Radar positions/nodes are meaningful, not decorative.
- Demo data proves realistic food-safety workflows.
- Optional Hugging Face features are either implemented behind flags or explicitly deferred with clean service boundaries.
- Tests cover the new scoring logic.
- Build and route smoke pass.
- `HANDOFF.md` and README are updated.

## Post-V2 Continuation Roadmap

This section captures the broader work planned after the V2 risk/exposure system is complete. It is meant as future context, not the immediate next implementation queue.

### Existing Planning Documents

The progress and roadmap information already exists across several docs:
- `docs/DEVELOPMENT_PLAN.md`: original milestone plan, build order, portfolio polish, and broad V2 roadmap.
- `docs/AI_MATCHING_SPEC.md`: detailed deterministic matching and later AI phases, including semantic similarity, entity extraction, summarization, Document QA, and shelf image analysis.
- `docs/API_DESIGN.md`: implemented V1 endpoints and future V2 endpoints for documents, images, and alerts.
- `docs/DATA_MODEL.md`: current core schema plus planned V2 tables for policies, documents, images, alerts, and organization features.
- `docs/TEST_PLAN.md`: backend and frontend test strategy, including future Playwright checks.
- `docs/DEPLOYMENT.md`: local/deployment strategy and production considerations.
- `docs/UI_REDESIGN_OPTIONS.md`: visual redesign options already used for the command-center redesign.

Even though those docs exist, `HANDOFF.md` should remain the running project memory and should summarize the current recommended path.

### Post-V2 AI Expansion

After configurable exposure scoring and meaningful radar are complete, expand AI features from the original Hugging Face task list.

Recommended order:
1. Semantic matching.
   - Hugging Face task: Sentence Similarity / Feature Extraction.
   - Purpose: improve recall-to-inventory matching when UPC/lot/brand data is incomplete.
   - Keep as one explainable signal inside the existing scoring system.

2. Recall/action summarization.
   - Hugging Face task: Summarization.
   - Purpose: generate short action summaries for operations staff.
   - Must preserve deterministic fallback.

3. Entity extraction.
   - Hugging Face task: Token Classification.
   - Purpose: extract brands, lot codes, allergens, pathogens, UPCs, locations, and affected product terms from recall text.

4. Document workflows.
   - Hugging Face task: Document Question Answering.
   - Purpose: upload recall PDFs, supplier notices, invoices, or distributor letters and ask operational questions.

5. Image workflows.
   - Hugging Face tasks: Image-to-Text, Visual Question Answering, Object Detection.
   - Purpose: analyze product label photos, shelf photos, or barcode/packaging images.

6. Translation.
   - Hugging Face task: Translation.
   - Purpose: translate recall summaries and action steps for multilingual teams.

7. Forecasting.
   - Hugging Face/task category: Time Series Forecasting.
   - Purpose: forecast review workload, supplier exposure trends, or recurring product-risk patterns.

### Post-V2 Product Features

Potential product roadmap:
- Organization settings and risk policy presets.
- Multi-location / multi-facility support.
- User roles and auth.
- Alerts and notifications.
- Email/SMS/slack-style alert routing.
- Barcode scanning workflow.
- USDA FSIS recall integration.
- Supplier profiles and recurring supplier risk.
- Model evaluation dashboard.
- Bulk review workflows.
- Saved filters and work queues.
- Exportable audit reports.
- Incident report generation.

### Post-V2 Data And Infrastructure

Recommended infrastructure improvements:
- Revisit PostgreSQL through Docker once Docker is available.
- Add production-ready PostgreSQL deployment path.
- Consider `pgvector` if semantic embeddings are stored.
- Add background jobs for slow imports/model inference.
  - Simple FastAPI background tasks first.
  - Redis/RQ or Celery later if needed.
- Add `.env.example` files for backend and frontend.
- Add a one-command local startup script.
- Add seed/demo reset command.
- Add sample CSV and demo data directory.

### Post-V2 Testing And Quality

Recommended quality work:
- Keep Playwright route smoke tests current for all primary pages.
- Keep action tests current for confirm, dismiss, resolve, and reopen.
- Add upload tests for valid and invalid CSVs.
- Add visual screenshot checks for desktop/tablet/mobile.
- Add CSS asset loading checks to catch the plain-HTML issue seen on port `3005`.
- Add backend integration tests for the full workflow:
  - seed recalls
  - seed inventory
  - run matching
  - calculate exposure
  - update review status
  - verify dashboard metrics and audit events

### Post-V2 Portfolio Packaging

Recommended portfolio work:
- Update README with:
  - product overview
  - problem statement
  - architecture
  - local setup
  - demo script
  - screenshots
  - AI tasks used
  - testing strategy
  - resume bullet examples
- Add architecture diagram or system flow diagram.
- Add screenshots from:
  - dashboard
  - meaningful risk radar
  - recall case file
  - review queue
  - inventory upload
- Add a "Why this is not a toy demo" section.
- Add "Real-world applications" section:
  - grocery chains
  - restaurants
  - campus dining
  - hospitals
  - food banks
- Add "Future work" section matching this roadmap.

### Post-V2 Production Readiness

Before presenting it as production-like:
- Add auth.
- Add tenant/org boundaries.
- Add audit export.
- Add role-based access.
- Add database backup guidance.
- Add monitoring/logging.
- Add rate limiting for external APIs.
- Add robust error pages and retry states.
- Add import job status tracking.
- Add deployment docs for a realistic hosting setup.

### Long-Term Product Vision

RecallRadar can evolve from recall matching into a broader food safety intelligence platform:
- Public recall monitoring.
- Supplier risk intelligence.
- Inventory exposure matching.
- Document and image evidence ingestion.
- Human-in-the-loop review.
- Regulatory audit support.
- Facility-level risk visibility.
- AI-assisted operations summaries.
- Predictive workload and supplier risk analytics.

## Resume/Portfolio Positioning

Strong resume angle:
- Built an AI-assisted food safety operations platform that ingests public recall data, normalizes inventory uploads, generates explainable exposure matches, and supports human-in-the-loop review with audit history.
- Designed a scalable full-stack architecture with FastAPI, Next.js, typed DTOs, async database access, deterministic scoring, and future Hugging Face model boundaries.
- Created a premium operational SaaS UI with dashboard analytics, triage workflows, case-file evidence review, and reusable component architecture.

## Handoff Instructions For Future Sessions

At the end of each future working session:
- Update this file with what changed.
- Update running ports/URLs.
- Update verification results.
- Add any new known issues.
- Refresh the suggested next steps.

At the start of a new session:
- Provide this file to the assistant.
- Ask it to read `HANDOFF.md` first.
- Then ask it to continue from the recommended next step or a new priority.
