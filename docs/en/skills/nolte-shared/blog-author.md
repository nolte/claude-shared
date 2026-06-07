---
title: blog-author
audience: [maintainer]
content_mode: reference
track: developer-docs
last_updated: generated
---

# blog-author

> Drafts a bilingual EN-canonical + DE-translated blog-post pair per this plugin's blog-author specs, writing into a consumer blog repo.

_Drafts a bilingual EN-canonical + DE-translated blog-post pair per this plugin's blog-author, post-writing-style, and post-audience-communication specs. Walks the operator through briefing inputs (topic-as-thesis, grounded artefact, primary audience, source list, slug, cross-language binding key), writes the EN draft, runs the pre-handover self-check, writes the DE translation, runs the per-pair self-check, executes the consumer's build command (reference `task build`), and dispatches [`lektorat-apply`](lektorat-apply.md) for the editorial audit. Invoke when the user asks to "schreibe einen neuen Blogpost", "draft a blog post about X", "neuer Eintrag zu Y", "operationalize blog-author", or equivalent German-language requests. Don't use to lektor an existing post (use [`lektorat-apply`](lektorat-apply.md)), to author portfolio pages (those live in the consumer's portfolio collection), or to redefine the consumer's post-frontmatter schema. Supports resume on re-invocation per `spec/claude/resumable-work/`._

- **Plugin:** `nolte-shared`
- **Phase:** 4 Build (`build`)
- **Tags:** `prose`, `audience`
- **Source:** [skills/blog-author/SKILL.md](https://github.com/nolte/claude-shared/blob/main/skills/blog-author/SKILL.md)

## Use when

- you want to draft a new blog post about a topic
- you want to operationalise the blog-author flow with the briefing inputs
- you want a bilingual post (EN + DE) authored end-to-end with lektorat hand-off

## Don't use when

- **You want to lektor an existing post rather than draft a new one** → [`lektorat-apply`](lektorat-apply.md)

## See also

- [`lektorat-apply`](lektorat-apply.md)

## Referenced by

- [`blog-author-trigger`](blog-author-trigger.md)
- [`lektorat-auto-revise`](lektorat-auto-revise.md)

---

## Blog Author

Operationalises the blog-author contract defined in this plugin's spec corpus and produces post pairs in any consumer repository that adopts the contract. The reference consumer is `nolte/blog`; the same skill works against any consumer that satisfies the §Consumer contract sections of the three load-bearing specs. The skill is the role-and-process layer that produces a bilingual EN-canonical + DE-translated post pair, runs the pre-handover self-check against the two sibling specs, and hands the pair off to the editorial layer via [`lektorat-apply`](lektorat-apply.md).

This skill binds the spec's contract to an on-disk procedure. It does not redefine the rules; when this skill and the specs disagree, the specs win and this skill needs the update. The three load-bearing specs in this plugin are:

- `spec/project/blog-author/` — the seven-step workflow, briefing inputs, pre-handover self-check, delivery contract, handover routes.
- `spec/project/post-writing-style/` — voice, readability thresholds (sentence length 14–20, paragraph ≤ 4 sentences, the cross-language **LIX** corridor on **both** bodies per `spec/project/readability-lix/` — EN aim ≤ 45, DE aim ≤ 50 — plus Flesch–Kincaid 7–10 as a supplementary EN signal), the closed forbidden-words list, bilingual typography (`"…"` EN vs. `„…"` DE, em-dash with spaces, `ä/ö/ü/ß`), AI-disclosure tone.
- `spec/project/post-audience-communication/` — primary-audience declaration (reference: `primaryAudience: A | B | C`), audience-specific rubrics, multi-audience layering, Diataxis positioning, named-third-party fairness.

The companion spec `spec/project/blog-author-trigger/` defines **when** this skill is invoked (e.g., after a `feature → done` transition); this skill defines **what** it produces and how, regardless of trigger source.

### Why this is a skill, not an agent

- **Mid-flow user approval is load-bearing**: the seven-step workflow has multiple operator-approval gates — briefing-gap resolution, EN-draft review before translation, DE-translation review, lektor-handover confirmation. Agents have no stable way to surface that dialogue back to the parent.
- **Externally visible writes**: each run writes at minimum two Markdown files at the consumer's post-pair location plus three delivery-contract artefacts; persistent on-disk state belongs to a skill, not an agent.
- **Orchestration role**: this skill dispatches [`lektorat-apply`](lektorat-apply.md) for the audit step at handover, and may dispatch [`prose-vale-curator`](../../agents/nolte-shared/prose-vale-curator.md) during the transitional regime; the skill-orchestrates pattern (per `spec/claude/skill-vs-agent/`) defaults the orchestrator to skill form.
- **Counter-dimension considered and accepted**: the EN-drafting step alone fits the agent shape cleanly (self-contained briefing input, structured Markdown output, no interactivity). It still lives in this skill because the briefing-clarification, the per-language self-check, and the lektor-handover each need operator dialogue, and consolidating them behind one entry point keeps the operator's mental model coherent. Follows the same precedent as [`lektorat-apply`](lektorat-apply.md).

### German trigger phrases

This skill also triggers on equivalent German-language requests, including:

- "schreibe einen neuen Blogpost"
- "neuer Eintrag zu <Thema>"
- "Briefing für einen Blogpost"
- "operationalisiere blog-author"
- "draft den Post zu <Repo / Thema>"

### User-language policy

Detect the user's language from their message and respond in it. The Markdown files written into the consumer's EN post directory are **always English** (the canonical source language per the consumer's `CLAUDE.md`); the files written into the consumer's DE post directory are **always German**. The delivery-contract artefacts (self-check manifest, source-to-claim mapping, handover manifest) are written in English so downstream tooling and [`lektorat-apply`](lektorat-apply.md) can parse them reliably; prose around the artefacts in the operator dialogue is localised.

The skill never translates user-supplied source quotes — those stay byte-identical in their original language, wrapped in block-quote markers.

### Consumer detection

Before any briefing intake, the skill resolves the consumer's contract surfaces (per `spec/project/blog-author/` §Consumer contract). The minimum it needs to know:

- **Post-pair location**: where to write the EN and DE files (reference: `src/content/posts/{en,de}/<slug>.md` in Astro consumers).
- **Frontmatter contract**: which fields are mandatory, including the cross-language binding key (reference: `translationKey`) and the AI-disclosure flag (reference: `aiGenerated: true`).
- **Audience artefact**: the file (reference: `AUDIENCES.md` at repository root) that defines the consumer's audience identifiers.
- **Build command**: the single canonical command (reference: `task build` / `task check`).
- **Editor entry point**: which of [`lektorat-apply`](lektorat-apply.md) (target state) or [`prose-vale-curator`](../../agents/nolte-shared/prose-vale-curator.md) (transitional) the consumer's `CLAUDE.md` accepts.

The skill resolves these from the consumer repository's `CLAUDE.md` (or equivalent contract document) plus the file-system layout. If a contract surface is missing or ambiguous, stop with a single-sentence operator message naming the missing surface; the operator either points at the surface or amends the consumer's `CLAUDE.md`.

### Inputs

The skill collects every briefing input listed in `spec/project/blog-author/` §Briefing inputs before any draft starts. Required fields gate the workflow; their absence either ends the run or surfaces as a documented open question that the operator confirms.

- **Topic-as-thesis** — one or two sentences naming what the post will assert. A keyword ("Astro Content Collections") fails the gate; an assertion ("I describe how the `astro:content` loader validates frontmatter") passes.
- **At least one grounded artefact** — a repo reference (name plus commit SHA or release tag), a diff, command output, a screenshot, a README citation, or an explicit operator briefing. Without this the run stops per the consumer repository's `Never invent technical facts` hard rule.
- **Primary audience** — exactly one of the consumer's direct-end-reader-subgroup identifiers (reference: `A` technical readers, `B` portfolio reviewers, `C` author as knowledge-base reader). The named-third-parties identifier (reference: `L`) and the search-engine identifier (reference: `M`) are never primary audiences.
- **Source list** — URLs to primary sources against which every concrete technical claim in the post can be verified. The list may grow during drafting; it cannot be empty when the post contains any named-project, named-library, or named-tool claim.
- **Slug** — ASCII kebab-case derived from the English title, stable post-publish, ≤ 60 characters.
- **Cross-language binding key** (reference: `translationKey`) — the cross-language binding contract; identical in both files of the pair.

Optional inputs: `secondaryAudiences` (subset of the consumer's end-reader subgroups, excluding the primary value), `portfolioProject` slug, Diataxis hint (`explanation` / `how-to` / `blend`), hero / OG image path plus descriptive alt text.

Update-vs.-new: when the briefing targets an already-published post, the operator supplies an **update reason** (one or two sentences) and the skill sets `updatedDate` in both frontmatter blocks; `slug` and the cross-language binding key never change in an update.

Named-third-party proof: when the post names a third party (reference audience identifier: `L`), the briefing carries a proof list (primary-source URL plus quoted passage with commit SHA or revision) and, for private-communication quotes, a consent note. Without these the post cannot proceed past the briefing gate. The briefing **SHOULD** also record the third party's **preferred name and capitalisation** (for example `npm` not `NPM`, `Astro` not `astro`) per `spec/project/blog-author/` §Briefing inputs (named-third-party evidence field), so the spelling isn't re-researched on every draft.

### Operations

#### 1. `run`

The skill exposes a single operation that walks the seven-step workflow from `spec/project/blog-author/` §Workflow in order. Each step is gated by the spec's per-step `MUST` rules; a step that fails its gate either repairs itself in place or stops the run with a single-sentence operator message naming the gate.

1. **Step 1 — Intake the briefing.** Resolve every required field listed under §Inputs against the operator's message. For each missing field, prompt the operator with the field name, its spec rationale (citing the specific bullet in `spec/project/blog-author/` §Briefing inputs), and the smallest acceptable answer shape. Record gaps that the operator explicitly defers as open questions in the briefing head; never fill a gap with a plausible-sounding guess.
2. **Step 2 — Write the EN draft** at the consumer's EN post location. Populate frontmatter per the consumer's contract (title, description, pubDate, lang: en, the cross-language binding key, tags, draft: false, the AI-disclosure flag set to `true`); shape the body to the primary-audience rubric in `spec/project/post-audience-communication/` (`A` artefact-first, `B` six-second signal in the lede, `C` Why-of-every-decision) and the voice / readability rules in `spec/project/post-writing-style/`. Surface the draft to the operator for first-pass review before proceeding.
3. **Step 3 — Pre-handover self-check on the EN draft.** Before walking the criteria, **read the draft aloud** or have TTS read it back, per `spec/project/blog-author/` §Workflow (the SHOULD read-aloud author duty restated from `spec/project/post-writing-style/` §Editing pass); this surfaces clumsy phrasing the silent eye skips. Then walk every per-post acceptance criterion in `spec/project/post-writing-style/` §Acceptance criteria (a-1 through a-17, including the cross-language LIX criterion **a-4a** checked on the EN body here — EN aim ≤ 45 per `spec/project/readability-lix/` — and scoped to EN where the criterion is EN-only) and in `spec/project/post-audience-communication/` §Acceptance criteria (a-1 through a-13). For each criterion, record one of `passed`, `finding: <reason>`, or `override: <reference to §Override procedure>` in the self-check manifest (see §Outputs). Repair any unhandled finding before Step 4; the spec forbids leaving them for the lektor.
4. **Step 4 — Write the DE translation** at the consumer's DE post location. Same filename slug, same cross-language binding key, identical `primaryAudience`, `secondaryAudiences`, `pubDate`, `tags`, `portfolioProject`, and AI-disclosure-flag values. The translation follows §Bilingual typography in `post-writing-style` (German quotes `„…"`, em-dash with spaces, no ASCII substitutes for `ä/ö/ü/ß`, technical identifiers byte-identical) and §Bilingual audience symmetry in `post-audience-communication` (idiom-for-idiom not word-for-word; audience targeting identical across the pair).
5. **Step 5 — Pre-handover self-check on the DE draft and the pair.** Read the DE draft aloud (or via TTS) the same way as the EN draft in Step 3, per `spec/project/blog-author/` §Workflow. Run the DE-half of the per-language criteria (including **a-4a** LIX on the DE body — DE aim ≤ 50, the higher German offset per `spec/project/readability-lix/`), then the per-pair block: cross-language binding key identical, file-slug identical, audience fields identical, AI-disclosure flag set in both, build command ready to run. As part of the per-pair block, **SHOULD** flip the EN ↔ DE pair once via the language switcher in the consumer's development server, per `spec/project/blog-author/` §Pre-handover self-check (per pair), so a cross-language binding mismatch or a silent pair break becomes visible. Repair findings before Step 6.
6. **Step 6 — Run the consumer's build command locally** in the consumer repo root. A green build is the gate to Step 7; a red build is repaired in place and the step re-runs. The skill never proceeds to handover with a red build.
7. **Step 7 — Hand off to the lektor** by dispatching the `nolte-shared:lektorat-apply` skill with operation `audit` over the EN+DE post pair. The skill **does not** re-implement editorial mechanics; it consumes [`lektorat-apply`](lektorat-apply.md)'s findings inventory. `critical` findings are repaired before the post pair lands in a commit; `warning` findings are addressed with documented dismissal rights; `suggestion` findings are optional.

The operation is resumable across all seven steps; see §Resumability for the checkpoint cadence.

### Outputs

Every run produces, at minimum, the post pair plus three delivery-contract artefacts. The post pair lands at the consumer's post-pair location; the delivery artefacts land alongside, written in English so [`lektorat-apply`](lektorat-apply.md) and any downstream skill can parse them.

For an Astro consumer (reference: `nolte/blog`), the layout is:

```
<consumer-repo>/
├── src/content/posts/
│   ├── en/<slug>.md         # EN-canonical post
│   └── de/<slug>.md         # DE translation, same cross-language binding key
└── project/handovers/<slug>.md   # delivery contract: the three artefacts below
```

The three delivery artefacts are required (`MUST`) when this skill writes them — the spec calls the skill an "agentic author" and §Delivery contract promotes them to `MUST` for that case:

- **Self-check manifest** — one status line per acceptance-criterion ID from the two sibling specs (`a-1`…`a-17` for `post-writing-style`, `a-1`…`a-13` for `post-audience-communication`), with value `passed`, `finding: <reason>`, or `override: <reference>`. Per-language block (EN + DE) and per-pair block kept separate so build status, cross-language binding identity, and audience-field identity show as their own lines.
- **Source-to-claim mapping** — every entry of the briefing source list mapped to the concrete post passage it supports (heading anchor + sentence number). Multi-source citation is allowed; an unused source is a `finding`, not a violation. Every named-project / named-library / named-tool claim in the post points at ≥ 1 source.
- **Handover manifest** — three lines naming (a) the chosen handover route (target-state via [`lektorat-apply`](lektorat-apply.md) or transitional via [`prose-vale-curator`](../../agents/nolte-shared/prose-vale-curator.md) + reviewer judgement), (b) the build status and the command used, (c) the repository state (branch name, optional commit SHA) the self-check ran against.

The skill writes all three under the consumer's handover-artefact path (reference: `project/handovers/<slug>.md`) as a single Markdown file with three top-level headings, one per artefact; the path is part of the merge-commit so [`lektorat-apply`](lektorat-apply.md) and any reviewer can read them together with the post pair.

### Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/blog-author/<run-id>.yml` after every successful operator-approval gate and after each named workflow step boundary (briefing-intake, en-drafted, en-selfcheck-passed, de-drafted, de-selfcheck-passed, build-green, lektor-dispatched). On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation (matching key: `slug` plus cross-language binding key); if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope (`schema_version`, `run_id`, `inputs`, `phase`, `decisions[]`, `status`, ...) and the fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

### Hard rules

- Never publish a post in only one language. The EN + DE pair is the unit; a DE-only or EN-only file is a consumer-hard-rule violation and the skill refuses to commit the run.
- Never write the DE file before the EN file. EN is the canonical source language per the consumer's `CLAUDE.md`; the workflow steps 2 → 4 are not reorderable.
- Never remove or flip the AI-disclosure flag (reference: `aiGenerated: true`) on a post drafted by this skill. The flag is a consumer hard rule and a `post-writing-style` §AI-disclosure tone invariant.
- Never let the cross-language binding key differ between the EN and the DE file of the same pair; never let the file slug differ between the EN and DE sides.
- Never invent a technical claim about a named project, library, or tool. Every such claim cites a source listed in the briefing source list and re-verified during the self-check (consumer hard rule, `post-writing-style` §AI-disclosure tone, `post-audience-communication` §Named-third-party treatment).
- Never quote private communication (DMs, private email, closed-issue threads, internal Slack) without an explicit consent note in the briefing's named-third-party proof list.
- Never rotate `primaryAudience` after a post is published; `secondaryAudiences` similarly. Both fields are write-once per `post-audience-communication` §Primary-audience declaration.
- Never proceed to lektor handover with a red build. The lektor is not a build-repair tool.
- Never re-implement editorial mechanics in this skill. The five quality dimensions (D1–D5), the three operations (`audit` / `patch` / `revise`), the severity floor, and the language-resolution chain live in `spec/project/lektorat/` and are owned by [`lektorat-apply`](lektorat-apply.md).
- Never define the consumer's post-frontmatter schema in this skill. The schema lives in the consumer's static-site engine configuration (reference: `src/content.config.ts` for Astro consumers); the skill consumes it and refuses to invent new fields.
- When this skill and one of the three load-bearing specs disagree, the spec wins and this skill needs the update. Propose the change as a PR against this plugin's spec corpus, never silently diverge.

### Gotchas

- **The `primaryAudience` / `secondaryAudiences` frontmatter fields may not yet be declared in the consumer's static-site schema.** `post-audience-communication` §Acceptance criteria notes the open question explicitly: until the consumer's schema declares them, `a-1` and `a-2` are author-side conventions that the build does not enforce. The skill still writes the fields (the spec's `MUST` greets author-side compliance regardless of build enforcement); a future schema migration will retroactively validate them. Don't drop the fields because the build accepts their absence today.
- **The lektor transitional regime is still alive in the spec.** `spec/project/blog-author/` §Handover routes allows either [`prose-vale-curator`](../../agents/nolte-shared/prose-vale-curator.md) over the EN file or a documented author self-review, until the consumer signals adoption of the target-state route. This skill defaults to the target-state path (dispatching [`lektorat-apply`](lektorat-apply.md)) because the skill exists and is operational; record the chosen route in the handover manifest so the route is auditable in the merge commit.
- **`task build` and `task check` are not interchangeable.** In Astro consumers, `task check` runs the content-schema validation only and is the cheaper gate; `task build` runs the full production build. The spec accepts either at Step 6, but a green `task check` does not guarantee a green `task build`. Default to `task build` for the actual handover gate; `task check` is acceptable as a mid-draft sanity ping.
- **The forbidden-words list lives in `post-writing-style`, not in this skill.** Don't hard-code the list here; the spec maintains it under §Forbidden words and phrases with documented add/remove rules and a re-review cadence per Claude model family. The skill grep-searches against the spec's current list at self-check time, not against a frozen copy.
- **Sentence-case headings are the rule even when the EN source title uses Title Case in references.** `post-writing-style` §Headings is unambiguous: H1 through H6 are sentence case in both EN and DE. A README cited in the source list that uses Title Case stays Title Case in the block quote; the post's own headings do not.
- **Don't draft the post into the consumer's DE post directory directly when the briefing targets EN only.** A DE-only briefing is a spec violation per the consumer's "EN is the source language" hard rule. The skill stops the run and surfaces the EN-first requirement; the operator may rebrief in EN, but the skill never silently inverts the language order.
- **The language-switcher flip in Step 5 needs the consumer's dev server running.** The per-pair SHOULD check (`spec/project/blog-author/` §Pre-handover self-check, per pair) wants the operator to flip EN ↔ DE once in the running development server so a binding-key mismatch or a silent pair break shows up; a green `task build` alone does not exercise the switcher. When no dev server is available, record the flip as a documented `finding` / deferral in the self-check manifest rather than silently skipping it.
- **The skill does not commit, push, or open a PR.** It writes files into the working tree and surfaces a follow-up hint pointing at `nolte-shared:pull-request-create`. Staging, committing, and PR creation stay the operator's call.

### Multi-model testing

The workflow steps and the self-check loop are expected to work on Claude Sonnet (default), Opus (long EN/DE pairs with heavy bilingual typography), and Haiku (briefing-intake-only or single-step re-runs). The [`lektorat-apply`](lektorat-apply.md) dispatch at Step 7 carries its own model pin per its frontmatter; this skill does not override it.
