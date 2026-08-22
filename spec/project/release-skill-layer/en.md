# Local Release Skill Layer

Status: draft
Portfolio-Scope: portfolio

## Context

Two existing specs frame how releases work in the portfolio. `release-automation` defines **how** the Draft → Published transition happens (a `workflow_dispatch`-triggered `release-publish.yml` consuming a `release-drafter` draft) and explicitly forbids body edits inside that workflow: per its §Operational contract, body edits **MUST** happen via `gh release edit` outside the workflow, or via `release-drafter` re-runs. `release-notes-audience-analysis` defines **what** the body should contain, by applying the audience-identification method to the bounded context "release notes of a GitHub release." Neither spec covers the operational layer that sits in the operator's terminal: a local procedure that reads the open draft, augments its body with project-context-aware sections derived from the audience artefact and the repo's architecture, and a separate local procedure that validates every pre-publish gate before dispatching `release-publish.yml`. This spec defines that layer as two reusable skills shipped from this plugin, so every adopting repo gets the same local entry point for the release decision without bypassing the workflow audit trail.

Readers: authors of the two release skills (`release-notes-curate`, `release-publish-trigger`) this spec defines, and operators driving the release decision from their terminal without bypassing the `release-automation` audit trail.

## Goals

- Provide a local skill (Skill A) that augments the open `release-drafter` draft with project-context-aware sections derived from the repo's project type and the audience artefact, idempotent on re-runs.
- Provide a local skill (Skill B) that validates every pre-publish gate locally and dispatches `release-publish.yml` via `gh workflow run`, never `gh release edit --draft=false` directly.
- Reuse the project-type taxonomy already established by `github-issue-templates-apply` (Claude plugin, Python application, Python library, Node / TypeScript, CLI tool, documentation-only) so portfolio-wide skill behaviour stays consistent.
- Anchor curated content to the audience artefact produced by `release-notes-audience-analysis`, so every section the skill writes traces back to a documented audience need.
- Stay portfolio-reusable: any repo that ships `release-drafter.yml` and `release-publish.yml` can adopt this skill layer without per-repo configuration beyond the existing audience artefact.

## Non-Goals

- Substituting `release-drafter`. The Conventional-Commits categorisation, version-derivation, and tag generation remain a workflow job.
- Substituting `release-publish.yml`. The workflow is and remains the audit-trail point for the Draft → Published transition.
- Calling `gh release edit --draft=false` directly from any local skill. Forbidden by `release-automation` and explicitly out of scope here; the only acceptable publish path is dispatching the workflow.
- Generating release notes from scratch. Skill A augments existing `release-drafter` output; it doesn't replace it.
- Versioning policy. Inherited from `release-drafter` configuration in `nolte/gh-plumbing:.github/commons-release-drafter.yml`.
- Post-publish operations (`release-cd-refresh-master.yml`, packaging workflows). Those are downstream of `release-publish.yml`.
- Identifying audiences. `release-notes-audience-analysis` (and its parent `audience-identification`) own that; Skill A consumes the artefact, never invents entries.

## Requirements

### Skill split and shared shape

- **MUST** ship as two distinct skills under `skills/<name>/SKILL.md` per `skill-management`, not as one combined skill: a curation skill (Skill A) and a publish-trigger skill (Skill B). The split is justified because the two operations have different blast radius (body edit is reversible; workflow dispatch fires an externally visible publish chain), different precondition surfaces (audience artefact vs version-bearing-file alignment), and naturally serve different points in the release decision (review-and-shape vs commit-to-ship).
- **MUST** both follow the same project-type detection signals used by `github-issue-templates-apply`: `.claude-plugin/plugin.json` for Claude plugin, `pyproject.toml` shape for Python application vs library, `package.json` for Node / TypeScript, declared CLI entry for CLI tool, `mkdocs.yml` / equivalent for docs-only.
- **MAY** support a per-repo override at `.github/release-skill-layer.yml` when autodetection misses (hybrid repos, monorepos with multiple package roots).

### Skill A: Draft notes curation

#### Operational contract

- **MUST** identify the open `release-drafter` draft on the default branch (`develop`) via `gh release list --json isDraft,tagName,targetCommitish,createdAt` and filter to the draft whose `targetCommitish` is `develop` (or the repo's declared default branch).
- **MUST** refuse to operate when no draft exists, when multiple drafts exist with ambiguous tags, or when the draft's tag isn't reachable from the default branch; surface each failure case with a concrete remediation path.
- **MUST** consume the audience artefact produced by `release-notes-audience-analysis` (typically `AUDIENCES.md`, an "Audiences" section in `README.md`, or a dedicated `docs/release-audiences.md`); when no audience artefact exists, dispatch the `audience-identify` skill to produce one before continuing.
- **MUST NOT** invent audience entries inline; the spec forbids it. Missing audiences raise a single open-question note in the curated body, not fabricated content.
- **MUST**, when the audience artefact and the autodetected project type conflict (for example the artefact lists "downstream Python integrators" but the repo is detected as a Claude plugin), prefer the audience artefact as the human-confirmed signal, and emit the conflict into the body's `## Open questions` subsection (§Content placement) so the reviewer sees the disagreement; **MUST NOT** silently override the artefact with the autodetected type.
- **MUST** derive project-context sections from the detected project type. Concrete bundles:
  - **Claude Code plugin**: `Skills changed` (added / renamed / removed under `skills/`), `Agents changed` (under `agents/`), `Specs changed` (under `spec/`), `Breaking changes for plugin consumers` (renamed slash commands, removed skills, plugin manifest version bump), `Required plugin re-install` (only when skill / agent artefacts moved or were renamed).
  - **Python application** (with hardware-touching variant per `github-issue-templates-apply` references): `Hardware support` (changes to supported devices, sensors, firmware-version constraints), `Runtime requirements` (Python version, OS, container base image), `Migration notes for operators` (config changes, breaking environment-variable renames).
  - **Python library**: `API changes`, `Compatibility breaks` (SemVer-major changes), `Deprecations` (with the deprecation removal target).
  - **Node / TypeScript library or app**: `API changes`, `Compatibility breaks`, `Runtime requirements` (Node version, package-manager version pin) when the package declares them.
  - **CLI tool**: `Command-line changes` (new commands, renamed flags), `Flag deprecations`, `Default-value changes`.
  - **Documentation-only repo**: `Restructured pages` (path moves), `Removed pages`, `New translations`.
- **MUST** add specialised or per-repo bundle extensions (for example a HACS-integration bundle or an OCI-image bundle) to `skills/release-notes-curate/references/project-bundles.md`, not to a separate spec; the normative core table above stays inline here.
- **SHOULD** attribute every section entry to a concrete commit SHA, PR number, or touched path so reviewers can validate without re-walking `git log`.
- **MUST** surface the planned augmentation to the user before any write (diff format showing the existing draft body, the additions, and the boundary markers), and block the write until the user confirms.
- **MUST** write the augmented body via `gh release edit <tag> --notes <body>`. **MUST NOT** call `gh release edit --draft=false`, ever; that path is reserved for `release-publish.yml`.

#### Re-run safety and markers

- **MUST** wrap the project-context augmentation in stable HTML-comment markers exactly: `<!-- release-skill-layer:project-context-start -->` and `<!-- release-skill-layer:project-context-end -->`. The markers are the contract that lets re-runs detect and update in place.
- **MUST** detect existing markers on every run and replace the content between them; **MUST NOT** create a second marker pair, append outside the markers, or duplicate sections.
- **MUST NOT** modify any content outside the marker boundaries on re-runs. `release-drafter` owns the body above the markers; the skill owns only the augmentation block.
- **MUST** verify after every write that the resulting body still contains exactly one marker pair; refuse to declare success otherwise.

#### Content placement

- **MUST** place the augmentation block **below** the `release-drafter` Conventional-Commits sections, separated by a clear divider (a horizontal rule plus a level-2 heading like `## Project context` is the recommended shape).
- **SHOULD** add a `## Audiences served` subsection at the top of the augmentation block when the audience artefact lists primary audiences, mapping each primary audience to the sections of the curated body that address its content dimensions per `release-notes-audience-analysis`.
- **MAY** include a final `## Open questions` subsection inside the augmentation block when audience-coverage gaps were detected; gaps are content the skill would have produced if the audience artefact had been more complete.

### Skill B: Release publish trigger

#### Pre-dispatch validation

- **MUST** validate every gate from `release-automation` §Pre-publish verification locally before dispatch:
  - exactly one open `release-drafter` draft exists on `develop`;
  - the draft's tag is reachable from the current `develop` tip;
  - every version-bearing file declared by `release-automation` §Version-bearing files (default table by repo type, or override at `.github/release-automation.yml`) equals the target tag at the draft's `target_commitish` under its declared transform;
  - the alignment commit on `develop` (when present) has the subject prefix `chore(release): <tag>`;
  - every required status check declared for `develop` reports `SUCCESS` on the commit where branch protection actually enforced it: the head of the pull request that the `develop` tip squash-merges, resolved via `gh api repos/<owner>/<repo>/commits/<tip-sha>/pulls`. Validating the tip itself is unsound and **MUST NOT** be done while a pull request is resolvable. Branch protection enforces its contexts on the pull-request head, and a required check whose workflow carries a `paths:` filter on its `push` trigger never reports on a tip whose merge touched none of those paths, so the context is routinely *absent* there. Absent isn't green: under the strict reading the gate blocks every release whose final commit missed those paths, and under a lenient one it silently validates a subset while appearing to validate the whole set. The tip's tree is nonetheless the tree those checks ran against, because `pull-request-workflow` §Branch freshness requires `required_status_checks.strict: true`, so a pull request can only merge while up to date with `develop`;
  - when the `develop` tip has no resolvable pull request (a direct push, or a merge the API doesn't associate), the tip itself is the only commit available and the gate **MUST** be evaluated there, with an absent required context counted as a **failure**. A repository that publishes from direct pushes has no commit on which its required contexts were ever enforced, and the gate **MUST NOT** paper over that;
  - `.github/workflows/release-publish.yml` exists in the repo.
- **MUST** refuse to dispatch when any of the gates above fails. The refusal message **MUST** name the failed gate and point at the remediation path (`chore(release): <tag>` PR for fallback alignment, `release-drafter` re-run for missing draft, etc.).
- **MUST** present the validated state to the user (tag, target SHA, version-bearing-file diff summary, audience-coverage summary if Skill A has run on the draft), and require explicit confirmation before dispatch.

#### Dispatch

- **MUST** dispatch `release-publish.yml` via `gh workflow run release-publish.yml --ref develop -f tag=<tag>`; the `tag` input is mandatory per `release-automation` §Operational contract regardless of how many drafts are open.
- **MUST NOT** call `gh release edit --draft=false`, `gh api -X PATCH /repos/.../releases/<id>` with `draft=false`, or any other body that flips the draft state outside the workflow. There is no admin-override path; this is identical in spirit to `pull-request-merge`'s `enforce_admins: true` rule.
- **SHOULD** support a `--dry-run` mode that runs every precondition validation and dispatches with `dry_run=true` workflow input per `release-automation` §Operational contract.
- **MUST NOT** let `--dry-run` write to the draft body (no "would-publish" comment or any other mutation); `--dry-run` stays strictly side-effect-free. The draft-body edit is Skill A's blast radius (§Skill split and shared shape); Skill B's only side effect is the workflow dispatch.
- **SHOULD** verify post-dispatch that the workflow run started (`gh run list --workflow=release-publish.yml --limit 1 --json status,conclusion,url`) and report the run URL plus its current status; don't poll to completion outside an explicit wait mode (matches `pull-request-merge`'s wait-mode contract).

#### Failure routing

- **MUST**, when a pre-dispatch validation fails because a required check on `develop` is red, route to `workflow-health` triage rather than retry the dispatch, same protocol as `pull-request-merge` step 4.
- **MUST**, when the workflow run itself fails after a successful dispatch, defer to `release-automation` §Observability and audit and `workflow-health` rather than attempting a second dispatch from the skill.

### Composition

- **MUST** allow Skill A to run independently of Skill B (curation without publish) and Skill B to run on a draft that hasn't been augmented (publish without curation). Neither skill is a precondition of the other in the spec; the operator decides the order.
- **SHOULD**, when Skill B detects a draft without a `release-skill-layer:project-context-start` marker, surface a non-blocking note offering to dispatch Skill A first; the operator MAY proceed without curation.
- **MAY** chain Skill A → Skill B in a single operator request when the operator says "curate and publish"; the chain is two sequential skill invocations, not a third combined skill.
- **MUST** be discoverable as the dispatch target of `release-artifact` §Dispatch boundary to release machinery: when sprint-review at sprint closure decides to publish, it dispatches the two skills defined here, not the underlying `release-publish.yml` workflow directly. The relationship is one-way (this spec is the lower layer, `release-artifact` is the higher), and the consuming spec **MUST NOT** redefine any rule declared here. `release-artifact` is the authority for which sprint state triggers the dispatch and how the operator-opt-in is recorded.

## Acceptance Criteria

- [ ] Two skills exist under `skills/release-notes-curate/` and `skills/release-publish-trigger/` (or equivalent ASCII kebab-case names) shipped by the `nolte-shared` plugin; each has a passing `skill-review` plan recorded under `.audits/skill-review/` at adoption time.
- [ ] Each skill's frontmatter `description` lists concrete user-trigger phrases (EN + DE) and explicit anti-triggers against the workflows it doesn't replace.
- [ ] Both skills detect project type via the same signals as `github-issue-templates-apply`, verifiable by reading the detection step of each `SKILL.md`.
- [ ] Skill A consumes the `release-notes-audience-analysis` artefact when present and dispatches `audience-identify` when absent, verifiable by the operator's transcript on a fresh repo.
- [ ] Skill A's augmentation is wrapped in `<!-- release-skill-layer:project-context-start -->` and `<!-- release-skill-layer:project-context-end -->` markers in every produced draft body.
- [ ] A re-run of Skill A on an already-curated draft produces no diff in the augmentation block when no new commits have landed since the previous run; the markers are present exactly once.
- [ ] Skill A never modifies content outside its marker boundaries, verifiable by diffing the body before and after a run.
- [ ] Skill B refuses to dispatch when any `release-automation` §Pre-publish verification gate fails, surfacing the failed gate verbatim.
- [ ] Skill B's run transcript shows `gh workflow run release-publish.yml ...` as the only mutation; grepping the transcript for `gh release edit --draft=false` finds no hit.
- [ ] Skill B reports the workflow run URL after dispatch and surfaces the run's current status without polling to completion (unless the operator opted in to wait mode, mirroring `pull-request-merge`).
- [ ] `release-automation` §Non-Goals (or §Relationship to other specs) cross-links to this spec as the local-skill counterpart for body curation and dispatch ergonomics.
- [ ] The `release-notes-audience-analysis` Acceptance Criteria line "reviewer can verify primary audience coverage before `release-publish.yml` is dispatched" is satisfied by Skill A's `## Audiences served` subsection.

## Open Questions

_All previously deferred open questions were settled on 2026-06-06: each provisional default is now the standing rule. The per-item decisions and rationale are preserved in git history (decision log, 2026-06-06)._
