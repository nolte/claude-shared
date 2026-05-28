---
title: Agents
audience: [maintainer]
content_mode: explanation
track: developer-docs
last_updated: 2026-05-19
---

# Agents

Agents sind spezialisierte Sub-Agents mit fokussiertem Tool-Zugriff und eigenem System-Prompt. Claude ruft sie über das `Agent`-Tool mit `subagent_type: <name>` auf.

Im Quellbaum von `claude-shared` liegen sie unter `agents/<name>.md`. Zur Laufzeit greift Claude Code auf sie unter `.claude/agents/<name>.md`, unter `~/.claude/agents/<name>.md` oder als Teil des `nolte-shared`-Plugins zu.

## Enthaltene Agents

| Agent | Zweck |
|-------|-------|
| `claude-plugin-developer` | Entwirft spec-konforme Plugin-Skills und -Agents für `nolte-shared` |
| `audience-doc-author` | Erzeugt oder überarbeitet zielgruppengetriebene Dokumentation gegen ein vorhandenes Audience-Artefakt |
| `audience-review` | Reviewt Audience-Artefakte aus `audience-identify` (nur lesend) |
| `spec-readiness-reviewer` | Prüft Specs auf Widersprüche, Audience-Fit und Requirement-vs-Acceptance-Vollständigkeit |
| `docs-freshness-checker` | Auditiert MkDocs-Dokumentation auf Sprach-Parität, tote Links, stale Pfadverweise, ADR-Hygiene |
| `prose-vale-curator` | Pflegt Prosa Vale-konform, ohne technische Aussagen zu verändern |
| `png-to-transparent-svg` | Wandelt PNGs mit eingebranntem Karomuster in SVGs mit echter Alpha-Transparenz |
| `feature-consistency-reviewer` | Prüft ein draft-Feature gegen Feature-Korpus, Source-Roots und Spec-Bestand auf Überlappung, Duplikation, Drift und Prior Art |

Alle Agents folgen derselben Spezifikation ([Agent-Autorenschaft](../references/specs/agent-management.md)). Kanonische Quelle pro Agent: `agents/<name>.md` im Quellbaum.

## Form eines Agents

Ein Agent ist eine einzelne Markdown-Datei mit YAML-Frontmatter und System-Prompt im Body:

```markdown
---
name: <kebab-case-name>
description: Konkrete Trigger ("einsetzen, wenn …") — nicht abstrakte Fähigkeiten.
tools: [Read, Grep, Glob]   # optional, Prinzip der minimalen Rechte
model: sonnet               # optional
---

# System Prompt

Rolle und Grenzen. Ausgabeformat. Arbeitsweise.
```

Das Frontmatter `name` muss dem Dateinamen ohne `.md` entsprechen. `tools` wird weggelassen, wenn der Agent die volle Tool-Oberfläche braucht — sonst auf den minimal nötigen Umfang gesetzt. Rein lesende Agents haben **keine** Schreib-/Edit-/Ausführungs-Tools.

## Quell- vs. Laufzeit-Ort

| Kontext | Pfad |
|---------|------|
| claude-shared Quellbaum | `agents/<name>.md` |
| Konsumierendes Projekt, projektbezogen | `.claude/agents/<name>.md` |
| Konsumierendes Projekt, benutzerbezogen | `~/.claude/agents/<name>.md` |
| Über Plugin ausgeliefert | der dafür vorgesehene Agents-Pfad des Plugins |

Agents dürfen keinen bestimmten Installationsort voraussetzen; alle internen Referenzen bleiben relativ zur Agent-Datei oder zum Projekt.

## Autor-Regeln

Die vollständigen Regeln, Akzeptanzkriterien und offenen Fragen stehen in:

- [Agent-Autorenschaft (Spec)](../references/specs/agent-management.md)
- Quelle (kanonisch EN): `spec/claude/agent-management/en.md`
- Übersetzung (DE): `spec/claude/agent-management/de.md`
