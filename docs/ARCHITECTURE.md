# RecallRadar AI Architecture

```text
Next.js App Router UI
  Dashboard / Recalls / Review / Inventory / Imports
        |
        v
FastAPI JSON API
  recall import, inventory upload, matching, review actions, dashboard
        |
        v
PostgreSQL via Docker for production-like validation
SQLite fallback for fast local demo mode
        |
        v
Deterministic scoring + optional Hugging Face support
  match confidence, exposure policy, semantic similarity, summaries
```

## Data Flow

1. Demo seed data or live openFDA records create `recalls`.
2. Demo inventory or CSV uploads create `inventory_items`.
3. Matching produces `recall_matches` with confidence, signals, exposure score, and exposure factors.
4. Review actions update status, recalculate exposure, and write audit events.
5. Optional Hugging Face calls record `model_runs` and fall back cleanly when disabled or unavailable.
