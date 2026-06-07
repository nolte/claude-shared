---
name: lektorat-apply
description: Reviews existing Markdown prose against five editorial dimensions (readability, comprehensibility, grammar, style, audience-fit) defined in `spec/project/lektorat/`. Three operations — `audit` (read-only report), `patch` (one finding, one diff, one approval), `revise` (full-artefact rewrite with diff review); dispatches `lektorat-scanner` for the detection phase. Invoke when the user asks to "lektoriere README.md", "audit docs for audience-fit", "revise this page with Lektorat", "prüfe auf Lesbarkeit", or equivalent EN/DE requests. Writes outputs to `.audits/lektorat/<YYYY-MM-DD-HHMM>/`. Don't use to author new prose (use `audience-doc-author`), curate Vale rules (use `prose-vale-curator`), lektor `spec/` files (out of scope), or edit code, configs, or LLM-instruction artefacts (SKILL.md, agents/*.md). Supports resume on re-invocation per `spec/claude/resumable-work/`.
tags: [prose, audit]
phase: quality
summary: "Reviews existing Markdown prose against five editorial dimensions (readability, comprehensibility, grammar, style, audience-fit)."
summary_de: "Prüft bestehende Markdown-Prosa gegen fünf Lektorats-Dimensionen (Lesbarkeit, Verständlichkeit, Grammatik, Stil, Audience-Fit)."
use_when:
  - "you want to audit existing docs for editorial quality"
  - "you want to apply a single editorial fix as a one-finding, one-diff change"
  - "you want a full-artefact rewrite with diff review (lektorat revise)"
dont_use_when:
  - situation: "You want to author new prose from scratch"
    alternative: audience-doc-author
  - situation: "You want to curate Vale rules rather than fix prose"
    alternative: prose-vale-curator
see_also:
  - audience-doc-author
  - prose-vale-curator
  - lektorat-scanner
resumable: true
---

# Lektorat Apply

Operationalises `spec/project/lektorat/` for the `nolte-shared` plugin: the editorial layer that audits, patches, or revises already-existing human-readable Markdown prose against five named quality dimensions, with a per-language rule set and explicit operator dialogue at every mutating step.

This skill binds the spec's contract to an on-disk procedure. It does not redefine the rules; when this skill and the spec disagree, the spec wins and this skill needs the update.

## German trigger phrases

This skill also triggers on equivalent German-language requests, including:

- "lektoriere die README"
- "prüfe diese Doku auf Lesbarkeit"
- "audit die Seite auf Audience-Fit"
- "revise diesen Eintrag mit Lektorat"
- "Rechtschreibung in den deutschen Docs prüfen"

## User-language policy

Detect the user's language from their message and respond in it. The machine-readable JSON output uses English keys (per `spec/project/lektorat/` §Outputs); the human-readable Markdown summary uses English section headings so downstream tooling can parse it reliably; prose around the report is localised.

The artefact being reviewed is **not** translated by this skill. Each file is reviewed against the rules of its own language (DE-rules on DE-text, EN-rules on EN-text); cross-language translation belongs to the `spec` skill or `docs-multilingual-authoring`.

## Why this is a skill, not an agent

- **Mid-flow user approval is load-bearing**: `patch` requires explicit per-finding approval before any write (one finding, one diff, one OK), and `revise` requires diff review on the full-artefact rewrite. Agents have no stable way to surface that dialogue back to the parent.
- **Externally visible writes**: outputs land under `.audits/lektorat/<YYYY-MM-DD-HHMM>/` and, in `patch` / `revise`, modify in-scope Markdown artefacts. The skill owns the persistent on-disk state.
- **Orchestration role**: this skill dispatches the `lektorat-scanner` agent for the read-only D1–D5 detection (context-window protection, tool restriction) and stays in the main thread to render results, run operator dialogues, and write outputs.
- **Counter-dimension considered and accepted**: the `audit` operation alone fits the agent shape cleanly (self-contained input, structured output, no interactivity). It still lives in this skill because `patch` and `revise` reuse the same detection inventory and consolidating the three operations behind one entry point keeps the operator's mental model coherent. The scan half is delegated to the agent; the orchestration half stays in the skill per the hybrid pattern from `spec/claude/skill-vs-agent/`.

## Inputs

- **Target set**: one of (a) a single artefact path the user named, (b) a directory the user named (every in-scope file under it is reviewed), (c) the whole repository (default when the user gave no scope but invoked the skill). The set is filtered through §Scope and applicability in `spec/project/lektorat/` before any scan runs.
- **Operation**: `audit` (default), `patch`, or `revise`. The operation name must match the spec's closed vocabulary exactly; synonyms like `check` or `rewrite` are rejected.
- **Severity floor** (optional, applies to all operations): defaults to `suggestion` (report everything). The caller may narrow to `warning` or `critical` to de-noise gate-style runs.
- **Audience-artefact path** (optional, defaults to `AUDIENCES.md` at the bounded-context root per `audience-identification`): the skill resolves the artefact through the priority chain in `spec/project/lektorat/` §Audience binding; missing artefact stops the run with the message documented under §Hard rules.

## Operations

### 1. `audit` (read-only)

Runs the spec's `audit` operation per §Operations §Operation A — `audit`. The operation completes without operator interaction and is suitable for CI / pre-commit / sprint-review / release-publish gates.

1. **Resolve scope** — filter the user-supplied target set against `spec/project/lektorat/` §Scope and applicability. Reject any path under `spec/`, `skills/`, `agents/`, source code, generated configs, or binary artefacts with the single-sentence rejection message the spec mandates. Code fences, inline code, HTML comments, and YAML frontmatter are read-only context.
2. **Resolve languages** — apply the file-to-language priority chain in §Language handling (path segment under `docs/<lang>/`, suffix convention `*.<lang>.md`, repository default from `spec/.spec-config.yml`, interactive operator choice as last resort). Never auto-detect from text content. Record the resolved language per file; this drives whether EN-mechanics or DE-mechanics fire.
3. **Resolve audiences** — read the audience artefact via the priority chain in §Audience binding. If missing at every declared location, **stop** with the single-sentence error message pointing at the `audience-identify` skill; never invent audiences. Resolve each artefact's applicable audiences via frontmatter `audience:` → artefact-type defaults → whole audience set (priority order from the spec).
4. **Dispatch the read-only scanner** — dispatch `lektorat-scanner` (Agent) with the resolved (file, language, audiences, content_mode, audience-artefact) tuples and the severity floor. Wait for its structured findings inventory before proceeding. The spec leaves the dispatch shape open (one agent run per artefact vs. one batched run for the whole set); pick batched as the default and split per-file only when an artefact set spans more files than a single agent context can hold comfortably.
5. **Render the JSON report** following the verbatim shape in `spec/project/lektorat/` §Outputs §Findings report (machine-readable). The top-level keys, in order, are `operation`, `operation_version`, `repository`, `ran_at`, `language_summary`, `pipeline_metadata`, `inventory_findings`, and `findings`. `pipeline_metadata.<language>` carries the resolved tool/version/configured_path per language; `inventory_findings` carries infrastructure-level scan conditions (closed `kind` enumeration) that the scanner could not silently work around. Keep `id` stable across runs (hash of file + dimension + line) so dismissals recorded in earlier runs can be honoured.
6. **Surface inventory conditions first** — when the scanner returns a non-empty `inventory_findings` array, render those as the first section of the Markdown summary under the heading **Infrastructure conditions**, before any severity-grouped editorial findings. They indicate parts of the scan that could not complete (Vale missing, DE pipeline missing, audience artefact missing, language ambiguous, content-mode missing). They carry no severity and are never auto-patchable.
7. **Render the human-readable Markdown summary** — severity-sorted (`critical` first, then `warning`, then `suggestion`), within severity grouped by file then dimension, with each finding showing the offending sample (≤240 chars), the named rule or metric, the resolution hint, and the audience IDs the finding cites.
8. **Write both outputs** under `.audits/lektorat/<YYYY-MM-DD-HHMM>/` (timestamp in UTC). The JSON file is `findings.json`; the Markdown summary is `summary.md`; the caller-side configuration record (severity floor, resolved target set, user-supplied options) is `run.json`. Pipeline metadata (tool name + version + configured path) lives in `findings.json`'s `pipeline_metadata` block per the spec, not in `run.json`.
9. **Confirm in the user's language** with: the audit-trail folder path, the per-severity counts, the `inventory_findings` count when non-zero, and a one-line next-step hint (`patch` for interactive fixes, `revise` for full-artefact rewrites, or no action when the run was a gate check).

The `audit` operation never writes outside `.audits/lektorat/`, never edits any in-scope artefact, and never dispatches any mutating tool. Deterministic re-run produces a byte-identical `findings` array (modulo `ran_at`) on an unchanged repository.

### 2. `patch` (one finding, one diff, one approval)

Runs the spec's `patch` operation per §Operations §Operation B — `patch`. Each approval cycle resolves at most one finding.

1. **Run `audit` first** (see operation 1) — the patch list is the audit's `findings` array (editorial findings only); `inventory_findings` are **not** patchable. If the caller invoked `patch` standalone, run `audit` implicitly and cache the inventory.
2. **Block on infrastructure conditions** — when `inventory_findings` is non-empty, surface the list to the operator before any patch loop starts. The operator decides: resolve the underlying condition and re-run, or proceed with the partial `findings` set acknowledging the skipped dimensions. Never silently iterate over a partial inventory.
3. **Sort findings in severity order** (`critical` → `warning` → `suggestion`) and present them to the operator one at a time. Within a severity, ties broken by file path then dimension.
4. **For each finding, render the proposed edit as a unified diff** against the on-disk artefact with at least three context lines, labelled with the operation name (`patch`), the finding ID, and the file's repo-relative path. Show the finding's evidence and resolution hint alongside the diff.
5. **Wait for explicit operator decision**: `approve` writes the diff to disk; `skip` defers the finding to the next run; `skip-and-record` records a permanent dismissal (by finding `id`) under `.audits/lektorat/<run>/dismissals.json` so future `audit` runs do not re-surface it.
6. **Pre-write safety checks** (refactor-safety per §Refactor safety): heading-text changes that move the MkDocs-derived slug **must** announce the slug churn to the operator before the write is approved; block-quoted citations and HTML comments **must** stay byte-identical; link `[text](target)` pairs are preserved unless the finding explicitly targets the link; frontmatter key set and key order are preserved; embedded include directives are byte-identical; list items, table rows, and checklist entries are neither reordered, merged, nor split.
7. **After every approved write, re-render the JSON and Markdown reports** under the same `.audits/lektorat/<run>/` folder so the audit-trail reflects the post-patch state. Do not start a fresh run folder per patch; the patch belongs to the audit run that surfaced the finding.

The `patch` operation never silently combines multiple findings into a single edit; a multi-finding fix is a sequence of `patch` operations, not a single one.

### 3. `revise` (full-artefact rewrite with diff review)

Runs the spec's `revise` operation per §Operations §Operation C — `revise`. The rewrite addresses every `critical` and `warning` finding from the prior `audit` in a single pass.

1. **Run `audit` first** on the target artefact (single file, not a set — `revise` is per-artefact). Cache the pre-`revise` findings list and the pre-`revise` total count.
2. **Compose the rewrite** addressing every `critical` and `warning` finding; `suggestion` findings are optional and only adopted when adopting them does not extend the rewrite scope.
3. **Enforce semantic preservation** per §Operation C: every fact, claim, command, identifier, link target, frontmatter key, and code block from the original must still be present in the rewrite, with at most lexical changes (active voice, shorter sentences, lifted prerequisites). Never delete a section, drop a list item or checklist entry, drop a table row, or change a code block — those are structural decisions outside the spec's `revise` scope and belong to the operator.
4. **Forbid new factual content**: if the prose required an addition (new command, new file path, new product name, new URL) that was not present in the original, the operation **must** surface a `suggestion` to the operator and stop. Never invent facts to round out the rewrite.
5. **Render the unified diff** of the proposed full-artefact rewrite (operation `revise`, finding IDs addressed, repo-relative path), with at least three context lines.
6. **Wait for explicit operator decision** on the full diff: `approve` writes the rewrite; `reject` discards it; `revise` invites operator edit instructions and re-composes the rewrite before showing the diff again. Until approval lands, the on-disk artefact is untouched.
7. **Re-run `audit` on the rewrite** before declaring success. Surface any **new** findings the rewrite introduced; if the post-`revise` total finding count exceeds the pre-`revise` count, label the run a **regression** in the operator-facing confirmation and let the operator decide whether to keep, reject, or `revise`-again.
8. **Update the audit-trail folder**: write `pre-revise.json`, `post-revise.json`, `rewrite.diff`, and update `summary.md` to record the regression status. Do not overwrite the original `audit` reports; the `revise` artefacts are siblings.

The `revise` operation never starts without a fresh `audit` pass and never writes the rewrite to disk until the operator explicitly approves the diff.

## Output handling

All persistent outputs live under `.audits/lektorat/<YYYY-MM-DD-HHMM>/` in the active repository (timestamp in UTC, minute-precision). The folder layout:

```
.audits/lektorat/<YYYY-MM-DD-HHMM>/
├── findings.json        # Machine-readable; top-level keys per spec §Outputs:
│                        #   operation, operation_version, repository, ran_at,
│                        #   language_summary, pipeline_metadata,
│                        #   inventory_findings, findings
├── summary.md           # Human-readable; Infrastructure conditions first,
│                        #   then editorial findings severity-sorted
├── run.json             # Caller-side config: severity floor, resolved target set,
│                        #   user-supplied options (NOT pipeline metadata —
│                        #   that lives in findings.json's pipeline_metadata)
├── dismissals.json      # Recorded skip-and-record entries (patch only)
├── pre-revise.json      # revise only: pre-rewrite audit
├── post-revise.json     # revise only: post-rewrite audit
└── rewrite.diff         # revise only: unified diff of the rewrite
```

Mirrors the audit-trail convention used by `.audits/portfolio/`, `.audits/skill-review/`, and similar layered audits. The folder is per-run; never reuse an existing timestamped folder for a fresh run.

## Examples

- Read `examples/01-audit-bilingual-repo.md` when running an `audit` across a repository with both DE and EN documentation trees.
- Read `examples/02-patch-readme-critical.md` when running `patch` on a published top-level artefact (README) with a mix of `critical` and `warning` findings.
- Read `examples/03-revise-tutorial-page.md` when running `revise` on a tutorial page whose readability metric crosses the corridor and whose voice flips active/passive.

## Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/lektorat-apply/<run-id>.yml` after every successful user-approval gate and after each named phase boundary. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope (`schema_version`, `run_id`, `inputs`, `phase`, `decisions[]`, `status`, ...) and the fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

## Hard rules

- The five quality dimensions (D1–D5), the three operations (`audit` / `patch` / `revise`), the three severities (`critical` / `warning` / `suggestion`), the JSON output shape, the per-language readability corridors, the refactor-safety invariants, the audience-binding priority chain, and the language-resolution chain are defined in `spec/project/lektorat/`. This skill **must not** redefine, relax, or extend them; when this skill and the spec disagree, the spec wins.
- Never lektor a file under `spec/`, `skills/**/SKILL.md`, `skills/**/templates/**`, `skills/**/examples/**`, or `agents/*.md`. Reject with a single-sentence message naming the responsible authoring flow (the `spec` skill for `spec/`, `skill-management` for skill artefacts, `agent-management` for agent artefacts).
- Never lektor source code, code comments, docstrings, generated configuration (`.github/*.yml`, `mkdocs.yml`, `Taskfile.yml`, lockfiles), or binary artefacts. The scope is **Markdown prose**.
- Never write to any in-scope artefact during `audit`. The operation is read-only and must run unattended.
- Never combine multiple findings into a single `patch` edit; one finding, one diff, one approval.
- Never write the `revise` rewrite to disk until the operator explicitly approves the diff. Never introduce new factual content not present in the original artefact during `revise`.
- Never invent audiences. When the audience artefact is missing at every location declared in `spec/project/lektorat/` §Audience binding, stop with the single-sentence error message pointing at the `audience-identify` skill.
- Never rewrite a non-English passage inside an English-resolved file (or vice versa). Such a passage is a `D3` (spelling) or `D5` (register) finding and the resolution is flagged for the operator, not silently fixed.
- Never auto-detect a file's language from its text content for scope decisions. Use the path-segment / suffix / repository-default / interactive-choice chain in priority order.
- Never modify a Vale rule, a vocabulary entry, or any rule mechanic. Vale and `nolte/vale-style` are owned by `prose-style` and `vocab-drift-audit`; this skill consumes their output and surfaces it as `D3` / `D4` findings.
- Always preserve refactor-safety invariants in every mutating operation: code blocks, inline code, HTML comments, YAML frontmatter (key set and key order), block-quoted citations, link `[text](target)` pairs, heading IDs, embedded include directives, and the order and count of list items, table rows, and checklist entries.
- Always record the DE pipeline (tool name, version, configured path) in `findings.json`'s `pipeline_metadata.de` block per `spec/project/lektorat/` §Outputs — **not** in `run.json`, which carries only caller-side configuration (severity floor, resolved target set, user-supplied options). The portfolio default is the LanguageTool HTTP API; a repository may override it but the chosen tool **must** be recorded in `pipeline_metadata.de` for the run to be reproducible.
- Always cite the spec section that motivates a finding in the finding's `rule` field (for example `lektorat §D1 Readability` or `lektorat §D5 Audience-fit`); a finding without a spec citation is not a finding.

## Gotchas

- **`audit` deterministic re-run depends on stable finding IDs.** The `id` is the hash of file + dimension + line; if the implementation re-keys findings on every run, dismissals recorded under one ID won't match the next run's IDs and the spec's "dismissal does not re-surface" acceptance criterion fails. Use a stable hash, document its inputs in `run.json`, and never include `ran_at` or absolute paths in the hash.
- **DE pipeline tool choice is resolved at spec level: the portfolio default is the LanguageTool HTTP API** (`spec/project/lektorat/` §Open Questions §OQ-2, resolved). Use the Public endpoint (`https://api.languagetool.org/v2`) for open-source repositories or a self-hosted deployment of the same engine for repositories with sensitivity, throughput, or air-gap constraints — the HTTP-API contract is identical. A repository **may** override the default by pinning an alternative tool in its `Lektorat`-local configuration, but record whatever tool was actually used in `findings.json`'s `pipeline_metadata.de` so the audit-trail is reproducible.
- **`mkdocs-include-markdown-plugin` directives look like prose but are not.** Treat `{% include … %}` (or whatever syntax the plugin uses in the repository) as byte-identical context per §Refactor safety; the included source is reviewed when its own file is in scope, not through the consumer page. A naïve re-flow that paraphrases inside the include directive will silently break the include resolution at MkDocs build time.
- **`content_mode: meta` exempts D1 entirely.** Navigational pages (Home, per-section index) have no readability corridor; producing a D1 finding for a `meta` page is a spec violation, not a smell-test catch. Read the page's frontmatter `content_mode` before running D1 evaluation; when absent, fall back to the spec's `content_mode` default per `spec/project/mkdocs-structure/`.
- **`audit` against the whole repository on a first run can produce hundreds of findings.** The severity floor exists for a reason — gate-style runs (release-publish, sprint-review) should narrow to `critical` to keep the report actionable; the first end-to-end audit on a repo that never ran Lektorat before will surface a large `suggestion` backlog. Surface the per-severity counts up front in the operator-facing confirmation so the operator can decide whether to triage now or defer.
- **GitHub Release-note bodies and Issue / PR bodies live outside the repository tree.** The spec includes them as in-scope artefact types (per §Scope and applicability), but they are fetched via `gh api`, not read from `.`. The audit-trail still writes to `.audits/lektorat/<...>/` in the active repository; the source artefact's identifier in `findings.json` uses the `gh` URL shape (`gh:nolte/<repo>/release/<tag>` or `gh:nolte/<repo>/issues/<n>`) rather than a relative path so the link is unambiguous.
- **The skill never bumps version, never opens a PR, and never commits.** Mutating operations land on disk in the working tree; staging, committing, and PR-creation are the operator's call (via `git add` / `git commit` and `nolte-shared:pull-request-create`). Surfacing those follow-ups in the operator-facing confirmation is helpful; performing them silently is forbidden.

## Multi-model testing

Examples and operations in this skill are expected to work on Claude Sonnet (default), Haiku (cost-sensitive runs, smaller `audit` scopes), and Opus (high-stakes runs, large `revise` rewrites). The skill body has no model-specific assumptions beyond standard tool-call semantics; the dispatched `lektorat-scanner` agent pins its own model per its frontmatter.
