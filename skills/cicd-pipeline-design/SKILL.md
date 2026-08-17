---
name: cicd-pipeline-design
description: "Designs, scaffolds, and audits a repository's CI/CD pipeline against spec/project/continuous-integration/ (pre-merge stage sequence, reproducible inputs, cache discipline, local↔CI parity), spec/project/continuous-delivery/ (artifact immutability, provenance, the artifact-to-securing-stage matrix, rollback, the handover boundary to deployment), and spec/project/github-actions-best-practices/ (digest pinning, least-privilege permissions, untrusted input, short-lived credentials, reusable-workflow reuse, concurrency, caching). Writes and patches workflow files in the target repository. Invoke when the user asks to design, set up, rework, harden, or audit a CI/CD pipeline or GitHub Actions workflows; also German. Don't use to triage a red run (`workflow-health-triage`), run the gate (`quality-gate`), or publish a release (`release-publish-trigger`). Supports resume on re-invocation per `spec/claude/resumable-work/`."
tags: [scaffolding, release]
phase: design
summary: "Designs, scaffolds, and audits a repository's CI/CD pipeline against the CI, CD, and GitHub Actions specs."
summary_de: "Entwirft, scaffoldet und auditiert die CI/CD-Pipeline eines Repositories gegen die CI-, CD- und GitHub-Actions-Specs."
use_when:
  - "you want to design or set up a CI/CD pipeline for a repository"
  - "you want to rework or harden an existing pipeline or its workflows"
  - "you want to audit workflows for pinning, permissions, or cache defects"
  - "you want to place supply-chain or delivery stages in the pipeline"
  - "you want the artifact-to-securing-stage matrix derived for a project"
dont_use_when:
  - situation: "A workflow run is red and you want it triaged"
    alternative: workflow-health-triage
  - situation: "You want to run lint, type-check, and tests right now"
    alternative: quality-gate
  - situation: "You want to publish the open draft release"
    alternative: release-publish-trigger
  - situation: "You want to scaffold repository structure beyond the pipeline"
    alternative: project-structure-apply
see_also:
  - cicd-pipeline-reviewer
  - workflow-health-triage
  - quality-gate
  - project-structure-apply
---

# CI/CD Pipeline Design

Operationalizes three specs into one working pipeline: `spec/project/continuous-integration/` (the pre-merge half), `spec/project/continuous-delivery/` (the post-merge half), and `spec/project/github-actions-best-practices/` (the single concrete platform binding). The specs declare the discipline; this skill applies it to a specific repository and writes the result.

## Why this is a skill, not an agent

- **It writes.** Designing a pipeline ends in workflow files on disk. An agent returns a report and forgets; the deliverable here is a diff.
- **It's a multi-step dialogue.** Stage selection depends on the project type, the artifact classes it ships, and which stages the operator wants required versus advisory. Those are decisions to take with the operator, not to infer.
- **It has a read-only companion.** The detection half is genuinely isolated and parallel, so it lives in the `cicd-pipeline-reviewer` agent, which this skill dispatches for the `audit` operation. Skill writes, agent detects—the same split as `dockerfile-audit` and its scanner.

## User-language policy

Detect the user's language and conduct the dialogue in it. Workflow files, comments inside them, and commit messages stay English per the repository's authoring rules, regardless of conversation language.

## German trigger phrases

The frontmatter `description` keeps its trigger lexicon English-only per `spec/claude/skill-management/` §Structure. Treat these as equivalent:

- "entwirf eine CI/CD-Pipeline für dieses Repo"
- "die Pipeline umbauen / härten"
- "prüfe die Workflows auf Pinning und Berechtigungen"
- "wo gehört der Dependency-Scan in die Pipeline?"
- "welche Stufe sichert welches Artefakt ab?"

## Precondition

Verify that all three canonical spec files are reachable in the current project:

- `spec/project/continuous-integration/<canonical_language>.md`
- `spec/project/continuous-delivery/<canonical_language>.md`
- `spec/project/github-actions-best-practices/<canonical_language>.md`

If any is missing, stop and say so. These specs are the input; without them there's no authoritative stage sequence, no securing-stage vocabulary, and no platform rule set. Don't improvise a replacement.

## Operations

### 1. `design` — derive the pipeline for this repository

Produces a proposed stage set and the reasoning behind it. Writes nothing.

1. **Detect the project type and its artifact classes.** Read the repository: lock files, `Taskfile.yml`, `.github/workflows/`, the container and chart definitions, and `project/portfolio.yml` where present. Resolve the artifact classes against `spec/project/release-artifact/` §Artefact taxonomy—never re-enumerate that taxonomy, read it.
2. **Map the canonical stage sequence onto the repository** per `continuous-integration` §A. For every stage the repository doesn't need, record the omission and its reason; a silent omission is what §A forbids.
3. **Order for feedback** per §B: cheapest-with-broadest-coverage first. Name which stages are required and which are advisory, and confirm the split with the operator—an advisory stage that can't fail is the failure mode §B calls out.
4. **Derive the artifact-to-securing-stage matrix** per `continuous-delivery` §D: for each artifact class the project ships, which delivery stage secures it and which guarantee it carries (`built-from-source`, `integrity`, `provenance`, `policy-cleared`). An artifact class with no securing stage is a defect to surface, not a gap to leave.
5. **Locate the handover boundary** per `continuous-delivery` §F: name the artifact reference the deployment side consumes. Stop there.
6. **Identify reuse candidates** per `continuous-integration` §H and `github-actions-best-practices` §E: any logic identical across repositories belongs upstream in `nolte/gh-plumbing`, not in this repository. Emit those as named upstream work packages (see Hard rules).
7. Present the design and get the operator's agreement before `scaffold` writes anything.

### 2. `scaffold` — write the workflow files

Applies an agreed design to disk.

- Write or patch files under `.github/workflows/`, honouring `spec/project/project-structure/` for placement and `spec/project/branching-model/` for which workflows must exist. Neither is redefined here; both are read.
- Every third-party action reference is a full-length commit digest with a comment naming the version, per `github-actions-best-practices` §A. Resolve the digest for the intended version rather than guessing it, and verify it belongs to the action's own repository.
- Every workflow gets an explicit `permissions` block, minimum at workflow level, write scopes at job level only, per §B.
- Every stage that a contributor can run locally is invoked through the repository's Taskfile target, per `continuous-integration` §E and `spec/project/taskfile/` §Local and CI parity. Never re-implement the command inline.
- Cache keys are derived from the content that determines the cached data, per `continuous-integration` §D and `github-actions-best-practices` §G.
- Concurrency groups follow §F: cancel-on-new-run for pre-merge workflows, never for delivery or release workflows.
- Show the diff and get approval before writing. Re-run `audit` afterwards so the written state is verified, not assumed.

### 3. `audit` — check an existing pipeline

- Dispatch the `cicd-pipeline-reviewer` agent for detection. It returns severity-classified findings with `file:line`.
- Apply the severity judgement and assemble the report: which spec rule each finding violates, and the concrete remedy.
- Offer to fix findings whose remedy is mechanical and local (a missing `permissions` block, a tag reference that should be a digest, a cache key missing its determining input). Each fix is shown as a diff and approved individually.
- Route findings that belong elsewhere rather than fixing them here: a red run goes to `workflow-health-triage`, a portfolio-wide defect becomes an upstream work package (see Hard rules).

## Delimitation

- **Red run triage** is `workflow-health-triage` and `spec/project/workflow-health/`. This skill designs the pipeline; it doesn't diagnose a broken run.
- **Running the gate** is `quality-gate`. This skill places the gate in the sequence and wires the invocation.
- **Publishing a release** is `release-publish-trigger` and `spec/project/release-automation/`. This skill's delivery stages dispatch into that machinery and never reimplement its pre-publish gates.
- **Cluster rollout** is `deployment-chart-manage` and the deployment specs. This skill stops at the published artifact plus its provenance.
- **Repository scaffolding** is `project-structure-apply`. Both skills touch `.github/workflows/`, so the split is by question: `project-structure-apply` answers *which files must exist* (the required-workflow set `spec/project/branching-model/` mandates, plus the rest of the `.github/` layout) and creates them from the standard wiring. This skill answers *what the pipeline does* — stage set, ordering, pinning, permissions, caching, securing stages — and edits workflow content. When a required workflow is missing outright, hand that to `project-structure-apply` first and design against the result.

## Examples

- Read `examples/01-design-greenfield-pipeline.md` when running `design` against a repository that has only its release workflows and needs a full stage set derived.
- Read `examples/02-audit-existing-workflows.md` when running `audit` over existing workflow files and deciding which findings to fix in place versus route elsewhere.
- Read `examples/03-upstream-work-package.md` when a finding's correct remedy lives in `nolte/gh-plumbing` and the consumer repository must be left alone.

## Gotchas

- **A tag is not immutable, even from a trusted publisher.** The March 2025 `tj-actions/changed-files` compromise moved existing version tags to malicious code. Digest pinning is what protects against that; publisher trust is not. See `github-actions-best-practices` §A.
- **A cache entry can't be updated in place.** When a key matches, nothing new is written. A key that fails to change when the content changes pins the pipeline to stale data indefinitely, and a prefix fallback restores an older entry rather than repairing the key.
- **`continue-on-error` on a required stage is indistinguishable from not running it.** If a stage is genuinely advisory, make it a non-required check instead.
- **A test stage that collects nothing must fail.** A green run over an empty suite is the most expensive kind of false signal; `continuous-integration` §E makes this explicit.
- **Don't quote upstream platform limits.** Nesting depth, cache size, and retention change. The specs reference their sources deliberately; repeating a number here would make this skill go stale silently.
- **Efficiency is a guide, not a gate.** Never propose removing a stage from the required set to make a pipeline faster; §B names that as a coverage reduction requiring review, not a performance fix.

## Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/cicd-pipeline-design/<run-id>.yml` at each named phase boundary (detection complete, design agreed, scaffold approved, audit reported), carrying the detected project type, the agreed stage set, and the artifact-to-securing-stage matrix so an interrupted run resumes without re-deriving them. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation and offer `resume / start-new / discard`. The state-file envelope and the fail-closed semantics on schema or YAML errors live in the spec; don't duplicate them here.

## Hard rules

- Never write a workflow file without showing the diff and getting approval first.
- Never reference a third-party action by tag or branch. A full-length commit digest with a version comment is the only accepted form.
- Never add a trigger to a job that calls a reusable workflow without checking what that reusable's inputs default to. A default derived from a specific event payload (`${{ github.event.release.tag_name }}` and the like) is empty under every other trigger, so the added path is inert — the defect `github-actions-best-practices` §E now forbids. Forward the input explicitly: a declared input plus `${{ inputs.<name> || github.event.<field> }}` where the trigger accepts inputs, a context the event does populate where it doesn't. When the reusable lives in another repository and you can't read it, say so and ask rather than assuming the default is safe.
- Never grant a blanket write-all permission set to get past an unclear failure; identify the scope the failing step needs.
- Never patch a consumer repository with a local copy of logic that belongs in `nolte/gh-plumbing`. When the correct remedy is upstream, emit a named upstream work package and leave the consumer alone. A consumer-local workaround is permitted only as a recorded interim measure naming the upstream change it waits for.
- Never weaken a test or a gate to make a pipeline green. The no-cheating invariant of `spec/project/test-falsifiability/` applies in full under pipeline pressure.
- Never re-enumerate the artifact taxonomy, the required-workflow list, or the quality-gate composition; read them from `release-artifact`, `branching-model`, and `quality-gate` respectively.
- Never cache secret material, and never cache a build output or test result the pipeline is supposed to produce and verify.
- When a spec disagrees with this skill, the spec wins. Propose updating this skill rather than diverging silently.
