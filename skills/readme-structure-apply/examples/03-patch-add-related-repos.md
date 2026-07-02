# Example 03 — `patch` a missing section and fix section order

`README.md` is present and a prior audit surfaced two findings: a
missing `## Related repositories` section and a consumer-first
ordering violation. Exercises the additive `patch` operation —
one finding per approval, existing prose preserved verbatim — plus
the mandatory post-write Vale delegation.

## Input prompt

> Add the Related repositories section and fix the section order the
> audit flagged.

## Input files

`README.md` (168 lines) has `## Purpose`, `## Structure`, `## Usage`,
`## Status`, `## License` — note `## Structure` sits above `## Usage`.
No `## Related repositories` section, though `nolte/example-consumer`
and `nolte/example-shared` are sibling portfolio repos. All prose is
otherwise well-formed and within budget.

## Expected behaviour

1. **Operation is `patch`** — `README.md` present; only the two flagged
   findings are in scope. Every untouched section's prose is carried
   over verbatim (a truncating patch is a data-loss bug).
2. **First approval — missing section.** The skill proposes a
   `## Related repositories` block with a two-item bullet list, each
   peer linked by absolute `https://github.com/nolte/<repo>` URL plus a
   `# TODO` marker for the one-line description; it waits for approval.
3. **Second approval — ordering fix.** As a separate edit, it proposes
   moving `## Usage` above `## Structure` so consumer sections precede
   contributor sections, showing the before / after section sequence
   inline. Unrelated changes are never bundled into one approval.
4. **Post-write Vale delegation.** After the approved writes, the skill
   dispatches `prose-vale-curator` for the Vale check and reports the
   count — it never claims "Vale-clean" itself.
5. **Caller follow-ups.** The `# TODO` description markers route to
   `audience-doc-author`; committing and the PR stay with
   `pull-request-create`.
