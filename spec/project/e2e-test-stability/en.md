# End-to-End Test Stability Engineering

Status: draft

## Context

A full-suite stabilization pass over a consuming project's E2E suite (≈720 Selenium + pytest tests, xdist-parallel, Docker-composed app stack) showed that most instability **doesn't** come from the concerns the automation standard already governs (page objects, condition-based waits, locator hierarchy per `spec/project/e2e-test-automation/`). It came from five recurring mechanics that no locator or wait discipline prevents:

1. **Shared-state coupling**: tests consuming "the first row," seed leftovers, or entities another test (on another parallel worker) happened to create. Symptoms: order-dependent silent skips (13 tests silently skipping in every run), tests that pass or fail depending on worker scheduling.
2. **Global server-side state mutated across workers**: a per-user singleton (experience level on a shared anonymous-mode user) flipped mid-assertion by an unrelated test file running on another worker.
3. **Hazard-prone UI interactions**: a blind `ESC`-to-body "backdrop dismissal" that closes the *parent dialog* whenever the select menu already closed itself (a race that hit ~20 copy-pasted page-object methods); clicks intercepted by still-collapsing snackbars.
4. **Optimistic UI feedback**: a "saved" snackbar queued *before* the PATCH resolved; the test trusted it, reloaded, and the in-flight request was killed—the change silently lost (a real user-facing data-loss bug, not a test problem).
5. **Genuine application concurrency defects that only parallel E2E load exposes**: a create-on-first-read race minting duplicate singleton documents (no unique index), and a read-modify-write-full-document update losing concurrent PATCHes of disjoint fields. Both reproduced deterministically outside the suite once identified.

A later stabilization pass over the same project's **mobile** E2E profile (141 → 72 → 8 → 5 failures across four full runs, with the desktop profiles green on the same commits) added a sixth mechanic, **viewport-dependent behaviour**: role collisions with hidden responsive chrome, layout switches that change the DOM shape, breakpoint-dependent wrapper geometry, activation models a synthetic fallback can't drive, popovers repositioning mid-animation. Most of these don't fail loudly: they produce empty reads and no-op interactions that let tests pass for the wrong reason. §G catalogs that class.

The load-bearing insight: **a parallel E2E suite is a de-facto concurrency test of the application.** Failures it surfaces split into test-design debt (1–3), app-truthfulness debt (4), and product concurrency defects (5)—and each class has a different correct fix. Stabilizing by retries, skips, serializing everything, or weakening assertions hides all three.

This spec turns those findings into design rules so new suites are stable from the first commit, and into a bounded stabilization loop for existing suites. It complements `spec/project/e2e-test-automation/` (which owns the suite's *shape*: page objects, waits, locators, screenshots, protocol, traceability); this spec owns the suite's *runtime stability* under parallel execution.

Readers: authors and reviewers of E2E suites; the `e2e-test-generator` / `e2e-test-reviewer` agents; the test-cycle skills that classify and repair failing runs.

## Goals

- Make E2E tests deterministic by design: self-provisioned data, no cross-test or cross-worker coupling
- Make suites parallel-safe: global mutable state is inventoried and everything that mutates it serialized, everything else stays parallel
- Catalog the known UI-interaction hazards (blind keyboard dismissals, transient-overlay intercepts) and mandate the guarded helpers that avoid them
- Catalog the responsive/viewport hazards a mobile or tablet profile adds (cross-breakpoint role collisions, layout-switch readers, unsound click fallbacks, animation races) and mandate layout-asserting, loud-failing page objects and an animation-free harness
- Key every wait on durable, truthful signals—and treat optimistic success feedback in the app as an implementation defect
- Route concurrency failures surfaced by parallel E2E runs to the application as product defects instead of absorbing them in the test layer
- Keep skips and expected-failure markers honest: deterministic, explained, monitored, and removed when healed
- Define the stabilization loop (classify → fix by class → re-run → green twice without intervention) as the exit criterion for suite work

## Non-Goals

- The E2E suite's shape and discipline (page-object encapsulation, deterministic waiting primitives, locator strategy, screenshots, protocol, markers, traceability), owned by `spec/project/e2e-test-automation/`
- The failure-classification taxonomy and flake-vs-real adjudication process, owned by `spec/project/test-cycle-result-analysis/`; this spec consumes its classes
- How a confirmed real defect is fixed in production code (including the no-cheating invariant), owned by `spec/project/test-cycle-code-adaptation/`
- Provisioning testability hooks (`data-testid`, state exposition) in the application, owned by `spec/frontend/testability-identifiers/`
- Test-tier placement (what belongs in E2E at all), owned by `spec/project/test-pyramid-foundation/`
- The cross-tier taxonomy and detection of tests that can't fail, owned by `spec/project/test-falsifiability/`; this spec's §A/§E (skips), §D (state-changer read-back), and §G (silent responsive passes) supply the E2E instances that taxonomy cites as T3, T4, T6, and T7

## Requirements

### A. Test-data isolation (self-provisioning)

- A test that mutates an entity, or depends on an entity's sub-state (for example "has no quality assessment yet"), **MUST** create that entity itself, tagged with a collision-free unique identifier (UUID-derived; unique across parallel workers and repeated runs)
- A test **MUST NOT** depend on entities created by other test files, on their execution order, or on which parallel worker ran them; "click the first row" is acceptable only for read-only assertions that hold for *any* row
- Read-only tests **MAY** consume shared seed data, but when the expected data can legitimately be absent they **MUST** fall back to self-provisioning instead of skipping—an availability-dependent skip is a silent coverage hole, not a pass
- Self-provisioning helpers **MUST** distinguish "creation impossible for an expected domain reason" (explicit, reasoned skip) from "creation failed" (loud failure), and **MUST NOT** convert the latter into the former

### B. Parallel execution and global state

- A suite **MUST** maintain an inventory of global server-side mutable state its tests touch (singleton documents, shared-user preferences for anonymous/light modes, cluster-wide feature flags) and which test files mutate or assert on each
- Tests that mutate or assert on the same global state **MUST** be serialized against each other across parallel workers (inter-process lock, scheduler groups, or equivalent) while the rest of the suite stays parallel; serializing the whole suite isn't an acceptable substitute
- When a test is stable in isolated repetition but fails under the parallel suite, that asymmetry **MUST** be treated as evidence of cross-test interference and investigated as such (isolation experiment: N consecutive single-file runs against the same stack), not re-labeled a flake
- A concurrency failure surfaced by parallel execution (duplicate rows from a create-on-first-read race, a lost update from a read-modify-write-full-record pattern, a missing unique constraint on a logically-unique key) **MUST** be classified as an application defect and fixed in the application (unique constraint plus `upsert` semantics; partial field-level updates), **never** absorbed by test-side retries, ordering, or lock scope creep
- Fixes for such application defects **SHOULD** include a regression test at the lowest tier that can express the race (usually a unit/integration test asserting the update-doc shape or the `upsert` path), so the E2E tier isn't the only guard

### C. Interaction-hazard catalog

- A test or page object **MUST NOT** send a blind keyboard dismissal (`ESC` to `body`) to "clean up" a menu, popover, or backdrop: when the popover has already closed itself, the key lands in the parent dialog and closes it—a timing race. Dismissal **MUST** go through a guarded helper that (1) returns immediately when the popover is already gone, (2) waits briefly for it to close on its own, (3) sends `ESC` only while the popover is verifiably still open, then (4) waits for it to be gone
- A click on an element that a transient overlay (snackbar, toast, collapse animation) can cover **MUST** use an overlay-tolerant click (scroll into view, then click with an intercepted-click fallback), not a bare element click
- After selecting an option from a menu/select, the interaction flow **MUST** wait until the popover is gone before the next element interaction; where the form allows it, plain input fields **SHOULD** be filled before menu-opening interactions rather than after
- These guarded helpers **MUST** live once in the shared page-object base; per-page copies of interaction plumbing are how the same hazard was re-introduced ~20 times

### D. Truthful asynchronous signals

- A wait **MUST** be keyed on a durable signal (server-confirmed state, a read-back after full reload, an element whose presence proves persistence), never on optimistic UI feedback that precedes the underlying request's resolution
- When the application emits success feedback before the change is durably persisted (fire-and-forget dispatch followed by an immediate success toast), that's an **implementation defect** (a user who navigates away promptly loses the change) and **MUST** be fixed in the application (await persistence, then confirm; error feedback on failure). Test-side compensation (sleeps, trusting the toast anyway) is forbidden
- A state-changing helper **MUST** verify its effect (read-back with bounded retries, re-attempting the action where legitimate) and **MUST** fail loudly when the state never materializes; silently proceeding after an exhausted retry loop leaves the test asserting against the *previous* state and produces one-off-by-one failures that get attributed to the wrong cause for hours
- Fail-open versus fail-closed rendering during async loads (navigation showing everything vs. form fields hidden while a fetch is in flight) **MUST** be understood per surface and reflected in what the test polls for; a poll that can never distinguish "not yet loaded" from "correctly absent" isn't a valid assertion

### E. Skip and expected-failure hygiene

- Every skip **MUST** be deterministic for a given (code, seed, configuration) triple and carry a reason string naming the concrete precondition; a skip whose firing depends on worker scheduling or test order is a test defect covered by §A
- An expected-failure marker (`xfail`) **MUST** be non-strict only with a documented reason, a pointer to the underlying finding/issue, and a revisit condition; suites **MUST** watch the `xpass` count, and once the underlying cause is fixed and the marked tests pass consistently through the suite's green-confirmation window (§F), the markers **MUST** be removed rather than left to rot
- Triage output **MUST** surface per-file skip counts so silently-lost coverage is visible; a class of tests skipping in every run is a finding, not background noise

### F. Stabilization loop (process)

- Every non-pass **MUST** be classified before anything is changed, using the classes of `spec/project/test-cycle-result-analysis/` (real defect / flake / test bug / infrastructure), and the fix **MUST** match the class: test bug → minimal surgical test fix; implementation bug → root-cause fix in the application; flake → prove by independent re-run, then harden the condition or setup; infrastructure → fix the harness
- A profile/suite counts as stabilized only after passing **twice consecutively without any intervention** in between; any code or test change resets the counter
- Retries-as-fix, new skips, deleted tests, and weakened assertions are forbidden stabilization means (the no-cheating invariant of `spec/project/test-cycle-code-adaptation/` applied to the suite level); deleting a test requires an explicit justification against its test-case specification
- Run artifacts (screenshots, application/container logs, request logs, the machine-generated protocol) **MUST** be retained per run and used as triage evidence; a claim about "what the app showed" is settled by the screenshot, and a claim about "what the server did" by the request log—including request-count diffs between runs, which settle whether the server was even asked—before any hypothesis is coded against
- When the same surface fails repeatedly with rotating root causes, the loop **MUST** keep drilling until a mechanism is *proven* (reproduced outside the suite, or demonstrated by isolation asymmetry)—three distinct stacked causes on one page (optimistic feedback, lost update, duplicate singletons) is a realistic outcome, and stopping after the first plausible fix leaves the suite red

### G. Responsive and viewport-dependent hazards

A responsive UI renders different chrome, DOM shapes, and geometry per breakpoint, so a suite that adds a mobile or tablet profile inherits a hazard class §A–F don't cover—and most of it fails silently, as empty reads and no-op interactions that let tests pass for the wrong reason:

- A locator built on a structural or ARIA role alone (a bare dialog or listbox role, a bare table or cell selector) **MUST NOT** be used unscoped: component libraries assign the same role to different chrome at different breakpoints, and a hidden, kept-mounted responsive element can carry the role and precede the real target in the DOM. Scope the selector to its owning container or address a dedicated test hook, per `spec/project/e2e-test-automation/` §Locator strategy
- A page object **MUST NOT** read a layout-specific structure (a desktop table, a mobile card list) without asserting that layout is active, and a reader that can't find its expected structure **MUST** fail loudly rather than return an empty result—an empty read that satisfies a "nothing unexpected present" assertion is a silent coverage hole
- Access into a responsive collection **MUST** be key-based, never position-based: a positional read is wrong at every breakpoint, on desktop merely undetectably so. The provider-side obligations this depends on—the same key-based hooks in every layout, per-layout discriminability of lists, the identifier on the interaction-receiving element—are owned by `spec/frontend/testability-identifiers/`
- A click fallback (a synthetic script click, coordinate-based event dispatch) **MUST** be sound for the target component's activation model or **MUST** fail loudly; a fallback that can't produce the effect but reports success is worse than no fallback, and coordinate-based dispatch performs no interactability hit-test, so it delivers events to whatever sits on top
- A helper that opens a menu, select, or popover **MUST** verify the component actually opened (an expanded-state attribute or equivalent) instead of assuming the click worked—§D's verify-its-effect rule applied to the open step
- A viewport-conditional affordance (a section collapsed behind a disclosure control, an overflow menu, drawer navigation) **MUST** be part of the page object's contract, expanded condition-based and idempotently before dependent interactions
- The browser harness **MUST** disable UI animations suite-wide (a forced reduced-motion preference or the framework equivalent); clicking a still-animating, repositioning popover is a race no wait can reliably close
- Only one application stack **MUST** run against a given browser grid at a time; concurrent stacks exhaust the grid's session capacity and produce mass setup errors that masquerade as suite failures
- A profile in a declared test matrix **MUST** count as covered only after at least one valid baseline run; an infrastructure-poisoned run isn't a baseline

## Acceptance Criteria

- [ ] New E2E tests self-provision the entities they mutate or whose sub-state they depend on, with collision-free unique identifiers
- [ ] The suite documents its global-mutable-state inventory and serializes exactly the mutating/asserting test files against each other, nothing more
- [ ] No page object sends an unguarded `ESC`-to-body dismissal; menu/overlay dismissal goes through the shared guarded helper
- [ ] No wait keys on optimistic UI feedback; state-changing helpers read back their effect and fail loudly on non-application
- [ ] Concurrency defects found under parallel runs are fixed in the application (with a lower-tier regression test), not absorbed by the test layer
- [ ] All skips are deterministic and reasoned; `xfail` markers carry reason + revisit condition and are removed once they `xpass` through a full green-confirmation window
- [ ] Suite stabilization work follows classify → class-matched fix → re-run, with green-twice-without-intervention as the exit criterion
- [ ] No structural/ARIA-role locator is used unscoped; layout-specific readers assert their layout is active and fail loudly instead of returning empty results
- [ ] Click fallbacks are sound for the target's activation model or fail loudly, open-helpers verify the opened state, the harness runs animation-free with one stack per browser grid, and a matrix profile counts as covered only after a valid baseline run
- [ ] The `e2e-test-generator` and `e2e-test-reviewer` agents apply this spec alongside `spec/project/e2e-test-automation/` when scaffolding or reviewing suites

## References

- `spec/project/e2e-test-automation/`: the suite-shape standard this spec complements (page objects, waits, locators, screenshots, protocol, traceability)
- `spec/project/test-cycle-result-analysis/`: failure-classification taxonomy consumed by §F
- `spec/project/test-cycle-code-adaptation/`: the no-cheating invariant and root-cause fixing for confirmed defects
- `spec/project/test-pyramid-foundation/`: tier placement; the lower-tier regression tests required by §B
- `spec/frontend/testability-identifiers/`: provider-side testability hooks in the application under test
- `spec/project/test-falsifiability/`: the cross-tier falsifiability taxonomy that generalizes this spec's loud-failure rules and consumes §F's request-count evidence as a detection route
- Source experience: kamerplanter full-suite E2E stabilization (2026-07), branch `fix/e2e-full-run-stabilization`: order-dependent harvest-detail skips, ESC-race across ~20 page objects, optimistic experience-level snackbar, preference lost-update, duplicate singleton preference documents; each mechanic listed in §Context maps to a reproduced incident there; the mobile-profile pass (runs `20260725_010046`, `030325`, `055859`, `073849`; 141 → 72 → 8 → 5 failures) supplied the §G viewport hazards

## Open Questions

- Should the global-state inventory (§B) be a machine-readable artifact (for example a conftest-level registry the lock fixture derives its file list from) instead of prose? The consuming project currently hard-codes the serialized-module set next to the lock
- Whether the isolation experiment (§B) should be automated as a triage skill step (run the failing file N× against a fresh stack and report the asymmetry) or stay a manual diagnostic
