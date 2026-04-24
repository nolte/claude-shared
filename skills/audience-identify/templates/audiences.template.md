# Audiences — {{Context Name}}

<!--
Produced via the `audience-identify` skill, following
spec/project/audience-identification/.
Do not add audiences without first declaring the bounded context below.
-->

## Bounded context

<!-- What this module/service/library/project *is*, where its boundaries run,
     what is explicitly outside. One short paragraph or a bullet list. -->

-

## Audiences

Each entry: label, relationship category, interaction surface, expectation,
open questions, `confirmed` or `assumed`, criticality (primary / secondary /
peripheral). Mark a whole category as `none — <reason>` when it does not apply.

### Direct consumers

- **{{Label}}** — _category_: direct-consumer · _surface_: {{API / CLI / …}} ·
  _expects_: {{what they need}} · _status_: `assumed` · _criticality_: {{primary|secondary|peripheral}}
  - Open questions: {{list, or "none"}}

### Operators

-

### Contributors / maintainers

-

### Governing parties

-

### Indirect audiences

-

## Open questions (cross-cutting)

<!-- Questions that do not belong to a single audience entry. -->

-

## Revisit triggers

<!-- Events that should cause this list to be re-run via the `revisit` op:
     new public API, new deployment target, new regulated data class, new stakeholder, ... -->

-
