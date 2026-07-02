---
name: blog-author-trigger
description: "Operationalises spec/project/blog-author-trigger/: on a feature→done transition it derives a blog-post briefing from the feature record, computes a new/update/defer suggestion from the blog consumer's existing-post index, presents the three-way operator choice, and either dispatches blog-author with the derived briefing (Choices 1 and 2, via the cross-repository handover with explicit operator confirmation) or writes a deferral artefact under project/blog-triggers/ (Choice 3). Typically automatically dispatched by sprint-execute right after a feature reaches done; also invocable directly (\"trigger a blog post for feature X\", \"Blog-Trigger für Feature X\", \"soll ich zu Feature X bloggen?\"). Don't use to draft the post itself (use blog-author), to define the feature record (feature spec), to close a sprint (sprint-review), or to publish a release (release-publish-trigger). Supports resume on re-invocation per spec/claude/resumable-work/."
tags: [prose, lifecycle]
phase: build
summary: "On a feature→done transition, derives a blog-post briefing, suggests new/update/defer, and either dispatches blog-author or writes a deferral artefact."
summary_de: "Bei einem feature→done-Übergang leitet es ein Blog-Post-Briefing ab, schlägt neu/update/defer vor und dispatched entweder blog-author oder schreibt ein Deferral-Artefakt."
use_when:
  - "a feature reached done and you want to decide whether it warrants a blog post"
  - "sprint-execute just marked a feature done and automatically dispatched the blog trigger"
  - "you want the derived briefing handed to blog-author or deferred to a backlog entry"
dont_use_when:
  - situation: "You want to draft the post itself rather than decide and derive the briefing"
    alternative: blog-author
  - situation: "You want to publish a release rather than trigger a blog post"
    alternative: release-publish-trigger
see_also:
  - blog-author
  - sprint-execute
resumable: true
---

# Blog Author Trigger

Operationalises `spec/project/blog-author-trigger/<canonical_language>.md`: the **when** layer that bridges a `feature → done` transition in a source consumer (a `claude-shared`-shape repository with `project/features/`) to the **what** layer, `blog-author`, which drafts the bilingual post pair in a blog consumer (reference: `nolte/blog`). The trigger spec is contract-only and leaves the wiring mechanism open; this skill is the reference wiring per the spec's §Open questions resolution — a dedicated trigger skill that `sprint-execute` automatically dispatches after it writes a feature's `done` status.

This skill binds the spec's contract to an on-disk procedure. When this skill and the spec disagree, the spec wins and this skill needs the update.

## Why this is a skill, not an agent

- **Mid-flow operator decision is load-bearing** — the spec's §Operator decision contract requires the operator to answer exactly one of three choices (new post / update existing post / defer to backlog) at the trigger point, in the same session; an agent's fire-and-forget shape can't carry that gate.
- **Cross-repository handover is an externally-visible action under confirmation** — Choices 1 and 2 hand off to a separate blog-consumer working tree; the spec forbids silent writes there, so the working-directory switch needs operator confirmation that only a conversational skill surfaces.
- **Orchestrator that dispatches another skill** — Choices 1 and 2 dispatch `blog-author`; the skill-orchestrates pattern (per `spec/claude/skill-vs-agent/`) defaults the orchestrator to skill form.
- Counter-dimension considered: the briefing-derivation step alone is deterministic (§Briefing derivation maps a feature record to a briefing with no interactivity) and would fit an agent cleanly. It still lives here because the three-way decision and the cross-repository confirmation each need operator dialogue, and consolidating them behind one entry point keeps the operator's mental model coherent. Same precedent as `release-publish-trigger`.

## German trigger phrases

This skill also triggers on equivalent German-language requests, including:

- "Blog-Trigger für Feature <X>"
- "soll ich zu Feature <X> bloggen?"
- "leite ein Blog-Briefing aus Feature <X> ab"

## User-language policy

Detect the operator's language and respond in it. The derived briefing fields are written in English (they feed `blog-author`, whose EN post is the canonical source per the blog consumer's `CLAUDE.md`); the deferral-artefact YAML keys and the `<feature-slug>.briefing.md` pre-stage file are English so downstream tooling parses them reliably. Feature IDs, slugs, `translationKey`, and `portfolioProject` stay English regardless of prose language.

## Consumer contract resolution

Before deriving anything, resolve the two roles per `spec/project/blog-author-trigger/` §Consumer contract from the source consumer's `CLAUDE.md`:

- **Source consumer** — this repository: hosts features under `project/features/<slug>.md` and drives transitions via `sprint-execute`. The `in_progress → done` transition is the trigger event.
- **Blog consumer** — the repository declared in `CLAUDE.md` that receives derived briefings (reference: `nolte/blog`, clone path `~/repos/github/blog`). The source consumer **MAY** declare itself as its own blog consumer.

When `CLAUDE.md` declares no blog consumer, stop with a single-sentence message naming the missing declaration; the operator amends `CLAUDE.md` (per the source-consumer contract) before the trigger can proceed.

## Inputs — the trigger event

The trigger event payload is derived **only** from the on-disk feature record and git history, per `spec/project/blog-author-trigger/` §Trigger event:

- feature **`id`** and **`slug`**;
- feature **`title`** and **`description`** (free-text body);
- the **acceptance criteria** list (the `## Acceptance criteria` block);
- the **roadmap-item back-reference** (`roadmap_item`) when present;
- the source-consumer **repository name** (for example `nolte/claude-shared`) and the **commit SHA** of the `in_progress → done` transition commit.

When `sprint-execute` automatically dispatches this skill, it passes the just-transitioned feature's `id`/`slug`. When invoked directly, resolve the payload from `project/features/<slug>.md` plus `git log` for the transition SHA.

## Operations

### 1. Resolve the trigger event

- Read `project/features/<slug>.md`. Confirm `status: done`; if it is anything else, **refuse** — only `feature → done` fires this trigger (no other lifecycle transition does).
- Resolve the `done`-transition commit SHA: the commit that set `status: done` on the record (`git log -1 --format=%H -- project/features/<slug>.md`, cross-checked against the `ended` date).
- Assemble the payload above. Carry nothing not derivable from the record or git history (the trigger is reproducible).

### 2. Derive the briefing

Apply the deterministic rules from `spec/project/blog-author-trigger/` §Briefing derivation. The derived values are starting points the operator refines at `blog-author` intake, never final values:

- **topic-as-thesis** — feature `title` plus the first sentence of `description`, phrased as an assertion.
- **grounded artefact** — `<owner>/<repo>` plus the `done`-transition SHA (satisfies `blog-author` §Briefing inputs minimally).
- **primary audience** — left **unset**; the operator selects it at `blog-author` intake (the trigger has no basis to choose).
- **source list** — seeded with `https://github.com/<owner>/<repo>/commit/<sha>`; the operator extends it.
- **slug** — the feature `slug` with the lifecycle prefix removed (for example `add-lektorat-scanner-agent` → `lektorat-scanner-agent`).
- **cross-language binding key** (`translationKey`) — derived from the post slug per the blog consumer's rule (reference consumer: equal to the slug).
- **`portfolioProject`** — derived from the source repository name when the blog consumer ships a portfolio mapping; otherwise the operator supplies it at intake.

### 3. Compute the suggestion and present the three-way choice

- When the blog consumer's existing-post index is reachable, compute an advisory suggestion (the operator's choice always overrides it): derived slug absent from the index → suggest Choice 1; derived slug present → suggest Choice 2 with that post as target; the feature is a non-value-verifying mid-sprint feature whose sprint's `verifies_sprint_value` feature hasn't shipped → suggest Choice 3.
- Present **exactly three** choices and require the operator to pick one in this session. If the session ends without a choice, the trigger is implicitly deferred (Choice 3).
- When multiple `feature → done` transitions fire in one session, surface them **sequentially** — one three-way choice per feature, never batched into a single decision (per `spec/project/blog-author-trigger/` §Operator decision contract, this keeps the exactly-three-choices gate intact per feature). You **MAY** offer a "skip all remaining → defer to backlog" shortcut that defers every remaining feature via Choice 3.

### 4. Execute the chosen path

- **Choice 1 — new post.** Pre-stage the derived briefing at `project/blog-triggers/<feature-slug>.briefing.md` in the source consumer, surface the blog consumer's clone path, and dispatch `blog-author` with the briefing as Step-1 input (in-place when the source consumer is its own blog consumer; otherwise per §Cross-repository handover).
- **Choice 2 — update existing post.** As Choice 1, plus the target post's existing `slug` and `translationKey` (operator picks from the index) and an **update reason** derived from the feature `title` plus a one-line summary of what changed.
- **Choice 3 — defer to backlog.** Write the deferral artefact (next operation). No `blog-author` dispatch.

### 5. Deferral artefact and consumption

- A Choice-3 deferral writes `project/blog-triggers/<feature-slug>.yml` in the **source** consumer, carrying the full §Trigger-event payload plus `deferred_at` (ISO timestamp), `deferral_reason` (operator-supplied), and `status: deferred`.
- A later trigger-run on the same feature `id` **consumes the existing artefact** rather than creating a second one: on a subsequent Choice 1 or 2 it sets `status: deferred → consumed`. `status: cancelled` is operator-set only, never trigger-set.
- `sprint-review` surfaces unconsumed deferrals at sprint close (the source consumer's wiring; this skill writes the artefact, doesn't drive the surfacing).

## Cross-repository handover

When source consumer ≠ blog consumer (the reference pair `nolte/claude-shared` + `nolte/blog`):

- Run within the **source** consumer's working directory; read the feature record and write the deferral / pre-stage files under the source consumer's `project/blog-triggers/`.
- **Never** silently `cd` into the blog-consumer working tree. Surface its path and let the operator confirm the working-directory switch (or open a new session in the blog clone) before any `blog-author` dispatch.
- **Never** write files into the blog consumer's working tree without explicit operator confirmation.
- The pre-staged `project/blog-triggers/<feature-slug>.briefing.md` uses the briefing shape `blog-author` §Briefing inputs expects, so the operator can copy or open it in the blog session.

When the source consumer **is** the blog consumer, the handover collapses: dispatch `blog-author` in-place with no working-directory switch.

## Automatic dispatch from sprint-execute

`sprint-execute` Operation C (`in_progress → done`), step 6, dispatches this skill for the just-completed feature after it surfaces the updated sprint state. The dispatch is the reference wiring for the spec's `feature → done` trigger event; the operator then walks Operations 3 to 5 here. A feature done via a direct invocation of this skill (not through `sprint-execute`) follows the identical path.

## Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/blog-author-trigger/<run-id>.yml` after the operator's three-way choice and after each named phase boundary (event-resolved, briefing-derived, choice-made, dispatched-or-deferred). On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation (matching key: feature `id`); if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope and the fail-closed semantics on schema or YAML errors are load-bearing in that spec; don't duplicate them here.

## Examples

- Read `examples/01-new-post-from-feature-done.md` when a feature reaches `done`, its slug is absent from the blog consumer's index, and the operator chooses to author a new post.
- Read `examples/02-defer-to-backlog.md` when the operator defers and the skill writes the deferral artefact under `project/blog-triggers/`.
- Read `examples/03-update-existing-post.md` when the derived slug already exists in the blog consumer's index and the operator picks Choice 2 to update that post.

## Hard rules

- **Never** fire on any transition other than `feature → done`. `ready → in_progress`, `done → cancelled`, and sprint-level transitions don't trigger this skill.
- **Never** carry trigger-event payload that isn't derivable from the on-disk feature record or git history; the trigger is reproducible.
- **Never** write files into the blog consumer's working tree without explicit operator confirmation, and never silently `cd` into it.
- **Never** proceed past the trigger point without the operator's three-way choice; a session that ends without one is an implicit Choice-3 deferral.
- **Never** create a second deferral artefact for a feature `id` that already has one; consume the existing artefact instead.
- **Never** set `status: cancelled` on a deferral artefact; that value is operator-set only. The trigger sets `deferred → consumed`.
- **Never** draft the post itself; dispatching `blog-author` is the only authoring path.
- When `spec/project/blog-author-trigger/` disagrees with this skill, the spec wins. Propose updating this skill rather than silently diverging.
