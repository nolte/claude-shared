---
name: sprint-execute
description: Drive the daily mechanics of an active sprint per the project sprint spec. Invoke when the user asks to start a sprint, start a feature, mark a feature in progress, mark a feature done, sync a sprint's feature list, or update the sprint's last commit. Also handles equivalent German-language requests. Promotes a `planned` sprint to `active` when the first feature starts, drives feature lifecycle transitions (`ready → in_progress`, `in_progress → done`), keeps the `## Features` body list and `features` frontmatter in lockstep, updates `last_commit` whenever a feature reaches `done`, and refuses to start a feature whose sprint isn't this one while another sprint is already `active`.
tags: [scaffolding]
---

# Sprint Execute

Drives the lifecycle of an `active` sprint per `spec/project/sprint/<canonical_language>.md`. This skill is the canonical write authority for `planned → active` promotion, feature `ready → in_progress` and `in_progress → done` transitions inside the sprint's scope, the `last_commit` frontmatter field, and the `## Features` body / `features` frontmatter sync. It deliberately doesn't close the sprint—`sprint-review` owns `active → review` and beyond.

## Why this is a skill, not an agent

- **The at-most-one-active-sprint invariant requires user-visible refusal** — when the user asks to start a feature whose sprint isn't the currently `active` one, the skill must surface the offending sprint number and the conflicting `active` sprint to the user, not silently fail; an agent's structured-report shape can't carry the recovery dialogue cleanly.
- **Output flows back into the main conversation** — feature transitions, sprint promotions, and `last_commit` updates all change frontmatter the user is iterating on; isolating them behind an agent boundary would obscure the running picture.
- **Mid-flow confirmation on lifecycle promotion** — `planned → active` happens as a side effect of the first `ready → in_progress`, but the operator deserves a one-line "starting sprint <N>" confirmation; that gate is core to the contract.
- Counter-dimension considered: a tool-restricted agent (read + a single frontmatter writer) could perform the bidirectional invariant check cleanly, but the load-bearing dimension is the user-facing refusal path on the parallel-active-sprint conflict — skill wins.

## User-language policy

Detect the user's language and respond in it. Sprint and feature markdown content stays in the project's primary language; frontmatter keys, lifecycle tokens, feature / sprint IDs, and the SHA strings written into `last_commit` are always English.

## Preconditions

Before mutating any sprint or feature file, confirm:

- Current working directory is inside a git repository with `project/sprints/` and `project/features/` populated.
- The user has named (or implied) a single concrete operation: start the next sprint, start a specific feature, mark a specific feature done, or sync the body / frontmatter of a specific sprint. If the request is ambiguous, ask before mutating.
- At most one sprint is currently `active`. If two or more are `active`, that's a pre-existing invariant violation per `spec/project/sprint/` §Lifecycle; stop, report the offending sprint files, and hand back—repair is the operator's job.

## Operations

This skill performs whichever of the operations below the user's request maps to. Each operation is its own deterministic block; the skill never silently extends one operation into another (no "started a feature, may as well close the sprint while I'm here").

### A. Promote `planned → active`

Triggered as a side effect of the first `ready → in_progress` transition on a feature whose `sprint` field matches a `planned` sprint, or directly when the user explicitly asks to start the sprint.

Steps:

1. Read every `project/sprints/*.md` file's frontmatter. Confirm no sprint is currently `active`. **If another sprint is `active`, refuse the promotion** with a verbatim error naming the conflicting sprint's number and slug, and stop. The at-most-one-active-sprint invariant comes from `spec/project/sprint/` §Lifecycle and is the canonical refusal point.
2. Confirm the target sprint is the lowest-numbered `planned` sprint. Promoting a higher-numbered `planned` sprint while a lower-numbered one exists is forbidden per the same spec section.
3. Set `status: active` and `started: <today's ISO date>` in the sprint's frontmatter.
4. Surface a one-line confirmation to the user: "Starting sprint <NNNN> — <slug>".

### B. Transition a feature `ready → in_progress`

Triggered when the user asks to start a specific feature.

Steps:

1. Read the feature file's frontmatter. Confirm `status: ready` and `sprint: <NNNN>` is non-null.
2. Read the sprint `<NNNN>` file's frontmatter. The feature's `id` **MUST** appear in the sprint's `features` list; if not, the back-reference is broken (per `spec/project/sprint/` §Roadmap and feature linkage). Stop and report the inconsistency.
3. **Enforce the at-most-one-active-sprint invariant.** Determine the sprint's current `status`:
   - `active` → continue to step 4.
   - `planned` and no other sprint is `active` → invoke operation A first, then continue.
   - `planned` while another sprint is `active` → **refuse the transition**, surface the conflicting `active` sprint, and stop. Don't promote, don't transition, don't sync; the operator must close or cancel the conflicting sprint first per the spec's invariant.
   - `review`, `closed`, or `cancelled` → refuse; the sprint is past activation.
4. Set `status: in_progress` on the feature.
5. Mark the feature's roadmap item `active` if it's still `proposed` per `spec/project/roadmap/` §Lifecycle.

### C. Transition a feature `in_progress → done`

Triggered when the user asks to mark a feature done.

Steps:

1. Read the feature file. Confirm `status: in_progress`. Confirm every acceptance-criterion checkbox in `## Acceptance criteria` is checked, and every `## Test hooks` entry has status `passing` or `skipped` (per `spec/project/feature/` §Lifecycle and gates). Stop and report any unchecked criterion or `pending` / `failing` hook.
2. Confirm the sprint named by the feature's `sprint` field is `active` or `review` per `spec/project/feature/` §Lifecycle and gates.
3. Set `status: done` and `ended: <today's ISO date>` on the feature.
4. **Update the sprint's `last_commit`.** Run `git rev-parse HEAD` to resolve the most recent commit SHA on the current branch, then write the result to the sprint's `last_commit` frontmatter field. This is the canonical write authority for that field per `spec/project/sprint/` §Frontmatter schema; `last_commit` anchors the artefact ancestry check that `sprint-review` runs at closure.
5. Surface the updated sprint state to the user: features remaining `in_progress`, `last_commit` SHA, and a hint that `sprint-review` becomes invokable when every feature in the sprint is `done`.

### D. Sync `## Features` body bullets with `features` frontmatter

Triggered when the user adds or removes a feature mid-sprint, or when a stale body / frontmatter divergence is detected during another operation.

Steps:

1. Read the sprint file. Diff the `features` frontmatter list against the `## Features` body bullets (each bullet is expected to link to `project/features/<slug>.md` and show the feature's current status).
2. **Refuse partial updates.** If the user's request mutates only the body or only the frontmatter, stop and report; the body and the frontmatter list **MUST** be updated in the same operation per `spec/project/sprint/` §Roadmap and feature linkage.
3. Apply the requested addition or removal to both surfaces atomically. When adding a feature mid-sprint, also set the feature file's `sprint` field to this sprint's number (and check that no other sprint already references it). When removing, clear the feature file's `sprint` field (set to null).

### E. Decline transitions outside this skill's scope

The following requests are **out of scope** for this skill:

- `active → review` and any subsequent transition — owned by `sprint-review`.
- Cancelling a sprint at any stage — `sprint-review` writes the cancellation rationale per `spec/project/sprint/` §Hobby-scale variability.
- Mutating `value_statement` on a sprint that's already `active` — refuse and hand back. The field is frozen after activation per `spec/project/sprint/` §Roadmap and feature linkage; the recovery path is `cancelled` plus a fresh sprint, owned by `sprint-review`.
- Mutating `roadmap_items` or `artifact_ref` on a sprint that's already `active` — refuse and hand back. `roadmap_items` may be edited only while `planned` (per `sprint-plan`); `artifact_ref` is `sprint-review`'s authority at closure.

When the user asks for any of the above, stop and surface the correct skill to invoke instead.

## Hard rules

- **Never** allow two sprints to be `active` simultaneously. The at-most-one-active-sprint invariant is non-negotiable per `spec/project/sprint/` §Lifecycle; on conflict, refuse the offending feature transition and surface the conflicting sprint to the user.
- **Never** transition a feature to `in_progress` while its `sprint` field points at a `planned` sprint that can't be promoted right now (because another sprint is still `active`). The feature transition fails and `planned → active` doesn't fire.
- **Never** mutate the `## Features` body bullets without mutating the `features` frontmatter list in the same write, and vice versa. Partial updates are forbidden.
- **Never** mark a feature `done` while any acceptance-criterion checkbox is unchecked or any test-hook status is `pending` or `failing`.
- **Never** write `last_commit` on a sprint as a side effect of anything other than a feature in that sprint reaching `done`. The field's only canonical writer is operation C.
- **Never** transition a sprint past `active` from this skill. `active → review`, `review → closed`, `review → cancelled`, and the cancellation paths from any earlier state are `sprint-review`'s authority.
- **Never** alter `value_statement` on an `active` sprint. If reality has shifted, the sprint must be cancelled and rescheduled per `spec/project/sprint/` §Roadmap and feature linkage.
- When `spec/project/sprint/` or `spec/project/feature/` disagrees with this skill, the spec wins. Propose updating this skill rather than silently diverging.
