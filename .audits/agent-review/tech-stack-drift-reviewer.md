---
review-type: agent-review
target: "agents/tech-stack-drift-reviewer.md"
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

# Agent Review: tech-stack-drift-reviewer

## Scope

Target: `agents/tech-stack-drift-reviewer.md` (frontmatter + full body; no external referenced assets).
Specs applied: `agent-management`, `skill-vs-agent`, `review-plan`, `agent-review` (revisions recorded in frontmatter).
Narrowing: none — full review in the `agent-review` §Review procedure order (frontmatter → description/triggers → distribution → model → tools/scope → prompt structure → rationale → referenced assets → duplicate-prevention → Info).
Tool-use convention applied: a declared tool counts as used when the body names it in a procedure step or states it as the working method; a tool never named anywhere in the body is recorded as dead permission per `agent-review` §Tool-scope checks.
Model-form rule applied at the widened revision — alias, full model ID, and `inherit` are all conformant.
Explicitly out of scope: runtime behaviour of the agent, Vale/markdown style (agent files aren't Vale-gated), and the dispatching skill's own conformance.
Read-only classification: read-only; no `Bash`, no write tools — the read-only invariant holds by construction.
Model check: `model` absent, so the agent inherits the caller's model per `agent-management` §Model selection; the MAY-Info wasn't raised.

## Summary

- Critical: 0
- Warning: 1
- Suggestion: 0
- Info: 1

Go/no-go: PASS — no Critical findings.
Next concrete action: Name `Grep` at the procedure step that performs the content search.

## Findings

### Warning

- [ ] [agent-review.Tool-scope checks] `Grep` is declared but never named in any procedure step; `## Preconditions` even says the agent verifies "using `Read` and `Glob` only", so the declaration reads as dead permission.
      Where: `agents/tech-stack-drift-reviewer.md:5` (declaration) against `agents/tech-stack-drift-reviewer.md:118` and `:148-158` (Surface 3, where the on-disk signal search actually happens).
      Fix: Name `Grep` in Surface 3, where declared entries are matched against in-file signals such as `[tool.uv]` in `pyproject.toml`.
      Verify: The body names `Grep` in a procedure step, so the declared-vs-used check passes in both directions.

### Info

- [ ] [agent-management.Description contract] The reverse delimitation against `tech-stack-fitness-reviewer` is absent from `description` but deliberately so — the peer carries it, and the spec's tight-chain SHOULD prefers a single cross-reference over a fourth enumerated entry.
      Where: `agents/tech-stack-drift-reviewer.md:3` and the peer at `agents/tech-stack-fitness-reviewer.md:3`.
      Fix: n/a (deliberate design) — `see_also` and the peer's own `description` already route the reader.
      Verify: n/a.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
