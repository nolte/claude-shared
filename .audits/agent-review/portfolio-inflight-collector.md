---
review-type: agent-review
target: "agents/portfolio-inflight-collector.md"
target-kind: agent
specs-applied:
  - slug: agent-management
    revision: "92086e1803ec5667da892807749636461de55b39"
  - slug: skill-vs-agent
    revision: "92086e1803ec5667da892807749636461de55b39"
  - slug: review-plan
    revision: "e75ffbbafaf33cd55ae46dda966894add3ae01e4"
  - slug: agent-review
    revision: "e75ffbbafaf33cd55ae46dda966894add3ae01e4"
repo-revision: "e75ffbbafaf33cd55ae46dda966894add3ae01e4"
created: "2026-07-24"
status: open
---

# Agent Review: portfolio-inflight-collector

## Scope

Target: `agents/portfolio-inflight-collector.md` (frontmatter + full body; no external referenced assets).
Specs applied: `agent-management`, `skill-vs-agent`, `review-plan`, `agent-review` (revisions recorded in frontmatter).
Narrowing: none — full review in the `agent-review` §Review procedure order (frontmatter → description/triggers → distribution → model → tools/scope → prompt structure → rationale → referenced assets → duplicate-prevention → Info).
Tool-use convention applied: a declared tool counts as used when the body names it in a procedure step or states it as the working method; a tool never named anywhere in the body is recorded as dead permission per `agent-review` §Tool-scope checks.
Model-form rule applied at the widened revision — alias, full model ID, and `inherit` are all conformant.
Explicitly out of scope: runtime behaviour of the agent, Vale/markdown style (agent files aren't Vale-gated), and the dispatching skill's own conformance.
Read-only classification: read-only (collector, detection only), so the read-only tool bans apply and `Bash` is assessed under the narrow exception.
Model check: `model: sonnet` is declared and justified.
MCP tools (`mcp__github__*`) are read-only GitHub reads; the spec's network-read section names `WebSearch`/`WebFetch` only, so no `## Network-read justification` is required here.

## Summary

- Critical: 0
- Warning: 2
- Suggestion: 0
- Info: 1

Go/no-go: PASS — no Critical findings.
Next concrete action: Add the missing negative trigger to `description`; defer the body-length Warning.

## Findings

### Warning

- [ ] [agent-management.Description contract] `description` carries no negative trigger even though the sibling `portfolio-manifest-collector` is a plausible-overlap peer (both are read-only nolte-portfolio collectors dispatched by a portfolio skill).
      Where: `agents/portfolio-inflight-collector.md:3`.
      Fix: Replace the redundant trailing `Writes nothing.` (already implied by the leading "Read-only") with a `Don't use for …` cross-reference to `portfolio-manifest-collector`.
      Verify: `description` names the peer; the change is token-neutral against the routing budget.
- [ ] [agent-management.Recommendations] System-prompt body is 265 lines, past the ~200-line soft target.
      Where: `agents/portfolio-inflight-collector.md:21-284`.
      Fix: Tighten prose — `## Hard rules` restates `## Scope and boundaries` "does not" almost item for item.
      Verify: Body line count is at or near 200.
      → deferred: <https://github.com/nolte/claude-shared/issues/460> (same class as the other body-length findings in this batch; the `## Read-only Bash justification` allow-list and the `## Output shape` template are both contract surfaces a bulk trim would put at risk)

### Info

- [ ] [agent-management.Tool access] `Bash` on a read-only agent, downgraded from Critical to Info because the narrow exception is satisfied.
      Where: `agents/portfolio-inflight-collector.md:5` and `## Read-only Bash justification` at lines 35-52.
      Fix: n/a (observation) — the section enumerates the exact read-only `gh` allow-list and forbids every mutating verb.
      Verify: n/a.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
