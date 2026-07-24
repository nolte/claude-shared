---
id: F-10
title: Documented, absent-safe GitHub MCP server setup
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
  reruns:
    - performed_at: 2026-07-13
      agent_version: feature-consistency-reviewer@dc510c9
      trigger: "Material change — recast as purely documentary (per-machine chezmoi setup, no repo .mcp.json); title + Description + acceptance-1/3/4 reworded; OQ-B resolved."
      findings:
        - kind: overlap
          target: F-13
          resolution: proceed
        - kind: overlap
          target: F-9
          resolution: proceed
---

## Description

The GitHub MCP server is provisioned **per-machine, outside this repository** — the real, working setup lives in the operator's chezmoi-managed `~/.claude.json` under `mcpServers.github` (the hosted remote endpoint, PAT via an environment variable). This feature does **not** introduce a repo-committed `.mcp.json`; instead `claude-shared` **documents** that per-machine setup as the reference and guarantees the absent-safe contract, so a consumer without an MCP server is unaffected. No token or secret is committed to a tracked file — the PAT lives only in the `GITHUB_MCP_PAT` environment variable.

Merely having the server configured changes no artefact's output: at this stage no in-scope artefact prefers MCP yet (adoption starts with the F-13 pilot), so the setup is output-neutral. It only makes the MCP tools reachable for artefacts that later opt to prefer them, while the `gh`-only path stays fully intact.

## Acceptance criteria

- [ ] **acceptance-1** The per-machine MCP server setup is documented (referencing the chezmoi-managed `~/.claude.json` `mcpServers.github` pattern with the hosted endpoint and PAT env var); no repo-committed `.mcp.json` is introduced.
- [ ] **acceptance-2** With the MCP server absent, every in-scope GitHub-touching skill/agent still completes its GitHub reads via `gh` — the `gh`-only path is unbroken.
- [ ] **acceptance-3** Having the MCP server configured changes no artefact's output: every in-scope artefact produces output identical to its `gh`-only baseline when the server is merely present (setup is output-neutral).
- [ ] **acceptance-4** No token or secret is committed to a tracked file; the PAT lives only in the `GITHUB_MCP_PAT` environment variable.

## Test hooks

- **acceptance-1** — manual: confirm the docs describe the per-machine `~/.claude.json` setup; assert no `.mcp.json` is committed to the repo — `pending`
- **acceptance-2** — manual: run an in-scope artefact with the server absent; confirm it completes via `gh` — `pending`
- **acceptance-3** — manual: run an in-scope artefact with the server configured vs `gh`-only; confirm output is unchanged — `pending`
- **acceptance-4** — manual: `git ls-files` shows no committed token; the PAT is only in `GITHUB_MCP_PAT` — `pending`

## Consistency notes

The consistency check ran via the `feature-consistency-reviewer` agent (`agent_version: feature-consistency-reviewer@90d0141`) and returned one finding.

- **overlap** (`F-13`, the P6 pilot sibling; resolution `proceed`): both F-10 and F-13 carry an identical-output acceptance criterion, which is a criterion-to-criterion match the consistency surface is built to flag. The two checks verify **genuinely different properties**, so `proceed` is correct rather than `merge-into F-13`. **Rationale (one paragraph, as the blocker rule requires for a `proceed` on an `overlap` finding):** F-10's acceptance-3 is a *config-neutrality* assertion — at F-10's stage no in-scope artefact prefers MCP (adoption starts at the P6/F-13 pilot per the #378 analysis dependency ordering `{P2,P3,P4,P5} → P6`), so all acceptance-3 proves is that merely *provisioning* the server changes nothing about any artefact's output. F-13's identical-output check is a different thing entirely: it is the per-artefact diff of the pilot collector *after* it adopts MCP-preferred reads, comparing the MCP-present run against the `gh`-only run of the same artefact. Folding F-10 into F-13 (`merge-into`) would collapse the P2→P6 dependency edge and fuse config provisioning with pilot adoption, which the analysis deliberately stages apart; the config must exist and be proven output-neutral before any artefact is taught to prefer MCP. Following the reviewer's recommendation, acceptance-3 is scoped to config-enablement neutrality ("no artefact's output changes on enablement") so it stays strictly inside F-10's config-provisioning scope and does not read as the per-artefact diff that belongs to F-13.

The spec surface aligns rather than conflicts: `spec/claude/mcp-tool-preference/en.md` Open Questions §"Provisioning surface" explicitly delegates OQ-B to the provisioning work package (P2 of #378), and its Non-Goal §reserves the server's installation/auth/config surface to a separate concern — F-10 *is* that owner, so no drift or prior-art applies.

**2026-07-13 — re-run (`feature-consistency-reviewer@dc510c9`), triggered by a material change.** F-10 was recast as **purely documentary**: the server is provisioned per-machine via the operator's chezmoi-managed `~/.claude.json` `mcpServers.github` entry (hosted endpoint + PAT env var), F-10 introduces no repo-committed `.mcp.json`, and OQ-B is resolved to "per-machine, outside the repo." The re-run returned two findings, and confirmed **no drift** vs P3 — documenting-per-machine selects one of the two options P3 §"Provisioning surface" explicitly enumerates and delegates to this work package, so it is a clean OQ-B resolution, not a re-implementation.

- **overlap** (`F-13`; resolution `proceed`): the prior finding still holds under the new wording. F-10 acceptance-3 remains a *setup-neutrality* assertion (merely provisioning the server changes no artefact's output, since no in-scope artefact prefers MCP yet), which is a distinct property from F-13's post-adoption per-artefact identical-output diff; the one-paragraph rationale in the paragraph above continues to apply and `merge-into F-13` would still wrongly collapse the P2→P6 staging.
- **overlap** (`F-9`; resolution `proceed`): the documentary recast pulled the PAT / `GITHUB_MCP_PAT` secret-handling into F-10 acceptance-4 near-verbatim to F-9 acceptance-2 — a new criterion-to-criterion match surfaced by this re-run. **Rationale (one paragraph, as required for a `proceed` on an `overlap` finding):** the match sits on the deliberate P1(decision)→P2(provisioning) boundary. F-9 records the auth-model *decision* (a decision-only artefact stating the least-privilege model), while F-10 documents and verifies the *provisioned reality* (the actual setup carries no committed token, and F-10 additionally owns the absent-safe / output-neutrality contract F-9 does not touch). Each side carries non-redundant work over the shared token-handling clause; `merge-into F-9` would fuse the on-disk documentation and absent-safe guarantee into a decision-only artefact and erase the decide-then-document boundary the #378 analysis keeps apart. This is structurally the same staged-overlap `proceed` already recorded for F-13→F-14.

## Risks

- **MCP absent in headless/cron.** The optional contract must be real: acceptance-2 and acceptance-3 are the hard checks that the `gh`-only path is unbroken and output-neutral. Mitigation is that both are gating acceptance criteria.
- **Auth-token / secret handling.** The config is secret-adjacent; acceptance-4 keeps any token out of tracked files. Treat the config as secret-adjacent at PR time.

## Open questions

- **OQ-B (config surface)** — **resolved (2026-07-13)**: per-machine, outside the repo. The server is provisioned via the operator's chezmoi-managed `~/.claude.json` `mcpServers.github` entry, not a repo-committed `.mcp.json`; `claude-shared` documents that setup rather than shipping config. (Evidence: `nolte/workstation` `chezmoi_config/modify_dot_claude.json`.)

## References

- Roadmap item R-10 (`project/roadmap.md`).
- Work package P2 in the issue #378 pre-analysis (retired to git history).
- GitHub issue #378; tracking issue #382.
