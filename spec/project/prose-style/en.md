# Prose Style

Status: draft

## Context
Documentation, specifications, READMEs, release notes, and other human-readable Markdown across this portfolio must read consistently regardless of who—or what—wrote the text. [Vale](https://vale.sh) is the shared prose linter used to enforce that consistency. The canonical source is the portfolio-local style package in [`nolte/vale-style`](https://github.com/nolte/vale-style); a repository's `.vale.ini` composes the upstream Microsoft and RedHat style packages with a pinned release of that package, which also carries the shared technical vocabulary. When a new term, product name, or phrasing convention is introduced, it must be deposited in `nolte/vale-style` rather than tracked per repository, so that future text generation—whether by a human or by an AI assistant—produces output that already passes the shared rules.

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

### Pull-request descriptions and release notes
- **MUST** apply the same shared Vale rule set to pull-request descriptions and to GitHub Release notes (drafted by release-drafter, edited before publishing), because this prose flows directly into external changelogs and user-facing release pages
- **MUST** check pull-request descriptions in CI (for example via a PR-check workflow) at the repository's configured `MinAlertLevel`, failing on `error`-level alerts the same way documentation does
- **SHOULD** verify the final Release notes body against Vale before the release is published, so the published changelog doesn't carry prose violations into public view

### Multilingual text
- **MUST** scope Vale to English-authored content only; files authored in any language other than English **MUST NOT** be included in Vale's lint scope
- **MUST** define the English-only lint scope in both the `.vale.ini` format sections and the Taskfile `lint:prose` target so local and CI apply the same scope; typical English paths are `README.md`, `docs/en/`, `skills/*/SKILL.md` (authored in English per the `skill-management` spec), and each spec's canonical-language file where English is canonical (`spec/<topic>/<slug>/en.md`)
- **MUST NOT** include any path that holds non-English content in the lint scope: `docs/de/`, `spec/<topic>/<slug>/de.md`, `*.de.md`, and any equivalent non-English path stays outside Vale
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
- [ ] No English-scoped file contains non-English prose anywhere in its body, YAML frontmatter, inline comments, or quoted examples; Vale at `error` level confirms this

## Open Questions
- _None—all prior open points have been resolved. The drift audit between repository-local vocabularies and the pinned `nolte/vale-style` release is delegated to a dedicated Claude Skill rather than enforced through a periodic CI cron._
