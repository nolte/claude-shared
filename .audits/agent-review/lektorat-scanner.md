---
review-type: agent-review
target: "agents/lektorat-scanner.md"
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

# Agent Review: lektorat-scanner

## Scope

Target: `agents/lektorat-scanner.md` (frontmatter + full body; referenced assets `scripts/readability_lix.py`, `spec/project/lektorat/calque-de.yml`, `spec/project/lektorat/protected-terms-de.yml` all resolve on disk).
Specs applied: `agent-management`, `skill-vs-agent`, `review-plan`, `agent-review` (revisions recorded in frontmatter).
Narrowing: none — full review in the `agent-review` §Review procedure order (frontmatter → description/triggers → distribution → model → tools/scope → prompt structure → rationale → referenced assets → duplicate-prevention → Info).
Tool-use convention applied: a declared tool counts as used when the body names it in a procedure step or states it as the working method; a tool never named anywhere in the body is recorded as dead permission per `agent-review` §Tool-scope checks.
Model-form rule applied at the widened revision — alias, full model ID, and `inherit` are all conformant.
Explicitly out of scope: runtime behaviour of the agent, Vale/markdown style (agent files aren't Vale-gated), and the dispatching skill's own conformance.
Read-only classification: read-only (scanner, detection only), so `Bash` is assessed under the narrow exception.
Model check: `model: sonnet` is declared and justified.
Lowercase severity tokens (`critical`/`warning`/`suggestion`) are conformant here — `spec/project/lektorat/` is named in `review-plan` §Editorial sub-scale carve-out.

## Summary

- Critical: 0
- Warning: 2
- Suggestion: 0
- Info: 1

Go/no-go: PASS — no Critical findings.
Next concrete action: Name the network-read class in the Bash justification; defer the body-length Warning.

## Findings

### Warning

- [ ] [agent-management.Tool access] `## Read-only Bash justification` frames every listed command as side-effect-free, but the pinned DE pipeline may resolve to an HTTP endpoint (the output contract's `de.configured_path` explicitly allows "HTTP endpoint URL (Public or self-hosted)"), which is the network-read class of §Sanctioned command classes and must be named with its bound.
      Where: `agents/lektorat-scanner.md:44-54` (justification) against `agents/lektorat-scanner.md:166` (the `de` pipeline `configured_path`).
      Fix: Add one sentence naming the network-read class for the DE pipeline endpoint and stating the bound (read-only request, never a mutating call, never a write to remote state).
      Verify: The justification section names the network-read class; a class the section doesn't list stays forbidden.
- [ ] [agent-management.Recommendations] System-prompt body is 223 lines, past the ~200-line soft target.
      Where: `agents/lektorat-scanner.md:27-249`.
      Fix: Tighten prose — the D1-D6 detection sections and `## Hard rules` restate the same closed vocabularies.
      Verify: Body line count is at or near 200.
      → deferred: <https://github.com/nolte/claude-shared/issues/460> (the per-dimension detection prose is the agent's behavioural contract against `spec/project/lektorat/`; trimming it is a content decision, not a mechanical edit)

### Info

- [ ] [agent-management.Tool access] `Bash` on a read-only agent, downgraded from Critical to Info because the narrow exception is satisfied.
      Where: `agents/lektorat-scanner.md:5` and `## Read-only Bash justification` at lines 42-54.
      Fix: n/a (observation) — Vale, the LIX reference script, and the `git ls-files` / `git rev-parse` reads are all named explicitly.
      Verify: n/a.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
