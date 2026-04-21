# Spezifikationen

Die Spezifikationen unter `spec/` definieren die verbindlichen Regeln für Autoren von Skills und Agents. Sie sind **mehrsprachig**: Kanonisch auf Englisch, übersetzt nach Deutsch — strukturell und semantisch synchron gehalten durch den [Spec-Skill](../skills/spec.md).

## Vorhandene Specs

| Topic | Slug | Titel (DE) | Titel (EN) | Status |
|-------|------|-----------|-----------|--------|
| claude | [agent-management](agent-management.md) | Claude-Agent-Autorenschaft | Claude Agent Authoring | draft |
| claude | [skill-management](skill-management.md) | Claude-Skill-Autorenschaft | Claude Skill Authoring | draft |

Der aktuelle Stand des Indexes wird von `spec/README.md` geführt und durch den Spec-Skill aktualisiert.

## RFC-2119-Konventionen

Normative Aussagen nutzen RFC-2119-Keywords, in Übersetzungen mit der englischen Form glossiert:

- **MUST** → `MUSS [MUST]`
- **MUST NOT** → `DARF NICHT [MUST NOT]`
- **SHOULD** → `SOLLTE [SHOULD]`
- **SHOULD NOT** → `SOLLTE NICHT [SHOULD NOT]`
- **MAY** → `KANN [MAY]`

## Mitwirken an Specs

Neue Spec oder Änderung? Immer über den [Spec-Skill](../skills/spec.md) — so bleiben Kanon und Übersetzungen und der Index garantiert synchron. Direkte Edits an Übersetzungen sind der häufigste Drift-Verursacher und werden vom Skill beim nächsten Drift-Check gemeldet.
