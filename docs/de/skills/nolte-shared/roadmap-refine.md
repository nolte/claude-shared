---
title: roadmap-refine
audience: [maintainer]
content_mode: reference
track: developer-docs
last_updated: generated
---

# roadmap-refine

_Enforces the detail-level invariant on `project/roadmap.md` per `spec/project/roadmap/` §Detail-level convention. Invoke when the user asks to \"refine the roadmap\", \"check roadmap detail levels\", \"is the roadmap ready for the next sprint\", \"promote roadmap items to fine\", or equivalent German-language requests. Resolves the current and next sprint by reading `project/sprints/`, walks every roadmap item, emits a structured violation record on stderr for every item with `target_sprint` equal to the current or next sprint and `detail` other than `fine`, exits non-zero when any violation is open, and walks per-item fix proposals one at a time. Don't use to add items, retarget sprints, or flip MVP flags (use `roadmap-planner`); don't use to scaffold the roadmap from scratch (use `roadmap-init`)._

- **Plugin:** `nolte-shared`
- **Phase:** 2 Plan (`plan`)
- **Tags:** `audit`
- **Quelle:** [skills/roadmap-refine/SKILL.md](https://github.com/nolte/claude-shared/blob/main/skills/roadmap-refine/SKILL.md)

---

## Roadmap Refine

Enforces the detail-level invariant declared in `spec/project/roadmap/<canonical_language>.md` §Detail-level convention and refinement rule: at any point in time, every roadmap item with `target_sprint` set to the **current sprint** or the **next sprint** carries `detail: fine`. Coarse and backlog items two or more sprints out are fine; promotion to `fine` is the trigger for this skill to pull each affected item into shape.

### German trigger phrases

This skill also triggers on equivalent German-language requests, including:

- "Roadmap verfeinern"
- "Roadmap-Detailstufen prüfen"

### Why this is a skill, not an agent

- **Mid-flow interactivity is the contract** — fix proposals (promote `coarse → fine`, write the missing body paragraph, expand the feature checklist) are negotiated with the user one item at a time; an agent's structured-report shape would lose that per-item iteration.
- **Output flows back into the main conversation** — the violation list and the per-item drafts must be visible in the working context so the user can confirm each fix before it hits disk.
- **Orchestrator role** — fixes that exceed simple promotion (re-targeting a sprint, adding a feature checklist) are dispatched into `roadmap-planner`; the orchestrator is always a skill per `skill-vs-agent`.
- Counter-dimension considered: the violation-detection step alone (read `project/sprints/`, walk roadmap items, emit records) would suit an agent's isolated context, but the load-bearing dimension is the per-item user dialogue around remediation, not the detection mechanics — skill wins.

### User-language policy

Detect the user's language and respond in it. Violation records, remediation hints, and any prose the skill writes back into `project/roadmap.md` use the project's primary language (the same language already used in `goals.md` and `roadmap.md`).

### Preconditions

Before walking the roadmap:

- `project/roadmap.md` and `project/goals.md` exist. When either is missing, stop and direct the user to `roadmap-init`.
- `project/sprints/` exists and contains at least one sprint file under the `<NNNN>-<slug>.md` shape declared by `spec/project/sprint/`. When the directory is missing or empty, the current and next sprint can't be resolved; stop and report the gap so the operator can scaffold sprints first.
- The roadmap items under audit parse: every item exposes a `### <id>` heading immediately followed by a fenced ```yaml block carrying `id`, `title`, `detail`, `outcomes`, `target_sprint`, `mvp` (when `project/mission.md` exists), and `status`. When parsing fails on any item, surface the parse error and stop — partial enforcement on a partially-parsed file would leak false positives.

### Operations

#### 1. Resolve the current and next sprint

The spec defines the resolution exactly; this skill **MUST** follow it without local interpretation:

1. **Current sprint** — the sprint whose `status` is `active` per `spec/project/sprint/`. At most one sprint per project carries `active`. When no sprint is `active`, fall back to the **lowest-numbered** sprint whose `status` is `planned`. When no sprint is `planned`, fall back to the **highest-numbered** sprint whose `status` is `closed`. When the project has only `cancelled` sprints, treat the current sprint as undefined and report the gap; the invariant cannot be checked, so emit a single non-violation diagnostic and exit zero.
2. **Next sprint** — the lowest-numbered sprint whose `status` is `planned` and whose `number` is strictly greater than the current sprint's `number`. When no such sprint exists, treat the next sprint as undefined and only enforce the invariant against the current sprint.

When the skill runs, it echoes both resolved values back to the user before walking items so the operator sees the assumption the skill is auditing against:

```
Current sprint: 0007 (active)
Next sprint:    0008 (planned)
```

#### 2. Walk the roadmap

For every roadmap item:

1. Read its YAML block.
2. Skip when `target_sprint` is `null` or does not match the current or next sprint number.
3. When `target_sprint` matches the current or the next sprint and `detail` is anything other than `fine`, emit a violation record (see step 3).
4. Independently of the detail invariant, surface but do **not** treat as a violation here: a `target_sprint` pointing at a `closed` or `cancelled` sprint. That is a separate lint owned by `sprint-plan` per the spec; report it as an informational note and let `roadmap-planner` pick it up.

#### 3. Emit violation records

Each violation **MUST** carry:

- `id` — the item's `R-<n>`;
- `target_sprint` — the offending sprint number;
- `current_detail` — the item's current `detail` value (`coarse` or `backlog`);
- `resolved_current_sprint` — the sprint number this skill resolved as current;
- `resolved_next_sprint` — the sprint number this skill resolved as next, or `null`;
- `remediation_hint` — one short line of advice ("Promote to `detail: fine` and add a feature checklist", "Retarget to a later sprint via `roadmap-planner`", "Split into a `fine` slice and a `coarse` follow-up").

Write each record to **stderr** (or the skill's structured output channel) so downstream tooling can pick them up. **Exit non-zero** when at least one violation is open. Exit zero only when every audited item is compliant.

Suggested record shape (one record per line, machine-readable):

```
violation id=R-3 target_sprint=8 current_detail=coarse resolved_current_sprint=7 resolved_next_sprint=8 hint="Promote to detail: fine and add feature checklist"
```

#### 4. Walk fix proposals per item

For each violation, in roadmap order, propose a fix to the user **one item at a time**:

1. Show the current item (heading, YAML block, body) and the violation record.
2. Offer the canonical remediation paths:
   - **Promote to `fine`** — flip the YAML field and draft the missing body shape (paragraph stating the user-visible change plus a feature checklist). The skill drafts both; the user confirms or edits.
   - **Retarget the sprint** — change `target_sprint` to a later sprint. Refuse to do this directly; dispatch `roadmap-planner` so cross-references (outcome resolution, sprint resolution) are validated end-to-end.
   - **Drop the sprint anchor** — set `target_sprint: null` so the item drops back to unscheduled. Direct edit is acceptable here because no cross-reference materially changes.
3. Apply the chosen fix in-place inside `project/roadmap.md`. Refuse partial writes that would leave the file in a half-fixed state — when the user changes their mind mid-walk, revert to the pre-walk file and exit non-zero.
4. On every individual-fix completion, the skill re-resolves current and next sprint numbers from disk in case the operator changed sprint state in parallel.

When the user wants to accept all violations and just record the audit without fixing, refuse: this skill is the canonical enforcement point and writing the queue back unchanged after a violation would defeat its contract. Direct the user to either fix the items or dispatch `roadmap-planner` for non-trivial restructuring.

#### 5. Final report

On run completion, the skill reports:

- The count of violations found, fixed, deferred, and skipped.
- The final exit code (zero only when no violations remain after the walk).
- When violations remain (the user deferred a fix), the skill keeps the exit code non-zero so calling automation sees the failure.

### Examples

- Read `examples/01-clean-no-violations.md` when all roadmap items are already spec-compliant and the skill produces a clean report.
- Read `examples/02-coarse-near-sprint-violation.md` when a near-sprint item is still flagged `coarse` and the skill surfaces the violation.
- Read `examples/03-walk-fixes-promote-and-retarget.md` when the walk phase fixes a coarse violation by promoting to `fine` and retargeting the item.

### Gotchas

- **Detail-level invariant applies only to current and next sprint items**: items targeted at sprints two or more out are intentionally `coarse` or `backlog` — do not flag them as violations; applying the `fine` requirement beyond the two-sprint horizon is over-enforcement.
- **Sprint state must be re-read after each per-item fix**: `roadmap-refine` step 4.4 explicitly re-resolves current and next sprint numbers from disk after each fix, because the operator may change sprint state in parallel; using a cached sprint resolution across multiple fix rounds can produce stale violation records.
- **A missing or empty `project/sprints/` directory is a hard stop, not a skip**: without a resolvable current sprint the invariant cannot be checked; stop and report the gap rather than falling back to wall-clock heuristics or guessing from roadmap content.

### Hard rules

- **Never** resolve the current or next sprint by any rule other than the one declared in `spec/project/roadmap/` §Detail-level convention and refinement rule. The fallback chain (active → lowest planned → highest closed; next is lowest planned strictly greater than current) is exact and not negotiable.
- **Never** treat the absence of a `planned` next sprint as a violation. The invariant only applies to sprints that exist; when the next sprint is undefined, audit only against the current one.
- **Never** retarget `target_sprint` directly inside this skill. Cross-reference validation belongs to `roadmap-planner`; this skill dispatches into it.
- **Never** suppress a violation on stderr to keep automation green. The exit code and the violation records are the contract.
- **Never** rewrite a roadmap item's body without showing the draft to the user first; per-item user confirmation is the contract.
- **Never** silently demote a `fine` item to `coarse` or `backlog`. The spec only governs the upward direction (promotion to `fine` for near-sprint items); demotion is owned by `roadmap-planner` and requires explicit user intent.
- **Never** treat a `target_sprint` pointing at a `closed` or `cancelled` sprint as this skill's violation. Surface it as an informational note and route it to `roadmap-planner` and `sprint-plan`.
- When `spec/project/roadmap/` disagrees with this skill, the spec wins. Propose updating this skill rather than silently diverging.
