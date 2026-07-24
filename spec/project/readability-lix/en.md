# Readability (LIX)

Status: draft

## Context

Portfolio repositories already measure readability inside the editorial layer: [`spec/project/lektorat/`](../lektorat/en.md) §D1 evaluates English prose with Flesch Reading Ease (FRE) and Flesch–Kincaid Grade Level (FKGL) and German prose with the Wiener Sachtextformel (WSTF) and LIX. That split has a structural weakness for a bilingual corpus: the English and German halves of the same documentation set are held to **different, non-comparable** scales, so "is this page readable?" has no single answer that travels across the EN ↔ DE pair, and an iterative author-to-editor loop has no common target to converge on.

LIX (Läsbarhetsindex, Carl-Hugo Björnsson, 1968) is the one metric in that set that's **comparatively language-independent**: it counts letters, not syllables, which is why cross-language correlation studies (French/English, German/English, Greek/English) found that translated parallel texts keep their relative difficulty ranking under LIX. This spec elevates LIX from "the German-only metric" to the **primary, cross-language readability metric** computed identically for English and German, so a single readability target governs the whole bilingual corpus and the author ↔ editor loop has one number to drive down.

This spec is the **single source of truth** for: the LIX formula and its long-word rule, the tokenization and segmentation decisions that make a LIX value reproducible and EN/DE-comparable, the interpretation scale, the cross-language calibration (the German-versus-English caveat), the per-content-type target corridors, the catalogue of meaning-preserving transformations that lower a LIX score, and LIX's relationship to the supplementary metrics. [`spec/project/lektorat/`](../lektorat/en.md) §D1, [`spec/project/post-writing-style/`](../post-writing-style/en.md), and [`spec/project/lektorat-auto-revise/`](../lektorat-auto-revise/en.md) reference this spec rather than restating any of it.

**Readers** of this spec are implementors of the `lektorat-scanner` agent (which computes LIX), the `lektorat-apply` and `lektorat-auto-revise` skills (which drive the iterative improvement loop), and the authoring layer (`audience-doc-author` agent, `blog-author` skill) whose drafts are measured against a LIX corridor. Familiarity with [`spec/project/mkdocs-structure/`](../mkdocs-structure/en.md) (the `content_mode` enum), [`spec/project/lektorat/`](../lektorat/en.md) (the D1–D6 dimensions, the §Outputs JSON shape, and the §Language handling stripping rules), and [`spec/project/audience-identification/`](../audience-identification/en.md) (the audience artefact and protected-terms sources) is assumed; terms from those specs are used without restatement.

A deliberate design honesty: the **formula, the long-word threshold, and the five interpretation reference points are stable, primary-source-attested historical facts** (Björnsson 1968). The **target corridors, the German-versus-English offset, and the lever-priority ranking are engineering judgment** calibrated from those facts plus the existing `lektorat` corridors, and are labelled as such throughout. Each judgment carries an Open Question with a revisit condition gated on accumulated portfolio audit data, mirroring how `lektorat` treats its own corridor calibration.

## Goals

- One **canonical definition of LIX** (formula, long-word rule, tokenization, segmentation) computed **identically** for English and German, so a LIX value is comparable across the bilingual corpus and reproducible across runs.
- A **language-aware target-corridor system** per `content_mode`, with an explicit German offset that's justified by the documented compound-word inflation effect rather than invented per repository.
- A **catalogue of meaning-preserving transformations** that lower a LIX score, mapped to the lever each one moves (sentence length versus long-word ratio) and ranked by impact and risk, with an explicit anti-gaming boundary that separates genuine readability gains from edits that merely move the number.
- A **pinned, reproducible computation pipeline** (library, version, tokenizer, sentence segmenter) recorded in the run metadata, so the same prose yields the same LIX value and EN and DE stay comparable.
- An explicit, **subordinating relationship to the supplementary metrics** (FRE/FKGL for English, WSTF for German): LIX is primary and cross-language; the others are advisory signals that never override a LIX finding.
- A definition of how LIX participates in the **iterative author ↔ editor improvement loop**: the convergence target, the per-pass briefing inputs the author needs, and the gate that distinguishes real improvement from regression or gaming.

## Non-Goals

- Defining the **editorial operation mechanics** (`audit` / `patch` / `revise`, severity classification, the findings-report JSON shape): those are owned by [`spec/project/lektorat/`](../lektorat/en.md). This spec defines **what LIX is and how it's computed, targeted, and improved**, which `lektorat` §D1 then consumes.
- Defining **first-authorship voice, tone, and structure**: those are owned by [`spec/project/prose-style/`](../prose-style/en.md) (documentation) and [`spec/project/post-writing-style/`](../post-writing-style/en.md) (blog posts). This spec supplies the readability target those authors write toward.
- **Redefining FRE, FKGL, or WSTF**: those keep their definitions from their own sources and remain supplementary signals (§Relationship to other metrics).
- Defining the **routing, re-audit gate, or per-file bound** of the autonomous revise loop: those are owned by [`spec/project/lektorat-auto-revise/`](../lektorat-auto-revise/en.md). This spec defines only the LIX-specific inputs and convergence target that loop consumes (§Iterative improvement loop).
- **Mandating one implementation** of the metric: the spec constrains the formula, the corridors, the pipeline contract, and the reproducibility guarantees, not the code. A conformant stdlib-only reference implementation ships with the plugin (see §Reproducibility), but the chosen library and tokenizer stay implementation detail, subject to the pinning and comparability requirements below.
- Acting as a **blocking release gate**: a LIX finding's severity and gate-eligibility are governed by `lektorat` §Severity classification (advisory by default), and this spec adds no blocking behaviour of its own.

## Requirements

### LIX definition (canonical)

- **MUST** compute LIX with the canonical Björnsson formula:

  ```
  LIX = ASL + LWP
        where  ASL = A / B          (average sentence length, words per sentence)
               LWP = (C × 100) / A  (percentage of long words)
               A   = number of words (tokens)
               B   = number of sentences
               C   = number of long words
  ```

  Equivalently, `LIX = A/B + (C × 100)/A`. The result **MUST** be reported as an integer rounded to the nearest whole number; the underlying `ASL`, `LWP`, and the raw `A`, `B`, `C` counts **MUST** be retained at full precision for the finding evidence (§Reproducibility) so an author knows which lever to pull.
- **MUST** define a **long word** as a word of **more than 6 letters** (so, **7 or more**). The threshold is fixed and **MUST NOT** be made configurable; Björnsson chose `> 6` because it maximised the discriminating difference between simple and difficult texts, and a movable threshold would destroy cross-run and cross-repository comparability.
- **MUST** pin the **"letters versus characters" decision** explicitly, because it's the dominant source of EN/DE incomparability and of drift between implementations:
  - A word's length for the long-word test **MUST** be the count of its **Unicode letter characters**, including German `ä ö ü ß` and any accented Latin letters, and **MUST** exclude surrounding or embedded punctuation (the trailing period, commas, quotation marks, parentheses).
  - This deliberately diverges from the naive `len(token)` that some libraries use (for example `textstat` measures `len(w)`), because raw character length lets trailing punctuation and digit groups shift the count at the threshold edge and breaks comparability. An implementation built on such a library **MUST** normalise tokens (strip bounding punctuation) before applying the length test, or document that its library already does so.
- **MUST** treat the following token classes consistently across both languages:
  - **Numbers**: a numeric token (`2026`, `3.14`, `v1.2.0`) counts as one **word** toward `A` and `B`-relative sentence length, and counts as a **long word** only if its letter count exceeds 6—which, since digits aren't letters, means a purely numeric token is **never** a long word. This keeps version strings and dates from inflating `LWP`.
  - **Hyphenated words** (`build-and-test`, `Audience-Doc-Author`): count as **one** token; the long-word test applies to the letter count of the whole token. This matches how a reader parses a single hyphenated concept.
  - **Abbreviations and acronyms**: counted as one token; the long-word test applies to their letter count. Abbreviation-internal periods (`e.g.`, `z. B.`) **MUST NOT** be treated as sentence boundaries (§Word and sentence segmentation).
- **MUST** compute LIX over **prose only**: before scoring, an implementation **MUST** strip the same non-prose elements that [`spec/project/lektorat/`](../lektorat/en.md) §Language handling already strips—fenced code blocks, inline code, HTML comments, YAML frontmatter, and Markdown link / image **targets** (the visible link **text** is prose and is retained)—reusing that stripping so a LIX value reflects what a human reads, not the Markdown scaffolding. Code identifiers and URLs **MUST NOT** contribute to `A`, `B`, or `C`.

### Word and sentence segmentation

- **MUST** pin a **single tokenization-and-sentence-segmentation pipeline** used for **both** English and German, and record it in the run metadata (§Reproducibility). A LIX value is only as reproducible and as cross-language-comparable as the segmenter that produced `A`, `B`, and `C`; two different segmenters on the same text produce different LIX values, so the segmenter is part of the contract, not an implementation free choice.
- **MUST** segment sentences on terminal punctuation (`.`, `!`, `?`) and the colon (`:`) when it introduces an independent clause, consistent with the canonical "number of periods" definition of `B`, while suppressing false boundaries at:
  - known **abbreviations** (`e.g.`, `i.e.`, `etc.`, `z. B.`, `d. h.`, `usw.`, `Dr.`, `Nr.`),
  - **decimal and version numbers** (`3.14`, `v1.2.0`),
  - **ordinals** in German (`1.`, `2.` followed by a lower-case continuation).
- **MUST** treat every **Markdown structural boundary** as a sentence terminator once the structure markers are stripped: a heading, a list item, a table row, and a block-quote line each end a sentence at their line end even without terminal punctuation, and a paragraph break always ends one. Flattened structural text **MUST NOT** concatenate into a synthetic sentence: without this rule, table-heavy reference pages merge rows into enormous pseudo-sentences and score far above their corridor, while a prose-to-bullet-list rewrite that clearly improves human readability *worsens* the measured score because the collapsed list lowers `B` and inflates `ASL`. A structure-heavy page that stays above its corridor even with correct segmentation is the intended use case for the per-file corridor override in [`spec/project/lektorat/`](../lektorat/en.md) §D1, never a reason to distort the counting.
- **SHOULD** prefer a maintained multilingual segmenter (for example `syntok` or `ucto`) over a naive split-on-period, because abbreviation and number handling materially change `B` and therefore `ASL`. When the chosen readability library doesn't segment internally (for example `andreasvc/readability` requires pre-segmented, pre-tokenized input), the upstream segmenter **MUST** be the pinned one and **MUST** be recorded; "the quality of preprocessing affects the validity of the results" is a property of the pipeline, not an excuse to leave it unspecified.
- **MUST** apply byte-for-byte-equivalent stripping and tokenization to the EN and DE files of the same artefact, so a reported EN-versus-DE LIX delta reflects the prose, not a tokenizer asymmetry.

### Score interpretation

- **MUST** anchor interpretation on Björnsson's **five canonical reference points**, treated as **reference points, not band edges**:

  | Reference point | LIX | Reader-facing meaning |
  | --- | --- | --- |
  | Very easy | 20 | Children's books |
  | Easy | 30 | Fiction, popular press |
  | Medium | 40 | Normal newspaper / general non-fiction |
  | Difficult | 50 | Specialist / official prose |
  | Very difficult | 60 | Academic, bureaucratic, dissertation prose |

- **MUST NOT** present any finer-grained "band table" (for example "Very Easy 20–25 / Easy 30–35 / …") as canonical or as attributable to Björnsson; such explicit band edges circulate widely online but **aren't** primary-source-attested (they were refuted in the research that grounds this spec). Only the five reference points above are authoritative; any operative thresholds are this spec's own engineering judgment (§Target corridors), labelled as such.
- **SHOULD** read the corpus calibration from the grounding research as a sanity anchor for the reference points (children's texts ≈ 22, news ≈ 40, encyclopedia ≈ 45, parliamentary prose ≈ 47), not as additional thresholds.

### Cross-language calibration

This section is the **highest-priority caveat** for a bilingual pipeline.

- **MUST** treat a raw LIX value as **language-relative**: the same LIX number **doesn't** denote equal reading difficulty in German and English. German's productive compounding (Komposita) and generally longer words inflate the long-word ratio (`LWP`) even when the words are concrete and easily understood. `Vergrößerungsglas` ("magnifying glass") is one long word but not a difficult one. Morphological length isn't the same as reading difficulty in a compounding language.
- **MUST** compensate for this inflation by setting **German corridors higher than English corridors by a fixed offset Δ**, so that equal *actual* difficulty maps to a higher *raw* German LIX. The default offset is **Δ = 5 LIX points** (engineering judgment). An implementation **MUST** apply Δ via the per-language corridor table in §Target corridors rather than by adjusting a raw score after the fact, so the recorded LIX value stays a faithful measurement and only the *threshold* differs by language.
- **MAY** instead normalise by **decompounding German words before the long-word test** (splitting `Vergrößerungsglas` into `Vergrößerungs` + `Glas` for length counting only, never in the rendered text) as an advanced alternative to the offset. An implementation that does this **MUST** record it in the run metadata, **MUST NOT** combine it with the offset (that would double-correct), and **MUST NOT** alter the rendered prose. The default remains the offset; decompounding is opt-in.
- **MUST** label the Δ = 5 value as **provisional engineering judgment**; the empirically calibrated German-versus-English offset is an Open Question gated on accumulated bilingual audit data.

### Target corridors

The corridors below are **engineering judgment**, anchored on the §Score interpretation reference points (40 = medium, 50 = difficult), reconciled with the existing [`spec/project/lektorat/`](../lektorat/en.md) §D1 German LIX corridors, and offset per §Cross-language calibration (German = English + Δ, Δ = 5). The design intent of the `aim` column is **"comfortable for an educated technical reader without being patronisingly simple."** For technical prose that target sits around the medium-to-difficult reference points (LIX ≈ 40–55), not down at the children's-book end.

- **MUST** declare per-`content_mode`, per-language corridors with three thresholds: `aim` (the convergence target the author writes toward), `warn` (a `warning`-level D1 finding when exceeded), and `crit` (a `critical`-level D1 finding when exceeded):

  | `content_mode` | EN aim / warn / crit | DE aim / warn / crit |
  | --- | --- | --- |
  | `tutorial`, `how-to`, `troubleshooting` | ≤ 40 / > 45 / > 55 | ≤ 45 / > 50 / > 60 |
  | `explanation`, `reference`, `glossary` | ≤ 50 / > 55 / > 65 | ≤ 55 / > 60 / > 70 |
  | blog post (peer-professional) | ≤ 45 / > 50 / > 55 | ≤ 50 / > 55 / > 60 |

- **MUST** keep the German `warn` / `crit` columns **consistent with `lektorat` §D1's existing German LIX corridors** (tutorial group `> 50 / > 60`; explanation/reference/glossary group `> 60 / > 70`); this spec adopts those values verbatim for German and derives the English columns as the German columns minus Δ. When `lektorat` §D1 is updated to reference this spec, the German numbers don't change.
- **MUST** exempt pages whose `content_mode` is `meta` from LIX evaluation entirely, consistent with `lektorat` §D1's meta exemption; navigational prose isn't held to a readability corridor.
- **MUST** select the blog-post row only for artefacts in the blog-post scope (a consumer that adopts [`spec/project/blog-author/`](../blog-author/en.md)); the row is calibrated so a post hitting [`spec/project/post-writing-style/`](../post-writing-style/en.md)'s English Flesch–Kincaid 7–10 target also lands inside the LIX `aim`, keeping the two readability targets mutually consistent rather than competing.
- **MAY** allow a repository to override a corridor per file via the same `lektorat`-local configuration mechanism `lektorat` §D1 already defines (`LIX_warn` / `LIX_crit` keys, named rationale, within ±50 % of the default); this spec adds no second override mechanism.
- **MUST** label the corridor values as **provisional**; portfolio-wide re-calibration is an Open Question gated on at least three Portfolio-Member repositories contributing LIX audit data, mirroring the `lektorat` §D1 corridor-calibration Open Question.

### Improving a LIX score

LIX has exactly **two levers**: average sentence length (`ASL`, the `A/B` term) and the long-word ratio (`LWP`, the `(C × 100)/A` term). Every meaning-preserving improvement moves one or both.

- **MUST** classify each transformation by the lever it moves, and **SHOULD** apply them in the priority order below (highest impact and lowest meaning-risk first):

  | Priority | Transformation | Lever | Notes |
  | --- | --- | --- | --- |
  | 1 | Split a long sentence into two | `ASL` ↓ | Highest-impact, lowest-risk lever; one split can move LIX by several points without touching a single word. |
  | 2 | Remove filler and redundancy: shorten `in order to` to `to`, drop empty openers | `ASL` ↓ | Shortens sentences and improves prose independently. |
  | 3 | Convert nominalisations to verbs ("perform a validation of" → "validate") | `ASL` ↓ and `LWP` ↓ | Moves both levers; almost always a genuine readability gain. |
  | 4 | Prefer active voice over passive | `ASL` ↓ | Usually shortens and clarifies; consistent with `prose-style` voice rules. |
  | 5 | Replace a long word with a shorter exact synonym | `LWP` ↓ | Only when the synonym is genuinely as precise; never trade precision for length. |
  | 6 | Break a German compound where the split reads more naturally | `LWP` ↓ | German-only; high meaning-risk—see anti-gaming rule. |

- **SHOULD** prioritise the **`ASL` lever** for typical technical prose: sentence-splitting and filler-removal are the safest and most reliable way to lower LIX while genuinely improving readability, whereas word-substitution (the `LWP` lever) carries the highest risk of trading precision for a lower number. The relative magnitude of the two levers for a given corpus is an Open Question; the priority ordering is risk-first engineering judgment, not a measured impact ranking.
- **MUST NOT** make an edit whose **only** effect is to lower the metric without improving human readability ("gaming"). Explicitly forbidden:
  - splitting a sentence mid-clause where the break harms comprehension,
  - arbitrarily decompounding an established German technical term so it reads as two words on the page (`Pull-Request` isn't improved by becoming `Pull Request` purely to drop a long word),
  - replacing a precise domain term with a shorter, vaguer word,
  - altering any **protected term** (proper noun, product name, technical identifier, command, or term sourced from the audience artefact or the `lektorat` protected-terms list) to reduce `LWP`.
- **MUST** treat the LIX corridor as serving readability, not the reverse: when the only way to enter the corridor is an edit forbidden above, the correct outcome is to **leave the finding open and surface it to the operator**, not to game the score. This subordination is what keeps the metric honest across the iterative loop.

### Reproducibility

- **MUST** record the LIX computation pipeline in the run's machine-readable output so a value is reproducible and EN/DE-comparable. The pipeline metadata **MUST** carry, per language: the readability library `name` and `version`, the tokenizer/segmenter `name` and `version`, the `long_word_threshold` (always `6`), and whether `decompounding` was applied (boolean, German only). This extends the `pipeline_metadata` block `lektorat` §Outputs already defines rather than introducing a parallel artefact.
- **MUST** record, per file with a LIX finding, the computed `lix` (integer), `asl`, `lwp`, and the raw `words` (`A`), `sentences` (`B`), and `long_words` (`C`) counts in the finding evidence, so the finding is auditable and directs the author to the dominant lever.
- **MUST** validate the implementation against the **canonical formula**, not against a library's documentation string: the widely used `textstat` library ships a **docstring that states a transposed, mathematically wrong formula** (`A/B + A*100/C`) while its executed code is correct—an implementor who copies the docstring will compute the wrong number. A conformance test **MUST** assert that a known fixture text yields the hand-computed canonical LIX.
- **MUST** use the **same library and the same tokenizer** for English and German; using two different implementations reintroduces the incomparability this spec exists to remove.
- **SHOULD** use the **bundled reference implementation** the plugin ships at `scripts/readability_lix.py` (invoked via `${CLAUDE_PLUGIN_ROOT}` so it resolves inside the installed plugin, not the consumer's working tree). It's deliberately stdlib-only (no `pip install` in the consumer repo), applies the stripping, segmentation, and counting rules above identically for both languages, reports `pipeline_metadata.readability` with `library: nolte-readability-lix` and its version, and is pinned by the conformance test `tests/test_readability_lix.py`. A consumer **MAY** substitute another library (for example `textstat` or `andreasvc/readability`) provided it satisfies the canonical-formula and same-implementation requirements above and records its own `library`/`version` in the metadata.

### Relationship to other metrics

- **MUST** treat **LIX as the primary readability metric** for both languages, because its letter-counting design (no syllable counting) is what makes it transferable across EN and DE where Flesch-family metrics, being English-syllable-tuned, aren't.
- **MUST** treat FRE and FKGL (English) and WSTF (German) as **supplementary, advisory signals**: they may be computed and reported alongside LIX (they catch syllable-level density effects LIX is blind to, and they're familiar to authors), but a supplementary-metric reading **MUST NOT** override, escalate, or suppress a LIX-based D1 finding.
- **MUST NOT** gate the iterative improvement loop on a supplementary metric; convergence is defined against the LIX corridor (§Iterative improvement loop). A supplementary metric that disagrees with LIX is surfaced as advisory context, not as a competing target.
- **SHOULD** note that no direct quantitative LIX-versus-WSTF or LIX-versus-FKGL correlation was established in the grounding research; keeping the supplementary metrics is a reasoned hedge (familiarity, syllable-level coverage), not an evidence-backed equivalence, and their continued use is an Open Question.

### Iterative improvement loop

This section defines how LIX participates in the autonomous author ↔ editor cycle owned by [`spec/project/lektorat-auto-revise/`](../lektorat-auto-revise/en.md); it adds LIX-specific inputs and a convergence target to that loop without redefining its routing, bound, or re-audit mechanics.

- **MUST** define the **LIX convergence target** for a file as: the file's LIX is at or below the `warn` threshold of its resolved `content_mode`-and-language corridor (§Target corridors). A file at or below `aim` is comfortably converged; a file between `aim` and `warn` is acceptable; a file above `warn` isn't converged.
- **MUST** include, in the per-file briefing the revise loop composes for an author, the file's current `lix`, `asl`, `lwp`, the resolved corridor (`aim` / `warn` / `crit` for the file's `content_mode` and language), and the **dominant lever** (whichever of `ASL` or `LWP` contributes more distance above the corridor), so each author pass is **directed** at the right lever rather than rewriting blind.
- **MUST** treat a re-audit in which a file's LIX moves from above `warn` to at or below `warn` as **progress**, and a re-audit in which LIX rises as a **regression**, feeding the existing `lektorat-auto-revise` re-audit gate; the per-file pass **bound** and the routing (`audience-doc-author` for documentation, `blog-author` for posts) are unchanged and owned by that spec.
- **MUST** reject, via the existing semantic-preservation and anti-gaming guarantees, any author pass that lowered LIX through a forbidden transformation (§Improving a LIX score); a lower number obtained by gaming **isn't** convergence.

## Acceptance Criteria

- [ ] A fixture text with hand-computed `A`, `B`, `C` produces the exact canonical `LIX = A/B + (C × 100)/A`, rounded to the nearest integer, from the implementation.
- [ ] A word of exactly 6 letters **isn't** counted as a long word; a word of 7 letters **is** (the `> 6` threshold is honoured).
- [ ] A purely numeric token (`2026`, `v1.2.0`) is counted as a word but **never** as a long word.
- [ ] German `ä ö ü ß` and accented Latin letters are counted as letters in the long-word length test (a 7-letter word containing `ü` qualifies).
- [ ] Trailing punctuation on a token **doesn't** change its long-word classification (`Konfiguration,` counts identically to `Konfiguration`).
- [ ] Fenced code blocks, inline code, HTML comments, YAML frontmatter, and Markdown link/image targets **don't** contribute to `A`, `B`, or `C`; visible link text does.
- [ ] An abbreviation-internal period (`e.g.`, `z. B.`) and a decimal/version number (`3.14`, `v1.2.0`) **don't** create a false sentence boundary.
- [ ] The same library and tokenizer/segmenter are used for the EN and DE files of an artefact, and both are recorded in the run's `pipeline_metadata` with name and version.
- [ ] The `pipeline_metadata` records `long_word_threshold: 6` and, for German, a `decompounding` boolean.
- [ ] A German file and an English file of equal *actual* difficulty are held to corridors that differ by the offset Δ (the German `warn`/`crit` exceed the English by 5), per §Target corridors.
- [ ] The German `warn`/`crit` corridor values match `lektorat` §D1's existing German LIX corridors verbatim (tutorial group `> 50 / > 60`; explanation/reference/glossary group `> 60 / > 70`).
- [ ] A page whose `content_mode` is `meta` produces **no** LIX finding.
- [ ] A blog-post artefact is evaluated against the blog-post corridor row, and that row's `aim` contains the LIX value of a post that meets `post-writing-style`'s Flesch–Kincaid 7–10 target.
- [ ] A LIX D1 finding records `lix`, `asl`, `lwp`, and the raw `words`/`sentences`/`long_words` counts in its evidence.
- [ ] An implementation built on `textstat` computes the **canonical** formula, not the transposed formula stated in the `textstat` docstring (a conformance test asserts the fixture value).
- [ ] A supplementary-metric reading (FRE/FKGL/WSTF) never overrides, escalates, or suppresses a LIX-based D1 finding.
- [ ] The per-file briefing the revise loop composes for an author includes the file's `lix`, the resolved corridor, and the dominant lever (`ASL` or `LWP`).
- [ ] An author pass that lowers LIX by altering a protected term, decompounding an established technical term purely to drop a long word, or replacing a precise term with a vaguer shorter one **isn't** accepted as converged.
- [ ] A LIX value moving from above `warn` to at or below `warn` is recorded as progress by the re-audit gate; a rising LIX is recorded as a regression.

## Open Questions

- **What's the empirically calibrated German-versus-English offset Δ?** The compound-inflation effect is established directionally (German scores several points higher for equal difficulty), but the grounding research provided no calibrated number. Δ = 5 is provisional engineering judgment. Revisit when at least three Portfolio-Member repositories with bilingual `docs/en` + `docs/de` trees have accumulated LIX audit data that pairs structurally-parallel EN/DE pages, allowing the mean EN-versus-DE LIX delta on equal-difficulty content to be measured. Until then, Δ = 5 stands.
- **Are the per-content-type corridors right for a technical-professional audience?** The grounding research yielded Björnsson's generic five-point scale and corpus means (news ≈ 40, encyclopedia ≈ 45) but no text-type-specific recommendation for technical-professional readers. The corridors are anchored on those points and reconciled with `lektorat`'s existing German values. Revisit jointly with the `lektorat` §D1 corridor-calibration Open Question once three repos contribute audit data.
- **Which lever moves LIX more for typical technical prose, `ASL` or `LWP`?** The priority ordering in §Improving a LIX score is risk-first engineering judgment, not a measured impact ranking. Revisit when an audit corpus large enough to regress LIX delta against per-edit lever attribution exists.
- **Should decompounding-before-scoring replace the offset as the default German normalisation?** It's offered as an opt-in alternative. Revisit when a maintained German decompounder has been evaluated against the offset on the same bilingual corpus and shown to track human-judged difficulty more closely.
- **Should the supplementary metrics (FRE/FKGL/WSTF) be retired once LIX is the cross-language primary?** No direct LIX-versus-WSTF/FKGL correlation was established, so the supplementary metrics are kept as a hedge. Revisit when accumulated audit data shows whether they ever surface a readability problem LIX missed; if they never diverge usefully, retire them to reduce pipeline surface.

## Sources

<!-- Authoritative external references the requirements above were validated against; verified via a fact-checked deep-research pass (23 of 25 extracted claims confirmed, 2 refuted). -->

- Björnsson, C. H. (1968). *Läsbarhet.* Stockholm: Liber.—Defines LIX (`LIX = A/B + (C × 100)/A`), the `> 6`-letter long-word threshold (chosen for maximal discrimination, p. 217), and the five interpretation reference points (very easy 20 … very difficult 60, p. 89).
- Anderson, J. (1981). *Analysing the readability of English and non-English texts in the classroom with Lix.* ERIC ED207022.—Step-by-step LIX procedure; cross-language correlation studies (French/English, German/English, Greek/English) showing preserved relative difficulty ranking across translated parallel texts; states that language-specific norms are necessary and that the cross-language research base is preliminary.
- Anderson, J. (1983). *Lix and Rix: Variations on a little-known readability index.* Journal of Reading 26(6), 490–496.—The letter-counting (not syllable-counting) design that makes LIX/RIX suitable for non-English languages.
- *Cross-lingual readability assessment* (2024). arXiv:2404.01196.—Formula restatement (`A` = tokens, `B` = sentences, `C` = words with > 6 letters); the compound-word inflation caveat (a morphologically complex compound such as *forstørrelsesglass* / German *Vergrößerungsglas* is long but not difficult); corpus calibration (children ≈ 22, news ≈ 40, encyclopedia ≈ 45, parliament ≈ 47).
- `textstat` source—[`_lix.py`](https://github.com/textstat/textstat/blob/main/textstat/backend/metrics/_lix.py) and [`_count_long_words.py`](https://github.com/textstat/textstat/blob/main/textstat/backend/counts/_count_long_words.py).—Correct executed formula (`asl + 100 × long_words / words`, long word = `len(w) > 6`) **but a transposed, wrong docstring** (`A/B + A*100/C`): validate against the formula, not the docstring.
- `andreasvc/readability`—[PyPI](https://pypi.org/project/readability/) / [GitHub](https://github.com/andreasvc/readability).—Computes LIX and RIX for English, German, and Dutch in one library, but **doesn't** tokenize or sentence-segment internally; requires pre-segmented input, so the upstream segmenter must be pinned.
- *Lix (readability test)*—[Wikipedia](https://en.wikipedia.org/wiki/Lix_(readability_test)).—Restates the formula and the "number of periods" definition of `B` (period, colon, or capital first letter as boundary).
- Flesch, R. (1948); Kincaid et al. (1975); Bamberger & Vanecek (1984).—Definitions of the supplementary metrics (FRE, FKGL, WSTF) kept as advisory signals per §Relationship to other metrics; consumed via [`spec/project/lektorat/`](../lektorat/en.md).
