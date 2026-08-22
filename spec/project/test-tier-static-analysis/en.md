# Test Tier: Static Analysis

Status: draft

## Context

Static analysis is the **foundation tier** of the test pyramid defined in `spec/project/test-pyramid-foundation/`: the broad, cheap, fast base every other tier rests on. It's the one tier that verifies code **without executing it**: it reads source (or compiled) artefacts and reports defects from their structure alone, needing no test cases and no running system [R5], [R6]. Empirically it's not a redundant duplicate of the dynamic tiers—static and dynamic analysis find largely **non-overlapping** defect sets, so the foundation layer reaches problems unit and integration tests never will [R6], [R7].

This spec is the per-tier realisation of the foundation's **invariant shape** for the static-analysis tier. It fills every field that shape mandates (purpose and scope boundary, isolation, speed and determinism, execution placement, traceability, canonical anti-patterns, optional reference profile) and adds the tier-specific governance—the sub-category taxonomy, the SAST/SCA boundary, type checking as a first-class sub-tier, and the baseline-and-ratchet model for adopting analysis on legacy code.

It's deliberately **tool-agnostic**: the binding requirements never name a tool. The concrete linters, type checkers, formatters, and SAST engines that realise the tier appear only as an illustrative reference profile.

**Relationship to the other specs.** This tier is bounded by responsibility, not by overlap:

- `spec/project/test-pyramid-foundation/` [R1] owns the tier model and this tier's place in it (the foundation layer). This spec details the tier; it doesn't restate the model.
- `spec/project/quality-gate/` [R2] **executes** the fast tiers (lint, typecheck, test) as a single invocation and owns the run mechanics and output shape. This spec defines *what the static-analysis tier must contain and how it gates*; quality-gate defines *how it's run*.
- `spec/project/dependency-audit/` [R3] owns third-party dependency CVE scanning (software composition analysis, SCA). This spec's SAST sub-category analyses **first-party source**; it **MUST NOT** claim the dependency-CVE responsibility—that boundary is load-bearing [R8], [R9].
- The **Unit tier** (`spec/project/test-tier-unit/`, sibling) is the first *executing* tier directly above static analysis; the boundary is "analyses code shape" vs "runs the code and asserts behaviour."

Readers: spec authors writing the sibling per-tier specs; skill and agent authors building the static-analysis development/execution/analysis triad; developers wiring the tier into pre-commit and CI; reviewers checking that the tier is deterministic, gated, and correctly bounded.

## Goals

- Define what the static-analysis tier verifies—and, sharply, what it can't—so it's never asked to do a dynamic tier's job
- Enumerate the sub-categories (lint, type-check, format, complexity, SAST, dead-code, import hygiene) as a single recognised taxonomy
- Establish type checking as a first-class sub-tier—"tests you don't write"—with a gradual-adoption and strictness-ratchet model
- Draw the SAST↔SCA boundary so static security analysis of first-party code never absorbs dependency-CVE scanning
- Encode the governance that keeps the tier trusted: inline fast feedback, deterministic and reproducible runs, severity-based PR gating, baseline-and-ratchet for legacy code, and disciplined suppression
- Keep the tier tool-agnostic, with a swappable reference profile rather than a mandated toolchain

## Non-Goals

- Executing the tier or defining its run mechanics and output table—owned by `spec/project/quality-gate/` [R2]
- Scanning third-party dependencies for known vulnerabilities (SCA / CVE drift)—owned by `spec/project/dependency-audit/` [R3]
- Dynamic security testing (DAST) of a running system—that's an end-to-end/system-scope concern per the foundation's cross-cutting dimensions, not this tier
- Asserting runtime behaviour, business logic, or integration correctness—those belong to the executing tiers above
- Mandating specific linters, type checkers, formatters, or SAST engines—the reference profile is illustrative
- Defining the repository-wide rule set or per-language config content—that's a per-repository decision; this spec defines the tier's shape and governance, not its rule lists
- Defining the falsifiability checks over test code (swallowed post-conditions, vacuous assertions, empty-default readers)—the check catalog is owned by `spec/project/test-falsifiability/` [R17]; this tier owns the regime those checks run under (rule identifiers, baseline-and-ratchet, effective-signal governance)

## Requirements

### Purpose and scope boundary

- **MUST** define the static-analysis tier as verification performed **without executing the program**: reading source or compiled artefacts and reporting defects from their structure, requiring no test cases [R5], [R6].
- **MUST** treat the tier as **complementary to, not a subset of, the executing tiers**: static and dynamic analysis catch largely non-overlapping defects, so static analysis is additive coverage, never a substitute for unit/integration tests [R6], [R7].
- **MUST NOT** ask the static-analysis tier to assert **runtime behaviour, business-logic correctness, or integration outcomes**; a defect that can only be observed by running the code belongs to the Unit tier or above. This is the boundary to the first executing tier.
- **MUST** position the tier as the **foundation (broadest, cheapest, fastest)** layer of the pyramid per `spec/project/test-pyramid-foundation/` [R1], [R10].
- **MUST** be enforced by **tooling rather than by a generator-plus-reviewer agent pair**, unlike the four executing tiers. This tier's checks are configured once per repository rather than authored per feature, so a generator would have nothing to scaffold for a new feature and a reviewer of its output would duplicate the wiring audit that `quality-gate-enforcer` already performs. The enforcement chain is: `spec/project/quality-gate/` requires the lint and type-check categories, `quality-gate` executes them, `quality-gate-enforcer` audits their wiring, and `test-pyramid-check` routes the tier away from its own audit for this reason. The absence of a `static-analysis-test-generator` and a `static-analysis-test-reviewer` is therefore the **designed state**, not the gap it looks like beside the four sibling tiers, and an inventory comparing tiers by agent-pair count **MUST NOT** report it as one.

### Sub-category taxonomy

- **MUST** recognise the following sub-categories as the closed set the tier comprises, each catching defects from code structure alone:
  1. **Linting / lint rules**: likely-bug and style-violation patterns (unused variables, shadowing, suspicious constructs).
  2. **Type checking**: static type verification and inference (see §"Type checking as a first-class sub-tier").
  3. **Formatting**: deterministic layout, verified in check mode (see §"Formatting is autofixed, not gated by debate").
  4. **Complexity & maintainability**: cyclomatic/cognitive complexity and maintainability thresholds.
  5. **Static security analysis (SAST)**: first-party-code security defects (see §"SAST scope and the SCA boundary").
  6. **Dead-code / unused-symbol detection**: unreachable code, unused exports.
  7. **Import / dependency hygiene**: import ordering, cycle detection, banned-import rules (structural, not CVE—see boundary).
- **MAY** omit a sub-category that doesn't apply to a language or project, recorded as a deliberate omission rather than a silent gap, per the foundation's tier-omission rule.

### Type checking as a first-class sub-tier

- **MUST** treat static type checking as a **first-class part of the tier**, not an optional extra: static types are "tests you don't write," and empirical study found a mature type checker catches on the order of **~15% of otherwise-shipped public bugs** in untyped code (Flow 0.30 / TypeScript 2.0, ICSE 2017) [R11], [R12].
- **MUST** adopt **gradual typing** on existing untyped code rather than demanding full annotation at once: annotate a subset first, then ratchet strictness progressively toward a strict target, and **block only newly introduced type errors in CI** while grandfathering the legacy baseline [R13], [R14].
- **SHOULD** track a strictness target and tighten it over time (the Dropbox 4-million-line / multi-year trajectory is the reference experience) rather than freezing at the loosest setting [R13], [R14].

### SAST scope and the SCA boundary

- **MUST** scope the SAST sub-category to **first-party source code**: data-flow / taint analysis that reports defect classes such as injection, buffer overflow, unsafe deserialisation, and hardcoded secrets, each with file, line, and snippet [R8].
- **MUST NOT** treat SAST as **complete security coverage**: it can't reliably detect authentication, access-control, or cryptographic-design flaws, and it's inherently noisy with false positives—it's one signal, not a security sign-off [R8], [R9].
- **MUST** keep the boundary to **software composition analysis (SCA)** sharp: scanning *third-party dependencies* for known CVEs is owned by `spec/project/dependency-audit/` [R3], not by this tier; SAST analyses the project's own code [R9].
- **MUST** keep the boundary to **DAST** sharp: dynamic security testing of a running system is an end-to-end/system-scope cross-cutting concern, never part of the no-execution static tier.

### Determinism and reproducibility

- **MUST** require the tier to be **fully deterministic**: the same source and the same pinned rule/tool versions always produce the same findings, with no dependence on wall-clock, network, machine, or ordering. Because the tier executes nothing, the foundation's test-double vocabulary doesn't apply—there are no collaborators to isolate; the determinism guarantee instead rests on **pinned analyzer and rule-set versions**.
- **MUST** pin the analyzer and rule-set versions (per the repository's dependency-management mechanism) so a finding is reproducible across machines and over time; an unpinned ruleset that silently changes findings between runs is a flakiness defect per the foundation.

### Execution placement and feedback economics

- **MUST** place the tier **first and fastest** in the feedback chain—editor/IDE, then a pre-commit hook, then a PR-gating CI check—so defects are caught at the cheapest possible point [R10], [R15].
- **MUST** deliver findings **inline at code-review / PR time**, not solely on an out-of-band nightly dashboard: at-review placement is what makes static analysis acted upon; a separate dashboard that developers must remember to visit is a documented failure mode (FindBugs nightly went unused; the inline approach succeeded) [R15].
- **SHOULD** integrate the same rule set into the editor so the developer sees a finding before commit, not only after push.

### Severity gating and the baseline-and-ratchet model

- **MUST** assign findings a **severity** and gate the PR on the blocking severities (errors), while non-blocking severities (warnings/info) are surfaced but don't fail the gate; the gating subset is declared as required checks per `spec/project/pull-request-workflow/` and executed per `spec/project/quality-gate/`.
- **MUST** govern the tier by **effective signal**: a rule whose findings developers routinely ignore or override is a cost (alert fatigue), and a tier dominated by noise loses trust; rules that produce action are kept, rules that don't are tuned or removed [R15].
- **MUST** adopt **baseline-and-ratchet** when introducing analysis on a legacy codebase: capture the existing findings as a grandfathered baseline, **block any new finding above the baseline**, and tighten the baseline over time—never block the whole backlog at once, and never leave the gate permanently off [R13], [R16].
- **MUST NOT** encode a fixed numeric false-positive or coverage threshold as a portfolio requirement (for example "automatically disable above 10% noise"); such a hard threshold isn't an established, verifiable invariant—govern by effective signal, not a magic number.

### Suppression discipline

- **MUST** require every suppression of a finding to be **narrow and justified**: an inline, single-finding suppression carrying a reason, never a blanket file- or repo-wide disable that silently hides a whole rule class.
- **SHOULD** make suppressions reviewable—visible in the diff and subject to the same review as code—so a suppression is a deliberate, auditable decision rather than a hidden escape hatch.

### Formatting is autofixed, not gated by debate

- **MUST** treat formatting as **applied mechanically**, not a matter of per-PR debate: a single deterministic formatter is the source of truth, CI verifies in check mode, and style is never the subject of review comments (format wars / bikeshedding are an anti-pattern).
- **SHOULD** autofix trivially fixable findings (formatting, import order) rather than blocking a PR on them; the gate blocks on what can't be autofixed.

### Traceability

- **MUST** make every finding **traceable to a file, line, and rule identifier**, so a developer can locate and understand it without rerunning analysis [R8].
- **SHOULD** map each enforced rule to the concern it protects (a bug class, a security class, a maintainability threshold) so the rule set is reviewable by intent, not just by name. Unlike the executing tiers, static-analysis findings trace to **code locations and rule IDs**, not to requirement / TC-IDs—there is no test case behind a lint rule.

### Optional reference profile

- **MAY** pin a fully worked, stack-specific reference profile, clearly demoted to "reference" and never elevated to a requirement. An illustrative Python profile: a consolidated fast linter+formatter (for example `ruff` covering lint + import-sort + format, replacing the older `flake8`+`isort`+`black` stack), a static type checker (for example `mypy` or `pyright`) wired to block new errors, and a first-party SAST pass (for example `bandit` or `semgrep`). Other ecosystems realise the same tier with their own tools (ESLint/`tsc`/Prettier; golangci-lint/`gofmt`; clippy/`rustfmt`). The trend toward **consolidated "format + lint + fix" runners** is noted as illustrative, not mandated.

## Acceptance Criteria

- [ ] The spec states that the tier is tool-enforced rather than agent-enforced, names the artefacts forming the enforcement chain, and says that the absence of a generator/reviewer pair is the designed state rather than a gap
- [ ] The spec names which of its own requirements the enforcement chain doesn't cover, rather than implying the chain covers all of them

- [ ] The spec defines the tier as no-execution verification that needs no test cases, and cites the foundation and a primary source for the static/dynamic complementarity (non-overlapping defects)
- [ ] The sub-category taxonomy lists the seven sub-categories (lint, type-check, format, complexity, SAST, dead-code, import hygiene)
- [ ] Type checking is established as a first-class sub-tier with the gradual-typing + strictness-ratchet + block-new-errors model, cited to the type-study and mypy sources
- [ ] The SAST sub-category is scoped to first-party code, declared as incomplete security coverage, and bounded against SCA (`dependency-audit`) and DAST
- [ ] Determinism is required via pinned analyzer/rule versions, and the spec notes the foundation's test-double vocabulary doesn't apply (no execution)
- [ ] Execution placement requires inline/at-review feedback and rejects the out-of-band-nightly-dashboard-only pattern, cited to the Google source
- [ ] Severity gating, govern-by-effective-signal, and baseline-and-ratchet for legacy code are required, and no fixed numeric noise/coverage threshold is mandated
- [ ] Suppression discipline (narrow, justified, reviewable) and formatting-autofix-not-debate are required
- [ ] Traceability is to file/line/rule-ID, and the spec notes this tier doesn't trace to requirement/TC-IDs
- [ ] The delimitation against `quality-gate` (executes), `dependency-audit` (SCA), and the Unit tier (first executing tier) is explicit
- [ ] An optional, clearly-demoted reference profile is provided without mandating a toolchain
- [ ] EN and DE versions are structurally identical (same headings, requirement count, acceptance-criteria count) and the spec index lists the new slug

## References

- [R1] `spec/project/test-pyramid-foundation/`: the tier model this spec realises (static analysis is the foundation tier)
- [R2] `spec/project/quality-gate/`: executes the fast tiers and owns the run mechanics / output shape
- [R3] `spec/project/dependency-audit/`: owns third-party dependency CVE scanning (SCA); the SAST↔SCA boundary
- [R4] `spec/project/pull-request-workflow/`: owns the required-status-check enforcement the gating subset feeds
- [R5] ISTQB / ASTQB, *Static Testing Basics*: <https://astqb.org/3-1-static-testing-basics/>
- [R6] Kent C. Dodds, *The Testing Trophy and Testing Classifications* (static is the base tier): <https://kentcdodds.com/blog/the-testing-trophy-and-testing-classifications>
- [R7] A. Habib & M. Pradel, *How Many of All Bugs Do We Find? A Study of Static Bug Detectors* (static and dynamic find non-overlapping defects): <https://arxiv.org/abs/1711.05019>
- [R8] OWASP, *Source Code Analysis Tools* (SAST: taint/data-flow, defect classes, file/line/snippet, false positives): <https://owasp.org/www-community/Source_Code_Analysis_Tools>
- [R9] OWASP, *Static Code Analysis* control / *Dependency-Check* (SAST vs SCA boundary): <https://owasp.org/www-community/controls/Static_Code_Analysis> , <https://owasp.org/www-project-dependency-check/>
- [R10] Kent C. Dodds, *Static vs Unit vs Integration vs E2E Tests*: <https://kentcdodds.com/blog/static-vs-unit-vs-integration-vs-e2e-tests>
- [R11] Z. Gao, C. Bird & E. T. Barr, *To Type or Not to Type: Quantifying Detectable Bugs in JavaScript* (ICSE 2017; ~15% of public bugs): <https://earlbarr.com/publications/typestudy.pdf>
- [R12] Microsoft Research, *To Type or Not to Type* (study PDF): <https://www.microsoft.com/en-us/research/wp-content/uploads/2017/09/gao2017javascript.pdf>
- [R13] mypy, *Using mypy with an existing codebase* (gradual typing, ratchet to strict, block new errors): <https://mypy.readthedocs.io/en/stable/existing_code.html>
- [R14] Dropbox, *Our journey to type checking 4 million lines of Python*: <https://dropbox.tech/application/our-journey-to-type-checking-4-million-lines-of-python>
- [R15] C. Sadowski et al., *Lessons from Building Static Analysis Tools at Google* (CACM 2018; inline beats nightly dashboards, govern by effective false positive): <https://cacm.acm.org/research/lessons-from-building-static-analysis-tools-at-google/>
- [R16] *Ratcheting* (baseline-and-ratchet pattern for legacy code): <https://ponomarev.uk/blog/ratcheting>
- [R17] `spec/project/test-falsifiability/`: owns the test-code falsifiability check catalog this tier operates

## Open Questions

- Should the portfolio declare a minimum baseline sub-category set every repository's static-analysis tier MUST enable (for example: at least one linter, one formatter, and—where the language has one—a type checker), or stay fully per-project?
- Where the language is dynamically typed and has no mature type checker, does the tier record the absence of the type-check sub-category as a justified omission, or require a typed superset (for example typed Python) as the portfolio default?
- **Decision (2026-08-22, #558):** the triad needs no dedicated agent pair. `quality-gate` (execute) plus `quality-gate-enforcer` (wiring audit) is sufficient, and the requirement under §Purpose and scope boundary records this. What stays open is narrower and worth naming rather than closing by implication: **the tier's own distinctive rules aren't enforced by anything today.** `quality-gate-enforcer` audits that the lint and type-check categories exist and are wired correctly; it checks neither §Severity gating and the baseline-and-ratchet model, nor §Suppression discipline, nor §SAST scope and the SCA boundary. Whether those become checks in that agent, a lint rule, or stay reviewer guidance isn't settled, and this spec is anchored by the enforcement chain above only for the parts that chain actually covers.
