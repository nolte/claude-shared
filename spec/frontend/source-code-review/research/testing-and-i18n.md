# Research — Frontend test code, user-facing text, and locale handling

Research date: 2026-07-25. Feeds dimensions **F10** (user-facing text, i18n, and content in
code) and **F11** (frontend test-code quality).

## R-T1 — The guiding principle and the documented query priority

**Confidence: verified.** Primary source, quoted verbatim.

Testing Library's guiding principle: "your test should resemble how users interact with your
code (component, page, etc.) as much as possible." The documented priority is:

1. Queries accessible to everyone — `getByRole` (top preference), `getByLabelText` (best for
   form fields), `getByPlaceholderText`, `getByText`, `getByDisplayValue`
2. Semantic queries — `getByAltText`, `getByTitle`
3. Test IDs — `getByTestId`, verbatim: "The user cannot see (or hear) these, so this is only
   recommended for cases where you can't match by role or text or it doesn't make sense."

- Testing Library, *About Queries* — <https://testing-library.com/docs/queries/about/>
- Testing Library, *Guiding Principles* — <https://testing-library.com/docs/guiding-principles/>

**Consequence:** F11 can require the priority order and, importantly, note the diagnostic value
of a violation: reaching for a test id because no role or label matches usually means the markup
has an accessibility gap (an F8 finding hiding behind an F11 symptom).

## R-T2 — Implementation details are the documented thing not to test

**Confidence: verified.**

The documented list of implementation details to avoid asserting on: a component's internal
state, internal methods, lifecycle methods, and child components. The stated purpose is that
refactoring — changing the implementation without changing the behaviour — must not break the
test.

- Testing Library, *Guiding Principles* (see R-T1)
- Kent C. Dodds, *Testing Implementation Details* —
  <https://kentcdodds.com/blog/testing-implementation-details>

**Consequence:** F11 inherits the core spec's D6 (behaviour over implementation) and adds the
frontend-specific instances: assertions on props or internal state, deep DOM traversal coupling
a test to markup structure, and snapshot blobs standing in for assertions.

## R-T3 — Frontend test flakiness has recognisable code shapes

**Confidence: partial.**

Named smells: arbitrary timeouts instead of awaiting an assertion; `waitFor` used where a
`findBy*` query is the documented form; fake timers installed and not restored; mocking one's
own modules or components instead of the network boundary; assertions that depend on the
machine's locale or timezone without pinning them.

- Testing Library, *Async Methods* (`findBy*` as the documented await form) —
  <https://testing-library.com/docs/dom-testing-library/api-async/>
- Mock Service Worker, *Philosophy* (intercept at the network boundary instead of stubbing the
  client) — <https://mswjs.io/docs/philosophy>

**Consequence:** F11 lists the classes; single-tier conformance detail routes to the owning tier
reviewer per the core spec's route-out rule.

## R-T4 — Error and empty paths are the states tests skip

**Confidence: partial (inference from R-E4 plus checklist sources).**

If the spec requires a three-state contract (pending, failed with recovery, empty), the test
dimension must require that the failure and empty branches are actually exercised; otherwise the
contract is declared and never verified.

**Consequence:** F11 pairs with F2 explicitly — an F2 finding about a missing error path and an
F11 finding about an untested error path are one work package, not two.

## R-I1 — Hardcoded user-facing strings and concatenated sentences

**Confidence: verified.**

Checklists state the rule plainly: all user-facing text is pulled from the internationalisation
layer, with no hardcoded strings in templates. The concatenation problem is documented normatively:
sentences assembled from fragments cannot be reordered or inflected by a translator, which is why
the message-format approach uses a single pattern string with placeholders and explicit plural
and gender selectors.

- Unicode CLDR / ICU, *MessageFormat* (plural and select categories) —
  <https://unicode-org.github.io/icu/userguide/format_parse/messages/>
- Front-End Checklist (i18n section) — <https://github.com/thedaviddias/Front-End-Checklist>

**Consequence:** F10 covers hardcoded strings, concatenated sentences, and missing plural
handling; translation-key *coverage* routes to `spec/project/i18n-completeness/`.

## R-I2 — Locale-sensitive formatting and comparison belong to the platform API

**Confidence: verified.**

Dates, times, numbers, currencies, lists, relative times, and string collation are locale-
sensitive; the platform provides `Intl.*` for each, and hand-rolled formatting or a raw
`localeCompare`-free sort produces wrong output outside the developer's own locale.

- MDN, *Intl* — <https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl>
- ECMA-402, *ECMAScript Internationalization API Specification* —
  <https://tc39.es/ecma402/>

**Consequence:** F10 covers manual formatting where a locale API exists, plus the commonly missed
surfaces — `aria-label`, `alt`, `title`, and the document title — which are user-facing text that
escapes a naive "strings in JSX" scan.

## Currency addendum

None yet.
