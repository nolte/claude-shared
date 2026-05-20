---
title: roadmap-init
audience: [maintainer]
content_mode: reference
track: developer-docs
last_updated: generated
---

# roadmap-init

_Scaffold the project planning pair `project/goals.md` and `project/roadmap.md` for the first time, per `spec/project/roadmap/`. Invoke when the user asks to "set up the roadmap", "initialise project goals", "create goals.md and roadmap.md", "bootstrap the roadmap", "wir brauchen eine Roadmap für dieses Projekt", "lege project/goals.md und project/roadmap.md an", or any equivalent fresh-bootstrap request. Also handles equivalent German-language requests. Verifies the audience artefact exists (and dispatches `audience-identify` when it doesn't), drafts the Vision plus numbered Outcomes in `project/goals.md`, drafts an empty queue plus optional phase headings in `project/roadmap.md`, presents both files for explicit approval, then writes them. Do NOT use to add roadmap items, retarget sprints, or flip MVP flags — that is `roadmap-planner`. Do NOT use to enforce the detail-level invariant — that is `roadmap-refine`._

- **Plugin:** `nolte-shared`
- **Phase:** 2 Plan (`plan`)
- **Tags:** `scaffolding`
- **Quelle:** [skills/roadmap-init/SKILL.md](https://github.com/nolte/claude-shared/blob/main/skills/roadmap-init/SKILL.md)

---

## Roadmap Init

Bootstraps the planning pair declared by `spec/project/roadmap/<canonical_language>.md`: a single `project/goals.md` carrying the Vision and the outcome catalogue, plus a single `project/roadmap.md` carrying an (initially empty) queue. Once both files exist, lifecycle work moves to `roadmap-planner` for adds and edits and to `roadmap-refine` for the detail-level invariant.

### Why this is a skill, not an agent

- **Mid-flow interactivity is the contract** — Vision wording and per-outcome phrasing are negotiated with the user; an agent's structured-report shape would lose the iteration.
- **Output flows back into the main conversation** — the drafted `goals.md` and `roadmap.md` need to be visible in the working context so the user can confirm them before they hit disk.
- **Orchestrator role** — when the audience artefact is missing, this skill dispatches `audience-identify` and resumes; the skill-orchestrates pattern (per `skill-vs-agent`) keeps the orchestrator in skill form.
- Counter-dimension considered: a narrow agent prompt could sharpen end-user-benefit phrasing for outcomes, but the load-bearing dimension is approval-before-write, not phrasing quality — skill wins.

### User-language policy

Detect the user's language and respond in it. The written `goals.md` and `roadmap.md` files use the project's primary language (per the spec's "project's primary language" wording). Detect that language by inspecting existing `project/`-level prose, the repo README, or — when the project has none yet — by asking the user explicitly.

The five fixed schema strings (`fine`, `coarse`, `backlog`, `proposed`, `active`, `done`, `cancelled`, plus the `O-<n>` and `R-<n>` ID shapes) stay in their canonical English form regardless of the project's primary language; they are machine-parseable identifiers, not prose.

### Preconditions

Before any write:

- The current working directory is inside a git repository.
- `project/goals.md` and `project/roadmap.md` **do not yet exist**. If either file is already present, stop and direct the user to `roadmap-planner` (for additions) or `roadmap-refine` (for invariant enforcement) instead of overwriting.
- The repo's audience artefact (typically `AUDIENCES.md`, or whichever location the project's `audience-identification` adoption uses) exists and is non-empty. When the artefact is missing or empty, dispatch the `audience-identify` skill and pause this skill until the user signals the artefact is ready; resume by re-reading it from disk. The spec mandates this dispatch, and outcome authoring is blocked until it completes.
- `project/mission.md` may or may not exist; this skill does not require it. Mission authoring is owned by a separate skill family.

### Operations

#### 1. Resolve the audience artefact

1. Locate the audience artefact (search for `AUDIENCES.md` at the repo root and inside `docs/`; check the README for an "Audiences" or "Intended consumers" section). If precedent exists, use it.
2. When no audience artefact is found, dispatch `audience-identify` and pause this skill; resume only after the user signals the artefact is ready. Do not invent audiences inline; the spec is explicit that fabricated audiences are a blocker, not a hint.
3. Read the resolved audience artefact and capture the audience identifiers (short labels). The outcomes drafted in step 2 cite these identifiers; an outcome that cannot be tied back to a confirmed or assumed audience entry is rejected.
4. When `audience-identify` was dispatched in step 2, resume only after the user signals the audience artefact is ready; do not poll. Re-read the artefact from disk on resume — never trust a stale in-memory copy.

#### 2. Draft `project/goals.md`

Compose two sections, in this order:

1. `# Vision` (or the project's existing top heading convention) — one paragraph stating what the project is and who it is for, phrased in the project's primary language.
2. `## Outcomes` — a list of outcomes. For each outcome:
   - Assign a stable identifier `O-1`, `O-2`, … monotonically. Never reuse an ID across the project's lifetime, even after deletion.
   - Write a one-sentence end-user benefit (not an internal capability statement). "Operators run a single command to ship a release" is acceptable; "We refactor the release pipeline" is not.
   - Cite the audience identifier the outcome serves; the audience must resolve to an entry in the audience artefact.

Recommended shape per outcome (the spec mandates the ID and the one-sentence benefit; the trailing audience cite is recommended for the audit trail):

```markdown
- **O-1** — End users authenticate via the new SSO provider in under three steps. _(audience: end-user)_
```

Iterate with the user until the Vision and every outcome are approved. Do not write the file yet.

#### 3. Draft `project/roadmap.md`

Compose:

1. A short top-of-file paragraph stating that this file is the queue governed by `spec/project/roadmap/`, and that detail levels and lifecycle are enforced by `roadmap-refine` and `roadmap-planner`.
2. Optional level-2 phase headings (for example `## Phase 1 — Foundations`, `## Phase 2 — Stabilisation`) when the user wants them. Phases are documentation, not schema; a flat roadmap with zero phase headings is equally valid. Ask the user; do not assume phases.
3. No roadmap items. The queue starts empty by design — items are added by `roadmap-planner`.

Item IDs (`R-<n>`) are monotonic and never reused across the project's lifetime, parallel to outcome IDs in `goals.md`. The empty queue created here means `roadmap-planner` will start its counter at `R-1`; document the convention in the top-of-file paragraph so later contributors don't reset it.

#### 4. Present both drafts and confirm

Show the drafted `goals.md` and `roadmap.md` side by side. Iterate per-section on the user's feedback. Do not write either file until the user explicitly approves both.

#### 5. Write the files

Once approved:

1. Create `project/` if it does not yet exist.
2. Write `project/goals.md` and `project/roadmap.md` in one operation; refuse partial writes. When the write of either file fails, roll back so a freshly bootstrapped project never lands in a half-bootstrapped state with one file present and the other missing.
3. Confirm the paths back to the user in their language and remind them that:
   - `roadmap-planner` is the entry point for adding items, retargeting sprints, and flipping MVP flags.
   - `roadmap-refine` walks the queue and reports detail-level violations once items exist.
   - When `project/mission.md` is added later, every roadmap item will start carrying the `mvp` field.

### Gotchas

- The audience artefact's location is **not** standardised by `audience-identification`; follow whatever precedent the repo already uses (`AUDIENCES.md`, a README section, or an ADR). Inventing a new location here just because none was obvious is wrong; ask the user before introducing a new convention.
- Outcome IDs and roadmap item IDs share the same monotonicity rule but live in different files; do not cross the streams. `O-1` and `R-1` are independent counters.
- The spec does not prescribe the Vision heading text. Match whatever convention the project already uses (German repos often title it `# Vision` or `# Zielbild`); the canonical-language wording does not force a translation here.

### Hard rules

- **Never** invent audience entries inline. When no audience artefact exists, dispatch `audience-identify` first; outcomes whose audience is fabricated cannot serve a real reader.
- **Never** overwrite an existing `project/goals.md` or `project/roadmap.md`. If either file is present, stop and redirect to the appropriate sibling skill.
- **Never** assign an outcome ID that has already existed in the file's history (even if currently deleted). `O-<n>` is monotonic and never reused across the project's lifetime.
- **Never** phrase an outcome as an internal capability ("we refactor X", "we set up Y"); outcomes are end-user benefits.
- **Never** add roadmap items inside this skill. The queue starts empty; additions are owned by `roadmap-planner`.
- **Never** write the files before the user has approved both drafts in the same review.
- **Never** assume the project's primary language; detect it from existing prose or ask explicitly.
- When `spec/project/roadmap/` disagrees with this skill, the spec wins. Propose updating this skill rather than silently diverging.
