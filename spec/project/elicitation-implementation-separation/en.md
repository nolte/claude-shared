# Elicitation–Implementation Separation

Status: draft
Portfolio-Scope: portfolio

## Context

Readers: contributors working under the portfolio's working method—the person who
elicits requirements (the *elicitor*), the reviewer who approves the requirements
pull request, and the specialists who later implement against the merged
requirements. This spec anchors an **optional, named working mode** that cleanly
separates **requirements elicitation** (*Bearbeitung*) from **implementation**
(*Umsetzung*).

The portfolio already separates analysis from implementation *within a single
orchestrated run*: `spec/project/issue-orchestration/` comprehends an issue, elicits
or confirms its requirements, decomposes them, and only then dispatches specialists—all
inside one worktree, one pass, one pull request. That works when the requirements
and the implementation are handled together by one contributor in one sitting.

What that pattern doesn't offer is a way to make the **elicited requirements a
standalone, merged artefact with a stable permalink** that lands *before* any implementation
begins, so a different contributor—or the same one, later—can pick up a
commit-stable requirements document and implement it. Sometimes the elicitation is
the valuable, reviewable work in its own right; the implementation is deferred,
handed to a specialist, or scheduled independently. Without a named mode, that split
is improvised: requirements and code land in the same pull request, the requirements
never exist as an independently reviewable artefact, and the hand-off from "what we
agreed to build" to "who builds it" is informal.

This spec names that split and prescribes its flow. It does **not** make separation
mandatory: a contributor who wants to elicit and implement together stays on the
integrated `issue-orchestration` path. The mode is a tool a contributor **MAY** reach
for when they want the requirements to be a merged artefact before implementation
starts.

## Goals

- Give the portfolio a **named, optional working mode** that separates requirements
  elicitation from implementation, so contributors have a shared vocabulary and a
  prescribed flow when they choose to split the two phases
- Make the elicited requirements a **standalone, merged, commit-stable artefact** that
  lands before any implementation, so it can be referenced by a permalink and handed
  to a specialist
- Prescribe a **four-step flow**—dedicated elicitation working copy → requirements-only
  pull request → tracking issue in the implementation-owning repo → specialist
  implementation—as the binding sequence *within* the mode, without forcing the mode
  on anyone
- Keep the mode **complementary to `issue-orchestration`**, not competing: the same
  elicitation-before-implementation discipline, lifted to a cross-working-copy /
  cross-pull-request workflow that orchestration MAY build on
- Keep affected documentation current: when specialists implement, every affected
  doc/spec is updated in the same pull request, reviewer-verified

## Non-Goals

- **Making separation mandatory.** This spec never forces the split. It says "*this*
  is how you separate cleanly when you choose to", not "you *must* always separate".
  The integrated path (`issue-orchestration`) remains fully valid.
- **Redefining requirements elicitation.** `spec/project/requirements-elicitation/`
  remains authoritative for *how* requirements are elicited and for the `U_gate` /
  `τ_high` confidence contract; this spec only positions the elicitation as a separate,
  merged phase and consumes that spec's artefact shape.
- **Redefining the worktree discipline.** `spec/project/parallel-working-copies/`
  remains authoritative for how a dedicated working copy is created and scoped; this
  spec only requires that step 1 uses one.
- **Redefining pull-request or merge rules.** `spec/project/pull-request-workflow/`
  and `spec/project/branching-model/` remain authoritative; the requirements-only pull
  request of step 2 flows through those gates unchanged.
- **Prescribing a tracking-issue template.** This spec fixes the *minimum field set*
  the tracking issue must carry (below); whether a fixed issue template or a label set
  backs it's left to the adopting repo.
- **Prescribing the implementation specialists.** Which specialist implements in step 4
  is resolved by the implementation-owning repo (for example, via
  `issue-orchestration`'s runtime specialist lookup), not fixed here.

## Requirements

### The working mode and its flow

- **MUST** treat "elicitation–implementation separation" as an **optional, named
  working mode**, not a mandatory gate: a contributor **MAY** choose it when they want
  to separate requirements elicitation (*Bearbeitung*) from implementation
  (*Umsetzung*); the portfolio **MUST NOT** require it for a change to be valid
- **MUST**, when the mode is chosen, follow a **four-step flow** as the binding
  sequence *within the mode*: (1) requirements elicitation in a dedicated working copy;
  (2) a pull request that lands **only** the requirements document into the default
  branch; (3) a tracking issue referencing the merged document, created in the
  implementation-owning repo; (4) implementation by specialists. The steps **MUST**
  run in this order—the merged requirements document is a precondition for the
  tracking issue, which is a precondition for implementation
- **MUST** be authored **portfolio-wide**: a spec under `spec/project/` inherited by
  adopting repos per `spec/project/portfolio-inherited-spec-layer/`, describing the
  mode as a portfolio way of working, not a repository-local convention

### Step 1—Elicitation in a dedicated working copy

- **MUST**, when the mode is chosen, perform requirements elicitation in its **own
  dedicated working copy** (a worktree per `spec/project/parallel-working-copies/`)
  whose **sole deliverable** is the requirements document
  (`project/requirements/<slug>.md`); no implementation happens in that working copy
- **SHOULD** produce that document through `spec/project/requirements-elicitation/`
  (the `requirements-elicit` methodology), so the merged artefact carries a confirmed
  understanding (its `U_gate` / confidence record) rather than unconfirmed prose

### Step 2—Pull request of the requirements document

- **MUST**, in step 2, open a pull request that lands **only the requirements
  document** into the default branch (`develop`) **before any implementation begins**;
  the merged document with a stable permalink is the hand-off artefact. The pull request flows
  through `spec/project/pull-request-workflow/` unchanged
- **MUST NOT** include implementation changes (code, specs beyond the requirements
  document, configuration) in the step-2 pull request; mixing them defeats the
  separation the mode exists to provide

### Step 3—Tracking issue with a stable reference

- **MUST** create the tracking issue in **the repo that owns the artefact to be
  implemented**—generalised as "the repo that owns the artefact to be implemented";
  it's not necessarily the repo where elicitation happened
- **MUST** have the tracking issue carry, at minimum: (a) a **commit-stable permalink
  to the merged requirements document** (the load-bearing reference—a permalink
  pinned to the merge commit, not a branch-relative link); (b) a short **title /
  description** of the change to implement; (c) a pointer to the **responsible
  specialists** or the expected implementation approach; (d) the explicit **charge to
  keep affected docs current**—the bridge to step 4's documentation-currency contract

### Step 4—Implementation by specialists

- **MUST** have the implementation performed by **specialists** (not the elicitor), who
  assess the necessary changes from the merged requirements document and carry them out
- **MUST**, when specialists implement, update **every affected doc/spec in the same
  pull request as the implementation**, and the pull-request reviewer **MUST** verify
  this as part of approval; documentation drift isn't admitted. This is the concrete,
  acceptance-testable meaning of "keep the docs current"

### Relation to `issue-orchestration` (complementary, not competing)

- **MUST** position this mode as **complementary to** `spec/project/issue-orchestration/`,
  which already separates analysis / elicitation from implementation *within a single
  orchestrated run*: this mode lifts the same separation to a **standalone, opt-in
  cross-working-copy / cross-pull-request workflow**—elicitation as a separate, merged
  artefact before any implementation—that orchestration **MAY** build on. It **MUST
  NOT** be framed as a competing rule; a contributor chooses the integrated path or the
  separated path per change, and both remain valid

### Scope of choosing the mode, and deferred mechanics

- **MAY** be chosen at the contributor's discretion: because the mode is opt-in, there
  is **no trivial-change exemption to define**—the threshold for what's "substantial
  enough" to warrant separating the phases is left to contributor judgement, not fixed
  by this spec
- **MAY** leave the fallback for "no suitable specialist exists" for step 4—whether
  the elicitor self-implements or the work is routed back—to the implementation step;
  this spec doesn't fix that fallback
- **MAY** leave the exact tracking-issue mechanics (a fixed issue template, a label
  set) to the adopting repo; only the minimum field set in step 3 is binding

### Placement of this spec (resolved)

- The placement of this working-method change—a new standalone spec versus an
  amendment / cross-reference inside existing working-method specs—was **resolved in
  favour of this standalone spec** (`spec/project/elicitation-implementation-separation/`),
  so the named mode and its four-step flow live in one coherent place rather than being
  fragmented across `parallel-working-copies`, `requirements-elicitation`, and
  `issue-orchestration`. Those specs remain authoritative for their own scope and are
  cross-referenced here

## Acceptance Criteria

- [ ] The mode is documented as optional and named; no portfolio spec makes the
  elicitation–implementation separation a precondition for a change to be valid
- [ ] When the mode is chosen, the four steps are present and ordered: a dedicated
  elicitation working copy, a requirements-only pull request, a tracking issue
  referencing the merged document, and specialist implementation
- [ ] The step-2 pull request contains only the requirements document
  (`project/requirements/<slug>.md`) and no implementation change
- [ ] The step-3 tracking issue carries a commit-stable permalink to the merged
  requirements document, a title/description, a specialist/approach pointer, and the
  doc-currency charge
- [ ] The step-4 implementation pull request updates every affected doc/spec in the
  same pull request, and the reviewer confirms this as part of approval
- [ ] The spec references `issue-orchestration` as complementary (not competing) and
  states that a contributor chooses the integrated or the separated path per change
- [ ] The spec is authored under `spec/project/` with `Portfolio-Scope: portfolio`, so
  adopting repos inherit it per `portfolio-inherited-spec-layer`

## Open Questions

- The fallback when **no suitable specialist exists** for step 4 (elicitor
  self-implements versus routing the work back) is deliberately left to the
  implementation step; whether the portfolio should fix a default is deferred until
  enough real runs exist to calibrate it.
- Whether the tracking issue of step 3 should be backed by a **fixed issue template /
  label set** (rather than only the binding minimum field set) is deferred to the
  adopting repos' preference.
- Whether `issue-orchestration` should gain an explicit "resume from a merged
  requirements artefact" entry path that consumes a step-2 document directly is noted
  as a natural extension but not required here.
