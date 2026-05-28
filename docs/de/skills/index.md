---
title: Skills
audience: [maintainer]
content_mode: meta
track: developer-docs
last_updated: generated
---

# Skills

[**Nach Aufgabe stöbern →**](../by-task.md)

Auto-generierter Katalog aller Skills aus den konfigurierten Plugin-Source-Roots. Inhalt stammt direkt aus den `SKILL.md`-Frontmattern und -Bodies. Gruppiert nach Phase des Liefer-Lebenszyklus.

## 1 Vision

- [`mission-define`](nolte-shared/mission-define.md) — Verfasst die erste project/mission.md eines Projekts entlang des SMART-Walks und der vier Pflicht-Sektionen.
- [`mission-revise`](nolte-shared/mission-revise.md) — Überarbeitet eine bestehende project/mission.md: Statement, Audiences, Time-Bound oder mvp_status-Lifecycle-Flips.

## 2 Plan

- [`audience-identify`](nolte-shared/audience-identify.md) — Führt die Audience-Identifikation gegen einen abgegrenzten Kontext aus und erzeugt ein autoritatives Audience-Artefakt.
- [`feature-decompose`](nolte-shared/feature-decompose.md) — Zerlegt einen Roadmap-Eintrag in Feature-Dateien mit testbaren Akzeptanzkriterien und Test-Hooks.
- [`roadmap-init`](nolte-shared/roadmap-init.md) — Scaffoldet das Planungspaar project/goals.md und project/roadmap.md zum ersten Mal.
- [`roadmap-plan`](nolte-shared/roadmap-plan.md) — Fügt Roadmap-Items hinzu, retargetet sie und passt sie an in project/roadmap.md mit vollständiger Lifecycle-Validierung.
- [`roadmap-refine`](nolte-shared/roadmap-refine.md) — Erzwingt die Detail-Level-Invariante in project/roadmap.md (Items für aktuellen und nächsten Sprint müssen 'fine' sein).
- [`sprint-plan`](nolte-shared/sprint-plan.md) — Erstellt eine neue Sprint-Datei unter project/sprints/ mit Value-Statement, Features und value-verifizierendem Akzeptanzkriterium.

## 3 Design

- [`cookiecutter-template-manage`](nolte-shared/cookiecutter-template-manage.md) — Verwaltet den Cookiecutter-Template-Lebenszyklus: scaffolden, überarbeiten, Hooks absichern, pytest-cookies einrichten.
- [`docs-audience-tracks-apply`](nolte-shared/docs-audience-tracks-apply.md) — Verdrahtet Per-Page-Track-Frontmatter und Audience-zu-Track-Mapping in MkDocs docs/; Audit-, Migrate- oder Patch-Operationen.
- [`docs-dry-refactor`](nolte-shared/docs-dry-refactor.md) — Erkennt duplizierte MkDocs-Absätze und extrahiert sie in mkdocs-include-markdown-plugin-Snippets.
- [`github-issue-templates-apply`](nolte-shared/github-issue-templates-apply.md) — Scaffoldet spec-konforme GitHub-Issue-Forms (.github/ISSUE_TEMPLATE/), zugeschnitten auf Projekttyp und Audience.
- [`mermaid-diagrams-apply`](nolte-shared/mermaid-diagrams-apply.md) — Auditiert und verdrahtet das MkDocs-Mermaid-Setup; hilft beim Hinzufügen eines Mermaid-Diagramms mit verpflichtendem Source-Marker.
- [`mkdocs-structure-apply`](nolte-shared/mkdocs-structure-apply.md) — Auditiert und scaffoldet das portfolio-weite MkDocs-Skelett: Per-Sprache-docs/-Tree, Plugin-Baseline, Nav-Kontrakt, Per-Page-Frontmatter.
- [`permission-allowlist-maintain`](nolte-shared/permission-allowlist-maintain.md) — Kuratiert die eingecheckte .claude/settings.json permissions.allow-Liste gemäß Permission-Allowlist-Spec.
- [`project-structure-apply`](nolte-shared/project-structure-apply.md) — Auditiert ein Repository gegen die Project-Structure-Spec und scaffoldet fehlende Artefakte (README, .github/, Renovate, Taskfile, MkDocs, .claude/).
- [`readme-structure-apply`](nolte-shared/readme-structure-apply.md) — Auditiert, scaffoldet oder patcht README.md eines Repos gegen die Readme-Structure-Spec (sechs Pflicht-Sektionen, ≤200 Zeilen).
- [`skill-agent-catalog-apply`](nolte-shared/skill-agent-catalog-apply.md) — Verdrahtet den MkDocs-Skill-und-Agent-Katalog (gen-files + literate-nav, Generator-Hook, Source-Roots) in einem Plugin- oder Konsumenten-Repo.
- [`skill-management`](nolte-shared/skill-management.md) — Scaffoldet oder überarbeitet einen nolte-shared Claude-Code-Skill-Ordner.
- [`spec`](nolte-shared/spec.md) — Verfasst, übersetzt, indiziert und prüft mehrsprachige Spezifikationen unter spec/.
- [`tech-stack-capture`](nolte-shared/tech-stack-capture.md) — Erfasst oder aktualisiert den tech_stack-Block in project/portfolio.yml durch Sondieren von Lockfiles, Taskfile, CI und Tooling-Configs.
- [`webview-ui-optimize`](nolte-shared/webview-ui-optimize.md) — Auditiert und patcht ein Browser-gerendertes Frontend über Performance, Security, Barrierefreiheit (WCAG 2.2 AA), i18n und UX.
- [`yaml-json-schema`](nolte-shared/yaml-json-schema.md) — Verfasst, auditiert, refaktoriert und validiert YAML-codierte JSON-Schema-2020-12-Dokumente.

## 4 Build

- [`blog-author`](nolte-shared/blog-author.md) — Verfasst ein zweisprachiges Blog-Post-Paar (EN-canonical + DE-übersetzt) nach den blog-author-Specs dieses Plugins und schreibt es in ein Konsumenten-Blog-Repo.
- [`sprint-execute`](nolte-shared/sprint-execute.md) — Treibt das Tagesgeschäft eines aktiven Sprints: Lifecycle-Übergänge, Feature-Listen-Sync, last_commit-Updates.

## 5 Review

- [`agent-review`](nolte-shared/agent-review.md) — Prüft einen Claude-Code-Agent gegen die Spec und erzeugt einen umsetzbaren Review-Plan unter .audits/agent-review/.
- [`continuous-improvement-triage`](nolte-shared/continuous-improvement-triage.md) — Triagiert Portfolio-Audit-Findings und dispatched die Behebung an den passendsten spezialisierten Agent oder Skill.
- [`portfolio-inflight-triage`](nolte-shared/portfolio-inflight-triage.md) — Führt den nur-Lese periodischen In-Flight-Audit über nolte/* aus (offene PRs, Branches, Issues, Review-Threads) mit Severity-Klassifikation.
- [`pull-request-create`](nolte-shared/pull-request-create.md) — Öffnet einen spec-konformen Draft-GitHub-Pull-Request auf dem aktuellen Feature-Branch.
- [`pull-request-merge`](nolte-shared/pull-request-merge.md) — Befördert einen Draft-PR auf develop und durchläuft jeden Pull-Request-Workflow-Gate.
- [`skill-review`](nolte-shared/skill-review.md) — Prüft einen Claude-Code-Skill gegen die Spec und erzeugt einen umsetzbaren Review-Plan unter .audits/skill-review/.
- [`skills-agents-sweep`](nolte-shared/skills-agents-sweep.md) — Orchestriert ein portfolio-weites Sweep-Audit aller Skills und Agents mit übergreifenden Findings und einer Wave-basierten Roadmap.
- [`spec-drift-audit`](nolte-shared/spec-drift-audit.md) — Auditiert jede Spec gegen die Repo-Implementierung und erzeugt ein traceable Spec-Drift-Audit-Artefakt.

## 6 Quality

- [`dependency-audit`](nolte-shared/dependency-audit.md) — Scannt den Dependency-Baum des Projekts nach bekannten CVEs und optional Lizenz-Compliance-Issues; Severity-sortierter Report.
- [`lektorat-apply`](nolte-shared/lektorat-apply.md) — Prüft bestehende Markdown-Prosa gegen fünf Lektorats-Dimensionen (Lesbarkeit, Verständlichkeit, Grammatik, Stil, Audience-Fit).
- [`portfolio-audit`](nolte-shared/portfolio-audit.md) — Auditiert, rendert und bootstrappt das cross-repo Capability-Portfolio über nolte/*.
- [`quality-gate`](nolte-shared/quality-gate.md) — Führt das Lint-+-Typecheck-+-Test-Gate des Projekts parallel aus und tabelliert, welche Checks gescheitert sind.
- [`vocab-drift-audit`](nolte-shared/vocab-drift-audit.md) — Auditiert lokale Vale-Vokabularien gegen den gepinnten Upstream-Release nolte/vale-style auf Drift.
- [`workflow-health-triage`](nolte-shared/workflow-health-triage.md) — Triagiert einen roten GitHub-Actions-Workflow auf develop/main und dispatched den passendsten spezialisierten Agent zur Behebung.

## 7 Close & Release

- [`release-notes-curate`](nolte-shared/release-notes-curate.md) — Reichert den offenen release-drafter-Draft auf develop mit projektkontext-bewussten Sektionen via gh release edit an.
- [`release-publish-trigger`](nolte-shared/release-publish-trigger.md) — Prüft jeden Pre-Publish-Gate lokal und dispatched dann release-publish.yml für den offenen Release-Drafter-Draft auf develop.
- [`sprint-review`](nolte-shared/sprint-review.md) — Schließt einen aktiven Sprint gemäß Sprint-Spec: validiert das Deploy-Artefakt und protokolliert den Value-Delivery-Audit-Trail.
