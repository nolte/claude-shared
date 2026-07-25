# Research — Error handling and asynchronous state in the client

Research date: 2026-07-25. Feeds dimensions **F2** (error and state handling) and **F5**
(rendering, effects, and reactivity correctness).

## R-E1 — `fetch()` does not reject on an HTTP error status

**Confidence: verified.**

MDN, verbatim: "A `fetch()` promise only rejects when the request fails, for example, because of
a badly-formed request URL or a network error. A `fetch()` promise *does not* reject if the
server responds with HTTP status codes that indicate errors (`404`, `504`, etc.). Instead, a
`then()` handler must check the `Response.ok` and/or `Response.status` properties."

- MDN, *Window: fetch() method* — <https://developer.mozilla.org/en-US/docs/Web/API/Window/fetch>
- WHATWG Fetch Standard (the promise settles with a Response for any completed exchange) —
  <https://fetch.spec.whatwg.org/>

**Consequence:** "calls `fetch` and never inspects `response.ok` or `status`" is a concrete,
mechanically checkable F2 finding — a `404` silently becomes a success path.

## R-E2 — `AbortController` is the documented cancellation mechanism

**Confidence: verified.**

`fetch()` accepts a `signal`; aborting rejects with an `AbortError` `DOMException`.

- MDN, *Window: fetch() method*, Exceptions section (see R-E1)
- MDN, *AbortController* — <https://developer.mozilla.org/en-US/docs/Web/API/AbortController>

**Consequence:** F2 and F5 can require a cancellation or staleness guard on in-flight requests
whose component may unmount or whose inputs may change, and name the mechanism.

## R-E3 — Error boundaries catch render-tree errors only

**Confidence: verified.**

An unhandled error during rendering unmounts the whole tree unless a boundary catches it; a
boundary displays a fallback for its subtree and lets the rest of the application keep working.
The documented limitation is that boundaries do **not** catch errors in event handlers, in most
asynchronous callbacks, during server-side rendering, or errors thrown by the boundary itself.

- React documentation, *Component: componentDidCatch / error boundaries* —
  <https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary>
- Legacy React documentation, *Error Boundaries* (explicit "do not catch" list) —
  <https://legacy.reactjs.org/docs/error-boundaries.html>

**Consequence:** two distinct F2 findings. First: a subtree with no boundary at all, so one
render error blanks the application. Second: an async or event-handler failure path that relies
on a boundary that structurally cannot catch it.

## R-E4 — Granular boundary placement, composed with the loading fallback

**Confidence: partial.** Consistent practitioner guidance, no single normative source.

The recommended composition is one boundary per meaningful widget or route rather than one at
the application root, wrapping the loading fallback, so that the three outcomes (content,
pending, failed) each have an owner, with a reset or retry affordance on the failure path.

- OneUptime, *How to implement React error boundaries for resilient UIs* —
  <https://oneuptime.com/blog/post/2026-02-20-react-error-boundaries/view>
- React documentation, *Suspense* (fallback composition) —
  <https://react.dev/reference/react/Suspense>

**Consequence:** F2 requires the *three-state contract* (pending, failed with recovery, empty,
each distinguishable from success) rather than prescribing a specific library.

## R-E5 — Boolean state pairs permit impossible states; a discriminated union does not

**Confidence: partial.** Widely documented modelling guidance; TypeScript's discriminated union
is the normative language feature.

`isLoading` plus `data` plus `error` as three independent fields admits combinations that cannot
occur (loading *and* errored, done *and* neither data nor error), and those combinations are
exactly where a UI gets stuck on a spinner.

- TypeScript Handbook, *Discriminated unions* —
  <https://www.typescriptlang.org/docs/handbook/2/narrowing.html#discriminated-unions>
- React documentation, *Choosing the state structure* — "avoid contradictions in state" —
  <https://react.dev/learn/choosing-the-state-structure>

**Consequence:** F2 can recommend a state model rather than a coat of extra guards.

## R-E6 — Uncancelled async work in effects produces stale-response races

**Confidence: verified.**

React documentation, verbatim on the fix: "This ensures that when your Effect fetches data, all
responses except the last requested one will be ignored." The documented pattern is an `ignore`
flag (or an abort) set in the effect's cleanup function.

- React documentation, *You Might Not Need an Effect* — <https://react.dev/learn/you-might-not-need-an-effect>
- React documentation, *Synchronizing with Effects* (cleanup contract) —
  <https://react.dev/learn/synchronizing-with-effects>

**Consequence:** F5 covers the missing-cleanup class generally (listeners, timers,
subscriptions, observers, object URLs) and the stale-response race specifically.

## R-E7 — Errors that reach nobody

**Confidence: partial.**

A caught error that is neither surfaced to the user, propagated, nor reported to an error sink
is invisible in a browser: there is no crash, no non-zero exit code, no failing health check —
only a control that silently does nothing. This is the frontend instance of the core spec's
swallowed-error no-go (`spec/project/source-code-review/` §Core review dimensions, D1, and its
severity floor).

**Consequence:** F2 inherits the core Critical/Warning severity floor verbatim rather than
inventing a second scale, and adds "not reported to the observability sink" as a route-out to
the observability audit instead of a deep finding.

## Currency addendum

None yet.
