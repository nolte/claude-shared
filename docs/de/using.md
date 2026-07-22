---
title: nolte-shared nutzen
audience: [downstream-user, downstream-end-user]
content_mode: explanation
track: user-docs
last_updated: 2026-05-30
---

# nolte-shared nutzen

Diese Seite richtet sich an **Downstream-Claude-Code-Nutzer**, die das Plugin
`nolte-shared` in ihren eigenen Projekten einsetzen wollen. Wer stattdessen am
Plugin selbst *entwickeln* möchte, beginnt bei der
[Entwickler-Dokumentation](getting-started/index.md).

## Warum nolte-shared

Software-Teams wollen meist eine konsistente Claude-Code-Basis über alle
Repositories hinweg: dieselben Review-Gewohnheiten, dieselben Coding-Richtlinien,
dieselben Helfer-Agents. Diese Basis in jedem Repository neu zu bauen, führt zu
Drift und doppeltem Aufwand. `nolte-shared` bündelt die Basis einmal — wiederverwendbare **Skills** (Slash-Commands und Workflows) und **Agents** (fokussierte
Sub-Agents) plus geteilte **Konventionen** — sodass jedes Projekt, das das Plugin
installiert, dieselben spec-konformen Workflows erhält, ohne sie neu zu
implementieren.

## Für wen ist das gedacht?

- **Downstream-Claude-Code-Nutzer** (`downstream-user`): Entwickler, die die
  Slash-Commands des Plugins (zum Beispiel `/nolte-shared:spec`,
  `/nolte-claude-dev:skill-management`, `/nolte-shared:pull-request-create`) und
  dessen Sub-Agents in ihren eigenen Portfolio-Projekten aufrufen. Du bekommst
  stabile Command-Namen, reproduzierbare Outputs und konsistente Review- und
  Release-Disziplin.
- **Endnutzer von Downstream-Projekten** (`downstream-end-user`): Du rufst das
  Plugin nie direkt auf; du siehst nur das Downstream-Produkt. Das Plugin prägt
  dessen Code-Qualität und Release-Disziplin indirekt, übernimmt aber keine
  Verantwortung für Endnutzer-Ergebnisse.

Die Audience-Identifier verweisen auf das Audience-Artefakt des Projekts,
[`AUDIENCES.md`](https://github.com/nolte/claude-shared/blob/develop/AUDIENCES.md).

## Was du damit machen kannst

Das Plugin ist für diese Szenarien ausgelegt:

- Einen einheitlichen **Pull-Request-Workflow**
  (`/nolte-shared:pull-request-create`, `/nolte-shared:pull-request-merge`) über
  Repositories hinweg anwenden.
- Ein konsistentes **Quality-Gate** und einen **Dependency-Audit** vor Commit
  oder Release laufen lassen (`/nolte-engineering:quality-gate`,
  `/nolte-engineering:dependency-audit`).
- **Skills, Agents und Specs** gegen geteilte Autorenschafts-Regeln verfassen und
  reviewen (`/nolte-claude-dev:skill-management`, `/nolte-shared:spec` sowie die
  Review-Skills).
- **Projektstruktur, Dokumentation und Release-Automation** an der
  Portfolio-Basis ausgerichtet halten.

Ausdrücklich **außerhalb des Scopes**: `nolte-shared` ist Tooling, kein Managed
Service. Es liefert kein SLA (Service-Level-Agreement), keine Garantie auf seine beratenden Outputs (ein
sauberer Report ist keine Zusicherung, dass eine Änderung sicher auslieferbar
ist) und keinen Support-Vertrag. Release-, Code- und Security-Verantwortung
bleiben bei deinem Projekt.

## In deinem Projekt installieren

Füge dieses Repository als Plugin-Marketplace hinzu und installiere dann das
Plugin `nolte-shared` aus Claude Code heraus:

```bash
/plugin marketplace add nolte/claude-shared
/plugin install nolte-shared@nolte-shared
```

Nach der Installation ist jeder Skill als `/nolte-shared:<name>` aufrufbar (zum
Beispiel `/nolte-shared:spec`); Agents werden von Skills dispatcht oder direkt
über das `Task`-Tool, wenn du weißt, welchen Agent du willst. Du brauchst keinen
Clone dieses Repositories und keine lokale Toolchain, um das Plugin zu nutzen —
die Installation passiert vollständig in deiner eigenen Claude-Code-Umgebung.
