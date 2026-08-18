# GitHub Actions Best Practices

Status: draft
Portfolio-Scope: portfolio

## Context

`spec/project/continuous-integration/` and `spec/project/continuous-delivery/` define this portfolio's pipeline discipline without naming a platform. Both are deliberately tool-independent, and both would be untestable if nothing bound them to the one platform every repository here actually runs on. This spec is that binding, and the only one: GitHub Actions is the single concrete platform this portfolio specifies. Other CI platforms are a non-goal, not an omission.

The binding has to do two things the abstract specs can't. First, it says how a platform-independent invariant is realized in GitHub Actions concretely enough to check: "pin every external input" becomes a rule about action references and reusable-workflow references; "reproducibility" becomes rules about caches, concurrency, and runner assumptions. Second, it covers the hazards that only exist because of how this platform works—token permissions that default wider than a job needs, expression interpolation that turns a pull-request title into shell code, and triggers that hand a fork's code the repository's secrets.

Those hazards aren't hypothetical. In March 2025 the widely-used `tj-actions/changed-files` action was compromised and its **existing version tags were moved to point at malicious code**, causing affected repositories to leak secrets into their run logs; repositories that referenced the action by commit digest rather than by tag were unaffected [R4], [R5]. The rule that follows from that incident is in §A, and it's a MUST.

This spec also writes against a structure the portfolio already has. `spec/project/branching-model/` §Required GitHub workflows declares that every repository wires its release workflows to reusable workflows published by `nolte/gh-plumbing`, and `spec/project/pull-request-workflow/` recommends implementing the pull-request linter there too, "so every repository inherits one implementation rather than forking local copies that drift." That existing reuse model is the shape this spec generalizes, not a parallel one it introduces.

**Readers:** contributors and AI agents writing or reviewing workflow files in this portfolio, and the authors of the `cicd-pipeline-design` skill and `cicd-pipeline-reviewer` agent that operationalize this spec.

## Goals

- Every workflow input resolves to content that can't change under the repository's feet
- A workflow job holds only the privileges it needs, so a compromised step has the smallest reachable blast radius
- Input from an outside contributor can't become executable code or reach a privileged context
- Credentials are short-lived and scoped where the platform supports it, rather than long-lived secrets copied into the repository
- Workflow logic shared across repositories is inherited from one implementation, and a fix to it reaches every consumer
- The platform mechanics that affect reproducibility—caching, concurrency, runner state—are used in ways that can't change a run's verdict

## Non-Goals

- The pipeline design these rules bind: stage sequence, feedback ordering, delivery guarantees, rollback—owned by `spec/project/continuous-integration/` and `spec/project/continuous-delivery/`
- Which workflows a repository must contain and how a published release propagates—owned by `spec/project/branching-model/`
- Where workflow files live and how the repository is scaffolded—owned by `spec/project/project-structure/`
- Required status checks, branch protection, and merge mechanics—owned by `spec/project/pull-request-workflow/`
- Triaging a red run, classifying a flake, and the `GITHUB_TOKEN` event-cascade constraint—owned by `spec/project/workflow-health/`
- The draft-to-published release transition—owned by `spec/project/release-automation/`
- Any other CI platform. This spec is the portfolio's only concrete platform binding, and a second platform would need its own spec rather than an extension of this one
- The internals of the `nolte/gh-plumbing` reusable workflows themselves; this spec governs how a consumer repository consumes them

## Requirements

### A. Pinning external references

- **MUST** reference every third-party action by a full-length commit digest rather than by tag or branch. GitHub states that pinning to a full-length commit digest "is currently the only way to use an action as an immutable release" [R1], and the March 2025 `tj-actions/changed-files` compromise moved existing tags to malicious code while digest-pinned consumers stayed unaffected [R4], [R5]
- **MUST** accompany a digest-pinned reference with a comment naming the human-readable version it corresponds to, so the pin stays reviewable and upgradable rather than opaque
- **MUST** verify that a chosen digest belongs to the action's own repository rather than to a fork before pinning to it [R1]
- **MUST** pin every reusable-workflow reference to an immutable reference rather than to a moving branch, per `spec/project/branching-model/`, which already requires a tag for `nolte/gh-plumbing` references and governs the bump cadence through `spec/project/workflow-health/`
- **MUST NOT** treat a tag as immutable on the grounds that the publisher is trusted: the tj-actions incident compromised a trusted publisher's tags, so trust in the publisher isn't the property that pinning protects [R4]
- **SHOULD** let the repository's update automation propose pin bumps as reviewable pull requests, so a digest pin ages visibly rather than silently
- **MAY** reference an action published by this portfolio's own organization by tag when the organization controls the tag's mutability, and **MUST** record that choice rather than leaving it implicit

### B. Least-privilege permissions

- **MUST** declare an explicit `permissions` block rather than relying on the repository or organization default, so a job's privileges are readable in the workflow instead of in a settings page
- **MUST** set the workflow-level `permissions` to the minimum the workflow needs, and grant additional write scopes at the job level only where a job genuinely needs them. GitHub advises setting the default token permission "to read access only" [R1], and OpenSSF Scorecard checks exactly this shape: read-only at the top level, required write permissions declared at the job level [R2]
- **MUST NOT** grant a blanket write-all permission set to work around an unclear failure; the correct response is to identify the scope the failing step needs and grant that scope
- **MUST** scope the `id-token` write permission to the job that requests a short-lived credential (§D), never workflow-wide
- **SHOULD** re-derive a job's permissions when its steps change, because a permission granted for a step that has since been removed is a privilege nothing needs

### C. Handling untrusted input and dangerous triggers

- **MUST NOT** interpolate an untrusted context value directly into a `run` script. GitHub's stated mitigation is to bind the value to an intermediate environment variable and reference that variable from the script instead [R1]; OpenSSF Scorecard classes direct interpolation of untrusted context as a dangerous workflow [R2]
- **MUST** treat every field an outside contributor controls as untrusted, including pull-request titles, bodies, branch names, and commit messages
- **MUST NOT** check out and execute code from an untrusted pull request in a workflow that holds repository secrets or elevated token permissions. GitHub warns that such workflows are privileged and expose the repository to compromise, and recommends separating the privileged step from the untrusted code [R1], [R2]
- **MUST** justify any use of a trigger that runs in the base repository's privileged context while carrying a fork's code, and **MUST** keep the untrusted code out of that context when the trigger is genuinely needed
- **SHOULD** prefer a trigger that runs untrusted code without secrets, and hand results to a separate privileged workflow, over granting the untrusted run the privileges it would need to act directly [R1]

### D. Credentials

- **MUST** obtain cloud credentials through the platform's short-lived-token exchange rather than storing long-lived provider credentials as repository secrets, wherever the provider supports it. The platform issues a short-lived access token valid for a single job only, which then expires automatically, removing the need to duplicate cloud credentials as long-lived secrets [R3]
- **MUST** constrain the trust relationship on the provider side to the specific repository, and where applicable the specific environment, that legitimately needs it, rather than to the organization as a whole [R3]
- **MUST NOT** store a structured blob as a single secret when its parts are used separately; GitHub advises registering individual secrets so that each value stays redacted on its own [R1]
- **MUST** treat a secret that has appeared in a log as compromised and rotate it, rather than deleting the log and considering the matter closed [R1]
- **MUST NOT** pass secrets into a called reusable workflow more broadly than that workflow needs. Secrets reach only the directly-called workflow, so a chain forwards them explicitly at each step—this is a boundary to use deliberately, not to defeat with a blanket inherit [R6]
- **SHOULD** register any sensitive value the workflow derives at run time with the platform's masking mechanism, so a transformation of a secret stays redacted [R1]

### E. Reusable workflows and composite actions

- **MUST** implement logic that's identical across repositories as a reusable workflow in `nolte/gh-plumbing` and consume it by pinned reference, rather than copying it into each repository. This generalizes the rule `spec/project/pull-request-workflow/` already applies to the pull-request linter and `spec/project/branching-model/` applies to the release workflows
- **MUST NOT** fix a defect in shared workflow logic by patching a consumer-local copy. This is the same rule `spec/project/workflow-health/` states for the `GITHUB_TOKEN` event-cascade constraint: the remedy belongs upstream so every consumer receives it, and a per-repository workaround creates the drifting fork the reuse model exists to prevent
- **MUST**, when a consumer repository genuinely needs an interim local workaround, record it as an interim measure naming the upstream change it waits for, so the workaround is visibly temporary
- **SHOULD** choose a **reusable workflow** when the shared unit is one or more whole jobs with their own runner and permissions, and a **composite action** when the shared unit is a sequence of steps that runs inside a caller's job
- **SHOULD** keep the call chain shallow. The platform enforces a documented maximum nesting depth [R6]; a chain that approaches it becomes hard to reason about long before the platform rejects it
- **MUST** account for the fact that a reusable workflow doesn't inherit the caller's environment, and **MUST** pass what it needs through declared inputs rather than assuming ambient values are present [R6]

### F. Concurrency

- **MUST** declare a concurrency group for any workflow where two runs on the same branch would interfere, so a superseded run can't race the run that replaced it
- **MUST** derive the concurrency group from the workflow identity and the branch or pull-request identity, so runs on different branches don't cancel each other [R7]
- **MUST NOT** apply cancel-on-new-run behaviour to a delivery or release workflow, where cancelling a run in flight can leave a partially-published artifact; the pattern belongs to pre-merge feedback, where superseding a stale run is the desired outcome
- **SHOULD** enable cancel-on-new-run for pre-merge workflows, so pushing a follow-up commit doesn't leave a stale run consuming capacity and reporting an obsolete verdict [R7]. This recommendation presupposes that the job's runtime fits the cadence of its triggering event: a lane whose runtime exceeds the push cadence ends mostly `cancelled` under cancel-in-progress and never delivers a verdict—observation and remediation (trigger re-placement, not `cancel-in-progress: false`) are owned by `spec/project/workflow-health/` §Cancellation rates

### G. Caching

- **MUST** treat the cache rules of `spec/project/continuous-integration/` §D as binding here, and **MUST NOT** use platform cache features in a way that lets a cache change a run's verdict
- **MUST** build a cache key from the content that determines the cached data, because a cache entry can't be updated in place: when a key matches an existing entry, no new entry is written, so a key that fails to change when the content changes pins the pipeline to stale data indefinitely [R8]
- **MUST NOT** rely on a prefix-match fallback to recover from a stale entry; the fallback restores an older entry rather than correcting the key, so the staleness persists unless the consuming step detects and repairs it [R8]
- **MUST NOT** cache credentials or any other secret material [R1]
- **SHOULD** account for the platform's branch-scoped cache visibility when reasoning about why a run on a feature branch behaves differently from one on the default branch [R8]

### H. Provenance

- **MUST** generate the provenance record required by `spec/project/continuous-delivery/` §C through the platform's own attestation mechanism rather than through a step in the build being attested, because the platform generates and signs the record independently of the build [R9], [R10]
- **MUST** grant the attestation-related permissions at the job that produces the attestation, per §B, and **MUST NOT** widen them to the workflow
- **MUST NOT** present an attestation as evidence that an artifact is safe. GitHub states plainly that artifact attestations aren't a guarantee that an artifact is secure, and that they instead link an artifact to the source and build instructions that produced it [R9]
- **SHOULD** consume shared reusable workflows for the build step where the organization uses them, which is also the path the platform documents toward a stronger provenance level [R9]

### I. Runners

- **MUST NOT** run workflows from public repositories on self-hosted runners. GitHub states that self-hosted runners should almost never be used for public repositories, because anyone can open a pull request and persistently compromise the runner environment [R1]
- **MUST** treat a runner as disposable: a job **MUST NOT** depend on state a previous job or run left behind, which is the platform-level form of the stage-isolation rule in `spec/project/continuous-integration/` §C
- **SHOULD**, where a self-hosted runner is genuinely required for a private repository, use an ephemeral runner that starts from a clean environment for each job [R1]

### J. Delimitation

- **MUST NOT** restate a rule owned by `continuous-integration`, `continuous-delivery`, `branching-model`, `project-structure`, `pull-request-workflow`, `workflow-health`, or `release-automation`; where this spec binds one of those rules to the platform, it references the owning spec and adds only the platform-specific mechanics
- **MUST** route the `GITHUB_TOKEN` event-cascade constraint to `spec/project/workflow-health/`, which owns it, rather than re-deriving it here
- **MUST** route a red run to `spec/project/workflow-health/` for triage
- **MUST** route the decision of whether to run a merge queue at all to `spec/project/pull-request-workflow/` §"Merge queue" as the owner of the merge path; §K binds only the platform mechanics that follow from that decision

### K. Merge-queue event wiring

This section binds the merge-queue mechanics to the platform. Whether a repository should run a merge queue at all is owned by `spec/project/pull-request-workflow/` §"Merge queue" and isn't decided here; these rules apply once one is enabled.

- **MUST** add `merge_group` (activity type `checks_requested`) as a trigger to every workflow whose job is a required status check for the queued branch. A merge queue waits for the required checks to be reported against the merge group, and a workflow that only triggers on `pull_request` reports nothing there, so the entry waits for a status that never arrives [R11], [R12]
- **MUST NOT** leave a required check that can only run in pull-request context—a title or body linter, a check reading `pull_request` payload fields—registered as required for a queued branch. In a merge group there's no pull request to inspect, and a workflow that doesn't start reports no status at all rather than a skip that counts as success. Such a check is either removed from the required set or restructured so its job still runs and reports success in the merge-group context while its pull-request-only steps are skipped [R12]
- **MUST** configure a third-party CI provider to run on pushes to branches with the `gh-readonly-queue/{base_branch}` prefix, the temporary branches the queue creates; these carry a different SHA from the pull request head [R12]
- **MUST NOT** protect a queued branch through a branch-protection rule whose name pattern uses a wildcard: a merge queue can't be enabled on such a rule [R12]
- **MUST** derive the concurrency group of a merge-group run (§F) from a key that's populated in that context; a group keyed on a pull-request-only expression collapses every merge-group run into one group, so a newly queued entry cancels the run the queue is still waiting on
- **SHOULD** account for the doubled execution before enabling a queue: the same pipeline now runs once per pull request and again per merge group, and a removed entry rebuilds the entries behind it. Where that cost matters, the stage-scoping rules of `spec/project/continuous-integration/` §A and §E decide what runs in which context—this spec doesn't re-derive them

## Acceptance Criteria

- [ ] Every third-party action reference in `.github/workflows/` is a full-length commit digest with a comment naming the corresponding version
- [ ] Every reusable-workflow reference is pinned to an immutable reference rather than a moving branch
- [ ] Each pinned digest was verified to belong to the action's own repository rather than to a fork, and that verification is recorded in the pinning change
- [ ] Every workflow declares an explicit `permissions` block, with write scopes granted at job level rather than workflow level
- [ ] In a repository that runs a merge queue, every workflow backing a required status check triggers on `merge_group` as well, no required check depends on pull-request-only context, and third-party CI runs on the `gh-readonly-queue/` prefix
- [ ] No workflow grants a blanket write-all permission set
- [ ] No `run` script interpolates an untrusted context value directly; such values reach the script through an intermediate environment variable
- [ ] No workflow checks out untrusted pull-request code in a context that holds secrets or elevated permissions
- [ ] Where a cloud provider supports short-lived token exchange, the repository uses it rather than a stored long-lived credential, and the provider-side trust condition names the specific repository
- [ ] No secret holds a structured blob whose parts are consumed separately, and every secret that has appeared in a log has been rotated rather than only having the log deleted
- [ ] No called reusable workflow receives secrets beyond the ones it needs
- [ ] Logic identical across repositories is consumed from `nolte/gh-plumbing` by pinned reference, with no consumer-local copy present and any interim workaround recorded as such
- [ ] Every workflow whose concurrent runs would interfere declares a concurrency group derived from workflow and branch identity
- [ ] No delivery or release workflow cancels in-flight runs
- [ ] Every cache key includes the content that determines the cached data, and no cache stores secret material
- [ ] Artifact provenance is produced by the platform's attestation mechanism, with its permissions scoped to the producing job
- [ ] No public repository in the portfolio targets a self-hosted runner
- [ ] No job depends on state a previous job or run left on the runner
- [ ] Reviewing this spec against `continuous-integration`, `continuous-delivery`, `workflow-health`, and `branching-model` surfaces no restated rule, only platform bindings

## References

Source classes are labelled per `spec/claude/research-triangulate/`. The load-bearing rules of §A, §B, §C, and §H each rest on two or more independent sources.

- [R1] *Secure use reference* (GitHub Docs, **Primary**): commit-digest pinning as the only immutable action reference, read-only default token permissions with job-level write grants, the intermediate-environment-variable mitigation for untrusted input, secret hygiene and masking, the privileged-trigger warning, and the self-hosted-runner guidance: <https://docs.github.com/en/actions/reference/security/secure-use>
- [R2] *OpenSSF Scorecard checks* (**Primary**, independent of GitHub): `Pinned-Dependencies` (a pinned dependency is set to a specific hash rather than a mutable version), `Token-Permissions` (read-only at the top level, required write permissions at run level), and `Dangerous-Workflow` (untrusted code checkouts and script injection with untrusted context variables): <https://github.com/ossf/scorecard/blob/main/docs/checks.md>
- [R3] *OpenID Connect in GitHub Actions* (GitHub Docs, **Primary**): short-lived tokens valid for a single job, removal of duplicated long-lived cloud credentials, and subject-claim-based trust conditions: <https://docs.github.com/en/actions/concepts/security/openid-connect>
- [R4] *GitHub Action tj-actions/changed-files supply chain attack* (Wiz, **Secondary**, dated March 2025): the attacker moved existing version tags to malicious code, and hash-pinned consumers were unaffected unless they adopted a compromised digest during the window: <https://www.wiz.io/blog/github-action-tj-actions-changed-files-supply-chain-attack-cve-2025-30066>
- [R5] *Supply Chain Compromise of Third-Party tj-actions/changed-files (CVE-2025-30066)* (CISA, **Secondary**, independent of R4, dated 2025-03-18): the government advisory for the same incident: <https://www.cisa.gov/news-events/alerts/2025/03/18/supply-chain-compromise-third-party-tj-actionschanged-files-cve-2025-30066-and-reviewdogaction>
- [R6] *Reuse workflows* (GitHub Docs, **Primary**): the `workflow_call` mechanism, the documented maximum nesting depth, the rule that environments aren't inherited, and the rule that secrets reach only the directly-called workflow: <https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows>
- [R7] *Control the concurrency of workflows and jobs* (GitHub Docs, **Primary**): concurrency groups, cancel-in-progress semantics, and the workflow-plus-ref group expression pattern: <https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency>
- [R8] *actions/cache* (**Primary**, the action's own repository): a matching key writes no new entry, so cache entries can't be updated in place; `restore-keys` performs prefix matching against older entries; cache visibility is scoped by key, version, and branch: <https://github.com/actions/cache>
- [R9] *Artifact attestations* (GitHub Docs, **Primary**): platform-generated build provenance, the shared-reusable-workflow path to a stronger provenance level, and the explicit statement that attestations aren't a guarantee that an artifact is secure: <https://docs.github.com/en/actions/concepts/security/artifact-attestations>
- [R10] *SLSA v1.0 build levels* (**Primary**, independent of GitHub): the requirement that the build platform generates and signs provenance rather than the build process itself: <https://slsa.dev/spec/v1.0/levels>
- [R11] *Events that trigger workflows* (GitHub Docs, **Primary**): the `merge_group` event with its single activity type `checks_requested`, and the statement that a repository using Actions for required pull-request checks must add the event or the merge fails because the status is never reported, `https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows`
- [R12] *Managing a merge queue* (GitHub Docs, **Primary**): the CI-configuration requirement to trigger and report on merge-group events, the `gh-readonly-queue/{base_branch}` temporary-branch prefix carrying a different SHA, the wildcard branch-protection limitation, and the worked scenarios where a removed entry causes the temporary branches behind it to be recreated, `https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue`
- `spec/project/continuous-integration/`, `spec/project/continuous-delivery/`: the tool-independent specs this spec binds to the platform
- `spec/project/branching-model/`, `spec/project/pull-request-workflow/`, `spec/project/project-structure/`, `spec/project/workflow-health/`, `spec/project/release-automation/`: the neighbouring specs whose rules this spec references rather than restates

## Open Questions

- §A permits referencing this organization's own actions by tag when the organization controls tag mutability, but the portfolio hasn't decided whether to enable the platform's tag-immutability controls. Until it does, the exemption rests on convention rather than on an enforced property.
- §E states when to choose a reusable workflow over a composite action but doesn't settle what the `nolte/gh-plumbing` catalog should contain beyond what `branching-model` and `pull-request-workflow` already mandate. The extraction candidates named in `continuous-integration` §H haven't been inventoried.
- §D's short-lived-credential rule is conditioned on provider support. Which credentials this portfolio holds as long-lived secrets today, and which of them could migrate, hasn't been surveyed.
- The acceptance criteria are written to be checkable by inspection, but no linter enforces them. Whether to adopt an existing workflow-scanning tool or to rely on the `cicd-pipeline-reviewer` agent alone is unresolved.
- Upstream platform limits (nesting depth, cache retention, cache size) are referenced rather than quoted, deliberately, so this spec doesn't carry numbers that go stale. A reviewer who needs the current value reads the cited source.
