from app.services.evaluation import evaluate_portfolio_matching, portfolio_release_gate_failures


def test_portfolio_matching_evaluation_meets_release_gate() -> None:
    metrics = evaluate_portfolio_matching(min_score=0.50)

    assert metrics["precision"] >= 0.95
    assert metrics["recall"] >= 0.95
    assert metrics["high_confidence_predictions"] >= 3
    assert metrics["medium_confidence_predictions"] >= 3
    assert portfolio_release_gate_failures(metrics) == []


def test_portfolio_release_gate_rejects_regression() -> None:
    metrics = evaluate_portfolio_matching()
    metrics["precision"] = 0.5
    assert portfolio_release_gate_failures(metrics)