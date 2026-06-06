---
type: decision-log
title: Disposition — tech-stack documentation rendering + AC8 Benefits/backlink
created: 2026-06-06
context: >
  A portfolio-wide spec-drift sweep raised two SHOULD-class warnings against the
  tech-stack inventory: (1) tech-stack-discovery §AC8 — the rendered portfolio
  documentation page must include the §Benefits section (verbatim or paraphrased)
  with a backlink to the discovery spec; and (2) tech-stack §Documentation
  rendering — the rendered portfolio inventory must carry a "Global tech stack"
  section plus per-Portfolio-Member tech-stack subsections with
  inherited/repo-specific/suppressed/regrouped badges, group-first ordering, and
  a Mermaid kind-distribution. Neither is currently rendered: scripts/docs/
  gen_portfolio.py references neither `tech_stack` nor `Benefits`, and
  portfolio/aggregate.yml carries no `tech_stack` data.
---

# Decision log — tech-stack rendering disposition (2026-06-06)

## Facts established

1. **Both governing specs are `draft`.** `spec/portfolio/tech-stack/en.md` and
   `spec/portfolio/tech-stack-discovery/en.md` both carry `Status: draft` at this
   revision. Neither has been promoted to `accepted`.

2. **The rendering requirement is a generated-output MUST, not a hand-authored
   page.** `spec/portfolio/tech-stack/` §Documentation rendering states the
   tech-stack inventory **MUST be generated automatically from
   `portfolio/tech-stack.yml` plus every Portfolio-Member's
   `project/portfolio.yml`** and the rendered files **MUST NOT be hand-edited.**
   `docs/<lang>/portfolio/index.md` is produced by `scripts/docs/gen_portfolio.py`
   from the committed `portfolio/aggregate.yml` snapshot and is verified fresh in
   CI via `git diff --exit-code`. A hand-authored tech-stack page under
   `docs/<lang>/portfolio/` would therefore directly violate the MUST-NOT and be
   overwritten/flagged by the generator on the next `task docs:portfolio` run.

3. **The data the renderer would need does not exist yet.** The render is a pure
   function of `portfolio/aggregate.yml`. That snapshot is populated by the
   `portfolio-audit` skill's Render operation and currently carries no
   `tech_stack` block for any member (`grep tech_stack portfolio/aggregate.yml`
   returns nothing). Rendering the global stack + per-repo effective-stack +
   delta view + kind-distribution Mermaid requires the Render operation to first
   aggregate each member's `tech_stack:` block (inherited resolution, override
   suppression, regroup re-classification) into the snapshot. That aggregation
   pipeline is not implemented.

4. **The full rendering contract is substantial.** §Documentation rendering
   demands: a top-level "Global tech stack" section preceding the per-repo
   inventory; per-consumer effective-stack with four badge classes
   (inherited / repo-specific / suppressed-with-rationale / regrouped-with-
   before-after-group-and-rationale); group-first then kind-second ordering; a
   SHOULD kind-distribution Mermaid; and a SHOULD per-consumer delta view. This
   is a generator subsystem comparable in size to the existing capability
   renderer, not a section append.

## Decision

**Defer implementation; do not build a partial or hand-authored page now.**
Recorded as a deliberate disposition rather than actioned, because every
available "fix" is worse than the documented gap:

- A hand-authored `docs/<lang>/portfolio/` page violates the §Documentation
  rendering MUST-NOT (hand-edit) and is non-durable (overwritten by the
  generator, flagged by the CI freshness gate).
- A partial generator extension that renders a tech-stack section from empty
  `aggregate.yml` data would emit an empty or misleading section and couples the
  renderer to a snapshot shape the `portfolio-audit` Render operation does not
  yet produce — building drift in the opposite direction.
- Both governing specs are still `draft`; the rendering contract (badge
  vocabulary, ordering, delta view) may still shift before promotion.

## Implementation trigger (when this disposition is discharged)

Implement the rendering in one coordinated change, gated on **all** of:

1. `spec/portfolio/tech-stack/` and `spec/portfolio/tech-stack-discovery/`
   promoted from `draft` to `accepted` (the rendering contract is then frozen).
2. The `portfolio-audit` Render operation extended to aggregate each member's
   resolved effective `tech_stack:` (inherited + additions − overrides, with
   regroup applied) into `portfolio/aggregate.yml` under a `tech_stack` key per
   member plus a top-level `global_tech_stack` block.
3. `scripts/docs/gen_portfolio.py` extended to render, from that snapshot:
   - a top-level "Global tech stack" section (group-first, kind-second);
   - per-member effective-stack subsections with the four badge classes;
   - the SHOULD kind-distribution Mermaid (per `spec/project/mermaid-diagrams/`,
     with the mandatory `<!-- diagram-source: ... -->` comment);
   - the SHOULD per-consumer delta view;
   - **and** (tech-stack-discovery §AC8) a §Benefits paraphrase with a backlink
     to `spec/portfolio/tech-stack-discovery/` — this is the cheapest of the
     requirements and lands in the same generator change.
4. EN + DE parity via the existing per-language `L` chrome table in
   `gen_portfolio.py`; spec-conformant frontmatter is already emitted by
   `render_page` (`audience`, `content_mode`, `track`, `last_updated`).

Until the trigger is met, the two warnings stand as known-and-accepted gaps
against `draft` specs, tracked by this decision-log entry. AC8's Benefits/
backlink requirement is intentionally bundled into the same generator change
rather than hand-authored separately, because the only spec-conformant home for
it is the generated `docs/<lang>/portfolio/` page, which MUST NOT be hand-edited.
