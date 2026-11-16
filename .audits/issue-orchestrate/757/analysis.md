---
artifact-type: issue-orchestration-analysis
repo: nolte/claude-shared
issue: "757"
classification: feature-request
secondary-classes: []
route: direct
status: approved
created: 2026-11-16
---

# Issue Orchestration — Pre-analysis (#757)

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #757 — name the pillar of each unverified entry in the scanner Health line
- **Labels**: enhancement, nolte-linux
- **Linked items**: none
- **Prior art checked**: no linked or open PR; no `project/features/` entry
- **Requirement gate**: `project/requirements/nolte-linux-plugin.md` `U_gate = 0.80 = τ_high` — met

## Classification

- **Primary class**: feature-request
- **Rationale**: output-shape extension of the scanner and audit report; no defect.
- **Asserted cause verified**: confirmed with drifted line numbers — scanner Health line at `plugins/nolte-linux/agents/linux-image-scanner.md:134` (`Unverified entries relied on: <list or none>`, issue said ~132); audit consumes it at `plugins/nolte-linux/skills/linux-image-audit/SKILL.md:79` and lists it in the report's Health section at `SKILL.md:~108` (issue said ~106).

## Scope

- **In scope**: scanner Health line shape; audit step 7 / report Health shape; any fixture matcher that parses the line.
- **Out of scope**: changing which entries count as relied on.

## Route

- **Decision**: direct — one outcome, one PR strand.

## Work packages

### P1 — Pillar-qualified Health line in scanner and audit

- **Problem statement**: the Health line names §I entries but not the pillar/requirement they back, so §F payload-signature vs §C reproducibility handling is invisible.
- **Acceptance criteria**: (a) scanner output shape: each entry as `§X <requirement>: [Rn] <entry>`, e.g. `§F payload signature: [R23] Mender`; (b) audit SKILL.md step 7 and report Health shape carry the same form; (c) `python3 scripts/validate_skills.py` within token budgets; (d) `pytest tests/e2e/linux_image_audit` green.
- **Touched files**: `plugins/nolte-linux/agents/linux-image-scanner.md`, `plugins/nolte-linux/skills/linux-image-audit/SKILL.md`, possibly `tests/e2e/linux_image_audit/scenario.py`
- **Specialist**: `nolte-claude-dev:claude-plugin-developer`
- **Depends on**: none

## Dependency ordering

P1

## Risks

- Same files as #755 P2 (`linux-image-scanner.md`, different line) — rebase after whichever PR merges first.
- nolte-linux description/body token budgets tight — measured by `validate_skills.py`.

## Open questions

none

## Findings

| Finding | Source | Outcome | Reproduction | Issue |
|---|---|---|---|---|

## Dispatch log
