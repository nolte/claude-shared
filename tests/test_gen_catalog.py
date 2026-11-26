"""Tests for undecodable-input handling in scripts/docs/gen_catalog.py.

A non-UTF-8 input file must surface through the generator's own error channel
(``CatalogError`` -> CLI exit 1 / MkDocs ``PluginError``) naming the offending
path, never as a bare ``UnicodeDecodeError`` traceback. An undecodable
*generated* page is stale output and gets overwritten; an identical page stays
untouched so the generator remains idempotent.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "gen_catalog", ROOT / "scripts" / "docs" / "gen_catalog.py"
)
gen_catalog = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = gen_catalog  # dataclasses resolve the defining module by name
assert _spec.loader is not None
_spec.loader.exec_module(gen_catalog)

# 0xff is never valid in UTF-8, so decoding fails at byte 0 of the body.
UNDECODABLE = b"---\nname: broken\n---\n\xff\xfe body\n"


def _source(local: Path) -> gen_catalog.SourceRoot:
    return gen_catalog.SourceRoot(
        name="test-plugin",
        local=local,
        skills_path="skills",
        agents_path="agents",
        repo_url="https://example.invalid/repo",
        branch="main",
    )


@pytest.fixture
def undecodable_skill(tmp_path: Path) -> Path:
    path = tmp_path / "plugin" / "skills" / "broken" / "SKILL.md"
    path.parent.mkdir(parents=True)
    path.write_bytes(UNDECODABLE)
    return path


@pytest.fixture
def undecodable_agent(tmp_path: Path) -> Path:
    path = tmp_path / "plugin" / "agents" / "broken.md"
    path.parent.mkdir(parents=True)
    path.write_bytes(UNDECODABLE)
    return path


@pytest.fixture
def isolated_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the generator at a throwaway sources file, mkdocs file and docs dir."""
    plugin = tmp_path / "plugin"
    plugin.mkdir(exist_ok=True)
    sources = tmp_path / "catalog-sources.yml"
    sources.write_text(
        "sources:\n"
        "  - name: test-plugin\n"
        f"    local: {plugin}\n"
        "    repo_url: https://example.invalid/repo\n",
        encoding="utf-8",
    )
    mkdocs = tmp_path / "mkdocs.yml"
    mkdocs.write_text("plugins:\n  - i18n:\n      languages:\n        - locale: en\n", encoding="utf-8")
    monkeypatch.setattr(gen_catalog, "SOURCES_FILE", sources)
    monkeypatch.setattr(gen_catalog, "MKDOCS_FILE", mkdocs)
    monkeypatch.setattr(gen_catalog, "DOCS_DIR", tmp_path / "docs")
    return tmp_path


def test_undecodable_skill_raises_catalog_error_naming_path(undecodable_skill: Path) -> None:
    with pytest.raises(gen_catalog.CatalogError, match="not valid UTF-8") as exc:
        gen_catalog.discover_skills(_source(undecodable_skill.parents[2]), ["en"])
    assert str(undecodable_skill) in str(exc.value)


def test_undecodable_agent_raises_catalog_error_naming_path(undecodable_agent: Path) -> None:
    with pytest.raises(gen_catalog.CatalogError, match="not valid UTF-8") as exc:
        gen_catalog.discover_agents(_source(undecodable_agent.parents[1]), ["en"])
    assert str(undecodable_agent) in str(exc.value)


def test_undecodable_sources_file_raises_catalog_error_naming_path(
    isolated_config: Path,
) -> None:
    gen_catalog.SOURCES_FILE.write_bytes(b"sources:\n  - name: \xff\n")
    with pytest.raises(gen_catalog.CatalogError, match="not valid UTF-8") as exc:
        gen_catalog.load_sources()
    assert str(gen_catalog.SOURCES_FILE) in str(exc.value)


def test_invalid_yaml_sources_file_raises_catalog_error_naming_path(
    isolated_config: Path,
) -> None:
    gen_catalog.SOURCES_FILE.write_text("sources: [unclosed\n", encoding="utf-8")
    with pytest.raises(gen_catalog.CatalogError, match="invalid YAML") as exc:
        gen_catalog.load_sources()
    assert str(gen_catalog.SOURCES_FILE) in str(exc.value)


def test_undecodable_mkdocs_file_raises_catalog_error_naming_path(
    isolated_config: Path,
) -> None:
    gen_catalog.MKDOCS_FILE.write_bytes(b"site_name: \xff\n")
    with pytest.raises(gen_catalog.CatalogError, match="not valid UTF-8") as exc:
        gen_catalog.load_languages()
    assert str(gen_catalog.MKDOCS_FILE) in str(exc.value)


def test_main_exits_1_and_names_undecodable_path(
    isolated_config: Path, undecodable_skill: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert gen_catalog.main() == 1
    err = capsys.readouterr().err
    assert err.startswith("gen_catalog: ")
    assert str(undecodable_skill) in err
    assert "Traceback" not in err


def test_on_pre_build_raises_plugin_error_naming_path(
    isolated_config: Path, undecodable_agent: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The CI test lane doesn't install MkDocs; the hook imports PluginError lazily,
    # so a stand-in `mkdocs.exceptions` module exercises the same code path.
    class PluginError(Exception):
        pass

    exceptions = types.ModuleType("mkdocs.exceptions")
    exceptions.PluginError = PluginError
    mkdocs = types.ModuleType("mkdocs")
    mkdocs.exceptions = exceptions
    monkeypatch.setitem(sys.modules, "mkdocs", mkdocs)
    monkeypatch.setitem(sys.modules, "mkdocs.exceptions", exceptions)

    with pytest.raises(PluginError) as exc:
        gen_catalog.on_pre_build(config=None)
    assert str(undecodable_agent) in str(exc.value)


def test_write_page_overwrites_undecodable_existing_page(tmp_path: Path) -> None:
    page = tmp_path / "out" / "page.md"
    page.parent.mkdir()
    page.write_bytes(b"stale \xff output\n")
    gen_catalog.write_page(page, "fresh content\n")
    assert page.read_text(encoding="utf-8") == "fresh content\n"


def test_write_page_keeps_identical_page_untouched(tmp_path: Path) -> None:
    page = tmp_path / "page.md"
    page.write_text("same content\n", encoding="utf-8")
    os.utime(page, ns=(1_000_000_000_000_000_000, 1_000_000_000_000_000_000))
    gen_catalog.write_page(page, "same content\n")
    assert page.stat().st_mtime_ns == 1_000_000_000_000_000_000
