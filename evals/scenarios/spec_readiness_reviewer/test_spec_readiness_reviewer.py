"""Behavioural eval: the spec-readiness-reviewer agent on a planted spec.

Surface exercised: a read-only report *agent* (input -> severity-sorted report).
The fixture spec plants a same-subject MUST-vs-MUST-NOT contradiction (caching the
resolved widget configuration) and an orphan Acceptance Criterion (audit-log rotation,
which ties to no Requirement). A correct audit surfaces both. Read-only is enforced at
the harness level (`--permission-mode plan`, `--allowedTools Read,Glob,Grep`).

Skipped unless RUN_EVALS=1.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from evals.harness import judge, runner
from evals.harness.scorecard import aggregate_samples

SCENARIO_DIR = Path(__file__).parent
SCENARIO_ID = "spec-readiness-reviewer/planted-findings"

RUBRIC = """\
The OUTPUT is a spec-readiness audit report for spec/project/widget-config.
PASS only if ALL of the following hold:
1. It reports the same-subject MUST vs MUST NOT contradiction about caching the resolved
   widget configuration, classified as Critical.
2. It flags the orphan Acceptance Criterion (the "audit log is rotated daily" criterion,
   which maps to no Requirement) as a Warning.
3. Findings use only the canonical severity buckets (Critical, Warning, Suggestion, Info)
   with no invented levels.
4. At least one finding cites a concrete spec path and a line or section reference.
5. The report does not claim to have edited, created, or written any file.
"""


@pytest.mark.behavioural
def test_planted_findings(plugin_dir, fixture_repo, record_scorecard, n_samples, threshold):
    repo = fixture_repo(SCENARIO_DIR)
    prompt = runner.agent_prompt(
        "spec-readiness-reviewer",
        "audit the spec at spec/project/widget-config for readiness, covering "
        "contradictions and acceptance-criterion coverage.",
    )

    samples = []
    for _ in range(n_samples):
        report = runner.run_headless(
            prompt,
            plugin_dir,
            cwd=str(repo),
            allowed_tools=runner.READONLY_TOOLS,
            permission_mode="plan",
        ).text
        samples.append(
            {
                "mentions-caching-contradiction": "cach" in report.lower(),
                "uses-Critical-severity": "Critical" in report,
                # "uses only canonical severity buckets" needs context (the word
                # "blocker" appears legitimately in prose), so it lives in the judge
                # rubric (item 3), not a brittle substring check here.
                "judge:rubric": judge.judge(report, RUBRIC),
            }
        )

    scenario = aggregate_samples(SCENARIO_ID, samples)
    record_scorecard(scenario)
    assert scenario.pass_rate >= threshold, (
        f"{SCENARIO_ID}: pass-rate {scenario.pass_rate:.0%} < threshold {threshold:.0%}"
    )
