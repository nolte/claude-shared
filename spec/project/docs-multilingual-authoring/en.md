# Multilingual Documentation Authoring

Status: draft

## Context

Portfolio repositories ship MkDocs sites that are bilingual by default: `spec/project/mkdocs-structure/` §Per-language layout already mandates `docs/<lang>/` subdirectories with structurally identical file trees, and `spec/project/docs-freshness/` §Finding categories audits the resulting drift as a `Language-parity gap` finding. What neither spec defines is the **authoring protocol**: how and when a documentation-producing skill or agent puts a page into every configured language tree. The result is asymmetric authoring: a skill writes `docs/en/foo.md`, leaves `docs/de/foo.md` for later, and the gap only surfaces in the next quarterly `docs-freshness` audit. By that point the canonical page has drifted, the author has paged out the context, and the translation is reconstructed from a stale snapshot.

This spec closes that gap by lifting the canonical-and-translation contract that already governs `spec/<topic>/<slug>/` (one file per language, written atomically, English canonical, drift-managed) to every Markdown page under `docs_dir`. It's the **authoring counterpart** to the `mkdocs-structure` shape contract and the `docs-freshness` audit contract: shape says "the trees must be parallel," audit says "we detect when they aren't," and this spec says "every authoring step keeps them parallel from the start."

## Goals

- Documentation-producing skills and agents write every configured language version of a `docs/<lang>/` page **atomically in the same authoring step**, with English as the canonical source and other configured languages as structurally identical translations
- The repository never enters a state where a page exists in one language tree but not in another as a result of skill or agent output
- The protocol reuses the configuration surface that already governs `spec/<topic>/<slug>/` (namely `spec/.spec-config.yml`'s `canonical_language` and `languages` keys), so a repository declares its language matrix in exactly one place
- README.md is explicitly excluded from the multilingual contract; it stays English-only per `spec/project/readme-structure/` §File and language
- The boundary against `mkdocs-structure` (shape), `docs-freshness` (audit), and `readme-structure` (README exemption) is sharp enough that no requirement is restated in two specs

## Non-Goals

- Defining the per-language directory layout, plugin choice, or nav contract—that's owned by `spec/project/mkdocs-structure/`
- Detecting drift between language trees after the fact—that's the `Language-parity gap` finding owned by `spec/project/docs-freshness/`
- Translating README.md—the README stays English-only per `spec/project/readme-structure/` §File and language, and its Non-Goals already exclude README translations
- Translating release notes: `spec/project/release-skill-layer/` owns the release-notes contract and decides its own language policy
- Translating GitHub Issue Forms under `.github/ISSUE_TEMPLATE/`: `spec/project/github-issue-templates/` owns that surface
- Translating CHANGELOG.md or any Markdown artefact outside `docs_dir`
- Mandating a specific translation quality bar or a specific translation engine—this spec contracts the **structural** protocol (which files exist, what shape they share, who writes them when); the per-token translation quality remains the responsibility of the producing skill or agent
- Mandating that human-authored ad-hoc edits inside one language tree trigger an immediate translation pass—drift caused by manual edits is detected by `docs-freshness`, not prevented by this spec

## Requirements

<!-- Use RFC 2119 keywords: MUST, SHOULD, MAY. One atomic requirement per bullet. -->

### Authoring protocol

- **MUST** treat any skill or agent that creates, edits, renames, or deletes a Markdown file (`*.md`) under the MkDocs `docs_dir` configured in `mkdocs.yml` as a *documentation-producing capability* in scope of this spec; the producing capability is responsible for satisfying every MUST below in the **same authoring step** (the same skill invocation, the same agent run, the same tool call sequence—not "later," not "in a follow-up commit")
- **MUST** resolve the language matrix from `spec/.spec-config.yml` (`canonical_language`, `languages`) at the start of every authoring step; the same file that governs `spec/<topic>/<slug>/` is reused here so the repository declares its language matrix in exactly one place
- **MUST** treat the value of `canonical_language` as the **source of truth** for every page authored in this step; every other entry in `languages` is a **translation** that mirrors the canonical page structurally
- **MUST** write or update the corresponding file under `docs/<other_language>/<same-relative-path>` for **every** other language in `languages` whenever the canonical file under `docs/<canonical_language>/<relative-path>` is created or updated; the operation is **atomic**: either every language version is written in the same step, or none is
- **MUST NOT** mark an authoring step as successful when one or more configured language versions of a touched page are missing on disk; a partial write is a violation regardless of the producing skill's exit status
- **MUST NOT** translate, rename, or delete `README.md` at the repository root, nor any file the producing skill identifies as English-only by repository convention (Cross-Ref: `spec/project/readme-structure/` §File and language declares README EN-only)
- **MUST** propagate file-tree operations symmetrically across language trees: renaming `docs/<canonical_language>/a.md` to `docs/<canonical_language>/b.md` MUST rename the counterpart in every other language tree in the same step; deleting `docs/<canonical_language>/foo.md` MUST delete every counterpart

### Structural parity of the translation

- **MUST** keep the heading tree of every translation file structurally identical to its canonical counterpart: same `#`/`##`/`###` depth, same heading order, same heading count. Heading **text** is translated; heading **structure** isn't
- **MUST** preserve the YAML frontmatter key set across languages: every key declared on the canonical page (`title`, `audience`, `content_mode`, `last_updated`, `track`, and any project-type-specific MUST key) appears with the same name on every translation
- **MUST** localise frontmatter **values** that are user-facing display strings (typically `title`) and **MUST NOT** localise frontmatter **values** that are portfolio-wide identifiers (`audience` IDs from the audience artefact per `spec/project/audience-identification/`, `track` enum values from `spec/project/docs-audience-tracks/`, `content_mode` enum values from `spec/project/mkdocs-structure/`); identifiers are stable across languages by design
- **MUST** keep relative internal markdown links pointing to the same target path within the page's own language tree; a link from `docs/en/a.md` to `b.md` translates to a link from `docs/de/a.md` to `b.md` (same relative path, same target page, no `../en/` traversal across language trees)
- **MUST** keep `mkdocs-include-markdown-plugin` directives identical across language versions when the included source is language-neutral (a source file under `src/`, `spec/`, a YAML config, a code excerpt); the include directive itself is identical text in both translations, so the rendered content stays in sync without per-language forks
- **MUST** keep RFC 2119 keywords (`MUST`, `SHOULD`, `MAY`) in English inside translation files and gloss them in the target language inline (for example `MUSS [MUST]`, `SOLLTE [SHOULD]`, `KANN [MAY]`), matching the convention `spec/<topic>/<slug>/` already follows
- **MUST NOT** drop, reorder, or merge bullets, list items, table rows, checklist entries, or code blocks between the canonical and a translation; the *content* of each unit translates, the *count and order* are preserved

### Snippets

- **MUST** apply this protocol only to **pages** (files outside `_`-prefixed folders under `docs/<lang>/`); snippet fragments inside `_`-prefixed folders (`docs/<lang>/_snippets/` and equivalents per `spec/project/mkdocs-structure/` §Snippet inclusion (DRY)) aren't pages and aren't in scope of the structural-parity MUSTs above
- **MAY** keep a language-neutral snippet (a code excerpt, a YAML fragment, a CLI transcript) in only one language tree, included by both language trees via `mkdocs-include-markdown-plugin`; this is the preferred shape for content that doesn't translate
- **MUST** apply this protocol's structural-parity MUSTs to a snippet that contains translatable prose (a fragment of explanatory text included by multiple pages); such a snippet is authored once per language, mirrored across `docs/<lang>/_snippets/` like a page

### Coordination with neighbouring specs

- **MUST** reference `spec/project/mkdocs-structure/` §Per-language layout for the file-tree parity contract and `spec/project/docs-freshness/` §Finding categories for the audit-time detection of violations; this spec **MUST NOT** restate either contract
- **MUST** reference `spec/project/readme-structure/` §File and language as the source of the README EN-only exemption; this spec **MUST NOT** restate the README rule
- **MUST NOT** override or relax any MUST declared in `mkdocs-structure`, `docs-freshness`, `readme-structure`, `docs-audience-tracks`, or `audience-identification`; conflicts are resolved by amending the upstream spec, not by exception in this one
- **MUST** treat generated catalog pages under `docs/<lang>/skills/` and `docs/<lang>/agents/` as documentation-producing output bound by the §Authoring protocol structural MUSTs (one page per language per artefact, parallel trees); `spec/claude/skill-agent-catalog/` owns their per-language rendering and uses its reserved `_translation-pending` auto-tag and "translation pending" badge as the catalog-specific form of the `needs-review` escape hatch. This spec **MUST NOT** restate the catalog's summary-resolution or fallback rules

### Translation quality and review

- **SHOULD** ship the canonical edit and every translation in the same commit so a reviewer reads both sides together; staging them in separate commits is a smell that defeats the atomic-write MUST above
- **SHOULD** mark a translation with an inline HTML comment `<!-- translation-status: needs-review -->` when the producing skill can't itself guarantee semantic fidelity (for example, a generator that emits canonical content from structured data and a best-effort target-language rendering); the marker is a `docs-freshness` finding (warning severity) until a reviewer removes it
- This spec defines exactly one author-set translation-debt marker, `needs-review`. Generator best-effort output is signalled by `spec/claude/skill-agent-catalog/`'s `_translation-pending` auto-tag; canonical-versus-translation staleness is detected by `spec/project/docs-freshness/`. A richer closed set lands in `docs-freshness` §Severity classification only when an audit pattern shows the binary marker is insufficient (see Open Questions)
- **MUST** place the `<!-- translation-status: needs-review -->` marker as an HTML comment on the first body line immediately after the frontmatter block, so it stays invisible in the rendered MkDocs page yet greppable from CI (the same content-scan detection `spec/project/docs-freshness/` §Finding categories already uses for stale markers); the marker **MUST NOT** be expressed as a frontmatter key, which would break the §Structural parity of the translation frontmatter-key-set MUST (the canonical page carries no such key)
- **MUST** treat an author who can't yet guarantee a still-drafting page's translation—including an ADR under `docs/<lang>/adr/` with `proposed` status—as bound by the §Authoring protocol atomic-write MUST like every other page: both language files ship in the same step, with `<!-- translation-status: needs-review -->` on the translation as the escape hatch; there is no status-conditional exemption
- **MAY** delegate the per-token translation to `audience-doc-author` (or a comparable agent that already owns translation in the portfolio) as a sub-step of the producing capability, rather than re-implementing translation in every skill

### Single-language repositories

- **MAY** a repository whose `spec/.spec-config.yml` `languages:` list contains exactly one entry treat this spec as trivially satisfied: every authoring step writes exactly one language version, which is also the canonical version, and no parity MUSTs apply. The repository **MUST** continue to use the `docs/<lang>/` layout per `mkdocs-structure` §Per-language layout so adding a second language later is a pure-additive change

## Acceptance Criteria

<!-- Testable, checkable conditions. A reviewer should be able to mark each as done/not done. -->

- [ ] Every skill under `skills/` and every agent under `agents/` whose body declares it writes Markdown into `docs/<lang>/` references this spec in its hard-rules section and follows the atomic-authoring MUST above
- [ ] A test invocation of `audience-doc-author` that produces a new page emits `docs/<canonical_language>/<slug>.md` and `docs/<other_language>/<slug>.md` in the same run, with identical heading trees and identical frontmatter key sets
- [ ] A simulated single-language write (deliberately removing one of the language files after the authoring step) is flagged by `docs-freshness` as a `Language-parity gap` finding with severity `warning`
- [ ] `README.md` at the repository root remains English-only across the whole skill and agent corpus; no skill or agent that implements this spec produces `README.de.md` or any other localised README variant
- [ ] `spec/project/mkdocs-structure/` §Per-language layout cross-references this spec as the authoring counterpart (additive sentence, no contract change)
- [ ] `spec/project/docs-freshness/` §Finding categories cross-references this spec as the authoring counterpart (additive sentence, no contract change)
- [ ] `spec/project/readme-structure/` §Non-Goals cross-references this spec as the canonical declaration that the README exemption is portfolio-wide (additive sentence, no contract change)
- [ ] A rename of a canonical page (`git mv docs/en/foo.md docs/en/bar.md`) performed through a documentation-producing skill renames the counterpart in every configured language tree in the same step

## Open Questions

_All previously deferred open questions were settled on 2026-06-06: each provisional default is now the standing rule. See `.audits/decisions/2026-06-06-settle-open-questions.md` for the per-item decisions and rationale._
