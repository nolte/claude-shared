# Example 01 — Full-scope quarterly audit (2026-Q2)

## Trigger phrase

> "Run the quarterly spec-drift audit for Q2 2026."

## Context

Repository: `claude-shared`, branch `develop`, revision `b1b4d0b`.
Date: 2026-05-20. Quarter: Q2 (April–June 2026).

---

## Session transcript

**User:** Run the quarterly spec-drift audit for Q2 2026.

**Skill (step 1 — scope confirmation):**

Confirmed trigger: quarterly full-scope audit.
Reading `spec/.spec-config.yml` → `canonical_language: en`.

Collecting in-scope specs (non-empty Requirements or AC sections):
- `spec/project/spec-drift-audit/en.md`
- `spec/project/pull-request-workflow/en.md`
- `spec/project/project-structure/en.md`
- `spec/claude/skill-management/en.md`
- `spec/claude/skill-vs-agent/en.md`
- `spec/claude/skill-review/en.md`
- `spec/claude/agent-review/en.md`
- `spec/project/prose-style/en.md`

Git revision: `git rev-parse HEAD` → `b1b4d0b3f9c1a2d4e8f05b6c7d9e0f1a2b3c4d5e`

Shall I proceed with this scope and dispatch the partial auditors?

**User:** Yes, proceed.

---

**Skill (step 4 — partial auditors):**

Running `project-structure-apply` (audit-only)…

```
project-structure-apply findings:
  PASS  .github/settings.yml — boring-cyborg extends pointer present
  PASS  Renovate config extends portfolio preset
  FAIL  .github/ISSUE_TEMPLATE/ — missing feature-request.yml (required by project-structure §Issue templates)
  PASS  Taskfile.yml — task lint, task test, task docs present
  PASS  MkDocs config present and valid
```

Running `vocab-drift-audit`…

```
vocab-drift-audit findings:
  Duplicates to remove: 2 entries already upstream at nolte/vale-style@v0.1.9
    - styles/config/vocabularies/technical/accept.txt: "hotfix"
    - styles/config/vocabularies/technical/accept.txt: "subagent"
  Upstream PR candidates: 0
  Health: pin is current (v0.1.9 = latest)
```

Running `task lint`…

```
task lint: all pre-commit hooks passed (0 errors)
```

---

**Skill (step 5 — per-criterion check):**

Remaining spec criteria evaluated manually:

| Spec | Criterion | Result | Notes |
|------|-----------|--------|-------|
| `spec/project/spec-drift-audit/` | AC1: traceable audit history ≥1/quarter | pass | `docs/audits/` has entries for 2026-Q1 |
| `spec/project/spec-drift-audit/` | AC3: no undecided fail findings | pass | prior audit closed cleanly |
| `spec/project/pull-request-workflow/` | AC: PR title follows Conventional Commits | pass | recent PRs conform |
| `spec/project/project-structure/` | AC: ISSUE_TEMPLATE/ complete | fail | see F1 |
| `spec/claude/skill-management/` | AC: every skill has phase field | fail | see F2 |
| `spec/project/prose-style/` | AC: local vocab duplicates removed after pin bump | fail | see F3 |

---

**Skill (step 6–7 — artifact):**

Writing `docs/audits/2026-Q2.md`…

```markdown
---
audit-type: spec-drift-audit
repo-revision: b1b4d0b3f9c1a2d4e8f05b6c7d9e0f1a2b3c4d5e
created: 2026-05-20
scope: full
triggers:
  - quarterly
tools-used:
  - project-structure-apply@develop-b1b4d0b
  - vocab-drift-audit@develop-b1b4d0b
  - task lint (0 errors)
status: open
---

# Spec Drift Audit — 2026-Q2

## Findings

### F1 — Missing feature-request.yml in ISSUE_TEMPLATE
Spec: spec/project/project-structure/en.md §Issue templates
Result: fail
Observed: .github/ISSUE_TEMPLATE/ has bug.yml only
Expected: feature-request.yml required per project-structure AC

### F2 — Skills missing `phase` frontmatter field
Spec: spec/claude/skill-management/en.md §Structure
Result: fail
Observed: plugins/nolte-planning/skills/roadmap-init/SKILL.md has no `phase` field
Expected: every skill declares phase from the eight-value vocabulary

### F3 — Local vocab duplicates not removed post pin-bump
Spec: spec/project/prose-style/en.md §Vocabulary maintenance
Result: fail
Observed: 2 entries in accept.txt already accepted upstream at v0.1.9
Expected: local duplicates removed once upstream accepts the term
```

Artifact written. Ready to commit? (Confirm to stage `docs/audits/2026-Q2.md`.)

**User:** Yes, commit it.

**Skill:** Staged and committed: `chore(audit): open 2026-Q2 spec-drift audit — 3 findings`
