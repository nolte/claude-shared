# Group pre-analysis: 2026-11-17-merge-review-gate

- Repository: nolte/claude-shared, develop 11b7bcdb
- Source: partition .audits/issue-backlog-partition/2026-11-17.md (operator-approved 2026-11-17), handed on as a lane (lane: true)
- Tier: 2

## Scope of this analysis

Question: what has to change so that no change lands, and no lane returns `committed-locally`, without an independent review of its real worktree diff through skills that exist, and without its red checks classified?

Logical change: **No change lands or leaves a lane without an independent review of its real worktree diff, run through skills that exist, and without its red checks classified.**

## Members

| Issue | Class | Predicate | Evidence (re-checked against the live issues) |
|---|---|---|---|
| #772 | bug | shared touch surface | `skills/pull-request-merge/SKILL.md` named in #772 and #778; `SKILL.md:3,67,182` delegate to `Skill(skill="review")`; no `review` skill in the session's skill list (`code-review` exists) |
| #778 | feature-request | dependency chain + shared touch surface | adopts #772's worktree-diff review (`git -C <worktree> diff origin/develop...HEAD`) and moves it before `committed-locally`; `skills/issue-orchestrate/SKILL.md:244-256` closeout has no review before the lane return |

Both authors nolte (trusted), no comments, no linked PRs, both bounded. Partition records confirmed. Order: #772 → #778.

## Mode decision

Mode A (single strand): #778 rests on #772's review pattern, so neither member is removable on its own.

## Structural finding

Symptom cluster (overturns the partition's provisional "class"): the delivery skills define the pre-merge gate by naming built-in skills (`review`, `security-review`) instead of by the diff the gate must cover. The names drift (`review` no longer exists), the built-ins read the session cwd rather than the worktree, and the gate sits only in `pull-request-merge`, so lanes reach `committed-locally` unreviewed. #772's red non-required check is the same gap at step 4 (gate defined by required checks, not by every red check on the head commit).

Process finding (recurring): `security-review` cwd scoping is already in memory, and three merges in this run (#759, #763, #779) replaced the missing `review` skill by a hand-dispatched read-only agent. This group is the preventive change.

Class sweep (develop), predicate:

```sh
git grep -nE 'Skill\(skill="review"\)|the `review` skill|`review` skill delegation' -- '*.md'
```

5 hits: `skills/pull-request-merge/SKILL.md:3,67,182`, `skills/pull-request-merge/examples/01-clean-merge-via-automerge-label.md:102`, `spec/project/api-error-handling/en.md:26`.

## Plan approval

Approved by the operator on 2026-11-17. Authorises dispatching #772 and #778 as `authorised_by: 2026-11-17-merge-review-gate/plan-approval`.

## Completeness matrix

| Member | Skills (source) | Spec | Tests | Docs | Config / workflows | Generated index |
|---|---|---|---|---|---|---|
| #772 | `skills/pull-request-merge/SKILL.md` description, step 2, step 4, hard rules; `references/skill-vs-agent-rationale.md`; `examples/01:102`; check: `python3 scripts/validate_skills.py` + sweep predicate → 0 hits | `spec/project/pull-request-workflow/` where it names the `review` skill or only required checks (EN+DE); `spec/project/api-error-handling/{en,de}.md:26`; check: section refs + Vale | guard test for references to non-existent skills (scope decided in the run; else own issue) | not applicable — verify no `docs/en` page restates step 2 (`git grep`) | not applicable — no workflow invokes the review | `docs/*/skills/` catalog (description change); check: `task docs` |
| #778 | `skills/issue-orchestrate/SKILL.md` op 6 + closeout, `references/closeout.md`; `skills/issue-batch-orchestrate/SKILL.md` op 5/6: worktree-diff review before `committed-locally`, findings triaged into the artifact; `pull-request-merge` step 2 as confirmation; check: `validate_skills.py` (token cap) | `spec/project/issue-orchestration/` §Verification, `spec/project/issue-batch-integration/` lane rule (EN+DE) where they place review only at merge; check: section refs + Vale | covered by the group guard | not applicable — as above | not applicable | catalog; check: `task docs` |

## Risks

- `skills/issue-orchestrate/SKILL.md` body near its token cap; move text into `references/` if needed.
- `code-review` is a built-in; keep the read-only worktree-diff agent as the always-available path.
- Later outcomes (#775, #774, red-check-handling) share files; they are ordered after this group.

## Open questions for the operator

none

## Member results

| Member | Result | Verification (actual output) |
|---|---|---|
| #772 | done (specialist `nolte-claude-dev:claude-plugin-developer`; spec part by the orchestrator via the `nolte-shared:spec` contract) — step 2 reviews the real worktree diff via `code-review <PR#>` + read-only agent, security lane = security-briefed read-only agent (`security-review` only when cwd is the worktree), step 4 classifies red non-required checks; new `references/pre-merge-review.md`; `pull-request-workflow` gains the non-required-check MUST + AC (EN+DE); `api-error-handling` stale owner fixed | sweep predicate over `skills/` → 0 hits (rc=1); `validate_skills.py` rc=0, 0 findings for pull-request-merge, body ~4450 tokens (develop ~4460), description 899 chars; pre-commit (6 files) rc=0; markdownlint rc=0; spec EN/DE parity 134/29 both; Vale on spec en.md rc=0 |
| #778 | done (specialist `nolte-claude-dev:claude-plugin-developer`; spec part by the orchestrator via the `nolte-shared:spec` contract) — issue-orchestrate op 6 and issue-batch-orchestrate op 5 review the worktree diff before the PR or `committed-locally`, record findings with the head SHA; pull-request-merge step 2 confirms (later commits may only remove `.audits/`); spec issue-orchestration gains the MUST + AC, security verification aligned to the security-briefed reviewer; issue-batch-integration lane rule extended | `validate_skills.py` rc=0, no finding for the three skills; tokens issue-orchestrate 4494→4490, issue-batch-orchestrate 4004→4170, pull-request-merge 4450→4471; pre-commit (9 + 2 files) rc=0; markdownlint rc=0; spec EN/DE parity 102 bullets / 27 AC and 149 bullets; Vale rc=0 |

## Deviations

- Local adaptation (#778): `pull-request-merge` confirms a recorded review when later commits only remove `.audits/` artifacts (the fix-forward `git rm` always follows the review).
- Local adaptation (#772): the security lane uses a security-briefed read-only agent instead of `code-security-reviewer`, which is a whole-codebase audit whose description excludes diff-scoped review; #772 offers "or a read-only agent".

## Requirement coverage

not applicable — symptom cluster

## Findings

| Finding | Source | Outcome | Reproduction | Issue |
|---|---|---|---|---|
