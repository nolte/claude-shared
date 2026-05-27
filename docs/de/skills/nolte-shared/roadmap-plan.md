---
title: roadmap-plan
audience: [maintainer]
content_mode: reference
track: developer-docs
last_updated: generated
---

# roadmap-plan

> Fügt Roadmap-Items hinzu, retargetet sie und passt sie an in project/roadmap.md mit vollständiger Lifecycle-Validierung.

_Adds, retargets, and reshapes roadmap items in `project/roadmap.md` per `spec/project/roadmap/` and `spec/project/mission/`. Invoke when the user asks to \"add a roadmap item\", \"queue work for sprint N\", \"promote roadmap item to fine\", \"retarget R-3 to sprint 9\", \"flip MVP on this item\", or equivalent German-language requests. Validates outcome IDs against `goals.md`, validates `target_sprint` against `project/sprints/`, enforces the lifecycle transitions declared in the roadmap and mission specs (including the asymmetric MVP-flag rule: `false→true` allowed before stabilisation, `true→false` forbidden after the item entered `status: active`), and refuses partial writes that would leave inconsistencies. Don't use to scaffold the roadmap from scratch (use [`roadmap-init`](roadmap-init.md)) or to enforce the detail-level invariant (use [`roadmap-refine`](roadmap-refine.md)). Supports resume on re-invocation per `spec/claude/resumable-work/`._

- **Plugin:** `nolte-shared`
- **Phase:** 2 Plan (`plan`)
- **Tags:** `planning`
- **Quelle:** [skills/roadmap-plan/SKILL.md](https://github.com/nolte/claude-shared/blob/main/skills/roadmap-plan/SKILL.md)

## Anwenden wenn

- you want to add a roadmap item or queue work for sprint N
- you want to retarget an existing roadmap item to another sprint
- you want to flip the MVP flag on a roadmap item

## Nicht anwenden wenn

- **project/roadmap.md does not exist yet** → [`roadmap-init`](roadmap-init.md)
- **You want to enforce the queue-wide detail-level invariant** → [`roadmap-refine`](roadmap-refine.md)

## Siehe auch

- [`roadmap-init`](roadmap-init.md)
- [`roadmap-refine`](roadmap-refine.md)
- [`feature-decompose`](feature-decompose.md)
- [`sprint-plan`](sprint-plan.md)

---

## Roadmap Plan

Mutates the queue in `project/roadmap.md` per `spec/project/roadmap/<canonical_language>.md` and the cross-cutting MVP semantics declared by `spec/project/mission/<canonical_language>.md`. Owns adds, detail promotions, sprint retargets, MVP flips, and lifecycle transitions on existing items. The detail-level invariant is checked here on every write; the wider per-queue audit belongs to [`roadmap-refine`](roadmap-refine.md).

### Why this is a skill, not an agent

- **Mid-flow interactivity is the contract** — every mutation (new item draft, sprint retarget, MVP flip) needs explicit confirmation before it hits disk; an agent's structured-report shape would lose the per-edit gate.
- **Output flows back into the main conversation** — drafted items, validated cross-references, and lifecycle warnings all need to be readable in the working context so the user can iterate before confirming.
- **Orchestrator role** — when this skill discovers that the audience artefact or the goals file is missing, it dispatches [`audience-identify`](audience-identify.md) or [`roadmap-init`](roadmap-init.md) and resumes; when fixes spread across the queue, it cooperates with [`roadmap-refine`](roadmap-refine.md). The orchestrator stays in skill form per `skill-vs-agent`.
- Counter-dimension considered: a narrow agent could sharpen the cross-reference validation pass (resolve every `O-<n>` and every `target_sprint` in one shot), but the load-bearing dimension is the per-mutation user dialogue, not the validator's output specialisation — skill wins.

### User-language policy

Detect the user's language and respond in it. Item titles, bodies, and any prose written into `project/roadmap.md` use the project's primary language (the same language already used in `goals.md` and `roadmap.md`).

### Preconditions

Before any mutation:

- `project/roadmap.md` and `project/goals.md` exist. When either is missing, stop and direct the user to [`roadmap-init`](roadmap-init.md).
- The roadmap parses end-to-end; a partially-parsed file is rejected because partial writes risk corrupting items the parser couldn't reach.
- `project/sprints/` is reachable when the requested mutation cites a `target_sprint`; otherwise the cross-reference can't be validated and the mutation is refused.
- `project/mission.md` may or may not exist. When it exists, every roadmap item carries the `mvp` field; when it does not, items **MAY** carry `mvp: false` uniformly or omit the field entirely. This skill respects whichever shape the file already uses and refuses to mix the two on a single write.

### Operations

#### 1. `add` — append a new roadmap item

1. Collect from the user:
   - **Title** — one line in the project's primary language.
   - **Outcomes** — at least one `O-<n>` from `goals.md`. When the user names an outcome that does not yet exist, refuse and direct them to add it via the goals workflow first; do not invent outcomes inline.
   - **Detail** — `fine`, `coarse`, or `backlog`. When the user requests `fine` and supplies no `target_sprint`, ask whether the item is genuinely near-term enough to justify the body depth.
   - **`target_sprint`** — integer sprint number or null. Resolve against `project/sprints/`; a number that does not match a sprint file is refused. A number pointing at a `closed` or `cancelled` sprint is refused (the spec rejects items whose `target_sprint` points at a terminal sprint as a lint violation).
   - **`mvp`** — boolean, only when `project/mission.md` exists. Default to `false` and ask the user to confirm before flipping to `true`; `mvp: true` carries the achievability bound from the mission spec.
   - **`status`** — defaults to `proposed`. Direct creation as `active` or `done` is refused; lifecycle transitions are owned by step 4.
2. Assign a fresh `id` of shape `R-<n>` where `<n>` is monotonic and never reused — including past IDs that have since been deleted.
3. Draft the body to the depth required by `detail`:
   - `fine` — paragraph stating the user-visible change plus a feature checklist (titles only; actual feature schema lives in `spec/project/feature/`).
   - `coarse` — one or two sentences describing the intent.
   - `backlog` — a single sentence.
4. **Validate the detail-level invariant** before writing: when the new item's `target_sprint` resolves to the current or next sprint (per the resolution rule in `spec/project/roadmap/` §Detail-level convention and refinement rule), `detail` **MUST** be `fine`. Refuse otherwise.
5. Show the drafted item to the user and iterate until approved. Only then append it to `project/roadmap.md` in the appropriate phase section (or at the end when the file is flat).

#### 2. `promote` — move `coarse` or `backlog` to `fine`

1. Locate the item by `id`.
2. Refuse the promotion when `status` is `cancelled` (cancelled items are archival per the lifecycle).
3. Draft the missing body shape: paragraph plus feature checklist.
4. Show the diff and confirm with the user.
5. Write the change in one operation; refuse partial writes that would leave a `fine` YAML field paired with a `coarse`-shaped body.

#### 3. `retarget` — change `target_sprint`

1. Locate the item by `id`.
2. Resolve the new `target_sprint` against `project/sprints/`. Reject:
   - non-existent sprint numbers;
   - sprint numbers whose file shows `status: closed` or `status: cancelled`;
   - retargets that move a `mvp: true` item off a sprint while leaving `detail: fine` intact when no successor sprint is in the current/next window — surface this and ask the user whether to also demote detail.
3. **Re-check the detail-level invariant** after the retarget. When the new `target_sprint` resolves to the current or next sprint and `detail` is not `fine`, refuse the retarget; route through `promote` first.
4. Special case `null` retarget: setting `target_sprint: null` is always allowed (the item drops back to unscheduled). The spec explicitly names `null` as a valid post-closure state.
5. Show the diff and confirm with the user.

#### 4. `transition` — advance `status`

The roadmap spec permits exactly these transitions:

- `proposed → active`
- `active → done`
- `proposed → cancelled`
- `active → cancelled`

Every other transition (in particular `proposed → done` and any path back from `cancelled`) is refused.

Additional gates:

- `active → done` requires that every feature this item spawned (under `project/features/`) is itself `done`, and that the corresponding sprint has reached `closed` (specifically `closed`, not `cancelled`). When a sprint reaches `cancelled` with features attached, the item remains `active` until the pending features are re-targeted to a successor sprint that itself reaches `closed`. This skill checks the sprint state via `project/sprints/`; when the gate fails, refuse the transition with a verbatim error citing the spec.
- `proposed → active` is normally driven by [`sprint-execute`](sprint-execute.md) when a feature on the item enters `in_progress`; this skill performs the transition only when explicitly requested by the user and only when no sprint-side state would be left inconsistent.

#### 5. `mvp-flip` — change the `mvp` boolean

The mission spec governs the asymmetry:

- `false → true` is allowed at any time **before** the project's `mvp_status` reaches `stabilised`. Once stabilised, `false → true` is refused with a verbatim error.
- `true → false` is allowed **only while the item's `status` is still `proposed`**. Once the item enters `status: active`, the flip from `true` to `false` is forbidden because removing it from MVP scope retroactively breaks the achievability bound the SMART contract relies on.

Read `project/mission.md` to resolve `mvp_status` when the file exists; when it does not exist, the asymmetric rule is dormant and the flag's only constraint is the on-disk consistency declared by the roadmap spec. Show the user which rule the skill applied to their flip and confirm before writing.

#### 6. Validate every write end-to-end

After any mutation, before the file is written:

- Every item's `outcomes` list resolves: each `O-<n>` exists in `goals.md`. Empty `outcomes` lists are refused.
- Every non-null `target_sprint` resolves to a sprint file under `project/sprints/`, and the sprint is not in a terminal status that would make the reference a lint violation.
- Every item with `target_sprint` equal to the current or next sprint carries `detail: fine`.
- Every YAML block carries the seven required keys in the declared order (`id`, `title`, `detail`, `outcomes`, `target_sprint`, `mvp`, `status`); when `project/mission.md` does not exist, omitting `mvp` uniformly is also acceptable as long as the file is consistent.
- Every `id` is unique within the file and follows the `R-<n>` shape.

When any check fails, **refuse the write entirely**. Do not produce partial output. Show the failing check and let the user choose to fix the input or abort.

### Gotchas

- **The MVP-flag rule is asymmetric.** `mvp: false → true` is allowed before stabilisation; `mvp: true → false` is forbidden after the item entered `status: active` (per `spec/project/mission/`). The skill enforces both directions, but the operator routinely confuses the two — flag flips on already-active MVP items get refused with a verbatim error citing the spec section.
- **`R-<n>` IDs are monotonic across the project's lifetime, never reused** even after deletion. The skill reads the highest existing ID under the roadmap plus the highest deleted ID from `git log -- project/roadmap.md` before assigning. Reusing a retired ID would silently bind two different features to the same ID across the project's history.
- **`target_sprint` pointing at a `closed` or `cancelled` sprint isn't this skill's violation** — that's a separate lint owned by [`roadmap-refine`](roadmap-refine.md). The skill surfaces the situation as an informational note and refuses to retarget directly; the operator either accepts the note or runs [`roadmap-refine`](roadmap-refine.md) for the cross-queue fix.
- **Mission file presence changes the schema.** When `project/mission.md` exists, every roadmap item carries an `mvp: bool` field; when the mission file is absent, the field is silently dropped. Authoring a roadmap item in a mission-less project and later adding the mission flips every item to require a default `mvp: false` — this skill won't backfill silently; the operator runs a follow-up pass with [`mission-define`](mission-define.md) first.
- **`outcomes` resolution against `goals.md` is strict.** An outcome ID that doesn't exist in `goals.md` blocks the write; there's no "warn-and-continue" mode. When the operator wants a placeholder outcome, they must add the outcome to `goals.md` first via the goals-authoring path; this skill doesn't author outcomes.

### Examples

- Read `examples/01-add-item-target-sprint.md` when adding a new roadmap item and targeting it to a specific sprint.
- Read `examples/02-flip-mvp-flag-asymmetric.md` when flipping the `mvp` flag on an item and you need to see the asymmetry rules in action.
- Read `examples/03-retarget-and-promote-detail.md` when retargeting an item to a different sprint and promoting it from `coarse` to `fine` detail.

### Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/roadmap-plan/<run-id>.yml` after every successful user-approval gate and after each named phase boundary. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope (`schema_version`, `run_id`, `inputs`, `phase`, `decisions[]`, `status`, ...) and the fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

### Hard rules

- **Never** invent outcomes, audience entries, or sprint numbers inline. Missing outcomes route to the goals workflow; missing audiences route to [`audience-identify`](audience-identify.md); non-existent sprint numbers are refused.
- **Never** assign an `R-<n>` ID that has already existed in the file's history (even if currently deleted). IDs are monotonic and never reused.
- **Never** allow `proposed → done` or any transition back from `cancelled`. Direct `proposed → done` is forbidden because every done item must have been actively worked on.
- **Never** flip `mvp: true → false` after the item entered `status: active`. The asymmetry is mandated by `spec/project/mission/`.
- **Never** flip `mvp: false → true` after `mvp_status` reached `stabilised`. Surface a verbatim error citing the mission spec.
- **Never** retarget an item to a `closed` or `cancelled` sprint. The valid post-terminal values are `null` or a `planned` sprint number.
- **Never** leave a `fine`-flagged YAML field paired with a body that lacks the required paragraph plus feature checklist. The two surfaces are written in the same operation.
- **Never** allow partial writes when end-to-end validation fails. Refuse the whole mutation and report the failing check.
- **Never** mix shapes on a single write: when `project/mission.md` exists, every item carries `mvp`; when it does not, the file uses a uniform stance (all items omit, or all items carry `mvp: false`). Do not introduce `mvp` on a subset.
- When `spec/project/roadmap/` (or, for the MVP semantics, `spec/project/mission/`) disagrees with this skill, the spec wins. Propose updating this skill rather than silently diverging.

### Multi-model testing

Examples and operations in this skill are verified on Claude Sonnet 4.6 as the default model; spot-checked on Haiku 4.5 for cost-sensitive runs; Opus 4.7 is appropriate for high-stakes audits that require deeper reasoning. The skill body has no model-specific assumptions beyond standard tool-call semantics.
