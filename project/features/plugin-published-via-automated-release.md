---
id: F-2
title: Plugin published via automated release pipeline
status: done
roadmap_item: R-2
sprint: 2
created: 2026-05-11
ended: 2026-05-28
verifies_sprint_value: acceptance-1
consistency_check:
  performed_at: 2026-05-11
  agent_version: manual-2026-05-11
  findings:
    - kind: clean
      target: n/a
      resolution: proceed
---

## Description

A consumer of the `nolte-shared` plugin can install a tagged, non-draft release of `claude-shared` whose publication was performed by the repository's own pipeline rather than by hand. The release body carries the `release-drafter` changelog; the tag is reachable from `main` once the regular develop-to-main propagation runs, so consumers who install by tag receive the artefact the pipeline cut.

The pipeline is composed of three already-shipped pieces — the `release-drafter` workflow (collects develop PRs into a draft release), the `release-publish` workflow (publishes the draft), and the `release-publish-trigger` skill (validates every pre-publish gate locally before dispatching `release-publish.yml`). The remaining gap is that `.github/workflows/ci.yml` lacks a `workflow_dispatch` trigger, so the skill's "required-checks-on-develop-tip" gate fails by default; closing that gap and then running the skill end-to-end produces the first real published release.

## Acceptance criteria

- [x] **acceptance-1** A published (non-draft) GitHub release tag exists on `nolte/claude-shared` for a version greater than `v0.1.1`, with a body produced from the `release-drafter` template; the publish event was caused by `release-publish.yml`, not by a manual `gh release edit --draft=false`. Closed by the v0.1.3 publish: `release-publish.yml` run `26593368091` (event `workflow_dispatch`, `conclusion: success`, head `3b7fc1d`) flipped the draft to published on 2026-05-28T18:13:34Z; `author=github-actions[bot]`.
- [x] **acceptance-2** `.github/workflows/ci.yml` carries an `on.workflow_dispatch` trigger; manually dispatching the workflow against `develop` produces a SUCCESS run that satisfies every required status check the branch-protection ruleset names. Closed by PR #211 (`c2e47ee`) which added `workflow_dispatch`; dispatch run `26600382940` against `develop` reached `conclusion: success` with `lint`, `test`, `docs` all green.
- [x] **acceptance-3** Running `/nolte-shared:release-publish-trigger` against `develop` HEAD passes every pre-publish gate from `spec/project/release-skill-layer/` §"Skill B — Release publish trigger" and dispatches `release-publish.yml`, with the resulting workflow run reaching `conclusion: success` and flipping the open draft to published. Closed by the `release-publish-trigger` run that dispatched `release-publish.yml` run `26593368091` (all five pre-publish gates green; `conclusion: success`; draft flipped to published).
- [x] **acceptance-4** After publication the released tag's version string matches the version declared in `.claude-plugin/plugin.json` and in both `version` fields of `.claude-plugin/marketplace.json` (`metadata.version` and `plugins[0].version`), so consumers reading either manifest see consistent metadata. Closed by PR #95 `chore(release): v0.1.3 (#95)` at `3ccd5da89fa93459e81fff982462818d3a04d4bf` — see `## Consistency notes` for the provenance correction relative to the original wording.

## Test hooks

- **acceptance-1** — manual: `gh release list --repo nolte/claude-shared --json tagName,isDraft,publishedAt,author` shows a non-draft entry > v0.1.1 whose `author.login` matches the release-publish workflow's bot — `passing` (v0.1.3, `isDraft=false`, `author=github-actions[bot]`; the authoritative proof is `release-publish.yml` run `26593368091`, `conclusion: success`, which performed the publish)
- **acceptance-2** — manual: open `.github/workflows/ci.yml` and verify `on.workflow_dispatch`; then `gh workflow run ci.yml --ref develop` and `gh run list --workflow ci.yml --branch develop --limit 1 --json conclusion` shows `conclusion: success` — `passing` (`workflow_dispatch` added in PR #211 `c2e47ee`; dispatch run `26600382940` on `develop`, `conclusion: success`)
- **acceptance-3** — skill: invoke `/nolte-shared:release-publish-trigger`; expect "all gates green" plus a dispatched `release-publish.yml` run; `gh run view <id> --json conclusion` shows `success` — `passing` (all five pre-publish gates green; dispatched `release-publish.yml` run `26593368091`, `conclusion: success`)
- **acceptance-4** — manual: after publish, `gh release view <tag> --json tagName` and grep `.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json` for the version string; assert all three occurrences (`plugin.json.version`, `marketplace.json.metadata.version`, `marketplace.json.plugins[0].version`) match the tag — `passing` (verified after PR #95 squash-merge on `develop`; all three read `0.1.3`)

## Consistency notes

The consistency check ran as a manual fallback because the running plugin runtime hadn't loaded the `feature-consistency-reviewer` agent as a subagent at the time of authoring; the same fallback path was used for F-1 on 2026-05-09. A `/reload-plugins` (or a runtime upgrade) would lift the fallback in any subsequent invocation, and the right long-term resolution is to rerun the check via the agent path once the runtime catches up.

Investigation surfaces, walked from short SHA `d8076ed`:

- **Feature corpus** under `project/features/`: only `mission-statement-published.md` (F-1), which targets `project/mission.md`. No overlap with the release-pipeline scope of this feature.
- **Spec corpus** under `spec/`: four release-relevant specs exist — `spec/project/release-automation/`, `spec/project/release-artifact/`, `spec/project/release-notes-audience-analysis/`, and `spec/project/release-skill-layer/`. This feature operationalises those specs on `claude-shared` itself (the plugin as reference adopter per O-3); it implements, never contradicts, any MUST in them.
- **Source-code surface** (claude-plugin shape per `spec/project/project-structure/`): `skills/release-publish-trigger/`, `skills/release-notes-curate/`, and the workflows `ci.yml`, `release-drafter.yml`, `release-publish.yml`, `release-cd-refresh-master.yml`, `release-cd-deliver-docs.yml` are already in place. This feature adds an `on.workflow_dispatch` trigger to `ci.yml` (closing the gap noted in memory `project_ci_yml_workflow_dispatch_gap.md`) and runs the existing pipeline end-to-end for the first time; no duplicated prior art was found.

Result: a single `kind: clean` finding, `resolution: proceed`. The feature is cleared for `draft → ready` once the sprint-side `sprint` field is assigned by `sprint-plan`.

**2026-05-12 — provenance correction and acceptance-4 closure (manual follow-up, no consistency-check re-run):**

acceptance-1's reading on 2026-05-11 implicitly assumed the active pipeline cuts every published release. Investigation on 2026-05-12 shows otherwise: `v0.1.2` (published 2026-05-11 15:50 UTC) was **manually flipped from Draft to Published** — no `release-publish.yml` run exists in the publish window (the last run on that workflow is `24910214461` from 2026-04-24, conclusion `failure`; the last *successful* run is `24910178405`, also from 2026-04-24, which cut `v0.1.1`). Only reactive workflows fired on the resulting `release` event: `release-cd-refresh-master.yml` (run `25681009008`) and `release-cd-deliver-docs.yml`, both at 15:50:32 UTC. The release API's `author: github-actions[bot]` refers to the `release-drafter.yml` run on 2026-05-10 22:02 that created the Draft, not to whoever published it 17 hours later. Consequence for this feature: `v0.1.2` does not retroactively satisfy acceptance-1, and the value-verification therefore requires a fresh pipeline-cut on `v0.1.3` (or later) — that's exactly what sprint 0002 produces.

acceptance-4 is closed by PR #95 (`chore(release): v0.1.3 (#95)` at `3ccd5da89fa93459e81fff982462818d3a04d4bf`): after the squash-merge, all three version-bearing fields read `0.1.3` (`plugin.json.version`, `marketplace.json.metadata.version`, `marketplace.json.plugins[0].version`). The original acceptance-4 wording cited `project/portfolio.yml` as one of the manifests; that file is a capability inventory per `spec/portfolio/portfolio-management/` and carries no `version` field. The corrected wording in `## Acceptance criteria` cites `marketplace.json` instead. The correction does not change the consistency-check finding (still `kind: clean`).

## Risks

- The pipeline depends on multiple already-shipped workflows; an undetected regression in `release-drafter.yml` or `release-publish.yml` between now and Sprint-2 close could surface only during the actual publish attempt and would block `verifies_sprint_value`.
- Adding `workflow_dispatch` to `ci.yml` widens the set of triggers any develop-pusher (or scheduled run) can fire. The change is committed in code (not in `.claude/settings.json`), so the impact is bounded; still worth surfacing on the eventual review PR's Risk / rollout notes.
- `release-publish.yml` has not run since 2026-04-24 (the last successful run cut `v0.1.1`). Four weeks of inactivity is enough for action-version drift, expired secret bindings, or upstream-reusable-workflow changes to have accumulated unnoticed. The first dispatch on `develop` HEAD as part of this feature may surface those failures; per `spec/project/workflow-health/`, that's a triage event (`stale pin` / `infra` / `secret drift`), not a retry-the-skill event.
