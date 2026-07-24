# Prose Style

Status: draft

## Context
Documentation, specifications, READMEs, release notes, and other human-readable Markdown across this portfolio must read consistently regardless of who—or what—wrote the text. [Vale](https://vale.sh) is the shared prose linter used to enforce that consistency. The canonical source is the portfolio-local style package in [`nolte/vale-style`](https://github.com/nolte/vale-style); a repository's `.vale.ini` composes the upstream Microsoft and RedHat style packages with a pinned release of that package, which also carries the shared technical vocabulary. When a new term, product name, or phrasing convention is introduced, it must be deposited in `nolte/vale-style` rather than tracked per repository, so that future text generation—whether by a human or by an AI assistant—produces output that already passes the shared rules.

Readers: humans and AI assistants authoring Markdown across the portfolio, reviewers running Vale, and the `nolte/vale-style` maintainers who own the shared style package and vocabulary.

## Goals
- Human-readable text in every repository follows the same lint-enforced style rules
- Shared technical vocabulary has a single canonical home at `nolte/vale-style`
- Newly coined terms are reviewable and reusable across the portfolio instead of drifting per repository
- AI-assisted text generation produces output that already passes the shared Vale configuration

## Non-Goals
- Code comments, docstrings, and API reference text (governed by code-level tooling, not Vale)
- Visual styling of rendered output (themes, CSS, typography)
- Translation quality beyond vocabulary consistency
- Language choice between English and German (handled by the per-project documentation policy)

## Requirements

### Shared Vale configuration
- **MUST** configure Vale in every repository that contains human-readable Markdown using a `.vale.ini` that composes the Microsoft and RedHat packages plus a pinned release of [`nolte/vale-style`](https://github.com/nolte/vale-style) as the canonical portfolio style source
- **MUST** pin the `nolte/vale-style` package to an explicit release version (not `develop`/`main`) so local and CI runs are reproducible
- **MUST** set `StylesPath` and `MinAlertLevel` consistently so local and CI runs produce the same alerts
- **SHOULD** mirror the `IgnoredScopes` list from the canonical config (at minimum `code`, `tt`, `em`) so fenced code samples don't trigger prose rules
- **SHOULD** run Vale against every Markdown scope the repository ships, including per-language documentation folders (`docs/en/`, `docs/de/`, …)

### Running Vale
- **MUST** run `vale sync` before the first lint invocation so the pinned packages are fetched
- **MUST** expose a Taskfile target (for example `task docs:lint` or `task lint:prose`) that runs Vale across all human-readable Markdown
- **MUST** wire that Taskfile target into CI so pull requests fail when Vale alerts at `error` level
- **MUST** register a pre-commit hook that runs Vale on changed Markdown files locally, invoking the same Taskfile target CI uses

### Text generation
- **MUST** treat the active Vale configuration (Microsoft + RedHat + `nolte/vale-style`) as authoritative when generating or rewriting prose—whether the author is a human or an AI assistant
- **MUST** verify that new or substantially rewritten Markdown passes Vale at the repository's configured `MinAlertLevel` before the change is treated as finished work
- **SHOULD** prefer phrasings already accepted by the shared vocabulary over coining new terms, and reuse terminology from neighbouring specs and docs when it fits
- **MUST NOT** silence Vale alerts with per-file ignore comments when the real fix is a vocabulary or style update upstream in `nolte/vale-style`

### New terms and phrasings
- **MUST** add newly introduced technical terms, product names, or project-specific jargon to the shared vocabulary at [`nolte/vale-style`](https://github.com/nolte/vale-style), specifically under `src/styles/config/vocabularies/<vocab>/accept.txt`, rather than to a repository-local override
- **MUST** group additions by an existing vocabulary topic (for example `technical`, `esphome`) whenever one fits, and only propose a new vocabulary when no existing one applies
- **SHOULD** open a pull request against `nolte/vale-style` with a one-line justification per new entry, so additions are reviewable
- **MAY** keep a term in a repository-local vocabulary only while the upstream PR is pending; once the upstream change is released, the local entry **MUST** be removed and the pinned `nolte/vale-style` release **MUST** be bumped

The drift between repository-local vocabularies and the pinned `nolte/vale-style` release is audited by the `vocab-drift-audit` skill rather than by a periodic CI cron.

### Pull-request descriptions and release notes
- **MUST** apply the same shared Vale rule set to pull-request descriptions and to GitHub Release notes (drafted by release-drafter, edited before publishing), because this prose flows directly into external changelogs and user-facing release pages
- **MUST** check pull-request descriptions in CI (for example via a PR-check workflow) at the repository's configured `MinAlertLevel`, failing on `error`-level alerts the same way documentation does
- **SHOULD** verify the final Release notes body against Vale before the release is published, so the published changelog doesn't carry prose violations into public view

### Voice and tone

The Vale rule sets enforce a mechanical baseline, but the rules below codify the *editorial* posture every authored or AI-generated paragraph must already have **before** Vale runs. The rules below come from the Microsoft Writing Style Guide (Top-10 tips + Brand voice), the Google Developer Documentation Style Guide (Voice and Audience), and the Write the Docs documentation principles; each rule below is supported by at least two of those sources.

- **MUST** write in **active voice** by default; passive voice **MAY** be used only when the actor is genuinely unknown, irrelevant, or when active voice would force an awkward subject (Microsoft Top-10 §Revise weak writing: "Most of the time, start each statement with a verb"; Google Voice and Tone)
- **MUST** address the reader in the **second person** (`you`, `your`) on every page whose `content_mode` is `tutorial` (which includes quickstart pages per `spec/project/docs-audience-tracks/` §User-docs content contract), `how-to`, or `troubleshooting`; `reference`, `explanation`, and `glossary` pages stay impersonal (Microsoft Top-10 §Project friendliness; Diátaxis tutorials/how-to-guides: "the learner / the reader"; Diátaxis Explanation: "higher and wider perspective" implies a third-person register)
- **MUST** use **present tense** for system behaviour ("the command returns," not "the command will return") and for instructions ("select," not "you will select"); past tense is reserved for changelog and release-note prose (Microsoft Brand voice; Google Voice)
- **MUST** use **sentence-case capitalisation** for every heading, list item, button name, and table cell with three or fewer words; title-case ("Like This") is forbidden outside proper nouns and product names (Microsoft Top-10 §When in doubt, don't capitalize: "Never Use Title Capitalization (Like This). Never Ever"; ratified by Vale's Microsoft style)
- **MUST** front-load the answer or the first command before any background; this is the page-level equivalent of the §Content modes (Diátaxis alignment) framing rule in `spec/project/mkdocs-structure/` (Microsoft Top-10 §Get to the point fast; Google "Clear information first"; WtD Skimmable)
- **SHOULD** keep paragraphs short (typically three sentences or fewer) and prefer lists for any sequence of three or more parallel items (Microsoft Top-10 §Be brief; WtD Skimmable)
- **SHOULD** use **contractions** sparingly but consistently per language tree (English documentation uses `you're`, `it's`, `don't`; the German tree retains the unabbreviated forms required by the Microsoft Localization Style Guide for German) (Microsoft Top-10 §Project friendliness; Microsoft Localization Style Guides—German)
- **SHOULD** open every non-`reference` page with a one- to three-sentence framing paragraph that names the reader's situation (what they have, what they want) before the first H2 (mirrors `spec/project/mkdocs-structure/` §Content modes (Diátaxis alignment))
- **MUST NOT** ship **idioms, slang, sports metaphors, military metaphors, or culturally specific references** in any English-scoped prose; the prose must read for a global audience whose first language may not be English (Google Voice "No culturally specific references"; Microsoft Bias-Free Communication §Militaristic language)
- **MUST NOT** ship **gendered generic pronouns** (`he`, `she`, `his`, `hers`, `he/she`); rewrite to second person, plural, or role-based references (Microsoft Bias-Free Communication: "Don't use he, him, his, she, her, or hers in generic references"; Linguistic Society of America Guidelines for Inclusive Language)
- **MUST NOT** ship **ableist or otherwise non-inclusive phrasing**; in particular, the substitutions in Microsoft's Bias-Free Communication §Don't use terms that may carry unconscious racial bias (`primary` / `subordinate` instead of `master` / `slave`; `stop responding` instead of `hang`; `perimeter network` instead of `DMZ`) are mandatory. The shared Vale vocabulary at `nolte/vale-style` carries the curated replacement list; new inclusive-language substitutions are deposited there per §New terms and phrasings, not in per-repo overrides.
- **MUST NOT** ship **exclamation marks** outside genuine emphasis (release-note "🎉 Released!" style is allowed in release notes; documentation prose isn't the place) (Google Voice "Avoid exclamation marks")
- **MUST NOT** ship **emoji** in spec, ADR, or reference prose; emoji **MAY** appear in release notes, README badge rows, and informal blog posts when the project's voice supports it (portfolio convention; not contradicted by upstream style guides)
- **MAY** use **microcopy patterns** ratified by Microsoft Top-10 (verb-first list items, "you can" pruned away, two-or-three-word headings without end punctuation)

By default these §Voice and tone rules stay **editorial guidance**: they're enforced by the human or AI lektorat pass (`spec/project/lektorat/` §Detection dimensions, which surfaces them as D4 style findings) and by pull-request review, not by bespoke Vale rules. The portfolio doesn't author a general active-voice detector, a title-case detector, or a gendered-pronoun detector in `nolte/vale-style` until recorded drift justifies the rule cost; the [`spec/project/lektorat/`](../lektorat/en.md) §Non-Goals defers this same decision back to this spec as the owner. The one exception already automated is the bias-free substitution table, which `nolte/vale-style` carries upstream (see the inclusive-language bullet above and the §Acceptance Criteria entry for it). When automation does become justified, deposit targeted upstream rules in this order—gendered generic pronouns, exclamation marks, and title-case headings first, because they're the lowest-false-positive classes—and keep the general active-voice class manual, because it's the most false-positive-prone. The countable revisit trigger is recorded in §Open Questions.

### Multilingual text
- **MUST** scope Vale to English-authored content only; files authored in any language other than English **MUST NOT** be included in Vale's lint scope
- **MUST** define the English-only lint scope in both the `.vale.ini` format sections and the Taskfile `lint:prose` target so local and CI apply the same scope; the scope covers end-user-facing prose only—typical English paths are `README.md`, `docs/en/`, and each spec's canonical-language file where English is canonical (`spec/<topic>/<slug>/en.md`)
- **MUST NOT** include any path that holds non-English content in the lint scope: `docs/de/`, `spec/<topic>/<slug>/de.md`, `*.de.md`, and any equivalent non-English path stays outside Vale
- **MUST NOT** include LLM-instruction artifacts in the lint scope: `skills/**/SKILL.md`, `skills/**/templates/**`, `skills/**/examples/**`, `agents/*.md`, and any equivalent plugin-authored Claude Code artifact stays outside Vale; these files are tool-author-to-LLM instructions, not end-user prose, and applying Microsoft-style end-user-writing rules to them produces noise rather than signal
- **MUST** keep every file that's in Vale's scope free of non-English prose (body text, YAML frontmatter fields, inline comments, quoted example strings) because Vale can't distinguish language boundaries inside a scoped file and will flag foreign words as spelling errors
- **SHOULD** mirror significant English documentation into a parallel non-English file under `docs/de/` or `spec/<topic>/<slug>/de.md` for readers of that language; those files are authored and maintained without Vale checks and are free to use their own native vocabulary
- **MUST NOT** introduce a language-scoped vocabulary (for example `vocabularies/technical-de/`) into `nolte/vale-style` as a workaround for mixed-language files inside Vale's scope; the canonical remediation for a non-English passage in a scoped file is to move the passage into a language-scoped file outside the scope, not to teach Vale foreign vocabulary

## Acceptance Criteria
- [ ] `.vale.ini` exists at the repository root (or at the documentation root) and references a pinned `nolte/vale-style` release
- [ ] `vale sync` succeeds against the committed configuration without manual intervention
- [ ] A Taskfile target runs Vale across all human-readable Markdown in the repository
- [ ] CI fails when Vale reports alerts at `error` level on changed Markdown
- [ ] `.pre-commit-config.yaml` registers a Vale hook that runs against changed Markdown using the same Taskfile target as CI
- [ ] No repository-local vocabulary file contains a term that's already accepted by the pinned `nolte/vale-style` release
- [ ] Every domain term introduced by a recent change appears in a PR or recent release of `nolte/vale-style`, not only in the downstream repository
- [ ] Any AI-assisted text generation operation verifies the output against the repository's Vale configuration before the task is treated as done
- [ ] Pull-request descriptions and GitHub Release notes pass Vale at the configured `MinAlertLevel` under the same configuration as the repository's Markdown documentation
- [ ] Vale's configured lint scope contains no files authored in a language other than English; `docs/de/`, `spec/<topic>/<slug>/de.md`, and any `*.de.md` are explicitly absent from the scope
- [ ] Vale's configured lint scope contains no LLM-instruction artifacts; `skills/**/SKILL.md`, `skills/**/templates/**`, `skills/**/examples/**`, and `agents/*.md` are explicitly absent from the scope
- [ ] No English-scoped file contains non-English prose anywhere in its body, YAML frontmatter, inline comments, or quoted examples; Vale at `error` level confirms this
- [ ] Authored or AI-generated paragraphs follow the §Voice and tone rules (active voice, second person on instructional pages, present tense, sentence-case headings, front-loaded answer); a reviewer can spot-check any page and find the rules upheld
- [ ] No English-scoped prose carries gendered generic pronouns (`he`, `she`, `his`, `hers`, `he/she`), militaristic or ableist substitutions ratified by the Microsoft Bias-Free Communication table, exclamation marks outside genuine emphasis, or culturally specific idioms; the shared Vale vocabulary at `nolte/vale-style` flags every known offender at `error` level
- [ ] The shared Vale vocabulary at `nolte/vale-style` carries Microsoft's bias-free substitutions (`primary` / `subordinate`, `stop responding`, `perimeter network`, …) so a per-repo override isn't needed to enforce them

## Open Questions

_All previously deferred open questions were settled on 2026-06-06: each provisional default is now the standing rule. The per-item decisions and rationale are preserved in git history (decision log, 2026-06-06)._

## Sources
<!-- Authoritative external references the requirements above were validated against (≥2 independent sources per claim). -->
- Microsoft Writing Style Guide (learn.microsoft.com/style-guide)—Top-10 tips, Brand voice, Bias-Free Communication, Militaristic language guidance
- Microsoft Localization Style Guides—German (learn.microsoft.com/de-de/globalization/localization/styleguides)—DACH house-style rules for contractions and forms of address in the German language tree
- Google Developer Documentation Style Guide (developers.google.com/style)—Voice and Tone, Audience, "Clear information first" framing
- Write the Docs documentation principles (writethedocs.org/guide)—ARID, Skimmable, Exemplary, Current, Consistent
- Linguistic Society of America Guidelines for Inclusive Language (linguisticsociety.org)—second-line ratification of the inclusive-pronoun guidance Microsoft sources
