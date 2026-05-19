---
title: docs-audience-tracks-apply
audience: [maintainer]
content_mode: reference
track: developer-docs
last_updated: generated
---

# docs-audience-tracks-apply

_Audits a repository against spec/project/docs-audience-tracks/<canonical_language>.md and, with per-item user approval, scaffolds or patches the documentation-tracks layer: per-page `track:` frontmatter on every docs/<lang>/ page, the four required user-docs content blocks (installation, value proposition, audience, use cases) plus the SHOULD blocks (quickstart, troubleshooting), the three required developer-docs content blocks (setup, tech-stack, interfaces) plus the SHOULD blocks (architecture overview, glossary, troubleshooting, contribution flow), and the audience-to-track mapping inside the project's audience artefact. Three operations: `audit` (read-only conformance report), `migrate` (greenfield: add track frontmatter to every page that lacks it, scaffold missing content blocks), `patch` (additive fixes for one finding at a time). Invoke when the user asks to apply, audit, migrate, or patch documentation tracks against the spec; also handles equivalent German-language requests. Don't use for the MkDocs structural skeleton (use `mkdocs-structure-apply`), for the audience artefact itself (use `audience-identify`), for page content authoring (use `audience-doc-author`), for drift detection (use `docs-freshness-checker`), or for `prose` mechanics (use `prose-vale-curator`)._

- **Plugin:** `nolte-shared`
- **Phase:** 3 Design (`design`)
- **Tags:** `scaffolding`, `audit`
- **Source:** [skills/docs-audience-tracks-apply/SKILL.md](https://github.com/nolte/claude-shared/blob/main/skills/docs-audience-tracks-apply/SKILL.md)

---

## Documentation Audience Tracks Apply

Operationalises `spec/project/docs-audience-tracks/<canonical_language>.md` inside the current repository. The skill audits whether every page under `docs/<lang>/` carries the `track:` frontmatter, whether each track ships the content blocks the spec mandates, and whether the project's audience artefact maps each audience to a track. With explicit per-item user consent it migrates a greenfield documentation tree onto the contract or patches a single finding at a time.

When the spec isn't present in the target repository, fall back to the copy shipped by the `nolte-shared` plugin (read it at runtime from the plugin install path). Never invent requirements that don't appear in the spec.

### Rationale (why a skill, not an agent)

Per `spec/claude/skill-vs-agent/` §Decision dimensions, this capability is a skill because:

- **Mid-flow user approval is the contract.** Every page-frontmatter edit, every content-block scaffold, and every audience-artefact patch is written only with explicit per-change confirmation; the audit is read-only and the apply step is a sequence of approvals an agent's fire-and-forget shape can't carry.
- **Persistent on-disk output that flows back into the main conversation.** The audit table, the per-page proposals, the audience-artefact diff, and the post-migration `mkdocs build --strict` output all surface in the conversation so the user can decide; isolating them in a structured-report boundary would obscure the per-file approval surface.
- **Orchestrator pattern.** The skill can dispatch the `audience-doc-author` agent for content-block authoring once the container exists, the `audience-identify` skill for missing audience artefacts, and `docs-freshness-checker` for the post-migration parity check; per `spec/claude/skill-vs-agent/` §Hybrid pattern, the orchestrator is always a skill.
- **Precedent.** Follows the same audit + scaffold + patch shape as `mkdocs-structure-apply`, `project-structure-apply`, `skill-agent-catalog-apply`; portfolio-wide consistency (`spec/claude/skill-vs-agent/` §Portfolio-wide consistency) favours the same artefact type.
- **Counter-dimension considered.** A narrower agent could specialise on per-page frontmatter rewriting and gain on context-window protection, but the high-impact part is the per-block approval dialogue and the audience-artefact patch — both load-bearing on user judgement, not mechanical generation; skill wins.

### User-language policy

Detect the user's language from their message and respond in it. Generated artefacts (`docs/<lang>/` frontmatter, content-block placeholder pages, audience-artefact patches) are written in the language the surrounding `docs/<lang>/` tree uses; the `track:` and `content_mode:` keys are English-only because they're enumeration values, not prose.

### Tool selection rationale

Declared tools: `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`.

- `Read` / `Glob` / `Grep` for repository inspection (docs/<lang>/ trees, page frontmatter, audience artefact, marker files that indicate active extension specs).
- `Write` / `Edit` for scaffold and patch operations on per-page frontmatter, content-block placeholder pages, and the audience artefact; never overwriting an existing audience artefact wholesale (delegate that to `audience-identify`).
- `Bash` is necessary for `mkdocs build --strict` verification after migrations and for `git rev-parse --is-inside-work-tree` precondition. No destructive bash (no `git push`, no `gh pr create`, no `rm`).
- No `WebFetch` / `WebSearch`: the spec is the only source of truth.

### Preconditions

Before doing anything:

1. Confirm the working directory is a git repository (`git rev-parse --is-inside-work-tree`).
2. Locate `spec/project/docs-audience-tracks/<canonical_language>.md` — either in the target repo or via the `nolte-shared` plugin. If neither is reachable, stop and ask the user which spec source to use.
3. Locate the audience artefact per `spec/project/audience-identification/` §Artifact location (`AUDIENCES.md` at the bounded-context root, or the documented alternative). If the artefact is missing, stop and route the user to the `audience-identify` skill — this skill cannot proceed without an authoritative audience list.
4. Locate `mkdocs.yml` and derive the language list. If `mkdocs.yml` is absent, route the user to `mkdocs-structure-apply` first.
5. Resolve the operation:
   - User asked for a read-only audit → `audit`.
   - `docs/<lang>/` pages mostly lack `track:` frontmatter (>50% missing) → `migrate` is the default (subject to user confirmation).
   - Single finding to fix → `patch`.
6. Check for uncommitted changes in `docs/`, the audience artefact, and `mkdocs.yml`. If the tree is dirty there, report and ask whether to stash, commit, or abort — never overwrite uncommitted work.

### Operations

#### 1. `audit` (read-only)

Walk through the spec's Acceptance Criteria one item at a time, classify each finding as `pass`, `missing`, or `drift`. Group findings by spec area:

- **Track frontmatter** (per `spec/project/docs-audience-tracks/` §Per-page contract): every page under `docs/<lang>/` outside `_`-prefixed snippet folders carries `track:` whose value is `user-docs`, `developer-docs`, or an explicitly opted-in extension value. Report:
  - Missing-key findings.
  - Unrecognised-value findings.
- **Audience-to-track mapping** (per §Audience-to-track mapping): the audience artefact maps every listed audience to exactly one canonical track, or carries an explicit omission note for an unserved track. Verify the default mapping (`user` → `user-docs`; `contributor` / `operator` / `release-manager` → `developer-docs`) when the artefact doesn't override.
- **User-docs content contract** (per §User-docs content contract; skip when the audience artefact opts out of `user-docs`): the four MUST blocks (installation / onboarding, value proposition, audience, use cases) are present and reachable from the Home page within one navigation step. The two SHOULD blocks (quickstart, troubleshooting) are reported as suggestions, not failures.
- **Developer-docs content contract** (per §Developer-docs content contract; skip when the audience artefact opts out of `developer-docs`): the three MUST blocks (setup / prerequisites, tech-stack, interfaces / contracts) are present and reachable from the Home page within one navigation step. The four SHOULD blocks (architecture overview, glossary, troubleshooting, contribution flow) are reported as suggestions.
- **Content-mode mapping** (per §Content-mode mapping): every page declares `track` and `content_mode` independently; no page infers one from the other. Cross-check against the audience-track mismatch heuristic (`audience` value mapping to a different track than the page's `track` value) — report each mismatch.
- **Home-page contract** (per §Home-page contract): when the repository serves both tracks, the Home page (`docs/<lang>/index.md`) names both tracks in routing prose.

Audit is read-only — never autofix during audit.

#### 2. `migrate` (greenfield: most pages lack `track:`)

For each step below, confirm with the user per file or per group before writing.

- For every page under `docs/<lang>/` (outside `_`-prefixed snippet folders): propose adding `track:` to its frontmatter. Default the value from the page's path and existing `audience` frontmatter via the portfolio-baseline default mapping; never invent. When neither the path nor `audience` gives a deterministic answer, propose `track: # TODO: confirm` and ask the user inline.
- For every track the audience artefact serves and that lacks one of the MUST content blocks: scaffold a placeholder page at a stable location (`docs/<lang>/getting-started/installation.md` for installation, `docs/<lang>/index.md` H2 sections for value proposition / audience / use cases, `docs/<lang>/getting-started/setup.md` for setup, …). Write only the container plus the per-page frontmatter contract — page-content authoring belongs to the `audience-doc-author` agent or the human author.
- Patch the audience artefact to add the `track:` field next to each audience entry. When the artefact uses a structured table or list form (per the `audience-identify` skill's template), insert the new field in the right column or sub-bullet. When the artefact lacks a `track` field shape entirely, propose extending it and route the user to re-run `audience-identify`'s `validate` operation afterwards.
- When the repository serves both tracks but the Home page doesn't route between them, propose a one-paragraph addition to the Home page that points end users at the user-docs entry and contributors at the developer-docs entry.
- After every successful write, re-run `mkdocs build --strict` so the user sees the change verified end-to-end. A failing build stops the operation and surfaces the raw output verbatim; never claim success on a red build.

#### 3. `patch` (additive: a single finding from a prior audit)

For each `missing` or `drift` finding from an audit run, propose the exact change and ask the user to approve it before writing. Don't bundle unrelated changes into a single approval step.

- **Missing `track:` on a page**: propose the value via the default mapping, surface the rationale, request approval.
- **Unrecognised `track:` value**: surface the value, list the legal enumeration, request approval for a replacement.
- **Missing MUST content block**: propose the placeholder page (containers only, no prose), request approval.
- **Audience-track mismatch**: surface the conflict, propose two resolutions (change `track:` on the page, or change the audience-artefact entry), request the user's decision.
- **Audience artefact missing `track:` fields**: route the user to `audience-identify` to add them through the canonical methodology, rather than patching the artefact from this skill.

### Output contract

The skill returns to the user, in this order:

1. **Operation + target**: which operation ran (`audit` / `migrate` / `patch`), absolute target repo root, detected language list, detected audience artefact location.
2. **Pre-state**: brief summary of what was found (audience artefact present? `track:` coverage percentage across `docs/<lang>/`? both tracks served per audience artefact?).
3. **Audit findings** (always): grouped per spec area, with one row per Acceptance-Criteria item showing status (`pass` / `missing` / `drift`) and a one-line evidence snippet.
4. **Planned edits** (for `migrate` / `patch`): list of files to create or modify, one line per file, with rationale linking back to the spec line.
5. **Approval gate** (for `migrate` / `patch`): explicit user-decision point; nothing is written until the user confirms.
6. **Applied edits** (after approval): list of files actually written, with absolute paths.
7. **Build verification**: `mkdocs build --strict` exit code plus a raw output snippet on failure; on success report the build summary line only.
8. **Caller follow-ups**: explicit list — commit the working-tree edits, dispatch `audience-doc-author` to fill in the placeholder pages' bodies, route to `audience-identify` if the audience artefact needs the `track:` field added through the canonical methodology, open the PR via `pull-request-create`, and similar.

### Hard rules

1. **Never** author the prose body of a content block. The skill creates the *containers* (placeholder pages with frontmatter, the H1, and a single-paragraph stub naming the block's purpose), but never the prose. Block authoring belongs to the `audience-doc-author` agent or the human author.
2. **Never** invent a `track:` value when neither the path nor `audience` gives a deterministic mapping. The fallback is `track: # TODO: confirm` plus an inline question to the user.
3. **Never** rewrite the audience artefact wholesale. Inline patches (adding a `track:` field next to an existing entry) are permitted; structural rewrites belong to `audience-identify`.
4. **Never** modify content outside `docs/<lang>/`, the audience artefact, and (when explicitly approved) the Home page's routing paragraph. Theme, palette, nav order, and plugin baseline belong to `mkdocs-structure-apply`.
5. **Always** read the spec at runtime: prefer the target repo's `spec/project/docs-audience-tracks/<canonical_language>.md`; fall back to the copy shipped by the `nolte-shared` plugin only when the target repo lacks one. Never carry a baked-in copy inside the skill itself.
6. **Always** verify the build after every write: `mkdocs build --strict` must run green before the operation ends. A red build stops the operation.
7. **Always** preserve existing frontmatter keys when patching `track:` onto a page that already has `title` / `audience` / `content_mode` / `last_updated`. Add `track:` in its canonical position (between `content_mode` and `last_updated`) without touching the other keys.

### Sources

- `spec/project/docs-audience-tracks/` — the canonical authoritative spec this skill operationalises
- `spec/project/mkdocs-structure/` — the per-page frontmatter MUST set (`title`, `audience`, `content_mode`, `track`, `last_updated`) and the seven-section nav baseline
- `spec/project/audience-identification/` — the audience artefact this skill consumes and patches
- `spec/claude/skill-vs-agent/` — the skill-vs-agent decision dimensions that justify this artefact as a skill, not an agent
