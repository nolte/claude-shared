# Example 02 — Mission with three audiences and per-audience paragraphs

A first-write where the audience artefact lists three distinct
audiences spanning two relationship categories. Exercises the
audience-walk loop running per identifier (never batched), the
bidirectional `audiences` ↔ `## Audiences` validation, and the
non-grouping default (each audience gets its own paragraph because the
MVP-deliverables genuinely differ).

## Input prompt

> Set up the mission file. We have three audiences in `AUDIENCES.md`
> and the MVP cuts across all three.

## Input files

`project/goals.md` resolves outcomes `O-1` (consumers can integrate the
library in under fifteen minutes) and `O-2` (operators can run a single
diagnostic command before opening a support ticket).

`AUDIENCES.md` (excerpt — three audiences across two categories):

```markdown
## Direct consumers

- **library-integrators** — _confirmed_ — Python application authors
  who pip-install the package and call its public API.
- **cli-operators** — _confirmed_ — operations engineers who run the
  bundled `nolte-diag` CLI against a deployed service.

## Contributors / maintainers

- **plugin-contributors** — _confirmed_ — external authors writing
  third-party plugins against the documented extension surface.
```

`project/roadmap.md` resolves four `mvp: true` items spanning library
public API (`R-1`), CLI command set (`R-2`), plugin extension surface
(`R-3`), and the integration-test harness that exercises all three
(`R-4`); each carries `detail: fine` and a non-null `target_sprint`
within sprints 6-9.
`project/features/integration-harness.md:acceptance-1` reads "The
integration-test harness exercises one library call, one CLI command,
and one plugin extension hook in a single end-to-end run."
`project/mission.md` does **not** yet exist.

## Expected behaviour

1. **Preconditions and inputs** resolve as in example 01: mission file
   absent, goals parse, audience artefact found at `AUDIENCES.md`
   (three identifiers extracted), four `mvp: true` roadmap items, the
   integration-harness feature on the menu.
2. **SMART walked one letter at a time.** The Specific step yields a
   `mission_statement` that names the *what* and resolves the *for
   whom* to all three audience identifiers explicitly (the skill
   refuses any phrasing that collapses them into "users" or
   "developers"). Measurable lands on
   `F-4:acceptance-1` (the harness, because it's the single criterion
   that proves all three audiences are served simultaneously).
   Achievable confirms the four-item MVP fits the two-to-five-sprint
   guidance. Relevant ties to `[O-1, O-2]`. Time-bound is set to
   `{ kind: mvp_completion }`.
3. **Audience walk runs three times, once per identifier.** Per the
   spec, a bare audience list without per-audience paragraphs **MUST**
   be refused; the skill enforces this by gathering one paragraph at a
   time:
   - **library-integrators** — three-to-five-sentence paragraph naming
     the audience and stating what the MVP delivers (a stable public
     API installable via pip with a fifteen-minute integration path).
   - **cli-operators** — separate paragraph (deliverable differs
     materially: a single diagnostic command, not a library API).
   - **plugin-contributors** — separate paragraph (deliverable differs
     again: a documented extension surface plus a working example).
   The skill considers grouping but **does not group** because the
   MVP-deliverables are not identical; grouping is reserved for the
   identical-deliverable case and the rationale must be stated inline
   when used.
4. **Bidirectional validation.** The composed
   `audiences: [library-integrators, cli-operators, plugin-contributors]`
   frontmatter list and the three `## Audiences` paragraphs are
   cross-checked: every frontmatter entry has a paragraph, every
   paragraph names a frontmatter entry, and the order matches.
   A draft that names a fourth audience inline (or omits one of the
   three) is refused with a pointer to the spec's bidirectional rule.
5. **Compose step renders** the eight frontmatter fields in declared
   order with `mvp_status: defining`, `created: 2026-05-10`,
   `revised_at: null`; the body carries the four required sections in
   declared order. `## Verification` quotes `acceptance-1` verbatim;
   `## Source` records `AUDIENCES.md` plus its last-commit SHA, the
   consulted `goals.md` path, and the operator-plus-skill audit line.
6. **Confirm and write.** Full draft presented back; only after
   explicit approval does the skill write `project/mission.md`. The
   closing message reminds the operator that adding a fourth audience
   later means re-running `audience-identify` first, then
   `mission-revise` — never an inline edit from this skill.
