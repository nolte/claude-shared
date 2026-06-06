---
review-type: skill-review
target: "skills/license-check/SKILL.md"
target-kind: skill
specs-applied:
  - slug: skill-management
    revision: "467439f"
  - slug: skill-vs-agent
    revision: "b91b67b"
  - slug: review-plan
    revision: "ea7a5e1"
  - slug: skill-review
    revision: "ea7a5e1"
repo-revision: "b311e01"
created: "2026-06-05"
status: in-progress
---

# Skill Review: license-check

## Scope

Target: `skills/license-check/` (`SKILL.md`, 177 lines; no `references/` / `templates/` / `assets/` / `scripts/` / `examples/` — no relative asset references).
Specs applied: `skill-management`, `skill-vs-agent`, `review-plan`, `skill-review` (revisions in frontmatter).
Validator: override — `skills-ref` is not provisioned in this repository; the Taskfile `validate:skills` target (`scripts/validate_skills.py`) is the named `skills-ref` stop-gap per `skill-review` §"Checks derived from external skill-structure validation", and it ran clean for this skill (no errors, no warnings).
Narrowing: none (full review).
Companion agent: the skill dispatches `license-check-scanner`; a separate `agent-review` is being run against it in the same session.
Explicitly out of scope: runtime behavior of the skill, Vale/markdown style (handled by `task lint`), the dispatched agent beyond confirming the orchestration direction.

## Summary

- Critical: 0
- Warning: 1
- Suggestion: 1
- Info: 2

Go/no-go: PASS — no `Critical`; the single `Warning` is a documented, by-design capability split, not an unresolved collision.
Next concrete action: author decides whether to add `examples/` evaluation scenarios (Suggestion) before or after merge; the Warning is already mitigated by the spec-level authority/implementer split.

## Findings

### Warning

- [ ] [skill-vs-agent.duplicate-prevention] Capability overlap with `dependency-audit`, whose `description` advertises a license-compliance pass over the dependency tree.
      Where: `skills/license-check/SKILL.md` frontmatter `description` vs. `skills/dependency-audit/SKILL.md` `description`.
      Fix: none required — the overlap is deliberate and already split: `spec/project/license-check/` §Delimitation makes `license-check` the policy authority and frames `dependency-audit`'s license pass as the implementer for the dependency slice, and both descriptions encode the split (`license-check` says "Don't use for CVE… that's dependency-audit"; `dependency-audit` §License audit now defers classification/policy to `license-check`). Confirm the split reads clearly to a new reader; no merge or rename.
      Verify: `grep -i "license" skills/dependency-audit/SKILL.md` shows its license pass scoped to dependencies and deferring policy; `license-check` owns own-code + AI-provenance + the policy gate.

### Suggestion

- [x] [skill-review.evaluation-discipline] No `examples/` evaluation scenarios (the spec SHOULDs at least three input/expected-behavior scenarios; absence is a `Suggestion` for a new skill).
      Where: `skills/license-check/` has no `examples/` folder (sibling `dependency-audit` ships `examples/01..03`).
      Fix: add at least three scenarios under `skills/license-check/examples/` (for example: a permissive Python repo that passes; a repo with a transitive MPL-2.0 finding routed to `review`; a conveyed GPL component that is `deny`), each as a `Read examples/NN-… when …` load-triggered reference.
      Verify: `ls skills/license-check/examples/` lists ≥3 scenario files, each referenced with a load-trigger phrase in `SKILL.md`.

### Info

- [ ] [skill-vs-agent.rationale-counter-dimension] The rationale section names four positive skill dimensions plus a hybrid split; the counter-dimension (the read-only scan is agent-shaped) is acknowledged via the hybrid split rather than a standalone "an agent could…" sentence.
      Where: `SKILL.md` §"Why this is a skill, not an agent" (Hybrid split bullet).
      Fix: n/a (observation) — the SHOULD counter-dimension is satisfied by the hybrid-split acknowledgement; a future edit may make it an explicit one-liner if desired.
      Verify: n/a.
- [ ] [skill-management.frontmatter-description-length] `description` is 976 / 1024 characters — valid but near the platform cap; a future trigger-phrase addition could push it over.
      Where: `SKILL.md` frontmatter `description`.
      Fix: n/a (observation) — within limit; trim a clause if a future edit needs headroom.
      Verify: n/a.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
2026-06-05 — examples-evaluation-discipline — added three load-triggered scenarios under skills/license-check/examples/ (permissive pass, transitive MPL-2.0 review, conveyed GPL deny) and referenced them with "Read examples/NN-… when …" phrases in SKILL.md §Examples — verified: ls skills/license-check/examples/ shows 3 files, each referenced with a load-trigger phrase
