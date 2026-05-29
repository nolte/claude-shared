---
title: Agent-Autorenschaft
audience: [maintainer]
content_mode: reference
track: developer-docs
last_updated: 2026-05-29
---

# Agent-Autorenschaft

Diese Seite fasst die Spezifikation aus `spec/claude/agent-management/de.md` zusammen. Kanonische Quelle ist `spec/claude/agent-management/en.md`.

**Status:** draft

## Kontext

Das Repository claude-shared sammelt wiederverwendbare Claude-Code-Skills und -Agents. Ein Agent hat zwei Ausprägungen: eine **Quell-Form** hier (`agents/`) und eine **Laufzeit-Form** im konsumierenden Projekt (`.claude/agents/` oder `~/.claude/agents/`), aus der Claude Code den Agent lädt und das `Agent`-Tool per `subagent_type` dispatcht.

Ohne einheitliche Form driften Agents in Benennung, Trigger-Beschreibung, Tool-Scoping und System-Prompt-Qualität — Wiederverwendung wird brüchig und Routing unzuverlässig.

## Ziele und Nicht-Ziele

**Ziele**

- Einheitliche Form auf der Festplatte
- Routbar über präzise, trigger-orientierte `description`
- Minimal notwendiger Tool-Zugriff (Principle of Least Authority)
- Portabel ohne versteckte Abhängigkeiten
- Klare Checkliste und Template für Autoren

**Nicht-Ziele**

- Plugin-Paketierung
- Nachgelagerte `.claude/`-Konfiguration
- Konkretes Agent-Verhalten jenseits struktureller Regeln
- Orchestrierungslogik im aufrufenden Claude

## Anforderungen (Auszug)

### Struktur

- **MUSS [MUST]** einzelne Markdown-Datei `<name>.md` in ASCII-Kebab-Case
- **MUSS [MUST]** YAML-Frontmatter mit `name` und `description`
- **MUSS [MUST]** `name` = Dateiname ohne `.md`
- **MUSS [MUST]** `description` mit konkreten Triggern ("einsetzen, wenn …") — nicht abstrakte Fähigkeiten
- **MUSS [MUST]** System-Prompt im Markdown-Body: eine Verantwortlichkeit, erwartete Ausgabeform
- **MUSS [MUST]** Frontmatter und System-Prompt auf Englisch halten (Token-Effizienz)
- **MUSS [MUST]** in sich geschlossen sein — eine einzelne Top-Level-`agents/<name>.md`; kein Schwester-Ordner `agents/<name>/` (rekursive Discovery würde genestete Markdown als Phantom-Agent registrieren)

### Tool-Zugriff

- **MUSS [MUST]** `tools`-Feld deklarieren, wenn eingeschränkt; weglassen nur bei tatsächlichem Vollzugriff
- **MUSS [MUST]** `tools` minimal halten (Principle of Least Authority)
- **DARF NICHT [MUST NOT]** rein lesenden Agents Schreib-/Edit-/Ausführungs-Tools geben
- **SOLLTE [SHOULD]** dedizierte Tools (`Read`, `Grep`, `Glob`, `Edit`) gegenüber `Bash`-Äquivalenten bevorzugen

### Modell-Wahl

- **KANN [MAY]** `model` deklarieren (`opus`, `sonnet`, `haiku`)
- **SOLLTE [SHOULD]** ein fixiertes `model` begründen (Kommentar oder System-Prompt)

### Ablageorte

- **MUSS [MUST]** Quelle bei `agents/<name>.md`
- **MUSS [MUST]** Laufzeit aus `.claude/agents/<name>.md`, `~/.claude/agents/<name>.md` oder Plugin-Pfad ladbar
- **DARF NICHT [MUST NOT]** einen bestimmten Installationsort voraussetzen

### Empfehlungen

- **SOLLTE [SHOULD]** System-Prompt in der Reihenfolge: Rolle/Grenzen → Ausgabeformat → Arbeitsweise
- **SOLLTE [SHOULD]** explizit festhalten, ob Agent Code schreibt oder nur recherchiert
- **SOLLTE [SHOULD]** System-Prompt unter ~200 Zeilen halten
- **SOLLTE [SHOULD]** in `description` positive und (bei Überschneidung) negative Trigger nennen

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
