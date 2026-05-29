# Lektorat

Status: draft

## Context

Portfolio repositories already enforce a mechanical prose baseline: [`spec/project/prose-style/`](../prose-style/en.md) wires Vale (Microsoft + RedHat + `nolte/vale-style`) across every English-scoped Markdown surface, and [`spec/project/docs-multilingual-authoring/`](../docs-multilingual-authoring/en.md) guarantees that DE/EN page trees stay structurally parallel. What neither spec answers is the **editorial** question once a draft exists: is the page actually **readable** for its audience, does it **make sense without hidden prerequisites**, is the **German** side spelled correctly, and does the **tone** match the audience the document was written for?

`Lektorat` (editorial review) closes that gap. It's the operative layer that **audits, patches, or revises** already-existing prose against four quality dimensions—readability, comprehensibility, spelling/grammar, writing style—plus a fifth **audience-fit** dimension that ties the prose back to the audience artefact produced by [`spec/project/audience-identification/`](../audience-identification/en.md) and the per-page track contract from [`spec/project/docs-audience-tracks/`](../docs-audience-tracks/en.md). Vale stays responsible for its rule mechanics; `audience-doc-author` stays responsible for first authorship; this spec defines what happens **after** a text exists and **before** it's treated as finished work.

Two design constraints shape the spec. First, the layer is **operative**, not descriptive: it mandates three operations (`audit`, `patch`, `revise`) with explicit pre- and postconditions, so a downstream skill and agent can implement the contract without re-litigating semantics. Second, the layer is **per-language**: each language file is reviewed against the rules of its own language (DE-rules on DE-text, EN-rules on EN-text), and translation synchronisation remains the responsibility of `spec` and `docs-freshness`.

**Readers** of this spec are implementors of the `lektorat-apply` skill and `lektorat-scanner` agent (primary) and operators invoking `audit` / `patch` / `revise` from CI, sprint-review, or release-publish gates (secondary). Familiarity with `spec/project/mkdocs-structure/` (the `content_mode` enum), `spec/project/audience-identification/` (the audience artefact), and `spec/project/docs-audience-tracks/` (the per-page `audience` / `track` frontmatter) is assumed; terms drawn from those specs are used without restatement.

## Goals

- Existing human-readable prose in this repository (and in consumer repositories that adopt the spec) can be reviewed and revised against a stable, named set of editorial quality dimensions without re-implementing the rules per skill
- Skills and agents that perform editorial work distinguish three operations (`audit` for read-only inspection, `patch` for per-finding edits with explicit approval, `revise` for full-document overhauls with diff review), and the operation chosen is visible in their output
- Editorial findings are reproducibly classified by **severity** (`critical` / `warning` / `suggestion`) so a downstream gate (CI, sprint-review, release-publish) can decide what blocks and what's advisory
- Readability and comprehensibility findings reference **named metrics with per-language target corridors**, so a finding is auditable rather than a stylistic opinion
- Audience-fit is checked against the **audience artefact** the repository already produces, not against an ad-hoc audience guess invented per review
- DE-text and EN-text are checked with **language-appropriate mechanics**; the DE pipeline doesn't depend on Vale, which `prose-style` scopes to English only
- The boundary against `prose-style` (rule mechanics), `audience-doc-author` (first authorship), `docs-freshness` (drift detection), and `spec` (translation synchronisation) is sharp enough that no requirement is restated in two specs

## Non-Goals

- Defining or maintaining the Vale configuration, the Vale vocabulary, or the prose rule mechanics—that's owned by [`spec/project/prose-style/`](../prose-style/en.md) and the upstream package at [`nolte/vale-style`](https://github.com/nolte/vale-style)
- First authorship of new pages—that's owned by the `audience-doc-author` agent and its triggering skills (`readme-structure-apply`, `audience-doc-author` itself); `Lektorat` operates on prose that already exists
- Translating prose from one language into another—that's owned by the `spec` skill (for `spec/` content), by `docs-multilingual-authoring` (for atomic per-page DE/EN parity), and by `audience-doc-author` (for new pages); `Lektorat` reviews each language independently
- Synchronising parity between DE and EN versions of the same artefact—that's owned by `docs-freshness` (audit-time detection) and `docs-multilingual-authoring` (authoring-time prevention)
- Lektoring source code, code comments, docstrings, API reference text, generated manifests, generated configs, or YAML/JSON config bodies; the layer reviews prose **in Markdown** and treats fenced code blocks as untouchable
- Lektoring files under `spec/`: they follow the `spec` skill's translation flow and have their own authoritative drift checks; including them here would create a second source of truth for spec prose
- Vale-rule authoring (active-voice detector, gendered-pronoun detector, and similar): `prose-style` already lists this as a deferred decision and `Lektorat` doesn't pre-empt it
- Slack messages, wiki pages, blog posts, or other non-Markdown human-facing prose surfaces: `Lektorat` covers GitHub Issue and pull-request bodies as a deliberate scope extension (they're user-visible Markdown that flows into search engines and project history). Note that `prose-style` §Pull-request descriptions and release notes already mandates Vale coverage on EN PR bodies and EN release-note bodies; `Lektorat` adds **no** coverage there but extends it with the D1/D2/D5 dimensions and the DE pipeline. Findings from `prose-style`'s Vale CI gate are deduplicated by Vale rule ID per §Coordination with neighbouring specs. Other prose surfaces remain out of scope until separately specified
- A blocking gate for editorial findings of severity `suggestion`; only `critical` findings are gate-eligible, and even then opt-in per repository (see §Severity classification)

## Requirements

### Scope and applicability

- **MUST** treat any of the following artefact types as **in scope** for `Lektorat`: MkDocs pages under `docs/<lang>/` (excluding `_`-prefixed snippet folders, which are reviewed with their hosting page), top-level repository Markdown (`README.md`, `ONBOARDING.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `SECURITY.md`), the body of GitHub Releases (release notes), and the body of GitHub Issues and pull requests
- **MUST NOT** include any file under `spec/` in `Lektorat` scope; spec prose is governed by the `spec` skill's authoritative flow and its translation-sync rules. A finding that would require editing a spec file is a finding **against the calling skill's instructions**, not against the spec
- **MUST NOT** include source code, code comments, docstrings, generated configuration (`.github/*.yml` produced by `project-structure-apply`, `mkdocs.yml`, `Taskfile.yml`, lockfiles), LLM-instruction artefacts (`skills/**/SKILL.md`, `skills/**/templates/**`, `skills/**/examples/**`, `agents/*.md`), or any binary artefact in `Lektorat` scope
- **MUST** treat fenced code blocks (```` ``` ```` … ```` ``` ````), inline code (`` ` `` … `` ` ``), HTML comments (`<!-- … -->`), and YAML frontmatter (` --- … --- ` at the head of the file) as **read-only**: the layer reads them for context but **MUST NOT** rewrite, reformat, or annotate them
- **MUST** allow a repository to narrow the in-scope set via a `Lektorat`-local configuration (path globs, artefact-type allow-list) but **MUST NOT** allow a repository to widen the scope to include any artefact type that the spec explicitly forbids above

### Quality dimensions

The five dimensions below are the **authoritative** list. Each finding produced by a `Lektorat` operation **MUST** name exactly one dimension. The severities map to a dimension-specific rubric defined under §Severity classification.

#### D1—Readability

- **MUST** evaluate readability against named metrics with explicit per-language target corridors:
  - **English text**: Flesch Reading Ease (FRE) and Flesch–Kincaid Grade Level (FKGL)
  - **German text**: Wiener Sachtextformel (WSTF) variant 1 and LIX
- **MUST** declare per-`content_mode` target corridors so a `tutorial` page isn't held to the same density as a `reference` page; the default corridors are:

  | `content_mode` (per `spec/project/mkdocs-structure/`) | EN: FRE warn / crit | EN: FKGL warn / crit | DE: WSTF warn / crit | DE: LIX warn / crit |
  | --- | --- | --- | --- | --- |
  | `tutorial`, `how-to`, `troubleshooting` | < 60 / < 45 | > 10 / > 14 | > 7 / > 10 | > 50 / > 60 |
  | `explanation`, `reference`, `glossary` | < 45 / < 30 | > 14 / > 18 | > 10 / > 13 | > 60 / > 70 |

  The `crit` column is derived by extending the `warn` bound by one **corridor width** (the absolute gap between the two `content_mode` rows for the same metric): FRE width = 15, FKGL width = 4, WSTF width = 3, LIX width = 10. The `crit` thresholds above are the operative values; the derivation is documented so a future content-mode row can be added consistently.

- **MUST** classify a metric whose value crosses the `warn` threshold (but not the `crit` threshold) as a `warning` finding, and a metric whose value crosses the `crit` threshold as a `critical` finding; thresholds are read from the per-`content_mode` row above
- **MUST NOT** apply D1 evaluation to a page whose `content_mode` is `meta` (per `spec/project/mkdocs-structure/`); meta pages (Home, per-section index) are exempt from readability metrics because their prose is navigational rather than instructional, and no corridor row applies
- **MUST** report the computed metric value, the corridor, and at least one offending sample (longest sentence, deepest nesting) so the finding is auditable
- **MUST NOT** rewrite a passage on readability grounds alone in `patch` mode without a metric value or a named heuristic citation in the finding; an opinion isn't a finding
- **SHOULD** complement metric findings with **structural heuristics** (paragraphs longer than three sentences, lists with more than seven peers, headings deeper than `####`)—these are `suggestion`-level by default
- **SHOULD** compute the named metrics by consuming a maintained per-language readability library (a `textstat`-class library for English, a `readability-de`-class library for German) rather than re-implementing the classic formulas; the spec constrains only the metric names and the corridors above, not the implementation, and the chosen library **MAY** be recorded alongside the pipeline metadata (§Outputs) for reproducibility

#### D2—Comprehensibility

- **MUST** detect and flag the following patterns as comprehensibility findings:
  - **Jargon load**: a domain term appearing without prior definition, where "domain term" covers anything outside the project's audience-appropriate base vocabulary (per §Audience binding)
  - **Unexplained abbreviations**: an abbreviation (`SRE`, `RTO`, `CSP`) appearing without expansion on first use in the page
  - **Hidden prerequisites**: an instruction or claim that depends on an earlier file, an environment state, or a tool that's not mentioned on the current page
  - **Implicit assumptions**: a sentence that presumes the reader's role, tooling, or background without saying so (typical markers: "simply," "just," "as everyone knows")
- **MUST** classify each D2 pattern with the default severity below, escalating only via the stated rule. The base severity bucket vocabulary is `critical` / `warning` / `suggestion` per §Severity classification; this table is the per-pattern resolution and is what implementations apply:

  | D2 pattern | Default severity | Escalation |
  | --- | --- | --- |
  | Jargon load | `warning` | `critical` when the artefact is a published surface (`README.md`, release-note body, top-level docs) **and** the resolved audience includes a non-operator role |
  | Unexplained abbreviations | `warning` | `critical` when the abbreviation appears in a heading, the first paragraph, or a callout (the page's load-bearing surfaces) |
  | Hidden prerequisites | `warning` | `critical` on pages whose `content_mode` is `tutorial` or `how-to` (the prerequisite would block the reader) |
  | Implicit assumptions | `suggestion` | `warning` when the marker word (“simply,” “just,” “obviously”) is paired with a step the reader must execute |

- **MUST** prefer the **add-context** patch (one short sentence, one inline expansion) over the **delete-jargon** patch when a domain term is genuinely load-bearing; comprehensibility findings aren't licence to strip technical precision
- **MUST NOT** flag a term that's glossed elsewhere in the page (definition list, prior section, inline parenthetical) as a comprehensibility finding

#### D3—Spelling and grammar

- **MUST** apply **language-specific** spelling and grammar checks:
  - **English text**—defer to the Vale-driven mechanics already governed by `prose-style`; `Lektorat` does **not** re-implement spelling/grammar for English, it consumes Vale's output and surfaces it as `D3` findings in the unified report
  - **German text**—apply a `Lektorat`-owned DE pipeline (portfolio default: LanguageTool HTTP API; see §Language handling) because `prose-style` explicitly scopes Vale to English only and a DE alternative isn't available portfolio-wide
- **MUST** protect **proper nouns, product names, technical identifiers, command names, file paths, URLs, and project-specific jargon** from spelling correction by sourcing the protected set from the audience artefact and the `nolte/vale-style` vocabulary (for English) or from the `Lektorat`-local protected-terms list (for German)
- **MUST** classify a spelling or grammar finding as `critical` when it would change rendered meaning or is visible in a published artefact (release-note body, README, top-level docs), and as `warning` otherwise
- **MUST NOT** correct a spelling that the audience artefact or the protected-terms list marks as intentional (a brand name, a product spelling, a deliberate stylisation)

#### D4—Writing style

- **MUST** evaluate writing style against the **applicable** subset of `prose-style` §Voice and tone for English text; the rules listed there are authoritative and `Lektorat` doesn't redefine them
- **MUST** apply analogous rules to German text (active voice by default, present tense for system behaviour, sentence-case headings, “Sie”-Anrede on tutorial/how-to/troubleshooting pages and impersonal on reference/explanation/glossary, no gendered generic constructs); a violation is a `warning` by default and a `critical` finding when it would change the document's register against its declared audience
- **MUST** detect and flag **inconsistency within the same artefact** as a `warning`: mixed voice (active/passive flip-flop), mixed tense (present/future flip-flop), mixed address (`du`/`Sie` flip-flop on the same page), mixed capitalisation in headings—internal consistency is more important than the choice itself
- **MAY** offer a style-rewrite suggestion in `patch` mode that flips the entire artefact to one consistent posture, with an explicit before/after diff

#### D5—Audience-fit

- **MUST** resolve the artefact's **declared audience** from the page's frontmatter (`audience` key for MkDocs pages per `docs-audience-tracks`) or, when no frontmatter exists, from the artefact-type defaults defined under §Audience binding below
- **MUST** read the **audience artefact** produced by `audience-identification` from its canonical location (`AUDIENCES.md` at the bounded-context root per `audience-identification` §Requirements, or the alternative location declared there—README section "## Audiences" / "## Intended consumers" or an ADR) and use it as the **authoritative description** of what each audience does and doesn't understand; `Lektorat` **MUST NOT** invent audience properties not present in the artefact
- **MUST** flag audience-fit findings under the following patterns:
  - **Register mismatch**: an instructional page targeted at end-users that uses operator-internal jargon (or vice-versa)
  - **Missing audience-required content**: an artefact whose declared audience expects a specific section (per `docs-audience-tracks` content blocks) that's absent or empty
  - **Wrong-audience content**: a section that targets an audience the page doesn't declare (typical: a contributor-oriented appendix on an end-user quickstart)
- **MUST** classify register mismatch and missing audience-required content as `critical` for any artefact whose declared audience includes a non-operator audience (end-users, customers, evaluators); a documentation gap that a paying consumer notices isn't a `suggestion`
- **MUST NOT** rewrite content to match a different audience than the one declared; the resolution for a wrong-audience section is to **flag it for the operator to move**, not to silently re-frame the section

### Severity classification

- **MUST** classify every finding into one of exactly three severities:
  - `critical`: would change rendered meaning, is visible in a published artefact, or fails the audience-fit gate above
  - `warning`: fails a named metric corridor, fails a `prose-style` MUST that didn't flip into `critical`, or breaks internal consistency
  - `suggestion`: qualifies a heuristic, proposes a stylistic refinement, or expands a sentence for clarity without changing meaning
- **MUST** use these severity names verbatim in machine-readable output (JSON keys, frontmatter values, CLI exit-code mapping); `info`, `error`, `notice`, and similar synonyms are **MUST NOT**
- **MUST** keep severity classification **dimension-aware**: a D3 misspelling in a published release note is `critical`, the same misspelling in a draft Markdown comment is `warning`, the same misspelling inside a code identifier produces **no finding** (out of scope per §Scope and applicability)
- **MUST** treat `critical` findings as **advisory by default** in downstream gates (`sprint-review`, `release-publish-trigger`): a `critical` finding **MUST NOT** block a sprint review or a release on its own. A repository **MAY** opt into blocking on `critical` via a `Lektorat`-local flag, mirroring how `docs-freshness` surfaces findings without blocking releases. The portfolio-wide promotion of `critical` from advisory to blocking is a tracked follow-up, gated on the first quarter of accumulated audit data, and isn't yet in force

### Operations

The `Lektorat` layer **MUST** distinguish exactly three operations. The names below are the **only** legal operation names in machine-readable output.

#### Operation A: `audit`

- **MUST** be **read-only**; the operation **MUST NOT** write to any in-scope artefact, **MUST NOT** edit any other file, and **MUST NOT** dispatch any tool that mutates repository state
- **MUST** produce a **structured findings report** (§Outputs) sorted by severity (`critical` first, then `warning`, then `suggestion`) and within severity by source path then dimension
- **MUST** complete without user interaction (no mid-flow approvals, no questions) so it can be invoked from CI, pre-commit, sprint-review, and release-publish gates
- **MUST** be **deterministic for the same input**: re-running `audit` on the same artefact set with the same configuration produces the same findings (ordering identical, severities identical, metric values within ±1 for floating-point computations)

#### Operation B: `patch`

- **MUST** apply at most **one finding's** resolution per approval cycle; the operator is shown the finding, the proposed edit (as a unified diff), and **MUST** approve before the edit lands on disk
- **MUST** preserve every aspect of the artefact not covered by the approved finding: surrounding paragraphs, frontmatter, code blocks, link targets, heading IDs, file-relative paths
- **MUST NOT** silently combine multiple findings into a single edit; a multi-finding fix is a sequence of `patch` operations, not a single one
- **MUST** offer a "skip" and a "skip-and-record" path so the operator can defer or permanently dismiss a finding, with the dismissal recorded so future `audit` runs don't re-surface it
- **SHOULD** present findings to the operator in severity order so `critical` items are handled first

#### Operation C: `revise`

- **MUST** rewrite the **full artefact** in one pass, addressing every `critical` and `warning` finding the prior `audit` produced; `suggestion` findings are optional and **SHOULD** be addressed when adopting them doesn't extend the rewrite scope
- **MUST** produce a **unified diff** of the proposed full-artefact rewrite and **MUST NOT** write the rewrite to disk until the operator explicitly approves the diff
- **MUST** preserve **semantic content**: every fact, every claim, every command, every identifier, every link target, every frontmatter key, every code block from the original artefact **MUST** still be present in the rewrite, with at most lexical changes (active voice, shorter sentences, lifted prerequisites)
- **MUST NOT** delete a section, drop a list item, drop a checklist entry, drop a table row, or change a code block; structural deletions are out of scope for `revise` and are a separate operator decision
- **MUST NOT** introduce new factual content (new commands, new file paths, new product names, new URLs) that wasn't present in the original; if the prose required an addition, the operation **MUST** surface a `suggestion` to the operator and stop
- **MUST** re-run `audit` on the rewritten artefact and surface any **new** findings the rewrite introduced; if the post-`revise` `audit` shows more total findings than the pre-`revise` `audit`, the operation is a **regression** and the operator **MUST** be told before the diff is approved

### Audience binding

- **MUST** read the **audience artefact** produced by `audience-identification` from its canonical location (`AUDIENCES.md` at the bounded-context root per `audience-identification` §Requirements) or one of the alternative locations that spec declares (a README section "## Audiences" / "## Intended consumers," or an ADR); when no such artefact exists at any of these locations, `Lektorat` **MUST** stop with a single-sentence error pointing at the `audience-identify` skill rather than guess audiences
- **MUST** resolve each artefact's **applicable audiences** as follows (in priority order):
  1. Page frontmatter `audience:` value (one or more audience IDs from the artefact)—for MkDocs pages with `docs-audience-tracks` frontmatter applied
  2. Artefact-type defaults derived from the `track` field that `audience-identification` §Requirements mandates on every audience entry:
     - `README.md` → every audience listed in the artefact (the README is the universal entry point and serves every reader category)
     - `ONBOARDING.md`, `CONTRIBUTING.md`, GitHub Issue bodies, GitHub pull-request bodies → audiences whose `track` is `developer-docs` (typically contributors, operators, maintainers, release-managers)
     - GitHub Release-note bodies → the audiences enumerated by `spec/project/release-notes-audience-analysis/`, which is the authoritative resolver for that surface
     - `SECURITY.md`, `CHANGELOG.md` → every audience listed in the artefact (both surfaces target every reader)
  3. The **whole audience set** declared in the artefact—for any in-scope artefact that the prior two rules don't match
- **MUST** treat `audience` values as **stable identifiers** across languages; an audience ID never gets localised (matches `docs-multilingual-authoring` §Structural parity of the translation)
- **MAY** dispatch the `audience-review` agent to obtain a **second-line read** on whether an artefact's declared audience set is still appropriate (for example, when a `D5` register-mismatch finding suggests the declared audience is the wrong one); the dispatch is **opt-in** per repository and the agent's output is advisory

### Language handling

- **MUST** select the rule set **per file** based on the file's language, resolved in this priority:
  1. Path segment under `docs/<lang>/`—`docs/en/foo.md` is English, `docs/de/foo.md` is German
  2. Suffix convention: `foo.en.md` is English, `foo.de.md` is German
  3. Repository default declared in `spec/.spec-config.yml` (`canonical_language`): for top-level Markdown without a language segment (`README.md` typically resolves to the canonical language)
  4. As a last resort, the operator chooses interactively; `Lektorat` **MUST NOT** autodetect language from text content for scope decisions
- **MUST** apply **English-only mechanics** (Vale, prose-style §Voice and tone, FRE/FKGL) to English-resolved files and **German-only mechanics** (DE spelling/grammar pipeline, WSTF/LIX, German-tone heuristics) to German-resolved files
- **MUST** protect the following classes from any language-mechanics correction in any operation: code blocks (per §Scope and applicability), inline code, URL targets, command-line invocations, file paths, identifier-like tokens (`camelCase`, `snake_case`, `kebab-case` runs that are visibly identifiers), product names declared in the audience artefact or the protected-terms list, and proper nouns sourced from those same lists
- **MUST NOT** rewrite a non-English passage inside an English-resolved file or vice versa; such a passage is a finding (`D3` for spelling, `D5` for register), and the resolution is **flagged for the operator**, not silently fixed
- **MUST** record the chosen DE pipeline in the `Lektorat`-local configuration as `{tool: <name>, version: <version>, configured_path: <endpoint-or-binary-path>}` so the operator can reproduce a run; the **portfolio default** is the **LanguageTool HTTP API** (`tool: "languagetool-http"`, with `configured_path` pointing at either the Public endpoint `https://api.languagetool.org/v2` or a self-hosted deployment of the same engine—the API contract is identical). A repository **MAY** override the default by pinning an alternative tool in its `Lektorat`-local configuration; the load-bearing contract is the JSON output shape declared in §Outputs, not the tool identity

### Refactor safety

- **MUST** preserve the **literal text of any block-quoted citation** (`> …`) and the **literal text of any HTML-comment marker** (`<!-- … -->`) across every operation; both classes are off-limits for paraphrasing
- **MUST** preserve **link text and link target** of every Markdown link unless the finding's resolution explicitly proposes a link change; the default safe path is `[text](target)` → `[text](target)` byte-identical
- **MUST** preserve **heading IDs** (the slug MkDocs derives from heading text); when a finding requires a heading text change, the operation **MUST** surface that the heading's slug will change and ask the operator to confirm—slug churn breaks deep links from other pages
- **MUST** preserve **frontmatter key set and key order**; values may be edited only by an operation whose finding explicitly targets a frontmatter value (typically a `D5` audience-binding finding)
- **MUST** preserve **embedded include directives** of `mkdocs-include-markdown-plugin` byte-identical; the included source is reviewed when its own file is in scope, not through the consumer
- **MUST NOT** reorder, merge, or split list items in any operation; lexical edits inside a bullet are allowed, structural edits across bullets aren't
- **MUST NOT** introduce or remove blank lines that change Markdown rendering (separator between paragraphs and lists, separator between heading and following content)

### Outputs

#### Findings report (machine-readable)

- **MUST** emit a findings report in **JSON** alongside any operation that produces findings (`audit` always, `patch` and `revise` for the pre-`audit` and post-`audit` they wrap)
- **MUST** use this top-level shape:

  ```json
  {
    "operation": "audit",
    "operation_version": "1",
    "repository": "<short repo identifier>",
    "ran_at": "<RFC 3339 UTC timestamp>",
    "language_summary": [{"language": "en", "files": 12}, {"language": "de", "files": 11}],
    "pipeline_metadata": {
      "en": {
        "tool": "vale",
        "version": "<output of `vale --version`>",
        "configured_path": "<repo-relative path to the active .vale.ini or vale.yml>"
      },
      "de": {
        "tool": "languagetool-http",
        "version": "<value of LanguageTool /v2/info `buildDate` or the self-hosted release tag>",
        "configured_path": "<HTTP endpoint URL (Public or self-hosted) or, for an alternative tool, the resolved binary path>"
      }
    },
    "inventory_findings": [
      {
        "kind": "vale-unavailable|language-pipeline-missing|language-ambiguous|content-mode-missing|audience-artefact-missing",
        "language": "en|de|null",
        "file": "<repo-relative path, or null when the condition is repository-wide>",
        "message": "<one-sentence operator-facing description, ≤ 240 chars>"
      }
    ],
    "findings": [
      {
        "id": "<stable hash of file + dimension + line>",
        "severity": "critical|warning|suggestion",
        "dimension": "D1|D2|D3|D4|D5",
        "file": "<repo-relative path>",
        "line_start": 1,
        "line_end": 1,
        "message": "<one-sentence finding>",
        "rule": "<rule or metric identifier>",
        "language": "en|de",
        "audience": ["<audience id>", "..."],
        "evidence": "<offending sample, ≤ 240 chars>",
        "suggested_resolution": "<one-line operator hint, ≤ 240 chars>"
      }
    ]
  }
  ```

- **MUST** populate `pipeline_metadata.<language>` for every language present in `language_summary` whose pipeline could be resolved; the three sub-fields `tool`, `version`, and `configured_path` are all required and load-bearing for the reproducibility Acceptance Criterion. Placeholder values are forbidden: when one of the three can't be resolved (for example the binary is missing), the corresponding `pipeline_metadata.<language>` block is **omitted** and the scan condition is recorded in `inventory_findings` instead (see below)
- **MUST** surface every infrastructure-level scan condition in the `inventory_findings` array, **never** in `findings`. The `findings` array carries only editorial findings classified under the closed severity set (`critical` / `warning` / `suggestion`) of §Severity classification; `inventory_findings` carries pre-evaluation conditions that prevented part of the scan from completing. The `kind` field is a closed enumeration with exactly these five values:
  - `vale-unavailable`: Vale binary not callable but English files are in scope; D3/D4 EN mechanics are skipped. `file: null`.
  - `language-pipeline-missing`: German files are in scope but no DE pipeline config was passed (or the configured endpoint/binary isn't callable); D3 for the affected file is skipped. `file` names the affected file; emit one entry per affected file.
  - `language-ambiguous`: the language-resolution priority chain (see §Language handling) can't resolve the file; the operator decides interactively. `file` names the affected file.
  - `content-mode-missing`: the file has no `content_mode` in the caller-supplied map; D1 for that file is skipped (`meta`-exemption depends on a known mode). `file` names the affected file.
  - `audience-artefact-missing`: the audience artefact path resolves to nothing; D5 is skipped for every file in the scope. `file: null`.
- **MUST NOT** introduce any further `kind` value without first amending this spec; an unknown `kind` in `inventory_findings` is a spec-conformance violation, not an extension point
- **MUST** keep `id` stable across runs for the same finding on the same file/line/dimension so a dismissal can be recorded by `id`
- **MUST** also emit a **human-readable** Markdown summary (severity-sorted) for operator review; the JSON is for machines, the Markdown is for humans
- **SHOULD** write both outputs under `.audits/lektorat/<YYYY-MM-DD-HHMM>/` so a repository accumulates a reviewable audit trail (mirrors `spec/project/spec-drift-audit/` and similar layered audits)
- The `.audits/lektorat/` JSON is the **contract**; rendering findings as **pull-request-line annotations** (or CI annotations) is explicitly **out of scope** for this spec and is a downstream CI/rendering decision layered over that JSON, consistent with how the portfolio's other audit specs treat their on-disk audit trail as the deliverable

#### Edit diff (for `patch` and `revise`)

- **MUST** present every proposed edit as a **unified diff** against the on-disk artefact, with at least three context lines, before any write
- **MUST NOT** combine a `patch` edit with a `revise` edit in a single diff; one operation, one diff
- **MUST** label the diff with the operation name, the finding IDs it addresses, and the affected file's repo-relative path

### Skill and agent distribution (recommendation)

The spec deliberately leaves the exact implementation shape **open**, but **SHOULD** be implemented as the following split, mirroring the portfolio's hybrid pattern (for example `dependency-audit` skill + `dependency-audit-scanner` agent, `vocab-drift-audit` skill + `vocab-drift-scanner` agent):

- **`lektorat-apply` skill**—user-facing entry point; orchestrates `audit` / `patch` / `revise`; owns all operator dialogue (approvals, dismissals, language disambiguation); composes the final outputs; never reads source files itself for the audit step
- **`lektorat-scanner` agent**—read-only scanner; performs D1–D5 detection across one or more in-scope artefacts; returns the structured findings inventory the skill renders; never edits, never asks
- The skill **MAY** dispatch the existing `prose-vale-curator` agent for D3/D4 mechanics on English text and the `audience-review` agent for advisory D5 second-line reads; both dispatches are **opt-in** per repository

### Coordination with neighbouring specs

- **MUST** reference `spec/project/prose-style/` as the authoritative source of EN voice/tone rules and Vale mechanics; `Lektorat` consumes them and **MUST NOT** redefine them
- **MUST** reference `spec/project/audience-identification/` as the authoritative source of audience identifiers and audience properties; `Lektorat` reads the artefact and **MUST NOT** invent audiences
- **MUST** reference `spec/project/docs-audience-tracks/` for the per-page `audience` / `track` / `content_mode` frontmatter contract; `Lektorat` resolves applicable audiences through that contract
- **MUST** reference `spec/project/mkdocs-structure/` for the `content_mode` enum that drives readability corridors and for the `_`-prefixed snippet-folder convention
- **MUST** reference `spec/project/docs-multilingual-authoring/` for the cross-language parity contract; `Lektorat` **MUST NOT** synchronise translations
- **MUST** reference `spec/project/docs-freshness/` for cross-language drift detection; `Lektorat` **MUST NOT** detect parity drift
- **MUST** treat any D3 or D4 finding on **any EN file in `prose-style`'s Vale lint scope** (top-level Markdown, `docs/en/` pages, EN PR bodies, EN release-note bodies) that `prose-style`'s Vale CI gate has already surfaced—identified by the `rule` field carrying the Vale rule ID—as consumed; `Lektorat` **MUST NOT** re-surface the same Vale-rule-ID finding for the same file as a new finding of its own. Deduplication is one-way: Vale gates the prose first, `Lektorat` adds the D1/D2/D5 dimensions and the DE-side D3/D4 mechanics on top
- **MUST NOT** override, relax, or duplicate any MUST declared in the specs above; conflicts are resolved by amending the upstream spec, not by exception in `Lektorat`

## Acceptance Criteria

- [ ] `spec/.spec-config.yml` languages list is read by every `Lektorat` operation and drives the file-to-language resolution under §Language handling
- [ ] An `audit` invocation against a representative bilingual repository produces a JSON report whose shape matches §Outputs verbatim (top-level keys, finding-object keys, severity values from the closed set)
- [ ] An `audit` invocation produces a Markdown summary alongside the JSON, sorted by severity (`critical` first), and writes both to `.audits/lektorat/<YYYY-MM-DD-HHMM>/`
- [ ] An `audit` invocation completes without any operator interaction (suitable for CI / pre-commit / sprint-review gates)
- [ ] Re-running the same `audit` invocation produces a byte-identical JSON `findings` array (modulo `ran_at`) on an unchanged repository
- [ ] An English file produces at least one D1 finding when Flesch Reading Ease drops below its content-mode corridor, with the metric value and corridor included in the finding
- [ ] A German file produces at least one D1 finding when WSTF exceeds its content-mode corridor, with the metric value and corridor included in the finding
- [ ] A page whose `content_mode` is `meta` does **not** produce a D1 finding (the meta exemption is honoured)
- [ ] A file with an unexplained abbreviation produces at least one D2 finding naming the abbreviation, the absent expansion, and the line of first occurrence
- [ ] A file with a hidden prerequisite (an instruction referencing a tool or environment state not mentioned on the page) produces a D2 finding identifying the missing prerequisite
- [ ] A jargon-load D2 finding in a published-surface artefact (`README.md`, release-note body, top-level docs) whose resolved audience includes a non-operator role is classified `critical`; the same jargon-load finding in an internal draft doc, or in a published surface whose audience is operator-only, stays `warning` (D2 jargon-load escalation honoured)
- [ ] An unexplained-abbreviation D2 finding whose abbreviation appears in a heading, the first paragraph, or a callout is classified `critical`; the same abbreviation appearing only in a later body paragraph stays `warning` (D2 abbreviation escalation honoured)
- [ ] A hidden-prerequisite D2 finding on a page whose `content_mode` is `tutorial` or `how-to` is classified `critical`; the same finding on a `reference` or `explanation` page stays `warning` (D2 prerequisite escalation honoured)
- [ ] An implicit-assumption D2 finding whose marker word ("simply," "just," "obviously") is paired with a step the reader must execute is classified `warning`; the same marker word in a non-imperative context stays `suggestion` (D2 implicit-assumption escalation honoured)
- [ ] A D3 spelling finding for an English file is sourced from Vale (per `prose-style`) and not re-implemented in `Lektorat`
- [ ] A D3 spelling finding for a German file is sourced from a `Lektorat`-owned DE pipeline whose `tool` name, `version`, and `configured_path` are all recorded in `pipeline_metadata.de` of the run's JSON output
- [ ] A D3 misspelling in a published artefact (`README.md`, release-note body, top-level docs) is classified `critical`; the same misspelling in a draft Markdown comment is classified `warning`; the same string inside a code identifier produces no finding (severity dimension-awareness honoured)
- [ ] A file with mixed voice (active/passive flip in adjacent sentences), mixed tense, or mixed address (`du`/`Sie` flip) produces at least one D4 inconsistency finding within the same artefact
- [ ] A page that declares a frontmatter `audience:` value differing from the artefact-type default for its path resolves to the frontmatter value (priority-rule 1 wins over rule 2); a file with no frontmatter and no matching artefact-type default resolves to the whole audience set (rule 3 wins)
- [ ] A `patch` invocation applies exactly one finding per approval cycle and surfaces a unified diff to the operator before any write
- [ ] A `patch` invocation offers a "skip" and a "skip-and-record" path; a recorded dismissal doesn't re-surface in subsequent `audit` runs
- [ ] A `revise` invocation produces a unified diff of the full-artefact rewrite, addresses every `critical` and `warning` finding from the prior `audit`, and refuses to write until the operator approves
- [ ] A `revise` invocation re-runs `audit` on the rewrite and flags the run as a **regression** when the post-`revise` total finding count is higher than the pre-`revise` count
- [ ] A `revise` invocation preserves every code block, frontmatter key, link target, heading ID, and HTML comment byte-identical to the original artefact
- [ ] A `revise` or `patch` invocation preserves the literal text of every block-quoted citation (`> …`) byte-identical to the original artefact
- [ ] A `revise` or `patch` invocation preserves the order and count of every list item, table row, and checklist entry; lexical edits within a single item are allowed, structural cross-item edits aren't
- [ ] A file under `spec/` is rejected by every `Lektorat` operation with a single-sentence message naming the `spec` skill as the authoritative path
- [ ] A file under `skills/**/SKILL.md`, `skills/**/templates/**`, `skills/**/examples/**`, or `agents/*.md` is rejected by every `Lektorat` operation
- [ ] An audience-fit finding (D5) names exactly one audience ID from the audience artefact and references the artefact path
- [ ] When the audience artefact is missing, every `Lektorat` operation stops with a message pointing at the `audience-identify` skill, and **MUST NOT** invent audiences
- [ ] Every Markdown link's `[text](target)` is byte-identical across every operation that doesn't explicitly produce a finding against that link
- [ ] Every heading-text change surfaced by a `patch` or `revise` operation announces the slug change to the operator before the write is approved

## Open Questions

- Should `Lektorat` extend its scope to **API reference text generated from source** (typedoc, sphinx, godoc output)? Default for now: **no**, generated reference is a code-tooling concern and a separate spec topic; revisit when a portfolio repository ships a reference site whose audience extends beyond developers.
- Should the `lektorat-scanner` agent be **dispatchable in parallel per file** (one agent run per artefact, results joined by the skill) or **batched** (one agent run for the whole repository)? Default for now: open—let the first implementation measure; the JSON output shape is the same either way.

## Sources

<!-- Authoritative external references the requirements above were validated against. -->

- Flesch, R. (1948). *A new readability yardstick.* Journal of Applied Psychology—original definition of Flesch Reading Ease.
- Kincaid, J. P., Fishburne, R. P., Rogers, R. L., Chissom, B. S. (1975). *Derivation of new readability formulas.* Defines the Flesch–Kincaid Grade Level.
- Bamberger, R., Vanecek, E. (1984). *Lesen—Verstehen—Lernen—Schreiben.* Defines the Wiener Sachtextformel (WSTF) variants.
- Björnsson, C. H. (1968). *Läsbarhet.* Defines LIX (Läsbarhetsindex); portable to German per readability research consensus.
- Microsoft Writing Style Guide (learn.microsoft.com/style-guide)—voice, tone, bias-free communication; consumed via `spec/project/prose-style/`.
- Microsoft Localization Style Guides—German (learn.microsoft.com/de-de/globalization/localization/styleguides)—DACH conventions for contractions and forms of address.
- Google Developer Documentation Style Guide (developers.google.com/style)—audience and voice principles; consumed via `spec/project/prose-style/`.
- Diátaxis (diataxis.fr)—the `content_mode` enum (`tutorial` / `how-to` / `reference` / `explanation`) that drives `Lektorat`'s readability corridors; consumed via `spec/project/mkdocs-structure/`.
