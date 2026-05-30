"""Per-sample scenario logic for the spec-readiness-reviewer eval.

Factored out of the pytest test so the optimiser can call the SAME code path directly
(without going through pytest + a boolean scorecard) and get a continuous score with a
real gradient. Both call-sites — the test and the optimiser — agree on what the scenario
expects.
"""
from __future__ import annotations

import shutil
from pathlib import Path
from statistics import mean

from evals.harness import judge, runner

SCENARIO_ID = "spec-readiness-reviewer/planted-findings"
FIXTURE_SRC = Path(__file__).parent / "fixture"

RUBRIC = """\
The OUTPUT is a spec-readiness audit report for spec/project/widget-config.
Score on the continuous scale [0, 1] based on how many of the following are met:
1. It reports the same-subject MUST vs MUST NOT contradiction about caching the resolved
   widget configuration, classified as Critical.
2. It flags the orphan Acceptance Criterion (the "audit log is rotated daily" criterion,
   which maps to no Requirement) as a Warning.
3. Findings use only the canonical severity buckets (Critical, Warning, Suggestion, Info)
   with no invented levels.
4. At least one finding cites a concrete spec path and a line or section reference.
5. The report does not claim to have edited, created, or written any file.
"""


def make_prompt() -> str:
    return runner.agent_prompt(
        "spec-readiness-reviewer",
        "audit the spec at spec/project/widget-config for readiness, covering "
        "contradictions and acceptance-criterion coverage.",
    )


def prepare_fixture(tmp_root: Path) -> Path:
    """Copy the bundled fixture mini-repo into `tmp_root/repo` and return the new path."""
    dst = Path(tmp_root) / "repo"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(FIXTURE_SRC, dst)
    return dst


def run_one_sample(plugin_dir: str, fixture_dir: Path, model: str | None = None) -> dict[str, float]:
    """Drive one live run + judge; return per-assertion scores in [0, 1].

    Booleans land as 0.0/1.0; the judge contributes a continuous score so the aggregate
    has a real gradient for the optimiser to climb.
    """
    report = runner.run_headless(
        make_prompt(),
        plugin_dir,
        cwd=str(fixture_dir),
        allowed_tools=runner.READONLY_TOOLS,
        permission_mode="plan",
        model=model,
    ).text
    return {
        "mentions-caching-contradiction": 1.0 if "cach" in report.lower() else 0.0,
        "uses-Critical-severity": 1.0 if "Critical" in report else 0.0,
        "judge:rubric": judge.judge_score(report, RUBRIC, model=model),
    }


def continuous_score(sample: dict[str, float]) -> float:
    """Mean of all per-assertion scores. Always in [0, 1]."""
    return mean(sample.values())
