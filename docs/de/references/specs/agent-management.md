---
title: Agent-Autorenschaft
audience: [maintainer]
content_mode: reference
track: developer-docs
last_updated: 2026-05-29
---

# Agent-Autorenschaft

Diese Seite fasst `spec/claude/agent-management/de.md` zusammen. Kanonisch gilt `spec/claude/agent-management/en.md`.

**Status:** draft

## Kontext

Das Repository claude-shared sammelt teilbare Claude-Code-Skills und -Agents. Ein Agent hat zwei Formen. Die **Quell-Form** liegt hier (`agents/`). Die **Laufzeit-Form** liegt im Ziel-Projekt (`.claude/agents/` oder `~/.claude/agents/`). Aus ihr lädt Claude Code den Agenten. Dann ruft es das `Agent`-Tool per `subagent_type` auf.

Ohne feste Form driften Agents in Namen, Trigger-Text, Tool-Scope und Prompt-Güte. Dann wird Wiedernutzung brüchig und Routing unsicher.

## Ziele und Nicht-Ziele

**Ziele**

- Feste Form auf der Platte
- Routbar über genaue, trigger-nahe `description`
- Nur nötiger Tool-Zugriff (Principle of Least Authority)
- Portabel, ohne versteckte Bindung
- Klare Liste und Vorlage für Autoren

**Nicht-Ziele**

- Plugin-Paketierung
- Spätere `.claude/`-Konfiguration
- Agent-Verhalten jenseits der Form-Regeln
- Routing-Logik im rufenden Claude

## Anforderungen (Auszug)

### Struktur

- **MUSS [MUST]** einzelne Markdown-Datei `<name>.md` in ASCII-Kebab-Case
- **MUSS [MUST]** YAML-Frontmatter mit `name` und `description`
- **MUSS [MUST]** `name` = Dateiname ohne `.md`
- **MUSS [MUST]** `description` mit klaren Triggern ("einsetzen, wenn …") — keine vagen Fähigkeiten
- **MUSS [MUST]** System-Prompt im Markdown-Body: eine Rolle, erwartete Ausgabeform
- **MUSS [MUST]** Frontmatter und System-Prompt auf Englisch halten (senkt Claudes Kosten)
- **MUSS [MUST]** in sich ruhen — eine einzelne Top-Level-`agents/<name>.md`; kein Geschwister-Ordner `agents/<name>/` (rekursive Suche würde genestetes Markdown als Phantom-Agent listen)

### Tool-Zugriff

- **MUSS [MUST]** `tools`-Feld setzen, wenn knapp; weglassen nur bei echtem Vollzugriff
- **MUSS [MUST]** `tools` knapp halten (Principle of Least Authority)
- **DARF NICHT [MUST NOT]** rein lesenden Agents Schreib-/Edit-/Run-Tools geben
- **SOLLTE [SHOULD]** eigene Tools (`Read`, `Grep`, `Glob`, `Edit`) vor `Bash`-Wegen wählen

### Modell-Wahl

- **KANN [MAY]** `model` setzen (`opus`, `sonnet`, `haiku`)
- **SOLLTE [SHOULD]** ein festes `model` begründen (Kommentar oder System-Prompt)

### Ablageorte

- **MUSS [MUST]** Quelle bei `agents/<name>.md`
- **MUSS [MUST]** Laufzeit aus `.claude/agents/<name>.md`, `~/.claude/agents/<name>.md` oder Plugin-Pfad ladbar
- **DARF NICHT [MUST NOT]** einen festen Ort voraussetzen

### Empfehlungen

- **SOLLTE [SHOULD]** System-Prompt in der Folge: Rolle/Grenzen → Ausgabeform → Arbeitsweise
- **SOLLTE [SHOULD]** klar sagen, ob Agent Code schreibt oder nur sucht
- **SOLLTE [SHOULD]** System-Prompt unter ~200 Zeilen halten
- **SOLLTE [SHOULD]** in `description` gute und (bei Überlapp) schlechte Trigger nennen

## Akzeptanzkriterien

- [ ] Quelldatei existiert unter `agents/<name>.md` in claude-shared mit `<name>` in ASCII-Kebab-Case
- [ ] Agent in konsumierendem Projekt via `subagent_type: <name>` dispatchbar
- [ ] Frontmatter parst als valides YAML mit mindestens `name` und `description`
- [ ] `name` im Frontmatter == Dateiname ohne `.md`
- [ ] `description` enthält konkrete Trigger
- [ ] `tools` (falls gesetzt) ausreichend und ohne unbenutzte Einträge
- [ ] Rein lesende Agents haben keine Schreib-/Edit-/Ausführungs-Tools
- [ ] Agent funktioniert ohne claude-shared-spezifischen Kontext
- [ ] Keine absoluten Pfade
- [ ] Dokumentation von Zielen und Vorbedingungen bei Seiteneffekten

## Offene Fragen

- Soll der Dateiname exakt dem `subagent_type`-String entsprechen?
- Brauchen Agents Versions-/Kompatibilitäts-Metadaten?
- Grenze zwischen Skill und Agent?
- Sollen Agents Delegationsziele deklarieren?
- Konvention für Rückmeldungen (strukturiert vs. freitextlich)?

## Volltext

- Kanonisch (EN): `spec/claude/agent-management/en.md`
- Übersetzung (DE): `spec/claude/agent-management/de.md`
