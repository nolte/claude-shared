# Example: Cross-Cutting Discovery of a Spec-Induced Gap

This walkthrough shows how phase 2 cross-cutting analysis surfaces a phantom skill
(a spec-induced gap) that no individual per-artefact review could detect on its own.

---

## Context

Phase 1 is complete. The skill has produced 43 per-artefact plans. During phase 2
the skill scans every skill and agent body for `spec/` path citations.

---

## Turn 1 — gap detection during cross-cutting analysis

**Skill internal analysis (phase 2, spec-induced gap dimension):**

Scanning all skill bodies for referenced spec paths...

```
spec/project/spec-drift-audit/en.md
  cited by: spec-readiness-reviewer (agent body, § Scope)
  cited by: feature-consistency-reviewer (agent body, § Working method)
  cited by: workflow-health-triage (skill body, § Operations › 3. escalate)
```

Checking whether a `spec-drift-audit` skill or agent exists...

```
skills/spec-drift-audit/  — NOT FOUND
agents/spec-drift-audit.md — NOT FOUND
```

**Gap classified as L1 (spec-induced phantom skill):**

- The spec `spec/project/spec-drift-audit/en.md` has `Status: draft` but is
  spec-complete (Requirements and Acceptance Criteria present).
- Three artefacts reference `spec-drift-audit` as a hand-off target.
- A user following the hand-off from `spec-readiness-reviewer` would invoke a
  non-existent skill.

**Wave classification:** structural new artefact (Wave 4), but high priority because
three existing artefacts cite the missing target.

---

## Turn 2 — skill presents the finding to the user

> Cross-cutting analysis found a spec-induced gap:
>
> **L1 — Missing `spec-drift-audit` skill**
>
> `spec/project/spec-drift-audit/en.md` is spec-complete (Requirements + AC present)
> but no operationalising skill or agent exists. Three artefacts reference it:
>
> - `agents/spec-readiness-reviewer.md` (§ Scope)
> - `agents/feature-consistency-reviewer.md` (§ Working method)
> - `skills/workflow-health-triage/SKILL.md` (§ Operations › 3. escalate)
>
> Any user following those hand-offs will land on a non-existent skill.
>
> Proposed resolution (Wave 4.1): new skill `spec-drift-audit`.
> Per `spec/claude/skill-vs-agent/`: mid-flow user decisions + persistent audit
> artifact = skill-bias.
>
> Continue to remaining cross-cutting dimensions?

---

## Turn 3 — user confirms, analysis continues

> "Yes, continue."

The skill records the gap in the consolidated report's `## Lücken-Inventar` section:

```markdown
| L1 | **`spec-drift-audit` skill** | `spec/project/spec-drift-audit/en.md` spec-complete;
cited by `spec-readiness-reviewer`, `feature-consistency-reviewer`,
`workflow-health-triage` | New skill `spec-drift-audit` (Wave 4.1, high priority) |
```

The wave-based roadmap entry:

```markdown
| W4.1 | New skill `spec-drift-audit` | L | High |
3 artefacts cite the missing target; spec is complete. |
```

The finding is also noted in the executive summary top-findings table as a Warning
(not Critical — the missing skill does not block existing functionality, but it breaks
documented hand-offs).

---

## Key observation

This gap was invisible to the 43 individual per-artefact reviews:

- `spec-readiness-reviewer`'s plan noted "hand-off to `spec-drift-audit`" as correct
  per its own spec binding — the per-artefact review had no reason to check whether
  the target existed.
- Only the cross-cutting scan of all `spec/` citations across the full inventory
  revealed the pattern: three artefacts pointing at the same missing target.

This is the primary use case for the skills-agents-sweep skill over per-artefact reviews.
