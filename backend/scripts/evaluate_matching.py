import json
import sys

from app.services.evaluation import evaluate_portfolio_matching, portfolio_release_gate_failures

if __name__ == "__main__":
    metrics = evaluate_portfolio_matching()
    print(json.dumps(metrics, indent=2))
    failures = portfolio_release_gate_failures(metrics)
    if failures:
        print("Portfolio matching release gate failed:", file=sys.stderr)
        print("\n".join(f"- {failure}" for failure in failures), file=sys.stderr)
        raise SystemExit(1)
