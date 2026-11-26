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
    assert isinstance(exc.value.__cause__, gen_catalog.CatalogError)


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


# --- #816: unreadable files and a non-mapping sources file name the path -------


def test_unreadable_skill_raises_catalog_error_naming_path(tmp_path: Path) -> None:
    if os.geteuid() == 0:
        pytest.skip("root reads a mode-000 file")
    path = tmp_path / "plugin" / "skills" / "broken" / "SKILL.md"
    path.parent.mkdir(parents=True)
    path.write_text("---\nname: broken\n---\nbody\n", encoding="utf-8")
    path.chmod(0)
    try:
        with pytest.raises(gen_catalog.CatalogError, match="can't be read") as exc:
            gen_catalog.discover_skills(_source(tmp_path / "plugin"), ["en"])
    finally:
        path.chmod(0o644)
    assert str(path) in str(exc.value)


def test_unreadable_sources_file_raises_catalog_error_naming_path(
    isolated_config: Path,
) -> None:
    gen_catalog.SOURCES_FILE.unlink()
    gen_catalog.SOURCES_FILE.mkdir()
    with pytest.raises(gen_catalog.CatalogError, match="can't be read") as exc:
        gen_catalog.load_sources()
    assert str(gen_catalog.SOURCES_FILE) in str(exc.value)


@pytest.mark.parametrize("text", ["- sources\n", "just a string\n", "42\n"])
def test_non_mapping_sources_file_raises_catalog_error_naming_path(
    isolated_config: Path, text: str
) -> None:
    gen_catalog.SOURCES_FILE.write_text(text, encoding="utf-8")
    with pytest.raises(gen_catalog.CatalogError, match="must be a mapping") as exc:
        gen_catalog.load_sources()
    assert str(gen_catalog.SOURCES_FILE) in str(exc.value)


@pytest.mark.parametrize("field, value", [("local", 5), ("name", ["a"]), ("repo_url", 7)])
def test_non_string_source_field_raises_catalog_error_naming_path(
    isolated_config: Path, field: str, value: object
) -> None:
    entry = {"name": "test-plugin", "local": str(isolated_config / "plugin"),
             "repo_url": "https://example.invalid/repo", field: value}
    gen_catalog.SOURCES_FILE.write_text(
        gen_catalog.yaml.safe_dump({"sources": [entry]}), encoding="utf-8")
    with pytest.raises(gen_catalog.CatalogError, match=field) as exc:
        gen_catalog.load_sources()
    assert str(gen_catalog.SOURCES_FILE) in str(exc.value)


@pytest.mark.parametrize("text", ["sources: just-a-string\n", "sources:\n  name: test-plugin\n"])
def test_non_list_sources_raises_catalog_error_naming_path(isolated_config: Path, text: str) -> None:
    gen_catalog.SOURCES_FILE.write_text(text, encoding="utf-8")
    with pytest.raises(gen_catalog.CatalogError, match="'sources' must be a list") as exc:
        gen_catalog.load_sources()
    assert str(gen_catalog.SOURCES_FILE) in str(exc.value)


@pytest.mark.parametrize("field", ["skills_path", "agents_path", "branch"])
@pytest.mark.parametrize("value", [None, 5, ["a"], "", "  "])
def test_malformed_optional_source_field_raises_catalog_error_naming_path(
    isolated_config: Path, field: str, value: object
) -> None:
    entry = {"name": "test-plugin", "local": str(isolated_config / "plugin"),
             "repo_url": "https://example.invalid/repo", field: value}
    gen_catalog.SOURCES_FILE.write_text(
        gen_catalog.yaml.safe_dump({"sources": [entry]}), encoding="utf-8")
    with pytest.raises(gen_catalog.CatalogError, match=field) as exc:
        gen_catalog.load_sources()
    assert str(gen_catalog.SOURCES_FILE) in str(exc.value)


def test_absent_optional_source_fields_keep_their_defaults(isolated_config: Path) -> None:
    """Refutation control: absent skills_path / agents_path / branch keep the defaults."""
    (source,) = gen_catalog.load_sources()
    assert (source.skills_path, source.agents_path, source.branch) == ("skills", "agents", "main")


# --- #816: a frontmatter description that isn't a string names the file ------

# Bare scalars (`42`, `true`) stay strings in this hand-rolled parser; only the
# flow-list and block branches hand the value to yaml.safe_load.
@pytest.mark.parametrize("description", ["[a, b]", "\n  key: value\n  other: 1"])
@pytest.mark.parametrize("kind", ["skill", "agent"])
def test_non_string_description_raises_catalog_error_naming_file_and_key(
    tmp_path: Path, kind: str, description: str
) -> None:
    plugin = tmp_path / "plugin"
    if kind == "skill":
        path = plugin / "skills" / "foo" / "SKILL.md"
        extra = ""
    else:
        path = plugin / "agents" / "foo.md"
        extra = "distribution: plugin\n"
    path.parent.mkdir(parents=True)
    path.write_text(f"---\nname: foo\ndescription: {description}\n{extra}phase: build\n---\nbody\n",
                    encoding="utf-8")
    discover = gen_catalog.discover_skills if kind == "skill" else gen_catalog.discover_agents
    with pytest.raises(gen_catalog.CatalogError, match="'description' must be a string") as exc:
        discover(_source(plugin), ["en"])
    rel = "skills/foo/SKILL.md" if kind == "skill" else "agents/foo.md"
    assert f"test-plugin:{rel}" in str(exc.value)  # the generator's file label
