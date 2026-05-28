---
title: Nutzung
audience: [maintainer, downstream-user]
content_mode: how-to
track: developer-docs
last_updated: 2026-05-19
---

# Nutzung

Sobald das Plugin geladen ist, stehen seine Skills als Slash-Commands im Claude-Code-Prompt bereit. Diese Seite klärt die wichtigsten Aufrufmuster und den Namespace.

## Skills aufrufen

Skills des Plugins sind per Name aufrufbar — optional mit Plugin-Prefix:

```
/nolte-shared:spec
/nolte-shared:skill-management
```

Claude Code zeigt sie außerdem unter `/skills` an. Von dort lassen sie sich mit Tab auswählen.

## Welcher Skill für was

| Skill | Zweck | Typische Trigger |
|-------|-------|-----------------|
| [`skill-management`](../skills/nolte-shared/skill-management.md) | Neue Skills anlegen, bestehende gegen die Spec validieren | "neuen Skill anlegen", "Skill für X erstellen", "validate this skill" |
| [`spec`](../skills/nolte-shared/spec.md) | Mehrsprachige Spezifikationen schreiben, übersetzen, indizieren, auf Drift prüfen | "schreib eine Spec für X", "ist X schon abgedeckt?", "Index neu bauen" |

## Antwortsprache

Die Skill-Dateien selbst sind konsequent auf Englisch gehalten (Token-Effizienz). Claude erkennt aber die Sprache der Nutzereingabe und antwortet in dieser Sprache — Deutsch fragen ergibt Deutsch als Antwort.

## Namespace-Kollisionen

Trägt ein Projekt eigene Skills mit gleichem Namen, bleibt die Plugin-Version erreichbar. Zur Auflösung einer Mehrdeutigkeit immer die namespaced Form `/nolte-shared:<skill>` nutzen.

## Nächste Schritte

- [Skill-Management](../skills/nolte-shared/skill-management.md) im Detail
- [Spec-Skill](../skills/nolte-shared/spec.md) im Detail
- [Spezifikationen](../references/specs/index.md) — verbindliche Autoren-Regeln
