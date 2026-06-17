---
title: Agents
audience: [maintainer]
content_mode: meta
track: developer-docs
last_updated: generated
---

# Agents

[**Nach Aufgabe stöbern →**](../by-task.md)

Auto-generierter Katalog aller Agents aus den konfigurierten Plugin-Source-Roots. Inhalt stammt direkt aus den Agent-Markdown-Dateien. Gruppiert nach Phase des Liefer-Lebenszyklus.

## 2 Plan

### nolte-shared

- [`audience-review`](nolte-shared/audience-review.md) — Prüft ein vorhandenes Audience-Analyse-Artefakt gegen die Spec; nur-Lese strukturierter Findings-Report.
- [`feature-consistency-reviewer`](nolte-shared/feature-consistency-reviewer.md) — Prüft eine Draft-Feature-Datei auf Überlappung, Duplikate und Vorarbeit gegen Features, Source-Code und das Spec-Corpus.
- [`roadmap-coherence-reviewer`](nolte-shared/roadmap-coherence-reviewer.md) — Nur-Lese-Roadmap-Kohärenz-Audit gegen Goals, Mission, Sprints und Features; strukturierte Findings-Liste.
- [`security-requirements-reviewer`](nolte-shared/security-requirements-reviewer.md) — Read-only Security-Architektur-Review eines Anforderungs-/Spec-Sets auf Security- und Datenschutz-Vollständigkeit: Findings, Datensparsamkeits- und Autorisierungs-Matrix, DSGVO-Rechte-Checkliste.
- [`sprint-readiness-reviewer`](nolte-shared/sprint-readiness-reviewer.md) — Nur-Lese-Sprint-Readiness-Gate: Go/No-Go-Report zu einem Sprint, bevor sprint-execute ihn planned → active befördert.
- [`tech-stack-fitness-reviewer`](nolte-shared/tech-stack-fitness-reviewer.md) — Read-only Architektur-Review der Stack-Eignung gegen Anforderungen: Abdeckungsmatrix, Lücken, Über-/Unterarchitektur, Risiken, priorisierte Empfehlungen.

## 3 Design

### nolte-engineering

- [`test-case-extractor`](nolte-engineering/test-case-extractor.md) — Leitet strukturierte, framework-agnostische, rückverfolgbare Testfälle aus einem Anforderungsdokument ab, aus der Perspektive nutzer-beobachtbaren Verhaltens.
- [`webview-ui-expert`](nolte-engineering/webview-ui-expert.md) — Nur-Lese-Cross-File-Deep-Review eines benannten Frontend-Ziels über Performance, Security, Barrierefreiheit, i18n, UX.

### nolte-media

- [`graphic-prompt-generator`](nolte-media/graphic-prompt-generator.md) — Verfasst brand-konforme, generatorfertige KI-Bild-Prompts als dauerhafte Markdown-Dokumente aus einem kurzen Grafik-Briefing.

### nolte-shared

- [`audience-doc-author`](nolte-shared/audience-doc-author.md) — Verfasst oder überarbeitet audience-zugeschnittene Doku (README, Release-Notes, MkDocs-Seiten) gegen ein vorhandenes Audience-Artefakt.
- [`claude-plugin-developer`](nolte-shared/claude-plugin-developer.md) — Verfasst spec-konforme Claude-Code-Plugin-Artefakte (Skill oder Agent) für nolte-shared; Executor im Skill-orchestriert-Agent-Pattern.
- [`spec-readiness-reviewer`](nolte-shared/spec-readiness-reviewer.md) — Nur-Lese-Audit einer Spec auf Widersprüche, Audience-Fit und AC-Coverage.

## 4 Build

### nolte-engineering

- [`component-test-generator`](nolte-engineering/component-test-generator.md) — Erzeugt spec-konforme Component-Tests in der passenden Ausprägung (Frontend render-and-query oder Service-über-eigene-API mit gedoubelten Externen), mit Determinismus und TC-IDs.
- [`contract-test-generator`](nolte-engineering/contract-test-generator.md) — Erzeugt spec-konforme Contract-Tests (consumer-driven als Vorgabe: Consumer-Erwartungen + Provider-Verifikation, Broker, can-i-deploy), die nur Agreement-Kompatibilität prüfen.
- [`e2e-test-generator`](nolte-engineering/e2e-test-generator.md) — Erzeugt das Grundgerüst einer spec-konformen E2E-Suite (Page Objects, Waits, Screenshots, Marker, Protokoll) für ein Feature, mit dem Selenium-+-pytest-Referenzprofil als Vorgabe.
- [`frontend-usability-optimizer`](nolte-engineering/frontend-usability-optimizer.md) — Senior-UX-Engineer, der die Usability bestehenden Frontend-Codes direkt verbessert — gegen den selbst erkannten Stack und die dokumentierten UI-Konventionen des Projekts.
- [`fullstack-developer`](nolte-engineering/fullstack-developer.md) — Senior-Full-Stack-Entwickler, der eine scharf umrissene Anforderung als produktionsreifen Code gegen den selbst erkannten Stack, das Layout und die Qualitätsmesslatte des Projekts umsetzt.
- [`integration-test-generator`](nolte-engineering/integration-test-generator.md) — Erzeugt spec-konforme schmale Integrationstests (ein echter ephemerer Kollaborateur, der Rest gedoubelt, seam-only-Assertions, Per-Test-Isolation, Readiness-Waits, TC-IDs).
- [`test-code-adapter`](nolte-engineering/test-code-adapter.md) — Verwandelt einen bestätigt-roten Fall in die minimale korrekte Produktions-Code-Änderung unter der No-Cheating-Invariante (einfachste-Änderung-dann-Refactor, Wurzelursache, Verify per Re-Execution).
- [`unit-test-generator`](nolte-engineering/unit-test-generator.md) — Erzeugt spec-konforme Unit-Tests (FIRST, AAA, beobachtbares-Verhalten-Assertions, disziplinierte Doubles, TC-IDs) für ein Modul, mit pytest-Referenzprofil als Vorgabe.

## 5 Review

### nolte-engineering

- [`code-security-reviewer`](nolte-engineering/code-security-reviewer.md) — Read-only Whole-Codebase-OWASP-Audit, das Befunde über Dateien hinweg zu einem nach Schweregrad klassifizierten Report korreliert.
- [`component-test-reviewer`](nolte-engineering/component-test-reviewer.md) — Prüft bestehende Component-Tests (Frontend oder Service) gegen die Component-Stufen-Spec, liefert ein checklistenbasiertes Konformitätsurteil und wendet nur minimale, gezielte Korrekturen an.
- [`contract-test-reviewer`](nolte-engineering/contract-test-reviewer.md) — Prüft bestehende Contract-Tests gegen die Contract-Stufen-Spec, liefert ein checklistenbasiertes Konformitätsurteil und wendet nur minimale, gezielte Korrekturen an.
- [`dependency-audit-scanner`](nolte-engineering/dependency-audit-scanner.md) — Nur-Lese-CVE-Scanner pro Projekttyp (pip-audit, npm audit, govulncheck, cargo audit); liefert strukturiertes Drift-Inventar.
- [`e2e-result-reviewer`](nolte-engineering/e2e-result-reviewer.md) — Prüft Screenshots und Protokoll eines E2E-Laufs visuell gegen die Anforderungs-/UI-Specs und liefert priorisierte, rein lesende Befunde.
- [`e2e-test-reviewer`](nolte-engineering/e2e-test-reviewer.md) — Prüft eine bestehende E2E-Suite gegen die Spec, liefert ein checklistenbasiertes Konformitätsurteil und wendet nur minimale, gezielte Korrekturen an.
- [`integration-test-reviewer`](nolte-engineering/integration-test-reviewer.md) — Prüft bestehende Integrationstests gegen die Integration-Stufen-Spec, liefert ein checklistenbasiertes Konformitätsurteil und wendet nur minimale, gezielte Korrekturen an.
- [`license-check-scanner`](nolte-engineering/license-check-scanner.md) — Nur-Lese-Lizenz-Inventar-Scanner: SBOM mit aufgelösten Lizenzen, SPDX-Identifikation und Kategorie-Klassifizierung pro Stack.
- [`test-result-analyzer`](nolte-engineering/test-result-analyzer.md) — Klassifiziert die rohen Ergebnisse eines Testlaufs in geroutete Kategorien (Defekt/Flake/Test-Bug/Infra/…) mit Evidenz gemäß der Ergebnis-Analyse-Spec, damit der Zyklus die nächste Phase kennt.
- [`unit-test-reviewer`](nolte-engineering/unit-test-reviewer.md) — Prüft bestehende Unit-Tests gegen die Unit-Stufen-Spec, liefert ein checklistenbasiertes Konformitätsurteil und wendet nur minimale, gezielte Korrekturen an.

### nolte-shared

- [`diagram-opportunity-reviewer`](nolte-shared/diagram-opportunity-reviewer.md) — Nur-Lese-Prosa-Scanner, der Markdown-Passagen markiert, die als Mermaid-Diagramm besser ausgedrückt wären.
- [`gdpr-data-protection-reviewer`](nolte-shared/gdpr-data-protection-reviewer.md) — Read-only repository-weites DSGVO-Datenschutzaudit; trennt code-verifizierbare Befunde von rechtsprüfungs-erforderlichen.
- [`lektorat-scanner`](nolte-shared/lektorat-scanner.md) — Nur-Lese-Lektorats-Scanner über die sechs Dimensionen (D1 Lesbarkeit, D2 Verständlichkeit, D3 Grammatik, D4 Stil, D5 Audience-Fit, D6 Idiomatik).
- [`portfolio-inflight-collector`](nolte-shared/portfolio-inflight-collector.md) — Nur-Lese-In-Flight-Datensammler: offene Issues, PRs (inkl. Drafts), Branches ohne PR, ungelöste Review-Threads + Discussions über nolte/*.
- [`portfolio-manifest-collector`](nolte-shared/portfolio-manifest-collector.md) — Nur-Lese-Inventar-Sammler: erfasst per-Repo project/portfolio.yml-Manifeste über nolte/*.
- [`vocab-drift-scanner`](nolte-shared/vocab-drift-scanner.md) — Nur-Lese-Diff der lokalen Vale-Vocab-Dateien gegen den gepinnten Upstream-Release nolte/vale-style.

## 6 Quality

### nolte-engineering

- [`i18n-completeness-checker`](nolte-engineering/i18n-completeness-checker.md) — Read-only-Vollständigkeits-Audit der Übersetzungsdateien gegeneinander und gegen die Code-Verwendung als nach Schweregrad sortierter Report.

### nolte-shared

- [`docs-freshness-checker`](nolte-shared/docs-freshness-checker.md) — Nur-Lese-Frische-Audit der MkDocs-Doku: Sprach-Parität, tote Links, veraltete spec-/code-Refs, ADR-Hygiene, Mermaid-Derived-Source-Drift.
- [`link-rot-scanner`](nolte-shared/link-rot-scanner.md) — Nur-Lese-Link-Rot-Audit: interne, Anker-, Cross-Tree- und externe Links über scripts/check_links.py, triagiert in einen schweregrad-sortierten Report.
- [`mermaid-diagram-reviewer`](nolte-shared/mermaid-diagram-reviewer.md) — Statisches Audit jedes Mermaid-Blocks in docs/<lang>/ gegen die Spec plus MkDocs-Setup; strukturierte Findings, kein Rendering.
- [`project-structure-reviewer`](nolte-shared/project-structure-reviewer.md) — Nur-Lese-Audit des Repo-Layouts gegen die Project-Structure-Spec; Severity-sortierte Findings nur auf Disk-Basis.
- [`prose-vale-curator`](nolte-shared/prose-vale-curator.md) — Kuratiert Prosa, damit Vale grün ist, bevorzugt mitgelieferte Vokabularien, erweitert accept.txt nur in Vokabular-eigenden Repos.
- [`quality-gate-enforcer`](nolte-shared/quality-gate-enforcer.md) — Prüft die Quality-Gate-Verdrahtung (Taskfile, pre-commit, CI-Workflow, Timeouts) auf Spec-Konformität; führt das Gate nie aus.
- [`tech-stack-drift-reviewer`](nolte-shared/tech-stack-drift-reviewer.md) — Nur-Lese-Tech-Stack-Drift-Audit: diffed deklariertes Manifest gegen On-Disk-Repo-Signale (Lockfiles, Configs, Workflows).

## 8 Cross-cutting

### nolte-media

- [`png-to-transparent-svg`](nolte-media/png-to-transparent-svg.md) — Konvertiert ein PNG mit Fake-Transparency-Hintergrund (Checkerboard oder Einfarbig) in ein sauberes SVG mit echtem Alpha.

### nolte-shared

- [`cookiecutter-template-author`](nolte-shared/cookiecutter-template-author.md) — Scaffoldet oder überarbeitet Cookiecutter-Templates, härtet Hooks ab, richtet pytest-cookies-Harness + GitHub-Actions-Matrix ein.
