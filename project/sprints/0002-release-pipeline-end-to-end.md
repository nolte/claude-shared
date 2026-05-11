---
number: 0002
status: planned
started: null
ended: null
value_statement: "Consumers of the nolte-shared plugin can install a published release that was cut end-to-end through this repo's own release pipeline, without any manual gh release steps."
artifact_ref: null
last_commit: null
roadmap_items: [R-2]
features: [F-2]
---

## Goal

Deliver to consumers of the `nolte-shared` plugin a published, non-draft release of `claude-shared` that was cut by this repo's own release pipeline rather than by hand. By sprint close, an installable tag exists on `nolte/claude-shared` whose publication event was caused by `release-publish.yml`, the `release-publish-trigger` skill has passed every pre-publish gate from `spec/project/release-skill-layer/` §"Skill B — Release publish trigger" on `develop` HEAD, and the version string is consistent across `project/portfolio.yml` and `.claude-plugin/plugin.json` — proving R-2 (Release pipeline automated end-to-end) is operational for downstream installs.

## Features

- [F-2](../features/plugin-published-via-automated-release.md) — status: ready

## Out of scope

- Validation against an external downstream consumer repository (covered by R-6 in a later sprint, not this one).
- Hardening of the develop quality gate beyond what `release-publish-trigger` already requires (covered by R-3).
- Documentation site or skill-agent catalog publishing (covered by R-4).

## Review notes

_Populated by `sprint-review` at closure._
