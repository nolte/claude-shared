---
title: Skill-Autorenschaft
audience: [maintainer]
content_mode: reference
track: developer-docs
last_updated: 2026-05-19
---

# Skill-Autorenschaft

Diese Seite fasst die Spezifikation aus `spec/claude/skill-management/de.md` zusammen. Kanonische Quelle ist `spec/claude/skill-management/en.md`.

**Status:** draft

## Kontext

Das Repository claude-shared sammelt wiederverwendbare Claude-Code-Skills und -Agents für nachgelagerte Projekte. Ein Skill hat zwei Ausprägungen:

- **Quell-Form** in diesem Repository: `skills/<name>/`
- **Laufzeit-Form** im konsumierenden Projekt: `.claude/skills/<name>/` oder `~/.claude/skills/<name>/`

Ohne einheitliche Form driften Skills in Benennung, Trigger-Beschreibungen und innerer Struktur auseinander. Wiederverwendung wird dann brüchig.

## Ziele und Nicht-Ziele

**Ziele**

- Jeder Skill hat dieselbe vorhersehbare Form auf der Festplatte
- Skills sind durch präzise, trigger-orientierte Beschreibungen für Claude auffindbar
- Skills sind portabel über jedes Projekt, das claude-shared konsumiert
- Autoren haben eine klare Checkliste und ein Template als Startpunkt

**Nicht-Ziele**

- Plugin-Paketierung und -Verteilung (separat)
- `.claude/`-Konfiguration in nachgelagerten Projekten
- Konkrete Skill-Inhalte jenseits struktureller Regeln

## Anforderungen (Auszug)

### Struktur

- **MUSS [MUST]** als Ordner `<name>/` in ASCII-Kebab-Case angelegt werden
- **MUSS [MUST]** `SKILL.md` am Ordner-Root enthalten
- **MUSS [MUST]** YAML-Frontmatter mit `name` und `description` enthalten
- **MUSS [MUST]** `name` exakt gleich dem Ordnernamen setzen
- **MUSS [MUST]** eine `description` schreiben, die konkrete User-Trigger benennt, keine abstrakten Fähigkeiten
- **MUSS [MUST]** die Anweisungen in `SKILL.md` auf Englisch halten (senkt Claudes Verarbeitungskosten)
- **MUSS [MUST]** in sich geschlossen sein — alle unterstützenden Assets im Skill-Ordner

### Ablageorte

Quelle: `skills/<name>/` in claude-shared. Laufzeit: `.claude/skills/<name>/`, `~/.claude/skills/<name>/`, oder der Plugin-Pfad. Keine hartkodierten absoluten Pfade.

### Empfehlungen

- **SOLLTE [SHOULD]** eine Section "Hard rules" für Invarianten enthalten
- **SOLLTE [SHOULD]** `SKILL.md` unter ~150 Zeilen halten
- **SOLLTE [SHOULD]** Hilfsdateien in `templates/`, `references/`, `examples/` gruppieren

## Akzeptanzkriterien

- [ ] Quellordner existiert unter `skills/<name>/` mit `<name>` in ASCII-Kebab-Case
- [ ] Skill ist in einem konsumierenden Projekt unter `.claude/skills/<name>/` ladbar
- [ ] `SKILL.md` parst mit gültigem YAML-Frontmatter (`name`, `description`)
- [ ] `name` im Frontmatter entspricht dem Ordnernamen
- [ ] `description` enthält konkrete User-Phrasen als Trigger
- [ ] Skill funktioniert in einem nachgelagerten Projekt ohne claude-shared-spezifischen Kontext
- [ ] Keine absoluten Pfade; alle internen Pfade relativ zur Skill-Datei
- [ ] Wenn der Skill Dateien schreibt, sind Zielorte und Vorbedingungen dokumentiert

## Offene Fragen

- Soll der Ordnername zwingend dem nutzerseitigen Slash-Command entsprechen oder darf er abweichen?
- Brauchen Skills Versions- oder Kompatibilitäts-Metadaten?
- Wo verläuft die Grenze zwischen Skill und Agent?
- Gibt es eine maximale Verschachtelungstiefe für Supporting-Subfolder?

## Volltext

- Kanonisch (EN): `spec/claude/skill-management/en.md`
- Übersetzung (DE): `spec/claude/skill-management/de.md`
