---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "647"
classification: "feature-request"
route: "direct"
status: approved
created: "2026-09-19"
group: "2026-09-19-runner-slot-economy"
---

# Issue Orchestration — Pre-analysis (member of a group run)

- **Classification:** feature-request (skills/agents). **Route:** direct. **Requirements
  gate:** operator override at the group write gate (decisions: reference in
  `cicd-pipeline-design/references/`, cited from `workflow-health-triage`; reviewer
  checks file-only; cancelled-lane routing in triage op 1).
- **Asserted cause verified:** the recipe is written down nowhere: `grep -rn -i
  "started_at\|slot" skills agents` before dispatch → no hit; `cicd-pipeline-design/`
  had no `references/` directory (`ls`); `workflow-health-triage/SKILL.md:64` classified
  every `cancelled` run as `other` and stopped.
- **P1** → `nolte-claude-dev:claude-plugin-developer`: new
  `references/slot-capacity-measurement.md` (103 lines), `cicd-pipeline-design` op 1 +
  `## References` + description 949 chars, `workflow-health-triage` op 1 routing via
  `${CLAUDE_PLUGIN_ROOT}/skills/cicd-pipeline-design/references/…`,
  `cicd-pipeline-reviewer` §Platform two checks + Grep sweep + Delimitation clarification;
  agent description unchanged. `validate_skills.py` 0 Critical; body estimates 3012 /
  4189 / 2670 tokens; `check_section_refs.py` exit 0, both cited headings resolve.
- **Deviation (local adaptation):** severity of the stand-alone sub-minute-job check set
  to Suggestion (the agent's §Severity puts SHOULD-level deviations there), gate-in-
  `needs:` at Warning (it amplifies wait onto everything behind it); the write gate had
  said Warning for both. Accepted: the agent's own scale governs its findings.
- **Refutation:** none.
