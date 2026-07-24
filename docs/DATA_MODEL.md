# RecallRadar AI Data Model

## 1. Design Goals

The data model must support:

- Source traceability.
- Explainable matching.
- Human review.
- Auditability.
- Future AI model runs.
- Future document and image evidence.

V1 should stay simple, but avoid painting the project into a corner.

## 2. Entity Overview

Core V1 entities:

- `recalls`
- `inventory_items`
- `uploaded_files`
- `recall_matches`
- `human_reviews`
- `audit_events`
- `model_runs`

Planned V2 entities:

- `invoices`
- `invoice_line_items`
- `product_images`
- `image_detections`
- `locations`
- `suppliers`

## 3. Tables

## recalls

Stores normalized public recall records.

Recommended fields:

- `id`: UUID primary key.
- `source`: enum, initially `openfda`.
- `source_recall_id`: string, unique with source.
- `source_url`: string nullable.
- `status`: string nullable.
- `classification`: string nullable.
- `product_description`: text.
- `brand_name`: string nullable.
- `recalling_firm`: string nullable.
- `reason_for_recall`: text nullable.
- `distribution_pattern`: text nullable.
- `recall_initiation_date`: date nullable.
- `report_date`: date nullable.
- `termination_date`: date nullable.
- `normalized_product_name`: string nullable.
- `normalized_brand_name`: string nullable.
- `summary`: text nullable.
- `raw_payload`: JSONB.
- `created_at`: timestamp.
- `updated_at`: timestamp.

Indexes:

- Unique index on `source`, `source_recall_id`.
- Index on `classification`.
- Index on `recall_initiation_date`.
- Full-text or trigram index on product and reason fields.

## inventory_items

Stores uploaded local inventory rows.

Recommended fields:

- `id`: UUID primary key.
- `product_name`: string.
- `brand`: string nullable.
- `upc`: string nullable.
- `lot_code`: string nullable.
- `quantity`: numeric nullable.
- `unit`: string nullable.
- `location`: string nullable.
- `location_type`: string nullable.
- `location_criticality`: string nullable.
- `public_serving`: boolean default false.
- `region`: string nullable.
- `supplier`: string nullable.
- `purchase_date`: date nullable.
- `normalized_product_name`: string nullable.
- `normalized_brand`: string nullable.
- `uploaded_file_id`: UUID nullable.
- `active`: boolean default true.
- `raw_row`: JSONB.
- `created_at`: timestamp.
- `updated_at`: timestamp.

Indexes:

- Index on `normalized_product_name`.
- Index on `normalized_brand`.
- Index on `upc`.
- Index on `lot_code`.
- Index on `active`.

## uploaded_files

Tracks user-uploaded files.

Recommended fields:

- `id`: UUID primary key.
- `file_type`: enum, initially `inventory_csv`.
- `original_filename`: string.
- `storage_path`: string nullable.
- `row_count`: integer default 0.
- `valid_row_count`: integer default 0.
- `invalid_row_count`: integer default 0.
- `status`: enum, `uploaded`, `processed`, `failed`.
- `error_summary`: text nullable.
- `created_at`: timestamp.
- `updated_at`: timestamp.

## recall_matches

Stores scored matches between recalls and inventory items.

Recommended fields:

- `id`: UUID primary key.
- `recall_id`: UUID foreign key.
- `inventory_item_id`: UUID foreign key.
- `score`: decimal between 0 and 1.
- `confidence`: enum, `high`, `medium`, `low`.
- `exposure_score`: decimal between 0 and 100.
- `exposure_level`: enum, `critical`, `high`, `medium`, `low`.
- `exposure_factors`: JSONB.
- `status`: enum, `needs_review`, `confirmed`, `dismissed`, `resolved`.
- `signals`: JSONB.
- `explanation`: text.
- `matched_fields`: JSONB.
- `reviewed_at`: timestamp nullable.
- `created_at`: timestamp.
- `updated_at`: timestamp.

Indexes:

- Unique index on `recall_id`, `inventory_item_id`.
- Index on `confidence`.
- Index on `status`.
- Index on `score`.

Example `signals`:

```json
[
  {
    "name": "brand_similarity",
    "score": 0.92,
    "weight": 0.25,
    "detail": "Recall brand and inventory brand are highly similar."
  },
  {
    "name": "product_similarity",
    "score": 0.84,
    "weight": 0.35,
    "detail": "Both descriptions refer to organic spinach."
  }
]
```

## human_reviews

Stores explicit human review actions.

Recommended fields:

- `id`: UUID primary key.
- `recall_match_id`: UUID foreign key.
- `action`: enum, `confirmed`, `dismissed`, `resolved`, `reopened`.
- `note`: text nullable.
- `reviewer_name`: string nullable for V1.
- `created_at`: timestamp.

## audit_events

Stores system and user actions.

Recommended fields:

- `id`: UUID primary key.
- `entity_type`: string.
- `entity_id`: UUID.
- `event_type`: string.
- `actor_type`: enum, `system`, `user`.
- `actor_label`: string nullable.
- `metadata`: JSONB.
- `created_at`: timestamp.

Example events:

- `recall.imported`
- `inventory.uploaded`
- `match.generated`
- `match.confirmed`
- `match.dismissed`
- `match.resolved`

## model_runs

Tracks AI or algorithmic runs.

Recommended fields:

- `id`: UUID primary key.
- `run_type`: string.
- `model_name`: string nullable.
- `model_version`: string nullable.
- `input_ref_type`: string.
- `input_ref_id`: UUID nullable.
- `output_ref_type`: string nullable.
- `output_ref_id`: UUID nullable.
- `parameters`: JSONB.
- `metrics`: JSONB.
- `status`: enum, `queued`, `running`, `completed`, `failed`.
- `error_message`: text nullable.
- `started_at`: timestamp nullable.
- `completed_at`: timestamp nullable.
- `created_at`: timestamp.

## 4. V2 Tables

## invoices

Stores uploaded supplier invoices.

Key fields:

- Vendor.
- Invoice date.
- Source file.
- Extracted text.
- Extraction confidence.

## invoice_line_items

Stores extracted invoice products.

Key fields:

- Product description.
- Quantity.
- UPC.
- Lot code.
- Unit cost.
- Matched inventory item.

## product_images

Stores shelf or product photo metadata.

Key fields:

- Storage path.
- Uploaded date.
- Location.
- Caption.
- Visual embedding reference.

## image_detections

Stores detected product regions or label evidence.

Key fields:

- Image ID.
- Bounding box.
- Label.
- Confidence.
- Extracted text.

## 5. Status Rules

Recall match status transitions:

```text
needs_review -> confirmed
needs_review -> dismissed
confirmed -> resolved
dismissed -> needs_review
resolved -> needs_review
```

Every user-driven status transition should create a `human_reviews` row and an `audit_events` row.

## 6. Data Retention

For portfolio V1:

- Keep all raw recall payloads.
- Keep uploaded inventory rows.
- Do not store sensitive personal information.
- Allow seed data reset.

For production:

- Add tenant isolation.
- Add retention policies.
- Add file deletion workflows.
- Add access controls.
