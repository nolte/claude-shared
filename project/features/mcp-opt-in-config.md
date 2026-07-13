---
id: F-10
title: Opt-in, absent-safe GitHub MCP server config
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
    - kind: overlap
      target: F-13
      resolution: proceed
---

## Description

The `claude-shared` repository gains an opt-in GitHub MCP server configuration a maintainer can enable, without breaking any run where the server is absent. The config is claude-shared-repo-scoped — each consumer provisions its own server per the portfolio-scope boundary — and no token or secret is committed to a tracked file.

Merely enabling the config changes no artefact's output: at this stage no in-scope artefact prefers MCP yet (adoption starts with the F-13 pilot), so the config is output-neutral. It only makes the MCP tools reachable for artefacts that later opt to prefer them, while the `gh`-only path stays fully intact.

## Acceptance criteria

- [ ] **acceptance-1** An opt-in GitHub MCP server config exists in the repo (surface per OQ-B); enabling it connects the server.
- [ ] **acceptance-2** With the MCP server absent, every in-scope GitHub-touching skill/agent still completes its GitHub reads via `gh` — the `gh`-only path is unbroken.
- [ ] **acceptance-3** Enabling the MCP config changes no artefact's output: every in-scope artefact produces output identical to its `gh`-only baseline when the config is merely present (config-enablement is output-neutral).
- [ ] **acceptance-4** No token or secret is committed to a tracked file; if a token file is introduced it is `.gitignore`d.

## Test hooks

- **acceptance-1** — manual: inspect the config surface; confirm it connects the server when enabled — `pending`
- **acceptance-2** — manual: run an in-scope artefact with the server absent; confirm it completes via `gh` — `pending`
- **acceptance-3** — manual: run an in-scope artefact with the config present vs `gh`-only; confirm output is unchanged — `pending`
- **acceptance-4** — manual: `git ls-files` shows no committed token; any token file is gitignored — `pending`

## Consistency notes

The consistency check ran via the `feature-consistency-reviewer` agent (`agent_version: feature-consistency-reviewer@90d0141`) and returned one finding.

- **overlap** (`F-13`, the P6 pilot sibling; resolution `proceed`): both F-10 and F-13 carry an identical-output acceptance criterion, which is a criterion-to-criterion match the consistency surface is built to flag. The two checks verify **genuinely different properties**, so `proceed` is correct rather than `merge-into F-13`. **Rationale (one paragraph, as the blocker rule requires for a `proceed` on an `overlap` finding):** F-10's acceptance-3 is a *config-neutrality* assertion — at F-10's stage no in-scope artefact prefers MCP (adoption starts at the P6/F-13 pilot per the #378 analysis dependency ordering `{P2,P3,P4,P5} → P6`), so all acceptance-3 proves is that merely *provisioning* the server changes nothing about any artefact's output. F-13's identical-output check is a different thing entirely: it is the per-artefact diff of the pilot collector *after* it adopts MCP-preferred reads, comparing the MCP-present run against the `gh`-only run of the same artefact. Folding F-10 into F-13 (`merge-into`) would collapse the P2→P6 dependency edge and fuse config provisioning with pilot adoption, which the analysis deliberately stages apart; the config must exist and be proven output-neutral before any artefact is taught to prefer MCP. Following the reviewer's recommendation, acceptance-3 is scoped to config-enablement neutrality ("no artefact's output changes on enablement") so it stays strictly inside F-10's config-provisioning scope and does not read as the per-artefact diff that belongs to F-13.

The spec surface aligns rather than conflicts: `spec/claude/mcp-tool-preference/en.md` Open Questions §"Provisioning surface" explicitly delegates OQ-B to the provisioning work package (P2 of #378), and its Non-Goal §reserves the server's installation/auth/config surface to a separate concern — F-10 *is* that owner, so no drift or prior-art applies.

## Risks

- **MCP absent in headless/cron.** The optional contract must be real: acceptance-2 and acceptance-3 are the hard checks that the `gh`-only path is unbroken and output-neutral. Mitigation is that both are gating acceptance criteria.
- **Auth-token / secret handling.** The config is secret-adjacent; acceptance-4 keeps any token out of tracked files. Treat the config as secret-adjacent at PR time.

## Open questions

- **OQ-B (config surface)** — open: a repo-root shipped `.mcp.json` versus a documented per-consumer setup. Resolved when this feature is implemented.

## References

- Roadmap item R-10 (`project/roadmap.md`).
- Work package P2 in `.audits/issue-orchestrate/378/analysis.md`.
- GitHub issue #378; tracking issue #382.
