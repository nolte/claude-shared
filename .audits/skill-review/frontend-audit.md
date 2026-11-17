---
review-type: skill-review
target: "plugins/nolte-engineering/skills/frontend-audit/SKILL.md"
target-kind: skill
specs-applied:
  - slug: skill-management
    revision: "4ceb6872"
  - slug: skill-vs-agent
    revision: "66d65137"
  - slug: review-plan
    revision: "7be3b552"
  - slug: skill-review
    revision: "27cbff13"
repo-revision: "152a3565"
created: "2026-11-17"
status: complete
---

# Skill Review: frontend-audit

## Scope

Target: `plugins/nolte-engineering/skills/frontend-audit/` (`SKILL.md`, 86 lines, ~1,710 body tokens; `references/spec/third-party-audit-skills.md` and `.de.md`, bundled copies of `spec/frontend/third-party-audit-skills/`).
Specs applied: `skill-management`, `skill-vs-agent`, `review-plan`, `skill-review` (revisions recorded in frontmatter).
Validator: override — `skills-ref` is not provisioned in this repository (`which skills-ref` returns nothing); `scripts/validate_skills.py` ran in its place and reported no finding for this skill. Checks that only `skills-ref` performs remain uncovered.
Narrowing: none.
Companion agent-review: not triggered. The dispatched agents `frontend-code-reviewer` and `webview-ui-expert` received only an additive input paragraph in this change (the delegated/fallback rule list); their frontmatter and contracts are unchanged.
Explicitly out of scope: runtime behavior of the skill, Vale/markdown style (handled by `task lint`), dispatched agents beyond confirming the orchestration direction.

## Summary

- Critical: 0
- Warning: 2
- Suggestion: 1
- Info: 1

Go/no-go: CONDITIONAL — both Warnings resolved before merge
Next concrete action: align spec §I with the skill's resume-state writes, and disambiguate the `webview-ui-optimize` trigger "audit the frontend".

## Findings

### Critical

(none)

### Warning

- [x] [skill-review.restated-rule-matches-spec] The skill writes resume state under `.resume/frontend-audit/`, but spec §I allows no write apart from the report file.
      Where: `SKILL.md` §Hard rules ("Never write outside `.audits/frontend-audit/` and `.resume/frontend-audit/`") vs `spec/frontend/third-party-audit-skills/en.md` §I.
      Fix: extend spec §I (EN + DE + bundled copies) to permit the run's resume state under `.resume/frontend-audit/`.
      Verify: `grep -n "resume" spec/frontend/third-party-audit-skills/en.md` shows the allowance in §I; bundled copies are byte-identical.
- [x] [skill-review.duplicate-capability] `webview-ui-optimize` lists the bare trigger "audit the frontend", which also matches this skill's purpose; routing between the two is ambiguous.
      Where: `plugins/nolte-engineering/skills/webview-ui-optimize/SKILL.md:3` (description trigger list).
      Fix: narrow the peer trigger to "audit the frontend against the webview-ui spec rules", keeping its description under 1024 characters.
      Verify: `git grep -n '"audit the frontend\\"' plugins/` returns no bare trigger; `scripts/validate_skills.py` stays clean.

### Suggestion

- [x] [skill-review.evaluation-scenarios] The skill ships no `examples/` with at least three evaluation scenarios.
      Where: `plugins/nolte-engineering/skills/frontend-audit/`.
      Fix: add three scenarios (all skills available with URL; `react-best-practices` missing; non-React app without URL).
      Verify: `ls plugins/nolte-engineering/skills/frontend-audit/examples/` lists three files, each with input, preconditions, expected report header.

### Info

- [x] [skill-review.observation] Procedure step 6 re-fetches the guidelines URL with `curl` to hash it when the skill doesn't expose the fetched text; the two fetches can in principle differ if upstream changes between them. Spec §E doesn't settle how the hash is obtained, so the spec may need to grow.
      Where: `SKILL.md` §Procedure step 6.
      Fix: n/a (observation).
      Verify: n/a.

## Processing log

2026-11-17 — W1 resume-state — spec §I (EN+DE+bundled) permits `.resume/frontend-audit/` — verified: grep §I + cmp bundled copies
2026-11-17 — W2 trigger overlap — webview-ui-optimize trigger narrowed to "audit the frontend against the webview-ui spec rules" (desc 968 chars) — verified: validate_skills.py clean
2026-11-17 — S1 examples — added examples/01–03 with load-trigger lines in SKILL.md §Examples — verified: ls examples/ (3 files)
2026-11-17 — I1 hash re-fetch — recorded as Open Question in spec (EN+DE+bundled) — verified: grep "second time" spec
