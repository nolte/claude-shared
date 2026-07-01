---
name: docs-dry-refactor
description: "Operationalises spec/project/mkdocs-structure/ §Snippet inclusion (DRY). Detects paragraph duplication across MkDocs pages and, with per-snippet user approval, extracts duplicates into `mkdocs-include-markdown-plugin` includes pointing at a canonical source (preferring a live source file over a dedicated per-language _snippets/ folder). Three operations: `audit` (read-only ranked findings), `propose` (surface canonical source, markers, include directives for a target snippet ID, await approval), `apply` (write markers, replace consumer blocks, verify via `mkdocs build --strict`). Invoke when the user asks to dedupe, DRY-refactor, extract snippets, or factor out duplicated MkDocs content; also handles equivalent German-language requests. Don't use for non-MkDocs markdown trees, single-file snippet authoring, prose linting (`prose-vale-curator`), structural scaffolding (`mkdocs-structure-apply`), or drift detection (`docs-freshness-checker`). Supports resume on re-invocation per `spec/claude/resumable-work/`."
tags: [scaffolding, audit]
phase: design
summary: "Detects duplicated MkDocs paragraphs and extracts them into mkdocs-include-markdown-plugin snippets."
summary_de: "Erkennt duplizierte MkDocs-Absätze und extrahiert sie in mkdocs-include-markdown-plugin-Snippets."
use_when:
  - "you want to DRY-refactor duplicated content across MkDocs pages"
  - "you want to extract a paragraph into a shared snippet with a canonical source"
  - "you want a read-only ranked finding list of likely-duplicate paragraphs"
dont_use_when:
  - situation: "You want prose-style linting rather than DRY refactoring"
    alternative: prose-vale-curator
  - situation: "You need MkDocs scaffolding rather than content refactoring"
    alternative: mkdocs-structure-apply
  - situation: "You need drift detection across docs"
    alternative: docs-freshness-checker
see_also:
  - mkdocs-structure-apply
  - docs-freshness-checker
resumable: true
---

# Docs DRY Refactor

Operationalises `spec/project/mkdocs-structure/<canonical_language>.md` §Snippet inclusion (DRY) inside the current repository. The skill scans the configured `docs/<lang>/` trees for paragraph-level duplication that violates the spec's DRY threshold, proposes a canonical-source extraction for each finding, and—after explicit per-snippet user approval—rewrites the consumer pages to include from that source via `mkdocs-include-markdown-plugin`.

When the spec isn't present in the target repository, fall back to the copy shipped by the `nolte-shared` plugin (read it at runtime from `${CLAUDE_PLUGIN_ROOT}/spec/project/mkdocs-structure/<canonical_language>.md`). Never invent requirements that don't appear in the spec.

## Why this is a skill, not an agent

Per `spec/claude/skill-vs-agent/` §Decision dimensions, this capability is a skill because:

- **Mid-flow per-snippet user approval is the contract.** Each candidate extraction (canonical source choice, marker placement, every consumer's include directive) is a separate user decision; an agent's fire-and-forget shape would collapse the per-snippet approvals into a single opaque report.
- **Persistent on-disk output that flows back into the main conversation.** The findings table, the per-finding proposal, and the build-verification output all surface in the conversation so the user can decide; isolating them in a structured-report boundary would obscure the per-snippet approval surface.
- **Orchestrator pattern.** The skill may later dispatch the `audience-doc-author` agent for snippet-body authoring (when no canonical source exists and a fresh dedicated snippet file is needed) or chain to `mkdocs-structure-apply audit` to verify the §Snippet inclusion (DRY) acceptance items post-extract; per `spec/claude/skill-vs-agent/` §Hybrid pattern, the orchestrator is always a skill.
- **Precedent.** Follows the same audit-then-act shape as `mkdocs-structure-apply` and `project-structure-apply`; portfolio-wide consistency (`spec/claude/skill-vs-agent/` §Portfolio-wide consistency) favours the same artifact type and the shared `scaffolding, audit` tag cluster.
- **Counter-dimension considered.** A narrower agent could specialise on the duplicate-detection scan and gain on context-window protection during large docs trees, but the high-impact part is the per-snippet approval dialogue and the build-verification loop, not the scan itself; skill wins.

## User-language policy

Detect the user's language from their message and respond in it. Generated file contents (marker comments, include directives, new dedicated snippet files under `docs/<lang>/_snippets/`) are always written in English so portfolio-wide automation stays predictable.

## Tool selection rationale

Declared tools: `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`.

- `Read` / `Glob` / `Grep` for repository inspection (page walking, paragraph hashing, marker hunting in candidate canonical sources, existing-include detection).
- `Edit` for in-place replacement of duplicated paragraph blocks with `{% include-markdown … %}` directives, and for inserting start/end marker comments into canonical sources.
- `Write` only for creating a new dedicated `docs/<lang>/_snippets/<topic>.md` when no canonical source already exists.
- `Bash` is necessary for `mkdocs build --strict` post-write verification and for filesystem traversal idioms `Glob` doesn't cover. Bash is never destructive (no `git push`, no `gh pr create`, no `pip install`, no `rm` outside an explicitly scoped scratch path).
- No `WebFetch` / `WebSearch`: the spec is the only source of truth.

## Preconditions

Before doing anything:

1. Confirm the working directory is a git repository (`git rev-parse --is-inside-work-tree`).
2. Locate `spec/project/mkdocs-structure/<canonical_language>.md`—either in the target repo or via the `nolte-shared` plugin at `${CLAUDE_PLUGIN_ROOT}/spec/project/mkdocs-structure/<canonical_language>.md`. Read the spec's §Snippet inclusion (DRY) subsection and the four DRY-related Acceptance Criteria items at runtime; never bake the thresholds into the skill. When neither copy is reachable, stop and ask the user which spec source to use (matches the parent spec's §Extension hooks §"Project-type discovery" fallback pattern).
3. Resolve the language list from `spec/.spec-config.yml` `languages`. When that file is absent, ask the user which languages to scan; never default silently.
4. Verify `mkdocs.yml` declares `mkdocs-include-markdown-plugin` and that the plugin is pinned in the project's Python dep manifest. When the plugin is missing, stop and route the user to `mkdocs-structure-apply patch` to wire the baseline first; this skill never adds the plugin itself.
5. Check for uncommitted changes in `docs/`, `mkdocs.yml`, and any candidate canonical-source files. When the tree is dirty there, report and ask whether to stash, commit, or abort—never overwrite uncommitted work.
6. Confirm the operation: `audit` (default, read-only), `propose <id>` (surface a proposal and await approval), or `apply <id>` (write after approval).

## Operations

### 1. `audit` (read-only, default)

Inputs: target repo root (defaults to the current working directory), optional `--lang <language>` filter.

Walk every `docs/<lang>/` tree for languages in the resolved language list. Exclude:

- Any folder whose name starts with `_` (snippet folders aren't pages).
- Generated catalog pages owned by the catalog generator (per `spec/claude/skill-agent-catalog/`): `docs/<lang>/skills/SUMMARY.md`, `docs/<lang>/skills/<plugin>/<name>.md`, `docs/<lang>/agents/SUMMARY.md`, `docs/<lang>/agents/<plugin>/<name>.md`, `docs/<lang>/tags.md`.
- Pages already containing at least one `{% include-markdown … %}` directive—surfaced separately as "partial DRY (existing include chain)" hints, not as fresh findings.

For each remaining page:

1. Strip YAML frontmatter from the page head (the `---`-delimited block) before splitting; frontmatter is never DRY-refactored.
2. Split the body into paragraph blocks separated by one or more blank lines. Treat each fenced code block (```…```) as one indivisible block even if it spans many blank-line-separated lines.
3. Normalise each block by collapsing whitespace runs (`re.sub(r'\s+', ' ', block).strip()`) and hashing the result.
4. Group blocks sharing the same hash. A finding is any group whose member blocks are ≥3 lines (pre-normalisation) and whose occurrence count is ≥2 pages. The thresholds come from the spec's §Snippet inclusion (DRY) MUST; never bake them in.
5. Rank findings by `line_count × occurrence_count` descending.

For each finding, identify the **proposed canonical source**:

- First, search the repository for the verbatim block in non-docs files (CONTRIBUTING.md, `pyproject.toml`, `.github/workflows/*.yml`, `README.md`, source files). When found, propose that file as the canonical source plus the marker positions needed.
- Otherwise, propose a new dedicated `docs/<lang>/_snippets/<topic>.md` (one per configured language tree when the content is language-specific; one shared snippet under the canonical language only when the content is language-neutral).

The `audit` emits a structured findings table only; never writes.

### 2. `propose <finding-id>`

Inputs: a `finding-id` produced by a prior `audit` in the same session.

Surface:

- The full snippet body (verbatim, with line count).
- The proposed canonical-source path and the start/end marker comment lines to insert there, in the source file's native comment syntax (per Hard rule 12).
- For each consumer page, the exact `{% include-markdown "<docs_dir-relative-path>" start="<marker>" end="<marker>" %}` directive that will replace the duplicated block (paths resolve relative to `docs_dir`, not to the consuming page; see Gotchas).
- The expected `mkdocs build --strict` delta (pages added or modified, snippet file added when applicable).

End with an explicit approval gate: nothing is written until the user responds with `approve <id>` or `skip <id>`. Batch approval (`approve all`) is acceptable when the user explicitly asks for it; silent rewrite is forbidden (Hard rule 1).

### 3. `apply <finding-id>`

Preconditions: the finding-id has been `propose`d and approved in this session.

Writes in this order:

1. Insert the start/end marker comments into the canonical source. When the canonical source is a new dedicated snippet file under `docs/<lang>/_snippets/<topic>.md`, create the file with the snippet body framed by the markers and no per-page frontmatter (Hard rule 11).
2. Replace each consumer page's duplicated block with the `{% include-markdown … %}` directive, preserving page frontmatter and any surrounding paragraphs untouched (Hard rule 2).
3. Run `mkdocs build --strict` (Hard rule 5). On non-zero exit, revert every write made for this finding and surface the raw stderr (Hard rule 3); the finding-id stays approved but unapplied so the user can retry after fixing the underlying issue.

## Output contract

The skill returns to the user, in this order:

1. **Operation + target**: which operation ran (`audit` / `propose` / `apply`), absolute target repo root, resolved language scope.
2. **Pre-state** (for `audit`): page count walked, total markdown lines hashed, pages skipped (catalog generator, `_`-prefixed folders, already-include consumers).
3. **Findings table** (for `audit`): ranked rows with `id`, `lines`, `occurrences`, `pages` (absolute paths), `snippet_preview` (first 200 chars), `proposed_canonical_source`; followed by the `approve <id>` / `skip <id>` choice list.
4. **Proposed extraction** (for `propose`): full snippet body, canonical source path with marker positions, per-consumer include directive, expected build delta.
5. **Approval gate** (for `propose`): explicit user-decision point; nothing is written until the user confirms.
6. **Applied edits** (for `apply`): list of files actually written, with absolute paths and the marker comments inserted (one row per file).
7. **Build verification** (for `apply`): `mkdocs build --strict` exit code; on failure the raw stderr block verbatim plus the revert log.
8. **Caller follow-ups**: explicit list — commit the working-tree edits, optionally re-run `audit` to surface residual findings, optionally route to `mkdocs-structure-apply audit` to verify §Snippet inclusion (DRY) conformance end-to-end, open the PR via `pull-request-create`. Never bump the plugin version, commit, push, tag, or open PRs from this skill.

## Examples

- Read `examples/01-audit-duplicate-paragraphs.md` when running a read-only `audit` that hashes paragraph blocks, ranks duplicates over the DRY threshold, and proposes a canonical source per finding.
- Read `examples/02-propose-live-source-extraction.md` when running `propose <id>` for a finding whose canonical source is a live non-docs file (e.g. `CONTRIBUTING.md`) and surfacing markers plus include directives at the approval gate.
- Read `examples/03-apply-new-snippet-file.md` when running `apply <id>` for a finding with no live source, creating a dedicated `_snippets/` fragment and gating the write on `mkdocs build --strict`.

## Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/docs-dry-refactor/<run-id>.yml` after every successful user-approval gate and after each named phase boundary. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope (`schema_version`, `run_id`, `inputs`, `phase`, `decisions[]`, `status`, ...) and the fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

## Hard rules

1. **Never auto-rewrite.** Each proposed extraction requires per-snippet user approval. `approve all` after a `audit` is acceptable when the user explicitly asks for it; silent rewrite is forbidden.
2. **Never destroy page frontmatter.** When a duplicated block sits next to a page's frontmatter (`title`, `audience`, `last_updated`), preserve the frontmatter intact. Those fields **MUST NOT** ever migrate into a snippet.
3. **Never commit a page whose `mkdocs build --strict` fails post-extract.** A failing build reverts every write made for the failing finding and surfaces the raw stderr; the finding stays approved but unapplied so the user can retry after fixing the cause.
4. **Always read the spec at runtime.** Prefer `spec/project/mkdocs-structure/<canonical_language>.md` in the target repo; fall back to the copy shipped by the `nolte-shared` plugin only when the target lacks one. Never bake the DRY thresholds (≥3 lines, ≥2 pages) into the skill. When neither copy is reachable, stop and ask the user which spec source to use.
5. **Always run `mkdocs build --strict` after every `apply`.** The build is the authoritative rendering gate; a passing local build is the floor, not the ceiling.
6. **Never touch generated catalog pages.** `docs/<lang>/skills/SUMMARY.md`, `docs/<lang>/skills/<plugin>/<name>.md`, `docs/<lang>/agents/<plugin>/<name>.md`, `docs/<lang>/tags.md` are emitted by the catalog generator and are excluded from `audit`. The skill never rewrites or proposes extractions over them.
7. **Never break existing include chains.** Pages already containing `{% include-markdown … %}` are flagged as "partial DRY (existing include)" hints in `audit` and skipped from new findings; the skill never overlays a new include over an existing one.
8. **Prefer live-source canonical files over dedicated snippet files.** When the duplicated content originates from a non-docs file (CONTRIBUTING.md, `pyproject.toml`, a workflow step name, a source file), surface that file as the canonical source. Only when no such source exists, propose a new `docs/<lang>/_snippets/<topic>.md`.
9. **Never bump versions, commit, push, tag releases, or open pull requests.** The skill produces working-tree edits only; lifecycle is owned by `pull-request-create`, `pull-request-merge`, and `release-publish-trigger`.
10. **Never dispatch the `Skill` tool recursively into this skill.** The skill **MAY** orchestrate the `audience-doc-author` agent for snippet-body authoring and chain to the `mkdocs-structure-apply` skill (audit mode) for post-extract verification at the explicit hand-off points named in the Output contract; silent recursion isn't allowed.
11. **Dedicated snippet files are fragments, not pages.** They **MUST NOT** carry per-page frontmatter (`title`, `audience`, `last_updated`) and **MUST** live under a `_`-prefixed folder inside `docs/<lang>/` (typically `docs/<lang>/_snippets/`) so MkDocs doesn't render them in the nav.
12. **Marker format is consistent and content-named.** Start and end markers use the canonical source's native comment syntax (`<!-- docs-include-start: <name> -->` for HTML and Markdown, `# docs-include-start: <name>` for YAML and Python, `// docs-include-start: <name>` for JSON-with-comments). Marker names are kebab-case after the content they bracket (`lint-job`, `release-checklist`), never positional (`section-1`, `section-2`).
13. **Always** apply snippet extractions, marker insertions, and consumer-page rewrites symmetrically across every language tree configured in `spec/.spec-config.yml`'s `languages` list, per `spec/project/docs-multilingual-authoring/` §Authoring protocol. A language-neutral snippet (a code excerpt, a YAML fragment, a CLI transcript) **MAY** live in only one language tree and be included from every other (the spec's preferred shape for non-prose content); a translatable-prose snippet **MUST** exist once per language under `docs/<lang>/_snippets/`. Rewriting a consumer page in `docs/<canonical_language>/` without applying the same include directive to every counterpart in `docs/<other_language>/` is a violation.

## Gotchas

Per `spec/claude/skill-management/` §Gotchas: concrete corrections to non-obvious environment facts the executing agent would otherwise get wrong.

- **Whitespace-tolerance vs. semantic equality.** Two paragraph blocks are treated as identical only when, after `re.sub(r'\s+', ' ', s).strip()`, their hashes match. Trailing whitespace, mixed indentation, and consecutive blank lines collapse harmlessly; differing words (even one) produce different hashes and aren't deduplicated. That's the desired behaviour—near-duplicates that diverge by design shouldn't be DRY-refactored (per spec §Snippet inclusion (DRY): "if the wording must diverge by design, the divergence is a sign the content isn't really shared").
- **Code-fence awareness.** Blocks inside ```…``` fences count as one indivisible unit and are hashed whole; multi-line code blocks are never split mid-fence. Inline code (single backticks) hashes as part of its containing paragraph, which is the right behaviour for CLI-snippet DRY detection.
- **Frontmatter is stripped before splitting.** The `---`-delimited YAML block at the page head is removed before paragraph-split, so frontmatter never appears in findings (Hard rule 2 enforces the invariant on the write side; this is the read-side mirror).
- **`mkdocs-include-markdown-plugin` resolves include paths relative to `docs_dir`, not to the consuming page.** A `{% include-markdown "../CONTRIBUTING.md" %}` from `docs/en/guides/intro.md` resolves from `docs/` outward, not from the page file's directory. The skill computes the include path from `docs_dir` when generating directives so the user doesn't get bitten by the wrong path origin.
- **Existing include chains are skipped, not consolidated.** Pages already containing at least one `{% include-markdown … %}` are surfaced as "partial DRY" hints (with a note pointing at potentially-overlapping consolidation candidates) but never replaced; consolidating overlapping include chains is a separate decision the user owns, not an automatic transformation.
