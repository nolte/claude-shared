---
number: 0004
status: planned
started: null
ended: null
value_statement: "Contributors and downstream adopters can audit every plan-, structure-, sprint-, quality-gate-, Mermaid-, and tech-stack artefact with a read-only reviewer agent paired to each apply-style skill before they commit."
artifact_ref: null
last_commit: null
roadmap_items: [R-8]
features: [F-4]
---

## Goal

Deliver to contributors and downstream adopters a complete set of read-only reviewer agents, one per planning- and quality-relevant artefact cluster, each paired with its apply-style skill. By sprint close, every cluster R-8 names (roadmap / plan, project structure, sprint, quality gate, Mermaid diagrams, tech-stack drift) has a dedicated reviewer agent under `agents/` that audits without mutating, names its apply-style counterpart, and renders bilingually in the skill-agent catalog. The verifying acceptance criterion (`F-4:acceptance-1`) confirms all six clusters are covered, which is exactly the value-delivery claim this sprint makes.

This sprint is framed retroactively: the six reviewer agents already ship on `develop` (delivered through PRs #152 to #157). The value-bearing delta is therefore not new agent authoring but the formal verification and roadmap reconciliation that closes R-8 against its delivered surface. The agents themselves, already at HEAD, are the artefact; this sprint records that the coverage is complete and spec-conformant.

## Features

- [F-4](`../features/reviewer-agent-coverage.md`) — status: ready

## Out of scope

- Authoring any new reviewer agent beyond the six R-8 names; the six are already shipped and this sprint verifies rather than extends them.
- Changes to the apply-style skills the reviewers pair with (`roadmap-plan`, `project-structure-apply`, `sprint-plan`, `quality-gate`, `mermaid-diagrams-apply`, `tech-stack-capture`); those ship independently.
- Reviewer coverage for clusters not named by R-8 (for example a release-cluster reviewer); a future roadmap item may widen the set.
- Promotion of additional roadmap items beyond R-8 into this sprint (R-3 stays queued in Sprint 0003; R-4 through R-7 remain proposed).

## Review notes

_Populated by `sprint-review` at closure._
