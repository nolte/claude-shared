"""Tests for scripts/check_pr_body.py.

The load-bearing cases are the two directions of the class-sweep rule, which
`spec/project/pull-request-workflow/` §Acceptance Criteria names explicitly: one
direction alone doesn't distinguish the check from a constant.
"""

from __future__ import annotations

import importlib.util
import pathlib

import pytest

MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "check_pr_body.py"
_spec = importlib.util.spec_from_file_location("check_pr_body", MODULE_PATH)
check_pr_body = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(check_pr_body)

check = check_pr_body.check

FIVE_SECTIONS = """## Summary

Repair the tenant-id read on the update route.

## Changes

- Validate the tenant id against the session on the update route

## Linked issues

Closes #1

## Testing

- `task check`

## Risk / rollout notes

None
"""

SWEEP = """
## Class sweep

- Predicate: `rg "body\\[.tenant_id.\\]" backend/routes/`
- Hits: 4
- Repaired: 4
- Guard: `scripts/check_tenant_body_field.py`, wired as the `static` required check
"""


def test_fix_pr_without_class_sweep_fails():
    failures = check("fix(api): validate the tenant id on the update route", FIVE_SECTIONS)
    assert failures, "a fix PR without the section must fail"
    assert any("Class sweep" in f for f in failures)


def test_same_body_with_class_sweep_passes():
    """The other direction: same title, same five sections, section added."""
    assert check("fix(api): validate the tenant id on the update route", FIVE_SECTIONS + SWEEP) == []


@pytest.mark.parametrize("pr_type", ["feat", "chore", "docs", "exp"])
def test_requirement_is_type_conditional(pr_type):
    """A non-fix PR passes the identical body that fails as a fix."""
    assert check(f"{pr_type}(api): rework the update route", FIVE_SECTIONS) == []


@pytest.mark.parametrize("field", ["Predicate", "Hits", "Repaired", "Guard"])
def test_each_sweep_field_is_required(field):
    mutilated = "\n".join(
        line for line in SWEEP.splitlines() if not line.startswith(f"- {field}:")
    )
    failures = check("fix(api): x", FIVE_SECTIONS + mutilated)
    assert any(field in f for f in failures)


@pytest.mark.parametrize("value", ["many", "4 of 6", "~4", ""])
def test_counts_must_be_integers(value):
    body = FIVE_SECTIONS + SWEEP.replace("- Hits: 4", f"- Hits: {value}")
    failures = check("fix(api): x", body)
    assert any("Hits" in f for f in failures)


def test_placeholder_is_not_a_value():
    body = FIVE_SECTIONS + SWEEP.replace(
        "- Guard: `scripts/check_tenant_body_field.py`, wired as the `static` required check",
        "- Guard: <path or required-check context>",
    )
    failures = check("fix(api): x", body)
    assert any("Guard" in f for f in failures)


def test_guard_none_with_a_reason_is_accepted():
    body = FIVE_SECTIONS + SWEEP.replace(
        "- Guard: `scripts/check_tenant_body_field.py`, wired as the `static` required check",
        "- Guard: none — the route was deleted, so the class has no remaining members",
    )
    assert check("fix(api): x", body) == []


def test_missing_required_section_fails_any_type():
    body = FIVE_SECTIONS.replace("## Testing", "## Verification")
    failures = check("feat(api): x", body)
    assert any("Testing" in f for f in failures)


def test_sections_out_of_order_fail():
    parts = FIVE_SECTIONS.split("## Linked issues")
    reordered = "## Linked issues" + parts[1].split("## Testing")[0] + parts[0] + "## Testing" + \
        parts[1].split("## Testing")[1]
    failures = check("feat(api): x", reordered)
    assert any("out of order" in f for f in failures)


def test_empty_summary_fails():
    body = FIVE_SECTIONS.replace("Repair the tenant-id read on the update route.", "None")
    failures = check("feat(api): x", body)
    assert any("Summary" in f for f in failures)


def test_html_comment_does_not_count_as_content():
    body = FIVE_SECTIONS.replace(
        "Repair the tenant-id read on the update route.",
        "<!-- one to three sentences -->",
    )
    failures = check("feat(api): x", body)
    assert any("Summary" in f for f in failures)


@pytest.mark.parametrize(
    "title",
    ["refactor(api): x", "Fix(api): x", "fix: ", "no type at all"],
)
def test_title_vocabulary_is_closed(title):
    assert check(title, FIVE_SECTIONS + SWEEP)


def test_repository_specific_section_after_the_five_is_allowed():
    body = FIVE_SECTIONS + "\n## Deployment notes\n\nNone\n"
    assert check("feat(api): x", body) == []


# --------------------------------------------------------------------------- #
# Dependency-bot exemption (#582). A Renovate body, captured from #569, has none
# of the five sections. It must pass for the allowlisted bot, fail for anyone
# else, and never exempt the title.
# --------------------------------------------------------------------------- #
RENOVATE_TITLE = "chore(deps): update dependency pymdown-extensions to v11.0.2"
RENOVATE_BODY = """This PR contains the following updates:

| Package | Change | Age | Confidence |
|---|---|---|---|
| pymdown-extensions | `==11.0.1` -> `==11.0.2` | age | confidence |

---

### Release Notes

<details>
<summary>facelessuser/pymdown-extensions (pymdown-extensions)</summary>

#### 11.0.2

- **FIX**: InlineHilite: Improve performance of inline code matching.

</details>

---

### Configuration

**Automerge**: Disabled by config. Please merge this manually once you are satisfied.

---

This PR was generated by Mend Renovate.
"""


def test_allowlisted_bot_body_passes():
    assert check(RENOVATE_TITLE, RENOVATE_BODY, author="renovate[bot]") == []


def test_same_bot_body_fails_for_a_human():
    assert any("missing the required section" in f for f in check(RENOVATE_TITLE, RENOVATE_BODY, author="nolte"))


@pytest.mark.parametrize("author", ["dependabot[bot]", "app/renovate", "renovate", None])
def test_only_the_exact_payload_login_is_exempt(author):
    # `app/renovate` is how the gh CLI renders the login; the payload carries `renovate[bot]`.
    assert check(RENOVATE_TITLE, RENOVATE_BODY, author=author)


def test_bot_title_is_still_checked():
    failures = check("update pymdown-extensions", RENOVATE_BODY, author="renovate[bot]")
    assert failures and all("title" in f for f in failures)


def test_every_allowlist_entry_carries_a_reason():
    assert check_pr_body.EXEMPT_BOT_AUTHORS
    assert all(reason.strip() for reason in check_pr_body.EXEMPT_BOT_AUTHORS.values())


def test_main_reads_the_author_from_the_environment(monkeypatch, capsys):
    monkeypatch.setenv("PR_TITLE", RENOVATE_TITLE)
    monkeypatch.setenv("PR_BODY", RENOVATE_BODY)
    monkeypatch.setenv("PR_AUTHOR", "renovate[bot]")
    assert check_pr_body.main([]) == 0
    assert "skipped for the allowlisted dependency bot renovate[bot]" in capsys.readouterr().out
    monkeypatch.setenv("PR_AUTHOR", "nolte")
    assert check_pr_body.main([]) == 1


def test_bot_fix_title_needs_no_class_sweep():
    # The class sweep is body content like the five sections, so the exemption covers it;
    # a human `fix` PR with the same body still fails.
    title = "fix(deps): update dependency pymdown-extensions to v11.0.2"
    assert check(title, RENOVATE_BODY, author="renovate[bot]") == []
    assert check(title, RENOVATE_BODY, author="nolte")


# --- spec/project/spec-driven-development/ Requirement 2: spec anchor (#585) ---
def _body_with_linked(linked: str) -> str:
    return FIVE_SECTIONS.replace("## Linked issues\n", "## Linked issues\n\n" + linked + "\n", 1)


def test_implementation_change_without_refs_spec_fails():
    failures = check_pr_body.check("feat(ci): x", _body_with_linked("Closes #1"), "nolte", ["scripts/x.py", "spec/a/b/en.md"])
    assert any("Refs spec/<topic>/<slug>/" in f for f in failures)


@pytest.mark.parametrize("title, files, head, linked", [
    ("feat(ci): x", ["scripts/x.py"], None, "Refs spec/project/quality-gate/"),
    ("docs(spec): x", ["spec/project/a/en.md", "spec/project/a/de.md"], None, "Closes #1"),
    ("feat(ci): x", ["scripts/x.py"], "exp/try", "Closes #1"),
    ("docs(prose): fix typos", ["docs/en/index.md"], None, "Refs spec/project/prose-style/"),
    ("feat(ci): x", None, None, "Closes #1"),
])
def test_spec_anchor_exemptions_and_anchored_changes_pass(title, files, head, linked):
    failures = check_pr_body.check(title, _body_with_linked(linked), "nolte", files, head)
    assert not any("Refs spec/<topic>/<slug>/" in f for f in failures)


def test_main_reads_changed_files_and_head_ref_from_the_environment(monkeypatch, tmp_path, capsys):
    files = tmp_path / "files.txt"; files.write_text("scripts/x.py\n")
    monkeypatch.setenv("PR_TITLE", "feat(ci): x")
    monkeypatch.setenv("PR_BODY", _body_with_linked("Closes #1"))
    monkeypatch.setenv("PR_AUTHOR", "nolte")
    monkeypatch.setenv("CHANGED_FILES_FILE", str(files))
    monkeypatch.setenv("PR_HEAD_REF", "feat/x")
    assert check_pr_body.main([]) == 1
    assert "Refs spec/" in capsys.readouterr().out
