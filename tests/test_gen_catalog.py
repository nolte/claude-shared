"""Regression tests for `scripts/docs/gen_catalog.py` input decoding (#812).

A catalog source or config file that isn't valid UTF-8 must fail the build with
a `CatalogError` naming the file (exit 1 on the CLI, `PluginError` in the MkDocs
hook), never a bare `UnicodeDecodeError` traceback.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

DOCS_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts" / "docs"
sys.path.insert(0, str(DOCS_SCRIPTS))

import gen_catalog as g  # noqa: E402


def _source(root: Path) -> g.SourceRoot:
    return g.SourceRoot(name="p", local=root, skills_path="skills", agents_path="agents",
                        repo_url="https://example.invalid/r", branch="main")


def test_non_utf8_skill_raises_catalog_error_naming_the_file(tmp_path):
    skill = tmp_path / "skills" / "foo" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_bytes(b"---\nname: foo\ndescription: caf\xe9\n---\nbody\n")
    with pytest.raises(g.CatalogError, match=r"SKILL\.md: not valid UTF-8"):
        g.discover_skills(_source(tmp_path), ["en"])


def test_non_utf8_agent_raises_catalog_error_naming_the_file(tmp_path):
    agent = tmp_path / "agents" / "a.md"
    agent.parent.mkdir(parents=True)
    agent.write_bytes(b"---\nname: a\ndescription: \xff\n---\n")
    with pytest.raises(g.CatalogError, match=r"a\.md: not valid UTF-8"):
        g.discover_agents(_source(tmp_path), ["en"])


def test_non_utf8_sources_file_fails_the_cli_with_exit_1(monkeypatch, tmp_path, capsys):
    cfg = tmp_path / "catalog-sources.yml"
    cfg.write_bytes(b"sources: [\xff]\n")
    monkeypatch.setattr(g, "SOURCES_FILE", cfg)
    assert g.main() == 1
    assert "catalog-sources.yml: not valid UTF-8" in capsys.readouterr().err


def test_stale_generated_page_that_isnt_utf8_is_overwritten(tmp_path):
    page = tmp_path / "page.md"
    page.write_bytes(b"\xff")
    g.write_page(page, "fresh\n")
    assert page.read_text(encoding="utf-8") == "fresh\n"
