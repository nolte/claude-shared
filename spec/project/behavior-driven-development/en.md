# Behavior-Driven Development

Status: draft
Portfolio-Scope: portfolio

## Context

Behavior-Driven Development (BDD) is the practice of specifying a system's behavior through concrete, business-readable examples, discovered collaboratively and written so that the same examples serve as the acceptance criteria, the automated test, and the living documentation. Its reusable, portfolio-wide part isn't a framework or a file format: it's the discipline of turning a shared understanding of *what the system should do* into examples that read in the language of the domain, describe one behavior each, stay declarative about *what* rather than *how*, and trace back to the requirement they verify. That discipline is tool-independent. The throwaway part is the glue: which library parses the examples, which directory holds them, which step-binding syntax a given stack uses.

This spec owns that reusable discipline. It's the normative treatment BDD gets in this corpus: collaborative example discovery, the Given-When-Then scenario language, declarative scenario design, ubiquitous language, living documentation, and step-definition principles, plus the derivation path from an abstract **test-case document** to **executable BDD scenarios**. `spec/project/test-cycle-case-determination/` already names Example Mapping and Specification by Example / BDD (Given-When-Then) as a **SHOULD** for discovering cases before coding but mandates no BDD framework; this spec turns that pointer into a full, still tool-neutral standard. The normative core is **tier-neutral**: a BDD scenario can drive a unit, component, integration, or end-to-end test. End-to-end (E2E) is the primary application and gets its own requirement group, because that's where a business-readable scenario earns the most, but the core never assumes a tier.

Because the corpus is polyglot, this spec states the discipline as the binding core and pins one concrete, illustrative **reference profile** (Gherkin plus the Cucumber family) as a non-normative appendix, so an author sees the discipline made real without the profile becoming a requirement. This mirrors how `spec/project/e2e-test-automation/` demotes its Selenium stack to a swappable reference profile.

**Relationship to the other specs.** Bounded by responsibility:

- `spec/project/test-cycle-case-determination/` [R1] owns *when*, in the recurring test cycle, examples are discovered and which design techniques apply. This spec owns *how* BDD structures that discovery and encodes it as scenarios; it doesn't restate the cycle.
- `spec/project/test-case-derivation/` [R2] owns deriving abstract, framework-agnostic test cases from a requirement document. This spec **consumes** such a test-case document as its input and doesn't re-derive it.
- `spec/project/e2e-test-automation/` [R3] owns the E2E execution mechanics: page objects, condition-based waits, screenshots, protocols, and requirement traceability. This spec owns the scenario/specification layer *above* that machinery; a step delegates down into it rather than restating it.
- `spec/frontend/testability-identifiers/` [R4] owns the stable selector contract a step ultimately resolves against. This spec never specifies selectors; it relies on that provider-side contract through the execution layer.

Readers: spec authors writing the sibling test specs; skill and agent authors building a BDD capability that turns a test-case document into runnable scenarios; developers, testers, and business analysts who write or review scenarios; reviewers checking that a scenario set is declarative, one-behavior-per-scenario, traceable, and readable as documentation.

## Goals

- State the tool-neutral BDD discipline once, as the binding core every consuming project satisfies regardless of framework or tier
- Keep the core executable on any BDD stack by demoting Gherkin and the Cucumber family to an illustrative, swappable reference profile rather than a requirement
- Make collaborative discovery (Example Mapping, Three Amigos) the front door, so scenarios encode a shared understanding rather than one author's guess
- Define a normative, ordered workflow that turns an abstract test-case document into executable BDD scenarios with end-to-end traceability
- Treat scenarios as living documentation written in the domain's ubiquitous language, not as disguised test scripts
- Give BDD-on-E2E its own requirements while keeping the core tier-neutral, deferring execution mechanics to `spec/project/e2e-test-automation/`
- Name the recurring BDD anti-patterns so a consuming skill and its reviewers can reject them

## Non-Goals

- Deciding *when* in the cycle examples are discovered or which test-design technique families apply: owned by `spec/project/test-cycle-case-determination/` [R1], which this spec operationalizes for the BDD case rather than restates
- Deriving the abstract, framework-agnostic **test cases** from a requirement document: owned by `spec/project/test-case-derivation/` [R2]; this spec consumes such cases (by their TC-IDs) as input and doesn't produce them
- The E2E **execution mechanics** a scenario runs on (page objects, waits, screenshots, protocol, driver glue): owned by `spec/project/e2e-test-automation/` [R3]; this spec governs the scenario layer above them
- Provisioning the stable **selectors** a step resolves against: owned by `spec/frontend/testability-identifiers/` [R4]; a scenario relies on that contract and never names a selector
- Mandating a specific BDD framework, parser, or file extension: the core is tool-neutral; Gherkin and the Cucumber family are the illustrative reference profile, not a requirement
- Setting the tier taxonomy or coverage governance: owned by `spec/project/test-pyramid-foundation/` [R5]

## Requirements

### Tool neutrality and tier scope

- The binding requirements in this spec **MUST** be expressed against capabilities every BDD approach provides (discover examples, express a behavior as precondition / action / expected outcome, bind that expression to executable steps, run it as a test that doubles as documentation), and **MUST NOT** name a concrete framework, parser, language, or file extension.
- The normative core **MUST** stay tier-neutral: a BDD scenario **MAY** drive a unit, component, integration, or end-to-end test, and this spec **MUST NOT** assume one tier for the core. Tier placement stays the tier model's call [R5] (lowest tier that gives confidence).
- End-to-end **MUST** be treated as the primary application (see *BDD on end-to-end tests*), but a consuming project **MAY** apply the discipline at any tier without adopting the E2E-specific requirements.
- Everything the reference profile ships (Gherkin syntax, feature-file layout, step-binding examples, the Cucumber family) is illustrative and **MAY** be replaced wholesale by a project on another stack, provided the binding core still holds.

### Collaborative discovery

- A consuming project **SHOULD** discover the examples that become scenarios **collaboratively before coding**, so a scenario encodes a shared understanding rather than a single author's after-the-fact guess [R6], [R7].
- It **SHOULD** use **Example Mapping** to structure that discovery: for a story, map its business **rules**, a concrete **example** per rule, and the open **questions** the conversation surfaces, so an under-specified or oversized story is exposed before code is written [R7].
- It **SHOULD** run the discovery as a **Three Amigos** conversation across the three perspectives (business / product, development, testing), because each perspective catches examples the others miss [R6], [R8].
- An open question raised during discovery **MUST** be recorded and resolved rather than silently encoded as an assumption in a scenario; an unresolved question means the behavior isn't yet understood.

### Scenario language

- A behavior **MUST** be expressed in the **Given-When-Then** structure: **Given** the starting context, **When** the triggering event, **Then** the expected observable outcome [R9]. Additional context or outcomes use **And** / **But**; this is the structural equivalent of Arrange-Act-Assert named by `spec/project/test-pyramid-foundation/` [R5].
- Each scenario **MUST** describe **exactly one behavior**. A scenario with more than one distinct **When** that triggers more than one behavior **MUST** be split.
- A scenario **MUST** be **declarative**, stating *what* the behavior is in domain terms, not *how* the user drives the interface. Imperative, UI-mechanical steps ("type X into the third field, click the blue button") belong in the step layer, never in the scenario text [R10].
- A shared precondition common to every scenario in a feature **SHOULD** be lifted into a **Background** rather than repeated, and a Background **MUST** contain only setup, never a **When** or a **Then**.
- A behavior exercised across a set of example rows (equivalence classes, boundary values) **SHOULD** use a **Scenario Outline** with an **Examples** table rather than copy-pasted near-identical scenarios; each row **MUST** exercise the same single behavior.
- Scenarios **SHOULD** carry **tags** for selection and traceability (see the derivation workflow), and a project **SHOULD** define its tag vocabulary rather than let tags accrete ad hoc.
- Each scenario and feature **MUST** have an **intention-revealing title** that names the behavior, not the steps; a title that merely restates the Given-When-Then is a smell.

### Ubiquitous language

- Scenarios **MUST** be written in the domain's **ubiquitous language**: the same terms the business, the requirements, and the code use for the same concepts, so a non-programmer stakeholder can read a scenario and confirm it [R11].
- A term used in a scenario **MUST NOT** drift from its meaning in the requirement it traces to; where the domain lacks an agreed term, discovery (above) **MUST** establish one rather than a scenario inventing a private synonym.

### Living documentation

- The scenario set **MUST** be usable as **living documentation**: the authoritative, executable description of what the system does, kept truthful because it runs against the system and fails when it drifts [R12].
- A scenario that's obsolete because the behavior changed **MUST** be updated or retired in step with the change, never left green-but-lying or disabled without a recorded reason; a permanently skipped scenario is documentation that no longer documents.
- Documentation prose that duplicates what a scenario already states **SHOULD** reference the scenario instead, so the executable example stays the single source of truth.

### Step-definition design

- A step definition **MUST** be **thin**: it translates one Gherkin step into an action against the system (or, at E2E, into a call on the page-object layer [R3]) and holds no business logic of its own.
- Step definitions **MUST** be **reused** across scenarios; the same domain step **MUST NOT** be re-implemented per feature. Shared setup and helper logic live in the step/support layer, not copied into each binding.
- A Gherkin step **MUST NOT** contain assertions; the **Then** step's *binding* performs the assertion, while the scenario text states the expected outcome in domain terms. Assertion logic **MUST NOT** leak into the scenario file.
- A step's binding **MUST** resolve selectors and low-level interaction only through the layer that owns them (`spec/project/e2e-test-automation/`'s page objects [R3], resolving `spec/frontend/testability-identifiers/`'s contract [R4] at E2E); a step **MUST NOT** name a raw selector inline.

### From test-case document to executable scenarios

- The derivation **MUST** consume an abstract **test-case document** (TC-IDs and their behaviors, as produced under `spec/project/test-case-derivation/` [R2]) as its input and **MUST NOT** re-derive the cases; this workflow encodes existing cases as scenarios, it doesn't invent them.
- The derivation **MUST** follow this ordered workflow:
  1. **MUST** group the test cases by the domain capability they exercise and map each capability to one **Feature**.
  2. **MUST** derive **one Scenario per distinct TC-level behavior**; a test case describing several behaviors becomes several scenarios, and near-identical cases over a data set **SHOULD** collapse into one **Scenario Outline** with one row per case.
  3. **MUST** translate each case's parts into Given-When-Then: its **precondition** becomes **Given**, its **action** becomes **When**, its **expected result** becomes **Then**, keeping every step declarative even when the source case lists UI mechanics.
  4. **MUST** tag each resulting scenario with its source **TC-ID** (for example `@TC-042`) so the requirement-to-scenario link is machine-checkable and bidirectional; a scenario without a resolvable TC-ID tag is untraceable and **MUST** be flagged.
  5. **SHOULD** lift preconditions shared by every scenario in a feature into a **Background**, and **SHOULD** carry the case's tier hint so the scenario lands at the tier the case chose [R1].
- The derivation **MUST** preserve the **TC-ID → scenario** traceability so coverage of the test-case document is auditable, extending the traceability chain that `spec/project/test-cycle-case-determination/` [R1] and `spec/project/e2e-test-automation/` [R3] already require.
- A test case that **MUST NOT** be normalized into a single declarative behavior (it's really several behaviors, or its expected outcome isn't observable) **MUST** be reported back rather than forced into a misshapen scenario; a case that resists the workflow isn't yet understood.

### BDD on end-to-end tests

- At the E2E tier, the BDD scenario layer **MUST** sit *above* the execution machinery: the scenario names intent in the ubiquitous language, its step binding delegates to the page-object layer owned by `spec/project/e2e-test-automation/` [R3], and that layer owns waits, screenshots, protocol, and selector resolution.
- A scenario at E2E **MUST NOT** absorb the responsibilities the execution spec owns: it **MUST NOT** encode waits, sleeps, screenshot calls, or selectors, and **MUST NOT** restate the page-object discipline. It relies on that spec through the step layer.
- E2E scenarios **MUST** stay lean and journey-focused, consistent with the over-populated-apex rule in `spec/project/e2e-test-automation/` [R3] and the tier model [R5]: a field-level check that a lower tier could verify **MUST NOT** be written as an E2E scenario just because BDD makes it readable.
- The scenario's **TC-ID** tag **MUST** compose with, not replace, the requirement traceability the execution spec already mandates, so a run is auditable from requirement through case to scenario to screenshot.

### Anti-patterns

- The following **MUST** be treated as defects and rejected in review:
  - **Imperative, UI-coupled scenarios**: steps that describe clicking, typing, and selectors instead of the behavior [R10].
  - **Assertions in the scenario file** or business logic in a step binding: the layers are inverted.
  - **Multi-behavior scenarios**: several unrelated **When/Then** pairs in one scenario, or a conjunction-heavy chain of **And** steps hiding distinct behaviors.
  - **Incidental detail**: data or steps irrelevant to the behavior under test, which obscure intent and cause false breakages.
  - **Scenario-per-method / testing internals**: scenarios mirroring implementation structure rather than user-observable behavior.
  - **Scenarios as scripts, not documentation**: titles that restate steps, no ubiquitous language, unreadable by a non-programmer stakeholder.
  - **Untraceable scenarios**: no resolvable TC-ID or requirement link, so coverage can't be audited.

## Reference profile (illustrative, non-normative)

This profile makes the tool-neutral core concrete with **Gherkin** and the **Cucumber family** (Cucumber-JVM, Cucumber.js, `pytest-bdd`, `behave`). It's illustrative: a project on another stack satisfies the core without it. The shipped `templates/` directory carries a worked example.

- **Feature files** (`*.feature`) hold Gherkin: a `Feature:`, an optional `Background:`, and `Scenario:` / `Scenario Outline:` blocks with `Given` / `When` / `Then` / `And` / `But` steps, tags on the line above (`@TC-042`), and an `Examples:` table for outlines [R9].
- **Step definitions** bind each step's text to code in the project's language and stay thin, delegating to the domain or, at E2E, to the page-object layer [R3].
- A worked feature file plus a matching step-definition skeleton (`pytest-bdd`, chosen to match the Python reference profile of `spec/project/e2e-test-automation/`) lives under `spec/project/behavior-driven-development/templates/`.

## Acceptance Criteria

- [ ] The binding core is stated tool-neutrally, with Gherkin and the Cucumber family confined to the illustrative reference profile
- [ ] The core is explicitly tier-neutral, with E2E named as the primary application in its own requirement group
- [ ] Collaborative discovery (Example Mapping rules/examples/questions, Three Amigos) is required as the front door
- [ ] The Given-When-Then scenario language is specified: one behavior per scenario, declarative not imperative, Background for shared setup, Scenario Outline for data sets, tags, intention-revealing titles
- [ ] Ubiquitous language and living-documentation requirements are present
- [ ] Step-definition principles are specified: thin steps, cross-scenario reuse, no assertions in Gherkin, selector resolution only through the owning layer
- [ ] The test-case-document to executable-scenario derivation is an ordered MUST/SHOULD workflow: one scenario per TC behavior, precondition/action/result to Given-When-Then, and a TC-ID scenario tag for machine-checkable traceability
- [ ] BDD-on-E2E requirements place the scenario layer above the execution layer and defer mechanics to `e2e-test-automation`
- [ ] The Non-Goals link all four neighbour specs (`test-cycle-case-determination`, `test-case-derivation`, `e2e-test-automation`, `testability-identifiers`) by responsibility
- [ ] The anti-pattern list names imperative scenarios, assertions in Gherkin, multi-behavior scenarios, incidental detail, testing internals, scripts-not-documentation, and untraceable scenarios
- [ ] EN and DE versions are structurally identical (same headings, requirement count, acceptance-criteria count) and the spec index lists the new slug

## References

- [R1] `spec/project/test-cycle-case-determination/`: owns when in the cycle examples are discovered and which design techniques apply; names Example Mapping / BDD as a SHOULD that this spec operationalizes
- [R2] `spec/project/test-case-derivation/`: derives the abstract test cases this spec consumes as input
- [R3] `spec/project/e2e-test-automation/`: owns the E2E execution mechanics a scenario's steps delegate to
- [R4] `spec/frontend/testability-identifiers/`: owns the stable selector contract a step ultimately resolves against
- [R5] `spec/project/test-pyramid-foundation/`: owns the tier taxonomy and coverage governance; names Given-When-Then as the structural equivalent of Arrange-Act-Assert
- [R6] Dan North, *Introducing BDD* (behavior-driven development, the ubiquitous-language and example origin): <https://dannorth.net/introducing-bdd/>
- [R7] Matt Wynne / Cucumber, *Example Mapping* (rules, examples, questions): <https://cucumber.io/docs/bdd/example-mapping/>
- [R8] George Dinwiddie / Cucumber, *The Three Amigos* (business, development, testing perspectives): <https://cucumber.io/docs/bdd/who-does-what/>
- [R9] Cucumber, *Gherkin Reference* (Given-When-Then, Background, Scenario Outline, tags): <https://cucumber.io/docs/gherkin/reference/>
- [R10] Cucumber, *Writing better Gherkin* (declarative over imperative scenarios): <https://cucumber.io/docs/bdd/better-gherkin/>
- [R11] Eric Evans / Martin Fowler, *Ubiquitous Language*: <https://martinfowler.com/bliki/UbiquitousLanguage.html>
- [R12] Gojko Adzic, *Specification by Example* (living documentation from executable examples): <https://www.manning.com/books/specification-by-example>

## Open Questions

- Should the TC-ID scenario tag be a hard gate at review time (a scenario without a resolvable TC-ID fails), or a strong SHOULD, given some exploratory scenarios precede a formal test case?
- Should the reference profile ship more than one Cucumber-family skeleton (for example a Cucumber.js binding alongside `pytest-bdd`), or does one worked example suffice to keep the profile illustrative?
- Does the ubiquitous-language requirement warrant a project-level glossary artefact, or is consistency-within-the-scenario-set enough without mandating a separate document?
