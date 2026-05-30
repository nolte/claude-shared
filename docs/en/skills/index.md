---
title: Skills
audience: [maintainer]
content_mode: meta
track: developer-docs
last_updated: generated
---

# Skills

[**Browse by task →**](../by-task.md)

Auto-generated catalog of every skill discovered across the configured plugin source roots. Content is taken verbatim from each `SKILL.md` frontmatter and body. Grouped by delivery-lifecycle phase.

## 1 Vision

- [`mission-define`](nolte-shared/mission-define.md) — Authors a project's first project/mission.md via the SMART walk and the four required body sections.
- [`mission-revise`](nolte-shared/mission-revise.md) — Revises an existing project/mission.md: statement, audiences, time bound, or mvp_status lifecycle flips.

## 2 Plan

- [`audience-identify`](nolte-shared/audience-identify.md) — Runs the audience-identification methodology against a bounded context and produces an authoritative audience artifact.
- [`feature-decompose`](nolte-shared/feature-decompose.md) — Decomposes a roadmap item into feature files with testable acceptance criteria and test hooks.
- [`roadmap-init`](nolte-shared/roadmap-init.md) — Scaffolds the project planning pair project/goals.md and project/roadmap.md for the first time.
- [`roadmap-plan`](nolte-shared/roadmap-plan.md) — Adds, retargets, and reshapes roadmap items in project/roadmap.md with full lifecycle validation.
- [`roadmap-refine`](nolte-shared/roadmap-refine.md) — Enforces the detail-level invariant on project/roadmap.md (current and next sprint items must be 'fine').
- [`sprint-plan`](nolte-shared/sprint-plan.md) — Creates a new sprint file under project/sprints/ with value statement, features, and value-verifying acceptance criterion.

## 3 Design

- [`cookiecutter-template-manage`](nolte-shared/cookiecutter-template-manage.md) — Manages a Cookiecutter template lifecycle: scaffold, refactor, harden hooks, set up the pytest-cookies harness.
- [`docs-audience-tracks-apply`](nolte-shared/docs-audience-tracks-apply.md) — Wires up per-page track frontmatter and audience-to-track mapping in MkDocs docs/; audit, migrate, or patch operations.
- [`docs-dry-refactor`](nolte-shared/docs-dry-refactor.md) — Detects duplicated MkDocs paragraphs and extracts them into mkdocs-include-markdown-plugin snippets.
- [`github-issue-templates-apply`](nolte-shared/github-issue-templates-apply.md) — Scaffolds spec-conformant GitHub Issue Forms (.github/ISSUE_TEMPLATE/) tailored to project type and audience.
- [`mermaid-diagrams-apply`](nolte-shared/mermaid-diagrams-apply.md) — Audits and wires up MkDocs Mermaid setup; helps an author add a single Mermaid diagram with the mandatory source marker.
- [`mkdocs-structure-apply`](nolte-shared/mkdocs-structure-apply.md) — Audits and scaffolds the portfolio-wide MkDocs skeleton: per-language docs/ tree, plugin baseline, nav contract, per-page frontmatter.
- [`permission-allowlist-maintain`](nolte-shared/permission-allowlist-maintain.md) — Curates the committed .claude/settings.json permissions.allow list per the permission-allowlist spec.
- [`project-structure-apply`](nolte-shared/project-structure-apply.md) — Audits a repository against the project-structure spec and scaffolds missing artefacts (README, .github/, Renovate, Taskfile, MkDocs, .claude/).
- [`readme-structure-apply`](nolte-shared/readme-structure-apply.md) — Audits, scaffolds, or patches a repository's README.md against the readme-structure spec (six required sections, ≤200 lines).
- [`skill-agent-catalog-apply`](nolte-shared/skill-agent-catalog-apply.md) — Wires up the MkDocs skill-and-agent catalog (gen-files + literate-nav, generator hook, source-roots) in a plugin or consumer repo.
- [`skill-management`](nolte-shared/skill-management.md) — Scaffolds or revises a nolte-shared Claude Code skill folder.
- [`spec`](nolte-shared/spec.md) — Authors, translates, indexes, and drift-checks bilingual specifications under spec/.
- [`tech-stack-capture`](nolte-shared/tech-stack-capture.md) — Captures or refreshes the tech_stack block in project/portfolio.yml by probing lockfiles, Taskfile, CI, and tooling configs.
- [`webview-ui-optimize`](nolte-shared/webview-ui-optimize.md) — Audits and patches a browser-rendered frontend across Performance, Security, A11y (WCAG 2.2 AA), i18n, and UX.
- [`yaml-json-schema`](nolte-shared/yaml-json-schema.md) — Authors, audits, refactors, and validates YAML-encoded JSON Schema 2020-12 documents.

## 4 Build

- [`blog-author`](nolte-shared/blog-author.md) — Drafts a bilingual EN-canonical + DE-translated blog-post pair per this plugin's blog-author specs, writing into a consumer blog repo.
- [`blog-author-trigger`](nolte-shared/blog-author-trigger.md) — On a feature→done transition, derives a blog-post briefing, suggests new/update/defer, and either dispatches blog-author or writes a deferral artefact.
- [`image-generate`](nolte-shared/image-generate.md) — Generates an image from a text prompt via a swappable provider backend (Cloudflare/Pollinations/Gemini), writing the image plus a metadata sidecar to a chosen path.
- [`sprint-execute`](nolte-shared/sprint-execute.md) — Drives the daily mechanics of an active sprint: lifecycle transitions, feature-list sync, last_commit updates.

## 5 Review

- [`agent-review`](nolte-shared/agent-review.md) — Reviews a Claude Code agent against the spec and emits an actionable review plan under .audits/agent-review/.
- [`continuous-improvement-triage`](nolte-shared/continuous-improvement-triage.md) — Triages portfolio audit findings and dispatches hands-on remediation to the most specialised available agent or skill.
- [`portfolio-inflight-triage`](nolte-shared/portfolio-inflight-triage.md) — Runs the read-only periodic in-flight audit across nolte/* (open PRs, branches, issues, review threads) with severity classification.
- [`pull-request-create`](nolte-shared/pull-request-create.md) — Opens a spec-conformant draft GitHub pull request on the current feature branch.
- [`pull-request-merge`](nolte-shared/pull-request-merge.md) — Promotes a draft PR to merged on develop, passing every pull-request-workflow gate.
- [`skill-review`](nolte-shared/skill-review.md) — Reviews a Claude Code skill against the spec and emits an actionable review plan under .audits/skill-review/.
- [`skills-agents-sweep`](nolte-shared/skills-agents-sweep.md) — Orchestrates a portfolio-wide sweep audit of all skills and agents with cross-cutting findings and a wave-based roadmap.
- [`spec-drift-audit`](nolte-shared/spec-drift-audit.md) — Audits every spec against the repository implementation and produces a traceable spec-drift audit artifact.

## 6 Quality

- [`dependency-audit`](nolte-shared/dependency-audit.md) — Scans the project's dependency tree for known CVEs and (optionally) license-compliance issues; severity-sorted report.
- [`lektorat-apply`](nolte-shared/lektorat-apply.md) — Reviews existing Markdown prose against five editorial dimensions (readability, comprehensibility, grammar, style, audience-fit).
- [`portfolio-audit`](nolte-shared/portfolio-audit.md) — Audits, renders, and bootstraps the cross-repository capability portfolio across nolte/*.
- [`quality-gate`](nolte-shared/quality-gate.md) — Runs the project's lint + typecheck + test gate in parallel and tabulates which checks failed.
- [`vocab-drift-audit`](nolte-shared/vocab-drift-audit.md) — Audits repository-local Vale vocabularies against the pinned upstream nolte/vale-style release to detect drift.
- [`workflow-health-triage`](nolte-shared/workflow-health-triage.md) — Triages a failing GitHub Actions workflow on develop/main and dispatches the most specialised agent to remediate.

## 7 Close & Release

- [`release-notes-curate`](nolte-shared/release-notes-curate.md) — Augments the open release-drafter draft on develop with project-context-aware sections via gh release edit.
- [`release-publish-trigger`](nolte-shared/release-publish-trigger.md) — Validates every pre-publish gate locally, then dispatches release-publish.yml for the open release-drafter draft on develop.
- [`sprint-review`](nolte-shared/sprint-review.md) — Closes an active sprint per the sprint spec: validates the deployable artefact and records the value-delivery audit trail.
