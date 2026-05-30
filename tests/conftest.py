"""Shared pytest fixtures for the eval harness.

Behavioural tests (marked ``behavioural``) drive a real skill/agent via the Anthropic
API and are skipped unless ``RUN_EVALS=1``. When they do run, each test appends its
`ScenarioResult` via the `record_scorecard` fixture; the session writes a single
`scorecard.json` at teardown, which `evals.harness.compare` then diffs across runs.
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

from evals.harness import runner
from evals.harness.scorecard import Scorecard

REPO_ROOT = Path(__file__).resolve().parents[1]  # the plugin dir (contains .claude-plugin)


def pytest_collection_modifyitems(config, items):
    if os.environ.get("RUN_EVALS") == "1":
        return
    skip = pytest.mark.skip(reason="behavioural eval; set RUN_EVALS=1 to run (incurs API cost)")
    for item in items:
        if "behavioural" in item.keywords:
            item.add_marker(skip)


@pytest.fixture
def plugin_dir() -> str:
    return str(REPO_ROOT)


@pytest.fixture
def fixture_repo(tmp_path):
    """Copy a scenario's ``fixture/`` mini-repo into a fresh tmp dir; return its path.

    Copying (never the live tree) is what lets a file-mutating skill scribble freely and
    lets the test assert on the *resulting* files without touching the real repo.
    """

    def _make(scenario_dir) -> Path:
        src = Path(scenario_dir) / "fixture"
        dst = tmp_path / "repo"
        shutil.copytree(src, dst)
        return dst

    return _make


@pytest.fixture(scope="session")
def _scorecard_collector():
    results: list = []
    yield results
    if not results:
        return
    out = Path(
        os.environ.get("EVAL_SCORECARD", str(REPO_ROOT / "evals" / "out" / "scorecard.json"))
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    Scorecard.build(results, model=runner.eval_model()).write(out)


@pytest.fixture
def record_scorecard(_scorecard_collector):
    """Return a callable that records a `ScenarioResult` into the session scorecard."""
    return _scorecard_collector.append


@pytest.fixture
def n_samples() -> int:
    return int(os.environ.get("EVAL_SAMPLES", "3"))


@pytest.fixture
def threshold() -> float:
    return float(os.environ.get("EVAL_THRESHOLD", "0.6"))
