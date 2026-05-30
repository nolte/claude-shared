"""Unit tests for the optimiser's pure accept/revert and early-stop logic (no LLM calls)."""
from __future__ import annotations

from evals.optimize import decide, should_stop


def test_decide_accepts_only_strict_improvement():
    assert decide(best=0.5, candidate=0.75) == "accept"
    assert decide(best=0.5, candidate=0.5) == "revert"  # equal is not an improvement
    assert decide(best=0.5, candidate=0.25) == "revert"


def test_should_stop_at_or_above_quality():
    assert should_stop(1.0, quality=1.0) is True
    assert should_stop(0.9, quality=1.0) is False
    assert should_stop(0.67, quality=0.6) is True
