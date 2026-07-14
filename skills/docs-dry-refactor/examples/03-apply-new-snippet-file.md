# Example 03 — Applying an extraction into a new dedicated snippet file

Exercises the `apply <finding-id>` operation for a finding with **no**
live canonical source: the skill creates a dedicated `_snippets/` fragment,
rewrites the consumers to include it, and gates the whole change on
`mkdocs build --strict`, reverting every write on a red build.

## Input prompt

> Apply finding `d2`.

## Input files

Finding `d2`, approved in this session via `propose`: a six-line
release-checklist paragraph duplicated across two `docs/en/` pages with no
matching source anywhere outside `docs/`, so the proposal named a new
dedicated snippet `docs/en/_snippets/release-checklist.md`.

## Expected behaviour

1. **Approved-in-session precondition.** `apply` runs only because `d2`
   was `propose`d and approved this session; an unproposed id is refused.
2. **Snippet file created as a fragment.** The skill writes
   `docs/en/_snippets/release-checklist.md` under a `_`-prefixed folder
   with the six-line body framed by `docs-include-start`/`-end` markers
   and **no** per-page frontmatter (Hard rule 11) so MkDocs never renders
   it in the nav.
3. **Consumers rewritten, frontmatter preserved.** Each consumer page's
   duplicated block is replaced with the `{% include-markdown … %}`
   directive; the pages' `title`/`audience`/`last_updated` frontmatter and
   surrounding paragraphs are left untouched (Hard rule 2).
4. **Multilingual symmetry.** A translatable-prose snippet exists once per
   configured language under `docs/<lang>/_snippets/`; the include
   directives are applied to every language counterpart (Hard rule 13).
5. **Build gates the write.** `mkdocs build --strict` runs after the
   rewrite. On a non-zero exit the skill reverts every write for `d2` and
   surfaces the raw stderr; the finding stays approved-but-unapplied so
   the user can retry after fixing the cause (Hard rule 3).
6. **No lifecycle side effects.** The skill produces working-tree edits
   only — it never commits, pushes, tags, or opens a PR (Hard rule 9),
   and hands those follow-ups to `pull-request-create`.
