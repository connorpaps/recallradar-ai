# RecallRadar AI API Design

## 1. API Goals

The API should be simple, testable, and easy for the frontend to consume.

V1 uses REST endpoints with JSON responses. File uploads use multipart form data.

Base URL for local development:

```text
http://localhost:8000
```

## 2. Conventions

- JSON request and response bodies unless uploading files.
- ISO 8601 timestamps.
- UUID identifiers.
- Pagination for list endpoints.
- Stable error response format.

Error shape:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Inventory CSV is missing required columns.",
    "details": {}
  }
}
```

## 3. Health

### GET /health

Returns API status.

Response:

```json
{
  "status": "ok"
}
```

## 4. Recall Endpoints

### POST /recalls/import/openfda

Imports recent openFDA food enforcement recall records.

Request:

```json
{
  "limit": 100,
  "since": "2026-01-01"
}
```

Response:

```json
{
  "imported": 42,
  "updated": 8,
  "skipped": 12
}
```

### POST /recalls/seed

Developer-only fallback. Disabled unless `ENABLE_DEMO_RECALL_SEED=true`.

Response:

```json
{
  "created": 12
}
```

### GET /recalls

Lists recalls.

Query parameters:

- `q`
- `classification`
- `status`
- `has_matches`
- `date_from`
- `date_to`
- `page`
- `page_size`

Response:

```json
{
  "items": [
    {
      "id": "uuid",
      "source": "openfda",
      "product_description": "Organic baby spinach",
      "brand_name": "Fresh Valley",
      "classification": "Class I",
      "reason_for_recall": "Potential Listeria contamination",
      "recall_initiation_date": "2026-07-01",
      "match_count": 3,
      "highest_confidence": "high"
    }
  ],
  "page": 1,
  "page_size": 25,
  "total": 1
}
```

### GET /recalls/{recall_id}

Returns recall detail.

Response includes:

- Normalized recall fields.
- Source payload summary.
- Summary.
- Match counts.
- Audit events.

### GET /recalls/{recall_id}/matches

Returns matches for a recall.

Response:

```json
{
  "items": [
    {
      "id": "uuid",
      "inventory_item": {
        "id": "uuid",
        "product_name": "Fresh Valley Organic Spinach",
        "brand": "Fresh Valley",
        "upc": "123456789012",
        "lot_code": "L2408",
        "quantity": 12,
        "location": "Back Cooler"
      },
      "score": 0.88,
      "confidence": "high",
      "status": "needs_review",
      "explanation": "Brand and product name are highly similar. Distribution information does not rule this item out."
    }
  ]
}
```

## 5. Inventory Endpoints

### POST /inventory/upload

Uploads inventory CSV.

Content type:

```text
multipart/form-data
```

Fields:

- `file`: CSV file.

Response:

```json
{
  "uploaded_file_id": "uuid",
  "row_count": 50,
  "valid_row_count": 47,
  "invalid_row_count": 3,
  "errors": [
    {
      "row": 12,
      "message": "product_name is required"
    }
  ]
}
```

### POST /inventory/seed

Loads seed inventory for demo mode.

Response:

```json
{
  "created": 40
}
```

### GET /inventory

Lists inventory items.

Query parameters:

- `q`
- `brand`
- `supplier`
- `location`
- `active`
- `page`
- `page_size`

### GET /inventory/{inventory_item_id}

Returns inventory item detail and related matches.

## 6. Matching Endpoints

### POST /matches/run

Runs matching across current recalls and inventory.

Request:

```json
{
  "recall_id": null,
  "inventory_upload_id": null,
  "min_score": 0.35
}
```

Response:

```json
{
  "created": 18,
  "updated": 6,
  "skipped": 120
}
```

### GET /matches

Lists recall matches.

Query parameters:

- `status`
- `confidence`
- `recall_id`
- `inventory_item_id`
- `min_score`
- `page`
- `page_size`

### GET /matches/{match_id}

Returns match detail, exposure fields, signals, recall, inventory item, and reviews.

V2 match responses include:

- `exposure_score`: operational urgency from 0 to 100.
- `exposure_level`: `critical`, `high`, `medium`, or `low`.
- `exposure_factors`: weighted explanation inputs for the exposure score.

### PATCH /matches/{match_id}/status

Updates human review status.

Request:

```json
{
  "status": "confirmed",
  "note": "Item found in back cooler. Removed from active inventory.",
  "reviewer_name": "Demo User"
}
```

Response:

```json
{
  "id": "uuid",
  "status": "confirmed",
  "reviewed_at": "2026-07-22T15:30:00Z"
}
```

## 7. Dashboard Endpoints

### GET /dashboard/summary

Returns key metrics.

Response:

```json
{
  "active_recalls": 24,
  "inventory_items": 50,
  "matches_needing_review": 9,
  "high_confidence_matches": 3,
  "matches_by_status": {
    "needs_review": 9,
    "confirmed": 2,
    "dismissed": 5,
    "resolved": 1
  },
  "matches_by_confidence": {
    "high": 3,
    "medium": 8,
    "low": 6
  },
  "matches_by_exposure": {
    "critical": 1,
    "high": 2,
    "medium": 5,
    "low": 3
  },
  "top_exposed_locations": [],
  "top_exposed_suppliers": []
}
```

## 8. Audit Endpoints

### GET /audit

Lists audit events.

Query parameters:

- `entity_type`
- `entity_id`
- `event_type`
- `page`
- `page_size`

## 9. Future V2 Endpoints

- `POST /documents/upload`
- `GET /documents/{document_id}/qa`
- `POST /images/upload`
- `GET /images/{image_id}/detections`
- `POST /alerts/test`
- `GET /models/runs`
- `GET /evaluation/matching`
