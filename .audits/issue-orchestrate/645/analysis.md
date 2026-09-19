---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "645"
classification: "spec-change"
route: "direct"
status: approved
created: "2026-09-19"
group: "2026-09-19-runner-slot-economy"
---

# Issue Orchestration — Pre-analysis (member of a group run)

- **Classification:** spec-change. **Route:** direct. **Requirements gate:** operator
  override at the group write gate (decisions: §L after §K, five rules as proposed, [R13]).
- **Asserted cause verified:** the platform spec binds runner trust (§I) but not scarcity:
  `grep -n -i "concurren\|slot\|allotment" spec/project/github-actions-best-practices/en.md`
  before editing → hits only in §F (concurrency groups) and §K (merge-group concurrency
  key); no rule prices a job. Starvation re-measured in this repository (group artifact).
- **P1 spec** → `nolte-shared:spec` (inline): §L (intro + 2 MUST, 2 SHOULD, 1 MAY), §J
  routing bullet, two acceptance criteria, [R13], EN + DE. Vale forced "SHOULD NOT" →
  "SHOULD keep … out of / inside …" (Microsoft.Contractions flags the phrase; the corpus
  has no other `**SHOULD NOT**`), "seven percent" → "7 %", "diagnosability" reworded.
- **Deviation (local adaptation):** placement §L instead of the issue's "after §I", to
  keep §J/§K letters stable (§K is cross-referenced from `pull-request-workflow`).
- **Refutation:** none.
