# Frontend Source Code Review

Status: draft

## Context

`spec/project/source-code-review/` defines the holistic senior-engineer review: a language-agnostic core of ten dimensions (D1–D10), a tooling-first rule, one language profile per programming language, and a report contract whose disjoint work packages route to specialists. Its own Open Questions already name the frontend as the likeliest second profile.

Frontend code breaks that model in one place. The core spec's profile axis is the **language**, but what makes a browser-hosted component hard to review isn't TypeScript—it's the surface. A component owns a DOM tree that must stay operable by keyboard and assistive technology, a render loop whose cost the user feels directly, a trust boundary that sits *outside* the process it runs in, every string the user reads, and design decisions encoded as style values. A review that applies only D1–D10 to a component file passes over all of it: the swallowed `catch` that leaves a spinner turning forever, the discount rule computed in the client and never re-checked by the server, the `div` with a click handler that no keyboard reaches, the hex colour that bypasses the design tokens the project already ships.

This spec is the **frontend extension** of the core review. It adds a dimension overlay (F1–F11) on top of D1–D10, defines a framework-profile contract alongside the core's language profiles, narrows the review unit from the file to the **component slice**, and draws a hard line to the UX review: this review judges code, never taste. It's the foundation of a review process that produces specialist-ready findings with implementation proposals, exactly as the Python review does for server-side code.

Readers: authors of the frontend reviewer agent and the dispatching skill; reviewers who consume the report; frontend developers who run the review before a release or after a feature lands.

## Goals

- Extend the core review rather than fork it: every core rule (tooling-first, severity vocabulary, per-finding attribution, disjoint work packages, read-only reviewer) applies verbatim, and this spec adds only what the surface demands
- Make **business logic in the client** a precisely defined dimension that separates "right client, wrong layer" from "must not run in the client at all"
- Make **frontend error handling** a first-class dimension with the core's severity floor, because a swallowed error in a browser produces no crash, no exit code, and no failing health check—only a control that silently does nothing
- Define the review unit as the **component slice**, so a component is never reviewed without its hooks, its styles, and its tests
- Draw an explicit, operational boundary to the pure UX review, in both directions
- Define a framework-profile contract with React and TypeScript as the reference profile, so further frameworks extend the spec without touching the overlay
- Produce findings whose remediation is an **implementation proposal** a specialist can act on, routed and cut along slice boundaries so remediation runs in parallel

## Non-Goals

- The core review dimensions themselves (D1–D10), the tooling-first rule, the severity vocabulary, and the work-package contract—owned by `spec/project/source-code-review/`, applied here unchanged
- UX, usability, visual-design, and content-quality judgment—see §Delimitation from the UX review; owned by `spec/frontend/webview-ui-optimization/` §"UX and native feel" and its `webview-ui-optimize` skill / `frontend-usability-optimizer` agent
- Deep WCAG conformance auditing, contrast measurement, target-size evaluation, and assistive-technology testing—owned by `spec/frontend/webview-ui-optimization/` §Accessibility; this review flags the code-level defect and routes the conformance question
- Measured runtime performance: Core Web Vitals thresholds, bundle-size budgets, profiling—owned by `spec/frontend/webview-ui-optimization/` §"Performance and rendering"; this review sees only what the source shows
- Deep client security auditing, Content Security Policy, and HTTP security headers—owned by `spec/project/code-security-audit/` and `spec/frontend/webview-ui-optimization/` §"Security and sandboxing"; frontend security findings here are flagged floors that route out
- Translation-key coverage and locale completeness—owned by `spec/project/i18n-completeness/`
- The test-identifier contract itself—owned by `spec/frontend/testability-identifiers/`
- Single-tier test conformance (component, integration, E2E checklists)—owned by the `spec/project/test-tier-*/` specs and their reviewers
- Running mechanical tooling (`spec/project/quality-gate/`) and applying fixes: the review finds, classifies, proposes, and routes; specialists remediate

## Requirements

### Relationship to the core review

- **MUST** be applied only together with `spec/project/source-code-review/`: a frontend review is the core review **plus** this overlay, never a second competing review that restates core rules in frontend words
- **MUST NOT** duplicate a core rule; where a frontend rule sharpens a core dimension, it names the core dimension it extends (F4 extends D4, F6 extends D7, F11 extends D6, F9 extends D10)
- **MUST** tag every finding with exactly **one** dimension ID, either a core `D` ID or a frontend `F` ID; when both fit, the **F** ID wins because it's the more specific one, and the finding names the core dimension it extends
- **MUST** inherit the core §Report contract unchanged: the severity vocabulary from `spec/claude/review-plan/` §Severity scale (Critical / Warning / Suggestion / Info, verbatim Title Case), per-finding `file:line`, the `production` or `test` marker, the confirmed-or-suspected flag, and the §Work packages section with disjoint file sets and routing targets
- **MUST** inherit the core §Reviewer contract unchanged: the reviewer is strictly read-only, applies no fixes, and inserts no suppression comments
- **MUST** inherit the core tooling-first rule: a finding the project's configured linter, formatter, style linter, accessibility linter, or type checker already reports isn't a review finding, and a missing baseline is exactly **one** adoption finding rather than hand-reported mechanical violations

### Review unit: The component slice

- **MUST** treat the **component slice** as the unit of review: the component file or files, the hooks or composables it owns, its co-located styles, its tests and fixtures or stories, and the translation keys it references. A component reviewed without its tests is an incomplete review, not a partial one
- **MUST** discover the frontend surface from the repository itself—package manifest, framework and bundler configuration, router setup, style pipeline, translation layer, data-access layer—rather than assuming a layout
- **MUST** record, in the report header, the four baselines the overlay judges against: the detected **framework profile**, the **design-token or theme source**, the **internationalisation layer**, and the **data-access layer**. A finding under F1, F7, or F10 judged without its baseline recorded isn't reproducible
- **MUST** keep the core's equal-weight rule: test code carries the `test` marker and the same rigour as production code
- **SHOULD**, when a narrower target is given, state which slices were reviewed and which were deliberately left out

### F1—Layering and business logic in the client

The dimension distinguishes three classes, and a finding **MUST** name which one it belongs to, because the remediation differs in each case.

- **Class 1—misplaced logic inside a component.** A domain rule, calculation, state-machine transition, mapping, or orchestration embedded in the render body or the markup rather than in a hook, a service, or a framework-free domain module. The remediation is an extraction that names the target layer.
- **Class 2—authoritative rules implemented client-side.** A decision the server must not trust the client for: pricing, discounts, tax, entitlement and permission checks, quotas, eligibility, or any rule whose outcome the backend consumes. The severity depends on the enforcement question: where the server independently enforces the same rule, the client copy is legitimate for responsiveness and the finding is a **duplication and drift** finding under F4; where the client's result is the only enforcement, or the server accepts it without recomputing, the finding is at least **Warning** and **Critical** when confirmed, and routes to `spec/project/code-security-audit/` under F9.
- **Class 3—backend-shaped work in the client.** Joining or aggregating data from several endpoints in the client, pulling a full dataset to sort, filter, or paginate it locally, or per-item request fan-out that a single endpoint should serve. The remediation names the endpoint or layer change.

Further F1 rules:

- **MUST** report direct network calls issued from inside a component (or from markup-bound handlers) when the project has a data-access layer, and name that layer as the target
- **MUST** report transport shapes leaking through the UI—raw API payloads threaded unmapped into components—when the project declares an anti-corruption or mapping layer
- **MUST** report server state copied into a client-state store where the project has a server-state cache, per the ownership rule: data the server owns belongs in the query or cache layer, data the client owns belongs in client state
- **MUST NOT** classify presentation logic as business logic: display formatting, conditional rendering, layout branching, and view-model shaping are the component's job
- **MUST NOT** demand a specific architecture. The repository's own declared layering wins; when the repository declares none, the reviewer states the layering it assumed and files layering findings as **suspected**

### F2—Error and asynchronous-state handling

The core D1 severity floor for swallowed and missing error handling applies verbatim: a confirmed instance is **Critical**, a suspected one is at least **Warning**, and it always enters the work packages. This dimension names the frontend shapes that floor takes.

- **MUST** report a request whose HTTP status is never inspected, where the client API resolves rather than rejects on an error status, so a `404` or `500` silently continues down the success path
- **MUST** report a rejection handler that neither surfaces a user-visible state, nor propagates, nor reports to the project's error sink—the browser instance of the core's swallowed-error no-go
- **MUST** report an asynchronous or event-handler failure path that relies on a render-error boundary, which structurally can't catch it
- **MUST** report a route or widget subtree with no error boundary above it where one render error blanks the whole application, and treat "one boundary at the application root" as that finding rather than as coverage
- **MUST** report a violation of the **three-state contract**: every asynchronous surface renders a pending state, a failure state carrying a recovery affordance, and an empty state, each distinguishable from success. A missing pending or empty state alone is **Warning**; a missing failure path is the Critical floor above
- **SHOULD** recommend a state model that makes contradictory combinations impossible to represent when independent boolean flags admit them—pending and failed at once, or settled with neither data nor error
- **MUST** report an in-flight request with no staleness or cancellation guard where the inputs can change or the component can unmount, so a late response overwrites a newer one
- **MUST** report error output that exposes raw exception text, stack traces, or backend internals to the user
- **MUST** report an optimistic update with no rollback on failure, and a mutation whose failure leaves the rendered state inconsistent with the server
- **SHOULD** report unbounded or unbacked-off retry, and blanket retry on client-error responses that can't succeed on repetition
- **SHOULD** report an application with no global handler for uncaught errors and unhandled rejections
- **MUST** route "errors never reach the observability sink" as a D10 route-out to `spec/project/monitoring-observability/` rather than deepening it here

### F3—Component design and public API

- **MUST** report a component that carries rendering, business logic, side effects, and every UI state at once, naming the responsibility to extract
- **MUST NOT** file a size finding on line count alone: a size finding names the responsibility that should leave the component
- **SHOULD** report configuration-driven components that a composition would express better, boolean-prop explosion where variants or children belong, and props threaded through several layers that don't consume them
- **SHOULD** report a shared-state mechanism used where local state suffices, and local state used where the project's shared mechanism is the declared home
- **MUST** report incoherent controlled and uncontrolled behaviour on an input surface, and props whose names leak the implementation rather than describing the contract
- **MUST** report unstable list identities—positional keys on a collection that reorders, inserts, or deletes—and the identity-driven remount used as a substitute for state design
- **SHOULD** report unknown props spread onto host elements, and imperative DOM manipulation where declarative state expresses the same thing
- **MUST** report a newly introduced component that duplicates one the project's shared component layer already provides, naming both

### F4—Frontend domain-knowledge duplication (extends D4)

The core D4 rule holds: this is **semantic** duplication, not textual similarity, every site is named, and one single-source-of-truth location is proposed. The frontend axes are:

- Validation rules duplicated between client and server without a shared schema or contract-generated source. The proposal names the shared source or the generation step, never "keep them in sync"
- Domain constants, enumerations, and status-to-label mappings re-declared in the client instead of derived from the API contract
- The same formatting or labelling rule—currency, units, thresholds, status wording—implemented in more than one component
- Data-fetching, caching, and invalidation logic re-implemented per component where a query layer exists
- Design values duplicated instead of referencing a token (the styling face of this class is F7; file it there when the issue is the token bypass, and here when the same *rule* is encoded twice)

### F5—Rendering, effects, and reactivity correctness

- **MUST** report state derived from existing props or state and stored instead of calculated during rendering
- **MUST** report effects used for logic that belongs to an event handler, and effect chains whose only purpose is to trigger one another through state
- **MUST** report state reset through an effect where the framework's identity mechanism expresses it
- **MUST** report a missing cleanup that leaks: event listeners, timers, subscriptions, observers, and object URLs created and never released
- **MUST** report side effects performed during the render phase—module state mutated, storage or the DOM written—rather than in the effect or handler that owns them
- **SHOULD** report dependency sets that are incomplete or that depend on identities recreated on every render, where the project's linter doesn't already cover it
- **MUST** report render output that isn't deterministic for the same inputs where the project renders on the server or hydrates, including unguarded access to browser-only global objects
- **SHOULD** report an effect that isn't idempotent under the framework's development-mode double invocation

### F6—Frontend performance visible in the source (extends D7)

This dimension is capped at what the source shows. Measured budgets route to `spec/frontend/webview-ui-optimization/`.

- **MUST** report request waterfalls and per-item request fan-out that the data layer should batch or the endpoint should serve
- **MUST** report a collection rendered in full where the data volume makes virtualisation or pagination the established answer
- **SHOULD** report a missing route-level split on a large route, whole-library or barrel imports that defeat tree shaking, and a heavy dependency carried for a trivial need (the dependency-choice face is D9)
- **SHOULD** report expensive derivation recomputed on every interaction where the input changes far less often
- **MUST** make the **memoization judgment conditional on the reviewed repository's build configuration**:
  - Where the project enables compiler-based automatic memoization, hand-written memoization isn't a finding unless it's incorrect, masks a real bug, or defeats the compiler
  - Where it doesn't, missing memoization is a finding only with a named, plausible cost—a large collection, a demonstrably expensive derivation, or a dependency that must stay referentially stable
  - **MUST NOT** file a blanket memoization finding in either direction, and **MUST NOT** present added memoization as an improvement without that named cost

### F7—Styling and design-system conformance

- **MUST** report hardcoded design values where the project ships tokens or a theme: colours, spacing, font sizes and weights, radii, shadows, z-index values, breakpoints, and motion durations
- **MUST** report z-index values outside a declared scale, and responsive rules written against ad-hoc pixel values instead of the project's breakpoint scale
- **SHOULD** report specificity escalation and forced-priority declarations used to defeat the system, style rules that escape their scoping mechanism into the global namespace, and dead or unused style blocks
- **SHOULD** report a duplicated style block that an existing token, variant, or shared component already expresses
- **MUST NOT** judge whether a chosen value is the *right* value: that's design. This dimension owns only whether the code bypasses the system the project already has

### F8—Accessibility defects visible in code

Capped at what a reviewer decides from the source; the conformance question routes out.

- **MUST** report a non-semantic element used as a control—a click handler on a generic element that carries no role, can't take focus, and handles no keyboard input—where a native element carries the semantics and behaviour already
- **MUST** report a role applied without the keyboard interaction and state management it promises, and roles or attributes that contradict the native semantics of the element they sit on
- **MUST** report an element hidden from assistive technology, or marked presentational, while remaining focusable
- **MUST** report form controls without a programmatic label, validation messages not programmatically associated with their control, icon-only controls without an accessible name, and images whose alternative-text decision is absent
- **SHOULD** report focus handling defects a reviewer can decide statically: a dialog that neither moves nor restores focus, a route change that leaves focus stranded, a positive tab index, and a focus indicator removed without a replacement
- **SHOULD** report asynchronous status changes announced to sighted users only, with no live region
- **MUST** route contrast ratios, conformance level, target sizes, and assistive-technology experience to `spec/frontend/webview-ui-optimization/` §Accessibility instead of judging them here
- **MUST NOT** report what the project's accessibility linter already reports (tooling-first)

### F9—Client trust boundary and security floors (extends D10)

The core D10 rule holds: these are **flagged and routed**, never investigated in depth here, and the remediation line is "dispatch the owning audit." The core severity floor still applies, so an active sink with attacker-controllable input is **Critical**.

- **MUST** flag HTML-injection sinks: raw HTML assignment or the framework's escape-hatch property fed with non-constant input and no sanitizing step
- **MUST** flag user-controlled URL sinks—link targets and resource sources without a scheme allowlist—which framework escaping doesn't cover
- **MUST** flag secrets, keys, and credentials present in client code or embedded into the bundle by the build
- **MUST** flag long-lived credentials placed in web storage, and client-side access control treated as enforcement (the security face of F1 class 2: file it once, under F9, and cross-reference the F1 class)
- **SHOULD** flag cross-document hazards visible in markup and message handling: an externally opened target without the opener restriction, and a message receiver that doesn't verify the sender's origin
- **SHOULD** flag user content that reaches a renderer without sanitizing—rich text, markdown, or charts—and framework escaping disabled explicitly
- **MUST NOT** audit Content Security Policy, HTTP security headers, or the authentication design here: those route to `spec/frontend/webview-ui-optimization/` §"Security and sandboxing" and `spec/project/code-security-audit/`

### F10—User-facing text and locale handling in code

- **MUST** report user-facing strings hardcoded in components where the project ships an internationalisation layer, including the surfaces a naive scan misses: accessible names, alternative text, tooltips, and document titles
- **MUST** report sentences assembled from concatenated or interpolated fragments, which can't be reordered or inflected by a translator, and quantity-dependent text without plural handling
- **MUST** report manual formatting of dates, times, numbers, currencies, and lists where a locale-aware platform API exists, and locale-unsafe sorting, casing, or comparison
- **SHOULD** report translation keys built dynamically at call sites, which defeat static coverage analysis
- **MUST** route key coverage and missing-translation completeness to `spec/project/i18n-completeness/`

### F11—Frontend test-code quality (extends D6)

The core D6 rules apply verbatim; these are the frontend shapes, and every finding carries the `test` marker.

- **MUST** report queries that reach past the accessible surface where a role, label, or text query would match—class names, component internals, deep DOM traversal, or a test identifier used where a semantic query works
- **MUST**, when a test *can't* query by role or label, report the finding as a probable **accessibility** defect in the component under test (an F8 finding surfacing as an F11 symptom), not as a test-only issue
- **MUST** report assertions on internal state, props, or lifecycle rather than on rendered output and observable behaviour
- **MUST** report snapshot assertions standing in for behavioural assertions, and snapshots too large to be reviewed meaningfully
- **MUST** report non-determinism: arbitrary waiting instead of awaiting an assertion, fake timers that are never restored, real network access, and assertions that depend on the machine's locale or timezone without pinning
- **MUST** report mocking of the project's own components or hooks where the network boundary is the honest seam
- **MUST** report untested failure and empty branches where F2's three-state contract applies. An F2 finding about a missing error path and an F11 finding about that path being untested belong in **one** work package
- **MUST** route ad-hoc test identifiers to `spec/frontend/testability-identifiers/`, and single-tier conformance detail to the owning tier reviewer

### Framework profiles

Every framework profile **MUST** define, and a reviewer applies as one unit:

- **Tooling baseline:** the linter and its framework and accessibility plugins, the formatter, the type checker and its strictness, the style linter, and the test runner with its DOM-testing library—the set the tooling-first rule defers to
- **Component and logic model:** where logic lives (component, hook or composable, framework-free domain module), and how client state and server state are categorised
- **Reactivity and effect model:** the framework's synchronisation primitive and its documented pitfalls, reviewed under F5
- **Rendering-cost model:** how re-render cost arises, and whether an automatic memoization step is part of the build—the input to F6's conditional memoization rule
- **Styling model:** how components reach the token or theme layer, and how style scoping works, reviewed under F7
- **Data-access model:** the project's client, cache, or query layer, reviewed under F1 and F4
- **Test-stack profile:** the idiomatic test stack and its F11-relevant conventions
- **Accessibility affordances:** what the framework and its linter give for free, so F8 stays above the tooling line

A framework without a profile **MUST** be reported as unsupported rather than reviewed ad hoc, exactly as the core spec requires for languages; the report states which profile it applied.

### React and TypeScript reference profile

- **Tooling baseline:** TypeScript in strict mode; ESLint with the React hooks rules and the JSX accessibility plugin; a formatter; a style linter where CSS is authored; a test runner with React Testing Library, a user-interaction library, and a network-level mocking layer. Formatting, import hygiene, hook-rule violations, and the mechanical accessibility rules belong to that tooling—the reviewer defers per the tooling-first rule
- **Component and logic model (F1):** components render; stateful behaviour lives in custom hooks; domain rules live in framework-free modules that import nothing from React; server state lives in the query or cache layer; client state stays local until a second consumer justifies lifting it
- **Typing discipline (D5, F3):** no escape-hatch `any`, unchecked casts, or non-null assertions on props and API payloads; API responses parsed or validated at the boundary rather than asserted into a type; asynchronous UI state modelled as a discriminated union rather than independent boolean flags; explicit prop types with explicit children; typed event handlers
- **Effect pitfalls (F5):** state derived in an effect instead of calculated during render; state reset in an effect instead of through a component key; event-handler logic placed in an effect; effect chains that cascade renders; fetches without an ignore flag or abort in the cleanup; missing cleanup on listeners, timers, subscriptions, and observers; unguarded `window` or `document` access on a server-rendered path
- **Rendering-cost model (F6):** re-render cost follows from identity churn and expensive derivation. Whether hand-written memoization is expected depends on whether the project enables compiler-based automatic memoization in its build configuration; the reviewer reads that from the repository and applies F6's conditional rule accordingly
- **Styling model (F7):** the project's theme or token module is the source of design values; scoped styling mechanisms mustn't leak globally; style objects recreated per render are an F7 finding when the issue is discipline and an F6 finding when the issue is measured cost
- **Data-access model (F1, F4):** one client or query layer owns requests, caching, and invalidation; components consume hooks over that layer, never a bare request function
- **Test-stack profile (F11):** Testing Library's documented query priority—role, then label, then text, with test identifiers as the last resort; a user-interaction library over low-level event dispatch; awaited asynchronous queries over arbitrary waiting; network-boundary mocking over stubbing the project's own modules
- **Accessibility affordances (F8):** the JSX accessibility plugin covers the mechanical rules, so F8 findings here are the ones it can't decide—role promises without the interaction behaviour, focus management, live regions, and label association across component boundaries

Vue, Angular, Svelte, and native web components have no profile in this spec yet and are reported as unsupported.

### Report, implementation proposals, and routing

The core §Report contract applies unchanged. This spec adds:

- **MUST** express every Critical and Warning finding's remediation as an **implementation proposal** a specialist can act on without re-deriving the analysis. The proposal names: the **target layer or file** for the change, the **shape** of the change (extract the rule into a hook, introduce a discriminated union for the request state, add a boundary around the route, replace the sink with the sanitising path, move the enforcement to the server), the **acceptance signal** (the test or observable behaviour that proves it), and the **risk** of applying it blindly
- **MUST NOT** apply, stage, or attach a patch: the reviewer stays read-only, and the proposal is prose plus, where it clarifies the shape, a short illustrative snippet marked as illustrative
- **SHOULD** cut work packages along **component-slice boundaries**, so that no two packages touch one slice; this satisfies and strengthens the core's disjoint-file-set guarantee, since a slice's component, styles, and tests move together
- **MUST** route each work package to the specialist that owns it: frontend production-code remediation to the implementing engineer role (`fullstack-developer`); accessibility conformance questions to `webview-ui-expert`; security floors to `code-security-reviewer`; translation coverage to the internationalisation checker; single-tier test conformance to the owning tier reviewer
- **MUST** group the report's findings by component slice in addition to severity, so a specialist receives one coherent unit of work rather than a scattered list
- **MUST** persist to the core artifact location, `.audits/source-code-review/<target-slug>.md` per `spec/claude/review-plan/` §"File location and naming," with the target slug distinguishing a frontend-scoped run from a whole-tree one; a re-run overwrites the canonical file
- **MUST** record in the header, alongside the core's scope and tooling baseline: the framework profile applied, any unsupported framework detected, and the four baselines from §"Review unit: The component slice"

### Delimitation from the UX review

This is a load-bearing boundary, not a courtesy note. The two reviews look at the same screen and answer different questions, and a frontend code review that drifts into UX judgment loses the authority that makes its findings actionable.

**The rule:** this review answers *is this code correct, layered, safe, accessible by construction, testable, and consistent with the system the project itself declares?* It never answers *is this the right experience?*

- **MUST NOT** file a finding whose only evidence is a rendered impression. Out of scope by construction: the wording, tone, or helpfulness of user-facing copy; visual hierarchy, spacing, and aesthetic choice; information architecture and navigation flow; whether a control is discoverable; whether a flow needs fewer steps; whether an interaction feels responsive; whether an empty state is motivating
- **MUST** file the **code-side twin** where one exists, and file only that. The twins that recur:

| UX question (not this review) | Code question (this review) |
|---|---|
| Is this error message friendly and helpful? | Is there an error path at all, and does it swallow the failure? (F2) |
| Is this the right shade of blue? | Does the value bypass the token layer the project ships? (F7) |
| Is this dialog confusing? | Does the dialog trap and restore focus? (F8) |
| Does this copy read well? | Is the copy hardcoded and untranslatable? (F10) |
| Does this list feel slow? | Is the whole collection rendered, and does each row fetch? (F6) |
| Is this the right default? | Is the default a domain rule the server must own? (F1) |

- **MUST** report a UX-class observation the reviewer happens to notice as a **single Info entry** with the routing target `frontend-usability-optimizer` or `webview-ui-optimize`, never above Info, and never inside the work packages
- **MUST NOT** be presented as a substitute for the UX or usability review: both are needed, they produce separate artifacts, and neither gates the other
- The boundary holds in reverse as well: the UX review doesn't file code findings, and a usability report is never merged into the code-review artifact

## Acceptance Criteria

- [ ] A frontend review runs the core D1–D10 dimensions **and** this overlay's F1–F11, and no finding carries both a D and an F ID
- [ ] The report header records the framework profile, the design-token or theme source, the internationalisation layer, and the data-access layer; a detected framework without a profile appears as unsupported
- [ ] A component is reviewed together with its hooks, styles, and tests; a report covering component files but no test files is rejected as incomplete
- [ ] A domain rule computed in a component is reported under F1 with its class named, and a rule the server must own but doesn't recompute is Critical when confirmed and routed to the security audit
- [ ] Presentation logic—display formatting, conditional rendering, layout branching—produces no F1 finding
- [ ] A rejection handler that surfaces nothing, propagates nothing, and reports nothing is Critical when confirmed and at least Warning when suspected, and it appears in the work packages
- [ ] An asynchronous surface missing a distinct pending, failure-with-recovery, or empty state produces an F2 finding, and its untested failure branch lands in the **same** work package as an F11 finding
- [ ] A memoization finding exists only with either a named cost or a named incorrectness, and no blanket memoization finding appears in either direction; the judgment matches what the repository's build configuration enables
- [ ] A hardcoded design value is reported under F7 where the project ships tokens, while the choice of value itself produces no finding
- [ ] A click handler on a non-semantic element that carries no role, can't take focus, and handles no keyboard input is reported under F8, while contrast and conformance-level questions appear only as route-outs
- [ ] An HTML or URL injection sink is flagged under F9 with a routing note and no in-depth analysis, and its severity respects the floor
- [ ] Every Critical and Warning finding carries an implementation proposal naming target layer, change shape, acceptance signal, and risk; no patch is applied or attached
- [ ] Work packages are cut along component slices, no two touch one slice, and each carries a routing target
- [ ] No finding above Info rests on a rendered impression; UX-class observations appear as Info entries routed to the usability capability and never in the work packages
- [ ] The persisted report lives at `.audits/source-code-review/<target-slug>.md` and a re-run overwrites it

## References

- [R1] The core review this spec extends (dimensions D1–D10, tooling-first rule, report and reviewer contracts): `spec/project/source-code-review/`
- [R2] Severity vocabulary and audit-artifact conventions: `spec/claude/review-plan/`
- [R3] Runtime quality of the web surface—measured performance, security headers and CSP, WCAG conformance, i18n runtime, UX and native feel (the main route-out and delimitation partner): `spec/frontend/webview-ui-optimization/`
- [R4] Whole-codebase security audit (route-out target for F9 floors): `spec/project/code-security-audit/`
- [R5] Observability audit (route-out target for unreported errors): `spec/project/monitoring-observability/`
- [R6] Translation-key coverage and locale completeness (route-out target for F10): `spec/project/i18n-completeness/`
- [R7] Test-identifier contract (route-out target for F11 identifier findings): `spec/frontend/testability-identifiers/`
- [R8] Test-tier specs and reviewers (route-out targets for tier conformance): `spec/project/test-pyramid-foundation/` and `spec/project/test-tier-*/`
- [R9] Mechanical gate the tooling-first rule defers to: `spec/project/quality-gate/`
- [R10] Agent authoring rules and read-only tool discipline: `spec/claude/agent-management/`
- [R11] Research methodology and source thresholds behind this spec's rules: `spec/claude/research-triangulate/`
- [R12] Evidence notes with the sources behind each dimension: `spec/frontend/source-code-review/research/`

## Open Questions

- Which framework profile follows the React and TypeScript reference—Vue, Angular, or Svelte—and does it live in this spec or in a sibling profile document once the profile count grows?
- Is the frontend reviewer one agent per framework, mirroring the per-language reviewer agents of the core spec, or one profile-driven agent that selects its profile at dispatch time? The core spec's per-language dispatch argues for the first; the shared F1–F11 overlay argues for the second.
- Where does a shared client-and-server validation contract live when the two sides are separate repositories, and does F4's single-source-of-truth proposal reach across a repository boundary before the portfolio-inherited spec layer ships a cross-repo resolver?
- Should F6 gain a bundle-composition view (what a dependency costs at the import site) or does that stay entirely with the measured budgets in `spec/frontend/webview-ui-optimization/`?
