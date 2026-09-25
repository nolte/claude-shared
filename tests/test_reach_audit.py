"""Tests for plugins/nolte-engineering/skills/capability-reach-audit/scripts/reach_audit.py.

Requirement ids refer to project/requirements/capability-reach-executor.md.

The doubles are honest ones: change detection runs against real git repositories
created in ``tmp_path`` (git is never mocked), and the environment step runs a
``task`` executable placed first on ``PATH`` that reads the target's
``Taskfile.yml`` and fails an unknown target the way go-task does. The T1 case
stands up a real loopback HTTP server through that shim.
"""
from __future__ import annotations

import hashlib
import json
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
SCHEMA_PATH = REPO_ROOT / "schemas" / "reach-probe-v1.1.schema.yaml"
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


def marker_argv(marker: Path, output: str = "3") -> list[str]:
    """An observation step that leaves a trace, so a test can prove it never ran."""
    return [PY, "-c", f"open({str(marker)!r}, 'w').write('ran'); print({output!r})"]


@pytest.fixture
def target(tmp_path) -> Target:
    t = Target(tmp_path / "target")
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
    assert "schemas/reach-probe-v1.1.schema.yaml" in bound.values()


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
    moved = target.commit("move declaration")
    data = yaml.safe_load((target.path / rel).read_text())
    data["derived_from"] = moved
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
    assert f"but {DECL} did not change in between" in row[9]
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
    assert row[7] == ra.STATE_WEAKENED and f"but {DECL} did not change in between" in row[9]


def test_SCR001_re_derivation_after_a_renamed_declaration_is_clean(target):
    _, rel = derived_probe(target)
    target.git("mv", DECL, "docs/requirements-v2.md")
    renamed = target.commit("rename the declaration")
    _rewrite(target, rel, declaration_path="docs/requirements-v2.md", derived_from=renamed)
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
    target.commit("re-add it weakened")
    _, report = run_audit(target)
    row = row_of(report, "p1")
    assert row[7] == ra.STATE_WEAKENED and "carries no readable derived_from" in row[9]


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
    moved = target.commit("move declaration")
    target.write_probe(make_probe(derived_from=moved))
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
    assert (f"but docs/other.md already held {other[:12]} when the previous derivation was recorded in "
            f"{recorded[:12]}, so re-pointing at it shows no declaration change") in reason


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
    assert "cannot both be resolved to commits" in reason
