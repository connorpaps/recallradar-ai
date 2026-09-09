# Matching evaluation

RecallRadar uses deterministic matching for the release path. The evaluator runs the real scoring function against the bundled MetroMart portfolio fixture, compares predictions with eight labeled recall/inventory pairs, and reports evidence before any optional AI signal is enabled.

Run it from `backend`:

```text
.venv/Scripts/python -m scripts.evaluate_matching
```

Current verified result:

```json
{
  "min_score": 0.5,
  "total_cases": 240,
  "expected_matches": 8,
  "predicted_matches": 8,
  "true_positives": 8,
  "false_positives": 0,
  "false_negatives": 0,
  "precision": 1.0,
  "recall": 1.0,
  "high_confidence_predictions": 5,
  "medium_confidence_predictions": 3
}
```

## Interpretation

- **Match confidence** estimates whether the inventory item corresponds to the recall.
- **Operational exposure** estimates urgency from quantity, location, service context, and recall severity.
- A high exposure score does not turn an uncertain match into a confirmed recall.
- Human review remains required before confirmation, dismissal, resolution, or reopening.
- The evaluation is fixture-backed evidence for the portfolio scenario. It does not establish production accuracy on arbitrary FDA records.

The surfaced release threshold is `0.50`. This avoids presenting weak lexical coincidences as operational matches while retaining the known high- and medium-confidence examples required for the demo.
