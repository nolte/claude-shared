"""Behavioural eval: the readme-structure-apply skill (audit op) on a planted README.

Surface exercised: a *skill* triggered headless via its slash command. The `audit`
operation is read-only, so it is single-shot-friendly (no mid-flow approval); it must
detect the planted defect (the required "License" section is missing) and must not mutate
the README. This proves the harness drives a skill and asserts both on its report text
and on the fixture's file state — the file-side-effect dimension pytest exists for.

Skipped unless RUN_EVALS=1.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from evals.harness import judge, runner
from evals.harness.scorecard import aggregate_samples

SCENARIO_DIR = Path(__file__).parent
SCENARIO_ID = "readme-structure-apply/audit-missing-license"

RUBRIC = """\
The OUTPUT is a README-structure audit report for the repository's README.md against the
readme-structure spec. PASS only if ALL of the following hold:
1. It identifies that the required "License" section is missing from the README.
2. It reports the README as non-conformant (it is not a clean pass).
3. It does not claim to have edited, created, or written any file (audit is read-only).
"""


@pytest.mark.behavioural
def test_audit_flags_missing_license(
    plugin_dir, fixture_repo, record_scorecard, n_samples, threshold
):
    repo = fixture_repo(SCENARIO_DIR)
    readme = repo / "README.md"
    original = readme.read_text(encoding="utf-8")
    prompt = runner.skill_prompt("nolte-shared:readme-structure-apply", "audit")

    samples = []
    for _ in range(n_samples):
        report = runner.run_headless(
            prompt,
            plugin_dir,
            cwd=str(repo),
            allowed_tools=runner.READONLY_TOOLS,
            permission_mode="plan",
        ).text
        lowered = report.lower()
        samples.append(
            {
                "mentions-License": "license" in lowered,
                "flags-as-missing": any(
                    w in lowered for w in ("missing", "absent", "not present", "no license")
                ),
                "readme-unchanged": readme.read_text(encoding="utf-8") == original,
                "judge:rubric": judge.judge(report, RUBRIC),
            }
        )

    scenario = aggregate_samples(SCENARIO_ID, samples)
    record_scorecard(scenario)
    assert scenario.pass_rate >= threshold, (
        f"{SCENARIO_ID}: pass-rate {scenario.pass_rate:.0%} < threshold {threshold:.0%}"
    )
