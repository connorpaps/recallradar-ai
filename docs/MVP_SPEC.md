# RecallRadar AI MVP Specification

## 1. Product Objective

Build a portfolio-ready V1 of RecallRadar AI that helps a small food organization identify whether public food recalls may affect its inventory.

The MVP must feel like a real internal operations product. It should demonstrate practical AI architecture, useful data modeling, clear UX, and explainable decision support.

## 2. MVP Problem

Small retailers, restaurants, food banks, and dining teams often lack automated recall management systems. They may hear about recalls through public notices, vendor messages, or news, then manually compare those notices against inventory spreadsheets and invoices.

The MVP focuses on the highest-value workflow:

**Public recall data + uploaded inventory = explainable match review workflow.**

## 3. Target User

The primary user is an operations manager responsible for food safety at a small organization.

The user needs to:

- See active recalls.
- Upload inventory.
- Know which products may be affected.
- Understand why the system thinks there is a match.
- Take a review action.
- Leave an audit trail.

## 4. MVP User Flow

1. User opens the dashboard.
2. User sees counts for active recalls, high-confidence matches, unresolved reviews, and recently imported inventory.
3. User imports or refreshes openFDA recall data.
4. User uploads an inventory CSV.
5. App validates inventory rows and displays import results.
6. System generates recall-to-inventory matches.
7. User reviews matches in the recall inbox or review queue.
8. User opens a recall detail page.
9. User reviews matched inventory items and match explanations.
10. User marks a match as `confirmed`, `dismissed`, or `resolved`.
11. App records the decision in audit history.

## 5. V1 Features

### Recall Ingestion

- Fetch recent food enforcement recalls from openFDA.
- Normalize source records into local schema.
- Store source payloads for traceability.
- Avoid duplicate imports by source recall ID.
- Support manual refresh from the UI or API.

### Inventory Upload

- Accept CSV uploads.
- Validate required columns.
- Report row-level validation errors.
- Store valid inventory rows.
- Keep uploaded file metadata.
- Trigger matching after successful import.

Required CSV columns:

```csv
product_name,brand,upc,lot_code,quantity,location,supplier,purchase_date
```

Only `product_name` is strictly required for V1. Other fields improve match quality.

### Matching Engine

- Score recall-to-inventory matches.
- Use transparent signals.
- Generate confidence levels.
- Generate human-readable explanations.
- Persist match scores and signal details.

V1 match statuses:

- `needs_review`
- `confirmed`
- `dismissed`
- `resolved`

V1 confidence levels:

- `high`
- `medium`
- `low`

### Recall Inbox

- List imported recalls.
- Show recall reason, date, classification, source, and match count.
- Filter by match status, classification, source, and date.
- Search by product, brand, firm, or reason.

### Recall Detail

- Show normalized recall data.
- Show source text and source link.
- Show AI or rule-generated summary.
- Show matched inventory.
- Show match score and evidence signals.
- Provide review actions.
- Show audit history.

### Review Queue

- List all matches needing human review.
- Sort by confidence and recall date.
- Allow quick confirm, dismiss, or resolve.
- Link to recall detail.

### Dashboard

- Active recalls count.
- High-confidence matches count.
- Unresolved review count.
- Recent inventory import count.
- Matches by confidence.
- Review status breakdown.

### Seed Demo Mode

- Include sample recalls and inventory rows.
- Allow the app to demonstrate without external API availability.
- Include messy names and partial fields to show the matching engine's value.

## 6. Explicit Non-Goals For V1

V1 will not include:

- User accounts.
- Multi-tenant organizations.
- Production email or SMS alerts.
- Shelf image upload.
- Barcode scanning.
- Invoice PDF upload.
- Document question answering.
- USDA FSIS data ingestion.
- Forecasting.
- Mobile app.
- Payment or billing.

## 7. Acceptance Criteria

The MVP is complete when:

- The app can import or seed recall data.
- The app can upload inventory CSV data.
- The backend validates inventory rows.
- The system creates recall-to-inventory matches.
- Every match has a score, confidence, and explanation.
- The UI displays recall inbox, recall detail, dashboard, and review queue.
- Users can update match review status.
- Review actions are recorded as audit events.
- The project can run locally from documented commands.
- Tests cover recall normalization, CSV validation, matching, and status updates.

## 8. Portfolio Demo Script

1. Start with an empty dashboard.
2. Import recent recall records.
3. Upload sample inventory.
4. Show generated matches.
5. Open a high-confidence recall match.
6. Explain how signals created the confidence score.
7. Confirm one match and dismiss another.
8. Show audit history and dashboard updates.

