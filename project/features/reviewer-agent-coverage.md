---
id: F-4
title: Reviewer agent coverage across every skill cluster
status: ready
roadmap_item: R-8
sprint: 4
created: 2026-05-28
ended: null
verifies_sprint_value: acceptance-1
consistency_check:
  performed_at: 2026-05-28
  agent_version: feature-consistency-reviewer@da0e52d
  findings:
    - kind: prior-art
      target: agents/ (all six reviewer agents)
      resolution: proceed
    - kind: clean
      target: n/a
      resolution: proceed
---

## Description

Contributors and downstream adopters find a dedicated read-only reviewer agent for every planning- and quality-relevant artefact cluster, each paired with its apply-style skill. They can audit the roadmap, the project structure, a sprint, the quality gate, Mermaid diagrams, and tech-stack drift before they commit, without holding the governing spec in their head. The six agents follow two shipped templates (the `feature-consistency-reviewer` plan/quality style and the `vocab-drift-scanner` / `docs-freshness-checker` drift style), closing the review-depth gap that apply-only skills leave open.

The feature is framed retroactively: the six reviewer agents already ship on `develop` (delivered through PRs #152 to #157). Its acceptance criteria therefore verify the existence and spec-conformance of the delivered agents rather than their creation.

## Acceptance criteria

- [ ] **acceptance-1** All six artefact clusters named by R-8 have a dedicated read-only reviewer agent present under `agents/`: `roadmap-coherence-reviewer` (plan), `project-structure-reviewer` (structure), `sprint-readiness-reviewer` (sprint), `quality-gate-enforcer` (quality-gate), `mermaid-diagram-reviewer` (Mermaid), and `tech-stack-drift-reviewer` (tech-stack).
- [ ] **acceptance-2** Each of the six agents declares a read-only tool set (no `Edit`, no `Write`; `Bash` only under the documented narrow read-only exception per `spec/claude/agent-management/`), so an audit run can never mutate the repository.
- [ ] **acceptance-3** Each of the six agents names its paired apply-style skill in `see_also` (for example `project-structure-reviewer` to `project-structure-apply`), so a reader finds the review/apply pairing without guessing.
- [ ] **acceptance-4** Each of the six agents carries both `summary` and `summary_de` frontmatter, so the bilingual skill-agent catalog renders the reviewer in either language.
- [ ] **acceptance-5** `task validate:skills` passes with all six agents present, confirming their frontmatter conforms to `spec/claude/agent-management/`.

## Test hooks

- **acceptance-1** — manual: confirm `agents/roadmap-coherence-reviewer.md`, `agents/project-structure-reviewer.md`, `agents/sprint-readiness-reviewer.md`, `agents/quality-gate-enforcer.md`, `agents/mermaid-diagram-reviewer.md`, and `agents/tech-stack-drift-reviewer.md` all exist — `pending`
- **acceptance-2** — manual: read the `tools` frontmatter of each of the six agent files; assert none lists `Edit` or `Write` — `pending`
- **acceptance-3** — manual: read the `see_also` frontmatter of each; assert each names its apply-style skill — `pending`
- **acceptance-4** — manual: read each agent's frontmatter and assert both `summary` and `summary_de` are present — `pending`
- **acceptance-5** — CLI: `task validate:skills` exits `0` — `pending`

## Consistency notes

The consistency check ran via the `feature-consistency-reviewer` agent (`agent_version: feature-consistency-reviewer@da0e52d`) and returned two findings:

- **prior-art** (`agents/`, all six reviewer agents; resolution `proceed`): every acceptance criterion describes behaviour the source surface already implements, because the six agents shipped through PRs #152 to #157. This is `prior-art` by definition, not `duplication`: no sibling feature file claims this scope, and the prior-art lives in source. The feature openly frames itself as retroactive verification of existence and spec-conformance rather than creation, so `proceed` is correct. Per `spec/project/feature/` §Consistency check, `prior-art` is not a blocking kind, so it does not gate the `draft → ready` transition.
- **clean** (`n/a`; resolution `proceed`): the existing feature corpus carries no overlapping scope. F-1 targets `project/mission.md` (R-1), F-2 the release pipeline (R-2), and F-3 `README.md` plus `Taskfile.yml` (R-3); none touches `agents/` or claims R-8. The spec corpus is consistent: acceptance-2's read-only wording restates `spec/claude/agent-management/` §Tool access, and acceptance-4's `summary` / `summary_de` requirement matches the same spec, with no drift.

The reviewing agent noted that its `rg`-backed enumeration tooling was unavailable in that run; it established the three-feature corpus by direct reads of F-1, F-2, and F-3 plus the roadmap's R-1/R-2/R-3 mapping. The same three-feature corpus was confirmed independently before this file was written.

## Risks

- The acceptance criteria assert the present-tense existence and shape of six agents. A future rename or removal of any reviewer agent (or a change to its `tools` / `see_also` / `summary` frontmatter) would silently break a criterion; the catalog freshness check and `validate:skills` are the standing guards, but this feature does not itself install a regression gate.
- Framed retroactively, the feature documents already-delivered work. Its value to consumers is real (the review depth exists today), but the planning artefact must not be read as a forward commitment to build the agents; the `## Description` makes the retroactive framing explicit to prevent that misreading.
