# Frontend Testability: Stable Test Identifiers

Status: draft

## Context

An end-to-end test can only be trustworthy if the surface it drives is addressable: every test-relevant element and page must expose a stable, unique identifier a test can select by. That's the **provider side** of testability, and it's application work—not test work. `spec/project/e2e-test-automation/` governs the **consumer side** (how a suite *selects*: the locator robustness hierarchy, page objects, condition-based waits) and deliberately scopes provisioning *out*: its Non-Goals name "generating production application code or `data-testid` hooks in the application under test (the suite *relies on* such hooks; adding them is application work)." This spec claims that scoped-out application work as its subject. The two specs are consumer/provider siblings: one norms how tests select, this one norms what the frontend must provide.

The reusable part of provisioning is framework-independent: the *obligation* to mark test-relevant elements, the *stability contract* that keeps those marks from silently breaking, the *naming schema* that keeps them predictable, and the rule that repeated collections stay addressable by a business key rather than a position. The throwaway part is the mechanism—which attribute carries the identifier in a given technology. This spec states the obligation framework-neutrally as the binding core, then pins one concrete, fully worked **Web reference profile** (`data-testid` in the DOM) as a normative section, so a web project gets a batteries-included default while other stacks realise the same core.

The content is generalised from the kamerplanter `UI-NFR-022` provisioning standard (`R-001..R-025`) and lifted out of its plant domain: the plant-specific `species-*` examples become `<entity>-*` placeholders so the rules read portfolio-wide rather than as one app's convention.

Readers: frontend developers who build or reshape a portfolio UI (`nolte-engineering` audience); the UX/usability role that edits an existing presentation layer; reviewers verifying that a diff keeps the surface addressable. It's operationalised in lockstep with the frontend build and UX agents that consume it (`fullstack-developer`, `frontend-usability-optimizer`, `webview-ui-expert`).

## Goals

- State the provisioning obligation once, framework-neutrally, as the binding core every consuming frontend must satisfy so its surface is addressable by an E2E suite.
- Keep the core realisable on any UI stack by demoting the concrete carrier attribute to a swappable reference profile rather than a requirement.
- Ship one fully worked, normative **Web reference profile** (`data-testid`, DOM) so a web project is productive immediately.
- Make identifiers a stability contract: deterministic, predictable by a naming schema, stable across element states, and never silently renamed or removed.
- Bind not only frontend implementers but also the UX/usability role, so a usability edit preserves the identifiers a test depends on rather than breaking them.
- Cross-reference the consumer sibling (`e2e-test-automation` §Locator strategy) so provider and consumer stay a matched pair.

## Non-Goals

- **Selecting** by these identifiers in a test suite—the locator robustness hierarchy, page-object encapsulation, and waiting discipline are owned by `spec/project/e2e-test-automation/` §Locator strategy (the consumer sibling). This spec provisions the hooks that hierarchy consumes; it doesn't govern how tests use them.
- The **component-test tier's** query philosophy: `spec/project/test-tier-component/` prefers user-facing queries (role, label, text) and treats a test id as a last resort, by Testing-Library design. That's intentionally different from the E2E provider contract here (test-hook-first) and is a delimitation, not a contradiction: the two tiers optimise for different failure modes.
- **Non-web framework profiles** (native mobile, Flutter, desktop)—deferred until a consumer forces one, exactly as `e2e-test-automation` defers non-Selenium profiles. The neutral core already binds them; only the concrete profile is missing.
- **Naming a concrete linter or enforcement tool**: enforcement is described as an optional MAY (see §Optional enforcement); this spec mandates no specific tooling.
- Authoring or editing the test suites that consume these identifiers.

## Requirements

### Framework neutrality

- The binding requirements in this section **MUST** be expressed against a capability every UI stack provides—attaching a stable, machine-readable identifier to a rendered element—and **MUST NOT** name a concrete attribute, framework, or component library.
- A consuming project **MUST** declare which mechanism realises the identifier; absent a declaration, consumers and consuming agents **MUST** assume the Web reference profile (`data-testid`) below.
- Every concrete artefact this spec names (the `data-testid` attribute, the DOM examples) is part of the **reference profile** and **MAY** be replaced wholesale by a project on a different stack, provided the binding core still holds.

### Provisioning obligation and the provisioning-vs-selection split

- The frontend **MUST** *provide* a stable, unique identifier on every test-relevant element and page; a test suite *selects* by that identifier but **MUST NOT** be relied upon to create it. Provisioning is application work; selection is test work.
- An element is **test-relevant** when a user-journey test would need to locate it: interactive controls, form fields, dialogs, navigational landmarks, and any status or result display whose content a test asserts on. When in doubt, an element **SHOULD** be treated as test-relevant (recall over precision).
- The provided identifier **MUST** be the primary selection anchor named first in the consumer's locator hierarchy (`e2e-test-automation` §Locator strategy: dedicated test hook → id → semantic/role → CSS → XPath).

### Page-level markers

- Every routable page or top-level view **MUST** carry a page marker identifier of the form `<entity>-<view>-page`, so a test can assert it has landed on the right page before acting.
- A shared loading-state marker (`loading-skeleton` or an equivalent single, stable name) **MUST** be provided while a page or region is loading, so a test can wait on a condition rather than a fixed delay.

### Element-level provisioning

- Interactive elements (buttons, links, toggles, menu items) that a test drives **MUST** each carry a stable identifier.
- Form fields **MUST** carry a stable identifier of the form `form-field-<name>`, where `<name>` is the field's stable business name, not its position or label text.
- Dialogs, modals, and overlays **MUST** carry a stable identifier on their root so a test can scope selection to the open dialog.
- Any status, validation, or result display whose content a test asserts on **MUST** carry a stable identifier; this holds regardless of how the element is mounted (inline, portal, toast, overlay)—mounting context doesn't exempt a test-relevant element from provisioning.

### Repeated collections addressable by business key

- Rows of a repeated list or table **MUST** be addressable by a stable **business key** (for example `<entity>-row-<businessKey>`), never by list index or DOM position, so a test survives reordering, filtering, and pagination.
- WHEN no natural business key exists, the frontend **MUST** provide a stable synthetic key that's deterministic across renders; a render-order index or an ephemeral runtime id **MUST NOT** be used as the addressing key.

### Naming schema

- Identifier values **MUST** follow a single naming schema: kebab-case, English, composed from stable business terms (`<entity>-<view>-page`, `form-field-<name>`, `<entity>-row-<businessKey>`).
- Identifier values **MUST NOT** encode volatile facts (positional index, pixel geometry, generated hashes, localised display text); the value **MUST** stay readable and predictable from the schema alone.

### Stability as a contract

- A provided identifier **MUST** be deterministic across renders and **MUST** remain stable across an element's states (enabled/disabled, loading/loaded, valid/invalid, empty/populated).
- A provided identifier **MUST NOT** be silently renamed or removed; a change to an identifier is a breaking change to the test surface and **MUST** be treated as such (announced, coordinated with the consuming suite).
- Framework-generated identifiers, hashed CSS-module class names, and other non-deterministic or non-speaking values **MUST NOT** be used to satisfy the provisioning obligation.
- An identifier **MUST** survive cosmetic markup changes (style changes, added wrapper elements, layout refactors), mirroring the consumer requirement that selectors survive such changes.

### Accessibility hooks as a secondary anchor

- Accessibility attributes (`role`, `aria-label`, and equivalents) **MAY** serve as a secondary selection anchor and **SHOULD** be present for their own sake, but **MUST NOT** replace the primary provided identifier: a11y semantics and the test hook are complementary, and a test-relevant element still carries its dedicated identifier.

### UX and usability role obligation

- The UX/usability role (concretely the `frontend-usability-optimizer` agent; secondarily the UX domain of the `webview-ui-expert` review) is an addressed provider and **MUST** observe this contract.
- WHEN the UX/usability role reshapes an existing element—a form, dialog, list or table, detail page, or its loading/error/empty states—the frontend **MUST** preserve the element's stable identifier: a usability edit **MUST NOT** silently rename or drop a provided identifier (a special case of the stability contract above).

### Optional enforcement

- A consuming project **MAY** add a lint or review rule that a new interactive component ships a provided identifier (the `UI-NFR-022` definition-of-done pattern), but this spec **MUST NOT** name a specific linter or mandate a specific enforcement mechanism; the obligation is normative, the tooling is a project choice.

### Web reference profile (normative)

This profile is the binding realisation of the core for web (DOM) projects and the default consuming agents assume when no other mechanism is declared. A project on another stack replaces this section wholesale but still satisfies the core above.

- The provided identifier **MUST** be carried by the `data-testid` attribute in the DOM; it's the dedicated test hook the consumer hierarchy names first.
- A routable page **MUST** render `data-testid="<entity>-<view>-page"` on its top-level container; a loading region **MUST** render `data-testid="loading-skeleton"` while loading.
- A form field **MUST** render `data-testid="form-field-<name>"`; an interactive control **MUST** render a `data-testid`; a dialog root **MUST** render a `data-testid`; a test-relevant status or result element **MUST** render a `data-testid`.
- A repeated row **MUST** render `data-testid="<entity>-row-<businessKey>"` keyed by the business key, never by index.
- All `data-testid` values **MUST** be kebab-case English per §Naming schema, and `data-testid` **MUST NOT** be applied through a positional or hashed value.
- `role`/`aria-label` **MAY** accompany a `data-testid` but **MUST NOT** replace it.

## Acceptance Criteria

- [ ] Every binding requirement outside the reference-profile section is expressed without naming a concrete attribute, framework, or component library.
- [ ] The Web reference profile is concrete enough that a web project can provision a conformant surface from it alone (page markers, `loading-skeleton`, `form-field-<name>`, interactive controls, dialogs, status displays, business-key rows).
- [ ] The provisioning-vs-selection split is stated and cross-referenced to `e2e-test-automation` §Locator strategy, and that spec carries a forward pointer back to this one.
- [ ] Page markers, element identifiers, and business-key row addressing are all required, with index-based addressing explicitly forbidden.
- [ ] The naming schema (kebab-case, English, no volatile facts) and the stability contract (deterministic, state-stable, no silent rename, no framework-generated or hashed values) are both normative.
- [ ] Accessibility hooks are positioned as a secondary anchor that never replaces the primary identifier.
- [ ] The UX/usability role is bound as an addressed provider, and identifier preservation on a usability edit is required.
- [ ] Enforcement is mentioned only as an optional MAY, with no linter named.
- [ ] The component-tier delimitation (`test-tier-component`, user-facing-query-first) is noted as an intentional difference, not a contradiction.

## References

- [R1] Consumer sibling (locator strategy, page objects, waiting discipline; the suite that consumes these hooks): `spec/project/e2e-test-automation/` §Locator strategy
- [R2] Component-tier query philosophy, delimited against this spec: `spec/project/test-tier-component/`
- [R3] Frontend performance/security/a11y/i18n/UX rules for the same web surface: `spec/frontend/webview-ui-optimization/`
- [R4] Provenance of the provisioning rules, generalised here from their plant domain: kamerplanter `UI-NFR-022` (`R-001..R-025`), PR #581
- [R5] Agent authoring rules the consuming agents conform to: `spec/claude/agent-management/`

## Open Questions

- Whether a second, equally normative non-web profile (native mobile, Flutter, desktop) should ship once a portfolio project needs it, or whether the Web profile plus the framework-neutral core is enough guidance. Provisional default until a consumer forces the question: ship only the Web profile and rely on the core.
- ~~Whether the consuming UX/build agents (`frontend-usability-optimizer`, `webview-ui-expert`, `fullstack-developer`) should cite this spec from their own `description`/`use_when`, or whether the binding declared here is sufficient.~~ **Resolved:** the binding is now wired into each agent's **body** (system prompt), not its routing `description`/`use_when`—`fullstack-developer` provisions identifiers on the UI it builds, `frontend-usability-optimizer` preserves them on a reshape, and `webview-ui-expert` flags missing/broken ones as a UX-domain finding. The body was chosen over the frontmatter to keep the operative rules where behaviour lives and to avoid growing the agent-routing `description` budget.
