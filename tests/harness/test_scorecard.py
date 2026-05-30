"""Unit tests for the deterministic sample-aggregation and scorecard I/O core."""
from __future__ import annotations

import pytest

from evals.harness.scorecard import (
    SCHEMA_VERSION,
    Scorecard,
    ScenarioResult,
    aggregate_samples,
)


def test_aggregate_basic_pass_rates():
    samples = [
        {"a": True, "b": True},
        {"a": True, "b": False},
        {"a": True, "b": True},
        {"a": False, "b": True},
    ]
    res = aggregate_samples("s", samples)
    assert res.n_samples == 4
    by_name = {a.name: a for a in res.assertions}
    assert by_name["a"].pass_count == 3
    assert by_name["b"].pass_count == 3
    assert by_name["a"].pass_rate == 0.75


def test_scenario_pass_requires_every_assertion():
    samples = [
        {"a": True, "b": True},  # passes
        {"a": True, "b": False},  # fails (b)
        {"a": False, "b": True},  # fails (a)
    ]
    res = aggregate_samples("s", samples)
    assert res.pass_count == 1
    assert res.pass_rate == pytest.approx(1 / 3)


def test_single_assertion_perfect_run():
    res = aggregate_samples("s", [{"x": True}] * 5)
    assert res.pass_count == 5
    assert res.pass_rate == 1.0


def test_mismatched_assertion_keys_raise():
    with pytest.raises(ValueError, match="assertion names"):
        aggregate_samples("s", [{"a": True}, {"b": True}])


def test_empty_samples_raise():
    with pytest.raises(ValueError, match="at least one sample"):
        aggregate_samples("s", [])


def test_scorecard_round_trip(tmp_path):
    scorecard = Scorecard.build(
        scenarios=[
            aggregate_samples("agent/x", [{"contains": True, "judge": True}] * 3),
            aggregate_samples("skill/y", [{"contains": True, "judge": False}] * 2),
        ],
        model="claude-sonnet-4-6",
        generated="2026-05-29T12:00:00+00:00",
    )
    path = tmp_path / "scorecard.json"
    scorecard.write(path)
    loaded = Scorecard.read(path)

    assert loaded.model == "claude-sonnet-4-6"
    assert loaded.generated == "2026-05-29T12:00:00+00:00"
    assert {s.id for s in loaded.scenarios} == {"agent/x", "skill/y"}
    y = next(s for s in loaded.scenarios if s.id == "skill/y")
    assert y.pass_rate == 0.0  # judge fails every sample


def test_from_dict_rejects_unknown_version():
    bad = {"schema_version": SCHEMA_VERSION + 99, "model": "m", "generated": "t", "scenarios": []}
    with pytest.raises(ValueError, match="schema_version"):
        Scorecard.from_dict(bad)


def test_scenario_result_zero_samples_is_safe():
    # Construction guards against div-by-zero even if a degenerate result is built.
    res = ScenarioResult(id="s", n_samples=0, pass_count=0, assertions=())
    assert res.pass_rate == 0.0
