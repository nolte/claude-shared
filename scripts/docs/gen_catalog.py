#!/usr/bin/env python3
"""Generate the Skills and Agents catalog as physical Markdown files.

Operationalises ``spec/claude/skill-agent-catalog/<canonical_language>.md``.

Architecturally this script writes physical files under ``docs/<lang>/`` rather
than emitting through ``mkdocs-gen-files``. The reason: the installed
``mkdocs-static-i18n`` (1.3.x) only classifies files whose ``abs_src_path`` is
under ``mkdocs_config.docs_dir``; ``gen-files`` virtual files live in a temp
directory and are silently dropped from the i18n file set. Writing physical
files satisfies the spec's hard rules just as well — they're gitignored under
``/docs/<lang>/skills/`` etc. so the "no committed generated markdown" rule
still holds.

Sources are configured in ``docs/catalog-sources.yml``. For each configured
plugin source root the script walks ``<local>/<skills_path>/<name>/SKILL.md``
and ``<local>/<agents_path>/<name>.md``, parses the YAML-ish frontmatter, and
emits one catalog page per artifact per configured docs language plus
``SUMMARY.md`` files for ``mkdocs-literate-nav`` and a ``tags.md`` index.

The build fails (non-zero exit, ``CatalogError``) on malformed frontmatter;
the spec forbids silently skipping broken artefacts.
"""

from __future__ import annotations

import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = REPO_ROOT / "docs"
SOURCES_FILE = DOCS_DIR / "catalog-sources.yml"
MKDOCS_FILE = REPO_ROOT / "mkdocs.yml"

CHROME = {
    "de": {
        "skills_title": "Skills",
        "skills_intro": (
            "Auto-generierter Katalog aller Skills aus den konfigurierten Plugin-Source-Roots. "
            "Inhalt stammt direkt aus den `SKILL.md`-Frontmattern und -Bodies."
        ),
        "agents_title": "Agents",
        "agents_intro": (
            "Auto-generierter Katalog aller Agents aus den konfigurierten Plugin-Source-Roots. "
            "Inhalt stammt direkt aus den Agent-Markdown-Dateien."
        ),
        "tags_title": "Tags",
        "tags_intro": (
            "Querverweise: jeder Tag listet alle Skills und Agents, die ihn deklarieren."
        ),
        "no_tags": "Bisher sind keine Tags vergeben.",
        "source_label": "Quelle",
        "distribution_label": "Distribution",
        "tags_label": "Tags",
        "plugin_label": "Plugin",
    },
    "en": {
        "skills_title": "Skills",
        "skills_intro": (
            "Auto-generated catalog of every skill discovered across the configured plugin source "
            "roots. Content is taken verbatim from each `SKILL.md` frontmatter and body."
        ),
        "agents_title": "Agents",
        "agents_intro": (
            "Auto-generated catalog of every agent discovered across the configured plugin source "
            "roots. Content is taken verbatim from each agent markdown file."
        ),
        "tags_title": "Tags",
        "tags_intro": (
            "Cross-reference: each tag links to every skill and agent that declares it."
        ),
        "no_tags": "No tags have been declared yet.",
        "source_label": "Source",
        "distribution_label": "Distribution",
        "tags_label": "Tags",
        "plugin_label": "Plugin",
    },
}


class CatalogError(RuntimeError):
    """Raised when an artefact is malformed; fails the build."""


@dataclass(frozen=True)
class SourceRoot:
    name: str
    local: Path
    skills_path: str
    agents_path: str
    repo_url: str
    branch: str


@dataclass
class Artifact:
    kind: str  # "skill" or "agent"
    plugin: str
    name: str
    description: str
    distribution: str | None
    tags: list[str]
    body: str
    source_relpath: str
    repo_url: str
    branch: str

    @property
    def source_url(self) -> str:
        return f"{self.repo_url}/blob/{self.branch}/{self.source_relpath}"


FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?(.*)\Z", re.DOTALL)
FRONTMATTER_LINE_RE = re.compile(r"\A([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)\Z")
TAG_RE = re.compile(r"\A[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def parse_frontmatter(text: str, file_label: str) -> tuple[dict, str]:
    """Parse the YAML-ish frontmatter block leniently.

    Skill and agent frontmatter is flat (no nested mappings) but ``description``
    routinely contains colons followed by spaces — for example ``status: planned``
    — which PyYAML rejects as ambiguous plain scalars. We treat each top-level
    line as ``key: value`` with the value taken verbatim, handling YAML block
    scalars (``>``, ``>-``, ``|``, ``|-``) via continuation collection. Bracketed
    list values like ``tags: [a, b]`` are delegated to PyYAML.
    """

    match = FRONTMATTER_RE.match(text)
    if not match:
        raise CatalogError(f"{file_label}: missing YAML frontmatter block")
    raw, body = match.group(1), match.group(2)
    lines = raw.split("\n")
    meta: dict[str, object] = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        m = FRONTMATTER_LINE_RE.match(line)
        if not m:
            raise CatalogError(
                f"{file_label}: cannot parse frontmatter line: {line!r}"
            )
        key, raw_value = m.group(1), m.group(2).strip()
        i += 1
        if raw_value in (">", ">-", "|", "|-"):
            block_lines: list[str] = []
            while i < len(lines):
                cont = lines[i]
                if cont and not cont[0].isspace():
                    break
                block_lines.append(cont.strip())
                i += 1
            if raw_value.startswith(">"):
                meta[key] = " ".join(filter(None, block_lines))
            else:
                meta[key] = "\n".join(block_lines).rstrip()
        elif raw_value.startswith("[") and raw_value.endswith("]"):
            try:
                meta[key] = yaml.safe_load(raw_value)
            except yaml.YAMLError as exc:
                raise CatalogError(
                    f"{file_label}: invalid list value for {key!r}: {exc}"
                ) from exc
        elif (
            len(raw_value) >= 2
            and raw_value[0] == raw_value[-1]
            and raw_value[0] in ("'", '"')
        ):
            meta[key] = raw_value[1:-1]
        else:
            meta[key] = raw_value
    return meta, body.lstrip("\n")


def load_sources() -> list[SourceRoot]:
    with SOURCES_FILE.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    sources_raw = data.get("sources") or []
    if not sources_raw:
        raise CatalogError(f"{SOURCES_FILE}: no sources configured")
    result: list[SourceRoot] = []
    for idx, entry in enumerate(sources_raw):
        if not isinstance(entry, dict):
            raise CatalogError(f"{SOURCES_FILE}: source #{idx} is not a mapping")
        try:
            local_value = entry["local"]
            name = entry["name"]
            repo_url = entry["repo_url"]
        except KeyError as exc:
            raise CatalogError(f"{SOURCES_FILE}: source #{idx} missing field {exc}") from exc
        local_path = (REPO_ROOT / local_value).resolve()
        result.append(
            SourceRoot(
                name=name,
                local=local_path,
                skills_path=entry.get("skills_path", "skills"),
                agents_path=entry.get("agents_path", "agents"),
                repo_url=repo_url.rstrip("/"),
                branch=entry.get("branch", "main"),
            )
        )
    return result


def load_languages() -> list[str]:
    with MKDOCS_FILE.open("r", encoding="utf-8") as fh:
        raw = fh.read()
    locales = re.findall(r"^\s*-\s*locale:\s*([a-zA-Z][\w-]*)", raw, re.MULTILINE)
    if not locales:
        raise CatalogError(
            f"{MKDOCS_FILE}: no i18n locales found; mkdocs-static-i18n configuration required"
        )
    return locales


def _normalize_tags(raw, label: str) -> list[str]:
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise CatalogError(f"{label}: frontmatter 'tags' must be a list")
    if len(raw) > 5:
        raise CatalogError(f"{label}: frontmatter 'tags' must have at most 5 entries")
    tags: list[str] = []
    for tag in raw:
        if not isinstance(tag, str):
            raise CatalogError(f"{label}: tag entries must be strings")
        if len(tag) > 30 or not TAG_RE.match(tag):
            raise CatalogError(
                f"{label}: tag '{tag}' must be lowercase ASCII kebab-case, ≤30 chars"
            )
        tags.append(tag)
    return tags


def discover_skills(source: SourceRoot) -> list[Artifact]:
    skills_dir = source.local / source.skills_path
    if not skills_dir.is_dir():
        return []
    artefacts: list[Artifact] = []
    for entry in sorted(skills_dir.iterdir()):
        skill_md = entry / "SKILL.md"
        if not skill_md.is_file():
            continue
        label = f"{source.name}:{source.skills_path}/{entry.name}/SKILL.md"
        text = skill_md.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(text, label)
        name = meta.get("name")
        if not name:
            raise CatalogError(f"{label}: frontmatter missing 'name'")
        if name != entry.name:
            raise CatalogError(
                f"{label}: frontmatter name '{name}' must match folder name '{entry.name}'"
            )
        description = meta.get("description")
        if not description:
            raise CatalogError(f"{label}: frontmatter missing 'description'")
        artefacts.append(
            Artifact(
                kind="skill",
                plugin=source.name,
                name=str(name),
                description=str(description),
                distribution=None,
                tags=_normalize_tags(meta.get("tags"), label),
                body=body,
                source_relpath=f"{source.skills_path}/{entry.name}/SKILL.md",
                repo_url=source.repo_url,
                branch=source.branch,
            )
        )
    return artefacts


def discover_agents(source: SourceRoot) -> list[Artifact]:
    agents_dir = source.local / source.agents_path
    if not agents_dir.is_dir():
        return []
    artefacts: list[Artifact] = []
    for entry in sorted(agents_dir.iterdir()):
        if entry.suffix != ".md" or not entry.is_file():
            continue
        label = f"{source.name}:{source.agents_path}/{entry.name}"
        text = entry.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(text, label)
        name = meta.get("name")
        if not name:
            raise CatalogError(f"{label}: frontmatter missing 'name'")
        if name != entry.stem:
            raise CatalogError(
                f"{label}: frontmatter name '{name}' must match file stem '{entry.stem}'"
            )
        description = meta.get("description")
        if not description:
            raise CatalogError(f"{label}: frontmatter missing 'description'")
        distribution = meta.get("distribution")
        if distribution not in ("plugin", "project"):
            raise CatalogError(
                f"{label}: frontmatter 'distribution' must be 'plugin' or 'project'"
            )
        artefacts.append(
            Artifact(
                kind="agent",
                plugin=source.name,
                name=str(name),
                description=str(description),
                distribution=str(distribution),
                tags=_normalize_tags(meta.get("tags"), label),
                body=body,
                source_relpath=f"{source.agents_path}/{entry.name}",
                repo_url=source.repo_url,
                branch=source.branch,
            )
        )
    return artefacts


def render_page(artifact: Artifact, chrome: dict) -> str:
    parts: list[str] = []
    parts.append(f"# {artifact.name}\n")
    parts.append(f"_{artifact.description}_\n")
    parts.append("")
    parts.append(f"- **{chrome['plugin_label']}:** `{artifact.plugin}`")
    if artifact.distribution:
        parts.append(f"- **{chrome['distribution_label']}:** `{artifact.distribution}`")
    if artifact.tags:
        tag_list = ", ".join(f"`{t}`" for t in artifact.tags)
        parts.append(f"- **{chrome['tags_label']}:** {tag_list}")
    parts.append(
        f"- **{chrome['source_label']}:** "
        f"[{artifact.source_relpath}]({artifact.source_url})"
    )
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append(artifact.body.rstrip() + "\n")
    return "\n".join(parts)


def group_by_plugin(artefacts: Iterable[Artifact]) -> dict[str, list[Artifact]]:
    groups: dict[str, list[Artifact]] = {}
    for art in artefacts:
        groups.setdefault(art.plugin, []).append(art)
    for plugin in groups:
        groups[plugin].sort(key=lambda a: a.name)
    return dict(sorted(groups.items()))


def write_page(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def emit_section(
    lang: str,
    section: str,  # "skills" or "agents"
    artefacts: list[Artifact],
    chrome: dict,
) -> None:
    section_dir = DOCS_DIR / lang / section
    if section_dir.exists():
        shutil.rmtree(section_dir)
    section_dir.mkdir(parents=True, exist_ok=True)

    groups = group_by_plugin(artefacts)

    for art in artefacts:
        write_page(section_dir / art.plugin / f"{art.name}.md", render_page(art, chrome))

    title_key = f"{section}_title"
    intro_key = f"{section}_intro"

    index_parts = [f"# {chrome[title_key]}\n\n{chrome[intro_key]}\n"]
    for plugin, items in groups.items():
        index_parts.append(f"\n## {plugin}\n")
        for art in items:
            index_parts.append(
                f"- [`{art.name}`]({plugin}/{art.name}.md) — {art.description}"
            )
    write_page(section_dir / "index.md", "\n".join(index_parts) + "\n")

    summary_parts = [f"* [{chrome[title_key]}](index.md)"]
    for plugin, items in groups.items():
        summary_parts.append(f"* {plugin}")
        for art in items:
            summary_parts.append(f"    * [{art.name}]({plugin}/{art.name}.md)")
    write_page(section_dir / "SUMMARY.md", "\n".join(summary_parts) + "\n")


def emit_tag_index(lang: str, all_artefacts: list[Artifact], chrome: dict) -> None:
    by_tag: dict[str, list[Artifact]] = {}
    for art in all_artefacts:
        for tag in art.tags:
            by_tag.setdefault(tag, []).append(art)
    for tag in by_tag:
        by_tag[tag].sort(key=lambda a: (a.kind, a.plugin, a.name))

    path = DOCS_DIR / lang / "tags.md"
    parts = [f"# {chrome['tags_title']}\n\n{chrome['tags_intro']}\n"]
    if not by_tag:
        parts.append(f"\n{chrome['no_tags']}\n")
    else:
        for tag in sorted(by_tag):
            parts.append(f"\n## `{tag}`\n")
            for art in by_tag[tag]:
                section = "skills" if art.kind == "skill" else "agents"
                href = f"{section}/{art.plugin}/{art.name}.md"
                parts.append(f"- [{art.name}]({href}) — {art.plugin}")
    write_page(path, "\n".join(parts) + "\n")


def main() -> int:
    try:
        sources = load_sources()
        languages = load_languages()

        skills: list[Artifact] = []
        agents: list[Artifact] = []
        for source in sources:
            skills.extend(discover_skills(source))
            agents.extend(discover_agents(source))

        for lang in languages:
            chrome = CHROME.get(lang, CHROME["en"])
            emit_section(lang, "skills", skills, chrome)
            emit_section(lang, "agents", agents, chrome)
            emit_tag_index(lang, skills + agents, chrome)
    except CatalogError as exc:
        print(f"gen_catalog: {exc}", file=sys.stderr)
        return 1

    print(
        f"gen_catalog: wrote {len(skills)} skill(s) and {len(agents)} agent(s) "
        f"for languages {languages}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
