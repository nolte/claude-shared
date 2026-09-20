"""Tests for scripts/check_default_branch_claims.py.

Each test builds a small repository in tmp_path so a rule is pinned by a fact the
test controls; the last tests run the guard over this repository itself.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys
import textwrap

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "check_default_branch_claims", ROOT / "scripts" / "check_default_branch_claims.py"
)
guard = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = guard  # dataclasses resolve the defining module by name
assert _spec.loader is not None
_spec.loader.exec_module(guard)

SETTINGS = """\
repository:
  name: claude-shared
  default_branch: develop
"""


def write(root: pathlib.Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(text), encoding="utf-8")


@pytest.fixture
def repo(tmp_path):
    # One live allowlist subject, so the staleness rule (G4) doesn't fire in the
    # tests that are about the predicate; its own tests re-point the allowlist.
    write(tmp_path, ".github/settings.yml", SETTINGS)
    write(tmp_path, "skills/excused/references/scoping.md", EXCUSED)
    return tmp_path


EXCUSED = """\
# Scoping

Where the two differ (a repo whose default is `main` while `develop` integrates),
the diff is inflated rather than empty.
"""


@pytest.fixture(autouse=True)
def allowlist_points_at_the_fixture(monkeypatch):
    """Point the shipped allowlist at the fixture's excused file."""
    entry = guard.ALLOWLIST[0]
    monkeypatch.setattr(
        guard, "ALLOWLIST",
        (guard.Allowed("skills/excused/references/scoping.md", entry.substring, entry.reason),),
    )


def claims(findings) -> list[str]:
    return [f.cls for f in findings]


def prose(repo, text: str) -> list:
    write(repo, "spec/project/workflow/en.md", text)
    return guard.check(repo)


# --------------------------------------------------------------------------- #
# The predicate
# --------------------------------------------------------------------------- #
def test_naming_the_configured_branch_passes(repo):
    assert prose(repo, "# W\n\nThe repository's default branch is `develop`, so autolinks fire there.\n") == []


def test_naming_another_branch_is_a_finding(repo):
    findings = prose(repo, "# W\n\nThe repository's default branch is `main`, so a `develop` merge closes nothing.\n")
    assert claims(findings) == ["default-branch-claim"]
    assert "names `main`" in findings[0].message and "configures `develop`" in findings[0].message


def test_a_claim_wrapped_across_two_lines_is_a_finding(repo):
    # Regression for the G6 selector failure: the line-by-line form of this
    # predicate missed every claim whose marker and branch literal sat on
    # different source lines. A sentence is not a line.
    findings = prose(repo, """\
        # W

        GitHub's reference-closing autolink fires only on the repository's
        **default branch** (`main` under this branching model), so a squash-merge
        into `develop` leaves referenced tracking issues `OPEN`.
        """)
    assert claims(findings) == ["default-branch-claim"]
    assert findings[0].line == 3  # the unit's first line, not the literal's line


def test_a_marker_without_a_branch_literal_passes(repo):
    assert prose(repo, "# W\n\nThe default branch is whatever the configuration declares.\n") == []


def test_a_branch_literal_without_a_marker_passes(repo):
    assert prose(repo, "# W\n\nFeature branches are created off `origin/develop` and merged into `main` at release.\n") == []


def test_an_unbackticked_branch_word_is_not_a_claim(repo):
    # `main` is also an ordinary English word; only a code literal names a branch.
    assert prose(repo, "# W\n\nThe default branch follows from the settings file, so main is prose here.\n") == []


def test_a_claim_in_another_sentence_of_the_same_unit_does_not_leak(repo):
    # The marker and the literal must meet inside one sentence, or every long
    # paragraph mentioning both would be a finding.
    assert prose(repo, """\
        # W

        The default branch carries the autolink. Release promotion fast-forwards
        `main` from the integration branch.
        """) == []


@pytest.mark.parametrize("marker", [
    "the repository's default branch is",
    "the repository's default-branch setting names",
    "der **Default-Branch** des Repositorys ist",
    "under this branching model the default is",
    "the branch it defaults to is",
])
def test_each_marker_form_is_recognised(repo, marker):
    assert claims(prose(repo, f"# W\n\nHere {marker} `main`.\n")) == ["default-branch-claim"]


@pytest.mark.parametrize("branch", ["main", "master", "trunk"])
def test_every_foreign_branch_name_is_recognised(repo, branch):
    assert claims(prose(repo, f"# W\n\nThe default branch is `{branch}`.\n")) == ["default-branch-claim"]


def test_a_claim_inside_a_fenced_template_is_a_finding(repo):
    # An operator-visible `gh --comment` template states the claim to a reader who
    # never opens the file; its backticks are backslash-escaped to survive a shell.
    findings = prose(repo, """\
        # W

        ```
        gh issue close <n> --comment "this repo's default is \\`main\\`, fast-forwarded from \\`develop\\`."
        ```
        """)
    assert claims(findings) == ["default-branch-claim"]


# --------------------------------------------------------------------------- #
# The expected value is read, never hard-coded
# --------------------------------------------------------------------------- #
def test_changing_the_configuration_flips_the_verdict(repo):
    text = "# W\n\nThe repository's default branch is `main`.\n"
    assert claims(prose(repo, text)) == ["default-branch-claim"]
    write(repo, ".github/settings.yml", "repository:\n  default_branch: main\n")
    assert [f for f in guard.check(repo) if f.cls == "default-branch-claim"] == []


def test_a_missing_or_keyless_settings_file_is_a_usage_error(repo, capsys):
    (repo / ".github" / "settings.yml").unlink()
    with pytest.raises(LookupError):
        guard.configured_branch(repo)
    write(repo, ".github/settings.yml", "repository:\n  name: claude-shared\n")
    with pytest.raises(LookupError):
        guard.configured_branch(repo)


# --------------------------------------------------------------------------- #
# Scope
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("rel", [
    ".audits/issue-orchestrate/652/analysis.md",
    "docs/en/skills/nolte-shared/pull-request-merge.md",
])
def test_records_of_their_day_and_the_generated_catalog_are_out_of_scope(repo, rel):
    write(repo, rel, "# R\n\nThe repository's default branch is `main`.\n")
    assert guard.check(repo) == []


@pytest.mark.parametrize("rel", [
    "project/sprints/0007.md",
    "project/mission.md",
])
def test_the_planning_tree_is_in_scope(repo, rel):
    """`project/` is live prose, not a dated record tree.

    An earlier draft of this guard excluded it alongside `.audits/`. Measuring the
    repository refuted that assumption: `project/` produced no hits, so the
    exclusion bought nothing and narrowed the selector below the property it
    asserts, which is the failure `defect-class-guards` G6 names.
    """
    write(repo, rel, "# P\n\nThe repository's default branch is `main`.\n")
    assert claims(guard.check(repo)) == ["default-branch-claim"]


def test_a_new_top_level_file_is_in_scope_by_default(repo):
    write(repo, "CLAUDE.md", "# C\n\nThe repository's default branch is `main`.\n")
    assert claims(guard.check(repo)) == ["default-branch-claim"]


# --------------------------------------------------------------------------- #
# The allowlist (G4)
# --------------------------------------------------------------------------- #
def test_the_allowlisted_sentence_is_excused(repo):
    assert guard.check(repo) == []


def test_the_allowlist_excuses_only_its_own_file(repo):
    write(repo, "skills/other/references/scoping.md", EXCUSED)
    findings = guard.check(repo)
    assert claims(findings) == ["default-branch-claim"]
    assert findings[0].file == "skills/other/references/scoping.md"


def test_a_stale_allowlist_entry_fails_the_run(repo):
    (repo / "skills" / "excused" / "references" / "scoping.md").unlink()
    findings = guard.check(repo)
    assert claims(findings) == ["stale-allowlist-entry"]
    assert "drop the entry" in findings[0].message


def test_an_entry_whose_sentence_changed_is_stale_rather_than_excusing(repo):
    write(repo, "skills/excused/references/scoping.md",
          "# S\n\nWhere a repository's default branch is `main`, the diff is inflated.\n")
    assert sorted(claims(guard.check(repo))) == ["default-branch-claim", "stale-allowlist-entry"]


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def test_main_exit_codes(repo):
    assert guard.main(["--repo", str(repo)]) == 0
    prose(repo, "# W\n\nThe repository's default branch is `main`.\n")
    assert guard.main(["--repo", str(repo)]) == 1
    assert guard.main(["--repo", str(repo / "nowhere")]) == 2


def test_report_lists_the_allowlist(repo, capsys):
    assert guard.main(["--repo", str(repo), "--report"]) == 0
    assert "allowlist: skills/excused/references/scoping.md" in capsys.readouterr().out


# --------------------------------------------------------------------------- #
# This repository
# --------------------------------------------------------------------------- #
def test_repository_states_no_contradicted_default_branch(monkeypatch):
    monkeypatch.undo()  # the shipped allowlist, against the real corpus
    assert [str(f) for f in guard.check(ROOT)] == []


def test_the_repository_configures_develop():
    # A positive control: the clean run above is a check, not an empty scan.
    assert guard.configured_branch(ROOT) == "develop"
