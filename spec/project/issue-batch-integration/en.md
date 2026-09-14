# Issue Batch Integration

Status: draft

## Context

`spec/project/issue-orchestration/` takes **one** raw GitHub issue through comprehension, classification, the requirements gate, decomposition into work packages, specialist dispatch, and a verification gate, and stops at one open pull request. That contract is sound for an isolated issue and isn't changed here.

It gets expensive as soon as the backlog holds a *cluster*. Processed one at a time, a cluster of `n` issues costs `n` pull requests, and `spec/project/pull-request-workflow/` §"Sequential merge of multiple open PRs" then requires those `n` to merge serially with a rebase between each consecutive pair—so the cluster pays `n` quality-gate runs, `n` rebases, and `n` review contexts for what a reviewer understands as one change. Where the members touch the same files, those rebases also collide with each other.

That clusters occur here is **established**: `git log develop` shows `b4dd0f16` (#623), `0316be01` (#624), and `c969bc02` (#625) as three consecutive pull requests, each repairing the same repository-settings surface, each merged separately. Whether grouping would have measurably reduced that cost is **unestablished**—the observation that would settle it, a run of this process against a comparable cluster, hasn't been made.

This spec adds the group layer only: how a cluster is admitted as a group, understood and planned once at group level, developed on one dedicated integration branch, bundled into a single integration into `develop`, and closed out afterwards.

Boundaries: `spec/project/issue-orchestration/` owns everything that happens *inside* one member issue. `spec/project/pull-request-workflow/` owns pull-request shape, gates, merge strategy, and issue-closure semantics. `spec/project/branching-model/` owns branch prefixes, protection, and the release flow. `spec/project/parallel-working-copies/` owns worktree paths and lifecycle. `spec/claude/research-plan-implement/` owns the phase discipline this spec consumes for its analysis and plan. `spec/project/continuous-improvement/` owns the portfolio gap-closure loop and its recurrence threshold, and `spec/project/defect-class-guards/` owns what a closed defect class leaves behind; §E feeds both rather than restating them.

Readers: operators running a grouped backlog pass, skill and agent authors implementing the group layer, and reviewers who receive a bundle pull request and need to judge whether the group was one change.

## Goals

- A cluster becomes a group by a stated predicate, not by an operator's sense that the issues go together
- The group is understood and planned **once**, at group level, before any member is implemented
- The plan makes completeness checkable: every member traces to every artifact class it has to change, so a missing spec, test, doc, or index update is visible before the bundle opens rather than after the merge
- The group reaches `develop` as exactly one pull request, so the cluster costs one review context, one gate, one merge
- The choice between the two strand modes is deterministic rather than a judgement call
- Every member issue is closed after the integration, with a trail back to the bundle that produced it
- A cluster is read as evidence about the process that produced it, not only as a queue of work: a recurring pattern questions the rule or the gate that let it recur
- The existing per-issue machinery is reused unchanged

## Non-Goals

- Per-issue comprehension, classification, the requirements gate, decomposition, and specialist dispatch: `issue-orchestration` stays authoritative and this spec triggers it rather than redefining it
- Pull-request body structure, required checks, merge strategy, and the closing-keyword semantics: `pull-request-workflow` stays authoritative
- Branch prefixes, branch protection, and the release flow: `branching-model` stays authoritative
- Worktree paths, mapping, and retirement mechanics: `parallel-working-copies` stays authoritative
- The Research/Plan/Implement phase contract and its tier table: `spec/claude/research-plan-implement/` stays authoritative; this spec names only where its own phases sit
- The `roadmap → feature → sprint` pipeline: an unbounded issue routes there per `issue-orchestration` §"Routing to the formal pipeline" and grouping is never a substitute for planning
- Deciding *which* issues deserve attention: backlog triage is owned by `portfolio-inflight-triage` and the repository's sprint cadence
- The recurrence threshold at which a portfolio gap has to be closed, and the gap-closure loop itself: `continuous-improvement` stays authoritative and §E feeds it rather than re-deriving it

## Requirements

### A. Group formation and admission

- **MUST** admit an issue to a group only on at least one of exactly three predicates, recorded per member: **thematic coupling** (the members change the same capability or the same spec topic), **shared touch surface** (their work packages change overlapping files or paths), or **dependency chain** (one member's change has to land before another can)
- **MUST NOT** admit an issue on the ground that it's open in the same iteration or time window. A shared time window isn't coupling, and a group admitted that way is exactly the "unrelated changes in one pull request" case that `pull-request-workflow` §PR preconditions forbids outside an `exp/` branch
- **MUST** record, per admitted member, which predicate admitted it and the evidence for that predicate
- **MUST** state the group's single logical change in one sentence in the group artifact. This sentence is what reconciles a multi-issue bundle with `pull-request-workflow` §PR preconditions' one-logical-change rule: a group that satisfies the admission predicates *is* one logical change, so it needs no `exp/` carve-out. A cluster whose change can't be stated in one sentence isn't a group—its issues are processed individually
- **MUST** keep every member inside `issue-orchestration`'s *bounded* definition (one goal outcome, one pull-request strand, no new or retargeted roadmap item). An unbounded issue routes to the formal pipeline and **MUST NOT** be carried in a group
- **MUST NOT** admit a `question`-class issue, which yields no work packages by construction
- **MUST** assign the group a stable id `<YYYY-MM-DD>-<slug>`, used verbatim for the integration branch, the artifact path, and the checkpoint, so the three can't drift apart
- **SHOULD** keep a group small enough that its bundle diff is reviewable in one sitting; a group larger than that gets split into two groups rather than merged as one bundle too large to review

### B. Branch and working-copy topology

- **MUST** develop the group on exactly one dedicated **integration branch** created off `origin/develop`, inside a dedicated worktree per `parallel-working-copies` §Path layout and §Lifecycle: Create; the primary checkout stays on `develop`
- **MUST** name the integration branch `<type>/<group-id>`, where `<type>` is the Conventional-Commits type of the group's dominant change per `branching-model` §Branch roles
- **MUST NOT** default to the `exp/` prefix for a group that carries shipped work. `branching-model` §Branch roles excludes `exp` pull-request titles from user-facing release notes, so bundling outcome-bearing fixes or features onto `exp/` would erase them from the notes. `exp/` stays reserved for a group that's genuinely exploratory
- **MUST** re-synchronize the integration branch onto `develop` by rebase whenever `develop` advances, per `pull-request-workflow` §Branch freshness. The integration branch is the single point where that rule applies; member sub-branches rebase onto the integration branch, not onto `develop`
- **MUST**, in Mode B (§C), create each member sub-branch off the integration branch tip in its own worktree, since a branch is checked out at most once per `parallel-working-copies` §Branch-to-worktree mapping, and merge it back into the integration branch **without opening a pull request**
- **MUST NOT** open a pull request whose base is the integration branch. `pull-request-workflow` §PR preconditions requires every pull request to target `develop`, and the bundle pull request is the group's single review surface. The accepted trade-off is that a member gets no review gate of its own; §"Open Questions" records it
- **MUST** retire every member sub-branch and its worktree once it's merged into the integration branch, per `parallel-working-copies` §Lifecycle: Retire

### C. The mode gate

- **MUST** decide the strand mode before the first member is implemented, and record the decision with its reason in the group artifact:
  - **Mode A (single strand)**: every member is implemented directly on the integration branch
  - **Mode B (sub-branch)**: every member is implemented on its own sub-branch and merged into the integration branch per §B
- **MUST** choose Mode B when any member is likely to need **removal** from the bundle: its acceptance is uncertain, it depends on something outside the group's control, or a review that could reject it remains outstanding—most commonly a member classified `security`. That property is the criterion because a Mode B member can be removed from the bundle by dropping one merge, while a Mode A member is entangled in a shared commit strand
- **MUST** otherwise choose Mode A
- **MUST**, when a member turns out to need removal after Mode A was chosen, treat it as a **structural regression** per `spec/claude/research-plan-implement/` §"Re-planning is explicit": stop, name the assumption that failed, and return to Plan—either extracting that member onto its own branch or removing it from the group
- **MUST** return a dropped member to individual processing under `issue-orchestration` and record the drop in the group artifact; a dropped member stays in no group

### D. Group pre-analysis and the implementation plan

- **MUST** classify the group's work under `spec/claude/research-plan-implement/` §"Phase depth scales with blast radius" and record the tier. A group spans several issues and several files, so it's **at least Tier 2** and is Tier 3 when it crosses repositories or changes a published contract; the operator approval gate between Plan and Implement is therefore always required
- **MUST** persist the group's Research findings and its Plan as a single artifact at `.audits/issue-batch-integration/<group-id>/analysis.md`, carrying: the group id, the one-sentence logical change (§A), the member table (issue, class, admitting predicate, evidence), the cross-member dependency ordering, the shared touch surface, the mode decision with its reason (§C), the completeness matrix below, the risks, and the open questions for the operator
- **MUST** anchor every load-bearing claim in the findings to a `file:line`, a path, or a command with its output, per `spec/claude/research-plan-implement/` §"Research is isolated and anchored"
- **MUST** carry a **completeness matrix** whose rows are the member issues and whose columns are the artifact classes the repository actually ships—at minimum source, spec, tests, documentation, configuration and workflows, and generated indexes or catalogs. Every cell **MUST** hold either the named change or an explicit `not applicable` with a reason. An empty cell is an incomplete plan, not a tacit "nothing to do here"; the matrix is what makes "every relevant adaptation happened" checkable instead of asserted, and it's the form `spec/claude/research-plan-implement/` §"The plan is the review surface" already requires
- **MUST** derive the column set from the repository under change rather than from a fixed list, so a repository that ships no tests doesn't carry an empty column and one that ships a generated catalog doesn't silently omit it
- **MUST** give every matrix cell that holds a change the check that proves it, per `spec/claude/research-plan-implement/` §"Verification belongs inside the plan"
- **MUST** obtain operator approval of the artifact before the first member is implemented; implementing against an unapproved group plan is forbidden
- **MUST** treat the admission of a further member after the plan is approved as a structural regression, not an amendment: the plan returns to Plan, the matrix is recomputed, and the operator re-approves
- **MUST** treat the artifact as run-scoped exactly as `issue-orchestration` §"Pre-analysis artifact lifecycle" treats its own: committed on the integration branch, removed by a fix-forward `git rm` once every member is implemented and the gate is green, never reaching the default branch, and never concealed behind a `.gitignore` entry. Where a delegated member run writes its own `.audits/issue-orchestrate/<n>/analysis.md` on the same branch, both are removed before the bundle merges
- **MUST NOT** restate a member's own decomposition in the group artifact; the group artifact records the group layer, and the member's work packages stay with the delegated run

### E. Structural findings and process feedback

- **MUST** analyse the group **across** its members for a structural cause before the plan is written, and record the result in the group artifact. A group is by construction a set of issues that already share a coupling, so it's the first corpus in which a pattern shows that no single issue reveals; analysing each member only in isolation throws that evidence away
- **MUST** distinguish a **symptom cluster** (several issues, one root cause) from a **class cluster** (several issues of one recurring defect class), and record which of the two the group is. Where the group is a symptom cluster, the plan **MUST** target the root cause rather than repairing `n` symptoms
- **MUST**, where the group is a class cluster, bind the class per `spec/project/defect-class-guards/` §"Binding into the closing process" and carry its sweep once at group level per §G
- **MUST** feed every recurring finding class the group surfaces into the portfolio loop that `spec/project/continuous-improvement/` §"Portfolio gap closure (the loop stays alive)" owns, recording the class and its recurrence count. This spec **MUST NOT** restate or re-derive that spec's recurrence threshold: the group supplies the evidence, the loop owns the trigger
- **MUST** record a **process finding** when the structural cause sits in the development process rather than in the changed artifacts—a rule that permits the defect, a gate that doesn't catch it, a check that doesn't exist—and **MUST** file it as its own issue against the governing spec or gate, referencing the group id. A process finding **MUST NOT** count as resolved once the group's members are repaired, because repairing them leaves the process that produced them untouched
- **MUST** name, for every process finding, the concrete preventive change: the rule, the guard, or the check that would have stopped the group from arising. A process finding without a named preventive change is an observation, not a finding, and isn't filed as one
- **SHOULD** record explicitly when no structural cause was found, so its absence is a statement the operator can challenge rather than a silent omission

### F. Per-member delegation

- **MUST** delegate each member's comprehension, classification, requirements gate, decomposition, and specialist dispatch to `issue-orchestration`, and **MUST NOT** re-derive any of them here
- **MUST** name the hand-off boundary per `spec/claude/research-plan-implement/` §"Binding on skill and agent authoring": the group layer owns Research, Plan, and the member ordering; the delegated run owns its member's Implement phase and its verification, and **MUST NOT** open a pull request or merge
- **MUST** implement members in the dependency order the artifact records, and **MUST** record each member's result before a dependent member starts
- **MUST** run `quality-gate` against the **integration branch tip** before the bundle pull request opens. A green gate on a member sub-branch isn't evidence for the bundle, for the same reason `parallel-working-copies` §"Interaction with other portfolio specs" gives: a green gate in a different worktree isn't evidence for this one

### G. Bundling and integration

- **MUST** reach `develop` as exactly one pull request, opened from the integration branch and satisfying `pull-request-workflow` in full; its title type equals the integration branch's prefix
- **MUST** list every member under `## Linked issues` with the repository's closing keyword, and **MUST** record in **Risk / rollout notes**: the group id, the admitting predicate per member, the mode with its reason, and per member the dispatched specialist or the explicit no-matching-specialist note that `issue-orchestration` §"Verification and traceability" already requires per issue
- **MUST**, where the bundle's type is `fix`, carry exactly **one** `## Class sweep` section per `pull-request-workflow` §"Class sweep" covering the group's defect class as a whole. A group admitted on thematic coupling of one defect class has one predicate by construction; one sweep per member would restate it `n` times and measure nothing extra
- **MUST** remove every transient artifact (§D) before the bundle merges, so the durable trail is the pull-request body plus the per-issue comments
- **MUST**, when a member has to be dropped after the bundle pull request is open, remove that member's changes from the integration branch—in Mode B by dropping its merge—and update both the artifact and the pull-request body, or close the bundle and re-group; a bundle **MUST NOT** merge while claiming a member it no longer carries
- **MUST NOT** merge the bundle itself; the group process stops at an open, audit-trailed pull request and hands the merge to `pull-request-merge`

### H. Closeout

- **MUST** close every member issue after the bundle's squash-commit lands on `develop`, with explicit operator confirmation. `pull-request-workflow` §"Linked-issue closure on develop merge" establishes that the closing keyword doesn't fire on a `develop` merge, so closure is an act of this process rather than a platform side effect
- **MUST** name, in each closure comment, the bundle pull request, the merge-commit SHA on `develop`, and the group id, so a member issue leads back to the bundle that resolved it
- **MUST NOT** close a member that was dropped from the group
- **MUST** retire the integration branch and its worktree after the merge, per `parallel-working-copies` §Lifecycle: Retire

### I. Resumption and operator gating

- **MUST** be resumable per `spec/claude/resumable-work/`, with checkpoints at every phase boundary—admit, analyse, plan, per-member implement, bundle, close—as `spec/claude/research-plan-implement/` §"Binding on skill and agent authoring" requires at minimum
- **MUST** gate every externally-visible action on operator confirmation: the artifact write, the mode decision, each member dispatch, the bundle pull request, and each issue closure

## Acceptance Criteria

- [ ] Every member in a group artifact records exactly one admitting predicate from the closed set of three, with its evidence, and no member is admitted on a shared time window
- [ ] The group artifact states the group's logical change in one sentence
- [ ] The group artifact records a tier of 2 or higher and an operator approval taken before the first member was implemented
- [ ] The completeness matrix carries one row per member and one column per artifact class the repository ships, no cell is empty, and every cell holding a change names the check that proves it
- [ ] Every group artifact records either a structural finding across its members or an explicit statement that none was found
- [ ] Every group artifact records whether the group is a symptom cluster or a class cluster, and every symptom cluster's plan targets the root cause rather than `n` symptom repairs
- [ ] Every process finding names its preventive change (a rule, a guard, or a check) and exists as its own issue referencing the group id; none was treated as resolved by repairing the group's members alone
- [ ] Every recurring finding class a group surfaced reached the `continuous-improvement` loop with its recurrence count, and no group artifact restates that spec's recurrence threshold
- [ ] The integration branch's prefix equals the Conventional-Commits type of the bundle pull-request title, and is `exp/` only where the group is exploratory
- [ ] No pull request in the repository has a base other than `develop` (`gh pr list --state all --json baseRefName`), so no group-internal pull request was opened
- [ ] For every Mode B group, each member sub-branch was merged into the integration branch and carries no pull request of its own
- [ ] Every group artifact records its mode with a reason, and no Mode A group carries a member marked as needing removal
- [ ] Every dropped member is recorded as returned to individual processing and isn't closed
- [ ] The default branch's tree carries no `.audits/issue-batch-integration/` path (`git ls-tree -r --name-only develop -- .audits/issue-batch-integration/` is empty) and no commit reachable from it adds one
- [ ] The integration branch carries both the artifact's creation commit and its removal commit, the removal post-dates the last member result, and `.gitignore` carries no `.audits/issue-batch-integration/` entry
- [ ] The bundle pull request's **Risk / rollout notes** names the group id, the per-member admitting predicate, the mode with its reason, and per member the dispatched specialist or the explicit no-matching-specialist note
- [ ] A `fix`-typed bundle carries exactly one `## Class sweep` section whose `Predicate` was actually run
- [ ] `quality-gate` reported green on the integration branch tip before the bundle pull request opened, and that result wasn't inherited from a member sub-branch
- [ ] Every member issue was closed after the `develop` merge with a comment naming the bundle pull request, the merge-commit SHA, and the group id; none was closed silently by the platform autolink
- [ ] After the merge, neither `git worktree list` nor `git branch --list` mentions the integration branch or any member sub-branch
- [ ] The checkpoint under `.resume/` records a decision entry for every gate: the artifact write, the mode decision, each member dispatch, the bundle pull request, and each issue closure

## Open Questions

- Whether a group needs a size backstop in addition to the removal criterion (§C) is deferred. That criterion names the property Mode B actually buys; a member count would be a proxy whose threshold no run has yet calibrated. **Revisit trigger:** a recorded group whose Mode A strand grew too large to review while no member needed removal.
- §B removes the per-member review gate by forbidding group-internal pull requests, which keeps the process consistent with `pull-request-workflow` §PR preconditions at the cost of reviewing every member only in the bundle. Whether that needs a compensating mechanism—a per-member review pass inside the bundle, or a declared exemption in `pull-request-workflow`—stays open until a bundle is recorded in which a member's defect survived the collective review.
- Whether the group artifact should be mirrored into each member issue by default, rather than only on operator confirmation, is deferred pending operator preference across real runs.
