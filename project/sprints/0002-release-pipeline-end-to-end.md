---
number: 0002
status: closed
started: 2026-05-28
ended: 2026-05-28
value_statement: "Consumers of the nolte-shared plugin can install a published release that was cut end-to-end through this repo's own release pipeline, without any manual gh release steps."
artifact_ref: "nolte-shared@0.1.3"
last_commit: c2e47eeab7aa40cf7fff429e05e3f77697627fff
roadmap_items: [R-2]
features: [F-2]
---

## Goal

Deliver to consumers of the `nolte-shared` plugin a published, non-draft release of `claude-shared` that was cut by this repo's own release pipeline rather than by hand. By sprint close, an installable tag exists on `nolte/claude-shared` whose publication event was caused by `release-publish.yml`, the `release-publish-trigger` skill has passed every pre-publish gate from `spec/project/release-skill-layer/` §"Skill B — Release publish trigger" on `develop` HEAD, and the version string is consistent across `project/portfolio.yml` and `.claude-plugin/plugin.json` — proving R-2 (Release pipeline automated end-to-end) is operational for downstream installs.

## Features

- [F-2](../features/plugin-published-via-automated-release.md) — status: done

## Out of scope

- Validation against an external downstream consumer repository (covered by R-6 in a later sprint, not this one).
- Hardening of the develop quality gate beyond what `release-publish-trigger` already requires (covered by R-3).
- Documentation site or skill-agent catalog publishing (covered by R-4).

## Review notes

Closed on 2026-05-28 following the `sprint-review` flow. The sprint traversed `planned` to `closed` in a single operator session; `started` and `ended` therefore carry the same date.

### Artefact validation

Project type: Claude plugin. Per `spec/project/release-artifact/` §"Validation at sprint closure":

- `git rev-parse v0.1.3` resolves to `3b7fc1d`: the plugin version tag exists.
- `gh release view v0.1.3 --json isDraft` returns `isDraft=false` (published 2026-05-28T18:13:34Z, `author=github-actions[bot]`): the release is non-draft and was published by automation.
- Marketplace-resolution probe: `.claude-plugin/marketplace.json` at HEAD lists plugin version `0.1.3` in both `metadata.version` and `plugins[0].version`; `.claude-plugin/plugin.json` declares `0.1.3`.
- `git merge-base --is-ancestor 3b7fc1d c2e47ee` succeeds: the artefact commit `3b7fc1d` is reachable from the sprint's `last_commit` `c2e47ee`.

Note on commit ordering: `last_commit` (`c2e47ee`, the `ci.yml` `workflow_dispatch` enabler from PR #211) is newer than the artefact tag `v0.1.3` (`3b7fc1d`). The release was cut from an earlier `develop` state; the `workflow_dispatch` enabler and the Sprint 0001 closure (PR #210) landed afterwards as part of wrapping this sprint. The release-artifact reachability rule (artefact commit reachable from `last_commit`) holds.

### Value-delivery contract

Satisfied by `features/plugin-published-via-automated-release.md` `acceptance-1`, checked `[x]`: a published, non-draft GitHub release `v0.1.3` (greater than `v0.1.1`) exists, and the publish event was caused by `release-publish.yml` (workflow run `26593368091`, event `workflow_dispatch`, `conclusion: success`, head `3b7fc1d`), not by a manual `gh release edit --draft=false`. This is the fresh pipeline-cut the feature's 2026-05-12 provenance correction required (`v0.1.2` had been published by hand and did not satisfy the criterion).

### Acceptance-criteria provenance

- `acceptance-2`: `ci.yml` carries `on.workflow_dispatch` (PR #211, `c2e47ee`); the manual dispatch run `26600382940` against `develop` reached `conclusion: success` with `lint`, `test`, and `docs` all green, satisfying every required status check.
- `acceptance-3`: `release-publish-trigger` passed every pre-publish gate on `develop` HEAD and dispatched `release-publish.yml` (run `26593368091`, `success`), flipping the open draft to published.
- The criteria were satisfied out of declared order (`acceptance-3` ahead of `acceptance-2`): the publish gate `2d` validated the `push`-triggered required checks on the `develop` tip, which did not depend on `workflow_dispatch`. All four criteria are now met.

### Release-skill-layer chain

Chained. `release-notes-curate` augmented the v0.1.3 draft body with the project-context block, and `release-publish-trigger` dispatched `release-publish.yml` (run `26593368091`, `success`); the downstream `release-cd-refresh-master.yml` run `26593382535` reached `success` and fast-forwarded `main`. Both ran earlier in the same operator session, ahead of this closure.

### Roadmap follow-through

R-2 (Release pipeline automated end-to-end) advances to `done`: its only feature (F-2) is done and this sprint has reached `closed`. R-2's pre-closure status was `proposed` (a lifecycle drift, it should have been `active` while the sprint ran); the closure corrects it directly to `done`.
