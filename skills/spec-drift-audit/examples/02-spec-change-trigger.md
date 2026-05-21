# Example 02 — Thematic partial audit triggered by a spec change

## Trigger phrase

> "The pull-request-workflow spec just got a new MUST rule. Trigger the matching partial spec-drift audit."

## Context

Repository: `claude-shared`, branch `develop`.
Trigger: PR #119 added `§Parallel-working-copies MUST rule` to `spec/project/pull-request-workflow/en.md`.
Scope: thematic — pull-request-workflow only.

---

## Session transcript

**User:** The pull-request-workflow spec just got a new MUST rule in PR #119. Trigger the matching partial spec-drift audit.

**Skill (step 1 — scope confirmation):**

Detected trigger: spec-change.
Triggering spec: `spec/project/pull-request-workflow/en.md` (changed in PR #119).
Proposed thematic scope: pull-request-workflow criteria only.

Reading `spec/.spec-config.yml` → `canonical_language: en`.
Git revision: `git rev-parse HEAD` → `c7dc927a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e`

Narrowing rationale: "thematic audit triggered by spec-change:pull-request-workflow in PR #119 — only pull-request-workflow criteria evaluated."

Shall I proceed with this scope?

**User:** Yes.

---

**Skill (step 3–5 — criteria evaluation):**

Loading `spec/project/pull-request-workflow/en.md` — reading all Acceptance Criteria.

New MUST rule from PR #119:
> "Feature branches MUST be rebased on develop (not merged) before opening a PR; the branch MAY diverge by at most 5 commits from the develop tip."

Checking implementation surface:
- `.github/PULL_REQUEST_TEMPLATE.md` — no divergence check mentioned.
- `skills/pull-request-create/SKILL.md` — step 3 checks "branch is synchronized with develop" but does not enforce the 5-commit divergence cap.
- `.github/workflows/ci.yml` — no divergence enforcement.

Result: `fail` — new MUST rule not yet implemented in the skill or enforced in CI.

Other pull-request-workflow criteria (previously passing): re-checked → all `pass`.

---

**Skill (step 6–7 — artifact):**

Writing `docs/audits/2026-Q2-pull-request-workflow.md`…

```markdown
---
audit-type: spec-drift-audit
repo-revision: c7dc927a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e
created: 2026-05-20
scope: thematic:pull-request-workflow
triggers:
  - spec-change:pull-request-workflow (PR #119)
tools-used:
  - task lint (0 errors)
status: open
---

# Spec Drift Audit — 2026-Q2 — pull-request-workflow

## Scope

Trigger: spec-change triggered by PR #119 adding §Parallel-working-copies MUST rule.
Narrowing: pull-request-workflow spec criteria only. Full-scope Q2 audit runs separately.

## Per-criterion results

| Spec | Criterion | Result | Notes |
|------|-----------|--------|-------|
| pull-request-workflow | New MUST: 5-commit divergence cap enforced | fail | F1 |
| pull-request-workflow | PR title: Conventional Commits format | pass | |
| pull-request-workflow | PR body: five-section structure | pass | |
| pull-request-workflow | Branch synchronized with develop before PR | pass | skill checks this |

## Findings

### F1 — 5-commit divergence cap not enforced

Spec: spec/project/pull-request-workflow/en.md §Parallel-working-copies
Criterion: Feature branches MAY diverge by at most 5 commits from develop tip; enforced before PR open.
Result: fail
Observed: pull-request-create skill checks "branch synchronized" (rebase done) but does not count or cap commits ahead of develop.
Expected: skill or CI gate rejects PRs with >5 commits ahead of develop tip.
Severity: standard
```

Artifact written at `docs/audits/2026-Q2-pull-request-workflow.md`.
Commit? (Confirm to stage.)

**User:** Yes.

**Skill:** Staged and committed: `chore(audit): open 2026-Q2-pull-request-workflow thematic spec-drift audit — 1 finding`
