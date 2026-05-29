# Blog author trigger

Status: draft

<!-- vale Microsoft.Quotes = NO -->
<!-- vale Microsoft.Contractions = NO -->
<!-- vale Microsoft.Dashes = NO -->

## Context

Readers: implementors of a future trigger skill or hook that invokes the [`blog-author`](../blog-author/en.md) skill (primary), human operators considering when a feature's completion warrants a blog-post update (secondary), and skill authors integrating this trigger with the consumer's sprint and feature lifecycle.

The [`blog-author`](../blog-author/en.md) skill defines **what** an author produces—a bilingual post pair, a self-check manifest, a sources-to-claim mapping, a handover manifest. What that spec deliberately leaves open is **when** the author is invoked. Today the only canonical trigger is operator-initiated: the operator types `/nolte-shared:blog-author` (or an equivalent natural-language request) and walks the briefing intake. The post pair lives in a separate consumer repository (the reference consumer is `nolte/blog`); the trigger doesn't fire automatically when work in the **same** consumer's source tree reaches a state that warrants writing about it.

This spec closes the gap on one side of that question: it defines the contract by which a **feature-done event** in a consumer of this plugin's sprint-and-feature specs (`spec/project/sprint/`, `spec/project/feature/`) can be wired to a **blog-post suggestion** that the operator either accepts (which invokes `blog-author` with a derived briefing) or defers (which records the trigger in a per-feature backlog). The spec is **contract-only**: it names the trigger event, the derived briefing shape, the operator decision points, and the relationship to the calling skills. It does **not** prescribe the wiring mechanism (a hook in `settings.json`, a follow-up dispatch from `sprint-execute`, a separate trigger skill); that choice is open and tracked under §Open questions.

The reference scenario this spec is designed for: a feature in `nolte/claude-shared` (this plugin) reaches `done` via `sprint-execute`; the operator wants `blog-author` to produce a draft (new post or update to an existing post) about that feature in `nolte/blog`. The spec is phrased so the same trigger works for any consumer pair where one repository hosts the source of work and another repository hosts the personal blog.

## Goals

- Define a **named trigger event** (`feature → done`) that downstream skills, hooks, or operator workflows can attach to, with a closed input contract derived from the feature record.
- Define the **briefing-derivation contract**: how a feature record (per `spec/project/feature/`) is converted into a briefing that satisfies the §Briefing inputs of [`blog-author`](../blog-author/en.md).
- Define the **operator decision contract**: at the trigger point, the operator answers one of three choices—author a new post, update an existing post, defer to backlog. The spec names how each choice flows downstream.
- Define the **dual-repository contract**: the source feature lives in one consumer repository (here: a `claude-shared`-shape repository with `project/features/`); the post pair lives in a separate consumer repository (here: a `blog-author`-shape blog repository). The trigger is the bridge.
- Define the **deferral artefact**: a defer-to-backlog choice doesn't silently drop the trigger; it produces a per-feature record that can be re-surfaced at sprint review or later.
- Keep the spec **wiring-agnostic**: the mechanism (hook, skill chain, separate trigger skill) is open. The spec is the contract every mechanism must honour.

## Non-goals

- Defining the **wiring mechanism** for the trigger. Whether the trigger fires from a Claude Code `settings.json` hook, from a follow-up dispatch inside `sprint-execute`, from a new dedicated trigger skill, or from a GitHub Action is intentionally out of scope; see §Open questions.
- Defining **how `blog-author` produces the post** once invoked. That's exhaustively covered by [`blog-author`](../blog-author/en.md); this spec ends at the operator's choice and at handing the derived briefing over.
- Defining **the feature record shape itself** (frontmatter, lifecycle states, AC structure). That's owned by [`spec/project/feature/`](../feature/en.md); this spec consumes the feature record as it exists.
- Defining **the sprint-execute lifecycle** (when a feature transitions `in_progress → done`, who decides, what gates apply). That's owned by [`spec/project/sprint/`](../sprint/en.md); this spec consumes the transition event.
- Defining **cross-repository write access** (whether the trigger skill operates in one repo and writes into another, or whether the operator switches repos manually). The spec describes the contract; the §Reference example annex names how the reference consumer pair (`nolte/claude-shared` + `nolte/blog`) handles it, but other consumer pairs may handle it differently.
- Defining **publishing cadence policy** (every feature gets a post vs. only milestone features vs. sprint-summary posts vs. ad-hoc curation). That's a roadmap-level question for the source consumer, not a trigger-spec question.
- Defining **the editor-side response to a triggered post** (would `lektorat-apply` treat triggered posts differently than operator-initiated ones?). Today the answer is no—triggered and manual posts share the same `blog-author` workflow, the same delivery contract, and the same lektor handover.

## Consumer contract

This spec presupposes two consumer repositories—a **source consumer** and a **blog consumer**: that may or may not be the same repository. A consumer adopting this spec **MUST** declare which role each side plays in its `CLAUDE.md` (or equivalent contract document).

### Source consumer

A source consumer adopting this spec **MUST** satisfy the following:

- The repository hosts features per [`spec/project/feature/`](../feature/en.md) and sprints per [`spec/project/sprint/`](../sprint/en.md). Features carry frontmatter that names at minimum a title, a status, and an acceptance-criteria block, and live under `project/features/<slug>.md`.
- The repository invokes [`sprint-execute`](../../../skills/sprint-execute/SKILL.md) (or an equivalent skill conforming to `spec/project/sprint/`) to drive feature transitions. The `in_progress → done` transition is the trigger event named in §Trigger event.
- The repository declares in its `CLAUDE.md` which **blog consumer** receives derived briefings—by name (for example `nolte/blog`), by clone path (for example `~/repos/github/blog`), or by both. A source consumer **MAY** declare itself as its own blog consumer (a single repository hosts both source work and the blog).

### Blog consumer

A blog consumer adopting this spec **MUST** satisfy the §Consumer contract of [`blog-author`](../blog-author/en.md). It additionally **MUST** declare:

- An **existing-post index** that the trigger can consult to answer the operator's "update an existing post?" question. The reference convention is the consumer's post-pair location (`src/content/posts/en/` for Astro consumers) plus a corpus listing that maps existing slugs to their `pubDate`, `tags`, and `portfolioProject` frontmatter.
- A **portfolio-project mapping** (optional, **SHOULD**) that lets the trigger pre-populate the briefing's `portfolioProject` field from the source consumer's repository name (for example, a feature in `nolte/claude-shared` maps to `portfolioProject: claude-shared`). When absent, the operator supplies the value at briefing intake.

## Requirements

### Trigger event

- **MUST** name the trigger event as **`feature → done`**: the transition of a feature record from `status: in_progress` to `status: done` per [`spec/project/feature/`](../feature/en.md) §Lifecycle. The event is observed at the moment the feature record is written to disk with the new status—not at the moment a PR is merged, not at the moment a sprint closes.
- **MUST** the trigger event carry the following payload, derived directly from the feature record:
  - The feature **`id`** and **`slug`**.
  - The feature **`title`** and **`description`** (free-text body of the feature record).
  - The feature's **acceptance criteria** as a list of strings (the body block under §Acceptance criteria in the feature file).
  - The feature's **roadmap-item back-reference** (if present) per [`spec/project/feature/`](../feature/en.md)—used to derive `portfolioProject` when the source consumer ships a roadmap-to-portfolio mapping.
  - The source-consumer **repository name** (for example, `nolte/claude-shared`) and the **commit SHA** of the `in_progress → done` transition commit.
- **MUST NOT** the trigger event carry any payload not derivable from the on-disk feature record or git history. The trigger is reproducible: given the same feature record and git history, the same trigger event fires.
- **MUST NOT** other lifecycle transitions (`ready → in_progress`, `done → cancelled`, sprint-level transitions) fire this trigger. Their semantics differ; their treatment belongs in separate triggers if and when needed (see §Open questions).
- **SHOULD** the trigger event carry a **derived suggestion** about whether the feature warrants a new post or an update to an existing post, computed from the existing-post index (see §Operator decision contract). The suggestion is advisory; the operator's choice overrides it.

### Briefing derivation

The trigger event is converted into a briefing that satisfies the §Briefing inputs of [`blog-author`](../blog-author/en.md). The derivation rules below are deterministic: given the same trigger event payload, the same briefing is produced.

- **MUST** derive the **topic-as-thesis** from the feature `title` plus the first sentence of the feature `description`. The operator is prompted to refine the thesis at briefing intake; the derived form is a starting point, not the final value. Example: feature "Add lektorat-scanner agent" with description "Read-only scanner that walks Markdown artefacts and returns D1–D5 findings" derives the thesis "I describe the read-only lektorat-scanner agent that walks Markdown artefacts and returns D1–D5 findings".
- **MUST** populate the **grounded-artefact** field with the source-consumer repository reference (`<owner>/<repo>` plus the `done`-transition commit SHA). This satisfies [`blog-author`](../blog-author/en.md) §Briefing inputs "at least one grounded artefact" minimally; the operator **MAY** add diffs, command outputs, or screenshots at intake.
- **MUST** leave the **primary audience** unset in the derived briefing. The trigger has no basis on which to choose between the consumer's end-reader subgroups (reference: `A`/`B`/`C`); the operator **MUST** select at intake.
- **MUST** seed the **source list** with at least the source-consumer repository URL (`https://github.com/<owner>/<repo>/commit/<sha>`). The operator extends the list at intake; the seed satisfies the spec's empty-list prohibition for posts that name the source consumer's repository.
- **MUST** derive the **slug** from the feature `slug` with the prefix removed (for example, feature `add-lektorat-scanner-agent` derives post slug `lektorat-scanner-agent`); when the derived slug already exists in the blog consumer's existing-post index, the trigger flags an update (see §Operator decision contract).
- **MUST** derive the **cross-language binding key** (reference: `translationKey`) from the post slug. The convention follows the blog consumer's slug-to-key rule; the reference consumer (`nolte/blog`) sets `translationKey` equal to the slug.
- **SHOULD** derive the **`portfolioProject`** from the source consumer's repository name when the blog consumer ships a portfolio mapping (for example, `nolte/claude-shared` → `portfolioProject: claude-shared`). When absent, the operator supplies the value at intake.

### Operator decision contract

At the trigger point, the operator answers exactly one of the three choices below. The choice is the gate to downstream behaviour; the trigger doesn't proceed without it.

- **Choice 1—author a new post.** The trigger dispatches [`blog-author`](../blog-author/en.md) with the derived briefing as Step-1 input. The operator walks the standard seven-step workflow from there.
- **Choice 2—update an existing post.** The trigger dispatches [`blog-author`](../blog-author/en.md) with the derived briefing plus the existing post's `slug` and `translationKey` (the operator picks the target post from the existing-post index). The update path is governed by [`blog-author`](../blog-author/en.md) §Briefing inputs "Update vs. new-post fields"; the trigger supplies the **update reason** as the feature `title` plus a one-line summary of what changed.
- **Choice 3—defer to backlog.** The trigger writes a per-feature backlog entry (see §Deferral artefact). The operator may revisit at sprint review or any time after; the entry persists until either consumed by a later trigger run or explicitly cancelled.

The operator **MUST** make the choice within the same Claude Code session in which the trigger fires; the trigger doesn't span sessions. If the session ends without a choice, the trigger is implicitly deferred per Choice 3.

When multiple `feature → done` transitions fire in one session, the trigger **MUST** surface them sequentially—one three-way choice per feature—rather than batching several features into a single decision; this keeps a-4's "exactly three choices per trigger point" intact per feature. The trigger **MAY** offer a skip-all-remaining shortcut that defers every remaining feature via Choice 3.

The trigger **MAY** carry a **derived suggestion** (per §Trigger event) recommending Choice 1, 2, or 3 based on the existing-post index lookup. Example heuristics (not normative):

- Derived slug not in the existing-post index → suggest Choice 1.
- Derived slug already in the existing-post index → suggest Choice 2 with that post as the target.
- Feature is the third in a sprint whose `verifies_sprint_value` feature hasn't yet shipped → suggest Choice 3 (defer until the sprint's value-verifying feature is ready, then write a sprint-summary post).

### Deferral artefact

A Choice-3 deferral writes a backlog entry that survives across Claude Code sessions and can be re-surfaced.

- **MUST** the deferral artefact live in the **source consumer's** repository (not the blog consumer's), under `project/blog-triggers/<feature-slug>.yml`. The path keeps the deferral co-located with the feature record it refers to.
- **MUST** the deferral YAML carry the full trigger-event payload (per §Trigger event) plus a `deferred_at` timestamp, a `deferral_reason` (free-text, operator-supplied at decision time), and a `status` field with one of the values `deferred`, `cancelled`, `consumed`.
- **MUST** a later trigger-run that re-encounters the same feature `id` consume the existing deferral artefact rather than create a second one. The trigger updates `status: deferred → consumed` when the operator chooses Choice 1 or Choice 2 on the second pass; `status: cancelled` is operator-set and never trigger-set. A deferral artefact can never become stale through feature cancellation: it is written only after `feature → done`, and [`spec/project/feature/`](../feature/en.md) §Lifecycle makes `cancelled` reachable only from `draft`, `ready`, or `in_progress`—never from `done`—so a feature carrying a deferral can never reach `cancelled` through the legal lifecycle.
- **SHOULD** the source consumer's `sprint-review` skill (per [`spec/project/sprint/`](../sprint/en.md) lifecycle) surface unconsumed deferrals at sprint close, so deferrals don't accumulate silently. The mechanism is the source consumer's choice; this spec describes the contract, not the wiring.

### Cross-repository handover

When the source consumer and the blog consumer are **different repositories**, the trigger crosses a repository boundary. The handover contract:

- **MUST** the trigger run within the source consumer's Claude Code working directory; the trigger reads the feature record from `project/features/<slug>.md` and writes the deferral artefact (when applicable) under the source consumer's `project/blog-triggers/`.
- **MUST** the dispatch to [`blog-author`](../blog-author/en.md) (Choices 1 and 2) cross the repository boundary explicitly. The trigger **MUST NOT** silently `cd` into the blog-consumer working directory; it **MUST** surface the path to the operator and let the operator confirm the working-directory switch (or open a new Claude Code session in the blog consumer's clone).
- **MUST NOT** the trigger write files into the blog consumer's working tree without explicit operator confirmation. The blog consumer's working tree is the operator's local clone; the trigger respects the local repository as the operator's working environment.
- **MAY** the trigger pre-stage the derived briefing as a Markdown file under the source consumer's `project/blog-triggers/<feature-slug>.briefing.md` for the operator to copy or open in the blog consumer's session. The pre-staged file uses the briefing shape that [`blog-author`](../blog-author/en.md) §Briefing inputs expects.

When the source consumer **is** the blog consumer (a single repository hosts both source work and the blog), the cross-repository handover collapses: the trigger dispatches `blog-author` in-place, with no working-directory switch.

The unconditional no-silent-write stance above is settled: this spec carries **no** opt-in for fully automatic cross-repo posting, and the operator confirmation **MUST** precede every write into the blog consumer's working tree regardless of how single-handed the consumer pair is. A future iteration that trades this safety margin for convenience (for example a `cross_repo_autopost` declaration that lets the trigger open the blog-consumer session automatically) is a deliberate owner-authorised change to this section, not a default the trigger may assume.

## Acceptance criteria

A trigger implementation (hook, skill, or operator workflow) satisfies this spec when **all** of the per-trigger criteria below hold.

- [ ] **a-1** The trigger fires exactly on the `feature → done` transition; no other lifecycle transition triggers it (per §Trigger event).
- [ ] **a-2** The trigger-event payload is fully derivable from the on-disk feature record and git history; no other source contributes to the payload (per §Trigger event).
- [ ] **a-3** The derived briefing satisfies the mandatory-fields list of [`blog-author`](../blog-author/en.md) §Briefing inputs, modulo the explicitly-operator-required fields (primary audience) (per §Briefing derivation).
- [ ] **a-4** The operator is presented with exactly the three choices (new post, update existing post, defer to backlog) at the trigger point (per §Operator decision contract).
- [ ] **a-5** A Choice-3 deferral writes a backlog entry under the source consumer's `project/blog-triggers/<feature-slug>.yml` with the schema described in §Deferral artefact.
- [ ] **a-6** A later trigger-run on the same feature `id` consumes the existing deferral artefact rather than create a duplicate (per §Deferral artefact).
- [ ] **a-7** When source consumer ≠ blog consumer, the trigger doesn't write files into the blog consumer's working tree without explicit operator confirmation (per §Cross-repository handover).
- [ ] **a-8** When the operator chooses Choice 1 or Choice 2, the derived briefing is handed to [`blog-author`](../blog-author/en.md) Step 1 and the standard seven-step workflow runs from there.

## Reference example annex

The reference consumer pair is:

- **Source consumer**: `nolte/claude-shared` (this plugin's repository). Hosts features under `project/features/<slug>.md`, invokes [`sprint-execute`](../../../skills/sprint-execute/SKILL.md) to drive transitions.
- **Blog consumer**: `nolte/blog` (a bilingual Astro static blog). Hosts post pairs under `src/content/posts/{en,de}/<slug>.md`, satisfies all `blog-author` consumer-contract surfaces per `spec/project/blog-author/` §Reference example annex.

The cross-repository handover for this pair is: the operator runs the trigger from the `claude-shared` clone; on Choice 1 or 2 the trigger writes a pre-staged briefing under `claude-shared/project/blog-triggers/<feature-slug>.briefing.md`, surfaces the path to `~/repos/github/blog`, and the operator opens a new Claude Code session in `~/repos/github/blog` and invokes `blog-author` with the pre-staged briefing as input.

The reference wiring that fires the trigger is the [`blog-author-trigger`](../../../skills/blog-author-trigger/SKILL.md) skill, automatically dispatched from [`sprint-execute`](../../../skills/sprint-execute/SKILL.md) Operation C (`in_progress → done`) step 6. The skill owns the briefing derivation, the three-way operator choice, and the deferral artefact; `sprint-execute` only fires it after marking the feature `done`. This pairing (a dedicated skill, dispatched in-session from `sprint-execute` per [`sprint/en.md`](../sprint/en.md)) is the reference choice only; the spec stays wiring-agnostic and other consumers remain free to pick a different mechanism.

Portfolio-project mapping for this pair: any feature in `nolte/claude-shared` maps to `portfolioProject: claude-shared` in the blog consumer's portfolio collection. The mapping is declared in the blog consumer's `CLAUDE.md`.

Other consumer pairs adopting this spec carry an analogous annex in the source consumer's `CLAUDE.md` (or equivalent contract document).

## Open questions

- **Trigger from `ready → in_progress` (start-of-work post).** Some posts make more sense when work starts (a "here's the problem I'm taking on" post) than when work finishes. Whether this spec grows a second trigger event for the start-of-work case is open. Triggered by the first operator who asks for it; until then, start-of-work posts are operator-initiated like any other.
- **Sprint-summary trigger.** A sprint-level summary post (one post per sprint, covering all features in that sprint) is a different shape than a per-feature post. Whether this spec grows a `sprint → review` trigger event for sprint summaries—wired to [`sprint-review`](../../../skills/sprint-review/SKILL.md)—is open. The two could compose: a sprint with five features would fire five per-feature triggers (most deferred), and one sprint-summary trigger at sprint close. Deferred until the operator has run at least one full sprint with this spec wired.
## References

Sibling specs (in this plugin):

- [`blog-author/en.md`](../blog-author/en.md)—what the author produces; consumes the briefing this spec derives.
- [`feature/en.md`](../feature/en.md)—the feature record this spec reads.
- [`sprint/en.md`](../sprint/en.md)—the sprint lifecycle whose `feature → done` transition this spec attaches to.
- [`roadmap/en.md`](../roadmap/en.md)—the source of the portfolio-project mapping referenced in §Briefing derivation.

Background:

- [`spec/claude/resumable-work/`](../../claude/resumable-work/en.md)—relevant if the operator chooses Choice 1 or 2 and the resulting `blog-author` invocation needs resume semantics.
- [Trigger skills vs. hooks vs. dispatch]—internal design pattern not yet codified in `spec/claude/`; tracked under §Open questions.

<!-- vale Microsoft.Quotes = YES -->
<!-- vale Microsoft.Contractions = YES -->
<!-- vale Microsoft.Dashes = YES -->
