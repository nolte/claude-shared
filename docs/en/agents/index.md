---
title: Agents
audience: [maintainer]
content_mode: meta
track: developer-docs
last_updated: generated
---

# Agents

[**Browse by task →**](../by-task.md)

Auto-generated catalog of every agent discovered across the configured plugin source roots. Content is taken verbatim from each agent markdown file. Grouped by delivery-lifecycle phase.

## 2 Plan

- [`audience-review`](nolte-shared/audience-review.md) — Reviews an existing audience-analysis artifact against the spec; read-only structured findings report.
- [`feature-consistency-reviewer`](nolte-shared/feature-consistency-reviewer.md) — Reviews a draft feature file for overlap, duplication, and prior art against features, source code, and the spec corpus.
- [`roadmap-coherence-reviewer`](nolte-shared/roadmap-coherence-reviewer.md) — Read-only roadmap-coherence audit against goals, mission, sprints, and features; structured findings list.
- [`security-requirements-reviewer`](nolte-shared/security-requirements-reviewer.md) — Read-only security architect's review of a requirement/spec set for security & privacy completeness: findings, data-minimization & authorization matrices, GDPR rights checklist.
- [`sprint-readiness-reviewer`](nolte-shared/sprint-readiness-reviewer.md) — Read-only sprint-readiness gate: go/no-go report on a sprint before sprint-execute promotes it planned → active.
- [`tech-stack-fitness-reviewer`](nolte-shared/tech-stack-fitness-reviewer.md) — Read-only architect's review of a stack's fitness against requirements: coverage matrix, gaps, over-/under-engineering, risks, prioritized recommendations.

## 3 Design

- [`audience-doc-author`](nolte-shared/audience-doc-author.md) — Drafts or refines audience-tailored documentation (README, release notes, MkDocs pages) against an existing audience artifact.
- [`claude-plugin-developer`](nolte-shared/claude-plugin-developer.md) — Drafts spec-conformant Claude Code plugin artifacts (skill or agent) for nolte-shared, executor in the skill-orchestrates-agent pattern.
- [`graphic-prompt-generator`](nolte-shared/graphic-prompt-generator.md) — Authors brand-conformant, generator-ready AI image prompts as durable Markdown documents from a short graphic brief.
- [`spec-readiness-reviewer`](nolte-shared/spec-readiness-reviewer.md) — Read-only audit of a spec for contradictions, audience fit, and AC coverage.
- [`test-case-extractor`](nolte-shared/test-case-extractor.md) — Derives structured, framework-agnostic, traceable test cases from a requirement document, written from the user-observable-behaviour perspective.
- [`webview-ui-expert`](nolte-shared/webview-ui-expert.md) — Read-only deep cross-file review of one named frontend target across Performance, Security, A11y, i18n, UX.

## 4 Build

- [`component-test-generator`](nolte-shared/component-test-generator.md) — Scaffolds spec-conformant component tests in the right flavour (frontend render-and-query, or service-through-its-API with externals doubled), with determinism and TC-IDs.
- [`contract-test-generator`](nolte-shared/contract-test-generator.md) — Scaffolds spec-conformant contract tests (consumer-driven by default: consumer expectations + provider verification, broker, can-i-deploy), asserting agreement compatibility only.
- [`e2e-test-generator`](nolte-shared/e2e-test-generator.md) — Scaffolds a spec-conformant E2E suite (page objects, waits, screenshots, markers, protocol) for a feature, defaulting to the Selenium + pytest reference profile.
- [`frontend-usability-optimizer`](nolte-shared/frontend-usability-optimizer.md) — Senior UX engineer that improves the usability of existing frontend code in place against the project's own detected stack and documented UI conventions.
- [`fullstack-developer`](nolte-shared/fullstack-developer.md) — Senior full-stack engineer that implements a scoped requirement as production-ready code against the project's own detected stack, layout, and quality bar.
- [`integration-test-generator`](nolte-shared/integration-test-generator.md) — Scaffolds spec-conformant narrow integration tests (one real ephemeral collaborator, the rest doubled, seam-only assertions, per-test isolation, readiness waits, TC-IDs).
- [`unit-test-generator`](nolte-shared/unit-test-generator.md) — Scaffolds spec-conformant unit tests (FIRST, AAA, observable-behaviour assertions, disciplined doubles, TC-IDs) for a module, defaulting to a pytest reference profile.

## 5 Review

- [`code-security-reviewer`](nolte-shared/code-security-reviewer.md) — Read-only whole-codebase OWASP audit correlating findings across files into a severity-classified report.
- [`component-test-reviewer`](nolte-shared/component-test-reviewer.md) — Reviews existing component tests (frontend or service) against the component-tier spec, returns a checklist-based conformance verdict, and applies only minimal surgical fixes.
- [`contract-test-reviewer`](nolte-shared/contract-test-reviewer.md) — Reviews existing contract tests against the contract-tier spec, returns a checklist-based conformance verdict, and applies only minimal surgical fixes.
- [`dependency-audit-scanner`](nolte-shared/dependency-audit-scanner.md) — Read-only CVE scanner per project type (pip-audit, npm audit, govulncheck, cargo audit); returns structured drift inventory.
- [`diagram-opportunity-reviewer`](nolte-shared/diagram-opportunity-reviewer.md) — Read-only prose scanner that flags Markdown passages which would be expressed better as a Mermaid diagram.
- [`e2e-result-reviewer`](nolte-shared/e2e-result-reviewer.md) — Reviews an E2E run's screenshots and protocol visually against the requirement/UI specs and returns prioritised, read-only findings.
- [`e2e-test-reviewer`](nolte-shared/e2e-test-reviewer.md) — Reviews an existing E2E suite against the spec, returns a checklist-based conformance verdict, and applies only minimal surgical fixes.
- [`gdpr-data-protection-reviewer`](nolte-shared/gdpr-data-protection-reviewer.md) — Read-only whole-repository GDPR data-protection audit; separates code-verifiable findings from legal-review-required ones.
- [`integration-test-reviewer`](nolte-shared/integration-test-reviewer.md) — Reviews existing integration tests against the integration-tier spec, returns a checklist-based conformance verdict, and applies only minimal surgical fixes.
- [`lektorat-scanner`](nolte-shared/lektorat-scanner.md) — Read-only editorial scanner across the six lektorat dimensions (D1 readability, D2 comprehensibility, D3 grammar, D4 style, D5 audience-fit, D6 idiomatic naturalness).
- [`license-check-scanner`](nolte-shared/license-check-scanner.md) — Read-only license-inventory scanner: SBOM with resolved licenses, SPDX identification, and category classification per stack.
- [`portfolio-inflight-collector`](nolte-shared/portfolio-inflight-collector.md) — Read-only in-flight data collector: open issues, PRs (incl. drafts), branches without PR, unresolved review threads + Discussions across nolte/*.
- [`portfolio-manifest-collector`](nolte-shared/portfolio-manifest-collector.md) — Read-only inventory collector: gathers per-repo project/portfolio.yml manifests across nolte/*.
- [`unit-test-reviewer`](nolte-shared/unit-test-reviewer.md) — Reviews existing unit tests against the unit-tier spec, returns a checklist-based conformance verdict, and applies only minimal surgical fixes.
- [`vocab-drift-scanner`](nolte-shared/vocab-drift-scanner.md) — Read-only diff of repository-local Vale vocab files against the pinned upstream nolte/vale-style release.

## 6 Quality

- [`docs-freshness-checker`](nolte-shared/docs-freshness-checker.md) — Read-only freshness audit of MkDocs docs: language parity, dead links, stale spec/code refs, ADR hygiene, Mermaid derived-source drift.
- [`i18n-completeness-checker`](nolte-shared/i18n-completeness-checker.md) — Read-only completeness audit of translation files against each other and against code usage, as a severity-sorted report.
- [`link-rot-scanner`](nolte-shared/link-rot-scanner.md) — Read-only link-rot audit: internal, anchor, cross-tree, and external links via scripts/check_links.py, triaged into a severity-sorted report.
- [`mermaid-diagram-reviewer`](nolte-shared/mermaid-diagram-reviewer.md) — Static audit of every Mermaid block in docs/<lang>/ against the spec plus MkDocs setup; structured findings, no rendering.
- [`project-structure-reviewer`](nolte-shared/project-structure-reviewer.md) — Read-only audit of the repository's layout against the project-structure spec; severity-sorted findings on disk only.
- [`prose-vale-curator`](nolte-shared/prose-vale-curator.md) — Curates prose to pass Vale, prefers shipped vocabularies, extends accept.txt only inside vocabulary-owning repos.
- [`quality-gate-enforcer`](nolte-shared/quality-gate-enforcer.md) — Reviews the quality-gate wiring (Taskfile, pre-commit, CI workflow, timeouts) for spec-conformance; never executes the gate.
- [`tech-stack-drift-reviewer`](nolte-shared/tech-stack-drift-reviewer.md) — Read-only tech-stack drift audit: diffs declared manifest against on-disk repo signals (lockfiles, configs, workflows).

## 8 Cross-cutting

- [`cookiecutter-template-author`](nolte-shared/cookiecutter-template-author.md) — Scaffolds or refactors Cookiecutter templates, hardens hooks, sets up pytest-cookies harness + GitHub Actions matrix.
- [`png-to-transparent-svg`](nolte-shared/png-to-transparent-svg.md) — Converts a PNG with fake-transparency background (checkerboard or single colour) into a clean SVG with real alpha.
