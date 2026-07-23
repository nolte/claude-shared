---
name: sprint-review
description: Closes an active sprint per the project sprint spec, validating the deployable artefact and recording the value-delivery audit trail. Invoke when the user asks to close a sprint, review a sprint, finish a sprint, ship a sprint, or wrap a sprint. Also handles equivalent German-language requests. Promotes `active → review`, validates `artifact_ref` per the release-artifact spec's per-project-type rules, confirms the named `verifies_sprint_value` acceptance criterion is checked, optionally chains into `release-notes-curate` and `release-publish-trigger` (operator-opt-in, recorded verbatim in `## Review notes`), then promotes `review → closed`. Falls back to `review → cancelled` with a one-paragraph rationale when artefact validation fails unrecoverably. Supports resume on re-invocation per `spec/claude/resumable-work/`.
tags: [scaffolding, release]
phase: close-release
summary: "Closes an active sprint per the sprint spec: validates the deployable artefact and records the value-delivery audit trail."
summary_de: "Schließt einen aktiven Sprint gemäß Sprint-Spec: validiert das Deploy-Artefakt und protokolliert den Value-Delivery-Audit-Trail."
use_when:
  - "you want to close, finish, or ship an active sprint"
  - "you want to validate the sprint's artifact_ref against the release-artifact spec"
  - "you want the optional chain into release-notes-curate and release-publish-trigger"
dont_use_when:
  - situation: "You want to drive day-to-day mechanics of the sprint"
    alternative: sprint-execute
  - situation: "You want to plan or open a new sprint"
    alternative: sprint-plan
see_also:
  - sprint-execute
  - sprint-plan
  - release-notes-curate
  - release-publish-trigger
resumable: true
---

# Sprint Review

Closes an `active` sprint per `spec/project/sprint/<canonical_language>.md`. This skill is the canonical write authority for `active → review`, `review → closed`, and the cancellation paths from any stage. It delegates artefact validation to the rules declared by `spec/project/release-artifact/<canonical_language>.md` and may chain (with explicit operator opt-in) into `release-notes-curate` and `release-publish-trigger` per `spec/project/release-skill-layer/<canonical_language>.md`.

## Why this is a skill, not an agent

- **Externally-visible mutations gate on user confirmation** — promoting a sprint to `closed` is irreversible bookkeeping, the artefact-validation results need to be reviewed by the user before the promotion fires, and the `release-skill-layer` chain is operator-opt-in by spec; an agent's fire-and-forget shape would lose those gates.
- **Orchestrator that chains other skills** — this skill conditionally dispatches `release-notes-curate` and `release-publish-trigger` mid-flow, and falls through to a cancellation path on validation failure; the skill-orchestrates pattern (per `skill-vs-agent`) defaults the orchestrator to skill form.
- **Output flows back into the main conversation** — the validation transcript, the `## Review notes` audit block, and the chosen lifecycle outcome (`closed` vs `cancelled`) all belong in the user's working context, not behind an agent's structured-report boundary.
- Counter-dimension considered: a narrower agent could sharpen the per-kind artefact verification step (`git rev-parse`, `gh release view`, `docker manifest inspect`, etc.), but the load-bearing dimension is the multi-step orchestration with operator-opt-in branches — skill wins.

## User-language policy

Detect the user's language and respond in it. Sprint markdown content (including `## Review notes`) stays in the project's primary language; frontmatter keys, lifecycle tokens, verification command outputs (exit codes, key output lines), and any `gh` / `git` / `docker` invocations remain English so portfolio automation reads them deterministically.

## Preconditions

Before mutating the sprint or dispatching any chained skill, confirm:

- Current working directory is inside a git repository with `project/sprints/` populated.
- The user has named the sprint to close (or there's exactly one `active` sprint—use that one and confirm with the user before mutating).
- The sprint's `status` is `active`. Refuse on `planned` (operate via `sprint-execute` first), `review` (mid-flow recovery; ask the user how to proceed), `closed`, or `cancelled` (already terminal).
- Every feature listed in the sprint's `features` frontmatter is `done` (read each feature file and check `status`). On any non-`done` feature, stop and report the offending features; this skill doesn't drive feature transitions—`sprint-execute` does.
- The sprint's `features` frontmatter list is non-empty. An empty list makes the value-delivery contract unsatisfiable per `spec/project/sprint/` §Lifecycle; refuse the `active → review` transition with a verbatim error.
- The sprint's `last_commit` frontmatter field is non-null per `spec/project/sprint/` §Acceptance Criteria. If it's null, hand back—`sprint-execute` is the canonical writer of that field.

## Operations

The skill follows a strict order. The artefact-validation block (step 3) **MUST** complete before the release-skill-layer dispatch (step 5); a failure in step 3 short-circuits to step 7 (cancellation), never to step 5. The order is fixed because publishing a release whose artefact ancestry is broken is the exact failure mode `release-artifact` exists to prevent.

### 1. Promote `active → review`

1. Confirm every precondition above. On any failure, stop and report; don't write.
2. Set `status: review` on the sprint's frontmatter. Don't set `ended` yet—the field is reserved for `closed` or `cancelled`.
3. Surface the sprint summary to the user: number, slug, `value_statement`, the feature list with each feature's `verifies_sprint_value` field, and the current `artifact_ref` (which **MUST** be non-null per `spec/project/sprint/` §Artefact contract; if null, refuse the transition and hand back).

### 2. Detect the project type

Use the same signals as `release-skill-layer` and `github-issue-templates-apply` per `spec/project/release-artifact/` §Project-type detection:

- `.claude-plugin/plugin.json` → Claude plugin
- `pyproject.toml` shape → Python application or library
- `package.json` → Node / TypeScript
- declared CLI entry → CLI tool
- `custom_components/<name>/manifest.json` → HACS integration
- `mkdocs.yml` (or equivalent) → documentation-only

A per-repo override at `.github/release-skill-layer.yml` (`artifact_kinds: [...]`) takes precedence; **MUST NOT** introduce any other override file.

### 3. Validate `artifact_ref` per the release-artifact spec

Parse the sprint's `artifact_ref` (string or list of strings) per the detected project type and the optional `artifact_kinds` override. For every component, run the per-kind verification command listed in `spec/project/release-artifact/` §Validation at sprint closure:

- Git tag → `git rev-parse <tag>`
- GitHub release → `gh release view <tag>`
- Container image → `docker manifest inspect <image>`
- PyPI distribution → `pip index versions <dist>`
- npm package → `npm view <pkg>@<version>`
- Doc-site deploy URL → HEAD request
- Claude plugin → `git rev-parse <plugin-version-tag>` plus a marketplace-resolution probe (read `.claude-plugin/marketplace.json` at HEAD and confirm the plugin version is listed)
- HACS integration → `git rev-parse <tag>` plus a `manifest.json` `version`-field equality check at the artefact's commit

Then confirm: the resolved artefact's commit (when applicable) **MUST** equal the sprint's `last_commit` frontmatter field or be reachable from it. A missing or null `last_commit` blocks closure; surface the failure verbatim.

A bare commit SHA as `artifact_ref` is rejected unless the project explicitly opts in via `.github/release-skill-layer.yml`.

**Tooling (optional GitHub MCP):** prefer `github:get_release_by_tag` for the GitHub-release artefact check when a GitHub MCP server is connected, falling back to `gh release view` otherwise, per `spec/claude/mcp-tool-preference/`; the `git rev-parse <tag>` validations stay local git and the publish dispatch stays `gh`. `gh`/git stays authoritative and output is identical.

Record the verification transcript (commands run, exit codes, key output lines) for later persistence in `## Review notes`. **On any failure, do not proceed to step 4 or 5.** Surface the failed check verbatim, ask the user whether the failure is recoverable (re-cut the artefact and rerun) or unrecoverable (cancel the sprint), and route accordingly: recoverable → stop; unrecoverable → step 7.

### 4. Confirm `verifies_sprint_value`

Walk the sprint's feature list and confirm:

- Exactly one feature carries a non-null `verifies_sprint_value` field per `spec/project/sprint/` §Value-delivery contract.
- The named `acceptance-<n>` identifier exists on that feature.
- The named acceptance-criterion bullet is checked (`- [x] **acceptance-<n>** …`).

On any violation (zero or multiple `verifies_sprint_value` declarations, missing identifier, or unchecked bullet), refuse closure and surface the offence verbatim. Sprint closure with a missing or unchecked verifier is a hard violation per `spec/project/sprint/` §Acceptance Criteria.

### 5. Operator-opt-in chain into release machinery (optional)

This step runs only when the project type publishes via `release-publish.yml` (typical for Claude plugin, Python library, Node library, CLI tool, HACS integration—the project types named by `spec/project/release-artifact/` §Dispatch boundary to release machinery).

Ask the user explicitly whether to chain. The chain points are fixed:

- **`release-notes-curate`** — augments the open `release-drafter` draft body with project-context-aware sections; idempotent on re-runs per `spec/project/release-skill-layer/` §Skill A.
- **`release-publish-trigger`** — validates every gate from `spec/project/release-automation/` §Pre-publish verification and dispatches `release-publish.yml` via `gh workflow run`.

Outcomes to record verbatim in `## Review notes`:

- "Chained: release-notes-curate (run URL or summary), release-publish-trigger (workflow run URL)" — when the user opts in.
- "Skipped: release-notes-curate / release-publish-trigger; reason: <one-line rationale>" — when the user declines, naming who or what dispatches publication later (operator manually, automated post-merge job, or a follow-up sprint) per `spec/project/sprint/` §Dispatch into release machinery.

The recording is mandatory; a sprint that closes without a recorded operator decision on the chain fails validation per `spec/project/sprint/` §Acceptance Criteria.

### 6. Promote `review → closed`

1. Set `status: closed` and `ended: <today's ISO date>` on the sprint's frontmatter.
2. Populate `## Review notes` with: the verification transcript from step 3 (commands and outcomes), the verifying feature's full location (`features/<slug>.md` plus the `acceptance-<n>` ID) per `spec/project/sprint/` §Value-delivery contract, the operator's release-skill-layer chain decision from step 5, and any cross-references to out-of-band artefacts published during the sprint (per `spec/project/release-artifact/` §Out-of-band artefacts).
3. If the sprint's roadmap items each have every feature `done`, advance their `status` to `done` per `spec/project/roadmap/` §Lifecycle. A roadmap item whose pending features fall outside the sprint stays `active` until a successor sprint closes.
4. **Surface unconsumed blog-trigger deferrals.** Per `spec/project/blog-author-trigger/` §Deferral artefact (SHOULD: the source consumer's `sprint-review` surfaces unconsumed deferrals at sprint close so they don't accumulate silently), scan `project/blog-triggers/*.yml` for entries with `status: deferred`. List each by `feature-slug` plus its `deferral_reason` and `deferred_at`, so the operator can revisit them (re-invoke `blog-author-trigger` to author / update, or leave deferred). This is a read-only surfacing step; sprint-review never consumes or mutates the deferral artefact (only a later trigger run sets `status: consumed`). When the directory is absent or holds no `deferred` entry, note "no unconsumed blog-trigger deferrals" and move on.
5. Surface the closed sprint summary to the user: path, ended date, the artefact reference, the verifying feature, the chain decision.

### 7. Cancellation path: `review → cancelled` (or earlier)

Triggered when step 3 fails unrecoverably (the underlying release pipeline is broken and re-cutting the artefact isn't feasible at this time) or when the user explicitly cancels at any earlier stage.

1. Set `status: cancelled` and `ended: <today's ISO date>`.
2. Populate `## Review notes` with a one-paragraph rationale that **MUST** name (a) the lifecycle stage at which cancellation occurred (`planned`, `active`, or `review`), and (b) why recovery wasn't feasible at this time. Missing rationale or stage citation is a hard validation failure per `spec/project/sprint/` §Acceptance Criteria.
3. Hand off the `target_sprint` re-targeting of every roadmap item still pointing at the cancelled sprint to `sprint-plan`, which owns clearing or re-targeting terminal-sprint references per `spec/project/roadmap/` §Sprint and feature linkage (valid post-terminal values: `null` or a `planned` successor). Surface the affected roadmap items to the operator and route the fix through `sprint-plan`; this skill doesn't rewrite `target_sprint` itself. Roadmap items **MUST NOT** advance to `done` from a `cancelled` sprint even when every feature is individually `done`; the items remain `active` until a successor sprint reaches `closed`.
4. Surface the cancelled sprint summary to the user, naming the rationale and the re-targeting outcome.

## Gotchas

- **`artifact_ref` validation is per-project-type.** The skill detects the project type from the marker-file signals of Operation 2 (with the `.github/release-skill-layer.yml` override) and applies the matching artifact-ref shape from the release-artifact spec: a Claude plugin sprint expects a published-release tag, a Python library expects a PyPI version, a documentation-only project expects a deployed-docs commit SHA, and so on. A wrong project-type detection produces a misleading "artifact_ref invalid" refusal. The skill surfaces the detected type before validating so the operator can override.
- **`active → review` is reversible** (a failed artifact validation can route back to `active`); `review → closed` and `review → cancelled` are NOT. The skill warns explicitly before either terminal transition and requires verbatim operator confirmation.
- **The `verifies_sprint_value` acceptance criterion is the load-bearing closure gate.** When the named criterion isn't checked on the carrying feature, the skill refuses `closed` and routes to `cancelled` (with a clear rationale paragraph) — operators sometimes try to argue the criterion "was achieved differently"; the spec is strict that the named criterion is the audit trail, not a related observation.
- **Optional chaining into `release-notes-curate` and `release-publish-trigger` is operator-opt-in.** Defaulting to chain leads to surprise releases; the skill stays explicit about each chain hop and records the operator's opt-in verbatim in `## Review notes`.
- **Cancelled sprints leave a value-delivery gap that the next sprint must explain.** When the skill cancels a sprint, the unfinished features need re-targeting (typically to the next sprint or back to the roadmap queue). The skill surfaces the affected feature IDs and asks where each one lands; nothing is silently re-targeted.
- **Unconsumed blog-trigger deferrals are surfaced read-only, not consumed.** At `review → closed` the skill lists `project/blog-triggers/*.yml` entries with `status: deferred` (per `spec/project/blog-author-trigger/` §Deferral artefact) so they stay visible, but it never edits them: the `deferred → consumed` transition is owned by a later `blog-author-trigger` run, and `cancelled` is operator-set. The surfacing is a SHOULD reminder, not a closure gate — a sprint still closes when deferrals remain.

## Examples

- Read `examples/01-clean-close-claude-plugin.md` when closing a sprint cleanly for a Claude plugin project with all features done.
- Read `examples/02-artifact-validation-fails-cancel.md` when artifact validation fails and the sprint must be cancelled instead of closed.
- Read `examples/03-chain-into-release-skill-layer.md` when the user opts in to chaining into `release-notes-curate` and `release-publish-trigger` after sprint closure.

## Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/sprint-review/<run-id>.yml` after every successful user-approval gate and after each named phase boundary. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope (`schema_version`, `run_id`, `inputs`, `phase`, `decisions[]`, `status`, ...) and the fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

## Hard rules

- **Never** call `gh release edit --draft=false`, `gh api -X PATCH /repos/.../releases/<id> draft=false`, or any other path that flips the draft state outside `release-publish.yml`. The rule comes from `spec/project/release-automation/`, `spec/project/release-skill-layer/`, and `spec/project/release-artifact/` §Dispatch boundary to release machinery and is non-negotiable here too. The only acceptable publish path is dispatching `release-publish-trigger`.
- **Never** transition `active → closed` without passing through `review`. The value-coverage check lives in `review` per `spec/project/sprint/` §Lifecycle.
- **Never** close a sprint while any feature in `features` is non-`done`, or while the `features` frontmatter list is empty, or while `last_commit` is null, or while `artifact_ref` is null. Each is a hard refusal point.
- **Never** close a sprint with zero or more than one `verifies_sprint_value` declarations across its features, or with the named acceptance-criterion bullet unchecked.
- **Never** accept a bare commit SHA as `artifact_ref` unless the project explicitly opts in via `.github/release-skill-layer.yml`.
- **Never** chain into `release-notes-curate` or `release-publish-trigger` without the user's explicit opt-in, and never close the sprint without recording the operator's chain decision (chained or skipped) verbatim in `## Review notes`.
- **Never** advance a roadmap item to `status: done` from a `cancelled` sprint, even when every feature is individually `done`. Re-target the pending features to a successor sprint instead.
- **Never** edit any sprint other than the one being reviewed in this run. `sprint-plan` and `sprint-execute` own the other sprints' lifecycles.
- When `spec/project/sprint/`, `spec/project/release-artifact/`, `spec/project/release-skill-layer/`, or `spec/project/release-automation/` disagrees with this skill, the spec wins. Propose updating this skill rather than silently diverging.

## Multi-model testing

Examples and operations in this skill are verified on Claude Sonnet 4.6 as the default model; spot-checked on Haiku 4.5 for cost-sensitive runs; Opus 4.7 is appropriate for high-stakes audits that require deeper reasoning. The skill body has no model-specific assumptions beyond standard tool-call semantics.
