"""Behavioural eval: the spec-readiness-reviewer agent on a planted spec.

The per-sample logic lives in `scenario.py` so the optimiser (`evals.optimize`) can
drive the exact same code path and obtain a continuous gradient. This test threshold-s
the per-assertion floats back into booleans for the binary scorecard the rest of the
harness expects.

Skipped unless RUN_EVALS=1.
"""
from __future__ import annotations

import pytest

from evals.harness.scorecard import aggregate_samples
from evals.scenarios.spec_readiness_reviewer import scenario


@pytest.mark.behavioural
def test_planted_findings(plugin_dir, tmp_path, record_scorecard, n_samples, threshold):
    repo = scenario.prepare_fixture(tmp_path)

    samples = []
    for _ in range(n_samples):
        raw = scenario.run_one_sample(plugin_dir, repo)
        # Threshold per-assertion floats to booleans for the scorecard (judge >= 0.5 = pass).
        samples.append({k: v >= 0.5 for k, v in raw.items()})

    result = aggregate_samples(scenario.SCENARIO_ID, samples)
    record_scorecard(result)
    assert result.pass_rate >= threshold, (
        f"{scenario.SCENARIO_ID}: pass-rate {result.pass_rate:.0%} < threshold {threshold:.0%}"
    )
