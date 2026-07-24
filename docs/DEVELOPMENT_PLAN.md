# RecallRadar AI Development Plan

## 1. Strategy

Build a narrow, complete V1 before adding advanced AI features.

The first release should prove the core workflow:

```text
recalls -> inventory -> matching -> review -> audit
```

That workflow is stronger for a portfolio than a wide set of disconnected model demos.

## 2. Milestone 0: Project Setup

Deliverables:

- Repository structure.
- Backend scaffold.
- Frontend scaffold.
- Environment configuration.
- Local development commands.
- Initial README.

Recommended structure:

```text
frontend/
backend/
docs/
docker-compose.yml
.env.example
README.md
```

Done when:

- Backend health endpoint runs.
- Frontend shell runs.
- README explains setup.

## 3. Milestone 1: Data Model and Persistence

Deliverables:

- PostgreSQL setup.
- SQLAlchemy or SQLModel models.
- Alembic migrations.
- Tables for recalls, inventory items, uploads, matches, reviews, audit events, and model runs.

Done when:

- Migrations run locally.
- Database can store seed recalls and inventory.
- Tests can create and query core entities.

## 4. Milestone 2: Recall Ingestion

Deliverables:

- openFDA recall client.
- Recall normalization.
- Duplicate prevention.
- Raw payload storage.
- Seed recall loader.

Done when:

- API can import recent recalls.
- API can load seed recalls without network.
- Recall inbox endpoint returns normalized records.

## 5. Milestone 3: Inventory Upload

Deliverables:

- CSV parser.
- Validation rules.
- Upload metadata.
- Row-level error reporting.
- Inventory list endpoint.

Done when:

- User can upload sample CSV.
- Valid rows are stored.
- Invalid rows are reported clearly.
- Tests cover missing product names and malformed dates.

## 6. Milestone 4: Matching Engine

Deliverables:

- Normalization helpers.
- Product similarity signal.
- Brand similarity signal.
- UPC signal.
- Lot-code signal.
- Distribution signal.
- Weighted scoring.
- Explanation generation.

Done when:

- Match run endpoint creates matches.
- Each match has score, confidence, signals, and explanation.
- Seed data produces known high, medium, and low matches.
- Tests cover scoring behavior.

## 7. Milestone 5: Frontend Core

Deliverables:

- App shell.
- Dashboard.
- Recall inbox.
- Recall detail page.
- Inventory upload page.
- Review queue.

Done when:

- User can complete the main demo flow in browser.
- UI shows loading, empty, success, and error states.
- Data is fetched from backend API.

## 8. Milestone 6: Human Review and Audit

Deliverables:

- Match status update endpoint.
- Human review records.
- Audit event creation.
- Review history UI.

Done when:

- User can confirm, dismiss, resolve, and reopen matches.
- Audit history appears on recall detail.
- Dashboard metrics update after review actions.

## 9. Milestone 7: Portfolio Polish

Deliverables:

- Demo seed command.
- Screenshot-ready UI.
- Strong README.
- Architecture diagram.
- Test coverage.
- Error handling.
- Empty states.
- Optional deployed demo.

Done when:

- A reviewer can run the project locally.
- Demo flow takes less than 5 minutes.
- README includes resume bullets and architecture overview.

## 10. V2 Roadmap

Add after V1 is stable:

- USDA FSIS recall integration.
- Semantic embeddings with Hugging Face sentence similarity.
- Recall summarization.
- Token classification for entity extraction.
- Invoice upload and document QA.
- Shelf image upload and image-to-text.
- Visual question answering.
- Barcode scanning.
- Multi-location support.
- Email alerts.
- Model evaluation dashboard.
- pgvector integration.
- Redis/RQ or Celery background jobs.

## 11. Recommended Build Order

1. Create backend FastAPI scaffold.
2. Create frontend Next.js scaffold.
3. Add Docker Compose.
4. Add database schema.
5. Add seed data.
6. Add openFDA ingestion.
7. Add inventory upload.
8. Add matching engine.
9. Add dashboard APIs.
10. Build frontend dashboard.
11. Build recall inbox.
12. Build recall detail.
13. Build inventory upload.
14. Build review queue.
15. Add tests.
16. Polish docs and demo flow.

## 12. Engineering Priorities

- Keep business logic testable outside web handlers.
- Store raw source data.
- Make matching explainable.
- Treat AI output as decision support.
- Keep V1 usable without paid APIs.
- Make seed data good enough for demos.
- Avoid overbuilding authentication before core product value exists.

