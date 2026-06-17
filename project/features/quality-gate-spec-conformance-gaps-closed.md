---
id: F-3
title: Quality-gate documentation and Taskfile composite close the spec gaps
status: done
roadmap_item: R-3
sprint: 3
created: 2026-05-27
ended: 2026-05-29
verifies_sprint_value: acceptance-1
consistency_check:
  performed_at: 2026-05-27
  agent_version: feature-consistency-reviewer@11993eb
  findings:
    - kind: prior-art
      target: spec/project/quality-gate/en.md §"Open Questions" (line 75)
      resolution: proceed
    - kind: prior-art
      target: skills/quality-gate/SKILL.md §Operations / "Prefer Taskfile targets" (line 59)
      resolution: proceed
    - kind: clean
      target: n/a
      resolution: proceed
---

## Description

The README explicitly names the quality-gate's local invocation and the
expected output shape per `spec/project/quality-gate/` §Acceptance
criteria #7, so a new contributor reproducing the gate on a fresh clone
sees one canonical command and one canonical table contract before
reading the underlying Taskfile or workflow yaml. The README also lists
which CI lint-side categories `.pre-commit-config.yaml` covers locally
and which the contributor must invoke separately before push, so the
gap between pre-commit scope and CI scope is explicit rather than
discoverable by accident.

`Taskfile.yml` exposes a `check` aggregate target that wraps the lint
and test categories the repo has (the `docs` category remains its own
CI job because the docs build is the gate for documentation freshness,
not the code gate). The `/nolte-engineering:quality-gate` skill already
prefers a composite `check` target when present and falls back to
category-specific targets otherwise; landing the `check` target
satisfies `spec/project/quality-gate/` §Acceptance criteria #8 without
any skill-side change.

Branch protection on `develop` (`enforce_admins: true`, required
`required_status_checks.contexts: [lint, test, docs]`), the local
pre-commit hooks for the lint category, and the Renovate-automerge
gating contract via the gh-plumbing reusable workflow already satisfy
the spec at HEAD and are explicitly out of scope for this feature.

## Acceptance criteria

- [x] **acceptance-1** A reader of the repo's `README.md` finds, in the
  Usage section, the canonical local invocation of the gate (the
  `task` target name) and a one-paragraph description of the output
  shape per `spec/project/quality-gate/` §Output shape (the four
  statuses `pass`/`fail`/`skipped`/`timeout` and the four table
  columns `Check`/`Status`/`Runner`/`Details`); no contributor needs
  to open the Taskfile or `ci.yml` to learn how to run the gate
  locally.
- [x] **acceptance-2** The README lists every gate category named in
  `ci.yml`'s `lint` / `test` / `docs` jobs, marking each as
  `covered by pre-commit` or `contributor-invoked`; the list resolves
  one-to-one against the job names so a reader can confirm
  completeness by string match.
- [x] **acceptance-3** `Taskfile.yml` declares a `check` task that
  invokes the lint and test categories the repo has relevant code for;
  `task check` exits zero on a clean tree and non-zero when any
  category fails.

## Test hooks

- **acceptance-1** — manual: open `README.md`, locate the gate
  invocation and the output-shape paragraph in the Usage section;
  cross-reference against `spec/project/quality-gate/` §Output shape —
  `passing` (README §"Running the quality gate" names `task check` and
  the output-shape table per PR #224, shipped in v0.1.4)
- **acceptance-2** — manual: extract the README's gap list; assert
  one-to-one match between its entries and the job names in
  `ci.yml`'s `lint` / `test` / `docs` jobs; assert each entry's
  marker is one of `covered by pre-commit` or `contributor-invoked` —
  `passing` (README lists `lint`=covered-by-pre-commit,
  `test`/`docs`=contributor-invoked, one-to-one with ci.yml jobs)
- **acceptance-3** — manual: on a clean tree, run `task check`;
  assert exit 0 plus the table-shape output; introduce a deliberate
  lint failure (e.g., a Vale-banned token in a tracked Markdown
  file), re-run `task check`, assert exit non-zero — `passing`
  (verified locally: clean tree exits 0; a deliberate Vale error in
  README exits 1)

## Consistency notes

Re-review at short SHA `11993eb` against the canonical feature-spec
surfaces (feature corpus, source-code surface, spec corpus) returned
zero `overlap` or `duplication` findings on the narrowed scope: F-3
only touches `README.md` and `Taskfile.yml`, so the prior broader-batch
overlap with F-2 (`plugin-published-via-automated-release`, which
touches `.github/workflows/ci.yml`) has been eliminated. Roadmap R-3
carries the single bullet `quality-gate-spec-conformance-gaps-closed`,
so the previously-noted sibling overlaps (`vale-prose-check-integrated-into-gate`
and `renovate-lockfile-checks-required-on-develop`) are absent.

**Prior art — `spec/project/quality-gate/en.md` §Open Questions, line
75:** the spec flags the composite target's portfolio-wide name as an
unresolved open question ("Should the spec mandate a single top-level
target name (`task check`) … or is the per-repository choice between
`task check`, `task gate`, and equivalent acceptable?"). Acceptance-3
commits this repo to `check` specifically. That's not drift — the
spec's §Composition SHOULD already exemplifies the name `task check`,
and the `quality-gate` skill enumerates `check` first in its
composite-preference list. Should the open question close on a
different name later, the rename is a one-line change in Taskfile and
README; no behaviour shifts.

**Prior art — `skills/quality-gate/SKILL.md` §Operations, line 59:**
the `quality-gate` skill already prefers a composite `check` target
when one exists and otherwise falls back to category-specific targets.
Acceptance-3 fills the gap (no composite exists today) and the skill
picks it up automatically with no skill-side change. The skill is
prior art for the gate's *execution*, but not for the README
documentation or the composite target itself, both of which are net-new
in this feature.

**Clean — feature corpus + narrowed source surface + roadmap:** F-1
targets `project/mission.md` only; F-2 targets `.github/workflows/ci.yml`
plus the release pipeline; neither touches `README.md` or `Taskfile.yml`
in the scopes F-3 occupies. The narrowed surface produces zero
blocking hits.

## Risks

- README documentation drifts when `Taskfile.yml` or
  `.pre-commit-config.yaml` evolves and the README is not touched in
  the same PR; mitigation is a workflow-health concern (the
  `quality-gate-enforcer` agent's audit would catch the drift), not a
  gate-side concern.
- The `task check` aggregate adds a third invocation path next to the
  individual `task lint` / `task test` targets; the spec permits both,
  but contributors may diverge on which one they use locally. The
  README's canonical-invocation paragraph resolves the ambiguity by
  naming `task check` as the documented entry point.

## Open questions

- `spec/project/quality-gate/` §Open Questions, line 75 — the spec
  hasn't yet decided whether `task check` is a portfolio-wide mandate
  or a per-repository preference. F-3 picks `check` locally; if the
  spec later mandates a different name, this feature's `Taskfile.yml`
  and README paragraph are the two touch-points for the rename.
