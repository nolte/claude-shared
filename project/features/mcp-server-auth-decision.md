---
id: F-9
title: Decide the GitHub MCP server + least-privilege auth model
status: draft
roadmap_item: R-10
sprint: null
created: 2026-07-13
ended: null
verifies_sprint_value: null
consistency_check:
  performed_at: 2026-07-13
  agent_version: feature-consistency-reviewer@90d0141
  findings:
    - kind: prior-art
      target: spec/claude/mcp-tool-preference/en.md
      resolution: proceed
---

## Description

Maintainers of `claude-shared` get a single recorded decision that fixes the enabling choices before any MCP wiring begins: which GitHub MCP server is used, how it is version-pinned, and the least-privilege auth model. This is a decision-only feature — it produces a written record, not code — mirroring how an analysis-artifact feature records a verdict.

It exists so the downstream wiring (F-10 config), allowlist extension (F-11), agent `tools:` grants (F-12), and the pilot (F-13) all reference one fixed choice instead of re-deciding it. The decision is a claude-shared rollout decision: it names the reference server the P3 convention (`spec/claude/mcp-tool-preference/`) already points at, rather than mandating a single server portfolio-wide (the convention is deliberately server-agnostic, and each consumer provisions its own server).

## Acceptance criteria

- [ ] **acceptance-1** A recorded decision names the GitHub MCP server — the P3 convention's reference server, GitHub's official `github-mcp-server`, which a consumer MAY replace — and the version-pin approach.
- [ ] **acceptance-2** The decision states the least-privilege auth model — read-only scopes for repo / actions / issues / pull-requests — and that no broader or write scope is requested.
- [ ] **acceptance-3** The decision records the opt-in + absent-safe stance: no artefact ever requires MCP, and an absent server is always safe.
- [ ] **acceptance-4** The decision resolves OQ-C (server choice) and records that any operation lacking a clean MCP tool (OQ-D — for example GitHub-App install checks or `gh release edit`) stays on `gh`.

## Test hooks

- **acceptance-1** — manual: open the decision record; confirm the named reference server and the version-pin approach — `pending`
- **acceptance-2** — manual: confirm the read-only least-privilege scope list is stated and no write scope is requested — `pending`
- **acceptance-3** — manual: confirm the opt-in / absent-safe stance is recorded — `pending`
- **acceptance-4** — manual: confirm OQ-C is resolved and the OQ-D `gh`-stays coverage note is present — `pending`

## Consistency notes

The consistency check ran via the `feature-consistency-reviewer` agent (`agent_version: feature-consistency-reviewer@90d0141`) and returned one non-blocking finding. No `overlap` or `duplication` was raised, so the `draft → ready` gate is not blocked by this review.

- **prior-art** (`spec/claude/mcp-tool-preference/en.md`; resolution `proceed`): the shipped P3 convention already fixes, as normative rules, the constraints this feature restates — it names `github-mcp-server` as the server-agnostic reference server (en.md:55) and mandates the optionality / absent-safe / identical-output invariants (en.md:36–39). F-9 is net-new at the source level (no MCP wiring, no `.mcp.json`, no prior decision artifact on disk), and its job is precisely to pin the provisional defaults P3 and the #378 analysis leave open (OQ-C server choice, OQ-D per-operation tool coverage). This is prior-art, not duplication (F-9 is a repo-rollout decision record, P3 is the authoring convention — different level) and not drift (F-9 contradicts no P3 MUST). One caution carried from the reviewer and honoured in the description above: F-9's server choice **references** P3's server-agnostic reference-server naming rather than restating it as a portfolio-wide mandate — restating it as a mandate would create the very drift this finding does not yet see.

## Risks

- **MCP tool-name drift across server versions.** The decision must pin the server version so the exact tool names are verifiable against the pinned catalog at implementation time (F-11 / F-12 depend on those names). An unpinned server would let tool names drift and silently break the allowlist and agent grants.

## Open questions

- **OQ-C (server choice)** — provisional default: GitHub's official `github-mcp-server`. This feature is the place OQ-C is resolved.
- **OQ-D (per-operation tool coverage)** — some operations (GitHub-App install checks, `gh release edit`) may lack a clean MCP tool and stay on `gh`; the decision records the coverage stance, and the per-artefact detail is confirmed downstream (F-15, F-16).

## References

- Roadmap item R-10 (`project/roadmap.md`).
- Work package P1 in `.audits/issue-orchestrate/378/analysis.md`.
- GitHub issue #378; tracking issue #382.
