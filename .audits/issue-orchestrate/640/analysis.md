---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "640"
classification: "spec-change"
secondary-classes: []
route: "direct"
status: approved
created: "2026-09-19"
group: "2026-09-19-verification-discipline-specs"
---

# Issue Orchestration — Pre-analysis (member of a group run)

- **Classification:** spec-change. **Route:** direct. **Requirements gate:** operator
  override at the group write gate (decisions: new G7, not a G1 addendum; prose-satisfies-
  the-check as a named T6 form, not G3).
- **Cause verification:** the issue's claim that neither G1–G6 nor T1–T9 covers the form:
  confirmed by reading `defect-class-guards/en.md:36-41` (G1 asks for existence, G3 for
  the selector, G4 for allowlists; none constrains what the guard asserts) and
  `test-falsifiability/en.md:48` (T6 named only wrong-element resolution).
- **P1 spec** → `nolte-shared:spec` (inline): G7 + acceptance criterion (with the PR #1573
  falsification) + reference line in `defect-class-guards` EN/DE; T6 second shape +
  source line in `test-falsifiability` EN/DE. Restatement sweep `grep -rn -E
  "G1[–-]G6|\bG[1-7]\b"` outside the spec → `skills/issue-orchestrate/SKILL.md:247-249`
  (verify step names G1/G3/G6 → G7 clause added) and `guard-coverage-check/SKILL.md:76`
  (cites G3 for enumeration only → no change needed).
- **Falsification check (issue's own):** G7 applied to PR #1573: the new test's
  `"e._from == @vertex"` assertion pins the outbound anchoring of the still one-sided
  bidirectional edge → it asserts a member the fix didn't repair as intended → G7
  violation identified. Recorded in the acceptance criterion.
- **Vale:** "unrepaired" (×4) and "accessor" flagged by Vale.Spelling → reworded.
- **Refutation:** none.
