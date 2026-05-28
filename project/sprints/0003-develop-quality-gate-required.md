---
number: 0003
status: planned
started: null
ended: null
value_statement: "Anyone reading claude-shared's README on a fresh clone — a downstream consumer evaluating the plugin, a contributor opening the next PR — can reproduce the develop quality gate from a single documented `task` invocation without reading the underlying Taskfile or workflow YAML."
artifact_ref: null
last_commit: null
roadmap_items: [R-3]
features: [F-3]
---

## Goal

Sprint 0003 closes the documentation and Taskfile-composite gaps that
prevent a new contributor or downstream consumer from reproducing the
quality gate on day one. The develop-side gating itself already ships
at HEAD (`enforce_admins: true` on `develop`, required status checks
`[lint, test, docs]`, `.pre-commit-config.yaml` mirroring the lint
category, Renovate-automerge gated via the gh-plumbing reusable
workflow), so the value-bearing delta is the spec-conformance
documentation in `README.md` plus the `task check` aggregate target in
`Taskfile.yml` — both narrow surfaces, single feature.

The value-verifying acceptance criterion is `F-3:acceptance-1` (the
README documents the canonical gate-invocation target plus the
expected output shape per `spec/project/quality-gate/` §Output shape);
when that bullet is checked at sprint closure, anyone reading the
README on a fresh clone can reproduce the gate from the single
documented `task` invocation — which is exactly the value-delivery
claim this sprint makes. The develop-side gating itself, which is
what actually keeps the snapshot consumable, already ships at HEAD and
is named in `## Out of scope` below.

## Features

- [F-3](`../features/quality-gate-spec-conformance-gaps-closed.md`) — status: ready

## Out of scope

- Branch-protection wiring on `develop` (`enforce_admins`, required
  status checks) — already in `.github/settings.yml`, no change needed.
- Pre-commit hook coverage for the lint category — already in
  `.pre-commit-config.yaml`, no change needed.
- Renovate-automerge gating contract for `nolte/gh-plumbing` bumps —
  enforced by the gh-plumbing reusable workflow per
  `spec/project/workflow-health/` §Upstream drift, no per-repo change
  needed. A future R-3 successor or workflow-health-side roadmap item
  may name the exclusion explicitly.
- The `typecheck` category — this repo has no Python or TypeScript
  source surface today; the gate reports `skipped` per
  `spec/project/quality-gate/` §Composition.
- R-8 reconciliation (the 6 reviewer agents are shipped but the roadmap
  still says `proposed`) — separate concern, handled outside this
  sprint.

## Review notes

_Populated by `sprint-review` at closure._
