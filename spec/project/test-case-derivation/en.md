# Test-Case Derivation from Requirements

Status: draft

## Context

A requirement document describes what a system must do, but it doesn't verify itself. Turning a requirement into a set of executable test cases is manual, error-prone work that drifts: a tester reads the spec, imagines the scenarios, and writes them down in whatever shape is at hand—so coverage gaps go unnoticed, traceability back to the requirement is lost, and two requirements get inconsistent test structures. The valuable, reusable part of that work is **deriving black-box test cases from the user-observable behaviour a requirement describes**, a discipline (IREB/ISTQB) that's independent of any test-automation framework. The throwaway part is the project-specific glue: which automation library runs the cases, which directory holds them, which domain vocabulary they use.

This spec governs that reusable derivation, operationalised by the `test-case-extractor` agent (`distribution: plugin`). It's the generalised core of a project-local extractor that hard-coded one app's agricultural domain, its German-only requirement format, its React/MUI assumption, and its `spec/test-cases/` path. The portfolio form derives framework-agnostic, structured, traceable test-case documents from any requirement document, in the source document's own language, for whatever user-facing interface the project exposes.

This is deliberately the only test-related capability extracted to the plugin: the project-local predecessors that generate or review automation code (Selenium/Playwright/Cypress page objects), run test suites and fix failures, or audit a project's specific test-tier shape are too stack-coupled or already covered by `quality-gate`, and stay project-local.

Readers: agent authors maintaining the extractor; QA engineers and developers who derive test cases after a requirement is specified; reviewers verifying coverage and traceability.

## Goals

- Systematically derive test cases from a requirement document, covering happy paths, negative cases, validation, state transitions, navigation, and error states the user can observe
- Keep every test case written from the **user-observable-behaviour** perspective—no internal implementation detail (API calls, status codes, queries) in the steps
- Produce structured, self-contained, retrieval-friendly test-case documents with full traceability back to the source requirement section
- Stay framework-agnostic: the derived cases are executable by a manual tester or any automation framework, because they describe behaviour, not framework calls
- Adapt to the project's language, output location, and user-facing interface type rather than assuming one stack

## Non-Goals

- Generating test-automation **code** (Selenium/Playwright/Cypress page objects, fixtures)—stack-specific, stays project-local
- Running test suites, classifying failures, or fixing test code—owned by `spec/project/quality-gate/` and project-local runners
- Auditing a project's test-tier distribution (the "test pyramid" shape)—a separate, opinion-bearing concern that stays project-local
- Authoring or editing the requirement documents themselves—the agent reads requirements, it doesn't write them
- Visual review of a test run's screenshots or logs against a spec—a separate, stack-coupled concern
- Batch orchestration across many requirements (selection and commit policy) is a consuming-project skill that dispatches this agent per requirement (the skill-orchestrates/agent-executes hybrid), not a responsibility of this agent

## Requirements

### Inputs and discovery

- **MUST** accept one or more requirement documents as input and read each fully before deriving cases; the agent **MUST NOT** hard-code one project's requirement path or ID scheme, and **MUST** report which documents it processed
- **MUST** work in the **source document's language**: test cases are written in the language the requirement is written in, with domain terms preserved verbatim and an optional code-identifier gloss in parentheses for traceability
- **MAY** consult the project's user-facing surface (route definitions, page inventory, CLI command list, public API surface) to ground the cases in the real interface, when that surface is discoverable; absent it, the agent derives from the requirement text alone and states that assumption
- **MUST** determine the project's user-facing interface type (browser UI, CLI, API client, mobile) so the test steps describe actions in that surface; when it can't be determined, default to the requirement's described surface and state the assumption

### Derivation discipline

- **MUST** decompose each requirement into its functional requirements, acceptance criteria, user-facing state changes, input/validation rules, and observable error states before deriving cases
- **MUST** write every test step as a **user-observable action** (navigate, click, type, select, invoke a command) and every expected result as a **user-observable outcome** (a message, a visible state, a returned value); the agent **MUST NOT** describe internal implementation (HTTP status codes, database state, function calls) in steps or expected results
- **MUST**, when a requirement's rule surfaces only as a behaviour (a disabled control, a validation message, a missing option), describe the behaviour, not the underlying rule
- **MUST** cover, for each must-level requirement, at least one happy-path case and at least one negative/edge case
- **SHOULD** apply the standard derivation techniques—user-journey, input/boundary, state-transition, navigation, visual-feedback, and error-guessing—and name the technique a case exercises in its category field

### Output contract

- **MUST** write structured test-case documents to a single configurable output directory rather than a hard-coded path, defaulting to `tests/cases/` in the consuming repository, one document per source requirement, named for the requirement it traces to
- **MUST** give each document a YAML frontmatter block (at least: source requirement id, title, test-case count, covered areas, generated date) and each test case the structure: title, requirement reference, priority, category, preconditions, steps, expected results, postconditions, tags; this structure is portfolio-fixed—only language, output directory, and interface-surface vocabulary adapt per project
- **MUST** end each document with a coverage summary mapping requirement sections to the cases that cover them, and **MUST** explicitly list requirement sections from which no case could be derived (open requirements) rather than silently omitting them
- **MUST** keep each test case self-contained and retrieval-friendly (a one-line intent summary, prominent tags and identifiers, consistent domain vocabulary, explicit cross-references to related cases) so it survives ingestion into a retrieval system as an independent chunk
- **MUST** regenerate a requirement's document deterministically: re-running on the same requirement yields the same cases (modulo the generated timestamp); the agent overwrites its own prior output and doesn't merge with hand-edits silently
- **MUST** restrict writes to test-case documents under the configured output directory; the agent **MUST NOT** edit source code, the requirement documents, or any other file

## Acceptance Criteria

- [ ] Running the agent on a requirement document writes one structured test-case document under the configured output directory (default `tests/cases/`), named for the source requirement
- [ ] Each document carries YAML frontmatter with at least source-requirement id, title, case count, covered areas, and generated date
- [ ] Each test case has the full structure (title, requirement reference, priority, category, preconditions, steps, expected results, postconditions, tags)
- [ ] Every test step is a user-observable action and every expected result is a user-observable outcome; no step or expected result names an HTTP code, a database query, or an internal function call
- [ ] Each must-level requirement has at least one happy-path and one negative case
- [ ] The document ends with a coverage table and an explicit list of requirement sections with no derivable case
- [ ] Test cases are written in the source document's language, with domain terms preserved
- [ ] Re-running on the same requirement reproduces the same cases apart from the generated timestamp
- [ ] The agent writes only test-case documents under the configured directory and edits no source or requirement files
- [ ] The agent cites this spec in its body or `description`, and its `description` delimits it from automation-code generation, test running, and test-tier auditing

## References

- [R1] Agent authoring rules this agent conforms to: `spec/claude/agent-management/`
- [R2] Skill-vs-agent decision rule and rationale-section requirement: `spec/claude/skill-vs-agent/`
- [R3] Test execution / failure handling (delimited against this spec): `spec/project/quality-gate/`
- [R4] ISTQB test-design techniques (background methodology): <https://www.istqb.org/>

## Open Questions

- Should the agent emit a machine-readable traceability index (requirement → cases) alongside the human-readable documents, for downstream coverage tooling?
