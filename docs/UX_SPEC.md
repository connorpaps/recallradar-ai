# RecallRadar AI UX Specification

## 1. UX Goal

RecallRadar should feel like a calm, practical operations dashboard for food-safety review. The UI should prioritize clarity, evidence, and fast decision-making.

The design should avoid marketing-page styling. The first screen should be the usable dashboard.

## 2. Navigation

Primary navigation:

- Dashboard
- Recalls
- Review Queue
- Inventory
- Imports

Secondary or later navigation:

- Documents
- Images
- Evaluation
- Settings

## 3. Visual Style

Recommended tone:

- Clean.
- Operational.
- High trust.
- High contrast.
- Minimal decoration.

Recommended color roles:

- Red: high-risk or urgent recall.
- Amber: medium confidence or needs review.
- Green: resolved or confirmed safe.
- Blue: neutral information.
- Gray: inactive, dismissed, or source metadata.

Avoid a one-note palette. Use color sparingly for status and priority.

## 4. Dashboard

Purpose:

Give the user immediate operational status.

Content:

- Active recalls.
- Matches needing review.
- High-confidence matches.
- Recently uploaded inventory.
- Review status chart.
- Confidence breakdown chart.
- Recent activity list.

Primary actions:

- Import recalls.
- Upload inventory.
- Run matching.
- Open review queue.

Empty state:

- If no data exists, show actions to load seed data, import recalls, or upload inventory.

## 5. Recall Inbox

Purpose:

Let users scan active recall notices and identify which ones matter.

Columns:

- Product.
- Brand or firm.
- Recall class.
- Reason.
- Recall date.
- Match count.
- Highest confidence.
- Review status.

Filters:

- Search.
- Recall class.
- Match status.
- Confidence.
- Date range.

Row behavior:

- Click opens recall detail.
- High-confidence unresolved recalls should be visually prominent.

## 6. Recall Detail Page

Purpose:

Show source data, generated summary, matches, and review history.

Sections:

- Header with product, classification, and status.
- Source recall details.
- Plain-language summary.
- Matched inventory table.
- Evidence panel for selected match.
- Recommended action checklist.
- Audit history.

Matched inventory table columns:

- Product.
- Brand.
- UPC.
- Lot code.
- Quantity.
- Location.
- Score.
- Confidence.
- Status.
- Actions.

Review actions:

- Confirm.
- Dismiss.
- Resolve.
- Reopen.

## 7. Match Evidence Panel

Purpose:

Explain why the system suggested a match.

Content:

- Overall score.
- Confidence level.
- Explanation sentence.
- Signal chips.
- Matched field comparison.
- Missing evidence notes.
- Conflict notes.

Example signal chips:

- Brand similarity: strong.
- Product similarity: strong.
- UPC: unavailable.
- Lot code: unavailable.
- Distribution: compatible.

## 8. Inventory Upload

Purpose:

Make CSV upload predictable and recoverable.

Content:

- Required columns.
- Downloadable or visible template text.
- Upload control.
- Validation preview.
- Import summary.
- Row-level errors.

Important states:

- Uploading.
- Parsing.
- Import succeeded.
- Import partially succeeded.
- Import failed.

## 9. Review Queue

Purpose:

Give users a focused worklist.

Content:

- Match cards or table rows.
- Recall summary.
- Inventory item.
- Confidence.
- Explanation.
- Quick actions.

Sort order:

1. High confidence.
2. Newest recall.
3. Largest quantity.
4. Medium confidence.
5. Low confidence.

## 10. Interaction Principles

- Never hide source evidence.
- Always distinguish AI suggestion from human decision.
- Keep destructive actions reversible where practical.
- Make low-confidence states visually clear.
- Use concise labels.
- Avoid long instructional text inside the app.
- Show loading and error states for every network action.

## 11. Live Data UX

The empty dashboard should offer a clear live-data path:

- Refresh live openFDA recalls.
- Load company inventory.
- Run matching.

This lets portfolio reviewers evaluate the app quickly.
