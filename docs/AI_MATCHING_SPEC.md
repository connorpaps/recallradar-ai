# RecallRadar AI Matching Specification

## 1. Purpose

The matching engine determines whether a public food recall may apply to a local inventory item.

The engine must be explainable. Users should know why a match was suggested, which fields contributed, and how confident the system is.

V1 prioritizes transparent scoring over opaque model behavior. More advanced Hugging Face models can be added behind the same interface later.

## 2. Inputs

Recall inputs:

- Product description.
- Brand name.
- Recalling firm.
- Reason for recall.
- Classification.
- Distribution pattern.
- Recall dates.
- Raw source payload.

Inventory inputs:

- Product name.
- Brand.
- UPC.
- Lot code.
- Quantity.
- Location.
- Supplier.
- Purchase date.
- Raw CSV row.

## 3. Normalization

Normalize text before matching:

- Lowercase.
- Trim whitespace.
- Remove punctuation noise.
- Normalize common units.
- Remove duplicate spaces.
- Strip common legal suffixes from firms where useful.
- Preserve raw values for display.

Example:

```text
"Fresh Valley, Inc. Organic Baby Spinach 5 OZ"
-> "fresh valley organic baby spinach 5 oz"
```

## 4. V1 Scoring Signals

Each signal returns a score from `0.0` to `1.0` and a human-readable explanation.

### Product Similarity

Compares recall product description to inventory product name.

Recommended V1 approach:

- Token overlap.
- Fuzzy ratio.
- Optional sentence embedding similarity.

Default weight: `0.35`

### Brand Similarity

Compares recall brand or recalling firm to inventory brand.

Default weight: `0.25`

### UPC Match

Checks exact UPC match when both sides have UPC data.

Default weight: `0.20`

Rules:

- Exact match returns `1.0`.
- Missing data returns neutral `0.0` but should not create a negative explanation.
- Conflicting UPCs can reduce confidence.

### Lot Code Match

Checks exact or partial lot-code match.

Default weight: `0.15`

Rules:

- Exact lot-code match is strong evidence.
- Partial visible lot-code match is medium evidence.
- Missing lot codes are common and should not block matching.

### Distribution Relevance

Checks whether recall distribution text appears compatible with inventory location.

Default weight: `0.05`

Examples:

- Recall distribution includes the user's state.
- Distribution says nationwide.
- Distribution is unknown.

## 5. Score Formula

V1 score:

```text
score = weighted_sum(signal_score * signal_weight)
```

After calculating weighted score, apply boosts:

- Exact UPC match: add up to `0.15`.
- Exact lot-code match: add up to `0.15`.
- Exact brand plus strong product similarity: add up to `0.10`.

Apply penalties:

- Clear UPC conflict: subtract up to `0.20`.
- Clear product category conflict: subtract up to `0.20`.

Final score is clamped between `0.0` and `1.0`.

## 6. Confidence Levels

Recommended thresholds:

- `high`: score >= `0.75`
- `medium`: score >= `0.50` and < `0.75`
- `low`: score >= `0.35` and < `0.50`
- below `0.35`: do not persist by default

The threshold can be adjusted in development based on seed data quality.

## 7. Match Explanation

Every persisted match should include:

- Short summary sentence.
- List of positive signals.
- List of missing or uncertain signals.
- Any conflicts.

Example:

```text
Fresh Valley Organic Spinach may match this recall because the brand names are nearly identical and both product descriptions reference organic spinach. No UPC or lot code was available in the recall notice, so this should be reviewed before action.
```

## 8. Signal JSON Shape

```json
[
  {
    "name": "product_similarity",
    "score": 0.86,
    "weight": 0.35,
    "matched_values": {
      "recall": "organic baby spinach",
      "inventory": "fresh valley organic spinach"
    },
    "detail": "Product names both reference organic spinach."
  }
]
```

## 9. AI Integration Roadmap

## V2 Exposure Scoring

V2 keeps matching confidence separate from operational exposure:

- `score` answers whether an inventory item appears to match a recall.
- `exposure_score` answers how urgent that possible match is for the organization.

Default exposure inputs:

- Match confidence.
- Recall class.
- Lot or UPC exactness.
- Quantity.
- Location criticality and public-serving status.
- Supplier overlap.
- Review status pressure.

### Phase 1: Deterministic Matching

- Token overlap.
- Fuzzy string similarity.
- Exact UPC and lot-code matching.
- Explanation templates.

### Phase 2: Semantic Similarity

Hugging Face task:

- Sentence Similarity.
- Feature Extraction.
- Text Ranking.

Use embeddings to compare:

- Recall product description.
- Inventory product name.
- Recall reason.
- Supplier descriptions.

### Phase 3: Entity Extraction

Hugging Face task:

- Token Classification.

Extract:

- Brand.
- Product.
- Lot code.
- UPC.
- Allergen.
- Pathogen.
- Distribution region.
- Firm.

### Phase 4: Summarization

Hugging Face task:

- Summarization.

Generate:

- Plain-language recall summaries.
- Staff action instructions.
- Risk summaries.

### Phase 5: Document QA

Hugging Face task:

- Document Question Answering.
- Visual Document Retrieval.

Support:

- Supplier invoices.
- Packing slips.
- Product notices.
- Purchase records.

### Phase 6: Shelf Image Analysis

Hugging Face task:

- Image-to-Text.
- Visual Question Answering.
- Object Detection.
- Zero-Shot Object Detection.
- Image Feature Extraction.

Support:

- Product label recognition.
- Shelf photo search.
- Visual package similarity.
- Barcode or lot-code region detection.

## 10. Evaluation Metrics

Track:

- Precision of suggested matches.
- Recall of known seeded matches.
- False-positive rate.
- Human dismissal rate.
- Human confirmation rate.
- Score distribution.
- Signal contribution distribution.
- Average matches per recall.

Seed data should include known expected matches so the engine can be tested deterministically.
