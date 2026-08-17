# Workflow Health

Status: draft
Portfolio-Scope: portfolio

## Context
GitHub Actions workflows gate every path through the portfolio: pull-request merges (`pr-lint.yml`, CI), release drafting (`release-drafter.yml`), `main` refresh on release (`release-cd-refresh-master.yml`), documentation delivery (`release-cd-deliver-docs.yml`), and optional packaging workflows. When any of them starts failing and the failure isn't caught, merges stall, releases don't ship, and `main` drifts away from the last published tag. Existing specs declare **which** workflows must exist (`branching-model`), **where** they live and how they're pinned (`project-structure`), and **what they gate** for PRs (`pull-request-workflow`). None of them declares the **operational process** that keeps those workflows reliably green and responds when they turn red. This spec fills that gap so that workflow failures are observed, classified, and fixed through the same PR gate as any other change—never silenced, never bypassed.

## Goals
- A failing workflow run on `develop` or `main` is never silently ignored—every failure is either fixed, explicitly disabled with an owner, or classified as a known transient and tracked
- Every remediation flows through the standard pull-request path (`fix/` branch, Conventional-Commits title, required checks green): there is no admin-override shortcut
- Root-cause triage happens before re-runs—a red workflow is never "fixed" by clicking "Re-run" until it happens to pass
- Upstream drift (broken tags in `nolte/gh-plumbing`, changed reusable workflows) is surfaced and resolved by bumping the pin, not by unpinning
- The process is identical across repositories so humans and AI agents can respond to a failure without per-repo onboarding

## Non-Goals
- Which workflows must exist in a repository (covered by the `branching-model` and `project-structure` specs)
- PR description structure and CI-gating mechanics (covered by the `pull-request-workflow` spec)
- The internal content of any specific workflow file (job steps, matrix strategy, caching)
- Incidents caused entirely outside the repository—GitHub Actions platform outages, Probot app downtime, registry outages—beyond the observation that they must be ruled out before attributing a failure to code
- Release-artifact contents, changelog generation, versioning policy
- Test-authoring conventions or flake-root-cause analysis of any specific test (this spec prescribes only that flakes are tracked)

## Requirements

### Visibility and detection
- **MUST** surface the status of every workflow declared as a required status check on `develop` via a CI badge in `README.md`, as already mandated by the `readme-structure` spec; the badge set **MUST** match the required-checks set declared in `.github/settings.yml`
- **MUST** keep GitHub's default workflow-failure notifications enabled for at least one maintainer of the repository, or route notifications to a portfolio-wide channel that a maintainer monitors
- **SHOULD** treat a red required status check on `develop` as a merge-flow incident—further merges into `develop` are blocked by branch protection anyway, so the remedy is to fix the failure, not to waive the check
- **SHOULD** treat a red workflow on `main` (for example a failing `release-cd-refresh-master.yml` run) as a release-integrity incident, because `main` is release-presentation per the `branching-model` spec and drift from the latest release tag is a bug

### Triage before remediation
- **MUST**, on the first failure of a previously-green workflow, classify the root cause before any re-run into exactly one of:
  1. **defect**: code or configuration change in this repository broke the workflow
  2. **flake**: same commit SHA passes on re-run with no code change and no infrastructure signal
  3. **infra / platform**: upstream provider outage, registry 5xx, rate-limit, network—reproducible only in a narrow time window; **or** a deterministic platform behaviour this repository can't configure away, per §Known platform constraints. The two differ in duration, not in class: neither is a defect in this repository, and neither is fixed by a re-run
  4. **stale pin**: a `nolte/gh-plumbing` (or other reusable-workflow) tag pinned in this repository no longer matches the expected contract; newer tag exists with the fix
  5. **secret / credential drift**: a token, deploy key, or OIDC trust expired or was rotated
  6. **other**: explicitly labelled, with a short note in the fix PR explaining why it doesn't fit the five categories
- **MUST NOT** re-run a failed workflow more than once without a recorded triage classification; repeated blind re-runs are drift
- **MUST** capture the classification in the eventual fix PR's **Risk / rollout notes** section (per the `pull-request-workflow` spec) so failure patterns are visible across PR history
- **MAY** open a tracking GitHub Issue for non-urgent follow-up (documentation of a known flake, a planned upstream bump) instead of an immediate fix PR, provided the Issue names an owner

### Known platform constraints

GitHub Actions intentionally doesn't trigger downstream workflow runs from events produced by a step authenticated with `GITHUB_TOKEN`, with the exception of `workflow_dispatch` and `repository_dispatch`. This is a deterministic platform behavior, not a transient failure, and it has to be planned for rather than triaged on each occurrence.

- **MUST** classify as a known platform constraint (triage tag `infra`) any downstream workflow failing to fire because its triggering event was produced by a `GITHUB_TOKEN`-authenticated step elsewhere in the portfolio's automation chain. Relevant chains observed to date:
  - `release-drafter.yml` (trigger: `push: develop`) doesn't fire when the push to `develop` was produced by an `automerge.yaml` squash-merge authenticated with `GITHUB_TOKEN`
  - `release-cd-refresh-master.yml` (trigger: `release: published`) doesn't fire when the publish step was produced by `release-publish.yml` authenticated with `GITHUB_TOKEN`
  - Any other chain where one workflow's output event is another workflow's input trigger and the producer uses `GITHUB_TOKEN`
- **MUST** remediate this constraint at the portfolio level—in the `nolte/gh-plumbing` reusable workflows—rather than in each consumer repository, because the constraint applies uniformly to every consumer of those reusable workflows. The acceptable remediation is to authenticate the downstream-triggering step with a credential whose events GitHub considers user-initiated (a GitHub App installation token or a PAT with appropriate scopes), not `GITHUB_TOKEN`.
- **MUST NOT** work around this constraint by replacing `GITHUB_TOKEN` with a personal PAT directly in a consumer repository's workflow—the fix belongs upstream in the reusable, so every consumer benefits from one correctly-scoped credential instead of a per-repository PAT collection.
- **SHOULD** document any interim workaround a repository uses (a user-authored commit to re-fire `release-drafter`, a manual fast-forward of `main` to catch up a missed `release-cd-refresh-master.yml` run, a manual `workflow_dispatch` if the downstream workflow provides one) as a short note in `README.md`, with a reference to the upstream `nolte/gh-plumbing` tracking issue.
- **MUST NOT** count a `workflow_dispatch` fallback as an available workaround until it has been exercised on that trigger. Declaring the trigger isn't the same as it working: the called workflow's inputs may default to payload fields the fallback event doesn't carry, so the fallback fails on exactly the path this constraint made necessary—and in the workflow file, a fallback that was never exercised looks identical to one that works. The input-completeness rule this follows from is owned by `spec/project/github-actions-best-practices/` §E.
- **MUST** recognize that the same App-token / PAT remediation that lifts this cascade constraint also enables the primary path of `spec/project/release-automation/` §Version-bearing file alignment; both constraints are solved by a single portfolio-level fix in `nolte/gh-plumbing`, not two separate fixes.

The same family carries a second, independent constraint, on the push side rather than the trigger side. GitHub rejects a push from a GitHub App identity that creates or updates any file under `.github/workflows/` unless the installation holds the `workflows` permission. `GITHUB_TOKEN` is such an identity—the GitHub Actions app—and the workflow `permissions:` block exposes no `workflows` scope, so no permissions declaration can lift it.

- **MUST** classify as a known platform constraint (triage tag `infra`) a push rejected with `refusing to allow a GitHub App to create or update workflow ... without 'workflows' permission`, rather than as a branch-protection or credential defect.
- **MUST NOT** infer from an unprotected target branch that such a push will succeed. The rejection is independent of branch protection: it was observed pushing to a branch carrying no protection rule at all.
- **MUST** expect this constraint to surface intermittently rather than on every run, because it triggers only when the diff between the target branch and the source ref happens to touch `.github/workflows/`. A presentation-branch refresh that succeeded while the branch was current fails once the branch has fallen far enough behind to carry a workflow change—so a green history is no evidence the next refresh will pass.
- **MUST** remediate it through the same credential that lifts the cascade constraint above, minted in the `nolte/gh-plumbing` reusable, and **MUST** widen that credential's scope to cover workflow files: an App installation needs `workflows: write` in addition to `contents: write`, and a PAT on the alternative branch of that pair needs the classic `workflow` scope. `contents: write` alone satisfies neither.

### Remediation path
- **MUST** route every workflow fix through the standard pull-request path declared by the `pull-request-workflow` spec: `fix/` branch prefix, Conventional-Commits title (type `fix`), all required checks green before merge
- **MUST NOT** bypass branch protection to merge a workflow fix; `enforce_admins: true` on `develop` (mandated by the `pull-request-workflow` spec) has no exception path, and a persistently-broken required check is remedied by a PR against `.github/settings.yml`, not by an admin override
- **MUST** fix the root cause rather than masking it—the following patterns are prohibited as remediation:
  - adding `continue-on-error: true` to a required-check job to turn a red job green
  - moving a failing job out of the required-checks set in `.github/settings.yml` without opening an Issue that tracks its re-inclusion and names an owner
  - repointing a `nolte/gh-plumbing` reusable-workflow reference from a release tag to a branch (for example `@main`) to pick up an unreleased fix
  - commenting out assertion steps or swallowing non-zero exit codes inside a workflow step
- **MUST** keep every `uses: nolte/gh-plumbing/.github/workflows/...` reference pinned to a release tag (per the `project-structure` and `branching-model` specs) even while remediating; if the currently-pinned tag is broken, the fix is to bump to a newer tag
- **MAY** temporarily disable a broken **non-required** workflow by restricting its `on:` triggers or by disabling it in the Actions UI, provided a tracking Issue is opened the same day naming an owner and a target re-enablement criterion; temporarily disabling a **required** workflow isn't permitted—the required-checks set is the source of truth

### Specialized-agent dispatch for remediation
The hands-on implementation work of a workflow fix—editing the broken artifact, bumping a pin, rotating a secret, authoring the fix PR—is delegated to the most specialized Claude Agent available. The generalist Claude's responsibility is classification and dispatch, not hands-on editing.

- **MUST** dispatch the implementation work of a remediation to the most specialized available Claude Agent via `Agent(subagent_type=<name>)` (as governed by the `agent-management` spec), when at least one agent's `description` matches the triage classification or the concrete failing artifact (workflow YAML, Renovate pin bump, secret rotation, test defect, documentation build, etc.)
- **MUST NOT** have the dispatching Claude perform specialized remediation work itself when a matching specialized agent exists; the generalist triages, dispatches, and verifies the result—it doesn't replace the specialized agent
- **MUST** treat a failure class that has recurred three or more times without a matching specialized agent as a portfolio gap requiring action: either author a new agent per the `agent-management` spec (`distribution: plugin` when the pattern recurs across repositories, `distribution: project` when the pattern is repository-local) or extend an existing agent's `description` so future failures of the same class route to it automatically; failure classes with fewer than three recurrences **SHOULD** be tracked as candidates for the same treatment
- **SHOULD** prefer a plugin-distributed agent (`distribution: plugin`) over a project-local agent for remediation patterns that recur across the portfolio, so the remediation expertise travels with the `nolte-shared` plugin rather than being copied per repository
- **SHOULD** record in the fix PR's **Risk / rollout notes** section (alongside the triage classification, per the `pull-request-workflow` spec) which specialized agent produced the fix, or note that no matching specialized agent exists and a generalist handled it—this makes portfolio-wide coverage gaps visible. **Precedence note:** a portfolio continuous-improvement policy may raise this same record to a **MUST** for every in-scope finding, workflow-health findings included; where such a policy is in force, the stronger requirement wins, so a workflow-fix PR that omits the specialist/originating-source record is non-conformant under that policy even though this bullet alone is only a SHOULD. The triage, classification, and remediation *process* defined in this spec remain this spec's authority and aren't overridden by that carve-out.
- **MAY** chain multiple specialized agents in sequence when a single remediation spans responsibilities (for example: a workflow-YAML-fix agent to correct syntax, then the `pull-request-create` skill to open the fix PR); each artifact in the chain obeys its own declared `tools` scope
- **MUST NOT** permit a dispatched specialized agent to bypass any gate from this spec or the `pull-request-workflow` spec—the agent ships its change through the same `fix/` PR flow, with all required checks green and no admin override

### Upstream (`nolte/gh-plumbing`) drift
- **MUST** treat a new release of `nolte/gh-plumbing` as a candidate bump, not an automatic one; the bump is performed by updating the pinned tag in every affected `uses:` line and letting the standard PR gate validate the result
- **SHOULD** rely on Renovate to propose the tag bump as a PR; the Renovate PR itself goes through the gate like any other change
- **MUST NOT** enable Renovate automerge for `nolte/gh-plumbing` tag bumps even when every required check is green—a human acknowledgement is the portfolio-wide rollback signal for a reusable-workflow change, and its cost (seconds) is less than the cost of a reusable-workflow defect fanning out to every consumer repository; other Renovate automerge rules **MAY** continue unchanged for non-`nolte/gh-plumbing` packages
- **MUST NOT** skip the PR step for a version bump of `nolte/gh-plumbing` references just because "it's only a tag change"; the gate exists to catch exactly this class of breakage

### Probot app availability
- **SHOULD**, before attributing a failure of `release-drafter.yml`, settings-sync, or label-sync to code, verify that the underlying Probot apps (`settings`, `release-drafter`, `boring-cyborg`, `stale`) are still installed on the repository—the `project-structure-apply` audit checks this
- **MUST** treat "Probot app uninstalled" as a configuration-drift incident distinct from a code defect; the fix is to re-authorize the app, not to change repository code

### Flake handling
- **MUST** identify a run as a flake only on reproducible evidence—a re-run of the same commit SHA with no code change returns green and no upstream infra signal explains the first failure
- **MUST** track known flakes in a repository-visible artifact so patterns are visible rather than absorbed silently into the re-run loop; the portfolio-wide default is a `FLAKES.md` at the repository root, and a dedicated set of GitHub Issues labelled `flake` is accepted as an equivalent when the repository already centralizes tracking in Issues
- **MUST NOT** maintain both forms (`FLAKES.md` and a `flake`-labelled Issue set) for the same repository—one or the other is authoritative, chosen consciously and linked from `CLAUDE.md` or `README.md`
- **SHOULD** treat a flake that trips a required check in more than roughly one in ten runs as a defect rather than a transient—at that rate the flake blocks merges materially and deserves a real fix, not a tracking entry

### Cancellation rates
A lane whose runtime exceeds the cadence of its triggering event never reaches a verdict under cancel-in-progress: every new push cancels the run the previous push started, most runs end `cancelled`, and the lane reports nothing while looking active. Observed in a consuming project: one per-push security-scan lane cancelled in 85% of its runs, a second in 44%—both appeared healthy because a cancelled run is neither red nor green.

- **MUST** observe, for every gating or reporting lane, the cancellation rate over its recent runs (guide value: the last 20, for example `gh run list --workflow <file> --limit 20`), analogous to the flake-rate threshold above
- **MUST** treat a lane the majority of whose runs end `cancelled` as equivalent to a lane that doesn't exist: it delivers no verdict, and any claim resting on it ("the scan runs on every PR") is unbacked until the rate is remediated
- **MUST** remediate by re-placing the trigger so the event cadence matches the job runtime (for example once per merged commit on the target branch, or a schedule), **not** by setting `cancel-in-progress: false`—that only queues stale runs, consumes capacity, and delivers obsolete verdicts; the cancel-on-new-run recommendation for pre-merge workflows in `spec/project/github-actions-best-practices/` §F presupposes that the runtime fits the cadence

### Time expectations
- **SHOULD** acknowledge a failed required check on `develop` within one business day of the failure appearing and have a fix PR open within two business days
- **SHOULD** acknowledge a failed release-flow workflow on `main` (for example `release-cd-refresh-master.yml`) with higher urgency than a `develop` failure, because it blocks the next release from presenting correctly
- **MAY** extend these windows when the repository is explicitly on low-maintenance status, provided that status is declared in `README.md` or `CLAUDE.md` so future readers understand why red checks linger

### Third-party required checks
Required status checks on `develop` may include providers that aren't GitHub Actions workflows—SaaS code-quality bots, security scanners, coverage reporters, signed-commit verifiers. The same operational rules apply.

- **MUST** apply the triage classifications and the remediation path of this spec to third-party required status checks the same way as to GitHub Actions workflows—the PR gate, the no-override rule, the pinned-tag discipline (where analogous), and the specialized-agent dispatch all apply identically
- **MUST** declare any removal or deactivation of a third-party required check as a PR against `.github/settings.yml`, not as a change made through the provider's own UI alone; UI-only changes are drift and have to be reconciled back into the file
- **MUST** treat an outage of a third-party check provider as `infra / platform` for triage purposes, not as `defect`
- **MAY** use the provider's own "disable check" mechanism in place of an `on:`-trigger restriction (which doesn't apply outside Actions) when pausing a **non-required** third-party check; a tracking Issue with an owner and re-enablement criterion is still required, exactly as for Actions workflows

### Auditing
- **SHOULD** periodically review `gh run list --status failure --branch develop --limit 20` and `gh run list --status failure --branch main --limit 20` to detect a backlog of unresolved failures that slipped past notifications
- **SHOULD** include a workflow-health pass in any portfolio audit that already visits `.github/workflows/` (for example the `project-structure-apply` skill); the audit cross-checks that no required-check workflow is currently red at HEAD without a fix PR in flight

## Acceptance Criteria
- [ ] `README.md` CI badges cover every workflow listed as a required status check for `develop` in `.github/settings.yml`; the two sets match exactly
- [ ] `gh run list --status failure --branch develop --limit 20` shows no failed run older than two business days that isn't either (a) superseded by a green run on a later SHA or (b) covered by an open `fix/` PR
- [ ] `gh run list --status failure --branch main --limit 20` shows no failed run of a release-flow workflow without either a resolution commit on `develop` or an open tracking Issue
- [ ] No workflow file in `.github/workflows/` contains `continue-on-error: true` on a step or job that belongs to the required-checks set declared in `.github/settings.yml`
- [ ] Every `uses: nolte/gh-plumbing/.github/workflows/...` reference in `.github/workflows/` resolves to a release tag (matches `@v[0-9]+`), not to a branch name
- [ ] For the last 10 PRs that touch `.github/workflows/` or pin bumps of `nolte/gh-plumbing`, every one was merged through the standard PR flow (squash-merge, required checks green, no admin override)
- [ ] The repository's Renovate configuration doesn't automerge `nolte/gh-plumbing` tag bumps—either no automerge rule applies to that dependency, or the rule explicitly excludes `nolte/gh-plumbing`
- [ ] If the repository declares any third-party required status check for `develop`, its removal or deactivation is reflected in `.github/settings.yml`, not only in the provider's UI
- [ ] For the last 10 workflow-fix PRs, the **Risk / rollout notes** section names the triage classification (`defect`, `flake`, `infra`, `stale pin`, `secret drift`, or `other` with a short note)
- [ ] For the same 10 workflow-fix PRs, the **Risk / rollout notes** section names either the specialized Claude Agent that produced the fix (via `Agent(subagent_type=…)`) or records that no matching specialized agent exists and a generalist handled it
- [ ] When a failure class has recurred three or more times and been handled by a generalist each time, either a specialized agent now exists in the plugin (per the `agent-management` spec) or an open Issue tracks its creation with a named owner
- [ ] Any temporarily-disabled workflow (restricted `on:` triggers, commented job, disabled in the Actions UI) is accompanied by a tracking Issue naming an owner and a re-enablement criterion; no required workflow appears in this state
- [ ] A known-flake register exists in the repository: `FLAKES.md` at the repository root or a `flake`-labelled Issue set, but not both—whenever at least one flake has been observed and acknowledged; the register is referenced from `CLAUDE.md` or `README.md` so it's discoverable
- [ ] No gating or reporting lane ends `cancelled` in the majority of its last 20 runs; where one does, an open fix PR or tracking Issue re-places its trigger to match the event cadence rather than setting `cancel-in-progress: false`
- [ ] Every `workflow_dispatch` fallback the repository documents as a workaround for a known platform constraint has at least one run recorded against that trigger; a declared-but-never-dispatched fallback isn't counted as available
- [ ] No push rejected with `refusing to allow a GitHub App to create or update workflow ... without 'workflows' permission` is classified as `secret drift` or `defect` in its fix PR's **Risk / rollout notes**; the recorded class is `infra / platform`
- [ ] Where a repository refreshes a presentation branch from a release ref, the credential that performs the push carries workflow-file scope (App installation `workflows: write`, or a PAT with the classic `workflow` scope), or the repository records why its refresh diff can never touch `.github/workflows/`
- [ ] `.github/settings.yml` still declares the full required-checks set for `develop` as code; no required check has been silently dropped to work around a persistent failure

## Open Questions
- _None at this time; all drafting questions have been resolved._

## Sources

Both platform behaviours in §Known platform constraints are author-time external assertions triangulated per `spec/claude/research-triangulate/` §Author-time assertions (author-time tier: at least three independent sources, ordered Primary-first). The cascade assertion is cross-referenced from `spec/project/release-automation/` §Permissions and protection, which cites the same sources. Retrieval date for the cascade sources: 2026-07-24; for the `workflows`-permission sources: 2026-08-17.

- **GitHub Actions doesn't trigger new workflow runs from events created with the automatic `GITHUB_TOKEN`, except `workflow_dispatch` and `repository_dispatch`**: GitHub Docs, "Triggering a workflow" (*"events triggered by the GITHUB_TOKEN ... will not create a new workflow run"*) (Primary), `https://docs.github.com/en/actions/using-workflows/triggering-a-workflow`; GitHub Changelog, "Use the GITHUB_TOKEN with `workflow_dispatch` and `repository_dispatch`" (Primary), `https://github.blog/changelog/2022-09-08-github-actions-use-github_token-with-workflow_dispatch-and-repository_dispatch/`; GitHub community discussion #25702, *"Push from Action does not trigger subsequent action"* (Secondary), `https://github.com/orgs/community/discussions/25702`
- **Empirical portfolio evidence**: the portfolio's own `v0.1.5` release run confirmed this behaviour directly, when a `release: published` event emitted under `GITHUB_TOKEN` didn't cascade to `release-cd-refresh-master.yml` as a new run (Primary, direct observation; recorded in the release-process verification for `nolte/claude-shared`).
- **A GitHub App identity can't create or update a file under `.github/workflows/` without the `workflows` permission, and the workflow `permissions:` block has no such scope**: GitHub Docs, "Workflow syntax" §`permissions`, whose complete scope list is `actions, artifact-metadata, attestations, checks, code-quality, contents, deployments, discussions, id-token, issues, packages, pages, pull-requests, security-events, statuses, vulnerability-alerts`—no `workflows` entry (Primary), `https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#permissions`; GitHub community discussion #51520, *"refusing to allow a GitHub App to create or update workflow `.github/workflows/ci.yml` without `workflows` permission"* (Secondary), `https://github.com/orgs/community/discussions/51520`; GitHub community discussion #27072, same rejection with the PAT-`workflow`-scope and App-permission remedies (Secondary), `https://github.com/orgs/community/discussions/27072`
- **Empirical portfolio evidence**: `nolte/taskfiles` run `32065009956` rejected a `GITHUB_TOKEN` push resetting the unprotected `main` to `v0.1.5` with exactly this message, because seven workflow files differed between the two refs (Primary, direct observation).
