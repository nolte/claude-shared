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
- [`sprint-readiness-reviewer`](nolte-shared/sprint-readiness-reviewer.md) — Read-only sprint-readiness gate: go/no-go report on a sprint before sprint-execute promotes it planned → active.

## 3 Design

- [`audience-doc-author`](nolte-shared/audience-doc-author.md) — Drafts or refines audience-tailored documentation (README, release notes, MkDocs pages) against an existing audience artifact.
- [`claude-plugin-developer`](nolte-shared/claude-plugin-developer.md) — Drafts spec-conformant Claude Code plugin artifacts (skill or agent) for nolte-shared, executor in the skill-orchestrates-agent pattern.
- [`spec-readiness-reviewer`](nolte-shared/spec-readiness-reviewer.md) — Read-only audit of a spec for contradictions, audience fit, and AC coverage.
- [`webview-ui-expert`](nolte-shared/webview-ui-expert.md) — Read-only deep cross-file review of one named frontend target across Performance, Security, A11y, i18n, UX.

## 5 Review

- [`dependency-audit-scanner`](nolte-shared/dependency-audit-scanner.md) — Read-only CVE scanner per project type (pip-audit, npm audit, govulncheck, cargo audit); returns structured drift inventory.
- [`diagram-opportunity-reviewer`](nolte-shared/diagram-opportunity-reviewer.md) — Read-only prose scanner that flags Markdown passages which would be expressed better as a Mermaid diagram.
- [`lektorat-scanner`](nolte-shared/lektorat-scanner.md) — Read-only editorial scanner across the five lektorat dimensions (D1 readability, D2 comprehensibility, D3 grammar, D4 style, D5 audience-fit).
- [`portfolio-inflight-collector`](nolte-shared/portfolio-inflight-collector.md) — Read-only in-flight data collector: open issues, PRs (incl. drafts), branches without PR, unresolved review threads + Discussions across nolte/*.
- [`portfolio-manifest-collector`](nolte-shared/portfolio-manifest-collector.md) — Read-only inventory collector: gathers per-repo project/portfolio.yml manifests across nolte/*.
- [`vocab-drift-scanner`](nolte-shared/vocab-drift-scanner.md) — Read-only diff of repository-local Vale vocab files against the pinned upstream nolte/vale-style release.

## 6 Quality

- [`docs-freshness-checker`](nolte-shared/docs-freshness-checker.md) — Read-only freshness audit of MkDocs docs: language parity, dead links, stale spec/code refs, ADR hygiene, Mermaid derived-source drift.
- [`mermaid-diagram-reviewer`](nolte-shared/mermaid-diagram-reviewer.md) — Static audit of every Mermaid block in docs/<lang>/ against the spec plus MkDocs setup; structured findings, no rendering.
- [`project-structure-reviewer`](nolte-shared/project-structure-reviewer.md) — Read-only audit of the repository's layout against the project-structure spec; severity-sorted findings on disk only.
- [`prose-vale-curator`](nolte-shared/prose-vale-curator.md) — Curates prose to pass Vale, prefers shipped vocabularies, extends accept.txt only inside vocabulary-owning repos.
- [`quality-gate-enforcer`](nolte-shared/quality-gate-enforcer.md) — Reviews the quality-gate wiring (Taskfile, pre-commit, CI workflow, timeouts) for spec-conformance; never executes the gate.
- [`tech-stack-drift-reviewer`](nolte-shared/tech-stack-drift-reviewer.md) — Read-only tech-stack drift audit: diffs declared manifest against on-disk repo signals (lockfiles, configs, workflows).

## 8 Cross-cutting

- [`cookiecutter-template-author`](nolte-shared/cookiecutter-template-author.md) — Scaffolds or refactors Cookiecutter templates, hardens hooks, sets up pytest-cookies harness + GitHub Actions matrix.
- [`png-to-transparent-svg`](nolte-shared/png-to-transparent-svg.md) — Converts a PNG with fake-transparency background (checkerboard or single colour) into a clean SVG with real alpha.
