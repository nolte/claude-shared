# Requirements — CI/CD pipeline specialist (spec foundation + skill + review agent)

<!--
Produced via the `requirements-elicit` skill, following
spec/project/requirements-elicitation/.
Runs as the requirements gate for the `feat/cicd-specialist` working copy, settling
OQ1–OQ5 recorded in `.resume/cicd-specialist/plan.md` §3 before any spec is written.
`c_d` is an uncertainty proxy (self-consistency-derived), not a calibrated probability.
A requirement is `confirmed` only after an explicit teach-back or an authoritative
operator choice.
-->

## Bounded context

- **What:** A CI/CD **pipeline-design** capability — three specs plus the pair of artifacts that operationalize them. Two tool-independent specs define the continuous-integration and continuous-delivery disciplines; one platform spec binds them to GitHub Actions. A writing skill designs and scaffolds a pipeline into a repository; a read-only agent audits an existing one.
- **For whom:** Maintainers and operators of `nolte/*` repositories who set up, rework, or audit a pipeline.
- **Load-bearing axes:** **reproducibility** (pinned inputs, cache that can't change a result, local↔CI parity, immutable artifacts) and **reusability** (`workflow_call` and composite reuse against the existing `nolte/gh-plumbing` model). Efficiency — runtime, cache hit rate — is a guide, never a gate.
- **The gap being closed:** no spec today governs the *design* of a pipeline. Neighbouring specs each own one piece: `workflow-health` owns the **operation** of red workflows, `branching-model` **which** workflows must exist, `project-structure` **where** they live and how they're pinned, `pull-request-workflow` **what** gates a merge, `quality-gate` and `taskfile` the lint/test contract plus the local↔CI parity rule, `release-artifact` and `release-automation` the release line. The convention has to be reconstructed from seven places.
- **Out of scope:** operating and triaging red workflows (`workflow-health`); the Draft→Published transition (`release-automation`); the required-workflow enumeration (`branching-model`); the lint/type-check/test gate itself (`quality-gate`, `taskfile`); the test model CI executes (`test-pyramid-foundation`, `test-tier-*`, `test-cycle-*`); rolling a workload into a cluster (`kubernetes-deployment-best-practices`, `bjw-s-common-chart-deployment`); any non-GitHub CI platform.
- **Origin:** operator-initiated working copy `feat/cicd-specialist` (author `nolte`, repo OWNER — trusted). No GitHub issue; the driving artifact is `.resume/cicd-specialist/plan.md`.

## Understanding KPI

- Thresholds: `τ_low = 0.4`, `τ_high = 0.8`, self-consistency `k = 2`, question budget = `12` (spec defaults, unchanged; 10 questions used across 5 turns)
- `U_gate = min_d c_d` over required dimensions = **0.85**
- Termination: `saturation` (every required dimension ≥ `τ_high` through authoritative operator choices plus one whole-reading teach-back; no remaining candidate question carried positive net EVPI — the residue is spec-authorship detail, recorded below as assumptions)

### Gap matrix

| Dimension | Applicable | `c_d` | Uncertainty source | Evidence event |
|---|---|---|---|---|
| `functional` | yes | 0.90 | specification | Operator choice: three specs (CI + CD + Actions binding) plus a writing design/scaffold skill and a read-only review agent |
| `non_functional` | yes | 0.88 | specification | Operator choice: spec conformance **plus** demonstrable reproducibility as the acceptance measure; efficiency stays a guide |
| `constraints` | yes | 0.88 | specification | Operator choice: `nolte-shared` placement, GitHub Actions as the only concrete binding, reference-never-duplicate against the neighbouring specs |
| `domain_objects` | yes | 0.85 | interpretation | Whole-reading teach-back confirmed; vocabulary listed below and derived from the neighbouring specs rather than invented |
| `actors` | yes | 0.88 | specification | Operator choice: interactive writing skill for the operator, read-only agent for the audit; both reached through `nolte-shared` |
| `acceptance_criteria` | yes | 0.88 | specification | Operator choice: every MUST rule checkable at the repository, plus a demonstrable reproducibility claim |
| `edge_cases` | yes | 0.85 | specification | Operator choice on the portfolio-wide finding: report an upstream work package, never patch the consumer with a local copy |
| `scope_boundaries` | yes | 0.90 | specification | Operator choices: CD ends at handover, single-stage delivery normative with promotion optional, other CI platforms are a non-goal |

## Requirements

- **R1** — The capability SHALL be founded on **two** tool-independent specs, `spec/project/continuous-integration/` and `spec/project/continuous-delivery/`, rather than one combined document, because the two carry different triggers (pre-merge feedback versus post-merge delivery), different consumers, and different invariants.
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: operator choice "Zwei tool-neutrale Specs + Actions-Spec" (settles OQ1)
- **R2** — The concrete platform binding SHALL be a single spec named `spec/project/github-actions-best-practices/`, following the `dockerfile-best-practices` and `kubernetes-deployment-best-practices` naming pattern already in the corpus. The delivery spec SHALL be named `continuous-delivery`, not `continuous-deployment`, because `release-publish.yml` triggers on `workflow_dispatch` only and that deliberate manual gate is continuous delivery.
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: operator choice "continuous-delivery + github-actions-best-practices" (settles OQ2)
- **R3** — WHEN the CI spec is authored, it SHALL define the pre-merge feedback discipline: stage ordering (checkout → build → static analysis → test tiers → package/artifact → supply-chain scan), fail-fast and fast-feedback ordering, caching that accelerates without changing a result, matrix fan-out, and the local↔CI parity rule expressed through Taskfile targets.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: plan §3 "CI spec (tool-independent)", unchallenged through the interview
- **R4** — WHEN the CD spec is authored, it SHALL define the post-merge delivery discipline: artifact provenance and immutability, the **artifact-to-securing-stage matrix**, the release dispatch into `release-automation`, and the rollback contract expressed over artifact versions.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: plan §3 "CD spec (tool-independent)", unchallenged through the interview
- **R5** — The CD spec SHALL reference the artifact taxonomy of `spec/project/release-artifact/` as the authoritative source for which software artifacts exist, and SHALL NOT re-enumerate them.
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: plan §2 "the canonical source for 'the software artefacts CI/CD secures'"
- **R6** — WHEN the GitHub Actions spec is authored, it SHALL write against the portfolio's existing reusable-workflow model in `nolte/gh-plumbing` rather than beside it, and SHALL cover pinning, least-privilege `permissions`, `concurrency`, cache-key design, OIDC and secret handling, `workflow_call` versus composite actions, matrix fan-out, and environments.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: bounded-context teach-back naming `gh-plumbing`, accepted without correction; grounded in `pull-request-workflow` §"so every repository inherits one implementation rather than forking local copies that drift"
- **R7** — Reproducibility and reusability SHALL be the two load-bearing axes stated explicitly in all three specs; pipeline efficiency (runtime, cache hit rate, feedback latency) SHALL be treated as a guide and SHALL NOT be given normative thresholds.
  - _dimension_: `non_functional` · _status_: `confirmed` · _source_: whole-reading teach-back "Reproduzierbarkeit und Wiederverwendbarkeit sind die beiden tragenden Achsen; Effizienz ist Richtwert, kein Gate" — confirmed
- **R8** — The three new specs SHALL reference the neighbouring specs (`workflow-health`, `branching-model`, `project-structure`, `pull-request-workflow`, `quality-gate`, `taskfile`, `test-*`, `release-*`, the deployment specs, the supply-chain specs) and SHALL NOT restate any rule those specs already own.
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: whole-reading teach-back "sie referenzieren die bestehenden Nachbar-Specs und duplizieren keine ihrer Regeln" — confirmed
- **R9** — The specialist SHALL be delivered as a **writing skill** named `cicd-pipeline-design` that designs a pipeline, scaffolds or patches the workflow files in the target repository, and audits an existing pipeline.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: operator choices "Entwerfen + scaffolden + prüfen" and "cicd-pipeline-design + cicd-pipeline-reviewer" (settles OQ3, first half)
- **R10** — The specialist SHALL additionally be delivered as a **read-only** review agent named `cicd-pipeline-reviewer` that audits an existing pipeline against the three specs and returns severity-classified findings with `file:line` attribution, applying no edits.
  - _dimension_: `actors` · _status_: `confirmed` · _source_: operator choice "Skill (design/scaffold) + Review-Agent" (settles OQ3, second half)
- **R11** — Both artifacts SHALL be homed in the **`nolte-shared`** plugin at the repository root. The distribution-contract justification is that `spec/project/branching-model/` mandates release workflows in *every* adopting repository, including non-code-bearing ones — this repository itself is non-code-bearing and still runs a `ci.yml` with lint, test, and docs — so the consumer audience is identical to `nolte-shared`'s, and no distribution-contract difference exists that would satisfy `spec/claude/plugin-scoping/` §"When to split into a separate plugin".
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: operator choice "nolte-shared" (settles OQ4)
- **R12** — The CI/CD specs SHALL stay tool-independent and the GitHub Actions spec SHALL be the **only** concrete platform binding; other CI platforms (GitLab CI, Jenkins) and local workflow emulation SHALL be named as non-goals rather than specified.
  - _dimension_: `scope_boundaries` · _status_: `confirmed` · _source_: operator choice "GitHub Actions als einzige Bindung" (settles OQ5)
- **R13** — A pipeline produced or approved by the specialist SHALL be judged primarily by two conditions: every MUST rule of the three specs is checkable against the repository, **and** reproducibility is demonstrable — identical inputs yield the identical artifact, and every CI stage is runnable locally through the same Taskfile target.
  - _dimension_: `acceptance_criteria` · _status_: `confirmed` · _source_: operator choice "Spec-Konformität + nachweisbare Reproduzierbarkeit"
- **R14** — WHEN the specialist detects a finding whose correct remedy belongs upstream in `nolte/gh-plumbing`, it SHALL report a named upstream work package and SHALL NOT patch the consumer repository with a local copy — the same rule `spec/project/workflow-health/` already sets for the `GITHUB_TOKEN` cascade.
  - _dimension_: `edge_cases` · _status_: `confirmed` · _source_: operator choice "Upstream-Work-Package melden, Consumer nicht patchen"
- **R15** — The CD spec's scope SHALL end at the **handover**: building, provenance, immutable publication (release, image, chart, docs), and the rollback contract over artifact versions. Rolling a workload into a cluster SHALL remain with `kubernetes-deployment-best-practices` and `bjw-s-common-chart-deployment`; the CD spec names the handover point as its boundary instead of duplicating those specs.
  - _dimension_: `scope_boundaries` · _status_: `confirmed` · _source_: operator choice "Endet an der Übergabe; Deployment ist Konsument"
- **R16** — The CD spec SHALL define single-stage delivery as the normative model and SHALL describe environment promotion (GitHub Environments, approval gates) as an **optional** pattern for repositories that need it, never as a requirement on all of them.
  - _dimension_: `scope_boundaries` · _status_: `confirmed` · _source_: operator choice "Einstufig, Promotion als optionale Erweiterung"
- **R17** — All three specs SHALL be English-canonical with a synchronized German translation, authored through the `spec` skill, and the GitHub Actions spec's best-practice claims SHALL be backed by triangulated sources per `spec/claude/research-triangulate/`.
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: whole-reading teach-back "Drei EN-kanonische Specs (+DE)" — confirmed; plan §5 invariants

### Domain objects

`pipeline`, `stage`, `job`, `runner`, `trigger`, `pre-merge` / `post-merge`, `build artifact`, `artifact provenance`, `immutability`, `rollback`, `cache key`, `pin` (tag / SHA), `reusable workflow` (`workflow_call`), `composite action`, `permissions scope`, `concurrency group`, `matrix`, `environment`, `promotion`, `local↔CI parity`, `required status check`, `upstream work package`.

## Surviving assumptions / open risks

- **A1 (assumed)** — The artifact-to-securing-stage matrix is keyed by the artifact types `spec/project/release-artifact/` already declares per project type; whether it renders as a table in the CD spec or as per-stage bullets is a spec-authorship detail. _source_: plan §3 "Records the software-artefact → securing-stage matrix (references `release-artifact`)".
- **A2 (assumed)** — The `cicd-pipeline-design` skill dispatches `cicd-pipeline-reviewer` for its `audit` operation rather than re-implementing detection, mirroring the `dockerfile-audit` / `dockerfile-audit-scanner` split. The exact division between agent detection and skill severity judgement is settled during artifact authoring.
- **A3 (assumed)** — "Demonstrable reproducibility" (R13) is evidenced by pinned inputs plus the Taskfile-target parity check, not by a byte-identical rebuild proof; a stronger hermetic-build claim would need tooling the portfolio doesn't have today.
- **A4 (assumed)** — No neighbouring spec needs to be edited to point at the new specs. If `spec-readiness-reviewer` finds a ghost reference or a contradiction, the fix stays a reference addition in the neighbouring spec, never a rule move.
- **Open risk (non-blocking)** — R11 places a pipeline-design capability in `nolte-shared` whose deploy-stage neighbours (`dockerfile-audit`, `deployment-chart-manage`) live in `nolte-engineering`. Specs are repo-wide so no spec boundary is crossed, but a consumer running `nolte-shared` alone will get CD guidance whose deploy-side follow-up capabilities it hasn't installed. The specs must name that follow-up explicitly rather than assume it's reachable.
- **Open risk (non-blocking)** — Efficiency stays a guide (R7). If a repository's pipeline later becomes slow enough to block merges, there's no normative threshold to appeal to; the remedy would be a spec revision, not an operator override.
