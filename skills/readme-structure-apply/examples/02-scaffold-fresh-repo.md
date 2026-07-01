# Example 02 — `scaffold` a fresh README for a new repo

`README.md` is absent at the repo root, so the skill defaults to the
`scaffold` operation. Exercises the greenfield skeleton: H1 derived
from a marker file, one CI badge per merge-gating workflow, a tagline
stub with `# TODO` markers, and the six required sections in order —
with body prose delegated, not authored here.

## Input prompt

> Create a README for this repo from scratch.

## Input files

No `README.md` at the repo root. `.claude-plugin/plugin.json` declares
`"name": "nolte-example"`. `.github/workflows/ci.yml` gates merges to
`develop` (`branches: [develop]`); `.github/workflows/release.yml`
runs only on tags. `LICENSE` is MIT. A `Taskfile.yml` is present. One
neighbouring portfolio repo (`nolte/example-consumer`) exists.

## Expected behaviour

1. **Operation is `scaffold`** — `README.md` absent.
2. **Skeleton proposed, awaiting per-section approval:**
   - `# nolte-example` H1 — derived from the plugin manifest `name`.
   - CI badge block — one badge for `ci.yml` only (the `develop`
     gate); `release.yml` is tag-triggered, so it gets no badge.
   - Tagline — a one-sentence stub with two `# TODO` markers (the
     deliverable shape and the intended consumer audience); the
     audience marker routes to `audience-identify`.
   - The six sections in order: `## Purpose`, `## Usage` (with a
     `### Local development` sub-section because a `Taskfile.yml`
     ships), `## Structure` (plugin layout is non-obvious),
     `## Related repositories` (peer exists), `## Status`,
     `## License` (`[MIT](LICENSE)` relative link).
3. **No body prose.** Each section gets a placeholder paragraph plus
   `# TODO` markers only; authoring is delegated to `audience-doc-author`.
4. **English-only.** No `README.de.md` is produced; multilingual
   content stays under `docs/<lang>/`.
5. **Follow-ups.** After approval, the skill routes to
   `audience-doc-author` for the bodies and `prose-vale-curator` for
   the Vale check; it commits nothing.
