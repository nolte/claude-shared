# Post audience communication

Status: draft

<!-- vale Microsoft.Quotes = NO -->
<!-- vale Microsoft.Contractions = NO -->
<!-- vale Microsoft.Dashes = NO -->

## Context

Readers: implementors of the [`blog-author`](../blog-author/en.md) skill in the `nolte-shared` plugin (primary), human authors who curate AI-drafted blog posts (secondary), and downstream review skills that may check a post against this spec before publish.

This spec is the companion to [`post-writing-style`](../post-writing-style/en.md). Where `post-writing-style` tells the author **how to write** (voice, readability, typography, forbidden words), this spec tells the author **whom to write for, and how to shape a single post so the right reader is served first without alienating the others**.

The consumer repository—a bilingual personal-blog or technical-blog repository adopting the [`blog-author`](../blog-author/en.md) contract—supplies an audience artefact produced via [`spec/project/audience-identification/`](../audience-identification/en.md). That artefact lists the consumer's audiences and ranks their criticality. This spec uses an **abstract audience shape** (described in §Consumer audience contract) and refers to specific audience identifiers only when they exist in the consumer artefact. The reference consumer is `nolte/blog`; the §Reference example annex names its concrete identifiers (`A`/`B`/`C`/`L`/`M`).

The hard problem this spec solves: **a single blog post can't maximally optimise for every direct end-reader subgroup simultaneously.** A peer technical reader wants depth; a portfolio reviewer wants a six-second signal; a future-self knowledge-base reader wants raw working notes that the other two would find too rough. Existing technical-communication research (Carliner, Lannon, gov.uk Content Design, NN/g progressive disclosure) converges on a single answer: layered writing with a declared primary audience per post. That answer is what this spec codifies.

## Goals

- Mandate that every post **declares exactly one primary audience** so the author and the `blog-author` skill have an unambiguous target when shaping the lede, the depth, and the closing.
- Provide a **per-audience-shape addressing rubric**: for each of the three reference end-reader shapes (peer technical reader, portfolio reviewer, future-self knowledge-base reader)—that names what to optimise for, what to avoid, the lede pattern, and the conflict-resolution stance when audiences disagree.
- Provide **multi-audience layering rules** so a post written primarily for one audience still serves the others through progressive disclosure (skim-able lede → body depth → optional drawer / footnote / linked appendix).
- Codify **named-third-party treatment** (the peripheral "named third parties" audience, reference identifier `L`): how to characterise them fairly, when permission is required, what the correction path is.
- Pin **bilingual audience symmetry**: the EN and DE post pair serves the same primary audience in both languages; the choice doesn't flip between sides.
- Stay **personal-blog-scoped**: the spec governs the body of a Markdown post produced by a consumer that adopts this spec. Header metadata, sitemap, OG card content, and RSS shape are out of scope (those serve the search-engine / crawler audience and are governed elsewhere).

## Non-Goals

- Defining the **audience artefact** itself or the audience-identification methodology—that lives in the consumer's `AUDIENCES.md` (or equivalent) and [`spec/project/audience-identification/`](../audience-identification/en.md).
- Replacing [`post-writing-style`](../post-writing-style/en.md). The writing-style spec defines voice, readability, typography, and forbidden vocabulary regardless of audience. This spec defines audience targeting on top of that; the two are designed to compose.
- Defining **per-page docs-tracks frontmatter**. Post frontmatter doesn't carry the docs-audience-tracks `track:` field that the MkDocs-side spec uses, because every blog post serves the same end-reader track. The audience signal in this spec lives in a separate frontmatter field (see §Primary-audience declaration).
- Defining **content selection**. Which projects, decisions, or experiences make it into a post is a roadmap / sprint concern, not an audience-communication concern. Once a topic is chosen, this spec defines whom the post is for.
- Defining **SEO / metadata for the search-engine / crawler audience**. The crawler-facing surface is structured-data shape, not body prose; it belongs in a separate metadata or robots-policy spec.
- Substituting **journalistic editorial standards**. The author isn't a journalist; the spec borrows the BBC / Reuters / AP norms that apply to third-party portrayal but doesn't mandate the full editorial governance those organisations carry.
- Rendering the **audience signal on the page** (a visible "for developers" / "for portfolio readers" badge near the post header). That's a consumer-side presentation concern on the consumer's docs / UX roadmap, and the spec's default is to keep the signal internal-only (frontmatter)—visible badges risk reading as defensive. This mirrors how [`blog-author`](../blog-author/en.md) delegates hero-image rendering and style policy to a consumer-side roadmap item rather than carrying it as a spec-level open question.

## Consumer audience contract

This spec is written against an **abstract audience shape**, not against specific identifier letters. A consumer repository adopting this spec **MUST** supply an audience artefact (per [`spec/project/audience-identification/`](../audience-identification/en.md)) that satisfies the following shape:

- At least three **direct end-reader subgroups** that map onto the three rubrics in §Per-audience addressing rubrics:
  - a **peer-technical reader** (the reference consumer calls this `A`): a developer dropping in via search, RSS, or a peer's link, reading for technical accuracy and "show your work" depth.
  - a **portfolio reviewer** (reference: `B`): a recruiter or hiring manager arriving from CV / LinkedIn, reading for a fast signal of project work, working style, and recency. Six-to-seven-second initial scan.
  - a **future-self knowledge-base reader** (reference: `C`): the author re-reading own posts to recover a decision, a method, or context. Tolerates rougher drafts; needs durable, self-coherent explanation.
- At least one **peripheral audience for named third parties** (reference: `L`): people, projects, libraries, and tools characterised by name in posts. Read fairness rules apply to them regardless of the primary audience.
- Optionally, a **peripheral search-engine / crawler audience** (reference: `M`): out of scope for body prose.

A consumer **MAY** ship additional subgroups (a fourth direct audience, a sponsor audience, etc.); those are addressed by following the same rubric pattern as the closest reference shape, documented in the consumer's own annex.

Where this spec uses bare identifier letters (`A`, `B`, `C`, `L`, `M`)—to keep the rubrics readable—those letters refer to the **reference consumer's** identifiers. A consumer with different identifiers interprets every such reference against its own audience artefact via the mapping in §Reference example annex.

## Requirements

### Primary-audience declaration

- **MUST** declare exactly one **primary audience** for every post via a frontmatter field `primaryAudience: <identifier>`. Only direct-end-reader-subgroup identifiers (reference: `A`, `B`, `C`) are valid values for this field; the named-third-parties identifier (reference: `L`) is never a primary audience (it's a constraint, not a target—see §Named-third-party treatment) and the search-engine / crawler identifier (reference: `M`) is out of scope per §Non-Goals.
- **MUST** declare a secondary-audience list via a frontmatter field `secondaryAudiences: [<identifier>, …]`. The list **MUST NOT** contain the value used in `primaryAudience`; it **MAY** be empty (`[]`) when the post is intentionally narrow.
- **MUST NOT** rotate `primaryAudience` after publish to retarget an underperforming post. The frontmatter field is a write-once contract that anchors the post's shape; a post that wants to serve a different audience is a new post under a new slug.
- **SHOULD** target a **balanced distribution** across the consumer's three reference end-reader subgroups, measured at a five-post rolling window. The reference distribution for `nolte/blog` is **A: roughly 50 %, B: roughly 20 %, C: roughly 30 %**; other consumers pin their own target based on their audience artefact's criticality ranking and traffic data. The split is a starting point to be calibrated against actual traffic / referrer data; deviations are fine in any single post and signal a calibration question only over a 10-post horizon.
- **MAY** mark a post `primaryAudience: <future-self-knowledge-base identifier>` even when content is durable and shareable; the field declares which reader the post's shape was optimised for, not who is allowed to read it.

### Per-audience addressing rubrics

The three rubrics below correspond to the three reference end-reader subgroups in §Consumer audience contract. A consumer's audience artefact may use different identifier letters; in that case, the rubric attaches by audience-shape (the rubric below for "peer technical readers" attaches to whichever identifier the consumer assigns to that shape).

#### Peer-technical-reader rubric (reference identifier `A`)

A peer technical reader arrived via search, an RSS reader, or a link from another developer. The reader's first question is "does this person know what they're talking about", answered in the first paragraph. The reader's second question is "can I copy / adapt / verify the work shown here", answered in the body.

- **MUST** lead with the concrete artefact—the problem statement, the failing case, the actual code under discussion, the version pin. The first 80 words of an `A`-post **MUST NOT** be background context; they **MUST** name the technical claim.
- **MUST** carry the working artefact verbatim: the diff, the command output, the config, the failing test, the screenshot of the UI state—whichever is what the reader would need to reproduce. The artefact isn't an illustration of the post; the post is the explanation around the artefact.
- **MUST** name versions of every tool / library / framework discussed (`Astro 5.x`, `Tailwind 4.0`, `Claude Opus 4.7`, `Python 3.12`) so the reader can date-anchor the claim and decide if it still applies to their setup.
- **MUST NOT** assume the portfolio-reviewer's vocabulary. "MVP", "ROI", `stakeholder`, and "value delivery" are out of register; if a business framing genuinely matters, name it in technical terms ("we wanted this to run in CI without paying for a hosted runner").
- **MUST NOT** under-show because "the reader already knows that". When in doubt, link to the primary source rather than skipping the reference; an `A`-reader uses the links, a `B`-reader skips them, neither pays a price.
- **SHOULD** close with an "out of scope / open questions / what I would do next" section. This serves `A`'s curiosity (other paths through the problem) and serves the future-self reader (`C`) at the same time, at no cost to `B` who has already left.
- **SHOULD** signal expertise level early. "I had not touched X before this project" sets the reader's expectations as accurately as "I have shipped X in production for five years"; both are honest and both are useful to `A`.

#### Portfolio-reviewer rubric (reference identifier `B`)

A portfolio reviewer is a recruiter, hiring manager, or someone evaluating the author's portfolio from a non-technical-deep angle. Eye-tracking studies put the initial scan at six to seven seconds; the post has to signal **what was built, what role the author played, and how recent the work is** in that window or the reader leaves.

- **MUST** make the first 80 words (the inverted-pyramid lead required by [`post-writing-style`](../post-writing-style/en.md)) work as a six-second signal: it **MUST** name (a) the project or topic, (b) what was done, and (c) the author's first-person role. "I rewrote the deploy pipeline of my Home Assistant integration to ship green every push" passes; "Today we'll explore CI/CD" fails.
- **MUST** carry a one-line "what this means in practice" sentence early—what changed, what shipped, what was learned—phrased in plain language. A `B`-reader doesn't parse `kubectl rollout restart` but reads "I cut deploy time from 12 minutes to 90 seconds".
- **MUST** keep the post visually scannable: at least two H2 headings on any post over 600 words, the first H2 within the first viewport's worth of text (≈ 400 words on a desktop reading column).
- **MUST NOT** require the reader to read the code blocks. A `B`-reader skips fenced code. The surrounding prose **MUST** carry the message; the code substantiates it but isn't the message.
- **MUST NOT** open with a jargon barrier ("This post is about k8s operators built on CRDs…"). The jargon may come in the body once the broader claim has landed.
- **SHOULD** name the portfolio project explicitly and link to its repository (or to the consumer's `/projects/<slug>` route for portfolio entries) so the `B`-reader can pivot from the post to the project page in one click.
- **SHOULD** include a date signal beyond the frontmatter `pubDate`—"in May 2026" in the lede, or a tag like "ongoing work" / "shipped to production"—because `B`-readers reading a post in 2027 want to know it's still recent.

#### Future-self-knowledge-base rubric (reference identifier `C`)

A future-self reader is the author re-reading own work months or years later to recover a decision, a method, or a piece of context that has fallen out of memory. The reader's expectation is durability and self-coherence: the post should pick up cold, without the surrounding conversation that produced it.

- **MUST** record the **why** of every decision the post describes, not only the **what**. "I went with `bun` over `node`" without "because the build was 4× faster and `node_modules` had been a constant source of merge conflicts" is useless to future-self.
- **MUST** name the **alternatives considered and rejected** when the post describes a non-obvious choice. The list of "what I didn't pick" is at least as valuable for future-self as the final pick—those are the cul-de-sacs the author won't have to re-explore.
- **MUST** carry a **glossary or "what these terms mean in this post" note** when the post relies on terminology that may have shifted by re-reading time. Tag the term once with a short parenthetical or a link to the original RFC / project README; future-self doesn't necessarily remember the in-2026 meaning of `agent` or `skill` by 2028.
- **MAY** be rougher than an `A`-targeted or `B`-targeted post—broken thoughts in brackets, half-finished sentences left in, "TODO: come back to this" markers—provided the post is honestly tagged `primaryAudience: C`. The rough form is the feature; sanding it down to `A`-grade would erase the property that makes `C`-posts useful in the digital-garden sense.
- **MUST** still meet the **writing-style spec's verifiable-claim rule**: roughness is allowed in form, not in factual accuracy. A `C`-post that says "library X does Y" with no source is the same violation as an `A`-post that does it.
- **SHOULD** be cross-linked aggressively to other posts on related topics. `C`-posts derive their value from the linked graph; an isolated `C`-post is a less useful `C`-post.

### Named-third-party treatment (reference identifier `L`)

The named-third-parties audience covers everyone the post characterises by name: maintainers of libraries discussed, projects the author critiques, people quoted, tools compared. The fairness rules below are non-negotiable regardless of which primary audience the post serves.

- **MUST** ground every characterisation of a named third party in a primary source—the project's README, the maintainer's public statement, a release note, a code reference at a pinned revision. Critique is permitted; unverified factual claims about behaviour aren't.
- **MUST** use the third party's preferred name and capitalisation when known (for example, `npm` not `NPM`, `Astro` not `astro`). For people, the publicly used form.
- **MUST NOT** quote private communications (DMs, private email, closed-issue threads, internal Slack) without explicit permission of the source.
- **MUST NOT** characterise a third party's intent ("they did this because they wanted to lock users in") without a public statement supporting the characterisation; intent claims are the highest-libel-risk class of statement in either jurisdiction (EN-speaking and DE-speaking).
- **SHOULD** route correction requests through the implicit channels available today—public source repository issues and the email on the consumer's About page—and the implicit-channel form is the compliant baseline for the current state of the spec. When the consumer's audience artefact resolves the open question of a dedicated contact / correction channel, this **SHOULD** is promoted to a **MUST** that **MUST** name the declared channel; the promotion is recorded as a spec revision, not a silent edit. The intent of this conditional is to keep the rule unambiguously compliant today rather than indeterminate.
- **SHOULD** carry a one-line attribution when the post leans heavily on someone else's work or framing ("the framing of X as Y comes from <name>'s post at <url>"). This serves `L` (the cited party feels seen rather than appropriated) and `A` (the reader learns where to follow up).
- **MAY** name a specific person in praise; **SHOULD NOT** name a specific person in critique when the critique is at the project or codebase level—name the project, link to the public artefact, and let the named maintainer come find the post if they want. Project-level critique is easier to keep fair than person-level critique.

### Multi-audience layering

A single post serves multiple audiences only when its **shape** lets each audience self-select the depth they need. The required layers below derive from NN/g progressive disclosure and the "writing for multiple audiences" tradition in technical communication.

- **MUST** carry an **inverted-pyramid lede** (required by [`post-writing-style`](../post-writing-style/en.md)) that delivers the post's claim to every audience in ≤ 80 words. The lede is the shared surface; it **MUST NOT** require any of the direct end-reader subgroups to keep reading to extract the headline.
- **MUST** carry a **body that depth-serves the primary audience**. The body's prose register, code-block density, terminology depth, and link density are tuned for `primaryAudience`. Cross-referenced material that would interest a secondary audience belongs in escape-hatch links, not in the main flow.
- **SHOULD** carry an **escape-hatch layer** for the most likely secondary audience. Common patterns:
  - For a `primaryAudience: A` post with secondary `B`: a one-line "what this means for non-engineers" sentence early in the body, and a link out from the lede to `/projects/<slug>` (or the consumer's portfolio-entry route).
  - For a `primaryAudience: B` post with secondary `A`: a "details and pitfalls" section toward the end with the deeper technical material, written so a `B`-reader who has already left doesn't miss anything important.
  - For a `primaryAudience: C` post with secondary `A`: a "if you got here by accident, here's the context" paragraph near the top.
- **MAY** use a **collapsible drawer** (`<details>…</details>`) to hide a long code block or a side argument that the primary audience doesn't need but the secondary audience might. Drawers **MUST NOT** be used to bury content the primary audience does need; that's "hide your work" and violates the spec.
- **MUST NOT** layer beyond three depths (lede, body, escape-hatch). Adding a fourth layer ("…and if you really want to go deep…") signals that the post should be split into two posts.

### Diátaxis positioning

The Diátaxis framework partitions documentation into Tutorial, How-to, Reference, and Explanation. Personal-blog posts on a consumer of this spec sit in two of those four quadrants and explicitly **stay out of** the other two.

- **MUST** position every post as **Explanation**, **How-to**, or a blend of the two:
  - *Explanation*: the post explains why something is the way it is, what trade-off was chosen, what the author learned. Maps cleanly to `primaryAudience: A` or `primaryAudience: C`.
  - *How-to*—the post walks through solving a specific problem with a working artefact. Maps cleanly to `primaryAudience: A`; rarely `primaryAudience: B`.
- **MUST NOT** structure a post as **Tutorial** in the Diátaxis sense (a teaching journey through a beginner curriculum). The blog isn't a course; tutorial content belongs to upstream project documentation, not here. A post that would be a tutorial should be either an Explanation of what the author learned by working through the tutorial, or a How-to addressing a specific snag.
- **MUST NOT** structure a post as pure **Reference** (an enumerated, complete API or schema description). Reference belongs in source-code documentation or a dedicated docs site. A post that would be reference content should be split: the reference material lives where it belongs; the post explains the why or walks through a use case.
The Diátaxis stance is implicit in the lede ("here's how I made X work" → How-to; "here's why I picked X over Y" → Explanation) and **MAY** be stated explicitly in surrounding prose when doing so sharpens the post; a dedicated frontmatter field is intentionally **not** required (see §Open questions for the deferred lint-friendly variant). This guidance is reviewer-meta and isn't a checkable per-post rule—no Acceptance Criterion targets it.

### Conflict resolution between audiences

When the audiences want incompatible things—`A` wants more depth, `B` wants brevity, `C` wants raw notes—the post follows the rules below in order.

- **MUST** resolve in favour of the declared `primaryAudience`. The whole point of the frontmatter declaration is that the trade-off has been made up front; the post doesn't negotiate it paragraph by paragraph.
- **MUST** never resolve **against** the named-third-parties audience's expectations (reference: `L`). It isn't a primary audience but is an **inviolable constraint**: a post is allowed to be too dense for `B` or too sparse for `C`, but it's **never** allowed to characterise a named third party unfairly to serve `A`'s appetite for sharp critique.
- **SHOULD** resolve secondary-audience pulls into escape-hatch links rather than inline accommodations. A `primaryAudience: A` post that drifts into `B`-friendly business framing in the middle loses `A`'s trust without serving `B`; the right move is a single `B`-targeted sentence at the top and a link out at the bottom, not a middle paragraph that serves neither.
- **MAY** split a single underlying topic into two posts, each with its own `primaryAudience`, when one post can't serve both audiences without compromising both. The two posts cross-link, share tags, and may share a `portfolioProject`. Splitting is the canonical answer to the recurring "this post wants to be two posts" feeling.

### Bilingual audience symmetry

- **MUST** keep `primaryAudience` identical between the EN file and the DE file of a post pair. A post is "for `A`" in both languages or "for `C`" in both languages; the frontmatter field doesn't differ across the cross-language binding.
- **MUST** keep `secondaryAudiences` identical between EN and DE for the same reason.
- **MUST** translate audience-specific framings idiomatically. A `B`-targeted lede that names a job-market signal ("I shipped this between contracts") translates idiomatically to a DE phrasing that carries the same recruiter-readable signal, not a word-for-word rendering.
- **MAY** localise references that genuinely differ between EN- and DE-speaking audiences (for example, a legal-citation reference) when the localisation is honest and the underlying claim is unchanged. Re-translation **MUST NOT** change the post's substance—only its surface.
- **MUST NOT** flip a post's audience target to `fix` an unbalanced corpus distribution mid-translation. Corpus-level rebalancing happens at the next-post level, not by retconning an existing pair.

## Acceptance criteria

A post conforms to this spec when **all** of the following hold. The criteria are written so a reviewer (the author, the `blog-author` skill, or a future lint skill) can mark each one done / not done without ambiguity.

**Enforcement status (open question—see §Open questions, "Frontmatter schema impact").** Criteria `a-1` and `a-2` reference frontmatter fields (`primaryAudience`, `secondaryAudiences`) that the consumer's static-site schema may not yet declare. Until the consumer's schema gap is closed, `a-1` and `a-2` apply to posts authored or updated after this spec is adopted by the consumer, and remain author-side conventions that the build won't enforce. Legacy posts pre-dating that transition are exempt; reviewers and lint skills **MUST** treat the absence of these fields on a legacy post as outside the spec's scope rather than as a failed criterion. A reviewer or lint skill encountering a post with no `primaryAudience` **SHOULD** treat it as `primaryAudience: A` (peer-technical reader), the corpus's most common shape; this default is what the consumer's schema migration inherits.

- [ ] **a-1** Frontmatter declares exactly one `primaryAudience` from the consumer's direct-end-reader-subgroup identifiers (reference: `{A, B, C}`).
- [ ] **a-2** Frontmatter declares a `secondaryAudiences` list from the same identifier set that doesn't contain the primary value.
- [ ] **a-3** The first 80 words of the body deliver the post's headline in a form that doesn't require keeping reading.
- [ ] **a-4** The body's depth, terminology, and code-block density are tuned for the declared `primaryAudience`, not split mid-post to serve a secondary audience.
- [ ] **a-5** When the post has a non-empty `secondaryAudiences` list, at least one explicit escape-hatch (link, drawer, one-line accommodation) is present in the post body and identifiable as serving that audience—by adjacent prose, by the link's anchor text, or by the drawer's summary text.
- [ ] **a-6** Every named third party (reference identifier `L`) is grounded in a primary-source citation; no private communication is quoted without explicit permission; no intent claim is asserted without a public statement supporting it.
- [ ] **a-7** The post fits Diátaxis Explanation, How-to, or a blend; it isn't a Tutorial in the Diátaxis sense and not pure Reference.
- [ ] **a-8** The EN file and the DE file carry identical `primaryAudience` and `secondaryAudiences`.
- [ ] **a-9** No post in the recent five-post window targets the peer-technical-reader audience (reference: `A`) exclusively; the corpus shows at least one portfolio-reviewer-targeted and at least one future-self-targeted post in any rolling 10-post window (corpus-level criterion, checked at sprint review, not per post).
- [ ] **a-10** When audience needs collide in the post, the resolution favours `primaryAudience` and never against the named-third-parties audience (reference: `L`); the reviewer can name the specific trade-off without hunting.
- [ ] **a-11** Post body depth-serves the declared `primaryAudience` per its rubric—concretely:
  - For `primaryAudience: A`: working artefact present (diff / output / config / screenshot), versions of named tools pinned, "out of scope / next" section present, **expertise level signalled early** ("I had not touched X before this project" or "I have shipped X in production for years"—either way, honest).
  - For `primaryAudience: B`: lede names project + role + recency in plain language, body readable without parsing code blocks, link to the consumer's portfolio-entry route (or equivalent), **date signal present beyond `pubDate`** (an in-prose month / year, or a tag like "ongoing work" / "shipped to production").
  - For `primaryAudience: C`: `why` of every decision recorded, alternatives considered named, glossary or context note present where re-reader-confusing terminology appears.
- [ ] **a-12** The post doesn't layer beyond three depths (lede, body, escape-hatch).
- [ ] **a-13** No `<details>` collapsible drawer in the body holds content the post's argument relies on for the **primary** audience; drawers carry only material a secondary audience might want, never material the primary audience requires.

## Reference example annex

The reference consumer is the `nolte/blog` repository. Its audience artefact (`AUDIENCES.md` at the repository root) maps onto this spec's abstract shape as follows:

- Peer-technical reader → identifier **`A`**.
- Portfolio reviewer → identifier **`B`**.
- Future-self knowledge-base reader → identifier **`C`**.
- Named third parties → identifier **`L`**.
- Search engines and LLM crawlers → identifier **`M`** (out of scope for body prose).
- Author as site maintainer → identifier **`D`** (out of scope for the post body—the spec doesn't address site-maintenance reading).
- Claude Code as AI co-operator → identifier **`E`** (out of scope for the post body—the spec doesn't address AI-tooling reading).

Corpus distribution target (reference consumer only): **A: ~ 50 %, B: ~ 20 %, C: ~ 30 %** at a five-post rolling window, recalibrated against actual traffic / referrer data after the first 20 posts.

Other consumers adopting this spec carry an analogous annex in their own repository documentation. A consumer **MAY** ship its annex inline in its `CLAUDE.md` rather than as a separate file.

## Open questions

- **Frontmatter schema impact.** Default: when a post (or its consumer schema) carries no `primaryAudience`, reviewers and lint skills treat it as `primaryAudience: A` (peer-technical reader)—encoded as a SHOULD in the §Acceptance criteria enforcement-status block. Revisit when: the reference consumer `nolte/blog` ships the schema change in `src/content.config.ts` declaring `primaryAudience` and `secondaryAudiences` (a feature item in `nolte/blog`) and removes the enforcement-status caveat from its `CLAUDE.md`; at that point `a-1` / `a-2` flip from author-side convention to build-enforced and this enforcement-status block plus this bullet are deleted.
- **Corpus distribution gate.** Revisit when: the reference consumer `nolte/blog` reaches 20 published posts AND has traffic / referrer analytics available; the re-check at the next sprint review compares actual A/B/C readership against the modelled `50/20/30` (specifically, drop the peer-technical-reader `A` share if LinkedIn portfolio-reviewer `B` traffic is materially higher than modelled). The upstream signal lives in the consumer repository's analytics, not in this portfolio plugin.
- **Correction-channel formalism.** Revisit when: `nolte/blog`'s `AUDIENCES.md` (the named-third-parties audience, reference identifier `L`) adds a dedicated, named correction / contact channel. Confirmed not yet present—the [`audience-identification`](../audience-identification/en.md) spec's own open questions name no correction channel and its only open question concerns future threat-modeling / SLA specs, so the consumer-side declaration that would unblock this doesn't exist yet.
- **Threshold for permission on non-private but personal characterisations.** §Named-third-party treatment requires explicit permission only for private-communication quotes; public statements are handled via the public form plus a link. Revisit when: a real contested case involving a named third party arises (an `L`-affected post that draws a fairness / consent dispute), OR enough `L`-affected posts ship to establish a pattern that the public-form threshold is insufficient. This mirrors [`blog-author`](../blog-author/en.md)'s reactive-tightening pattern—a concrete contested case triggers a later spec tightening, not a prospective one.
- **Diátaxis frontmatter signal.** §Diátaxis positioning keeps the stance implicit in the lede and a dedicated frontmatter field is intentionally not required. Revisit when: a downstream lint or audit skill is introduced that needs to read the Diátaxis position programmatically (machine-readably) rather than inferring it from the lede. Until such a consumer exists, the implicit-in-lede form stands; [`blog-author`](../blog-author/en.md)'s own briefing-side YAML-schema question is likewise still open, so no machine-readable consumer for the position exists yet either.

## References

Audience methodology and content design:

- [Content design: planning, writing and managing content—GOV.UK](https://www.gov.uk/guidance/content-design)
- [Content design: writing for GOV.UK](https://www.gov.uk/guidance/content-design/writing-for-gov-uk)
- [Audience Analysis: Primary, Secondary and Hidden Audiences—Writing Commons](https://writingcommons.org/article/audience-analysis-primary-secondary-and-hidden-audiences/)
- [Audience—Howdy or Hello? Technical and Professional Communication](https://odp.library.tamu.edu/howdyorhello/chapter/audience/)
- [The Elements of Content Strategy by Erin Kissane (A Book Apart)](https://elements-of-content-strategy.abookapart.com/)

Documentation frameworks:

- [Diátaxis project page](https://diataxis.fr/)
- [Start here—Diátaxis in five minutes](https://diataxis.fr/start-here/)
- [Progressive Disclosure—IBM Documentation](https://www.ibm.com/docs/en/technical-content?topic=practices-progressive-disclosure)
- [Progressive Disclosure—I'd Rather Be Writing](https://idratherbewriting.com/ucd-progressive-disclosure/)

Reader behaviour:

- [Inverted Pyramid: Writing for Comprehension—NN/G](https://www.nngroup.com/articles/inverted-pyramid/)
- [How to Prevent F-Pattern Scanning—Mailchimp](https://mailchimp.com/resources/f-pattern-scanning/)
- [Ladders Updates Popular Recruiter Eye-Tracking Study—PR Newswire](https://www.prnewswire.com/news-releases/ladders-updates-popular-recruiter-eye-tracking-study-with-new-key-insights-on-how-job-seekers-can-improve-their-resumes-300744217.html)
- [Eye tracking study shows recruiters look at resumes for 7 seconds—HR Dive](https://www.hrdive.com/news/eye-tracking-study-shows-recruiters-look-at-resumes-for-7-seconds/541582/)

Writing for developers (peer-technical-reader audience):

- [How to Write for a Developer Audience—Kalyna Marketing](https://kalynamarketing.com/blog/writing-for-developers)
- [Writing for Developers: 5 Best Practices—Firebrand](https://www.firebrand.marketing/deep-dives/writing-for-developers-5-best-practices/)
- [Kalzumeus—Patrick McKenzie's archive](https://www.kalzumeus.com/archive/)
- [Julia Evans—jvns.ca](https://jvns.ca/)

Knowledge-base / future-self writing:

- [Evergreen notes—Andy Matuschak](https://notes.andymatuschak.org/Evergreen_notes)
- [A Brief History & Ethos of the Digital Garden—Maggie Appleton](https://maggieappleton.com/garden-history)
- [The Garden of Maggie Appleton](https://maggieappleton.com/garden/)

Named-third-party fairness:

- [BBC sets protocol for generative AI content—Broadcast](https://www.broadcastnow.co.uk/production-and-post/bbc-sets-protocol-for-generative-ai-content/5200816.article)
- [Key AI concepts to grasp in a new hybrid journalism era—Reuters Institute](https://reutersinstitute.politics.ox.ac.uk/key-ai-concepts-grasp-new-hybrid-journalism-era-transparency-autonomy-and-authorship)
- [Offering Criticism in Open Source Projects—Jonathan Desrosiers](https://jonathandesrosiers.com/2026/02/offering-criticism-in-open-source-projects/)

Personal-blog principles:

- [POSSE—IndieWeb](https://indieweb.org/POSSE)
- [Own your data—IndieWeb](https://indieweb.org/own_your_data)
- [The Promise of Stripe Press—alohomora](https://morgmah.substack.com/p/the-promise-of-stripe-press)

<!-- vale Microsoft.Quotes = YES -->
<!-- vale Microsoft.Contractions = YES -->
<!-- vale Microsoft.Dashes = YES -->
