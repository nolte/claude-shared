---
id: F-15
title: Tier-2 MCP adoption (read metadata / verification)
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
    - kind: clean
      target: n/a
      resolution: proceed
---

## Description

Medium-benefit artefacts adopt the same optional / `gh`-fallback contract for their GitHub metadata reads: `portfolio-audit`, `portfolio-inflight-triage`, `vocab-drift-audit`, `release-notes-curate`, `pull-request-merge` (status reads), `continuous-improvement-triage` / `sprint-review`, and `project-structure-apply`. Each prefers MCP reads when the server is present and falls back to `gh` when absent, with output identical either way.

Where a specific operation has no clean MCP tool (OQ-D — for example GitHub-App install checks or `gh release edit`), that operation stays on `gh` and the artefact documents that the fallback is intentional there. This feature is gated behind the Tier-1 work (F-14).

## Acceptance criteria

- [ ] **acceptance-1** Each listed artefact prefers GitHub MCP reads when the server is present and falls back to `gh` when absent.
- [ ] **acceptance-2** Each produces the same output on the MCP-present run as on the `gh`-only run (identical deterministic output).
- [ ] **acceptance-3** Each references the P3 convention (`spec/claude/mcp-tool-preference/`).
- [ ] **acceptance-4** Any operation without a clean MCP tool (OQ-D) stays on `gh`, and the artefact documents that the `gh` path is intentional there.

## Test hooks

- **acceptance-1** — manual: per artefact, confirm MCP-preferred reads with `gh` fallback — `pending`
- **acceptance-2** — diff: per artefact, MCP-present vs `gh`-only output identical over the deterministic payload — `pending`
- **acceptance-3** — manual: per artefact, confirm the citation of `spec/claude/mcp-tool-preference/` — `pending`
- **acceptance-4** — manual: confirm any `gh`-only operation is documented as an intentional coverage gap — `pending`

## Consistency notes

The consistency check ran via the `feature-consistency-reviewer` agent (`agent_version: feature-consistency-reviewer@90d0141`) and returned a single `clean` finding. The `draft → ready` gate is not blocked.

- **clean** (resolution `proceed`): all three mandated surfaces were scanned with no actionable hit. No existing feature under `project/features/` shares R-10's Tier-2 scope or a matching acceptance criterion (rules out `overlap` / `duplication`); none of the seven listed skills already implements the MCP-preferred read path (rules out source `prior-art`); and every criterion maps onto a P3 MUST without contradicting one — notably `pull-request-merge` (status reads) and `gh release edit` are correctly kept on the `gh` / write path per §Reads-versus-writes (rules out `drift`). The one MCP reference found in the source surface (`continuous-improvement-triage`, the trusted-author injection guard) is unrelated to Tier-2 read adoption.

Procedural note: at decomposition time the sibling drafts F-13 / F-14 / F-16 were not yet on disk, so the disjoint-artefact partition could not be cross-checked against actual files. Per `spec/project/feature/` §Consistency check, a re-run on F-15 is advisable once those siblings land ("a feature with overlapping scope is added elsewhere in `project/features/`" is a re-run trigger); the sibling set is expected to remain disjoint from F-15's seven artefacts.

## Risks

- **OQ-D coverage variance.** Some listed artefacts may have operations without a clean MCP tool; acceptance-4 keeps those on `gh` explicitly rather than forcing an unsatisfiable adoption.
- **Prerequisite.** Gated behind F-14 (Tier-1 remainder), which is itself gated behind the F-13 pilot.

## Open questions

- **OQ-D (per-operation tool coverage)** — open: which listed operations lack a clean MCP tool and therefore stay on `gh` (GitHub-App install checks, `gh release edit`, status-only reads). Confirmed per artefact at implementation time.

## References

- Roadmap item R-10 (`project/roadmap.md`).
- Work package P8 in `.audits/issue-orchestrate/378/analysis.md`.
- GitHub issue #378; tracking issue #382.
