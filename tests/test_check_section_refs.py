"""Tests for scripts/check_section_refs.py.

Each test builds a small repository in tmp_path so a rule is pinned by a fact
the test controls; the last test runs the guard over this repository itself.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys
import textwrap

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("check_section_refs", ROOT / "scripts" / "check_section_refs.py")
guard = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = guard  # dataclasses resolve the defining module by name
assert _spec.loader is not None
_spec.loader.exec_module(guard)

TARGET_EN = """\
# Target
## Requirements
### File location and naming
### Delimitation from other specs and skills
### H. Consumer contract
## Acceptance Criteria
"""
TARGET_DE = """\
# Ziel
## Anforderungen
### Dateiort und Namensgebung
### Abgrenzung zu anderen Specs und Skills
### H. Konsumenten-Vertrag
## Akzeptanzkriterien
"""


def write(root: pathlib.Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(text), encoding="utf-8")


@pytest.fixture
def repo(tmp_path):
    write(tmp_path, "spec/claude/review-plan/en.md", TARGET_EN)
    write(tmp_path, "spec/claude/review-plan/de.md", TARGET_DE)
    write(tmp_path, "spec/project/citing/en.md", "# Citing\n## Acceptance Criteria\n")
    write(tmp_path, "spec/project/citing/de.md", "# Zitierend\n## Akzeptanzkriterien\n")
    return tmp_path


def citing_de(repo, line: str) -> list:
    write(repo, "spec/project/citing/de.md", f"# Zitierend\n## Anforderungen\n{line}\n## Akzeptanzkriterien\n")
    return guard.check(repo)


def classes(findings) -> list[str]:
    return [f.cls for f in findings]


# --------------------------------------------------------------------------- #
# section-other-language
# --------------------------------------------------------------------------- #
def test_german_file_citing_the_english_heading_is_blocking(repo):
    findings = citing_de(repo, "- gemäß `spec/claude/review-plan/` §„File location and naming“")
    assert classes(findings) == ["section-other-language"]
    assert findings[0].blocking and "'Dateiort und Namensgebung'" in findings[0].message


def test_german_file_citing_the_german_heading_passes(repo):
    assert citing_de(repo, "- gemäß `spec/claude/review-plan/` §„Dateiort und Namensgebung“") == []


@pytest.mark.parametrize("reference", [
    "`review-plan` §Dateiort und Namensgebung, gefolgt von Prosa",   # unquoted, prose follows
    "`review-plan` §\"Abgrenzung\"",                                  # quoted prefix of a heading
    "`review-plan` §H legt fest",                                     # letter label
    "[review-plan §Dateiort und Namensgebung](../../claude/review-plan/de.md)",  # relative link
    "`review-plan` §Dateiort und Namensgebung und §Abgrenzung zu anderen Specs und Skills",
])
def test_resolving_reference_forms_pass(repo, reference):
    assert citing_de(repo, f"- siehe {reference}") == []


def test_unquoted_reference_needs_a_word_boundary_after_the_heading(repo):
    write(repo, "spec/project/citing/en.md", "# Citing\n## Requirements\n### Scope\n- per §Scopes elsewhere\n## Acceptance Criteria\n")
    assert classes(guard.check(repo)) == ["section-unresolved"]


def test_own_file_heading_resolves_without_a_target(repo):
    write(repo, "spec/project/citing/en.md", "# Citing\n## Requirements\n### Scope\n- per §Scope above\n## Acceptance Criteria\n")
    assert guard.check(repo) == []


@pytest.mark.parametrize("line", [
    "- `§Nicht aufgelöst` steht im Code-Span",
    "- nach § 5 DDG",
    "- GitHub Docs §`permissions`",
    "```\n§File location and naming\n```",
])
def test_non_references_are_ignored(repo, line):
    assert citing_de(repo, line) == []


def test_reference_resolving_in_no_language_is_advisory(repo):
    findings = citing_de(repo, "- gemäß `spec/claude/review-plan/` §\"Required sections\"")
    assert classes(findings) == ["section-unresolved"]
    assert not findings[0].blocking


# --------------------------------------------------------------------------- #
# heading-contract
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("rel, heading", [
    ("spec/project/citing/de.md", "## Abnahmekriterien"),
    ("spec/project/citing/de.md", "## Acceptance Criteria"),
    ("spec/project/citing/en.md", "## Acceptance criteria"),
])
def test_non_contract_acceptance_heading_is_blocking(repo, rel, heading):
    write(repo, rel, f"# X\n{heading}\n")
    assert classes(guard.check(repo)) == ["heading-contract"]


# --------------------------------------------------------------------------- #
# moved-artifact-path
# --------------------------------------------------------------------------- #
def test_path_moved_under_a_plugin_is_blocking(repo):
    write(repo, "plugins/nolte-engineering/skills/quality-gate/SKILL.md", "# qg\n")
    write(repo, "docs/en/guide.md", "The skill lives at `skills/quality-gate/SKILL.md`.\n")
    findings = guard.check(repo)
    assert classes(findings) == ["moved-artifact-path"]
    assert "`plugins/nolte-engineering/skills/quality-gate/SKILL.md`" in findings[0].message


def test_path_relative_to_its_own_plugin_passes(repo):
    write(repo, "plugins/nolte-claude-dev/skills/skill-review/SKILL.md", "# sr\n")
    write(repo, "plugins/nolte-claude-dev/skills/skill-management/examples/01.md", "Read `skills/skill-review/SKILL.md`.\n")
    assert guard.check(repo) == []


def test_existing_root_path_and_historical_records_pass(repo):
    write(repo, "skills/spec/SKILL.md", "# spec\n")
    write(repo, "plugins/nolte-engineering/skills/quality-gate/SKILL.md", "# qg\n")
    write(repo, "docs/en/guide.md", "See `skills/spec/SKILL.md`.\n")
    write(repo, ".audits/spec-drift/2026-Q4.md", "Cited `skills/quality-gate/` at the time.\n")
    write(repo, "project/goals.md", "Authored via `skills/quality-gate/SKILL.md`.\n")
    assert guard.check(repo) == []


# --------------------------------------------------------------------------- #
# main and the repository itself
# --------------------------------------------------------------------------- #
def test_main_exit_codes(repo, capsys):
    assert guard.main(["--repo", str(repo)]) == 0
    citing_de(repo, "- gemäß `spec/claude/review-plan/` §\"Required sections\"")
    assert guard.main(["--repo", str(repo)]) == 0
    citing_de(repo, "- gemäß `spec/claude/review-plan/` §„File location and naming“")
    assert guard.main(["--repo", str(repo)]) == 1
    assert guard.main(["--repo", str(repo / "nowhere")]) == 2


def test_repository_has_no_blocking_findings():
    blocking = [str(f) for f in guard.check(ROOT) if f.blocking]
    assert blocking == []
