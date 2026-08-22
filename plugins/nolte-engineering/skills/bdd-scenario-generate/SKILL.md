---
name: bdd-scenario-generate
description: Generates executable BDD scenarios from an abstract test-case document (TC-IDs plus behaviors) per spec/project/behavior-driven-development/, emitting English Gherkin `.feature` files and thin `pytest-bdd` step-definition skeletons that honor the page-object decoupling contract of spec/project/bdd-page-object-integration/ (thin steps delegate down, assertions only in the `Then` binding). Groups cases into Features, one Scenario per TC-level behavior, precondition/action/result mapped to Given/When/Then, `@TC-<id>` tags for traceability. Runs an advisory `lektorat-apply` audit over the scenario wording and emits a work-package list for any page-object or app change instead of touching it. Invoke to turn a test-case document into runnable BDD/Gherkin scenarios; also German. Don't derive the cases (test-case-extractor), scaffold a full E2E suite (e2e-test-generator), or audit the scenarios (bdd-scenario-reviewer). Supports resume.
tags: [quality-gate, scaffolding]
phase: build
summary: "Generates executable BDD scenarios and thin pytest-bdd step skeletons from an abstract test-case document, honoring the Gherkin discipline and the page-object decoupling contract."
summary_de: "Erzeugt ausführbare BDD-Szenarien und schlanke pytest-bdd-Step-Gerüste aus einem abstrakten Testfall-Dokument, gemäß der Gherkin-Disziplin und dem Page-Object-Entkopplungsvertrag."
use_when:
  - "you have an abstract test-case document (TC-IDs + behaviors) and want it turned into runnable BDD scenarios"
  - "you want English Gherkin .feature files plus thin step-definition skeletons for a feature"
  - "you want TC-ID-traceable scenarios that honor the page-object decoupling contract"
dont_use_when:
  - situation: "you need to derive the abstract test cases from a requirement document first"
    alternative: test-case-extractor
  - situation: "you want a full runnable E2E suite (page objects, waits, screenshots) scaffolded"
    alternative: e2e-test-generator
  - situation: "you want to audit or grade an existing BDD scenario set for conformance"
    alternative: bdd-scenario-reviewer
see_also:
  - test-case-extractor
  - e2e-test-generator
  - fullstack-developer
  - bdd-scenario-reviewer
resumable: true
---

# BDD Scenario Generate

Turn an abstract **test-case document** into **executable BDD scenarios**: English Gherkin `.feature` files plus thin `pytest-bdd` step-definition skeletons, with end-to-end `@TC-<id>` traceability. This skill applies the ordered derivation workflow of `spec/project/behavior-driven-development/` and emits step glue that honors the decoupling contract of `spec/project/bdd-page-object-integration/`. It **consumes** cases; it never re-derives them, and it never touches page objects or application code.

Implements `spec/project/behavior-driven-development/` §"From test-case document to executable scenarios" and `spec/project/bdd-page-object-integration/` §"The step-as-glue contract". Those specs own the discipline; this skill binds it to the on-disk procedure and owns the emission, the advisory wording review, and the work-package handoff. When this skill and either spec disagree, the spec wins and this skill needs the update.

## German trigger phrases

This skill also triggers on equivalent German-language requests, including:

- "BDD-Szenarien generieren" / "Gherkin-Szenarien aus den Testfällen erzeugen"
- "Feature-Dateien aus dem Testfall-Dokument ableiten"
- "Given-When-Then-Szenarien mit Step-Gerüst erzeugen"

## User-language policy

Detect the user's language from their message and respond in it. The emitted `.feature` files and their step docstrings are **English-only** regardless of the consuming repository's language (see Hard rules); prose around the run — the report, the work-package list, the confirmation — is localised.

## Why this is a skill, not an agent

- **Dispatches a sub-skill (decisive):** the advisory wording review dispatches `lektorat-apply` in `audit` mode over the extracted scenario prose. An agent **must not** call the `Skill` tool (`spec/claude/skill-vs-agent/`), so the surface that runs the lektor pass and maps its findings back has to be a skill.
- **Mid-flow interactivity:** mapping advisory lektor findings back onto `.feature` lines, and handing the operator a work-package list to route to a specialist, are operator-gated decisions that favour the skill side.
- **Persistent, multi-capability orchestration:** the run writes `.feature` files, step skeletons, an extraction doc, and a work-package list across named phase boundaries, and coordinates the generation core with the lektor sub-skill.
- **Counter-dimension (favours an agent):** the pure generation core — test-case document in, scenarios plus step skeletons out — is self-contained input→output, exactly the shape of the sibling `e2e-test-generator` agent, and could be delegated to a future generator agent under the hybrid pattern. That pull is real and honoured, but the sub-skill dispatch and the operator-routed handoff keep the orchestrating surface a skill.

## Scope and delimitation

This skill owns the **scenario/specification layer** only. Bounded against its neighbours by responsibility:

- **Input — `test-case-derivation` / the `test-case-extractor` agent.** They derive the abstract, framework-agnostic test cases (TC-IDs + behaviors). This skill **consumes** that document and **must not** re-derive, invent, or extend the cases; a gap in the cases is reported back to the case owner, not patched here.
- **Execution — `e2e-test-automation` / `e2e-test-generator`.** They own the execution machinery a scenario runs on: page objects, condition-based waits, screenshots, protocol, selector resolution. This skill sits *above* that layer; a step delegates down into it and never restates it. Scaffolding a full runnable suite is `e2e-test-generator`'s job.
- **Page-object wiring — `bdd-page-object-integration`.** This skill emits step skeletons that *call* page objects; it never writes or modifies a page object, a selector, or app code. A needed page-model change becomes a **work package** for a specialist.
- **Review — `bdd-scenario-reviewer` (the read-only reviewer agent).** The generator **writes**; that reviewer **audits** an existing scenario set (declarative, one-behavior-per-scenario, traceable, decoupled). This skill does not review, and does not author that agent.

## Inputs

- **Test-case document**: the abstract cases (TC-IDs and their precondition / action / expected-result behaviors) as produced under `spec/project/test-case-derivation/`. Required — without it, stop and route the caller to `test-case-extractor`.
- **Target BDD tree**: the project's `.feature` and step-definition directories. Default to the reference-profile layout (`features/` + `step_defs/`) when the project declares none. When the harness or target tree does not exist, **stop and report** rather than inventing test infrastructure (mirrors `e2e-test-generator`'s write precondition).
- **Reference profile**: Gherkin + `pytest-bdd` by default, composing with the Selenium + `pytest` profile of `spec/project/e2e-test-automation/`. The core stays tool-neutral; a project on another BDD stack swaps the profile and the binding discipline still holds.
- **Tier hint** (optional): the tier a case chose, carried onto the scenario so it lands at the right tier per `spec/project/test-cycle-case-determination/`.

## Operations

### 1. `generate` (default)

An ordered workflow. Steps 1–5 apply the `behavior-driven-development` derivation; steps 6–7 emit; step 8 is the advisory review; steps 9–10 hand off and report.

1. **Load and validate the test-case document.** Parse the TC-IDs and their precondition/action/expected-result parts. Do **not** re-derive or invent cases. A case whose expected outcome is not observable, or that is really several behaviors, is set aside for step 10.
2. **Group by domain capability → one `Feature`.** Map each domain capability the cases exercise to exactly one Feature file, titled in the domain's ubiquitous language.
3. **One `Scenario` per distinct TC-level behavior.** A case describing several behaviors becomes several scenarios; near-identical cases over a data set collapse into one **`Scenario Outline`** with an **`Examples`** table, one row per case, each row exercising the same single behavior.
4. **Map parts to Given-When-Then.** Precondition → `Given`, action → `When`, expected result → `Then`, keeping every step **declarative** in domain terms even when the source case lists UI mechanics. Additional context/outcomes use `And` / `But`. Each scenario describes exactly one behavior with an intention-revealing title.
5. **Tag and factor.** Tag every scenario with its source `@TC-<id>` so the requirement-to-scenario link is machine-checkable; a scenario with no resolvable TC-ID is flagged, never shipped silently. Lift preconditions shared by every scenario in a Feature into a **`Background`** (setup only — never a `When`/`Then`); carry the tier hint.
6. **Emit the `.feature` files** in English Gherkin. No assertions, no selectors, no waits, no screenshot calls in the scenario text — those belong to the step/page-object layers.
7. **Emit thin step-definition skeletons** (`pytest-bdd` reference profile) honoring `bdd-page-object-integration`:
   - Each step binding is **thin**: it translates one Gherkin step into one or a few calls on a page object and holds no business logic.
   - **Assertions live only in the `Then` binding**, comparing page-object-returned state against the scenario's expected outcome — never in the `.feature`, never in a page object. A `Then` binding is falsifiable per `spec/project/test-falsifiability/`: never satisfiable by a reader's empty default (T2/T3), never solely a negative without a positive assertion on the effect.
   - Page objects are received by **dependency injection** (a `pytest` fixture); the skeleton **references** page-object methods and a scenario-scoped `context` fixture but **does not define, import, or modify** any page object. A referenced method that does not yet exist is a **work package** (step 9), not something this skill writes.
   - No raw driver call, selector, or wait appears in a step; every UI interaction goes through a page object.
8. **Advisory wording review.** Extract the natural-language lines (Feature/Scenario titles and Given-When-Then step text) into a temporary Markdown document under `.audits/bdd-scenario-generate/<YYYY-MM-DD>/scenario-prose.md`, dispatch `lektorat-apply` in `audit` mode over it, and map each finding back to its `.feature` file and line. This is **advisory**: findings **should** be resolved (clearer titles, ubiquitous-language drift, readability), but a residual finding does **not** hard-block generation. Surface the mapped findings in the report.
9. **Emit the work-package list.** For any change outside this skill's scope — a new/changed page-object method, a missing selector hook, an application change a scenario implies — emit a structured work package (target specialist, touched files, goal) for the **operator to route**. This skill **must not** dispatch the specialist itself.
10. **Report back the non-normalizable cases.** Any test case that could not become a single declarative, observable behavior is reported explicitly (with the reason) rather than forced into a misshapen scenario — a case that resists the workflow isn't yet understood and goes back to the case owner.

## Report shape

```text
# BDD Scenario Generation

Source: <test-case document path>, <n> cases
Target: <features dir> + <step_defs dir>  (profile: Gherkin + pytest-bdd)
Git revision: <sha>

## Emitted
- Features: <n> (<file list>)
- Scenarios: <n> (outlines: <n>, background lifts: <n>)
- Step skeletons: <n> bindings across <n> files
- TC-ID coverage: <mapped>/<total> cases  (untraceable: <list or none>)

## Advisory wording review (lektorat-apply, audit)
- <feature:line> — <dimension>: <finding> (advisory)
- ... (residual findings do not block; see .audits/bdd-scenario-generate/<date>/)

## Work packages (for the operator to route — not dispatched)
- [<specialist>] <goal> — files: <list>

## Reported back (not normalized)
- <TC-id>: <reason it is not a single observable behavior>
```

## Work-package shape

Each work package the operator routes carries exactly:

- **specialist**: the target capability (`fullstack-developer` for a page-object/app change, `e2e-test-generator` for scaffolding the surrounding suite, `test-case-extractor` for a case-document gap).
- **files**: the paths the specialist is expected to touch (a page-object module, a template, the app surface that needs a selector hook).
- **goal**: one sentence naming the behavior to enable (for example "add `LoginPage.submit_with(username, password)` so the `@TC-042` `When` step can delegate").

## Gotchas

- **The generator writes scenarios and step glue; it never writes a page object.** A step skeleton legitimately references a page-object method that does not exist yet — that reference becomes a work package, not an edit. Writing the method here would fuse the layers `bdd-page-object-integration` keeps apart.
- **Assertions never leave the `Then` binding.** The `.feature` states the expected outcome in domain terms; the assertion is code in the `Then` step's binding. An assertion in the Gherkin text, or in a page object, is a layer inversion the spec rejects.
- **`.feature` files stay English even in a German repo.** The scenario language is fixed English (Hard rules); the operator dialogue and report are localised. Do not translate `Given`/`When`/`Then` or the scenario prose to match the repo's docs language.
- **One behavior per scenario.** A case with two distinct `When`s that trigger two behaviors becomes two scenarios, not a conjunction-heavy chain of `And` steps hiding distinct behaviors.
- **A near-identical data set is a `Scenario Outline`, not copy-paste.** Equivalence classes and boundary values collapse into one outline with one `Examples` row per case; each row must exercise the same single behavior.
- **The lektor review is advisory, not a gate.** A residual `lektorat-apply` finding on scenario wording is surfaced for the operator but never blocks emission. Do not hard-fail generation on a readability or naturalness finding.
- **An untraceable scenario is a defect, not a shrug.** Every scenario carries a resolvable `@TC-<id>`. A behavior with no backing case is reported back to the case owner, not tagged with an invented ID.
- **Do not scaffold execution infrastructure.** When the target BDD tree or harness is absent, stop and report; standing up `features/`, `conftest.py`, or the driver wiring is `e2e-test-generator`'s job, dispatched as a work package.

## Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/bdd-scenario-generate/<run-id>.yml` after each named phase boundary (grouping, scenario-emit, step-skeleton-emit, lektor-review, work-package-emit). On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope (`schema_version`, `run_id`, `inputs`, `phase`, `decisions[]`, `status`, ...) and the fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

## Hard rules

- **Never** re-derive, invent, or extend the test cases; this skill consumes an existing test-case document and reports a gap back to the case owner (`test-case-extractor`).
- **Never** write, modify, or import a page object, a selector, or application code. A needed page-model change is emitted as a work package for a specialist; the step skeleton only *references* the page-object method.
- **Never** dispatch the specialist named in a work package (`fullstack-developer`, `e2e-test-generator`); the operator routes it. This skill dispatches only `lektorat-apply` for the advisory review.
- **Always** emit `.feature` files in English regardless of the consuming repository's language; step docstrings should also be English. The operator dialogue and report are localised.
- **Never** place an assertion in a `.feature` file or in a page object; the assertion lives only in the `Then` step's binding, and no selector/wait/driver call appears in a step.
- **Always** give every scenario exactly one behavior, a declarative (non-imperative) body, an intention-revealing title, and a resolvable `@TC-<id>` tag; flag any scenario that cannot be traced.
- **Always** treat the `lektorat-apply` wording review as advisory: surface findings, but never hard-block generation on a residual one.
- **Always** report back any test case that cannot be normalized into a single declarative, observable behavior rather than forcing a misshapen scenario.
- When `spec/project/behavior-driven-development/` or `spec/project/bdd-page-object-integration/` and this skill disagree, the spec wins; this skill needs the update.
