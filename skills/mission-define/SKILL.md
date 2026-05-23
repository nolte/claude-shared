---
name: mission-define
description: "Authors a project's first `project/mission.md` per the canonical-language file under spec/project/mission/. Invoke when the user says \"define the mission\", \"write project/mission.md\", \"set up the mission file\", \"draft the SMART mission\", or equivalent German-language requests. Walks SMART one letter at a time (Specific statement, Measurable verifies_via pointer, Achievable MVP scope, Relevant outcome IDs, Time-bound shape), gathers a per-audience MVP-deliverable paragraph, composes the frontmatter plus the four required body sections (Statement, Audiences, Verification, Source), and writes the file with `mvp_status: defining`. Refuses to run when `project/mission.md` already exists (use `mission-revise`) or when `project/goals.md` or the audience artefact is missing. Supports resume on re-invocation per `spec/claude/resumable-work/`."
tags: [scaffolding]
phase: vision
resumable: true
---

# Mission Define

Authors the first-write of `project/mission.md` against `spec/project/mission/<canonical_language>.md` (canonical language: English). The spec is the authority for the on-disk shape; this skill is the interactive front-end that fills it in.

## German trigger phrases

This skill also triggers on equivalent German-language requests, including:

- "Mission definieren"
- "die SMART-Mission formulieren"
- "Mission-Datei aufsetzen"

## Why this is a skill, not an agent

- **Persistent on-disk artefact** — the output is a versioned markdown file consuming skills (`mission-revise`, future audits, the roadmap layer) read for years to come; a skill owns persistent state, an agent returns a structured report and forgets.
- **Mid-flow user gating is the SMART contract** — every letter of SMART is a per-step user dialogue (audience choice, verifying-feature pointer, MVP scope size, outcome list, time-bound shape); the spec forbids batched output, so an agent's fire-and-forget shape would lose the gates.
- **Output flows back into the main conversation** — the audience tailoring paragraphs and the verifying-feature reference must surface in the conversation so the user can iterate before the file is written; isolating them behind an agent's structured-report boundary would obscure the iterative drafting.
- Counter-dimension considered: a narrower agent prompt could sharpen SMART-statement phrasing, but the load-bearing dimension here is interactivity (every SMART letter requires confirmation), not prose specialisation — skill wins.

## User-language policy

Detect the user's language and respond in it. The mission file's `mission_statement` and per-audience paragraphs are written in the project's primary language (follow the precedent of existing artefacts in `project/`, defaulting to English when no precedent exists). Frontmatter keys, enum values, audience identifiers, outcome IDs, and feature-acceptance references stay in their canonical English form regardless of the user's language.

## Preconditions

Before any drafting work:

- Confirm the working directory is the target project root (`git rev-parse --is-inside-work-tree`).
- Confirm `git` is reachable in `PATH`; the `## Source` audit trail in operation 4 captures the audience artefact's last-commit SHA via `git log` and the mission write fails without it.
- Confirm `project/mission.md` does **not** yet exist. If it does, stop and tell the user this skill is first-write only — `mission-revise` owns edits.
- Confirm `project/goals.md` exists and parses (Vision section plus `O-<n>` outcomes per the sibling `roadmap` spec). If absent or empty, stop and ask the user to author goals first; outcomes are an input to mission Relevant, not something this skill invents.
- Confirm the audience artefact exists at the location declared by `audience-identification` (typically `AUDIENCES.md`). If absent, dispatch `audience-identify` first; the spec forbids inventing audiences inline.
- Confirm at least one feature under `project/features/` exists with an `acceptance-<n>` criterion that can serve as the mission-verifying criterion. If none exists, stop and ask the user whether to author the verifying feature first (via `feature-decompose`) or to declare the mission's verifying criterion as a deferred decision and revisit.

## Operations

### 1. Read inputs

Load and parse, in this order:

- `project/goals.md` — extract every `O-<n>` outcome ID and its one-sentence description.
- The audience artefact — extract every audience identifier and its category, interaction surface, and expectation.
- `project/roadmap.md` — list every roadmap item carrying `mvp: true` (or note that `mvp` is unset across the queue, in which case operation 3 will flag the MVP scope as a fresh decision).
- `project/features/` — list every feature file plus its `acceptance-<n>` IDs so the user has a menu when picking the verifying feature.

### 2. Walk SMART one letter at a time

Surface each letter to the user; never batch.

1. **Specific** — propose a single-sentence `mission_statement` that names **what** the project does and **for whom**. The "for whom" **MUST** resolve to one or more entries from the audience artefact's identifier list. Iterate with the user until the sentence is one sentence, no markdown beyond inline punctuation, and the audience identifier is explicit (not "for users").
2. **Measurable** — present the feature menu from operation 1 and ask the user to pick exactly one `<feature-id>:acceptance-<n>` pair. Verify the named feature file exists and the named acceptance ID exists on it. Reject any pair that doesn't resolve.
3. **Achievable** — present the `mvp: true` roadmap items (or, if none yet, walk the roadmap with the user and gather the MVP scope). Verify every selected item carries `detail: fine` and a non-null `target_sprint` per the sibling `roadmap` spec. The MVP count **SHOULD** be roughly two-to-five sprints' worth of capacity; reject an unbounded scope (every roadmap item flagged) with the verbatim error from the spec.
4. **Relevant** — ask which outcome IDs the mission ties to. Reject an empty list and any unresolved entry. Prefer one or two; long lists are a smell.
5. **Time-bound** — offer the two legal shapes: `{ kind: outcome, ref: O-<n> }` or `{ kind: mvp_completion }`. Reject any free-text deadline or calendar date with the spec's verbatim rejection.

### 3. Walk audiences one at a time

For every audience identifier on the `audiences` list, gather a three-to-five-sentence paragraph naming the audience and stating what the MVP delivers to that audience specifically. Group two audiences in a single paragraph only when their MVP-deliverable is genuinely identical and the grouping rationale is stated in the paragraph. A bare audience list without per-audience paragraphs **MUST** be refused.

### 4. Compose the file

Render the mission file with:

- **YAML frontmatter** carrying the eight required fields in the declared order: `mission_statement`, `relevant_outcomes`, `audiences`, `verifies_via`, `time_bound`, `mvp_status`, `created`, `revised_at`. Set `mvp_status: defining`, `created` to today's ISO date, `revised_at: null`.
- **`## Statement`** — repeat the `mission_statement` as prose, immediately followed by a five-line SMART decomposition naming which frontmatter field anchors each letter.
- **`## Audiences`** — one paragraph per audience identifier, in the same order as `audiences`. No paragraph names an audience absent from the frontmatter list, and no frontmatter audience lacks a paragraph.
- **`## Verification`** — short prose pointer to the `verifies_via` feature plus the criterion text repeated verbatim from the feature file so the mission is readable without walking the feature corpus.
- **`## Source`** — the audit trail: the audience artefact path plus its last-commit SHA at write time (`git log -n 1 --format=%H -- <path>`), the consulted `goals.md` path, and "operator: <git config user.name> via mission-define skill, commit-pending".

### 5. Confirm and write

Present the full draft (frontmatter plus body) back to the user in their language and iterate until they approve. Only then write `project/mission.md`. Never write a partial file; either every required field and section is present or the write is deferred.

After writing, remind the user that the next mission-side operation is `mission-revise` (for the `defining → in_progress` flip once the first MVP item enters `status: active`) and that `mvp: true` flags on roadmap items are the authoritative MVP-membership signal — keep them in sync via `roadmap-refine`, never inline-edit them from this skill.

## Gotchas

- The **Time-bound** letter does **not** map to a date even when the user volunteers one. The two legal shapes are outcome-anchored or `mvp_completion`-anchored; reject calendar dates with the spec's verbatim rejection rather than translating them into a fake `mvp_completion`.
- The `verifies_via` field names exactly **one** feature plus exactly **one** `acceptance-<n>` ID. The sibling `feature` spec already enforces "at most one feature per sprint carries a non-null `verifies_sprint_value`"; if the user proposes two verifying features, the mission scope is wrong, not the constraint.
- The audience artefact path is *not* always `AUDIENCES.md` — it's whatever the project's `audience-identification` run picked (README section, dedicated file, or ADR). Read the actual artefact and capture its real path plus last-commit SHA in `## Source`; never hard-code `AUDIENCES.md`.
- An `mvp: true` flag on a roadmap item without `detail: fine` and a non-null `target_sprint` is a roadmap-side lint violation, not something to silently accept here. Surface it back to the user and ask whether to fix the roadmap first via `roadmap-refine`.
- The `## Source` audit trail is part of the spec contract, not optional metadata. A first-write without an audience-artefact SHA, a `goals.md` reference, and an authorship line fails validation downstream.

## Examples

- Read `examples/01-fresh-mission-claude-plugin.md` when writing a first `project/mission.md` for a Claude plugin project.
- Read `examples/02-mission-with-multiple-audiences.md` when the project has multiple distinct audiences that each need a dedicated outcome.
- Read `examples/03-refusal-when-mission-exists.md` when the user triggers `define` but a `project/mission.md` already exists on disk.

## Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/mission-define/<run-id>.yml` after every successful user-approval gate and after each named phase boundary. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope (`schema_version`, `run_id`, `inputs`, `phase`, `decisions[]`, `status`, ...) and the fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

## Hard rules

- **Never** create `project/mission.md` when one already exists. First-write only.
- **Never** invent audience identifiers, outcome IDs, or feature-acceptance pairs. Every reference **MUST** resolve to an existing artefact at write time.
- **Never** accept a calendar date or free-text deadline in `time_bound`. The spec's two legal shapes are the only legal shapes.
- **Never** accept an MVP scope that flags every roadmap item with `mvp: true`. The Achievable bound exists for a reason.
- **Never** set `mvp_status` to anything other than `defining` on first-write. Lifecycle transitions are `mission-revise`'s job.
- **Never** name an audience in `## Audiences` that's absent from the `audiences` frontmatter, or vice versa. The two surfaces are bidirectionally validated.
- **Never** batch the SMART walk or the audience walk. Per-step user confirmation is the contract.
- **Never** copy an existing mission file from another repository. Each project's mission is its own.
- When `spec/project/mission/` disagrees with this skill, the spec wins. Propose updating this skill rather than silently diverging.
