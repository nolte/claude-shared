# Example 01 — `audit` an existing README against the spec

A read-only conformance check against
`spec/project/readme-structure/`. `README.md` is present, so the
default apply operation would be `patch`, but the operator asks for a
read-only report first. Exercises the per-spec-area findings table,
the consumer-first ordering check, and the ≤200-line budget.

## Input prompt

> Audit our README against the spec — report only, no edits.

## Input files

`README.md` exists (312 lines). It opens with `# example-service` and
one CI badge, then a marketing-heavy three-sentence tagline. Section
order is `## Purpose`, `## Structure`, `## Usage`, `## Status`,
`## License`. `LICENSE` (MIT) ships at the repo root and is linked via
an absolute `https://github.com/...` URL. `.github/workflows/ci.yml`
gates merges to `develop`.

## Expected behaviour

1. **Preconditions pass.** cwd is a git repo; spec read from the target
   repo. Operation is `audit` — read-only.
2. **Findings grouped by spec area.** Notable rows:
   - **Header block** → `drift`: tagline uses marketing language and
     names no consumer audience.
   - **Consumer-first ordering** → `drift`: `## Structure` (a
     contributor section) precedes `## Usage` (a consumer section).
   - **Links and badges** → `drift`: `LICENSE` linked by absolute URL
     instead of a relative path.
   - **Length and density** → `drift`: 312 lines exceeds the ~200-line
     budget and trips the >250-line hard fail.
3. **Vale not run here.** The File-and-language row notes the Vale check
   is delegated to `prose-vale-curator`; the audit surfaces the intent,
   not the alert list.
4. **No autofix.** Every finding carries a one-line evidence snippet;
   the operator is routed to re-run in `patch` mode to apply fixes per
   approval. Nothing is written.
