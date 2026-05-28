---
title: vocab-drift-audit
audience: [maintainer]
content_mode: reference
track: developer-docs
last_updated: generated
---

# vocab-drift-audit

> Auditiert lokale Vale-Vokabularien gegen den gepinnten Upstream-Release nolte/vale-style auf Drift.

_Audit repository-local Vale vocabularies against the pinned upstream release of nolte/vale-style to detect drift. Dispatches vocab-drift-scanner agent for the read-only diff step; follow-up actions (delete entries, bump pin, draft upstream PR) stay user-controlled in this skill. Invoke when the user asks to audit the Vale vocabulary, check for vocabulary drift, diff the local vocab against nolte/vale-style, or review whether local Vale terms can be retired. Also handles equivalent German-language requests. Reports local entries that are already accepted upstream (should be deleted) and local entries that aren't yet upstream (should be PR'd to nolte/vale-style). Supports resume on re-invocation per `spec/claude/resumable-work/`._

- **Plugin:** `nolte-shared`
- **Phase:** 6 Quality (`quality`)
- **Tags:** `audit`
- **Quelle:** [skills/vocab-drift-audit/SKILL.md](https://github.com/nolte/claude-shared/blob/main/skills/vocab-drift-audit/SKILL.md)

## Anwenden wenn

- you want to audit the local Vale vocabulary for drift against upstream
- you want to find local terms that can be retired (already upstream)
- you want to find local terms that should be PR'd upstream

## Siehe auch

- [`vocab-drift-scanner`](../../agents/nolte-shared/vocab-drift-scanner.md)
- [`prose-vale-curator`](../../agents/nolte-shared/prose-vale-curator.md)

---

## Vocab Drift Audit

Operationalises the MUST rule in `spec/project/prose-style/<canonical_language>.md`: "once the upstream change is released, the local entry MUST be removed and the pinned `nolte/vale-style` release MUST be bumped." Apply the prose-style spec's rules when it's present in the current project; otherwise, fall back to the conventions described here.

### Why this is a skill, not an agent

- **Output flows back into the main conversation** — the diff report (duplicates to remove, upstream PR candidates) is the input to follow-up actions the user authorises in the same turn (delete local entries, draft an upstream PR, bump the pinned tag).
- **Interactivity guards against destructive defaults** — the skill never deletes accepted-locally entries or bumps the pin without explicit user confirmation; that gating is core to the contract and would be lost in an agent's fire-and-forget shape.
- **Orchestration role** — typical use is one step inside a "tidy the prose tooling before a release" flow that may chain into [`pull-request-create`](pull-request-create.md) for the upstream contribution; the skill-orchestrates pattern (per `skill-vs-agent`) defaults the orchestrator to skill form.
- Counter-dimension considered and accepted: the read-only scan phase is now extracted into [`vocab-drift-scanner`](../../agents/nolte-shared/vocab-drift-scanner.md) (agent) per the Hybrid pattern in `skill-vs-agent`. The follow-up actions (delete entries, bump pin, draft upstream PR) require user confirmation and stay in the skill; the orchestration role keeps the skill form appropriate for this outer flow.

### User-language policy

Detect the user's language from their message and respond in it. The audit report itself uses English section headings (matching the upstream repo), but prose around the report is localised.

### Inputs

- **Repo root**: default: current working directory. The repo must contain a `.vale.ini` (at root or under a documentation root) that pins a `nolte/vale-style` release.
- **Upstream pin**: parsed automatically from `.vale.ini`. Look at the `Packages =` line for a URL of the form `https://github.com/nolte/vale-style/releases/download/<tag>/nolte-styles.zip`; the `<tag>` is the pin. If the URL is missing or the tag is non-semver, stop and report instead of guessing.
- **Local vocabularies**: every git-tracked `accept.txt` under the repo's Vale `StylesPath` (and under any folder named `vocabularies/` inside the repo). `vale sync`'d files are conventionally gitignored, so git-tracked entries are treated as local overrides.

### Operations

1. **Locate the Vale config.** Read `.vale.ini` from the repo root first, then from common alternative locations (`docs/.vale.ini`, `.github/.vale.ini`). Extract `StylesPath` and the `nolte/vale-style` pin tag. If either is missing, stop with a clear message.
2. **Dispatch [`vocab-drift-scanner`](../../agents/nolte-shared/vocab-drift-scanner.md) (Agent) for the read-only diff between the repository's local `accept.txt` files and the pinned upstream `nolte/vale-style` tag. Wait for its drift inventory before proceeding to user-confirmation and follow-up actions.**
3. **Render the report** from the agent's drift inventory as Markdown with three sections in this order: `## Duplicates to remove`, `## Upstream PR candidates`, `## Health`. Group findings under each section by local vocabulary file, and show the file path relative to the repo root.
4. **Offer follow-up actions** in the response (don't execute them without explicit confirmation):
   - Delete the duplicate lines from the local `accept.txt` files and bump the pinned tag in `.vale.ini` if a newer `nolte/vale-style` release is available.
   - Draft a single PR body for `nolte/vale-style` that lists all upstream PR candidates grouped by target vocabulary, with a one-line justification placeholder per entry.

### Report format

```
## Vocab Drift Audit

Pin: nolte/vale-style@<tag> (from <.vale.ini path>)
StylesPath: <value>

### Duplicates to remove
<path/to/accept.txt>
- <entry>  (also in upstream: <vocab>)
- …

### Upstream PR candidates
<path/to/accept.txt>
- <entry>  (suggested upstream vocab: <best-guess vocab>)
- …

### Health
- Local vocabularies: <n> files, <m> entries total
- Upstream vocabularies at <tag>: <n> vocabs, <m> entries total
- Duplicates: <count>
- PR candidates: <count>
- Latest nolte/vale-style release: <tag> (<note whether the pin is behind>)
```

The "Latest release" line comes from `gh api repos/nolte/vale-style/releases/latest --jq .tag_name`. If it differs from the pin, flag it but don't bump automatically.

### Gotchas

- **`vale sync` populates `.vale-styles/` (or whatever `StylesPath` resolves to) at build time.** The audit reads from the actual `accept.txt` files on disk, not from the upstream tag in `.vale.ini`'s `Packages:` block. When the local `vale sync` ran against an old pin, the audit reflects the old pin's vocabulary — re-run `vale sync` before the audit if the local pin matches but the local files look stale.
- **Repository-local vocabularies live under `styles/` / `nolte-styles/` / `config/vocabularies/`** depending on the repo. The audit walks every directory configured in `.vale.ini`'s `StylesPath` plus the `Packages:` cache; assuming a single canonical location misses entries. Read `.vale.ini` first and enumerate every path the audit touches.
- **An entry that's "already accepted upstream" depends on the upstream tag pin, not on the latest upstream release.** The audit compares against the pinned upstream tag's `accept.txt` snapshot — bumping the pin is a separate operator decision, not part of this audit. The "delete locally" recommendation only fires when the entry exists at the *currently pinned* upstream tag.
- **Regex entries in `accept.txt` need careful comparison.** Two entries may match the same string but be different patterns (`pip-?audit` vs. `pip ?audit`); the audit treats them as distinct entries even when their match-set overlaps. Don't recommend deletion just because the upstream regex has wider coverage; the operator decides whether the wider regex makes the local one redundant.
- **The `## Old patterns` section in `accept.txt` is a graveyard, not active scope.** Some vocabularies use a section to keep historical-but-no-longer-active terms; the audit skips that section by convention. Verify the per-vocabulary convention in the repository's curation spec when it exists; otherwise the agent treats every line as active and may flag legitimate retired entries.

### Examples

- Read `examples/01-local-entries-now-upstream.md` when local vocabulary entries are already accepted upstream and should be deleted locally.
- Read `examples/02-local-entries-not-yet-upstream.md` when local entries aren't yet in the upstream vocabulary and need to be PR'd to `nolte/vale-style`.
- Read `examples/03-pinned-tag-vs-latest-release.md` when the pinned upstream tag differs from the latest release and you need to understand how the comparison is scoped.

### Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/vocab-drift-audit/<run-id>.yml` after every successful user-approval gate and after each named phase boundary. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope (`schema_version`, `run_id`, `inputs`, `phase`, `decisions[]`, `status`, ...) and the fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

### Hard rules

- Never modify files without explicit user confirmation. This skill reports; mutations are a follow-up step the user approves.
- Never bump the `nolte/vale-style` pin unless the user asks for it, even when the audit shows duplicates.
- Never invent upstream entries. If `gh api` fails or the tag doesn't exist, stop and report the error—don't fall back to `main`/`develop`.
- Never skip a local vocabulary file because it "looks like" an upstream copy. Membership in the upstream set is determined by the fetched upstream content, not by filename heuristics.
- Keep the report sections in the fixed order (`Duplicates to remove`, `Upstream PR candidates`, `Health`) so downstream consumers can parse it reliably.
- Don't touch anything outside the prose-style / Vale scope. This skill isn't a general vocabulary linter for other stylers.

### Multi-model testing

Examples and operations in this skill are verified on Claude Sonnet 4.6 as the default model; spot-checked on Haiku 4.5 for cost-sensitive runs; Opus 4.7 is appropriate for high-stakes audits that require deeper reasoning. The skill body has no model-specific assumptions beyond standard tool-call semantics.
