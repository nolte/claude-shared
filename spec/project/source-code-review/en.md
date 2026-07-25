# Holistic Source Code Review

Status: draft

## Context

The portfolio's existing review surfaces are deliberately narrow: `code-security-audit` covers OWASP security only, the test-tier reviewers check one tier's checklist each, `quality-gate` runs mechanical tooling without judgment, and the built-in diff review sees only the current branch's changes and persists nothing. None of them answers the question a senior engineer answers in a real code review: is this code correct, maintainable, idiomatic, free of duplicated domain knowledge, and is its test code held to the same standard as its production code?

This spec governs that holistic review. It's split into two layers that never mix: a **language-agnostic core** defining the review dimensions, the scope model, and the report contract, and one **language profile** per programming language defining the idioms, pitfalls, tooling baseline, and test-framework conventions the reviewer applies. Python is the first reference profile. The review is operationalised by the `source-code-review` skill, which detects the target language and dispatches the matching language reviewer agent (`python-code-reviewer` for Python); the report it persists is decomposed into disjoint, specialist-routed work packages so remediation can run in parallel.

Readers: authors and maintainers of the review skill and the language reviewer agents; reviewers who consume the report; developers who run the review before a release or after a feature lands.

## Goals

- Define one holistic senior-engineer source-code review covering production **and** test code with equal weight
- Separate the language-agnostic review dimensions from language-specific particulars, so new language profiles extend the spec without touching the core
- Make **domain-knowledge duplication** (the same business rule, constant, or validation implemented more than once) a first-class review dimension, distinct from textual clone detection
- Start where mechanical tooling ends: the review never restates what a linter, formatter, or type checker already reports
- Produce a persisted, severity-classified report whose findings decompose into **disjoint work packages, each routed to a specialist**, so remediation is parallel-dispatchable
- Draw explicit boundaries to the security audit, the dependency audit, the observability audit, the test-tier reviewers, and the quality gate

## Non-Goals

- Deep OWASP security auditing—owned by `spec/project/code-security-audit/`; this review only flags obvious security smells and routes them there
- CVE / dependency-vulnerability scanning—owned by `spec/project/dependency-audit/`
- Observability-contract auditing—owned by `spec/project/monitoring-observability/`; this review only flags obvious logging smells and routes them there
- Test-tier conformance in depth (unit / integration / component / contract / E2E checklists)—owned by the `spec/project/test-tier-*/` specs and their reviewers; this review covers cross-cutting test-code quality and routes tier-specific findings out
- Running or replacing mechanical tooling (`quality-gate` owns lint / typecheck / test execution)
- Applying fixes: the review finds, classifies, and routes; specialists remediate

## Requirements

### Two-layer review model

- **MUST** keep the core dimensions (this spec's §Core review dimensions) language-agnostic: no rule in the core names a language construct, library, or tool
- **MUST** define everything language-specific in a named language profile (§Language profiles); the Python reference profile below is the first
- **MUST** review against exactly one profile per dispatched reviewer; a polyglot repository gets one reviewer dispatch per detected language, never one blended review
- A language without a profile in this spec **MUST** be reported as unsupported rather than reviewed ad hoc; the review states which profile it applied

### Scope model

- **MUST** treat production code and test code as **equal-priority review subjects**: test code is long-lived engineering code, not an annex; every finding carries a `production` or `test` marker
- **MUST** default to the whole source tree (production plus test roots) and accept an explicit narrower target (a package, module set, or directory) from the caller; the report states the reviewed scope either way
- **MUST** discover source roots and the test layout from the repository itself (build metadata, project configuration) rather than assuming one layout

### Tooling-first rule

- **MUST NOT** report a finding the project's configured mechanical tooling (linter, formatter, type checker) already reports or would fix automatically; the review's value begins where tooling judgment ends
- **MUST**, when the project lacks a tooling baseline the language profile names as standard, raise exactly **one** finding recommending the baseline's adoption instead of hand-reporting the individual mechanical violations that tooling would catch
- **SHOULD** note where a tooling configuration materially weakens the baseline (broad ignore lists, disabled strictness) as a single configuration finding

### Core review dimensions

The reviewer **MUST** assess every in-scope file against the following dimensions and tag each finding with its dimension ID. The catalog is closed at rule level; extending it requires a spec change.

- **D1—Correctness and robustness.** Logic errors, unhandled edge cases (empty, boundary, overflow, encoding), missing error handling on fallible operations, silently swallowed or suppressed errors (a failure signal caught, discarded, and neither handled, propagated, nor logged), input validation at trust boundaries, resource leaks, race conditions and shared mutable state, off-by-one and ordering assumptions.
- **D2—Readability and maintainability.** Intention-revealing naming, function and module size, nesting depth and cognitive complexity, dead code, commented-out code, misleading or redundant comments, magic values that deserve a named constant.
- **D3—Design and architecture.** Separation of concerns, layering violations, coupling and cohesion, leaky abstractions, over-engineering and speculative generality (YAGNI), god objects/modules, misplaced responsibility, and violation of the project's own declared architecture.
- **D4—Domain-knowledge duplication.** The same business rule, domain constant, validation, calculation, or mapping implemented in more than one place: **semantic duplication, not textual similarity**. Two structurally different functions encoding the same domain decision are a finding; two textually similar but semantically independent blocks aren't. Each finding names every duplicate site and proposes the single-source-of-truth location. Boilerplate the language forces and deliberate decoupling across bounded contexts aren't findings; the rule of three applies to speculative extraction.
- **D5—Idiomatic usage.** Conformance to the language profile's idiom catalog and known-pitfall list, and to the repository's own established conventions; the repository's conventions win over the reviewer's preferences when both are defensible.
- **D6—Test-code quality.** Cross-cutting test health independent of tier: tests assert observable behaviour (not implementation detail), each test states its intent, no logic-bearing tests (conditionals/loops computing the expectation), no assertion-free or always-green tests, no over-mocking that couples the test to internals, no hidden inter-test dependencies or shared mutable fixtures, no duplicated setup that a fixture should own, deterministic execution (no real time, network, or sleep-based waiting), and test data that states only what matters to the case. Coverage gaps for changed or critical behaviour are reported as findings; tier-conformance detail routes to the tier reviewers.
- **D7—Performance and resource efficiency.** Accidental algorithmic complexity (quadratic membership scans, N+1 request or query patterns), unbounded growth (caches, accumulators, unclosed resources), work inside hot loops that belongs outside, blocking calls on asynchronous paths, and premature optimisation that costs readability without a measured need.
- **D8—API contracts and documentation.** Public-surface clarity: coherent signatures, documented behaviour and error contracts on public entry points, honest naming of side effects, backward-compatibility hazards on published interfaces, and documentation that matches what the code does. In a repository that publishes an OpenAPI document, conformance of that document is owned by `spec/project/api-documentation/` and routes there.
- **D9—Dependency and boundary hygiene.** Rebuilt standard-library or established-dependency functionality, unnecessary new dependencies for trivial needs, vendored copies of upstream code, and business logic bleeding into framework glue or vice versa. CVE status is out of scope (dependency audit).
- **D10—Cross-cutting floors (route-out).** Obvious security smells (string-built queries, hard-coded secrets, unsafe loading of serialized data) and obvious observability smells (debug prints, sensitive data in logs) are **flagged with a routing note** to the owning audit—never investigated in depth here. A floor finding's remediation is "dispatch the owning audit," not a described fix.

### Language profiles

A **surface extension** may add dimensions on top of this core where a review subject carries concerns no language profile can express. `spec/frontend/source-code-review/` is the first: for browser-rendered code it overlays frontend dimensions (F1–F11) and a framework-profile axis onto D1–D10. An extension inherits this spec's tooling-first rule, severity vocabulary, report contract, and reviewer contract unchanged, never restates a core rule, and tags each finding with exactly one dimension ID.

Every language profile **MUST** define, and a reviewer applies as one unit:

- **Tooling baseline:** the linter / formatter / type-checker set the tooling-first rule defers to, and what "standard strictness" means
- **Idiom catalog:** the constructs idiomatic code uses and the non-idiomatic patterns to flag (D5)
- **Known-pitfall list:** language-specific defect patterns reviewed under D1
- **Typing discipline:** what the profile expects on public and internal surfaces
- **Test-framework profile:** the idiomatic test stack and its D6-relevant conventions
- **Performance idioms:** the profile-specific patterns reviewed under D7

### Python reference profile

- **Tooling baseline:** `ruff` (lint + format) and a strict type checker (`mypy` or `pyright`) on production code, `pytest` as the test runner. Style, import order, formatting, and mechanically detectable errors belong to the tooling—the reviewer defers per the tooling-first rule.
- **Idiom catalog (D5):** context managers for every owned resource; `pathlib` over string paths; f-strings; comprehensions and generator expressions where they stay readable, loops where they don't; `dataclasses` (or the project's model library, for example `pydantic`) over bare dictionaries and tuples for structured data; `enum` over magic strings; unpacking and keyword-only arguments where they clarify call sites; EAFP over LBYL where the exception path is genuinely exceptional; module-level `__all__` on public modules; absolute imports; no wildcard imports; no side effects at import time.
- **Known-pitfall list (D1):** mutable default arguments; late-binding closures in loops; bare `except:` and silently swallowed exceptions; `is` comparisons against non-singletons; shadowing built-in names; circular imports; module-global mutable state; truthiness traps on emptiness checks where `None` and "empty" differ; float equality; naive-vs-aware `datetime` mixing; forgotten `await`; blocking calls (file/network/`time.sleep`) inside an event loop.
- **Typing discipline:** public functions, methods, and `dataclass` fields are annotated; `Optional` is explicit and narrowed before use; `Any` isn't used to silence the checker; structural dependencies are typed as `Protocol` rather than concrete classes where the seam matters; `TypedDict` or a `dataclass` replaces a dictionary of unknown shape on any boundary that crosses a module.
- **Exception and error handling:** exceptions are specific types, not `Exception` catch-alls; re-raises chain with `raise … from`; a package with a public error contract defines its own exception hierarchy; exceptions aren't used for expected control flow on hot paths; error messages carry the failing value, not just the fact of failure.
- **Logging:** the `logging` module (or the project's structured logger) with module-level loggers—never `print` in production paths; lazy interpolation (`logger.info("x=%s", x)`) over eager f-strings in log calls; log levels match severity semantics.
- **Test-framework profile (D6, pytest):** fixtures over `setUp`/xUnit inheritance; `parametrize` over copy-pasted cases; `tmp_path`, `monkeypatch`, `capsys` over homegrown equivalents; `pytest.raises(..., match=...)` for error cases; mocking at owned boundaries only (patch where the name is looked up); no mixing of `unittest` style into a pytest suite unless the project already standardised on it; deterministic clocks (freezing) over `sleep`; test names state behaviour, not method names.
- **Performance idioms (D7):** `str.join` over concatenation in loops; set/dict membership over list scans; generators for streaming over materialised lists; `functools.lru_cache` only with bounded, immutable inputs; batch I/O over per-item round trips.

### Report contract

- **MUST** classify every finding with the portfolio-wide severity vocabulary from `spec/claude/review-plan/` §Severity scale (Critical / Warning / Suggestion / Info, verbatim Title Case)—never a P0–P3 or high/medium/low scale
- **MUST** apply a severity floor to D1 error-handling findings: a finding that reports a silently swallowed or suppressed error, or missing error handling on a fallible operation, is classified **Critical** when confirmed and at least **Warning** when suspected—never Suggestion or Info—so it always enters §Work packages; absent or swallowed error handling is a no-go, not a style preference
- **MUST** attribute every finding with file:line, its dimension ID (D1–D10), its `production` or `test` marker, and whether it's confirmed or suspected; an uncertain finding is reported as suspected, never silently dropped
- **MUST** lead with an overall assessment: reviewed scope (roots, globs, language profile, commit), the tooling baseline found, and a per-dimension finding count
- **MUST** end with a **§Work packages** section that decomposes all Critical and Warning findings into work packages where **no two packages touch the same file**, so specialists can remediate concurrently without merge conflicts; each package carries its finding IDs, its file set, a one-line goal, and a **routing target** (the specialist skill or agent that owns the remediation—production-code fixes to the implementing engineer role, tier-conformance findings to the owning tier reviewer, D10 floors to the owning audit)
- **MUST** declare any ordering dependency between packages explicitly; packages without a declared dependency are parallel-safe by contract
- **MUST**, when persisted by the calling skill, live at `.audits/source-code-review/<target-slug>.md` per `spec/claude/review-plan/` §File location and naming; a re-run overwrites the canonical file
- **SHOULD** keep Suggestion and Info findings out of the work packages (they're listed, not dispatched)

### Reviewer contract

- **MUST** be strictly read-only: the language reviewer agent declares only read and search tools, applies no fixes, and inserts no suppression comments; the report is the single output
- **MUST** cite this spec in the reviewer agent's and the skill's body or `description`
- **MUST** route the operator's remediation through the report's work packages (directly or via an implementation plan grounded in the report), never through ad-hoc fixing inside the review flow

## Acceptance Criteria

- [ ] The reviewer agent declares only `Read`, `Grep`, `Glob`, applies no edits, and returns a report classified with the review-plan severity vocabulary
- [ ] Every finding carries file:line, a D1–D10 dimension ID, a `production`/`test` marker, and a confirmed/suspected flag
- [ ] A repository with `ruff`/`mypy` configured yields no finding that duplicates what those tools report; a repository without them yields exactly one baseline-adoption finding instead of mechanical single findings
- [ ] The same domain rule implemented in two places is reported once under D4, naming both sites and a single-source-of-truth proposal; textually similar but semantically independent code isn't flagged
- [ ] Test files are reviewed with the same rigour as production files, and D6 findings (logic-bearing tests, over-mocking, non-determinism, inter-test coupling) appear with the `test` marker
- [ ] The report's §Work packages contain disjoint file sets, each with a routing target; undeclared-dependency packages are parallel-dispatchable
- [ ] A silently swallowed error or missing error handling on a fallible operation is reported under D1 at severity Critical when confirmed (at least Warning when suspected) and appears in §Work packages; no such finding is filed as Suggestion or Info
- [ ] A finding covered by a narrower owning audit (security, dependency, observability, test tier) appears only as a routed D10/route-out entry, not as a deep finding
- [ ] A non-Python target is reported as unsupported by the Python profile rather than reviewed ad hoc
- [ ] The persisted report lives at `.audits/source-code-review/<target-slug>.md` and a re-run overwrites it

## References

- [R1] Severity vocabulary and audit-artifact conventions: `spec/claude/review-plan/`
- [R2] Whole-codebase security audit (route-out target for D10 security floors): `spec/project/code-security-audit/`
- [R3] Dependency / CVE audit (delimited): `spec/project/dependency-audit/`
- [R4] Observability audit (route-out target for D10 observability floors): `spec/project/monitoring-observability/`
- [R5] Test-tier specs and reviewers (route-out targets for tier conformance): `spec/project/test-pyramid-foundation/` and `spec/project/test-tier-*/`
- [R6] Mechanical gate the tooling-first rule defers to: `spec/project/quality-gate/`
- [R7] Agent authoring rules and read-only tool discipline: `spec/claude/agent-management/`
- [R8] Skill-vs-agent decision rule: `spec/claude/skill-vs-agent/`
- [R9] Frontend surface extension (dimensions F1–F11, framework profiles, delimitation from the UX review): `spec/frontend/source-code-review/`
- [R10] Falsifiability taxonomy and detection criteria behind D6's always-green-test rule and the test-code instance of D1's swallowed-error no-go: `spec/project/test-falsifiability/`

## Open Questions

- Should the D4 domain-duplication dimension gain a cross-repository mode (duplication across portfolio members), or stay repository-local until the portfolio-inherited spec layer ships a cross-repo resolver?
- Which second **language** profile should be added first, and does it live in this spec or in a sibling profile document once profile count grows? The browser surface is now covered by the frontend extension [R9], which carries its own framework profiles, so the open slot is server-side TypeScript—a repository running a Node service plus a browser client currently gets the extension for its client and no profile for its server.
