---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "812"
classification: "bug"
secondary-classes: ["refactor"]
route: "direct"
status: approved
created: "2026-11-23"
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #812 — pull-request-merge-order: follow-ups from the final review round of #811
- **URL**: https://github.com/nolte/claude-shared/issues/812
- **Labels**: enhancement, skills
- **Linked items**: Refs #811 (merged 5cba4dc4); no PR references #812 (`gh pr list --state all --search "812 in:body"` → empty)
- **Prior art checked**: no `project/requirements/` artifact for merge-order; no open PR touching `skills/pull-request-merge-order/`; none found
- **Working copy**: /home/nolte/repos/.worktrees/claude-shared/812-merge-order-followups; created via `task worktree:add -- fix/812-merge-order-followups 812-merge-order-followups` off origin/develop 9c504dbc; `git check-ignore -q .audits/issue-orchestrate/812/analysis.md` → exit 1 (not ignored)
- **Author trust**: issue author `nolte` = repository owner → trusted
- **Requirements gate**: operator override 2026-11-23 — the issue states the fix per finding; scope = all six findings with the issue's fixes; finding 2 resolved by operator as "list as not mergeable" (not "warn only")

## Classification

- **Primary class**: bug
- **Secondary class(es)**: refactor
- **Rationale**: findings 1–4 are wrong script behaviour (missed edges, a blocked PR can become head, wrong exit code, late failure); 5–6 are wording and dead-field cleanup.
- **Asserted cause verified**: confirmed by measurement on develop 9c504dbc (`python3 -I` against `merge_order.py`):
  - F1: `_mentions("Depends on #3, #4, and #5")` → `[3, 4]`; `"Depends on #5 and on #6"` → `[5]`; `"depends on PR #4"` → `[]` (`merge_order.py:47`, `DEPENDS_RE`)
  - F2: snapshot with one PR `mergeStateStatus=BLOCKED`, green required checks, `reviewDecision=""` → `order[0].position == 1`, no warning about the block (`merge_order.py:136–142`, `readiness()` ranks BLOCKED as 2; `blockers()` has no BLOCKED branch)
  - F3: `order` on a file containing bytes `\xff\xfe` → exit 1, `UnicodeDecodeError` traceback (`merge_order.py:383` catches only `OSError, json.JSONDecodeError`; `open(...)` without `with`)
  - F4: `collect` type-checks the PR list (`:101`) but not the elements returned by `required_checks()` (`:105`); `order` later dereferences `c["name"]`/`c.get` (`:126`, `:138`)
  - F5: `SKILL.md:89` "never reorder its output by hand" vs. `SKILL.md:57–60` operator head choice
  - F6: `headRefName` in `PR_FIELDS` (`:38`) is read nowhere in `merge_order.py`; `tests/test_merge_order.py:122` sets `headRefName="main"` with no effect

## Scope

- **In scope**: F1–F6 as stated in the issue, with tests and the matching text in `references/ordering.md` / `SKILL.md`.
- **Out of scope**: any change to the ordering rules beyond F2; `pull-request-runner-sweep`; `backlog-delivery-orchestrate` merge-train.

## Route

- **Decision**: direct
- **Rationale**: one outcome (correct the merge-order helper), one PR strand, no roadmap item.

## Work packages

### P1 — Dependency phrases (F1)

- **Problem statement**: `DEPENDS_RE` misses an Oxford comma before `and`, a repeated `on`, and `PR` before the number.
- **Acceptance criteria**: `Depends on #3, #4, and #5` → edges from 3, 4, 5; `Depends on #5 and on #6` → 5, 6; `depends on PR #4` → 4; existing forms and the negative case (`depends on #5 itself and #99 elsewhere` → none) unchanged; new forms added to `test_body_dependency_forms_are_proposed`; `references/ordering.md` Rule 1 calls body proposals best effort.
- **Touched files**: `skills/pull-request-merge-order/scripts/merge_order.py`, `tests/test_merge_order.py`, `skills/pull-request-merge-order/references/ordering.md`
- **Specialist**: nolte-engineering:fullstack-developer
- **Depends on**: none

### P2 — BLOCKED with unknown cause is not mergeable (F2)

- **Problem statement**: a `BLOCKED` PR with no pending/cancelled required check and no recognised blocker ranks like pending and can become head.
- **Acceptance criteria**: such a PR is listed under not mergeable with reason `blocked, cause unknown`; a `BLOCKED` PR with a pending or cancelled required check still ranks as pending; `BLOCKED` + `REVIEW_REQUIRED` keeps only `required review missing`; when `requiredChecks` is empty the reason says the checks may not be reported yet and to re-run `collect`; Rule 0/Rule 2 in `references/ordering.md` and the SKILL.md gotcha on "not reported yet" updated; new parametrised test cases.
- **Touched files**: `merge_order.py`, `tests/test_merge_order.py`, `references/ordering.md`, `SKILL.md`
- **Specialist**: nolte-engineering:fullstack-developer
- **Depends on**: none

### P3 — Input robustness (F3, F4)

- **Problem statement**: non-UTF-8 snapshot exits 1 with a traceback; snapshot opened without `with`; `collect` accepts non-object `requiredChecks` elements.
- **Acceptance criteria**: non-UTF-8 snapshot → exit 2 with `cannot read snapshot`; file read via `with` (or `Path.read_text`); `collect` with a check list like `[1, "x"]` → exit 2 `collect failed`; tests for both in `test_cli_rejects_unreadable_snapshot_and_bad_edge` / `test_collect_fails_closed_when_check_state_is_unknown`.
- **Touched files**: `merge_order.py`, `tests/test_merge_order.py`
- **Specialist**: nolte-engineering:fullstack-developer
- **Depends on**: none

### P4 — Wording and leftovers (F5, F6)

- **Problem statement**: hard rule contradicts step 3; dead `headRefName` field and test argument.
- **Acceptance criteria**: SKILL.md hard rule reads "never reorder its output by hand, except the operator's head choice in step 3"; `headRefName` removed from `PR_FIELDS`, from the `pr()` fixture if unused, and from `test_stacked_pr_is_out_of_scope_and_creates_no_edge` (test keeps its out-of-scope assertions); `grep -n headRefName` over the skill and test shows no remaining use.
- **Touched files**: `SKILL.md`, `merge_order.py`, `tests/test_merge_order.py`
- **Specialist**: nolte-engineering:fullstack-developer
- **Depends on**: none

## Existing installations / upgrade / rollback

health gate: none (Claude plugin). | Package | Surfaces read | Check |
|---|---|---|
| P1–P4 | invocation names unchanged (`pull-request-merge-order`, `collect`/`order`, `--edge`, `--json`); snapshot JSON shape unchanged except `headRefName` no longer collected — `order` never read it | `pytest tests/test_merge_order.py`; `validate_skills.py`; a snapshot from the previous release still orders (fixture snapshots carry `headRefName` and pass) |

## Dependency ordering

P1 ; P2 ; P3 ; P4 — independent; one dispatch, applied in that order because all touch `merge_order.py` and the test file.

## Risks

- P2 makes a just-pushed `BLOCKED` PR without reported checks unorderable until `collect` is re-run → mitigated by the reason text naming the re-run; safer than a wrong head.
- Broadened `DEPENDS_RE` could over-match → negative test case kept; proposals stay advisory (never applied without `--edge`).
- SKILL.md body token budget → check `validate_skills.py` after P2/P4.
- No security-sensitive path touched.

## Open questions

none

## Findings

| Finding | Source | Outcome | Reproduction | Issue |
|---|---|---|---|---|

## Dispatch log
