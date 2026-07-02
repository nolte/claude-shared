# Example 02 — Proposing an extraction against a live canonical source

Exercises the `propose <finding-id>` operation: the skill surfaces the
full snippet, the canonical-source markers, and the per-consumer include
directives for one finding, then stops at an explicit approval gate. It
writes nothing.

## Input prompt

> Propose the extraction for finding `d1`.

## Input files

Finding `d1` from the Example 01 audit: the four-line install paragraph on
three `docs/en/` pages, with `CONTRIBUTING.md` proposed as the live
canonical source.

## Expected behaviour

1. **Snippet surfaced verbatim.** The full four-line block is shown with
   its line count so the user can confirm what will be shared.
2. **Canonical source + markers named.** The skill shows the
   `CONTRIBUTING.md`-relative marker lines it will insert in Markdown/HTML
   comment syntax (`<!-- docs-include-start: install-cli -->` … `-->`),
   named after the content (kebab-case), never positional (Hard rule 12).
3. **Include directives resolve from `docs_dir`.** For each of the three
   consumer pages, the exact `{% include-markdown "../CONTRIBUTING.md"
   start="…" end="…" %}` directive is shown, with the path computed
   relative to `docs_dir` — not to the consuming page — so the user isn't
   bitten by the wrong path origin.
4. **Expected build delta stated.** The skill names which pages will be
   modified and that `CONTRIBUTING.md` gains marker comments, before any
   write.
5. **Approval gate.** It ends by requiring `approve d1` or `skip d1`;
   nothing is written on a bare "looks good" (Hard rule 1). Batch
   `approve all` is honoured only if the user explicitly asked for it.
