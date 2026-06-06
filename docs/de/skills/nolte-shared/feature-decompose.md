---
title: feature-decompose
audience: [maintainer]
content_mode: reference
track: developer-docs
last_updated: generated
---

# feature-decompose

> Zerlegt einen Roadmap-Eintrag in Feature-Dateien mit testbaren Akzeptanzkriterien und Test-Hooks.

_Decompose a roadmap item into feature files under project/features/ per spec/project/feature/. Invoke when the user asks to decompose a roadmap item, break down a roadmap entry into features, draft features, scaffold a feature file, plan features for the next sprint, or write a new feature. Also handles equivalent German-language requests. Walks the operator through title, description, 3-7 testable acceptance criteria, and test hooks per feature; identifies which carries `verifies_sprint_value`; dispatches [`feature-consistency-reviewer`](../../agents/nolte-shared/feature-consistency-reviewer.md) (or records a manual fallback) before allowing the feature to leave `draft`. Don't use to transition feature status (`ready → in_progress` / `in_progress → done` is [`sprint-execute`](sprint-execute.md) / [`sprint-review`](sprint-review.md)) or to author roadmap items, sprints, or the mission file. Supports resume on re-invocation per `spec/claude/resumable-work/`._

- **Plugin:** `nolte-shared`
- **Phase:** 2 Plan (`plan`)
- **Tags:** `scaffolding`
- **Quelle:** [skills/feature-decompose/SKILL.md](https://github.com/nolte/claude-shared/blob/main/skills/feature-decompose/SKILL.md)

## Anwenden wenn

- you want to break a roadmap entry into feature files
- you want to scaffold features for the next sprint
- you want to draft a new feature against the feature spec

## Nicht anwenden wenn

- **You want to transition a feature's status (ready → in_progress)** → [`sprint-execute`](sprint-execute.md)
- **You want to mark a feature done at sprint review** → [`sprint-review`](sprint-review.md)
- **You want to author or retarget roadmap items themselves** → [`roadmap-plan`](roadmap-plan.md)

## Siehe auch

- [`roadmap-plan`](roadmap-plan.md)
- [`sprint-plan`](sprint-plan.md)
- [`sprint-execute`](sprint-execute.md)
- [`feature-consistency-reviewer`](../../agents/nolte-shared/feature-consistency-reviewer.md)

---

## Feature Decompose

Decomposes one roadmap item into one or more feature files at `project/features/<slug>.md` per `spec/project/feature/<canonical_language>.md`. This skill is the only authoring surface in the feature lifecycle that creates feature files; later status transitions belong to [`sprint-execute`](sprint-execute.md) and [`sprint-review`](sprint-review.md).

### Why this is a skill, not an agent

- **Mid-flow agent dispatch is the contract** — the spec mandates a consistency check via the [`feature-consistency-reviewer`](../../agents/nolte-shared/feature-consistency-reviewer.md) agent before `draft → ready`; the orchestrator that dispatches an agent is always a skill per `spec/claude/skill-vs-agent/` §Hybrid pattern.
- **Per-feature operator approval** — title, description, acceptance criteria, test hooks, and the `verifies_sprint_value` choice each require user confirmation; an agent's structured-report shape can't carry those checkpoints.
- **Persistent on-disk artefact under iterative drafting** — feature files live next to the roadmap and sprint corpus and are mutated again later by other skills; the iterative drafting (consistency findings → resolutions → final write) flows back into the main conversation naturally.
- Counter-dimension considered: a narrower agent prompt could sharpen acceptance-criterion phrasing, but the load-bearing dimensions here are mid-flow agent dispatch and per-step operator approval — skill wins.

### User-language policy

Detect the user's language and respond in it. Feature files themselves (frontmatter, body sections, identifiers) are written in the **project's primary language** as declared by the consuming repo's root convention file (typically `CLAUDE.md`); when no primary language is declared, English is the default. Frontmatter field names, identifiers (`F-<n>`, `R-<n>`, `acceptance-<n>`), and the closed-vocabulary status tokens (`pending`, `passing`, `skipped`, `failing`) stay English regardless of prose language.

### Preconditions

Before any write, confirm:

- The current repository carries `spec/project/feature/<canonical_language>.md`. If absent, stop — the spec is the input to this skill, not optional.
- `project/roadmap.md` exists and the target `roadmap_item` (passed by the user as `R-<n>`) is present in it; resolve its `outcomes`, `detail`, `target_sprint`, and `mvp` fields so they can be quoted into per-feature context.
- `project/goals.md` exists and the roadmap item's `outcomes` list resolves; if not, stop and surface the broken outcome reference rather than guessing.
- An audience artefact exists when the project carries `project/mission.md`; missing audiences block feature authoring the same way they block outcome and mission authoring (per `spec/project/roadmap/` and `spec/project/mission/`). Dispatch [`audience-identify`](audience-identify.md) first if needed.
- The [`feature-consistency-reviewer`](../../agents/nolte-shared/feature-consistency-reviewer.md) agent is reachable in the current plugin runtime, **or** the operator explicitly acknowledges the manual-fallback path and provides a manual-pass identifier of the form `manual-<YYYY-MM-DD>` (per `spec/project/feature/` §Consistency check). The fallback is permitted only until the agent ships; once the agent is reachable, refuse to fall back.
- The next free `F-<n>` ID is determinable by reading the highest existing ID under `project/features/`; never reuse a retired ID.

### Operations

#### 1. Decompose

The decomposition produces N ≥ 1 features for the given roadmap item; the
operator decides N.

1. **Restate the roadmap item.** Read its YAML block from
   `project/roadmap.md` and replay its `title`, `outcomes`, `detail`,
   `target_sprint`, and `mvp` flag back to the operator. If `detail` is
   `coarse` or `backlog` and the item is targeted at the current or next
   sprint, stop and recommend running [`roadmap-refine`](roadmap-refine.md) first — decomposing a
   non-`fine` item violates the roadmap spec.
2. **Propose a feature split.** Suggest one to four feature titles based on
   the roadmap item's body checklist (when present) or its prose. The
   operator confirms the split, adds, removes, or renames before any file is
   written.
3. **For each feature, gather:**
   - **Title** — one-line summary in the project's primary language.
   - **Slug** — ASCII kebab-case, ≤ 6 words, derived from the title; confirm
     with the operator and verify the path `project/features/<slug>.md` is
     free.
   - **Description** — one to three paragraphs phrased from the end-user
     perspective; ask follow-ups until the description is concrete enough
     that a reader unfamiliar with the roadmap can grasp the change.
   - **Acceptance criteria** — three to seven testable bullets, atomic and
     user-visible (no workflow gates such as "PR merged"). Each bullet uses
     the pattern `- [ ] **acceptance-<n>** <criterion>`. One is suspicious;
     more than ten suggests splitting the feature.
   - **Test hooks** — one entry per acceptance criterion, in the format
     `- **acceptance-<n>** — <mechanism> — <status>`, where `<mechanism>`
     names a test path, skill name, CLI command, or manual procedure, and
     `<status>` is one token from the closed vocabulary `pending` (default
     at decomposition), `passing`, `skipped`, `failing`.
4. **Identify the value-verifier.** Across the N features, ask the operator
   whether one feature carries `verifies_sprint_value`. The field is
   non-null on **at most one** feature per sprint (per
   `spec/project/feature/` §Frontmatter schema). When this decomposition
   produces the feature that closes the MVP per `spec/project/mission/`,
   that feature **MUST** carry `verifies_sprint_value: acceptance-<n>`
   naming the criterion that proves the sprint's `value_statement`. When
   the operator is unsure, leave all features with
   `verifies_sprint_value: null` — [`sprint-plan`](sprint-plan.md) may reassign it later.
5. **Run the consistency check** (mandatory; see Operation 2). Block the
   write until the check completes and every `overlap` or `duplication`
   finding is resolved.
6. **Write the feature file(s).** For each feature, render the frontmatter
   with the nine fields in the declared order (`id`, `title`,
   `status: draft`, `roadmap_item`, `sprint: null`, `created`,
   `ended: null`, `verifies_sprint_value`, `consistency_check`) and the
   five required level-2 sections in the declared order (`## Description`,
   `## Acceptance criteria`, `## Test hooks`, `## Consistency notes`,
   `## Risks`). Optional sections (`## Open questions`, `## References`)
   MAY follow the required five.
7. **Confirm paths back to the operator** in their language and remind
   them that `draft → ready`, `ready → in_progress`, and
   `in_progress → done` are owned by [`sprint-plan`](sprint-plan.md), [`sprint-execute`](sprint-execute.md), and
   [`sprint-review`](sprint-review.md) respectively — not by this skill.

#### 2. Run the consistency check

Mandatory before the feature file is written with `status: draft` AND a
populated `consistency_check` frontmatter object. The check is what allows a
downstream skill to later transition `draft → ready`; without it, the
feature is malformed.

1. **Dispatch the [`feature-consistency-reviewer`](../../agents/nolte-shared/feature-consistency-reviewer.md) agent** with the draft
   frontmatter and body assembled in step 3 of Operation 1, the resolved
   `roadmap_item`, the slug, and a short git revision identifier
   (`git rev-parse --short HEAD` from the dispatching skill — the agent
   has no shell access by design and can't compute this itself). The
   agent reviews the existing feature corpus under `project/features/`,
   the project's primary source roots, and the spec corpus under `spec/`,
   and returns a `findings` array. Confirm the working tree is a git
   repository (`git rev-parse --is-inside-work-tree`) before invoking
   the agent — that precondition has moved from the agent to here when
   the agent's `tools` list dropped `Bash`.
2. **Manual fallback (deprecated, transitional only).** The
   [`feature-consistency-reviewer`](../../agents/nolte-shared/feature-consistency-reviewer.md) agent ships with this skill — under
   normal conditions the dispatch in step 1 succeeds and the fallback
   isn't reached. The fallback exists exclusively for repos whose
   plugin runtime predates the agent's availability: when step 1 can't
   resolve the agent at all, walk the same investigation surface
   yourself — read every existing feature's frontmatter and
   `## Description`, scan the project's primary source roots for
   already-implemented behaviour, and grep `spec/` for prior decisions
   that constrain the new feature. Capture findings in the same shape
   the agent would emit. Acceptance of this path **MUST** be explicit:
   ask the operator before proceeding, and surface the runtime version
   gap so they know the right long-term fix is upgrading the plugin
   runtime, not normalising the manual pass.
3. **Persist findings on the feature** in two places:
   - **Frontmatter** — populate the `consistency_check` object with
     `performed_at: <ISO date>`, `agent_version: <agent-id>` (or
     `manual-<YYYY-MM-DD>` for the fallback), and a non-empty `findings`
     list. Each finding carries `kind` (`overlap`, `duplication`, `drift`,
     `prior-art`, or `clean`), `target` (file path or feature ID), and
     `resolution` (`merge-into <id>`, `supersede <id>`,
     `split-out <ids>`, `proceed`, or `revisit-after <event>`). A clean
     run still records exactly one finding with `kind: clean` so the array
     is never empty.
   - **Body** — populate `## Consistency notes` with one paragraph per
     finding restating the finding in human-readable prose plus the chosen
     resolution.
4. **Block the write** when any finding has `kind: overlap` or
   `kind: duplication` and its `resolution` is `proceed` without an
   explicit one-paragraph rationale in `## Consistency notes`. Surface the
   offending finding to the operator and ask for a non-`proceed`
   resolution or a written rationale before continuing. A
   `merge-into <id>` resolution is a first-class outcome and may end the
   decomposition for that feature; record the choice and skip writing the
   redundant file.
5. **Record the manual-pass author** in `## Consistency notes` when
   `agent_version` starts with `manual-`. The fallback is already
   deprecated as of the commit that ships this skill alongside the
   [`feature-consistency-reviewer`](../../agents/nolte-shared/feature-consistency-reviewer.md) agent. Every manual pass on a repo
   whose plugin runtime can resolve the agent is a workflow-health
   finding per `spec/project/feature/` §Consistency check; the right
   resolution is to upgrade the plugin runtime and rerun the check via
   the agent path.

### Examples

- Read `examples/01-single-feature-from-roadmap-item.md` when decomposing a single roadmap item into a feature for the first time.
- Read `examples/02-split-into-multiple-features.md` when a roadmap item is large enough to warrant multiple features.
- Read `examples/03-consistency-check-overlap.md` when the consistency checker reports potential overlap with existing features.

### Gotchas

- **The [`feature-consistency-reviewer`](../../agents/nolte-shared/feature-consistency-reviewer.md) agent has no shell access** (per `agent-management` §Tool access — read-only invariant). The dispatching call from this skill **MUST** confirm the working tree is a git repository (`git rev-parse --is-inside-work-tree`) and pass the short SHA (`git rev-parse --short HEAD`) as a dispatch argument; the agent uses the SHA to populate `agent_version` in its findings report. Skipping this step and dispatching anyway produces an `agent_version: unknown` field in every consistency-check result.
- **The manual-fallback path is deprecated, not removed.** When the agent dispatch in Operation 2 step 1 fails because the plugin runtime predates the agent's release, the operator can still walk the investigation surface manually — but the skill **MUST** ask explicit permission before falling back, and the resulting `consistency_check` block carries `agent: manual-<YYYY-MM-DD>` instead of an agent name. Auditing later that bypasses surface as if it were a regular agent run mis-attributes the resolution decisions.
- **`verifies_sprint_value` is a feature-side invariant, not a sprint-side one.** At most one feature per sprint carries a non-null `verifies_sprint_value`; setting it on two features in the same sprint is a hard violation per `spec/project/feature/` §Frontmatter schema. The skill defaults the field to `null` on every new feature; the operator opts in explicitly when authoring or when [`sprint-plan`](sprint-plan.md) reassigns the verifier.
- **The `R-<n>` and `F-<n>` ID counters are monotonic across the project's lifetime, never reused** even after deletion. Deriving the next ID from "max existing ID + 1" without checking the git history's deleted IDs would silently re-use a retired ID. The skill reads the highest existing ID under `project/features/` plus the highest deleted ID from `git log` before assigning.

### Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/feature-decompose/<run-id>.yml` after every successful user-approval gate and after each named phase boundary. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope (`schema_version`, `run_id`, `inputs`, `phase`, `decisions[]`, `status`, ...) and the fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

### Hard rules

- **Never** transition a feature past `status: draft`. Only [`sprint-plan`](sprint-plan.md)
  (`draft → ready` after a `sprint` value is assigned) and [`sprint-execute`](sprint-execute.md) /
  [`sprint-review`](sprint-review.md) (later transitions) own status flips. This skill writes
  `status: draft` and stops.
- **Never** write a feature file without a populated `consistency_check`
  frontmatter object whose `findings` array is non-empty (a clean run still
  records `kind: clean`) and a populated `## Consistency notes` section.
- **Never** set `verifies_sprint_value` on more than one feature per sprint
  within a single decomposition; the at-most-one-per-sprint invariant is
  feature-side per the spec.
- **Never** invent a roadmap item, an outcome, or an audience inline;
  missing references block the write rather than fabricating them.
- **Never** rename a slug after the feature leaves `draft`; the skill writes
  the slug once and treats it as immutable thereafter.
- **Never** carry a process-internal acceptance criterion ("PR approved",
  "merged to develop", "CI green"); criteria are user-visible behaviour,
  not workflow gates.
- **Never** include effort estimates, points, due dates, or assignment
  fields beyond the nine declared frontmatter fields; lints flag unknown
  keys.
- **Never** dispatch [`feature-consistency-reviewer`](../../agents/nolte-shared/feature-consistency-reviewer.md) from inside an agent
  context. This is a skill operation; the parent dispatcher of this skill
  is the user or another skill, never an agent.
- **Never** write the feature file when the operator declines to resolve an
  `overlap` or `duplication` finding; the partial write would silently
  break the `draft → ready` gate downstream.
- When `spec/project/feature/` disagrees with this skill, the spec wins.
  Propose updating this skill rather than silently diverging.
