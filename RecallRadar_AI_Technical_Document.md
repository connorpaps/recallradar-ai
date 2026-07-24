# RecallRadar AI Technical Project Document

## 1. Project Overview

**Project Name:** RecallRadar AI

**Project Type:** Multimodal food-safety intelligence and retail recall response platform

**Target Build Timeline:** 1-3 months for a solo engineer or small team

**Primary Goal:** Help grocery stores, restaurants, campus dining teams, food banks, and small retailers identify recalled products faster by combining public recall APIs, shelf images, invoices, receipts, inventory records, and natural-language risk summaries.

RecallRadar AI monitors food recall and public health alert data, matches recalls against local inventory, analyzes shelf or stockroom photos, extracts product details from invoices and receipts, and creates prioritized action plans for removing risky items.

The platform is designed as a practical AI operations tool rather than a simple chatbot. It demonstrates multimodal AI, real-world data ingestion, document intelligence, computer vision, search, alerting, and workflow design.

## 2. Problem Statement

Food recalls move fast, but smaller organizations often rely on manual emails, vendor notices, spreadsheets, paper invoices, and staff memory to determine whether affected products are present on site.

Operational problems include:

- Recall notices contain inconsistent product names, lot codes, brands, pack sizes, and distribution regions.
- Store shelves and stockrooms may contain products that are not reflected in clean digital inventory.
- Invoices and receipts are often PDFs, scans, or photos.
- Staff need plain-language guidance on what to remove, quarantine, document, or escalate.
- Duplicate recall notices and vague alerts create unnecessary noise.
- Small teams lack the tooling large retailers use for automated recall response.

RecallRadar AI solves this by connecting public recall data to local product evidence using Hugging Face tasks across vision, language, document QA, tabular modeling, and retrieval.

## 3. Real-World Users

### Independent Grocery Owner

Needs to quickly determine whether any recalled products are on shelves or in backstock.

### Restaurant or Campus Dining Manager

Needs to check invoices and supplier records against new recalls before serving food.

### Food Bank Operations Lead

Needs to screen donated products and inventory for recall exposure with limited staff.

### Quality Assurance Coordinator

Needs an auditable workflow showing what was checked, what matched, and what action was taken.

### Hiring Manager or Portfolio Reviewer

Needs to see a project that demonstrates production-minded AI engineering, not just prompt usage.

## 4. Key Hugging Face Tasks

### Multimodal Tasks

- **Image-Text-to-Text:** Ask questions about shelf, pantry, or stockroom images.
- **Visual Question Answering:** Answer questions such as "Is this product the recalled brand?" or "Can you see a lot code?"
- **Document Question Answering:** Extract invoice numbers, vendors, product names, quantities, dates, UPCs, and lot codes from scanned invoices or PDFs.
- **Visual Document Retrieval:** Retrieve the invoice, packing slip, or supplier notice most relevant to a recall.

### Computer Vision Tasks

- **Image Classification:** Classify product photos by broad category such as dairy, frozen food, canned goods, produce, snacks, supplements, meat, or prepared meals.
- **Object Detection:** Detect packaged products, labels, barcodes, nutrition panels, expiration labels, or shelf tags.
- **Zero-Shot Object Detection:** Search images for prompted product types or packaging features without training a custom detector.
- **Image-to-Text:** Generate captions from product and shelf images.
- **Image Feature Extraction:** Create visual embeddings for product-image similarity search.
- **Image Segmentation:** Isolate product packaging from cluttered shelf photos for better recognition.

### Natural Language Processing Tasks

- **Text Classification:** Classify recall severity, product type, allergen risk, pathogen risk, or action urgency.
- **Token Classification:** Extract entities such as brand, product name, lot code, UPC, state, firm, contaminant, allergen, and recall class.
- **Summarization:** Convert long recall notices into concise operational instructions.
- **Question Answering:** Answer user questions over recall notices and local evidence.
- **Sentence Similarity:** Match fuzzy product descriptions from recalls to messy inventory names.
- **Text Ranking:** Rank likely inventory, invoice, or photo matches for each recall.
- **Zero-Shot Classification:** Classify unfamiliar recall categories without a custom labeled dataset.
- **Translation:** Translate recall summaries or staff instructions for multilingual teams.

### Tabular Tasks

- **Tabular Classification:** Predict whether an inventory item is likely affected by a recall.
- **Tabular Regression:** Estimate recall exposure score or expected units-at-risk.
- **Time Series Forecasting:** Forecast recall workload, product-risk trends, or inspection demand by category.

### Optional Audio Tasks

- **Automatic Speech Recognition:** Let staff record a voice note while checking shelves.
- **Text-to-Speech:** Generate spoken recall instructions for workers using mobile devices.

## 5. Real-World Data Sources

### Recall and Safety APIs

- **openFDA Food Recall Enforcement Reports:** Public FDA recall enforcement data returned as JSON.
- **openFDA Food Adverse Events:** Public adverse-event data related to foods, dietary supplements, and cosmetics.
- **USDA FSIS Recall API:** Recall and public health alert data for meat, poultry, and egg products.

### Food Product Data

- **USDA FoodData Central API:** Food search and food detail endpoints, including branded food data.
- **Open Food Facts API:** Product names, brands, ingredients, nutrition, packaging, and barcode data.

### Local Business Data

- Uploaded inventory CSV files.
- POS exports.
- Supplier invoices.
- Packing slips.
- Receipt photos.
- Shelf and stockroom images.
- Manual product scans.

### Optional Contextual Data

- State distribution fields from recall records.
- Store locations and service areas.
- Supplier master data.
- Sales velocity and inventory counts.

## 6. Product Capabilities

### 6.1 Recall Monitoring

The system periodically imports recall and alert data from FDA and USDA sources.

Each recall record is normalized into:

- Recall ID.
- Source agency.
- Product name.
- Brand.
- Firm.
- Recall class.
- Reason for recall.
- Contaminant or allergen.
- Distribution states.
- Dates.
- Affected lot codes.
- UPCs or product identifiers when available.
- Recommended action.
- Source URL and raw payload.

### 6.2 Local Inventory Matching

RecallRadar AI compares recall records against local inventory and purchasing evidence.

Matching signals include:

- Exact UPC match.
- Brand similarity.
- Product-name similarity.
- Lot-code match.
- Supplier match.
- Distribution-region match.
- Purchase-date overlap.
- Visual package similarity.
- Invoice or receipt evidence.

The output is an explainable match score with evidence attached.

### 6.3 Shelf and Stockroom Image Analysis

Staff can upload photos from shelves, coolers, freezers, pantries, or storage areas.

The vision pipeline:

1. Detects visible packaged products.
2. Crops likely product regions.
3. Generates captions and OCR-like product descriptions.
4. Searches for visible brands, labels, codes, or barcode regions.
5. Compares visual features against known affected products.
6. Flags possible matches for human review.

### 6.4 Invoice and Receipt Intelligence

Users can upload PDFs, scans, or photos of invoices and receipts.

The document pipeline extracts:

- Vendor.
- Invoice date.
- Product descriptions.
- Quantities.
- Prices.
- Lot codes.
- UPCs.
- Purchase order numbers.
- Delivery location.

Document Question Answering allows users to ask:

- "Did we buy this product in the affected date range?"
- "Which vendor supplied this brand?"
- "What lot codes appear on this invoice?"
- "How many cases were delivered?"

### 6.5 Recall Action Center

Each recall gets an operational response page with:

- AI-generated plain-language summary.
- Risk category and urgency.
- Matched inventory items.
- Matched invoices or receipts.
- Matched shelf photos.
- Evidence score.
- Recommended actions.
- Staff assignment.
- Resolution checklist.
- Audit log.

### 6.6 Multilingual Staff Instructions

Recall notices can be translated into clear instructions for multilingual teams.

Example outputs:

- "Remove affected product from shelf."
- "Check freezer inventory for this brand and lot code."
- "Quarantine matching items pending manager review."
- "Photograph product labels before disposal."

### 6.7 Search and Natural-Language Investigation

Users can ask:

- "Do we have any active Class I recalls involving dairy?"
- "Show recalls that mention undeclared peanuts."
- "Which invoices mention the recalled brand?"
- "Find shelf photos that may contain this product."
- "Which locations have unresolved high-risk matches?"

The system combines structured search, vector retrieval, document QA, and AI summaries.

## 7. Recommended Technical Architecture

## 7.1 Frontend

Recommended stack:

- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui or Radix UI
- TanStack Query
- TanStack Table
- Recharts or Observable Plot
- Browser camera upload support

Primary views:

- Recall inbox.
- Recall detail and action center.
- Inventory match review.
- Shelf image review.
- Invoice/document search.
- Risk analytics dashboard.
- Staff task board.
- Model evaluation page.

## 7.2 Backend API

Recommended stack:

- Python FastAPI for AI services.
- Node.js/NestJS or FastAPI for product API.
- OpenAPI-generated client.
- REST endpoints for predictable integration.

Core services:

- Recall ingestion service.
- Inventory import service.
- Product matching service.
- Document extraction service.
- Image analysis service.
- Alerting service.
- User review service.
- Audit logging service.

## 7.3 Data Layer

Recommended stack:

- PostgreSQL for relational records.
- pgvector, Qdrant, or Weaviate for semantic and visual embeddings.
- Redis for background jobs and caching.
- S3-compatible object storage for images and documents.
- Optional Elasticsearch or OpenSearch for keyword search.

Core tables:

- `recalls`
- `recall_products`
- `inventory_items`
- `suppliers`
- `locations`
- `invoices`
- `invoice_line_items`
- `product_images`
- `image_detections`
- `recall_matches`
- `staff_tasks`
- `human_reviews`
- `model_runs`
- `audit_events`

## 7.4 Async Processing

Recommended stack:

- Celery, RQ, BullMQ, or Temporal.
- Redis or RabbitMQ queue.

Example jobs:

- `sync_openfda_recalls`
- `sync_fsis_recalls`
- `normalize_recall_record`
- `embed_recall_text`
- `import_inventory_csv`
- `parse_invoice_document`
- `analyze_shelf_image`
- `score_inventory_matches`
- `generate_recall_summary`
- `translate_staff_instructions`
- `send_alerts`

## 7.5 AI/ML Layer

Recommended tools:

- Hugging Face Transformers.
- Sentence Transformers.
- PyTorch.
- OCR tooling such as Tesseract, PaddleOCR, or cloud OCR for fallback.
- ONNX Runtime for optimized inference.
- MLflow or Weights & Biases for experiment tracking.

Model responsibilities:

- Entity extraction from recall text.
- Semantic matching between recalls and inventory.
- Document QA over invoices.
- Image captioning and visual matching.
- Recall severity classification.
- Summary generation.
- Multilingual instruction generation.

## 7.6 Deployment and Operations

Recommended stack:

- Docker Compose for local development.
- GitHub Actions for tests and builds.
- Fly.io, Render, Railway, AWS ECS, or GCP Cloud Run.
- Managed PostgreSQL.
- Managed object storage.
- Sentry for error monitoring.
- OpenTelemetry for traces.
- Prometheus and Grafana for metrics.

Important operational metrics:

- Recall ingestion freshness.
- Match scoring latency.
- Queue depth.
- Number of high-risk unresolved matches.
- Human correction rate.
- False positive match rate.
- False negative discoveries from manual review.
- Document extraction success rate.
- Image analysis confidence distribution.

## 8. High-Level System Flow

```text
openFDA / USDA FSIS / USDA FoodData Central / Open Food Facts
        |
        v
Recall and Product Ingestion Services
        |
        v
Normalized Recall + Product Database
        |
        v
Local Inventory, Invoices, Receipts, Shelf Images
        |
        v
Async AI Processing Queue
        |
        v
Text Extraction + Document QA + Vision Models + Embeddings
        |
        v
Recall Match Scoring + Evidence Ranking
        |
        v
Recall Action Center + Alerts + Human Review
```

## 9. Minimum Viable Product Scope

The MVP should support a single organization with uploaded inventory and public recall monitoring.

Recommended MVP:

- Import recent food recalls from openFDA.
- Import USDA FSIS recalls.
- Upload inventory CSV files.
- Normalize recall and inventory product names.
- Use sentence similarity to match recalls to inventory.
- Generate AI summaries of recall notices.
- Display a recall inbox with severity and match count.
- Build a recall detail page with evidence and recommended actions.
- Upload invoices and extract product line items.
- Add human review controls for match approval or rejection.

This MVP is achievable in 4-6 weeks and already demonstrates useful AI, data engineering, and workflow design.

## 10. Stretch Features

- Shelf photo upload and product detection.
- Barcode scanning from mobile camera.
- Visual product matching using image embeddings.
- Document QA over invoices and supplier notices.
- Multilingual staff instructions.
- Email or SMS alerting.
- Multi-location support.
- Role-based permissions.
- Recall workload forecasting.
- Active learning from human corrections.
- Supplier risk analytics.
- Public demo mode with seeded sample inventory.

## 11. Technical Risks and Mitigations

### Risk: Recall Data Is Messy

Recall records may have inconsistent product names, incomplete UPCs, vague distribution data, or missing lot codes.

Mitigation:

- Store raw records.
- Normalize fields into structured entities.
- Use fuzzy and semantic matching.
- Show evidence instead of making hidden decisions.
- Require human confirmation for high-impact actions.

### Risk: Product Matching False Positives

Loose semantic matching may flag unrelated products.

Mitigation:

- Combine multiple signals.
- Weight exact UPC and lot-code matches higher.
- Require review for uncertain matches.
- Track false positives in evaluation dashboards.

### Risk: Image Analysis Limitations

Shelf images can be blurry, crowded, or partially blocked.

Mitigation:

- Ask for close-up product label photos when confidence is low.
- Use image segmentation and cropped detections.
- Treat image results as supporting evidence.
- Provide confidence scores and review workflows.

### Risk: Medical or Safety Overclaiming

The platform should not make medical decisions or replace official recall guidance.

Mitigation:

- Always link to source recall notices.
- Present AI output as operational assistance.
- Preserve source text.
- Include audit trails.
- Require human sign-off for closure.

### Risk: API Rate Limits

External APIs may limit request volume.

Mitigation:

- Cache recall records.
- Schedule sync jobs.
- Use incremental updates.
- Store source payload snapshots.
- Respect API key requirements and terms.

## 12. Evaluation Strategy

Evaluate the system using:

- Recall-to-inventory match precision.
- Recall-to-inventory match recall.
- Human approval and rejection rates.
- Entity extraction accuracy for brands, lot codes, UPCs, and allergens.
- Document extraction accuracy from invoices.
- Image detection confidence and correction rates.
- Average time from recall ingestion to staff alert.
- Average time from alert to action completion.

Useful evaluation views:

- Confusion matrix for severity classification.
- Top false-positive product matches.
- Match score distribution by signal type.
- OCR/document extraction failure report.
- Human corrections by supplier or product category.
- Time-to-resolution dashboard.

## 13. Suggested 12-Week Build Plan

### Weeks 1-2: Data and Product Foundation

- Set up repository, Docker, database, and API structure.
- Build recall ingestion from openFDA and USDA FSIS.
- Create normalized recall schema.
- Build initial recall inbox UI.

### Weeks 3-4: Inventory Matching

- Add inventory CSV upload.
- Normalize inventory item names.
- Generate text embeddings for recalls and inventory.
- Implement fuzzy and semantic matching.
- Build match review UI.

### Weeks 5-6: Summaries and Action Workflow

- Add recall summarization.
- Generate recommended action steps.
- Build recall action center.
- Add staff task statuses and audit events.

### Weeks 7-8: Document Intelligence

- Add invoice and receipt upload.
- Extract line items and supplier metadata.
- Add document QA.
- Link invoices to recall matches.

### Weeks 9-10: Vision Pipeline

- Add shelf and product image upload.
- Implement image captioning and product detection.
- Add visual product matching.
- Build image review workflow.

### Weeks 11-12: Evaluation and Polish

- Add model evaluation dashboard.
- Add alerting.
- Improve UX, loading states, and accessibility.
- Add integration tests and seed data.
- Deploy public demo and write portfolio case study.

## 14. Portfolio Value

RecallRadar AI is portfolio-worthy because it demonstrates:

- Real-time public API ingestion.
- Multimodal AI across text, documents, and images.
- Entity extraction and fuzzy matching.
- Vector search and ranking.
- Workflow software for real operational decisions.
- Safety-aware UX with human review.
- Auditable AI outputs.
- Practical deployment architecture.
- Evaluation and monitoring.

It also has a strong demo story. A reviewer can upload sample inventory, watch new recalls appear, see AI match likely affected products, inspect invoice evidence, and resolve a task through a realistic operations flow.

## 15. Resume-Ready Impact Statements

- Built a multimodal food-safety intelligence platform that ingests FDA and USDA recall APIs, matches recalls against inventory, and generates auditable staff action workflows.
- Integrated Hugging Face NLP, document QA, image-to-text, object detection, and embedding models to analyze recall notices, invoices, receipts, and shelf photos.
- Designed a recall matching engine combining UPC, lot-code, supplier, semantic similarity, visual evidence, and distribution-region signals.
- Implemented human-in-the-loop review, confidence scoring, audit logging, and evaluation dashboards to reduce false positives in safety-critical workflows.
- Developed a production-style architecture using FastAPI, PostgreSQL, vector search, Redis queues, object storage, Docker, and CI/CD.

## 16. Why This Stands Out in the 2025 Job Market

RecallRadar AI stands out because it is not another general-purpose chatbot. It applies AI to a narrow, high-stakes operational workflow where reliability, evidence, and reviewability matter.

The project shows employers that you can:

- Work with real public APIs.
- Build robust data pipelines.
- Combine multiple AI model types.
- Design useful human-centered workflows.
- Think about safety, uncertainty, and auditability.
- Ship a product-shaped system with measurable impact.

This is the kind of project that can become a GitHub repository, demo video, technical blog post, architecture diagram, and strong interview discussion.

## 17. Public API References

- openFDA APIs: https://open.fda.gov/apis/
- openFDA Food Recall Enforcement Reports: https://open.fda.gov/apis/food/enforcement/
- USDA FoodData Central API Guide: https://fdc.nal.usda.gov/api-guide/
- USDA FSIS Recall API: https://www.fsis.usda.gov/science-data/developer-resources/recall-api
- Hugging Face Tasks: https://huggingface.co/tasks

