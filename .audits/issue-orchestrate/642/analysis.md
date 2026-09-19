---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "642"
classification: "spec-change"
secondary-classes: []
route: "direct"
status: approved
created: "2026-09-19"
group: "2026-09-19-verification-discipline-specs"
---

# Issue Orchestration — Pre-analysis (member of a group run)

Delegated by `issue-batch-orchestrate`; admission, mode and write-gate decisions live in
the group artifact. Member-specific record:

- **Classification:** spec-change. **Route:** direct. **Requirements gate:** operator
  override at the group write gate (decisions: new T10; §Mechanics under Negative
  verification; cross-reference to `parallel-working-copies`).
- **Cause verification:** the issue's claim that the spec never says how to restore the
  pre-fix state and that the only stash mention in the corpus endorses the command:
  confirmed by `grep -rn -i "git stash" spec/project/*/en.md` → only
  `parallel-working-copies/en.md:84-85`; `test-falsifiability/en.md:72-79` names no
  restore mechanic.
- **P1 spec** → `nolte-shared:spec` (inline): T10 in the taxonomy, a T10 review question,
  two mechanics bullets, two acceptance criteria, one source line — EN + DE.
  Restatement sweep: `grep -rn -E "T1[–-]T9|\bT9\b"` outside the spec finds only T9
  fidelity references in the tier specs and agents, no enumeration of the taxonomy, so no
  restatement needed a T10 update.
- **Falsification check (issue's own):** the mechanics bullet names `git stash` as the
  wrong tool with the failure it produces; a counter-proof described as "stashed, ran
  red, popped" is non-conformant by that sentence alone.
- **Refutation:** none.
