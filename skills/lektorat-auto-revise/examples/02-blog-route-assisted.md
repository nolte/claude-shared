# Example 02 — Assisted blog route preserving the blog-author touchpoint

Exercises the blog-post route: a file carrying the consumer's
cross-language binding key routes to the `blog-author` **skill** and runs
**assisted** — the skill surfaces the findings-derived briefing but never
fabricates the interactive intake inputs `blog-author` owns.

## Input prompt

> Remediate the lektorat findings with the right author.

## Input files

A `findings.json` whose one affected file is
`~/repos/github/blog/src/posts/lektorat-scanner-agent.md`, whose
frontmatter carries `translationKey: lektorat-scanner-agent`. It has two
`warning` findings (D3 grammar, D6 idiomatic naturalness).

## Expected behaviour

1. **Routed by frontmatter, not prose.** The `translationKey` in
   frontmatter classifies the file as `blog-post`, regardless of where it
   lives — so it routes to the `blog-author` skill, not the autonomous
   `audience-doc-author` agent. Misrouting it would skip `blog-author`'s
   load-bearing briefing touchpoint.
2. **Assisted, not autonomous.** The skill composes the findings-derived
   briefing and hands it to `blog-author`, letting that skill's briefing
   touchpoint stand — the operator confirms topic-as-thesis, source list,
   and slug there. The skill never fabricates those inputs (Hard rule).
3. **No prose rewritten here.** The rewrite is entirely `blog-author`'s;
   this skill only routes, briefs, and gates.
4. **Convergence gate.** After the assisted pass the skill re-runs the
   `lektorat` audit with the same config and marks the post converged only
   when no finding at or above the severity floor remains and the post
   count did not rise (no regression).
5. **Bounded loop.** On non-convergence it re-dispatches up to **2**
   author passes, then escalates the residual to the operator rather than
   looping further.
6. **Run trail written** under
   `.audits/lektorat-auto-revise/<YYYY-MM-DD-HHMM>/`, with the blog file's
   diff and pass count recorded.
