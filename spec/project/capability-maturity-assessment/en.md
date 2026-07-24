# Capability Maturity Assessment

Status: draft
Portfolio-Scope: portfolio

## Context

A working application accumulates dozens of business-facing functions—"add a location," "detect a hardiness zone," "export a print view"—and stakeholders keep asking the same two questions about them: *who is each function for*, and *how done is it, really?* The second question hides three separate ones that teams routinely collapse into a single gut feeling: is the function **fully built** against what it promised, is it **well built** as code, and is it **trustworthily built** as in verified by tests at the right levels. A function can be feature-complete yet untested, or immaculately tested yet a thin stub, and a one-word answer ("done") erases that difference. What's missing is a **repeatable, top-down process** that inventories the application's business functions, ties each to the audiences it serves, and grades each function's *build maturity* along those three axes on a shared, defensible scale.

This spec defines that process. It governs how to **enumerate** the business-facing capabilities of an application, **map** each to the audiences it serves (consuming the audience artifact rather than reinventing it), and **classify** each capability into a **Bronze / Silver / Gold** maturity tier per axis—implementation completeness, code quality, and test coverage across tiers—plus a **separate overall tier** derived from those axes. It fixes the *criteria and the contract*, not a fixed list of functions: any application in the portfolio inherits the same rubric and produces its own capability matrix.

The tri-medal grading isn't invented ad hoc: graded project-quality tiers with exactly the Bronze/Silver/Gold shape are the established convention of the **OpenSSF Best Practices Badge** (passing/silver/gold) [R11], the three assessment axes are each grounded in an established body of practice (the ISO/IEC 25010 product-quality model for code quality [R8], McCabe cyclomatic complexity as a maintainability signal [R9], the portfolio's own Test Pyramid foundation for the test axis [R2]), and the deliberate distinction from *process* maturity models (CMMI [R12]) keeps the assessment about the product, not the organisation.

The spec draws a **hard boundary**: it governs *inventory, audience mapping, and grading only*. The moment a capability's tier is assigned and written to the matrix, the process stops. Enforcing a tier as a merge gate, prioritising which Bronze capability to promote next, or wiring the grade into a dashboard is **downstream action**, out of scope (see §Non-Goals). In particular this spec isn't a pass/fail quality gate: `spec/project/quality-gate/` [R3] answers "may this PR merge?" with a binary; this spec answers "how mature is this capability?" with a graded, advisory classification that never blocks a merge.

It's a sibling of `spec/project/kpi-definition-process/` [R7] in shape—both are `Portfolio-Scope: portfolio` methodology specs that ground a downstream `nolte-engineering` skill whose read-only scanner reads the source tree, and both separate mechanical detection from a human judgement call. They differ in question: KPIs measure *business outcomes at runtime* (did the app achieve its goal?), while this spec measures *build maturity of a capability* (is the function fully, well, and verifiably built?). The two compose—a Gold-tier capability can still drive a poor KPI, and a critical KPI can rest on a Bronze-tier capability that needs promotion.

Readers: teams that need to know how complete and trustworthy each of their application's functions is, and for whom; the authors of the future `maturity-assess` skill and its read-only scanner agent; reviewers checking a maturity matrix; consumer repositories that inherit this spec by reference.

## Goals

- The application's business-facing capabilities are **inventoried top-down** as user-meaningful functions traceable to requirements, not bottom-up from whatever code modules happen to exist
- Every capability is **mapped to the audiences it serves**, consuming the `spec/project/audience-identification/` [R1] artifact, so "who is this for" is answered from an authoritative list, not a private assumption
- Every capability is graded on three explicit, independent axes—implementation completeness, code quality, and test coverage across tiers—so the "how done is it" question is decomposed rather than collapsed
- Each axis is classified into one of **Bronze / Silver / Gold** against a stated rubric, with a fourth implicit **Unrated** floor for a capability that doesn't yet clear Bronze on that axis
- A **separate overall tier** is derived from the three axis tiers by a **weakest-link** rule and reported *alongside* the per-axis tiers, so a reader sees both the summary and where the summary comes from
- The grading cleanly separates **machine-derivable signals** (static analysis, complexity, coverage, tier presence, CI status) from **judgement inputs** (audience mapping, completeness against acceptance criteria), so the process is automatable where it can be and honest where it can't
- The graded capabilities land in a **human-readable, judgement-legible artifact** (`project/maturity/<slug>.md`) that a reader can follow and challenge, because a maturity tier is a defensible claim, not a machine dump
- Tier thresholds (coverage bands, complexity ceilings) are **project-configurable parameters** with a fixed monotonicity invariant, so the *rubric structure* is portfolio-wide while the *numbers* fit each stack
- The process is **portfolio-inheritable**: a consumer repository references this spec at a pinned hub release and grades its own application's capabilities against the same contract

## Non-Goals

- **Enforcing a tier as a gate.** Blocking a merge, failing CI, or refusing a release because a capability is below a target tier is downstream action; this spec produces an advisory grade, never a gate. The pass/fail merge decision stays owned by `spec/project/quality-gate/` [R3]
- **Prioritisation and roadmapping.** Deciding *which* Bronze capability to promote next, or sequencing promotion work, is a planning decision owned by `spec/project/roadmap/` and `spec/project/sprint/`; this spec grades the current state, it doesn't plan the next one
- **Dashboards and trend tracking.** Rendering the matrix into a dashboard, tracking tier movement over time, or alerting on regressions is a measurement/presentation concern out of scope here
- **Defining the application's audiences.** Enumerating and characterising audiences is owned by `spec/project/audience-identification/` [R1]; this spec *consumes* that artifact, it doesn't produce it
- **Redefining the test tiers or the coverage-as-guide rule.** The functional tier taxonomy (static → unit → component → integration → contract → E2E) and the "coverage is a guide, not a target" governance rule are owned by `spec/project/test-pyramid-foundation/` [R2]; the test axis *consumes* them
- **A fixed, universal capability list.** This spec defines the *process and rubric* to grade project-specific capabilities, not a canned catalogue of "the functions every app has"; the capabilities are always inventoried from *this* application
- **Assessing organisational or process maturity.** CMMI-style process-capability levels [R12] grade how an organisation builds software; this spec grades how mature a built capability is. The name similarity is coincidental and the boundary is deliberate

## Requirements

### The capability inventory

- The process **MUST** inventory **business-facing capabilities**: user-meaningful units of functionality that a named audience can recognise as a thing the application does (for example "record a harvest," "detect a climate zone"), each traceable to a requirement or acceptance criterion. A capability **MUST NOT** be defined as a code artifact (a module, class, or endpoint); code artifacts are the *evidence* a capability is graded against, not the unit of grading
- The inventory **MUST** be derived **top-down** from the application's requirements, feature set, or user-facing surface, and **MUST NOT** be assembled bottom-up from the directory structure; a capability that can't be laddered back to something a user or audience wants is a code artifact, not a capability
- Each capability **MUST** carry a stable short identifier (for example `C1`) for cross-reference, a human-readable name, and a one-sentence description of what the function does for its audience
- The process **MUST** be re-runnable: when the application changes, re-assessment **SHOULD** show which capabilities held their tier, which moved up, and which regressed, rather than silently replacing the matrix

### Audience mapping

- Every capability **MUST** be mapped to **at least one audience** drawn from the repository's `spec/project/audience-identification/` [R1] artifact (`AUDIENCES.md` or its ratified alternative). A capability that serves no identifiable audience is a defect in the inventory—either the audience list is incomplete or the capability is dead
- The process **MUST** consume the existing audience artifact and **MUST NOT** re-derive or invent audiences; when no audience artifact exists, the process **MUST** warn that audience mapping is unavailable and **SHOULD** recommend running the audience-identification method first, then proceed with audience mapping recorded as an open item (a **soft gate**, mirroring the sibling KPI spec's carve-out [R7])
- A capability's maturity tier is assigned **per capability** by default; where the maturity **materially diverges by audience** (for example the function is Gold for the primary audience but the path for a secondary audience is a Bronze stub), the process **SHOULD** record the per-audience divergence rather than flatten it to a single tier

### The three assessment axes

- Every capability **MUST** be graded on exactly these **three independent axes**, each classified into Bronze / Silver / Gold (or Unrated below Bronze):
  - **Axis A** (implementation completeness): how fully the capability is built against what it promised (its acceptance criteria / requirement)
  - **Axis B** (code quality): how well the code realising the capability is built, per the ISO/IEC 25010 product-quality model [R8] and static-analysis signals
  - **Axis C** (test coverage across tiers): how trustworthily the capability is verified by automated tests at the appropriate levels of the Test Pyramid [R2]
- The three axes **MUST** be graded and reported **independently**; a strong axis **MUST NOT** silently compensate for a weak one at the axis level (compensation is explicitly forbidden by the weakest-link overall rule below). This is the load-bearing decomposition of the whole spec: "how done is it" is three questions, not one

### Axis A: Implementation completeness

- Axis A **MUST** be graded against the capability's **acceptance criteria / requirement**, consuming the abstract cases of `spec/project/test-case-derivation/` [R4] and the acceptance criteria of `spec/project/spec-driven-development/` [R5] where they exist; where they don't, the assessor **MUST** state the completeness baseline used, because completeness is meaningless without a "complete against what?"
- The tier rubric for Axis A **MUST** be:
  - **Bronze**: the core happy path is implemented and reachable by its audience; at least the primary acceptance criterion is satisfied; visible gaps, stubs, or TODOs are permitted; error handling and edge cases aren't required
  - **Silver**: all documented acceptance criteria for the capability are satisfied; the principal error and validation paths are handled; there are no known functional gaps on the primary audience path; the capability is complete across its full surface (for example API + UI + i18n) for that path
  - **Gold**: Silver, plus edge and failure cases are handled, the non-functional requirements that apply to the capability are met (for example performance, accessibility, security, data-protection obligations), there are no open functional defects or TODOs against it, and end-user documentation exists for every mapped audience
- Axis A is **primarily a judgement input** (see §"Machine-derivable vs. judgement inputs"): assessing completeness against acceptance criteria requires reading the requirement, which a scanner can't do; the scanner **MAY** surface signals (unimplemented markers, `TODO`/`FIXME`, feature flags, stub returns) but **MUST NOT** assign the Axis A tier

### Axis B: Code quality

- Axis B **MUST** be grounded in the **ISO/IEC 25010** product-quality model [R8]—principally its *maintainability* characteristic (modularity, reusability, analysability, modifiability, testability)—and in the portfolio's static-analysis tier (`spec/project/test-tier-static-analysis/`), read against the repository's own style guides
- The tier rubric for Axis B **MUST** be:
  - **Bronze**: the code builds/runs and passes static analysis (lint, type-check, format-check) with **no errors** (warnings permitted); the applicable style guide is broadly followed
  - **Silver**: static analysis passes with **no warnings**; the style guide is fully followed; the architectural layering / module boundaries of the project are respected; cyclomatic complexity [R9] is under the project's configured ceiling and duplication is under its configured bound; the code is typed where the stack supports it
  - **Gold**: Silver, plus public interfaces are documented, there are no remaining code smells or technical-debt markers, security-oriented static rules (SAST) pass clean, complexity is low throughout rather than merely under ceiling, and the code has passed human review
- Axis B is **largely machine-derivable**: static-analysis status, complexity metrics, duplication, and type coverage are scanner signals; the **Gold** step ("no remaining smells," "passed human review") retains a judgement component the skill **MUST** confirm rather than infer

### Axis C: Test coverage across tiers

- Axis C **MUST** consume the functional tier taxonomy and governance rules of `spec/project/test-pyramid-foundation/` [R2] and **MUST NOT** redefine a tier. It grades a capability by **which test tiers verify it and whether they pass**, not by a single coverage number
- The tier rubric for Axis C **MUST** be:
  - **Bronze**: the capability's core logic is covered by **unit** tests that pass, and static analysis is green; the capability's line/branch coverage clears the project's configured **lower** band
  - **Silver**: Bronze, plus **component and/or integration** tests exercise the capability, and **contract** tests cover any service boundary it crosses; coverage clears the configured **middle** band; every one of these tiers passes in CI
  - **Gold**: Silver, plus at least one **end-to-end** test drives the capability through a mapped audience's real workflow, failure and edge cases are tested, coverage clears the configured **upper** band, and each test is traceable to the capability it verifies (per the requirement→TC-ID→test chain of [R2])
- Axis C **MUST** honour the Test Pyramid's **coverage-as-a-guide** rule [R2], [R10]: the coverage bands are a **graded maturity signal, advisory only**, and clearing a band **MUST NOT** be turned into a PR merge gate by this spec (gating stays with `quality-gate` [R3]). Where the toolchain supports it, **mutation score SHOULD** be reported as the stronger suite-quality signal alongside coverage, exactly as [R2] requires
- Axis C is **largely machine-derivable** (tier presence, pass/fail status, coverage %, mutation score), with a judgement residue for whether an E2E test genuinely exercises the *mapped audience's* workflow

### Per-axis tiering and the overall tier

- Each capability **MUST** be reported with **all three per-axis tiers explicitly** (Axis A, Axis B, Axis C), never only a summary; the per-axis breakdown is where the assessment's information lives
- A **separate overall tier MUST** be derived by the **weakest-link** rule: the overall tier is the **minimum** of the three axis tiers (Gold only when *every* axis is Gold; Silver when the weakest axis is Silver; Bronze when any axis is Bronze; Unrated when any axis is below Bronze). A strong axis **MUST NOT** compensate for a weak one in the overall tier
- The overall tier and the three axis tiers **MUST** both appear in the matrix; the process **MUST NOT** collapse them into the overall tier alone, because the axis divergence *is* the actionable content
- Where the axes diverge (for example Axis B Gold, Axis C Bronze), the process **SHOULD** record the divergence as an explicit improvement lever—the single axis that, if raised, would raise the overall tier—so the matrix reads as guidance, not just a scoreboard

### Machine-derivable vs. judgement inputs

- The process **MUST** classify every grading input as **machine-derivable** (a read-only scanner can compute it: static-analysis status, cyclomatic complexity, duplication, type coverage, per-tier test presence and pass/fail, coverage %, mutation score, `TODO`/stub markers) or **judgement** (a human must decide it: audience mapping, completeness against acceptance criteria, whether an NFR is met, whether an E2E test exercises the mapped workflow, whether Gold-level smells remain)
- The read-only scanner **MUST** perform **detection only** and **MUST NOT** assign a final tier; the interactive skill owns tier assignment, the judgement inputs, the operator confirmation, and the write. This mirrors the sibling KPI spec's scanner/skill seam [R7] and the read-only-agent discipline of `spec/claude/`
- Where an axis is largely machine-derivable (B and C), the scanner's signals **SHOULD** produce a **proposed** tier that the skill confirms or overrides; where an axis is primarily judgement (A), the scanner supplies evidence but the skill assigns the tier from the start

### The output artifact

- The graded capabilities **MUST** be written to `project/maturity/<slug>.md`, mirroring the layout of `project/kpis/<slug>.md`: a header naming the inventory scope, the audience artifact consumed, and the configured thresholds, followed by one structured block (or one table row) per capability
- Each capability block **MUST** carry: `id`, `name`, `description`, mapped `audience(s)`, the three per-axis tiers (A/B/C), the derived `overall` tier, the `improvement-lever` (the axis to raise next), and a short `rationale` making each axis tier defensible; where maturity diverges by audience, the per-audience divergence **MUST** be recorded
- The artifact **MUST** be **human-readable Markdown**, not a bare data dump, because a maturity tier is a defensible claim a reader must be able to follow and challenge; each capability's audience mapping **MUST** resolve to a real audience in the consumed artifact (a ghost audience is a defect)
- The header **SHOULD** state the rubric parameters used (the configured coverage bands and complexity ceiling) and list any capability whose Axis A couldn't be graded for lack of acceptance criteria as a named open item, so the assessment is auditable

### Thresholds are project-configurable

- The **numeric thresholds** the rubric references—the lower/middle/upper coverage bands (Axis C) and the complexity ceiling and duplication bound (Axis B)—these **MUST** be **project-configurable parameters**, not values hard-coded in this spec, so the rubric structure is portfolio-wide while the numbers fit each stack and language
- The configured thresholds **MUST** satisfy the **monotonicity invariant** `Bronze ≤ Silver ≤ Gold` on every graded band; a configuration that inverts or flattens the bands is invalid
- This spec **MAY** recommend starting defaults, but **MUST NOT** mandate a universal coverage percentage or complexity number; a fixed universal threshold would contradict both the application-agnostic goal and the coverage-as-a-guide rule [R2]

### Tooling shape (skill + read-only scanner)

- The process **MUST** be operationalised as an **interactive skill** (working name `maturity-assess`) plus **one read-only scanner agent** (working name `capability-maturity-scanner`): the scanner mines the source tree for the machine-derivable signals of Axes B and C and the Axis A evidence markers; the skill owns the inventory, the audience mapping, the judgement axes, the tier assignment, the operator confirmation, and the write. The skill **MUST** stay interactive because inventory, audience mapping, and completeness are judgement calls; the scanner **MUST** stay read-only and side-effect-free
- The tooling **MUST** live in the `nolte-engineering` plugin—its audience is code-bearing repositories, because the scanner reads source code and test results—while this spec remains repo-wide under `spec/`
- The tooling **SHOULD** be a single scanner rather than a scanner-per-axis, to respect the agent-description routing budget of `spec/claude/`

### Delimitation against neighbouring specs

- Against `spec/project/quality-gate/` [R3]: quality-gate is a **binary PR gate** over the fast tiers; this spec is a **graded, advisory classification** per capability. A capability can be Bronze overall and still pass the quality gate, and vice versa; the two never substitute for each other
- Against `spec/project/test-pyramid-foundation/` [R2] and the `test-tier-*` specs: those **own** the tier definitions, the coverage-as-guide rule, and the traceability chain; Axis C **consumes** them and adds only the *grading bands*, never a new tier
- Against `spec/project/kpi-definition-process/` [R7]: KPIs measure **business outcomes at runtime**; maturity measures **build quality of a capability**. A capability's tier is an input to *whether a KPI can be trusted*, not a KPI itself
- Against CMMI [R12]: CMMI grades **organisational process** capability; this spec grades **product capability** maturity. Named only to delimit
- Against `spec/project/audience-identification/` [R1]: that spec **produces** the audience list; this spec **consumes** it for the mapping column

### Portfolio scope and inheritance

- This spec carries `Portfolio-Scope: portfolio` and **MUST** remain inheritable by reference per `spec/project/portfolio-inherited-spec-layer/` [R6]: a consumer repository declares `inherits:` at a pinned hub `ref` and grades its own application's capabilities against this contract, never copying the spec text
- The spec's normative content **MUST** be **application-agnostic**: it prescribes the *inventory method, the three axes, the tier rubrics, and the artifact contract*, never a fixed capability list, audience list, or threshold number, so any application in the portfolio can inherit it and produce its own capability matrix

### Framework anchors

- The spec's normative content **MUST** be read against the anchors in §References: the **OpenSSF Best Practices Badge** [R11] as the precedent for a graded project-quality ladder (its own metal series runs passing/silver/gold, which this spec's Bronze/Silver/Gold rubric mirrors in shape, not in criteria); **ISO/IEC 25010** [R8] as the code-quality model behind Axis B; **McCabe cyclomatic complexity** [R9] as the maintainability signal Axis B references; the portfolio's **Test Pyramid foundation** [R2] (and Fowler's coverage-as-guide caveat [R10]) as the basis of Axis C; and **CMMI** [R12] named only to delimit product- from process-maturity
- Each external framework attribution ([R8]–[R12]) is an author-time external assertion carrying its own triangulated source list in §References (at least three independent sources each, retrieved 2026-07-24) per `spec/claude/research-triangulate/`, and **SHOULD** be re-validated against current sources whenever this spec is promoted beyond `draft` or its sources age past their advisory time-to-live; the internal-spec references ([R1]–[R7]) are load-bearing cross-references, not external claims

## Acceptance Criteria

- [ ] `spec/project/capability-maturity-assessment/` exists with `en.md` (canonical) and `de.md` (translation), carries `Portfolio-Scope: portfolio`, and is listed in `spec/README.md`
- [ ] The capability unit is defined as a **business-facing, audience-recognisable function traceable to a requirement**, and is explicitly barred from being a code artifact; the inventory is required to be top-down
- [ ] Every capability is required to map to **at least one audience** from the `audience-identification` artifact, with the missing-artifact **soft gate** (warn + recommend, don't block) and the per-audience divergence rule stated
- [ ] Exactly **three independent axes** (implementation completeness, code quality, test coverage across tiers) are defined, each with an explicit **Bronze / Silver / Gold** rubric and an **Unrated** floor
- [ ] Axis A is grounded in acceptance criteria (consuming `test-case-derivation` / `spec-driven-development`) and marked **primarily judgement**; Axis B is grounded in ISO/IEC 25010 + static analysis + McCabe complexity and marked **largely machine-derivable**; Axis C consumes the Test Pyramid tiers and marked **largely machine-derivable**
- [ ] The **weakest-link overall tier** (minimum over axes) is specified, reported **alongside** the three per-axis tiers, with axis compensation forbidden and the **improvement lever** recorded on divergence
- [ ] The **machine-derivable vs. judgement** split is stated per input, and the scanner is barred from assigning a final tier (detection only; the skill assigns and writes)
- [ ] Axis C **honours coverage-as-a-guide** [R2]: the coverage bands are advisory grading signals and are explicitly **not** turned into a PR merge gate by this spec; mutation score is named as the stronger signal where available
- [ ] The **output artifact** `project/maturity/<slug>.md` is specified: human-readable, mirroring `project/kpis/`, one block per capability carrying id/name/description/audiences/three axis tiers/overall/improvement-lever/rationale, with audience mapping resolving to a real audience
- [ ] Thresholds (coverage bands, complexity ceiling, duplication bound) are specified as **project-configurable parameters** with the `Bronze ≤ Silver ≤ Gold` **monotonicity invariant**, and no universal numeric threshold is mandated
- [ ] The **tooling shape** is specified: an interactive `maturity-assess` skill + one read-only `capability-maturity-scanner` agent in `nolte-engineering`, with the skill owning inventory/mapping/judgement/assignment/write and the scanner read-only
- [ ] The **delimitations** against `quality-gate` (graded ≠ gate), `test-pyramid-foundation` (consume ≠ redefine), `kpi-definition-process` (build maturity ≠ business outcome), CMMI (product ≠ process), and `audience-identification` (consume ≠ produce) are each stated
- [ ] The spec is **application-agnostic and portfolio-inheritable** (prescribes method/axes/rubric/contract, not a fixed capability, audience, or threshold list) and remains referenceable per `portfolio-inherited-spec-layer`
- [ ] EN and DE versions are structurally identical (same headings, requirement count, and acceptance-criteria count) and the spec index lists the new slug

## Open Questions

- **Capability granularity.** How coarse or fine a "business-facing capability" should be (a whole feature area such as "location management" versus a single function such as "detect a hardiness zone") is a per-project judgement; this spec fixes the traceable-to-a-requirement and audience-recognisable tests, not a universal granularity. Whether the inventory should reuse an existing artifact (`project/features/`, a REQ list) as its capability source rather than re-inventorying is settled when the `maturity-assess` skill is authored
- **Exact skill/agent names.** Working names `maturity-assess` (skill) and `capability-maturity-scanner` (agent) are confirmed against the `<object-noun>-<action>` naming convention and catalogue discoverability at skill-authoring time
- **Overall-tier rule beyond weakest-link.** The spec fixes weakest-link (minimum) as the overall rule; whether a project may *opt in* to a stricter "Gold requires Gold on all axes **and** a passed human review" or a looser variant via a local override is deferred
- **Per-audience tiering depth.** Whether per-audience divergence should be a full parallel grading (three axes × each audience) or a lightweight note on the capability is deferred to skill-authoring; the spec requires recording the divergence, not a fixed depth
- **Threshold default recommendations.** Whether this spec should ship *recommended* starting coverage bands and a complexity ceiling (clearly demoted to "reference," per the tool-agnostic precedent of `test-pyramid-foundation`) or leave every number to the project is deferred

## References

- [R1] `spec/project/audience-identification/`: Audience Identification (produces the audience list the mapping column consumes)
- [R2] `spec/project/test-pyramid-foundation/`: Test Pyramid Foundation (owns the functional tier taxonomy, the coverage-as-guide rule, and the traceability chain that Axis C consumes)
- [R3] `spec/project/quality-gate/`: Quality Gate (the binary PR gate this spec's graded classification is delimited against)
- [R4] `spec/project/test-case-derivation/`: Test-Case Derivation from Requirements (the acceptance/TC-IDs Axis A grades completeness against)
- [R5] `spec/project/spec-driven-development/`: Spec-Driven Development (the acceptance-criteria basis for Axis A)
- [R6] `spec/project/portfolio-inherited-spec-layer/`: Portfolio-Inherited Spec Layer (how a consumer repo inherits this spec by reference)
- [R7] `spec/project/kpi-definition-process/`: KPI Definition Process (sibling methodology spec; the build-maturity-vs-business-outcome delimitation)
The external framework anchors [R8]–[R12] are author-time external assertions triangulated per `spec/claude/research-triangulate/` §Author-time assertions (author-time tier: at least three independent sources, ordered Primary-first). Retrieval date for every external source below: 2026-07-24.

- [R8] ISO/IEC 25010—Systems and software Quality Requirements and Evaluation (SQuaRE), product quality model. The current second edition, **ISO/IEC 25010:2023**, defines **nine** characteristics, not the eight of the withdrawn :2011 edition: Safety was added, Usability became Interaction Capability, Portability became Flexibility, and quality-in-use moved out to ISO/IEC 25019:2023. Maintainability, the characteristic Axis B leans on, keeps its five sub-characteristics (modularity, reusability, analysability, modifiability, testability).
  - ISO/IEC 25010 portal, carrying the :2023 characteristic tree including the maintainability sub-characteristics (Secondary): <https://iso25000.com/index.php/en/iso-25000-standards/iso-25010>
  - arc42 Quality Model, "ISO/IEC 25010," annotating the renamed characteristics (Secondary): <https://quality.arc42.org/standards/iso-25010>
  - arc42, "Update on ISO 25010, version 2023," dating the revision to November 2023 and listing the sub-characteristic deltas (Secondary): <https://quality.arc42.org/articles/iso-25010-update-2023>
  - Sonar, "ISO/IEC 25010 Explained: 9 Software Quality Characteristics" ("from eight to nine software product quality characteristics") (Secondary): <https://www.sonarsource.com/resources/library/iso-iec-25010-explained/>
- [R9] Thomas J. McCabe, *A Complexity Measure*, IEEE Transactions on Software Engineering, vol. SE-2, no. 4, pp. 308–320, December 1976 (`doi:10.1109/TSE.1976.233837`); the paper itself sits behind a publisher paywall, so the citable trail is the standards-body methodology built on it plus tool-vendor documentation of the metric.
  - NIST Special Publication 500-235, *Structured Testing: A Testing Methodology Using the Cyclomatic Complexity Metric* (Watson/McCabe), the standards-body treatment of the 1976 measure (Primary): <https://www.nist.gov/publications/structured-testing-testing-methodology-using-cyclomatic-complexity-metric>
  - Microsoft Learn, "Code metrics—cyclomatic complexity", documenting the metric as a testability and maintainability signal with a practical ceiling (Secondary): <https://learn.microsoft.com/en-us/visualstudio/code-quality/code-metrics-cyclomatic-complexity>
  - Overview of cyclomatic complexity, with the full bibliographic record of the 1976 paper (Tertiary): <https://en.wikipedia.org/wiki/Cyclomatic_complexity>
- [R10] Martin Fowler, *TestCoverage* (coverage as a guide, not a target): <https://martinfowler.com/bliki/TestCoverage.html> (Primary)
  - `Laura Inozemtseva` and Reid Holmes, *Coverage Is Not Strongly Correlated with Test Suite Effectiveness*, ICSE 2014 (*"should not be used as a quality target"*) (Primary, peer-reviewed): <https://www.cs.ubc.ca/~rtholmes/papers/icse_2014_inozemtseva.pdf>
  - Google Testing Blog, "Code Coverage Goal: 80% and No Less!," the parable against rigid coverage mandates (Primary, independent practitioner org): <https://testing.googleblog.com/2010/07/code-coverage-goal-80-and-no-less.html>
- [R11] OpenSSF Best Practices Badge Program. The graded metal series runs **passing / silver / gold** and is cumulative (gold requires silver); since the OpenSSF adoption the programme also carries a separate Baseline series (levels 1–3), so "the badge levels" is no longer a single ladder.
  - OpenSSF Best Practices Badge criteria, listing both series (Primary): <https://www.bestpractices.dev/en/criteria>
  - OpenSSF project page for the Best Practices Badge, distinguishing the metal from the baseline series (Primary): <https://openssf.org/projects/best-practices-badge/>
  - `ossf/best-practices-badge` repository, recording the rename from the CII Best Practices badge (Primary): <https://github.com/ossf/best-practices-badge>
- [R12] CMMI (Capability Maturity Model Integration)—process-capability maturity levels, named only to delimit product- from process-maturity. Maturity levels 1–5 (Initial, Managed, Defined, Quantitatively Managed, Optimizing) are staged and organisation-wide, with V2.0/V3.0 adding a level 0 "Incomplete"; capability levels are the per-practice-area continuous representation. The model is stewarded by ISACA (which acquired the CMMI Institute in 2016), and CMMI V3.0 has been the only appraisal basis since 2024-01-01. CMMI **appraises**, it doesn't certify.
  - Carnegie Mellon SEI, "Transforming software quality assessment," the origin record of the CMM/CMMI line (Primary): <https://www.sei.cmu.edu/history-of-innovation/transforming-software-quality-assessment/>
  - CIO, *"What is CMMI? A model for optimizing development processes,"* recording the ISACA acquisition and the 2023 V3.0 release (Secondary): <https://www.cio.com/article/274530/cmmi-explained.html>
  - Core Business Solutions, "CMMI V3.0 update explained," dating V3.0 to April 2023 and the appraisal transition to 2024-01-01 (Secondary): <https://www.thecoresolution.com/cmmi-v3-update-explained>
  - Capability Maturity Model Integration overview, covering the staged-versus-continuous representations (Tertiary): <https://en.wikipedia.org/wiki/Capability_Maturity_Model_Integration>

Verified 2026-07-24. Two anchors moved since this spec was drafted and the entries above are corrected rather than merely cited: ISO/IEC 25010 carries nine characteristics under the :2023 edition (the earlier "eight characteristics" wording described the withdrawn :2011 model), and the OpenSSF badge is no longer a single passing/silver/gold ladder. One sourcing limit is recorded deliberately: every primary CMMI surface (the ISACA model pages, `cmmiinstitute.com`, and the retired SEI CMMI-for-Development reports) was unreachable to automated retrieval on the retrieval date, so [R12] rests on one primary origin record plus independent secondary coverage.
