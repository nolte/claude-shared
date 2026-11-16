"""Behavioural eval: the linux-image-scanner agent on every fixture under fixture/.

One parametrised scenario per case (`linux-image-audit/<case>`). Each sample is
one headless ``claude -p`` run with only the nolte-linux plugin loaded and the
read-only tool set, in a working directory whose path names no case; the
dispatch inputs (tracked files, validator results) are computed beforehand by
`scenario.prepare_fixture` and `scenario.make_prompt`. The inventory is scored
deterministically against the case's expected.yaml (`scenario.score`);
``EVAL_JUDGE=1`` adds an LLM-judge call per sample (off by default).

Each run passes `scenario.HEADLESS_ARGS` (``--setting-sources project
--strict-mcp-config``), so the operator's user settings, plugins, hooks, and
MCP servers stay out of it. Known limitation: whether the CLI still loads the
user's global CLAUDE.md under that flag isn't documented.

Skipped unless RUN_EVALS=1. One full run, 19 headless runs (one per case):

    RUN_EVALS=1 EVAL_SAMPLES=1 python3 -m pytest tests/e2e/linux_image_audit

writes the scorecard to evals/out/scorecard.json (or $EVAL_SCORECARD). Without
EVAL_SAMPLES the harness default of 3 samples applies (57 runs). EVAL_TIMEOUT sets
the per-run timeout in seconds (default 600); a run that hits it is recorded as a
failed sample (`run-completed` false), never dropped from the scorecard.
"""
from __future__ import annotations

import os
import shutil

import pytest

from evals.harness import judge
from evals.harness.scorecard import aggregate_samples

from . import scenario

RUBRIC = """\
The OUTPUT is a linux-image-scanner inventory for one fixture repository.
Score on the continuous scale [0, 1] by how many of these hold:
1. It follows the agent's output shape (Declaration, Mandatory pillars, Other sections,
   Not decidable statically, Health).
2. Every not-decidable result carries exactly one cause (resolvable, unverified,
   spec-gap, delegated, or evidence).
3. It assigns no severity and no gate verdict.
4. It claims no file was written, built, or executed.
5. It matches this fixture: {summary}
"""


@pytest.mark.behavioural
@pytest.mark.parametrize("case", scenario.case_names())
def test_scanner_inventory(case, record_scorecard, n_samples, threshold):
    expected = scenario.load_expected(case)
    repo = scenario.prepare_fixture(case)  # neutral path: the case id never reaches the run
    plugin_dir = str(scenario.PLUGIN_DIR)
    use_judge = os.environ.get("EVAL_JUDGE") == "1"

    samples, reasons = [], []
    try:
        for _ in range(n_samples):
            text, sample = scenario.run_one_sample(plugin_dir, repo, case)
            completed = sample["run-completed"]
            if use_judge:
                rubric = RUBRIC.format(summary=" ".join(expected["summary"].split()))
                # no judge call for a timed-out run: nothing to judge, and its own timeout would drop the case
                sample["judge:rubric"] = completed and judge.judge_score(text, rubric) >= 0.5
            samples.append(sample)
            reasons.extend(scenario.explain(text, expected) if completed else ["run timed out"])
    finally:
        shutil.rmtree(repo.parent, ignore_errors=True)

    result = aggregate_samples(f"{scenario.SCENARIO_PREFIX}/{case}", samples)
    record_scorecard(result)
    assert result.pass_rate >= threshold, (
        f"{result.id}: pass-rate {result.pass_rate:.0%} < threshold {threshold:.0%}; "
        f"failed: {sorted({a.name for a in result.assertions if a.pass_count < a.n_samples})}; "
        f"reasons: {reasons}"
    )
