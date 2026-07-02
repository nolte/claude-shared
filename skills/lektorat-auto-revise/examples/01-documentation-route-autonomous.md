# Example 01 — Autonomous documentation route with a D1 readability finding

Exercises the documentation route: a `docs/<lang>/` page routes to the
`audience-doc-author` agent **fully autonomously** (no per-finding gate),
with a D1 readability finding that carries the LIX corridor and dominant
lever into the briefing, then converges on a machine re-audit.

## Input prompt

> Auto-revise the findings in
> `.audits/lektorat/2026-06-30-1400/findings.json`.

## Input files

A `findings.json` (verbatim `spec/project/lektorat/` §Outputs shape) with
one affected file, `docs/en/guides/setup.md`, carrying a `warning` D1
readability finding (LIX above the page's `crit` corridor) and a `warning`
D5 audience-fit finding. The repo has an `AUDIENCES.md` and the
`prose-style` baseline.

## Expected behaviour

1. **Report consumed verbatim.** The skill loads the `findings` array and
   never re-classifies, re-weights, or renames a field.
2. **Grouped and routed once.** Findings are grouped by `file`;
   `setup.md` lives under `docs/en/` with no cross-language binding key,
   so it routes to `documentation` → the `audience-doc-author` agent.
3. **Briefing composed with LIX inputs.** The per-file briefing binds the
   findings verbatim, the resolved audience set (via the `lektorat`
   priority chain), the bound writing-style spec, and — because of the D1
   finding — the current `lix`, the resolved `aim`/`warn`/`crit` corridor
   for the page's `content_mode` and language, and the dominant lever
   (`ASL` or `LWP`) per `readability-lix` §Iterative improvement loop.
4. **Dispatched fully autonomously.** The agent revises with no
   per-finding approval and no diff gate; the skill never rewrites the
   prose itself (Hard rule).
5. **Convergence gate.** After the pass the skill re-runs the `lektorat`
   audit with the same config. The file converges only when no finding at
   or above the severity floor remains, the post count ≤ the pre count,
   **and** the re-audit shows LIX at or below the page's `warn` corridor.
   A LIX drop earned by decompounding or a vaguer-shorter swap is a
   semantic-preservation failure, not convergence.
6. **Run trail written.** Outputs land under
   `.audits/lektorat-auto-revise/2026-06-30-1400/`: `routing.json`,
   `run.json`, the per-file diff with pre/post counts, and `summary.md`.
