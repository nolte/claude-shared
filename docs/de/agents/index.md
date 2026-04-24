# Agents

Agents sind spezialisierte Sub-Agents mit fokussiertem Tool-Zugriff und System-Prompt. Claude ruft sie über das `Agent`-Tool mit `subagent_type: <name>` auf. Im Quellbaum von `claude-shared` sollen sie unter `agents/<name>.md` liegen, zur Laufzeit unter `.claude/agents/<name>.md` oder `~/.claude/agents/<name>.md` — oder als Teil des `nolte-shared`-Plugins.

!!! note "Status"
    Das Repository enthält aktuell vier gepflegte Agents: `claude-plugin-developer` (entwirft spec-konforme Plugin-Skills und -Agents), `audience-doc-author` (erzeugt Audience-getriebene Dokumentation gegen die jeweilige Doc-Type-Spec), `audience-review` (reviewt Audience-Artefakte aus `audience-identify`) und `prose-vale-curator` (pflegt Prosa Vale-konform, ohne technische Aussagen zu verändern). Weitere Agents werden nach derselben Spezifikation ([Agent-Autorenschaft](../specs/agent-management.md)) gebaut.

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

- [Agent-Autorenschaft (Spec)](../specs/agent-management.md)
- Quelle (kanonisch EN): `spec/claude/agent-management/en.md`
- Übersetzung (DE): `spec/claude/agent-management/de.md`
