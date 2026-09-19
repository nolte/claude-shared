---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "637"
classification: "spec-change"
secondary-classes: []
route: "direct"
status: approved
created: "2026-09-19"
group: "2026-09-19-verification-discipline-specs"
---

# Issue Orchestration — Pre-analysis (member of a group run)

- **Classification:** spec-change. **Route:** direct. **Requirements gate:** operator
  override at the group write gate (decisions: G8 after #640's G7; grammar
  `SELF-REVOKED: #<issue> <YYYY-MM-DD>`; open issue **and** red/xfail guard; 30-day age
  bound, project-overridable with a reason; consumer lane out of scope).
- **Cause verification:** the issue's claim that the spec names no rule for a self-revoking
  comment: confirmed by `grep -n -i "comment\|revok\|marker" spec/project/defect-class-guards/en.md`
  before editing → G2 calls an advisory-lane guard "a comment" and G5 mentions comments
  as a place for the issue number; nothing constrains a comment that revokes the code.
- **P1 spec** → `nolte-shared:spec` (inline): G8 + acceptance criterion + reference line
  + open question (who ships the counter) in EN and DE. Restatement sweep for G-rule
  enumerations was run under #640 (two hits, neither enumerates beyond G3/G6/G7).
- **Refutation:** none.
