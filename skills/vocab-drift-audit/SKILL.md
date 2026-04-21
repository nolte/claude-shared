---
name: vocab-drift-audit
description: Audit repository-local Vale vocabularies against the pinned upstream release of nolte/vale-style to detect drift. Invoke when the user says things like "audit the Vale vocabulary", "check for vocabulary drift", "vocab drift audit", "diff the local vocab against nolte/vale-style", "are there local Vale terms that can be retired?", "Vokabular-Drift prüfen", "Vale-Wortschatz-Audit", or "welche lokalen Vale-Einträge sind jetzt upstream?". Reports local entries that are already accepted upstream (should be deleted) and local entries that are not yet upstream (should be PR'd to nolte/vale-style).
---

# Vocab Drift Audit

Operationalises the MUST rule in `spec/project/prose-style/<canonical_language>.md`: "once the upstream change is released, the local entry MUST be removed and the pinned `nolte/vale-style` release MUST be bumped". Apply the prose-style spec's rules when it is present in the current project; otherwise, fall back to the conventions described here.

## User-language policy

Detect the user's language from their message and respond in it. The audit report itself uses English section headings (matching the upstream repo), but prose around the report is localised.

## Inputs

- **Repo root** — default: current working directory. The repo must contain a `.vale.ini` (at root or under a documentation root) that pins a `nolte/vale-style` release.
- **Upstream pin** — parsed automatically from `.vale.ini`. Look at the `Packages =` line for a URL of the form `https://github.com/nolte/vale-style/releases/download/<tag>/nolte-styles.zip`; the `<tag>` is the pin. If the URL is missing or the tag is non-semver, stop and report instead of guessing.
- **Local vocabularies** — every git-tracked `accept.txt` under the repo's Vale `StylesPath` (and under any folder named `vocabularies/` inside the repo). `vale sync`'d files are conventionally gitignored, so git-tracked entries are treated as local overrides.

## Operation

1. **Locate the Vale config.** Read `.vale.ini` from the repo root first, then from common alternative locations (`docs/.vale.ini`, `.github/.vale.ini`). Extract `StylesPath` and the `nolte/vale-style` pin tag. If either is missing, stop with a clear message.
2. **Collect the upstream vocabulary for that pin.** List the upstream vocabulary directory at the pinned tag via `gh api "repos/nolte/vale-style/contents/src/styles/config/vocabularies?ref=<tag>"` and, for each subdirectory, fetch `accept.txt` at the same ref. Build one set per upstream vocabulary (for example `technical`, `esphome`, `technical-de`).
3. **Collect the repo-local vocabularies.** Use `git ls-files` filtered to `*/accept.txt` under `StylesPath` and any `vocabularies/` folder inside the repo. Normalise entries (strip comments starting with `#`, trim whitespace, drop empty lines). Case-sensitivity follows Vale: treat entries as case-insensitive for matching but preserve casing in the report.
4. **Diff.** For each local vocabulary, compute:
   - **Duplicates** — local entries whose normalised form already appears in any upstream vocabulary at the pinned tag. These MUST be removed per the prose-style spec.
   - **Upstream PR candidates** — local entries that do not appear in any upstream vocabulary. These are the reason the local override still exists; each one needs a PR against `nolte/vale-style`.
   - **Unused** — upstream entries that are also present locally are not flagged as unused; this audit does not touch upstream-only noise.
5. **Render the report** as Markdown with three sections in this order: `## Duplicates to remove`, `## Upstream PR candidates`, `## Health`. Group findings under each section by local vocabulary file, and show the file path relative to the repo root.
6. **Offer follow-up actions** in the response (do not execute them without explicit confirmation):
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

The "Latest release" line comes from `gh api repos/nolte/vale-style/releases/latest --jq .tag_name`. If it differs from the pin, flag it but do not bump automatically.

## Hard rules

- Never modify files without explicit user confirmation. This skill reports; mutations are a follow-up step the user approves.
- Never bump the `nolte/vale-style` pin unless the user asks for it, even when the audit shows duplicates.
- Never invent upstream entries. If `gh api` fails or the tag does not exist, stop and report the error — do not fall back to `main`/`develop`.
- Never skip a local vocabulary file because it "looks like" an upstream copy. Membership in the upstream set is determined by the fetched upstream content, not by filename heuristics.
- Keep the report sections in the fixed order (`Duplicates to remove`, `Upstream PR candidates`, `Health`) so downstream consumers can parse it reliably.
- Do not touch anything outside the prose-style / Vale scope. This skill is not a general vocabulary linter for other stylers.
