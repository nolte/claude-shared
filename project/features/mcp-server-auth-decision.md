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
  reruns:
    - performed_at: 2026-07-13
      agent_version: feature-consistency-reviewer@dc510c9
      trigger: "Material change — Description + acceptance-1/2 reworded to record the hosted endpoint (api.githubcopilot.com/mcp/) as the real working reference instance, PAT auth, server-agnostic; OQ-C resolved."
      findings:
        - kind: prior-art
          target: spec/claude/mcp-tool-preference/en.md
          resolution: proceed
        - kind: overlap
          target: F-10
          resolution: proceed
---

## Description

Maintainers of `claude-shared` get a single recorded decision that fixes the enabling choices before any MCP wiring begins: which GitHub MCP server is used, how it is version-pinned, and the least-privilege auth model. This is a decision-only feature — it produces a written record, not code — mirroring how an analysis-artifact feature records a verdict.

It exists so the downstream setup (F-10), allowlist extension (F-11), agent `tools:` grants (F-12), and the pilot (F-13) all reference one fixed choice instead of re-deciding it. The decision confirms GitHub's official MCP server as the reference and records the **real, already-working reference instance** — the hosted remote endpoint `https://api.githubcopilot.com/mcp/` (`type: http`), authenticated with a PAT and provisioned per-machine (see F-10) — as the concrete example. It stays deliberately **server-agnostic** per the P3 convention (`spec/claude/mcp-tool-preference/`): the endpoint above is the documented working example, not a portfolio-wide mandate, and a consumer MAY substitute the self-hosted `github-mcp-server` binary.

## Acceptance criteria

- [ ] **acceptance-1** A recorded decision confirms GitHub's official MCP server as the reference, records the real working reference instance (the hosted remote endpoint `https://api.githubcopilot.com/mcp/`, `type: http`), and stays server-agnostic per P3 (a consumer MAY substitute the self-hosted `github-mcp-server` binary). It records the version-pin stance per form: the hosted endpoint has no image pin, so its tool catalog is verified against the live endpoint; a self-hosted binary is pinned by image tag + digest.
- [ ] **acceptance-2** The decision states the least-privilege auth model: for the hosted endpoint a PAT (`GITHUB_MCP_PAT`) carried as a `Bearer` header, scoped read-only to repo / actions / issues / pull-requests, with no broader or write scope, and the token held only in an environment variable — never a tracked file.
- [ ] **acceptance-3** The decision records the opt-in + absent-safe stance: no artefact ever requires MCP, and an absent server is always safe.
- [ ] **acceptance-4** The decision records the OQ-C resolution (server choice settled) and that any operation lacking a clean MCP tool (OQ-D — for example GitHub-App install checks or `gh release edit`) stays on `gh`.

## Test hooks

- **acceptance-1** — manual: open the decision record; confirm the reference server, the recorded hosted-endpoint instance, the server-agnostic stance, and the per-form pin approach — `pending`
- **acceptance-2** — manual: confirm the PAT / `Bearer` least-privilege read scope model is stated, with the token in an env var and no write scope — `pending`
- **acceptance-3** — manual: confirm the opt-in / absent-safe stance is recorded — `pending`
- **acceptance-4** — manual: confirm OQ-C is resolved and the OQ-D `gh`-stays coverage note is present — `pending`

## Consistency notes

The consistency check ran via the `feature-consistency-reviewer` agent (`agent_version: feature-consistency-reviewer@90d0141`) and returned one non-blocking finding. No `overlap` or `duplication` was raised, so the `draft → ready` gate is not blocked by this review.

- **prior-art** (`spec/claude/mcp-tool-preference/en.md`; resolution `proceed`): the shipped P3 convention already fixes, as normative rules, the constraints this feature restates — it names `github-mcp-server` as the server-agnostic reference server (en.md:55) and mandates the optionality / absent-safe / identical-output invariants (en.md:36–39). F-9 is net-new at the source level (no MCP wiring, no `.mcp.json`, no prior decision artifact on disk), and its job is precisely to pin the provisional defaults P3 and the #378 analysis leave open (OQ-C server choice, OQ-D per-operation tool coverage). This is prior-art, not duplication (F-9 is a repo-rollout decision record, P3 is the authoring convention — different level) and not drift (F-9 contradicts no P3 MUST). One caution carried from the reviewer and honoured in the description above: F-9's server choice **references** P3's server-agnostic reference-server naming rather than restating it as a portfolio-wide mandate — restating it as a mandate would create the very drift this finding does not yet see.

**2026-07-13 — re-run (`feature-consistency-reviewer@dc510c9`), triggered by a material change.** The decision was re-grounded in the operator's real, already-working config (`nolte/workstation` `chezmoi_config/modify_dot_claude.json` → `~/.claude.json` `mcpServers.github`): the hosted remote endpoint `https://api.githubcopilot.com/mcp/` (`type: http`, `Bearer ${GITHUB_MCP_PAT}`) is now recorded as the real reference instance, acceptance-1/2 name the endpoint and PAT auth, and OQ-C is resolved. The re-run returned two findings.

- **prior-art** (`spec/claude/mcp-tool-preference/en.md`; resolution `proceed`): the reviewer confirmed the endpoint-specific rewrite **stays on the example-not-mandate side of P3** and is **not drift**. Recording `api.githubcopilot.com/mcp/` as the "real working reference instance" does not mandate a server, because F-9 frames it as the documented working example (not a portfolio-wide mandate) and keeps the "a consumer MAY substitute the self-hosted `github-mcp-server` binary" clause intact — mirroring P3:55's own "reference server … which a consumer MAY replace" structure. A drift verdict would require stripping the substitution clause or asserting the endpoint portfolio-wide; F-9 does neither.
- **overlap** (`F-10`; resolution `proceed`): the paired rewrites made F-9 acceptance-2 (PAT held "only in an environment variable — never a tracked file", naming `GITHUB_MCP_PAT`) and F-10 acceptance-4 (no committed secret; PAT only in `GITHUB_MCP_PAT`) a criterion-to-criterion match. **Rationale (one paragraph, as required for a `proceed` on an `overlap` finding):** the two features operate at different levels of the deliberate P1→P2 staging in the #378 analysis and carry non-redundant work. F-9 is decision-only — its acceptance-2 records the auth-model *decision* (the full least-privilege model: `Bearer`, read-only repo/actions/issues/pull-requests, no write scope, token in an env var). F-10 documents and verifies the *provisioned reality* — its acceptance-4 asserts the actual setup carries no committed token — and additionally owns the absent-safe / output-neutrality contract F-9 does not touch. `merge-into F-10` would be wrong: it would collapse the decide-then-document boundary and fuse the auth-model record into the provisioning doc, the same staging the analysis keeps apart. The shared token-handling clause is verified from two distinct angles (the decision states it; the setup proves it), not once redundantly.

## Risks

- **MCP tool-name drift.** The hosted remote endpoint (`api.githubcopilot.com/mcp/`) is a service, not a pinnable binary — its tool catalog is server-side and can change without a local version bump. Mitigation: verify the exact tool names against the live endpoint at implementation time (F-11 / F-12 depend on those names); a self-hosted binary alternative would instead be pinned by image tag + digest.

## Open questions

- **OQ-C (server choice)** — **resolved (2026-07-13)**: GitHub's official MCP server, with the hosted remote endpoint `https://api.githubcopilot.com/mcp/` as the real working reference instance (evidence: the operator's chezmoi-managed `~/.claude.json` `mcpServers.github` entry). The decision stays server-agnostic (self-hosted binary remains a valid substitute).
- **OQ-D (per-operation tool coverage)** — open: some operations (GitHub-App install checks, `gh release edit`) may lack a clean MCP tool and stay on `gh`; the decision records the coverage stance, and the per-artefact detail is confirmed downstream (F-15, F-16).

## References

- Roadmap item R-10 (`project/roadmap.md`).
- Work package P1 in the issue #378 pre-analysis (retired to git history).
- GitHub issue #378; tracking issue #382.
