---
review-type: agent-review
target: "agents/link-rot-scanner.md"
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

# Agent Review: link-rot-scanner

## Scope

Target: `agents/link-rot-scanner.md` (frontmatter + full body; the referenced `scripts/check_links.py` resolves on disk).
Specs applied: `agent-management`, `skill-vs-agent`, `review-plan`, `agent-review` (revisions recorded in frontmatter).
Narrowing: none — full review in the `agent-review` §Review procedure order (frontmatter → description/triggers → distribution → model → tools/scope → prompt structure → rationale → referenced assets → duplicate-prevention → Info).
Tool-use convention applied: a declared tool counts as used when the body names it in a procedure step or states it as the working method; a tool never named anywhere in the body is recorded as dead permission per `agent-review` §Tool-scope checks.
Model-form rule applied at the widened revision — alias, full model ID, and `inherit` are all conformant.
Explicitly out of scope: runtime behaviour of the agent, Vale/markdown style (agent files aren't Vale-gated), and the dispatching skill's own conformance.
Read-only classification: read-only (audit), so `Bash` is assessed under the narrow exception.
Tool-use: `Read` is exercised implicitly by the Precondition-3 checker-reachability resolution — with only `Read` and `Bash` declared, that step is a `Read`, so the declared-vs-used check passes.
Model check: `model: sonnet` is declared and justified.

## Summary

- Critical: 0
- Warning: 0
- Suggestion: 0
- Info: 2

Go/no-go: PASS — no Critical, Warning, or Suggestion findings.
Next concrete action: No rework required; close the plan.

## Findings

### Info

- [ ] [agent-management.Tool access] `Bash` on a read-only agent, downgraded from Critical to Info because the narrow exception is satisfied, including the network-read class.
      Where: `agents/link-rot-scanner.md:5` and `## Read-only Bash justification` at lines 33-45.
      Fix: n/a (observation) — the section names the checker's HTTP `HEAD`/`GET` probes as side-effect-free reads and forbids every mutating call, matching the §Sanctioned command classes network-read clause.
      Verify: n/a.
- [ ] [review-plan.Editorial sub-scale carve-out] The lowercase severity tokens in the triage phase are the checker's own JSON values, not report labels — the report's Summary table and section headings use Title Case; `spec/project/link-validation/` isn't in the carve-out list, so the spec may need to grow to cover this checker's wire vocabulary.
      Where: `agents/link-rot-scanner.md:102-107` (`### Phase 2`) against `:131-138` (the Title-Case report shape).
      Fix: n/a (observation) — recorded so a future `review-plan` revision can decide whether `link-validation` joins the carve-out.
      Verify: n/a.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
