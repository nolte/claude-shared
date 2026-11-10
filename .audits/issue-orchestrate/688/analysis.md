---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "688"
classification: "bug"
secondary-classes: ["spec-change"]
route: "direct"
status: approved
created: "2026-11-10"
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #688 — capability-reach-audit: a probe added in a later commit inherits a similar probe's history via copy detection and reads weakened
- **URL**: <https://github.com/nolte/claude-shared/issues/688>
- **Labels**: bug, test
- **Linked items**: Refs #685 (supersede cut `_lineage_problem`); related #701/#703, #702/#705, #704/#706
- **Prior art checked**: no open PR references #688; #705 (`_origin_problem`, status `A` at the oldest listed revision) and #706 (removal rule) are merged and do not change the copy pairing (measured below).

## Classification

- **Primary class**: bug
- **Secondary class(es)**: spec-change (operator chose a spec MUST plus an acceptance criterion for the copy rule)
- **Rationale**: a probe derived from a template one commit after a similar probe reads `weakened` with no change to it after its approval.
- **Asserted cause verified**: confirmed. Throwaway test on develop 6a529fb5, git 2.53: p1 committed, then p2 from the same template in a later commit; `git log --follow --name-status -- project/reach-probes/p2.yml` lists `C098 p1.yml → p2.yml` at p2's commit and then p1's `A`; `_state(p2)` = `weakened: probe changed in 7cb81e44fa1f after its derivation was recorded in d17b8330a847`. Code path: `Git.file_log` (`reach_audit.py:759`, `--follow --no-merges --name-status`) feeds the history to `probe_changes` (`reach_audit.py:~1460`), which walks past the copy into p1's revisions.

## Scope

- **In scope**: a revision at which `--follow` reports the probe's path as a copy (`C`, the source still present in the parent) is where that probe came into being: the walk ends there, and the #705 origin check accepts it like an `A`. Spec rule + AC (EN/DE), runner, tests, and the stale sentence in `references/runner-exit-codes.md:159`.
- **Out of scope**: renames (`R`) keep being followed (identity across a move); the supersede record and `_lineage_problem` stay; merge handling (#701/#702) unchanged.

## Route

- **Decision**: direct
- **Rationale**: one outcome, one PR strand, no roadmap item. Operator decision 2026-11-10: "An Kopie schneiden", "1 PR, mit Spec-Ergänzung".
- **Requirements gate**: operator override 2026-11-10 — the issue's proposal (author nolte, repository owner, trusted) plus the operator's decision above; no `requirements-elicit` run.

## Work packages

### P1 — Spec rule for a copied probe

- **Problem statement**: `spec/project/capability-reach-audit/` says nothing about copies; the runner reference documents copy inheritance as intended.
- **Acceptance criteria**: EN canonical gains one MUST bullet (a probe created as a copy of another, still existing probe file is judged from its own creating commit; it does not inherit the source's history; a rename keeps the history) and one AC checkbox; DE mirrors it (counts equal); Vale clean on both.
- **Touched files**: spec/project/capability-reach-audit/{en,de}.md
- **Specialist**: nolte-shared:spec (skill)
- **Depends on**: none

### P2 — Runner cut at a copy + tests + reference

- **Problem statement (hypothesis, refutable)**: ending the history at the newest revision with status `C` and treating a `C` oldest revision as an origin removes the false `weakened` without opening an escape: the kept, weakened source stays a finding; overwrite, delete-and-re-add at the same path, and rename keep reading `weakened`; deletion reads `removed` (#706).
- **Acceptance criteria**: new tests — (a) p2 added from p1's template in a later commit reads clean; (b) p2 copied from p1 and then edited after approval reads weakened at that edit; (c) a weakened p1 beside a new similar p2 without `supersedes`: p2 clean, p1 still weakened, exit non-zero; (d) rename of a weakened probe stays weakened; (e) copy whose source was created in a merge: no origin finding for the copy; (f) supersede cases of #685 still pass. `test_685_a_new_id_beside_the_kept_weakened_file_inherits_its_chain_by_copy_detection` is rewritten to the new behaviour. `references/runner-exit-codes.md:159` no longer claims a similar file under a new name reads weakened. Full suite green.
- **Touched files**: plugins/nolte-engineering/skills/capability-reach-audit/scripts/reach_audit.py, plugins/nolte-engineering/skills/capability-reach-audit/references/runner-exit-codes.md, tests/test_reach_audit.py
- **Specialist**: nolte-engineering:fullstack-developer (agent, foreground)
- **Depends on**: P1

### P3 — Verify

- **Problem statement**: gate and security scope of the changed history walk.
- **Acceptance criteria**: `task lint`, `task test` green in the worktree; `code-security-reviewer` on the worktree diff reports no Critical/High open.
- **Specialist**: nolte-engineering:quality-gate (skill), nolte-engineering:code-security-reviewer (agent)
- **Depends on**: P2

## Dependency ordering

P1 → P2 → P3

## Risks

- Cutting at `C` could let a probe escape a weakening by copying it. Mitigation: the source keeps its own finding; test (c). Security review in P3.
- git's copy detection threshold (50 %) varies with content; a dissimilar new file is already an `A`. No change there.

## Open questions

none

## Dispatch log
