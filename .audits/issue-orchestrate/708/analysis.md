---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "708"
classification: "bug"
secondary-classes: ["security"]
route: "direct"
status: approved
created: "2026-11-10"
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #708 — capability-reach-audit: two honest flows end permanently weakened (edit-then-rename, delete-and-restore)
- **URL**: https://github.com/nolte/claude-shared/issues/708
- **Labels**: bug, test
- **Linked items**: follow-up of #688 / PR #707 (merged d5f96e3f); sibling #709
- **Prior art checked**: no open PR references #708 (`gh pr list --search 708` → 0); no requirement artefact under `project/requirements/` for it; no in-progress `.resume/issue-orchestrate/` run for #708. Author nolte (repository owner, trusted).

## Classification

- **Primary class**: bug
- **Secondary class(es)**: security (both rules being relaxed exist to refuse a lowered bar; the relaxation must not reopen one)
- **Rationale**: an honest operator flow ends permanently at exit 4 with supersede as the only exit.
- **Asserted cause verified**: confirmed by reproduction on develop d5f96e3f (throwaway test in this worktree, removed):
  - Flow 1 (edit `docs/requirements.md`, `git mv` to `docs/b.md`, re-derive onto `blob:` of `docs/b.md`) → `weakened`, exit 4: "… but it also moved the declaration from docs/requirements.md to docs/b.md, where the previously anchored content is not; record the rename as a pure move first …" (`_path_move_problem`).
  - Flow 2 (content probe deleted, restored byte-identical at the same path) → `weakened`, exit 4: "… but the probe's previous revision (<deletion commit>) carries no readable derived_from …" (`_rebaseline_problem`, the deletion commit is listed by `git log --follow --name-status` with status `D`).

## Requirements gate

Operator override (2026-11-10): the issue's three acceptance criteria stand as the requirement; no `requirements-elicit` run. Design decisions taken by the operator in the same dialogue:

- Flow 1 rename evidence: **the removing commit**. A move to another path is a legitimate rename when the commit that removed the old path, with one parent, added the new path with exactly the blob the old path held in that parent, and the new path did not exist there. With that evidence the probe's declaration continues at the new path, so the move is judged as a re-derivation of the same declaration: the content at the new path at the baseline must differ from what the previous anchor anchored. No similarity heuristic.
- Flow 2 restore: **as before the deletion**. A deletion revision is not a probe revision. A restore whose document equals the revision before the deletion cancels the pair; a restore that differs is judged against the revision before the deletion (a lowered bar under the same anchor is a later change, a moved anchor a re-derivation). #706 removal reporting and `retire` stay untouched.

## Scope

- **In scope**: the two flows in `reach_audit.py` (`probe_changes`, `_path_move_problem`, a `Git` helper for the removing commit), regression tests including the lowering variants, `references/runner-exit-codes.md`.
- **Out of scope**: #709 hardening candidates; SHA-256 and historical commit-anchor moves (their path rule stays pure-move only); spec text (the spec states outcomes, not these mechanics).

## Route

- **Decision**: direct
- **Rationale**: one coherent outcome in one file plus tests and reference, a single PR strand, no roadmap item.

## Work packages

### P1 — Restore after deletion

- **Problem statement**: `probe_changes` treats the deletion commit as a probe revision, so a restored probe can never build on its previous derivation.
- **Acceptance criteria**: a probe deleted and restored unchanged reads clean; restored with a lowered bar under the same anchor reads `weakened` naming the restore commit; restored with a moved anchor is judged as a re-derivation against the revision before the deletion; a second delete/restore cycle behaves the same; #706 `removed` tests stay green.
- **Touched files / artifacts**: `plugins/nolte-engineering/skills/capability-reach-audit/scripts/reach_audit.py`, `tests/test_reach_audit.py`
- **Specialist**: nolte-engineering:fullstack-developer
- **Depends on**: none

### P2 — Rename evidence from the removing commit

- **Problem statement**: `_path_move_problem` accepts a path change only as a pure move, so an edit followed by a rename can't be re-derived.
- **Acceptance criteria**: edit-then-rename-then-re-derive reads clean; rename-then-edit-then-re-derive reads clean; the same shapes with the old path still present, recreated later, or the new path added in a different commit than the removal (or with another blob) read `weakened`; a re-point at an unrelated changed file still reads `weakened`; a re-derivation whose new content equals the previously anchored content is held to the pure-move rule.
- **Touched files / artifacts**: `reach_audit.py`, `tests/test_reach_audit.py`
- **Specialist**: nolte-engineering:fullstack-developer
- **Depends on**: none

### P3 — Reference

- **Problem statement**: `references/runner-exit-codes.md` names the two flows' workarounds and the strict rename definition.
- **Acceptance criteria**: the reference states both rules and drops the workaround text; markdownlint, Vale and the section-reference check pass.
- **Touched files / artifacts**: `plugins/nolte-engineering/skills/capability-reach-audit/references/runner-exit-codes.md`
- **Specialist**: nolte-engineering:fullstack-developer (same change set)
- **Depends on**: P1, P2

## Dependency ordering

P1 ; P2 (independent) → P3

## Risks

- Reopening a laundering path closed in #707 — mitigation: each relaxation gets its lowering counter-test, mutation probes, the reference-consumer state diff, and `code-security-reviewer` rounds on the worktree diff before the PR (the built-in `security-review` reads the primary checkout).
- `git log --diff-filter=D` with history simplification may miss the removing commit on a side branch — mitigation: `--full-history`, and fail closed (pure-move rule) when no removing commit is found.

## Open questions

none

## Dispatch log
