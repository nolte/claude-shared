# Example 03 — Triage cycle close after all decisions recorded

Demonstrates the `close` operation: the user asks to close the 2026-Q2 triage cycle. The skill verifies every finding carries a decision, confirms fix PRs contain the required audit-trail fields, flips the artifact status to `closed`, and returns the summary.

## Input prompt

> Alle Findings haben jetzt Entscheidungen. Bitte den Q2-Triage-Zyklus abschließen.

## Input files

Repository state when the skill is invoked:

- Open triage artifact at `.audits/continuous-improvement/2026-Q2.md` with `status: open`, containing:
  - **F1 — project-structure-apply gap**: decision `deferred (below threshold, no specialist; owner: nolte; target: 2026-Q3)`.
  - **F2 — vocab-drift-audit gap**: decision `dispatched to nolte-shared:vocab-drift-audit`; fix PR #118 opened.
  - **F3 — prose-style lint gap**: decision `gap-closure initiated—audience-doc-author description extended`; fix PR #119 opened.
- `## Decisions` contains three entries D1 (F1 deferred), D2 (F2 dispatched), D3 (F3 gap-closure).
- `## Processing log` contains the `audit` entry (2026-05-21) and one `update` entry (2026-05-21).

## Expected behaviour

1. **Verify completeness.** The skill reads `.audits/continuous-improvement/2026-Q2.md` and checks every finding in `## Findings` for a non-`pending` decision. F1 is deferred, F2 dispatched, F3 gap-closure initiated — all three carry decisions. Completeness check passes.

2. **Verify fix-PR audit trails.**
   - PR #118 (F2): run `gh pr view 118 --json body`. Parse **Risk / rollout notes**: originating source field present (`vocab-drift-audit` finding from PRs #115 and Q1 predecessor), dispatched specialist field present (`nolte-shared:vocab-drift-audit`). Check passes.
   - PR #119 (F3): run `gh pr view 119 --json body`. Parse **Risk / rollout notes**: originating source field present (prose-style lint findings from PRs #104, #109, #116), dispatched specialist field present ("gap-closure initiated—`audience-doc-author` description extended; prior occurrences read `no matching specialist existed — generalist handled`"). Check passes.
   - F1 is deferred with no fix PR — skip audit-trail verification for deferred findings.

3. **No blocking issues found.** All required fields are present; no amendment needed.

4. **Update the triage artifact.** Flip `status: open` → `status: closed` in the frontmatter. Append a `close` entry to `## Processing log`:

   ```

   - 2026-05-21 `close` — cycle closed; 1 dispatched (F2) / 1 gap-closure (F3) / 1 deferred (F1); next review due 2026-Q3 (≈ 2026-09-01)

   ```

5. **No additional file changes.** The skill writes only the triage artifact; it does not touch any other file. Staging: `.audits/continuous-improvement/2026-Q2.md` only.

6. **Report back.** Return:
   - Triage artifact: `.audits/continuous-improvement/2026-Q2.md`
   - Findings: 3 total — 1 dispatched (F2, fix PR #118), 1 gap-closure initiated (F3, fix PR #119), 1 deferred (F1, target 2026-Q3)
   - Outstanding gap-closure PRs: PR #119 (open, `audience-doc-author` extension).
   - Next review due: 2026-Q3 (earliest boundary ≈ 2026-09-01).
   - Reminder: PR #119 should be merged before the Q3 audit so `audience-doc-author` routes future prose-style findings automatically.

7. **Hard rules respected throughout.**
   - No finding was closed without a decision.
   - No fix PR was confirmed as compliant without reading its actual body via `gh pr view`.
   - Deferred finding F1 carries an explicit owner and target quarter — it is not silently dropped.
   - The triage artifact will be discoverable in `.audits/continuous-improvement/` for cross-quarter history.
