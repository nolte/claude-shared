# vocab-drift-audit

_Audit repository-local Vale vocabularies against the pinned upstream release of nolte/vale-style to detect drift. Invoke when the user asks to audit the Vale vocabulary, check for vocabulary drift, diff the local vocab against nolte/vale-style, or review whether local Vale terms can be retired. Also handles equivalent German-language requests. Reports local entries that are already accepted upstream (should be deleted) and local entries that aren't yet upstream (should be PR'd to nolte/vale-style)._


- **Plugin:** `nolte-shared`
- **Tags:** `audit`
- **Source:** [skills/vocab-drift-audit/SKILL.md](https://github.com/nolte/claude-shared/blob/main/skills/vocab-drift-audit/SKILL.md)

---

# Vocab Drift Audit

Operationalises the MUST rule in `spec/project/prose-style/<canonical_language>.md`: "once the upstream change is released, the local entry MUST be removed and the pinned `nolte/vale-style` release MUST be bumped." Apply the prose-style spec's rules when it's present in the current project; otherwise, fall back to the conventions described here.

## Why this is a skill, not an agent

- **Output flows back into the main conversation** — the diff report (duplicates to remove, upstream PR candidates) is the input to follow-up actions the user authorises in the same turn (delete local entries, draft an upstream PR, bump the pinned tag).
- **Interactivity guards against destructive defaults** — the skill never deletes accepted-locally entries or bumps the pin without explicit user confirmation; that gating is core to the contract and would be lost in an agent's fire-and-forget shape.
- **Orchestration role** — typical use is one step inside a "tidy the prose tooling before a release" flow that may chain into `pull-request-create` for the upstream contribution; the skill-orchestrates pattern (per `skill-vs-agent`) defaults the orchestrator to skill form.
- Counter-dimension considered: an agent with `Bash`-only tool restriction could perform the read-only diff equally well, but the report-then-mutate split would force a second hop for the follow-up actions — keeping the whole flow in one skill is simpler.

## User-language policy

Detect the user's language from their message and respond in it. The audit report itself uses English section headings (matching the upstream repo), but prose around the report is localised.

## Inputs

- **Repo root**: default: current working directory. The repo must contain a `.vale.ini` (at root or under a documentation root) that pins a `nolte/vale-style` release.
- **Upstream pin**: parsed automatically from `.vale.ini`. Look at the `Packages =` line for a URL of the form `https://github.com/nolte/vale-style/releases/download/<tag>/nolte-styles.zip`; the `<tag>` is the pin. If the URL is missing or the tag is non-semver, stop and report instead of guessing.
- **Local vocabularies**: every git-tracked `accept.txt` under the repo's Vale `StylesPath` (and under any folder named `vocabularies/` inside the repo). `vale sync`'d files are conventionally gitignored, so git-tracked entries are treated as local overrides.

## Operation

1. **Locate the Vale config.** Read `.vale.ini` from the repo root first, then from common alternative locations (`docs/.vale.ini`, `.github/.vale.ini`). Extract `StylesPath` and the `nolte/vale-style` pin tag. If either is missing, stop with a clear message.
2. **Collect the upstream vocabulary for that pin.** List the upstream vocabulary directory at the pinned tag via `gh api "repos/nolte/vale-style/contents/src/styles/config/vocabularies?ref=<tag>"` and, for each subdirectory, fetch `accept.txt` at the same ref. Build one set per upstream vocabulary (for example `technical`, `esphome`, `technical-de`).
3. **Collect the repo-local vocabularies.** Use `git ls-files` filtered to `*/accept.txt` under `StylesPath` and any `vocabularies/` folder inside the repo. Normalise entries (strip comments starting with `#`, trim whitespace, drop empty lines). Case-sensitivity follows Vale: treat entries as case-insensitive for matching but preserve casing in the report.
4. **Diff.** For each local vocabulary, compute:
   - **Duplicates**: local entries whose normalised form already appears in any upstream vocabulary at the pinned tag. These MUST be removed per the prose-style spec.
   - **Upstream PR candidates**: local entries that don't appear in any upstream vocabulary. These are the reason the local override still exists; each one needs a PR against `nolte/vale-style`.
   - **Unused**: upstream entries that are also present locally aren't flagged as unused; this audit doesn't touch upstream-only noise.
5. **Render the report** as Markdown with three sections in this order: `## Duplicates to remove`, `## Upstream PR candidates`, `## Health`. Group findings under each section by local vocabulary file, and show the file path relative to the repo root.
6. **Offer follow-up actions** in the response (don't execute them without explicit confirmation):
   - Delete the duplicate lines from the local `accept.txt` files and bump the pinned tag in `.vale.ini` if a newer `nolte/vale-style` release is available.
   - Draft a single PR body for `nolte/vale-style` that lists all upstream PR candidates grouped by target vocabulary, with a one-line justification placeholder per entry.

## Report format

```
# Vocab Drift Audit

Pin: nolte/vale-style@<tag> (from <.vale.ini path>)
StylesPath: <value>

## Duplicates to remove
<path/to/accept.txt>
- <entry>  (also in upstream: <vocab>)
- …

## Upstream PR candidates
<path/to/accept.txt>
- <entry>  (suggested upstream vocab: <best-guess vocab>)
- …

## Health
- Local vocabularies: <n> files, <m> entries total
- Upstream vocabularies at <tag>: <n> vocabs, <m> entries total
- Duplicates: <count>
- PR candidates: <count>
- Latest nolte/vale-style release: <tag> (<note whether the pin is behind>)
```

The "Latest release" line comes from `gh api repos/nolte/vale-style/releases/latest --jq .tag_name`. If it differs from the pin, flag it but don't bump automatically.

## Gotchas

- **`vale sync` populates `.vale-styles/` (or whatever `StylesPath` resolves to) at build time.** The audit reads from the actual `accept.txt` files on disk, not from the upstream tag in `.vale.ini`'s `Packages:` block. When the local `vale sync` ran against an old pin, the audit reflects the old pin's vocabulary — re-run `vale sync` before the audit if the local pin matches but the local files look stale.
- **Repository-local vocabularies live under `styles/` / `nolte-styles/` / `config/vocabularies/`** depending on the repo. The audit walks every directory configured in `.vale.ini`'s `StylesPath` plus the `Packages:` cache; assuming a single canonical location misses entries. Read `.vale.ini` first and enumerate every path the audit touches.
- **An entry that's "already accepted upstream" depends on the upstream tag pin, not on the latest upstream release.** The audit compares against the pinned upstream tag's `accept.txt` snapshot — bumping the pin is a separate operator decision, not part of this audit. The "delete locally" recommendation only fires when the entry exists at the *currently pinned* upstream tag.
- **Regex entries in `accept.txt` need careful comparison.** Two entries may match the same string but be different patterns (`pip-?audit` vs. `pip ?audit`); the audit treats them as distinct entries even when their match-set overlaps. Don't recommend deletion just because the upstream regex has wider coverage; the operator decides whether the wider regex makes the local one redundant.
- **The `## Old patterns` section in `accept.txt` is a graveyard, not active scope.** Some vocabularies use a section to keep historical-but-no-longer-active terms; the audit skips that section by convention. Verify the per-vocabulary convention in the repository's curation spec when it exists; otherwise the agent treats every line as active and may flag legitimate retired entries.

## Hard rules

- Never modify files without explicit user confirmation. This skill reports; mutations are a follow-up step the user approves.
- Never bump the `nolte/vale-style` pin unless the user asks for it, even when the audit shows duplicates.
- Never invent upstream entries. If `gh api` fails or the tag doesn't exist, stop and report the error—don't fall back to `main`/`develop`.
- Never skip a local vocabulary file because it "looks like" an upstream copy. Membership in the upstream set is determined by the fetched upstream content, not by filename heuristics.
- Keep the report sections in the fixed order (`Duplicates to remove`, `Upstream PR candidates`, `Health`) so downstream consumers can parse it reliably.
- Don't touch anything outside the prose-style / Vale scope. This skill isn't a general vocabulary linter for other stylers.
