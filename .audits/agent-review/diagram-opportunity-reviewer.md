---
review-type: agent-review
target: "agents/diagram-opportunity-reviewer.md"
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

# Agent Review: diagram-opportunity-reviewer

## Scope

Target: `agents/diagram-opportunity-reviewer.md` (frontmatter + full body; no external referenced assets).
Specs applied: `agent-management`, `skill-vs-agent`, `review-plan`, `agent-review` (revisions recorded in frontmatter).
Narrowing: none — full review in the `agent-review` §Review procedure order (frontmatter → description/triggers → distribution → model → tools/scope → prompt structure → rationale → referenced assets → duplicate-prevention → Info).
Tool-use convention applied: a declared tool counts as used when the body names it in a procedure step or states it as the working method; a tool never named anywhere in the body is recorded as dead permission per `agent-review` §Tool-scope checks.
Model-form rule applied at the widened revision — alias, full model ID, and `inherit` are all conformant.
Explicitly out of scope: runtime behaviour of the agent, Vale/markdown style (agent files aren't Vale-gated), and the dispatching skill's own conformance.
Read-only classification: read-only (prose scanner), so `Bash` is assessed under the narrow exception.
Lowercase severity tokens (`suggestion`/`info`) are conformant here — `spec/project/diagram-opportunity/` is named in `review-plan` §Editorial sub-scale carve-out.
Model check: `model` absent — the agent inherits the caller's model; the MAY-Info wasn't raised.

## Summary

- Critical: 0
- Warning: 2
- Suggestion: 0
- Info: 1

Go/no-go: PASS — no Critical findings.
Next concrete action: Name `Grep` at the marker-recognition step; defer the body-length Warning.

## Findings

### Warning

- [ ] [agent-review.Tool-scope checks] `Grep` is declared but never named in any procedure step — scope resolution is attributed to `Glob` / `Read` / `git ls-files`, so the declaration reads as dead permission.
      Where: `agents/diagram-opportunity-reviewer.md:5` (declaration) against `:75` (scope expansion) and `:166-167` (`### Marker recognition rules`).
      Fix: Name `Grep` at the mute-marker recognition step, which is the case-sensitive prefix scan the tool actually performs.
      Verify: The body names `Grep` in a procedure step, so the declared-vs-used check passes in both directions.
- [ ] [agent-management.Recommendations] System-prompt body is 297 lines, past the ~200-line soft target.
      Where: `agents/diagram-opportunity-reviewer.md:24-319`.
      Fix: Tighten prose — the trigger catalog, the confidence model, and the mute-marker handling each restate rules the authorizing spec already owns.
      Verify: Body line count is at or near 200.
      → deferred: <https://github.com/nolte/claude-shared/issues/460> (the catalog and confidence rules are the agent's deterministic contract with `spec/project/diagram-opportunity/`; trimming them changes detection behaviour)

### Info

- [ ] [agent-management.Tool access] `Bash` on a read-only agent, downgraded from Critical to Info because the narrow exception is satisfied.
      Where: `agents/diagram-opportunity-reviewer.md:5` and `## Read-only Bash justification` at lines 40-48.
      Fix: n/a (observation) — the section names the `git ls-files` / `git rev-parse` subset and forbids mutation.
      Verify: n/a.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
