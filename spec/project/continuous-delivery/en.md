# Continuous Delivery Pipeline Design

Status: draft
Portfolio-Scope: portfolio

## Context

`spec/project/continuous-integration/` owns the pre-merge half of the pipeline: the discipline that decides whether a commit is allowed into `develop`. Once a commit lands, a different discipline takes over, with different triggers, different consumers, and a different failure cost. A red pre-merge run blocks one pull request. A delivery defect ships.

The neighbouring specs again own the pieces without owning the whole. `spec/project/release-artifact/` declares the **taxonomy** of what a project ships and the shape of an `artifact_ref` per project type. `spec/project/release-automation/` declares the **transition** from an open draft release to a published one, including the pre-publish gates and the version-bearing files those gates align. `spec/project/branching-model/` declares how a published release propagates to `main`. `spec/project/release-skill-layer/` declares the curation and dispatch layer that operators drive. `spec/project/kubernetes-deployment-best-practices/` and `spec/project/bjw-s-common-chart-deployment/` declare how a workload is configured to run.

What none of them declares is the **delivery discipline** that connects them: which stages a post-merge pipeline runs, what property each shipped artifact has to carry, how an artifact is tied to the commit and the build that produced it, and what happens when a shipped version turns out to be wrong. This spec owns that discipline.

Its scope ends at a deliberate boundary. Delivery is responsible for **building, attesting, and immutably publishing** the artifact, and for the rollback contract expressed over artifact versions. Rolling a workload into a cluster is the concern of the deployment specs, which consume what delivery publishes. The boundary is named here rather than crossed, so neither side restates the other.

Two properties carry over from the pre-merge half and mean something sharper here:

- **Reproducibility** becomes **traceability of what shipped**. Every published artifact has to be attributable to one commit, one build, and one set of pinned inputs. An artifact nobody can trace back can't be audited, can't be reproduced, and can't be safely rolled back to.
- **Reuse over copying** becomes **one delivery path**. A project that publishes through one mechanism in the pipeline and another by hand has two delivery paths, and only one of them is governed.

**Readers:** contributors and AI agents building or reworking a repository's post-merge delivery, release operators deciding whether a version is safe to publish, and the authors of the `cicd-pipeline-design` skill and `cicd-pipeline-reviewer` agent that operationalize this spec.

## Goals

- Everything a project ships is produced by the delivery pipeline, so no artifact reaches a consumer through a path that bypasses the pipeline's guarantees
- Every published artifact is traceable to the commit, the build, and the pinned inputs that produced it
- A published artifact is immutable: a given version reference always resolves to the same bytes
- Each artifact class a project ships has a named delivery stage that secures it, so no artifact ships unattested by accident
- Recovering from a bad release is a rehearsed operation over artifact versions rather than an improvisation
- The boundary between publishing an artifact and running that artifact is explicit, so delivery and deployment don't restate or contradict each other

## Non-Goals

- The artifact taxonomy and the valid `artifact_ref` shapes per project type—owned by `spec/project/release-artifact/`; this spec says what a delivery stage must guarantee about an artifact, not which artifacts exist
- The draft-to-published release transition, the pre-publish gate, and version-bearing file alignment—owned by `spec/project/release-automation/`; this spec's release stage dispatches into that machinery and doesn't redefine it
- How a published release propagates to `main`, and which workflows must exist—owned by `spec/project/branching-model/`
- The operator-facing curation and dispatch layer—owned by `spec/project/release-skill-layer/`
- How a workload is configured, hardened, and rolled into a cluster—owned by `spec/project/kubernetes-deployment-best-practices/` and `spec/project/bjw-s-common-chart-deployment/`; delivery hands over to them and stops
- Everything before the merge: stage ordering for pre-merge feedback, the quality gate, test execution—owned by `spec/project/continuous-integration/`
- Operating the delivery workflows over time and triaging them when they turn red—owned by `spec/project/workflow-health/`
- Platform-specific syntax and mechanics. This spec is tool-independent; `spec/project/github-actions-best-practices/` is the single concrete binding

## Requirements

### A. Scope and trigger of the delivery pipeline

- **MUST** treat delivery as beginning at the merge into `develop` and ending at the publication of every artifact the version ships; work before the merge belongs to `spec/project/continuous-integration/`
- **MUST** trigger each delivery stage from a declared event rather than from a manual invocation whose steps live only in an operator's memory. Where the portfolio deliberately keeps a human decision point, that decision **MUST** be a declared trigger with a recorded rationale rather than an undocumented habit
- **MUST NOT** publish an artifact from a commit that didn't pass the pre-merge gate; delivery builds on the pre-merge verdict rather than replacing it
- **SHOULD** separate the stage that **produces** an artifact from the stage that **publishes** it, so a build failure and a publication failure are distinguishable and a produced artifact can be inspected before it becomes visible

### B. Artifact identity and immutability

- **MUST** give every published artifact a version reference that resolves to the same bytes forever; republishing different content under an existing version reference is prohibited
- **MUST** treat an accidental publication as a forward-only event: the remedy is to publish a new version and, where the ecosystem supports it, mark the bad version as withdrawn. Overwriting the bad version in place destroys the immutability guarantee every consumer depends on
- **MUST NOT** derive a version reference from anything that can change independently of the content, such as a moving branch name or a rebuilt-nightly label
- **MUST** ensure a version reference is independently re-fetchable at the moment the version is declared shipped, per `spec/project/release-artifact/`; this spec adds that the re-fetch **MUST** yield the same content the pipeline published
- **SHOULD** publish a content digest alongside the version reference where the ecosystem provides one, so a consumer can verify identity without trusting the reference alone

### C. Provenance

- **MUST** record, for every published artifact, the commit it was built from, the pipeline run that built it, and the pinned inputs the build resolved
- **MUST** have the provenance record produced by the pipeline itself rather than by the build being attested; a build that attests to its own integrity can't detect its own compromise
- **MUST** make the provenance record retrievable by a consumer of the artifact rather than only readable inside the pipeline's own logs, which expire
- **SHOULD** publish the provenance record in a verifiable form (a signed attestation) rather than as unsigned metadata, so tampering after publication is detectable
- **SHOULD** treat provenance as evidence of **origin**, never as evidence of **safety**: an attested artifact is one whose build path is known, not one that has been judged secure. Security findings remain the concern of the supply-chain stages in `spec/project/continuous-integration/` §G
- **MAY** omit signed attestation for an artifact class whose ecosystem provides no verification path, and **MUST**, when omitting it, record which artifact classes lack provenance rather than leaving the gap implicit

### D. The artifact-to-securing-stage matrix

Every artifact class a project ships needs a named stage that secures it. The point of the matrix is that a gap becomes visible: an artifact class with no securing stage is an artifact shipping unguarded.

- **MUST** declare, per project, a mapping from each artifact class it ships to the delivery stage that secures that class and the guarantee that stage provides. The artifact classes come from `spec/project/release-artifact/` §Artefact taxonomy and **MUST NOT** be re-enumerated here
- **MUST** treat the following guarantees as the securing obligations a stage can carry, and **MUST** name at least one for each artifact class:
  - **built-from-source**: the artifact was produced by the pipeline from the attested commit, not uploaded from elsewhere
  - **integrity**: the artifact's content is fixed and verifiable through a digest or signature
  - **provenance**: the artifact carries a retrievable record of its origin, per §C
  - **policy-cleared**: the artifact's dependency, license, and security obligations were evaluated before publication, per the specs that own them
- **MUST** treat an artifact class with no securing stage as a defect in the pipeline design rather than as an acceptable omission, and **MUST** surface it as such when the pipeline is reviewed
- **SHOULD** keep the mapping in a form a reviewer can read without reconstructing it from workflow files
- **MAY** let one stage secure several artifact classes when the guarantee genuinely applies to all of them

### E. Release dispatch boundary

- **MUST** dispatch into `spec/project/release-automation/` for the draft-to-published transition rather than implementing that transition in the delivery pipeline; the pre-publish gate, the version-bearing file alignment, and the publication mechanics are owned there
- **MUST NOT** restate, weaken, or shortcut any pre-publish gate declared by that spec. A delivery pipeline that publishes without those gates has replaced the governed path with an ungoverned one
- **MUST** treat the propagation of a published release to `main` as owned by `spec/project/branching-model/`, and **MUST NOT** implement a parallel mechanism for it
- **SHOULD** surface a failed dispatch as a delivery failure rather than as a silent no-op, so an unpublished release is visible instead of merely absent

### F. Handover to deployment

- **MUST** end the delivery pipeline's responsibility at the published artifact plus its provenance; configuring, hardening, and running the workload is owned by `spec/project/kubernetes-deployment-best-practices/` and `spec/project/bjw-s-common-chart-deployment/`
- **MUST** make the handover explicit: the delivery pipeline names the artifact reference a deployment consumes, and the deployment side resolves it. An implicit handover, where the deployment discovers a new version by watching a moving reference, defeats §B
- **MUST NOT** let a deployment concern leak back into the delivery pipeline as an undeclared stage; when delivery genuinely needs to trigger a deployment, the trigger **MUST** be a declared stage that hands over an artifact reference rather than a stage that configures the workload
- **SHOULD** treat the set of consumers of a published artifact as a known quantity, so a rollback (§G) can name who is affected

### G. Rollback

- **MUST** define recovery from a bad version as **selecting a different artifact version**, which is only possible because §B guarantees old versions still resolve to their original content
- **MUST NOT** define rollback as rebuilding an older commit: a rebuild resolves inputs at rebuild time and therefore produces a different artifact than the one that was known good
- **MUST** keep the previous known-good version reference retrievable for as long as a rollback to that version stays a plausible response
- **SHOULD** rehearse the rollback path rather than documenting it untested; an unrehearsed rollback is discovered to be broken at the worst moment
- **SHOULD** record, when a version is withdrawn, why it was withdrawn and which version supersedes it, so a consumer pinned to the bad version learns what to do

### H. Environments and promotion

- **MUST** treat single-stage delivery as the default model: an artifact is published once and consumed directly. This matches how the portfolio actually ships and keeps the governed path short
- **MUST**, when a project does introduce environment promotion, promote the **same artifact** through environments rather than rebuilding per environment; a rebuild per environment means the tested artifact isn't the shipped artifact
- **MUST** keep environment-specific values in configuration consumed at deployment time rather than baked into the artifact, so the promoted artifact stays identical across environments
- **MUST**, for an artifact class that genuinely can't defer its configuration to deployment time, take exactly one of two paths and record which: split the build so the environment-specific part is a separately-published, deployment-time-resolved input, or declare a recorded exemption naming the artifact class, the values baked in, and the compensating check that the per-environment builds differ only in those values. An unrecorded per-environment rebuild remains prohibited
- **SHOULD** declare an approval gate between environments as an explicit, recorded decision point when one exists, rather than as an operator convention
- **MAY** omit environment promotion entirely; it's an optional pattern, and a project without it isn't deficient

### I. Delimitation

- **MUST NOT** restate any rule owned by `release-artifact`, `release-automation`, `release-skill-layer`, `branching-model`, `workflow-health`, or the deployment specs; where this spec needs one of those rules, it references it
- **MUST** route a red delivery run to `spec/project/workflow-health/` for triage
- **MUST** hand back to `spec/project/continuous-integration/` for anything that runs before the merge, even when defined in the same file

## Acceptance Criteria

- [ ] Every artifact a project ships is produced by the delivery pipeline, and no publication path exists that bypasses it
- [ ] Every delivery stage runs from a declared trigger, and any human decision point in the chain is a declared trigger carrying a recorded rationale
- [ ] No published artifact traces to a commit that didn't pass the pre-merge gate
- [ ] No published version reference in the project can be republished with different content
- [ ] Every published artifact has a retrievable provenance record naming its commit, its pipeline run, and its pinned inputs
- [ ] The provenance record is produced by the pipeline rather than by the build it attests
- [ ] A per-project mapping exists from each shipped artifact class to a securing stage and at least one named guarantee, and no shipped artifact class is missing from it
- [ ] Artifact classes without a verification path are recorded as such rather than silently absent from the mapping
- [ ] The draft-to-published transition is dispatched into `release-automation` rather than rebuilt locally, and no pre-publish gate is bypassed
- [ ] The delivery pipeline hands a named artifact reference to the deployment side and configures no workload itself
- [ ] The documented rollback path selects a previously published artifact version and never rebuilds an older commit
- [ ] The previous known-good version reference resolves at the time a rollback would need it
- [ ] In a project with environment promotion, the artifact promoted to the last environment is byte-identical to the one tested in the first, or the artifact class carries a recorded build-time-configuration exemption naming its baked-in values and compensating check
- [ ] Reviewing the spec against `release-artifact`, `release-automation`, `branching-model`, and the deployment specs surfaces no restated rule, only references

## References

- `spec/project/continuous-integration/`: the pre-merge half of the pipeline this spec continues from
- `spec/project/release-artifact/`: the artifact taxonomy and `artifact_ref` shapes §D maps over and refuses to restate
- `spec/project/release-automation/`: the draft-to-published transition and pre-publish gate §E dispatches into
- `spec/project/release-skill-layer/`: the operator-facing curation and dispatch layer
- `spec/project/branching-model/`: how a published release propagates to `main`
- `spec/project/kubernetes-deployment-best-practices/`, `spec/project/bjw-s-common-chart-deployment/`: the deployment side §F hands over to
- `spec/project/dockerfile-best-practices/`: the build definition for the container-image artifact class
- `spec/project/workflow-health/`: the operational counterpart this spec hands red runs to
- `spec/project/github-actions-best-practices/`: the single concrete platform binding
- [R1] SLSA v1.0 build levels: the source of the §C rule that provenance is generated by the build platform rather than by the build itself, and of the distinction between attested origin and demonstrated safety: <https://slsa.dev/spec/v1.0/levels>

## Open Questions

- §C requires a retrievable provenance record but stops short of mandating a signed attestation for every artifact class, because not every ecosystem this portfolio publishes to offers a verification path. Which classes can reach signed provenance today, and which are genuinely blocked, hasn't been surveyed.
- §D's mapping has no declared file format. Whether it belongs in the repository's existing portfolio manifest, in a dedicated file, or as a documented section is unresolved; the requirement is that a reviewer can read it, not where it lives.
- §G requires that a previous known-good version stay retrievable for as long as a rollback to that version stays a plausible response, which is deliberately unquantified. Whether a portfolio-wide retention floor is worth setting should be revisited once a real rollback has been exercised.
- §H now specifies both paths for an artifact class that embeds configuration at build time (a build-time split, or a recorded exemption with a compensating check). Which classes in this portfolio actually need either path hasn't been surveyed, so the clause is specified but untested against a real case.
