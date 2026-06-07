---
title: Schnittstellen und Verträge
audience: [external-contributor, maintainer]
content_mode: reference
track: developer-docs
last_updated: 2026-06-06
---

# Schnittstellen und Verträge

Jede Schnittstelle, die `claude-shared` bereitstellt und die eine andere
Komponente, ein Plugin oder ein menschlicher Aufrufer ansteuern kann. Der
Großteil der Detail-Beschreibung pro Eintrag liegt in den generierten
Katalogseiten unter [Skills](../skills/index.md) und
[Agents](../agents/index.md); diese Seite zählt die Schnittstellen-*Arten* auf
und benennt, wo der jeweilige Vertrag definiert ist.

## Slash-Commands (Skills)

Jeder Skill unter `skills/<name>/SKILL.md` ist als Slash-Command
`/nolte-shared:<skill>` aufrufbar. Der Command-Name entspricht dem
Skill-Ordnernamen. Der maßgebliche Vertrag pro Skill (Trigger-Formulierungen,
Operationen, Eingaben) ist das Frontmatter und der Body der jeweiligen
`SKILL.md`; der gerenderte Katalog liegt unter [Skills](../skills/index.md).

## Agents (Subagent-Typen)

Jeder Agent unter `agents/<name>.md` ist als Sub-Agent dispatchbar, dessen
`subagent_type` dem Agent-Dateinamen entspricht. Das Frontmatter des Agents
deklariert seine Tool-Allow-List und das Modell; sein Body ist der
System-Prompt. Der gerenderte Katalog liegt unter [Agents](../agents/index.md).

## Plugin-Manifest-Vertrag

`.claude-plugin/plugin.json` ist der Install-Zeit-Vertrag, den der
Plugin-Marketplace konsumiert: Er deklariert `name` (`nolte-shared`, Teil jeder
Slash-Invocation), `version`, `author` und den Repository-Pointer. Der
Marketplace-Katalog (`.claude-plugin/marketplace.json`) ist die
Downstream-Installationsquelle.

## Spezifikations-Frontmatter-Vertrag

Jede Spec unter `spec/<area>/<topic>/<lang>.md` folgt der von
`spec/project/spec-driven-development/` geregelten Struktur und wird über
`spec/.spec-config.yml` konfiguriert (kanonische Sprache,
Übersetzungssprachen). Der generierte Index ist `spec/README.md` (nicht von
Hand bearbeiten).

## MkDocs-Frontmatter-Vertrag pro Seite

Jede Seite unter `docs/<lang>/` deklariert das fünf-Schlüssel-Frontmatter-MUST
(`title`, `audience`, `content_mode`, `track`, `last_updated`) gemäß
`spec/project/mkdocs-structure/` §Per-page structure und
`spec/project/docs-audience-tracks/` §Per-page contract. Katalog-generierte
Seiten tragen `last_updated: generated`. Das Frontmatter ist der Vertrag, auf
den sich Downstream-Tooling (`docs-freshness`, der Katalog-Generator) verlässt.

## Quellen

- `spec/project/docs-audience-tracks/` §Developer-docs content contract (Interface-Block)
- `spec/project/mkdocs-structure/` §Per-page structure
- `spec/claude/skill-agent-catalog/` — der Generator, der die Detail-Beschreibung pro Eintrag trägt
- `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`
