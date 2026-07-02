# Example 02 — Migrating a brownfield docs tree onto the audience-tracks layer

Exercises the `migrate` operation: most pages predate the tracks contract
and lack `track:` frontmatter, so the skill proposes the layer page by
page under explicit per-file approval, keeping every language tree
symmetric and verifying each write with `mkdocs build --strict`.

## Input prompt

> Wire up the audience tracks on our docs — most pages don't have them yet.

## Input files

`docs/en/` and `docs/de/` where >50 % of pages lack `track:`. `AUDIENCES.md`
maps `user` and `contributor`. `mkdocs.yml` declares `en`/`de`. The tree
is clean (no uncommitted changes under `docs/`).

## Expected behaviour

1. **Operation resolves to `migrate`.** Coverage below 50 % makes
   `migrate` the default, subject to user confirmation.
2. **Per-page proposal, per-file approval.** For each page the skill
   proposes a `track:` value defaulted from the path plus existing
   `audience` frontmatter via the portfolio-baseline mapping; where
   neither is deterministic it proposes `track: # TODO: confirm` and asks
   inline. Nothing is written without approval.
3. **MUST content blocks scaffolded as containers only.** For a served
   track missing a MUST block, the skill scaffolds a placeholder page
   (frontmatter, H1, one stub paragraph naming the block's purpose) — it
   never authors the prose body (Hard rule 1); that is `audience-doc-author`'s job.
4. **Audience artefact patched, not rewritten.** It adds a `track:` field
   next to each audience entry inline; a structural rewrite is routed to
   `audience-identify` instead.
5. **Multilingual symmetry enforced.** Every `track:` patch and every
   placeholder block is applied to both `docs/en/` and `docs/de/`
   counterparts — patching one language only is a Hard rule 8 violation.
6. **Build verified after each write.** `mkdocs build --strict` runs green
   after every change; a red build stops the operation and surfaces the
   raw output verbatim rather than claiming success.
