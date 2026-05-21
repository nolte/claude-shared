---
audit-type: skills-agents-sweep
target: <plugin-name> (<namespace> plugin)
scope: all <N> skills + <M> agents
repo-revision: <git-sha>
created: <ISO-date>
status: open
per-artefact-plans: <count> (under .audits/skill-review/ and .audits/agent-review/)
---

# Skills & Agents Sweep Audit — <slug>

## Scope

Portfolio-wide sweep of all <N> skills (`skills/<name>/SKILL.md`) and <M> agents (`agents/<name>.md`) in the `<namespace>` plugin, run against `spec/claude/skill-management/`, `spec/claude/agent-management/`, `spec/claude/skill-vs-agent/`, `spec/claude/skill-review/`, `spec/claude/agent-review/`, and `spec/claude/review-plan/`.

Three analysis streams:

1. **Per-artefact reviews** (<count> plan files under `.audits/skill-review/*.md` and `.audits/agent-review/*.md`) — each produced per `skill-review` / `agent-review` methodology.
2. **Cross-cutting: boundaries and gaps** — overlaps, workflow chains, gap inventory, skill-vs-agent classification.
3. **Cross-cutting: adoption friction and consistency** — preconditions, setup, trigger language, naming, operations vocabulary, spec binding, section naming.

**Validator override:** `skills-ref` CLI is not provisioned in this repository (`Taskfile.yml` contains no corresponding target). Per `spec/claude/skill-review/` the suppression is documented in each per-skill plan.

**Out of scope:** live behaviour of skills or agents; Vale and Markdown style (own tooling chain); external plugin consumers.

---

## Executive Summary

### Top Findings by Severity and Leverage

| # | Finding | Severity | Leverage | Proposal |
|---|---|---|---|---|
| 1 | <!-- highest-impact Critical finding --> | Critical | High | <!-- one-line proposal --> |
| 2 | <!-- second Critical or high-Warning --> | Critical / Warning | High / Medium | <!-- proposal --> |
| 3 | <!-- ... --> | | | |

Per-artefact plan paths for traceability:

- Skills: `.audits/skill-review/<name>.md` (one file per reviewed skill)
- Agents: `.audits/agent-review/<name>.md` (one file per reviewed agent)

### Tally by Class

| Class | Count | PASS | CONDITIONAL | FAIL | Critical Total | Warning Total |
|---|---|---|---|---|---|---|
| Skills | <N> | | | | | |
| Agents | <M> | | | | | |

### Go/No-Go

<!-- State whether Critical findings block release promotion. Example:
FAIL for current release promotion without addressing Critical clusters #1 and #2.
Both clusters are mechanically fixable with one focused PR each (see roadmap). -->

---

## Inventory

### Skills (<N>, grouped by lifecycle phase)

| # | Skill | Use case (one sentence) | Phase |
|---|---|---|---|
| 1 | `<name>` | <!-- one-sentence description --> | plan / develop / review / release / operate |

### Agents (<M>, alphabetical)

| # | Agent | Use case (one sentence) | Tools (declared) |
|---|---|---|---|
| 1 | `<name>` | <!-- one-sentence description --> | Read, Write, Edit, ... |

---

## Abgrenzungs-Matrix

### Overlaps (conflicts with trigger collision)

| A | B | Overlap description | Proposal |
|---|---|---|---|
| `<skill-a>` | `<skill-b>` | <!-- describe the trigger overlap --> | <!-- proposed resolution --> |

### Workflow chains (intentional, document for traceability)

```
<skill-a> --> <skill-b> --> <skill-c>
```

### Adjacent without clear "Don't use for" clauses (trigger risk)

| A | B | What the clause misses | Proposal |
|---|---|---|---|
| `<skill-a>` | `<skill-b>` | <!-- gap description --> | <!-- proposed clause text --> |

### Cluster assessment

| Cluster | Status | Note |
|---|---|---|
| <!-- cluster name --> | Clean / Gap | <!-- note --> |

---

## Lücken-Inventar

### Spec-induced gaps (specs exist, skills or agents do not)

| # | What is missing | Where visible | Proposal |
|---|---|---|---|
| L1 | <!-- phantom skill or agent --> | `spec/<topic>/` referenced in <!-- artefact --> | <!-- new skill / spec extension / agent --> |

### Workflow breaks

| # | What is missing | Where | Proposal |
|---|---|---|---|
| W1 | <!-- missing transition or bridge --> | <!-- skill or workflow --> | <!-- description fix or new skill --> |

### Decision-coverage gaps (spec SHOULD or MAY without an operator)

| # | What is missing | Where | Proposal |
|---|---|---|---|
| D1 | <!-- unoperationalised spec requirement --> | `spec/<topic>/` | <!-- proposed skill operation or spec extension --> |

### Trigger gaps (use cases without an entry point)

| # | What is missing | Where | Proposal |
|---|---|---|---|
| T1 | <!-- unlabelled trigger phrase --> | <!-- skill --> | <!-- description addition or new operation --> |

---

## Adoption-Friction

### Setup friction (external tools not in Preconditions)

| Skill | External requirement | Currently documented in | Proposal |
|---|---|---|---|
| `<name>` | <!-- tool --> | <!-- section --> | Dedicated `## Preconditions` block with detection logic |

### Prerequisite chains (implicit dependencies)

<!-- Describe deep prerequisite chains not visible from trigger phrases. -->

### Discovery friction

| Skill | Problem | Proposal |
|---|---|---|
| `<name>` | <!-- naming or scope confusion --> | <!-- description sharpening or catalog change --> |

### Operations-vocabulary inconsistency

| Operation | Skills using it | Deviating names |
|---|---|---|
| `audit` | <!-- list --> | <!-- outliers --> |
| `scaffold` | <!-- list --> | <!-- outliers --> |

### Rationale-section naming

| Variant | Count | Skills |
|---|---|---|
| `## Why this is a skill, not an agent` | <!-- N --> | Standard |
| <!-- variant --> | <!-- N --> | <!-- list --> |

---

## Skill-vs-Agent-Sortierung

### Skills that should be agents per decision rules

| Skill | Rationale |
|---|---|
| `<name>` | <!-- read-only, self-contained, no mid-flow approval --> |

### Agents that should be skills or hybrids

| Agent | Rationale |
|---|---|
| `<name>` | <!-- mid-flow decisions, persistent state --> |

### Hybrid candidates (skill orchestrates, new agent executes)

| Skill | Proposal | Rationale |
|---|---|---|
| `<name>` | + new `<name>-scanner` agent | <!-- context-window, read-only scan --> |

---

## Konsistenz-Findings

### German-trigger distribution

<!-- Classify each artefact: DE triggers in frontmatter (Critical), DE triggers in body section (conformant), generic "also handles German" without body phrases (Suggestion), no DE trigger support (Info). -->

### Naming outliers

| Skill | Outlier dimension | Recommendation |
|---|---|---|
| `<name>` | <!-- agent noun vs. verb form, etc. --> | <!-- rename or document --> |

### Spec binding

| Skill | Problem | Proposal |
|---|---|---|
| `<name>` | No spec, no `spec/` reference | Create `spec/project/<name>/` or mark as implementation-only with rationale |

### Body-section inconsistencies

<!-- List non-standard section heading variants, missing Gotchas sections, missing hard-rules spec-wins clause, etc. -->

---

## Nachgelagerte Umsetzungs-Roadmap

Sorted by effort times impact (strategy: mechanical sweeps first, structural changes last).

### Wave 1 — Mechanical Critical sweeps (one PR per cluster, parallelisable)

| # | Proposed PR title | Content | Effort | Impact |
|---|---|---|---|---|
| W1.1 | `fix(<scope>): <description>` | <!-- artefacts affected --> | XS / S / M / L | High / Medium / Low |

### Wave 2 — Description and boundary sweep

| # | Proposed PR title | Content | Effort | Impact |
|---|---|---|---|---|
| W2.1 | `chore(<scope>): <description>` | <!-- artefacts affected --> | | |

### Wave 3 — Spec extensions (precondition for structural changes)

| # | Spec PR | Content | Effort | Impact |
|---|---|---|---|---|
| W3.1 | `feat(spec): <description>` | <!-- spec path and change --> | | |

### Wave 4 — Structural new artefacts (gap-closing)

| # | What | Effort | Impact | Rationale |
|---|---|---|---|---|
| W4.1 | New skill `<name>` | L | High | <!-- spec path, referencing artefacts --> |

### Wave 5 — Soft improvements

| # | What | Effort | Impact |
|---|---|---|---|
| W5.1 | <!-- consistency sweep --> | S | Low |

---

## Hand-off

Implementation follows the `pull-request-workflow` spec: one PR per Wave-1 item (all parallelisable), then Wave 2 (description sweeps), then Wave 3 (specs as precondition), then Wave 4 (structural items with spec backing).

Per-artefact plans under `.audits/skill-review/` and `.audits/agent-review/` are the granular closure trail — work them off per `review-plan` lifecycle (mark items `- [x]`, append `## Processing log` entries, delete plan file with `review(<type>): close <target>--<counts>` commit message when complete).

---

## Processing log

<!-- Append one line per wave closure:
YYYY-MM-DD — <wave-id> — <decision: implemented | deferred | retired> — verified: <method>
-->
