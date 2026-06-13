---
title: Architekturüberblick
audience: [external-contributor, maintainer]
content_mode: explanation
track: developer-docs
last_updated: 2026-06-06
---

# Architekturüberblick

Ein Kurzüberblick, wie `claude-shared` aufgebaut ist — für
Neueinsteiger, die sich im Code zurechtfinden müssen.

## Kontext: was drinnen, was draußen ist

`claude-shared` ist ein einzelnes Claude-Code-Plugin (`nolte-shared`) plus das
Tooling, das es erstellt, validiert und veröffentlicht. Es ist ein
Dokumentations- und Automatisierungsprojekt — es gibt keinen Laufzeitdienst.

- **Drinnen**: die Skills, Agents und Specs des Plugins; die MkDocs-Site; die
  Taskfile-gesteuerte Automatisierung; die Planungssuite unter `project/`.
- **Draußen**: Claude Code selbst (das Plugin baut darauf auf, besitzt es aber
  nicht), die Downstream-Projekte, die das Plugin installieren, und die
  Schwester-Portfolio-Repos (`nolte/gh-plumbing`, `nolte/vale-style`,
  `nolte/taskfiles`), die dieses Repo als Abhängigkeiten konsumiert.

## Bausteine

- **Skills** (`skills/<name>/SKILL.md`): wiederverwendbare Slash-Commands. Jeder
  Ordner ist ein Skill; die Auslieferung erfolgt über den Plugin-Marketplace,
  niemals durch Kopieren in das `.claude/skills/` eines Consumers.
- **Agents** (`agents/<name>.md`): fokussierte Sub-Agents mit einer
  Tool-Allow-List und einem System-Prompt.
- **Specs** (`spec/`): die EN-kanonischen, DE-übersetzten Konventionen, die
  regeln, wie Skills, Agents, Docs und das Projekt selbst erstellt werden.
- **Docs** (`docs/<lang>/`): die zweisprachige MkDocs-Site inklusive des
  automatisch generierten Skill-/Agent-Katalogs.
- **Automatisierung** (`Taskfile.yml`, `scripts/`): das Quality-Gate, die
  Katalog-Generierung, die Validierung und der Dogfooding-Einstiegspunkt.

## Tragende Entscheidungen

Die nicht-trivialen Trade-offs sind als Konventionen in `spec/` und in
`CLAUDE.md` festgehalten, nicht als eigenständige ADRs (das Repo führt noch
keinen `docs/<lang>/adrs/`-Baum):

- **Auslieferung nur über das Plugin** — Skills werden nie in Consumer kopiert;
  der Marketplace ist der einzige Auslieferungsweg.
- **EN-kanonische Specs, zweisprachige Docs** — eine Quelle der Wahrheit pro
  Spec, strikt übersetzungssynchron gehalten.
- **Hauptordner-auf-`develop`-Regel** — alle Feature-Arbeit passiert in
  Worktrees; der Hauptordner ist eine reine Integrations-Startrampe (siehe
  `CLAUDE.md` §Parallel working copies und
  `spec/project/parallel-working-copies/`).

## Quellen

- `CLAUDE.md` — Repository-Orientierung und die tragenden Konventionen
- `spec/project/parallel-working-copies/` — die Worktree-Entscheidung
- [Projektstruktur](project-structure.md) — die On-Disk-Baustein-Karte
