"""Unit tests for the tech-stack rendering in scripts/docs/gen_portfolio.py.

Covers the normative rules of spec/portfolio/tech-stack/ §Documentation rendering
and §Inheritance semantics that the renderer implements: which global entries a
member inherits, how overrides and regroup records reshape the effective stack,
the group-first / kind-second ordering, the four origin badges, the global-stack
section preceding the per-repository inventory, the tech-stack-discovery §Benefits
paraphrase with its backlink, and the determinism the committed pages rely on.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

GEN = Path(__file__).resolve().parents[1] / "scripts" / "docs" / "gen_portfolio.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("gen_portfolio", GEN)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gp = _load_module()


# --- fixtures --------------------------------------------------------------

GLOBAL_ENTRIES = [
    {"name": "mkdocs", "kind": "docs", "group": "documentation",
     "role": "Docs generator.", "status": "active"},
    {"name": "vale", "kind": "lint", "group": "documentation",
     "role": "Prose linter.", "status": "active"},
    {"name": "pre-commit", "kind": "lint", "group": "quality",
     "role": "Hook framework.", "status": "active"},
    {"name": "renovate", "kind": "dep-bot", "group": "automation",
     "role": "Dependency bot.", "status": "experimental"},
    {"name": "retired-bot", "kind": "other", "group": "automation",
     "role": "Superseded bot.", "status": "deprecated"},
]


@pytest.fixture()
def member():
    return {
        "repo": "nolte/example",
        "repo_url": "https://github.com/nolte/example",
        "capabilities": [],
        "peers": [],
        "tech_stack": {
            "additions": [
                {"name": "astro", "kind": "framework", "group": "build-tooling",
                 "status": "active"},
            ],
            "overrides": [
                {"name": "mkdocs", "rationale": "ships an Astro site | not MkDocs"},
            ],
            "regroup": [
                {"name": "pre-commit", "group": "documentation",
                 "rationale": "runs against docs sources only"},
            ],
        },
    }


def _by_name(rows):
    return {r["name"]: r for r in rows}


# --- inheritance semantics -------------------------------------------------

def test_only_active_and_experimental_global_entries_are_inherited(member):
    rows = _by_name(gp.effective_stack(member, GLOBAL_ENTRIES))
    assert "renovate" in rows, "an experimental global entry is inheritable"
    assert "retired-bot" not in rows, "a deprecated global entry isn't inherited"


def test_override_marks_the_entry_suppressed_and_keeps_its_rationale(member):
    row = _by_name(gp.effective_stack(member, GLOBAL_ENTRIES))["mkdocs"]
    assert row["origin"] == "suppressed"
    assert "Astro site" in row["note"]


def test_regroup_reclassifies_the_group_and_records_the_shift(member):
    row = _by_name(gp.effective_stack(member, GLOBAL_ENTRIES))["pre-commit"]
    assert row["origin"] == "regrouped"
    assert row["group"] == "documentation", "the regrouped value wins over the global one"
    assert "`quality` → `documentation`" in row["note"]
    assert "docs sources" in row["note"]


def test_additions_are_marked_repo_specific(member):
    row = _by_name(gp.effective_stack(member, GLOBAL_ENTRIES))["astro"]
    assert row["origin"] == "repo-specific"
    assert row["group"] == "build-tooling"


def test_a_member_without_a_snapshot_yields_the_bare_inheritable_baseline():
    rows = gp.effective_stack({"repo": "nolte/plain"}, GLOBAL_ENTRIES)
    assert {r["origin"] for r in rows} == {"inherited"}
    assert len(rows) == 4


# --- ordering --------------------------------------------------------------

def test_groups_are_ordered_by_the_spec_group_enum():
    rows = [
        {"name": "a", "kind": "x", "group": "plugin-platform"},
        {"name": "b", "kind": "x", "group": "documentation"},
        {"name": "c", "kind": "x", "group": "automation"},
    ]
    assert [g for g, _ in gp._by_group(rows)] == [
        "documentation", "automation", "plugin-platform",
    ]


def test_an_unknown_group_sorts_last_instead_of_being_dropped():
    rows = [
        {"name": "a", "kind": "x", "group": "future-group"},
        {"name": "b", "kind": "x", "group": "quality"},
    ]
    assert [g for g, _ in gp._by_group(rows)] == ["quality", "future-group"]


def test_entries_are_ordered_by_kind_then_name_inside_a_group():
    rows = [
        {"name": "zebra", "kind": "docs", "group": "documentation"},
        {"name": "alpha", "kind": "lint", "group": "documentation"},
        {"name": "beta", "kind": "lint", "group": "documentation"},
    ]
    _, group_rows = gp._by_group(rows)[0]
    assert [r["name"] for r in group_rows] == ["zebra", "alpha", "beta"]


# --- cell escaping ---------------------------------------------------------

def test_table_cells_neutralise_pipes_and_angle_brackets_and_fold_line_breaks():
    assert gp._cell("a | b") == "a \\| b"
    assert gp._cell("skills/<name>/SKILL.md") == "skills/&lt;name&gt;/SKILL.md"
    assert gp._cell("wrapped\n  text") == "wrapped text"


# --- page composition ------------------------------------------------------

@pytest.fixture()
def snapshot(member):
    return {
        "global_tech_stack": GLOBAL_ENTRIES,
        "members": [member, {"repo": "nolte/plain", "capabilities": [], "peers": []}],
        "historical": [],
    }


@pytest.mark.parametrize("lang", ["en", "de"])
def test_the_page_renders_the_global_stack_before_the_first_member(snapshot, lang):
    page = gp.render_page(lang, snapshot)
    heading = gp.L[lang]["tech_global"]
    assert f"## {heading}" in page
    assert page.index(f"## {heading}") < page.index("## nolte/example")


@pytest.mark.parametrize("lang", ["en", "de"])
def test_the_page_carries_the_benefits_paraphrase_with_a_spec_backlink(snapshot, lang):
    page = gp.render_page(lang, snapshot)
    assert f"### {gp.L[lang]['tech_benefits']}" in page
    assert f"{gp.SPEC_BASE}/tech-stack-discovery/{lang}.md" in page
    # tech-stack-discovery §Benefits anchors every bullet to a goals.md outcome.
    for outcome in ("O-1", "O-2", "O-3"):
        assert outcome in page


@pytest.mark.parametrize("lang", ["en", "de"])
def test_every_origin_badge_reaches_the_rendered_page(snapshot, lang):
    page = gp.render_page(lang, snapshot)
    for badge in gp.L[lang]["origin_badge"].values():
        assert badge in page


def test_a_member_without_a_snapshot_renders_the_baseline_note(snapshot):
    page = gp.render_page("en", snapshot)
    assert gp.L["en"]["tech_member_none"] in page


def test_the_kind_distribution_diagram_carries_a_diagram_source_marker(snapshot):
    page = gp.render_page("en", snapshot)
    assert "<!-- diagram-source: derived—portfolio/aggregate.yml -->" in page
    assert '["framework × 1"]' in page


def test_rendering_is_deterministic(snapshot):
    assert gp.render_page("en", snapshot) == gp.render_page("en", snapshot)
