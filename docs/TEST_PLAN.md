# RecallRadar AI Test Plan

## 1. Testing Goals

Testing should protect the core workflow:

```text
recall ingestion -> inventory upload -> matching -> review status -> dashboard metrics
```

The most important tests are backend tests around data normalization, validation, and matching logic.

## 2. Backend Unit Tests

### Recall Normalization

Test:

- openFDA payload maps to internal recall model.
- Missing optional fields do not crash ingestion.
- Duplicate source IDs are handled.
- Dates are parsed correctly.
- Raw payload is preserved.

### Inventory CSV Validation

Test:

- Valid CSV imports successfully.
- Missing `product_name` returns row-level error.
- Blank optional fields are accepted.
- Invalid dates are reported.
- Quantity parsing handles integers and decimals.
- Extra columns are preserved in raw row or ignored safely.

### Matching Engine

Test:

- Exact UPC match produces high score.
- Strong brand and product similarity produces high or medium score.
- Missing UPC does not block a good semantic match.
- Conflicting UPC lowers score.
- Unrelated products are not persisted above threshold.
- Explanation includes the strongest signals.
- Score is always clamped between 0 and 1.

### Review Status

Test:

- Match can move from `needs_review` to `confirmed`.
- Match can move from `needs_review` to `dismissed`.
- Match can move from `confirmed` to `resolved`.
- Reopen returns match to `needs_review`.
- Review action creates `human_reviews` row.
- Review action creates `audit_events` row.

### Dashboard Metrics

Test:

- Active recall count is correct.
- High-confidence match count is correct.
- Unresolved review count is correct.
- Status breakdown updates after review.

## 3. Backend Integration Tests

Test flows:

- Seed recalls, seed inventory, run matching.
- Upload CSV, run matching, review match.
- Import mocked openFDA response.
- Fetch recall detail with matches and audit events.

External API tests should use mocked responses. Live openFDA calls should be optional.

## 4. Frontend Tests

Use Playwright once the core UI exists.

Test:

- Dashboard loads.
- CSS assets return HTTP 200 so the app never regresses to plain HTML.
- Empty state shows demo actions.
- Demo company inventory selector loads a profile and refreshes the ledger.
- Recall inbox displays seeded recalls.
- Recall inbox filters live/demo source and exposure state.
- Inventory upload accepts a valid CSV.
- Recall detail page opens.
- Recall detail shows AI support/fallback panel.
- Review queue displays matches.
- User can confirm a match.
- User can dismiss, resolve, and reopen a match.
- Dashboard metrics update after status change.

Run:

```bash
cd backend
.venv/Scripts/python -m uvicorn app.main:app --reload

cd frontend
npm run dev
npm run test:e2e
```

## 5. Manual QA Checklist

- Can run the project from README commands.
- Can load seed data.
- Can import recalls if network and API are available.
- Can upload sample CSV.
- Can run matching.
- Can explain why a match was created.
- Can change match status.
- UI handles empty states.
- UI handles API errors.
- UI remains usable on laptop-width screens.

## 6. Seed Dataset Tests

Seed data should include:

- At least 10 recalls.
- At least 40 inventory items.
- At least 3 known high-confidence matches.
- At least 5 medium-confidence matches.
- Several unrelated items.
- Messy names and missing UPCs.

Seed data should make the demo predictable.
