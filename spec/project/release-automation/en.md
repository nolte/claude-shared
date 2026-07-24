# Release Automation

Status: draft
Portfolio-Scope: portfolio

## Context

The `branching-model` spec defines **how** releases propagate once published (`release-drafter` maintains a draft, a human publishes it, `release-cd-refresh-master.yml` fast-forwards `main`). What it currently leaves manual is the **Draft → Published** step itself: §Local release operation requires an operator to run `gh release edit <tag> --draft=false` (or click *Publish* in the web UI).

That manual step is the last non-automated link in the release chain and is the root cause of `spec-drift-audit` 2026-Q2 Finding #3: `v0.1.1` sits as Draft on `claude-shared`, so `main` HEAD can't be aligned with a published release. The portfolio-wide decision **rejects** manual release promotion as the fix for the audit finding; instead, this spec defines the automated promotion process, and the finding resolves once the automation has cut a real release.

This spec fills the gap between `release-drafter` (builds and maintains the draft) and `release-cd-refresh-master.yml` (reacts to `release: [published]`): the workflow that flips `draft: true → false` on demand, under guardrails, without a human CLI keystroke on the tag.

## Goals

- The Draft → Published transition happens through a reviewable, reproducible workflow—not through an operator editing a release via CLI or web UI.
- The human stays in the loop for the **decision** to release (when, what version), but the mechanics (publish call, tag handling, error checking) are codified.
- The automation refuses to publish anything it didn't receive from `release-drafter`, closing off the hand-crafted-tag failure mode already forbidden by `branching-model` §Local release operation.
- The process is portfolio-reusable: implemented once as a reusable workflow under `nolte/gh-plumbing`, consumed by every repository that follows `branching-model`.
- Spec-drift-audit `main`-alignment criteria become satisfiable by triggering the workflow, not by running `gh` commands directly against the tag.

## Non-Goals

- Publishing artifacts to external registries (npm, PyPI, container registries, HACS ZIP uploads)—those stay with repository-specific `release: [published]` packaging workflows as `project-structure` describes.
- Binary builds, signing, SBOM generation.
- Release-notes content generation—that remains `release-drafter`'s responsibility, fed by Conventional-Commits PR titles. For the audience analysis that governs what content those notes must cover, see the repository's release-notes audience-analysis conventions.
- Versioning policy (SemVer major/minor/patch derivation)—inherited from `release-drafter` configuration in `nolte/gh-plumbing:.github/commons-release-drafter.yml`.
- The hotfix flow—owned by `branching-model` `§Hotfix flow`, which settles it as a standard `fix/` pull request against `develop` followed by an ordinary patch release; out of scope here.
- Deprecating the manual `gh release edit --draft=false` path entirely; the manual path remains a documented fallback for incident response when the workflow itself is broken.
- Prescribing which ecosystems are included in the portfolio convention table for §Version-bearing files; the table grows as repos of new types enter the portfolio, each addition being a minor spec amendment rather than a new spec.

## Requirements

### Workflow existence and trigger

- **MUST** provide a dedicated workflow (canonical name: `.github/workflows/release-publish.yml`) that performs the Draft → Published transition; the publish step **MUST NOT** live inside `release-drafter.yml` or any other workflow whose primary responsibility is a different release phase
- **MUST** expose `workflow_dispatch` as a trigger so the release decision is a deliberate human action, auditable via GitHub's workflow-run history
- **MUST NOT** trigger on `push`, `pull_request`, `schedule`, or `release: [created]` in the baseline specification; additional triggers **MAY** be added per repository only when a dedicated Open Question has been resolved for that repository
- **MUST**, once `nolte/gh-plumbing` ships it, consume the reusable workflow at `nolte/gh-plumbing/.github/workflows/reusable-release-publish.yml`: flat path, sibling to `reusable-release-drafter.yml` and `reusable-release-cd-refresh-master.yml` so the portfolio's reusable-naming convention stays consistent; until that reusable exists, a local implementation that satisfies the Requirements below is acceptable and **MUST** be migrated on the reusable's first availability
- **MUST** pin any `nolte/gh-plumbing` reference to a release tag (matching the `project-structure` and `workflow-health` pinning rules)
- **SHOULD** declare a `concurrency` block (`group: release-publish`, `cancel-in-progress: false`) so two overlapping dispatches queue rather than racing on the `--draft=false` API call

### Operational contract

- **MUST** operate exclusively on a release that's currently in `draft: true` state and whose body was written by `release-drafter`: identified by matching the release tag to the most recent draft produced on `develop`
- **MUST** refuse to publish when no `release-drafter` draft exists, or when the draft's tag doesn't correspond to a commit reachable from `develop`
- **MUST** accept an optional `tag` input on `workflow_dispatch`; when multiple `release-drafter` drafts are open, the workflow **MUST** fail with an actionable message that lists all open drafts unless `tag` is provided, and **MUST** then publish only the draft whose tag exactly matches the input (no "newest wins" heuristic)
- **MUST NOT** create a new tag, rewrite an existing tag, or tolerate an out-of-band `git tag` + `git push --tags` sequence as a release source; the tag that the `release-drafter` draft carries is the tag that gets published, and any release whose tag didn't originate from the drafter **MUST** be rejected—this closes the failure mode already forbidden by `branching-model` §Local release operation and observed historically as tag/release-name drift across the portfolio
- **MUST NOT** alter the release body inside this workflow; body edits, if needed, **MUST** happen before the run via `gh release edit <tag>` (title/body/tag adjustments per `branching-model` §Local release operation) or via `release-drafter` re-runs
- **MUST** surface the target tag, title, and a diff summary of the body in the workflow run output so the human triggerer can verify before the irreversible step
- **SHOULD** support a `dry_run: true` input on `workflow_dispatch` that performs every validation step but stops short of the actual `--draft=false` call
- **SHOULD** fail explicitly (non-zero exit, actionable message) when `release-cd-refresh-master.yml` is absent or disabled, because publishing without the downstream refresh would leave `main` out of sync with the latest release

### Version-bearing files

A *version-bearing file* is a file tracked in git whose content declares, at a well-defined location, the current release version of the project. Every such file must equal the published release tag at the release's target SHA. Repositories may have zero, one, or many such files.

**Portfolio convention table.** The default version-bearing files per repo type are:

| Repo type | File | Selector | Value transform |
|---|---|---|---|
| Claude Code plugin | `.claude-plugin/plugin.json` | `$.version` | strip leading `v` if repo convention omits it |
| Claude Code plugin | `.claude-plugin/marketplace.json` | `$.metadata.version` and `$.plugins[].version` | strip leading `v` if repo convention omits it |
| Python package | `pyproject.toml` | `[project].version` | strip leading `v` if repo convention omits it |
| Node.js package | `package.json` | `$.version` | strip leading `v` if repo convention omits it |
| HACS integration | `custom_components/<name>/manifest.json` | `$.version` | strip leading `v` if repo convention omits it |

- **MUST** treat this table as the default set for any repo whose type matches one of the listed rows; no repo-level declaration is needed to opt in.
- **MUST** declare the full version-bearing file list at `.github/release-automation.yml` when a repo deviates from its ecosystem's convention (extra files, different selectors, an additional repo-local file that holds the version). The declared list replaces the default, not extends it—explicit is better than implicit.
- **MAY** have no version-bearing files at all (for example, pure git-tag-based versioning like Go modules); the §Version-bearing file alignment verification step treats zero declared files as nothing to align.
- **MUST NOT** add a repo-type row to this table without a corresponding amendment PR to this spec; ad-hoc conventions drift the portfolio.

Selectors use JSONPath-style notation for JSON and YAML files, TOML-path notation for TOML files. The value transform is applied to the tag before the value is written or compared: `strip leading v if repo convention omits it` means `v0.1.1` becomes `0.1.1` only when the existing file value lacks the `v` prefix; if the file already uses a `v` prefix the tag is written verbatim.

### Version-bearing file alignment

Every published release **MUST** land on a commit whose tree has every version-bearing file (§Version-bearing files) equal to the target tag under its value transform. The alignment commit **MUST** use the Conventional-Commits subject `chore(release): <tag>` and **MUST** land on `develop` before the `--draft=false` call.

The alignment happens via one of two equivalent paths. Both paths produce the same end state; they differ only in which credential creates the commit.

#### Primary path: Workflow-driven

Applicable when the workflow has access to a credential that bypasses `develop`'s branch protection (a GitHub App installation token, or a PAT designated as a bypass actor). Not yet usable in this portfolio: the App/PAT is provisioned via `nolte/gh-plumbing` (same portfolio-level remediation as `spec/project/workflow-health/` §Known platform constraints).

- **MUST** read the version-bearing file list (default from §Version-bearing files, or the list declared at `.github/release-automation.yml` when the repo deviates) and update each file to the target tag under its transform
- **MUST** commit the aggregate update as `chore(release): <tag>` on `develop`, authored by the bypass credential
- **MUST** push the commit to `develop` via the bypass credential, respecting `enforce_admins: true` (the bypass is declared, not stolen)
- **MUST NOT** be enabled in a repository until the portfolio App/PAT is installed and `.github/settings.yml` explicitly names the credential as a bypass actor; otherwise the push fails and the fallback path **MUST** be used

#### Fallback path: Operator-driven

Applicable when only `GITHUB_TOKEN` is available and `develop` is fully protected (the current portfolio default).

- **MUST** be executed by a maintainer opening a PR titled `chore(release): <tag>` that updates every version-bearing file to the target tag
- **MUST** pass every required status check declared for `develop` in `.github/settings.yml`
- **MUST** be squash-merged via the GitHub UI by the maintainer, **not** via the `automerge` label; an `automerge`-label merge is authenticated with `GITHUB_TOKEN` and breaks the release-drafter cascade per `spec/project/workflow-health/` §Known platform constraints
- **MUST** be followed by a `workflow_dispatch` of `release-publish.yml`; the workflow detects that the manifest is already aligned, skips its own commit step, realigns `target_commitish` on the draft, and flips `draft: false`

#### Pre-publish verification (both paths)

- **MUST** verify before `--draft=false` that every version-bearing file at the draft's target SHA equals the target tag under its transform; any drift is a publish-blocking condition the workflow surfaces and refuses to proceed
- **MUST** accept a pre-aligned file if-and-only-if the last commit touching that file on `develop` has a subject that **starts with** `chore(release): <tag>`; this allows the `(#N)` suffix GitHub appends on squash-merge, so a fallback-path squash-merge commit with subject `chore(release): v0.1.1 (#21)` passes the check
- **MUST** reject any other pre-aligned state as a forbidden manual bump; the skill-authoring contract forbids feature PRs from touching the version field, so the only acceptable pre-alignment sources are a prior run of the primary path or a fallback-path `chore(release): <tag>` PR merge
- **SHOULD** implement the verification inside the reusable `reusable-release-publish.yml` so consumers inherit the behavior without repeating it per repository
- **SHOULD** derive the value written into (primary path) or compared against (both paths) the version field from the tag by stripping a leading `v` if the repository's existing convention omits it, matching whatever the current file already uses; the workflow **MUST NOT** silently rewrite the convention

### Inheritable spec payload

The portfolio-inherited spec layer lets a consumer repository reference the hub's portfolio-scoped specs at a pinned release tag instead of copying them; that mechanism defers the marketplace-payload packaging to this spec, so the shipping guarantee is declared here.

- **MUST** ship the repository's `spec/` corpus as part of the plugin payload, so that for an installed hub plugin every spec whose canonical file carries a `Portfolio-Scope: portfolio` header is readable at `${CLAUDE_PLUGIN_ROOT}/spec/` (the bundled-asset path convention every plugin skill already uses). The plugin source root is the resolver entry point and `spec/` is delivered beneath it.
- **MUST NOT** exclude `spec/` from the plugin payload through a packaging filter—a `files` allowlist in a plugin manifest, a `.gitattributes export-ignore` rule, an `.npmignore`-style exclusion, or any equivalent. The corpus ships wholesale; the `Portfolio-Scope:` header is the only inheritability gate, applied at resolution time, never at packaging time. The non-`portfolio` (`local`) specs ship too but are simply never resolved by a consumer.
- **MUST** keep this payload tag-pinned to the plugin release line: a consumer's pinned `ref` selects the installed hub-plugin release, and the `spec/` corpus resolved from that release is the regenerable cache the consumer references—never a copy committed into the consumer's own tree.

### Permissions and protection

- **MUST** run with `contents: write` and nothing broader; specifically **MUST NOT** request `actions: write`, `pull-requests: write`, or `id-token: write` unless explicitly justified in the workflow comments
- **MUST NOT** bypass `main` branch protection; the workflow's job is to publish a release, which then triggers `release-cd-refresh-master.yml`: the existing workflow already has the proper scoped permission to update `main`
- **MUST** use `GITHUB_TOKEN` on the fallback path (the workflow only needs read + release-edit permissions in that mode); **MUST** use the portfolio App installation token (or designated PAT) on the primary path, per §Version-bearing file alignment
- **MUST NOT** use a PAT that isn't explicitly declared as a branch-protection bypass actor in `.github/settings.yml`; undeclared PATs bypass audit trails
- **MUST** recognize that a `release: published` event emitted by this workflow under `GITHUB_TOKEN` doesn't cascade to `release-cd-refresh-master.yml` as a new workflow run: deterministic GitHub Actions platform behavior, classified under `spec/project/workflow-health/` §Known platform constraints; the same App-token remediation that enables the primary path above also lifts this cascade constraint, so both are solved by a single portfolio-level fix in `nolte/gh-plumbing`

### Release notes categorization

- **MUST** exclude `chore(release): <tag>` commits and PRs from `release-drafter` categorization so a release draft doesn't list its own version-alignment PR as a changelog entry
- **MUST** implement the exclusion portfolio-wide in `nolte/gh-plumbing:.github/commons-release-drafter.yml` (title-pattern exclusion or a label convention the drafter config filters out), not per-repo
- **SHOULD** align the exclusion with any existing Conventional-Commits filter already in the commons drafter config so the rule pattern stays consistent

### Relationship to other specs

- **MUST** update `branching-model` §Release flow and §Local release operation by in-place edits—no new dedicated §Automated release promotion section—so that: (a) the automated workflow is named as the primary Draft → Published path, and (b) the manual `gh release edit --draft=false` sequence is explicitly labeled a fallback for incident response
- **MUST NOT** re-specify anything already covered by `branching-model` (tag origin, `main` refresh, workflow pinning)—reference instead
- **SHOULD** resolve the Open Question in `project-structure` (line 164 at the time of writing) by cross-linking from `project-structure` §Release and documentation workflows into this spec
- **MUST** be cross-referenced by `release-artifact` as the authority for the Draft → Published transition. `release-artifact` §Dispatch boundary to release machinery routes sprint-side artefact validation outcomes into the workflow this spec governs; the boundary is one-way (this spec is the lower layer, `release-artifact` is the higher one), and the consuming spec **MUST NOT** redefine any rule declared here
- The local-skill counterpart to this workflow lives in [`spec/project/release-skill-layer/`](../release-skill-layer/en.md): Skill A (`release-notes-curate`) handles body curation via `gh release edit` outside this workflow, and Skill B (`release-publish-trigger`) is the local ergonomic entry point that validates every §Pre-publish verification gate and then dispatches this workflow via `gh workflow run`. That spec **MUST NOT** call `gh release edit --draft=false`; the only publish path is dispatching this workflow.

### Observability and audit

- **MUST** emit the tag name, the triggerer's GitHub username, the workflow run URL, and the `release-drafter` draft's `created_at` timestamp to the job summary, so post-release audits can trace the publish back through this workflow
- **SHOULD** append a one-line entry to the repository's audit-trail surface (if a convention emerges—currently not standardized); until then, GitHub's native run history is the audit source
- **MUST** make `gh run list --workflow=release-publish.yml` the canonical CLI for inspecting recent publish activity—analogous to the `release-drafter.yml` and `release-cd-refresh-master.yml` inspection commands in `branching-model` §Local release operation

## Acceptance Criteria

- [ ] `.github/workflows/release-publish.yml` exists in every repository that has `release-drafter.yml` and `release-cd-refresh-master.yml`
- [ ] The workflow declares `on: workflow_dispatch:` and doesn't declare `push`, `pull_request`, or `schedule` triggers
- [ ] The workflow's top-level or job-level `permissions:` block requests `contents: write` and no broader scope
- [ ] The workflow either `uses:` `nolte/gh-plumbing/.github/workflows/reusable-release-publish.yml@<tag>` or is a temporary local implementation with a tracked migration Issue
- [ ] Any `uses: nolte/gh-plumbing/...` reference is pinned to a release tag, not a moving branch
- [ ] The workflow refuses to run (visible failure in the run log) when invoked while no `release-drafter` draft is open
- [ ] A `dry_run: true` dispatch input is present and performs validation without flipping `draft: false`
- [ ] After a successful publish run, `gh release view <tag> --json isDraft` returns `{"isDraft": false}` for the published tag
- [ ] After a successful publish run, `gh run list --workflow=release-cd-refresh-master.yml --limit 1` shows a run started within 5 minutes of the publish run, confirming the downstream refresh fired; if it didn't start, the publish is considered incomplete and **MUST** be triaged under `workflow-health`
- [ ] `branching-model` §Local release operation has been updated to name `release-publish.yml` as the primary path and `gh release edit <tag> --draft=false` as a fallback
- [ ] The last three published releases in any repository adopting this spec were produced by the `release-publish.yml` workflow, verifiable via `gh run list --workflow=release-publish.yml --limit 10`
- [ ] For every published release of a repository that declares version-bearing files (per §Version-bearing files default or override), each declared file at the release's target SHA equals the release tag under its declared transform, and a `chore(release): <tag>` commit on `develop` produced that alignment before the publish run, whether via the primary or fallback path
- [ ] For the last three published releases on any repo adopting this spec, the `chore(release): <tag>` commit subject on `develop` (as viewed via `git log -1 --pretty=%s`) starts with `chore(release): <tag>`, confirming the guard's prefix-match acceptance criterion handles both primary-path commits and fallback-path squash-merges with `(#N)` suffix
- [ ] `nolte/gh-plumbing:.github/commons-release-drafter.yml` excludes `chore(release): <tag>` commits or PRs from release-notes categorization (§Release notes categorization)
- [ ] No published release in the adoption window has a `release-drafter` draft that remained after publish (confirming the workflow consumed the intended draft rather than creating a parallel one)
- [ ] At a published release tag, the installed `nolte-shared` plugin exposes `spec/` under `${CLAUDE_PLUGIN_ROOT}/spec/` with no packaging filter excluding it, so every spec whose canonical file carries `Portfolio-Scope: portfolio` is resolvable there for an inheriting consumer (§Inheritable spec payload)

## Open Questions

None at this time—all initial drafting questions were resolved during this spec's authoring. For traceability, the decisions are:

- **Triggers**: limited to `workflow_dispatch`; label-based and scheduled triggers are out of scope (additional attack surface; conflicts with "human decides when to ship").
- **Canonical reusable path**: `nolte/gh-plumbing/.github/workflows/reusable-release-publish.yml`, flat path consistent with the existing `reusable-release-drafter.yml` / `reusable-release-cd-refresh-master.yml` naming.
- **Multi-draft behavior**: fail with actionable message unless the dispatcher passes a `tag` input; no "newest-wins" heuristic.
- **`branching-model` integration**: in-place edit of §Release flow + §Local release operation; no new dedicated section.
- **Post-publish sanity checks**: encoded as Acceptance Criteria (`isDraft: false` and `release-cd-refresh-master.yml` run within 5 minutes), not as SHOULDs.
- **Two-path alignment**: primary (workflow-driven with bypass credential) vs fallback (operator PR + UI squash-merge); both paths land the same `chore(release): <tag>` commit shape. Primary is the portfolio target; fallback is the operative path today until the portfolio App/PAT ships via `nolte/gh-plumbing`.
- **Override config path**: `.github/release-automation.yml` for repos that deviate from the §Version-bearing files default; consistent with other `.github/*.yml` portfolio configs.
- **Portfolio convention table scope**: full list (Claude plugin, Python, Node, HACS) documents portfolio vision; rows grow organically as new ecosystems enter via minor spec amendments.
- **Pre-bump guard**: prefix-match on `chore(release): <tag>`, accepting the `(#N)` suffix GitHub appends on squash-merge.

## Sources

The `GITHUB_TOKEN`-does-not-cascade platform behaviour in §Permissions and protection is an author-time external assertion triangulated per `spec/claude/research-triangulate/` §Author-time assertions (author-time tier: at least three independent sources, ordered Primary-first). It's classified and cross-referenced under `spec/project/workflow-health/` §Known platform constraints, which cites the same sources. Retrieval date for every web source below: 2026-07-24.

- **GitHub Actions doesn't trigger new workflow runs from events created with the automatic `GITHUB_TOKEN`, except `workflow_dispatch` and `repository_dispatch`**: GitHub Docs, "Triggering a workflow" (Primary), `https://docs.github.com/en/actions/using-workflows/triggering-a-workflow`; GitHub Changelog, "Use the GITHUB_TOKEN with `workflow_dispatch` and `repository_dispatch`" (Primary), `https://github.blog/changelog/2022-09-08-github-actions-use-github_token-with-workflow_dispatch-and-repository_dispatch/`; GitHub community discussion #25702, *"Push from Action does not trigger subsequent action"* (Secondary), `https://github.com/orgs/community/discussions/25702`
- **Empirical portfolio evidence**: the portfolio's own `v0.1.5` release run confirmed this behaviour directly, when a `release: published` event emitted by this workflow under `GITHUB_TOKEN` didn't cascade to `release-cd-refresh-master.yml` as a new run (Primary, direct observation; recorded in the release-process verification for `nolte/claude-shared`).
