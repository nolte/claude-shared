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

import subprocess
import sys
from pathlib import Path

import pytest

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


def test_revision_after_stabilisation_without_rationale_is_critical():
    # #591 / F92: the statement changed after stabilisation, ## Source did not.
    revised = _GOOD.replace("A does X for the B audience.", "A does Y for the B audience.")
    assert _rules(v.check_revision_rationale(_GOOD, revised, "m")) == {"mission.post-stabilisation-rationale"}


def test_revision_after_stabilisation_with_rationale_passes():
    revised = _GOOD.replace("A does X for the B audience.", "A does Y for the B audience.").rstrip("\n") + "\n- 2026-09-13 revised: reason.\n"
    assert v.check_revision_rationale(_GOOD, revised, "m") == []


def test_revision_before_stabilisation_needs_no_rationale():
    early = _GOOD.replace("mvp_status: stabilised", "mvp_status: in_progress")
    assert v.check_revision_rationale(early, early.replace("does X", "does Y"), "m") == []


def test_historical_revision_01575fa_is_caught():
    import subprocess
    show = lambda ref: subprocess.run(["git", "show", f"{ref}:project/mission.md"], cwd=v.REPO, capture_output=True, text=True)
    before, after = show("01575fa^"), show("01575fa")
    if before.returncode or after.returncode:
        import pytest
        pytest.skip("history not available in this checkout")
    assert _rules(v.check_revision_rationale(before.stdout, after.stdout, "m")) == {"mission.post-stabilisation-rationale"}


def test_unreadable_explicit_base_ref_fails_closed(monkeypatch):
    # #591 review: a shallow CI checkout must not turn the rationale check into a no-op.
    monkeypatch.setenv("MISSION_BASE_REF", "0000000000000000000000000000000000000000")
    assert "mission.base-ref-unreadable" in _rules(v.check_mission(v.MISSION_PATH))


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


# --- #750: a flip to `stabilised` records its evidence in `## Source` --------

_ACHIEVED = _GOOD.replace("mvp_status: stabilised", "mvp_status: achieved")


def _flip(source_addition: str) -> str:
    return _GOOD.rstrip("\n") + "\n" + source_addition.rstrip("\n") + "\n"


_SUBSEQUENT_SPRINT_ENTRY = (
    "- 2026-05-29 — `mvp_status: achieved → stabilised`. Evidence: the full subsequent "
    "Sprint `0002` is `closed` with no MVP item re-opened.\n"
)
_EXEMPTION_ENTRY = (
    "- 2026-11-17 — `mvp_status: achieved → stabilised` via the retroactive-MVP exemption.\n"
    "\n"
    "The retroactive-MVP exemption applies: the MVP-closing sprint 1 ended 2026-07-02, commit "
    "`5ffdca5` first added `project/mission.md` at `mvp_status: achieved`, and the operator "
    "decided on 2026-11-17.\n"
)


def test_750_flip_with_subsequent_sprint_evidence_passes():
    assert v.check_stabilisation_evidence(_ACHIEVED, _flip(_SUBSEQUENT_SPRINT_ENTRY), "m") == []


def test_750_flip_with_german_subsequent_sprint_evidence_passes():
    entry = "- 2026-05-29 — `achieved → stabilised`: der volle Folgesprint `0002` ist `closed`.\n"
    assert v.check_stabilisation_evidence(_ACHIEVED, _flip(entry), "m") == []


@pytest.mark.parametrize("sentence", [
    "the one-full-subsequent-sprint condition is met by sprint `0002`.",
    "Sprint `0002` (MVP-closing + 1) is `closed`.",
    "der volle Folge-Sprint (Sprint `0002`) ist `closed`.",
    "the full subsequent Sprint `0002` (number `0001 + 1`) is `closed`.",
    "the full subsequent sprint\n  `0002` is `closed`.",  # hard-wrapped inside one sentence
])
def test_750_flip_with_subsequent_sprint_phrasings_passes(sentence):
    entry = f"- 2026-05-29 — `mvp_status: achieved → stabilised`. Evidence: {sentence}\n"
    assert v.check_stabilisation_evidence(_ACHIEVED, _flip(entry), "m") == []


@pytest.mark.parametrize("sentence", [
    # marker and number in different sentences: not one statement about the subsequent sprint
    "the subsequent sprint is `closed`. Sprint 1 closed the MVP.",
    # a sprint number without any subsequent-sprint marker
    "the MVP-closing sprint 1 is `closed`.",
    # marker and number in different list items
    "the subsequent sprint is `closed`\n- Sprint 1 closed the MVP",
])
def test_750_flip_with_unanchored_sprint_mention_is_critical(sentence):
    entry = f"- 2026-05-29 — `mvp_status: achieved → stabilised`. Evidence: {sentence}\n"
    assert _rules(v.check_stabilisation_evidence(_ACHIEVED, _flip(entry), "m")) == {
        "mission.stabilisation-evidence-missing"}


def test_750_exemption_without_retroactive_names_both_paths():
    entry = "- 2026-11-17 — `achieved → stabilised` under the exemption.\n"
    findings = v.check_stabilisation_evidence(_ACHIEVED, _flip(entry), "m")
    assert _rules(findings) == {"mission.stabilisation-evidence-missing"}
    assert "subsequent sprint" in findings[0].message and "retroactive-MVP exemption" in findings[0].message


def test_750_flip_with_full_exemption_rationale_passes():
    assert v.check_stabilisation_evidence(_ACHIEVED, _flip(_EXEMPTION_ENTRY), "m") == []


def test_750_flip_without_any_evidence_is_critical():
    entry = "- 2026-11-17 — `mvp_status: achieved → stabilised`.\n"
    assert _rules(v.check_stabilisation_evidence(_ACHIEVED, _flip(entry), "m")) == {
        "mission.stabilisation-evidence-missing"}


def test_750_flip_without_source_change_is_critical():
    assert _rules(v.check_stabilisation_evidence(_ACHIEVED, _GOOD, "m")) == {
        "mission.stabilisation-evidence-missing"}


def test_750_evidence_already_in_old_source_does_not_count():
    # Only lines the flip adds count; an older line can't evidence this flip.
    old = _ACHIEVED.rstrip("\n") + "\n" + _SUBSEQUENT_SPRINT_ENTRY
    assert _rules(v.check_stabilisation_evidence(old, old.replace("mvp_status: achieved", "mvp_status: stabilised", 1), "m")) == {
        "mission.stabilisation-evidence-missing"}


@pytest.mark.parametrize("cut, repl, missing", [
    ("sprint 1 ended", "sprint ended", "the MVP-closing sprint's number"),
    (" ended 2026-07-02", " closed on 2026-07-02", "`ended` date"),
    ("commit `5ffdca5` ", "", "the commit that first added"),
    (", and the operator decided on 2026-11-17", "", "the operator decision date"),
])
def test_750_exemption_rationale_missing_a_field_is_critical(cut, repl, missing):
    # Each case drops exactly one evidence field from an otherwise complete rationale.
    entry = _EXEMPTION_ENTRY.replace("- 2026-11-17 — ", "- ")
    assert cut in entry
    findings = v.check_stabilisation_evidence(_ACHIEVED, _flip(entry.replace(cut, repl)), "m")
    assert _rules(findings) == {"mission.stabilisation-exemption-evidence"}
    assert findings[0].message.count(";") == 0 and missing in findings[0].message


def test_750_no_flip_needs_no_evidence():
    assert v.check_stabilisation_evidence(_ACHIEVED, _ACHIEVED.replace("does X", "does Y"), "m") == []
    assert v.check_stabilisation_evidence(_GOOD, _GOOD, "m") == []


def test_750_historical_flip_a30d346_passes():
    # Positive control on real data: this repo's own achieved → stabilised flip (#225).
    def show(ref):
        return subprocess.run(["git", "show", f"{ref}:project/mission.md"], cwd=v.REPO, capture_output=True, text=True)

    before, after = show("a30d346^"), show("a30d346")
    if before.returncode or after.returncode:
        pytest.skip("history not available in this checkout")
    assert "stabilised" not in before.stdout.split("---")[1]
    assert v.check_stabilisation_evidence(before.stdout, after.stdout, "m") == []


@pytest.mark.parametrize("sentence,expected", [
    ("The subsequent sprint, e.g. Sprint 2, is `closed`.", True),
    ("Sprint `0002` (MVP-closing + 1) is `closed`.", True),
    ("Sprint 1 got a +1 from review.", False),
    ("Sprint 1 closed; one + 1 reviewers approved.", False),
])
def test_750_marker_and_sentence_edge_cases(sentence, expected):
    assert v._names_subsequent_sprint(sentence) is expected


# --- #814: a non-UTF-8 input is a Critical finding naming its path ----------

_UNDECODABLE = b"\xff\xfe not utf-8 \x80\n"


def _hermetic(monkeypatch, tmp_path):
    """Point every cross-reference input at an absent path under tmp_path."""
    monkeypatch.setattr(v, "GOALS_PATH", tmp_path / "absent-goals.md")
    monkeypatch.setattr(v, "AUDIENCES_PATH", tmp_path / "absent-audiences.md")
    monkeypatch.setattr(v, "FEATURES_DIR", tmp_path / "absent-features")


def _unreadable(findings):
    return [f for f in findings if f.rule == "mission.unreadable" and f.severity == "Critical"]


def test_814_unreadable_goals_and_feature_are_findings_not_tracebacks(monkeypatch, tmp_path):
    # An OSError (here: a directory where a file is expected) is reported like a
    # decode error, and the other checks still run.
    _hermetic(monkeypatch, tmp_path)
    goals = tmp_path / "goals.md"
    goals.mkdir()
    monkeypatch.setattr(v, "GOALS_PATH", goals)
    features = tmp_path / "features"
    (features / "0001-dir.md").mkdir(parents=True)
    # sorts after the unreadable one, so it shows the index kept going
    (features / "0002-ok.md").write_text(
        "---\nid: F-1\nverifies_sprint_value: acceptance-9\n---\n", encoding="utf-8")
    monkeypatch.setattr(v, "FEATURES_DIR", features)
    text = _GOOD.replace('"A does X for the B audience."', '""')
    findings = v.check_mission_text(text, "m")
    messages = [f.message for f in _unreadable(findings)]
    assert any(str(goals) in m for m in messages)
    assert any(str(features / "0001-dir.md") in m for m in messages)
    assert {"mission.mission-statement-empty", "mission.verifies-via-acceptance-mismatch"} <= _rules(findings)


def test_814_undecodable_mission_file_is_critical_and_exits_1(monkeypatch, tmp_path):
    _hermetic(monkeypatch, tmp_path)
    mission = tmp_path / "mission.md"
    mission.write_bytes(_UNDECODABLE)
    findings = v.check_mission(mission)
    hits = _unreadable(findings)
    assert len(hits) == 1 and str(mission) in hits[0].message and "utf-8" in hits[0].message
    monkeypatch.setattr(sys, "argv", ["validate_mission.py", str(mission)])
    assert v.main() == 1


def test_814_undecodable_goals_keeps_every_other_finding(monkeypatch, tmp_path):
    _hermetic(monkeypatch, tmp_path)
    goals = tmp_path / "goals.md"
    goals.write_bytes(_UNDECODABLE)
    monkeypatch.setattr(v, "GOALS_PATH", goals)
    text = (_GOOD.replace('"A does X for the B audience."', '""')
            .replace("verifies_via: F-1:acceptance-1", "verifies_via: nope"))
    findings = v.check_mission_text(text, "m")
    hits = _unreadable(findings)
    assert len(hits) == 1 and str(goals) in hits[0].message
    # findings collected before the goals read, and checks after it, all survive
    assert {"mission.mission-statement-empty", "mission.verifies-via-pattern"} <= _rules(findings)
    # an undecodable goals.md resolves nothing, like an absent one (no false unresolved)
    assert "mission.relevant-outcome-unresolved" not in _rules(findings)


def test_814_undecodable_audiences_keeps_every_other_finding(monkeypatch, tmp_path):
    _hermetic(monkeypatch, tmp_path)
    audiences = tmp_path / "AUDIENCES.md"
    audiences.write_bytes(_UNDECODABLE)
    monkeypatch.setattr(v, "AUDIENCES_PATH", audiences)
    text = (_GOOD.replace('"A does X for the B audience."', '""')
            .replace("verifies_via: F-1:acceptance-1", "verifies_via: nope"))
    findings = v.check_mission_text(text, "m")
    hits = _unreadable(findings)
    assert len(hits) == 1 and str(audiences) in hits[0].message
    assert {"mission.mission-statement-empty", "mission.verifies-via-pattern"} <= _rules(findings)
    assert "mission.audience-unresolved" not in _rules(findings)


def test_814_undecodable_feature_is_critical_and_others_still_index(monkeypatch, tmp_path):
    _hermetic(monkeypatch, tmp_path)
    features = tmp_path / "features"
    features.mkdir()
    (features / "0001-good.md").write_text(
        "---\nid: F-1\nverifies_sprint_value: acceptance-2\n---\n", encoding="utf-8")
    bad = features / "0002-bad.md"
    bad.write_bytes(_UNDECODABLE)
    monkeypatch.setattr(v, "FEATURES_DIR", features)
    findings = v.check_verifies_via("F-1:acceptance-1", "m")
    hits = _unreadable(findings)
    assert len(hits) == 1 and str(bad) in hits[0].message
    # the valid feature F-1 was still indexed and resolved against
    assert "mission.verifies-via-acceptance-mismatch" in _rules(findings)


def test_814_only_undecodable_features_is_not_silently_empty(monkeypatch, tmp_path):
    _hermetic(monkeypatch, tmp_path)
    features = tmp_path / "features"
    features.mkdir()
    bad = features / "0001-bad.md"
    bad.write_bytes(_UNDECODABLE)
    monkeypatch.setattr(v, "FEATURES_DIR", features)
    hits = _unreadable(v.check_verifies_via("F-1:acceptance-1", "m"))
    assert len(hits) == 1 and str(bad) in hits[0].message


def test_814_undecodable_committed_version_is_critical(monkeypatch, tmp_path):
    _hermetic(monkeypatch, tmp_path)
    monkeypatch.delenv("MISSION_BASE_REF", raising=False)
    real_run = subprocess.run

    def fake_run(cmd, *args, **kwargs):
        if cmd[:2] == ["git", "show"]:
            # Only an explicit strict UTF-8 decode is locale-independent; anything
            # else would decode by locale, so the fake refuses it.
            assert kwargs.get("text") and kwargs.get("encoding") == "utf-8" and "errors" not in kwargs
            _UNDECODABLE.decode("utf-8")  # raises, as the real text-mode decode does
        return real_run(cmd, *args, **kwargs)

    monkeypatch.setattr(v.subprocess, "run", fake_run)
    findings = v.check_mission(v.MISSION_PATH)
    hits = _unreadable(findings)
    assert len(hits) == 1 and "HEAD:project/mission.md" in hits[0].message


def test_814_committed_version_missing_stays_no_finding(monkeypatch, tmp_path):
    # returncode != 0 without MISSION_BASE_REF keeps meaning "no committed version".
    _hermetic(monkeypatch, tmp_path)
    monkeypatch.delenv("MISSION_BASE_REF", raising=False)

    def fake_run(cmd, *args, **kwargs):
        empty = "" if kwargs.get("text") else b""
        return subprocess.CompletedProcess(cmd, 128, stdout=empty, stderr=empty)

    monkeypatch.setattr(v.subprocess, "run", fake_run)
    assert v._committed_version(v.MISSION_PATH, "HEAD") is None
