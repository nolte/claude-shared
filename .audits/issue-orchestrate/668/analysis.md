---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "668"
classification: "bug"
secondary-classes: [spec-change]
route: "direct"
status: approved
created: "2026-09-25"
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #668 — capability-reach-audit: anchor derived_from on declaration content so re-derivation survives a squash merge
- **URL**: <https://github.com/nolte/claude-shared/issues/668>
- **Labels**: none
- **Linked items**: nolte/kamerplanter#1780, #1783, #1776 (consumer evidence); no PR references #668.
- **Prior art checked**: #663 (runner, merged `8b72edaf`), #661 (spec); no open PR; no `project/features/` entry.
- **Trusted author**: `nolte` (repository owner).

## Classification

- **Primary class**: bug
- **Secondary class(es)**: spec-change (probe schema revision)
- **Rationale**: the portfolio mandates squash merges (`spec/project/pull-request-workflow/`), and under them every probe re-derived in the same PR as its declaration reads `unresolved` after the merge. The runner defeats the workflow it ships into. Operator-confirmed 2026-09-25.
- **Asserted cause verified**: confirmed by reading the code at `8e4af10d` and tracing the path:
  - `schemas/reach-probe-v1.0.schema.yaml:70-77`: `derived_from` is "the commit of the target repository the probe was derived at … no content hash is stored".
  - `plugins/nolte-engineering/skills/capability-reach-audit/scripts/reach_audit.py:967-971` (`detect_change`): `derived_from` must resolve to a commit and be an ancestor-or-equal of `HEAD`, else `unresolved` ("… is not in the history of HEAD"). A squash leaves the branch commit outside `develop`'s history.
  - `:979`: stale iff the declaration's last commit is not an ancestor-or-equal of `derived_commit`.
  - `:917-919` (`_rebaseline_problem`): the previous and new `derived_from` must both resolve to commits, else `weakened` ("cannot both be resolved to commits"). After the follow-up PR the previous value is the vanished branch commit.
  - `spec/project/capability-reach-audit/en.md` does not prescribe a commit anchor (no `derived_from` mention; change detection at `:79`, AC `:135`, `:139`). The commit anchor is fixed by the schema and the runner only.
  - Consumer evidence (kamerplanter#1780: `git diff e9e0c3a52 c9d6d29ee -- <declaration>` empty) is carried forward as **unestablished here**: it was not re-run in this repository; the red-first squash test in P2 reproduces the mechanism locally instead.

## Decisions (operator, 2026-09-25)

- Anchor form: `derived_from: "blob:<sha1>"` for an in-repository declaration (git blob hash of the declaration file at derivation); a commit or pinned ref as before for inherited specs; external anchors unchanged.
- Migration: schema v1.1 and the runner accept both forms; commit-anchored probes keep today's logic until they are re-derived.
- Section-level hashing: out of scope; filed as its own issue after the verify gate.

## Requirements gate

No `project/requirements/` artifact. **Operator override**: the issue states the proposal, the trade-offs, and three acceptance items; the decisions above close its open points.

## Scope

- **In scope**: spec (EN/DE), schema v1.1 (new file), runner (embedded schema copy, `detect_change`, `_rebaseline_problem`), tests, scanner agent, skill, `references/runner-exit-codes.md`, `references/approval-batching.md`, one example probe in the new form.
- **Out of scope**: `schemas/reach-not-constructible-v1.0.schema.yaml` (records `derived_from` without change detection, `not_constructible_entry` at `reach_audit.py:1108`; any string is valid); section-level hashing; kamerplanter's probes.

## Route

- **Decision**: direct — one outcome, one PR strand, no roadmap item.

## Work packages

### P1 — Spec: change detection anchors on what a squash merge preserves

- **Problem statement**: the spec is silent on the anchor, so the schema's commit anchor became the contract. Hypothesis: add a requirement under the change-detection block (near `:79`) that an in-repository declaration is anchored on its content (the declaration file's git blob at derivation), so a probe re-derived in the same pull request stays clean after a squash merge and a later declaration edit makes it stale; a re-baseline is a re-derivation only when the anchored content changed and the new anchor equals the declaration at the recording commit; commit anchors stay valid for migration. Add one acceptance criterion; mirror in `de.md`; walk restatements.
- **Acceptance criteria**: EN/DE parity; AC count updated consistently; `pre-commit run --files` Passed.
- **Touched files**: `spec/project/capability-reach-audit/en.md`, `de.md`
- **Specialist**: skill `nolte-shared:spec`
- **Depends on**: none

### P2 — Schema v1.1 and runner: content anchor with red-first tests

- **Problem statement**: Hypothesis: `schemas/reach-probe-v1.1.schema.yaml` (new file per `spec/project/yaml-json-schema/` `:115`, `$id` minor bump) documents `derived_from` as `blob:<sha1>` for an in-repository anchor or a commit (migration) / pinned ref; the runner embeds v1.1. `detect_change` for a blob anchor: stale iff `git rev-parse HEAD:<path>` (or the working tree when dirty) differs from the stored blob; no ancestry check; a missing path is stale (rename/delete). `_rebaseline_problem` for a blob anchor: accepted iff the previous stored value differs from the new one and the new one equals the declaration's blob at the baseline (recording) commit; no commit outside the probe file's own history is resolved. Commit anchors keep today's code path.
- **Acceptance criteria (red-first, each test fails before the change)**: (a) squash transparency: declaration edit + re-derived blob probe on a branch, squash onto main → `clean`; (b) a later declaration edit → `stale`; (c) `derived_from` bump without a content change → `weakened`; (d) bump with a content change → `clean`, and no `refs/pull/*` fetch needed (the previous branch commit is absent from the repository); (e) a commit-anchored probe behaves exactly as before (existing R2/R3/SCR001 tests stay green); (f) A→B→A reads `clean` against A (documented trade-off); (g) `python3 -m pytest tests -q` passes; v1.0 schema file untouched.
- **Touched files**: `schemas/reach-probe-v1.1.schema.yaml` (new), `schemas/README.md` (if it indexes schemas), `plugins/nolte-engineering/skills/capability-reach-audit/scripts/reach_audit.py`, `tests/test_reach_audit.py`
- **Specialist**: `nolte-engineering:fullstack-developer`
- **Depends on**: none

### P3 — Scanner, skill, references, example in the new form

- **Problem statement**: `capability-reach-scanner.md:43` records `derived_from` via `git log -1 --format=%H -- <path>`; `:139`, `:164` show a 40-hex example; the skill (`SKILL.md:100`) and `references/runner-exit-codes.md` (`:20`, `:35`, `:46`, `:52-58`) and `references/approval-batching.md` describe the commit anchor. Hypothesis: the scanner records `blob:$(git rev-parse HEAD:<path>)` for an in-repository declaration; skill and references describe the blob anchor, the squash transparency, the new reason strings from P2, and the migration rule; one example probe (`examples/erasure-finalisation.yml` or another in-repo one) switches to the blob form so `tests/test_reach_audit_examples.py` covers it.
- **Acceptance criteria**: no remaining text that presents the commit as the only in-repo anchor; `python3 scripts/validate_skills.py plugins/nolte-engineering/` → no Critical, no budget finding; descriptions unchanged unless the budget allows; `pytest tests/test_reach_audit_examples.py` passes.
- **Touched files**: scanner agent, skill `SKILL.md`, the two references, one example
- **Specialist**: `nolte-claude-dev:claude-plugin-developer`
- **Depends on**: P2 (reason strings)

### P4 — Follow-up issue: section-level anchoring

- Filed after the verify gate (publication hold), referencing #668 and the PR.
- **Specialist**: orchestrator (issue filing, no code)
- **Depends on**: verify gate

## Dependency ordering

P1 ; P2 → P3 ; P4 after verify.

## Class sweep (for the fix PR)

- **Predicate**: `git grep -n -E 'resolve_commit\(|is_ancestor_or_equal\(' -- '*.py'` restricted to calls on a stored anchor value (not `HEAD`), run at `8e4af10d`.
- **Hits**: 5 — `reach_audit.py:917` (two resolves), `:921`, `:967`, `:970`, `:979`; `:620` and `:1356` resolve `HEAD` only; `git grep -E 'is-ancestor|merge-base'` over `*.py *.sh *.yml *.yaml` finds only the `Git` helper at `:558`.
- **Repaired**: 5 (a blob anchor takes none of these paths; commit anchors keep them by the migration decision).
- **Guard**: the squash-transparency test (P2 a) and the rebaseline tests (P2 c, d) — a red-first regression test that simulates the squash.

## Risks

- **Rename/delete**: a blob anchor on a moved declaration must read stale (as today); covered by an explicit test.
- **Line endings / filters**: `git rev-parse HEAD:<path>` hashes the committed blob; a dirty working tree already reads stale, so no normalisation question arises.
- **Description budgets**: the `nolte-engineering` agent budget and the skill's body are near their caps; P3 keeps descriptions unchanged.

## Open questions

none

## Dispatch log
