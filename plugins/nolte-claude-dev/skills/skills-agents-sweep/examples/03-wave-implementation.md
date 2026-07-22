# Example: Wave Implementation and Sweep Closure

This walkthrough covers recording wave decisions via `update` and closing a completed
sweep cycle via `close` once all waves are resolved.

---

## Context

The consolidated report `.audits/skills-agents-sweep/2026-05-20-baseline.md` is open.
Waves 1–3 have been implemented via merged PRs. Wave 4 items are deferred to tracked
issues. Wave 5 items are retired with explicit rationale.

---

## Turn 1 — recording Wave 1 implementation

> "Wave 1 is done. PRs: W1.1 was #147, W1.2 was #148, W1.3 was #149, W1.4 was #150,
> W1.5 was #151, W1.6 was #152."

**Skill action (update operation):**

1. Reads `.audits/skills-agents-sweep/2026-05-20-baseline.md`.
2. Verifies each PR URL against the GitHub API: all six are merged on `develop`.
3. Updates wave rows in the roadmap section:

   ```markdown
   | W1.1 | fix(agents): add phase frontmatter to 9 agents | ... → implemented: #147 |
   | W1.2 | fix(skills): move DE trigger phrases to body    | ... → implemented: #148 |
   | W1.3 | fix(skills): replace XML-tag placeholders        | ... → implemented: #149 |
   | W1.4 | fix(skills): extract ops to references/          | ... → implemented: #150 |
   | W1.5 | fix(skills): add examples/ load-trigger phrases  | ... → implemented: #151 |
   | W1.6 | fix(agents): reorder prompt structure             | ... → implemented: #152 |
   ```

4. Appends six log lines to `## Processing log`:

   ```
   2026-05-22 — W1.1 — implemented — verified: PR #147 merged on develop
   2026-05-22 — W1.2 — implemented — verified: PR #148 merged on develop
   2026-05-22 — W1.3 — implemented — verified: PR #149 merged on develop
   2026-05-23 — W1.4 — implemented — verified: PR #150 merged on develop
   2026-05-24 — W1.5 — implemented — verified: PR #151 merged on develop
   2026-05-24 — W1.6 — implemented — verified: PR #152 merged on develop
   ```

5. Flips `status` to `in-progress` in frontmatter (first closure).

> Wave 1 recorded. Status: in-progress. Diff shown for review.

---

## Turn 2 — deferring Wave 4 items

> "Wave 4 items W4.2, W4.3, W4.4, W4.5, W4.6 are deferred to issues.
> W4.1 (spec-drift-audit skill) was already done in PR #143."

**Skill action:**

Verifies PR #143 is merged. Checks issues for each deferred item:
user provides issue URLs: #153, #154, #155, #156, #157.

Updates wave rows:

```markdown
| W4.1 | New skill `spec-drift-audit` | ... → implemented: #143 |
| W4.2 | Hybrid `portfolio-audit`     | ... → deferred: #153    |
| W4.3 | Hybrid `cookiecutter-...`    | ... → deferred: #154    |
| W4.4 | Hybrid `vocab-drift-audit`   | ... → deferred: #155    |
| W4.5 | New skill `cont.-improv.-triage` | ... → deferred: #156 |
| W4.6 | Specs for dependency/quality | ... → deferred: #157    |
```

Appends log entries for each.

---

## Turn 3 — retiring Wave 5 items

> "Wave 5: W5.5 (rename roadmap-planner) is retired — breaking rename deferred to
> Major release. W5.1-5.4 were implemented in W1.5 and W2 PRs."

**Skill action:**

Updates W5.5 row:

```markdown
| W5.5 | Rename `roadmap-planner` → `roadmap-plan` | S | Low |
→ retired: breaking rename; scheduled for next Major release (0.2.0) |
```

Appends log entry:

```
2026-05-25 — W5.5 — retired — rationale: breaking rename deferred to Major release
```

---

## Turn 4 — close the sweep

> "All waves are resolved. Close the sweep."

**Skill action (close operation):**

1. Reads the report. Verifies every wave row has an annotation (`implemented`,
   `deferred`, or `retired`). All 28 wave items are annotated.
2. Verifies all `deferred` annotations carry live issue URLs — confirmed.
3. Proposes deletion commit message:

   ```
   sweep(skills-agents-sweep): close 2026-05-20-baseline--W1-W3-implemented,W4-deferred,W5-mixed

   Waves 1–3 fully implemented (#147–#152, #143, W2 PRs, W3 spec PRs).
   Wave 4 deferred: #153, #154, #155, #156, #157.
   Wave 5: W5.1–W5.4 implemented, W5.5 retired (Major release).

   repo-revision at sweep open: b1b4d0b48e406f63ccc235b052cf80aef3cf02ae
   ```

> Commit message shown above. Confirm to delete the report and commit?

---

## Turn 5 — confirm and close

> "Confirmed."

The skill deletes `.audits/skills-agents-sweep/2026-05-20-baseline.md` and runs the
commit. The sweep cycle is closed. A new sweep may now be opened.
