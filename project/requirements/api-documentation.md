# Requirements — API documentation capability (spec + audit tooling)

<!--
Produced via the `requirements-elicit` skill, following
spec/project/requirements-elicitation/.
Elicited 2026-07-24 in worktree feat/api-documentation-spec as the plan-mandated
gate before authoring. `c_d` is an uncertainty proxy (self-consistency-derived),
not a calibrated probability. A requirement is `confirmed` only after an explicit
teach-back / authoritative operator choice.
-->

## Bounded context

- **What:** One capability delivered in one PR: a normative spec
  `spec/project/api-documentation/` (OpenAPI documentation best practices — how an
  API must be documented so a review can check conformance) plus the
  operationalizing tooling in `nolte-engineering`: a read-only scanner agent and an
  audit skill, following the established `dockerfile-audit` /
  `observability-audit` capability pattern.
- **For whom:** Code repositories in the nolte portfolio that ship an HTTP API,
  and the operator auditing them.
- **Out of scope:** a new plugin, manual version bumps, `marketplace.json`
  changes; writing the API documentation itself (the capability specifies and
  audits, it does not author).
- **Origin:** worktree plan `.resume/api-documentation/plan.md` (operator-authored),
  open questions OQ-1..OQ-6 resolved in this elicitation.

## Understanding KPI

- Thresholds: `τ_low = 0.4`, `τ_high = 0.8`, self-consistency `k = 2`, question
  budget = `8` (5 turns; spec defaults, unchanged)
- `U_gate = min_d c_d` over required dimensions = **0.80**
- Termination: `saturation` (all eight dimensions ≥ `τ_high` via authoritative
  operator choices and teach-backs; question budget fully used: 8/8)

### Gap matrix

| Dimension | Applicable | `c_d` | Uncertainty source | Evidence event |
|---|---|---|---|---|
| `functional` | yes | 0.85 | specification | Operator choices OQ-1..OQ-4 fix the spec's normative content; plan §3 coverage list confirmed via context teach-back |
| `non_functional` | yes | 0.80 | interpretation | Plan §5 invariants (Vale/LIX prose gates, EN-canonical + DE lockstep, description budget) — CI-enforced repo conventions |
| `constraints` | yes | 0.85 | interpretation | Context teach-back "Ja, exakt": one PR, no new plugin, no version bumps, `marketplace.json` untouched; sibling-pattern conformance |
| `domain_objects` | yes | 0.82 | specification | Operator choice OQ-2 (version floor) fixes the OpenAPI object vocabulary; error-response objects delegated to `api-error-handling` |
| `actors` | yes | 0.80 | interpretation | Context teach-back: portfolio code repos shipping an HTTP API (consumers), operator (invokes audit), read-only scanner agent |
| `acceptance_criteria` | yes | 0.82 | specification | Operator choice OQ-4 (Spectral reference, SHOULD gate) + sibling-capability acceptance pattern (validator-clean, `task test`/`task lint` green) |
| `edge_cases` | yes | 0.85 | specification | Operator choices: no-spec-file → critical finding; final teach-back confirmed multi-file entry-point rule and per-file audit |
| `scope_boundaries` | yes | 0.88 | specification | Operator choice OQ-1 (OpenAPI-only, others Non-Goals) + known `yaml-json-schema` boundary (plan §2) |

## Requirements

- **R1** — The capability SHALL be delivered as three artifacts in one PR: the
  normative spec `spec/project/api-documentation/` (EN canonical + DE
  translation), a read-only scanner agent, and an audit skill in
  `nolte-engineering`, mirroring the `dockerfile-audit` capability pattern.
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: context teach-back "Ja, exakt"
- **R2** — The spec SHALL normatively cover OpenAPI/REST documentation only;
  AsyncAPI, GraphQL, and gRPC documentation SHALL be named as explicit Non-Goals
  with a growth note (own profiles/specs when the need arises).
  - _dimension_: `scope_boundaries` · _status_: `confirmed` · _source_: OQ-1 operator choice "OpenAPI-only"
- **R3** — WHEN a repository publishes an OpenAPI document, it MUST be OpenAPI
  3.0 or higher (Swagger 2.0 is a finding) and SHOULD target 3.1.
  - _dimension_: `domain_objects` · _status_: `confirmed` · _source_: OQ-2 operator choice "≥3.0, SHOULD 3.1"
- **R4** — The spec SHALL be neutral between spec-first and code-first flavours:
  all quality requirements apply to the published OpenAPI artifact regardless of
  how it is produced; WHEN a repository is code-first, the generated spec MUST be
  reproducibly exportable so the scanner and CI can audit it.
  - _dimension_: `edge_cases` · _status_: `confirmed` · _source_: OQ-3 operator choice "Neutral"
- **R5** — WHEN the audited repository ships an HTTP API but no OpenAPI document
  is discoverable (neither checked in nor exportable), the audit SHALL record
  this as its most severe (critical) finding and continue; it SHALL NOT abort or
  silently skip.
  - _dimension_: `edge_cases` · _status_: `confirmed` · _source_: edge-case operator choice "Critical-Finding"
- **R6** — The spec's requirement catalog SHALL cover: spec-file presence,
  location, and naming; the OpenAPI version floor (R3); `info` completeness; a
  per-operation contract (`operationId`, tags, summaries, descriptions,
  parameter documentation); schema hygiene (examples, response schemas for all
  documented status codes); security-scheme documentation; the lint gate (R7);
  and a published-spec-vs-runtime drift rule anchored in `docs-freshness`'s
  optional repo-level category. Error-response documentation SHALL reference
  `spec/project/api-error-handling/` instead of duplicating it.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: plan §3 coverage list, confirmed via context teach-back + OQ choices
- **R7** — The spec SHALL name Spectral as the reference linter in a
  tool-agnostic core (reference, never required); a CI lint gate over the
  OpenAPI document SHALL be a SHOULD, consistent with the sibling capabilities'
  advisory audit nature.
  - _dimension_: `acceptance_criteria` · _status_: `confirmed` · _source_: OQ-4 operator choice "Spectral, SHOULD"
- **R8** — Multi-file OpenAPI documents (`$ref`-split) SHALL be permitted, WHEN
  used a canonical entry-point document MUST be discoverable and bundleable.
  - _dimension_: `edge_cases` · _status_: `confirmed` · _source_: final teach-back "Ja, beide" (a)
- **R9** — WHEN the scanner discovers multiple OpenAPI documents in one
  repository, it SHALL audit each one and report findings per document.
  - _dimension_: `edge_cases` · _status_: `confirmed` · _source_: final teach-back "Ja, beide" (b)
- **R10** — The same PR SHALL add cross-reference pointers in
  `api-error-handling` (References), `source-code-review` (dimension D8),
  `docs-freshness` (optional category), and check the `yaml-json-schema`
  boundary wording — EN + DE in lockstep — plus a minimal see-also/body note in
  the `api-error-check` skill (no content rework).
  - _dimension_: `functional` · _status_: `confirmed` · _source_: plan §4 step 4 + OQ-6 operator choice "Ja, minimal"
- **R11** — The scanner agent SHALL be read-only (Read/Grep/Glob), detection
  only; all disk writes (the `.audits/` report) stay with the audit skill. Both
  artifacts SHALL pass `scripts/validate_skills.py`, follow
  `spec/claude/skill-agent-naming/`, and keep the agent `description` within the
  CI-guarded budget (baseline 18535).
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: plan §5 invariants (CI-enforced), context teach-back
- **R12** — The primary actors are: consumer code repositories shipping an HTTP
  API (spec addressees), the operator invoking the audit skill, and the
  read-only scanner agent dispatched by it.
  - _dimension_: `actors` · _status_: `confirmed` · _source_: context teach-back "Ja, exakt"

### Domain objects

`OpenAPI document`, `entry-point document`, `$ref` / bundling, `info` object,
`operation` (`operationId`, tags, summary, description), `parameter`,
`response schema`, `components.schemas`, `security scheme`, `Spectral ruleset`,
`lint gate`, `spec-vs-runtime drift`, `audit report`, `finding severity`.

## Surviving assumptions / open risks

- **A1 (assumed)** — Artifact names: skill `api-documentation-audit`
  (`<object-noun>-<action>`), agent `api-documentation-scanner`
  (`<subject>-<role-noun>`), per `spec/claude/skill-agent-naming/` and the
  `observability-audit` precedent. Mechanically checkable (OQ-5): to be
  validated against the naming spec and `scripts/validate_skills.py` during
  authoring; not worth an interview question.
- **A2 (assumed)** — Prose gates apply as to every spec: EN-canonical
  (`.spec-config.yml`), DE shipped in the same PR, Vale error-level rules
  (contractions, unspaced em-dashes not adjacent to code/bold), LIX
  readability. CI is authoritative where local Vale is unsyncable.
- **A3 (assumed)** — The audit skill writes its report under `.audits/` using
  the Critical / Warning / Suggestion / Info severity ladder of the sibling
  audit capabilities; exact report layout is a spec-authorship detail.
- **Open risk (non-blocking)** — Whether `test-tier-contract` and
  `backstage-catalog-generation` should gain reciprocal pointers to the new
  spec is left to authoring-time judgment (plan §2 names them as adjacent prior
  art, not as mandated cross-references).
