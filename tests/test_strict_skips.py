"""Strict-skip mode of tests/conftest.py: ``CI_FAIL_ON_SKIP=1`` fails non-behavioural skips.

Each case runs an inner pytest session (``pytester``) whose conftest re-exports the
real hooks from tests/conftest.py, so the assertions exercise the shipped code.
"""
from __future__ import annotations

import pytest

pytest_plugins = ["pytester"]

INNER_CONFTEST = """
from tests.conftest import pytest_collection_modifyitems, pytest_runtest_makereport  # noqa: F401


def pytest_configure(config):
    config.addinivalue_line("markers", "behavioural: opt-in eval")
"""

REASON = "needs-the-frobnicator-binary"

CASES = f"""
import pytest


@pytest.mark.skipif(True, reason="{REASON}")
def test_skipif():
    pass


def test_inline_skip():
    pytest.skip("{REASON}")


@pytest.fixture
def needs_capability():
    pytest.skip("{REASON}")


def test_fixture_skip(needs_capability):
    pass


@pytest.mark.behavioural
def test_behavioural():
    pass


@pytest.mark.xfail(reason="known bug")
def test_xfail():
    assert False


@pytest.mark.xfail(run=False, reason="not run")
def test_xfail_not_run():
    pass


def test_passes():
    pass
"""


@pytest.fixture
def run(pytester, monkeypatch):
    monkeypatch.delenv("RUN_EVALS", raising=False)
    pytester.makeconftest(INNER_CONFTEST)
    pytester.makepyfile(test_cases=CASES)

    def _run(strict: bool):
        if strict:
            monkeypatch.setenv("CI_FAIL_ON_SKIP", "1")
        else:
            monkeypatch.delenv("CI_FAIL_ON_SKIP", raising=False)
        return pytester.runpytest("-v", "-rA", "-p", "no:cacheprovider")

    return _run


def _outcome(result, name: str) -> str:
    """Return the verbose-mode outcome word (PASSED, FAILED, ERROR, SKIPPED, XFAIL) of a test."""
    prefix = f"test_cases.py::{name} "
    hits = [line[len(prefix):].split()[0] for line in result.outlines if line.startswith(prefix)]
    assert hits, f"{name} not in output:\n{result.stdout.str()}"
    return hits[0]


def test_skipif_skip_fails_under_strict_mode(run):
    result = run(strict=True)
    # A skipif marker fires during setup, so pytest reports the failure as an ERROR.
    assert _outcome(result, "test_skipif") == "ERROR"


def test_inline_pytest_skip_fails_under_strict_mode(run):
    result = run(strict=True)
    assert _outcome(result, "test_inline_skip") == "FAILED"


def test_fixture_skip_fails_under_strict_mode(run):
    result = run(strict=True)
    assert _outcome(result, "test_fixture_skip") == "ERROR"


def test_behavioural_skip_still_skips_under_strict_mode(run):
    result = run(strict=True)
    assert _outcome(result, "test_behavioural") == "SKIPPED"
    result.assert_outcomes(passed=1, failed=1, errors=2, skipped=1, xfailed=2)
    assert "behavioural eval; set RUN_EVALS=1" in result.stdout.str()


def test_without_variable_skips_stay_skips(run):
    result = run(strict=False)
    result.assert_outcomes(passed=1, skipped=4, xfailed=2)
    assert result.ret == 0


def test_xfail_unaffected_under_strict_mode(run):
    result = run(strict=True)
    assert _outcome(result, "test_xfail") == "XFAIL"
    assert _outcome(result, "test_xfail_not_run") == "XFAIL"


def test_failure_message_names_original_reason_and_fix(run):
    result = run(strict=True)
    out = result.stdout.str()
    assert out.count(f"CI_FAIL_ON_SKIP=1: test skipped -- {REASON}") == 3, out
    assert "mark the test `behavioural`" in out
    assert result.ret != 0
