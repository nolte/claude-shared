---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "701"
classification: "security"
secondary-classes: [bug]
route: "direct"
status: draft
created: "2026-11-10"
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #701 — capability-reach-audit: a probe weakened inside a merge commit is judged clean
- **URL**: https://github.com/nolte/claude-shared/issues/701
- **Labels**: bug, security
- **Linked items**: #698 (introduced `--no-merges`; gap predates it)
- **Prior art checked**: no open PR references #701 (`gh pr list --search 701` → 0); requirement covered by `spec/project/capability-reach-audit/en.md:82` (MUST: a probe weakened since its derivation is a finding) and AC `:138`; requirement artefact `project/requirements/capability-reach-executor.md` U_gate 0.80 = τ_high, so no new elicitation.

## Classification

- **Primary class**: security (operator-confirmed 2026-11-10)
- **Secondary class(es)**: bug
- **Rationale**: the gap lets a change disarm the audit's anti-tampering rule (a co-located probe lowered without a finding).
- **Asserted cause verified**: confirmed. Established 2026-11-10 (git 2.53, scratch repo): `git log --follow --no-merges -- p1.yml` → `side3-edit, approve` (evil merge absent); plain `git log -- path` lists it. Established via the `target` fixture: evil merge lowering `expected` 2→1 → `h` `clean`, exit 0, probe executed; same edit as a side-branch commit → `weakened`. `observation_digest` (`reach_audit.py:1805`) covers only `observe`/`environment`/`teardown`, so it doesn't catch `expected`. The docstring of `Git.file_history` (`reach_audit.py:638`) records the blind spot ("A merge that only edits a probe was already absent from `--follow` output") without handling it.
- **Refuted candidate fix**: `git log --follow --cc` lists *every* merge on the walk (benign and probe-creating ones without a file name, measured on git 2.53), so it can't stand in for the merge set without re-implementing the filter.

## Scope

- **In scope**: change detection in `probe_changes` (`reach_audit.py:1110`) treats a merge commit after the baseline that changes the probe's content against every parent ("evil merge") as a later, unapproved change → `weakened`. Supersession reuses `detect_change`, so it inherits the fix. Docstring of `file_history` corrected. Regression tests.
- **Out of scope**: merges *before* the baseline in the `earlier` revisions used by `_rebaseline_problem` (unestablished whether any verdict depends on them; recorded as a follow-up question, not changed here); a merge that both edits and re-records `derived_from` (already surfaced as weakened via the `run == []` branch, with a misleading "uncommitted changes" wording — observed by reading `reach_audit.py:1145-1148`, not measured); approval digest scope (spec-level decision).

## Route

- **Decision**: direct
- **Rationale**: one outcome (close the detection gap), one PR strand, no roadmap item.

## Work packages

### P1 — Scope the merge blind spot across the change-detection surface (audit)

- **Problem statement**: hypothesis: `probe_changes` is the only place where a merge-only probe edit escapes; `last_commit` (plain `git log -1`) already sees evil merges for declarations. The auditor may refute this and name further sites.
- **Acceptance criteria**: a list of every history read in `reach_audit.py` with file:line and whether a probe/declaration change made only inside a merge escapes it.
- **Touched files / artifacts**: read-only, `plugins/nolte-engineering/skills/capability-reach-audit/scripts/reach_audit.py`
- **Specialist**: nolte-engineering:code-security-reviewer
- **Depends on**: none

### P2 — Count evil merges after the baseline as later changes (fix + tests)

- **Problem statement**: hypothesis: adding `git log --merges --format=%H <baseline>..HEAD -- <probe.file>` (default history simplification lists only merges that differ from every parent for that path) to `later` in `probe_changes` closes the gap on every git version without touching the `--follow --no-merges` walk, so the merge-created replacement case (`test_685_SEC101_a_replacement_created_in_a_merge_commit…`) keeps its verdict. Renames after the baseline are already later commits, so the path is constant over the range. Partly established 2026-11-10 (scratch repo, git 2.53 and 2.56 via alpine:edge): `git log --merges <approve>..HEAD -- p1.yml` lists only the evil merge, not a benign merge of a side-branch edit nor an unrelated merge; for a file created in a merge it lists that merge, which `probe_changes` never reaches because such a probe has no history. The implementer may refute the rest.
- **Acceptance criteria**: (a) evil merge lowering `expected` after approval → `weakened`, exit 4, probe not executed, the message names the merge commit; (b) a merge after the baseline that doesn't touch the probe → still `clean`; (c) a merge that takes one side's probe edit (TREESAME to that parent) → verdict unchanged from today (the side commit is already flagged); (d) `test_685_SEC101_a_replacement_created_in_a_merge_commit…` and the full suite stay green; (e) `file_history` docstring no longer claims the exclusion drops nothing relevant.
- **Touched files / artifacts**: `plugins/nolte-engineering/skills/capability-reach-audit/scripts/reach_audit.py`, `tests/test_reach_audit.py`
- **Specialist**: nolte-engineering:fullstack-developer
- **Depends on**: P1

### P3 — Verify the produced diff (verify)

- **Problem statement**: confirm the fix closes the gap without new bypasses (argument injection via paths, unbounded git output).
- **Acceptance criteria**: `security-review` over the worktree diff (non-empty diff captured first), full suite green, also on git 2.56 (`alpine:edge`).
- **Touched files / artifacts**: read-only
- **Specialist**: security-review (built-in skill) + quality-gate
- **Depends on**: P2

## Dependency ordering

P1 → P2 → P3

## Risks

- False positives on legitimate conflict resolutions that touch a probe: by the spec any change after the derivation is a weakening, so the finding is intended; mitigation: message names the merge so the operator re-derives.
- `<baseline>..HEAD` with a baseline not an ancestor of HEAD: baseline comes from HEAD's own history, so it is an ancestor; the implementer guards the call anyway.
- Security-sensitive path (the audit's tamper detection): P1 + P3 required before the PR.

## Open questions

- none blocking. Follow-up candidate: do merges before the baseline matter for `_rebaseline_problem`? (unestablished)

## Dispatch log
2026-11-10 P1 dispatched to nolte-engineering:code-security-reviewer — hypothesis partly refuted: the gap originates only in `file_history`, but besides `later` it skews the baseline choice and the `earlier` revisions read by `_continuation_problem` (:1255, Critical: a merge-only weakening between recording R and a later legitimate re-derivation M is absorbed), `_run_length` (:1227) and `_rebaseline_problem` (:1522). `last_commit`, blob/content comparisons, `merge-base`, `_lineage_problem` and the digest are unaffected (code read; scenarios not executed). P2 scope widened accordingly.
2026-11-10 P2 dispatched to nolte-engineering:fullstack-developer — hypothesis partly refuted: default-simplified `git log --merges` misses an evil merge on a side branch whose net result matches the main line; used `--full-history -c --name-only --no-follow` instead (`Git.merges_changing`). Spans: baseline..HEAD (probe_changes), recording..move (_continuation_problem), key-moving merges (_key_moving_merges in _rebaseline_problem). Verified by orchestrator: full suite 764 passed / 3 skipped; with reach_audit.py reverted 8 of 10 test_701_* fail. Specialist reports git 2.56 (alpine:edge): 389 passed (not re-run by orchestrator).
2026-11-10 P3 dispatched to nolte-engineering:code-security-reviewer (built-in security-review reads the session cwd = primary checkout, empty diff → substituted, per reference_security_review_cwd_scoping) — no Critical/High in the new paths; injection and fail-closed hold. Medium (suspected, pre-existing class): rename inside a merge + weakening + later trivial commit judged clean (disappearing probe paths untracked) → separate issue. Low: since-not-ancestor window collapse; path-reuse false positive; missing octopus / hostile-config tests → returned to P2 specialist.
2026-11-10 P2 follow-up (same specialist) — Lows fixed: non-ancestor `since` widens to all merges reachable from `until`; per-path segments bounded at the rename commit; tests for octopus merge and hostile `log.follow`/`diff.renames` config. Orchestrator-verified: 769 passed / 3 skipped; delta read by orchestrator (no second agent pass). Medium merge-rename gap measured clean/exit 0 → separate issue. Class sweep: 4 `git log` sites under capability-reach-audit/scripts; 1 merge-blind (file_history) compensated; last_commit sees evil merges (default simplification), reach_replay is a non-verdict measurement aid on --first-parent.
