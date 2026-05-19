# sprint-plan

_Create a new sprint file at `project/sprints/<NNNN>-<slug>.md` per the project sprint spec. Invoke when the user asks to plan a sprint, open a sprint, draft the next sprint, schedule a sprint, or pull roadmap items into a sprint. Also handles equivalent German-language requests. Resolves the next monotonic sprint number, walks the value-delivery contract (rejects operator-internal verbs in `value_statement`), pulls in roadmap items whose `target_sprint` matches, populates the `features` list (delegating to `feature-decompose` when decompositions are missing), names the value-verifying feature, and writes the file with `status: planned`._

- **Plugin:** `nolte-shared`
- **Phase:** 2 Plan (`plan`)
- **Tags:** `scaffolding`
- **Source:** [skills/sprint-plan/SKILL.md](https://github.com/nolte/claude-shared/blob/main/skills/sprint-plan/SKILL.md)

---

## Sprint Plan

Creates `project/sprints/<NNNN>-<slug>.md` per `spec/project/sprint/<canonical_language>.md`. This skill owns the `planned` state of the sprint lifecycle: it resolves the sprint number, captures the `value_statement` from the operator, pins the value-verifying feature, and writes the planned-state markdown. It deliberately doesn't activate the sprint or move features—`sprint-execute` owns those transitions.

### Why this is a skill, not an agent

- **Mid-flow user dialogue is core** — the value statement is rejected if it begins with operator-internal verbs (`refactor`, `migrate`, …); resolving a rejection means a back-and-forth with the user, which an agent's structured-report shape can't carry.
- **Output flows back into the main conversation** — the drafted sprint markdown, the resolved roadmap-item list, and the named value-verifying feature all live in the user's working context; isolating them behind an agent boundary would obscure the iterative review.
- **Orchestrator that may dispatch other skills** — when a roadmap item lacks a feature decomposition, this skill reports the gap (and may chain `feature-decompose` per the skill-vs-agent hybrid pattern); orchestrators default to skill form.
- Counter-dimension considered: a tool-restricted agent could perform the next-number resolution and the YAML write cleanly, but the load-bearing dimension is the user-facing rejection / iteration loop on `value_statement` — skill wins.

### User-language policy

Detect the user's language and respond in it. The sprint markdown itself is written in the project's primary language (typically EN); the `value_statement`, `## Goal`, and other body content stay in the project's primary language so consuming skills (`sprint-execute`, `sprint-review`) read a single deterministic surface. Frontmatter keys, lifecycle tokens, and feature / roadmap IDs are always English.

### Preconditions

Before drafting any file, confirm:

- Current working directory is inside a git repository whose `project/` planning suite is adopted (at minimum `project/roadmap.md` and `project/goals.md` exist per `spec/project/roadmap/`). If `project/` is missing entirely, stop and report—planning hasn't been bootstrapped.
- A `project/sprints/` directory exists or can be created. List the existing sprint files (`ls project/sprints/*.md` or equivalent) to read every present `number` from frontmatter.
- The user has supplied (or will supply on prompt) a one-sentence `value_statement` from the end-user perspective. If they haven't, ask before proceeding; never invent it.
- At least one roadmap item is `proposed` or `active` and either has `target_sprint` matching the next sprint number or the user has named which roadmap items the new sprint should pull in. An empty roadmap is a hard stop—report and hand back.

### Operations

#### 1. Resolve the next sprint number

Read every `project/sprints/*.md` file's frontmatter `number` field. The next sprint's number is `max(existing numbers) + 1`, or `1` when no sprint files exist. Sprint numbers are strictly monotonic across the project's lifetime per `spec/project/sprint/` §Directory layout and file shape; never reuse a number from a `cancelled` or `closed` sprint.

Format the number as four-digit zero-padded (`0001`, `0007`, `0042`).

#### 2. Capture and validate the `value_statement`

Ask the user for a one-sentence value statement phrased from the end-user perspective. Reject the statement (don't write the file; surface the violation with the offending verb quoted) when it begins with or is built around an operator-internal verb in either the project's primary language or German:

- English: `refactor`, `restructure`, `set up`, `configure`, `clean up`, `migrate`, `bump`, `update dependency`
- German: `refaktorieren`, `umbauen`, `einrichten`, `konfigurieren`, `aufräumen`, `migrieren`, `aktualisieren`, `Abhängigkeit erneuern`

The list **MAY** be widened per project; consult `.github/sprint-rejection-rules.yml` if it exists. The check is heuristic: when the user genuinely delivers an end-user-facing change whose phrasing happens to start with one of these verbs, they **MAY** override with a one-line rationale that is then recorded verbatim in the sprint's `## Goal` section.

#### 3. Derive the slug

Slugify the `value_statement` (or a shortened form the user confirms) into ASCII kebab-case: lowercase, hyphens between words, no punctuation, target ≤6 words. The slug **SHOULD** stay aligned with the value statement so directory listings remain self-describing.

Filename: `project/sprints/<NNNN>-<slug>.md`.

#### 4. Resolve roadmap items

Read `project/roadmap.md` and collect every roadmap item whose `target_sprint` equals the new sprint's number. Present the list to the user and confirm. The user **MAY** add or remove items at this step; record the final list as `roadmap_items` in the sprint frontmatter.

An empty `roadmap_items` list is permitted only for hardening sprints whose features still link to a roadmap item per the `feature` spec. When the list is empty, the `## Goal` section **MUST** state the hardening intent explicitly and cite the roadmap item(s) the features link to (per `spec/project/sprint/` §Roadmap and feature linkage).

#### 5. Resolve features

For each roadmap item collected in step 4, walk `project/features/` and find features whose frontmatter `roadmap_item` matches and whose `sprint` is null or already equals the new sprint's number. Two outcomes per roadmap item:

- **Features exist** — collect their `id` values into the `features` list candidate.
- **No features exist** — surface the gap to the user and offer to dispatch `feature-decompose` (the skill that decomposes a roadmap item into one or more features per `spec/project/feature/`). Don't fabricate features inline; if the user declines decomposition, drop the roadmap item back out of the sprint and move on.

After confirming the final feature list with the user, set each chosen feature's `sprint` frontmatter field to the new sprint number in the same write operation that adds the feature's `id` to the sprint's `features` list. The bidirectional invariant (feature side ↔ sprint side) is the canonical check per `spec/project/feature/` §Frontmatter schema; partial updates are forbidden.

#### 6. Name the value-verifying feature

Exactly one feature in the sprint **MUST** carry a non-null `verifies_sprint_value: acceptance-<n>` frontmatter field per `spec/project/sprint/` §Value-delivery contract. Walk the candidate features:

- If exactly one feature already declares `verifies_sprint_value` and its named acceptance criterion plausibly verifies the sprint's `value_statement`, confirm with the user and keep it.
- If zero features declare it, ask the user to pick the verifying feature plus the specific `acceptance-<n>` identifier on that feature, and write the field. The `feature-decompose` skill is the canonical write authority at decomposition time; `sprint-plan` is the canonical write authority during planning per `spec/project/feature/` §Frontmatter schema.
- If more than one feature declares it, the constraint is violated; stop and ask the user to resolve down to exactly one before continuing.

#### 7. Render the sprint file

Write the file with this exact shape (frontmatter keys in the declared order from `spec/project/sprint/` §Frontmatter schema):

```markdown
---
number: <NNNN>
status: planned
started: null
ended: null
value_statement: <one sentence from step 2>
artifact_ref: null
last_commit: null
roadmap_items: [<R-x>, <R-y>]
features: [<F-a>, <F-b>]
---

### Goal

<paragraph elaborating value_statement; include override rationale here when step 2 used the heuristic-override path>

### Features

- [<F-a>](../features/<slug-a>.md) — status: ready
- [<F-b>](../features/<slug-b>.md) — status: ready

### Out of scope

- <items the user explicitly excluded; cite the roadmap item or `None`>

### Review notes

_Populated by `sprint-review` at closure._
```

The `## Features` body bullet list **MUST** mirror the `features` frontmatter list exactly; `sprint-execute` enforces the invariant on every later mutation, but the initial write must already be consistent.

#### 8. Present and confirm

Diff the planned file content back to the user before writing. Confirm:

- The resolved sprint number and filename.
- The accepted `value_statement` (and any rejection-override rationale).
- The `roadmap_items` and `features` lists, with the named verifying feature highlighted.

Only write the file once the user approves. Report back: the path written, the sprint number, the named verifying feature's `id` plus `acceptance-<n>`.

### Gotchas

- **`value_statement` must avoid operator-internal verbs.** "Refactor the release pipeline" reads as internal work; "Operators run a single command to ship a release" is the user-visible value the spec demands. The skill's heuristic flags imperative-form verbs that don't name a user benefit and asks the operator to rephrase before write.
- **The `## Features` body list and the `features` frontmatter array MUST stay in lockstep.** `sprint-execute` enforces the bidirectional invariant later, but this skill creates the initial pair; an asymmetric write (only frontmatter, only body) leaves the sprint malformed and blocks subsequent `sprint-execute` runs.
- **`verifies_sprint_value` lives on a feature, not on the sprint.** The sprint frontmatter names which feature carries the verifier (`verifies_sprint_value: F-<n>:acceptance-<m>`); the feature carries the actual `verifies_sprint_value: acceptance-<m>` field per the feature spec. Authoring the verifier in the sprint frontmatter without setting it on the feature side leaves the cross-reference half-broken.
- **Sprint numbers are monotonic, never reused.** The skill resolves the next sprint number by reading the highest existing `<NNNN>` under `project/sprints/` plus the highest deleted number from `git log -- project/sprints/`. A retired sprint number isn't available for reuse, even after a `cancelled` sprint.
- **At most one sprint is `active` at a time.** Creating a `planned` sprint while another is `active` is fine (planned sprints are queue items, not active commitments). The at-most-one invariant only applies to `status: active`; this skill writes `status: planned` and lets `sprint-execute` perform the `planned → active` promotion when the operator starts the first feature.

### Hard rules

- **Never** reuse a sprint number from a `cancelled` or `closed` sprint. Numbers are strictly monotonic per `spec/project/sprint/` §Directory layout and file shape.
- **Never** write a sprint with `status` other than `planned`. Activation is `sprint-execute`'s authority.
- **Never** invent roadmap items, features, or audiences inline. Missing decompositions are reported as gaps; missing audiences are a `roadmap`-side concern, not a sprint-side fix.
- **Never** persist a `value_statement` that begins with an operator-internal verb without an explicit user-supplied override rationale recorded in `## Goal`.
- **Never** write a `features` frontmatter list that diverges from the `## Features` body bullet list at initial creation.
- **Never** set `verifies_sprint_value` on more than one feature in the sprint, or leave it unset on every feature when the sprint is intended to close eventually.
- **Never** edit any sprint other than the one being planned in this run; lifecycle transitions on existing sprints are `sprint-execute` and `sprint-review` territory.
- When `spec/project/sprint/` disagrees with this skill, the spec wins. Propose updating this skill rather than silently diverging.
