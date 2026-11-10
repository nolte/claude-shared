---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "702"
classification: "security"
secondary-classes: [bug]
route: "direct"
status: draft
created: "2026-11-10"
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #702 — capability-reach-audit: a probe path that disappears is not tracked, so a rename inside a merge resets the probe's history
- **URL**: https://github.com/nolte/claude-shared/issues/702
- **Labels**: bug, security
- **Linked items**: #701 / PR #703 (merged `d1376bc3`; its `_merges_changing` docstring states a rename inside a merge is not covered)
- **Prior art checked**: no open PR for #702 (`gh pr list --search 702` → only merged #703, #687); requirement covered by `spec/project/capability-reach-audit/en.md:82` (a change to a probe after its derivation is a finding); the spec says nothing about a deleted probe file (`grep -i 'delet|remov|renam'` over the spec: no probe-removal rule).

## Classification

- **Primary class**: security (operator-confirmed 2026-11-10)
- **Secondary class(es)**: bug
- **Rationale**: a merge can rename and weaken an approved probe and the run judges it clean, disarming the tamper rule.
- **Asserted cause verified**: confirmed. Established 2026-11-10 (scratch repo, git 2.53): approve p1; merge with `git mv p1.yml p2.yml` and a lowered `expected`; trivial commit C on p2 → `git log --follow --no-merges -- p2.yml` = `C trivial` only, and `p2.yml` exists in `C^` (`git cat-file -e C^:p2.yml` succeeds). Control: the approving commit of p1 does create p1 (`R^:p1.yml` absent). Verdict clean/exit 0 measured by the #701 implementer with a temporary test (specialist report, not re-run here).

## Scope

- **In scope**: a probe whose oldest listed revision (`file_history`, after any supersede cut) does not create the file — the path already exists in that commit's parent — has an incomplete history: the probe's origin lies in a merge (rename or creation) the walk can't follow. Such a probe is never judged clean; it is a finding naming the commit and the reason. Covers the rename-inside-a-merge case and the creation-in-a-merge-followed-by-a-commit case (today: `test_685_SEC101_a_replacement_created_in_a_merge_commit_is_judged_without_a_cut` covers creation in a merge with no later commit only).
- **Out of scope**: a probe file deleted (or deleted and re-added dissimilar in one plain commit) — the spec defines no rule for removing a probe; tracked as a separate spec issue (to be filed at closeout).

## Route

- **Decision**: direct
- **Rationale**: one outcome, one PR strand, no roadmap item.

## Work packages

### P1 — Refuse an incomplete probe history (fix + tests)

- **Problem statement**: hypothesis: checking, in `probe_changes` (or `file_history`), that the oldest listed revision `(commit, path)` creates `path` — `entry_at(<commit>^, path)` is None, or the commit has no parent — and otherwise reporting the probe as a finding closes #702 without touching the `--follow --no-merges` walk; a cut history (supersede cut) is exempt because it ends deliberately. The implementer may refute this and choose differently.
- **Acceptance criteria**: (a) rename + weakening inside a merge, then a trivial commit → not clean, EXIT_FINDINGS, probe not executed, reason names the oldest listed commit and says the probe's origin isn't in its listed history; (b) creation inside a merge followed by a trivial commit → same; and a replacement created this way supersedes nothing; (c) a plain rename in a non-merge commit, a probe created in a root commit, and a shallow-clone boundary (oldest listed commit whose parent is unavailable) keep today's verdicts; (d) `test_685_SEC101_*` and the full suite stay green, also on git 2.56 (`alpine:edge`); (e) each new test fails on the current `develop` code where meaningful.
- **Touched files / artifacts**: `plugins/nolte-engineering/skills/capability-reach-audit/scripts/reach_audit.py`, `tests/test_reach_audit.py`
- **Specialist**: nolte-engineering:fullstack-developer
- **Depends on**: none

### P2 — Verify the produced diff (verify)

- **Problem statement**: confirm no bypass (e.g. a probe re-created in a plain commit after the merge; shallow clones; supersede-cut interaction) and no fail-open path.
- **Acceptance criteria**: read-only verification of the worktree diff with findings by severity; full suite green.
- **Touched files / artifacts**: read-only
- **Specialist**: nolte-engineering:code-security-reviewer (the built-in `security-review` reads the primary checkout and would see an empty diff)
- **Depends on**: P1

## Dependency ordering

P1 → P2

## Risks

- Shallow clones in CI: the oldest commit's parent may be missing; must not turn every probe into a finding (AC c).
- Legacy probes whose history genuinely starts in a merge now read as findings; remedy: re-derive in a plain commit. Squash-only `develop` has no merges, so consumers see this only on long-lived branches.
- Security-sensitive path: P2 required before the PR.

## Open questions

- none blocking; probe deletion goes to a separate spec issue.

## Dispatch log
2026-11-10 P1 dispatched to nolte-engineering:fullstack-developer — hypothesis refuted: "oldest listed revision absent in its parent" is bypassed by a merge renaming to an interim name and a plain rename onto the final name (measured clean, test_702_a_plain_rename_out_of_a_path_a_merge_created_is_weakened). Implemented instead: the oldest listed revision must be reported by `--follow` itself as an addition (`--name-status` status `A`; root and shallow boundary diff against the empty tree → `A`); otherwise STATE_WEAKENED with a reason naming the commit. New `Git.file_log`, `_origin_problem`; `probe_changes` returns `origin` (exempt when the supersede cut removed revisions). Orchestrator-verified: 776 passed / 3 skipped; with the script reverted 4 of 7 test_702_* fail (the 3 controls pass). Specialist: git 2.56 → 401 passed. Open: legacy probes whose history starts in a merge stay weakened (remedy: supersede); runner-exit-codes.md lacks the #701/#702 reasons.
2026-11-10 P2 dispatched to nolte-engineering:code-security-reviewer (built-in security-review sees the primary checkout only) — no Critical/High in the diff; parsing and fail-closed hold; supersede remedy works (code read). Low: `file_log`/`last_commit`/`is_dirty` lack `--literal-pathspecs`. Medium (pre-existing): probe disappearance (rewrite below rename threshold, delete-in-merge + re-add) → separate spec issue. Medium (pre-existing, locked in by the shallow test): shallow clones make every boundary commit an addition; operator decided 2026-11-10 to guard it in this PR (refuse a shallow repository).
2026-11-10 P1 follow-up (same specialist) — shallow repository refused in `require_local_working_copy` (EXIT_USAGE 2, `git fetch --unshallow` hint; applies to run, --check-migration, reach_replay); `--literal-pathspecs` in file_log/last_commit/is_dirty; runner-exit-codes.md and approval-batching.md updated (#701/#702 reasons, shallow). Orchestrator-verified: 778 passed / 3 skipped; markdownlint clean on both references; tests build repos in tmp_path, so the shallow CI checkout of the `test` job is unaffected. Remedy wording "re-derive in a plain commit" refuted by the specialist (a re-derivation does not adopt a merge weakening, test_701_a_weakening_in_a_merge_is_not_adopted_by_a_later_re_derivation) → revert or supersede.
