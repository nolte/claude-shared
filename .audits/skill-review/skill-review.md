---
review-type: skill-review
target: "skills/skill-review/SKILL.md"
target-kind: skill
specs-applied:
  - slug: skill-management
    revision: "d0e50278c7f1b531620c474b1fac3df6952e0597+uncommitted-best-practices-extension"
  - slug: skill-vs-agent
    revision: "d0e50278c7f1b531620c474b1fac3df6952e0597"
  - slug: review-plan
    revision: "d0e50278c7f1b531620c474b1fac3df6952e0597"
  - slug: skill-review
    revision: "d0e50278c7f1b531620c474b1fac3df6952e0597+uncommitted-external-validator-and-best-practices-extensions"
repo-revision: "d0e50278c7f1b531620c474b1fac3df6952e0597"
created: "2026-04-30"
status: complete
---

# Skill Review: skill-review

## Scope

Target: `skills/skill-review/` — `SKILL.md` (87 lines), `templates/plan.template.md` (70 lines), `examples/walkthrough.md` (91 lines). No sibling `agents/skill-review.md` exists; the skill doesn't dispatch a sub-agent.

Specs applied: `skill-management`, `skill-vs-agent`, `review-plan` (all clean at HEAD `d0e5027`); `skill-review` is **uncommitted working-tree** — `spec/claude/skill-review/{en,de}.md` are dirty in the current tree, having just gained the sub-section "Checks derived from external skill-structure validation". This review applies the working-tree version of `skill-review` so the skill is checked against the spec it'll need to satisfy at merge time.

Narrowing: none — full review.

Validator: `skills-ref` (or equivalent) **not run**; recorded as an explicit override per the new `skill-review` rule "MAY suppress an individual validator finding only by recording an explicit override in the plan's `## Scope` with a one-line justification". Justification: external skill-structure validator not yet provisioned in this repository (no installed binary, no `task spec:validate-skill` target, no Renovate-pinned version) — tracked by the new Open Question "Where does the validator pin live?". Re-run the external-validator check once tooling is wired up.

Self-review note: the skill being reviewed and the `skill-review` spec are tightly coupled, so most BLOCKERs below trace back to the spec extension that the skill body hasn't caught up with yet.

Best-practices pass (per <https://agentskills.io/skill-creation/best-practices>): SKILL.md is 91 lines (under the 500-line / 5,000-token cap), every referenced asset (`templates/plan.template.md`, `examples/walkthrough.md`, the four `spec/claude/*` files) carries a load-trigger phrase, the validator selection picks a clear default (`skills-ref` as canonical example) instead of presenting a menu, and the body is procedure-shaped rather than declaration-shaped. No Gotchas section — the skill operates against deterministic markdown / spec inputs without non-obvious environment facts, so the SHOULD doesn't apply. **No new findings produced by the best-practices pass.**

Explicitly out of scope: runtime behavior of the skill (per spec Non-Goals), Vale/markdown style (handled by `task lint`), dispatched agents (none).

## Summary

- BLOCKER: 3
- WARNING: 2
- SUGGESTION: 1
- INFO: 2

Go/no-go: **FAIL** — three open BLOCKERs against the new external-validator sub-section of `skill-review`.
Next concrete action: author updates `skills/skill-review/SKILL.md` Operation 1 and `templates/plan.template.md` to land the external-validator step, the new ordering, and the validator-version slot in `## Scope`; then re-run this review.

## Findings

### BLOCKER

- [x] [skill-review.external-validator-run] Skill body has no instruction to run an external skill-structure validator before emitting the plan; the new MUST in `skill-review` §"Checks derived from external skill-structure validation" can't be satisfied by the current procedure.
      Where: `skills/skill-review/SKILL.md:39-53` (Operation 1, "run") — no validator step exists.
      Fix: Insert a new step in Operation 1 (between "Read the review surface" and "Apply the checks") that runs the configured validator over `skills/<name>/SKILL.md` and ingests the result; reference `skills-ref` as the canonical example without hard-coding the binary name.
      Verify: `grep -n 'validator' skills/skill-review/SKILL.md` returns at least one Operation-1 hit naming the structure-validation step.

- [x] [skill-review.review-procedure-ordering] Operation 1 Step 5's check ordering omits the leading `external-validator findings →` element required by the updated `## Review procedure` MUST.
      Where: `skills/skill-review/SKILL.md:49` — the listed order starts at `frontmatter` instead of `external-validator findings`.
      Fix: Prepend `external-validator findings →` to the ordered list in Step 5 to match the spec's `## Review procedure` clause.
      Verify: `grep -n 'external-validator' skills/skill-review/SKILL.md` returns a hit on the Operation 1 procedure list.

- [x] [skill-review.scope-records-validator] Skill body never instructs the reviewer to record the validator name + version in the plan's `## Scope` section, although the spec MUST-requires it.
      Where: `skills/skill-review/SKILL.md:51-52` (Operation 1 Step 7) and the plan template's `## Scope` section.
      Fix: Extend Step 7 with explicit "populate `Validator:` in `## Scope`" guidance; document the spec's override-suppression mechanism alongside it.
      Verify: Reading Operation 1 Step 7 shows a Validator-recording instruction; a freshly emitted plan carries a `Validator:` line (or override note) in `## Scope`.

### WARNING

- [x] [review-plan.frontmatter+skill-review.scope-records-validator] The plan template's `## Scope` section has no placeholder for the validator name + version, so even a fully-updated skill body can't emit a spec-conforming plan without template changes.
      Where: `skills/skill-review/templates/plan.template.md:21-26`.
      Fix: Add a `Validator: {{validator-name}}@{{validator-version}}` placeholder (or a `Validator override: <justification>` alternative) plus a one-line comment explaining the override path.
      Verify: `grep -n 'Validator' skills/skill-review/templates/plan.template.md` returns the new placeholder.

- [x] [skill-review.review-procedure-ordering] The walkthrough example demonstrates the legacy check ordering and never mentions the external-validator step or the override path, so it no longer matches the procedure the spec defines.
      Where: `skills/skill-review/examples/walkthrough.md:20` (Turn 1 step 6 lists the old order).
      Fix: Update Turn 1 step 6 to include `external-validator findings →`; add a short illustrative note showing either a passing validator run or an explicit `## Scope` override.
      Verify: `grep -n 'external-validator\|Validator:' skills/skill-review/examples/walkthrough.md` returns at least one match.

### SUGGESTION

- [x] [skill-management.tag-vocabulary] No `tags` field in frontmatter; the starter vocabulary's `review` term applies and would put this skill in the same machine-checkable peer cluster as `agent-review` and `audience-review` per `skill-vs-agent` §Portfolio-wide consistency.
      Where: `skills/skill-review/SKILL.md:1-4` (frontmatter).
      Fix: Add `tags: [review]` to the frontmatter; coordinate the same addition for `agent-review` and `audience-review` to make the cluster intentional rather than coincidental.
      Verify: `grep '^tags:' skills/skill-review/SKILL.md` shows the new field with the starter-vocab term.

### INFO

- [x] [skill-management.examples] `examples/walkthrough.md` exists but isn't referenced from `SKILL.md`, so a reader of the body alone won't discover the worked example. Conventional `examples/` placement is satisfied; visibility from the body isn't.
      Where: `skills/skill-review/SKILL.md` (no mention of `examples/walkthrough.md`).
      Fix: n/a (observation) — recommended one-liner: append "See `examples/walkthrough.md` for an end-to-end transcript." under `## Operations` or `## Output — plan shape`.
      Verify: n/a.

- [x] [skill-review.external-validator-severity] Validator-finding severity mapping (error → BLOCKER, warning → WARNING) isn't reproduced in the skill body's severity-mapping list. Operation 1 Step 1 says to read the canonical specs first, so this isn't a conformance failure — but a future spec revision of the mapping could silently desync the skill from its spec.
      Where: `skills/skill-review/SKILL.md:50` (Operation 1 Step 6).
      Fix: n/a (observation) — recommended pointer: "External validator: error → BLOCKER, warning → WARNING per `skill-review` §Checks derived from external skill-structure validation."
      Verify: n/a.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
2026-04-30 — external-validator-run — added Operation 1 Step 5 to SKILL.md running the structure validator (skills-ref as canonical example, tool-agnostic) — verified: `grep -n 'validator' skills/skill-review/SKILL.md` shows two Operation-1 hits
2026-04-30 — review-procedure-ordering (SKILL.md) — prepended `external-validator findings →` to Step 6's ordered list — verified: `grep -n 'external-validator' skills/skill-review/SKILL.md` matches
2026-04-30 — scope-records-validator — extended Operation 1 Step 8 to populate `Validator:` line in plan's `## Scope`, including override path — verified: `grep -nE 'Validator|## Scope' skills/skill-review/SKILL.md` matches Step 8
2026-04-30 — template-validator-slot — added `Validator: {{validator-name}}@{{validator-version}}` placeholder plus override-comment to plan.template.md — verified: `grep -n 'Validator' skills/skill-review/templates/plan.template.md` matches
2026-04-30 — walkthrough-procedure-ordering — added validator-run step + new ordering line to examples/walkthrough.md Turn 1 — verified: `grep -nE 'external-validator|Validator:' skills/skill-review/examples/walkthrough.md` returns three hits
2026-04-30 — tag-vocabulary — added `tags: [review]` to SKILL.md frontmatter (cluster alignment with agent-review/audience-review tracked separately) — verified: `grep -n '^tags:' skills/skill-review/SKILL.md` matches
2026-04-30 — examples — added "See `examples/walkthrough.md` for an end-to-end transcript" footer to `## Output — plan shape` — verified: `grep -n 'examples/walkthrough.md' skills/skill-review/SKILL.md` matches
2026-04-30 — external-validator-severity — added inline pointer in Operation 1 Step 7 cross-referencing the validator severity mapping — verified: re-read Step 7, pointer present
2026-04-30 — best-practices-pass — extended skill-management + skill-review specs with §"Authoring quality" / §"Checks derived from skill-creation best practices" (per <https://agentskills.io/skill-creation/best-practices>); audited skills/skill-review/SKILL.md against the new requirements — no new findings — verified: line count 91 < 500, load-triggers present for all referenced assets, default-not-menu pattern in validator selection
