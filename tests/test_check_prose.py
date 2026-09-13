"""Tests for scripts/check_prose.py.

The enforced lane is the pr-lint job, which installs Vale. These tests pin the
masking and the exit semantics with a fake Vale runner, so they need no Vale
binary; one integration test runs the real binary where it is installed.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import shutil
from types import SimpleNamespace

import pytest

MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "check_prose.py"
_spec = importlib.util.spec_from_file_location("check_prose", MODULE_PATH)
check_prose = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(check_prose)

RENOVATE_ENTRY = (
    "* chore(deps): update dependency mkdocs-material to v9.7.7 (#408) "
    "@[renovate[bot]](https://github.com/apps/renovate)"
)


def fake_vale(errors=(), stdout=None, returncode=None):
    calls = []

    def runner(args, cwd=None, capture_output=None, text=None):
        calls.append({"args": list(args), "text": pathlib.Path(args[-1]).read_text(encoding="utf-8")})
        report = {args[-1]: [{"Severity": "error", "Check": c, "Message": "m", "Match": "x", "Line": 1} for c in errors]}
        out = stdout if stdout is not None else json.dumps(report if errors else {})
        rc = returncode if returncode is not None else (1 if errors else 0)
        return SimpleNamespace(returncode=rc, stdout=out, stderr="")

    runner.calls = calls
    return runner


@pytest.fixture
def vale_on_path(monkeypatch):
    monkeypatch.setattr(check_prose.shutil, "which", lambda name: "/usr/local/bin/vale")


# --------------------------------------------------------------------------- #
# Masking
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "title, expected",
    [
        ("fix(ci): update pr checks", "`fix(ci):` update pr checks"),
        ("feat(api)!: drop the v1 routes", "`feat(api)!:` drop the v1 routes"),
        ("docs: spec-polish sweep — follow-ups", "`docs:` spec-polish sweep — follow-ups"),
        ("no prefix at all", "no prefix at all"),
    ],
)
def test_mask_title_masks_only_the_prefix(title, expected):
    assert check_prose.mask_title(title) == expected


def test_mask_release_notes_masks_every_machine_token_in_an_entry():
    masked = check_prose.mask_release_notes(RENOVATE_ENTRY)
    for token in ["`chore(deps):`", "`mkdocs-material`", "`(#408)`",
                  "`@[renovate[bot]](https://github.com/apps/renovate)`"]:
        assert token in masked


def test_mask_release_notes_keeps_a_human_entry_checked():
    masked = check_prose.mask_release_notes("* fix(ci): update pr checks (#12) @nolte")
    assert "update pr checks" in masked and "`pr`" not in masked


def test_mask_release_notes_leaves_prose_lines_alone():
    body = "## Changes\n\nA curated sentence about ci and pr checks.\n"
    assert check_prose.mask_release_notes(body) == body


# --------------------------------------------------------------------------- #
# Exit semantics
# --------------------------------------------------------------------------- #
def test_title_with_an_error_fails(monkeypatch, vale_on_path, capsys):
    monkeypatch.setenv("PR_TITLE", "fix(spec): a titel with a typo")
    monkeypatch.delenv("PR_AUTHOR", raising=False)
    assert check_prose.main(["--title"], runner=fake_vale(errors=["Vale.Spelling"])) == 1
    assert "Vale.Spelling" in capsys.readouterr().out


def test_clean_title_passes(monkeypatch, vale_on_path):
    monkeypatch.setenv("PR_TITLE", "fix(spec): name the real flag")
    monkeypatch.setenv("PR_AUTHOR", "nolte")
    runner = fake_vale()
    assert check_prose.main(["--title"], runner=runner) == 0
    assert runner.calls[0]["text"].startswith("`fix(spec):` name the real flag")


def test_title_reaches_vale_as_a_file_that_is_removed_afterwards(monkeypatch, vale_on_path):
    monkeypatch.setenv("PR_TITLE", "fix(ci): x; rm -rf / $(echo pwned)")
    monkeypatch.setenv("PR_AUTHOR", "nolte")
    runner = fake_vale()
    check_prose.main(["--title"], runner=runner)
    args = runner.calls[0]["args"]
    assert not any("rm -rf" in a for a in args)
    assert args[-1].endswith(".md") and not pathlib.Path(args[-1]).exists()


def test_allowlisted_bot_title_is_skipped_without_running_vale(monkeypatch, vale_on_path):
    monkeypatch.setenv("PR_TITLE", "chore(deps): update dependency mkdocs-material to v9.7.7")
    monkeypatch.setenv("PR_AUTHOR", "renovate[bot]")

    def must_not_run(*a, **k):
        raise AssertionError("vale ran for an allowlisted bot title")

    assert check_prose.main(["--title"], runner=must_not_run) == 0


def test_unlisted_bot_title_is_checked(monkeypatch, vale_on_path):
    monkeypatch.setenv("PR_TITLE", "chore(deps): update dependency mkdocs-material to v9.7.7")
    monkeypatch.setenv("PR_AUTHOR", "dependabot[bot]")
    assert check_prose.main(["--title"], runner=fake_vale(errors=["Vale.Terms"])) == 1


def test_release_notes_are_advisory_even_with_errors(tmp_path, vale_on_path, capsys):
    notes = tmp_path / "notes.md"
    notes.write_text("## Changes\n\n" + RENOVATE_ENTRY + "\n")
    assert check_prose.main(["--file", str(notes)], runner=fake_vale(errors=["Microsoft.Dashes"] * 3)) == 0
    assert "advisory, never blocking" in capsys.readouterr().out


def test_missing_vale_is_an_error_not_a_pass(monkeypatch):
    monkeypatch.setattr(check_prose.shutil, "which", lambda name: None)
    monkeypatch.setenv("PR_TITLE", "fix(ci): anything")
    monkeypatch.delenv("PR_AUTHOR", raising=False)
    assert check_prose.main(["--title"]) == 2


def test_vale_runtime_error_json_is_an_error_not_a_pass(monkeypatch, vale_on_path):
    monkeypatch.setenv("PR_TITLE", "fix(ci): anything")
    monkeypatch.delenv("PR_AUTHOR", raising=False)
    # The shape Vale 3.15.2 prints with --output=JSON when it can't start.
    runtime_error = json.dumps({"Line": 0, "Path": ".vale.ini", "Text": "style not found", "Code": "E201", "Span": 1})
    assert check_prose.main(["--title"], runner=fake_vale(stdout=runtime_error, returncode=2)) == 2


def test_missing_release_notes_file_is_an_error_not_a_traceback(tmp_path, vale_on_path):
    assert check_prose.main(["--file", str(tmp_path / "absent.md")], runner=fake_vale()) == 2


def test_unparseable_vale_output_is_an_error_not_a_pass(monkeypatch, vale_on_path):
    monkeypatch.setenv("PR_TITLE", "fix(ci): anything")
    monkeypatch.delenv("PR_AUTHOR", raising=False)
    runner = fake_vale(stdout="E100 [vocab] Runtime error", returncode=1)
    assert check_prose.main(["--title"], runner=runner) == 2


@pytest.mark.skipif(shutil.which("vale") is None, reason="needs the vale binary; the pr-lint job is the enforced lane")
def test_real_vale_ignores_a_masked_prefix_but_still_checks_the_summary():
    try:
        masked = check_prose.run_vale(check_prose.mask_title("fix(ci): update the lint job") + "\n")
        unmasked = check_prose.run_vale("fix(ci): update the lint job\n")
        summary_error = check_prose.run_vale(check_prose.mask_title("fix(ci): update the pr checks") + "\n")
    except check_prose.CheckUnavailable as exc:
        pytest.skip(f"vale styles not synced here: {exc}")
    assert masked == []
    assert [a["Match"] for a in unmasked if a["Check"] == "Vale.Terms"] == ["ci"]
    assert [a["Match"] for a in summary_error if a["Check"] == "Vale.Terms"] == ["pr"]
