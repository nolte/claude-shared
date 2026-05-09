# Spezifikationen

Die Spezifikationen unter `spec/` definieren die verbindlichen Regeln für Autoren von Skills und Agents. Sie sind **mehrsprachig**: Kanonisch auf Englisch, übersetzt nach Deutsch — strukturell und semantisch synchron gehalten durch den [Spec-Skill](../skills/spec.md).

## Vorhandene Specs

Die autoritative, vom [Spec-Skill](../skills/spec.md) gepflegte Liste liegt in [`spec/README.md`](https://github.com/nolte/claude-shared/blob/develop/spec/README.md) — dort stehen alle Specs mit Topic, Slug, Sprachtiteln, Status und letztem Update-Datum.

Grober Schnitt zur Orientierung:

- **`spec/claude/`** — Regeln für Autoren von Skills und Agents (u. a. `skill-management`, `agent-management`, `skill-vs-agent`, `skill-review`, `agent-review`, `skill-agent-catalog`, `permission-allowlist`, `review-plan`)
- **`spec/project/`** — Regeln für Projekt- und Release-Konventionen (u. a. `project-structure`, `github-issue-templates`, `pull-request-workflow`, `parallel-working-copies`, `branching-model`, `release-automation`, `release-artifact`, `release-skill-layer`, `release-notes-audience-analysis`, `quality-gate`, `dependency-audit`, `workflow-health`, `docs-freshness`, `mermaid-diagrams`, `readme-structure`, `prose-style`, `spec-drift-audit`, `spec-driven-development`, `spec-readiness`, `audience-identification`, `mission`, `roadmap`, `sprint`, `feature`, `continuous-improvement`)

Detailseiten in dieser Doku existieren aktuell für `skill-management` und `agent-management`; weitere werden nachgezogen.

## RFC-2119-Konventionen

Normative Aussagen nutzen RFC-2119-Keywords, in Übersetzungen mit der englischen Form glossiert:

- **MUST** → `MUSS [MUST]`
- **MUST NOT** → `DARF NICHT [MUST NOT]`
- **SHOULD** → `SOLLTE [SHOULD]`
- **SHOULD NOT** → `SOLLTE NICHT [SHOULD NOT]`
- **MAY** → `KANN [MAY]`

## Mitwirken an Specs

Neue Spec oder Änderung? Immer über den [Spec-Skill](../skills/spec.md) — so bleiben Kanon und Übersetzungen und der Index garantiert synchron. Direkte Edits an Übersetzungen sind der häufigste Drift-Verursacher und werden vom Skill beim nächsten Drift-Check gemeldet.
