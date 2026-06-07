"""Unit tests for the baseline-vs-change scorecard diff (the regression engine)."""
from __future__ import annotations

from evals.harness.compare import diff_scorecards, main
from evals.harness.scorecard import Scorecard, aggregate_samples


def _card(rates: dict[str, float], n: int = 4, model: str = "m") -> Scorecard:
    """Build a scorecard whose scenarios have the given pass-rates (n samples each)."""
    scenarios = []
    for sid, rate in rates.items():
        passes = round(rate * n)
        samples = [{"j": i < passes} for i in range(n)]
        scenarios.append(aggregate_samples(sid, samples))
    return Scorecard.build(scenarios, model=model, generated="t")


def test_regression_detected():
    base = _card({"s": 1.0})
    head = _card({"s": 0.5})
    diff = diff_scorecards(base, head)
    assert diff.has_regression
    assert diff.rows[0].status(0.0) == "regressed"
    assert diff.rows[0].delta == -0.5


def test_improvement_no_regression():
    diff = diff_scorecards(_card({"s": 0.5}), _card({"s": 1.0}))
    assert not diff.has_regression
    assert diff.rows[0].status(0.0) == "improved"


def test_unchanged_within_tolerance():
    base = _card({"s": 1.0})
    head = _card({"s": 0.75})  # -25%
    assert diff_scorecards(base, head, tolerance=0.25).has_regression is False
    assert diff_scorecards(base, head, tolerance=0.10).has_regression is True


def test_new_scenario_is_not_a_regression():
    diff = diff_scorecards(_card({"a": 1.0}), _card({"a": 1.0, "b": 1.0}))
    assert not diff.has_regression
    b = next(r for r in diff.rows if r.scenario_id == "b")
    assert b.status(0.0) == "new"
    assert b.base_rate is None


def test_removed_scenario_counts_as_regression():
    diff = diff_scorecards(_card({"a": 1.0, "b": 1.0}), _card({"a": 1.0}))
    assert diff.has_regression
    b = next(r for r in diff.rows if r.scenario_id == "b")
    assert b.status(0.0) == "removed"


def test_main_exit_codes(tmp_path):
    base_p = tmp_path / "base.json"
    head_p = tmp_path / "head.json"
    _card({"s": 1.0}).write(base_p)

    _card({"s": 1.0}).write(head_p)
    assert main([str(base_p), str(head_p)]) == 0

    _card({"s": 0.5}).write(head_p)
    assert main([str(base_p), str(head_p)]) == 1
    assert main([str(base_p), str(head_p), "--tolerance", "0.6"]) == 0
