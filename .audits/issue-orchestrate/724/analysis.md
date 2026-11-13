---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "724"
classification: "bug"
secondary-classes: ["security"]
route: "direct"
status: approved
created: "2026-11-12"
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #724 — capability-reach-audit: an approved probe on a dropped line still reads clean in six merge shapes
- **URL**: https://github.com/nolte/claude-shared/issues/724
- **Labels**: bug
- **Linked items**: follow-up of #720 (PR #725, c3c5ecd6) and #709 (PR #723, 33be5312); no open PR
- **Prior art checked**: `gh pr list --state open` → none; `project/requirements/` holds no artefact for this
  issue (`capability-reach-executor.md`, `reach-probe-removal.md`, `reach-probe-section-anchor.md` cover other
  work)
- **Author / trust**: issue author `nolte` (repository owner, trusted); no comments

## Classification

- **Primary class**: bug
- **Secondary class(es)**: security (the misjudgement lets a lowered bar read clean)
- **Rationale**: the runner returns a wrong verdict (`clean`, exit 0) for eight reproduced histories.
- **Asserted cause verified**: confirmed for all eight scenarios on `develop` c3c5ecd6 — each prints
  `exit 0` with the harness `scratchpad/rv4/h4.py head <scenario>` (run 2026-11-12). The two causes named in
  the issue hold in the code: `_unlisted_write` skips merge commits and writes that descend from the revision
  that moved the probe off a path, and keys foreign paths on nothing
  (`plugins/nolte-engineering/skills/capability-reach-audit/scripts/reach_audit.py`, function `_unlisted_write`);
  `Git.merges_changing` searches `since..until` only, so a merge that is an ancestor of the oldest listed
  revision, or that sits on a dropped line outside a renamed path's span, is never searched.

## Requirements gate

No requirement artefact exists. The issue states eight reproducible histories and one testable acceptance
criterion, and the open point is a design direction, not an unknown requirement. **Operator override recorded 2026-11-13** ("setze es direkt um!", approving P1–P3, the direct route
and the override together); no `requirements-elicit` run.

## Measurement (established 2026-11-12, uncommitted prototype, since reverted)

Prototype (saved as `scratchpad/724-prototype.patch`, 49 diff lines, `_unlisted_write` plus one new
`Git.merges_editing`):

1. a merge anywhere in HEAD's history that differs from every parent on one of the probe's paths, and that no
   judged span already reports, is an unlisted write;
2. a plain write off HEAD's first-parent line under one of the probe's ids is an unlisted write on any path;
3. the "placed after the probe left that path" exemption applies only to writes on HEAD's first-parent line.

Result on the harness: `x_ours_then_add`, `x_mergecreate_mergedel_readd`, `x_sup_ours_then_add`, `x_span_ren`,
`x_side_ren_raise`, `x_side_ren_mergeraise`, `x_seg2_renameback`, `x_seg2_readd_old` → `exit 4` (were `exit 0`);
controls `x_seg2_ctrl`, `x_sup_ctrl`, `x_side_del` stay `exit 0`.

Result on `tests/test_reach_audit.py` (635 tests): 606 pass, 29 fail. 27 failures are the reason wording only
(the prototype's "on a merged line" text; avoidable by keeping the existing sentence). **2 are verdict changes
and must not ship as they are:**

- `test_701_a_merge_on_a_path_the_probe_left_is_not_the_probes_change`: clean → weakened. A side branch puts an
  unrelated, non-probe file at the old path; rule 3 can't tell it from a strict probe put back there. The id
  comes from the file-name stem, not from the document.
- `test_688_a_copy_of_a_probe_created_in_a_merge_gets_no_origin_finding[True]`: the copy `p2` clean → weakened.
  Cause **unestablished**: not debugged; the observation that settles it is the reason string of the `p2` row.

Unestablished: the effect on honest histories outside the suite (no adversarial run was made on the
prototype), and the run-time cost of one extra `git log` per probe path.

## Scope

- **In scope**: make the eight shapes read `weakened` with regression tests, without changing any verdict the
  suite pins as `clean`; update `references/runner-exit-codes.md` §First-parent rule (its limit paragraph).
- **Out of scope**: the linear declaration toggle (clean on every version, not a merge shape); any change to
  the first-parent policy itself; branch-protection guidance beyond the existing sentence.

## Route

- **Decision**: direct
- **Rationale**: one outcome (the runner's verdict for these shapes), one PR strand, no roadmap item.

## Work packages

### P1 — Widen the unlisted-write rule to the eight shapes

- **Problem statement**: rules 1–3 above, with two refinements the measurement requires: rule 3 counts an
  off-line write on a left path only when the document declares one of the probe's ids (a stem-derived id is
  no probe revision), and the `p2` copy regression is diagnosed and removed.
- **Acceptance criteria**: the eight scenarios read `weakened` (exit 4) as regression tests that fail on
  c3c5ecd6; every test in `tests/` that passes on c3c5ecd6 passes unchanged except for assertions on the
  reason text of already-`weakened` rows; no reason sentence changes for existing findings.
- **Touched files**: `plugins/nolte-engineering/skills/capability-reach-audit/scripts/reach_audit.py`,
  `tests/test_reach_audit.py`
- **Specialist**: fullstack-developer (subagent_type: nolte-engineering:fullstack-developer)
- **Depends on**: —

### P2 — Adversarial verification against `develop`

- **Problem statement**: three of four earlier review rounds on this runner found a case where the branch read
  clean and `develop` a finding, after a green suite.
- **Acceptance criteria**: a fresh build-and-run review over both trees reports no row that reads clean on the
  branch and a finding on c3c5ecd6, and no honest squash-merge history that turns from clean to a finding;
  every case it does find is fixed with a test or P1 is cut back.
- **Touched files**: none (read-only; findings feed P1)
- **Specialist**: no matching specialised agent — generalist remediation (`code-security-reviewer` reads only,
  it doesn't build repositories and run both trees)
- **Depends on**: P1

### P3 — Reference update

- **Problem statement**: §First-parent rule says these shapes read clean.
- **Acceptance criteria**: the limit paragraph names only what still reads clean after P1; Vale and
  markdownlint pass.
- **Touched files**: `plugins/nolte-engineering/skills/capability-reach-audit/references/runner-exit-codes.md`
- **Specialist**: no matching specialised agent — generalist remediation (a three-sentence edit bound to P1's
  outcome; `audience-doc-author` needs an audience artefact this reference doesn't have)
- **Depends on**: P1, P2

## Dependency ordering

P1 → P2 → P3

## Risks

- A fourth mechanism in a rule that was cut back twice this week. Stop rule: if P2 finds a clean-where-develop-
  finds case in two consecutive rounds, cut P1 back to the subset that survived and record the rest on #724 as
  an accepted limit.
- False positives on honest merge-commit histories; squash-merge repositories are unaffected by construction
  (no merged lines in HEAD's history).

## Open questions

- Is recording the remaining shapes as an accepted limit (branch protection that refuses pushed merges)
  acceptable if P2 forces a cut? The issue's acceptance criterion allows it.

## Defect-class decision

Guard: the regression tests in `tests/test_reach_audit.py`, run by the `test` required check. They enumerate
the reproduced shapes, not the class; a guard over the class (every merge topology) isn't possible, which is
what #709 and #720 established. The PR's class sweep states that.
