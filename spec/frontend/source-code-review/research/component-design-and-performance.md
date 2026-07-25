# Research — Component design, rendering cost, and styling discipline

Research date: 2026-07-25. Feeds dimensions **F3** (component design and API), **F6** (frontend
performance in code) and **F7** (styling and design-system conformance).

## R-C1 — Effects used for derived state, event logic, or effect chains

**Confidence: verified.** Primary source with verbatim rules and code pairs.

React documentation, verbatim:

- "When something can be calculated from the existing props or state, don't put it in state.
  Instead, calculate it during rendering."
- "Code that runs because a component was *displayed* should be in Effects, the rest should be
  in events."
- "If you can calculate something during render, you don't need an Effect."
- On resetting state when a prop changes, the documented alternative is a `key` rather than an
  effect: "you're asking React to treat two `Profile` components with different `userId` as two
  different components that should not share any state."
- On effect chains: "The component (and its children) have to re-render between each `set` call
  in the chain."

Sources:

- React documentation, *You Might Not Need an Effect* —
  <https://react.dev/learn/you-might-not-need-an-effect>
- ESLint plugin operationalising the same rules (independent implementation of the guidance) —
  <https://github.com/nickjvandyke/eslint-plugin-react-you-might-not-need-an-effect>

**Consequence:** F5 lists these four classes by name. Note the tooling-first interaction: where
the project runs the corresponding lint rules, the mechanical instances belong to the linter and
the review reports only what the linter cannot decide.

## R-C2 — Component API smells

**Confidence: partial.** Consistent across checklists; no normative source.

Recurring items: keep components small (checklists name 200–300 lines as the point at which to
extract a child); keep props small and single-purpose instead of threading large objects through
several layers; make reusable components genuinely generic rather than accidentally coupled;
isolate UI state from business state.

- Feature-Sliced Design checklist — <https://feature-sliced.design/blog/code-review-best-practices>
- Pagepro, *18 tips for a better React code review* —
  <https://pagepro.co/blog/18-tips-for-a-better-react-code-review-ts-js/>

**Consequence:** F3 carries the classes but the spec must forbid line-count-only findings — a
size finding needs a named responsibility that should be extracted.

## R-C3 — Memoization judgment depends on the build configuration

**Confidence: partial for the ecosystem claim, verified for the conditional formulation.**

The React documentation describes the compiler as automatically optimising an application "by
handling memoization for you, eliminating the need for manual `useMemo`, `useCallback`, and
`React.memo`", and ships a separate incremental-adoption guide rather than a blanket instruction
to strip existing memoization. Practitioner sources additionally report edge cases where the
compiler bails out (code inside `try`/`catch`; third-party libraries that depend on referential
equality and need an opt-out directive).

- React documentation, *React Compiler* — <https://react.dev/learn/react-compiler>
- React documentation, *React Compiler — incremental adoption* —
  <https://react.dev/learn/react-compiler/incremental-adoption>

**Consequence — this is the load-bearing methodological point:** a spec rule of the form "always
memoize" or "never memoize" would be wrong in one of the two worlds and would age badly. The
spec therefore makes the memoization rule **conditional on what the reviewed repository's own
build configuration enables**, which the reviewer reads directly from the repo. No volatile
upstream pin enters the spec, so the assertion is repo-internal and needs no triangulation
(`spec/claude/research-triangulate/` §When triangulation is required).

## R-C4 — Premature memoization is a cost, not a win

**Confidence: partial.**

Memoization has a bookkeeping cost and hides referential-identity bugs behind stale caches; a
memoization finding without a named, plausible cost (a large list, an expensive derivation, a
dependency that must stay referentially stable) is a preference, not a defect.

- React documentation, *useMemo* — "you should only rely on `useMemo` as a performance
  optimization" — <https://react.dev/reference/react/useMemo>
- React documentation, *React Compiler* (see R-C3).

**Consequence:** F6 forbids blanket memoization findings in both directions.

## R-C5 — Frontend performance classes visible in the source

**Confidence: partial.**

Code-level (as opposed to measured) performance classes named consistently: request waterfalls
and per-item fetch fan-out; rendering large collections without virtualisation; missing
route-level code splitting; whole-library or barrel imports that defeat tree shaking; expensive
derivation recomputed on every keystroke.

- Feature-Sliced Design checklist (code splitting, unnecessary re-renders) — see R-C2
- web.dev, *Reduce JavaScript payloads with code splitting* —
  <https://web.dev/articles/reduce-javascript-payloads-with-code-splitting>

**Consequence:** F6 stays code-level. Measured budgets (Core Web Vitals thresholds, bundle-size
budgets) belong to `spec/frontend/webview-ui-optimization/` and are a route-out, not a finding
here.

## R-C6 — Design-system drift is a code-review-visible defect

**Confidence: verified.**

Documented failure mode: in a codebase with many contributors, one-off visual values drift, so
the same colour ends up written three slightly different ways; buttons acquire slightly
different padding and headlines inconsistent sizes. The documented audit approach is to scan for
hardcoded visual values — hex and `rgb()` colours, pixel spacing, raw font sizes and weights,
border radii, `z-index` values, shadows, transition durations — and the documented remediation
is a shared token referenced by every consumer, backed by lint rules that prevent hardcoded
values.

- Penpot, *The developer's guide to design tokens and CSS variables* —
  <https://penpot.app/blog/the-developers-guide-to-design-tokens-and-css-variables/>
- W3C Design Tokens Community Group, format specification (tokens as the shared source of
  truth) — <https://tr.designtokens.org/format/>

**Consequence — and the sharpest UX boundary in the spec:** whether the chosen colour is the
*right* colour is a design question; whether the value bypasses the token layer the project
already ships is a code question. F7 owns only the second.

## Currency addendum

None yet.
