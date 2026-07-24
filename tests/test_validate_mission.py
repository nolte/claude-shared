"""Conformance tests for `scripts/validate_mission.py`, the `project/mission.md`
frontmatter linter (issue #461, item 1).

The linter turns the `spec/project/mission/` acceptance criteria that repeatedly
say "lints flag" / "fails validation" into a real gate. These tests lock:
  - a well-formed mission passes (no false positives on the negative fixtures'
    green sibling),
  - each planted defect fires the expected rule id (the negative proof, mirrored
    by the script's own `--self-test`),
  - the file-absent case is a pass (adoption is optional per the spec).
"""
from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import validate_mission as v  # noqa: E402


def _rules(findings):
    return {f.rule for f in findings}


_GOOD = """---
mission_statement: "A does X for the B audience."
relevant_outcomes:
  - O-1
audiences:
  - downstream-user
verifies_via: F-1:acceptance-1
time_bound:
  kind: mvp_completion
mvp_status: stabilised
created: 2026-05-09
revised_at: 2026-05-29
---

# Mission

## Statement

x

## Audiences

x

## Verification

x

## Source

x
"""


def test_well_formed_mission_passes(monkeypatch, tmp_path):
    # Neutralise cross-reference resolution so the unit stays hermetic: with no
    # goals.md / AUDIENCES.md / features corpus, resolution is skipped (returns
    # None / empty) and only the shape checks run.
    monkeypatch.setattr(v, "GOALS_PATH", tmp_path / "absent-goals.md")
    monkeypatch.setattr(v, "AUDIENCES_PATH", tmp_path / "absent-audiences.md")
    monkeypatch.setattr(v, "FEATURES_DIR", tmp_path / "absent-features")
    assert v.check_mission_text(_GOOD, "project/mission.md") == []


def test_mvp_completion_time_bound_accepts_only_kind():
    findings = v.check_time_bound({"kind": "mvp_completion"}, "m", ["O-1"])
    assert findings == []


def test_outcome_time_bound_requires_outcome_ref():
    ok = v.check_time_bound({"kind": "outcome", "ref": "O-2"}, "m", ["O-1"])
    assert ok == []
    bad = v.check_time_bound({"kind": "outcome", "ref": "someday"}, "m", ["O-1"])
    assert "mission.time-bound-ref" in _rules(bad)


def test_calendar_time_bound_is_rejected():
    findings = v.check_time_bound({"kind": "2026-12-31"}, "m", ["O-1"])
    assert "mission.time-bound-kind" in _rules(findings)


def test_verifies_via_pattern_enforced():
    assert "mission.verifies-via-pattern" in _rules(v.check_verifies_via("nope", "m"))
    assert "mission.verifies-via-pattern" in _rules(v.check_verifies_via("F-1:wrong", "m"))


def test_missing_frontmatter_is_critical():
    findings = v.check_mission_text("no fence here\n", "m")
    assert "mission.frontmatter-missing" in _rules(findings)


def test_self_test_fixture_fires_every_expected_rule():
    # The script's on-disk negative proof: every planted defect must fire.
    findings = v.check_mission_text(v._BROKEN_FIXTURE, "<fixture>")
    assert v._SELF_TEST_EXPECTED <= _rules(findings)


def test_run_self_test_returns_zero():
    assert v.run_self_test() == 0
