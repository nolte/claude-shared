"""Tests for plugins/nolte-engineering/skills/capability-reach-audit/scripts/reach_audit.py.

Requirement ids refer to project/requirements/capability-reach-executor.md.

The doubles are honest ones: change detection runs against real git repositories
created in ``tmp_path`` (git is never mocked), and the environment step runs a
``task`` executable placed first on ``PATH`` that reads the target's
``Taskfile.yml`` and fails an unknown target the way go-task does. The T1 case
stands up a real loopback HTTP server through that shim.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

from tests.conftest import REPO_ROOT, SCRIPTS, Target, ra, row_of, validate

SCRIPT_PATH = SCRIPTS / "reach_audit.py"
SCHEMA_PATH = REPO_ROOT / "schemas" / "reach-probe-v1.3.schema.yaml"
V12_SCHEMA_PATH = REPO_ROOT / "schemas" / "reach-probe-v1.2.schema.yaml"
PRIOR_SCHEMA_PATH = REPO_ROOT / "schemas" / "reach-probe-v1.1.schema.yaml"
EXAMPLES = SCRIPTS.parent / "examples"
FIXED_NOW = datetime(2026, 9, 23, 10, 0, 0, tzinfo=timezone.utc)
PY = sys.executable
DECL = "docs/requirements.md"


# --------------------------------------------------------------------------- #
# Fixtures and helpers
# --------------------------------------------------------------------------- #
# _isolated_git, Target, row_of and validate are shared fixtures/helpers defined
# in tests/conftest.py (SCR-007); imported above rather than redefined here.
def make_probe(pid: str = "p1", *, derived_from: str, tier: str = "T0", path: str | None = DECL,
               expected: dict | None = None, argv: list[str] | None = None, approved: bool = True,
               **extra) -> dict:
    declaration: dict = {"source": "requirement", "location": "§Export"}
    if path is not None:
        declaration["path"] = path
    probe: dict = {
        "id": pid,
        "declaration": declaration,
        "tier": tier,
        "expected": expected or {"kind": "count", "value": 3, "unit": "collections"},
    }
    if approved:
        probe["approval"] = {"approved_at": "2026-09-20T09:00:00Z", "approved_by": "nolte"}
    probe["derived_from"] = derived_from
    probe.update(extra)
    probe["observe"] = {"argv": argv or [PY, "-c", "print(3)"], "timeout_seconds": 30}
    return probe


# The reason a move onto a commit anchor reads weakened in a SHA-1 repository (#688).
COMMIT_MOVE_REFUSED = ("a move onto a commit anchor is never a re-derivation for a declaration inside the "
                       "repository; re-derive it, which records a content or section anchor")


def marker_argv(marker: Path, output: str = "3") -> list[str]:
    """An observation step that leaves a trace, so a test can prove it never ran."""
    return [PY, "-c", f"open({str(marker)!r}, 'w').write('ran'); print({output!r})"]


@pytest.fixture
def target(tmp_path) -> Target:
    t = Target(tmp_path / "target")
    t.write(DECL, "# Requirements\n\n## Export\n\nExports 3 collections.\n")
    t.commit("declare")
    return t


@pytest.fixture
def sha256_target(tmp_path) -> Target:
    """A SHA-256 repository: no content anchor exists there, so a commit anchor keeps the pre-v1.1 rules."""
    path = tmp_path / "target"
    path.mkdir()
    res = subprocess.run(["git", "init", "-q", "--object-format=sha256", str(path)],
                         capture_output=True, text=True, check=False)
    if res.returncode != 0:
        pytest.skip(f"local git cannot create a SHA-256 repository: {res.stderr.strip()}")
    t = Target(path)
    assert t.git("rev-parse", "--show-object-format") == "sha256"
    t.write(DECL, "# Requirements\n\n## Export\n\nExports 3 collections.\n")
    t.commit("declare")
    return t


def derived_probe(target: Target, **kw) -> tuple[str, str]:
    """Derive at HEAD, then commit the probe: the natural lifecycle."""
    sha = target.git("rev-parse", "HEAD")
    rel = target.write_probe(make_probe(derived_from=sha, **kw))
    target.commit("approve probe")
    return sha, rel


def run_audit(target: Target, include_t2: bool = False, env_timeout: float = 30) -> tuple[int, str]:
    code, _ = ra.run(str(target.path), include_t2=include_t2, env_timeout=env_timeout, clock=lambda: FIXED_NOW)
    return code, target.report()


# --------------------------------------------------------------------------- #
# Schema (R1, R7)
# --------------------------------------------------------------------------- #
_ANNOTATIONS = {"title", "description", "examples"}


def _structural(node):
    if isinstance(node, dict):
        return {k: _structural(v) for k, v in node.items() if k not in _ANNOTATIONS or not isinstance(v, (str, list))}
    if isinstance(node, list):
        return [_structural(v) for v in node]
    return node


def test_runner_schema_copy_matches_the_shipped_schema():
    """R1: the runner validates with exactly the structure schemas/ declares."""
    shipped = yaml.safe_load(SCHEMA_PATH.read_text())
    assert _structural(shipped) == _structural(ra.PROBE_SCHEMA)


def test_shipped_schema_is_valid_and_its_examples_validate():
    shipped = yaml.safe_load(SCHEMA_PATH.read_text())
    Draft202012Validator.check_schema(shipped)
    for example in shipped["examples"]:
        assert validate(example) == []


def test_example_probes_validate():
    files = sorted(f for f in EXAMPLES.glob("*.yml") if f.name != ra.MANIFEST_NAME)
    assert files, "the .schemas-config.yaml mapping needs at least one example to exercise"
    for f in files:
        assert validate(yaml.safe_load(f.read_text())) == [], f


def test_schemas_config_binds_the_example_glob():
    config = yaml.safe_load((REPO_ROOT / ".schemas-config.yaml").read_text())
    bound = {glob: schema for glob, schema in config["mappings"].items() if list(REPO_ROOT.glob(glob))}
    assert "schemas/reach-probe-v1.3.schema.yaml" in bound.values()


def _valid() -> dict:
    return make_probe(derived_from="a" * 40)


def test_a_valid_probe_passes():
    assert validate(_valid()) == []


@pytest.mark.parametrize("verdict", ["passed", "status", "result", "reached", "verdict"])
def test_R1_probe_cannot_state_a_verdict_at_top_level(verdict):
    """R1: the comparison happens in the runner; a probe has no verdict field."""
    probe = _valid() | {verdict: True}
    assert any("Additional properties" in m for m in validate(probe))


@pytest.mark.parametrize("where", ["expected", "observe", "declaration", "approval"])
def test_R1_probe_cannot_state_a_verdict_in_a_nested_object(where):
    probe = _valid()
    probe[where] = dict(probe[where], status="passed")
    assert validate(probe)


def test_R1_expected_as_free_text_is_rejected():
    probe = _valid() | {"expected": "all 15 collections are exported"}
    assert validate(probe)


def test_R1_expected_count_needs_an_integer():
    probe = _valid() | {"expected": {"kind": "count", "value": "fifteen", "unit": "collections"}}
    assert validate(probe)


def test_R1_expected_set_needs_members():
    probe = _valid() | {"expected": {"kind": "set", "values": []}}
    assert validate(probe)


def test_R7_probe_missing_tier_is_rejected():
    probe = _valid()
    del probe["tier"]
    assert any("'tier' is a required property" in m for m in validate(probe))


def test_R7_unknown_tier_is_rejected():
    assert validate(_valid() | {"tier": "T3"})


def test_R6_declaration_cannot_carry_both_path_and_inherited_spec():
    probe = _valid()
    probe["declaration"]["inherited_spec"] = "project/rest-api-design"
    assert validate(probe)


def test_environment_name_cannot_be_read_as_an_option():
    assert validate(_valid() | {"tier": "T1", "environment": ["--dry"]})


# --------------------------------------------------------------------------- #
# Load-time validation inside the runner (R1, R7)
# --------------------------------------------------------------------------- #
def test_R1_runner_validates_at_load_and_never_executes_a_self_asserting_probe(target, tmp_path):
    marker = tmp_path / "ran"
    sha = target.git("rev-parse", "HEAD")
    probe = make_probe(derived_from=sha, argv=marker_argv(marker)) | {"status": "passed"}
    target.write_probe(probe)
    target.commit("probe")
    code, report = run_audit(target)
    assert code == ra.EXIT_FINDINGS
    assert not marker.exists()
    assert "**invalid probe** `p1`" in report
    assert "no verdict or other undeclared field" in report
    assert row_of(report, "p1")[1] == ra.NOT_PROBED


def test_R7_T0_probe_with_an_environment_is_invalid(target):
    sha = target.git("rev-parse", "HEAD")
    target.write_probe(make_probe(derived_from=sha, environment=["up"]))
    target.commit("probe")
    code, report = run_audit(target)
    assert code == ra.EXIT_FINDINGS
    assert "a T0 probe runs against what already exists" in report


def test_duplicate_probe_ids_are_invalid(target):
    sha = target.git("rev-parse", "HEAD")
    target.write_probe(make_probe(derived_from=sha), name="a")
    target.write_probe(make_probe(derived_from=sha), name="b")
    target.commit("probes")
    code, report = run_audit(target)
    assert code == ra.EXIT_FINDINGS
    assert "duplicate probe id, already used by project/reach-probes/a.yml" in report


def test_unquoted_timestamp_gets_an_actionable_hint(target):
    sha = target.git("rev-parse", "HEAD")
    text = yaml.safe_dump(make_probe(derived_from=sha), sort_keys=False).replace(
        "'2026-09-20T09:00:00Z'", "2026-09-20T09:00:00Z"
    )
    target.write("project/reach-probes/p1.yml", text)
    target.commit("probe")
    _, report = run_audit(target)
    assert "quote the value" in report


def test_missing_dependency_fails_with_an_install_hint(monkeypatch, capsys, target):
    real_import = __builtins__["__import__"] if isinstance(__builtins__, dict) else __builtins__.__import__

    def fake_import(name, *args, **kwargs):
        if name == "jsonschema":
            raise ImportError("No module named 'jsonschema'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", fake_import)
    assert ra.main(["--repo", str(target.path)]) == ra.EXIT_MISSING_DEPENDENCY
    assert "pip install" in capsys.readouterr().err


# --------------------------------------------------------------------------- #
# R13: local working copy only
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("remote", ["https://github.com/nolte/kamerplanter", "git@github.com:nolte/kamerplanter.git"])
def test_R13_remote_address_is_refused(remote, capsys):
    assert ra.main(["--repo", remote]) == ra.EXIT_USAGE
    err = capsys.readouterr().err
    # The generic "not a local directory" fallback also says "local working copy",
    # so asserting only that would pass with the remote-address branch deleted
    # (measured by mutation). The branch's own wording is what proves the rule.
    assert "is a remote address" in err
    assert "clone the repository" in err


def test_R13_missing_directory_is_refused(tmp_path, capsys):
    assert ra.main(["--repo", str(tmp_path / "nope")]) == ra.EXIT_USAGE
    assert "not a local directory" in capsys.readouterr().err


def test_R13_directory_without_git_is_refused(tmp_path, capsys):
    plain = tmp_path / "plain"
    plain.mkdir()
    assert ra.main(["--repo", str(plain)]) == ra.EXIT_USAGE
    assert "has no .git" in capsys.readouterr().err


def test_R13_subdirectory_of_a_working_copy_is_refused(target, capsys):
    assert ra.main(["--repo", str(target.path / "docs")]) == ra.EXIT_USAGE
    assert "has no .git" in capsys.readouterr().err


def test_R13_bogus_git_marker_is_refused(tmp_path, capsys):
    fake = tmp_path / "fake"
    (fake / ".git").mkdir(parents=True)
    assert ra.main(["--repo", str(fake)]) == ra.EXIT_USAGE
    assert "--show-toplevel" in capsys.readouterr().err


def test_R13_working_copy_without_commits_is_refused(tmp_path, capsys):
    Target(tmp_path / "empty")
    assert ra.main(["--repo", str(tmp_path / "empty")]) == ra.EXIT_USAGE
    assert "no commit yet" in capsys.readouterr().err


# --------------------------------------------------------------------------- #
# R11, R12, R15: paths and the empty probe set
# --------------------------------------------------------------------------- #
def test_R11_R12_probes_read_from_project_and_report_written_under_audits(target):
    derived_probe(target)
    target.write("elsewhere/p2.yml", yaml.safe_dump(make_probe("p2", derived_from="x")))
    target.commit("stray probe outside the probe directory")
    before = set(target.git("ls-files", "--others", "--exclude-standard").splitlines())
    code, report = run_audit(target)
    assert code == ra.EXIT_OK
    assert "| p1 |" in report and "| p2 |" not in report
    after = set(target.git("ls-files", "--others", "--exclude-standard").splitlines())
    assert after - before == {".audits/capability-reach/2026-09-23.md"}
    assert target.git("status", "--porcelain", "--untracked-files=no") == ""


def test_R11_yaml_suffix_is_part_of_the_probe_set(target):
    sha = target.git("rev-parse", "HEAD")
    target.write("project/reach-probes/p1.yaml", yaml.safe_dump(make_probe(derived_from=sha)))
    target.commit("probe")
    _, report = run_audit(target)
    assert row_of(report, "p1")[1] == ra.REACHED


def test_R12_report_of_the_day_is_overwritten(target):
    derived_probe(target)
    run_audit(target)
    report = target.path / ".audits" / "capability-reach" / "2026-09-23.md"
    report.write_text("hand edit\n")
    run_audit(target)
    assert "hand edit" not in report.read_text()
    assert "| p1 |" in report.read_text()


def test_R12_report_is_not_written_through_a_symlink_outside_the_repo(target, tmp_path):
    derived_probe(target)
    outside = tmp_path / "outside"
    outside.mkdir()
    (target.path / ".audits").symlink_to(outside, target_is_directory=True)
    assert ra.main(["--repo", str(target.path)]) == ra.EXIT_ERROR
    assert not any(outside.rglob("*.md"))


def test_R15_absent_probe_directory_is_not_a_clean_result(target):
    code, report = run_audit(target)
    assert code == ra.EXIT_NO_PROBES
    assert "`project/reach-probes/` does not exist" in report
    assert "This is not a clean result" in report


def test_R15_empty_probe_directory_is_not_a_clean_result(target):
    (target.path / "project" / "reach-probes").mkdir(parents=True)
    code, report = run_audit(target)
    assert code == ra.EXIT_NO_PROBES
    assert "holds no probe file" in report


# --------------------------------------------------------------------------- #
# R2, R5: change detection against the declaration
# --------------------------------------------------------------------------- #
def test_R5_stored_probe_executes_without_being_rewritten(target, tmp_path):
    marker = tmp_path / "ran"
    _, rel = derived_probe(target, argv=marker_argv(marker))
    before = (target.path / rel).read_text()
    code, report = run_audit(target)
    assert code == ra.EXIT_OK and marker.exists()
    assert (target.path / rel).read_text() == before
    row = row_of(report, "p1")
    assert row[1] == ra.REACHED and row[7] == ra.STATE_CLEAN


def test_R2_declaration_changed_after_derivation_is_stale_and_not_executed(target, tmp_path):
    marker = tmp_path / "ran"
    derived_probe(target, argv=marker_argv(marker))
    target.write(DECL, "# Requirements\n\n## Export\n\nExports 4 collections.\n")
    changed = target.commit("move the declaration")
    _, report = run_audit(target)
    row = row_of(report, "p1")
    assert row[1] == ra.NOT_PROBED and row[7] == ra.STATE_STALE
    assert f"declaration changed since derivation: {DECL} last changed in {changed[:12]}" in row[9]
    assert not marker.exists()


def test_R2_unrelated_commits_after_derivation_do_not_make_it_stale(target):
    derived_probe(target)
    target.write("README.md", "unrelated\n")
    target.commit("unrelated")
    _, report = run_audit(target)
    assert row_of(report, "p1")[7] == ra.STATE_CLEAN


def test_R2_uncommitted_declaration_edit_is_stale(target):
    derived_probe(target)
    target.write(DECL, "edited, not committed\n")
    _, report = run_audit(target)
    row = row_of(report, "p1")
    assert row[7] == ra.STATE_STALE and "uncommitted changes" in row[9]


def test_R2_renamed_declaration_is_stale(target):
    derived_probe(target)
    target.git("mv", DECL, "docs/requirements-v2.md")
    target.commit("rename")
    _, report = run_audit(target)
    assert row_of(report, "p1")[7] == ra.STATE_STALE


def test_R2_declaration_on_a_merged_side_branch_is_stale(target):
    base = target.git("rev-parse", "HEAD")
    target.git("checkout", "-q", "-b", "side")
    target.write(DECL, "side edit\n")
    target.commit("side edit")
    target.git("checkout", "-q", "main")
    target.write_probe(make_probe(derived_from=base))
    target.commit("probe on main")
    target.git("merge", "-q", "--no-edit", "side")
    _, report = run_audit(target)
    assert row_of(report, "p1")[7] == ra.STATE_STALE


def test_R2_unknown_derived_from_is_unresolved(target):
    target.write_probe(make_probe(derived_from="0" * 40))
    target.commit("probe")
    _, report = run_audit(target)
    row = row_of(report, "p1")
    assert row[1] == ra.NOT_PROBED and row[7] == ra.STATE_UNRESOLVED
    assert "is not a commit of the target repository" in row[9]


def test_R2_derived_from_outside_the_history_of_head_is_unresolved(target):
    target.git("checkout", "-q", "-b", "other")
    other = target.commit("elsewhere")
    target.git("checkout", "-q", "main")
    target.write_probe(make_probe(derived_from=other))
    target.commit("probe")
    _, report = run_audit(target)
    assert "is not in the history of HEAD" in row_of(report, "p1")[9]


def test_R2_declaration_path_without_history_is_unresolved(target):
    derived_probe(target, path="docs/never-committed.md")
    _, report = run_audit(target)
    row = row_of(report, "p1")
    assert row[7] == ra.STATE_UNRESOLVED and "has no history" in row[9]


# --------------------------------------------------------------------------- #
# R3: weakened probes
# --------------------------------------------------------------------------- #
def _weaken(target: Target, rel: str) -> None:
    data = yaml.safe_load((target.path / rel).read_text())
    data["expected"]["value"] = 1
    target.write(rel, yaml.safe_dump(data, sort_keys=False))


def test_R3_probe_changed_after_derivation_is_a_weakened_finding(target, tmp_path):
    marker = tmp_path / "ran"
    _, rel = derived_probe(target, argv=marker_argv(marker))
    _weaken(target, rel)
    weakening = target.commit("lower the bar")
    code, report = run_audit(target)
    assert code == ra.EXIT_FINDINGS
    assert not marker.exists()
    row = row_of(report, "p1")
    assert row[1] == ra.NOT_PROBED and row[7] == ra.STATE_WEAKENED
    assert f"probe changed in {weakening[:12]}" in report
    assert report.index("## Findings") < report.index("## Probes")
    assert "**weakened** `p1`" in report


def test_R3_probe_and_declaration_changed_in_the_same_commit_is_weakened(target):
    _, rel = derived_probe(target)
    _weaken(target, rel)
    target.write(DECL, "moved\n")
    target.commit("both at once")
    code, report = run_audit(target)
    assert code == ra.EXIT_FINDINGS
    assert row_of(report, "p1")[7] == ra.STATE_WEAKENED


def test_R3_probe_and_declaration_changed_in_separate_commits_is_weakened(target):
    _, rel = derived_probe(target)
    target.write(DECL, "moved\n")
    target.commit("declaration first")
    _weaken(target, rel)
    target.commit("probe second")
    _, report = run_audit(target)
    assert row_of(report, "p1")[7] == ra.STATE_WEAKENED


def test_R3_uncommitted_probe_edit_is_weakened(target):
    _, rel = derived_probe(target)
    _weaken(target, rel)
    code, report = run_audit(target)
    assert code == ra.EXIT_FINDINGS
    assert "probe file has uncommitted changes" in row_of(report, "p1")[9]


def test_R3_renaming_the_probe_does_not_launder_a_weakening(target):
    _, rel = derived_probe(target)
    new_rel = "project/reach-probes/renamed.yml"
    target.git("mv", rel, new_rel)
    _weaken(target, new_rel)
    target.commit("rename and weaken")
    _, report = run_audit(target)
    assert row_of(report, "p1")[7] == ra.STATE_WEAKENED


def test_R3_R5_re_derivation_after_a_declaration_change_is_clean(target):
    _, rel = derived_probe(target)
    target.write(DECL, "# Requirements\n\nExports 3 collections, reworded.\n")
    target.commit("move declaration")
    data = yaml.safe_load((target.path / rel).read_text())
    data["derived_from"] = _blob(target)
    target.write(rel, yaml.safe_dump(data, sort_keys=False))
    target.commit("re-derive")
    code, report = run_audit(target)
    assert code == ra.EXIT_OK
    assert row_of(report, "p1")[1] == ra.REACHED


def test_uncommitted_probe_is_not_probed(target):
    sha = target.git("rev-parse", "HEAD")
    target.write_probe(make_probe(derived_from=sha))
    _, report = run_audit(target)
    row = row_of(report, "p1")
    assert row[1] == ra.NOT_PROBED and row[7] == ra.STATE_UNCOMMITTED


# --------------------------------------------------------------------------- #
# R6: inherited and external anchors
# --------------------------------------------------------------------------- #
def _inherited_probe(target: Target, derived_from: str, hub: str | None = None) -> None:
    probe = make_probe(derived_from=derived_from, path=None)
    probe["declaration"]["inherited_spec"] = "project/rest-api-design"
    if hub:
        probe["declaration"]["hub"] = hub
    target.write_probe(probe)


def _spec_config(target: Target, *refs: tuple[str, str]) -> None:
    config = {"canonical_language": "en", "languages": ["en"], "spec_root": "spec",
              "inherits": [{"source": s, "ref": r} for s, r in refs]}
    target.write("spec/.spec-config.yml", yaml.safe_dump(config))


def test_R6_inherited_spec_with_unchanged_ref_executes(target):
    _spec_config(target, ("nolte-shared", "v0.1.8"))
    _inherited_probe(target, "v0.1.8")
    target.commit("probe")
    _, report = run_audit(target)
    row = row_of(report, "p1")
    assert row[1] == ra.REACHED and row[7] == ra.STATE_CLEAN


def test_R6_inherited_spec_with_moved_ref_is_stale(target):
    _spec_config(target, ("nolte-shared", "v0.1.9"))
    _inherited_probe(target, "v0.1.8")
    target.commit("probe")
    _, report = run_audit(target)
    row = row_of(report, "p1")
    assert row[7] == ra.STATE_STALE and "pinned ref moved from v0.1.8 to v0.1.9" in row[9]


def test_R6_inherited_spec_without_config_is_unresolved(target):
    _inherited_probe(target, "v0.1.8")
    target.commit("probe")
    _, report = run_audit(target)
    assert row_of(report, "p1")[7] == ra.STATE_UNRESOLVED


def test_R6_several_hubs_need_the_probe_to_name_one(target):
    _spec_config(target, ("nolte-shared", "v0.1.8"), ("other-hub", "v2.0.0"))
    _inherited_probe(target, "v0.1.8")
    target.commit("probe")
    _, report = run_audit(target)
    assert "set declaration.hub" in row_of(report, "p1")[9]


def test_R6_hub_selects_the_pinning_entry(target):
    _spec_config(target, ("nolte-shared", "v0.1.8"), ("other-hub", "v2.0.0"))
    _inherited_probe(target, "v2.0.0", hub="other-hub")
    target.commit("probe")
    _, report = run_audit(target)
    assert row_of(report, "p1")[7] == ra.STATE_CLEAN


@pytest.mark.parametrize("path", [None, "../other-repo/docs/req.md", "https://example.invalid/spec"])
def test_R6_external_anchor_is_unmonitored_and_still_executes(target, tmp_path, path):
    marker = tmp_path / "ran"
    derived_probe(target, path=path, argv=marker_argv(marker))
    _, report = run_audit(target)
    row = row_of(report, "p1")
    assert row[7].startswith(ra.STATE_UNMONITORED) and row[1] == ra.REACHED
    assert marker.exists()


def test_R6_external_anchor_is_still_checked_for_weakening(target):
    _, rel = derived_probe(target, path=None)
    _weaken(target, rel)
    target.commit("weaken")
    _, report = run_audit(target)
    assert row_of(report, "p1")[7] == ra.STATE_WEAKENED


# --------------------------------------------------------------------------- #
# Approval and R8 (T2 opt-in)
# --------------------------------------------------------------------------- #
def test_unapproved_probe_is_never_executed(target, tmp_path):
    marker = tmp_path / "ran"
    derived_probe(target, approved=False, argv=marker_argv(marker))
    _, report = run_audit(target)
    row = row_of(report, "p1")
    assert row[1] == ra.NOT_PROBED and row[9] == ra.REASON_NOT_APPROVED
    assert not marker.exists()


def test_R8_T2_probe_is_not_probed_without_the_flag(target, tmp_path):
    marker = tmp_path / "ran"
    derived_probe(target, tier="T2", argv=marker_argv(marker))
    _, report = run_audit(target)
    row = row_of(report, "p1")
    assert row[1] == ra.NOT_PROBED and row[9] == ra.REASON_T2
    assert not marker.exists()
    assert "Tier T2: not requested" in report


def test_R8_T2_probe_runs_with_the_flag(target, tmp_path):
    marker = tmp_path / "ran"
    derived_probe(target, tier="T2", argv=marker_argv(marker))
    _, report = run_audit(target, include_t2=True)
    assert row_of(report, "p1")[1] == ra.REACHED and marker.exists()


def test_R8_T1_probe_runs_without_the_flag(target):
    derived_probe(target, tier="T1")
    _, report = run_audit(target)
    assert row_of(report, "p1")[1] == ra.REACHED


# --------------------------------------------------------------------------- #
# The `task` shim (R9, R10)
# --------------------------------------------------------------------------- #
# TASK_SHIM and the task_shim fixture are defined in tests/conftest.py (SCR-007)
# and imported above; only the observation argv for the loopback server is local.
OBSERVE_SERVER = [
    PY, "-c",
    "import os, urllib.request\n"
    "port = open(os.path.join(os.environ['REACH_STATE'], 'port')).read().strip()\n"
    "print(urllib.request.urlopen(f'http://127.0.0.1:{port}/items', timeout=5).read().decode())",
]


def _taskfile(target: Target, state: Path, extra: dict | None = None) -> None:
    server = state / "server.py"
    tasks = {
        "reach:up": {"cmds": [f"{PY} {server} up"]},
        "reach:down": {"cmds": [f"{PY} {server} down"]},
        "reach:broken": {"cmds": ["echo 'image pull failed: registry unreachable' >&2", "exit 3"]},
        "reach:slow": {"cmds": ["sleep 5"]},
    }
    tasks.update(extra or {})
    target.write("Taskfile.yml", yaml.safe_dump({"version": "3", "tasks": tasks}))


def _set_probe(**kw) -> dict:
    return {"expected": {"kind": "set", "values": ["alpha", "beta"], "unit": "endpoints"}, "tier": "T1", **kw}


def test_R9_environment_targets_run_before_the_observation(target, task_shim):
    _taskfile(target, task_shim)
    derived_probe(target, argv=OBSERVE_SERVER, **_set_probe(environment=["reach:up"], teardown=["reach:down"]))
    _, report = run_audit(target)
    row = row_of(report, "p1")
    assert row[1] == ra.REACHED and row[2] == "2/2 endpoints"
    assert not (task_shim / "port").exists(), "teardown must have stopped the server"


def test_R9_unknown_target_is_not_probed_naming_it(target, task_shim):
    _taskfile(target, task_shim)
    derived_probe(target, argv=OBSERVE_SERVER, **_set_probe(environment=["reach:missing"]))
    _, report = run_audit(target)
    row = row_of(report, "p1")
    assert row[1] == ra.NOT_PROBED
    assert 'environment target `reach:missing` failed (exit 200): task: Task "reach:missing" does not exist' in row[9]


def test_R9_task_not_on_path_is_not_probed(target, tmp_path, monkeypatch):
    bin_dir = tmp_path / "bin-no-task"
    bin_dir.mkdir()
    (bin_dir / "git").symlink_to(shutil.which("git"))
    monkeypatch.setenv("PATH", str(bin_dir))
    derived_probe(target, argv=OBSERVE_SERVER, **_set_probe(environment=["reach:up"]))
    _, report = run_audit(target)
    row = row_of(report, "p1")
    assert row[1] == ra.NOT_PROBED and "`task` not found on PATH" in row[9]


def test_R10_failing_environment_is_not_probed_with_its_output_never_not_reached(target, task_shim, tmp_path):
    marker = tmp_path / "ran"
    _taskfile(target, task_shim)
    derived_probe(target, argv=marker_argv(marker), **_set_probe(environment=["reach:broken"]))
    _, report = run_audit(target)
    row = row_of(report, "p1")
    assert row[1] == ra.NOT_PROBED
    assert "image pull failed: registry unreachable" in row[9]
    assert not marker.exists()


def test_R10_environment_timeout_is_not_probed(target, task_shim):
    _taskfile(target, task_shim)
    derived_probe(target, argv=OBSERVE_SERVER, **_set_probe(environment=["reach:slow"]))
    started = time.monotonic()
    _, report = run_audit(target, env_timeout=0.5)
    assert time.monotonic() - started < 4
    row = row_of(report, "p1")
    assert row[1] == ra.NOT_PROBED and "timed out after 0.5s" in row[9]


def test_teardown_runs_when_the_observation_fails(target, task_shim):
    _taskfile(target, task_shim)
    derived_probe(target, argv=[PY, "-c", "raise SystemExit(7)"],
                  **_set_probe(environment=["reach:up"], teardown=["reach:down"]))
    _, report = run_audit(target)
    assert "observation step exited 7" in row_of(report, "p1")[9]
    assert not (task_shim / "port").exists()


# --------------------------------------------------------------------------- #
# Classification: the runner compares, the probe only observes
# --------------------------------------------------------------------------- #
COUNT = {"kind": "count", "value": 15, "unit": "collections"}
SET = {"kind": "set", "values": ["a", "b", "c", "d"], "unit": "endpoints"}


@pytest.mark.parametrize(("observed", "cls", "reach"), [
    (15, ra.REACHED, "15/15 collections"),
    (0, ra.NOT_REACHED, "0/15 collections"),
    (6, ra.PARTIAL, "6/15 collections"),
    (16, ra.NOT_PROBED, "16/15 collections"),
])
def test_count_classification(observed, cls, reach):
    outcome = ra.classify(COUNT, observed)
    assert (outcome.cls, outcome.reach) == (cls, reach)


@pytest.mark.parametrize(("observed", "cls", "reach"), [
    ({"a", "b", "c", "d", "extra"}, ra.REACHED, "4/4 endpoints"),
    ({"x", "y"}, ra.NOT_REACHED, "0/4 endpoints"),
    (set(), ra.NOT_REACHED, "0/4 endpoints"),
    ({"a", "c", "x"}, ra.PARTIAL, "2/4 endpoints"),
])
def test_set_classification(observed, cls, reach):
    outcome = ra.classify(SET, observed)
    assert (outcome.cls, outcome.reach) == (cls, reach)


def test_partial_set_names_the_missing_members():
    assert ra.classify(SET, {"a", "c"}).reason == "missing: b, d"


@pytest.mark.parametrize(("argv", "reason"), [
    ([PY, "-c", "print(3); raise SystemExit(2)"], "observation step exited 2"),
    ([PY, "-c", "print('three')"], "is not a single non-negative integer"),
    ([PY, "-c", "print(-1)"], "is not a single non-negative integer"),
    ([PY, "-c", "pass"], ra.REASON_SILENT),
    (["/nonexistent/probe-binary"], "not found on PATH"),
])
def test_observation_failure_is_not_probed(target, argv, reason):
    derived_probe(target, argv=argv)
    _, report = run_audit(target)
    row = row_of(report, "p1")
    assert row[1] == ra.NOT_PROBED and reason in row[9]


def test_zero_exit_alone_is_never_reached(target):
    """A silent success is no observation: the exit code is not the measurement.

    SCR-003: for a set as much as for a count, empty stdout is not probed, never
    "not reached"; a command failing silently with exit 0 measured nothing.
    """
    derived_probe(target, argv=[PY, "-c", "import sys; sys.exit(0)"],
                  expected={"kind": "set", "values": ["a"], "unit": "endpoints"})
    _, report = run_audit(target)
    row = row_of(report, "p1")
    assert row[1] == ra.NOT_PROBED and row[9].startswith("observation step printed nothing")


def test_oversized_observation_is_not_probed(target, monkeypatch):
    monkeypatch.setattr(ra, "MAX_OBSERVATION_BYTES", 16)
    derived_probe(target, argv=[PY, "-c", "print('x' * 100)"])
    _, report = run_audit(target)
    assert "observation exceeds 16 bytes" in row_of(report, "p1")[9]


def test_observation_timeout_is_not_probed(target):
    # Derived with the tight timeout from the start: tightening it later and bumping
    # derived_from without a declaration change is the SCR-001 laundering shape.
    sha = target.git("rev-parse", "HEAD")
    data = make_probe(derived_from=sha, argv=[PY, "-c", "import time; time.sleep(5)"])
    data["observe"]["timeout_seconds"] = 1
    target.write_probe(data)
    target.commit("approve probe")
    _, report = run_audit(target)
    assert "observation step timed out after 1s" in row_of(report, "p1")[9]


# --------------------------------------------------------------------------- #
# R14, R16: the report
# --------------------------------------------------------------------------- #
def test_R14_report_leads_with_the_not_probed_count(target):
    sha, _ = derived_probe(target)
    target.write_probe(make_probe("p2", derived_from=sha, approved=False))
    target.commit("unapproved probe")
    _, report = run_audit(target)
    first_content = [ln for ln in report.splitlines() if ln and not ln.startswith(("#", "<!--"))][0]
    assert first_content.startswith("**Not probed: 1 of 2 probes.** No not-constructible manifest")


def test_R14_report_states_provenance(target):
    derived_probe(target)
    _, report = run_audit(target)
    assert "Audited set: the 1 probe file(s) on disk under `project/reach-probes/`" in report
    assert "Declaration sources covered by the probe set: requirement (1)." in report
    assert "Declaration sources with no probe: endpoint, capability, inventory." in report


def test_R14_R16_row_carries_ratio_command_tier_timestamp_derivation_and_state(target):
    sha, _ = derived_probe(target, argv=[PY, "-c", "print(2)"])
    _, report = run_audit(target)
    row = row_of(report, "p1")
    assert row[1] == ra.PARTIAL
    assert row[2] == "2/3 collections"
    assert row[3] == f"`{PY} -c 'print(2)'`"
    assert row[4] == "T0"
    assert row[5] == "2026-09-23T10:00:00Z"
    assert row[6] == sha[:12]
    assert row[7] == ra.STATE_CLEAN
    assert row[8] == f"requirement: {DECL} (§Export)"


def test_R16_unexecuted_probe_says_so_instead_of_a_timestamp(target):
    derived_probe(target, approved=False)
    _, report = run_audit(target)
    assert row_of(report, "p1")[5] == "not executed"


def test_report_reach_per_tier(target):
    sha, _ = derived_probe(target)
    target.write_probe(make_probe("p2", derived_from=sha, tier="T2"))
    target.commit("t2")
    _, report = run_audit(target)
    assert "| T0 | 1 | 0 | 0 | 0 |" in report
    assert "| T2 | 0 | 0 | 0 | 1 |" in report


def test_report_neutralises_untrusted_tool_output(target):
    derived_probe(target, argv=[PY, "-c", "import sys; sys.stderr.write('bad | cell\\x1b[31m\\nnext'); sys.exit(1)"])
    _, report = run_audit(target)
    line = next(ln for ln in report.splitlines() if ln.startswith("| p1 |"))
    assert "\x1b" not in line and "bad \\| cell" in line


# --------------------------------------------------------------------------- #
# End to end through the CLI (R5, R9, R12, R14, R16)
# --------------------------------------------------------------------------- #
def test_end_to_end_T0_and_T1_through_the_cli(target, task_shim):
    _taskfile(target, task_shim)
    target.commit("taskfile")
    commits = int(target.git("rev-list", "--count", "HEAD")) + 1  # the probe commit below
    sha = target.git("rev-parse", "HEAD")
    target.write_probe(make_probe(
        "history-count", derived_from=sha,
        expected={"kind": "count", "value": commits, "unit": "commits"},
        argv=["git", "rev-list", "--count", "HEAD"],
    ))
    target.write_probe(make_probe(
        "loopback-items", derived_from=sha, tier="T1", argv=OBSERVE_SERVER,
        expected={"kind": "set", "values": ["alpha", "beta", "gamma"], "unit": "items"},
        environment=["reach:up"], teardown=["reach:down"],
    ))
    target.commit("approve probes")
    started = time.monotonic()
    proc = subprocess.run([PY, str(SCRIPT_PATH), "--repo", str(target.path)],
                          capture_output=True, text=True, timeout=60, check=False)
    elapsed = time.monotonic() - started
    assert proc.returncode == ra.EXIT_OK, proc.stderr
    assert "report written" in proc.stdout
    report = target.report()
    assert row_of(report, "history-count")[1:3] == [ra.REACHED, f"{commits}/{commits} commits"]
    assert row_of(report, "loopback-items")[1:3] == [ra.PARTIAL, "2/3 items"]
    assert "missing: gamma" in row_of(report, "loopback-items")[9]
    assert "**Not probed: 0 of 2 probes.**" in report
    assert elapsed < 20
    print(json.dumps({"end_to_end_seconds": round(elapsed, 2)}))


def test_end_to_end_empty_set_exit_code_is_distinct_from_success(target):
    proc = subprocess.run([PY, str(SCRIPT_PATH), "--repo", str(target.path)],
                          capture_output=True, text=True, timeout=60, check=False)
    assert proc.returncode == ra.EXIT_NO_PROBES != ra.EXIT_OK
    assert "not a clean result" in proc.stdout


# --------------------------------------------------------------------------- #
# The not-constructible manifest (#662 P1b): entries without a probe still count
# --------------------------------------------------------------------------- #
MANIFEST_SCHEMA_PATH = REPO_ROOT / "schemas" / "reach-not-constructible-v1.0.schema.yaml"
MANIFEST_REL = "project/reach-probes/_not-constructible.yml"


def manifest_entry(eid: str = "nc1", reason: str = "needs_model_judgement", detail: str | None = "only a Claude session executes it",
                   **extra) -> dict:
    entry: dict = {
        "id": eid,
        "declaration": {"source": "capability", "path": DECL, "location": "§Routing"},
        "reason": reason,
    }
    if detail is not None:
        entry["detail"] = detail
    entry |= {"derived_from": "a" * 40, "recorded_at": "2026-09-22T08:00:00Z"}
    return entry | extra


class TestNotConstructibleManifest:
    """The runner counts the entries the derivation could not probe (spec §"The probe", §Reporting)."""

    @staticmethod
    def write_manifest(target: Target, *entries: dict, raw: str | None = None) -> None:
        target.write(MANIFEST_REL, raw if raw is not None else yaml.safe_dump({"entries": list(entries)}, sort_keys=False))
        target.commit("record not-constructible entries")

    @staticmethod
    def validate(doc: object) -> list[str]:
        return [e.message for e in Draft202012Validator(ra.NOT_CONSTRUCTIBLE_SCHEMA).iter_errors(doc)]

    @staticmethod
    def headline(report: str) -> str:
        return [ln for ln in report.splitlines() if ln and not ln.startswith(("#", "<!--"))][0]

    # -- schema ------------------------------------------------------------- #
    def test_runner_copy_matches_the_shipped_manifest_schema(self):
        shipped = yaml.safe_load(MANIFEST_SCHEMA_PATH.read_text())
        assert _structural(shipped) == _structural(ra.NOT_CONSTRUCTIBLE_SCHEMA)

    def test_shipped_schema_is_valid_and_its_examples_and_the_shipped_example_validate(self):
        shipped = yaml.safe_load(MANIFEST_SCHEMA_PATH.read_text())
        Draft202012Validator.check_schema(shipped)
        for example in shipped["examples"]:
            assert self.validate(example) == []
        assert self.validate(yaml.safe_load((EXAMPLES / ra.MANIFEST_NAME).read_text())) == []

    def test_schemas_config_binds_the_example_to_the_manifest_schema_only(self):
        config = yaml.safe_load((REPO_ROOT / ".schemas-config.yaml").read_text())
        bound = [schema for glob, schema in config["mappings"].items()
                 if (EXAMPLES / ra.MANIFEST_NAME) in {p.resolve() for p in REPO_ROOT.glob(glob)}]
        assert bound == ["schemas/reach-not-constructible-v1.0.schema.yaml"]

    def test_a_valid_manifest_and_an_empty_one_pass(self):
        assert self.validate({"entries": [manifest_entry(), manifest_entry("nc2", detail=None)]}) == []
        assert self.validate({"entries": []}) == []

    @pytest.mark.parametrize("verdict", ["passed", "status", "result", "reached", "verdict"])
    def test_an_entry_cannot_state_a_verdict(self, verdict):
        assert any("Additional properties" in m for m in self.validate({"entries": [manifest_entry() | {verdict: True}]}))
        assert any("Additional properties" in m for m in self.validate({"entries": [], verdict: True}))

    def test_a_sixth_reason_code_is_rejected(self):
        assert any("is not one of" in m for m in self.validate({"entries": [manifest_entry(reason="too_hard")]}))

    @pytest.mark.parametrize("missing", ["id", "declaration", "reason", "derived_from", "recorded_at"])
    def test_required_fields(self, missing):
        entry = manifest_entry()
        del entry[missing]
        assert any("is a required property" in m for m in self.validate({"entries": [entry]}))

    # -- headline, table, row ----------------------------------------------- #
    def test_entries_count_in_the_headline_and_the_manifest_is_no_probe(self, target):
        derived_probe(target)
        self.write_manifest(target, manifest_entry("nc1"), manifest_entry("nc2", reason="effect_in_third_party", detail=None))
        code, report = run_audit(target)
        assert code == ra.EXIT_OK
        assert self.headline(report) == "**Not probed: 2 of 3 entries, 2 of them not constructible.**"
        assert "invalid probe" not in report
        assert "| _not-constructible |" not in report

    def test_entries_appear_in_the_tier_table_and_as_rows(self, target):
        derived_probe(target)
        self.write_manifest(target, manifest_entry("nc1"))
        _, report = run_audit(target)
        assert "| T0 | 1 | 0 | 0 | 0 |" in report
        assert f"| {ra.TIER_NONE} | 0 | 0 | 0 | 1 |" in report
        row = row_of(report, "nc1")
        assert row[1] == ra.NOT_PROBED
        assert row[3] == "—" and row[4] == "none" and row[5] == "not executed"
        assert row[7] == ra.STATE_NOT_CONSTRUCTIBLE
        assert row[8] == f"capability: {DECL} (§Routing)"
        assert row[9] == "not constructible: needs_model_judgement: only a Claude session executes it"

    def test_no_tier_row_without_manifest_entries(self, target):
        derived_probe(target)
        _, report = run_audit(target)
        assert ra.TIER_NONE not in report

    # -- provenance --------------------------------------------------------- #
    def test_provenance_names_both_counts(self, target):
        derived_probe(target)
        self.write_manifest(target, manifest_entry("nc1"), manifest_entry("nc2"))
        _, report = run_audit(target)
        assert ("Audited set: the 1 probe file(s) on disk under `project/reach-probes/` plus "
                "2 not-constructible manifest entries, 3 in all") in report
        assert f"`{MANIFEST_REL}` lists 2 entries no probe could be constructed for" in report
        assert "Declaration sources with not-constructible entries: capability (2)." in report

    def test_absent_manifest_is_stated_in_headline_and_provenance(self, target):
        derived_probe(target)
        _, report = run_audit(target)
        assert "No not-constructible manifest" in self.headline(report)
        assert f"manifest `{MANIFEST_REL}` is absent" in report
        assert "This audit did not check which" in report

    def test_empty_manifest_says_nothing_was_left_out(self, target):
        derived_probe(target)
        self.write_manifest(target)
        code, report = run_audit(target)
        assert code == ra.EXIT_OK
        assert self.headline(report) == "**Not probed: 0 of 1 entries, 0 of them not constructible.**"
        assert "lists 0 entries: the derivation recorded no entry it could not probe" in report

    # -- contradictions and invalid manifests ------------------------------- #
    def test_id_both_probe_and_manifest_entry_is_one_not_probed_finding(self, target, tmp_path):
        marker = tmp_path / "ran"
        derived_probe(target, argv=marker_argv(marker))
        self.write_manifest(target, manifest_entry("p1"))
        code, report = run_audit(target)
        assert code == ra.EXIT_FINDINGS
        assert not marker.exists(), "a contradicted probe must not execute"
        assert self.headline(report) == "**Not probed: 1 of 1 entries, 0 of them not constructible.**"
        assert sum(1 for ln in report.splitlines() if ln.startswith("| p1 |")) == 1
        assert row_of(report, "p1")[1] == ra.NOT_PROBED
        assert row_of(report, "p1")[7].startswith(ra.STATE_CONTRADICTION)
        assert "- **contradiction** `p1`" in report

    def test_duplicate_manifest_id_is_a_finding_counted_once(self, target):
        derived_probe(target)
        self.write_manifest(target, manifest_entry("nc1"), manifest_entry("nc1"))
        code, report = run_audit(target)
        assert code == ra.EXIT_FINDINGS
        assert self.headline(report) == "**Not probed: 1 of 2 entries, 1 of them not constructible.**"
        assert "- **invalid manifest**" in report and "listed more than once" in report

    def test_invalid_entry_still_counts_and_is_a_finding(self, target):
        derived_probe(target)
        self.write_manifest(target, manifest_entry("nc1", reason="too_hard", status="reached"))
        code, report = run_audit(target)
        assert code == ra.EXIT_FINDINGS
        assert self.headline(report) == "**Not probed: 1 of 2 entries, 1 of them not constructible.**"
        assert row_of(report, "nc1")[1] == ra.NOT_PROBED
        assert "manifest entry fails the not-constructible schema" in row_of(report, "nc1")[9]
        assert "- **invalid manifest entry** `nc1`" in report

    @pytest.mark.parametrize("raw", ["entries: [unclosed\n", "entries: []\nverdict: reached\n", "- nc1\n"])
    def test_unreadable_manifest_is_a_finding_and_counted_as_such(self, target, raw):
        derived_probe(target)
        self.write_manifest(target, raw=raw)
        code, report = run_audit(target)
        assert code == ra.EXIT_FINDINGS
        assert "The not-constructible manifest is unreadable" in self.headline(report)
        assert "present but unreadable" in report
        assert "- **invalid manifest**" in report

    # -- exit codes --------------------------------------------------------- #
    def test_only_not_constructible_entries_is_not_a_clean_result(self, target):
        self.write_manifest(target, manifest_entry("nc1"), manifest_entry("nc2"))
        code, report = run_audit(target)
        assert code == ra.EXIT_NO_PROBES != ra.EXIT_OK
        assert "No probe set" not in report
        assert self.headline(report) == "**Not probed: 2 of 2 entries, 2 of them not constructible.**"
        assert "the 0 probe file(s)" in report

    def test_only_not_constructible_entries_through_the_cli(self, target):
        self.write_manifest(target, manifest_entry("nc1"))
        proc = subprocess.run([PY, str(SCRIPT_PATH), "--repo", str(target.path)],
                              capture_output=True, text=True, timeout=60, check=False)
        assert proc.returncode == ra.EXIT_NO_PROBES
        assert "nothing executed" in proc.stdout and "not a clean result" in proc.stdout

    def test_empty_manifest_without_probes_is_the_no_probe_set_report(self, target):
        self.write_manifest(target)
        code, report = run_audit(target)
        assert code == ra.EXIT_NO_PROBES
        assert "**Not probed: all. No probe set.**" in report
        assert "lists 0 entries" in report

    def test_findings_take_precedence_over_no_probe_file(self, target):
        self.write_manifest(target, manifest_entry("nc1", reason="too_hard"))
        code, _ = run_audit(target)
        assert code == ra.EXIT_FINDINGS


# --------------------------------------------------------------------------- #
# Pre-merge review fixes (SCR-001..003, W1, W3, S1..S4)
# --------------------------------------------------------------------------- #
def _rewrite(target: Target, rel: str, **changes) -> dict:
    data = yaml.safe_load((target.path / rel).read_text())
    for key, value in changes.items():
        if key == "expected_value":
            data["expected"]["value"] = value
        elif key == "declaration_path":
            data["declaration"]["path"] = value
        else:
            data[key] = value
    target.write(rel, yaml.safe_dump(data, sort_keys=False))
    return data


def test_SCR001_derived_from_bump_without_declaration_change_is_weakened(target, tmp_path):
    """One commit lowers `expected` and re-records derived_from at the then-HEAD.

    The declaration did not move, so the bump re-baselines nothing: the probe is
    weakened, a finding, and never executed.
    """
    marker = tmp_path / "ran"
    _, rel = derived_probe(target, argv=marker_argv(marker, "1"))
    _rewrite(target, rel, expected_value=1, derived_from=target.git("rev-parse", "HEAD"))
    laundering = target.commit("lower the bar and re-record the derivation")
    code, report = run_audit(target)
    assert code == ra.EXIT_FINDINGS
    assert not marker.exists()
    row = row_of(report, "p1")
    assert row[1] == ra.NOT_PROBED and row[7] == ra.STATE_WEAKENED
    assert f"re-baselined without a declaration change: {laundering[:12]} moved derived_from" in row[9]
    assert COMMIT_MOVE_REFUSED in row[9]
    assert "**weakened** `p1`" in report


def test_SCR001_re_pointing_the_anchor_at_a_changed_file_does_not_launder(target):
    """The anchor is read from the probe's previous revision, not from the laundering commit."""
    _, rel = derived_probe(target)
    target.write("docs/other.md", "recently changed\n")
    target.commit("unrelated file changes")
    _rewrite(target, rel, expected_value=1, declaration_path="docs/other.md",
             derived_from=target.git("rev-parse", "HEAD"))
    target.commit("re-point, weaken, re-record")
    _, report = run_audit(target)
    row = row_of(report, "p1")
    assert row[7] == ra.STATE_WEAKENED and COMMIT_MOVE_REFUSED in row[9]


def test_SCR001_re_derivation_after_a_renamed_declaration_is_clean(target):
    """A rename with an edit takes two commits since #688: the pure move, then the re-derivation."""
    _, rel = derived_probe(target)
    target.git("mv", DECL, "docs/requirements-v2.md")
    target.commit("rename the declaration")
    _rewrite(target, rel, declaration_path="docs/requirements-v2.md",
             derived_from=_blob(target, path="docs/requirements-v2.md"))
    target.commit("follow the rename as a pure move")
    target.write("docs/requirements-v2.md", "# Requirements\n\n## Export\n\nExports 3 collections, v2.\n")
    target.commit("edit the declaration")
    _rewrite(target, rel, derived_from=_blob(target, path="docs/requirements-v2.md"))
    target.commit("re-derive against the renamed file")
    code, report = run_audit(target)
    assert code == ra.EXIT_OK
    assert row_of(report, "p1")[7] == ra.STATE_CLEAN


def test_SCR001_inherited_re_baseline_needs_the_pin_to_move(target):
    """Two-step laundering: weaken under a bogus ref (stale, silent), then restore the ref."""
    _spec_config(target, ("nolte-shared", "v0.1.8"))
    _inherited_probe(target, "v0.1.8")
    target.commit("probe")
    rel = "project/reach-probes/p1.yml"
    _rewrite(target, rel, expected_value=1, derived_from="v0.1.9")
    target.commit("weaken under a ref nobody pins")
    _rewrite(target, rel, derived_from="v0.1.8")
    target.commit("restore the pinned ref")
    _, report = run_audit(target)
    row = row_of(report, "p1")
    assert row[7] == ra.STATE_WEAKENED
    assert "the pinned ref of project/rest-api-design did not move to it" in row[9]


def test_SCR001_inherited_re_derivation_with_the_pin_is_clean(target):
    _spec_config(target, ("nolte-shared", "v0.1.8"))
    _inherited_probe(target, "v0.1.8")
    target.commit("probe")
    _spec_config(target, ("nolte-shared", "v0.1.9"))
    _rewrite(target, "project/reach-probes/p1.yml", derived_from="v0.1.9")
    target.commit("bump the pin and re-derive")
    _, report = run_audit(target)
    row = row_of(report, "p1")
    assert row[1] == ra.REACHED and row[7] == ra.STATE_CLEAN


def test_SCR001_external_anchor_cannot_be_re_baselined(target):
    _, rel = derived_probe(target, path=None)
    _rewrite(target, rel, expected_value=1, derived_from=target.git("rev-parse", "HEAD"))
    target.commit("weaken and re-record")
    _, report = run_audit(target)
    row = row_of(report, "p1")
    assert row[7] == ra.STATE_WEAKENED and "anchor outside the repository" in row[9]


def test_SCR001_delete_and_re_add_does_not_launder(target):
    _, rel = derived_probe(target)
    text = (target.path / rel).read_text()
    (target.path / rel).unlink()
    target.commit("drop the probe")
    target.write(rel, text.replace("value: 3", "value: 1"))
    readded = target.commit("re-add it weakened")
    _, report = run_audit(target)
    row = row_of(report, "p1")
    # #708: the deletion is no probe revision; the re-add is judged against the
    # revision before it, under the same anchor, so it is a later probe change.
    assert row[7] == ra.STATE_WEAKENED and f"probe changed in {readded[:12]} after its derivation" in row[9]


def test_SCR002_count_of_5000_digits_is_not_probed_not_a_traceback(target):
    derived_probe(target, argv=[PY, "-c", "print('9' * 5000)"])
    code, report = run_audit(target)
    assert code == ra.EXIT_OK
    row = row_of(report, "p1")
    assert row[1] == ra.NOT_PROBED and row[9].startswith("observation has 5000 digits; a count has at most 18")


def test_SCR002_a_remaining_value_error_is_not_probed(monkeypatch):
    """The int() guard holds even when the digit bound is loosened."""
    monkeypatch.setattr(ra, "_COUNT_RE", ra.re.compile(r"^[0-9]+$"))
    observed, why = ra.parse_observation(b"9" * 5000 + b"\n", "count")
    assert observed is None and why.startswith("observation is not a usable integer")


def test_SCR002_latin1_byte_in_probe_history_is_classified_not_a_crash(target):
    sha = target.git("rev-parse", "HEAD")
    rel = "project/reach-probes/p1.yml"
    first = yaml.safe_dump(make_probe(derived_from=sha), sort_keys=False).encode() + b"# caf\xe9\n"
    (target.path / rel).parent.mkdir(parents=True, exist_ok=True)
    (target.path / rel).write_bytes(first)
    target.commit("probe with a Latin-1 comment")
    target.write(DECL, "# Requirements\n\nExports 3 collections, reworded.\n")
    target.commit("move declaration")
    target.write_probe(make_probe(derived_from=_blob(target)))
    target.commit("re-derive as UTF-8")
    code, report = run_audit(target)
    assert code == ra.EXIT_OK
    row = row_of(report, "p1")
    assert row[1] == ra.REACHED and row[7] == ra.STATE_CLEAN


# -- W1: approval bound to the observation step ------------------------------ #
def test_W1_observation_digest_pins_the_canonical_bytes():
    probe = {"observe": {"argv": ["python3", "-c", "print('ü')"], "timeout_seconds": 30}, "tier": "T0"}
    canonical = '{"environment":[],"observe":{"argv":["python3","-c","print(\'ü\')"],"timeout_seconds":30},"teardown":[]}'
    assert ra.observation_digest(probe) == hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    with_env = probe | {"environment": ["up"], "teardown": ["down"]}
    assert ra.observation_digest(with_env) != ra.observation_digest(probe)


def test_W1_schema_admits_a_digest_and_rejects_a_malformed_one():
    probe = _valid()
    probe["approval"]["observation_digest"] = "a" * 64
    assert validate(probe) == []
    probe["approval"]["observation_digest"] = "A" * 64
    assert validate(probe)


def _digest_probe(target: Target, argv: list[str], approved_argv: list[str]) -> None:
    sha = target.git("rev-parse", "HEAD")
    data = make_probe(derived_from=sha, argv=approved_argv)
    data["approval"]["observation_digest"] = ra.observation_digest(data)
    data["observe"]["argv"] = argv
    target.write_probe(data)
    target.commit("approve probe")


def test_W1_swapped_argv_under_an_old_digest_is_refused(target, tmp_path):
    marker = tmp_path / "ran"
    _digest_probe(target, argv=marker_argv(marker), approved_argv=[PY, "-c", "print(3)"])
    code, report = run_audit(target)
    assert code == ra.EXIT_FINDINGS
    assert not marker.exists()
    row = row_of(report, "p1")
    assert row[1] == ra.NOT_PROBED and row[9] == "approval does not cover the current observation step"
    assert row[7] == ra.STATE_APPROVAL_MISMATCH and "**approval mismatch** `p1`" in report


def test_W1_matching_digest_runs_without_a_note(target):
    _digest_probe(target, argv=[PY, "-c", "print(3)"], approved_argv=[PY, "-c", "print(3)"])
    code, report = run_audit(target)
    assert code == ra.EXIT_OK
    row = row_of(report, "p1")
    assert row[1] == ra.REACHED and ra.NOTE_NO_DIGEST not in row[9]


def test_W1_absent_digest_runs_with_a_note(target):
    derived_probe(target)
    code, report = run_audit(target)
    assert code == ra.EXIT_OK
    row = row_of(report, "p1")
    assert row[1] == ra.REACHED and row[9] == "approval carries no observation digest"


# -- W3: symlinks ------------------------------------------------------------ #
SECRET = "-----BEGIN OPENSSH PRIVATE KEY----- s3cr3t-key-material"


def test_W3_symlinked_probe_is_a_finding_and_its_target_is_never_read(target, tmp_path):
    secret = tmp_path / "id_ed25519"
    secret.write_text(f"tier: {SECRET!r}\n")
    derived_probe(target)
    (target.path / "project" / "reach-probes" / "key.yml").symlink_to(secret)
    target.commit("link a probe")
    code, report = run_audit(target)
    assert code == ra.EXIT_FINDINGS
    assert "s3cr3t" not in report
    assert "symlink: refused and not read" in row_of(report, "key")[9]
    assert "**invalid probe** `key`" in report


def test_W3_read_inside_refuses_an_in_repo_link_and_an_outside_resolution(target, tmp_path):
    (target.path / "docs" / "link.yml").symlink_to(target.path / DECL)
    with pytest.raises(ra.UnsafePathError, match="is a symlink"):
        ra.read_inside(target.path, target.path / "docs" / "link.yml")
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "p.yml").write_text(SECRET)
    (target.path / "linked-dir").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ra.UnsafePathError, match="resolves outside the repository"):
        ra.read_inside(target.path, target.path / "linked-dir" / "p.yml")


def test_W3_symlinked_report_path_is_refused(target, tmp_path):
    derived_probe(target)
    victim = tmp_path / "victim.txt"
    victim.write_text("precious\n")
    report_dir = target.path / ".audits" / "capability-reach"
    report_dir.mkdir(parents=True)
    (report_dir / "2026-09-23.md").symlink_to(victim)
    with pytest.raises(ra.AuditError, match="is a symlink; refusing to write through it"):
        ra.run(str(target.path), clock=lambda: FIXED_NOW)
    assert victim.read_text() == "precious\n"


def test_W3_symlinked_spec_config_is_unresolved_not_read(target):
    target.write("docs/pins.yml", yaml.safe_dump({"inherits": [{"source": "nolte-shared", "ref": "v0.1.8"}]}))
    (target.path / "spec").mkdir()
    (target.path / "spec" / ".spec-config.yml").symlink_to(target.path / "docs" / "pins.yml")
    _inherited_probe(target, "v0.1.8")
    target.commit("probe")
    _, report = run_audit(target)
    row = row_of(report, "p1")
    assert row[7] == ra.STATE_UNRESOLVED and "spec/.spec-config.yml is a symlink" in row[9]


def test_W3_spec_config_resolving_outside_the_repo_is_unresolved(target, tmp_path):
    outside = tmp_path / "outside-spec"
    outside.mkdir()
    (outside / ".spec-config.yml").write_text(yaml.safe_dump({"inherits": [{"source": "hub", "ref": "v0.1.8"}]}))
    (target.path / "spec").symlink_to(outside, target_is_directory=True)
    _inherited_probe(target, "v0.1.8")
    target.commit("probe")
    _, report = run_audit(target)
    assert "resolves outside the repository" in row_of(report, "p1")[9]


def test_W3_symlinked_manifest_is_an_unreadable_finding(target, tmp_path):
    derived_probe(target)
    secret = tmp_path / "manifest-secret.yml"
    secret.write_text(f"entries: [{SECRET!r}]\n")
    (target.path / MANIFEST_REL).symlink_to(secret)
    target.commit("link the manifest")
    code, report = run_audit(target)
    assert code == ra.EXIT_FINDINGS
    assert "s3cr3t" not in report and "present but unreadable" in report
    assert "refused and not read: is a symlink" in report


# -- S1: Markdown and code-span injection ------------------------------------ #
def test_S1_cell_escapes_markdown_that_opens_comments_html_or_links():
    assert ra.cell("a<!--b[c](d)>") == "a\\<!--b\\[c\\](d)\\>"
    assert ra.cell("\\<!--") == "\\\\\\<!--"


def test_S1_schema_error_cannot_comment_out_the_report(target):
    sha = target.git("rev-parse", "HEAD")
    target.write_probe(make_probe(derived_from=sha, tier="<!--"))
    target.commit("probe")
    _, report = run_audit(target)
    unescaped = [m.start() for m in re.finditer(r"(?<!\\)<!--", report)]
    assert len(unescaped) == 1, "only the generator comment may open an HTML comment"
    assert "tier: '\\<!--' is not one of \\['T0', 'T1', 'T2'\\]" in report
    assert "## Probes" in report


def test_S1_code_cell_fence_outgrows_any_backtick_run():
    assert ra.code_cell("echo ``x`` | y") == "``` echo ``x`` \\| y ```"
    assert ra.code_cell("plain") == "`plain`"


def test_S1_backtick_in_argv_stays_inside_its_code_span(target):
    derived_probe(target, argv=[PY, "-c", "print(3) # ``"])
    _, report = run_audit(target)
    assert row_of(report, "p1")[3] == f"``` {PY} -c 'print(3) # ``' ```"


# -- S3, S4: process control ------------------------------------------------- #
def test_S3_keyboard_interrupt_kills_the_process_group(tmp_path, monkeypatch):
    started: list[subprocess.Popen] = []

    class InterruptedPopen(subprocess.Popen):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            started.append(self)

        def wait(self, timeout=None):
            if timeout is not None:
                raise KeyboardInterrupt
            return super().wait()

    monkeypatch.setattr(ra.subprocess, "Popen", InterruptedPopen)
    try:
        with pytest.raises(KeyboardInterrupt):
            ra.run_command([PY, "-c", "import time; time.sleep(30)"], tmp_path, timeout=60)
        assert started and started[0].returncode == -signal.SIGKILL
    finally:
        for proc in started:
            if proc.returncode is None:
                proc.kill()
                subprocess.Popen.wait(proc)


def test_S4_runaway_observation_is_killed_at_the_byte_bound(tmp_path):
    argv = [PY, "-c", "import sys\nwhile True: sys.stdout.write('x' * 65536)"]
    started = time.monotonic()
    res = ra.run_command(argv, tmp_path, timeout=20, max_stdout=1024 * 1024, kill_on_overflow=True)
    assert time.monotonic() - started < 10
    assert res.oversized and res.returncode is None
    assert len(res.stdout) == 1024 * 1024


def test_S4_environment_output_past_the_bound_is_discarded_not_fatal(tmp_path):
    argv = [PY, "-c", "import sys; sys.stdout.write('x' * 200000); sys.exit(0)"]
    res = ra.run_command(argv, tmp_path, timeout=20, max_stdout=100)
    assert res.returncode == 0 and len(res.stdout) == 100


# -- S2: sanitiser ----------------------------------------------------------- #
@pytest.mark.parametrize("char", ["\u200e", "\u200f", "\u061c", "\u2028", "\u2029",
                                  "\u200b", "\u200c", "\u200d", "\u2060", "\ufeff"])
def test_S2_invisible_and_direction_characters_are_stripped(char):
    assert ra.safe_text(f"a{char}b") == "ab"


def test_S2_file_name_in_a_git_error_is_sanitised(monkeypatch, tmp_path):
    git = ra.Git(tmp_path)
    monkeypatch.setattr(git, "run", lambda *a: subprocess.CompletedProcess(a, 128, "", "fatal: no\u202e"))
    with pytest.raises(ra.AuditError) as err:
        git.out("log", "--", "project/reach-probes/a\u202eb.yml")
    assert "\u202e" not in str(err.value) and "a" + "b.yml" in str(err.value)


def test_S2_report_directory_outside_the_repo_is_named_sanitised(target, tmp_path):
    outside = tmp_path / "evil\u202edir"
    outside.mkdir()
    (target.path / ".audits").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ra.AuditError) as err:
        ra.report_path(target.path, "2026-09-23")
    assert "\u202e" not in str(err.value) and "evildir" in str(err.value)


def test_S2_probe_file_name_with_rlo_is_rendered_stripped(target):
    sha = target.git("rev-parse", "HEAD")
    target.write("project/reach-probes/bad\u202egnp.yml", "tier: [unclosed\n")
    target.write_probe(make_probe(derived_from=sha), name="p\u202eok")
    target.commit("probes with RLO in their names")
    code, report = run_audit(target)
    assert "\u202e" not in report
    assert "**invalid probe** `badgnp` (project/reach-probes/badgnp.yml)" in report
    # A non-ASCII probe path still classifies: git returns it unquoted.
    row = row_of(report, "p1")
    assert row[1] == ra.REACHED and row[7] == ra.STATE_CLEAN
    assert code == ra.EXIT_FINDINGS


# --------------------------------------------------------------------------- #
# Content anchors (#668): derived_from: "blob:<sha1>" survives a squash merge
# --------------------------------------------------------------------------- #
def _blob(target: Target, rev: str = "HEAD", path: str = DECL) -> str:
    """The content anchor of ``path`` at ``rev``: what the derivation records."""
    return "blob:" + target.git("rev-parse", f"{rev}:{path}")


def _has_commit(target: Target, sha: str) -> bool:
    res = subprocess.run(["git", "-C", str(target.path), "cat-file", "-e", f"{sha}^{{commit}}"],
                         capture_output=True, check=False)
    return res.returncode == 0


def _squash_merge(target: Target, branch: str) -> str:
    """Squash ``branch`` onto main as a new commit, then drop every trace of the branch."""
    target.git("checkout", "-q", "main")
    target.git("merge", "--squash", "-q", branch)
    squashed = target.commit(f"squash {branch}")
    target.git("branch", "-D", branch)
    target.git("reflog", "expire", "--expire=now", "--all")
    target.git("gc", "-q", "--prune=now")
    return squashed


def _plain(cell_text: str) -> str:
    """A report cell with its markdown escapes removed."""
    return cell_text.replace("\\", "")


def _content_probe(target: Target, **kw) -> str:
    """Derive with a content anchor at HEAD, then commit the probe."""
    rel = target.write_probe(make_probe(derived_from=_blob(target), **kw))
    target.commit("approve probe")
    return rel


def _pr_re_deriving(target: Target, rel: str, branch: str, text: str) -> list[str]:
    """On ``branch``: edit the declaration, re-derive the probe. Returns the branch commits."""
    target.git("checkout", "-q", "-b", branch)
    target.write(DECL, text)
    edit = target.commit("edit the declaration")
    _rewrite(target, rel, derived_from=_blob(target))
    return [edit, target.commit("re-derive the probe")]


def test_668_squash_merged_re_derivation_is_clean(target):
    """(a) The PR's own commits never reach main; the content anchor does not need them."""
    rel = _content_probe(target)
    branch_commits = _pr_re_deriving(target, rel, "feat/reword", "# Requirements\n\nExports 3 collections.\n")
    _squash_merge(target, "feat/reword")
    assert not any(_has_commit(target, c) for c in branch_commits)
    code, report = run_audit(target)
    row = row_of(report, "p1")
    assert code == ra.EXIT_OK, row[7:]
    assert row[1] == ra.REACHED and row[7] == ra.STATE_CLEAN


def test_668_declaration_edit_after_content_anchor_is_stale(target, tmp_path):
    """(b)"""
    marker = tmp_path / "ran"
    _content_probe(target, argv=marker_argv(marker))
    anchor = _blob(target)
    target.write(DECL, "# Requirements\n\nExports 4 collections.\n")
    target.commit("move the declaration")
    _, report = run_audit(target)
    row = row_of(report, "p1")
    assert row[1] == ra.NOT_PROBED and row[7] == ra.STATE_STALE
    assert f"declaration changed since derivation: the content of {DECL} at HEAD is no longer {anchor[:17]}" in row[9]
    assert not marker.exists()


def test_668_uncommitted_declaration_edit_under_content_anchor_is_stale(target):
    _content_probe(target)
    target.write(DECL, "edited, not committed\n")
    _, report = run_audit(target)
    row = row_of(report, "p1")
    assert row[7] == ra.STATE_STALE and f"{DECL} has uncommitted changes" in row[9]


@pytest.mark.parametrize("bogus", ["blob:" + "b" * 40, "blob:" + "0" * 40])
def test_668_content_anchor_bump_without_content_change_is_weakened(target, tmp_path, bogus):
    """(c) Lowering `expected` and moving the anchor, while the declaration stays put."""
    marker = tmp_path / "ran"
    rel = _content_probe(target, argv=marker_argv(marker, "1"))
    _rewrite(target, rel, expected_value=1, derived_from=bogus)
    laundering = target.commit("lower the bar and move the anchor")
    code, report = run_audit(target)
    assert code == ra.EXIT_FINDINGS and not marker.exists()
    row = row_of(report, "p1")
    assert row[7] == ra.STATE_WEAKENED
    assert f"re-baselined without a declaration change: {laundering[:12]} moved derived_from" in row[9]
    assert f"but {bogus[:12]} is not the content of {DECL} at {laundering[:12]}" in row[9]


def test_668_content_anchor_bump_to_another_file_does_not_launder(target):
    """Re-pointing the anchor at a changed file and naming its content proves nothing."""
    rel = _content_probe(target)
    target.write("docs/other.md", "recently changed\n")
    target.commit("unrelated file changes")
    _rewrite(target, rel, expected_value=1, declaration_path="docs/other.md",
             derived_from=_blob(target, path="docs/other.md"))
    target.commit("re-point, weaken, re-anchor")
    _, report = run_audit(target)
    row = row_of(report, "p1")
    assert row[7] == ra.STATE_WEAKENED and f"but {DECL} did not change in between" in row[9]


def test_668_content_anchor_bump_with_content_change_needs_no_old_commit(target):
    """(d) Two squashed PRs: neither the first nor the second derivation's commit survives."""
    rel = _content_probe(target)
    gone = _pr_re_deriving(target, rel, "feat/one", "# Requirements\n\nExports 3 collections, v2.\n")
    _squash_merge(target, "feat/one")
    gone += _pr_re_deriving(target, rel, "feat/two", "# Requirements\n\nExports 3 collections, v3.\n")
    _squash_merge(target, "feat/two")
    assert not any(_has_commit(target, c) for c in gone)
    code, report = run_audit(target)
    assert code == ra.EXIT_OK
    assert row_of(report, "p1")[7] == ra.STATE_CLEAN


@pytest.mark.parametrize("how", ["rename", "delete"])
def test_668_renamed_or_deleted_declaration_under_content_anchor_is_stale(target, how):
    """(e)"""
    _content_probe(target)
    if how == "rename":
        target.git("mv", DECL, "docs/requirements-v2.md")
    else:
        target.git("rm", "-q", DECL)
    target.commit(how)
    _, report = run_audit(target)
    row = row_of(report, "p1")
    assert row[7] == ra.STATE_STALE
    assert f"declaration changed since derivation: {DECL} no longer exists at HEAD" in row[9]


def test_668_re_derivation_after_a_renamed_declaration_under_content_anchor_is_clean(target):
    rel = _content_probe(target)
    target.git("mv", DECL, "docs/requirements-v2.md")
    target.commit("rename the declaration")
    _rewrite(target, rel, declaration_path="docs/requirements-v2.md",
             derived_from=_blob(target, path="docs/requirements-v2.md"))
    target.commit("re-derive against the renamed file")
    code, report = run_audit(target)
    row = row_of(report, "p1")
    assert code == ra.EXIT_OK, row[7:]
    assert row[7] == ra.STATE_CLEAN


def test_668_re_pointing_a_content_anchor_at_an_identical_copy_does_not_launder(target):
    """Same blob, other file: the anchor value stays, the path moves, the original stays put."""
    rel = _content_probe(target)
    target.write("docs/copy.md", (target.path / DECL).read_text())
    target.commit("copy the declaration")
    _rewrite(target, rel, expected_value=1, declaration_path="docs/copy.md")
    laundering = target.commit("re-point at the copy and weaken")
    _, report = run_audit(target)
    row = row_of(report, "p1")
    assert row[7] == ra.STATE_WEAKENED
    assert f"{laundering[:12]} moved the declaration of blob:" in row[9]
    assert f"from {DECL} to docs/copy.md, but {DECL} did not change in between" in row[9]


def test_668_declaration_edited_and_restored_is_clean(target):
    """(f) A -> B -> A: the content is what was derived from. Accepted trade-off: the
    content anchor judges the declaration's text, not the path it took."""
    _content_probe(target)
    original = (target.path / DECL).read_text()
    target.write(DECL, "# Requirements\n\nExports 4 collections.\n")
    target.commit("edit")
    target.write(DECL, original)
    target.commit("revert")
    code, report = run_audit(target)
    assert code == ra.EXIT_OK
    assert row_of(report, "p1")[7] == ra.STATE_CLEAN


def test_668_content_anchor_on_an_inherited_spec_is_unresolved(target, tmp_path):
    """(g) An inherited spec is anchored by its pinned ref; a blob names no pin."""
    marker = tmp_path / "ran"
    _spec_config(target, ("nolte-shared", "v0.1.8"))
    probe = make_probe(derived_from="blob:" + "a" * 40, path=None, argv=marker_argv(marker))
    probe["declaration"]["inherited_spec"] = "project/rest-api-design"
    target.write_probe(probe)
    target.commit("probe")
    _, report = run_audit(target)
    row = row_of(report, "p1")
    assert row[1] == ra.NOT_PROBED and row[7] == ra.STATE_UNRESOLVED
    assert "is a content anchor, but an inherited spec is anchored by its pinned inherits[].ref" in _plain(row[9])
    assert not marker.exists()


def test_668_content_anchor_on_an_external_anchor_is_unresolved(target):
    target.write_probe(make_probe(derived_from="blob:" + "a" * 40, path=None))
    target.commit("probe")
    _, report = run_audit(target)
    row = row_of(report, "p1")
    assert row[7] == ra.STATE_UNRESOLVED
    assert "a content anchor needs a declaration file inside the repository" in row[9]


@pytest.mark.parametrize("bad", ["blob:abc", "blob:" + "A" * 40, "blob:"])
def test_668_malformed_content_anchor_is_unresolved(target, bad):
    target.write_probe(make_probe(derived_from=bad))
    target.commit("probe")
    _, report = run_audit(target)
    row = row_of(report, "p1")
    assert row[7] == ra.STATE_UNRESOLVED
    assert "is not a content anchor of the form blob:<40 hex digits>" in _plain(row[9])


def test_668_commit_to_content_anchor_migration_after_a_declaration_change_is_clean(target):
    """(h) A probe derived before v1.1 re-derives onto a content anchor."""
    _, rel = derived_probe(target)
    target.write(DECL, "# Requirements\n\nExports 3 collections, reworded.\n")
    _rewrite(target, rel, derived_from="blob:" + target.git("hash-object", DECL))
    target.commit("edit the declaration and re-derive onto a content anchor")
    code, report = run_audit(target)
    row = row_of(report, "p1")
    assert code == ra.EXIT_OK, row[7:]
    assert row[7] == ra.STATE_CLEAN


def test_668_commit_to_content_anchor_migration_without_a_change_is_weakened(target):
    _, rel = derived_probe(target)
    _rewrite(target, rel, expected_value=1, derived_from=_blob(target))
    target.commit("migrate the anchor and lower the bar")
    _, report = run_audit(target)
    row = row_of(report, "p1")
    assert row[7] == ra.STATE_WEAKENED and f"but {DECL} did not change in between" in row[9]


def test_668_commit_to_content_anchor_migration_without_the_old_commit_needs_a_change(target):
    """An unresolvable commit anchor is judged by the content where it was recorded (#673 R2)."""
    rel = target.write_probe(make_probe(derived_from="0" * 40))
    target.commit("probe under an unknown commit")
    _rewrite(target, rel, expected_value=1, derived_from=_blob(target))
    target.commit("re-derive onto a content anchor and lower the bar")
    _, report = run_audit(target)
    row = row_of(report, "p1")
    assert row[7] == ra.STATE_WEAKENED
    assert f"but {DECL} did not change in between" in row[9]


def test_668_unresolvable_commit_anchor_on_a_then_missing_declaration_is_weakened(target):
    rel = target.write_probe(make_probe(derived_from="0" * 40, path="docs/later.md"))
    recorded = target.commit("probe under an unknown commit, for a file that does not exist yet")
    target.write("docs/later.md", "# Later\n\nExports 3 collections.\n")
    _rewrite(target, rel, derived_from="blob:" + target.git("hash-object", "docs/later.md"))
    target.commit("write the declaration, re-derive onto a content anchor")
    _, report = run_audit(target)
    row = row_of(report, "p1")
    assert row[7] == ra.STATE_WEAKENED
    assert ("but the previous derived_from cannot be resolved to a commit and docs/later.md did not exist at "
            f"{recorded[:12]}, where it was recorded, so no declaration change can be shown") in _plain(row[9])


def test_668_schema_admits_a_content_anchor():
    assert validate(_valid() | {"derived_from": "blob:" + "a" * 40}) == []


# --------------------------------------------------------------------------- #
# Independent-review findings on #668 (F1-F4): laundering through unproven anchors
# --------------------------------------------------------------------------- #
def _weakened_reason(target: Target, marker: Path | None = None) -> str:
    code, report = run_audit(target)
    row = row_of(report, "p1")
    assert code == ra.EXIT_FINDINGS, row[7:]
    assert row[1] == ra.NOT_PROBED and row[7] == ra.STATE_WEAKENED, row[7:]
    assert marker is None or not marker.exists()
    return _plain(row[9])


def _assert_clean(target: Target) -> None:
    code, report = run_audit(target)
    row = row_of(report, "p1")
    assert code == ra.EXIT_OK, row[7:]
    assert row[1] == ra.REACHED and row[7] == ra.STATE_CLEAN


def test_668_F1_laundering_through_an_unproven_content_anchor_is_weakened(target, tmp_path):
    """Y lowers `expected` and records a blob that never existed; Z restores the real blob."""
    marker = tmp_path / "ran"
    rel = _content_probe(target, argv=marker_argv(marker, "1"))
    anchor = _blob(target)
    _rewrite(target, rel, expected_value=1, derived_from="blob:" + "b" * 40)
    weakening = target.commit("lower the bar under a made-up anchor")
    _rewrite(target, rel, derived_from=anchor)
    target.commit("restore the real anchor")
    reason = _weakened_reason(target, marker)
    assert (f"but the previous derived_from blob:bbbbbbb is not the content of {DECL} at {weakening[:12]}, "
            "where it was recorded, so no declaration change can be shown") in reason


def test_668_F1_laundering_through_an_unproven_commit_anchor_is_weakened(target, tmp_path):
    """Same laundering with a commit anchor whose declaration content is another one."""
    marker = tmp_path / "ran"
    old = target.git("rev-parse", "HEAD")
    target.write(DECL, "# Requirements\n\nExports 3 collections, v2.\n")
    target.commit("edit the declaration")
    rel = _content_probe(target, argv=marker_argv(marker, "1"))
    anchor = _blob(target)
    _rewrite(target, rel, expected_value=1, derived_from=old)
    weakening = target.commit("lower the bar under an old commit anchor")
    _rewrite(target, rel, derived_from=anchor)
    target.commit("restore the real anchor")
    reason = _weakened_reason(target, marker)
    assert (f"but the content of {DECL} at the previous derived_from {old[:12]} is not its content at "
            f"{weakening[:12]}, where it was recorded, so no declaration change can be shown") in reason


@pytest.mark.parametrize("flow", ["later-commit", "same-commit"])
def test_668_F1_re_derivation_after_a_real_declaration_change_stays_clean(target, flow):
    rel = _content_probe(target)
    target.write(DECL, "# Requirements\n\nExports 3 collections, reworded.\n")
    if flow == "later-commit":
        target.commit("edit the declaration")
    _rewrite(target, rel, derived_from="blob:" + target.git("hash-object", DECL))
    target.commit("re-derive")
    _assert_clean(target)


def test_668_F2_rename_and_weakening_in_one_commit_is_weakened(target, tmp_path):
    marker = tmp_path / "ran"
    rel = _content_probe(target, argv=marker_argv(marker, "1"))
    target.git("mv", DECL, "docs/v2.md")
    _rewrite(target, rel, expected_value=1, declaration_path="docs/v2.md")
    laundering = target.commit("rename the declaration and lower the bar")
    reason = _weakened_reason(target, marker)
    assert f"{laundering[:12]} moved the declaration of blob:" in reason
    assert (f"from {DECL} to docs/v2.md, but the same commit changed the probe beyond declaration.path, "
            "which a pure move of the declaration does not justify") in reason


def test_668_F2_rename_and_path_update_in_one_commit_stays_clean(target):
    rel = _content_probe(target)
    target.git("mv", DECL, "docs/v2.md")
    _rewrite(target, rel, declaration_path="docs/v2.md")
    target.commit("rename the declaration and follow it")
    _assert_clean(target)


def _restamp(target: Target, rel: str) -> dict:
    """The approval block a re-derive writes: new time and operator, same observation digest."""
    approval = dict(yaml.safe_load((target.path / rel).read_text())["approval"])
    approval.update(approved_at="2026-09-25T08:00:00Z", approved_by="another operator")
    return approval


def test_668_F2_rename_path_update_and_re_approval_in_one_commit_stays_clean(target):
    """A re-derive after a rename re-approves the probe, so `approval` moves with the path."""
    rel = _content_probe(target)
    target.git("mv", DECL, "docs/v2.md")
    _rewrite(target, rel, declaration_path="docs/v2.md", approval=_restamp(target, rel))
    target.commit("rename the declaration, re-derive and re-approve")
    _assert_clean(target)


def test_668_F2_re_approval_does_not_cover_a_weakening_in_the_rename_commit(target, tmp_path):
    marker = tmp_path / "ran"
    rel = _content_probe(target, argv=marker_argv(marker, "1"))
    target.git("mv", DECL, "docs/v2.md")
    _rewrite(target, rel, expected_value=1, declaration_path="docs/v2.md", approval=_restamp(target, rel))
    target.commit("rename, re-approve and lower the bar")
    assert "the same commit changed the probe beyond declaration.path" in _weakened_reason(target, marker)


def test_668_F2_delete_and_re_point_at_an_existing_file_is_weakened(target, tmp_path):
    marker = tmp_path / "ran"
    target.write("docs/other.md", "# Other\n\nExports 1 collection.\n")
    target.commit("an unrelated document")
    rel = _content_probe(target, argv=marker_argv(marker, "1"))
    recorded = target.git("rev-parse", "HEAD")
    other = _blob(target, path="docs/other.md")
    target.git("rm", "-q", DECL)
    _rewrite(target, rel, expected_value=1, declaration_path="docs/other.md", derived_from=other)
    target.commit("delete the declaration, re-point and lower the bar")
    reason = _weakened_reason(target, marker)
    assert (f"but it also moved the declaration from {DECL} to docs/other.md, and that is no rename: {DECL} "
            f"still exists at ") in reason or f"docs/other.md already existed at {recorded[:12]}" in reason, reason


def test_668_F2_path_only_commit_cannot_adopt_an_earlier_weakening(target, tmp_path):
    marker = tmp_path / "ran"
    rel = _content_probe(target, argv=marker_argv(marker, "1"))
    recorded = target.git("rev-parse", "HEAD")
    _rewrite(target, rel, expected_value=1)
    weakening = target.commit("lower the bar")
    target.git("mv", DECL, "docs/v2.md")
    _rewrite(target, rel, declaration_path="docs/v2.md")
    target.commit("rename the declaration and follow it")
    reason = _weakened_reason(target, marker)
    assert (f"but the probe changed in {weakening[:12]} after its previous derivation was recorded in "
            f"{recorded[:12]}") in reason


def test_668_F3_pure_commit_to_content_anchor_migration_is_clean(target):
    _, rel = derived_probe(target)
    _rewrite(target, rel, derived_from=_blob(target))
    target.commit("migrate the anchor, nothing else")
    _assert_clean(target)


def test_668_F3_migration_cannot_adopt_an_earlier_weakening(target, tmp_path):
    marker = tmp_path / "ran"
    sha, rel = derived_probe(target, argv=marker_argv(marker, "1"))
    recorded = target.git("rev-parse", "HEAD")
    _rewrite(target, rel, expected_value=1)
    weakening = target.commit("lower the bar")
    _rewrite(target, rel, derived_from=_blob(target))
    target.commit("migrate the anchor")
    reason = _weakened_reason(target, marker)
    assert (f"but the probe changed in {weakening[:12]} after its previous derivation was recorded in "
            f"{recorded[:12]}") in reason


@pytest.mark.parametrize("kind", ["directory", "submodule"])
def test_668_F4_declaration_replaced_by_a_non_file_is_named_so(target, kind):
    _content_probe(target)
    target.git("rm", "-q", DECL)
    if kind == "directory":
        target.write(f"{DECL}/part.md", "a directory now\n")
        target.git("add", "-A")
    else:
        head = target.git("rev-parse", "HEAD")
        target.git("update-index", "--add", "--cacheinfo", f"160000,{head},{DECL}")
        (target.path / DECL).mkdir(parents=True)  # an uninitialised submodule: an empty directory, not dirty
    target.git("commit", "-q", "-m", f"replace the declaration with a {kind}")
    _, report = run_audit(target)
    row = row_of(report, "p1")
    assert row[7] == ra.STATE_STALE
    assert f"declaration changed since derivation: {DECL} is not a regular file at HEAD" in row[9]


# --------------------------------------------------------------------------- #
# Pre-merge review findings on #673 (R1, R2): commit-to-content migration
# --------------------------------------------------------------------------- #
def test_668_R1_pure_migration_with_the_approval_stamp_derive_writes_is_clean(target):
    """`derive` always re-stamps `approval`; a pure migration is still only a re-label."""
    _, rel = derived_probe(target)
    _rewrite(target, rel, derived_from=_blob(target), approval=_restamp(target, rel))
    target.commit("migrate the anchor and re-approve, nothing else")
    _assert_clean(target)


def test_668_R1_re_approval_does_not_cover_a_weakening_in_the_migration_commit(target, tmp_path):
    marker = tmp_path / "ran"
    _, rel = derived_probe(target, argv=marker_argv(marker, "1"))
    _rewrite(target, rel, expected_value=1, derived_from=_blob(target), approval=_restamp(target, rel))
    target.commit("migrate, re-approve and lower the bar")
    assert f"but {DECL} did not change in between" in _weakened_reason(target, marker)


def _squash_lost_commit_anchor(target: Target, *, probe_on_main: bool, **kw) -> str:
    """A v1.0 commit anchor recorded on a branch whose commits a squash merge dropped."""
    rel = derived_probe(target, **kw)[1] if probe_on_main else None
    target.git("checkout", "-q", "-b", "feat/v1")
    target.write(DECL, "# Requirements\n\nExports 3 collections, on a branch.\n")
    edit = target.commit("edit the declaration")
    if rel is None:
        rel = target.write_probe(make_probe(derived_from=edit, **kw))
    else:
        _rewrite(target, rel, derived_from=edit)
    target.commit("derive the probe at the branch commit")
    _squash_merge(target, "feat/v1")
    assert not _has_commit(target, edit)
    return rel


@pytest.mark.parametrize("probe_on_main", [False, True])
def test_668_R2_re_derivation_after_a_squash_lost_commit_anchor_is_clean(target, probe_on_main):
    """runner-exit-codes: re-derive, which records a content anchor."""
    rel = _squash_lost_commit_anchor(target, probe_on_main=probe_on_main)
    target.write(DECL, "# Requirements\n\nExports 3 collections, after the squash.\n")
    _rewrite(target, rel, derived_from="blob:" + target.git("hash-object", DECL), approval=_restamp(target, rel))
    target.commit("edit the declaration, re-derive onto a content anchor")
    _assert_clean(target)


def test_668_R2_pure_migration_of_a_squash_lost_commit_anchor_is_clean(target):
    rel = _squash_lost_commit_anchor(target, probe_on_main=False)
    _, report = run_audit(target)
    assert row_of(report, "p1")[7] == ra.STATE_UNRESOLVED
    _rewrite(target, rel, derived_from=_blob(target), approval=_restamp(target, rel))
    target.commit("migrate the anchor and re-approve, nothing else")
    _assert_clean(target)


def test_668_R2_squash_lost_anchor_migration_does_not_cover_a_weakening(target, tmp_path):
    marker = tmp_path / "ran"
    rel = _squash_lost_commit_anchor(target, probe_on_main=False, argv=marker_argv(marker, "1"))
    _rewrite(target, rel, expected_value=1, derived_from=_blob(target), approval=_restamp(target, rel))
    target.commit("migrate the anchor and lower the bar")
    assert f"but {DECL} did not change in between" in _weakened_reason(target, marker)


def test_668_R2_fabricated_unresolvable_anchor_cannot_launder_a_weakening(target, tmp_path):
    """Y lowers the bar under a commit that never existed; Z migrates without a declaration change."""
    marker = tmp_path / "ran"
    _, rel = derived_probe(target, argv=marker_argv(marker, "1"))
    _rewrite(target, rel, expected_value=1, derived_from="0" * 40)
    weakening = target.commit("lower the bar under a made-up commit anchor")
    _rewrite(target, rel, derived_from=_blob(target), approval=_restamp(target, rel))
    target.commit("migrate onto the real content anchor")
    reason = _weakened_reason(target, marker)
    assert (f"its previous derivation was no re-derivation either: {weakening[:12]} moved derived_from "
            "from ") in reason
    # The made-up commit does not resolve, so the commit that made the move stands in: the declaration there
    # is the one the previous derivation saw, and the move lowered the bar.
    assert (f"to 000000000000, but the content of {DECL} did not change in between, and a re-anchoring may "
            "change nothing but derived_from and the approval") in reason


# --------------------------------------------------------------------------- #
# Section anchors and re-confirmation (#674)
# Requirement ids R1-R10 refer to project/requirements/reach-probe-section-anchor.md.
# --------------------------------------------------------------------------- #
SECTIONED = (
    "# Requirements\n\n"
    "## 3 Export\n\n"
    "### 3.1 Collections\n\nExports 3 collections.\n\n"
    "#### 3.1.1 Format\n\nJSON.\n\n"
    "### 3.2 Schedules\n\nNightly.\n\n"
    "## 4. Rules\n\n"
    "| Id | Rule |\n|---|---|\n| AK-OS-07 | Delete on request |\n| AK-OS-08 | Export on request |\n"
)
LOCATORS = (("heading", "3.1"), ("row", "AK-OS-07"))


def _found(text: str, kind: str, locator: str) -> list[bytes]:
    return ra.find_sections(text.encode(), kind, locator)


def test_674_heading_section_runs_to_the_next_heading_of_the_same_or_a_higher_level():
    """R2: a heading's section keeps its deeper headings and ends at the next peer or parent."""
    assert _found(SECTIONED, "heading", "3.1") == [
        b"### 3.1 Collections\n\nExports 3 collections.\n\n#### 3.1.1 Format\n\nJSON.\n\n"]
    assert _found(SECTIONED, "heading", "3.1.1") == [b"#### 3.1.1 Format\n\nJSON.\n\n"]
    three = _found(SECTIONED, "heading", "3")
    assert len(three) == 1 and three[0].startswith(b"## 3 Export\n") and three[0].endswith(b"Nightly.\n\n")
    four = _found(SECTIONED, "heading", "4")  # "4." with the trailing dot stripped
    assert len(four) == 1 and four[0].startswith(b"## 4. Rules\n") and four[0].endswith(b"| AK-OS-08 | Export on request |\n")


def test_674_whitespace_and_line_endings_are_part_of_the_section():
    assert _found("## 3.1 A\r\nx \r\n## 3.2 B\r\n", "heading", "3.1") == [b"## 3.1 A\r\nx \r\n"]


def test_674_headings_inside_fenced_code_blocks_are_ignored():
    text = ("## 3.1 Real\n\nbody\n\n```md\n## 3.1 Fake\n## 5 Not a heading\n```\n\nmore\n\n"
            "~~~\n# 3.2 fenced\n~~~\n## 3.2 Next\n")
    assert _found(text, "heading", "3.1") == [
        b"## 3.1 Real\n\nbody\n\n```md\n## 3.1 Fake\n## 5 Not a heading\n```\n\nmore\n\n~~~\n# 3.2 fenced\n~~~\n"]
    assert _found(text, "heading", "5") == []
    assert len(_found(text, "heading", "3.2")) == 1


def test_674_front_matter_is_not_a_heading():
    assert _found("---\ntitle: x\n# 3.1 a comment\n---\n## 3.1 Real\n", "heading", "3.1") == [b"## 3.1 Real\n"]


def test_674_S1_a_byte_order_mark_does_not_hide_front_matter_or_the_first_heading():
    assert _found("\ufeff---\ntitle: x\n# 3.1 a comment\n---\n## 3.1 Real\n", "heading", "3.1") == [
        b"## 3.1 Real\n"]
    assert _found("\ufeff# 3.1 First\nbody\n# 3.2 Next\n", "heading", "3.1") == [
        "\ufeff# 3.1 First\nbody\n".encode()]


def test_674_S1_front_matter_needs_the_first_line_and_a_closing_line():
    # Unclosed: no front matter, so the heading after the rule counts.
    assert _found("---\n# 3.1 A\ntext\n", "heading", "3.1") == [b"# 3.1 A\ntext\n"]
    # Not on the first line: a thematic break, and the heading between the rules counts.
    assert _found("intro\n---\n# 3.1 A\n---\n", "heading", "3.1") == [b"# 3.1 A\n---\n"]


def test_674_S1_headings_and_rows_inside_html_comments_are_ignored():
    text = ("<!--\n## 3.1 Commented out\n| AK-OS-07 | old |\n-->\n"
            "## 3.1 Real\n\nbody <!-- inline -->\n\n<!-- one line -->\n"
            "<!-- starts\n## 3.2 still a comment\nends -->\n| AK-OS-07 | new |\n## 3.2 Next\n")
    assert _found(text, "heading", "3.1") == [
        b"## 3.1 Real\n\nbody <!-- inline -->\n\n<!-- one line -->\n"
        b"<!-- starts\n## 3.2 still a comment\nends -->\n| AK-OS-07 | new |\n"]
    assert _found(text, "heading", "3.2") == [b"## 3.2 Next\n"]
    assert _found(text, "row", "AK-OS-07") == [b"| AK-OS-07 | new |\n"]
    # A comment opener inside a fence opens nothing.
    assert len(_found("```\n<!--\n```\n## 3.1 A\n", "heading", "3.1")) == 1


@pytest.mark.parametrize("underline", ["=========", "---------"])
def test_674_setext_heading_is_not_a_heading(underline):
    assert _found(f"3.1 Title\n{underline}\n\ntext\n", "heading", "3.1") == []


def test_674_row_resolution():
    """R2: a row locator selects the single pipe-table row whose first cell is the id."""
    assert _found(SECTIONED, "row", "AK-OS-07") == [b"| AK-OS-07 | Delete on request |\n"]
    assert _found("AK-OS-09 | no leading pipe |\n", "row", "AK-OS-09") == []
    assert _found("```\n| AK-OS-07 | fenced |\n```\n", "row", "AK-OS-07") == []
    assert _found("| AK-OS-07 | x |\n", "row", "AK-OS") == []


def test_674_repeated_heading_or_row_is_ambiguous():
    assert len(_found("## 3.1 A\n## 3.1 B\n", "heading", "3.1")) == 2
    assert len(_found("| AK-OS-07 | a |\n| AK-OS-07 | b |\n", "row", "AK-OS-07")) == 2


def _sections_now(target: Target, locators=LOCATORS, path: str = DECL) -> list[dict]:
    """Locators with the digests of their sections in the working tree (the derivation's view)."""
    content = (target.path / path).read_bytes()
    sections = []
    for kind, locator in locators:
        found = ra.find_sections(content, kind, locator)
        digest = hashlib.sha256(found[0]).hexdigest() if len(found) == 1 else "0" * 64
        sections.append({kind: locator, "digest": digest})
    return sections


@pytest.fixture
def sectioned(tmp_path) -> Target:
    t = Target(tmp_path / "target")
    t.write(DECL, SECTIONED)
    t.commit("declare")
    return t


def _section_probe(target: Target, locators=LOCATORS, **kw) -> str:
    sections = _sections_now(target, locators)
    probe = make_probe(derived_from=ra.section_anchor(sections), **kw)
    probe["declaration"]["sections"] = sections
    rel = target.write_probe(probe)
    target.commit("approve probe")
    return rel


def _reanchor(target: Target, rel: str, *, mode: str | None = None, locators=None, sections=None,
              **changes) -> dict:
    """Re-record the section anchor from the working tree; ``mode`` re-stamps the approval."""
    data = yaml.safe_load((target.path / rel).read_text())
    for key, value in changes.items():
        if key == "expected_value":
            data["expected"]["value"] = value
        elif key.startswith("declaration_"):
            data["declaration"][key[len("declaration_"):]] = value
        else:
            data[key] = value
    if locators is None:
        locators = [next((k, v) for k, v in s.items() if k != "digest") for s in data["declaration"]["sections"]]
    data["declaration"]["sections"] = sections or _sections_now(target, locators, data["declaration"]["path"])
    data["derived_from"] = ra.section_anchor(data["declaration"]["sections"])
    if mode is not None:
        data["approval"] = dict(data["approval"], approved_at="2026-09-25T08:00:00Z", mode=mode)
    target.write(rel, yaml.safe_dump(data, sort_keys=False))
    return data


def _edit(target: Target, old: str, new: str, path: str = DECL) -> None:
    text = (target.path / path).read_text()
    assert old in text
    target.write(path, text.replace(old, new))


OUTSIDE = ("Nightly.", "Weekly.")          # in 3.2: outside every default locator
INSIDE = ("JSON.", "JSON and CSV.")        # in 3.1.1, so inside 3.1
IN_ROW = ("Delete on request", "Delete within 30 days")


def test_674_schema_admits_sections_and_the_approval_mode():
    probe = _valid() | {"derived_from": "sections:" + "a" * 64}
    probe["declaration"]["sections"] = [{"heading": "3.1.1", "digest": "b" * 64}, {"row": "AK-OS-07", "digest": "c" * 64}]
    probe["approval"]["mode"] = "reconfirmed"
    assert validate(probe) == []


@pytest.mark.parametrize("section", [
    {"heading": "3.1", "row": "AK-OS-07", "digest": "b" * 64},
    {"heading": "3.1", "digest": "B" * 64},
    {"heading": "3.1"},
    {"digest": "b" * 64},
    {"heading": "3.1 Collections", "digest": "b" * 64},
    {"row": "AK | x", "digest": "b" * 64},
])
def test_674_schema_rejects_a_malformed_locator(section):
    probe = _valid()
    probe["declaration"]["sections"] = [section]
    assert validate(probe)


def test_674_schema_rejects_sections_without_a_path_and_an_unknown_mode():
    probe = make_probe(derived_from="x", path=None)
    probe["declaration"]["sections"] = [{"heading": "3.1", "digest": "b" * 64}]
    assert validate(probe)
    probe = _valid()
    probe["approval"]["mode"] = "rubber-stamped"
    assert validate(probe)


def test_674_R9_every_v1_1_example_stays_valid():
    for example in yaml.safe_load(PRIOR_SCHEMA_PATH.read_text())["examples"]:
        assert validate(example) == []


def test_674_edit_outside_every_anchored_section_is_clean(sectioned):
    """R3: the point of the section anchor; a file anchor would read this as stale."""
    _section_probe(sectioned)
    _edit(sectioned, *OUTSIDE)
    sectioned.commit("edit another section")
    _assert_clean(sectioned)


def test_674_edit_inside_one_of_two_sections_is_stale_naming_that_locator(sectioned, tmp_path):
    marker = tmp_path / "ran"
    _section_probe(sectioned, argv=marker_argv(marker))
    _edit(sectioned, *INSIDE)
    sectioned.commit("edit 3.1.1, inside 3.1")
    _, report = run_audit(sectioned)
    row = row_of(report, "p1")
    assert row[1] == ra.NOT_PROBED and row[7] == ra.STATE_STALE and not marker.exists()
    assert f"declaration changed since derivation: in {DECL}, heading 3.1 changed" in row[9]
    assert "AK-OS-07" not in row[9]


def test_674_row_edit_is_stale_naming_the_row(sectioned):
    _section_probe(sectioned)
    _edit(sectioned, *IN_ROW)
    sectioned.commit("edit the row")
    _, report = run_audit(sectioned)
    row = row_of(report, "p1")
    assert row[7] == ra.STATE_STALE and f"in {DECL}, row AK-OS-07 changed" in row[9]


def test_674_uncommitted_edit_under_a_section_anchor_is_stale(sectioned):
    _section_probe(sectioned)
    _edit(sectioned, *OUTSIDE)
    _, report = run_audit(sectioned)
    row = row_of(report, "p1")
    assert row[7] == ra.STATE_STALE and f"{DECL} has uncommitted changes" in row[9]


def test_674_renumbered_section_is_stale_not_followed(sectioned):
    """R3: a renumbered section is not found; the runner does not guess where it went."""
    _section_probe(sectioned)
    _edit(sectioned, "### 3.1 Collections", "### 3.9 Collections")
    sectioned.commit("renumber")
    _, report = run_audit(sectioned)
    row = row_of(report, "p1")
    assert row[7] == ra.STATE_STALE and f"in {DECL}, heading 3.1 not found" in row[9]


def test_674_locator_turned_ambiguous_is_stale_naming_it(sectioned):
    _section_probe(sectioned)
    _edit(sectioned, "## 4. Rules", "### 3.1 Duplicate\n\n## 4. Rules")
    sectioned.commit("a second 3.1")
    _, report = run_audit(sectioned)
    row = row_of(report, "p1")
    assert row[7] == ra.STATE_STALE and f"in {DECL}, heading 3.1 is ambiguous (2 matches)" in row[9]


def test_674_R4_re_derivation_onto_an_ambiguous_locator_cannot_anchor(sectioned, tmp_path):
    marker = tmp_path / "ran"
    rel = _section_probe(sectioned, argv=marker_argv(marker, "3"))
    _edit(sectioned, "## 4. Rules", "### 3.1 Duplicate\n\n## 4. Rules")
    _reanchor(sectioned, rel)
    sectioned.commit("a second 3.1 and a re-derivation onto it")
    reason = _weakened_reason(sectioned, marker)
    assert f"the recorded sections are not the content of {DECL} at" in reason
    assert "heading 3.1 is ambiguous (2 matches)" in reason


# #710: a locator turned ambiguous by a duplicate elsewhere is invalid as an
# anchor (stale at HEAD, can't be recorded), but its own section is untouched,
# so it is no declaration change a re-derivation could answer.
DUPLICATE_31 = ("## 4. Rules", "### 3.1 Duplicate\n\n## 4. Rules")
BULK_5 = "\n## 5 Bulk\n\nExports 1 collection.\n"


def _duplicate_and_bulk(target: Target) -> None:
    _edit(target, *DUPLICATE_31)
    target.write(DECL, (target.path / DECL).read_text() + BULK_5)


def test_710_re_derivation_after_only_a_duplicate_heading_is_weakened(sectioned, tmp_path):
    marker = tmp_path / "ran"
    rel = _section_probe(sectioned, locators=(("heading", "3.1"),), argv=marker_argv(marker, "3"))
    _duplicate_and_bulk(sectioned)
    sectioned.commit("a second 3.1 heading and a new section 5")
    _reanchor(sectioned, rel, locators=[("heading", "5")], expected_value=1)
    sectioned.commit("re-derive onto section 5 and lower the bar")
    reason = _weakened_reason(sectioned, marker)
    assert "weakened: re-baselined without a declaration change" in reason, reason


def test_710_re_derivation_through_a_rename_after_only_a_duplicate_heading_is_weakened(sectioned, tmp_path):
    marker = tmp_path / "ran"
    rel = _section_probe(sectioned, locators=(("heading", "3.1"),), argv=marker_argv(marker, "3"))
    _duplicate_and_bulk(sectioned)
    sectioned.commit("a second 3.1 heading and a new section 5")
    sectioned.git("mv", DECL, "docs/v2.md")
    _reanchor(sectioned, rel, locators=[("heading", "5")], expected_value=1, declaration_path="docs/v2.md")
    sectioned.commit("rename the declaration, re-derive onto section 5 and lower the bar")
    reason = _weakened_reason(sectioned, marker)
    assert "weakened: re-baselined without a declaration change" in reason, reason


def test_710_re_derivation_after_a_real_change_beside_a_duplicate_heading_is_clean(sectioned, tmp_path):
    rel = _section_probe(sectioned, locators=(("heading", "3.1"),), argv=marker_argv(tmp_path / "ran", "1"))
    _duplicate_and_bulk(sectioned)
    _edit(sectioned, "Exports 3 collections.", "Exports 1 collection.")
    sectioned.commit("a second 3.1 heading, section 3.1 really changed, a new section 5")
    _reanchor(sectioned, rel, locators=[("heading", "5")], expected_value=1)
    sectioned.commit("re-derive onto section 5 and lower the bar")
    _assert_clean(sectioned)


def test_710_fall_back_to_a_file_anchor_after_only_a_duplicate_heading_cannot_lower_the_bar(sectioned, tmp_path):
    """Sections to a blob: anchor answers to the same change question as sections to sections."""
    marker = tmp_path / "ran"
    rel = _section_probe(sectioned, locators=(("heading", "3.1"),), argv=marker_argv(marker, "3"))
    _edit(sectioned, *DUPLICATE_31)
    sectioned.commit("a second 3.1 heading")
    data = yaml.safe_load((sectioned.path / rel).read_text())
    del data["declaration"]["sections"]
    data["derived_from"] = "blob:" + sectioned.git("hash-object", DECL)
    data["expected"]["value"] = 1
    sectioned.write(rel, yaml.safe_dump(data, sort_keys=False))
    sectioned.commit("fall back to the file anchor and lower the bar")
    assert f"but the anchored sections of {DECL} did not change in between" in _weakened_reason(sectioned, marker)


@pytest.mark.parametrize("rename", [False, True])
def test_710_re_derivation_onto_a_section_that_was_only_ambiguous_at_the_recording_is_weakened(
        sectioned, tmp_path, rename):
    """The new anchor's section 5 was duplicated at the recording; dropping the copy changes nothing in it.

    Section 3.1 really changed, so the previous anchor moved; but the bar is
    lowered onto section 5, whose bytes are the recording's, as without the copy.
    """
    marker = tmp_path / "ran"
    sectioned.write(DECL, SECTIONED + BULK_5 + BULK_5)
    sectioned.commit("section 5 twice")
    rel = _section_probe(sectioned, locators=(("heading", "3.1"),), argv=marker_argv(marker, "3"))
    path = DECL
    if rename:
        path = "docs/v2.md"
        sectioned.git("mv", DECL, path)
        sectioned.commit("rename the declaration")
    sectioned.write(path, SECTIONED.replace("Exports 3 collections.", "Exports 1 collection.") + BULK_5)
    _reanchor(sectioned, rel, locators=[("heading", "5")], expected_value=1, declaration_path=path)
    sectioned.commit("change 3.1, drop the copy of 5, re-derive onto 5 and lower the bar")
    reason = _weakened_reason(sectioned, marker)
    assert "but none of the sections it now anchors on changed since the previous derivation" in reason, reason


@pytest.mark.parametrize("case, expected", [
    ("digest-edited", "does not match the digests in declaration.sections"),
    ("no-sections", "is a section anchor, but declaration.sections is absent"),
    ("blob-with-sections", "declaration.sections needs derived_from of the form sections:<64 hex digits>"),
    ("malformed", "is not a section anchor of the form sections:<64 hex digits>"),
    ("duplicate-locator", "declaration.sections lists heading 3.1 more than once"),
])
def test_674_inconsistent_section_anchor_is_unresolved(sectioned, tmp_path, case, expected):
    marker = tmp_path / "ran"
    sections = _sections_now(sectioned)
    probe = make_probe(derived_from=ra.section_anchor(sections), argv=marker_argv(marker))
    probe["declaration"]["sections"] = sections
    if case == "digest-edited":
        sections[1]["digest"] = "d" * 64
    elif case == "no-sections":
        del probe["declaration"]["sections"]
    elif case == "blob-with-sections":
        probe["derived_from"] = _blob(sectioned)
    elif case == "malformed":
        probe["derived_from"] = "sections:abc"
    else:
        sections.append(dict(sections[0]))
        probe["derived_from"] = ra.section_anchor(sections)
    sectioned.write_probe(probe)
    sectioned.commit("probe")
    _, report = run_audit(sectioned)
    row = row_of(report, "p1")
    assert row[1] == ra.NOT_PROBED and row[7] == ra.STATE_UNRESOLVED and not marker.exists()
    assert expected in _plain(row[9])


@pytest.mark.parametrize("flow", ["later-commit", "same-commit"])
def test_674_R5_R6_re_confirmation_after_a_section_change_is_clean_and_reported(sectioned, flow):
    rel = _section_probe(sectioned)
    _edit(sectioned, *INSIDE)
    if flow == "later-commit":
        sectioned.commit("edit 3.1.1")
    _reanchor(sectioned, rel, mode="reconfirmed")
    sectioned.commit("re-confirm the probe")
    code, report = run_audit(sectioned)
    row = row_of(report, "p1")
    assert code == ra.EXIT_OK, row[7:]
    assert row[1] == ra.REACHED and row[7] == ra.STATE_CLEAN
    assert ra.NOTE_RECONFIRMED in row[9]
    assert f"{ra.PROVENANCE_RECONFIRMED}: 1 (p1)" in report


def test_674_R6_a_re_derivation_carries_no_re_confirmation_note(sectioned):
    rel = _section_probe(sectioned)
    _edit(sectioned, *INSIDE)
    _reanchor(sectioned, rel, mode="derived", expected_value=2)
    sectioned.commit("re-derive with a new expectation")
    _, report = run_audit(sectioned)
    row = row_of(report, "p1")
    assert row[7] == ra.STATE_CLEAN and ra.NOTE_RECONFIRMED not in row[9]
    assert ra.PROVENANCE_RECONFIRMED not in report


@pytest.mark.parametrize("change, named", [
    ({"expected_value": 1}, "expected"),
    ({"tier": "T2"}, "tier"),
    ({"observe": {"argv": [PY, "-c", "print(1)"], "timeout_seconds": 30}}, "observe"),
    ({"declaration_location": "§Elsewhere"}, "declaration.location"),
])
def test_674_R7_re_confirmation_that_changes_the_probe_is_weakened(sectioned, tmp_path, change, named):
    marker = tmp_path / "ran"
    rel = _section_probe(sectioned, argv=marker_argv(marker, "1"))
    _edit(sectioned, *INSIDE)
    sectioned.commit("edit 3.1.1")
    _reanchor(sectioned, rel, mode="reconfirmed", **change)
    sectioned.commit("re-confirm and change the probe")
    reason = _weakened_reason(sectioned, marker)
    assert (f"but a re-confirmation may change only derived_from, the section digests and approval, "
            f"and it also changed {named}") in reason


def test_674_R7_re_confirmation_cannot_swap_the_locators(sectioned, tmp_path):
    marker = tmp_path / "ran"
    rel = _section_probe(sectioned, argv=marker_argv(marker, "1"))
    _edit(sectioned, *INSIDE)
    sectioned.commit("edit 3.1.1")
    # 3.1.1 changed with 3.1, so the new anchor shows a change of its own; only the re-confirmation rule
    # refuses the swapped locator.
    _reanchor(sectioned, rel, mode="reconfirmed", locators=[("heading", "3.1.1"), ("row", "AK-OS-07")])
    sectioned.commit("re-confirm onto another section")
    assert "and it also changed declaration.sections" in _weakened_reason(sectioned, marker)


def test_674_re_confirmation_without_a_section_change_is_weakened(sectioned, tmp_path):
    marker = tmp_path / "ran"
    rel = _section_probe(sectioned, argv=marker_argv(marker, "1"))
    recorded = sectioned.git("rev-parse", "HEAD")
    _edit(sectioned, *OUTSIDE)
    sectioned.commit("edit another section")
    _reanchor(sectioned, rel, mode="reconfirmed")
    stamp = sectioned.commit("re-confirm although nothing anchored changed")
    # The digests are the recorded ones, so derived_from does not move: the stamp is
    # a plain later edit of the probe, never a re-derivation or a re-confirmation.
    assert _weakened_reason(sectioned, marker) == (
        f"weakened: probe changed in {stamp[:12]} after its derivation was recorded in {recorded[:12]}")


def test_674_R7_re_derivation_onto_other_locators_without_a_section_change_is_weakened(sectioned, tmp_path):
    marker = tmp_path / "ran"
    rel = _section_probe(sectioned, argv=marker_argv(marker, "1"))
    _edit(sectioned, *OUTSIDE)
    sectioned.commit("edit 3.2")
    _reanchor(sectioned, rel, locators=[("heading", "3.2")], expected_value=1)
    laundering = sectioned.commit("re-point at the edited section and lower the bar")
    reason = _weakened_reason(sectioned, marker)
    assert f"{laundering[:12]} moved derived_from" in reason
    assert f"but the anchored sections of {DECL} did not change in between" in reason


def test_674_R7_made_up_digests_in_one_commit_are_weakened(sectioned, tmp_path):
    marker = tmp_path / "ran"
    rel = _section_probe(sectioned, argv=marker_argv(marker, "1"))
    _reanchor(sectioned, rel, expected_value=1,
              sections=[{"heading": "3.1", "digest": "c" * 64}, {"row": "AK-OS-07", "digest": "c" * 64}])
    laundering = sectioned.commit("lower the bar under made-up digests")
    reason = _weakened_reason(sectioned, marker)
    assert f"but the recorded sections are not the content of {DECL} at {laundering[:12]}: heading 3.1 changed" in reason


def test_674_F1_laundering_through_an_unproven_section_anchor_is_weakened(sectioned, tmp_path):
    """Mirror of #673 F1: Y lowers the bar under made-up digests, Z restores the real ones."""
    marker = tmp_path / "ran"
    rel = _section_probe(sectioned, argv=marker_argv(marker, "1"))
    real = yaml.safe_load((sectioned.path / rel).read_text())["declaration"]["sections"]
    fake = _reanchor(sectioned, rel, expected_value=1, sections=[
        {"heading": "3.1", "digest": "c" * 64}, {"row": "AK-OS-07", "digest": "c" * 64}])["derived_from"][len("sections:"):]
    weakening = sectioned.commit("lower the bar under made-up digests")
    _reanchor(sectioned, rel, sections=real)
    sectioned.commit("restore the real digests")
    reason = _weakened_reason(sectioned, marker)
    assert (f"but the previous derived_from sections:{fake[:3]} is not the content of its sections of {DECL} at "
            f"{weakening[:12]}, where it was recorded, so no declaration change can be shown") in reason


def test_674_R7_re_confirmation_cannot_adopt_an_earlier_weakening(sectioned, tmp_path):
    marker = tmp_path / "ran"
    rel = _section_probe(sectioned, argv=marker_argv(marker, "1"))
    recorded = sectioned.git("rev-parse", "HEAD")
    data = yaml.safe_load((sectioned.path / rel).read_text())
    data["expected"]["value"] = 1
    sectioned.write(rel, yaml.safe_dump(data, sort_keys=False))
    weakening = sectioned.commit("lower the bar")
    _edit(sectioned, *INSIDE)
    _reanchor(sectioned, rel, mode="reconfirmed")
    sectioned.commit("edit 3.1.1 and re-confirm")
    reason = _weakened_reason(sectioned, marker)
    assert (f"and it also changed expected against the derivation recorded in {recorded[:12]}") in reason
    assert weakening != recorded


def test_674_R8_blob_to_section_migration_without_a_content_change_is_clean(sectioned):
    rel = _content_probe(sectioned)
    data = yaml.safe_load((sectioned.path / rel).read_text())
    data["declaration"]["sections"] = _sections_now(sectioned)
    data["derived_from"] = ra.section_anchor(data["declaration"]["sections"])
    data["approval"] = _restamp(sectioned, rel)
    sectioned.write(rel, yaml.safe_dump(data, sort_keys=False))
    sectioned.commit("migrate onto section anchors")
    _assert_clean(sectioned)
    _edit(sectioned, *OUTSIDE)
    sectioned.commit("edit another section")
    _assert_clean(sectioned)


def test_674_R8_migration_that_lowers_the_expectation_is_weakened(sectioned, tmp_path):
    marker = tmp_path / "ran"
    rel = _content_probe(sectioned, argv=marker_argv(marker, "1"))
    data = yaml.safe_load((sectioned.path / rel).read_text())
    data["declaration"]["sections"] = _sections_now(sectioned)
    data["derived_from"] = ra.section_anchor(data["declaration"]["sections"])
    data["expected"]["value"] = 1
    sectioned.write(rel, yaml.safe_dump(data, sort_keys=False))
    sectioned.commit("migrate and lower the bar")
    assert f"but {DECL} did not change in between" in _weakened_reason(sectioned, marker)


def test_674_R8_migration_cannot_adopt_an_earlier_weakening(sectioned, tmp_path):
    marker = tmp_path / "ran"
    rel = _content_probe(sectioned, argv=marker_argv(marker, "1"))
    _rewrite(sectioned, rel, expected_value=1)
    weakening = sectioned.commit("lower the bar")
    data = yaml.safe_load((sectioned.path / rel).read_text())
    data["declaration"]["sections"] = _sections_now(sectioned)
    data["derived_from"] = ra.section_anchor(data["declaration"]["sections"])
    sectioned.write(rel, yaml.safe_dump(data, sort_keys=False))
    sectioned.commit("migrate onto section anchors")
    assert f"but the probe changed in {weakening[:12]}" in _weakened_reason(sectioned, marker)


# --------------------------------------------------------------------------- #
# Independent review of #674: laundering through a self-made intermediate anchor
# (C1), adoption of an intermediate weakening (W1), the new anchor's own change.
# --------------------------------------------------------------------------- #
def _to_blob(target: Target, rel: str, **changes) -> dict:
    """Re-anchor on the whole file at the working tree, dropping the section locators."""
    data = yaml.safe_load((target.path / rel).read_text())
    data["declaration"].pop("sections", None)
    data["derived_from"] = "blob:" + target.git("hash-object", DECL)
    if "expected_value" in changes:
        data["expected"]["value"] = changes.pop("expected_value")
    data.update(changes)
    target.write(rel, yaml.safe_dump(data, sort_keys=False))
    return data


@pytest.mark.parametrize("edit", ["outside-3.1", "inside-3.1"])
def test_674_C1_a_self_made_section_anchor_cannot_launder_a_weakening(sectioned, tmp_path, edit):
    """C2 adds locator 3.2 and lowers the bar (weakened alone); C3 moves back onto 3.1 and AK-OS-07.

    With the edit outside 3.1 the new anchor shows no change of its own; with the
    edit inside 3.1 it does, and only the recursion into C2 refuses the move.
    """
    marker = tmp_path / "ran"
    rel = _section_probe(sectioned, argv=marker_argv(marker, "1"))
    _reanchor(sectioned, rel, locators=[*LOCATORS, ("heading", "3.2")], expected_value=1)
    weakening = sectioned.commit("anchor 3.2 too and lower the bar")
    _edit(sectioned, *(OUTSIDE if edit == "outside-3.1" else INSIDE))
    _reanchor(sectioned, rel, locators=list(LOCATORS))
    sectioned.commit("edit and move back onto the old sections")
    reason = _weakened_reason(sectioned, marker)
    if edit == "outside-3.1":
        assert (f"but none of the sections it now anchors on changed since the previous derivation was recorded "
                f"in {weakening[:12]}") in reason
    else:
        assert (f"but its previous derivation was no re-derivation either: {weakening[:12]} moved derived_from "
                f"from sections:") in reason
        assert f"but the anchored sections of {DECL} did not change in between" in reason


@pytest.mark.parametrize("edit", ["outside-3.1", "inside-3.1"])
def test_674_C1_a_self_made_blob_anchor_cannot_launder_a_weakening(sectioned, tmp_path, edit):
    """C2 records the file's blob and lowers the bar; C3 edits the file and moves back onto sections."""
    marker = tmp_path / "ran"
    rel = _section_probe(sectioned, argv=marker_argv(marker, "1"))
    _to_blob(sectioned, rel, expected_value=1)
    weakening = sectioned.commit("fall back to the file anchor and lower the bar")
    _edit(sectioned, *(OUTSIDE if edit == "outside-3.1" else INSIDE))
    data = yaml.safe_load((sectioned.path / rel).read_text())
    data["declaration"]["sections"] = _sections_now(sectioned)
    data["derived_from"] = ra.section_anchor(data["declaration"]["sections"])
    sectioned.write(rel, yaml.safe_dump(data, sort_keys=False))
    sectioned.commit("edit and switch back to the sections")
    reason = _weakened_reason(sectioned, marker)
    if edit == "outside-3.1":
        assert (f"but none of the sections it now anchors on changed since the previous derivation was recorded "
                f"in {weakening[:12]}") in reason
    else:
        assert (f"but its previous derivation was no re-derivation either: {weakening[:12]} moved derived_from "
                f"from sections:") in reason
        assert f"but the anchored sections of {DECL} did not change in between" in reason


def test_674_C1_re_anchoring_on_sections_that_did_not_change_is_weakened(sectioned, tmp_path):
    """One commit edits 3.2 and moves a file anchor onto 3.1 and AK-OS-07, lowering the bar.

    The file changed, so the previous anchor did; the sections the probe now
    anchors on did not, and those are what a re-derivation must answer to.
    """
    marker = tmp_path / "ran"
    rel = _content_probe(sectioned, argv=marker_argv(marker, "1"))
    recorded = sectioned.git("rev-parse", "HEAD")
    _edit(sectioned, *OUTSIDE)
    data = yaml.safe_load((sectioned.path / rel).read_text())
    data["declaration"]["sections"] = _sections_now(sectioned)
    data["derived_from"] = ra.section_anchor(data["declaration"]["sections"])
    data["expected"]["value"] = 1
    sectioned.write(rel, yaml.safe_dump(data, sort_keys=False))
    sectioned.commit("edit 3.2, narrow onto 3.1 and AK-OS-07, lower the bar")
    assert (f"but none of the sections it now anchors on changed since the previous derivation was recorded "
            f"in {recorded[:12]}") in _weakened_reason(sectioned, marker)


def test_674_C1_a_legitimate_chain_of_re_derivations_stays_clean(sectioned):
    """Two real re-derivations in a row: the recursion accepts each previous one."""
    rel = _section_probe(sectioned)
    _edit(sectioned, *INSIDE)
    sectioned.commit("edit 3.1.1")
    _reanchor(sectioned, rel, approval=_restamp(sectioned, rel))
    sectioned.commit("re-derive")
    _edit(sectioned, *IN_ROW)
    _to_blob(sectioned, rel)
    sectioned.commit("edit AK-OS-07 and re-derive onto the file")
    _edit(sectioned, "JSON and CSV.", "JSON, CSV.")
    data = yaml.safe_load((sectioned.path / rel).read_text())
    data["declaration"]["sections"] = _sections_now(sectioned)
    data["derived_from"] = ra.section_anchor(data["declaration"]["sections"])
    sectioned.write(rel, yaml.safe_dump(data, sort_keys=False))
    sectioned.commit("edit 3.1.1 and re-derive onto sections")
    _assert_clean(sectioned)


@pytest.mark.parametrize("mode", [None, "reconfirmed"])
def test_674_W1_a_section_re_anchor_cannot_adopt_an_intermediate_weakening(sectioned, tmp_path, mode):
    marker = tmp_path / "ran"
    rel = _section_probe(sectioned, argv=marker_argv(marker, "1"))
    recorded = sectioned.git("rev-parse", "HEAD")
    _rewrite(sectioned, rel, expected_value=1)
    weakening = sectioned.commit("lower the bar")
    _edit(sectioned, *INSIDE)
    _reanchor(sectioned, rel, mode=mode)
    sectioned.commit("edit 3.1.1 and re-anchor")
    reason = _weakened_reason(sectioned, marker)
    if mode is None:
        assert (f"but the probe changed in {weakening[:12]} after its previous derivation was recorded in "
                f"{recorded[:12]}") in reason
    else:
        assert f"and it also changed expected against the derivation recorded in {recorded[:12]}" in reason


@pytest.mark.parametrize("mode", [None, "reconfirmed"])
def test_674_W1_a_blob_re_anchor_cannot_adopt_an_intermediate_weakening(target, tmp_path, mode):
    marker = tmp_path / "ran"
    rel = _content_probe(target, argv=marker_argv(marker, "1"))
    recorded = target.git("rev-parse", "HEAD")
    _rewrite(target, rel, expected_value=1)
    weakening = target.commit("lower the bar")
    target.write(DECL, "# Requirements\n\nExports 3 collections, reworded.\n")
    approval = _restamp(target, rel) | ({"mode": mode} if mode else {})
    _rewrite(target, rel, derived_from="blob:" + target.git("hash-object", DECL), approval=approval)
    target.commit("edit the declaration and re-anchor")
    reason = _weakened_reason(target, marker)
    if mode is None:
        assert (f"but the probe changed in {weakening[:12]} after its previous derivation was recorded in "
                f"{recorded[:12]}") in reason
    else:
        assert f"and it also changed expected against the derivation recorded in {recorded[:12]}" in reason


def test_674_S3_re_confirming_an_unchanged_file_onto_sections_is_refused_by_the_re_confirmation_rule(sectioned, tmp_path):
    """A migration of an unchanged file passes the anchor check as a relabel; labelled a
    re-confirmation it adds locators, which only a derivation may do."""
    marker = tmp_path / "ran"
    rel = _content_probe(sectioned, argv=marker_argv(marker, "1"))
    recorded = sectioned.git("rev-parse", "HEAD")
    data = yaml.safe_load((sectioned.path / rel).read_text())
    data["declaration"]["sections"] = _sections_now(sectioned)
    data["derived_from"] = ra.section_anchor(data["declaration"]["sections"])
    data["approval"] = _restamp(sectioned, rel) | {"mode": "reconfirmed"}
    sectioned.write(rel, yaml.safe_dump(data, sort_keys=False))
    migration = sectioned.commit("migrate onto sections, labelled a re-confirmation")
    reason = _weakened_reason(sectioned, marker)
    assert reason == (
        f"weakened: re-baselined without a declaration change: {migration[:12]} moved derived_from from "
        f"{_blob(sectioned)[:12]} to {data['derived_from'][:12]}, but a re-confirmation may change only "
        "derived_from, the section digests and approval, and it also changed declaration.sections against the "
        f"derivation recorded in {recorded[:12]}")


def test_674_squash_merged_re_confirmation_of_a_section_anchor_is_clean(sectioned):
    rel = _section_probe(sectioned)
    sectioned.git("checkout", "-q", "-b", "feat/reword")
    _edit(sectioned, *INSIDE)
    edit = sectioned.commit("edit 3.1.1")
    _reanchor(sectioned, rel, mode="reconfirmed")
    confirm = sectioned.commit("re-confirm")
    _squash_merge(sectioned, "feat/reword")
    assert not _has_commit(sectioned, edit) and not _has_commit(sectioned, confirm)
    _assert_clean(sectioned)


def test_674_pure_move_of_a_section_anchored_declaration_is_clean(sectioned):
    rel = _section_probe(sectioned)
    sectioned.git("mv", DECL, "docs/v2.md")
    _reanchor(sectioned, rel, declaration_path="docs/v2.md")
    sectioned.commit("rename the declaration and follow it")
    _assert_clean(sectioned)


def test_674_section_to_file_anchor_after_a_section_change_is_clean(sectioned):
    rel = _section_probe(sectioned)
    _edit(sectioned, *INSIDE)
    data = yaml.safe_load((sectioned.path / rel).read_text())
    del data["declaration"]["sections"]
    data["derived_from"] = "blob:" + sectioned.git("hash-object", DECL)
    sectioned.write(rel, yaml.safe_dump(data, sort_keys=False))
    sectioned.commit("edit 3.1.1 and fall back to the file anchor")
    _assert_clean(sectioned)


def test_674_section_to_file_anchor_without_a_section_change_is_weakened(sectioned, tmp_path):
    marker = tmp_path / "ran"
    rel = _section_probe(sectioned, argv=marker_argv(marker, "1"))
    _edit(sectioned, *OUTSIDE)
    data = yaml.safe_load((sectioned.path / rel).read_text())
    del data["declaration"]["sections"]
    data["derived_from"] = "blob:" + sectioned.git("hash-object", DECL)
    data["expected"]["value"] = 1
    sectioned.write(rel, yaml.safe_dump(data, sort_keys=False))
    sectioned.commit("edit 3.2, fall back to the file anchor, lower the bar")
    assert f"but the anchored sections of {DECL} did not change in between" in _weakened_reason(sectioned, marker)


def test_674_R5_re_confirmation_of_a_file_anchor_is_clean_and_reported(target):
    rel = _content_probe(target)
    target.write(DECL, "# Requirements\n\nExports 3 collections, reworded.\n")
    target.commit("edit the declaration")
    _rewrite(target, rel, derived_from=_blob(target), approval=_restamp(target, rel) | {"mode": "reconfirmed"})
    target.commit("re-confirm")
    code, report = run_audit(target)
    row = row_of(report, "p1")
    assert code == ra.EXIT_OK and row[7] == ra.STATE_CLEAN and ra.NOTE_RECONFIRMED in row[9]


def test_674_R7_re_confirmation_of_a_file_anchor_that_lowers_the_bar_is_weakened(target, tmp_path):
    marker = tmp_path / "ran"
    rel = _content_probe(target, argv=marker_argv(marker, "1"))
    target.write(DECL, "# Requirements\n\nExports 3 collections, reworded.\n")
    target.commit("edit the declaration")
    _rewrite(target, rel, derived_from=_blob(target), expected_value=1,
             approval=_restamp(target, rel) | {"mode": "reconfirmed"})
    target.commit("re-confirm and lower the bar")
    assert "and it also changed expected" in _weakened_reason(target, marker)


# --------------------------------------------------------------------------- #
# Replay (R10)
# --------------------------------------------------------------------------- #
def test_674_R10_replay_counts_file_and_section_stale_events(sectioned, capsys):
    import reach_replay

    commits = [sectioned.git("rev-parse", "HEAD")]
    for old, new in (OUTSIDE, INSIDE, IN_ROW):
        _edit(sectioned, old, new)
        commits.append(sectioned.commit(f"edit {old}"))
    sectioned.write("docs/other.md", "unrelated\n")
    sectioned.commit("touch another file")
    _edit(sectioned, "Weekly.", "Monthly.")
    commits.append(sectioned.commit("edit 3.2 again"))
    _edit(sectioned, "### 3.1 Collections", "### 3.9 Collections")
    commits.append(sectioned.commit("renumber 3.1"))
    # A side branch changes the declaration and is merged: the replay walks the
    # first-parent history, so it sees the merge commit, never the side commit.
    sectioned.git("checkout", "-q", "-b", "side")
    _edit(sectioned, "Monthly.", "Yearly.")
    side = sectioned.commit("edit 3.2 on a side branch")
    sectioned.git("checkout", "-q", "main")
    sectioned.git("merge", "-q", "--no-ff", "-m", "merge side", "side")
    commits.append(sectioned.git("rev-parse", "HEAD"))
    assert side != commits[-1]
    code = reach_replay.main(["--repo", str(sectioned.path), "--declaration", DECL,
                              "--probe", "p1=heading:3.1", "--probe", "p2=row:AK-OS-07",
                              "--probe", "p3=heading:3.1,row:AK-OS-07"])
    assert code == 0
    c = [sha[:12] for sha in commits]
    assert capsys.readouterr().out.splitlines() == [
        f"replay of {DECL} at {sectioned.git('rev-parse', 'HEAD')[:12]}: 7 commits, 3 probes",
        f"{c[0]} first",
        f"{c[1]} file changed; sections changed: none; stale probes: file 3, section 0",
        f"{c[2]} file changed; sections changed: heading:3.1; stale probes: file 3, section 2",
        f"{c[3]} file changed; sections changed: row:AK-OS-07; stale probes: file 3, section 2",
        f"{c[4]} file changed; sections changed: none; stale probes: file 3, section 0",
        f"{c[5]} file changed; sections changed: heading:3.1 (not found); stale probes: file 3, section 2",
        f"{c[6]} file changed; sections changed: none; stale probes: file 3, section 0",
        "file-anchor stale events: 18",
        "section-anchor stale events: 6",
    ]


def test_674_R10_replay_refuses_a_malformed_locator(sectioned, capsys):
    import reach_replay

    assert reach_replay.main(["--repo", str(sectioned.path), "--declaration", DECL,
                              "--probe", "p1=chapter:3.1"]) == ra.EXIT_USAGE
    assert "chapter:3.1" in capsys.readouterr().err


# --------------------------------------------------------------------------- #
# Exit path after an intermediate weakening (follow-up to W1)
# --------------------------------------------------------------------------- #
def _weakened_chain(target: Target) -> str:
    """C1 derives, C2 lowers the bar, C3 edits 3.1.1 and re-anchors: weakened for good (W1)."""
    rel = _section_probe(target)
    _rewrite(target, rel, expected_value=1)
    target.commit("lower the bar")
    _edit(target, *INSIDE)
    _reanchor(target, rel)
    target.commit("edit 3.1.1 and re-anchor")
    assert "but the probe changed in" in _weakened_reason(target)
    return rel


def _fresh(target: Target, pid: str = "p1", locators=LOCATORS) -> dict:
    sections = _sections_now(target, locators)
    probe = make_probe(pid, derived_from=ra.section_anchor(sections))
    probe["declaration"]["sections"] = sections
    probe["approval"] = {"approved_at": "2026-09-25T08:00:00Z", "approved_by": "another operator"}
    return probe


def _state(target: Target, pid: str = "p1") -> tuple[str, str]:
    _, report = run_audit(target)
    row = row_of(report, pid)
    return row[7], _plain(row[9])


def test_674_exit_a_derive_overwrites_the_same_file(sectioned):
    rel = _weakened_chain(sectioned)
    sectioned.write(rel, yaml.safe_dump(_fresh(sectioned), sort_keys=False))
    sectioned.commit("derive afresh into the same file")
    state, reason = _state(sectioned)
    assert state == ra.STATE_WEAKENED, reason


def test_674_exit_b_delete_then_re_add_at_the_same_path(sectioned):
    rel = _weakened_chain(sectioned)
    (sectioned.path / rel).unlink()
    sectioned.commit("drop the weakened probe")
    sectioned.write(rel, yaml.safe_dump(_fresh(sectioned), sort_keys=False))
    readded = sectioned.commit("derive afresh at the same path")
    state, reason = _state(sectioned)
    # #708: the re-add is judged against the weakened chain before the deletion.
    assert state == ra.STATE_WEAKENED and f"probe changed in {readded[:12]} after its derivation" in reason, reason
    assert "its previous derivation was recorded in" in reason, reason


@pytest.mark.parametrize("flow, expected", [
    # In one commit git pairs the deletion and the new file as a rename, and the
    # history walk (--follow) carries the weakened chain over.
    ("one-commit", ra.STATE_WEAKENED),
    ("two-commits", ra.STATE_CLEAN),
])
def test_674_exit_c_fresh_probe_under_a_new_id_and_file(sectioned, flow, expected):
    """The documented exit: drop the weakened probe, then derive a new one under a new file name."""
    rel = _weakened_chain(sectioned)
    (sectioned.path / rel).unlink()
    if flow == "two-commits":
        sectioned.commit("drop the weakened probe")
    sectioned.write_probe(_fresh(sectioned, "p1-rederived"))
    sectioned.commit("derive afresh under a new id")
    state, reason = _state(sectioned, "p1-rederived")
    assert state == expected, reason


# --------------------------------------------------------------------------- #
# Pre-merge review of #675: moves onto a commit anchor (F1), SHA-256 repositories (F2)
# --------------------------------------------------------------------------- #
NO_COMMIT_PAIR = "the two cannot both be resolved to commits, so no declaration change can be shown"


def test_675_F1_section_to_commit_anchor_move_cannot_launder_a_weakening(sectioned, tmp_path):
    """A anchors on sections; B edits outside them (clean); C re-points at B's commit and lowers the bar."""
    marker = tmp_path / "ran"
    rel = _section_probe(sectioned, argv=marker_argv(marker, "1"))
    _edit(sectioned, *OUTSIDE)
    outside = sectioned.commit("edit another section")
    assert _state(sectioned)[0] == ra.STATE_CLEAN
    marker.unlink()
    data = yaml.safe_load((sectioned.path / rel).read_text())
    data["declaration"].pop("sections")
    data["derived_from"] = outside
    data["expected"]["value"] = 1
    sectioned.write(rel, yaml.safe_dump(data, sort_keys=False))
    sectioned.commit("re-point at the edit commit and lower the bar")
    assert NO_COMMIT_PAIR in _weakened_reason(sectioned, marker)


def test_675_F1_blob_to_commit_anchor_move_cannot_launder_a_weakening(target, tmp_path):
    """A anchors on the file's content; B edits it (stale); C re-points at B's commit and lowers the bar."""
    marker = tmp_path / "ran"
    rel = _content_probe(target, argv=marker_argv(marker, "1"))
    target.write(DECL, "# Requirements\n\nExports 3 collections, edited.\n")
    edit = target.commit("edit the declaration")
    _rewrite(target, rel, derived_from=edit, expected_value=1)
    target.commit("re-point at the edit commit and lower the bar")
    assert NO_COMMIT_PAIR in _weakened_reason(target, marker)


@pytest.fixture
def sha256_sectioned(tmp_path) -> Target:
    path = tmp_path / "target"
    path.mkdir()
    res = subprocess.run(["git", "init", "-q", "--object-format=sha256", str(path)],
                         capture_output=True, text=True, check=False)
    if res.returncode != 0:
        pytest.skip(f"local git cannot create a SHA-256 repository: {res.stderr.strip()}")
    t = Target(path)
    assert t.git("rev-parse", "--show-object-format") == "sha256"
    t.write(DECL, SECTIONED)
    t.commit("declare")
    return t


def test_675_F2_section_anchor_works_in_a_sha256_repository(sha256_sectioned):
    """The scanner records section anchors in SHA-256 repositories: the runner must read their blobs."""
    git = ra.Git(sha256_sectioned.path)
    assert git.file_bytes("HEAD", DECL) == SECTIONED.encode()
    _section_probe(sha256_sectioned)
    _assert_clean(sha256_sectioned)
    _edit(sha256_sectioned, *OUTSIDE)
    sha256_sectioned.commit("edit another section")
    _assert_clean(sha256_sectioned)
    _edit(sha256_sectioned, *INSIDE)
    sha256_sectioned.commit("edit 3.1.1, inside 3.1")
    state, reason = _state(sha256_sectioned)
    assert state == ra.STATE_STALE and "heading 3.1 changed" in reason, reason


# --------------------------------------------------------------------------- #
# Migration gate (#686): reconfirm-and-migrate.md §Migration step 1
# --------------------------------------------------------------------------- #
def _tree_state(target: Target) -> tuple[str, dict[str, bytes]]:
    """Everything a write could touch: git status (ignored files too) and every file's bytes."""
    status = target.git("status", "--porcelain", "--ignored", "--untracked-files=all")
    files = {p.relative_to(target.path).as_posix(): p.read_bytes()
             for p in target.path.rglob("*") if p.is_file() and ".git" not in p.relative_to(target.path).parts}
    return status, files


def _check_migration(target: Target, capsys) -> tuple[int, str]:
    before = _tree_state(target)
    code = ra.main(["--repo", str(target.path), "--check-migration"])
    assert _tree_state(target) == before, "the migration check wrote to the target"
    return code, capsys.readouterr().out


def _approve_together(target: Target, *probes: dict) -> None:
    """Commit several probes in one commit, so the history walk can't pair one with another as a rename."""
    for probe in probes:
        target.write_probe(probe)
    target.commit("approve probes")


def test_686_stale_candidate_refuses_the_migration_with_the_reconfirm_route(target, capsys):
    _approve_together(target, make_probe("p1", derived_from=_blob(target)), make_probe("p2", derived_from=_blob(target)))
    target.write(DECL, "# Requirements\n\n## Export\n\nExports 4 collections.\n")
    target.commit("change the declaration")
    code, out = _check_migration(target, capsys)
    assert code == ra.EXIT_MIGRATION_REFUSED
    for pid in ("p1", "p2"):
        assert f"refused {pid}: {ra.STATE_STALE}: declaration changed since derivation: the content of {DECL}" in out
    assert "route: reconfirm it after the diff (references/reconfirm-and-migrate.md §Re-confirmation)" in out
    assert "migratable" not in out


def test_686_clean_candidates_are_listed_as_migratable(target, capsys):
    # A pre-v1.1 commit anchor (p2) is a candidate too.
    _approve_together(target, make_probe("p1", derived_from=_blob(target)),
                      make_probe("p2", derived_from=target.git("rev-parse", "HEAD")))
    target.write("README.md", "unrelated\n")
    target.commit("unrelated")
    code, out = _check_migration(target, capsys)
    assert code == ra.EXIT_OK, out
    assert "migratable p1\n" in out and "migratable p2\n" in out
    assert "refused" not in out


def test_686_weakened_candidate_is_refused_as_not_healable_in_place(target, capsys):
    rel = _content_probe(target)
    _weaken(target, rel)
    target.commit("lower the bar")
    code, out = _check_migration(target, capsys)
    assert code == ra.EXIT_MIGRATION_REFUSED
    assert f"refused p1: {ra.STATE_WEAKENED}: probe changed in" in out
    assert "not healable in place" in out and "that lists it in supersedes" in out


def test_686_one_stale_candidate_refuses_even_beside_a_clean_one(target, capsys):
    target.write("docs/other.md", "# Other\n")
    target.commit("another declaration")
    _approve_together(target, make_probe("p1", derived_from=_blob(target)),
                      make_probe("p2", derived_from=_blob(target, path="docs/other.md"), path="docs/other.md"))
    target.write(DECL, "# Requirements\n\nchanged\n")
    target.commit("change the first declaration")
    code, out = _check_migration(target, capsys)
    assert code == ra.EXIT_MIGRATION_REFUSED
    assert "refused p1: stale" in out and "p2" not in out


def test_686_unapproved_candidate_is_refused(target, capsys):
    _content_probe(target, approved=False)
    code, out = _check_migration(target, capsys)
    assert code == ra.EXIT_MIGRATION_REFUSED
    assert f"refused p1: {ra.REASON_NOT_APPROVED}:" in out


def test_686_section_anchored_and_non_markdown_probes_are_no_candidates(sectioned, capsys):
    """Both are stale here, so they would be refused if the gate selected them."""
    sectioned.write("docs/api.yaml", "paths: {}\n")
    sectioned.commit("declare an endpoint")
    sections = _sections_now(sectioned)
    on_sections = make_probe("p1", derived_from=ra.section_anchor(sections))
    on_sections["declaration"]["sections"] = sections
    on_yaml = make_probe("p2", derived_from=_blob(sectioned, path="docs/api.yaml"), path="docs/api.yaml")
    _approve_together(sectioned, on_sections, on_yaml)
    _edit(sectioned, *INSIDE)
    sectioned.write("docs/api.yaml", "paths: {/x: {}}\n")
    sectioned.commit("change both declarations")
    assert {_state(sectioned, pid)[0] for pid in ("p1", "p2")} == {ra.STATE_STALE}
    code, out = _check_migration(sectioned, capsys)
    assert code == ra.EXIT_OK, out
    assert "p1" not in out and "p2" not in out
    assert "0 candidate(s) migratable" in out


def test_686_candidate_that_is_also_a_manifest_entry_is_refused_as_run_refuses_it(target, capsys):
    """run reports the id as a contradiction (exit 4); the migration must not list it as migratable."""
    _content_probe(target)
    target.write(MANIFEST_REL, yaml.safe_dump({"entries": [manifest_entry("p1")]}, sort_keys=False))
    target.commit("list p1 as not constructible too")
    code, out = _check_migration(target, capsys)
    assert code == ra.EXIT_MIGRATION_REFUSED, out
    assert (f"refused p1: {ra.STATE_CONTRADICTION}: id is both the probe file project/reach-probes/p1.yml "
            "and a not-constructible manifest entry") in out
    assert "route: re-derive the entry" in out and "migratable" not in out


def test_686_unreadable_manifest_refuses_the_migration(target, capsys):
    _content_probe(target)
    target.write(MANIFEST_REL, "entries: [unclosed\n")
    target.commit("break the manifest")
    code, out = _check_migration(target, capsys)
    assert code == ra.EXIT_MIGRATION_REFUSED, out
    assert f"refused {MANIFEST_REL}: invalid manifest: not parseable as YAML" in out


@pytest.mark.parametrize("raw", [False, True])
def test_686_invalid_candidate_is_refused_as_run_flags_it(target, capsys, raw):
    """A schema-invalid probe on a .md declaration, or one that can't be parsed at all (fail closed)."""
    if raw:
        target.write("project/reach-probes/p1.yml", "id: p1\nderived_from: [unclosed\n")
    else:
        target.write_probe(make_probe(derived_from=_blob(target), verdict="reached"))
    target.commit("approve an invalid probe")
    code, out = _check_migration(target, capsys)
    assert code == ra.EXIT_MIGRATION_REFUSED, out
    assert f"refused p1: {ra.STATE_INVALID}: " in out and "route: re-derive the entry" in out
    if not raw:
        assert f"{ra.REASON_INVALID_PROBE}: <root>: Additional properties" in out


def test_686_invalid_probe_on_a_non_markdown_declaration_is_no_candidate(target, capsys):
    target.write("docs/api.yaml", "paths: {}\n")
    target.commit("declare an endpoint")
    target.write_probe(make_probe(derived_from=_blob(target, path="docs/api.yaml"), path="docs/api.yaml",
                                  verdict="reached"))
    target.commit("approve an invalid probe")
    code, out = _check_migration(target, capsys)
    assert code == ra.EXIT_OK, out
    assert "p1" not in out


def test_686_help_names_the_mode_and_its_exit_code():
    text = ra.build_parser().format_help()
    assert "--check-migration" in text and "6 --check-migration refused" in " ".join(text.split())


# --------------------------------------------------------------------------- #
# Supersede (#685): a recorded replacement of a weakened probe
# --------------------------------------------------------------------------- #
ROW_08 = ("Export on request", "Export within 7 days")   # the AK-OS-08 row
WIDE = (*LOCATORS, ("row", "AK-OS-08"))


def _weakened_rebaseline(target: Target, **kw) -> str:
    """The kamerplanter case: C2 widens the locators without a declaration change (a weakened
    re-baseline), C3 really changes AK-OS-08 and re-derives. The chain stays weakened."""
    rel = _section_probe(target, **kw)
    _reanchor(target, rel, locators=WIDE)
    target.commit("re-anchor onto AK-OS-08 without a declaration change")
    _edit(target, *ROW_08)
    _reanchor(target, rel)
    target.commit("change AK-OS-08 and re-derive")
    return rel


def test_685_re_derivation_after_a_real_change_on_a_weakened_chain_stays_weakened(sectioned):
    """AC1: documents the behaviour the chain rule keeps; supersede does not relax it."""
    _weakened_rebaseline(sectioned)
    reason = _weakened_reason(sectioned)
    assert reason.startswith("weakened: re-baselined without a declaration change: "), reason
    assert "but its previous derivation was no re-derivation either: " in reason
    assert reason.endswith(f"but the anchored sections of {DECL} did not change in between")


def test_685_a_new_id_beside_the_kept_weakened_file_starts_its_own_history_and_leaves_the_kept_one_weakened(
        sectioned):
    """Measured with git 2.43 and 2.53: --follow pairs a new file with a kept, similar one as a copy (#688).

    The copy starts its own history, so the new id is clean; the kept probe keeps
    its own finding, which only a supersede record clears.
    """
    _weakened_rebaseline(sectioned)
    sectioned.write_probe(_fresh(sectioned, "p1-rederived", WIDE))
    sectioned.commit("derive afresh under a new id, keep the weakened probe")
    log = ra.Git(sectioned.path).file_log("project/reach-probes/p1-rederived.yml")
    assert len(log) > 1 and log[0][2] == "C", "git no longer pairs the copy; revisit the copy cut"
    state, reason = _state(sectioned, "p1-rederived")
    assert state == ra.STATE_CLEAN, reason
    assert _state(sectioned)[0] == ra.STATE_WEAKENED
    code, _ = run_audit(sectioned)
    assert code == ra.EXIT_FINDINGS


def _replacement(target: Target, pid: str = "p2", supersedes=("p1",), commit: bool = True, locators=WIDE,
                 **kw) -> dict:
    """A fresh probe on the same entry, derived and approved under a new id, listing what it replaces."""
    probe = _fresh(target, pid, locators)
    probe["observe"]["argv"] = kw.pop("argv", probe["observe"]["argv"])
    probe.update(kw)
    probe["supersedes"] = list(supersedes)
    _digested(probe)
    target.write_probe(probe)
    if commit:
        target.commit(f"derive {pid} to supersede {', '.join(supersedes)}")
    return probe


def _superseded(target: Target, marker: Path | None = None) -> str:
    """Weakened p1 plus a clean, approved p2 superseding it; returns the report."""
    _weakened_rebaseline(target, argv=marker_argv(marker) if marker else None)
    _replacement(target)
    return run_audit(target)[1]


def test_685_AC2_a_superseded_probe_is_reported_superseded_and_not_executed(sectioned, tmp_path):
    marker = tmp_path / "p1-ran"
    _weakened_rebaseline(sectioned, argv=marker_argv(marker))
    _replacement(sectioned)
    # git pairs p2 with the kept p1 as a copy: the record must end p2's walk there.
    assert len(sectioned.git("log", "--follow", "--format=%H", "--", "project/reach-probes/p2.yml").splitlines()) > 1
    code, report = run_audit(sectioned)
    assert code == ra.EXIT_OK, report
    old, new = row_of(report, "p1"), row_of(report, "p2")
    assert old[1] == ra.NOT_PROBED and old[5] == "not executed" and old[7] == ra.STATE_SUPERSEDED, old
    assert _plain(old[9]).startswith("superseded by p2; it was weakened: re-baselined without a declaration change")
    assert not marker.exists()
    assert new[1] == ra.REACHED and new[7] == ra.STATE_CLEAN, new
    assert f"- {ra.PROVENANCE_SUPERSEDED}: 1 (p1)." in report
    assert "## Findings\n\n- none\n" in report


def test_685_AC2_the_replacement_is_judged_on_its_own_later_history(sectioned, tmp_path):
    """After the supersede, lowering p2's bar weakens p2, and p1 is weakened again."""
    _superseded(sectioned)
    _rewrite(sectioned, "project/reach-probes/p2.yml", expected_value=1)
    sectioned.commit("lower p2's bar")
    code, report = run_audit(sectioned)
    assert code == ra.EXIT_FINDINGS
    assert row_of(report, "p2")[7] == ra.STATE_WEAKENED
    old = row_of(report, "p1")
    assert old[7] == ra.STATE_WEAKENED and "supersede by p2 not in effect: it is weakened" in _plain(old[9]), old


def test_685_AC2_renaming_the_replacement_keeps_its_own_weakening(sectioned):
    """The cut drops only the superseded probe's revisions, not the replacement's under an earlier name."""
    _superseded(sectioned)
    _rewrite(sectioned, "project/reach-probes/p2.yml", expected_value=1)
    sectioned.commit("lower p2's bar")
    sectioned.git("mv", "project/reach-probes/p2.yml", "project/reach-probes/p2-renamed.yml")
    sectioned.commit("rename p2's file")
    _, report = run_audit(sectioned)
    assert row_of(report, "p2")[7] == ra.STATE_WEAKENED
    assert row_of(report, "p1")[7] == ra.STATE_WEAKENED


@pytest.mark.parametrize("how, state", [
    ("unapproved", ra.REASON_NOT_APPROVED),
    ("digest", ra.STATE_APPROVAL_MISMATCH),
    ("anchor", ra.STATE_UNRESOLVED),
    ("stale", ra.STATE_STALE),
])
def test_685_AC3_a_replacement_that_does_not_run_as_approved_supersedes_nothing(sectioned, tmp_path, how, state):
    """Own approval and own anchor: without both, p1 stays a weakened finding."""
    marker = tmp_path / "p1-ran"
    _weakened_rebaseline(sectioned, argv=marker_argv(marker))
    probe = _replacement(sectioned, commit=False)
    if how == "unapproved":
        probe.pop("approval")
    elif how == "digest":
        probe["approval"]["observation_digest"] = "0" * 64
    elif how == "anchor":
        probe["derived_from"] = "sections:" + "0" * 64
    sectioned.write_probe(probe)
    sectioned.commit("derive p2")
    if how == "stale":
        _edit(sectioned, *IN_ROW)
        sectioned.commit("change AK-OS-07")
    code, report = run_audit(sectioned)
    assert code == ra.EXIT_FINDINGS
    old = row_of(report, "p1")
    assert old[7] == ra.STATE_WEAKENED and f"supersede by p2 not in effect: it is {state}" in _plain(old[9]), old
    assert not marker.exists()
    # The record took no effect, so p2 keeps its uncut verdict (SEC-002): its own history, which starts at
    # the commit that created it as a copy of p1 (#688).
    assert row_of(report, "p2")[7] == (ra.STATE_CLEAN if how == "unapproved" else state)


def test_685_AC3_deleting_the_replacement_leaves_the_superseded_probe_weakened(sectioned):
    _superseded(sectioned)
    (sectioned.path / "project/reach-probes/p2.yml").unlink()
    sectioned.commit("drop p2")
    _weakened_reason(sectioned)


def test_685_AC3_adding_the_record_to_an_approved_probe_later_weakens_that_probe(sectioned):
    _weakened_rebaseline(sectioned)
    probe = _fresh(sectioned, "p2", WIDE)
    sectioned.write_probe(probe)
    sectioned.commit("derive p2 without a record")
    sectioned.write_probe(probe | {"supersedes": ["p1"]})
    sectioned.commit("add the record afterwards")
    _, report = run_audit(sectioned)
    assert row_of(report, "p2")[7] == ra.STATE_WEAKENED
    assert "supersede by p2 not in effect: it is weakened" in _plain(row_of(report, "p1")[9])


def _supersede_finding(report: str, pid: str) -> str:
    found = [ln for ln in report.splitlines() if ln.startswith(f"- **{ra.FINDING_SUPERSEDE}** `{pid}`")]
    assert len(found) == 1, report
    return _plain(found[0])


def test_685_a_probe_that_is_not_weakened_cannot_be_superseded(sectioned, tmp_path):
    """The laundering the record must not allow: hiding a healthy probe behind a new one."""
    marker = tmp_path / "p1-ran"
    _section_probe(sectioned, argv=marker_argv(marker))
    _replacement(sectioned, locators=LOCATORS)
    code, report = run_audit(sectioned)
    assert code == ra.EXIT_FINDINGS
    assert "supersedes p1, which is clean, not weakened" in _supersede_finding(report, "p2")
    assert row_of(report, "p1")[1] == ra.REACHED and marker.exists()
    # A record that takes no effect never changes p2's verdict (SEC-002): p2 keeps its uncut history,
    # which starts at the commit that created it as a copy of p1 (#688), and so runs as a probe of its own.
    assert row_of(report, "p2")[7] == ra.STATE_CLEAN and row_of(report, "p2")[1] == ra.REACHED


def test_685_self_supersede_is_a_finding(sectioned):
    _replacement(sectioned, supersedes=("p2",))
    code, report = run_audit(sectioned)
    assert code == ra.EXIT_FINDINGS
    assert "supersedes lists the probe's own id" in _supersede_finding(report, "p2")


def test_685_a_cycle_is_a_finding_for_every_record_in_it(sectioned):
    a = _replacement(sectioned, "p2", supersedes=("p3",), commit=False)
    b = _replacement(sectioned, "p3", supersedes=("p2",), commit=False)
    _approve_together(sectioned, a, b)
    code, report = run_audit(sectioned)
    assert code == ra.EXIT_FINDINGS
    for pid, other in (("p2", "p3"), ("p3", "p2")):
        assert f"supersedes {other}, which leads back to it through supersedes (a cycle)" in _supersede_finding(report, pid)


@pytest.mark.parametrize("target_id, what", [
    ("p9", "no valid probe file"),
    ("nc1", "a not-constructible manifest entry"),
])
def test_685_a_record_without_a_probe_to_supersede_is_a_finding(sectioned, target_id, what):
    sectioned.write(MANIFEST_REL, yaml.safe_dump({"entries": [manifest_entry("nc1")]}, sort_keys=False))
    probe = _fresh(sectioned, "p2", WIDE) | {"supersedes": [target_id]}
    sectioned.write_probe(probe, name="p2‮")
    sectioned.commit("derive p2")
    code, report = run_audit(sectioned)
    assert code == ra.EXIT_FINDINGS
    line = _supersede_finding(report, "p2")
    assert f"supersedes {target_id}, which is {what} under project/reach-probes/" in line
    assert "‮" not in report


def test_685_a_replacement_on_another_declaration_entry_is_a_finding(sectioned):
    _weakened_rebaseline(sectioned)
    probe = _fresh(sectioned, "p2", WIDE)
    probe["declaration"]["location"] = "§Rules"
    sectioned.write_probe(probe | {"supersedes": ["p1"]})
    sectioned.commit("derive p2 on another entry")
    code, report = run_audit(sectioned)
    assert code == ra.EXIT_FINDINGS
    assert "which declares another entry" in _supersede_finding(report, "p2")
    assert row_of(report, "p1")[7] == ra.STATE_WEAKENED


def test_685_schema_admits_supersedes_and_rejects_a_malformed_one():
    assert validate(_valid() | {"supersedes": ["p0", "p0-old"]}) == []
    for bad in ([], ["p0", "p0"], ["P0"], "p0", [""]):
        assert validate(_valid() | {"supersedes": bad}), bad


def test_685_every_v1_2_example_stays_valid():
    for example in yaml.safe_load(V12_SCHEMA_PATH.read_text())["examples"]:
        assert validate(example) == []


def _file_anchored_weakened(target: Target) -> None:
    rel = _content_probe(target)
    _weaken(target, rel)
    target.commit("lower the bar")


def test_685_migration_skips_a_superseded_probe_and_judges_the_replacement(target, capsys):
    _file_anchored_weakened(target)
    target.write_probe(_digested(make_probe("p2", derived_from=_blob(target), supersedes=["p1"])))
    target.commit("derive p2 to supersede p1")
    code, out = _check_migration(target, capsys)
    assert code == ra.EXIT_OK, out
    assert "migratable p2\n" in out and "p1" not in out.replace("p2", "")


def test_685_migration_refuses_a_candidate_with_an_invalid_record(target, capsys):
    _content_probe(target)
    target.write_probe(make_probe("p2", derived_from=_blob(target), supersedes=["p1"]))
    target.commit("derive p2 to supersede a clean p1")
    code, out = _check_migration(target, capsys)
    assert code == ra.EXIT_MIGRATION_REFUSED, out
    assert f"refused p2: {ra.FINDING_SUPERSEDE}: supersedes p1, which is clean, not weakened" in out
    assert "migratable p1\n" in out or "refused p1" not in out


# --------------------------------------------------------------------------- #
# Pre-merge security review of the supersede record (SEC-001 to SEC-004)
# --------------------------------------------------------------------------- #
H_REL = "project/reach-probes/h.yml"


def _digested(probe: dict) -> dict:
    probe["approval"]["observation_digest"] = ra.observation_digest(probe)
    return probe


def _approved_h(target: Target, marker: Path) -> dict:
    """c1: probe h, approved with a matching digest, clean."""
    probe = _digested(make_probe("h", derived_from=_blob(target), argv=marker_argv(marker, "1")))
    target.write_probe(probe)
    target.commit("approve h")
    return probe


def _h_verdict(target: Target, marker: Path) -> tuple[int, list[str], str]:
    code, report = run_audit(target)
    return code, row_of(report, "h"), report


def test_685_SEC001_A_a_copy_of_the_claimant_cannot_cut_away_its_own_history(target, tmp_path):
    """One commit lowers h's bar, adds supersedes, and adds h-old as a copy of h's approved text."""
    marker = tmp_path / "h-ran"
    approved = _approved_h(target, marker)
    _rewrite(target, H_REL, expected_value=1, supersedes=["h-old"])
    target.write_probe(dict(approved, id="h-old"))
    target.commit("lower h's bar, supersede a copy of it")
    code, row, report = _h_verdict(target, marker)
    assert row[7] == ra.STATE_WEAKENED, row[7:]
    assert code == ra.EXIT_FINDINGS and not marker.exists()
    assert row_of(report, "h-old")[7] == ra.STATE_WEAKENED
    assert "descends from" in _supersede_finding(report, "h")


def test_685_SEC001_A_the_migration_gate_refuses_it_too(target, tmp_path, capsys):
    approved = _approved_h(target, tmp_path / "h-ran")
    _rewrite(target, H_REL, expected_value=1, supersedes=["h-old"])
    target.write_probe(dict(approved, id="h-old"))
    target.commit("lower h's bar, supersede a copy of it")
    code, out = _check_migration(target, capsys)
    assert code == ra.EXIT_MIGRATION_REFUSED, out
    assert "migratable h\n" not in out


@pytest.mark.parametrize("summary_words", [8, 400])
def test_685_SEC001_B_a_probe_at_the_claimants_earlier_path_cannot_cut_its_history(target, tmp_path, summary_words):
    """c2 renames h and lowers its bar with supersedes; c3 adds h-old at h's old path.

    Measured: with a short summary git pairs h-old with h2 as a copy, so h-old's
    history holds h2's newest revision; with a long one h-old is dissimilar,
    and --follow walks the reused path back into h's revision at c1.
    """
    marker = tmp_path / "h-ran"
    _approved_h(target, marker)
    target.git("mv", H_REL, "project/reach-probes/h2.yml")
    _rewrite(target, "project/reach-probes/h2.yml", expected_value=1, supersedes=["h-old"])
    renamed = target.commit("rename h, lower its bar")
    other = make_probe("h-old", derived_from=_blob(target), tier="T1",
                       summary=" ".join(f"unrelated{i}" for i in range(summary_words)),
                       argv=[PY, "-c", "print('different observation step entirely')"])
    target.write(H_REL, yaml.safe_dump(other, sort_keys=False))
    target.commit("add h-old at h's old path")
    follow = ra.Git(target.path).file_history(H_REL)
    paired_with_h2 = (renamed, "project/reach-probes/h2.yml") in follow
    assert paired_with_h2 == (summary_words == 8), follow
    code, row, report = _h_verdict(target, marker)
    assert row[7] == ra.STATE_WEAKENED, row[7:]
    assert code == ra.EXIT_FINDINGS and not marker.exists()
    assert row_of(report, "h-old")[7] != ra.STATE_SUPERSEDED


def test_685_SEC001_a_target_that_once_held_the_claimants_path_is_refused(target):
    """Fail closed on path reuse: w once lived at the path r is created at, so the walk can't tell them apart."""
    w = _digested(make_probe("w", derived_from=_blob(target)))
    target.write("project/reach-probes/r.yml", yaml.safe_dump(w, sort_keys=False))
    target.commit("approve w under r.yml")
    target.git("mv", "project/reach-probes/r.yml", "project/reach-probes/w.yml")
    _rewrite(target, "project/reach-probes/w.yml", expected_value=1)
    target.commit("move w away and lower its bar")
    target.write("project/reach-probes/r.yml",
                 yaml.safe_dump(_digested(make_probe("r", derived_from=_blob(target), supersedes=["w"])),
                                sort_keys=False))
    target.commit("derive r at w's old path")
    _, report = run_audit(target)
    assert "descends from this probe or sits on its earlier path" in _supersede_finding(report, "r")
    assert row_of(report, "w")[7] == ra.STATE_WEAKENED


def test_685_SEC002_a_dropped_record_does_not_change_the_claimants_verdict(target, tmp_path):
    """Scenario A, but h-old declares another entry: the record is a finding, and h is weakened."""
    marker = tmp_path / "h-ran"
    approved = _approved_h(target, marker)
    _rewrite(target, H_REL, expected_value=1, supersedes=["h-old"])
    elsewhere = copy.deepcopy(approved) | {"id": "h-old"}
    elsewhere["declaration"]["location"] = "§Elsewhere"
    target.write_probe(elsewhere)
    target.commit("lower h's bar, supersede a copy of it on another entry")
    code, row, report = _h_verdict(target, marker)
    assert row[7] == ra.STATE_WEAKENED, row[7:]
    assert code == ra.EXIT_FINDINGS and not marker.exists()
    assert "declares another entry" in _supersede_finding(report, "h")


def test_685_SEC002_a_claimant_whose_newest_revision_lies_in_the_target_reads_weakened(target, tmp_path):
    """c2 lowers h's bar with supersedes; c3 copies h to h-old without touching h."""
    marker = tmp_path / "h-ran"
    _approved_h(target, marker)
    data = _rewrite(target, H_REL, expected_value=1, supersedes=["h-old"])
    target.commit("lower h's bar")
    target.write_probe({k: v for k, v in data.items() if k != "supersedes"} | {"id": "h-old"})
    target.commit("copy h to h-old")
    code, row, report = _h_verdict(target, marker)
    assert row[7] == ra.STATE_WEAKENED, row[7:]
    assert code == ra.EXIT_FINDINGS and row[5] == "not executed", row
    # h-old, a copy of h made after h's change, starts its own history there (#688); the marker is
    # shared, so it shows h-old ran, not h.
    assert row_of(report, "h-old")[7] == ra.STATE_CLEAN


def test_685_SEC003_a_replacement_without_an_observation_digest_supersedes_nothing(sectioned):
    _weakened_rebaseline(sectioned)
    probe = _replacement(sectioned, commit=False)
    probe["approval"].pop("observation_digest")
    sectioned.write_probe(probe)
    sectioned.commit("derive p2 without a digest")
    _, report = run_audit(sectioned)
    old = row_of(report, "p1")
    assert old[7] == ra.STATE_WEAKENED
    assert "supersede by p2 not in effect: its approval carries no observation digest" in _plain(old[9]), old


def test_685_SEC004_a_replacement_on_another_declaration_file_is_a_finding(sectioned):
    sectioned.write("docs/other.md", SECTIONED)
    sectioned.commit("another declaration file with the same sections")
    _weakened_rebaseline(sectioned)
    probe = _fresh(sectioned, "p2", WIDE)
    probe["declaration"]["path"] = "docs/other.md"
    probe["declaration"]["sections"] = _sections_now(sectioned, WIDE, "docs/other.md")
    probe["derived_from"] = ra.section_anchor(probe["declaration"]["sections"])
    sectioned.write_probe(_digested(probe | {"supersedes": ["p1"]}))
    sectioned.commit("derive p2 on another file")
    _, report = run_audit(sectioned)
    assert "which declares another entry" in _supersede_finding(report, "p2")
    assert row_of(report, "p1")[7] == ra.STATE_WEAKENED


# --------------------------------------------------------------------------- #
# Second security review of the supersede record (SEC-101 to SEC-103)
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("summary_words", [8, 400])
def test_685_SEC101_rename_and_path_reuse_in_one_commit_cannot_cut_the_claimants_history(
        target, tmp_path, capsys, summary_words):
    """c2 renames h to h2, lowers its bar, adds supersedes, and writes h-old at h's old path."""
    marker = tmp_path / "h-ran"
    _approved_h(target, marker)
    target.git("mv", H_REL, "project/reach-probes/h2.yml")
    _rewrite(target, "project/reach-probes/h2.yml", expected_value=1, supersedes=["h-old"])
    other = make_probe("h-old", derived_from=_blob(target),
                       summary=" ".join(f"unrelated{i}" for i in range(summary_words)))
    target.write(H_REL, yaml.safe_dump(other, sort_keys=False))
    target.commit("rename h, lower its bar, reuse its path for h-old")
    code, row, report = _h_verdict(target, marker)
    assert row[7] != ra.STATE_CLEAN and not marker.exists(), row[7:]
    assert code == ra.EXIT_FINDINGS
    assert row_of(report, "h-old")[7] != ra.STATE_SUPERSEDED
    code, out = _check_migration(target, capsys)
    assert "migratable h\n" not in out


def test_685_SEC102_a_reconfirmed_approval_supersedes_nothing(sectioned):
    _weakened_rebaseline(sectioned)
    probe = _replacement(sectioned, commit=False)
    probe["approval"]["mode"] = ra.MODE_RECONFIRMED
    sectioned.write_probe(probe)
    sectioned.commit("derive p2 under a re-confirmed approval")
    _, report = run_audit(sectioned)
    assert "approval.mode reconfirmed" in _supersede_finding(report, "p2")
    assert row_of(report, "p1")[7] == ra.STATE_WEAKENED


def test_685_SEC102_a_replacement_moved_to_T2_supersedes_nothing(sectioned):
    """T2 is the one tier a default run withholds, so moving there drops the entry from the default audit."""
    _weakened_rebaseline(sectioned)
    probe = _replacement(sectioned, commit=False, tier="T2")
    sectioned.write_probe(_digested(probe))
    sectioned.commit("derive p2 at T2")
    _, report = run_audit(sectioned)
    assert "tier T2, but p1 is T0" in _supersede_finding(report, "p2")
    assert row_of(report, "p1")[7] == ra.STATE_WEAKENED


def test_685_SEC102_an_effective_supersede_shows_both_expectations_and_tiers(sectioned):
    _weakened_rebaseline(sectioned)
    _replacement(sectioned, expected={"kind": "count", "value": 2, "unit": "collections"})
    code, report = run_audit(sectioned)
    assert code == ra.EXIT_OK, report
    assert ("- Supersede p1 by p2: now expected count 2 `collections`, tier T0; before expected count 3 "
            "`collections`, tier T0; the replacement's approval is the only check of this change.") in report


def test_685_SEC102_the_schema_example_does_not_combine_supersedes_with_a_re_confirmation():
    for example in yaml.safe_load(SCHEMA_PATH.read_text())["examples"]:
        if "supersedes" in example:
            assert example.get("approval", {}).get("mode", "derived") == "derived", example


class _NoHistory:
    """A Git stand-in for the graph part of resolve_supersedes: no file has history."""

    def file_history(self, path):
        return []


def _graph(n: int, targets) -> list:
    probes = []
    for i in range(n):
        data = make_probe(f"n{i}", derived_from="x")
        if targets(i):
            data["supersedes"] = list(targets(i))
        probes.append(ra.Probe(f"project/reach-probes/n{i}.yml", data))
    return probes


@pytest.mark.parametrize("n, targets", [
    (1000, lambda i: [f"n{i + 1}"] if i + 1 < 1000 else []),                 # a long chain
    (100, lambda i: [f"n{(i + k) % 100}" for k in range(1, ra.MAX_SUPERSEDES + 1)]),  # dense, cyclic
])
def test_685_SEC103_a_long_chain_and_a_dense_graph_resolve_without_recursion_or_stalling(monkeypatch, n, targets):
    probes = _graph(n, targets)
    monkeypatch.setattr(ra, "detect_change", lambda *a, **k: ra.ChangeState(ra.STATE_WEAKENED, "w"))
    started = time.monotonic()
    result = ra.resolve_supersedes(Path("."), _NoHistory(), probes, set(), yaml)
    assert time.monotonic() - started < 10
    assert len(result.changes) == n


def test_685_SEC103_schema_caps_supersedes():
    assert validate(_valid() | {"supersedes": [f"p{i}" for i in range(ra.MAX_SUPERSEDES)]}) == []
    assert validate(_valid() | {"supersedes": [f"p{i}" for i in range(ra.MAX_SUPERSEDES + 1)]})


def test_685_SEC101_a_replacement_created_in_a_merge_commit_is_judged_without_a_cut(sectioned):
    """Measured (git 2.43, 2.53): `git log --follow` lists no commit for a file a merge commit adds, so p2
    has no history, reads uncommitted, and supersedes nothing; the merge can't serve as a creating commit.
    Git 2.56 follows p2 into p1 by copy detection on the merge; file_history's --no-merges keeps it empty."""
    _weakened_rebaseline(sectioned)
    sectioned.git("checkout", "-q", "-b", "side")
    sectioned.write("README.md", "side\n")
    sectioned.commit("side")
    sectioned.git("checkout", "-q", "main")
    sectioned.write("NOTES.md", "main\n")
    sectioned.commit("main")
    sectioned.git("merge", "-q", "--no-commit", "--no-ff", "side")
    _replacement(sectioned, commit=False)
    sectioned.git("add", "-A")
    sectioned.git("commit", "-q", "-m", "merge side and add p2 in the merge")
    follow = ra.Git(sectioned.path).file_history("project/reach-probes/p2.yml")
    assert follow == [], follow
    code, report = run_audit(sectioned)
    # Since #709 (K3) a probe created in a merge reads weakened, not uncommitted: it is committed.
    assert code == ra.EXIT_FINDINGS and row_of(report, "p2")[7] == ra.STATE_WEAKENED
    old = row_of(report, "p1")
    assert old[7] == ra.STATE_WEAKENED and "supersede by p2 not in effect: it is weakened" in _plain(old[9])


def test_685_SEC101_a_claimant_renamed_and_re_id_d_over_a_rewritten_path_is_refused(target, tmp_path):
    """SEC-101 with a new id for the claimant too: no cut revision carries its id, but h.yml is rewritten
    in the creating commit, so h2 is no copy of an untouched h-old."""
    marker = tmp_path / "h-ran"
    _approved_h(target, marker)
    target.git("mv", H_REL, "project/reach-probes/h2.yml")
    _rewrite(target, "project/reach-probes/h2.yml", id="h2", expected_value=1, supersedes=["h-old"])
    target.write(H_REL, yaml.safe_dump(make_probe("h-old", derived_from=_blob(target)), sort_keys=False))
    target.commit("rename h to h2 under a new id, reuse its path for h-old")
    _, report = run_audit(target)
    assert "descends from this probe or sits on its earlier path" in _supersede_finding(report, "h2")
    assert row_of(report, "h2")[7] != ra.STATE_CLEAN and not marker.exists()


def test_685_SEC101_a_claimant_taking_the_id_the_target_once_had_is_refused(target, tmp_path):
    """h-old was h until c2; c3 copies it, untouched, to h2.yml under the id h: the cut would reach h's revisions."""
    marker = tmp_path / "h-ran"
    _approved_h(target, marker)
    _rewrite(target, H_REL, id="h-old")
    target.commit("rename the id of h to h-old")
    data = _digested(yaml.safe_load((target.path / H_REL).read_text()) | {"id": "h", "supersedes": ["h-old"]})
    target.write("project/reach-probes/h2.yml", yaml.safe_dump(data, sort_keys=False))
    target.commit("derive h again as a copy, superseding h-old")
    _, report = run_audit(target)
    assert "descends from this probe or sits on its earlier path" in _supersede_finding(report, "h")
    assert row_of(report, "h-old")[7] == ra.STATE_WEAKENED


# --------------------------------------------------------------------------- #
# Third security review of the supersede record (SEC-201 to SEC-205)
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("kind", ["duplicate", "symlink", "unparseable", "schema-invalid"])
def test_685_SEC201_a_second_file_under_a_superseded_id_keeps_its_own_finding(sectioned, tmp_path, kind):
    _superseded(sectioned)
    if kind == "duplicate":
        sectioned.write_probe(_fresh(sectioned, "p1", WIDE), name="p1-copy")
    elif kind == "symlink":
        (sectioned.path / "project/reach-probes/p1.yaml").symlink_to(tmp_path)
    elif kind == "unparseable":
        sectioned.write("project/reach-probes/p1.yaml", "id: p1\nderived_from: [unclosed\n")
    else:
        sectioned.write_probe(_fresh(sectioned, "p1", WIDE) | {"verdict": "reached"}, name="p1-copy")
    sectioned.commit(f"add a {kind} file under the id p1")
    code, report = run_audit(sectioned)
    assert code == ra.EXIT_FINDINGS, report
    assert f"- {ra.PROVENANCE_SUPERSEDED}: 1 (p1)." in report
    rows = [ln for ln in report.splitlines() if ln.startswith("| p1 |")]
    assert sorted(r.split(" | ")[7] for r in rows) == sorted([ra.STATE_SUPERSEDED, ra.STATE_INVALID]), rows
    assert "- **invalid probe** `p1`" in report


def test_685_SEC201_the_migration_gate_refuses_a_second_file_under_a_superseded_id(target, capsys):
    _file_anchored_weakened(target)
    target.write_probe(_digested(make_probe("p2", derived_from=_blob(target), supersedes=["p1"])))
    target.write("project/reach-probes/p1.yaml", "id: p1\nderived_from: [unclosed\n")
    target.commit("derive p2 to supersede p1, add an unparseable p1.yaml")
    code, out = _check_migration(target, capsys)
    assert code == ra.EXIT_MIGRATION_REFUSED, out
    assert f"refused p1: {ra.STATE_INVALID}: " in out


def test_685_SEC202_a_replacement_on_another_hub_is_a_finding(target):
    _spec_config(target, ("nolte-shared", "v0.1.8"), ("other-hub", "v2.0.0"))
    _inherited_probe(target, "v0.1.8", hub="nolte-shared")
    target.commit("approve p1 on nolte-shared")
    _weaken(target, "project/reach-probes/p1.yml")
    target.commit("lower p1's bar")
    probe = make_probe("p2", derived_from="v2.0.0", path=None, supersedes=["p1"])
    probe["declaration"] |= {"inherited_spec": "project/rest-api-design", "hub": "other-hub"}
    target.write_probe(_digested(probe))
    target.commit("derive p2 on other-hub")
    _, report = run_audit(target)
    assert "which declares another entry" in _supersede_finding(report, "p2")
    assert row_of(report, "p1")[7] == ra.STATE_WEAKENED


PATHS_50 = [f"src/module_{i:02d}/a/rather/long/path/to/the/collection/file.py" for i in range(50)]


def test_685_SEC203_the_supersede_line_never_loses_the_new_side_to_a_long_old_side(sectioned):
    _weakened_rebaseline(sectioned, expected={"kind": "set", "values": PATHS_50, "unit": "paths"})
    _replacement(sectioned, expected={"kind": "count", "value": 1, "unit": "paths"})
    code, report = run_audit(sectioned)
    assert code == ra.EXIT_OK, report
    line = next(ln for ln in report.splitlines() if ln.startswith("- Supersede p1 by p2:"))
    assert "now expected count 1 `paths`, tier T0" in line, line
    assert "before expected set of 50 `paths`, tier T0" in line, line
    assert "… and 40 more (shortened)" in line and line.endswith("the only check of this change."), line
    assert f"`{PATHS_50[0]}`" in line and f"`{PATHS_50[9]}`" in line and PATHS_50[10] not in line


def test_685_SEC203_a_set_replacement_shows_added_and_removed_members(sectioned):
    _weakened_rebaseline(sectioned, expected={"kind": "set", "values": ["a, b", "c"], "unit": "names"})
    _replacement(sectioned, expected={"kind": "set", "values": ["c", "d"], "unit": "names"})
    _, report = run_audit(sectioned)
    line = next(ln for ln in report.splitlines() if ln.startswith("- Supersede p1 by p2:"))
    assert "members added: `d`; removed: `a, b`" in line, line


def test_685_SEC204_a_claimant_that_is_also_a_manifest_entry_supersedes_nothing(sectioned):
    _superseded(sectioned)
    sectioned.write(MANIFEST_REL, yaml.safe_dump({"entries": [manifest_entry("p2")]}, sort_keys=False))
    sectioned.commit("list p2 as not constructible too")
    code, report = run_audit(sectioned)
    assert code == ra.EXIT_FINDINGS
    old = row_of(report, "p1")
    assert old[7] == ra.STATE_WEAKENED and "supersede by p2 not in effect: it is a contradiction" in _plain(old[9])
    assert "- Supersede p1 by p2" not in report


def test_685_SEC204_a_target_that_is_also_a_manifest_entry_gets_no_supersede_line(sectioned):
    _superseded(sectioned)
    sectioned.write(MANIFEST_REL, yaml.safe_dump({"entries": [manifest_entry("p1")]}, sort_keys=False))
    sectioned.commit("list p1 as not constructible too")
    code, report = run_audit(sectioned)
    assert code == ra.EXIT_FINDINGS and row_of(report, "p1")[7] == ra.STATE_CONTRADICTION
    assert "- Supersede p1 by p2" not in report


def test_685_SEC205_a_superseded_row_keeps_the_notes_of_unmet_records(sectioned):
    _superseded(sectioned)
    probe = _replacement(sectioned, "p3", commit=False)
    probe.pop("approval")
    sectioned.write_probe(probe)
    sectioned.commit("derive p3 without approval")
    _, report = run_audit(sectioned)
    old = row_of(report, "p1")
    assert old[7] == ra.STATE_SUPERSEDED
    assert "supersede by p3 not in effect: it is not approved" in _plain(old[9]), old


# --------------------------------------------------------------------------- #
# #701: a probe changed inside a merge commit (an "evil merge")
# --------------------------------------------------------------------------- #
# file_history() walks `--follow --no-merges`, which never lists a merge whose
# result differs from every parent. Each test pairs the merge with what the
# runner says about the same change made in a plain commit at the same place.
BAR_OF_TWO = {"kind": "count", "value": 2, "unit": "collections"}


def _probe_observing_one(target: Target, marker: Path, **kw) -> tuple[str, str]:
    """An approved p1 under a content anchor that observes 1 against a bar of 2: lowering the bar clears it."""
    rel = _content_probe(target, argv=marker_argv(marker, "1"), expected=dict(BAR_OF_TWO), **kw)
    return rel, target.git("rev-parse", "HEAD")


def _merge_side(target: Target, branch: str = "side", *, on_side=None, in_merge=None) -> tuple[str, str]:
    """Merge ``branch`` into main with --no-ff; ``on_side`` edits on the branch, ``in_merge`` the merge result.

    Both lines carry an unrelated commit, so the merge is a real one. Returns
    ``(side commit, merge commit)``.
    """
    target.git("checkout", "-q", "-b", branch)
    target.write(f"{branch}.txt", f"{branch}\n")
    if on_side:
        on_side()
    side = target.commit(f"{branch} work")
    target.git("checkout", "-q", "main")
    target.write(f"main-beside-{branch}.txt", "main\n")
    target.commit(f"main work beside {branch}")
    target.git("merge", "-q", "--no-ff", "--no-commit", branch)
    if in_merge:
        in_merge()
    merge = target.commit(f"merge {branch}")
    assert target.git("rev-list", "--parents", "-n", "1", merge).count(" ") == 2
    return side, merge


def test_701_a_bar_lowered_inside_a_merge_after_approval_is_weakened(target, tmp_path):
    """AC (a): measured before the fix as clean, exit 0, executed."""
    marker = tmp_path / "ran"
    rel, recorded = _probe_observing_one(target, marker)
    _, merge = _merge_side(target, in_merge=lambda: _rewrite(target, rel, expected_value=1))
    assert ra.Git(target.path).file_history(rel) == [(recorded, rel)]
    reason = _weakened_reason(target, marker)
    assert reason == (f"weakened: probe changed in merge {merge[:12]} after its derivation was recorded in "
                      f"{recorded[:12]}"), reason


def test_701_a_merge_after_approval_that_leaves_the_probe_alone_stays_clean(target, tmp_path):
    """AC (b)."""
    marker = tmp_path / "ran"
    rel = _content_probe(target, argv=marker_argv(marker))
    _merge_side(target)
    _merge_side(target, "docs", on_side=lambda: target.write("README.md", "docs\n"))
    assert ra.Git(target.path).merges_changing(target.git("rev-list", "--max-parents=0", "HEAD"), "HEAD", rel) == []
    _assert_clean(target)
    assert marker.exists()


def test_701_a_side_branch_probe_edit_merged_without_conflict_reads_as_before(target, tmp_path):
    """AC (c): the merge takes the side's version, so the side commit alone is the change, named once."""
    marker = tmp_path / "ran"
    rel, recorded = _probe_observing_one(target, marker)
    side, merge = _merge_side(target, on_side=lambda: _rewrite(target, rel, expected_value=1))
    assert ra.Git(target.path).merges_changing(recorded, "HEAD", rel) == []
    reason = _weakened_reason(target, marker)
    assert reason == f"weakened: probe changed in {side[:12]} after its derivation was recorded in {recorded[:12]}"
    assert merge[:12] not in reason


def test_701_two_clean_edits_combined_by_a_merge_name_the_merge_too(target, tmp_path):
    """Both lines edit the probe on different lines and git merges them cleanly: the result is
    neither side's approved text, so the merge is named beside both edits."""
    marker = tmp_path / "ran"
    rel, recorded = _probe_observing_one(target, marker)

    def on_main() -> None:
        _rewrite(target, rel, tier="T1")

    target.git("checkout", "-q", "-b", "side")
    _rewrite(target, rel, expected_value=1)
    side = target.commit("lower the bar on side")
    target.git("checkout", "-q", "main")
    on_main()
    main = target.commit("move to T1 on main")
    target.git("merge", "-q", "--no-ff", "--no-edit", "side")
    merge = target.git("rev-parse", "HEAD")
    reason = _weakened_reason(target, marker)
    assert f"merge {merge[:12]}" in reason and side[:12] in reason and main[:12] in reason, reason


def test_701_a_weakening_in_a_merge_is_not_adopted_by_a_later_re_derivation(target, tmp_path):
    """AC (d), the Critical case: R approves, a merge lowers the bar, M changes the declaration and
    re-derives. Measured before the fix as clean, exit 0, executed: M absorbed the merge."""
    marker = tmp_path / "ran"
    rel, recorded = _probe_observing_one(target, marker)
    _, merge = _merge_side(target, in_merge=lambda: _rewrite(target, rel, expected_value=1))
    target.write(DECL, "# Requirements\n\n## Export\n\nExports 3 collections, reworded.\n")
    _rewrite(target, rel, derived_from="blob:" + target.git("hash-object", DECL))
    moved = target.commit("edit the declaration and re-derive")
    reason = _weakened_reason(target, marker)
    assert f"re-baselined without a declaration change: {moved[:12]} moved derived_from" in reason
    assert (f"but the probe changed in merge {merge[:12]} after its previous derivation was recorded in "
            f"{recorded[:12]}") in reason


def test_701_a_derivation_recorded_inside_a_merge_is_not_credited_to_a_later_commit(target, tmp_path):
    """Audit item (3): a merge moves a commit anchor and lowers the bar; a later plain commit edits the
    probe. file_history() lists only that commit, which would read as the move and carry both changes."""
    marker = tmp_path / "ran"
    sha, rel = derived_probe(target, argv=marker_argv(marker, "1"), expected=dict(BAR_OF_TWO))
    target.write(DECL, "# Requirements\n\n## Export\n\nExports 3 collections, reworded.\n")
    changed = target.commit("edit the declaration")
    _, merge = _merge_side(target, in_merge=lambda: _rewrite(target, rel, expected_value=1, derived_from=changed))
    _rewrite(target, rel, tier="T1")
    later = target.commit("a later edit")
    reason = _weakened_reason(target, marker)
    assert (f"{later[:12]} moved derived_from from {sha[:12]} to {changed[:12]}, but merge {merge[:12]} "
            f"changed derived_from after the previous derivation was recorded and before {later[:12]}, "
            "and a derivation recorded in a merge cannot be judged") in reason, reason


def test_701_a_derivation_recorded_inside_the_newest_merge_names_it_not_uncommitted_changes(target, tmp_path):
    """No listed revision carries today's derived_from: before the fix this read as uncommitted changes."""
    marker = tmp_path / "ran"
    _, rel = derived_probe(target, argv=marker_argv(marker, "1"), expected=dict(BAR_OF_TWO))
    recorded = target.git("rev-parse", "HEAD")
    target.write(DECL, "# Requirements\n\n## Export\n\nExports 3 collections, reworded.\n")
    changed = target.commit("edit the declaration")
    _, merge = _merge_side(target, in_merge=lambda: _rewrite(target, rel, expected_value=1, derived_from=changed))
    reason = _weakened_reason(target, marker)
    assert reason == (f"weakened: probe changed in merge {merge[:12]} after its derivation was recorded in "
                      f"{recorded[:12]}"), reason


@pytest.mark.parametrize("where", ["merge", "commit"])
def test_701_a_weakening_before_a_commit_anchor_re_derivation_is_outside_the_window(sha256_target, tmp_path,
                                                                                    where):
    """AC (e): a move onto a commit anchor keeps the pre-v1.1 rules and consults only the previous
    anchor, not the probe changes before it, so a plain commit there is adopted; a merge at the same
    place is treated the same and not reported. Since #688 that holds only in a SHA-256 repository;
    in a SHA-1 one the move itself is refused (test_688_SECR4_*)."""
    target = sha256_target
    marker = tmp_path / "ran"
    _, rel = derived_probe(target, argv=marker_argv(marker, "1"), expected=dict(BAR_OF_TWO))
    if where == "merge":
        _, weakening = _merge_side(target, in_merge=lambda: _rewrite(target, rel, expected_value=1))
    else:
        _rewrite(target, rel, expected_value=1)
        weakening = target.commit("lower the bar")
    target.write(DECL, "# Requirements\n\n## Export\n\nExports 3 collections, reworded.\n")
    changed = target.commit("edit the declaration")
    _rewrite(target, rel, derived_from=changed)
    target.commit("re-derive")
    code, report = run_audit(target)
    row = row_of(report, "p1")
    assert code == ra.EXIT_OK and row[7] == ra.STATE_CLEAN and marker.exists(), row[7:]
    assert weakening[:12] not in report


def test_701_merges_changing_refuses_an_option_shaped_revision(target):
    with pytest.raises(ra.AuditError):
        ra.Git(target.path).merges_changing("--output=x", "HEAD", DECL)


def test_701_a_merge_on_a_path_the_probe_left_is_not_the_probes_change(target):
    """Follow-up 2: R approves p1.yml, X renames it, an unrelated file later placed at p1.yml gets an
    add/add conflict resolved in a merge, M changes the declaration and re-derives. The probe never lived
    at p1.yml after X, so that merge is not its change (searching p1.yml up to M marked it weakened)."""
    rel = _content_probe(target)
    moved_rel = "project/reach-probes/renamed.yml"
    target.git("mv", rel, moved_rel)
    target.commit("rename the probe file")
    target.git("checkout", "-q", "-b", "reuse")
    target.write(rel, "side: 1\n")
    target.commit("an unrelated file at the old path")
    target.git("checkout", "-q", "main")
    target.write(rel, "main: 1\n")
    target.commit("another unrelated file at the old path")
    subprocess.run(["git", "-C", str(target.path), "merge", "-q", "--no-ff", "reuse"], capture_output=True, check=False)
    target.write(rel, "resolved: 1\n")
    merge = target.commit("resolve the add/add conflict")
    assert ra.Git(target.path).merges_changing(merge + "^", merge, rel) == [merge]
    target.git("rm", "-q", rel)
    target.commit("drop the unrelated file")
    target.write(DECL, "# Requirements\n\n## Export\n\nExports 3 collections, reworded.\n")
    _rewrite(target, moved_rel, derived_from="blob:" + target.git("hash-object", DECL))
    target.commit("edit the declaration and re-derive")
    _assert_clean(target)


def test_701_an_octopus_merge_that_edits_the_probe_is_weakened(target, tmp_path):
    """Follow-up 3: a merge with three parents is judged like any other merge."""
    marker = tmp_path / "ran"
    rel, recorded = _probe_observing_one(target, marker)
    for branch in ("one", "two"):
        target.git("checkout", "-q", "-b", branch, "main")
        target.write(f"{branch}.txt", f"{branch}\n")
        target.commit(f"{branch} work")
    target.git("checkout", "-q", "main")
    target.git("merge", "-q", "--no-ff", "--no-commit", "one", "two")
    _rewrite(target, rel, expected_value=1)
    merge = target.commit("octopus merge lowering the bar")
    assert target.git("rev-list", "--parents", "-n", "1", merge).count(" ") == 3
    reason = _weakened_reason(target, marker)
    assert reason == (f"weakened: probe changed in merge {merge[:12]} after its derivation was recorded in "
                      f"{recorded[:12]}"), reason


@pytest.mark.parametrize("config", [("log.follow", "true"), ("diff.renames", "copies")])
def test_701_the_targets_log_and_diff_config_does_not_hide_an_evil_merge(target, tmp_path, config):
    """Follow-up 3: the target's own git config cannot switch the merge search to --follow or copies."""
    marker = tmp_path / "ran"
    target.git("config", *config)
    rel, recorded = _probe_observing_one(target, marker)
    _, merge = _merge_side(target, in_merge=lambda: _rewrite(target, rel, expected_value=1))
    reason = _weakened_reason(target, marker)
    assert reason == (f"weakened: probe changed in merge {merge[:12]} after its derivation was recorded in "
                      f"{recorded[:12]}"), reason


def test_701_a_search_start_that_is_no_ancestor_widens_instead_of_finding_nothing(target):
    """Follow-up 1: R, an evil merge E, then A; D comes after A but is dated before R. In committer-date
    order the walk listed A, R, D, and D looked like the oldest revision of a span ending at A. Since
    #688 file_history() lists in topological order (D first), but a span can still start at a revision
    that is no ancestor of its end: D..A is empty, and the search must fail closed and still find E,
    which lies in A's ancestry. D sits on a branch merged back without a conflict."""
    rel = _content_probe(target)
    _, merge = _merge_side(target, in_merge=lambda: _rewrite(target, rel, expected_value=1))
    _rewrite(target, rel, tier="T1")
    after = target.commit("a later edit")
    target.git("checkout", "-q", "-b", "late")
    _rewrite(target, rel, tier="T0")
    target.git("add", "-A")
    subprocess.run(["git", "-C", str(target.path), "commit", "-q", "-m", "back-dated edit"], check=True,
                   env={**os.environ, "GIT_COMMITTER_DATE": "2001-01-01T00:00:00Z",
                        "GIT_AUTHOR_DATE": "2001-01-01T00:00:00Z"})
    forged = target.git("rev-parse", "HEAD")
    target.git("checkout", "-q", "main")
    target.write("unrelated.txt", "main\n")
    target.commit("main work")
    target.git("merge", "-q", "--no-ff", "--no-edit", "late")
    git = ra.Git(target.path)
    history = git.file_history(rel)
    assert [c for c, _ in history][0] == forged and git.is_ancestor_or_equal(after, forged)
    span = [rev for rev in history if rev[0] not in (after, forged)] + [(forged, rel)]
    assert [m for m, _ in ra._merges_changing(git, span, after)] == [merge]
    assert git.merges_changing(forged, after, rel) == [merge]


# --------------------------------------------------------------------------- #
# #702: a probe whose origin lies in a merge the history walk can't follow
# --------------------------------------------------------------------------- #
# file_history() walks `--follow --no-merges`, so a rename or a creation made
# inside a merge leaves the probe's listed history starting at a later plain
# commit that only edits the file. That commit must not read as the derivation.
MOVED = "project/reach-probes/p2.yml"


def _touch(target: Target, rel: str) -> str:
    """A trivial commit on ``rel`` that keeps every field, derived_from included."""
    target.write(rel, (target.path / rel).read_text() + "# reviewed\n")
    return target.commit(f"touch {rel}")


def _incomplete(commit: str, path: str, what: str = "a change to it") -> str:
    return (f"the probe's oldest listed revision {commit[:12]} does not create {path} but records {what}: the "
            "probe's origin isn't in its listed history but in a merge the walk can't follow, and a derivation "
            "recorded in a merge cannot be judged")


def test_702_a_rename_and_weakening_inside_a_merge_then_a_commit_is_weakened(target, tmp_path):
    """AC (a): measured before the fix as clean, exit 0, executed: C read as the probe's first commit."""
    marker = tmp_path / "ran"
    rel, _ = _probe_observing_one(target, marker)

    def in_merge() -> None:
        target.git("mv", rel, MOVED)
        _rewrite(target, MOVED, expected_value=1)

    _, merge = _merge_side(target, in_merge=in_merge)
    later = _touch(target, MOVED)
    assert ra.Git(target.path).file_history(MOVED) == [(later, MOVED)]
    assert target.git("rev-parse", f"{later}^") == merge
    reason = _weakened_reason(target, marker)
    assert reason == "weakened: " + _incomplete(later, MOVED), reason


def test_702_a_probe_created_inside_a_merge_then_a_commit_is_weakened(target, tmp_path):
    """AC (b): the same shape without a rename; with no later commit it reads uncommitted (SEC-101)."""
    marker = tmp_path / "ran"
    blob = _blob(target)
    _, merge = _merge_side(target, in_merge=lambda: target.write_probe(
        make_probe(derived_from=blob, argv=marker_argv(marker))))
    later = _touch(target, "project/reach-probes/p1.yml")
    assert ra.Git(target.path).file_history("project/reach-probes/p1.yml") == [(later, "project/reach-probes/p1.yml")]
    assert target.git("rev-parse", f"{later}^") == merge
    reason = _weakened_reason(target, marker)
    assert reason == "weakened: " + _incomplete(later, "project/reach-probes/p1.yml"), reason


def test_702_a_replacement_created_inside_a_merge_then_a_commit_supersedes_nothing(sectioned):
    """AC (b): before the fix p2 read clean and the record took effect, so p1 read superseded, exit 0."""
    _weakened_rebaseline(sectioned)
    _, merge = _merge_side(sectioned, in_merge=lambda: _replacement(sectioned, commit=False))
    later = _touch(sectioned, MOVED)
    assert sectioned.git("rev-parse", f"{later}^") == merge
    code, report = run_audit(sectioned)
    assert code == ra.EXIT_FINDINGS, report
    new = row_of(report, "p2")
    assert new[1] == ra.NOT_PROBED and new[5] == "not executed" and new[7] == ra.STATE_WEAKENED, new
    assert _plain(new[9]) == "weakened: " + _incomplete(later, MOVED), new[9]
    old = row_of(report, "p1")
    assert old[7] == ra.STATE_WEAKENED and "supersede by p2 not in effect: it is weakened" in _plain(old[9]), old


def test_702_a_plain_rename_reads_as_before(target, tmp_path):
    """AC (c): --follow lists a rename in a non-merge commit, so the history reaches the creating commit."""
    marker = tmp_path / "ran"
    rel, recorded = _probe_observing_one(target, marker)
    target.git("mv", rel, MOVED)
    renamed = target.commit("rename the probe file")
    later = _touch(target, MOVED)
    assert [c for c, _ in ra.Git(target.path).file_history(MOVED)] == [later, renamed, recorded]
    reason = _weakened_reason(target, marker)
    assert reason == (f"weakened: probe changed in {renamed[:12]}, {later[:12]} after its derivation was "
                      f"recorded in {recorded[:12]}"), reason


def test_702_a_probe_created_in_the_root_commit_stays_clean(tmp_path):
    """AC (c): the oldest listed revision has no parent, so it creates the probe."""
    marker = tmp_path / "ran"
    root = Target(tmp_path / "rooted")
    root.write(DECL, "# Requirements\n\n## Export\n\nExports 3 collections.\n")
    root.write_probe(make_probe(derived_from="blob:" + root.git("hash-object", DECL), argv=marker_argv(marker)))
    root.commit("declare and approve in the root commit")
    assert root.git("rev-list", "--max-parents=0", "HEAD") == root.git("rev-parse", "HEAD")
    _assert_clean(root)
    assert marker.exists()


def _shallow_clone(target: Target, tmp_path: Path) -> Target:
    clone = tmp_path / "shallow"
    subprocess.run(["git", "clone", "-q", "--depth", "1", f"file://{target.path}", str(clone)], check=True,
                   capture_output=True)
    shallow = Target.__new__(Target)
    shallow.path = clone
    assert shallow.git("rev-parse", "--is-shallow-repository") == "true"
    return shallow


def test_702_a_shallow_clone_is_refused_before_anything_runs(target, tmp_path, capsys):
    """Security follow-up: every boundary commit of a shallow clone reports each file as added, so at depth 1
    a probe's history is HEAD alone and a weakening before it is invisible. Before the guard the bar lowered
    in the full repository read clean in the clone, exit 0, executed."""
    marker = tmp_path / "ran"
    rel, _ = _probe_observing_one(target, marker)
    _rewrite(target, rel, expected_value=1)
    weakened = target.commit("lower the bar")
    code, _ = run_audit(target)
    assert code == ra.EXIT_FINDINGS and not marker.exists()
    shallow = _shallow_clone(target, tmp_path)
    assert ra.Git(shallow.path).file_history(rel) == [(weakened, rel)]
    with pytest.raises(ra.AuditError) as exc:
        ra.run(str(shallow.path), clock=lambda: FIXED_NOW)
    assert exc.value.code == ra.EXIT_USAGE
    assert "is a shallow clone" in str(exc.value) and "git fetch --unshallow" in str(exc.value)
    assert not marker.exists()
    assert not (shallow.path / ".audits").exists()
    assert ra.main(["--repo", str(shallow.path)]) == ra.EXIT_USAGE
    assert ra.main(["--repo", str(shallow.path), "--check-migration"]) == ra.EXIT_USAGE
    assert "is a shallow clone" in capsys.readouterr().err
    assert not marker.exists()


def test_702_an_unshallowed_clone_is_judged_again(target, tmp_path):
    """The remedy the refusal names: after `git fetch --unshallow` the weakening is found."""
    marker = tmp_path / "ran"
    rel, _ = _probe_observing_one(target, marker)
    _rewrite(target, rel, expected_value=1)
    target.commit("lower the bar")
    shallow = _shallow_clone(target, tmp_path)
    shallow.git("fetch", "-q", "--unshallow")
    assert _weakened_reason(shallow, marker).startswith("weakened: probe changed in ")


def test_702_a_probe_file_name_with_glob_characters_reads_only_its_own_history(target, tmp_path):
    """Security follow-up: without literal pathspecs `w[x].yml` is a glob that also matches `wx.yml`, so
    another probe's commits and uncommitted edits were read as this probe's."""
    marker = tmp_path / "ran"
    blob = _blob(target)
    rel = target.write_probe(make_probe("wbr", derived_from=blob, argv=marker_argv(marker)), name="w[x]")
    recorded = target.commit("approve w[x]")
    other = target.write_probe(make_probe("wx", derived_from=blob))
    target.commit("approve wx")
    _rewrite(target, other, tier="T1")
    target.commit("edit wx only")
    _rewrite(target, other, tier="T0")
    git = ra.Git(target.path)
    assert git.file_history(rel) == [(recorded, rel)]
    assert git.is_dirty(other) and not git.is_dirty(rel)
    assert git.last_commit(rel) == recorded
    code, report = run_audit(target)
    row = row_of(report, "wbr")
    assert row[1] == ra.REACHED and row[7] == ra.STATE_CLEAN, row[7:]
    assert marker.exists()


def test_702_a_plain_rename_out_of_a_path_a_merge_created_is_weakened(target, tmp_path):
    """Refutes the parent check alone: the merge moves the probe to an interim path and lowers the bar, a
    plain commit D renames it on. D does create its path, but --follow stops at D's rename because the
    interim path has no listed commit, so D read as the probe's derivation: clean, exit 0, executed."""
    marker = tmp_path / "ran"
    rel, _ = _probe_observing_one(target, marker)
    interim = "project/reach-probes/interim.yml"

    def in_merge() -> None:
        target.git("mv", rel, interim)
        _rewrite(target, interim, expected_value=1)

    _merge_side(target, in_merge=in_merge)
    target.git("mv", interim, MOVED)
    renamed = target.commit("rename the probe file")
    assert ra.Git(target.path).file_history(MOVED) == [(renamed, MOVED)]
    assert target.git("cat-file", "-t", f"{renamed}^:{interim}") == "blob"
    reason = _weakened_reason(target, marker)
    assert reason == ("weakened: " + _incomplete(renamed, MOVED, f"a rename from {interim}")), reason


# --------------------------------------------------------------------------- #
# #704: a probe that left the probe set is removed unless an approved
# retirement record accounts for it (project/requirements/reach-probe-removal.md)
# --------------------------------------------------------------------------- #
RETIRED_SCHEMA_PATH = REPO_ROOT / "schemas" / "reach-retired-v1.0.schema.yaml"
RETIRED_REL = "project/reach-probes/_retired.yml"
P1_REL = "project/reach-probes/p1.yml"


def retirement(pid: str = "p1", *, last: str = "a" * 40, reason: str = "capability-removed",
               approved: bool = True, **extra) -> dict:
    record: dict = {"id": pid, "reason": reason, "detail": "the export it measured was dropped",
                    "recorded_at": "2026-11-10T09:00:00Z", "last_revision": last}
    if approved:
        record["approval"] = {"approved_at": "2026-11-10T09:05:00Z", "approved_by": "nolte"}
    return record | extra


def _retire(target: Target, *records: dict, commit: bool = True, raw: str | None = None) -> None:
    target.write(RETIRED_REL, raw if raw is not None else yaml.safe_dump({"entries": list(records)}, sort_keys=False))
    if commit:
        target.commit("retire probes")


def _validate_retired(doc: object) -> list[str]:
    return [e.message for e in Draft202012Validator(ra.RETIRED_SCHEMA).iter_errors(doc)]


def _finding(report: str, kind: str, pid: str) -> str:
    """The text of the ``kind`` finding on ``pid``; fails when there is none."""
    head = f"- **{kind}** `{pid}` ("
    lines = [ln for ln in report.splitlines() if ln.startswith(head)]
    assert lines, f"no {kind} finding on {pid}:\n{report}"
    return _plain(lines[0].split("): ", 1)[1])


def _second(target: Target) -> None:
    """An approved p2 that git never pairs with p1 as a copy (dissimilar content)."""
    derived_probe(target, pid="p2", summary="a second probe on another reading of the entry " * 12)


def _kept_and_dropped(target: Target, **kw) -> tuple[str, str]:
    """Approved p1 and p2; a plain commit deletes p1. Returns (the last commit with p1, the deleting commit)."""
    derived_probe(target, **kw)
    _second(target)
    last = target.git("rev-parse", "HEAD")
    target.git("rm", "-q", P1_REL)
    return last, target.commit("drop p1")


# -- schema ----------------------------------------------------------------- #
def test_704_runner_copy_matches_the_shipped_retirement_schema():
    shipped = yaml.safe_load(RETIRED_SCHEMA_PATH.read_text())
    assert _structural(shipped) == _structural(ra.RETIRED_SCHEMA)
    assert ra.RETIRED_SCHEMA["$defs"]["Approval"] == ra.PROBE_SCHEMA["$defs"]["Approval"]


def test_704_shipped_retirement_schema_is_valid_and_its_examples_validate():
    shipped = yaml.safe_load(RETIRED_SCHEMA_PATH.read_text())
    Draft202012Validator.check_schema(shipped)
    for example in shipped["examples"]:
        assert _validate_retired(example) == []


def test_704_retirement_schema_is_closed_and_its_reason_codes_are_four():
    assert _validate_retired({"entries": [retirement(), retirement("p2", approved=False, last="b" * 64)]}) == []
    assert any("Additional properties" in m for m in _validate_retired({"entries": [retirement() | {"status": "ok"}]}))
    assert any("Additional properties" in m for m in _validate_retired({"entries": [], "verdict": "retired"}))
    assert any("is not one of" in m for m in _validate_retired({"entries": [retirement(reason="replaced")]}))
    assert any("does not match" in m for m in _validate_retired({"entries": [retirement(last="abc")]}))
    for missing in ("id", "reason", "detail", "recorded_at", "last_revision"):
        record = retirement()
        del record[missing]
        assert any("is a required property" in m for m in _validate_retired({"entries": [record]})), missing


# -- R1, AC1/AC2: a deleted probe is removed --------------------------------- #
def test_704_AC1_an_approved_probe_deleted_in_a_plain_commit_is_removed_naming_its_last_commit(target):
    last, _ = _kept_and_dropped(target)
    code, report = run_audit(target)
    assert code == 4, report
    text = _finding(report, "removed", "p1")
    assert text.startswith(f"no probe file carries this id any more; it last existed in {P1_REL} at {last}"), text
    assert text.endswith("no retirement record accounts for it"), text
    assert "**Not probed: 1 of 2 probes, 1 of them removed.**" in report
    assert "plus 1 removed probe id(s) that no effective retirement record accounts for, 2 in all" in report
    assert "| none (removed) | 0 | 0 | 0 | 1 |" in report


def test_704_AC1_an_approved_retirement_record_makes_the_run_clean_and_is_listed_as_new(target):
    last, _ = _kept_and_dropped(target)
    _retire(target, retirement(last=last))
    code, report = run_audit(target)
    assert code == 0, report
    assert "## Findings\n\n- none\n" in report
    assert "- Retired probe ids in `project/reach-probes/_retired.yml`: 1, 1 of them new since the manifest's previous commit." in report
    assert (f"- Retired `p1` (capability-removed), **new since the manifest's previous commit**: the export it "
            f"measured was dropped; last existed at {last[:12]}; approved by nolte at 2026-11-10T09:05:00Z.") in report
    assert "removed" not in row_of(report, "p2")[7]


def test_704_R8_a_record_is_marked_new_only_in_the_change_that_adds_it(target):
    last, _ = _kept_and_dropped(target)
    derived_probe(target, pid="p3", summary="a third probe, worded apart from the others " * 12)
    target.git("rm", "-q", "project/reach-probes/p3.yml")
    last3 = target.git("rev-parse", "HEAD~1")
    target.commit("drop p3")
    _retire(target, retirement(last=last))
    _retire(target, retirement(last=last), retirement("p3", last=last3, reason="duplicate"))
    code, report = run_audit(target)
    assert code == 0, report
    assert "- Retired `p1` (capability-removed): the export" in report
    assert "- Retired `p3` (duplicate), **new since the manifest's previous commit**:" in report
    assert ": 2, 1 of them new since the manifest's previous commit." in report


def test_704_AC2_a_never_approved_probe_deleted_later_is_removed_the_same_way(target):
    last, _ = _kept_and_dropped(target, approved=False)
    code, report = run_audit(target)
    assert code == 4, report
    assert _finding(report, "removed", "p1").startswith(f"no probe file carries this id any more; it last existed in {P1_REL} at {last}")


def test_704_R1_a_set_that_lost_every_probe_file_reports_each_removal_not_an_empty_set(target):
    derived_probe(target)
    target.git("rm", "-q", "-r", "project/reach-probes")
    target.commit("drop the whole probe set")
    code, report = run_audit(target)
    assert code == 4, report
    assert "No probe set" not in report
    _finding(report, "removed", "p1")


def test_704_R8_a_retired_set_without_probe_files_still_lists_the_retirement(target):
    derived_probe(target)
    last = target.git("rev-parse", "HEAD")
    target.git("rm", "-q", P1_REL)
    target.commit("drop p1")
    _retire(target, retirement(last=last))
    code, report = run_audit(target)
    assert code == 3, report
    assert "**Not probed: all. No probe set.**" in report
    assert "- Retired `p1` (capability-removed), **new since the manifest's previous commit**" in report


def test_704_R1_an_uncommitted_deletion_is_removed_and_no_record_accounts_for_it(target):
    derived_probe(target)
    _second(target)
    _retire(target, retirement())
    head = target.git("rev-parse", "HEAD")
    (target.path / P1_REL).unlink()
    code, report = run_audit(target)
    assert code == 4, report
    text = _finding(report, "removed", "p1")
    assert f"it last existed in {P1_REL} at HEAD {head}, and its removal is not committed" in text, text
    assert text.endswith("a retirement record can't account for a removal that is not committed"), text


# -- R4/AC3: only an approved, committed record takes effect ------------------ #
def test_704_AC3_a_record_without_an_approval_takes_no_effect(target):
    last, _ = _kept_and_dropped(target)
    _retire(target, retirement(last=last, approved=False))
    code, report = run_audit(target)
    assert code == 4, report
    assert _finding(report, "removed", "p1").endswith("its retirement record carries no approval, so it takes no effect")
    assert "- Retired probe ids in `project/reach-probes/_retired.yml`: 0, 0 of them new" in report


def test_704_AC3_a_record_with_a_malformed_approval_is_invalid_and_takes_no_effect(target):
    last, _ = _kept_and_dropped(target)
    _retire(target, retirement(last=last, approval={"approved_by": "nolte"}))
    code, report = run_audit(target)
    assert code == 4, report
    assert "approved_at" in _finding(report, "invalid retirement record", "p1")
    assert _finding(report, "removed", "p1").endswith("its retirement record is invalid (see Findings), so it takes no effect")


def test_704_R4_an_uncommitted_record_takes_no_effect(target):
    last, _ = _kept_and_dropped(target)
    _retire(target, retirement(last=last), commit=False)
    code, report = run_audit(target)
    assert code == 4, report
    assert _finding(report, "removed", "p1").endswith("its retirement record is not committed, so it takes no effect")


def test_704_R4_a_record_committed_with_the_deletion_takes_effect_whatever_last_revision_names(target):
    """The squash-merge shape: one commit deletes the probe and adds the record; last_revision may be unknown."""
    derived_probe(target)
    _second(target)
    target.git("rm", "-q", P1_REL)
    _retire(target, retirement(last="c" * 40))
    code, report = run_audit(target)
    assert code == 0, report
    assert "- Retired `p1` (capability-removed), **new since" in report


def test_704_R4_a_record_cannot_account_for_a_removal_it_predates(target):
    """Retired once, restored, removed again: the old record names an earlier removal."""
    last, _ = _kept_and_dropped(target)
    _retire(target, retirement(last=last))
    assert run_audit(target)[0] == 0
    target.write(P1_REL, target.git("show", f"{last}:{P1_REL}") + "\n")
    target.write(RETIRED_REL, "entries: []\n")
    target.commit("restore p1, drop its record")
    target.write(RETIRED_REL, yaml.safe_dump({"entries": [retirement(last=last)]}, sort_keys=False))
    restored = target.commit("put the old record back")
    target.git("rm", "-q", P1_REL)
    gone = target.commit("drop p1 again")
    shutil.rmtree(target.path / ".audits")
    code, report = run_audit(target)
    assert code == 4, report
    assert _finding(report, "removed", "p1").endswith(
        f"its retirement record was already in {RETIRED_REL} at {restored[:12]}, before the removal in "
        f"{gone[:12]}, so it can't account for that removal")


def test_704_R4_an_unreadable_retirement_manifest_is_a_finding_and_retires_nothing(target):
    last, _ = _kept_and_dropped(target)
    _retire(target, raw="entries: [unclosed\n")
    code, report = run_audit(target)
    assert code == 4, report
    assert "- **invalid retirement manifest** (project/reach-probes/_retired.yml): not parseable as YAML" in report
    assert _finding(report, "removed", "p1").endswith(ra.WHY_MANIFEST_UNREADABLE)
    assert "is present but unreadable (see Findings); no record in it takes effect" in report


def test_704_R4_a_record_listed_twice_is_a_finding(target):
    last, _ = _kept_and_dropped(target)
    _retire(target, retirement(last=last), retirement(last=last, reason="duplicate"))
    code, report = run_audit(target)
    assert code == 4, report
    assert _finding(report, "invalid retirement record", "p1") == "listed more than once; only the first record is read"


# -- R2/R5, AC4: an exchange under the same id -------------------------------- #
@pytest.mark.parametrize("flow", ["one-commit", "two-commits"])
def test_704_AC4_an_exchange_under_the_same_id_reports_the_old_probe_removed(target, tmp_path, flow):
    """p1 at p1.yml is dropped and a dissimilar file elsewhere takes the id: git pairs no rename."""
    marker = tmp_path / "ran"
    derived_probe(target)
    last = target.git("rev-parse", "HEAD")
    target.git("rm", "-q", P1_REL)
    if flow == "two-commits":
        target.commit("drop p1")
    weaker = make_probe(derived_from=target.git("rev-parse", "HEAD"), argv=marker_argv(marker, "1"),
                        expected={"kind": "count", "value": 1, "unit": "collections"},
                        summary="a much shorter probe " * 30)
    rel = target.write_probe(weaker, name="p1-replacement")
    adopted = target.commit("a new file under the old id")
    assert len(target.git("log", "--follow", "--format=%H", "--", rel).splitlines()) == 1
    code, report = run_audit(target)
    assert code == 4, report
    text = _finding(report, "removed", "p1")
    assert text.startswith(f"exchange under the same id: it last existed in {P1_REL} at {last}, and {rel} carries "
                           f"it now, but that file's own history first carries it in {adopted[:12]}"), text
    assert text.endswith("a retirement record can't account for an exchange under the same id: give the replacement "
                         "a new id and retire this one, or restore the earlier file and supersede it"), text


def test_704_AC4_R5_a_retirement_record_for_an_exchanged_id_is_a_contradiction(target):
    derived_probe(target)
    last = target.git("rev-parse", "HEAD")
    target.git("rm", "-q", P1_REL)
    target.write_probe(make_probe(derived_from=last, summary="unrelated text " * 40), name="p1-replacement")
    _retire(target, retirement(last=last))
    code, report = run_audit(target)
    assert code == 4, report
    assert _finding(report, "retirement contradiction", "p1").startswith(
        "the probe file project/reach-probes/p1-replacement.yml still carries this id")
    assert _finding(report, "removed", "p1").startswith("exchange under the same id")
    assert "Retired `p1`" not in report


def test_704_R2_an_uncommitted_file_taking_over_a_committed_id_is_an_exchange(target):
    derived_probe(target)
    _second(target)
    (target.path / P1_REL).unlink()
    target.write_probe(make_probe(derived_from="b" * 40, summary="unrelated text " * 40), name="p1-new")
    code, report = run_audit(target)
    assert code == 4, report
    assert "holds no committed revision that carries it" in _finding(report, "removed", "p1")


def test_704_R2_a_later_duplicate_of_a_kept_probe_dropped_again_is_no_exchange(target):
    """p1 keeps its id throughout; a second file took the id later and was removed: nothing left the set."""
    derived_probe(target)
    target.write_probe(make_probe(derived_from="b" * 40, summary="unrelated text " * 40), name="p1-copy")
    target.commit("a duplicate id")
    target.git("rm", "-q", "project/reach-probes/p1-copy.yml")
    target.commit("drop the duplicate")
    code, report = run_audit(target)
    assert code == 0, report
    assert "removed" not in report.split("## Findings")[1].split("## Probes")[0]


# -- R3, AC5: identity is the id ---------------------------------------------- #
def test_704_AC5_a_rename_that_keeps_the_id_is_no_removal(target):
    """The rename itself is judged as before (a later commit to the probe); it removes nothing."""
    _, rel = derived_probe(target)
    target.git("mv", rel, "project/reach-probes/export-populated.yml")
    target.commit("rename the probe file")
    _, report = run_audit(target)
    assert "- **removed**" not in report, report
    assert _finding(report, "weakened", "p1").startswith("probe changed in")


def test_704_AC5_editing_the_id_in_a_kept_file_reports_the_old_id_removed(target):
    _, rel = derived_probe(target)
    last = target.git("rev-parse", "HEAD")
    _rewrite(target, rel, id="p1-renamed")
    target.commit("rename the id")
    code, report = run_audit(target)
    assert code == 4, report
    assert _finding(report, "removed", "p1").startswith(f"no probe file carries this id any more; it last existed in {P1_REL} at {last}")
    assert "removed" not in _finding(report, "weakened", "p1-renamed")


# -- R5/R6, AC6: records for ids carried now, or never ----------------------- #
def test_704_AC6_a_record_for_an_id_still_carried_is_a_contradiction(target):
    derived_probe(target)
    _retire(target, retirement(last=target.git("rev-parse", "HEAD")))
    code, report = run_audit(target)
    assert code == 4, report
    assert _finding(report, "retirement contradiction", "p1").startswith(f"the probe file {P1_REL} still carries this id")
    assert row_of(report, "p1")[7] == ra.STATE_CLEAN


def test_704_AC6_a_record_for_an_id_never_carried_is_invalid(target):
    derived_probe(target)
    _retire(target, retirement("never-a-probe"))
    code, report = run_audit(target)
    assert code == 4, report
    assert _finding(report, "invalid retirement record", "never-a-probe") == (
        "no committed probe file under project/reach-probes/ in the history of HEAD ever carried this id")


def test_704_AC6_a_never_committed_id_cannot_be_retired(target):
    derived_probe(target)
    target.write_probe(make_probe("p9", derived_from="b" * 40))
    (target.path / "project/reach-probes/p9.yml").unlink()
    _retire(target, retirement("p9"))
    code, report = run_audit(target)
    assert code == 4, report
    _finding(report, "invalid retirement record", "p9")


# -- R7, AC7: a superseded probe's file stays ------------------------------- #
def test_704_AC7_deleting_a_superseded_probes_file_reports_it_removed(sectioned):
    _superseded(sectioned)
    last = sectioned.git("rev-parse", "HEAD")
    sectioned.git("rm", "-q", P1_REL)
    sectioned.commit("drop the superseded file")
    shutil.rmtree(sectioned.path / ".audits")
    code, report = run_audit(sectioned)
    assert code == 4, report
    assert _finding(report, "removed", "p1").startswith(f"no probe file carries this id any more; it last existed in {P1_REL} at {last}")


# -- R11: the id of a historical revision ------------------------------------ #
def test_704_R11_an_unparseable_historical_file_is_identified_by_its_file_name_stem(target):
    derived_probe(target)
    target.write("project/reach-probes/broken-probe.yml", "id: [unclosed\n")
    last = target.commit("an unparseable probe file")
    target.git("rm", "-q", "project/reach-probes/broken-probe.yml")
    target.commit("drop it")
    code, report = run_audit(target)
    assert code == 4, report
    assert _finding(report, "removed", "broken-probe").startswith(
        f"no probe file carries this id any more; it last existed in project/reach-probes/broken-probe.yml at {last}")


def test_704_R11_a_parseable_historical_file_is_identified_by_its_id_not_its_name(target):
    derived_probe(target)
    target.write_probe(make_probe("export-check", derived_from="b" * 40), name="file-name")
    target.commit("a probe whose file name is not its id")
    target.git("rm", "-q", "project/reach-probes/file-name.yml")
    target.commit("drop it")
    _, report = run_audit(target)
    _finding(report, "removed", "export-check")
    assert "`file-name`" not in report


# -- merges: an id carried anywhere in HEAD's history counts ----------------- #
def test_704_merge_a_probe_that_lived_only_on_a_merged_side_branch_is_removed(target):
    derived_probe(target)

    def add_and_drop() -> None:
        target.write_probe(make_probe("side-probe", derived_from="b" * 40))
        target.commit("side: add a probe")
        target.git("rm", "-q", "project/reach-probes/side-probe.yml")

    side, _ = _merge_side(target, on_side=add_and_drop)
    code, report = run_audit(target)
    assert code == 4, report
    assert f"at {side}~1" not in report
    assert _finding(report, "removed", "side-probe").startswith(
        f"no probe file carries this id any more; it last existed in project/reach-probes/side-probe.yml at "
        f"{target.git('rev-parse', side + '~1')}")


def test_704_merge_a_probe_added_and_dropped_only_inside_merges_is_removed(target):
    derived_probe(target)
    rel = "project/reach-probes/merge-only.yml"
    _merge_side(target, "one", in_merge=lambda: target.write_probe(make_probe("merge-only", derived_from="b" * 40)))
    _, dropped = _merge_side(target, "two", in_merge=lambda: target.git("rm", "-q", rel))
    assert not target.git("log", "--no-merges", "--format=%H", "--", rel)
    code, report = run_audit(target)
    assert code == 4, report
    # The merge that dropped it took it off its first parent, the last commit that still had it.
    assert _finding(report, "removed", "merge-only").startswith(
        f"no probe file carries this id any more; it last existed in {rel} at {target.git('rev-parse', dropped + '^1')}")


def test_704_merge_the_targets_log_config_does_not_hide_a_merge_only_probe(target):
    derived_probe(target)
    rel = "project/reach-probes/merge-only.yml"
    _merge_side(target, "one", in_merge=lambda: target.write_probe(make_probe("merge-only", derived_from="b" * 40)))
    _merge_side(target, "two", in_merge=lambda: target.git("rm", "-q", rel))
    for key, value in (("log.diffMerges", "first-parent"), ("log.follow", "true"), ("log.showRoot", "false"),
                       ("diff.renames", "copies")):
        target.git("config", key, value)
    code, report = run_audit(target)
    assert code == 4, report
    _finding(report, "removed", "merge-only")


def test_704_history_walk_reads_every_blob_once(target):
    derived_probe(target)
    for n in range(3):
        _rewrite(target, P1_REL, summary=f"revision {n}")
        target.commit(f"edit {n}")
    history = ra.probe_set_history(ra.Git(target.path), yaml, target.git("rev-parse", "HEAD"))
    assert history.ids == {"p1"}
    assert history.blobs == 4 and history.commits == 4
    assert history.at_head == {"p1": [P1_REL]}


def test_704_merge_a_probe_kept_on_a_side_branch_last_existed_at_its_tip_whatever_log_diff_merges_says(target):
    """Main drops p1, a side branch edits it, the merge keeps the deletion: only the diff against the
    second parent shows p1 leaving, so a first-parent-only walk would name the pre-branch commit."""
    derived_probe(target)
    _second(target)
    target.git("checkout", "-q", "-b", "side")
    _rewrite(target, P1_REL, summary="edited on the side")
    side = target.commit("side: edit p1")
    target.git("checkout", "-q", "main")
    target.git("rm", "-q", P1_REL)
    target.commit("main: drop p1")
    subprocess.run(["git", "-C", str(target.path), "merge", "-q", "--no-ff", "side"], capture_output=True, check=False)
    target.git("rm", "-q", P1_REL)
    merge = target.commit("merge side, keeping the deletion")
    assert target.git("rev-list", "--parents", "-n", "1", merge).count(" ") == 2
    target.git("config", "log.diffMerges", "first-parent")
    code, report = run_audit(target)
    assert code == 4, report
    assert _finding(report, "removed", "p1").startswith(
        f"no probe file carries this id any more; it last existed in {P1_REL} at {side}")


# --------------------------------------------------------------------------- #
# #704 security verification (P4): ids read the same way in history and at HEAD
# --------------------------------------------------------------------------- #
BIG_SUMMARY = "x" * (1024 * 1024 + 4096)  # past the old 1 MiB cap and the batch bound


def test_704_P4_1_an_oversize_revision_keeps_its_id_so_a_swap_to_the_stem_is_removed(target):
    """a.yml carries `big-id` padded past the batch bound, then one commit makes it a small `a`: big-id left."""
    derived_probe(target)
    rel = target.write_probe(make_probe("big-id", derived_from="b" * 40, summary=BIG_SUMMARY), name="a")
    last = target.commit("an oversize probe file")
    target.write_probe(make_probe("a", derived_from="b" * 40), name="a")
    target.commit("rewrite it small, under the file name's id")
    code, report = run_audit(target)
    assert code == 4, report
    assert _finding(report, "removed", "big-id").startswith(
        f"no probe file carries this id any more; it last existed in {rel} at {last}")


def test_704_P4_1_an_oversize_probe_at_head_is_no_removal(target):
    derived_probe(target)
    target.write_probe(make_probe("big-probe", derived_from="b" * 40, summary=BIG_SUMMARY), name="big")
    target.commit("an oversize probe file")
    _, report = run_audit(target)
    assert "- **removed**" not in report, report


def test_704_P4_1_a_historical_revision_missing_from_the_repository_stops_the_run(target, capsys):
    """A partial clone: the walk names a blob the object store lacks; no stem may stand in for it."""
    derived_probe(target)
    rel = target.write_probe(make_probe("gone", derived_from="b" * 40, summary="a probe whose object goes missing"))
    target.commit("add")
    blob = target.git("rev-parse", f"HEAD:{rel}")
    target.git("rm", "-q", rel)
    target.commit("drop")
    (target.path / ".git" / "objects" / blob[:2] / blob[2:]).unlink()
    assert ra.main(["--repo", str(target.path)]) == ra.EXIT_ERROR
    err = capsys.readouterr().err
    assert "does not hold" in err and blob in err, err


def test_704_P4_2_a_document_two_yaml_loaders_read_differently_has_one_id(target):
    """`id:<TAB>value` is an error to PyYAML's pure loader and an id to libyaml's: history and HEAD must agree."""
    derived_probe(target)
    target.write("project/reach-probes/tabbed.yml", "id:\tp-tab\ntier: T0\n")
    target.commit("a probe file with a tab after its key")
    _, report = run_audit(target)
    assert "- **removed**" not in report, report


def test_704_P4_2_every_yaml_read_goes_through_the_one_loader():
    source = SCRIPT_PATH.read_text()
    assert "safe_load(" not in source
    assert source.count("Loader=") == 1


@pytest.mark.parametrize("linked", ["project/reach-probes", "project"])
def test_704_P4_3_a_symlinked_probe_directory_is_refused(target, capsys, linked):
    derived_probe(target)
    real = target.path / "elsewhere"
    shutil.move(str(target.path / linked), str(real))
    (target.path / linked).parent.mkdir(parents=True, exist_ok=True)
    (target.path / linked).symlink_to(real.relative_to((target.path / linked).parent, walk_up=True))
    target.commit("move the probe set behind a link")
    assert (target.path / P1_REL).is_file()
    assert ra.main(["--repo", str(target.path)]) == ra.EXIT_USAGE
    assert f"{linked} is a symlink" in capsys.readouterr().err
    assert ra.main(["--repo", str(target.path), "--check-migration"]) == ra.EXIT_USAGE
    assert not (target.path / ".audits").exists()


def test_704_P4_4_a_record_cannot_take_effect_past_an_unreadable_manifest_before_the_removal(target):
    derived_probe(target)
    _second(target)
    _retire(target, raw="entries: [unclosed\n")
    carrier = target.git("rev-parse", "HEAD")
    target.git("rm", "-q", P1_REL)
    _retire(target, retirement(last=carrier), commit=False)
    removal = target.commit("drop p1 and retire it")
    code, report = run_audit(target)
    assert code == 4, report
    assert _finding(report, "removed", "p1").endswith(
        f"{RETIRED_REL} can't be read at {carrier[:12]}, before the removal in {removal[:12]}, so it can't be "
        "shown that the record postdates that removal")


# --------------------------------------------------------------------------- #
# #688: a probe created as a copy of another probe file starts its own history
# --------------------------------------------------------------------------- #
# git --follow pairs a file created beside a similar one that stays in place as
# a copy (C) and walks on into that file's revisions. A probe written from the
# same template as an earlier one must not take over the earlier probe's chain.
P2_REL = "project/reach-probes/p2.yml"


def _status_of(target: Target, rel: str, commit: str) -> tuple[str, str]:
    """git's status and source for ``rel`` at ``commit`` in its followed log."""
    found = [(status, source) for c, _, status, source in ra.Git(target.path).file_log(rel) if c == commit]
    assert len(found) == 1, found
    return found[0]


def _template_copy(target: Target, pid: str = "p2") -> str:
    """Write ``pid`` from the same template as p1 in a commit of its own; returns that commit."""
    target.write_probe(make_probe(pid, derived_from=_blob(target)))
    created = target.commit(f"derive {pid} from the same template")
    status, source = _status_of(target, f"project/reach-probes/{pid}.yml", created)
    assert (status, source) == ("C", P1_REL), "git no longer pairs the copy; revisit the copy cut"
    return created


def test_688_a_probe_added_from_the_template_of_an_earlier_one_reads_clean(target):
    """AC (a): measured before the fix as weakened, "probe changed in <p2's commit> after ... <p1's commit>"."""
    derived_probe(target)
    _template_copy(target)
    code, report = run_audit(target)
    assert code == ra.EXIT_OK, report
    for pid in ("p1", "p2"):
        row = row_of(report, pid)
        assert row[1] == ra.REACHED and row[7] == ra.STATE_CLEAN, row


def test_688_a_copy_edited_after_its_approval_reads_weakened_at_that_edit(target, tmp_path):
    """AC (b): the copy's own history still holds every later change."""
    derived_probe(target)
    created = _template_copy(target)
    _weaken(target, P2_REL)
    weakening = target.commit("lower p2's bar")
    code, report = run_audit(target)
    assert code == ra.EXIT_FINDINGS
    row = row_of(report, "p2")
    assert row[1] == ra.NOT_PROBED and row[7] == ra.STATE_WEAKENED, row
    assert (f"probe changed in {weakening[:12]} after its derivation was recorded in {created[:12]}"
            in _plain(row[9])), row[9]
    assert row_of(report, "p1")[7] == ra.STATE_CLEAN


def test_688_a_new_id_beside_a_kept_weakened_probe_is_clean_and_the_kept_one_stays_weakened(target):
    """AC (c): no supersede record, so p1 keeps its finding and the run fails."""
    _, rel = derived_probe(target)
    _weaken(target, rel)
    weakening = target.commit("lower p1's bar")
    _template_copy(target)
    code, report = run_audit(target)
    assert code == ra.EXIT_FINDINGS
    assert row_of(report, "p2")[7] == ra.STATE_CLEAN
    old = row_of(report, "p1")
    assert old[7] == ra.STATE_WEAKENED and f"probe changed in {weakening[:12]}" in _plain(old[9]), old


def test_688_a_renamed_weakened_probe_stays_weakened(target):
    """AC (d): a rename keeps the history; git reports R, not C."""
    _, rel = derived_probe(target)
    _weaken(target, rel)
    target.commit("lower p1's bar")
    target.git("mv", rel, "project/reach-probes/renamed.yml")
    moved = target.commit("rename p1's file")
    assert _status_of(target, "project/reach-probes/renamed.yml", moved) == ("R", rel)
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED, reason


@pytest.mark.parametrize("touched", [False, True])
def test_688_a_copy_of_a_probe_created_in_a_merge_gets_no_origin_finding(target, touched):
    """AC (e): measured before the fix, p2 read weakened, "does not create p2.yml but records a copy from p1.yml".

    The source keeps its own verdict: weakened, naming the merge that created it, when no plain commit
    lists it (SEC-101; uncommitted before #709), and weakened with an incomplete history when a later
    commit does (#702).
    """
    blob = _blob(target)
    _, merge = _merge_side(target, in_merge=lambda: target.write_probe(make_probe(derived_from=blob)))
    later = _touch(target, P1_REL) if touched else None
    created = _template_copy(target)
    assert ra.Git(target.path).file_history(P2_REL)[0] == (created, P2_REL)
    code, report = run_audit(target)
    assert code == ra.EXIT_FINDINGS, report
    new = row_of(report, "p2")
    assert new[1] == ra.REACHED and new[7] == ra.STATE_CLEAN, new
    old = row_of(report, "p1")
    if touched:
        assert old[7] == ra.STATE_WEAKENED and _plain(old[9]) == "weakened: " + _incomplete(later, P1_REL), old
    else:
        assert old[7] == ra.STATE_WEAKENED and _plain(old[9]) == "weakened: " + _created_in_merge(merge), old


@pytest.mark.parametrize("new_id", [False, True])
def test_688_a_weakened_probe_re_added_at_its_path_as_a_copy_is_not_read_as_fresh(target, new_id):
    """Delete-and-re-add keeps the history; re-added as a copy, git walks into the source instead of the path.

    Under the old id, the id is not new at the copy, so the walk goes on. Under
    a new id, the path's earlier revisions are not in the listed history, so the
    probe fails closed instead of starting clean at the copy.
    """
    rel = P1_REL
    # One commit, so git pairs neither with the other and p3's history holds no revision of p1.
    blob = _blob(target)
    _approve_together(target, make_probe("p1", derived_from=blob), make_probe("p3", derived_from=blob))
    _weaken(target, rel)
    target.commit("lower p1's bar")
    target.git("rm", "-q", rel)
    removal = target.commit("drop p1")
    pid = "p9" if new_id else "p1"
    target.write_probe(make_probe(pid, derived_from=_blob(target)), name="p1")
    readded = target.commit("re-add p1.yml from p3's text")
    assert _status_of(target, rel, readded) == ("C", "project/reach-probes/p3.yml")
    state, reason = _state(target, pid)
    assert state == ra.STATE_WEAKENED, reason
    assert not new_id or (f"the probe was created in {readded[:12]} as a copy of project/reach-probes/p3.yml at "
                          f"{rel}, which "
            f"already held a file in {removal[:12]}") in reason, reason


def test_688_a_copy_that_takes_the_source_s_id_keeps_the_source_s_history(target):
    """The weakened p1 copied to a new file under its own id, then the old file dropped: the same probe, moved."""
    _, rel = derived_probe(target)
    _weaken(target, rel)
    target.commit("lower p1's bar")
    moved = "project/reach-probes/moved.yml"
    target.write(moved, (target.path / rel).read_text())
    copied = target.commit("copy p1 under its own id")
    assert _status_of(target, moved, copied) == ("C", rel)
    target.git("rm", "-q", rel)
    target.commit("drop the old file")
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED, reason


# Security review of #688: a copy ends the history only when its id is new there.
LONG_ARGV = [PY, "-c", "import sys; print(3)  # decoy observation step with a long distinctive tail " + "x" * 120]
PROBES = "project/reach-probes"


def test_688_SEC1_an_id_hidden_behind_a_re_created_source_path_is_not_new_and_keeps_its_history(target):
    """Measured before the fix: xid read clean, exit 0 (origin/develop: weakened, exit 4).

    p.yml carried xid at c1 and was dropped; c3 re-creates p.yml as a tid
    variant, so --follow on p.yml stops at c3 and never lists the xid revision.
    The lowered xid copied from it at c4 carries an id a probe file carried
    before, so the copy does not end its history.
    """
    d = _blob(target)
    target.write_probe(make_probe("xid", derived_from=d), name="p")
    target.write_probe(make_probe("tid", derived_from=d), name="t")
    target.commit("c1")
    target.git("rm", "-q", f"{PROBES}/p.yml")
    target.commit("c2")
    target.write_probe(make_probe("tid", derived_from=d, argv=LONG_ARGV), name="p")
    target.commit("c3")
    target.write_probe(make_probe("xid", derived_from=d, argv=LONG_ARGV,
                                  expected={"kind": "count", "value": 1, "unit": "collections"}), name="Y")
    c4 = target.commit("c4")
    assert _status_of(target, f"{PROBES}/Y.yml", c4) == ("C", f"{PROBES}/p.yml"), "git no longer pairs the copy"
    target.git("rm", "-q", f"{PROBES}/p.yml")
    target.commit("c5")
    code, report = run_audit(target)
    assert code != ra.EXIT_OK, report
    assert row_of(report, "xid")[7] != ra.STATE_CLEAN, row_of(report, "xid")


@pytest.mark.parametrize("from_template", [False, True])
def test_688_SEC2_a_re_created_id_moved_back_onto_its_old_path_stays_weakened(target, from_template):
    """c1 W.yml carries xid; c2 drops it; c3 adds Y.yml with xid lowered (from_template: as a copy of the
    untouched template probe t.yml); c4 renames Y.yml to W.yml. A regression guard: never clean."""
    d = _blob(target)
    target.write_probe(make_probe("xid", derived_from=d), name="W")
    if from_template:
        target.write_probe(make_probe("tid", derived_from=d), name="t")
    target.commit("c1")
    target.git("rm", "-q", f"{PROBES}/W.yml")
    target.commit("c2")
    target.write_probe(make_probe("xid", derived_from=d, expected={"kind": "count", "value": 1, "unit": "collections"}),
                       name="Y")
    c3 = target.commit("c3")
    if from_template:
        assert _status_of(target, f"{PROBES}/Y.yml", c3) == ("C", f"{PROBES}/t.yml"), "git no longer pairs the copy"
    target.git("mv", f"{PROBES}/Y.yml", f"{PROBES}/W.yml")
    target.commit("c4")
    code, report = run_audit(target)
    assert code == ra.EXIT_FINDINGS, report
    assert row_of(report, "xid")[7] == ra.STATE_WEAKENED, row_of(report, "xid")


def test_688_SEC1_a_copy_merged_in_from_a_side_branch_stays_clean(target):
    """A --no-ff merge writes p2 (it differs from main's parent), after the copy: that write keeps p2's id new."""
    derived_probe(target)
    side, merge = _merge_side(target, on_side=lambda: target.write_probe(make_probe("p2", derived_from=_blob(target))))
    assert _status_of(target, P2_REL, side) == ("C", P1_REL), "git no longer pairs the copy"
    history = ra.probe_set_history(ra.Git(target.path), yaml, target.git("rev-parse", "HEAD"))
    assert (merge, P2_REL) in history.writes["p2"], history.writes["p2"]
    code, report = run_audit(target)
    assert code == ra.EXIT_OK, report
    assert row_of(report, "p2")[7] == ra.STATE_CLEAN


# Second security review of #688: a backdated side commit hides behind the creating copy or rename.
LOW = {"kind": "count", "value": 1, "unit": "collections"}


def _backdated_lowering(target: Target, created: str, rel: str) -> str:
    """On a side branch from ``created``, lower the bar of ``rel`` in a commit dated a day before
    ``created``, then merge it back with --no-ff; returns the lowering commit."""
    target.git("switch", "-q", "-c", "side", created)
    data = yaml.safe_load((target.path / rel).read_text())
    data["expected"] = dict(LOW)
    target.write(rel, yaml.safe_dump(data, sort_keys=False))
    target.git("add", "-A")
    when = f"@{int(target.git('log', '-1', '--format=%ct', created)) - 86400}"
    subprocess.run(["git", "-C", str(target.path), "commit", "-q", "-m", "D"], check=True,
                   env={**os.environ, "GIT_COMMITTER_DATE": when, "GIT_AUTHOR_DATE": when})
    lowering = target.git("rev-parse", "HEAD")
    target.git("switch", "-q", "-")
    target.git("merge", "-q", "--no-ff", "-m", "M", "side")
    return lowering


def test_688_SEC3_a_backdated_lowering_after_a_copy_is_listed_and_weakens_the_copy(target):
    """Measured before the fix (git 2.53): file_log(y.yml) listed only the copy and q's A; xid read clean, exit 0."""
    d = _blob(target)
    target.write_probe(make_probe("qid", derived_from=d), name="q")
    target.commit("c0")
    target.write_probe(make_probe("xid", derived_from=d), name="y")
    created = target.commit("C")
    y = f"{PROBES}/y.yml"
    assert _status_of(target, y, created) == ("C", f"{PROBES}/q.yml"), "git no longer pairs the copy"
    lowering = _backdated_lowering(target, created, y)
    assert lowering in [c for c, _, _, _ in ra.Git(target.path).file_log(y)]
    code, report = run_audit(target)
    assert code == ra.EXIT_FINDINGS, report
    row = row_of(report, "xid")
    assert row[7] == ra.STATE_WEAKENED, row
    assert (f"probe changed in {lowering[:12]} after its derivation was recorded in {created[:12]}"
            in _plain(row[9])), row[9]


def test_688_SEC3_a_backdated_lowering_after_a_rename_names_the_lowering(target):
    """Before the fix the rename variant read weakened only by accident: the lowering was not listed."""
    d = _blob(target)
    target.write_probe(make_probe("xid", derived_from=d), name="w")
    target.commit("c0")
    y = f"{PROBES}/y.yml"
    target.git("mv", f"{PROBES}/w.yml", y)
    renamed = target.commit("C'")
    assert _status_of(target, y, renamed) == ("R", f"{PROBES}/w.yml")
    lowering = _backdated_lowering(target, renamed, y)
    assert lowering in [c for c, _, _, _ in ra.Git(target.path).file_log(y)]
    state, reason = _state(target, "xid")
    assert state == ra.STATE_WEAKENED and "probe changed in " in reason and lowering[:12] in reason, reason


def test_688_SEC3_a_change_the_walk_does_not_list_is_reported_as_an_incomplete_history(target, monkeypatch):
    """Defense in depth: with the walk back in committer-date order, the probe-set history still sees D."""
    real = ra.Git.out

    def date_ordered(self, *args):
        return real(self, *(a for a in args if a != "--topo-order"))

    monkeypatch.setattr(ra.Git, "out", date_ordered)
    d = _blob(target)
    target.write_probe(make_probe("qid", derived_from=d), name="q")
    target.commit("c0")
    target.write_probe(make_probe("xid", derived_from=d), name="y")
    created = target.commit("C")
    y = f"{PROBES}/y.yml"
    lowering = _backdated_lowering(target, created, y)
    assert lowering not in [c for c, _, _, _ in ra.Git(target.path).file_log(y)]
    code, report = run_audit(target)
    assert code == ra.EXIT_FINDINGS, report
    row = row_of(report, "xid")
    assert row[7] == ra.STATE_WEAKENED, row
    # Since #709 (K5) the write lies off HEAD's first-parent line, so the reason names the merge that took it in.
    assert (f"changed the probe against its first parent after {lowering[:12]} changed {y} under the id xid on a "
            "merged line the probe's history walk does not list" in _plain(row[9])), row[9]


@pytest.mark.parametrize("rename_back", [False, True])
def test_688_SEC3_a_weakened_id_re_created_elsewhere_and_moved_back_onto_its_path_is_not_clean(target, rename_back):
    """y.yml carries xid, lowered, then dropped; w.yml re-creates xid; a re-derivation after a real
    declaration change moves it back onto y.yml. --follow stops at w.yml, so y.yml's earlier xid
    revisions are unlisted: without the move it's an exchange under the same id (#706), with it the
    listed history is incomplete."""
    y, w = f"{PROBES}/y.yml", f"{PROBES}/w.yml"
    target.write_probe(make_probe("xid", derived_from=_blob(target)), name="y")
    target.commit("approve xid")
    _weaken(target, y)
    target.commit("lower xid's bar")
    target.git("rm", "-q", y)
    target.commit("drop y.yml")
    target.write_probe(make_probe("xid", derived_from=_blob(target)), name="w")
    target.commit("re-create xid in w.yml")
    target.write(DECL, "# Requirements\n\n## Export\n\nExports 3 collections, reworded.\n")
    target.commit("change the declaration")
    if rename_back:
        target.git("mv", w, y)
    _rewrite(target, y if rename_back else w, derived_from=_blob(target))
    moved = target.commit("re-derive xid" + (" back at y.yml" if rename_back else ""))
    if rename_back:
        assert [s for c, _, s, _ in ra.Git(target.path).file_log(y) if c == moved] == ["R"]
    code, report = run_audit(target)
    assert code == ra.EXIT_FINDINGS, report
    if rename_back:
        row = row_of(report, "xid")
        assert row[7] == ra.STATE_WEAKENED, row
        assert f"changed {y} under the id xid, but the probe's history walk does not list it" in _plain(row[9]), row
    else:
        assert "exchange under the same id" in report, report


# Third security review of #688 (SEC-R3-2): a commit anchor moved back, then forward across a
# declaration change the probe had already seen, re-baselined a lowered bar.
HI = {"kind": "count", "value": 3, "unit": "collections"}


def test_688_SECR3_2_a_backward_commit_anchor_jump_cannot_re_baseline_a_lowering(sha256_target):
    """Measured before the fix (also on origin/develop): yid read clean, exit 0."""
    target = sha256_target
    d0 = target.git("rev-parse", "HEAD")
    target.write(DECL, "# Requirements\n\n## Export\n\nExports 3 collections and more.\n")
    d = target.commit("D decl change")
    target.write_probe(make_probe("yid", derived_from=d, expected=dict(HI)), name="y")
    target.commit("B0")
    target.write_probe(make_probe("yid", derived_from=d0, expected=dict(HI)), name="y")
    back = target.commit("b1 anchor back to D0")
    target.write_probe(make_probe("yid", derived_from=d, expected=dict(LOW)), name="y")
    lowered = target.commit("b2 anchor D, lowered")
    code, report = run_audit(target)
    assert code == ra.EXIT_FINDINGS, report
    row = row_of(report, "yid")
    assert row[1] == ra.NOT_PROBED and row[7] == ra.STATE_WEAKENED, row
    assert _plain(row[9]) == (
        f"weakened: re-baselined without a declaration change: {lowered[:12]} moved derived_from from "
        f"{d0[:12]} to {d[:12]}, but the content of {DECL} at the previous derived_from {d0[:12]} is not its "
        f"content at {back[:12]}, where it was recorded, so no declaration change can be shown"), row[9]


def test_688_SECR3_2_a_commit_anchored_re_derivation_after_a_real_declaration_change_stays_clean(sha256_target):
    """Positive control: the previous anchor is the declaration where it was recorded, and it changed since."""
    target = sha256_target
    derived_probe(target)
    target.write(DECL, "# Requirements\n\n## Export\n\nExports 3 collections, reworded.\n")
    moved = target.commit("change the declaration")
    _rewrite(target, P1_REL, derived_from=moved)
    target.commit("re-derive at the declaration change")
    code, report = run_audit(target)
    assert code == ra.EXIT_OK, report
    assert row_of(report, "p1")[7] == ra.STATE_CLEAN


def test_688_SECR3_2_a_forward_commit_anchor_jump_without_a_declaration_change_reads_as_before(sha256_target):
    """Unchanged by the fix: the forward move over no declaration change is refused as it was."""
    target = sha256_target
    sha, _ = derived_probe(target)
    target.write("unrelated.txt", "x\n")
    later = target.commit("unrelated work")
    _rewrite(target, P1_REL, derived_from=later, expected_value=1)
    moved = target.commit("re-anchor forward and lower the bar")
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED, reason
    assert reason.startswith(f"weakened: re-baselined without a declaration change: {moved[:12]} moved derived_from "
                             f"from {sha[:12]} to {later[:12]}, but {DECL} did not change in between"), reason


# -- #688 SEC-R4: a move onto a commit anchor in a SHA-1 repository ----------- #
def _commit_move_reason(target: Target) -> str:
    code, report = run_audit(target)
    row = row_of(report, "yid")
    assert code == ra.EXIT_FINDINGS and row[7] == ra.STATE_WEAKENED, row
    return _plain(row[9])


def test_688_SECR4_a_commit_anchored_re_derivation_after_a_real_declaration_change_is_refused(target):
    """Since v1.1 a re-derivation records a content anchor; a commit anchor is only a migration rule."""
    x = target.git("rev-parse", "HEAD")
    target.write_probe(make_probe("yid", derived_from=x, expected=dict(HI)), name="y")
    target.commit("record")
    target.write(DECL, "# Requirements\n\n## Export\n\nExports 3 collections, reworded.\n")
    changed = target.commit("change the declaration")
    target.write_probe(make_probe("yid", derived_from=changed, expected=dict(HI)), name="y")
    moved = target.commit("re-derive onto a commit anchor")
    assert _commit_move_reason(target) == (
        f"weakened: re-baselined without a declaration change: {moved[:12]} moved derived_from from {x[:12]} "
        f"to {changed[:12]}, but {COMMIT_MOVE_REFUSED}")


def test_688_SECR4_the_same_re_derivation_onto_a_content_anchor_is_clean(target):
    """Positive control: the recovery the refusal names."""
    x = target.git("rev-parse", "HEAD")
    target.write_probe(make_probe("yid", derived_from=x, expected=dict(HI)), name="y")
    target.commit("record")
    target.write(DECL, "# Requirements\n\n## Export\n\nExports 3 collections, reworded.\n")
    target.commit("change the declaration")
    target.write_probe(make_probe("yid", derived_from=_blob(target), expected=dict(HI)), name="y")
    target.commit("re-derive onto a content anchor")
    code, report = run_audit(target)
    assert code == ra.EXIT_OK and row_of(report, "yid")[7] == ra.STATE_CLEAN, report


def test_688_SECR4_a_declaration_path_re_pointed_at_a_decoy_cannot_prove_a_move(target):
    """Measured before the fix (also on origin/develop): clean, exit 0. The decoy changed, DECL never did."""
    x = target.git("rev-parse", "HEAD")
    target.write_probe(make_probe("yid", derived_from=x, expected=dict(HI)), name="y")
    target.commit("record")
    target.write_probe(make_probe("yid", derived_from=x, path="decoy.txt", expected=dict(HI)), name="y")
    target.commit("re-point the declaration only")
    target.write_probe(make_probe("yid", derived_from=x[:12], path="decoy.txt", expected=dict(HI)), name="y")
    target.commit("abbreviate the anchor, a run of its own")
    target.write("decoy.txt", "b\n")
    edit = target.commit("edit the decoy")
    target.write_probe(make_probe("yid", derived_from=edit, path="decoy.txt", expected=dict(LOW)), name="y")
    target.commit("move the anchor and lower")
    assert _commit_move_reason(target).endswith(COMMIT_MOVE_REFUSED)


def test_688_SECR4_a_rename_that_is_restored_cannot_prove_a_move(target):
    """Measured before the fix: clean, exit 0. The original declaration is back, unchanged and unwatched."""
    x = target.git("rev-parse", "HEAD")
    target.write_probe(make_probe("yid", derived_from=x, expected=dict(HI)), name="y")
    target.commit("record")
    target.git("mv", DECL, "docs/y.md")
    renamed = target.commit("rename")
    target.write(DECL, "# Requirements\n\n## Export\n\nExports 3 collections.\n")
    target.commit("restore the original")
    target.write_probe(make_probe("yid", derived_from=renamed, path="docs/y.md", expected=dict(LOW)), name="y")
    target.commit("follow the rename and lower")
    assert _commit_move_reason(target).endswith(COMMIT_MOVE_REFUSED)


def test_688_SECR4_an_edit_that_is_reverted_cannot_prove_a_move(target):
    """Measured before the fix: clean, exit 0. The declaration was touched, not changed."""
    x = target.git("rev-parse", "HEAD")
    target.write_probe(make_probe("yid", derived_from=x, expected=dict(HI)), name="y")
    target.commit("record")
    target.write(DECL, "tmp\n")
    target.commit("edit")
    target.write(DECL, "# Requirements\n\n## Export\n\nExports 3 collections.\n")
    reverted = target.commit("revert")
    target.write_probe(make_probe("yid", derived_from=reverted, expected=dict(LOW)), name="y")
    target.commit("move onto the revert and lower")
    assert _commit_move_reason(target).endswith(COMMIT_MOVE_REFUSED)


def test_688_SECR4_a_commit_anchor_absent_at_both_commits_proves_nothing(sha256_target):
    """A path holding no declaration where the previous anchor points can't prove that anchor."""
    target = sha256_target
    x = target.git("rev-parse", "HEAD")
    target.write_probe(make_probe("yid", derived_from=x, path="ghost.md", expected=dict(HI)), name="y")
    target.commit("record against a missing file")
    target.write("ghost.md", "now it exists\n")
    created = target.commit("create the file")
    target.write_probe(make_probe("yid", derived_from=created, path="ghost.md", expected=dict(LOW)), name="y")
    target.commit("move the anchor and lower")
    state, reason = _state(target, "yid")
    assert state == ra.STATE_WEAKENED, reason
    assert f"ghost.md did not exist at the previous derived_from {x[:12]}, so no declaration change" in reason


# -- #688 SEC-R5: a historical move onto a commit anchor, reached by a later migration ---------- #
RESTORED = "# Requirements\n\n## Export\n\nExports 3 collections.\n"


def _migrate_onto_content(target: Target, path: str = DECL, **kw) -> str:
    target.write_probe(make_probe("yid", derived_from=_blob(target, path=path), path=path, **kw), name="y")
    return target.commit("migrate onto a content anchor, nothing else")


def test_688_SECR5_an_edit_reverted_then_migrated_cannot_launder_a_lowering(target):
    """Measured before the fix: clean, exit 0. The commit move lowers; the migration makes it historical."""
    c0 = target.git("rev-parse", "HEAD")
    target.write_probe(make_probe("yid", derived_from=c0, expected=dict(HI)), name="y")
    target.commit("record")
    target.write(DECL, "tmp\n")
    target.commit("edit")
    target.write(DECL, RESTORED)
    reverted = target.commit("revert")
    target.write_probe(make_probe("yid", derived_from=reverted, expected=dict(LOW)), name="y")
    lowered = target.commit("move onto the revert and lower")
    _migrate_onto_content(target, expected=dict(LOW))
    reason = _commit_move_reason(target)
    assert reason.endswith(f"but its previous derivation was no re-derivation either: {lowered[:12]} moved "
                           f"derived_from from {c0[:12]} to {reverted[:12]}, but the content of {DECL} did not "
                           "change in between, and a re-anchoring may change nothing but derived_from and the "
                           "approval"), reason


def test_688_SECR5_a_rename_restored_then_migrated_cannot_launder_a_lowering(target):
    c0 = target.git("rev-parse", "HEAD")
    target.write_probe(make_probe("yid", derived_from=c0, expected=dict(HI)), name="y")
    target.commit("record")
    target.git("mv", DECL, "docs/y.md")
    renamed = target.commit("rename")
    target.write(DECL, RESTORED)
    target.commit("restore the original")
    target.write_probe(make_probe("yid", derived_from=renamed, path="docs/y.md", expected=dict(LOW)), name="y")
    target.commit("follow the rename and lower")
    _migrate_onto_content(target, path="docs/y.md", expected=dict(LOW))
    # #708 round 3: the restored original is still at the move commit, so the move is no rename at all,
    # which is refused before the pure-move check could see the lowering.
    reason = _commit_move_reason(target)
    assert reason.endswith(f"but it also moved the declaration from {DECL} to docs/y.md, and only a pure move of an "
                           "unchanged declaration, the old path gone, can change its path"), reason


def test_688_SECR5_a_decoy_path_then_migrated_cannot_launder_a_lowering(target):
    target.write("decoy.txt", "a\n")
    c0 = target.commit("the decoy exists at the anchor")
    target.write_probe(make_probe("yid", derived_from=c0, expected=dict(HI)), name="y")
    target.commit("record")
    target.write_probe(make_probe("yid", derived_from=c0, path="decoy.txt", expected=dict(HI)), name="y")
    repoint = target.commit("re-point the declaration only")
    target.write("decoy.txt", "b\n")
    edit = target.commit("edit the decoy")
    target.write_probe(make_probe("yid", derived_from=edit, path="decoy.txt", expected=dict(LOW)), name="y")
    target.commit("move the anchor and lower")
    _migrate_onto_content(target, path="decoy.txt", expected=dict(LOW))
    reason = _commit_move_reason(target)
    assert f"the probe changed in {repoint[:12]} after its previous derivation was recorded" in reason, reason


def test_688_SECR5_a_squash_re_anchoring_then_migrated_stays_clean(target):
    """Positive control: a re-anchoring onto the squash commit, content and probe unchanged, then a migration."""
    _squash_lost_commit_anchor(target, probe_on_main=False)
    squash = target.git("rev-parse", "HEAD")
    rel = "project/reach-probes/p1.yml"
    _rewrite(target, rel, derived_from=squash, approval=_restamp(target, rel))
    target.commit("re-anchor onto the squash commit")
    _rewrite(target, rel, derived_from=_blob(target), approval=_restamp(target, rel))
    target.commit("migrate onto a content anchor")
    _assert_clean(target)


def test_688_SECR5_the_migration_gate_routes_a_commit_move_to_a_re_derivation(target, capsys):
    """Unlike any other weakening, re-deriving onto a content or section anchor heals it."""
    x = target.git("rev-parse", "HEAD")
    target.write_probe(make_probe("p1", derived_from=x))
    target.commit("record")
    target.write(DECL, "# Requirements\n\n## Export\n\nExports 3 collections, reworded.\n")
    changed = target.commit("change the declaration")
    target.write_probe(make_probe("p1", derived_from=changed))
    target.commit("re-derive onto a commit anchor")
    code, out = _check_migration(target, capsys)
    assert code == ra.EXIT_MIGRATION_REFUSED
    assert f"route: {ra.ROUTE_REDERIVE}" in out and ra.ROUTE_WEAKENED not in out, out


def test_688_SECR5_an_unresolvable_commit_anchor_in_a_sha256_repository_keeps_the_old_rules(sha256_target):
    """The SHA-1 refusal names a content anchor that a SHA-256 repository doesn't have."""
    target = sha256_target
    x = target.git("rev-parse", "HEAD")
    target.write_probe(make_probe("yid", derived_from=x, expected=dict(HI)), name="y")
    target.commit("record")
    target.write_probe(make_probe("yid", derived_from="f" * 64, expected=dict(HI)), name="y")
    target.commit("move onto a commit that does not resolve")
    _, reason = _state(target, "yid")
    assert ra.REASON_COMMIT_MOVE not in reason, reason


def test_688_SECR6_a_decoy_path_and_back_cannot_launder_a_lowering(target):
    """Measured before the fix: clean, exit 0. Comparing two files' contents read the decoy as a change."""
    target.write("README.txt", "q\n")
    a = target.commit("an unrelated file")
    target.write_probe(make_probe("yid", derived_from=a, expected=dict(HI)), name="y")
    c1 = target.commit("record")
    target.write_probe(make_probe("yid", derived_from=c1, path="README.txt", expected=dict(LOW)), name="y")
    target.commit("move onto the decoy and lower")
    target.write_probe(make_probe("yid", derived_from=a, expected=dict(LOW)), name="y")
    back = target.commit("move back onto the declaration")
    _migrate_onto_content(target, expected=dict(LOW))
    reason = _commit_move_reason(target)
    # The walk refuses the newest of the two path moves first.
    assert (f"{back[:12]} moved derived_from from {c1[:12]} to {a[:12]}, but it also moved the declaration "
            f"from README.txt to {DECL}, and only a pure move of an unchanged declaration, the old path gone, can "
            "change its path") in reason, reason


def test_688_SECR6_a_pure_rename_under_a_commit_anchor_then_migrated_stays_clean(target):
    """Positive control: an earlier move that followed a rename and changed nothing else heals by re-deriving."""
    c0 = target.git("rev-parse", "HEAD")
    target.write_probe(make_probe("yid", derived_from=c0, expected=dict(HI)), name="y")
    target.commit("record")
    target.git("mv", DECL, "docs/y.md")
    renamed = target.commit("rename")
    target.write_probe(make_probe("yid", derived_from=renamed, path="docs/y.md", expected=dict(HI)), name="y")
    target.commit("follow the rename")
    _migrate_onto_content(target, path="docs/y.md", expected=dict(HI))
    code, report = run_audit(target)
    assert code == ra.EXIT_OK and row_of(report, "yid")[7] == ra.STATE_CLEAN, report


# -- #688 SEC-R7: a rename that also changes the anchor form; a switch of declaration kind ------ #
NEW_DECL = "docs/new.md"


def _renamed_and_relabelled(target: Target, rel: str, form: str, **changes) -> str:
    target.git("mv", DECL, NEW_DECL)
    target.commit("rename the declaration")
    doc = yaml.safe_load((target.path / rel).read_text())
    doc["declaration"]["path"] = NEW_DECL
    if form == "blob":
        doc["declaration"].pop("sections", None)
        doc["derived_from"] = _blob(target, path=NEW_DECL)
    else:
        sections = _sections_now(target, path=NEW_DECL)
        doc["declaration"]["sections"] = sections
        doc["derived_from"] = ra.section_anchor(sections)
    if "expected_value" in changes:
        doc["expected"]["value"] = changes["expected_value"]
    target.write(rel, yaml.safe_dump(doc, sort_keys=False))
    return target.commit("follow the rename onto another anchor form")


@pytest.mark.parametrize(("start", "form"), [("commit", "blob"), ("commit", "sections"), ("blob", "sections"),
                                             ("sections", "blob")])
def test_688_SECR7_a_rename_with_another_anchor_form_cannot_lower_the_bar(sectioned, start, form):
    """Measured before the fix (also on origin/develop): clean, exit 0, the declaration unchanged."""
    target = sectioned
    if start == "commit":
        _, rel = derived_probe(target)
    elif start == "blob":
        rel = _content_probe(target)
    else:
        rel = _section_probe(target)
    moved = _renamed_and_relabelled(target, rel, form, expected_value=1)
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED, reason
    assert reason.startswith(f"weakened: re-baselined without a declaration change: {moved[:12]} moved"), reason
    assert reason.endswith("but the same commit changed the probe beyond declaration.path, which a pure move of "
                           "the declaration does not justify"), reason


@pytest.mark.parametrize(("start", "form"), [("blob", "sections"), ("sections", "blob")])
def test_688_SECR7_a_rename_with_another_anchor_form_and_nothing_else_stays_clean(sectioned, start, form):
    """Positive control: the honest rename-and-re-derive."""
    target = sectioned
    rel = _content_probe(target) if start == "blob" else _section_probe(target)
    _renamed_and_relabelled(target, rel, form)
    _assert_clean(target)


def test_688_SECR7_a_switch_from_an_inherited_spec_to_a_file_is_no_re_derivation(target):
    """Measured before the fix (also on origin/develop): clean, exit 0, with the config restored afterwards."""
    _spec_config(target, ("nolte-shared", "v0.1.8"))
    _inherited_probe(target, "v0.1.8")
    target.commit("probe")
    parent = target.git("rev-parse", "HEAD")
    _spec_config(target, ("nolte-shared", parent))
    target.write_probe(make_probe(derived_from=parent, expected=dict(LOW)))
    target.commit("move the pin, switch to a file anchor, lower")
    _spec_config(target, ("nolte-shared", "v0.1.8"))
    target.commit("restore the pin")
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED, reason
    assert reason.endswith(f"but it also changed which declaration the probe anchors on (project/rest-api-design "
                           f"to {DECL}), which no re-derivation can show; derive a new probe instead"), reason


# -- #688 SEC-R8: a declaration renamed away and the probe re-pointed; a symlink declaration ---- #
def test_688_SECR8_a_declaration_renamed_away_cannot_justify_a_re_point_at_a_changed_file(target):
    """Measured before the fix (also on origin/develop): clean, exit 0, the content kept under another path."""
    rel = _content_probe(target)
    target.git("mv", DECL, "docs/c.md")
    target.write("README.txt", "new\n")
    _rewrite(target, rel, declaration_path="README.txt", derived_from="blob:" + target.git("hash-object", "README.txt"),
             expected_value=1)
    target.commit("rename the declaration away, re-point at a changed file, lower")
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED, reason
    assert (f"but it also moved the declaration from {DECL} to README.txt, where the previously anchored content "
            "is not; record the rename as a pure move first, then re-derive") in reason, reason


def test_688_SECR8_a_rename_with_an_edit_in_one_commit_is_refused(target):
    """The honest flow takes two commits; in one, it can't be told from the shape above."""
    rel = _content_probe(target)
    target.git("mv", DECL, "docs/v2.md")
    target.write("docs/v2.md", "# Requirements\n\n## Export\n\nExports 3 collections, v2.\n")
    _rewrite(target, rel, declaration_path="docs/v2.md", derived_from=_blob_now(target, "docs/v2.md"))
    target.commit("rename, edit and re-derive at once")
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED and "record the rename as a pure move first, then re-derive" in reason


def _blob_now(target: Target, path: str) -> str:
    return "blob:" + target.git("hash-object", path)


def test_688_SECR8_a_symlink_declaration_is_no_file_to_anchor_on(target):
    """Measured before the fix (also on origin/develop): clean, exit 0; the link text never changes."""
    rel = _content_probe(target)
    target.git("mv", DECL, "docs/c.md")
    os.symlink("c.md", target.path / DECL)
    target.git("add", DECL)
    _rewrite(target, rel, derived_from="blob:" + target.git("rev-parse", f":{DECL}"), expected_value=1)
    target.commit("replace the declaration by a symlink, anchor on the link text, lower")
    state, _ = _state(target)
    assert state == ra.STATE_WEAKENED


def test_688_SECR8_a_symlink_declaration_at_head_reads_not_a_regular_file(target):
    rel = _content_probe(target)
    target.git("mv", DECL, "docs/c.md")
    os.symlink("c.md", target.path / DECL)
    target.git("add", DECL)
    target.commit("replace the declaration by a symlink")
    assert rel
    state, reason = _state(target)
    assert state == ra.STATE_STALE and reason.endswith(f"{DECL} is not a regular file at HEAD"), reason


def _stale_from_its_first_commit(target: Target, **kw) -> tuple[str, str]:
    """Derived against the declaration's old content, committed after the declaration changed (a squash, say)."""
    old = _blob(target)
    target.write(DECL, "# Requirements\n\n## Export\n\nExports 3 collections, changed on develop.\n")
    target.commit("the declaration changes before the probe lands")
    rel = target.write_probe(make_probe(derived_from=old, **kw))
    target.commit("the probe lands")
    return old, rel


def test_688_SECR8_a_probe_stale_from_its_first_commit_heals_by_re_deriving(target):
    """Before the fix the re-derivation the stale route names read weakened, healable only by a supersede."""
    _, rel = _stale_from_its_first_commit(target)
    assert _state(target)[0] == ra.STATE_STALE
    _rewrite(target, rel, derived_from=_blob(target), approval=_restamp(target, rel))
    target.commit("re-derive against the declaration as it landed")
    _assert_clean(target)


def test_688_SECR8_a_probe_stale_from_its_first_commit_cannot_lower_the_bar_by_re_deriving(target):
    _, rel = _stale_from_its_first_commit(target)
    _rewrite(target, rel, derived_from=_blob(target), expected_value=1)
    target.commit("re-derive and lower")
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED and f"but {DECL} did not change in between" in reason, reason


# -- #688 SEC-R9: a copy beside an edited original is no rename; a stale-born section anchor ------ #
def test_688_SECR9_a_copy_of_the_old_content_beside_an_edited_original_is_no_rename(target):
    """Measured before the fix: clean, exit 0; the probe never saw the edit."""
    rel = _content_probe(target)
    old = (target.path / DECL).read_text()
    target.write(DECL, "# Requirements\n\n## Export\n\nExports 3 collections, edited.\n")
    target.commit("edit the declaration")
    target.write("docs/b.md", old)
    _rewrite(target, rel, declaration_path="docs/b.md")
    moved = target.commit("copy the old content and point the probe at it")
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED, reason
    assert reason.endswith(f"and that is no rename: {DECL} still exists at {moved[:12]} or docs/b.md already "
                           f"existed at {target.git('rev-parse', 'HEAD~2')[:12]}, where the previous derivation "
                           "was recorded"), reason


def test_688_SECR9_a_section_anchor_stale_from_its_first_commit_judges_sections_not_the_file(sectioned):
    """Measured before the fix: an edit outside the anchored sections re-baselined a lowering, exit 0."""
    target = sectioned
    sections = _sections_now(target)
    _edit(target, *INSIDE)
    target.commit("an anchored section changes before the probe lands")
    probe = make_probe(derived_from=ra.section_anchor(sections))
    probe["declaration"]["sections"] = sections
    rel = target.write_probe(probe)
    target.commit("the probe lands")
    _edit(target, *OUTSIDE)
    target.commit("an edit outside the anchored sections")
    _rewrite(target, rel, derived_from=_blob(target), expected_value=1)
    doc = yaml.safe_load((target.path / rel).read_text())
    doc["declaration"].pop("sections", None)
    target.write(rel, yaml.safe_dump(doc, sort_keys=False))
    target.commit("re-derive onto the file and lower")
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED, reason


# -- #708: honest recovery flows (delete and restore a probe; edit, then rename the declaration) -- #
def _drop(target: Target, rel: str) -> tuple[str, str]:
    """Delete the probe file in a commit of its own; returns its text and the deleting commit."""
    text = (target.path / rel).read_text()
    (target.path / rel).unlink()
    return text, target.commit("drop the probe")


def test_708_P1_a_probe_deleted_and_restored_unchanged_is_clean(target):
    """Measured before the fix: weakened, the deletion read as a revision with no readable derived_from."""
    rel = _content_probe(target)
    text, _ = _drop(target, rel)
    target.write(rel, text)
    target.commit("restore the probe")
    _assert_clean(target)


def test_708_P1_a_restore_with_a_lowered_bar_is_weakened(target):
    rel = _content_probe(target)
    text, _ = _drop(target, rel)
    target.write(rel, text)
    _rewrite(target, rel, expected_value=1)
    restored = target.commit("restore the probe with a lower bar")
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED, reason
    assert f"probe changed in {restored[:12]} after its derivation was recorded in" in reason, reason


def test_708_P1_a_restore_with_a_moved_anchor_and_no_declaration_change_is_weakened(sectioned):
    """The restore moves the section anchor onto another, unchanged section and lowers the bar."""
    target = sectioned
    rel = _section_probe(target)
    _drop(target, rel)
    probe = make_probe(expected={"kind": "count", "value": 1, "unit": "collections"},
                       derived_from=ra.section_anchor(_sections_now(target, (("heading", "3.2"),))))
    probe["declaration"]["sections"] = _sections_now(target, (("heading", "3.2"),))
    target.write_probe(probe)
    restored = target.commit("restore the probe re-anchored and lowered")
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED, reason
    assert f"{restored[:12]} moved derived_from" in reason, reason
    assert reason.endswith(f"but the anchored sections of {DECL} did not change in between"), reason


def test_708_P1_a_restore_re_derived_after_a_declaration_change_is_clean(target):
    """The restore is judged against the revision before the deletion, as a re-derivation."""
    rel = _content_probe(target)
    text, _ = _drop(target, rel)
    target.write(DECL, "# Requirements\n\n## Export\n\nExports 3 collections, edited.\n")
    target.commit("edit the declaration")
    target.write(rel, text)
    _rewrite(target, rel, derived_from=_blob(target))
    target.commit("restore the probe re-derived")
    _assert_clean(target)


def test_708_P1_two_delete_and_restore_cycles_are_clean(target):
    rel = _content_probe(target)
    for _ in range(2):
        text, _ = _drop(target, rel)
        target.write(rel, text)
        target.commit("restore the probe")
    _assert_clean(target)


def test_708_P1_a_lowered_bar_restored_in_the_second_cycle_is_weakened(target):
    """The first cycle cancels; the second restore is judged against the first restore."""
    rel = _content_probe(target)
    text, _ = _drop(target, rel)
    target.write(rel, text)
    target.commit("restore the probe")
    _drop(target, rel)
    target.write(rel, text)
    _rewrite(target, rel, expected_value=1)
    restored = target.commit("restore the probe with a lower bar")
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED, reason
    assert f"probe changed in {restored[:12]} after its derivation" in reason, reason


def _edited(target: Target, path: str = DECL) -> None:
    target.write(path, "# Requirements\n\n## Export\n\nExports 3 collections, edited.\n")
    target.commit("edit the declaration")


def _rename(target: Target, new: str = "docs/b.md") -> str:
    target.git("mv", DECL, new)
    return target.commit("rename the declaration")


def _re_derive_onto(target: Target, rel: str, new: str = "docs/b.md", **changes) -> str:
    _rewrite(target, rel, declaration_path=new, derived_from=_blob_now(target, new), **changes)
    return target.commit("re-derive onto the renamed declaration")


def test_708_P2_edit_then_rename_then_re_derive_is_clean(target):
    """Measured before the fix: weakened, `record the rename as a pure move first`."""
    rel = _content_probe(target)
    _edited(target)
    _rename(target)
    _re_derive_onto(target, rel)
    _assert_clean(target)


def test_708_P2_rename_then_edit_then_re_derive_is_clean(target):
    rel = _content_probe(target)
    _rename(target)
    _edited(target, "docs/b.md")
    _re_derive_onto(target, rel)
    _assert_clean(target)


def test_708_P2_a_section_anchor_edited_then_renamed_then_re_derived_is_clean(sectioned):
    target = sectioned
    rel = _section_probe(target)
    _edit(target, *INSIDE)
    target.commit("edit an anchored section")
    _rename(target)
    _reanchor(target, rel, declaration_path="docs/b.md")
    target.commit("re-derive onto the renamed declaration")
    _assert_clean(target)


def test_708_P2_a_section_anchor_renamed_with_an_edit_outside_its_sections_and_lowered_is_weakened(sectioned):
    """The anchored sections are unchanged at the new path: only a pure move, which may not lower the bar."""
    target = sectioned
    rel = _section_probe(target)
    _rename(target)
    _edit(target, *OUTSIDE, path="docs/b.md")
    target.commit("edit outside the anchored sections")
    _reanchor(target, rel, declaration_path="docs/b.md", expected_value=1)
    target.commit("re-derive onto the renamed declaration and lower")
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED, reason
    assert reason.endswith("but the same commit changed the probe beyond declaration.path, which a pure move "
                           "of the declaration does not justify"), reason


@pytest.mark.parametrize("again", ["kept", "removed again"])
def test_708_P2_the_old_path_recreated_after_the_rename_is_weakened(target, again):
    rel = _content_probe(target)
    _edited(target)
    _rename(target)
    target.write(DECL, "# Requirements\n\nSomething else.\n")
    target.commit("recreate the old path")
    if again == "removed again":
        (target.path / DECL).unlink()
        target.commit("remove the old path again")
    moved = _re_derive_onto(target, rel, expected_value=1)
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED, reason
    if again == "kept":
        assert f"and that is no rename: {DECL} still exists at {moved[:12]}" in reason, reason
    else:
        assert "where the previously anchored content is not; record the rename as a pure move first" in reason


@pytest.mark.parametrize("shape", ["added in another commit", "added with another blob"])
def test_708_P2_a_new_path_not_added_by_the_removal_with_its_blob_is_weakened(target, shape):
    rel = _content_probe(target)
    _edited(target)
    edited = (target.path / DECL).read_text()
    (target.path / DECL).unlink()
    if shape == "added in another commit":
        target.commit("remove the declaration")
        target.write("docs/b.md", edited)
    else:
        target.write("docs/b.md", edited + "\nAnd more.\n")
    target.commit("add the new declaration")
    _re_derive_onto(target, rel, expected_value=1)
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED, reason
    assert (f"but it also moved the declaration from {DECL} to docs/b.md, where the previously anchored content "
            "is not; record the rename as a pure move first, then re-derive") in reason, reason


def test_708_P2_a_re_point_at_an_unrelated_changed_file_after_a_rename_is_weakened(target):
    rel = _content_probe(target)
    _edited(target)
    _rename(target)
    target.write("README.txt", "new\n")
    _rewrite(target, rel, declaration_path="README.txt", derived_from=_blob_now(target, "README.txt"),
             expected_value=1)
    target.commit("re-point at an unrelated file and lower")
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED, reason
    assert (f"but it also moved the declaration from {DECL} to README.txt, where the previously anchored content "
            "is not") in reason, reason


def test_708_P2_a_rename_with_the_anchored_content_and_other_probe_changes_is_weakened(target):
    """The content at the new path equals what the previous anchor anchored: a pure move, nothing else."""
    rel = _content_probe(target)
    _rename(target)
    _rewrite(target, rel, declaration_path="docs/b.md", expected_value=1)
    target.commit("follow the rename and lower")
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED, reason
    assert reason.endswith("but the same commit changed the probe beyond declaration.path, which a pure move "
                           "of the declaration does not justify"), reason


def test_708_P2_a_rename_before_the_recording_proves_nothing_for_a_later_move(target):
    """The old path was renamed once before the derivation and later dropped in a merge.

    The only plain commit that removed it is that earlier rename, an ancestor of
    the recording: it says nothing about where the declaration went since.
    """
    target.git("branch", "-M", "main")
    target.git("mv", DECL, "docs/b.md")
    target.commit("an early rename")
    target.git("mv", "docs/b.md", DECL)
    target.commit("and back")
    rel = _content_probe(target)
    target.git("checkout", "-q", "-b", "side")
    target.write("side.txt", "side\n")
    target.commit("side work")
    target.git("checkout", "-q", "main")
    target.write("main.txt", "main\n")
    target.commit("main work")
    target.git("merge", "-q", "--no-commit", "--no-ff", "side")
    target.git("rm", "-q", DECL)
    target.write("docs/b.md", "# Requirements\n\n## Export\n\nExports 1 collection.\n")
    target.git("add", "docs/b.md")
    target.git("commit", "-q", "-m", "merge side, dropping the declaration and writing docs/b.md")
    _re_derive_onto(target, rel, expected_value=1)
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED, reason
    assert (f"but it also moved the declaration from {DECL} to docs/b.md, where the previously anchored content "
            "is not") in reason, reason


# -- #708 review: the stale-born section anchor, the new sections, the side-branch removal ------- #
def _stale_born_section_probe(target: Target) -> str:
    """The probe lands with the section digests from before an edit of an anchored section (R0)."""
    sections = _sections_now(target)
    _edit(target, *INSIDE)
    target.commit("an anchored section changes before the probe lands")
    probe = make_probe(derived_from=ra.section_anchor(sections))
    probe["declaration"]["sections"] = sections
    rel = target.write_probe(probe)
    target.commit("the probe lands")
    return rel


def test_708_P2_a_section_anchor_stale_from_its_first_commit_renamed_and_lowered_is_weakened(sectioned):
    """Review finding 1, measured on e65753bc: clean, exit 0. The rename is pure against what R0 held."""
    target = sectioned
    rel = _stale_born_section_probe(target)
    _rename(target)
    _reanchor(target, rel, declaration_path="docs/b.md", expected_value=1)
    target.commit("re-anchor onto the renamed declaration and lower")
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED, reason
    assert reason.endswith("but the same commit changed the probe beyond declaration.path, which a pure move "
                           "of the declaration does not justify"), reason


def test_708_P2_a_stale_born_section_anchor_renamed_onto_a_content_anchor_and_lowered_is_weakened(sectioned):
    """Review finding 1, content-anchor target, measured on e65753bc: clean, exit 0."""
    target = sectioned
    rel = _stale_born_section_probe(target)
    _rename(target)
    _rewrite(target, rel, declaration_path="docs/b.md", derived_from=_blob_now(target, "docs/b.md"),
             expected_value=1)
    doc = yaml.safe_load((target.path / rel).read_text())
    doc["declaration"].pop("sections", None)
    target.write(rel, yaml.safe_dump(doc, sort_keys=False))
    target.commit("re-derive onto the renamed file and lower")
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED, reason
    assert reason.endswith("but the same commit changed the probe beyond declaration.path, which a pure move "
                           "of the declaration does not justify"), reason


def test_708_P2_a_rename_re_derived_onto_only_unchanged_sections_and_lowered_is_weakened(sectioned):
    """Review finding 2, measured on e65753bc: clean, exit 0. The edited row is dropped from the anchor."""
    target = sectioned
    rel = _section_probe(target)
    _rename(target)
    _edit(target, *IN_ROW, path="docs/b.md")
    target.commit("edit the anchored row")
    _reanchor(target, rel, declaration_path="docs/b.md", locators=[("heading", "3.1")], expected_value=1)
    moved = target.commit("re-anchor onto the unchanged heading only and lower")
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED, reason
    assert f"{moved[:12]} moved derived_from" in reason, reason
    assert reason.endswith("but none of the sections it now anchors on changed since the previous derivation "
                           f"was recorded in {target.git('rev-parse', 'HEAD~3')[:12]}"), reason


def test_708_P2_a_rename_on_a_branch_forked_before_the_recording_is_no_rename_evidence(target):
    """Review finding 4: the rename happened to the declaration as it was before the derivation.

    Measured on e65753bc: clean, exit 0. The honest way to follow such a merged
    rename is a pure move first, then a re-derivation (see the companion test).
    """
    target.git("branch", "-M", "main")
    target.git("checkout", "-q", "-b", "side")
    _rename(target)
    target.git("checkout", "-q", "main")
    rel = _content_probe(target)
    target.git("merge", "-q", "--no-ff", "-m", "merge the rename", "side")
    _edited(target, "docs/b.md")
    _re_derive_onto(target, rel, expected_value=1)
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED, reason
    assert (f"but it also moved the declaration from {DECL} to docs/b.md, where the previously anchored content "
            "is not") in reason, reason


def test_708_P2_a_rename_merged_from_before_the_recording_heals_by_a_pure_move_first(target):
    target.git("branch", "-M", "main")
    target.git("checkout", "-q", "-b", "side")
    _rename(target)
    target.git("checkout", "-q", "main")
    rel = _content_probe(target)
    target.git("merge", "-q", "--no-ff", "-m", "merge the rename", "side")
    _rewrite(target, rel, declaration_path="docs/b.md")
    target.commit("follow the rename as a pure move")
    _edited(target, "docs/b.md")
    _re_derive_onto(target, rel)
    _assert_clean(target)


def test_708_P2_rename_evidence_holds_with_log_follow_configured(target):
    """Review finding 3: the repository's log.follow must not change the removal search."""
    target.git("config", "log.follow", "true")
    rel = _content_probe(target)
    _edited(target)
    _rename(target)
    _re_derive_onto(target, rel)
    _assert_clean(target)


# -- #708 review round 2: a stale-born anchor whose declaration is reset to the anchored content -- #
# The anchor names X, the first revision found Y, and the declaration is reset to X: the anchored
# content is exactly what the probe was derived from, so nothing changed and no bar may drop.
PURE_MOVE_REFUSED = ("but the same commit changed the probe beyond declaration.path, which a pure move of the "
                     "declaration does not justify")


def _reset_to_x(target: Target) -> None:
    _edit(target, INSIDE[1], INSIDE[0])
    target.commit("reset the declaration to the anchored content")


def _stale_born_content_probe(target: Target, anchor: str = "blob") -> str:
    """On ``sectioned``: the probe lands anchored on X (``blob:`` or the commit) after the declaration became Y."""
    x = _blob(target) if anchor == "blob" else target.git("rev-parse", "HEAD")
    _edit(target, *INSIDE)
    target.commit("the declaration changes before the probe lands")
    rel = target.write_probe(make_probe(derived_from=x))
    target.commit("the probe lands")
    return rel


def _to_sections(target: Target, rel: str, locators=LOCATORS, **changes) -> None:
    data = yaml.safe_load((target.path / rel).read_text())
    if "expected_value" in changes:
        data["expected"]["value"] = changes.pop("expected_value")
    data.update(changes)
    data["declaration"]["sections"] = _sections_now(target, locators, data["declaration"]["path"])
    data["derived_from"] = ra.section_anchor(data["declaration"]["sections"])
    target.write(rel, yaml.safe_dump(data, sort_keys=False))


def _to_blob(target: Target, rel: str, **changes) -> None:
    _rewrite(target, rel, **changes)
    data = yaml.safe_load((target.path / rel).read_text())
    data["derived_from"] = _blob_now(target, data["declaration"]["path"])
    data["declaration"].pop("sections", None)
    target.write(rel, yaml.safe_dump(data, sort_keys=False))


def test_708_R2_1_stale_born_content_anchor_reset_renamed_and_lowered_is_weakened(sectioned):
    target = sectioned
    rel = _stale_born_content_probe(target)
    _reset_to_x(target)
    _rename(target)
    _rewrite(target, rel, declaration_path="docs/b.md", expected_value=1)
    target.commit("follow the rename and lower")
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED and reason.endswith(PURE_MOVE_REFUSED), reason


def test_708_R2_2_stale_born_section_anchor_reset_renamed_and_lowered_is_weakened(sectioned):
    target = sectioned
    rel = _stale_born_section_probe(target)
    _reset_to_x(target)
    _rename(target)
    _reanchor(target, rel, declaration_path="docs/b.md", expected_value=1)
    target.commit("follow the rename and lower")
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED and reason.endswith(PURE_MOVE_REFUSED), reason


@pytest.mark.parametrize("anchor", ["blob", "commit"])
def test_708_R2_3_stale_born_file_anchor_reset_and_relabelled_lowered_is_weakened(sectioned, anchor):
    """Onto sections (blob) or onto a content anchor (commit), at the same path."""
    target = sectioned
    rel = _stale_born_content_probe(target, anchor)
    _reset_to_x(target)
    if anchor == "blob":
        _to_sections(target, rel, expected_value=1)
    else:
        _to_blob(target, rel, expected_value=1)
    target.commit("relabel and lower")
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED and reason.endswith(f"but {DECL} did not change in between"), reason


def test_708_R2_4_stale_born_section_anchor_reset_and_reordered_lowered_is_weakened(sectioned):
    target = sectioned
    rel = _stale_born_section_probe(target)
    _reset_to_x(target)
    _to_sections(target, rel, locators=tuple(reversed(LOCATORS)), expected_value=1)
    target.commit("reorder the locators and lower")
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED, reason
    assert reason.endswith(f"but the anchored sections of {DECL} did not change in between"), reason


def test_708_R2_5_stale_born_section_anchor_reset_and_relabelled_to_a_blob_lowered_is_weakened(sectioned):
    target = sectioned
    rel = _stale_born_section_probe(target)
    _reset_to_x(target)
    _to_blob(target, rel, expected_value=1)
    target.commit("relabel onto the file and lower")
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED, reason
    assert reason.endswith(f"but the anchored sections of {DECL} did not change in between"), reason


@pytest.mark.parametrize("anchor", ["blob", "sections"])
def test_708_R2_a_stale_born_probe_re_derived_after_a_change_to_a_third_content_is_clean(sectioned, anchor):
    """Positive control: the declaration becomes Z, neither X nor Y; a re-derivation keeping the bar heals."""
    target = sectioned
    rel = _stale_born_content_probe(target) if anchor == "blob" else _stale_born_section_probe(target)
    _edit(target, "JSON and CSV.", "JSON, CSV and XML.")
    target.commit("the declaration changes to Z")
    if anchor == "blob":
        _rewrite(target, rel, derived_from=_blob(target))
    else:
        _reanchor(target, rel)
    target.commit("re-derive against Z")
    _assert_clean(target)


def test_708_R2_a_stale_born_commit_anchor_reset_and_migrated_unchanged_is_clean(sectioned):
    """Positive control: the commit anchor names X, the declaration is X again; migrating onto blob:X heals."""
    target = sectioned
    rel = _stale_born_content_probe(target, "commit")
    _reset_to_x(target)
    _to_blob(target, rel)
    target.commit("migrate onto the content anchor")
    _assert_clean(target)


def test_708_R2_6_a_historical_commit_move_after_a_reset_cannot_carry_a_lowered_bar(sectioned):
    """A seventh shape: the lowering rides on a commit-anchor move that a later re-derivation's walk reaches.

    M1 re-anchors the stale-born commit anchor onto the reset declaration and lowers the bar; M2
    follows a real change to Z. M1's content is what the anchor named, so it may change nothing.
    """
    target = sectioned
    rel = _stale_born_content_probe(target, "commit")
    _reset_to_x(target)
    _rewrite(target, rel, derived_from=target.git("rev-parse", "HEAD"), expected_value=1)
    target.commit("M1: re-anchor onto the reset declaration and lower")
    _edit(target, "JSON.", "JSON, CSV and XML.")
    target.commit("the declaration changes to Z")
    _rewrite(target, rel, derived_from=_blob(target))
    target.commit("M2: re-derive against Z")
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED, reason
    assert "its previous derivation was no re-derivation either" in reason, reason
    assert reason.endswith(f"but the content of {DECL} did not change in between, and a re-anchoring may change "
                           "nothing but derived_from and the approval"), reason


def test_708_R2_a_historical_pure_move_of_a_reset_commit_anchor_heals(sectioned):
    """Positive control: M1 follows a rename of the reset declaration with a commit anchor and changes nothing else."""
    target = sectioned
    rel = _stale_born_content_probe(target, "commit")
    _reset_to_x(target)
    moved = _rename(target)
    _rewrite(target, rel, derived_from=moved, declaration_path="docs/b.md")
    target.commit("M1: follow the rename")
    _edit(target, "JSON.", "JSON, CSV and XML.", path="docs/b.md")
    target.commit("the declaration changes to Z")
    _rewrite(target, rel, derived_from=_blob_now(target, "docs/b.md"))
    target.commit("M2: re-derive against Z")
    _assert_clean(target)


# -- #708 review round 3: a historical commit-anchor move onto a copy; a stale-born section heals -- #
@pytest.mark.parametrize("stale_born", [False, True])
def test_708_R3_a_historical_commit_move_onto_a_copy_beside_the_kept_original_is_weakened(sectioned, stale_born):
    """Measured on 3ff2b544: clean, exit 0. M1's anchor names a commit where the old path was gone, but
    the old path is still there at M1: the probe was re-pointed at a copy, and M2 lowered the bar on it."""
    target = sectioned
    target.git("branch", "-M", "main")
    if stale_born:
        rel = _stale_born_content_probe(target, "commit")  # the anchor names X, the probe lands at Y
        _reset_to_x(target)                                  # so K1's docs/b.md holds X
        copy_text = SECTIONED                                 # the copy holds X
    else:
        _, rel = derived_probe(target)
        copy_text = (target.path / DECL).read_text()          # the copy holds Y
    k1 = _rename(target)
    target.git("mv", "docs/b.md", DECL)
    target.commit("rename it back")
    target.write("docs/b.md", copy_text)
    _rewrite(target, rel, derived_from=k1, declaration_path="docs/b.md")
    target.commit("M1: point the probe at a copy, anchored on the commit of the rename")
    _edit(target, "JSON", "Avro", path="docs/b.md")
    target.commit("edit the copy")
    _rewrite(target, rel, derived_from=_blob_now(target, "docs/b.md"), expected_value=1)
    target.commit("M2: re-derive onto the copy and lower")
    assert (target.path / DECL).read_text() == SECTIONED  # the declaration itself never changed since
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED, reason
    assert "its previous derivation was no re-derivation either" in reason, reason
    assert reason.endswith(f"but it also moved the declaration from {DECL} to docs/b.md, and only a pure move of "
                           "an unchanged declaration, the old path gone, can change its path"), reason


@pytest.mark.parametrize("mode", [None, "reconfirmed"])
def test_708_R3_stale_born_section_anchor_heals_by_re_deriving(sectioned, mode):
    """Measured on 3ff2b544: weakened, `the anchored sections … did not change in between`."""
    target = sectioned
    rel = _stale_born_section_probe(target)
    assert _state(target)[0] == ra.STATE_STALE
    _reanchor(target, rel, mode=mode)
    target.commit("re-derive against the sections as the probe found them")
    _assert_clean(target)


@pytest.mark.parametrize("change", ["lowered", "other locators"])
def test_708_R3_stale_born_section_anchor_re_derived_with_another_change_is_weakened(sectioned, change):
    target = sectioned
    rel = _stale_born_section_probe(target)
    if change == "lowered":
        _reanchor(target, rel, expected_value=1)
    else:
        _reanchor(target, rel, locators=[("heading", "3.1")])
    target.commit("re-derive with another change")
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED, reason
    assert reason.endswith(f"but the anchored sections of {DECL} did not change in between"), reason


def test_708_R3_a_section_anchor_not_stale_born_re_ordered_only_still_reads_weakened(sectioned):
    """The relabel of sections onto sections stays reserved for the stale-born case."""
    target = sectioned
    rel = _section_probe(target)
    _reanchor(target, rel, locators=tuple(reversed(LOCATORS)))
    target.commit("re-order the locators")
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED, reason
    assert reason.endswith(f"but the anchored sections of {DECL} did not change in between"), reason


def test_708_R3_a_historical_commit_move_onto_a_copy_older_than_the_recording_is_weakened(sectioned):
    """The copy already existed when the previous derivation was recorded; the original is deleted later."""
    target = sectioned
    target.write("docs/b.md", SECTIONED)
    target.commit("a copy beside the declaration")
    _, rel = derived_probe(target)
    (target.path / DECL).unlink()
    k1 = target.commit("delete the declaration")
    _rewrite(target, rel, derived_from=k1, declaration_path="docs/b.md")
    target.commit("M1: point the probe at the old copy")
    _edit(target, "JSON", "Avro", path="docs/b.md")
    target.commit("edit the copy")
    _rewrite(target, rel, derived_from=_blob_now(target, "docs/b.md"), expected_value=1)
    target.commit("M2: re-derive onto the copy and lower")
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED, reason
    assert reason.endswith(f"but it also moved the declaration from {DECL} to docs/b.md, and only a pure move of "
                           "an unchanged declaration, the old path gone, can change its path"), reason


# -- #708 review round 4: a pure move keeps the anchored sections; order-blind re-confirmation ---- #
SCOPE_REFUSED = "which a pure move of the declaration does not justify"
X_SECTION = ("heading", "3.2")   # Schedules: no default locator covers it


def _rename_and_reanchor(target: Target, rel: str, locators) -> str:
    target.git("mv", DECL, "docs/b.md")
    _reanchor(target, rel, declaration_path="docs/b.md", locators=locators)
    return target.commit("rename the declaration and follow it")


def test_708_R4_a_pure_move_that_swaps_the_sections_cannot_carry_a_later_lowering(sectioned):
    """Measured on f5cad19d: both steps clean, exit 0, although 3.1 and AK-OS-07 never changed."""
    target = sectioned
    rel = _section_probe(target)
    _rename_and_reanchor(target, rel, [X_SECTION])
    _edit(target, *OUTSIDE, path="docs/b.md")
    _reanchor(target, rel, expected_value=1)
    target.commit("edit the unrelated section, re-derive and lower")
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED, reason
    assert "its previous derivation was no re-derivation either" in reason, reason
    assert reason.endswith(SCOPE_REFUSED), reason


@pytest.mark.parametrize("locators", [[X_SECTION], [("heading", "3.1")], [*LOCATORS, X_SECTION],
                                      [LOCATORS[0], X_SECTION]],
                         ids=["swapped", "narrowed", "widened", "exchanged"])
def test_708_R4_a_pure_move_that_changes_the_locator_set_is_weakened(sectioned, locators):
    target = sectioned
    rel = _section_probe(target)
    _rename_and_reanchor(target, rel, locators)
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED, reason
    assert reason.endswith(SCOPE_REFUSED), reason


def test_708_R4_a_stale_born_section_anchor_renamed_onto_other_sections_is_weakened(sectioned):
    target = sectioned
    rel = _stale_born_section_probe(target)
    _rename_and_reanchor(target, rel, [X_SECTION])
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED, reason
    assert reason.endswith(SCOPE_REFUSED), reason


@pytest.mark.parametrize("shape", ["same order", "reordered", "stale-born, as found"])
def test_708_R4_a_pure_rename_keeping_the_locators_stays_clean(sectioned, shape):
    target = sectioned
    rel = _stale_born_section_probe(target) if shape.startswith("stale") else _section_probe(target)
    _rename_and_reanchor(target, rel, tuple(reversed(LOCATORS)) if shape == "reordered" else LOCATORS)
    _assert_clean(target)


def test_708_R4_a_stale_born_section_anchor_heals_by_a_reordered_re_confirmation(sectioned):
    """Measured on f5cad19d: weakened, `a re-confirmation may change only …, and it also changed declaration.sections`."""
    target = sectioned
    rel = _stale_born_section_probe(target)
    _reanchor(target, rel, mode="reconfirmed", locators=tuple(reversed(LOCATORS)))
    target.commit("re-confirm against the sections as found, in another order")
    _assert_clean(target)


def test_708_R4_a_stale_born_section_anchor_whose_locator_never_resolved_names_supersede(sectioned):
    target = sectioned
    sections = [{"heading": "3.9", "digest": "0" * 64}]
    probe = make_probe(derived_from=ra.section_anchor(sections))
    probe["declaration"]["sections"] = sections
    rel = target.write_probe(probe)
    target.commit("the probe lands on a section the declaration doesn't hold")
    _reanchor(target, rel, locators=LOCATORS)
    target.commit("re-derive onto real sections")
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED, reason
    assert reason.endswith("no re-derivation heals it; supersede the probe"), reason


def test_708_R4_a_stale_born_content_anchor_whose_file_was_missing_names_supersede(target):
    rel = target.write_probe(make_probe(derived_from=_blob(target), path="docs/later.md"))
    target.commit("the probe lands before its declaration file")
    target.write("docs/later.md", "# Later\n")
    target.commit("the declaration file arrives")
    _rewrite(target, rel, derived_from=_blob_now(target, "docs/later.md"))
    target.commit("re-derive")
    state, reason = _state(target)
    assert state == ra.STATE_WEAKENED, reason
    assert reason.endswith("no re-derivation heals it; supersede the probe"), reason


# --------------------------------------------------------------------------- #
# #709: runner hardening candidates from the #688 review (K1-K5)
# --------------------------------------------------------------------------- #
def _lowered_after_approval(target: Target, marker: Path) -> tuple[str, str, str]:
    """p1 approved against a bar of 2 (observing 1), then a plain commit W lowers the bar to 1.

    Returns ``(probe path, recording commit, W)``. Judged honestly this reads weakened, naming W;
    a history that makes W the probe's first commit would read it clean and executed.
    """
    rel, recorded = _probe_observing_one(target, marker)
    _rewrite(target, rel, expected_value=1)
    return rel, recorded, target.commit("lower the bar")


def _weakened_at(recorded: str, change: str) -> str:
    return f"weakened: probe changed in {change[:12]} after its derivation was recorded in {recorded[:12]}"


def test_709_K1_a_replace_ref_that_makes_the_weakening_a_root_commit_changes_nothing(target, tmp_path):
    """Measured before the fix: `git replace W W'` (W' = W's tree, no parent) made W' the probe's
    creating commit, so the lowered bar read clean, exit 0, executed."""
    marker = tmp_path / "ran"
    _, recorded, weakened = _lowered_after_approval(target, marker)
    forged = target.git("commit-tree", f"{weakened}^{{tree}}", "-m", "forged root")
    target.git("replace", weakened, forged)
    assert target.git("log", "--format=%H", "HEAD").split() == [weakened]
    assert _weakened_reason(target, marker) == _weakened_at(recorded, weakened)


def test_709_K1_a_replace_ref_that_swaps_the_probe_blob_changes_nothing(target, tmp_path):
    """A replaced probe blob reads the approved text wherever git shows W's probe."""
    marker = tmp_path / "ran"
    rel, recorded, weakened = _lowered_after_approval(target, marker)
    target.git("replace", target.git("rev-parse", f"{weakened}:{rel}"), target.git("rev-parse", f"{recorded}:{rel}"))
    assert "value: 2" in target.git("show", f"{weakened}:{rel}")
    assert ra.Git(target.path).show(weakened, rel) == (target.path / rel).read_text()
    assert _weakened_reason(target, marker) == _weakened_at(recorded, weakened)


def test_709_K1_a_graft_file_that_makes_the_weakening_a_root_commit_changes_nothing(target, tmp_path):
    """Measured on git 2.53: --no-replace-objects leaves info/grafts in force (the same W read clean, exit 0,
    executed with it alone); GIT_GRAFT_FILE pointed at the null device neutralises it."""
    marker = tmp_path / "ran"
    _, recorded, weakened = _lowered_after_approval(target, marker)
    (target.path / ".git" / "info").mkdir(exist_ok=True)
    (target.path / ".git" / "info" / "grafts").write_text(weakened + "\n")
    probe = subprocess.run(["git", "-C", str(target.path), "--no-replace-objects", "rev-list", "HEAD"],
                           capture_output=True, text=True, check=True)
    assert probe.stdout.split() == [weakened], "the flag alone no longer honours grafts: re-measure K1"
    assert _weakened_reason(target, marker) == _weakened_at(recorded, weakened)


def _single_commit_copy(target: Target, tmp_path: Path) -> Path:
    """Another repository whose one root commit holds ``target``'s working tree: every probe reads clean there."""
    other = Target(tmp_path / "other")
    for path in (target.path / "project").rglob("*"):
        if path.is_file():
            other.write(path.relative_to(target.path).as_posix(), path.read_text())
    other.write(DECL, (target.path / DECL).read_text())
    other.commit("everything at once")
    return other.path


@pytest.mark.parametrize("variables", [("GIT_DIR",), ("GIT_DIR", "GIT_WORK_TREE"), ("GIT_DIR", "GIT_INDEX_FILE")])
def test_709_K1_an_inherited_git_dir_does_not_redirect_the_audit(target, tmp_path, monkeypatch, variables):
    """Measured before the fix: GIT_DIR naming a repository that holds the working tree in one root commit
    made the audit read that history, so the lowered bar read clean, exit 0, executed."""
    marker = tmp_path / "ran"
    _, recorded, weakened = _lowered_after_approval(target, marker)
    other = _single_commit_copy(target, tmp_path)
    values = {"GIT_DIR": str(other / ".git"), "GIT_WORK_TREE": str(target.path),
              "GIT_INDEX_FILE": str(other / ".git" / "index")}
    for name in variables:
        monkeypatch.setenv(name, values[name])
    assert _weakened_reason(target, marker) == _weakened_at(recorded, weakened)


@pytest.mark.parametrize("name", ["GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY"])
def test_709_K1_an_inherited_index_or_object_store_does_not_change_a_clean_verdict(target, tmp_path, monkeypatch,
                                                                                   name):
    """Measured before the fix: an empty index read every file as staged for deletion (weakened, uncommitted
    changes), and an empty object store hid the history (exit 2)."""
    marker = tmp_path / "ran"
    _content_probe(target, argv=marker_argv(marker))
    empty = tmp_path / "empty"
    empty.mkdir()
    monkeypatch.setenv(name, str(empty / "index") if name == "GIT_INDEX_FILE" else str(empty))
    _assert_clean(target)
    assert marker.exists()


def test_709_K1_the_git_environment_keeps_only_the_config_file_choice(monkeypatch):
    redirecting = ["GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY",
                   "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE", "GIT_COMMON_DIR", "GIT_REPLACE_REF_BASE",
                   "GIT_SHALLOW_FILE", "GIT_CONFIG_PARAMETERS", "GIT_CONFIG_COUNT", "GIT_CONFIG_KEY_0",
                   "GIT_CONFIG_VALUE_0", "GIT_CEILING_DIRECTORIES", "GIT_TRACE"]
    for name in redirecting:
        monkeypatch.setenv(name, "/elsewhere")
    monkeypatch.setenv("GIT_NO_REPLACE_OBJECTS", "0")
    monkeypatch.setenv("GIT_GRAFT_FILE", "/elsewhere/grafts")
    env = ra._git_env()
    assert not [name for name in redirecting if name in env]
    assert env["GIT_NO_REPLACE_OBJECTS"] == "1" and env["GIT_GRAFT_FILE"] == os.devnull
    assert env["GIT_CONFIG_GLOBAL"] == os.environ["GIT_CONFIG_GLOBAL"] and env["GIT_CONFIG_NOSYSTEM"] == "1"
    assert env["PATH"] == os.environ["PATH"]


def test_709_K1_injected_config_does_not_reach_the_history_reads(target, tmp_path, monkeypatch):
    """Config a surrounding `git -c` exports (GIT_CONFIG_COUNT/KEY/VALUE) reaches no git call of the runner.

    Measured before the fix: an injected clean filter that writes the approved bar back made `git status`
    read the uncommitted lowered bar as unchanged, so it read clean, exit 0, executed.
    """
    marker = tmp_path / "ran"
    rel, _ = _probe_observing_one(target, marker)
    _rewrite(target, rel, expected_value=1)
    attributes = tmp_path / "attributes"
    attributes.write_text("*.yml filter=approved\n")
    injected = {"core.attributesFile": str(attributes), "filter.approved.clean": "sed 's/value: 1$/value: 2/'"}
    monkeypatch.setenv("GIT_CONFIG_COUNT", str(len(injected)))
    for i, (key, value) in enumerate(injected.items()):
        monkeypatch.setenv(f"GIT_CONFIG_KEY_{i}", key)
        monkeypatch.setenv(f"GIT_CONFIG_VALUE_{i}", value)
    assert _weakened_reason(target, marker) == "weakened: probe file has uncommitted changes"


def test_709_K2_a_probe_directory_listing_that_fails_stops_the_run(target, tmp_path, monkeypatch, capsys):
    """Measured before the fix: a failing `ls-tree` read as an empty probe directory at HEAD."""
    marker = tmp_path / "ran"
    _content_probe(target, argv=marker_argv(marker))
    real = ra.Git.run

    def failing_listing(self, *args):
        if "ls-tree" in args and args[-1] == ra.PROBE_DIR.as_posix() + "/":
            return subprocess.CompletedProcess(["git", *args], 128, "", "fatal: not a tree object")
        return real(self, *args)

    monkeypatch.setattr(ra.Git, "run", failing_listing)
    with pytest.raises(ra.AuditError) as exc:
        ra.run(str(target.path), clock=lambda: FIXED_NOW)
    assert exc.value.code == ra.EXIT_ERROR and "fatal: not a tree object" in str(exc.value), exc.value
    assert ra.main(["--repo", str(target.path)]) == ra.EXIT_ERROR
    assert "ls-tree" in capsys.readouterr().err
    assert not marker.exists()


def test_709_K2_a_probe_directory_head_does_not_hold_lists_nothing(target):
    """`ls-tree` on a path the commit does not hold exits 0: an absent directory stays an empty listing."""
    assert ra.Git(target.path).tree_entries("HEAD", ra.PROBE_DIR.as_posix()) == []



def _created_in_merge(merge: str, path: str = P1_REL) -> str:
    return (f"{path} is committed, but the probe's history walk lists no commit that creates it, and it was "
            f"created inside merge {merge[:12]}: the probe's origin isn't in its listed history but in a merge the "
            "walk can't follow, and a derivation recorded in a merge cannot be judged")


def test_709_K3_a_probe_created_only_inside_a_merge_is_weakened_naming_the_merge(target, tmp_path):
    """Measured before the fix: exit 0, `uncommitted`, "probe file is not committed", although the merge
    committed it (the walk lists no revision, so probe_changes() returned no baseline)."""
    marker = tmp_path / "ran"
    blob = _blob(target)
    _, merge = _merge_side(target, in_merge=lambda: target.write_probe(
        make_probe(derived_from=blob, argv=marker_argv(marker))))
    assert ra.Git(target.path).file_history(P1_REL) == []
    assert _weakened_reason(target, marker) == "weakened: " + _created_in_merge(merge)


def test_709_K3_a_probe_created_inside_a_merge_and_changed_in_a_later_one_names_both(target, tmp_path):
    marker = tmp_path / "ran"
    blob = _blob(target)
    _, created = _merge_side(target, in_merge=lambda: target.write_probe(
        make_probe(derived_from=blob, argv=marker_argv(marker, "1"), expected=dict(BAR_OF_TWO))))
    _, lowered = _merge_side(target, "later", in_merge=lambda: _rewrite(target, P1_REL, expected_value=1))
    reason = _weakened_reason(target, marker)
    assert reason == "weakened: " + _created_in_merge(created).replace(
        f"merge {created[:12]}:", f"merge {created[:12]} and changed in merge {lowered[:12]}:"), reason


def test_709_K3_a_probe_created_inside_a_merge_with_uncommitted_edits_says_both(target, tmp_path):
    marker = tmp_path / "ran"
    blob = _blob(target)
    _, merge = _merge_side(target, in_merge=lambda: target.write_probe(
        make_probe(derived_from=blob, argv=marker_argv(marker))))
    _rewrite(target, P1_REL, tier="T1")
    assert _weakened_reason(target, marker) == ("weakened: " + _created_in_merge(merge)
                                                + "; probe file has uncommitted changes")


@pytest.mark.parametrize("staged", [False, True])
def test_709_K3_an_untracked_or_only_staged_probe_still_reads_uncommitted(target, tmp_path, staged):
    marker = tmp_path / "ran"
    target.write_probe(make_probe(derived_from=_blob(target), argv=marker_argv(marker)))
    if staged:
        target.git("add", P1_REL)
    code, report = run_audit(target)
    row = row_of(report, "p1")
    assert code == ra.EXIT_OK, row[7:]
    assert row[1] == ra.NOT_PROBED and row[7] == ra.STATE_UNCOMMITTED, row[7:]
    assert _plain(row[9]).startswith("probe file is not committed"), row[9]
    assert not marker.exists()


def _restored_by_a_merge(target: Target, marker: Path, *, old_declaration: bool) -> tuple[str, str]:
    """v1 approved at R; branch `old` forks there. Main changes the declaration and re-derives (C, clean);
    `old` gets an unrelated commit; the merge M takes main's tree but sets the probe back to v1 (and, with
    ``old_declaration``, the declaration too), so M's probe equals its second parent's. Returns ``(C, M)``."""
    rel = _content_probe(target, argv=marker_argv(marker))
    target.git("branch", "old")
    old_text = (target.path / DECL).read_text()
    v1 = (target.path / rel).read_text()
    target.write(DECL, "# Requirements\n\n## Export\n\nExports 3 collections, reworded.\n")
    _rewrite(target, rel, derived_from=_blob_now(target, DECL))
    rederived = target.commit("edit the declaration and re-derive")
    target.git("checkout", "-q", "old")
    target.write("old.txt", "old\n")
    target.commit("unrelated work on old")
    target.git("checkout", "-q", "main")
    target.git("merge", "-q", "--no-ff", "--no-commit", "old")
    target.write(rel, v1)
    if old_declaration:
        target.write(DECL, old_text)
    merge = target.commit("merge old, restoring the probe")
    assert target.git("rev-parse", f"{merge}^2:{rel}") == target.git("rev-parse", f"{merge}:{rel}")
    assert target.git("status", "--porcelain") == ""
    return rederived, merge


# The probe-lineage reconstruction from #709 rounds 2-6 was cut (it didn't converge): a lowering can still be
# laundered through merge topology. Scenarios that read clean on the cut runner (= develop) name that gap.
XFAIL_720 = pytest.mark.xfail(strict=True, reason="laundering through merge topology, #720")


@pytest.mark.parametrize("old_declaration", [False, True])
def test_709_K4_a_merge_restoring_a_pre_baseline_probe_names_the_merge(target, tmp_path, old_declaration):
    """Measured before the fix: weakened, but "probe file has uncommitted changes" on a clean tree: the
    merge equals one parent for the probe, so the combined-diff search did not find it."""
    marker = tmp_path / "ran"
    rederived, merge = _restored_by_a_merge(target, marker, old_declaration=old_declaration)
    assert _weakened_reason(target, marker) == (f"weakened: probe changed in merge {merge[:12]} after its "
                                                f"derivation was recorded in {rederived[:12]}")


def test_709_K4_the_same_restore_left_uncommitted_still_says_uncommitted(target, tmp_path):
    marker = tmp_path / "ran"
    rel = _content_probe(target, argv=marker_argv(marker))
    v1 = (target.path / rel).read_text()
    target.write(DECL, "# Requirements\n\n## Export\n\nExports 3 collections, reworded.\n")
    _rewrite(target, rel, derived_from=_blob_now(target, DECL))
    rederived = target.commit("edit the declaration and re-derive")
    target.write(rel, v1)
    assert _weakened_reason(target, marker) == "weakened: probe file has uncommitted changes"
    assert rederived[:12] not in _weakened_reason(target, marker)


RENAMED = "project/reach-probes/renamed.yml"
DECL_V2 = "# Requirements\n\n## Export\n\nExports 3 collections, reworded.\n"


def _backport(target: Target, marker: Path, shape: str) -> dict[str, str]:
    """GitFlow across a rename. R approves p1 at P1_REL on main; `release` forks there. Main renames the
    probe to RENAMED (N). Then, by ``shape``:

    - ``decl-then-pick``: main changes the declaration and re-derives in one commit C; release commits the
      same declaration change itself, then cherry-picks C (the probe change lands at P1_REL).
    - ``pick``: release cherry-picks C alone, declaration and re-derivation together.
    - ``reverse``: release changes the declaration and re-derives at P1_REL (W); main cherry-picks W, which
      lands at RENAMED.
    - ``no-pick``: main only renames; release changes the declaration and re-derives at P1_REL; the merge
      combines the new path with the new content, which neither side had.

    Release is then merged back into main (M). Returns the named commits.
    """
    _content_probe(target, argv=marker_argv(marker))
    target.git("branch", "release")
    target.git("mv", P1_REL, RENAMED)
    named = {"N": target.commit("rename the probe")}

    def rederive(path: str) -> str:
        target.write(DECL, DECL_V2)
        _rewrite(target, path, derived_from=_blob_now(target, DECL))
        return target.commit("change the declaration and re-derive")

    if shape in ("decl-then-pick", "pick"):
        named["C"] = rederive(RENAMED)
        target.git("checkout", "-q", "release")
        if shape == "decl-then-pick":
            target.write(DECL, DECL_V2)
            target.commit("change the declaration on release")
        target.git("cherry-pick", "-x", named["C"])
        named["picked"] = target.git("rev-parse", "HEAD")
    elif shape == "reverse":
        target.git("checkout", "-q", "release")
        named["W"] = rederive(P1_REL)
        target.git("checkout", "-q", "main")
        target.git("cherry-pick", "-x", named["W"])
        named["C"] = target.git("rev-parse", "HEAD")
        target.git("checkout", "-q", "release")
    else:
        target.git("checkout", "-q", "release")
        named["W"] = rederive(P1_REL)
    assert target.git("ls-tree", "--name-only", "HEAD", "--", P1_REL) == P1_REL
    target.git("checkout", "-q", "main")
    target.git("merge", "-q", "--no-ff", "--no-edit", "release")
    named["M"] = target.git("rev-parse", "HEAD")
    assert target.git("status", "--porcelain") == ""
    assert target.git("ls-tree", "--name-only", "HEAD", "--", "project/reach-probes/") == RENAMED
    return named


@pytest.mark.parametrize("shape", ["decl-then-pick", "pick", "reverse"])
def test_709_K5_a_backport_across_a_rename_merged_back_unchanged_is_clean(target, tmp_path, shape):
    """Measured before the fix: exit 4, "<picked> changed project/reach-probes/p1.yml under the id p1, but the
    probe's history walk does not list it, so the listed history is incomplete …" although the merge leaves
    the probe byte-identical to main's."""
    marker = tmp_path / "ran"
    named = _backport(target, marker, shape)
    assert target.git("rev-parse", f"{named['M']}^1:{RENAMED}") == target.git("rev-parse", f"{named['M']}:{RENAMED}")
    unlisted = named["W"] if shape == "reverse" else named["picked"]
    assert unlisted not in [c for c, _ in ra.Git(target.path).file_history(RENAMED)]
    _assert_clean(target)
    assert marker.exists()


def _unlisted(write: str) -> str:
    return (f"{write[:12]} changed {P1_REL} under the id p1, but the probe's history walk does not list it, so "
            "the listed history is incomplete and no derivation in it can be judged")


def _merge_named(merge: str, write: str) -> str:
    return (f"merge {merge[:12]} on HEAD's first-parent line changed the probe against its first parent after "
            f"{write[:12]} changed {P1_REL} under the id p1 on a merged line the probe's history walk does not "
            "list, so no derivation a merge carried in can be judged")


def test_709_K5_a_merge_combining_a_rename_and_a_release_re_derivation_stays_weakened_naming_the_merge(target,
                                                                                                    tmp_path):
    """5d, the #701 design line: neither side had the merged result, so the merge is named. Measured before the
    fix with the reason "<W> changed … but the probe's history walk does not list it, so the listed history is
    incomplete …" in front of the merge."""
    marker = tmp_path / "ran"
    named = _backport(target, marker, "no-pick")
    reason = _weakened_reason(target, marker)
    assert reason == (f"weakened: {_merge_named(named['M'], named['W'])}; probe changed in merge "
                      f"{named['M'][:12]} after its derivation was recorded in {named['N'][:12]}"), reason
    assert "listed history is incomplete" not in reason


def _lowered_on_release(target: Target, marker: Path) -> dict[str, str]:
    """R approves p1 against a bar of 2 (observing 1); `release` forks there; main renames the probe (N),
    changes the declaration and re-derives (C, clean on its own); release lowers the bar at the old path (W)."""
    rel, recorded = _probe_observing_one(target, marker)
    target.git("branch", "release")
    target.git("mv", rel, RENAMED)
    named = {"R": recorded, "N": target.commit("rename the probe")}
    target.write(DECL, DECL_V2)
    _rewrite(target, RENAMED, derived_from=_blob_now(target, DECL))
    named["C"] = target.commit("change the declaration and re-derive")
    target.git("checkout", "-q", "release")
    _rewrite(target, rel, expected_value=1)
    named["W"] = target.commit("lower the bar on release")
    target.git("checkout", "-q", "main")
    return named


def _merge_release_keeping_main(target: Target) -> str:
    target.git("merge", "-q", "--no-ff", "--no-commit", "release")
    target.git("checkout", "HEAD", "--", RENAMED)
    if (target.path / P1_REL).exists():
        target.git("rm", "-q", "-f", P1_REL)
    merge = target.commit("merge release, keeping main's probe")
    assert target.git("rev-parse", f"{merge}^1:{RENAMED}") == target.git("rev-parse", f"{merge}:{RENAMED}")
    return merge


def test_709_K5_ADV_a_lowered_bar_on_the_merged_line_that_the_merge_takes_is_weakened(target, tmp_path):
    """(a) The merge takes release's lowered bar under main's new name."""
    marker = tmp_path / "ran"
    named = _lowered_on_release(target, marker)
    target.git("merge", "-q", "--no-ff", "--no-edit", "release")
    merge = target.git("rev-parse", "HEAD")
    assert "value: 1" in target.git("show", f"HEAD:{RENAMED}")
    reason = _weakened_reason(target, marker)
    assert _merge_named(merge, named["W"]) in reason, reason


def test_709_K5_ADV_a_lowered_bar_dropped_by_the_merge_and_taken_later_in_a_commit_is_weakened(target, tmp_path):
    """(b) The merge keeps main's probe, a later plain commit takes the lowered bar: both the unlisted write
    (its content is no listed revision, so it is no backport) and the later change are named."""
    marker = tmp_path / "ran"
    named = _lowered_on_release(target, marker)
    _merge_release_keeping_main(target)
    _rewrite(target, RENAMED, expected_value=1)
    later = target.commit("take release's bar")
    assert _weakened_reason(target, marker) == (
        f"weakened: {_unlisted(named['W'])}; " + _weakened_at(named["C"], later).removeprefix("weakened: "))


def test_709_K5_ADV_a_lowered_bar_dropped_by_one_merge_and_taken_by_a_later_merge_is_weakened(target, tmp_path):
    """(c) W is excused at the first merge; a second merge of a branch that still carries it takes the
    lowered bar. That merge descends from W and changes the probe against its first parent."""
    marker = tmp_path / "ran"
    named = _lowered_on_release(target, marker)
    _merge_release_keeping_main(target)
    target.git("checkout", "-q", "-b", "again", "release")
    target.write("again.txt", "again\n")
    target.commit("more release work")
    target.git("checkout", "-q", "main")
    target.git("merge", "-q", "--no-ff", "--no-commit", "again")
    _rewrite(target, RENAMED, expected_value=1)
    if (target.path / P1_REL).exists():
        target.git("rm", "-q", "-f", P1_REL)
    second = target.commit("merge again, taking its bar")
    reason = _weakened_reason(target, marker)
    assert _merge_named(second, named["W"]) in reason, reason


def test_709_K5_ADV_a_lowered_bar_dropped_by_the_merge_stays_a_gap(target, tmp_path):
    """The merge keeps main's approved probe, but release's write is no backport: its content is no revision
    the walk lists. It stays a gap, as on develop. Excusing it because the merge dropped it would excuse the
    approved revision just as well when the lowered line is the merge's first parent (the test below)."""
    marker = tmp_path / "ran"
    named = _lowered_on_release(target, marker)
    _merge_release_keeping_main(target)
    assert "value: 2" in (target.path / RENAMED).read_text()
    assert _weakened_reason(target, marker) == f"weakened: {_unlisted(named['W'])}"


def _approved_revision_dropped_by_a_merge(target: Target, marker: Path, merge: str) -> str:
    """R approves p1 (bar 2, observing 1) on main. `evil` forks before R: L1 drafts the declaration and adds
    p1 anchored on the draft; L2 restores the declaration byte for byte, renames the probe and re-derives it
    with a bar of 1. `evil` then merges main as its second parent and drops R's probe (``merge``: `ours`
    strategy, or a normal merge that deletes R's file), and main is moved to that merge. Returns R."""
    start = target.git("rev-parse", "HEAD")
    approved_text = (target.path / DECL).read_text()
    _, recorded = _probe_observing_one(target, marker)
    target.git("checkout", "-q", "-b", "evil", start)
    target.write(DECL, approved_text + "\nDraft wording.\n")
    target.write(P1_REL, yaml.safe_dump(make_probe(derived_from=_blob_now(target, DECL), argv=marker_argv(marker, "1"),
                                                   expected=dict(BAR_OF_TWO)), sort_keys=False))
    target.commit("draft the declaration, add the probe")
    target.git("mv", P1_REL, RENAMED)
    target.write(DECL, approved_text)
    _rewrite(target, RENAMED, derived_from=_blob_now(target, DECL), expected_value=1)
    target.commit("restore the declaration, rename and re-derive with a lower bar")
    if merge == "ours":
        target.git("merge", "-q", "--no-ff", "-s", "ours", "-m", "merge main", "main")
    else:
        target.git("merge", "-q", "--no-ff", "--no-commit", "main")
        target.git("rm", "-q", "-f", P1_REL)
        target.commit("merge main, dropping its probe")
    target.git("checkout", "-q", "-B", "main")
    assert target.git("rev-parse", f"HEAD:{DECL}") == target.git("rev-parse", f"{recorded}:{DECL}")
    assert "value: 1" in target.git("show", f"HEAD:{RENAMED}") and target.git("status", "--porcelain") == ""
    assert target.git("ls-tree", "--name-only", "HEAD", "--", "project/reach-probes/") == RENAMED
    return recorded


@pytest.mark.parametrize("merge", ["ours", "delete"])
def test_709_K5_ADV_an_approved_revision_dropped_by_a_merge_whose_first_parent_lowered_the_bar_is_a_gap(
        target, tmp_path, merge):
    """Pre-merge review of #723. The committer picks the order of a merge's parents: with the lowered line as
    first parent, the approved revision R lies off HEAD's first-parent line and the merge keeps its first
    parent's probe. Measured before the fix: clean, exit 0, executed and reached 1/1; on develop weakened
    with this reason. R's content is no revision the walk lists, so it is no backport."""
    marker = tmp_path / "ran"
    recorded = _approved_revision_dropped_by_a_merge(target, marker, merge)
    assert _unlisted(recorded) in _weakened_reason(target, marker)


def test_709_K5_an_unlisted_write_on_heads_own_line_stays_a_gap(target):
    """The excuse is only for a write off HEAD's first-parent line."""
    git = ra.Git(target.path)
    line = git.out("rev-list", "--first-parent", "HEAD", "--").split()
    assert ra._merges_bringing(git, line[-1], line, {P1_REL}) == []


def test_709_K5_ADV_a_dropped_lowered_bar_renamed_on_its_line_and_merged_again_as_is_is_weakened(target, tmp_path):
    """(c) without any merge edit: a branch off release renames the lowered probe to main's name and a second
    merge takes that file as it is, so the merge equals its second parent and no combined diff names it."""
    marker = tmp_path / "ran"
    named = _lowered_on_release(target, marker)
    _merge_release_keeping_main(target)
    target.git("checkout", "-q", "-b", "again", "release")
    target.git("mv", P1_REL, RENAMED)
    target.write(DECL, DECL_V2)
    moved = target.commit("rename on the release line")
    target.git("checkout", "-q", "main")
    target.git("merge", "-q", "--no-ff", "--no-commit", "again")
    target.git("checkout", "again", "--", RENAMED)
    second = target.commit("merge again, taking its probe")
    assert target.git("rev-parse", f"{second}^2:{RENAMED}") == target.git("rev-parse", f"{second}:{RENAMED}")
    assert "value: 1" in target.git("show", f"HEAD:{RENAMED}")
    reason = _weakened_reason(target, marker)
    assert f"probe changed in {named['W'][:12]}, {moved[:12]} after its derivation was recorded in " in reason, reason


# --------------------------------------------------------------------------- #
# #709 follow-up from the adversarial review (F1-F3)
# --------------------------------------------------------------------------- #
def _side_revision_then_lowering(target: Target, marker: Path, merge: str, side_anchor: str = "same") -> dict:
    """F1. R0 approves p1 (content anchor A0, bar 2, observing 1); `side` forks there and S changes only
    approval.approved_by (``side_anchor="other"``: also moves the anchor to an unrelated blob). Main changes
    the declaration and re-derives (R1, A1). ``merge`` merges side so main keeps its own probe (`-s ours`,
    `-X ours`, an octopus `-s ours` with a second branch). L then lowers the bar, anchor A1 untouched."""
    rel, r0 = _probe_observing_one(target, marker)
    target.git("checkout", "-q", "-b", "side")
    data = yaml.safe_load((target.path / rel).read_text())
    data["approval"]["approved_by"] = "someone else"
    if side_anchor == "other":
        data["derived_from"] = "blob:" + "1" * 40
    target.write(rel, yaml.safe_dump(data, sort_keys=False))
    s = target.commit("re-approve on side")
    target.git("checkout", "-q", "main")
    target.write(DECL, DECL_V2)
    _rewrite(target, rel, derived_from=_blob_now(target, DECL))
    r1 = target.commit("change the declaration and re-derive")
    branches = ["side"]
    if merge == "octopus":
        target.git("checkout", "-q", "-b", "other", r0)
        target.write("other.txt", "other\n")
        target.commit("other work")
        target.git("checkout", "-q", "main")
        branches.append("other")
    strategy = ["-X", "ours"] if merge == "X-ours" else ["-s", "ours"]
    target.git("merge", "-q", "--no-ff", *strategy, "-m", "merge side keeping main", *branches)
    m = target.git("rev-parse", "HEAD")
    assert target.git("rev-parse", f"{m}:{rel}") == target.git("rev-parse", f"{r1}:{rel}")
    _rewrite(target, rel, expected_value=1)
    lowered = target.commit("lower the bar")
    return {"R0": r0, "S": s, "R1": r1, "M": m, "L": lowered, "rel": rel}


@pytest.mark.parametrize("merge,side_anchor", [pytest.param("s-ours", "same", marks=XFAIL_720),
                                               pytest.param("X-ours", "same", marks=XFAIL_720),
                                               pytest.param("octopus", "same", marks=XFAIL_720),
                                               ("s-ours", "other")])
def test_709_F1_a_side_revision_a_merge_dropped_does_not_launder_a_later_lowering(target, tmp_path, merge,
                                                                                side_anchor):
    marker = tmp_path / "ran"
    named = _side_revision_then_lowering(target, marker, merge, side_anchor)
    walk = [c for c, _ in ra.Git(target.path).file_history(named["rel"])]
    print(merge, side_anchor, [ {v: k for k, v in named.items()}.get(c, c[:8]) for c in walk])
    reason = _weakened_reason(target, marker)
    if side_anchor == "same":
        assert reason == _weakened_at(named["R1"], named["L"]), reason


@pytest.mark.parametrize("lowering_on", ["side", "main"])
def test_709_F1_a_merge_that_keeps_the_lowered_line_is_judged_on_that_line(target, tmp_path, lowering_on):
    """The chain starts at the revision HEAD's probe came from, not at the newest listed one: both lines
    re-derive after the same declaration change, one of them then lowers the bar, and the merge keeps that
    line's probe. Started at a listed re-derivation of the other line, the run would be that revision alone
    and the lowering never read."""
    marker = tmp_path / "ran"
    rel, r0 = _probe_observing_one(target, marker)
    lines = {}
    for branch in ("main", "side"):
        target.git("checkout", "-q", *(["-b", branch, r0] if branch == "side" else [branch]))
        target.write(DECL, DECL_V2)
        _rewrite(target, rel, derived_from=_blob_now(target, DECL))
        if branch != lowering_on:
            _rewrite(target, rel, tier="T1")
        lines[branch] = target.commit(f"re-derive on {branch}")
        if branch == lowering_on:
            _rewrite(target, rel, expected_value=1)
            lines["lowered"] = target.commit(f"lower the bar on {branch}")
    target.git("checkout", "-q", "main")
    target.git("merge", "-q", "--no-ff", "--no-commit", "-s", "ours" if lowering_on == "main" else "recursive",
               "side")
    target.git("checkout", lines["lowered"], "--", rel)
    merge = target.commit("merge side, keeping the lowered probe")
    assert target.git("rev-parse", f"{merge}:{rel}") == target.git("rev-parse", f"{lines['lowered']}:{rel}")
    reason = _weakened_reason(target, marker)
    assert lines["lowered"][:12] in reason, reason


def _uncommitted_lowering(target: Target, marker: Path) -> str:
    rel, _ = _probe_observing_one(target, marker)
    _rewrite(target, rel, expected_value=1)
    return rel


def _approving_filter(target: Target, tmp_path: Path, where: str) -> None:
    """A clean filter that writes the approved bar back, so `git status` reads the lowered file as unchanged."""
    command = "sed 's/value: 1$/value: 2/'"
    if where == "global":
        attributes = tmp_path / "attributes"
        attributes.write_text("*.yml filter=approved\n")
        with open(os.environ["GIT_CONFIG_GLOBAL"], "a") as cfg:
            cfg.write(f"[core]\n\tattributesFile = {attributes}\n[filter \"approved\"]\n\tclean = {command}\n")
    else:
        target.git("config", "filter.approved.clean", command)
        (target.path / ".git" / "info").mkdir(exist_ok=True)
        (target.path / ".git" / "info" / "attributes").write_text("*.yml filter=approved\n")


@pytest.mark.parametrize("where", ["global", "repository"])
def test_709_F2_a_clean_filter_does_not_hide_an_uncommitted_lowering(target, tmp_path, where):
    """Measured before the fix (original and adf17d00): clean, exit 0, executed."""
    marker = tmp_path / "ran"
    rel = _uncommitted_lowering(target, marker)
    _approving_filter(target, tmp_path, where)
    assert target.git("status", "--porcelain", "--", rel) == ""
    assert _weakened_reason(target, marker) == "weakened: probe file has uncommitted changes"


@pytest.mark.parametrize("where", ["global", "repository"])
def test_709_F2_a_clean_filter_does_not_hide_an_uncommitted_declaration_edit(target, tmp_path, where):
    """The same for the declaration: an edit the filter hides from `git status` still reads stale."""
    marker = tmp_path / "ran"
    _content_probe(target, argv=marker_argv(marker))
    target.write(DECL, (target.path / DECL).read_text().replace("3 collections", "1 collections"))
    command = "sed 's/1 collections/3 collections/'"
    if where == "global":
        attributes = tmp_path / "attributes"
        attributes.write_text("*.md filter=approved\n")
        with open(os.environ["GIT_CONFIG_GLOBAL"], "a") as cfg:
            cfg.write(f"[core]\n\tattributesFile = {attributes}\n[filter \"approved\"]\n\tclean = {command}\n")
    else:
        target.git("config", "filter.approved.clean", command)
        (target.path / ".git" / "info").mkdir(exist_ok=True)
        (target.path / ".git" / "info" / "attributes").write_text("*.md filter=approved\n")
    assert target.git("status", "--porcelain", "--", DECL) == ""
    state, reason = _state(target)
    assert state == ra.STATE_STALE and reason.endswith(f"{DECL} has uncommitted changes"), reason
    assert not marker.exists()


@pytest.mark.parametrize("flag", ["--assume-unchanged", "--skip-worktree"])
def test_709_F3_an_index_flag_does_not_hide_an_uncommitted_lowering(target, tmp_path, flag):
    """Measured before the fix (original and adf17d00): clean, exit 0, executed."""
    marker = tmp_path / "ran"
    rel = _uncommitted_lowering(target, marker)
    target.git("update-index", flag, rel)
    assert target.git("status", "--porcelain", "--", rel) == ""
    assert _weakened_reason(target, marker) == "weakened: probe file has uncommitted changes"


def test_709_F3_a_staged_lowering_with_the_working_tree_reverted_still_reads_uncommitted(target, tmp_path):
    marker = tmp_path / "ran"
    rel, _ = _probe_observing_one(target, marker)
    approved = (target.path / rel).read_text()
    _rewrite(target, rel, expected_value=1)
    target.git("add", rel)
    target.write(rel, approved)
    assert _weakened_reason(target, marker) == "weakened: probe file has uncommitted changes"


def test_709_F2_a_crlf_checkout_of_the_committed_probe_is_no_change(target, tmp_path):
    """core.autocrlf renders every LF as CRLF in the working tree; the runner reads the same text either way."""
    marker = tmp_path / "ran"
    rel = _content_probe(target, argv=marker_argv(marker))
    for path in (rel, DECL):
        (target.path / path).write_bytes((target.path / path).read_bytes().replace(b"\n", b"\r\n"))
    target.git("config", "core.autocrlf", "true")
    _assert_clean(target)
    assert marker.exists()


def test_709_F2_a_crlf_checkout_with_a_lowered_bar_is_a_change(target, tmp_path):
    marker = tmp_path / "ran"
    rel = _uncommitted_lowering(target, marker)
    (target.path / rel).write_bytes((target.path / rel).read_bytes().replace(b"\n", b"\r\n"))
    target.git("config", "core.autocrlf", "true")
    assert _weakened_reason(target, marker) == "weakened: probe file has uncommitted changes"


def test_709_F2_same_bytes_accepts_only_the_exact_crlf_rendering():
    assert ra._same_bytes(b"a\nb\n", b"a\nb\n")
    assert ra._same_bytes(b"a\r\nb\r\n", b"a\nb\n")
    assert not ra._same_bytes(b"a\r\nb\n", b"a\nb\n")
    assert not ra._same_bytes(b"a\nb\n", b"a\r\nb\r\n")
    assert not ra._same_bytes(b"a\r\r\nb\r\n", b"a\r\nb\n")


# --------------------------------------------------------------------------- #
# #709 round 3 (adversarial review 2): R1-R3, A1, A2
# --------------------------------------------------------------------------- #
DECL_V3 = "# Requirements\n\n## Export\n\nExports 3 collections, reworded again.\n"


def _rederive(target: Target, rel: str, text: str, msg: str) -> str:
    target.write(DECL, text)
    _rewrite(target, rel, derived_from=_blob_now(target, DECL))
    return target.commit(msg)


@pytest.mark.parametrize("between", [DECL_V3, None], ids=["via-v3", "via-v1"])
def test_709_R1_a_restore_merge_bringing_back_a_dropped_lowering_is_weakened(target, tmp_path, between):
    """Measured on 3a4ff07c: clean, exit 0, executed. k lowered on side was dropped by M1 (-s ours); main
    re-derived back to the same anchor (R2); M2 takes k's probe again. The chain read R2 alone."""
    marker = tmp_path / "ran"
    rel, _ = _probe_observing_one(target, marker)
    _rederive(target, rel, DECL_V2, "R1")
    target.git("checkout", "-q", "-b", "side")
    _rewrite(target, rel, expected_value=1)
    k = target.commit("k: lower the bar on side")
    target.git("checkout", "-q", "main")
    target.git("merge", "-q", "--no-ff", "-s", "ours", "-m", "M1", "side")
    original = (target.path / DECL).read_text() if between is None else None
    _rederive(target, rel, between or "# Requirements\n\n## Export\n\nExports 3 collections.\n", "X")
    assert original is None or original != (target.path / DECL).read_text()
    _rederive(target, rel, DECL_V2, "R2")
    target.git("checkout", "-q", "side")
    target.write("side.txt", "side\n")
    target.commit("more side work")
    target.git("checkout", "-q", "main")
    target.git("merge", "-q", "--no-ff", "--no-commit", "side")
    target.git("checkout", k, "--", rel)
    target.commit("M2: take k's probe")
    assert "value: 1" in target.git("show", f"HEAD:{rel}")
    _weakened_reason(target, marker)


def test_709_R2_a_byte_identical_twin_on_a_dropped_line_does_not_launder_a_lowering(target, tmp_path):
    """Measured on 3a4ff07c: clean, exit 0, executed. S on side (re-derived with the bar lowered) is
    byte-identical to main's lowering L; -s ours drops side, and the chain started at S, listed first."""
    marker = tmp_path / "ran"
    rel, r0 = _probe_observing_one(target, marker)
    _rederive(target, rel, DECL_V2, "R")
    _rewrite(target, rel, expected_value=1)
    lowered = target.commit("L: lower the bar")
    target.git("checkout", "-q", "-b", "side", r0)
    target.write(DECL, DECL_V2)
    _rewrite(target, rel, derived_from=_blob_now(target, DECL))
    _rewrite(target, rel, expected_value=1)
    twin = target.commit("S: re-derive with the lowered bar")
    assert target.git("rev-parse", f"{twin}:{rel}") == target.git("rev-parse", f"{lowered}:{rel}")
    target.git("checkout", "-q", "main")
    target.git("merge", "-q", "--no-ff", "-s", "ours", "-m", "drop side", "side")
    reason = _weakened_reason(target, marker)
    assert lowered[:12] in reason, reason


def test_709_R3_a_declaration_a_sparse_checkout_leaves_out_is_no_uncommitted_change(target, tmp_path):
    """Measured on 3a4ff07c: stale, "docs/requirements.md has uncommitted changes" (develop: clean)."""
    marker = tmp_path / "ran"
    _content_probe(target, argv=marker_argv(marker))
    target.git("sparse-checkout", "set", "--no-cone", "/project/")
    assert not (target.path / DECL).exists()
    _assert_clean(target)


def test_709_R3_a_present_skip_worktree_file_is_still_compared(target, tmp_path):
    """F3 stays closed under a sparse checkout: a skip-worktree probe that is present is compared by bytes."""
    marker = tmp_path / "ran"
    rel = _uncommitted_lowering(target, marker)
    lowered = (target.path / rel).read_text()
    target.git("checkout", "--", rel)
    target.git("sparse-checkout", "set", "--no-cone", "/docs/")
    assert not (target.path / rel).exists()
    target.write(rel, lowered)
    target.git("update-index", "--skip-worktree", rel)
    assert _weakened_reason(target, marker) == "weakened: probe file has uncommitted changes"


@pytest.mark.parametrize("skip", [True, False])
def test_709_A1_a_working_tree_file_over_a_directory_at_head_is_uncommitted(target, tmp_path, skip):
    """Measured on 3a4ff07c and develop with skip-worktree: clean, exit 0, executed (the `git status`
    fallback for a directory at HEAD saw nothing)."""
    marker = tmp_path / "ran"
    rel = _content_probe(target, argv=marker_argv(marker, "1"), expected=dict(BAR_OF_TWO))
    text = (target.path / rel).read_text()
    target.git("rm", "-q", rel)
    target.write(f"{rel}/inner", "inner\n")
    target.commit("the probe path becomes a directory")
    if skip:
        target.git("update-index", "--skip-worktree", f"{rel}/inner")
    shutil.rmtree(target.path / rel)
    target.write(rel, text.replace("value: 2", "value: 1"))
    git = ra.Git(target.path)
    assert git.entry_at("HEAD", rel)[0] == "tree" and git.is_dirty(rel)
    code, report = run_audit(target)
    row = row_of(report, "p1")
    assert code == ra.EXIT_FINDINGS and row[7] == ra.STATE_WEAKENED, row[7:]
    assert not marker.exists()


def test_709_A1_a_working_tree_file_over_a_submodule_at_head_is_uncommitted(target):
    head = target.git("rev-parse", "HEAD")
    target.git("update-index", "--add", "--cacheinfo", f"160000,{head},vendor/mod")
    target.git("commit", "-q", "-m", "add a gitlink")
    target.write("vendor/mod", "a file now\n")
    git = ra.Git(target.path)
    assert git.entry_at("HEAD", "vendor/mod")[0] == "commit" and git.is_dirty("vendor/mod")


def test_709_A2_an_uncommitted_pin_reverted_to_the_derived_ref_is_stale(target):
    """Measured on 3a4ff07c and develop: clean; the pin was read from the working tree unchecked."""
    _spec_config(target, ("nolte-shared", "v0.1.9"))
    _inherited_probe(target, "v0.1.8")
    target.commit("probe; the pin already moved on")
    _spec_config(target, ("nolte-shared", "v0.1.8"))
    state, reason = _state(target)
    assert state == ra.STATE_STALE and reason.endswith("spec/.spec-config.yml has uncommitted changes"), reason


def test_709_A2_an_uncommitted_pin_file_proves_nothing(target):
    _inherited_probe(target, "v0.1.8")
    target.commit("probe")
    _spec_config(target, ("nolte-shared", "v0.1.8"))
    state, reason = _state(target)
    assert state == ra.STATE_UNRESOLVED and "spec/.spec-config.yml is not committed" in reason, reason


# --------------------------------------------------------------------------- #
# #709 round 4 (adversarial review 3): H1, H2, L1, and the honest chains that must stay clean
# --------------------------------------------------------------------------- #
def _cannot_place(why: str) -> str:
    return (f"weakened: the probe's origin can't be placed: {why}; a derivation whose history can't be read as "
            "a chain of parents cannot be judged")


@XFAIL_720
def test_709_H1a_a_plain_delete_and_restore_after_the_lowering_does_not_launder_it(target, tmp_path):
    """Measured on 442cd24c: clean, exit 0, executed. The restore was dropped as a no-op, the walk then
    stopped at a plain commit it doesn't list and fell back to the list's order."""
    marker = tmp_path / "ran"
    named = _side_revision_then_lowering(target, marker, "s-ours")
    text = (target.path / named["rel"]).read_text()
    target.git("rm", "-q", named["rel"])
    target.commit("delete the probe")
    target.write(named["rel"], text)
    target.commit("restore the same bytes")
    assert _weakened_reason(target, marker) == _weakened_at(named["R1"], named["L"])


@XFAIL_720
@pytest.mark.parametrize("holding", ["L", "R1"])
def test_709_H1b_a_delete_and_a_restore_by_merge_does_not_launder_the_lowering(target, tmp_path, holding):
    """Measured on 442cd24c (holding L's version): clean, exit 0, executed. Restoring the deleted revision
    itself is transparent (the lowering L is named); restoring an older one names the merge too."""
    marker = tmp_path / "ran"
    named = _side_revision_then_lowering(target, marker, "s-ours")
    rel = named["rel"]
    target.git("branch", "keep", named[holding])
    target.git("rm", "-q", rel)
    target.commit("delete the probe")
    target.git("checkout", "-q", "keep")
    target.write("keep.txt", "keep\n")
    target.commit("work on keep")
    target.git("checkout", "-q", "main")
    target.git("merge", "-q", "--no-ff", "--no-commit", "keep")
    target.git("checkout", "keep", "--", rel)
    merge = target.commit("merge keep, restoring the probe")
    reason = _weakened_reason(target, marker)
    if holding == "L":
        assert reason == _weakened_at(named["R1"], named["L"]), reason
    else:
        assert reason == f"weakened: probe changed in merge {merge[:12]} after its derivation was recorded in " \
                         f"{named['R1'][:12]}", reason


@XFAIL_720
@pytest.mark.parametrize("merges", [3, 1001])
def test_709_H1c_merges_past_the_step_limit_read_weakened_not_the_list_order(target, tmp_path, merges):
    """Measured on 442cd24c: 1001 plumbing merges (tree of L, parents R1 and the previous one) read clean,
    exit 0, executed; 3 read weakened. Past the limit the origin can't be placed, which reads weakened."""
    marker = tmp_path / "ran"
    named = _side_revision_then_lowering(target, marker, "s-ours")
    tree = target.git("rev-parse", f"{named['L']}^{{tree}}")
    previous = named["L"]
    for i in range(merges):
        previous = target.git("commit-tree", tree, "-p", named["R1"], "-p", previous, "-m", f"plumbing {i}")
    target.git("reset", "-q", "--hard", previous)
    reason = _weakened_reason(target, marker)
    if merges <= 1000:
        assert reason == _weakened_at(named["R1"], named["L"]), reason
    else:
        assert reason == _cannot_place("more than 1000 commits to cross to place it"), reason


def _approved_bar_one(target: Target, marker: Path) -> tuple[str, str, str]:
    """H2. R0 approves bar 1 on V1 (observing 1). Main: C re-derives on V2 with bar 2; D re-derives back on
    V1 with bar 2. Returns ``(rel, R0, D)``."""
    rel = _content_probe(target, argv=marker_argv(marker, "1"),
                         expected={"kind": "count", "value": 1, "unit": "collections"})
    r0 = target.git("rev-parse", "HEAD")
    v1 = (target.path / DECL).read_text()
    target.write(DECL, DECL_V2)
    _rewrite(target, rel, derived_from=_blob_now(target, DECL), expected_value=2)
    target.commit("C: re-derive on V2 with bar 2")
    target.write(DECL, v1)
    _rewrite(target, rel, derived_from=_blob_now(target, DECL))
    d = target.commit("D: re-derive back on V1, bar 2")
    return rel, r0, d


@XFAIL_720
@pytest.mark.parametrize("shape", ["plain", "criss-cross"])
def test_709_H2_a_restore_through_a_branch_that_merged_main_with_ours_is_weakened(target, tmp_path, shape):
    """Measured on 442cd24c: clean, exit 0, executed (bar 2 back to 1, the declaration V1 both times). The
    merge base of D and old's tip is D itself, so the old base check saw no change on main."""
    marker = tmp_path / "ran"
    rel, r0, d = _approved_bar_one(target, marker)
    target.git("checkout", "-q", "-b", "old", r0)
    target.write("old.txt", "old\n")
    target.commit("work on old")
    if shape == "criss-cross":
        target.git("checkout", "-q", "main")
        target.git("merge", "-q", "--no-ff", "-m", "main takes old's work", "old")
        target.git("checkout", "-q", "old")
        target.git("merge", "-q", "--no-ff", "-s", "ours", "-m", "old keeps its probe over main", d)
    else:
        target.git("merge", "-q", "--no-ff", "-s", "ours", "-m", "old keeps its probe over main", "main")
    target.git("checkout", "-q", "main")
    target.git("merge", "-q", "--no-ff", "--no-commit", "old")
    target.git("checkout", "old", "--", rel)
    merge = target.commit("merge old")
    assert "value: 1" in (target.path / rel).read_text()
    assert target.git("rev-parse", f"HEAD:{DECL}") == target.git("rev-parse", f"{r0}:{DECL}")
    reason = _weakened_reason(target, marker)
    assert reason == f"weakened: probe changed in merge {merge[:12]} after its derivation was recorded in " \
                     f"{r0[:12]}", reason


@pytest.mark.parametrize("order", [["launder", "honest"], ["honest", "launder"]])
def test_709_L1_an_octopus_whose_parents_disagree_on_the_origin_is_weakened_in_either_order(target, tmp_path,
                                                                                           order):
    """Measured on 442cd24c: [launder, honest] weakened, [honest, launder] clean (develop: weakened). Both
    side parents hold the merged bytes, made in different commits: the origin can't be placed."""
    marker = tmp_path / "ran"
    rel, r0 = _probe_observing_one(target, marker)
    target.git("checkout", "-q", "-b", "honest")
    target.write(DECL, DECL_V2)
    _rewrite(target, rel, derived_from=_blob_now(target, DECL), expected_value=1)
    target.commit("re-derive on V2 with bar 1")
    lowered = (target.path / rel).read_text()
    target.git("checkout", "-q", "-b", "launder", r0)
    target.write(rel, lowered)
    target.commit("copy the bytes, declaration unchanged")
    target.git("checkout", "-q", "main")
    target.write("main.txt", "main\n")
    target.commit("main work")
    target.git("merge", "-q", "--no-ff", "-m", "octopus", *order)
    merge = target.git("rev-parse", "HEAD")
    assert target.git("rev-list", "--parents", "-n", "1", merge).count(" ") == 3
    _weakened_reason(target, marker)


def _honest(target: Target, marker: Path, shape: str) -> None:
    # The lowering shape observes 2 against an approved bar of 3, so only the lowered bar is reached.
    rel = _content_probe(target, argv=marker_argv(marker, "2" if shape == "lower-with-declaration" else "3"))
    texts = iter([DECL_V2, DECL_V3, "# Requirements\n\n## Export\n\nExports 3 collections, fourth.\n",
                  "# Requirements\n\n## Export\n\nExports 3 collections, fifth.\n",
                  "# Requirements\n\n## Export\n\nExports 3 collections, sixth.\n",
                  "# Requirements\n\n## Export\n\nExports 3 collections, seventh.\n"])
    if shape == "re-derive":
        _rederive(target, rel, next(texts), "re-derive")
    elif shape == "lower-with-declaration":
        target.write(DECL, next(texts))
        _rewrite(target, rel, derived_from=_blob_now(target, DECL), expected_value=2)
        target.commit("the declaration changes and the bar with it")
    elif shape == "unrelated-merge-then-re-derive":
        _merge_side(target)
        _rederive(target, rel, next(texts), "re-derive")
    elif shape in ("feature-branch", "six-prs"):
        for n in range(6 if shape == "six-prs" else 1):
            target.git("checkout", "-q", "-b", f"pr{n}")
            _rederive(target, rel, next(texts), f"re-derive in pr{n}")
            target.git("checkout", "-q", "main")
            target.write(f"main{n}.txt", "main\n")
            target.commit(f"main moves on beside pr{n}")
            target.git("merge", "-q", "--no-ff", "-m", f"merge pr{n}", f"pr{n}")
    elif shape == "delete-and-restore":
        text = (target.path / rel).read_text()
        target.git("rm", "-q", rel)
        target.commit("delete the probe")
        target.write(rel, text)
        target.commit("restore it")
    elif shape == "delete-and-restore-by-merge":
        target.git("branch", "keep")
        target.git("rm", "-q", rel)
        target.commit("delete the probe")
        target.git("checkout", "-q", "keep")
        target.write("keep.txt", "keep\n")
        target.commit("work on keep")
        target.git("checkout", "-q", "main")
        target.git("merge", "-q", "--no-ff", "--no-commit", "keep")
        target.git("checkout", "keep", "--", rel)
        target.commit("merge keep, restoring the probe")


@pytest.mark.parametrize("shape", ["re-derive", "lower-with-declaration", "unrelated-merge-then-re-derive",
                                   "feature-branch", "six-prs", "delete-and-restore",
                                   "delete-and-restore-by-merge"])
def test_709_H_honest_chains_stay_clean(target, tmp_path, shape):
    """Fail-closed must not make the runner unusable: every honest form reads clean and runs."""
    marker = tmp_path / "ran"
    _honest(target, marker, shape)
    _assert_clean(target)
    assert marker.exists()


@XFAIL_720
def test_709_H_a_committed_deletion_with_an_untracked_file_back_in_place_is_weakened(target, tmp_path):
    """HEAD holds no file at the probe's path, but its history does: the file on disk is an uncommitted change."""
    marker = tmp_path / "ran"
    rel, _ = _probe_observing_one(target, marker)
    text = (target.path / rel).read_text()
    target.git("rm", "-q", rel)
    target.commit("delete the probe")
    target.write(rel, text.replace("value: 2", "value: 1"))
    assert _weakened_reason(target, marker) == "weakened: probe file has uncommitted changes"


# --------------------------------------------------------------------------- #
# #709 round 5 (review 4): honest merge-commit histories that must stay clean
# --------------------------------------------------------------------------- #
DECL_V4 = "# Requirements\n\n## Export\n\nExports 3 collections, fourth wording.\n"


def _gitflow(target: Target, marker: Path, shape: str) -> None:
    """FP1. main plays develop; `master` forks at the approval R0."""
    rel = _content_probe(target, argv=marker_argv(marker))
    target.git("branch", "master")
    if shape == "hotfix":
        c = _rederive(target, rel, DECL_V2, "c: re-derive on develop")
        target.git("checkout", "-q", "master")
        target.git("cherry-pick", "-x", c)
        _rederive(target, rel, DECL_V3, "hotfix: re-derive on master")
        target.git("checkout", "-q", "main")
        target.git("merge", "-q", "--no-ff", "-X", "theirs", "-m", "merge master into develop", "master")
    elif shape == "release":
        c = _rederive(target, rel, DECL_V2, "c: re-derive on develop")
        target.git("checkout", "-q", "master")
        target.git("cherry-pick", "-x", c)
        target.git("checkout", "-q", "-b", "release2", "main")
        _rederive(target, rel, DECL_V3, "re-derive on release2")
        target.git("checkout", "-q", "master")
        target.git("merge", "-q", "--no-ff", "-X", "theirs", "-m", "release2 into master", "release2")
        target.git("checkout", "-q", "main")
        target.git("merge", "-q", "--no-ff", "-m", "master into develop", "master")
    elif shape == "squash-then-merge":
        target.git("checkout", "-q", "-b", "feature")
        _rederive(target, rel, DECL_V2, "f2: re-derive on feature")
        target.git("checkout", "-q", "main")
        target.git("merge", "-q", "--squash", "feature")
        target.commit("squash feature")
        target.git("checkout", "-q", "feature")
        _rederive(target, rel, DECL_V3, "f3: re-derive again on feature")
        target.git("checkout", "-q", "main")
        target.git("merge", "-q", "--no-ff", "-X", "theirs", "-m", "merge feature", "feature")
    else:  # by-merge: the counter-check, V2 reaches master by a merge instead of a cherry-pick
        _rederive(target, rel, DECL_V2, "c: re-derive on develop")
        target.git("checkout", "-q", "master")
        target.git("merge", "-q", "--no-ff", "-m", "develop into master", "main")
        _rederive(target, rel, DECL_V3, "hotfix: re-derive on master")
        target.git("checkout", "-q", "main")
        target.git("merge", "-q", "--no-ff", "-m", "merge master into develop", "master")
    assert target.git("status", "--porcelain") == ""


@pytest.mark.parametrize("shape", ["hotfix", "release", "squash-then-merge", "by-merge"])
def test_709_FP1_a_cherry_picked_or_squashed_twin_of_the_main_lines_revision_stays_clean(target, tmp_path, shape):
    """Measured on 78418bf0: hotfix, release and squash-then-merge weakened ("probe changed in merge …"),
    by-merge clean. The taken version builds on a byte-identical twin of the main line's file."""
    marker = tmp_path / "ran"
    _gitflow(target, marker, shape)
    _assert_clean(target)
    assert marker.exists()


def test_709_FP2_a_hundred_and_twenty_honest_no_ff_prs_stay_clean(target, tmp_path):
    """Measured on 78418bf0: 55 PRs read "merges nest more than 50 deep" (weakened, exit 4)."""
    marker = tmp_path / "ran"
    rel = _content_probe(target, argv=marker_argv(marker))
    for n in range(120):
        target.git("checkout", "-q", "-b", f"pr{n}")
        _rederive(target, rel, f"# Requirements\n\n## Export\n\nExports 3 collections, wording {n}.\n",
                  f"re-derive in pr{n}")
        target.git("checkout", "-q", "main")
        target.git("merge", "-q", "--no-ff", "-m", f"merge pr{n}", f"pr{n}")
    started = time.monotonic()
    _assert_clean(target)
    print(f"FP2: 120 PRs audited in {time.monotonic() - started:.1f}s")
    assert marker.exists()


@pytest.mark.parametrize("then", ["nothing", "re-derive"])
def test_709_FP3_a_reverted_merge_that_deleted_the_probe_stays_clean(target, tmp_path, then):
    """Measured on 78418bf0: weakened for good ("merge … deleted …"), also after an honest re-derivation."""
    marker = tmp_path / "ran"
    rel = _content_probe(target, argv=marker_argv(marker))
    target.git("checkout", "-q", "-b", "drop")
    target.git("rm", "-q", rel)
    target.commit("drop the probe")
    target.git("checkout", "-q", "main")
    target.write("main.txt", "main\n")
    target.commit("main work")
    target.git("merge", "-q", "--no-ff", "-m", "merge drop", "drop")
    merge = target.git("rev-parse", "HEAD")
    target.git("revert", "--no-edit", "-m", "1", merge)
    if then == "re-derive":
        _rederive(target, rel, DECL_V2, "an honest re-derivation")
    _assert_clean(target)
    assert marker.exists()


def test_709_FP3_a_reverted_deletion_merge_restoring_other_bytes_is_judged(target, tmp_path):
    """Only the exact restore is transparent: restoring with a lowered bar after the deletion merge reads weakened."""
    marker = tmp_path / "ran"
    rel, recorded = _probe_observing_one(target, marker)
    text = (target.path / rel).read_text()
    target.git("checkout", "-q", "-b", "drop")
    target.git("rm", "-q", rel)
    target.commit("drop the probe")
    target.git("checkout", "-q", "main")
    target.write("main.txt", "main\n")
    target.commit("main work")
    target.git("merge", "-q", "--no-ff", "-m", "merge drop", "drop")
    target.write(rel, text.replace("value: 2", "value: 1"))
    restored = target.commit("restore with a lowered bar")
    assert _weakened_reason(target, marker) == _weakened_at(recorded, restored)


@XFAIL_720
def test_709_FP3_an_unplaceable_spot_is_not_healed_by_a_later_re_derivation(target, tmp_path):
    """Refutes healing an unplaceable spot before the recording: the octopus of L1 followed by an honest
    re-derivation stays weakened, as a named weakening does (test_701_a_weakening_in_a_merge_is_not_adopted…).
    The re-derivation rule judges every earlier derivation in the chain, so a chain that can't be read has
    no previous derivation to build on."""
    marker = tmp_path / "ran"
    rel, r0 = _probe_observing_one(target, marker)
    target.git("checkout", "-q", "-b", "honest")
    target.write(DECL, DECL_V2)
    _rewrite(target, rel, derived_from=_blob_now(target, DECL), expected_value=1)
    target.commit("re-derive on V2 with bar 1")
    lowered = (target.path / rel).read_text()
    target.git("checkout", "-q", "-b", "launder", r0)
    target.write(rel, lowered)
    target.commit("copy the bytes")
    target.git("checkout", "-q", "main")
    target.write("main.txt", "main\n")
    target.commit("main work")
    target.git("merge", "-q", "--no-ff", "-m", "octopus", "honest", "launder")
    merge = target.git("rev-parse", "HEAD")
    _rederive(target, rel, DECL_V3, "an honest re-derivation after it")
    assert _weakened_reason(target, marker) == _cannot_place(
        f"merge {merge[:12]} holds the version of 2 parents, made in different commits")


# --------------------------------------------------------------------------- #
# #709 round 6 (review 5): a merge must never drop the main line's own stretch
# --------------------------------------------------------------------------- #
def _merge_keeping_side(target: Target, branch: str, rel: str) -> str:
    target.git("merge", "-q", "--no-ff", "--no-commit", "-X", "theirs", branch)
    target.git("checkout", branch, "--", rel)
    return target.commit(f"merge {branch}")


def test_709_RS1_a_main_line_back_at_the_fork_file_does_not_launder_its_lowering(target, tmp_path):
    """Measured on bf4dcd4b: clean, exit 0, executed (develop: exit 4, naming L). Main re-derives to V2 (C)
    and back to V1 (D, bar 2), then L checks out R0's probe (bar 1, no declaration change); `old`, forked at
    R0, re-derives to Y. The taken chain reaches R0's file, which main only reached again after C, D, L."""
    marker = tmp_path / "ran"
    rel, r0, _ = _approved_bar_one(target, marker)
    target.git("checkout", r0, "--", rel)
    target.commit("L: back to R0's probe, bar 1")
    target.git("checkout", "-q", "-b", "old", r0)
    s2 = _rederive(target, rel, DECL_V3, "S2: re-derive on Y")
    target.git("checkout", "-q", "main")
    target.git("merge", "-q", "--no-ff", "-m", "merge old", "old")
    merge = target.git("rev-parse", "HEAD")
    assert target.git("rev-parse", f"{merge}:{rel}") == target.git("rev-parse", f"{s2}:{rel}")
    _weakened_reason(target, marker)


def test_709_RS1_P1b_a_lowering_undone_on_main_stays_a_finding_after_the_merge(target, tmp_path):
    """Measured on bf4dcd4b: clean, exit 0 (develop: exit 4 for L/U). Main lowers (L) and raises back to R0's
    file (U); side, forked at R0, re-derives to Y."""
    marker = tmp_path / "ran"
    rel, r0 = _probe_observing_one(target, marker)
    _rewrite(target, rel, expected_value=1)
    target.commit("L: lower the bar")
    target.git("checkout", r0, "--", rel)
    target.commit("U: back to R0's probe")
    target.git("checkout", "-q", "-b", "side", r0)
    _rederive(target, rel, DECL_V2, "S2: re-derive on side")
    target.git("checkout", "-q", "main")
    _merge_keeping_side(target, "side", rel)
    _weakened_reason(target, marker)


def _twin_of_lowering(target: Target, rel: str, r0: str, x_text: str) -> str:
    """On `side` from R0: P re-derives on ``x_text``, T re-derives back onto R0's declaration with bar 1,
    byte-identical to main's lowering. Returns T."""
    original = target.git("show", f"{r0}:{DECL}") + "\n"
    target.git("checkout", "-q", "-b", "side", r0)
    _rederive(target, rel, x_text, "P: re-derive on X")
    target.write(DECL, original)
    _rewrite(target, rel, derived_from=_blob_now(target, DECL), expected_value=1)
    return target.commit("T: re-derive back, bar 1")


def test_709_RS1_A6_a_deleted_lowering_restored_from_a_twin_on_side_is_weakened(target, tmp_path):
    """Measured on bf4dcd4b: clean, exit 0 (develop: exit 4). Main lowers (L) and deletes; side holds a
    byte-identical twin T made by a declaration cycle A to X to A; the merge restores T."""
    marker = tmp_path / "ran"
    rel, r0 = _probe_observing_one(target, marker)
    _rewrite(target, rel, expected_value=1)
    lowered = target.commit("L: lower the bar")
    target.git("rm", "-q", rel)
    target.commit("delete the probe")
    twin = _twin_of_lowering(target, rel, r0, DECL_V2)
    assert target.git("rev-parse", f"{twin}:{rel}") == target.git("rev-parse", f"{lowered}:{rel}")
    target.git("checkout", "-q", "main")
    # modify/delete conflict: resolved by taking side's file
    subprocess.run(["git", "-C", str(target.path), "merge", "-q", "--no-ff", "--no-commit", "side"],
                   capture_output=True, check=False)
    target.git("checkout", "side", "--", rel)
    target.commit("merge side, restoring the probe")
    assert target.git("rev-list", "--parents", "-n", "1", "HEAD").count(" ") == 2
    code, report = run_audit(target)
    row = row_of(report, "p1")
    assert code == ra.EXIT_FINDINGS and row[7] == ra.STATE_WEAKENED, row[7:]
    assert not marker.exists()


def test_709_RS1_A7_a_lowering_on_main_with_a_twin_on_side_is_weakened_after_the_merge(target, tmp_path):
    """Measured on bf4dcd4b: clean, exit 0 (develop: exit 4). Side R0, P (X), T (A, bar 1) byte-identical to
    main's lowering L, then S2 (Y); the merge takes S2."""
    marker = tmp_path / "ran"
    rel, r0 = _probe_observing_one(target, marker)
    _rewrite(target, rel, expected_value=1)
    lowered = target.commit("L: lower the bar")
    twin = _twin_of_lowering(target, rel, r0, DECL_V2)
    assert target.git("rev-parse", f"{twin}:{rel}") == target.git("rev-parse", f"{lowered}:{rel}")
    _rederive(target, rel, DECL_V3, "S2: re-derive on Y")
    target.git("checkout", "-q", "main")
    _merge_keeping_side(target, "side", rel)
    code, report = run_audit(target)
    row = row_of(report, "p1")
    assert code == ra.EXIT_FINDINGS and row[7] == ra.STATE_WEAKENED, row[7:]
    assert not marker.exists()


@pytest.mark.parametrize("back", ["no-ff", "fast-forward"])
def test_709_cut_a_lowering_undone_on_main_then_an_update_branch_merge_stays_weakened(target, tmp_path, back):
    """Review round 6 found the cut lineage reading this clean (develop: weakened). Main lowers (L) and undoes
    it (U); side, forked at R0, re-derives, merges main in ("Update branch"), and lands on main by --no-ff or
    fast-forward. On the cut runner it reads weakened, as on develop."""
    marker = tmp_path / "ran"
    rel, r0 = _probe_observing_one(target, marker)
    _rewrite(target, rel, expected_value=1)
    target.commit("L: lower the bar")
    target.git("checkout", r0, "--", rel)
    target.commit("U: back to R0's probe")
    target.git("checkout", "-q", "-b", "side", r0)
    _rederive(target, rel, DECL_V2, "S2: re-derive on side")
    target.git("merge", "-q", "--no-ff", "-m", "update branch", "main")
    target.git("checkout", "-q", "main")
    if back == "no-ff":
        target.git("merge", "-q", "--no-ff", "-m", "merge side", "side")
    else:
        target.git("merge", "-q", "--ff-only", "side")
    _weakened_reason(target, marker)


# --------------------------------------------------------------------------- #
# #709 fix-forward: declarations in their checkout form; entry_at fails closed
# --------------------------------------------------------------------------- #
def _recheckout(target: Target, rel: str) -> None:
    (target.path / rel).unlink()
    target.git("checkout", "--", rel)


@pytest.mark.parametrize("form", ["ident", "smudge", "eol-crlf-lone-cr"])
def test_709_X1_a_declaration_rewritten_on_checkout_is_no_uncommitted_change(target, tmp_path, form):
    """Measured on 27a7ee0b: stale, "docs/requirements.md has uncommitted changes" with `git status` empty
    (develop: clean). The working-tree file is the checkout form of HEAD's blob."""
    marker = tmp_path / "ran"
    if form == "ident":
        target.write(".gitattributes", "*.md ident\n")
        target.write(DECL, "# Requirements\n\n$Id$\n\n## Export\n\nExports 3 collections.\n")
    elif form == "smudge":
        target.git("config", "filter.up.smudge", "sed s/collections/COLLECTIONS/")
        target.git("config", "filter.up.clean", "sed s/COLLECTIONS/collections/")
        target.write(".gitattributes", "*.md filter=up\n")
    else:
        target.write(".gitattributes", "*.md text eol=crlf\n")
        (target.path / DECL).write_bytes(b"# Requirements\n\n## Export\n\nExports 3\rcollections.\n")
    target.commit("the declaration under checkout attributes")
    _content_probe(target, argv=marker_argv(marker))
    _recheckout(target, DECL)
    committed = subprocess.run(["git", "-C", str(target.path), "cat-file", "blob", f"HEAD:{DECL}"],
                               capture_output=True, check=True).stdout
    assert (target.path / DECL).read_bytes() != committed
    assert target.git("status", "--porcelain") == ""
    _assert_clean(target)
    assert marker.exists()


def test_709_X1_a_smudge_filter_that_lowers_a_probe_is_still_an_uncommitted_change(target, tmp_path):
    """Probes are compared raw: a smudge filter writing a lowered bar on checkout is a lowering, not HEAD."""
    marker = tmp_path / "ran"
    rel, _ = _probe_observing_one(target, marker)
    target.git("config", "filter.low.smudge", "sed 's/value: 2$/value: 1/'")
    target.git("config", "filter.low.clean", "cat")
    (target.path / ".git" / "info").mkdir(exist_ok=True)
    (target.path / ".git" / "info" / "attributes").write_text("*.yml filter=low\n")
    _recheckout(target, rel)
    assert "value: 1" in (target.path / rel).read_text()
    assert _weakened_reason(target, marker) == "weakened: probe file has uncommitted changes"


def test_709_X2_an_unreadable_tree_entry_stops_the_run(target, tmp_path, monkeypatch, capsys):
    """Measured on 27a7ee0b: a failing `ls-tree` for one path read as an absent file (None)."""
    marker = tmp_path / "ran"
    _content_probe(target, argv=marker_argv(marker))
    real = ra.Git.run

    def failing(self, *args):
        if "ls-tree" in args and args[-1] == DECL:
            return subprocess.CompletedProcess(["git", *args], 128, "", "fatal: not a tree object")
        return real(self, *args)

    monkeypatch.setattr(ra.Git, "run", failing)
    with pytest.raises(ra.AuditError) as exc:
        ra.Git(target.path).entry_at("HEAD", DECL)
    assert exc.value.code == ra.EXIT_ERROR and "fatal: not a tree object" in str(exc.value)
    assert ra.main(["--repo", str(target.path)]) == ra.EXIT_ERROR
    assert "ls-tree" in capsys.readouterr().err
    assert not marker.exists()


@pytest.mark.skipif(os.name != "posix" or os.geteuid() == 0, reason="needs a file the process can't read")
def test_709_a_declaration_the_runner_cannot_read_is_an_uncommitted_change_not_a_crash(target):
    """Pre-merge review of #723. Measured before the fix: PermissionError out of Git.is_dirty(); on develop
    `git status` reported the file and the probe read stale."""
    _content_probe(target)
    os.chmod(target.path / DECL, 0)
    try:
        state, reason = _state(target)
    finally:
        os.chmod(target.path / DECL, 0o644)
    assert state == ra.STATE_STALE and f"{DECL} has uncommitted changes" in reason, reason
