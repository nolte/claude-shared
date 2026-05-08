# Project Roadmap

Status: draft

## Context

Readers: repo maintainers of hobby-scale nolte projects who invoke the `roadmap-init`, `roadmap-refine`, and `roadmap-planner` skills, plus the implementing authors writing those skills against this schema.

The nolte portfolio is built largely from hobby-scale projects. Sprint cadence, available capacity, and even whether a project is currently active all vary widely from week to week. Existing specs cover individual delivery mechanics (`release-automation`, `release-skill-layer`, `quality-gate`) and reflective rituals (`continuous-improvement`, which explicitly opts out of sprint cadence), but nothing yet defines **what work is queued, why it matters, and in which order it should be executed**. This spec introduces that planning layer as a markdown artefact pair under `project/` in the target repo, intentionally lightweight enough for a hobby project yet structured enough that consuming Claude skills (`roadmap-init`, `roadmap-refine`, `roadmap-planner`) and the sibling specs (`sprint`, `feature`, `release-artifact`) can read and write it deterministically. The roadmap is a stepping-stone document: it ties every queued item back to a project outcome so that capacity is always spent on something the end user values.

## Goals

- Define the on-disk shape of a project roadmap as two markdown files at the repo root: `project/roadmap.md` (the queue) and `project/goals.md` (the vision plus outcomes the queue serves).
- Specify a stable per-item schema (frontmatter-anchored fields) so that consuming skills can parse, mutate, and re-render items without hand-rolling a parser per skill.
- Specify a mandatory detail-level convention (`fine` for the next two sprints, `coarse` or `backlog` beyond that) so that planning effort is spent where it pays off and farther-out items aren't over-specified prematurely.
- Tie every roadmap item to at least one outcome from `goals.md` so that prioritisation conversations always have an answer to "for whom does this matter."
- Stay portfolio-reusable: every project type the portfolio supports (Claude plugin, Python application, Python library, Node / TypeScript, CLI tool, documentation-only, the same taxonomy as `github-issue-templates-apply`) can adopt the layout without per-type schema variations.

## Non-Goals

- Defining sprint mechanics, feature schema, or release-artefact rules. Each of those is owned by its own sibling spec (`sprint`, `feature`, `release-artifact`); this spec only declares relationships, not internals.
- Replacing project-management tooling (Jira, Linear, GitHub Projects). The roadmap is a markdown artefact under version control, not a ticket store; cross-references to issue trackers are allowed but never authoritative.
- Mandating a time axis. Sprint duration is explicitly variable per the sibling `sprint` spec, so the roadmap doesn't carry start/end dates per item; it carries an ordering and a coarse-to-fine detail gradient instead.
- Substituting `continuous-improvement`. That spec runs on event- and calendar-driven audits, not on sprint cadence, and remains the authority for retrospective process change.
- Substituting `audience-identification`. Outcomes in `goals.md` are derived from the audience artefact when one exists; this spec consumes that artefact, never invents audiences inline.

## Requirements

### Directory layout

- **MUST** place both files at the repo root under `project/`: `project/roadmap.md` and `project/goals.md`. The directory is a top-level orientation point, not nested under `docs/`.
- **MUST NOT** split the roadmap across multiple files; there is exactly one `project/roadmap.md` per repository.
- **SHOULD** keep `project/goals.md` short enough that it can be read in one sitting (one screen of vision plus a flat list of outcomes is the target shape).
- **MAY** carry sibling files defined by other specs in the suite (`project/sprints/<n>-<slug>.md`, `project/features/<slug>.md`); their existence and shape is governed by the `sprint` and `feature` specs respectively.

### `goals.md` shape

- **MUST** open with a single-paragraph **Vision** section that states what the project is and who it's for, in the project's primary language.
- **MUST** carry an **Outcomes** section listing one or more outcomes. Every outcome **MUST** have a stable identifier (`O-<n>`, monotonically assigned, never reused) and a one-sentence description phrased as an end-user benefit.
- **MUST** trace each outcome back to an audience entry from the repo's audience artefact (typically `AUDIENCES.md` per `audience-identification`); when the repo has no audience artefact, `audience-identify` **MUST** be dispatched before writing outcomes—the dispatch is mandatory, not discretionary, because outcomes whose audience is invented inline can't serve a real reader.
- **MUST NOT** invent audience entries inline; missing audiences are a blocker for outcome authoring, not a hint to fabricate.

### `roadmap.md` shape and per-item schema

- **MUST** structure the roadmap as a flat ordered list (top-to-bottom is highest-to-lowest priority) of roadmap items. Items **MAY** be grouped under level-2 phase headings (for example `## Phase 1 — Foundations`) when phases help reading; phases are optional and carry no schema beyond the heading text.
- **MUST** represent every roadmap item as the following three-part shape, in this order: (a) a level-3 markdown heading naming the item (typically a `###` heading whose text reads `<id>` followed by an em-dash and the `<title>`, as illustrated in the concrete-shape example below); (b) immediately followed by a fenced YAML code block (` ```yaml … ``` `) carrying the schema fields below, in the declared order; (c) immediately followed by the free-text body whose required depth is gated by `detail` (see below). The heading-plus-YAML-block pair identifies the item to consuming skills; the body is for human reading. A standalone document-level YAML frontmatter (`---` at the top of `roadmap.md`) is **not** how items are represented; each item carries its own inline YAML code block.
- **MUST** carry the following fields in the per-item YAML block, in this order:
  - `id` (string, required): pattern `R-<n>`, monotonically assigned, never reused;
  - `title` (string, required): one-line summary in the project's primary language;
  - `detail` (enum, required): one of `fine`, `coarse`, `backlog`;
  - `outcomes` (list of outcome IDs, required, non-empty): every entry **MUST** match an `O-<n>` from `goals.md`;
  - `target_sprint` (integer or null, required, may be null): the sprint number this item is currently queued for; the field **MUST** appear in the YAML block even when null, so item parsers can rely on a stable key set;
  - `mvp` (boolean, required): `true` marks the item as part of the MVP scope (mandatory for fulfilling the project's mission), `false` marks it as post-MVP (optional, named explicitly so the boundary stays visible). The field's location in this schema is owned by this spec; the field's semantics, the stabilisation gate, and the audit rules around flag flips are owned by the sibling `mission` spec—see `spec/project/mission/<canonical_language>.md`. Repositories without a `project/mission.md` **MAY** carry `mvp: false` on every item or omit the file entirely; once a mission file exists, every roadmap item **MUST** carry the field;
  - `status` (enum, required): one of `proposed`, `active`, `done`, `cancelled`.
- **MUST** follow each YAML block with a free-text body whose required depth is gated by `detail`:
  - `fine`: a paragraph stating the user-visible change and a checklist of intended features (titles only; actual feature schema lives in the `feature` spec);
  - `coarse`: one or two sentences describing the intent;
  - `backlog`: a single sentence is enough.
- **MUST NOT** carry effort estimates, dates, or assignment fields; those belong to the consuming sprint and feature artefacts.

Concrete shape of one `fine` item inside `roadmap.md`:

````markdown
### R-3 — Replace the legacy auth flow

```yaml
id: R-3
title: Replace the legacy auth flow
detail: fine
outcomes: [O-1, O-4]
target_sprint: 7
mvp: true
status: proposed
```

End users authenticate via the new SSO provider in under three steps; the legacy session-token path is decommissioned.

- [ ] sso-redirect-flow
- [ ] legacy-auth-decommission
````

### Detail-level convention and refinement rule

- **MUST** ensure that, at any point in time, every roadmap item with `target_sprint` set to **the current sprint** or **the next one** carries `detail: fine`. **The current sprint** is defined as the sprint whose `status` is `active` per the sibling `sprint` spec (at most one such sprint per project); when no sprint is `active`, the current sprint is the lowest-numbered `planned` sprint, falling back to the highest-numbered `closed` sprint if none is `planned`. **The next sprint** is the lowest-numbered `planned` sprint whose `number` is greater than the current sprint's `number`. The skill `roadmap-refine` is the canonical enforcement point and **MUST** raise a violation when this invariant breaks. A violation **MUST** be reported as a structured record carrying the item `id`, the offending `target_sprint`, the current `detail`, the resolved current and next sprint numbers (so the operator can see why the item was flagged), and a one-line remediation hint; the consuming skill exit code is non-zero, and the violation is written to stderr (or the skill's structured output channel) for downstream tooling to pick up.
- **MAY** carry items with `detail: coarse` or `detail: backlog` for any sprint two or more ahead of the current one; promotion to `fine` is the trigger for `roadmap-refine` to pull the item into shape.
- **SHOULD** keep the count of `fine` items bounded to roughly the next two sprints' worth of capacity; an unbounded `fine` block defeats the gradient and re-introduces premature over-specification.

### Outcome linkage

- **MUST** reject any roadmap item whose `outcomes` list is empty or references an outcome ID that does not exist in `goals.md`. Consuming skills **MUST** refuse to write such items.
- **SHOULD** prefer one or two outcome links per item; long lists are a smell that the item should be split.

### Sprint and feature linkage

- **MAY** assign `target_sprint` to suggest which sprint should pick the item up; the suggestion is non-binding and the actual sprint composition is owned by `sprint-plan` per the sibling `sprint` spec.
- **MUST** clear or re-target `target_sprint` when its referenced sprint reaches terminal status (`closed` or `cancelled`) without picking the item up; `sprint-plan` owns this update at sprint closure. The valid post-closure values are `null` (item drops back to unscheduled) or a new integer pointing at a `planned` sprint. Leaving `target_sprint` pointing at a terminal sprint is a lint violation.
- **MUST NOT** include feature definitions inline. Decomposition of a roadmap item into one or more features is the contract of the sibling `feature` spec and the `feature-decompose` skill; the roadmap item only references its features by ID once they exist (the back-reference lives on the feature side, not in the roadmap).

### Lifecycle

- **MUST** transition `status` only along these paths: `proposed → active`, `active → done`, `proposed → cancelled`, `active → cancelled`. Direct `proposed → done` is forbidden because every done item must have been actively worked on; `cancelled → *` is forbidden because cancelled items are archival.
- **MUST** mark an item `active` no later than the moment one of its features enters `in_progress` per the `feature` spec; the consuming skill (`sprint-execute` when it advances a feature) is the canonical enforcement point.
- **MUST** mark an item `done` only when every feature it spawned is `done` **and** the corresponding sprint has reached `closed` (specifically `closed`, not `cancelled`); a sprint that closed without picking up every spawned feature blocks the item from `done` until the remaining features are re-targeted. A sprint that reaches `cancelled` from any stage **MUST NOT** advance any roadmap item to `done` even when every individual feature in the sprint reached `done`, because cancellation means no deployable artefact materialised the value statement; in that case the roadmap item's pending features **MUST** be re-targeted to a new sprint and the item remains `active` until that successor sprint reaches `closed`.

### Phases

- **MAY** group items under level-2 phase headings (for example `## Phase 1 — Foundations`); phases are documentation, not schema. A phase has no ID, no status, and no separate frontmatter, and a flat roadmap with zero phase headings is equally valid.

### Hobby-scale variability

- **MUST NOT** require dates, time estimates, or velocity tracking. Sprint duration is variable per the sibling `sprint` spec, and the roadmap is the wrong place to assert otherwise.
- **SHOULD** tolerate long stretches of inactivity gracefully: the roadmap is a queue, not a schedule, so `status: proposed` items remain valid indefinitely.

## Acceptance Criteria

- [ ] `project/roadmap.md` and `project/goals.md` exist at the repo root of every adopting project; nested or alternative locations fail validation.
- [ ] `goals.md` opens with a Vision paragraph and an Outcomes section where every outcome has an `O-<n>` ID and a one-sentence end-user benefit description.
- [ ] Every roadmap item in `roadmap.md` carries a level-3 markdown heading immediately followed by a fenced YAML code block (` ```yaml … ``` `) with the seven schema fields (`id`, `title`, `detail`, `outcomes`, `target_sprint`, `mvp`, `status`) in the declared order, immediately followed by the free-text body; `target_sprint` is always present, with the literal value `null` when the item is unscheduled, and `mvp` is always present as a boolean once the repository carries a `project/mission.md`.
- [ ] Every roadmap item's `outcomes` list resolves: each entry matches an `O-<n>` defined in `goals.md`; lints fail otherwise.
- [ ] No roadmap item with `target_sprint` equal to the current or next sprint carries `detail` other than `fine`; `roadmap-refine` raises a violation when this invariant is broken.
- [ ] No `proposed` item moves directly to `done`; the only allowed transitions are `proposed → active → done`, `proposed → cancelled`, and `active → cancelled`.
- [ ] No effort estimates, calendar dates, or assignment fields appear on roadmap items; lints flag any unknown frontmatter key.
- [ ] No roadmap item carries `target_sprint` pointing at a `closed` or `cancelled` sprint; lints fail when a sprint reaches terminal state without `sprint-plan` clearing or re-targeting items still pointing at it.
- [ ] No roadmap item is in `status: done` while any feature it spawned is still in a non-terminal state (`draft`, `ready`, `in_progress`); enforced at sprint closure by `sprint-review`.
- [ ] No roadmap item advances to `status: done` from a sprint whose own status is `cancelled`, even when every feature on the item is individually `done`; the item's pending features must be re-targeted to a new sprint and the item remains `active` until that successor sprint reaches `closed`.
- [ ] `audience-identification` is dispatched before outcome authoring on a fresh repo with no audience artefact; outcomes are never invented inline.

## Open Questions

- Should the roadmap allow a tagging field (`tags: [perf, ux, infra]`) for filtering large queues, or does that belong to a future surface (a generated index page)? Defer until a project's roadmap exceeds roughly twenty `coarse`+`backlog` items.
- How do we represent dependencies between roadmap items (`R-7 depends on R-3`)? Frontmatter list (`depends_on: [R-3]`) is the obvious shape, but a hobby-scale roadmap rarely needs strict ordering beyond top-to-bottom; revisit when a real project hits an actual blocker chain.
- Should `target_sprint` accept a range (`target_sprint: [3, 5]`) for items that span multiple sprints, or is splitting the item the right answer? Splitting is preferred today; revisit if a real cross-sprint item appears that genuinely cannot be split.
- Should phases carry a stable identifier so that downstream tooling (release notes, audience-doc-author) can group changes by phase? Defer until at least one phase-aware consumer exists.
