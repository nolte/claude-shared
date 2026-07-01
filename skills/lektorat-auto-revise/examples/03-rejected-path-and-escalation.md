# Example 03 — Rejected-class path plus a non-converging escalation

Exercises the two failure edges: a finding at a path `lektorat` excludes
is hard-rejected with no author dispatch, and a documentation file that
still has findings after two passes is escalated to the operator rather
than looped further — both surfaced first in `summary.md`.

## Input prompt

> Arbeite das Lektorat-Audit automatisch ab.

## Input files

A `findings.json` with two affected files:

- `spec/project/mermaid-diagrams/en.md` — a path under `spec/`, which
  `lektorat` §Scope and applicability excludes.
- `docs/de/tutorials/onboarding.md` — a documentation page with a stubborn
  `warning` D2 comprehensibility finding whose root cause the author can't
  fully resolve in two passes.

## Expected behaviour

1. **Rejected path hard-rejected.** `spec/project/mermaid-diagrams/en.md`
   is classified `rejected`; the skill emits a one-sentence message naming
   the owning flow (`spec` authoring, out of `lektorat` scope) and
   dispatches **no** author for it. It never widens the routing table to a
   class `lektorat` forbids.
2. **Documentation file routed and revised.** `onboarding.md` routes to
   `audience-doc-author`, gets a first autonomous pass, and is re-audited.
3. **Non-convergence bounded at 2 passes.** The D2 finding survives pass
   one, so the skill re-dispatches with the residual finding for pass two.
   Still unresolved, it **escalates** to the operator — it never runs a
   third pass (Hard rule).
4. **Regression never auto-accepted.** Had the re-audit shown a higher
   post-count than pre-count, the skill would flag the regression and
   refuse to mark the file converged.
5. **Unremediated work surfaced first.** `summary.md` lists the escalated
   `onboarding.md` and the rejected `spec/` path **before** any converged
   file, so nothing unremediated is overlooked.
6. **Localised prose.** The operator wrote in German, so the skill's
   conversational summary is German while the machine-readable
   `routing.json`/`run.json` keys stay English.
