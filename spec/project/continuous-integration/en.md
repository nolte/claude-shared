# Continuous Integration Pipeline Design

Status: draft
Portfolio-Scope: portfolio

## Context

Every repository in this portfolio runs a pre-merge pipeline, and the neighbouring specs each own one piece of it. `spec/project/branching-model/` declares **which** workflows must exist. `spec/project/project-structure/` declares **where** they live and how their reusable references are pinned. `spec/project/pull-request-workflow/` declares **what** gates a merge into `develop`. `spec/project/quality-gate/` declares the lint, type-check, and test contract, and `spec/project/taskfile/` declares the target vocabulary that contract is invoked through, including the local-and-CI parity rule. `spec/project/workflow-health/` declares the **operational** process that keeps those workflows green and triages them when they turn red.

What no spec declares is the **design** of the pipeline itself: which stages exist, in what order they run, what each stage is allowed to assume about the stages before it, and which properties the arrangement as a whole has to preserve. A contributor setting up or reworking a pipeline today reconstructs that convention from six documents and fills the remaining gaps by copying whichever repository looks closest. The result drifts: stage order differs, caching is bolted on until the run is fast enough, and nobody can say whether a green run means the same thing in two repositories.

This spec owns that design discipline for the **pre-merge** half of the pipeline. Its sibling `spec/project/continuous-delivery/` owns the post-merge half, and `spec/project/github-actions-best-practices/` binds both to the one platform this portfolio runs on. Two properties are load-bearing throughout and are stated as invariants rather than aspirations:

- **Reproducibility.** A pipeline run is a claim about a commit. If the same commit can produce a green run and a red run depending on when it ran, what a cache held, or which floating version resolved, the claim is worthless. Every rule about pinning, cache design, and stage isolation exists to protect this.
- **Reuse over copying.** A rule implemented once and inherited by every repository can't drift; a rule copied into twenty repositories will. This spec pushes shared mechanics toward the portfolio's reusable-workflow repository rather than into each consumer.

Pipeline **efficiency**—wall-clock runtime, cache hit rate, feedback latency—is treated as a guide throughout, never as a gate. Fast feedback is designed for by ordering stages, not enforced by a threshold, because no portfolio-wide threshold would survive contact with repositories of this range.

**Readers:** contributors and AI agents setting up or reworking a repository's pre-merge pipeline, reviewers judging whether a pipeline change is sound, and the authors of the `cicd-pipeline-design` skill and `cicd-pipeline-reviewer` agent that operationalize this spec.

## Goals

- The stages of a pre-merge pipeline, their order, and their preconditions are declared once, so two repositories that both report green mean the same thing by it
- A pipeline run is reproducible: the same commit yields the same verdict, and no cache, floating reference, or ambient runner state can change it
- Feedback is fast because cheap and broadly-informative stages run first, not because expensive stages were dropped
- Every stage that a contributor can also run locally is invoked through the identical entry point, so the local gate and the CI gate can't diverge
- Shared pipeline mechanics live in one reusable implementation rather than in per-repository copies
- The pipeline's supply-chain obligations (dependency, license, and code-security scanning) have a declared home in the stage sequence rather than existing as unattached workflows

## Non-Goals

- **Which** workflows a repository must contain, and how their reusable references are pinned—owned by `spec/project/branching-model/` §Required GitHub workflows and `spec/project/project-structure/`
- The **operation** of a pipeline over time: red-run triage, flake classification, upstream drift, re-run policy—owned by `spec/project/workflow-health/`
- The composition and output contract of the lint, type-check, and test gate itself—owned by `spec/project/quality-gate/`; this spec places that gate in the stage sequence and doesn't restate what it contains
- The Taskfile target vocabulary and namespacing—owned by `spec/project/taskfile/`; this spec depends on the parity rule declared there and doesn't redefine it
- What the tests themselves assert, how they're written, and how a test suite is shaped—owned by `spec/project/test-pyramid-foundation/`, the `test-tier-*` specs, and `spec/project/test-falsifiability/`
- Branch protection, required-status-check declaration, and merge mechanics—owned by `spec/project/pull-request-workflow/`
- Everything after the merge: artifact publication, provenance, release dispatch, rollback—owned by `spec/project/continuous-delivery/`
- Platform-specific syntax and mechanics. This spec is tool-independent; `spec/project/github-actions-best-practices/` is the single concrete binding

## Requirements

### A. Stage sequence

- **MUST** structure the pre-merge pipeline as an ordered sequence of named stages, each with a declared precondition on the stages before it. The canonical sequence is:
  1. **checkout**: obtain the exact commit under test, with the fetch depth the later stages actually need
  2. **provision**: install the toolchain and resolve dependencies from pinned inputs (§C)
  3. **static analysis**: the lint and type-check categories, whose composition `spec/project/quality-gate/` owns
  4. **test**: the test tiers, in ascending cost order (§E)
  5. **package**: produce the build artifact the commit would ship (§F)
  6. **supply-chain scan**: dependency vulnerabilities, license policy, and code-security review (§G)
- **MUST** allow a repository to omit a stage that doesn't apply to it (for example **package** in a repository that ships no build artifact) and **MUST** require that the omission be visible in the pipeline definition rather than silent
- **MUST NOT** reorder **checkout** or **provision**; every later stage depends on them
- **SHOULD** run **static analysis** and **test** as separate reported units rather than one aggregate step, so a red run names which class of problem occurred without opening the log
- **MAY** run independent stages concurrently when no precondition is violated; concurrency is an efficiency choice and **MUST NOT** be used to skip a precondition

### B. Fast feedback and failure behaviour

- **MUST** order stages so that the cheapest stage with the broadest failure coverage runs first: a lint error that's detectable in seconds **MUST NOT** be reported only after a multi-minute test suite
- **MUST** fail the pipeline run when any stage fails, and **MUST NOT** mark a run successful while a stage it contains reported failure
- **MUST NOT** use a continue-on-error escape to keep a required stage from failing the run. When a stage is genuinely advisory, it **MUST** be declared as a non-required check rather than as a required check that can't fail—an advisory stage reporting success regardless of its result can't be told apart from a stage that isn't running
- **SHOULD** let the remaining independent stages finish after the first failure rather than aborting the whole run, so one run surfaces every class of problem instead of one problem per push
- **SHOULD** treat pipeline runtime as a design input, reviewed when the pipeline is changed, and **MUST NOT** define a portfolio-wide runtime threshold as a merge gate
- **MUST NOT** address a slow pipeline by removing a stage from the required set; the remedy is to make the stage cheaper, run it concurrently, or narrow what it covers, and any reduction in coverage is a reviewable change rather than a performance fix

### C. Reproducibility of inputs

- **MUST** resolve every external input the pipeline consumes from a pinned reference: the toolchain version, the dependency set, the container base image, and any reusable pipeline component. A floating reference (a moving branch, a bare `latest`, an unbounded version range) **MUST NOT** appear in a pipeline definition
- **MUST** resolve dependencies from a committed lock file where the ecosystem provides one, so the dependency set is a property of the commit rather than of the moment the pipeline ran
- **MUST** treat a pinned reference as a reviewable artifact: bumping a pin is a change that passes the same gate as any other change, per `spec/project/pull-request-workflow/`
- **MUST NOT** let the pipeline mutate the working tree in a way that changes what a later stage sees without that mutation being an explicit, named stage; an implicit write is invisible to the reader and unreproducible on a rerun
- **SHOULD** keep each stage independent of ambient runner state—files left in a home directory, globally installed tools, or environment variables set by an earlier unrelated run—so a stage's result depends only on its declared inputs
- **SHOULD** be able to explain, for any green run, which pinned inputs produced it, so a later red run on the same commit is attributable to an input change rather than to chance

### D. Caching without changing a result

Caching is the most common place where a pipeline trades reproducibility for speed by accident. The rules below draw the boundary.

- **MUST** treat a cache strictly as an **accelerator**: a run with a cold cache and a run with a warm cache **MUST** reach the same verdict on the same commit. A cache that can change a result is a correctness defect, not a tuning problem
- **MUST** derive a cache key from the content that determines the cached data—typically the lock file, the toolchain version, and the platform—so that a change to any of them yields a different key rather than a stale hit
- **MUST NOT** cache anything the pipeline is supposed to produce and verify. Build outputs and test results are the pipeline's claims about the commit; restoring them from a previous run replaces the claim with an assertion that nothing changed
- **MUST NOT** cache credentials, tokens, or any other secret material
- **SHOULD** prefer a cache miss over a wrong hit when designing fallback keys: a partial-match fallback is only safe when a stale entry can be detected and corrected by the stage that consumes it
- **SHOULD** be able to disable caching entirely and still get a correct (slower) run; a pipeline that only passes with a warm cache isn't reproducible

### E. Test execution in the pipeline

- **MUST** run the test tiers in ascending cost order, so the cheapest tier that can detect a defect reports first; the tiers themselves and what each asserts are owned by `spec/project/test-pyramid-foundation/` and the `test-tier-*` specs
- **MUST** invoke the test stage through the repository's declared Taskfile target rather than by re-implementing the invocation inline, per the parity rule in `spec/project/taskfile/` §Local and CI parity
- **MUST NOT** weaken the suite to make the pipeline green: skipping, deselecting, or marking a case as expected-to-fail in order to unblock a merge is prohibited, and the no-cheating invariant owned by `spec/project/test-cycle-foundation/` and `spec/project/test-cycle-code-adaptation/` applies in full to any change made under pipeline pressure
- **MUST** ensure a test stage can fail. A stage that reports success when no test ran, when the suite failed to collect, or when the runner exited before the suite completed is a vacuous gate, and the pipeline **MUST** treat an empty or uncollected suite as a failure rather than as a pass
- **SHOULD** isolate test data per run so that concurrent pipeline runs on different commits can't interfere; the mechanics belong to the tier specs, the requirement that the pipeline not defeat them belongs here
- **MAY** fan out a tier across a matrix of platforms or versions when the tier's result genuinely depends on that axis, and **MUST** treat every matrix leg as required unless the leg is declared advisory per §B

### F. Producing the candidate artifact

- **MUST**, in a repository that ships a build artifact, build that artifact in the pre-merge pipeline from the commit under test, so a merge can't be the first time the build is attempted
- **MUST** build the artifact from the same definition the post-merge pipeline uses, so the pre-merge build is evidence about the artifact that would actually ship rather than about a parallel build path
- **MUST NOT** publish the pre-merge artifact to any consumer-visible location; publication is post-merge and belongs to `spec/project/continuous-delivery/`. The pre-merge build proves the commit builds, and its output is a run-scoped intermediate
- **SHOULD** retain the pre-merge artifact only as long as the run's diagnostics need it
<!-- vale Microsoft.Contractions = NO -->
- **SHOULD NOT** let anything downstream depend on the pre-merge artifact
<!-- vale Microsoft.Contractions = YES -->
- The artifact taxonomy per project type is owned by `spec/project/release-artifact/` and **MUST NOT** be restated here

### G. Supply-chain stages

- **MUST** give the repository's supply-chain obligations a declared position in the stage sequence rather than leaving them as workflows unattached to the pipeline: dependency vulnerability scanning (`spec/project/dependency-audit/`), license policy (`spec/project/license-check/`), and code-security review (`spec/project/code-security-audit/`)
- **MUST** run a supply-chain stage against the **resolved** dependency set of the commit under test, not against the declared ranges, so the finding matches what would actually ship
- **MUST** keep the severity policy and the response decision with the owning spec; this spec places the stage and **MUST NOT** define what a finding means or when it blocks
- **MAY** run a supply-chain obligation on a cadence rather than on every pull request when the owning spec declares one, and **MUST**, when it does, keep the cadence visible in the repository rather than implicit in a schedule nobody reads
- **MUST** accept, for an obligation whose owning spec declares neither a stage position nor a cadence, a recorded out-of-pipeline practice naming when the obligation is discharged. `spec/project/code-security-audit/` is the current case: it frames itself as an operator-invoked whole-codebase pass, so this spec **MUST NOT** demand a pipeline stage it doesn't declare

### H. Reuse of pipeline mechanics

- **MUST** implement pipeline mechanics that are identical across repositories once, in the portfolio's reusable-pipeline repository, and consume them by pinned reference rather than copying them into each repository. This is the same rule `spec/project/pull-request-workflow/` already applies to the pull-request linter, generalized to the pipeline
- **MUST NOT** fix a defect in shared pipeline mechanics by patching a local copy in one consumer repository; the fix belongs in the shared implementation so every consumer receives it. A consumer-local workaround is permitted only as a documented interim measure that names the upstream change it's waiting for
- **SHOULD** keep repository-specific pipeline content limited to what genuinely differs: the toolchain, the target matrix, and the repository's own stage set
- **SHOULD** treat a rule that has been copied into three or more repositories as a candidate for extraction into the shared implementation

### I. Delimitation

- **MUST NOT** restate any rule owned by `workflow-health`, `branching-model`, `project-structure`, `pull-request-workflow`, `quality-gate`, `taskfile`, `release-artifact`, or the test specs; where this spec needs one of those rules, it references it
- **MUST** route a red pipeline run to `spec/project/workflow-health/` for triage; this spec governs how the pipeline is built, not how a broken run is diagnosed
- **MUST** hand over to `spec/project/continuous-delivery/` at the merge boundary; a stage that runs after the merge belongs to that spec even when it's defined in the same file

## Acceptance Criteria

- [ ] A repository's pipeline definition presents a named, ordered stage set that maps onto §A, with any omitted stage visibly omitted rather than absent without comment
- [ ] No pipeline definition in the repository contains a floating reference for a toolchain version, dependency set, base image, or reusable component
- [ ] Every dependency-resolving stage reads a committed lock file where the ecosystem provides one
- [ ] Every cache key in the pipeline includes the content that determines the cached data, and no cache stores a build output, a test result, or secret material
- [ ] Disabling the cache produces a run that reaches the same verdict as the cached run on the same commit
- [ ] The lint, type-check, and test stages invoke the repository's Taskfile targets rather than re-implementing the commands inline
- [ ] No required stage in the pipeline is configured so that it can't fail the run
- [ ] A test stage that collects no tests reports failure rather than success
- [ ] In a repository that ships a build artifact, the pre-merge pipeline builds it from the same definition the post-merge pipeline uses, and publishes it nowhere
- [ ] Each of dependency-audit, license-check, and code-security review has a declared position in the stage sequence, a declared cadence, or a recorded out-of-pipeline practice in the repository
- [ ] Pipeline mechanics shared across repositories are consumed by pinned reference from the shared implementation, with no local copy of a shared workflow present
- [ ] Reviewing the spec against `workflow-health`, `quality-gate`, `taskfile`, and `branching-model` surfaces no restated rule, only references

## References

- `spec/project/quality-gate/`: the lint, type-check, and test contract this spec's §E places in the sequence
- `spec/project/taskfile/`: the canonical target vocabulary and the local-and-CI parity rule §E depends on
- `spec/project/test-pyramid-foundation/`, `spec/project/test-tier-static-analysis/`, `spec/project/test-tier-unit/`, `spec/project/test-tier-component/`, `spec/project/test-tier-integration/`, `spec/project/test-tier-contract/`: the tier model §E executes
- `spec/project/test-cycle-foundation/`, `spec/project/test-cycle-code-adaptation/`: the no-cheating invariant §E enforces under pipeline pressure
- `spec/project/test-falsifiability/`: the born-weak-test taxonomy, which §E's vacuous-stage rule guards against at pipeline level
- `spec/project/dependency-audit/`, `spec/project/license-check/`, `spec/project/code-security-audit/`: the supply-chain obligations §G places
- `spec/project/release-artifact/`: the artifact taxonomy §F refuses to restate
- `spec/project/branching-model/`, `spec/project/project-structure/`, `spec/project/pull-request-workflow/`: which workflows exist, where they live, and what gates a merge
- `spec/project/workflow-health/`: the operational counterpart this spec hands red runs to
- `spec/project/continuous-delivery/`: the post-merge half of the pipeline
- `spec/project/github-actions-best-practices/`: the single concrete platform binding

## Open Questions

- Whether the shared reusable-pipeline implementation should offer a complete opinionated pipeline that a consumer configures, or a set of composable stage building blocks a consumer assembles. The extraction rule in §H holds either way, but the shape of the shared implementation isn't settled.
- §B deliberately declines to set a runtime threshold. If a repository's pipeline later becomes slow enough to impede merges, there's no normative value to appeal to and the remedy would be a revision of this spec rather than a per-repository override. Whether an advisory portfolio-wide budget is worth introducing should be revisited once enough pipelines exist to calibrate one.
- The §D rule that a cold-cache run must reach the same verdict as a warm-cache run is stated as an invariant, but no mechanism verifies it. Whether a periodic cache-free run is worth wiring as a scheduled check is unresolved.
