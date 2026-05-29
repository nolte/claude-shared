# Blog author

Status: draft

<!-- vale Microsoft.Quotes = NO -->
<!-- vale Microsoft.Contractions = NO -->
<!-- vale Microsoft.Dashes = NO -->

## Context

Readers: implementors of the [`blog-author`](../../../skills/blog-author/SKILL.md) skill in the `nolte-shared` plugin (primary), human authors who curate AI-drafted blog posts in a consumer repository that adopts this contract (secondary), and downstream review skills (`lektorat-apply`, `prose-vale-curator`) that consume the post pair this spec produces (tertiary).

A consumer of this spec is a **bilingual personal-blog or technical-blog repository** that adopts the [`post-writing-style`](../post-writing-style/en.md) and [`post-audience-communication`](../post-audience-communication/en.md) sibling specs. The reference consumer is `nolte/blog`; the spec is phrased so other portfolio repositories with the same shape can adopt it without modification (see §Consumer contract and §Reference example annex).

Posts in this class are produced interactively: an operator briefs the topic, an author (a human or the `blog-author` skill drafting via Claude Code) writes an EN post, translates it into DE, and hands the pair off to an editorial layer ([`spec/project/lektorat/`](../lektorat/en.md)). What this workflow does **not** have without this spec is an explicit contract for the **author role itself**: for the **inputs** a post draft needs, the **steps** in which a post takes shape, and the **handover point** at which the post leaves the author and reaches the editor. This spec fills that gap.

Three sibling specs are referenced here, not duplicated:

- [`post-writing-style`](../post-writing-style/en.md) governs voice, readability, typography, forbidden words, and AI-disclosure tone—**how** to write.
- [`post-audience-communication`](../post-audience-communication/en.md) governs primary-audience declaration, audience rubrics, multi-audience layering, Diátaxis positioning, and named-third-party handling—**for whom** to write.
- [`spec/project/audience-identification/`](../audience-identification/en.md) produces the consumer's audience artefact, which both sibling specs (and this spec) read as the authoritative source for audience identifiers and their expectations.

This spec sits **before**: before, because it defines the briefing without which a `post-writing-style`-conformant draft can't exist; and before, because it defines the handover point to the editor, who consumes the sibling specs as the source of per-post acceptance criteria. The spec is deliberately **process- and contract-oriented**: it says **which information flows when and where**, not **which words live in the body**.

## Goals

- Define a **closed list of mandatory briefing inputs** that a post draft needs, so the author (a human or the `blog-author` skill) either produces a complete draft or surfaces an explicit, documented briefing gap—never silently invents a gap.
- Lay out the **workflow from briefing to editor handover** in named, sequential steps, so a skill implementation attaches at exactly the same steps a human attaches to.
- Mandate a **pre-handover self-check** that walks the per-post acceptance criteria from [`post-writing-style`](../post-writing-style/en.md) and [`post-audience-communication`](../post-audience-communication/en.md) as a closed list, so the editor starts with a post that doesn't obviously violate the sibling-spec rules.
- Phrase the **handover contract to the editor** so it integrates with [`spec/project/lektorat/`](../lektorat/en.md) (the editor's contract document) without restating the editor's internal mechanics.
- Bundle the **author's hard MUST-NOT rules** in one place, derived from the consumer's hard rules and from the MUST rules of the two sibling specs—so "what must the author never do" doesn't have to be reconstructed across three files.
- Serve as the **contract document** for the [`blog-author`](../../../skills/blog-author/SKILL.md) skill—the spec is phrased so a skill implementation can adopt the briefing inputs as its input schema, the workflow steps as its interactive phases, and the acceptance criteria as its internal verification one-to-one.

## Non-goals

- Defining **voice, tone, readability, typography, and forbidden words**: that's exhaustively covered by [`post-writing-style`](../post-writing-style/en.md). This spec references that spec's per-post acceptance criteria in the self-check; it doesn't restate them.
- Defining **audience rubrics, primary/secondary audience mechanics, Diátaxis positioning, or named-third-party fairness rules**: that's exhaustively covered by [`post-audience-communication`](../post-audience-communication/en.md). This spec demands the audience declaration as a mandatory briefing input and references that spec's per-post criteria in the self-check.
- Defining the **consumer's frontmatter schema** (key set, required fields, types)—that's declared by the consumer's static-site engine (Astro's Zod content-collection schema, Hugo's archetypes, Eleventy's data cascade) plus the consumer's `CLAUDE.md`. This spec presupposes those fields and points to them.
- Defining the **internal mechanics of the editor** (operations, dimensions, severity classification, JSON report shape)—that belongs to [`spec/project/lektorat/`](../lektorat/en.md). This spec defines only the **handover point** from the author's side.
- Defining **PR shape, commit-message conventions, branching model, or merge gates**: that belongs in [`spec/project/pull-request-workflow/`](../pull-request-workflow/en.md), not here. This spec ends at the editor handover; what follows is governed elsewhere.
- Defining **topic choice, publishing cadence, or corpus mix**: those are roadmap and sprint questions governed by [`spec/project/roadmap/`](../roadmap/en.md) and [`spec/project/sprint/`](../sprint/en.md). This spec applies once a topic has been chosen.
- Defining **the triggering mechanics that cause this skill to run when a feature reaches `done`**: that's the job of [`spec/project/blog-author-trigger/`](../blog-author-trigger/en.md). This spec defines what the author produces; the trigger spec defines when the author is invoked.
- Defining **lint or CI mechanics** that automate the acceptance criteria. The spec is reviewer judgement today; wiring it into `task check` or a downstream skill is open (see §Open questions).

## Consumer contract

A consumer repository adopting this spec **MUST** supply the contract surfaces named in [`post-writing-style`](../post-writing-style/en.md) §Consumer contract and [`post-audience-communication`](../post-audience-communication/en.md) §Consumer audience contract. In addition, this spec requires the following:

- A **post-pair handover surface** that survives a single commit: the EN file, the DE file, and the three delivery-contract artefacts named under §Delivery contract are **all reachable in the same merge commit** (in the commit body, in the PR body, or as referenced files in the diff). Such reachability is the gate; the storage shape is the consumer's choice.
- A **build command** that proves the post pair renders end-to-end (the reference convention is `task build` / `task check`).
- An **editor entry point** that consumes the post pair: today the reference editor is the `lektorat-apply` skill in `nolte-shared` (target state) or `prose-vale-curator` (transitional regime). The consumer **MUST** name which of the two it accepts as the entry point in its `CLAUDE.md` or equivalent.

Where this spec refers to "the EN file", "the DE file", "the cross-language binding key" (reference: `translationKey`), "the AI-disclosure flag" (reference: `aiGenerated: true`), or "the audience identifier set", it refers to the consumer's instances of these concepts under the sibling specs' contracts. The §Reference example annex names the concrete mapping for the `nolte/blog` consumer.

## Requirements

### Briefing inputs

A post draft starts with a **briefing**. The mandatory fields listed below are the closed minimum set; if one is missing, the draft **MUST NOT** start before the gap is either filled or recorded as a documented open question in the briefing (see the "briefing gaps" sub-rule at the end of this section). The optional fields extend the draft; their absence doesn't block it.

#### Mandatory fields

- **MUST** name a **topic** as a one- or two-sentence thesis, phrased as what the post will **state**: not as a keyword. "I describe how the `astro:content` loader validates the frontmatter" passes; "Astro Content Collections" fails.
- **MUST** name **at least one concretely grounded artefact** the post is built on: a repo reference (repo name plus commit SHA or tag), a diff, a command output, a screenshot, a README quote, or an explicit operator briefing. This requirement places the consumer's hard rule "Never invent technical facts about projects" at the workflow entry point—without an artefact, the draft must not start.
- **MUST** name a **primary audience** from the consumer's direct-end-reader-subgroup identifiers (reference: `{A, B, C}`), per [`post-audience-communication`](../post-audience-communication/en.md) §Primary-audience declaration. The named-third-parties identifier (reference: `L`) is never a primary audience; the search-engine / crawler identifier (reference: `M`) is out of scope.
- **MUST** maintain a **sources list** of URLs to primary sources against which every concrete technical claim in the post can be verified (README, release notes, RFC, GitHub issue, source file, operator briefing transcript). The list **MAY** grow as the draft develops; it **MUST NOT** stay empty if the post carries **a single** concrete claim about a named project, library, or tool.
- **MUST** set the **`slug`** in ASCII kebab case, derived from the English title; the slug is stable after publication. Maximum length follows the consumer's slug rule (reference: ≤ 60 characters).
- **MUST** set the **cross-language binding key** (reference: `translationKey`) shared between the EN and DE files of the post pair, per the consumer's contract.

#### Optional fields

- **MAY** declare **secondary audiences** (`secondaryAudiences`) as a list from the consumer's direct-end-reader-subgroup identifiers, excluding the primary value. An empty list signals a deliberately narrow post; a non-empty list triggers the multi-audience-layering requirements from [`post-audience-communication`](../post-audience-communication/en.md) §Multi-audience layering.
- **MAY** declare a **portfolio-project slug** (reference field: `portfolioProject`) if the post binds to an entry in the consumer's portfolio collection; this enables the cross-link expectation from [`post-audience-communication`](../post-audience-communication/en.md) §Portfolio-reviewer rubric ("link to the consumer's portfolio-entry route").
- **MAY** declare a **Diátaxis position** (`explanation`, `how-to`, `blend`) as a briefing hint; the consumer's frontmatter today may carry no such field (see [`post-audience-communication`](../post-audience-communication/en.md) §Open questions—Diátaxis frontmatter signal), but the position shapes the lede and body form and therefore belongs in the briefing.

#### Update vs. new-post fields

- **MUST** carry an **update reason** in the briefing when revising an already-published post: one or two sentences on what has changed and why the update is due now (a bug in the original claim, a new release of the cited library, a better artefact). A cosmetic correction without factual change **MAY** shorten the reason to "correction pass after editor finding `<id>`" or equivalent.
- **MUST** set the frontmatter field **`updatedDate`** to the ISO date of the update, per the consumer's frontmatter convention. The field **MUST NOT** be set silently without the update reason being documented in the briefing.
- **MUST NOT** an update change the **`slug`** or the **cross-language binding key**; that would be a new post under a new identity, per [`post-audience-communication`](../post-audience-communication/en.md) §Primary-audience declaration (write-once contract).
- Note: the **threshold** between update and new post—how large a factual change must be to justify a new post instead of an update—is deliberately **author judgement** and not governed by a hard criterion. A later spec tightening is triggered by a concrete contested case, not prospectively.

#### Named-third-party evidence field

- **MUST** carry, when the planned post characterises a **named third party** (reference audience identifier: `L`), an **evidence list** in the briefing with at least one primary-source citation for every characterisation (URL plus the cited passage, verbatim or with commit SHA / revision pin). This places the MUST from [`post-audience-communication`](../post-audience-communication/en.md) §Named-third-party treatment at the workflow entry point.
- **MUST** carry, for **quotations from private communication** (DMs, private email, closed issue threads, internal Slack), a **consent note** from the source in the briefing—at minimum as a reference to where the consent is recorded (own email reply, shared Slack thread). Without that note the quote **MUST NOT** land in the post.
- **SHOULD** record the **preferred name and capitalisation** of the third party in the briefing (for example `npm` instead of `NPM`, `Astro` instead of `astro`), so the spelling isn't re-researched on every draft.

#### Hero and OG image

- **MAY** plan a **hero / OG image** in the briefing, with a path relative to the consumer's public-asset root (reference: `/public/`) and a **descriptive alt-text proposal**. Hero images are **not** mandatory today.
- **MUST** describe, when a hero / OG image is included in the post, **what's visible in the image** in the alt text—not repeat the caption, and not read "hero image" or `screenshot` (analogous to the screenshot alt-text rule from [`post-writing-style`](../post-writing-style/en.md) §Code, commands, and other technical content).
- **MUST NOT** the post body use a **hero image as a substitute** for an inverted-pyramid lede; the image complements the lede, it doesn't replace it (cf. [`post-writing-style`](../post-writing-style/en.md) §Structure and flow).
- Note: the broader **hero-image policy** for the corpus (mandatory vs. optional, uniform style, generation pipeline) isn't decided; see §Open questions.

#### Briefing gaps

- **MUST** any **briefing gap** be documented explicitly before the draft starts—either as an "open question" in the briefing header, or as an inline marker in the later post body that forces the editor to address the gap before publication.
- **MUST NOT** the author (human or skill) fill a briefing gap **silently** with a plausible-sounding guess; that's exactly the failure mode the consumer's "Never invent technical facts" hard rule rules out.

### Workflow

The workflow is a **linear sequence** of named steps. Later steps presuppose earlier ones; jumping back is allowed, but **MUST NOT** result in a later step silently skipping an earlier one.

- **MUST** **Step 1—receive and clarify the briefing**: the briefing (see §Briefing inputs) is checked against the mandatory fields; gaps are addressed or recorded as explicit open questions. Without a satisfied briefing, the workflow ends here.
- **MUST** **Step 2—write the EN draft**: the English post body is drafted per [`post-writing-style`](../post-writing-style/en.md) and the audience rubric from [`post-audience-communication`](../post-audience-communication/en.md) for the `primaryAudience` named in the briefing. The frontmatter is filled per the consumer's contract, including the AI-disclosure flag (reference: `aiGenerated: true`) for AI-drafted posts.
- **MUST** **Step 3—pre-handover self-check**: the self-check (see §Pre-handover self-check) runs against the EN draft and its frontmatter; findings are fixed **before** step 4 starts.
- **MUST** **Step 4—write the DE translation**: the German post body is created at the consumer's DE post path (reference: `src/content/posts/de/<slug>.md`), with the same filename slug and the same cross-language binding key as the EN file, and identical values for `primaryAudience`, `secondaryAudiences`, `pubDate`, `tags`, `portfolioProject`, and the AI-disclosure flag. The translation follows §Bilingual typography from [`post-writing-style`](../post-writing-style/en.md) and §Bilingual audience symmetry from [`post-audience-communication`](../post-audience-communication/en.md).
- **MUST** **Step 5—pre-handover self-check (second half)**: the self-check runs against the DE draft and the pair invariants (see §Pre-handover self-check, per-pair block).
- **MUST** **Step 6—run the consumer's build command** (reference: `task build` / `task check`). A non-green run blocks the editor handover; the author fixes the build errors and repeats the step.
- **MUST** **Step 7—handover to the editor**, per §Handover to the editor. The author provides **no** own copy-editing mechanics; he hands over a post whose entry conditions the editor's `audit` stage accepts.
- **SHOULD** the author, between steps 2 and 3 (or between 4 and 5), **read the draft aloud** or have TTS read it, per [`post-writing-style`](../post-writing-style/en.md) §Editing pass. This read-aloud is an author duty in that spec; this spec restates it here so it stays visible in the workflow.

### Pre-handover self-check

The self-check is a **closed, walkable list**. Each item is a per-post requirement from a sibling spec or from the consumer's hard rules that the author (human or the `blog-author` skill) actively answers **once** for each of the two language files before editor handover. The self-check **doesn't replace** the editor; it merely ensures the editor starts with a post that doesn't obviously violate the spec rules.

#### Per language file (apply separately for EN and DE)

- **MUST** have walked **every per-post acceptance criterion** from [`post-writing-style`](../post-writing-style/en.md) §Acceptance criteria (a-1 through a-17) and carry no unresolved violation, in so far as the criterion applies to the language file under review (for example the Flesch–Kincaid requirement a-4 is today scoped to the EN body—see that criterion's provisional clause).
- **MUST** have walked **every per-post acceptance criterion** from [`post-audience-communication`](../post-audience-communication/en.md) §Acceptance criteria (a-1 through a-13), under the enforcement-status caveat of that spec for the frontmatter fields `primaryAudience` and `secondaryAudiences` (a-1 / a-2 are author-side conventions until the consumer's static-site schema declares them).
- **MUST** **cross-check every concrete technical claim** about a named project, library, or tool against the sources list kept in the briefing—re-open the cited passage, re-open the cited README at the pinned revision, or re-run the cited command (cf. [`post-writing-style`](../post-writing-style/en.md) §Editing pass).
- **MUST** have run a directed search-and-check for the **forbidden-word list** from [`post-writing-style`](../post-writing-style/en.md) §Forbidden words and phrases on the language file under review; every hit is either replaced or carries a documented override per that spec's §Override procedure.

#### Per pair (apply to the EN + DE pair as a whole)

- **MUST** the **cross-language binding key** be **identical** in both files, and the filename slug is identical in `<slug>.md` on both the EN and the DE side (per the consumer's slug rule).
- **MUST** the frontmatter field **`primaryAudience`** be identical in both files; **`secondaryAudiences`** also identical (per [`post-audience-communication`](../post-audience-communication/en.md) §Bilingual audience symmetry).
- **MUST** the **AI-disclosure flag** (reference: `aiGenerated: true`) be set in both files as long as the post is AI-drafted (per the consumer's hard rule and [`post-writing-style`](../post-writing-style/en.md) §AI-disclosure tone).
- **MUST** the consumer's **build command** (reference: `task build` / `task check`) run green locally against the working tree that contains both files.
- **SHOULD** the author flip the EN ↔ DE pair once via the language switcher in the consumer's development server, so a cross-language binding mismatch or a silent pair break becomes visible (per [`post-writing-style`](../post-writing-style/en.md) §Editing pass).

### Delivery contract

This section names the artefacts to be delivered **in addition** to the post pair itself, so that the editor and any downstream skill find the conditions formulated in §Pre-handover self-check and §Handover to the editor **verifiable**: not merely attested as "the author has checked".

The obligation is **role-conditional**:

- for the **human author**, the artefacts below are **SHOULD**, because a human assembles the evidence in their head and walks the self-check coherently;
- for the **`blog-author` skill** (and any other agentic author), they're **MUST**, because an agent without explicit output evidence can't be distinguished from a non-checking agent.

The form valid today for all three artefacts is Markdown prose (hand-written) or a plain list in the commit body / PR description. A machine-readable form (YAML / JSON, with schema) is deferred as a follow-on step (see §Open questions—"Briefing and delivery contract as YAML schema").

#### Self-check manifest

- **MUST** (for the `blog-author` skill; **SHOULD** for human authors) deliver a status line for every per-post acceptance-criterion ID from the sibling specs that §Pre-handover self-check references, with one of exactly three values:
  - `passed`—the criterion is satisfied;
  - `finding: <short reason>`—the criterion is violated, the finding is described;
  - `override: <reference to §Override procedure in post-writing-style or an analogous justification>`—the violation is documented and accepted.
- **MUST** (for the `blog-author` skill) keep the per-language-file and the per-pair blocks from §Pre-handover self-check separate in the manifest, so that build status, cross-language binding identity, and audience-field identity are visible as their own lines.
- **MAY** the manifest live in the commit body / PR description (a Markdown list is sufficient) or in a separate file beside the post pair (for example `<slug>.selfcheck.md`); the path isn't prescribed, but **reachability together with the post pair in the merge commit** is.

#### Sources-to-claim mapping

- **MUST** (for the `blog-author` skill; **SHOULD** for human authors) map every entry of the briefing's sources list to the concrete post passages it supports—minimally in the form "source <n> supports post paragraph <anchor or heading + sentence number>". Multi-source support is allowed; an unused source is a finding, not a violation.
- **MUST** (for the `blog-author` skill) every **concrete technical claim** about a named project / library / tool reference at least one source; otherwise it carries a `finding` entry in the self-check manifest (violation of §Forbidden practices for the author—"claims without sources").
- **MAY** the mapping be integrated into the self-check manifest or sit beside it as a second list; separate maintenance is allowed, separate readability is mandatory.

#### Handover manifest

- **MUST** (for the `blog-author` skill; **SHOULD** for human authors) a short one- to three-line note name the following fields explicitly:
  - the **chosen handover route** per §Handover to the editor (today: `prose-vale-curator`, self-judgement, or a combination—target state: a run of `lektorat-apply`);
  - the **build status** with the command used (`task build` or `task check`) and the result (`green`);
  - the **repository state** the self-check ran against (branch name plus optional commit SHA), so the editor knows which state it's checking against.
- **MUST** the handover manifest be **visible together with the post pair**: in the commit body, in the PR body, or as a referenced file. A handover done silently without a manifest is a violation of §Handover to the editor (entry conditions).
- **MUST NOT** the manifest claim that a procedure was carried out that wasn't actually executed; a false attestation is a heavier violation than an open `finding` entry.

### Handover to the editor

The **editor** is the downstream copy-editing stage governed by [`spec/project/lektorat/`](../lektorat/en.md). From the author's perspective, the editor is a black box with an `audit` entry stage; what happens inside (five dimensions, severity classification, JSON report shape) is out of scope for this spec. The handover is a **contract point**: the author hands over a post that meets the entry conditions and hands over editorial final responsibility to the editor.

#### Entry conditions for the editor's `audit` stage

- **MUST** the **EN + DE post pair** be present on disk in full, both files with valid frontmatter, identical cross-language binding key, identical slug, and identical audience fields (see §Pre-handover self-check, per pair).
- **MUST** the consumer's **build command** have run green; the editor isn't a build-repair tool, and a post that doesn't build isn't handover-ready.
- **MUST** the **AI-disclosure flag** (reference: `aiGenerated: true`) be set on AI-drafted posts; the editor bases its treatment of the post on this flag (cf. [`post-writing-style`](../post-writing-style/en.md) §AI-disclosure tone).
- **MUST** the **self-check** (see §Pre-handover self-check) be completed; open self-check findings are resolved **before** the handover, not **with** the handover.

#### Task boundary

- **MUST NOT** this spec demand that the blog author know or reproduce the **internal mechanics of the editor** (metrics, thresholds, dimension IDs). The author hands over a post; the editor returns findings. The spec defines the handover point, not the editor operation.
- **MUST NOT** the author attempt to **anticipate editor findings in advance** and thereby re-interpret the sibling-spec rules differently than they're written. The self-check serves the written rules; anything beyond is the editor's job.

#### Handover routes

The author **MUST** apply exactly one of the two routes below at step 7, and **MUST** name the chosen route in the handover manifest (see §Handover manifest) so the route is auditable in the merge commit.

- **Target-state route**: run the `audit` operation from [`lektorat-apply`](../../../skills/lektorat-apply/SKILL.md) over the EN + DE post pair. Every finding of severity **`critical`** is resolved before the post pair is merged (via `patch` operations, via author edits, or via the finding's built-in `skip-and-record` dismissal with a documented reason). The author **SHOULD** address findings of severity **`warning`**, with the right to a documented dismissal in individual cases. Findings of severity **`suggestion`** are optional.
- **Transitional route**: run the `prose-vale-curator` agent from `nolte-shared` over the **English** language file (covers EN Vale mechanics; no DE pipeline) **and** record a documented **reviewer judgement** by the human author against the self-check, explicitly noted as "transitional self copy-edit" in the handover manifest. This route is allowed only while [`spec/project/lektorat/`](../lektorat/en.md) hasn't yet been released for the consumer's adoption.

A consumer **MUST NOT** carry a third route. The transitional route is explicitly time-bounded and is replaced by the target-state route once the consumer signals adoption (by removing the transitional clause from its `CLAUDE.md` or equivalent contract document).

### Forbidden practices for the author

The following rules are the author's hard **MUST-NOT obligations**, bundled from the consumer's hard rules and from MUST rules of the two sibling specs. They're gathered in one place so "what must the author never do" doesn't have to be reconstructed across three files; the sibling specs and the consumer's `CLAUDE.md` remain the authoritative sources.

- **MUST NOT** set a **concrete technical claim** about a named project, library, or tool **without a primary source** in the briefing sources list (consumer hard rule; mirrored in [`post-writing-style`](../post-writing-style/en.md) §AI-disclosure tone).
- **MUST NOT** remove the **AI-disclosure flag** (reference: `aiGenerated: true`) on an AI-drafted post or set it to `false` (consumer hard rule).
- **MUST NOT** publish a post as **DE-only** or **EN-only**; the pair is mandatory (consumer hard rule; mirrored in §Briefing inputs and §Workflow).
- **MUST NOT** rotate the **`primaryAudience` value** after publication to repurpose an underperforming post ([`post-audience-communication`](../post-audience-communication/en.md) §Primary-audience declaration—write-once contract).
- **MUST NOT** quote **private communication** without explicit consent from the source, documented in the briefing's named-third-party evidence field ([`post-audience-communication`](../post-audience-communication/en.md) §Named-third-party treatment; mirrored in §Briefing inputs).
- **MUST NOT** use a word from the **closed forbidden list** in [`post-writing-style`](../post-writing-style/en.md) §Forbidden words and phrases without a documented override in the surrounding prose.
- **MUST NOT** let the **cross-language binding key** differ between the EN and DE files of the same post pair, or let the slug differ between the two languages (consumer slug rule; mirrored in §Pre-handover self-check).

## Acceptance criteria

A post draft satisfies this spec if **all** per-post criteria below hold. Each criterion is phrased so a reviewer (the author, the `blog-author` skill, or the editor itself) can mark it done / not done without ambiguity.

- [ ] **a-1** The briefing carries **all mandatory fields** from §Briefing inputs (topic, at least one grounded artefact, primary audience, sources list, slug, cross-language binding key); missing values are recorded as explicit open questions in the briefing.
- [ ] **a-2** When the post characterises named third parties (reference audience identifier: `L`), the briefing carries a **primary-source citation** for every characterisation in the evidence list and a **consent note** for every quotation from private communication.
- [ ] **a-3** The **EN draft was produced before the DE draft** (step 2 before step 4); the workflow step order is honoured.
- [ ] **a-4** The **pre-handover self-check** (§Pre-handover self-check) has been completed for **both** language files separately plus the pair as a whole; no unresolved finding remains before editor handover.
- [ ] **a-5** The consumer's **build command** (reference: `task build` / `task check`) runs green locally on the working tree that contains both files.
- [ ] **a-6** The EN + DE pair shares an identical cross-language binding key and an identical filename slug; `primaryAudience`, `secondaryAudiences`, `pubDate`, `tags`, `portfolioProject`, and the AI-disclosure flag are identical between the two files.
- [ ] **a-7** On an **update** to an already-published post, `updatedDate` is set **and** the update reason is documented in the briefing; `slug` and the cross-language binding key are unchanged.
- [ ] **a-8** When the post carries a **hero / OG image**, the alt text is descriptive (what's visible in the image) and doesn't repeat the image caption; the image doesn't substitute for the lede.
- [ ] **a-9** The editor handover happens only after the **entry conditions for the `audit` stage** (§Handover to the editor) are satisfied; the chosen handover route (target-state vs. transitional) is named in the handover manifest.
- [ ] **a-10** None of the **hard MUST-NOT rules** from §Forbidden practices for the author is violated; in particular, the AI-disclosure flag is set, no private communication is quoted without consent, no word from the forbidden list is used without override, and the `primaryAudience` value hasn't been rotated after publication.
- [ ] **a-11** For the **`blog-author` skill**: the self-check manifest, the sources-to-claim mapping, and the handover manifest are reachable per §Delivery contract together with the post pair in the merge commit; for a **human author**, at least the handover manifest is visible (chosen handover route, build status, repository state).

## Reference example annex

The reference consumer is the `nolte/blog` repository (a bilingual Astro static blog). It maps the abstract concepts in this spec onto the concrete fields below:

- Post-pair location: EN at `src/content/posts/en/<slug>.md`, DE at `src/content/posts/de/<slug>.md`.
- Cross-language binding key: frontmatter field `translationKey`.
- AI-disclosure flag: frontmatter field `aiGenerated: true`.
- Slug rule: ASCII kebab case, derived from the EN title, ≤ 60 characters, stable post-publish.
- Frontmatter schema source: Astro Zod schema at `src/content.config.ts`.
- Audience artefact: `AUDIENCES.md` at the repository root, with identifiers `A` (technical readers), `B` (portfolio reviewers), `C` (author as future-self), `L` (named third parties), `M` (search engines), `D` (author as site maintainer, out of scope for post body), `E` (Claude Code as AI co-operator, out of scope for post body).
- Author-facing contract document: `CLAUDE.md` at the repository root.
- Build command: `task build` (full) / `task check` (faster variant).
- Portfolio-entry route (for the `B`-rubric cross-link): `/projects/<slug>`.
- Editor entry point: `lektorat-apply` (target state) / `prose-vale-curator` (transitional).

Other consumers adopting this spec carry an analogous annex in their own repository documentation. A consumer **MAY** ship its annex inline in its `CLAUDE.md` rather than as a separate file.

## Open questions

- **Per-consumer adoption of the target-state handover route.** §Handover routes allows either the target-state route (`lektorat-apply`) or the transitional route (`prose-vale-curator` + reviewer judgement). A consumer's adoption signal is "remove the transitional clause from `CLAUDE.md`"—the trigger that flips this spec's contract surface from "two routes" to "one route" is per consumer, not portfolio-wide. Triggered when the first consumer (likely `nolte/blog`) ships the adoption signal.
- **Briefing and delivery contract as YAML schema.** §Briefing inputs and §Delivery contract are prose today, with mandatory-field and mandatory-artefact lists respectively. A machine-readable form for both sides—`project/briefings/<slug>.yml` with schema validation as **input**, `project/handovers/<slug>.yml` (or an embedded frontmatter sub-object) as **output**: would be more convenient for the `blog-author` skill than prose and would make the delivery contract automatically checkable rather than just attestable. Until then the prose form is sufficient on both sides. When the machine-readable form is introduced, the three artefacts named in §Delivery contract (self-check manifest, sources-to-claim mapping, handover manifest) are the natural top-level schemas. Triggered by the second contested handover attestation.
- **Hero-image corpus policy.** The mandatoriness, corpus-wide style, generation pipeline, and layout rendering of the hero-image field are open across consumers. The spec still carries the alt-text rule and the lede-substitution MUST-NOT in §Hero and OG image; the broader policy belongs to a consumer-side roadmap item (the reference consumer tracks this in `project/roadmap.md`).

### Intentionally not open

- **Update-vs-new-post threshold** isn't an open question but a deliberately reactive decision; the threshold is author judgement (see §Briefing inputs, update vs. new-post fields). A concrete contested case would trigger a later spec tightening.
- **Triggering integration is resolved, not open.** The companion spec [`spec/project/blog-author-trigger/`](../blog-author-trigger/en.md) is published; its §Briefing derivation satisfies this spec's §Briefing inputs, and the reference wiring (`sprint-execute` Operation C step 6 → `blog-author-trigger`) is implemented. The standing interface between the two specs remains §Briefing inputs.

## References

Sibling specs (in the same plugin):

- [`post-writing-style/en.md`](../post-writing-style/en.md)—voice, readability, typography, forbidden words, AI-disclosure tone.
- [`post-audience-communication/en.md`](../post-audience-communication/en.md)—primary-audience declaration, audience rubrics, multi-audience layering, Diátaxis, named-third-party handling.
- [`audience-identification/en.md`](../audience-identification/en.md)—methodology that produces the consumer's audience artefact.
- [`lektorat/en.md`](../lektorat/en.md)—the editor's contract document; the handover endpoint named in §Handover to the editor.
- [`blog-author-trigger/en.md`](../blog-author-trigger/en.md)—when the author is invoked (for example, from `sprint-execute` at a `feature → done` transition); produces the briefing this spec consumes.

Background for the workflow style of this spec:

- [Diátaxis project page](https://diataxis.fr/)—the quadrant theory consumed by [`post-audience-communication`](../post-audience-communication/en.md) §Diátaxis positioning; relevant here because the Diátaxis position is an optional briefing field.
- [Inverted Pyramid—Nielsen Norman Group](https://www.nngroup.com/articles/inverted-pyramid/)—the lede form required by both sibling specs; relevant here because the hero-image MUST-NOT prevents the image from substituting the inverted-pyramid lede.
- [Content design: writing for GOV.UK](https://www.gov.uk/guidance/content-design/writing-for-gov-uk)—inspiration for the "inputs—process—handover point" separation this spec adopts structurally.

<!-- vale Microsoft.Quotes = YES -->
<!-- vale Microsoft.Contractions = YES -->
<!-- vale Microsoft.Dashes = YES -->
