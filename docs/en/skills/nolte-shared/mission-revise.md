---
title: mission-revise
audience: [maintainer]
content_mode: reference
track: developer-docs
last_updated: generated
---

# mission-revise

_Revises an existing `project/mission.md` per the canonical-language file under spec/project/mission/. Invoke when the user says \"revise the mission\", \"update project/mission.md\", \"flip mvp_status\", \"the MVP is achieved\", \"the stabilisation gate is satisfied\", or equivalent German-language requests. Supports three operations: (A) revise statement, audiences, verifying-feature pointer, or time_bound; (B) flip `mvp_status` along the legal lifecycle (`defining→in_progress→achieved→stabilised`, plus regression path); (C) revise after stabilisation with the mandatory rationale. Verifies the stabilisation-gate conditions by reading `project/roadmap.md` and `project/sprints/` before allowing a flip to `stabilised`. Supports resume on re-invocation per `spec/claude/resumable-work/`._

- **Plugin:** `nolte-shared`
- **Phase:** 1 Vision (`vision`)
- **Tags:** `scaffolding`
- **Source:** [skills/mission-revise/SKILL.md](https://github.com/nolte/claude-shared/blob/main/skills/mission-revise/SKILL.md)

---

## Mission Revise

Edits an existing `project/mission.md` against `spec/project/mission/<canonical_language>.md` (canonical language: English). The spec is the authority for legal lifecycle transitions and the stabilisation gate; this skill enforces them mechanically and writes the resulting diff with explicit user confirmation.

### German trigger phrases

This skill also triggers on equivalent German-language requests, including:

- "Mission überarbeiten"
- "mvp_status umstellen"
- "die Mission ist stabilisiert"

### Why this is a skill, not an agent

- **Persistent on-disk artefact** — every revision mutates a versioned markdown file consuming skills (`mission-define` for first-write, future audits, the roadmap's `mvp` semantics) read; an agent would lose the persistent-state contract.
- **Per-step user gating drives the lifecycle** — `mvp_status` flips are explicit operator decisions per the spec, never silently inferred from satisfying the conditions; the spec mandates that the operator confirm the flip after the skill has shown the satisfied conditions, so an agent's structured-report shape can't carry the gate.
- **Output flows back into the main conversation** — the stabilisation-gate verification (which roadmap items are still open, which sprint closed last, whether a subsequent sprint has held) is itself useful conversational context; isolating it behind an agent boundary would obscure the operator decision the skill exists to support.
- Counter-dimension considered: a narrow agent could specialise on parsing roadmap and sprint frontmatter for the gate check and gain on context-window protection, but the load-bearing dimension is the per-step approval dialogue around each mutation, not parser sharpness — skill wins.

### User-language policy

Detect the user's language and respond in it. Mission-file content (`mission_statement`, audience paragraphs, prose) stays in the project's primary language (follow the existing file's precedent). Frontmatter keys, enum values, audience identifiers, outcome IDs, and feature-acceptance references stay in their canonical English form. The rationale paragraph required after stabilisation **MUST** be written in the same language as the rest of `## Source`.

### Preconditions

Before any revision:

- Confirm the working directory is the target project root (`git rev-parse --is-inside-work-tree`).
- Confirm `project/mission.md` exists and parses (eight required frontmatter fields plus the four required body sections in the declared order). If absent, stop and dispatch `mission-define`. If malformed, stop and ask the user whether to repair the file by hand before revising.
- Confirm the audience artefact and `project/goals.md` are still reachable, since revisions to `audiences` or `relevant_outcomes` resolve against them.
- Read `project/roadmap.md` and the contents of `project/sprints/` so operations 2 and 3 can verify cross-spec invariants (`mvp: true` item statuses, sprint lifecycle, mission-closing sprint, subsequent-sprint condition).

### Operations

Ask the user which operation they intend; offer the three branches below.

#### A. Revise the statement, audiences, verification, or time_bound

Walk through the field(s) the user wants to change, one at a time:

- **`mission_statement`** — re-walk Specific (statement names what + for whom; "for whom" resolves to current `audiences`). Reject changes that lose the audience identifier.
- **`audiences`** — for every added audience, gather a per-audience paragraph (three-to-five sentences naming the audience and what the MVP delivers to that audience specifically). For every removed audience, also remove its paragraph from `## Audiences`. Reject any change that leaves the two surfaces out of sync.
- **`verifies_via`** — verify the new `<feature-id>:acceptance-<n>` resolves to an existing feature file and an existing acceptance ID; update `## Verification` so the criterion text is repeated verbatim from the new feature file.
- **`relevant_outcomes`** — every entry **MUST** resolve to an `O-<n>` in `goals.md`; reject empty lists and unresolved entries.
- **`time_bound`** — only the two legal shapes are allowed (`{ kind: outcome, ref: O-<n> }` or `{ kind: mvp_completion }`). Reject calendar dates and free-text deadlines.

After every accepted change: update `revised_at` to today's ISO date; never edit `created`. If `mvp_status` is currently `stabilised`, route the operation through branch C below before writing.

#### B. Flip `mvp_status`

Legal transitions, per the spec:

| From | To | Trigger |
|---|---|---|
| `defining` | `in_progress` | At least one `mvp: true` roadmap item has reached `status: active` or `done`. |
| `in_progress` | `achieved` | Every `mvp: true` roadmap item is `status: done` **and** the `verifies_via` acceptance criterion is checked on its feature. |
| `achieved` | `stabilised` | The full §Stabilisation gate conditions are satisfied (see verification below). |
| `stabilised` | `in_progress` | An MVP item has re-opened to `status: active` (regression). |

Any other transition (for example `defining → achieved`, `achieved → defining`, `stabilised → defining`) **MUST** be refused with the spec's rejection clause.

For each requested flip:

1. **Verify the trigger conditions** by reading the artefacts named above. Show the user the evidence inline (which roadmap items, which sprints, which acceptance criterion) so the decision is auditable.
2. **For `achieved → stabilised` only, run the stabilisation-gate verification:**
   - **Every `mvp: true` roadmap item is `status: done`** — parse each item's YAML block in `project/roadmap.md` and confirm `status: done`. Any other status blocks the flip with a verbatim error citing the failing item ID.
   - **The MVP-closing sprint is `status: closed`** — the MVP-closing sprint is the sprint whose closure moved the last `mvp: true` roadmap item to `status: done` (identify it via the roadmap items' `target_sprint` history or, if ambiguous, ask the user to confirm). Read its file under `project/sprints/<NNNN>-<slug>.md` and verify `status: closed`. `cancelled` is not equivalent to `closed` for this condition.
   - **One full subsequent sprint has reached `closed` without regression** — find the sprint whose `number` is `MVP-closing-sprint-number + 1`. Verify its `status` is `closed` (or `cancelled` only when the `## Review notes` rationale states the cancellation was "no-fault-of-MVP"). Confirm no MVP item flipped back to `status: active` during this subsequent sprint. If no subsequent sprint has yet closed, block the flip and report that the gate isn't yet satisfied — never silently infer satisfaction.
   - **No defect-fix work is currently `status: in_progress` against an MVP item** — read every feature under `project/features/` whose `roadmap_item` references an `mvp: true` item and confirm none is in `status: in_progress` per the sibling `feature` spec. Open defect-fix work blocks the flip.
3. **Require the operator's explicit confirmation** for the flip itself. The conditions justify the decision; they never make it. Refuse to proceed without an explicit user "yes".
4. **For `stabilised → in_progress` (regression)** — record which MVP item re-opened and on what date in `## Source` so the audit trail is unbroken. Post-MVP items already in `status: active` at the moment of the revert **MAY** finish per the spec; don't touch them. Surface to the user that no new post-MVP item may start until stabilisation is restored.
5. After the flip is confirmed: update `mvp_status`, update `revised_at` to today's ISO date, and append a one-line entry to `## Source` (date, transition, evidence summary).

#### C. Revise after `mvp_status: stabilised` (rationale-required path)

When the current `mvp_status` is `stabilised` and operation A or B mutates the statement, audiences, verification, or time_bound, the spec **mandates** a one-paragraph rationale in `## Source` because the change redefines what the stabilised MVP was for.

- Block the write until the user supplies the rationale paragraph.
- Append the paragraph to `## Source` with today's ISO date and a short heading like `### Revision rationale (<date>)`.
- Never auto-generate the rationale text; it's an operator statement, not skill output.

A bare `mvp_status: stabilised → in_progress` regression flip from operation B does not by itself trigger this branch (the regression is recorded in `## Source` per branch B step 4 above); branch C applies when the *content* of the mission is being mutated while `mvp_status` is `stabilised`.

#### Final write

For every operation: present the diff (frontmatter delta plus body delta) back to the user, iterate until approval, then write `project/mission.md` in place. Never write a partial file; either every spec invariant holds or the write is deferred.

### Gotchas

- The "one full subsequent sprint" check looks for the sprint whose `number` is `MVP-closing-sprint-number + 1`, **not** simply the most recently closed sprint. If sprints have been opened out of order, walk by `number`, not by `ended` date.
- A `cancelled` subsequent sprint **only** counts toward stabilisation when its `## Review notes` rationale states the cancellation was unrelated to MVP work. Read the rationale; never assume.
- The MVP-closing sprint is identified by which sprint moved the **last** `mvp: true` roadmap item to `status: done` — not the sprint with the largest count of MVP items. When the closure is split across sprints, the one carrying the final transition is the gate-relevant one.
- A regression flip (`stabilised → in_progress`) does **not** automatically halt post-MVP roadmap items already in `status: active` — the spec lets in-flight work finish. The skill only blocks **new** post-MVP starts via the audit trail; never edit roadmap-item status from this skill.
- Branch C's rationale paragraph is required even for tiny revisions (a typo fix in the statement) once `mvp_status: stabilised` — the spec is intentionally strict because every post-stabilisation revision redefines what stabilisation meant.

### Examples

- Read `examples/01-revise-statement.md` when revising the mission statement wording while keeping the lifecycle status unchanged.
- Read `examples/02-flip-mvp-status-to-achieved.md` when flipping `mvp_status` from `in_progress` to `achieved` after all MVP items land.
- Read `examples/03-stabilisation-gate-blocks.md` when the stabilisation gate blocks a post-MVP revision and you need to see how to handle the refusal.

### Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/mission-revise/<run-id>.yml` after every successful user-approval gate and after each named phase boundary. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope (`schema_version`, `run_id`, `inputs`, `phase`, `decisions[]`, `status`, ...) and the fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

### Hard rules

- **Never** create `project/mission.md` from scratch. This skill is edit-only; first-write is `mission-define`'s job.
- **Never** infer a `mvp_status` flip silently from satisfied conditions. The flip is always an explicit operator decision.
- **Never** allow an illegal lifecycle transition (anything outside `defining → in_progress → achieved → stabilised` plus the regression path `stabilised → in_progress`).
- **Never** flip to `stabilised` before every gate condition is verified against the actual artefacts. Cite the evidence inline; never accept the user's word as a substitute for the check.
- **Never** edit `created`. The field is set once on first-write and frozen.
- **Never** auto-generate the post-stabilisation rationale paragraph. The operator writes it.
- **Never** name an audience in `## Audiences` that's absent from `audiences`, or vice versa. The two surfaces are bidirectionally validated after every revision.
- **Never** invent audience identifiers, outcome IDs, or feature-acceptance pairs in a revision. Every reference **MUST** resolve to an existing artefact at write time.
- **Never** allow a post-MVP roadmap item (`mvp: false`) to start while `mvp_status` is `defining`, `in_progress`, or `achieved`; surface this as a violation when the user reports it but never alter the roadmap from this skill — `roadmap-refine` is the canonical write authority for that surface.
- When `spec/project/mission/` disagrees with this skill, the spec wins. Propose updating this skill rather than silently diverging.
