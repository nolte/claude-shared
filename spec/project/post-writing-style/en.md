# Post writing style

Status: draft

<!-- vale Microsoft.Quotes = NO -->
<!-- vale Microsoft.Contractions = NO -->
<!-- vale Microsoft.Dashes = NO -->

## Context

Readers: implementors of the [`blog-author`](../blog-author/en.md) skill in the `nolte-shared` plugin (primary), and human authors who curate AI-drafted blog posts in any consumer repository that adopts this spec (secondary). Familiarity with [`spec/project/audience-identification/`](../audience-identification/en.md) (which produces the consumer's audience artefact) and the sibling [`post-audience-communication`](../post-audience-communication/en.md) (which decides whom to write for) is assumed; terms drawn from those specs are used without restatement.

A consumer of this spec is a **bilingual personal-blog or technical-blog repository** with an EN-canonical / DE-translated post pair contract, a static-site renderer (Astro, Hugo, Eleventy, MkDocs in `blog` mode, or equivalent), and an author profile that alternates between hand-writing posts and curating AI-drafted output. The reference consumer is `nolte/blog`; the spec is phrased so other portfolio repositories with the same shape can adopt it without modification (see §Consumer contract and §Reference example annex).

This spec **extends and operationalises** the consumer's own author-facing voice rules with research-grounded thresholds, an explicit forbidden-word inventory, bilingual-typography conventions, and lifecycle gates a lint or human reviewer can run against. Where the consumer's repository-level rules (its `CLAUDE.md`, its style guide, its README) carry a short voice line, this spec is the operative layer behind it.

Style decisions on this class of blog have a second-order property: because posts are drafted by an LLM, AI-tell vocabulary (`delve`, `tapestry`, `leverage`, `robust`, `seamless`) is the dominant failure mode rather than the formality drift typical of corporate blogs. The spec leans heavily into AI-tell suppression for that reason, and into `show-your-work` patterns that are hard for a generic LLM to fake—both of which directly serve a consumer's value of grounded, source-cited, project-derived posts.

## Goals

- Establish a single source of truth for **voice, tone, structure, formatting, readability, and typography** across every post pair (EN + DE) so the bilingual surface stays internally consistent and a `blog-author` skill (or a human curator) can draft against a stable contract.
- Pin **measurable thresholds** (sentence length averages, paragraph length, Flesch–Kincaid grade target, active-voice ratio target, heading depth) so style conformance is reviewable, not a matter of taste.
- Maintain a **closed-vocabulary "forbidden words" list** captured in this spec, derived from documented AI-tells, plain-language research, and observed failure modes, so additions and removals are auditable rather than invented per post.
- Mandate **AI-disclosure tone**: how a post phrases the fact that it was AI-drafted—separately from the consumer's frontmatter disclosure flag, so the textual signal and the structured signal stay aligned.
- Codify **bilingual typography rules** (quotation marks, em-dash, ß / umlauts, technical-identifier preservation) so the EN ↔ DE pair is typographically idiomatic on each side rather than a verbatim transliteration.
- Stay **personal-blog-scoped**: every requirement applies to a Markdown post produced by a consumer that adopts this spec. Project READMEs, ADRs, spec files, and PR descriptions are out of scope (those are covered by [`spec/project/prose-style/`](../prose-style/en.md) and [`spec/project/lektorat/`](../lektorat/en.md)).

## Non-Goals

- Defining **what topics** a post should cover, **which projects** to write about, or **how often** to publish—those are roadmap- and sprint-level concerns owned by [`spec/project/roadmap/`](../roadmap/en.md) and [`spec/project/sprint/`](../sprint/en.md).
- Defining the **audience analysis** itself. Audiences and their criticality are owned by the consumer's audience artefact (per [`spec/project/audience-identification/`](../audience-identification/en.md)). The sibling [`post-audience-communication`](../post-audience-communication/en.md) spec defines **how to address those audiences** in a single post; this spec defines **how to write** regardless of which audience a given post leans toward.
- Defining the **consumer's frontmatter schema**. Frontmatter shape (required fields, validation, types) is declared by the consumer's static-site engine (for example, Astro's Zod content-collection schema, Hugo's archetypes, Eleventy's data cascade) plus the consumer's `CLAUDE.md` or equivalent. This spec assumes the contract documented under §Consumer contract is satisfied and refers to its fields by their conventional names.
- Defining **SEO metadata, sitemap, OG images, RSS shape, or LLM-crawler stance**. Those serve audience M (search engines and LLM trainers) and are governed by the consumer's metadata or robots-policy spec, not here.
- Replacing **MkDocs / docs-tracks specs**. Those govern docs-site content with audience tracks; this spec governs the personal-blog corpus, where every post serves the same end-reader track.
- Defining **review workflow / merge gates**. PR review process belongs to [`spec/project/pull-request-workflow/`](../pull-request-workflow/en.md), not here. This spec defines what the post itself must look like, not how it gets to `main`.
- Defining **editorial review mechanics** (per-dimension findings, severity classification, JSON report shape). Those are owned by [`spec/project/lektorat/`](../lektorat/en.md); this spec defines what a post handed to the editor must look like, not what the editor does.

## Consumer contract

A consumer repository adopting this spec **MUST** supply the following—these are preconditions, not requirements this spec invents:

- A **post-pair location convention**: one canonical-language file and one translation file per post, sharing a stable cross-language binding key. The reference convention is `src/content/posts/{en,de}/<slug>.md` plus a `translationKey` frontmatter field; equivalent conventions in other engines are acceptable.
- A **frontmatter contract** that declares at minimum: `title`, `pubDate`, `lang` (or equivalent language tag), the cross-language binding key, `tags`, a draft flag, and an **AI-disclosure flag** (the reference name is `aiGenerated: true`; equivalent names are acceptable as long as the consumer's contract is unambiguous).
- An **audience artefact** produced via [`spec/project/audience-identification/`](../audience-identification/en.md), with at least one direct end-reader audience and at least one peripheral audience for named third parties (the reference consumer names these `A`/`B`/`C` for end-reader subgroups and `L` for third parties; equivalent labels are acceptable).
- A **build command** that renders the post pair end-to-end (the reference convention is `task build` / `task check` per [`spec/project/quality-gate/`](../quality-gate/en.md); other Taskfile targets or direct invocations are acceptable as long as a single command is canonical).
- A **slug convention**: ASCII kebab-case, derived from the EN title, stable post-publish, ≤ 60 characters—declared in the consumer's `CLAUDE.md` or equivalent.

Where this spec refers to a "post body", a "post pair", a "frontmatter field `aiGenerated`", or an "audience-L characterisation", it refers to the consumer's instance of these concepts under the contract above. The §Reference example annex names the concrete mapping for the `nolte/blog` consumer; other consumers carry an analogous annex in their own repository.

## Requirements

### Person, voice, and tone

- **MUST** write in the first person singular ("I"). Plural `we` is permitted only when the post explicitly speaks for a multi-person collaboration that exists in fact—never as a corporate plural masking a solo voice.
- **MUST** position the post on the four NN/g tone-of-voice dimensions (humour, formality, respectfulness, enthusiasm) at: serious-leaning-with-occasional-dryness, casual, respectful, matter-of-fact. Bursts of enthusiasm are allowed when something genuinely surprised the author; sustained enthusiastic register is **MUST NOT**.
- **MUST** read as a knowledgeable peer talking to a peer, not as documentation, not as a corporate post, not as a tutorial that begins with "In today's fast-paced world…". "Show the thinking, not just the conclusion": when a decision was hard, the post **MUST** say what made it hard before saying what was chosen.
- **MUST** prefer contractions ("it's", "you'll", "don't", "I've") in EN posts; expanding contractions reads as corporate or LLM-default and is treated as a style violation. The DE counterpart uses the natural German equivalents—no forced colloquialisms.
- **MUST NOT** open with a hook that flatters the topic or the reader ("In an era of rapid change…", "Developers everywhere are facing…"). Open with a concrete artefact (a fragment of code, a screenshot, a one-sentence claim, a specific question the post answers).
- **SHOULD** keep humour dry and rare. Self-deprecating asides at the author's expense are fine; the treatment of jokes about named third parties is governed exclusively by [§Audience-L safety](#audience-l-safety)—this section doesn't re-state the rule.

### Readability thresholds

- **MUST** keep the average sentence length in the post body between **14 and 20 words** (American Press Institute comprehension data: ≥ 90 % at 14 words, drops sharply above 25). Individual sentences **MAY** exceed 30 words when a single long sentence serves rhythm or precision, but never two in a row.
- **MUST** keep body paragraphs to **at most 4 sentences** (gov.uk research: people read 20–28 % of text on a page; long paragraphs amplify drop-off). One-sentence paragraphs are explicitly allowed when they carry a beat.
- **MUST** target Flesch–Kincaid Grade Level between **7 and 10** for the EN body excluding code blocks and frontmatter. Posts that drop below 7 read childish; posts above 10 lose readers who skim the post for a fast portfolio signal.
- **MUST** prefer active voice. The rule of thumb: if a passive sentence's grammatical subject is missing or "by the system / by the framework / by the user", rewrite to active. Passive is acceptable for sentences where the actor is genuinely unknown or where the object is the topic and the actor is incidental.
- **SHOULD** target a measured active-voice ratio of ≥ 70 % over the post body. The ratio is a target, not a hard gate, because some technical descriptions read more naturally in passive (for example, "the request is signed with HMAC-SHA256").

### Structure and flow

- **MUST** lead with an inverted-pyramid opening: the first paragraph **MUST** make the post's claim, scope, or question concrete in ≤ 80 words so an F-pattern skimmer can decide whether to keep reading.
- **MUST** carry a scannable subhead hierarchy. Every post longer than 600 words **MUST** have at least two H2 sub-heads; every section longer than ~ 400 words **SHOULD** carry at least one H3.
- **MUST NOT** use a "TL;DR" block as a substitute for an inverted-pyramid opening. If a TL;DR is genuinely the right shape (for example, a long technical post that lays out a multi-step argument), it **MAY** appear as the first block under the H1, but it **MUST** still read as one paragraph and **MUST NOT** be a bullet dump.
- **MUST** "show the work": when the post claims an outcome (a refactor, a decision, a measurement), it **MUST** carry at least one of (a) the diff, (b) the command output, (c) the screenshot, or (d) a verbatim quote / reference. Unsubstantiated outcome claims are a violation, since they're the failure mode this class of blog explicitly rejects per the consumer's "Never invent technical facts" hard rule.
- **SHOULD** close with a short coda that names what the author is uncertain about, what's intentionally out of scope, or what a follow-up post would cover. This serves the future-self knowledge-base audience more than peer-technical or portfolio-reviewer audiences, but doesn't cost the others anything because it's short.

### Headings

- **MUST** use **sentence case** for every heading (H1 through H6). First word capitalised, proper nouns capitalised, everything else lowercase. This aligns with Google Material, Apple HIG, and Microsoft Fluent guidance.
- **MUST** carry exactly one H1 per post—the post title—supplied by the post's frontmatter `title` via the consumer's layout. The body Markdown **MUST NOT** declare an additional H1.
- **MUST** nest headings sequentially. H1 is followed by H2 (never H3). H2 may be followed by H2 or H3, never H4. Skipping levels going deeper fails WCAG 1.3.1 (heading-order). Skipping levels going up (for example, H3 closing back to H2) is permitted.
- **MUST** keep heading text descriptive of the section content, not cute. "Picking a state library" is a valid heading; "The journey begins" isn't.
- **SHOULD** keep heading length under 60 characters so it renders cleanly in the in-page table of contents and the OG card derivative.

### Code, commands, and other technical content

- **MUST** declare a language identifier on every fenced code block. The accepted identifiers depend on the consumer's syntax-highlighter (Shiki, Prism, highlight.js); common ones are `ts`, `tsx`, `js`, `jsx`, `astro`, `bash`, `zsh`, `json`, `yaml`, `toml`, `html`, `css`, `md`, `mdx`, `diff`, `python`, `go`, `rust`. For pure output (no syntax to highlight), use `text` rather than leaving the identifier empty.
- **MUST** keep individual code lines ≤ 100 characters where reasonably possible. Wrap or refactor longer lines for readability inside the post even when the original source has them longer; cite the original location in surrounding prose.
- **MUST** separate code blocks from surrounding prose with a blank line on each side.
- **MUST** describe what the code does in surrounding prose **before** the block (set-up) and **after** the block when the output matters (interpretation). Code blocks are never the whole argument; they support it.
- **SHOULD** use inline code (single backticks) for short identifiers, file paths, CLI flags, and config-key references inside running text. Italic / bold formatting **MUST NOT** be used as a substitute for code formatting on identifiers.
- **MUST NOT** use screenshots of code as a substitute for fenced code blocks—screenshots aren't searchable, are inaccessible to screen readers, and break copy-paste. Screenshots are allowed only for UI states that can't be conveyed otherwise (a styling result, a layout, a chart).
- **SHOULD** label screenshots with descriptive alt text in the Markdown image syntax. The text **MUST NOT** repeat the caption or be `screenshot`—it **MUST** describe what's in the image so screen-reader users get the information.

### Links

- **MUST** make link text describe the link's destination on its own (WCAG 2.4.4 Link Purpose, Level A). "[the Astro content collection docs]" passes; "[click here]" or "[here]" fails.
- **MUST** prefer linking to the **primary source** over an aggregator. The W3C draft, the GitHub issue, the original paper, the upstream README—not a commentary or a content-farm summary.
- **MUST** use absolute URLs for external links. Internal cross-post links **MUST** use the relative slug-based URL the consumer's router exposes (no hard-coded `https://…` for own content).
- **SHOULD** link sparingly—every link is a context switch for the reader. A link earns its place by adding precision (a defined-term reference, a primary source citation, a deep-dive escape hatch), not by reflex.
- **MUST NOT** open external links in a new tab by default. Forced `target="_blank"` violates user-agency expectations; if a link genuinely must open new (for example, it interrupts a long workflow), say so in prose.

### AI-disclosure tone

- **MUST** keep the consumer's AI-disclosure frontmatter flag (the reference name is `aiGenerated: true`) set on every AI-drafted post; removing this flag is forbidden per the consumer's `CLAUDE.md` and re-iterated here as a style invariant because the **textual tone** depends on the flag being honest. Removing the flag while leaving the tone unchanged would deceive the post's reader and any named third party.
- **MUST NOT** wrap the post in an apologetic framing about being AI-drafted ("This was written with Claude, please be lenient…"). Direct end-reader audiences expect AI-drafted content to meet the same standard as hand-written content. The disclosure is structural—today via the AI-disclosure frontmatter flag; consumers that ship a visible per-post AI-disclosure badge (linking to an About-page explanation) make that badge part of the disclosure structure. The MUST is in force on the frontmatter flag today; the badge half becomes verifiable per the consumer's own roadmap signal.
- **MUST NOT** claim the post is hand-written when it's AI-drafted, including indirect claims via first-person memory framings ("when I sat down to write this…") that imply the keystrokes were the author's. Acceptable: first-person framings about decisions, opinions, and verifications the author actually made.
- **MUST** ground every concrete technical claim (a project does X, a library behaves Y, a tool emits Z) in a verifiable source—source code, README, release notes, command output, or an explicit user briefing—per the consumer's hard rule against inventing technical facts. Where the claim is the author's own opinion or experience, that **SHOULD** be signalled with phrasing like "I found that…", "in my use of X, …", not stated as an external fact.
- **SHOULD** position the AI-drafted-human-curated framing as a working method, not a novelty. The blog as a whole declares the workflow via its About page (or equivalent disclosure surface); individual posts don't need to re-explain it.

### Bilingual typography

- **MUST** preserve every **technical identifier** (function name, file path, CLI flag, package name, env var, branch name, error string, frontmatter key) unchanged between EN and DE. Translation operates on natural-language prose only.
- **MUST** use straight ASCII double quotes `"…"` in **EN posts** (the rendering convention is plain ASCII, matching the consumer's typography rule). Single quotes `'…'` for nested cases or contractions.
- **MUST** use German quotation marks `„…"` in **DE posts** (nine-below opener, six-above closer, per Duden). Guillemets `»…«` are an acceptable alternative for one stylistic exception (block quotes set off visually) but **MUST NOT** be mixed with `„…"` in the same post.
- **MUST** use the em-dash with surrounding spaces—like this—in **both EN and DE** prose (aligns with Duden's `Gedankenstrich mit Spatien` convention). The en-dash `–` is reserved for numeric ranges (`pages 12–15`, `2020–2024`); never use it as a thought-pause separator.
- **MUST** use proper German diacritics in DE posts: `ä` `ö` `ü` `ß`. ASCII substitutes (`ae`, `oe`, `ue`, `ss`) are **MUST NOT** in the post body. Slug fields **MUST** keep the EN slug (per the consumer's slug rule) so URLs stay ASCII regardless of the body language.
- **MUST NOT** render an EN idiom ("low-hanging fruit", `back-of-the-envelope`, "the elephant in the room") word-for-word in DE; the translator picks an equivalent German idiom or rewrites the sentence. The reverse direction is symmetric: a rare DE idiom on the DE side is rewritten on the EN side rather than translated literally.
- **SHOULD** translate so the post reads as if it were originally written in the target language—sentence rhythm, paragraph beats, and cultural references adjusted, not just vocabulary substituted.
- **MUST** keep the **cross-language binding invariant**: the EN file and the DE file share one cross-language binding key (`translationKey` or its equivalent) and one filename slug, per the consumer's contract. Style violations on one side that depend on the language (for example, a DE-only `„` placement) **MUST NOT** propagate as edits to the other side.

### Forbidden words and phrases

This is the **closed list** of words and phrases that **MUST NOT** appear in the post body without an explicit override. Inline code, direct quotes, and proper-noun product names (for example, a library actually called `Seamless.js`) are exempt; everything else is in scope.

#### Hype words

- `leverage` (use `use`)
- `delve` (use "go into", "look at", "dig into")
- `robust` (use a concrete property—"handles invalid input without crashing", "tested across X cases")
- `seamless` (delete, or replace with what's actually happening: "no manual step", "single command")

#### AI-tell additions (research-derived; documented across multiple sources cited under §References)

- `utilize` (use `use`)
- `harness` (use `use` or `tap`)
- `streamline` (use a concrete description—"skips the dry-run step", "halves the round-trips")
- `underscore` (use `highlights`, `shows`, or restructure to a noun)
- `pivotal` (use `central` or `important`)
- `cutting-edge` (delete; or name the specific version / capability)
- `innovative` (delete; describe the novelty concretely)
- `tapestry`, `realm`, `landscape`, `synergy`, `testament`, `underpinnings` (delete; rewrite the sentence)
- `It's worth noting that…`, `It's important to note that…`, `In conclusion`, `In summary` (delete the wrapper; keep the actual point)
- `In today's fast-paced …`, `In an era of …`, `As we navigate the …` (delete; open on the concrete claim)
- `Whether you're a … or a …` (drop the audience-flattering wrapper)

#### Corporate-speak / sales register

- `synergies`, `holistic`, `best-in-class`, `world-class`, `industry-leading`, `enterprise-grade`, `mission-critical`, `next-gen`
- `unlocks`, `empowers`, `accelerates`, `transforms`, `revolutionises`, `disrupts` (as transitive verbs about technology)

#### LLM-emphasis tics

- Sentences that begin "**It's** [adjective] **that**…" or "**It's** [adjective] **to**…"—restructure into a direct claim.
- Sentences that end with "…and that's a **good thing** / **bad thing**."—restructure into the specific reason.

#### Override procedure

- A specific word on the closed list **MAY** be retained in a single post when a documented reason applies (verbatim quote, named product, ironic use clearly framed as such). The post body **MUST** make the override visible in surrounding prose ("…the docs call this a 'seamless' integration, which …") rather than silently violating the list.

#### List maintenance

The list above is the spec's authoritative inventory. Changes to it aren't per-post events; they're spec-level changes governed by the rules below.

- **MUST** carry a source citation in the spec diff for any **addition** to any sub-list (Hype words, AI-tell additions, Corporate-speak, LLM-emphasis tics). Acceptable sources are documented AI-tell catalogues, plain-language style guides, or a recorded incident in a consumer repository where the word produced a known failure mode; the citation belongs in the commit message that introduces the addition, not necessarily in the spec body.
- **MUST** carry a one-line rationale in the spec diff for any **removal** from a sub-list (for example, "word entered everyday neutral usage; promoted off the list as of 2026-Qx").
- **MUST** re-review the entire list at every Claude model-family transition (for example, Claude 4.x → 5.x); the re-review is recorded as a continuous-improvement entry or a dedicated commit, not silently elided.
- **SHOULD** version the list implicitly via the spec's `Status:` line plus git history—no `version:` field is added; the audit trail lives in `git log -- spec/project/post-writing-style/`.

### Editing pass (pre-publish)

The requirements in this section govern the **author's pre-publish responsibilities** on a working copy of the post. A downstream lint skill or automated reviewer **MAY** check the items that have a corresponding Acceptance Criterion (see §Acceptance criteria—`a-2`, `a-3`, `a-4`, `a-9`, `a-14`, `a-15`, `a-16`); the remaining items in this section are human-author obligations that no current tool can verify and that the §Non-Goals "review workflow / merge gates" exclusion doesn't promote into a CI gate.

- **MUST** read the post aloud—or have it read aloud by a TTS—before publish. Sentences the author stumbles over are too long or contain hidden passive constructions; the read-aloud catches both.
- **MUST** verify every concrete claim about a project / library / tool against the cited source (per the consumer's hard rule). Re-running the cited command, opening the cited file at the cited revision, or quoting the README verbatim are the canonical verifications.
- **MUST** run the consumer's build command (reference: `task build` / `task check`) before publish. A post that doesn't build doesn't ship.
- **SHOULD** delete one paragraph that the author hesitates over—most posts published after that delete read tighter than the alternative. (Strunk / Zinsser principle, applied per post.)
- **SHOULD** check both the EN and DE files render under the consumer's development server against the live language switch before merging. A cross-language binding mismatch is a silent break that the build doesn't catch in every case.

### Audience-L safety

The reference identifier `L` (used by the `nolte/blog` audience artefact) names the peripheral audience of people and projects characterised by name in a post. Consumers using different identifier letters interpret this section against their own audience artefact's equivalent peripheral-third-party audience.

- **MUST** ground every characterisation of a third-party project / person / tool in a primary-source citation (the project's README, a maintainer's public statement, a code reference, a release note). Critiques are allowed; libellous claims about unverified behaviour aren't.
- **MUST** offer a correction path. The default correction path is implicit (the source repo is public, the email is on the About page); when the consumer's audience artefact resolves the open question of a dedicated contact / correction channel, this clause **MUST** be updated to name the specific channel.
- **MUST NOT** quote private communications (Slack DMs, private emails, closed-issue threads) without explicit permission of the source.
- **SHOULD** prefer the named project's preferred name and capitalisation (for example, `npm` not `NPM`, `Astro` not `astro`). For people, use the form they use publicly.

## Acceptance criteria

A post conforms to this spec when **all** of the per-post criteria below hold. The spec-level criteria (`a-18` and following) are verified against the spec corpus and its git history, not per post; they're reviewed when the spec itself changes. Every criterion is written so a reviewer (the author, the `blog-author` skill, or a future lint skill) can mark it done / not done without ambiguity.

### Per-post criteria

- [ ] **a-1** The body opens with an inverted-pyramid lead paragraph (≤ 80 words) that names the post's claim, scope, or question.
- [ ] **a-2** Average sentence length in the body falls within 14–20 words; no two consecutive sentences exceed 30 words.
- [ ] **a-3** No body paragraph exceeds 4 sentences (excluding bullet lists, which aren't paragraphs for this rule).
- [ ] **a-4** Flesch–Kincaid Grade Level on the EN body (code blocks excluded) falls within 7–10. **Provisional**: until a `textstat`-or-equivalent lint hook ships (see §Open questions), the check is reviewer judgement, and the 7–10 threshold itself is subject to recalibration after the first 10 EN posts in a given consumer repository. The DE body is exempt from this criterion pending a DE-specific readability target (see §Open questions).
- [ ] **a-5** Every fenced code block declares a supported language identifier.
- [ ] **a-6** Every link's text describes its destination on its own (passes WCAG 2.4.4).
- [ ] **a-7** Headings are sentence case throughout; the body declares no second H1; heading levels don't skip going deeper.
- [ ] **a-8** No word or phrase from the closed forbidden list appears in the body without a documented override in surrounding prose.
- [ ] **a-9** Every concrete technical claim about a named project / library / tool cites a verifiable source.
- [ ] **a-10** The consumer's AI-disclosure flag (reference: `aiGenerated: true`) is present in frontmatter; the body doesn't contradict the flag's truth value via "I sat down and wrote this myself" framings.
- [ ] **a-11** The EN file and the DE file share the same cross-language binding key (`translationKey` or its equivalent) and the same filename slug, and both render under the consumer's development server.
- [ ] **a-12** DE post uses `„…"` quotation marks, em-dash with surrounding spaces, and `ä`/`ö`/`ü`/`ß` (no ASCII substitutes). EN post uses ASCII `"…"` and em-dash with surrounding spaces.
- [ ] **a-13** Every characterisation of a named third party (peripheral audience for named third parties, reference identifier `L`) carries a primary-source citation; no private-communication quotes appear without explicit permission.
- [ ] **a-14** The consumer's build command (reference: `task build`) succeeds on the working tree containing both files.
- [ ] **a-15** The EN body uses contractions (`it's`, `you'll`, `don't`, `I've`, `we're`) in running prose; expanded forms appear only inside direct quotations, code blocks, or where a contraction would create real ambiguity.
- [ ] **a-16** When the post describes a non-obvious decision, the body names what made the decision hard **before** naming the choice that was taken (the "show the thinking" MUST in §Person, voice, and tone).
- [ ] **a-17** A consumer that ships a visible AI-disclosure badge in addition to the frontmatter flag carries the badge on the rendered page; consumers that haven't yet shipped the badge are exempt from this criterion, with the `aiGenerated: true` frontmatter flag covered by `a-10` as the in-force part of §AI-disclosure tone.

### Spec-level criteria

Verified against `git log -- spec/project/post-writing-style/`, not against individual posts. These criteria belong to the §Forbidden words and phrases—§List maintenance subsection.

- [ ] **a-18** Every addition to a sub-list under §Forbidden words and phrases carries a source citation in the spec-diff or in the commit message that introduces the addition.
- [ ] **a-19** Every removal from a sub-list under §Forbidden words and phrases carries a one-line rationale in the spec-diff or in the commit message that introduces the removal.
- [ ] **a-20** A re-review record for the §Forbidden words list exists at every Claude model-family transition (for example, 4.x → 5.x), identifiable in `git log` as either a commit message tag (for example, `forbidden-list re-review`) or a dedicated continuous-improvement entry.

## Reference example annex

The reference consumer is the `nolte/blog` repository (a bilingual Astro static blog). It maps the §Consumer contract concepts as follows:

- Post-pair location: `src/content/posts/en/<slug>.md` and `src/content/posts/de/<slug>.md`.
- Cross-language binding key: frontmatter field `translationKey`.
- AI-disclosure flag: frontmatter field `aiGenerated: true`.
- Frontmatter schema source: Astro Zod schema at `src/content.config.ts`.
- Audience artefact: `AUDIENCES.md` at the repository root, with identifiers `A` (technical readers), `B` (portfolio reviewers), `C` (author as future-self), `L` (named third parties), `M` (search engines).
- Author-facing contract document: `CLAUDE.md` at the repository root.
- Build command: `task build` (full) / `task check` (faster variant).

Other consumers adopting this spec carry an analogous annex in their own repository documentation, mapping their engine-specific names to the abstract contract above. A consumer **MAY** ship its annex inline in its `CLAUDE.md` rather than as a separate file.

## Open questions

- **Quantitative readability gate.** §Readability thresholds pins Flesch–Kincaid 7–10 as a target. A lint hook that measures FK grade per post hasn't shipped. Until it does, the gate is reviewer-judgement; a future feature item should wire `textstat` (or equivalent) into the consumer's build pipeline. The threshold itself may need recalibration once real measurements come in across the first 10 posts in a given consumer.
- **DE-side readability target.** Flesch–Kincaid is calibrated for English. The German equivalent is the Wiener Sachtextformel or the Amstad-adjusted Flesch. This spec doesn't pin a DE-side threshold pending data; the reviewer relies on §Person, voice, and tone + §Bilingual typography alone for DE posts. A follow-up revision **SHOULD** add a DE-specific readability target once at least 5 DE posts exist in a given consumer for calibration.
- **Forbidden-word list maintenance.** The closed list under §Forbidden words is research-derived as of the spec's `Status: draft` date. New AI-tell tics will surface as Claude versions and prompting patterns shift. The list **MUST** be re-reviewed at every model-family transition (for example, Claude 4.x → 5.x); the mechanism for that re-review isn't defined here and should be picked up by [`spec/project/continuous-improvement/`](../continuous-improvement/en.md) or a dedicated triage entry.
- **Override-procedure formalism.** §Override procedure currently allows in-prose justification of a forbidden word. A stricter mechanism—frontmatter field `style_overrides: [`seamless`]` with rationale—would make overrides reviewable in diff rather than buried in prose. Deferred until the third documented override case shows the prose mechanism doesn't scale.
- **AI-disclosure-badge wiring.** §AI-disclosure tone today MUSTs the frontmatter flag and leaves the badge half consumer-conditional. A future revision should name a portable badge contract (text content, position, link target) so consumers wiring the badge follow the same convention. Triggered by the first consumer shipping the badge.

## References

Voice and tone:

- [The Four Dimensions of Tone of Voice—NN/G](https://www.nngroup.com/articles/tone-of-voice-dimensions/)
- [Voice and tone—Google developer documentation style guide](https://developers.google.com/style/tone)
- [Active voice—Google developer documentation style guide](https://developers.google.com/style/voice)
- [Voice and Tone—Mailchimp Content Style Guide](https://styleguide.mailchimp.com/voice-and-tone/)
- [Top 10 tips for Microsoft style and voice—Microsoft Style Guide](https://learn.microsoft.com/en-us/style-guide/top-10-tips-style-voice)
- [Microsoft's brand voice; above all, simple and human—Microsoft Style Guide](https://learn.microsoft.com/en-us/style-guide/brand-voice-above-all-simple-human)

Plain language and readability:

- [Federal Plain Language Guidelines (plainlanguage.gov)](https://www.plainlanguage.gov/howto/guidelines/FederalPLGuidelines/FederalPLGuidelines.pdf)
- [Top 10 Principles for Plain Language—National Archives](https://www.archives.gov/open/plain-writing/10-principles.html)
- [Flesch–Kincaid readability tests—Wikipedia](https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests)
- [Sentence length—Readability guidelines](http://readabilityguidelines.wikidot.com/sentence-length)
- [Improve the readability of your technical documentation with Flesch (ClickHelp)](https://clickhelp.com/clickhelp-technical-writing-blog/improve-the-readability-of-your-technical-documentation-with-flesch/)

Structure and flow:

- [Inverted Pyramid: Writing for Comprehension—NN/G](https://www.nngroup.com/articles/inverted-pyramid/)
- [Content design: writing for GOV.UK](https://www.gov.uk/guidance/content-design/writing-for-gov-uk)
- [How to Prevent F-Pattern Scanning—Mailchimp](https://mailchimp.com/resources/f-pattern-scanning/)

Headings and accessibility:

- [Title Case vs. Sentence Case—Grammarly](https://www.grammarly.com/blog/sentences/title-case-sentence-case/)
- [G141: Organizing a page using headings—W3C WCAG Techniques](https://www.w3.org/TR/WCAG20-TECHS/G141.html)
- [Understanding Success Criterion 2.4.4: Link Purpose (In Context)—W3C WAI](https://www.w3.org/WAI/WCAG21/Understanding/link-purpose-in-context.html)
- [Headings—W3C Web Accessibility Initiative tutorial](https://www.w3.org/WAI/tutorials/page-structure/headings/)

Code and Markdown conventions:

- [Markdown best practices—Microsoft Learn (PowerShell contributor guide)](https://learn.microsoft.com/en-us/powershell/scripting/community/contributing/general-markdown)
- [Fenced Code Blocks—Python-Markdown documentation](https://python-markdown.github.io/extensions/fenced_code_blocks/)

AI-tell and forbidden words:

- [Don't Write Like AI: Red Flag Words—Blake Stockton](https://www.blakestockton.com/red-flag-words/)
- ["I'd like to delve into how AI is fostering changes in writing"—Mere Sophistry](https://meresophistry.substack.com/p/id-like-to-delve-into-how-ai-is-fostering)
- [How to Spot AI Writing Tells—Olivia Cal](https://www.oliviacal.com/post/ai-writing-tells)

AI-content disclosure norms:

- [BBC sets protocol for generative AI content—Broadcast](https://www.broadcastnow.co.uk/production-and-post/bbc-sets-protocol-for-generative-ai-content/5200816.article)
- [7 things you need to know about the BBC's AI guidance—Broadcast](https://www.broadcastnow.co.uk/production-and-post/7-things-you-need-to-know-about-the-bbcs-ai-guidance/5200901.article)
- [Key AI concepts to grasp in a new hybrid journalism era—Reuters Institute](https://reutersinstitute.politics.ox.ac.uk/key-ai-concepts-grasp-new-hybrid-journalism-era-transparency-autonomy-and-authorship)

German typography:

- [Duden—Anführungszeichen](https://www.duden.de/sprachwissen/rechtschreibregeln/anfuehrungszeichen)
- [Wikipedia:Typografie—Anführungszeichen und Gedankenstrich](https://de.wikipedia.org/wiki/Wikipedia:Typografie)

"Show your work" exemplar blogs:

- [Kalzumeus—Patrick McKenzie's archive](https://www.kalzumeus.com/archive/)
- [Julia Evans—jvns.ca](https://jvns.ca/)

<!-- vale Microsoft.Quotes = YES -->
<!-- vale Microsoft.Contractions = YES -->
<!-- vale Microsoft.Dashes = YES -->
