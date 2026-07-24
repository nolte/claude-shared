---
review-type: agent-review
target: "agents/docs-freshness-checker.md"
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

# Agent Review: docs-freshness-checker

## Scope

Target: `agents/docs-freshness-checker.md` (frontmatter + full body; the referenced `scripts/check_links.py` resolves on disk).
Specs applied: `agent-management`, `skill-vs-agent`, `review-plan`, `agent-review` (revisions recorded in frontmatter).
Narrowing: none — full review in the `agent-review` §Review procedure order (frontmatter → description/triggers → distribution → model → tools/scope → prompt structure → rationale → referenced assets → duplicate-prevention → Info).
Tool-use convention applied: a declared tool counts as used when the body names it in a procedure step or states it as the working method; a tool never named anywhere in the body is recorded as dead permission per `agent-review` §Tool-scope checks.
Model-form rule applied at the widened revision — alias, full model ID, and `inherit` are all conformant.
Explicitly out of scope: runtime behaviour of the agent, Vale/markdown style (agent files aren't Vale-gated), and the dispatching skill's own conformance.
Read-only classification: read-only (audit), so `Bash` is assessed under the narrow exception.
Model check: `model: sonnet` is declared and justified.

## Summary

- Critical: 0
- Warning: 1
- Suggestion: 0
- Info: 3

Go/no-go: PASS — no Critical findings; the single Warning is a body-length SHOULD.
Next concrete action: Body-length Warning deferred to #460; no rework needed on this agent.

## Findings

### Warning

- [ ] [agent-management.Recommendations] System-prompt body is 316 lines, the longest in the `nolte-shared` agent surface and well past the ~200-line soft target.
      Where: `agents/docs-freshness-checker.md:26-340`.
      Fix: Tighten prose — the `## Output shape` template alone runs ~115 lines and the eight working-procedure phases restate the categories it already enumerates.
      Verify: Body line count is at or near 200.
      → deferred: <https://github.com/nolte/claude-shared/issues/460> (the output template is the report contract downstream consumers read, and the phase prose carries the per-category detection rules; trimming both is a content decision that deserves its own change)

### Info

- [ ] [agent-management.Tool access] `Bash` on a read-only agent, downgraded from Critical to Info because the narrow exception is satisfied.
      Where: `agents/docs-freshness-checker.md:5` and `## Read-only Bash justification` at lines 30-42.
      Fix: n/a (observation) — the section enumerates the git reads plus the `--offline` link-checker delegation.
      Verify: n/a.
- [ ] [review-plan.Editorial sub-scale carve-out] The lowercase severity tokens in the classification phase are conformant, not drift — `spec/project/docs-freshness/` is named in the carve-out with exactly the `critical`/`warning`/`info` subset this agent uses.
      Where: `agents/docs-freshness-checker.md:322-326` (`### Phase 8`) against `review-plan` §Editorial sub-scale carve-out.
      Fix: n/a (observation) — the report's own headings and Summary table already use the Title-Case labels.
      Verify: n/a.
- [ ] [review-plan.Editorial sub-scale carve-out] The Summary table's omission of a `Suggestion` column is likewise sanctioned — the carve-out lets a named spec omit the levels its tool never emits.
      Where: `agents/docs-freshness-checker.md:97-110`.
      Fix: n/a (observation).
      Verify: n/a.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
