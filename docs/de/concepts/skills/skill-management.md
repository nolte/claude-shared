---
title: Skill-Management
audience: [maintainer]
content_mode: explanation
track: developer-docs
last_updated: 2026-05-19
---

# Skill-Management

Der Skill `skill-management` gerüstet und validiert Claude-Code-Skills. Er liegt unter `skills/skill-management/SKILL.md` und folgt der Spezifikation [Skill-Autorenschaft](../../specs/skill-management.md).

## Wann einsetzen

- "neuen Skill anlegen", "Skill für X erstellen"
- "create a new skill", "scaffold a skill for X", "add a skill to this repo"
- "validate this skill", "check if this skill follows our conventions"

## Zielort entscheiden

Vor dem Schreiben entscheidet der Skill, wo die neuen Skill-Dateien landen:

| Kontext | Zielpfad |
|---------|---------|
| claude-shared Quellbaum (top-level `skills/`, README erwähnt `claude-shared`) | `skills/<name>/` |
| Konsumierendes Projekt, projektbezogen | `.claude/skills/<name>/` |
| Konsumierendes Projekt, benutzerbezogen | `~/.claude/skills/<name>/` |

Nach dem Schreiben in den Quellbaum weist der Skill darauf hin, dass für den `/skills`-Dialog zusätzlich eine Runtime-Location (typischerweise per Symlink) nötig ist.

## Operationen

### 1. Neuen Skill anlegen

1. Erhebt vom Nutzer **Purpose**, **Triggers** (mindestens drei konkrete Phrasen), **Name** (ASCII-Kebab-Case).
2. Prüft, dass der Zielpfad noch nicht existiert.
3. Schreibt `SKILL.md` mit Frontmatter (`name`, `description`) und kurzem Body (Zweck, Sprachpolitik, Operationen, Hard Rules).
4. Erstellt Subfolder (`templates/`, `references/`, `examples/`) nur wenn tatsächlich benötigt — keine leeren Platzhalter.
5. Bestätigt in der Sprache des Nutzers mit den angelegten Pfaden.

### 2. Validieren

Checkliste, die der Skill abarbeitet:

- [ ] Ordnername ist ASCII-Kebab-Case
- [ ] `SKILL.md` liegt am Ordner-Root
- [ ] Frontmatter parst, enthält `name` und `description`
- [ ] `name` entspricht dem Ordnernamen
- [ ] `description` enumeriert konkrete User-Trigger (keine abstrakten Fähigkeiten)
- [ ] Anweisungen sind auf Englisch
- [ ] Keine hartkodierten absoluten Pfade
- [ ] Unterstützende Assets liegen im Skill-Ordner
- [ ] `SKILL.md` < ~150 Zeilen (weiche Grenze)

Pass/Fail pro Punkt. Mechanische Probleme (Frontmatter-Mismatch, absolute Pfade, fehlende Hard-Rules) korrigiert der Skill auf Wunsch direkt.

### 3. Überarbeiten

Gezielte Edits an bestehenden Skills: `description` schärfen, Hard-Rules-Abschnitt ergänzen, zu lange Anweisungen kürzen. Nach jeder Revision läuft die Validierung erneut.

## Hard Rules

- Niemals an einem Nicht-Standard-Pfad scaffolden.
- Niemals vage `description` wie "hilft bei X".
- Niemals die Absicht des Nutzers raten — bei fehlenden Triggern nachfragen.
- Bei Konflikt zwischen Skill und Spec gewinnt die Spec; Skill-Update vorschlagen, nicht still divergieren.
- Niemals einen Skill halbfertig hinterlassen.

## Quellen

- Skill-Datei: `skills/skill-management/SKILL.md`
- Spezifikation: [`spec/claude/skill-management/`](../../specs/skill-management.md)
