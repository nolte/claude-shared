# Requirements — Consolidated skill/agent frontmatter field spec (descriptive, with provenance + JSON-Schema companion)

<!--
Produced via the `requirements-elicit` skill, following
spec/project/requirements-elicitation/.
`c_d` is an uncertainty proxy (self-consistency-derived), not a calibrated
probability. A requirement is `confirmed` only after an explicit teach-back.
-->

## Bounded context

- **What is being built:** two coupled, *descriptive* artefacts —
  1. a **bilingual spec** `spec/claude/skill-agent-frontmatter/` (EN-canonical `en.md` +
     DE `de.md`, `Scope: local`) that documents the **complete skill- and agent-frontmatter
     field set** in one consolidated reference: for every field its task, type, limits,
     required/optional status, an explicit **provenance marker** (Anthropic/Claude-Code
     standard — with upstream source — vs. nolte-local invention), and a back-reference to
     the field's **normative owner** spec; plus the standard-vs-invention taxonomy and a
     **§Maintenance** process for keeping the doc in sync; and
  2. a **machine-readable JSON-Schema companion** `schemas/skill-agent-frontmatter-v1.0.schema.yaml`
     (JSON-Schema draft 2020-12, house style of `spec-config-v1.0` / `tech-stack-v1.0`) that
     encodes the **parse-error class** (field presence, type, limits, enum) only.
- **Normative model (load-bearing, Q2):** **Model A — descriptive/aggregating.** The new
  spec is a per-field map + provenance + maintenance process; it *points back* to the three
  existing owners (`skill-management`, `agent-management`, `skill-agent-catalog`) as the
  authoritative source of each rule and does **not** restate validator-backed limits as a
  second source of truth. The JSON-Schema stays structural (parse-error class), semantics
  remain with the owners — consistent with Model A.
- **For whom:** spec readers and skill/agent authors who need one field reference; the
  `validate_skills.py` maintainer and the `skill-agent-catalog` spec (the sync counterparts).
- **Explicitly out of scope:** any change to `validate_skills.py` behaviour now (descriptive
  spec, not new tooling — the schema is a companion the validator *could later* consume, a
  §Maintenance follow-up); trimming/refactoring the three existing owner specs (that would be
  Model B, rejected); portfolio-wide scope (this is `local`, like the other `spec/claude/` topics).

## Understanding KPI

- Thresholds: `τ_low = 0.4`, `τ_high = 0.8`, self-consistency `k = 2`, question budget = `~6`
  (spec defaults; unchanged).
- `U_gate = min_d c_d` over required dimensions = **0.85**. The plan (`.resume/frontmatter-field-spec/plan.md`)
  had already researched the current-state map (three owner specs + `validate_skills.py` +
  the schema precedents) and the standard-vs-invention taxonomy, so the interview was pure
  **specification uncertainty** at six decision points. All six settled: Q2/Q3/Q4 by explicit
  option/answer sign-off, Q1/Q5/Q6 by default-assumption confirmed in the consolidated
  teach-back ("ja passt").
- Termination: **saturation.** All six open questions of plan §3 are resolved; only narrow
  spec-authoring detail remains (exact per-field wording, schema field enumeration), routed to
  the `/nolte-shared:spec` authoring step, not to the operator.

### Gap matrix

| Dimension | Applicable | `c_d` | Uncertainty source | Evidence event |
|---|---|---|---|---|
| `functional` | yes | 0.88 | specification | Q1–Q5 sign-off: per-field reference (task/type/limits/req/provenance/owner) + taxonomy + §Maintenance + JSON-Schema companion |
| `non_functional` | yes | 0.85 | interpretation | Descriptive-not-tooling + Model A DRY/no-drift + schema in house style (plan §3/§5); teach-back "ja passt" |
| `constraints` | yes | 0.86 | interpretation | EN-canonical (`.spec-config.yml`), `Scope: local`, `/nolte-shared:spec` authoring, Vale-from-worktree (plan §5) |
| `domain_objects` | yes | 0.87 | specification | The frontmatter field set (skill+agent), the provenance marker, the two artefacts (prose spec + JSON-Schema); Q3/Q4 sign-off |
| `actors` | yes | 0.84 | interpretation | Teach-back: spec readers, skill/agent authors, `validate_skills.py` maintainer, `skill-agent-catalog` |
| `acceptance_criteria` | yes | 0.85 | interpretation | Q5 + plan §4: `task test`, Vale-clean, spec index regenerated, three owners cross-linked, schema validates |
| `edge_cases` | yes | 0.82 | specification | Overlapping skill/agent fields ("applies-to" column), Model-A-vs-schema-normativity tension resolved (parse-error class only), `_translation-pending` catalog fields |
| `scope_boundaries` | yes | 0.87 | interpretation | Q2 (Model A, no owner refactor) + descriptive-not-tooling (no `validate_skills.py` change) + `local` scope; teach-back confirmed |

## Requirements

<!-- EARS/CNL form; tagged confirmed/assumed with traceability. -->

### Spec (EN canonical + DE in sync)

- **R1** — WHEN the field spec is authored, it SHALL exist as
  `spec/claude/skill-agent-frontmatter/en.md` (canonical) + `de.md` (strict translation),
  `Scope: local`, produced via the `/nolte-shared:spec` authoring/translation path.
  - _dimension_: `constraints`, `functional` · _status_: `confirmed` (Q1) · _source_: plan §1 + teach-back "ja passt"
- **R2** — WHEN the spec documents a field, it SHALL record, per field, its **task/purpose,
  type, limits, required/optional status, a provenance marker, and a back-reference to the
  normative owner spec** — and SHALL NOT restate a validator-backed limit as a new source of
  truth (Model A: it maps and points, it does not fork the rule).
  - _dimension_: `functional`, `non_functional` · _status_: `confirmed` (Q2) · _source_: Q2 sign-off "A — beschreibend/aggregierend"
- **R3** — WHEN the spec is scoped, it SHALL cover **both skills and agents in one document**,
  using a shared table with an "applies-to" axis (`skill` / `agent` / `both`) so overlapping
  fields (`name`, `description`, `model`, the catalog fields) and their shared provenance are
  told once, not twice.
  - _dimension_: `domain_objects`, `scope_boundaries` · _status_: `confirmed` (Q3) · _source_: Q3 answer "skill und agent mit entstehen"
- **R4** — WHEN the spec presents provenance, it SHALL carry an explicit **standard-vs-invention
  taxonomy**: **Standard** = `name`, `description` (Agent Skills spec, R1) and the Claude-Code
  optional fields `when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`,
  `user-invocable`, `allowed-tools`, `model`, `effort`, `context`, `agent`, `hooks`, `paths`,
  `shell` (R3), plus agent-only `tools`, `color`; **nolte-invention** = `distribution`, `tags`,
  `phase`, `summary`, `summary_<lang>`, `use_when`, `dont_use_when`, `see_also`, `examples`,
  `resumable`. Each standard field SHALL cite its upstream source (R1–R6).
  - _dimension_: `functional`, `domain_objects` · _status_: `confirmed` · _source_: plan §2 taxonomy + Q2/Q4 sign-off
- **R5** — WHEN the spec defines maintenance, it SHALL contain a **§Maintenance** section that
  binds, for any new or changed field: (i) a **provenance review** (standard-with-upstream-proof
  vs. nolte-invention), (ii) a **sync gate** keeping the doc aligned with `validate_skills.py`,
  the **JSON-Schema companion (R7)**, and the `skill-agent-catalog` spec, and (iii) a **PR
  checklist item**.
  - _dimension_: `functional`, `acceptance_criteria` · _status_: `confirmed` (Q5) · _source_: Q5 teach-back confirmed
- **R6** — WHEN the canonical `en.md` is authored, `de.md` SHALL be kept in strict sync via the
  `/nolte-shared:spec` translation path, with the parity/drift check passing (EN canonical per
  `.spec-config.yml`).
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: plan §5 invariants

### JSON-Schema companion

- **R7** — WHEN the machine-readable companion is authored, it SHALL exist as
  `schemas/skill-agent-frontmatter-v1.0.schema.yaml` (JSON-Schema draft 2020-12), in the
  house style of `schemas/spec-config-v1.0.schema.yaml` /
  `portfolio/schemas/tech-stack-v1.0.schema.yaml`, encoding **only the parse-error class**
  (field presence, type, limits, enum) — semantics remain with the owner specs (Model A
  consistency). It is a companion the validator MAY later consume; wiring it into
  `validate_skills.py` is a §Maintenance follow-up, not part of this change.
  - _dimension_: `functional`, `scope_boundaries` · _status_: `confirmed` (Q4) · _source_: Q4 answer "Prosa + JSON-Schema"

### Process / quality

- **R8** — WHEN the change is prepared for review, `task test` SHALL be green, the changed spec
  prose SHALL be Vale-clean (run **from the worktree**), the spec index SHALL be regenerated,
  the three existing owner specs (`skill-management`, `agent-management`, `skill-agent-catalog`)
  SHALL be cross-linked to the new spec, and the PR SHALL autolink the new spec.
  - _dimension_: `acceptance_criteria` · _status_: `confirmed` · _source_: plan §4 steps 4–6

## Surviving assumptions / open risks

**Resolved (settled by explicit sign-off Q2/Q3/Q4 + consolidated teach-back "ja passt"):**

- ✅ **Q1 (slug/location):** `spec/claude/skill-agent-frontmatter/` (EN + DE), `Scope: local`.
- ✅ **Q2 (normative model):** **A — descriptive/aggregating.** New spec maps and back-references;
  the three owner specs stay the source of truth. No owner refactor (Model B rejected).
- ✅ **Q3 (coverage):** skills **and** agents in one document, shared table with an applies-to axis.
- ✅ **Q4 (form):** prose **and** a JSON-Schema companion (parse-error class only).
- ✅ **Q5 (maintenance):** §Maintenance section — provenance review + sync gate
  (`validate_skills.py` + JSON-Schema + `skill-agent-catalog`) + PR checklist item.
- ✅ **Q6 (portfolio scope):** `local`.

**Remaining residual risk (narrow spec-authoring detail; routed to `/nolte-shared:spec`, NOT to the operator):**

- **Exact per-field wording and the full field enumeration** (including any field the plan's
  survey missed) — reconciled against `skill-management` §, `agent-management` §, and
  `skill-agent-catalog` § during authoring; the spec points to the owner for each limit.
- **JSON-Schema field list** — which fields get a schema constraint vs. prose-only mention;
  keep it to the mechanically-checkable subset (presence/type/limit/enum), matching the
  parse-error-class ceiling of the precedent schemas.
- **Model-A-vs-schema tension** — the schema is machine-normative for structure but MUST NOT
  encode semantics that would fork an owner's rule; the §Maintenance sync gate is what keeps
  the schema honest to the owners.

**Constraint reminders (confirmed, not risks):** EN canonical + DE in sync; primary checkout
stays on `develop` (all work in this worktree); spec authoring/translation goes through
`/nolte-shared:spec`; Vale runs from the worktree; new vocabulary goes into the tracked
`accept.txt`, not inline waivers.
