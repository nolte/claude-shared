---
title: Glossar
audience: [external-contributor, maintainer]
content_mode: glossary
track: developer-docs
last_updated: 2026-06-06
---

# Glossar

Begriffe, die nur in `claude-shared` gelten. Allgemeine Prosa-Begriffe
gehören zum upstream `nolte/vale-style`-Vokabular (gemäß
`spec/project/prose-style/`); dieses Glossar erfasst nur das eigene
Delta.

- **ADR (Architecture Decision Record)**: ein kurzes Dokument, das eine
  architektonisch bedeutsame Entscheidung festhält — ihren Kontext, die
  getroffene Wahl und ihre Konsequenzen — versionskontrolliert abgelegt, damit
  die Begründung die Konversation überdauert, die sie hervorgebracht hat.
- **Agent**: ein fokussierter Claude-Code-Sub-Agent, definiert in
  `agents/<name>.md`, per `subagent_type` dispatchbar, mit eigener
  Tool-Allow-List und eigenem System-Prompt.
- **Catalog (Katalog)**: die automatisch generierten Skill-/Agent-Referenzseiten
  unter `docs/<lang>/skills/` und `docs/<lang>/agents/`, erzeugt vom
  skill-agent-catalog-Generator.
- **Dogfooding**: das eigene Plugin dieses Repos beim Entwickeln über
  `claude --plugin-dir .` gegen sich selbst betreiben.
- **Plugin-Marketplace**: der Auslieferungskanal, über den `nolte-shared` die
  Consumer-Projekte erreicht; der einzige Auslieferungsweg (kein Kopieren in
  `.claude/skills/`).
- **Portfolio**: die Menge der `nolte/*`-Repositories, die Konventionen teilen;
  dieses Repo ist ein Mitglied.
- **Primary checkout (Hauptordner)**: die reine Integrations-Arbeitskopie unter
  `~/repos/github/claude-shared/`, die auf `develop` bleiben MUSS.
- **Skill**: ein wiederverwendbarer Slash-Command, definiert in
  `skills/<name>/SKILL.md`, aufrufbar als `/nolte-shared:<skill>`.
- **Spec**: eine zweisprachige Spezifikation unter
  `spec/<area>/<topic>/<lang>.md`, mit einer EN-kanonischen Quelle und einer
  synchron gehaltenen DE-Übersetzung.
- **Track**: das `user-docs`/`developer-docs`-Audience-Track-Signal im
  Frontmatter jeder Docs-Seite (gemäß `spec/project/docs-audience-tracks/`).
- **Worktree**: eine dedizierte Git-Arbeitskopie, die von `develop` abzweigt und
  in der alle Feature-Arbeit passiert, abgelegt unter dem konfigurierbaren
  `NOLTE_WORKTREE_ROOT`.

## Quellen

- `spec/project/prose-style/` — das upstream `nolte/vale-style`-Vokabular als Baseline
- `CLAUDE.md` — Definitionen von Hauptordner, Worktree, Dogfooding
- `spec/project/docs-audience-tracks/` — Track-Definition
