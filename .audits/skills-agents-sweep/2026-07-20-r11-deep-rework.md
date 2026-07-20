---
artifact-type: skills-agents-sweep
slug: 2026-07-20-r11-deep-rework
repo-revision: 97048dd84aa59f4dad7773c5ece1ed30f7cb49b1
scope: full
inventory:
  skills: 59
  agents: 54
  total: 113
per-artefact-plans: 113
status: closed
created: "2026-07-20"
feature: F-17
roadmap_item: R-11
issue: 416
---

# Consolidated skills/agents sweep — R-11 deep-rework analysis gate

## Scope

Full-inventory sweep of all **113 shared artefacts** (59 skills + 54 agents across
nolte-shared, nolte-engineering, nolte-media) at repo-revision `97048dd`. This is
the analysis gate for **F-17 / roadmap R-11**: it surfaces whether any shared
agent or skill warrants **deep rework beyond its description** (merge / split /
retire / rewrite) so R-11's deferred per-candidate-rework strand (P2) can act on
evidence.

Phase 1 was run as a parallel per-artefact triage (one review agent per artefact,
each judging only structural deep-rework signals — description wording was out of
scope, already normalised by F-7). The per-artefact results are the evidence base:
`2026-07-20-r11-deep-rework-per-artefact.md` (one row per artefact). Note: the
phase-1 pass produced the deep-rework signal per artefact rather than a full
`skill-review`/`agent-review` plan per artefact under `.audits/{skill,agent}-review/`;
the triage was scoped to the rework decision F-17 needs, and the row-per-artefact
table stands in as the reusable evidence.

## Executive summary

**No artefact warrants deep rework. All 113 returned `verdict: none`.** This
confirms the F-5 focused analysis (`.audits/shared-plugin-analysis/2026-07-19.md`),
which found no duplicate capabilities and clean family clusters — the full
per-artefact pass reaches the same conclusion with per-artefact evidence.

| Top finding | Count | Class |
|---|---|---|
| Artefacts warranting deep rework (merge/split/retire/rewrite) | **0** | — |
| Artefacts well-formed and correctly scoped (`none`) | 113 | clean |
| Minor conformance / polish observations (non-rework) | 79 | Info (deferrable) |
| Boundary conflicts (true merge/split candidates) | 0 | clean |
| Spec-induced gaps (phantom spec references) | 1 | Info (deferrable) |
| Skill-vs-agent misclassifications | 0 | clean |

**Go / no-go:** **GO to close R-11's deep-rework strand (P2).** No rework features
are warranted; the strand's charter outcome ("act on surfaced candidates") is
satisfied by the evidence-based finding that there are none. R-11's remaining open
work is the independent authoring-slice carve-out decision (F-18). The 79 minor
observations are a **deferrable polish backlog** (Info-level, non-release-blocking),
captured in §Wave-based roadmap.

## Artefact inventory

| Plugin | Skills | Agents |
|---|---:|---:|
| nolte-shared | 45 | 23 |
| nolte-engineering | 12 | 29 |
| nolte-media | 2 | 2 |
| **Total** | **59** | **54** |

Per-artefact verdicts: `2026-07-20-r11-deep-rework-per-artefact.md`.

## Boundary matrix

The triage looked for pairs whose capability (not merely adjacent trigger phrasing)
genuinely overlaps enough to warrant a merge or split. **None found.** Every
adjacency the agents flagged is a *documented, reciprocal* boundary, not a
conflict:

- **Scanner ↔ orchestrating-skill pairs** (dependency-audit↔dependency-audit-scanner,
  dockerfile-audit↔dockerfile-audit-scanner, observability-audit↔…-scanner,
  license-check↔…-scanner, kpi-derive↔kpi-signal-scanner,
  release-regression-scope↔…-scanner): read-only detect vs. orchestrate/write —
  crisp division, no merge candidate.
- **Generator ↔ reviewer test-tier pairs** (unit/integration/component/contract/e2e):
  deliberate symmetric contract; distinct jobs.
- **audience-identify.validate ↔ audience-review**: inline check-and-fix owned by the
  writing skill vs. isolated read-only review-plan — defensibly distinct.
- **dependency-audit license pass ↔ license-check**: explicit reciprocal
  `dont_use_when`; dependency-audit scopes to the dependency slice, license-check owns
  the full pipeline.
- **lektorat-scanner D4 ↔ prose-vale-curator §5a voice check**: bounded adjacency,
  prose-vale-curator defers deep style analysis to lektorat-scanner.

Result: no merge, split, or rename warranted on boundary grounds.

## Spec-induced gap inventory

- **prose-vale-curator → `spec/vocabulary-and-style-curation/`** (Info): the agent's
  Precondition 5 references a spec path that does not exist under `spec/`. Either the
  reference is stale (fix the pointer) or the spec is a genuine phantom to author.
  Non-blocking; captured as polish item PB-3.

No other phantom spec references surfaced: the triage confirmed the governing spec
exists for every other artefact that cites one.

## Adoption-friction analysis

No blocking adoption friction. Minor observations only: a few skills lean on
`references/` + `examples/` for load-bearing detail (skill-agent-catalog-apply,
tech-stack-capture) — this is spec-conformant leanness per skill-management, not a
gap.

## Skill-vs-agent classification

**Zero misclassifications.** Every artefact carries the mandated
`## Why this is a {skill|agent}, not a{n} {agent|skill}` rationale with a named
counter-dimension, and the type is defensible in each case (read-only reviewers as
agents; interactive/persistent-artefact orchestrators as skills). The documented
name-form exceptions (`audience-review`, `png-to-transparent-svg`) were correctly
not flagged.

## Wave-based implementation roadmap

**Wave 0 — deep-rework decision (this analysis): IMPLEMENTED.**
Finding: no artefact warrants merge/split/retire/rewrite. R-11's P2 strand closes
with zero rework features. → this sweep report is the evidence.

**Wave 1 — optional polish backlog (Info-level, non-blocking): DEFERRED.**
The 79 minor conformance notes cluster into cheap mechanical sweeps; none affects
routing or capability, none is release-blocking. Deferred as a low-priority polish
backlog (no separate tracking issue required at Info level; a future
`continuous-improvement-triage` run or a small `chore` can pick them up):

- **PB-1 — MCP-tool prose lag:** `dependency-audit-scanner`, `vocab-drift-scanner`,
  `portfolio-manifest-collector` enumerate their tool set in body prose without the
  MCP read tools the frontmatter now grants (F-13 aftermath). Mechanical prose sync.
- **PB-2 — cross-plugin agent placement:** `gdpr-data-protection-reviewer` and
  `quality-gate-enforcer` live in `nolte-shared/agents/` while their family
  (`code-security-reviewer`, `dependency-audit`, the `quality-gate` skill) lives in
  `nolte-engineering`. A plugin-scoping placement question — **feeds F-18's boundary
  discussion**, not a rework of the agents themselves.
- **PB-3 — phantom spec ref:** `prose-vale-curator` → `spec/vocabulary-and-style-curation/`
  (see §Spec-induced gaps).
- **PB-4 — body/frontmatter op-count drift:** `portfolio-audit` (3 advertised vs 4
  defined), `implementation-plan-author` (write-effects table vs audit-path output),
  and similar minor internal inconsistencies.
- **PB-5 — spec restatement in bodies:** `blog-author` restates readability/LIX/
  typography owned by `post-writing-style` / `readability-lix`; trim toward pointers.
- **PB-6 — template/heading nits:** `spec-drift-audit` template omits the mandated
  `## Summary`; a few `dont_use_when`/description pointers name a spec rather than a
  sibling skill/agent. Cosmetic.

Ordering: Wave 1 is fully independent and optional; no constraint blocks R-11 or
F-18 on it.

## Processing log

- 2026-07-20 — W0 — implemented — verified: full 113-artefact parallel triage at
  `97048dd`; 0 rework candidates (`2026-07-20-r11-deep-rework-per-artefact.md`).
- 2026-07-20 — W1 — deferred — verified: 79 Info-level notes catalogued as PB-1..PB-6;
  non-blocking, no tracking issue required at Info level.

> Note: this report is retained on disk (not deleted per the sweep spec's `close`
> operation) because F-17 acceptance-1 requires the consolidated report to persist
> as the feature's evidence artefact.
