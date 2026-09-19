---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "636"
classification: "spec-change"
secondary-classes: []
route: "direct"
status: approved
created: "2026-09-19"
group: "2026-09-19-verification-discipline-specs"
---

# Issue Orchestration — Pre-analysis (member of a group run)

Delegated by `issue-batch-orchestrate`; the group artifact under
`.audits/issue-batch-integration/2026-09-19-verification-discipline-specs/` carries
admission, mode, and the write-gate decisions. This file records only what is
member-specific.

- **Classification:** spec-change. **Route:** direct. **Requirements gate:** operator
  override recorded at the group write gate (owner-authored issue with a measured
  reproduction, `nolte/kamerplanter#1405`, and a two-option proposal; decision "both").
- **Cause verification (#641's rule, applied voluntarily):** the issue's cause — the form
  is absent from `spec/project/test-falsifiability/en.md` §"Detection: Static criteria"
  and from `test-pyramid-check` op 5 — confirmed by reading `en.md:55-58` and
  `SKILL.md:69-83` before editing: neither names an unread pre-state or F841.
- **P1 spec** → `nolte-shared:spec` (inline): one bullet in §Static criteria (EN + DE), one
  source line in §References. Checks: EN/DE parity H=17/17, B=94/94, AC=11/11; Vale
  exit 0 on `en.md`; markdownlint + check-section-refs green.
- **P2 skill** → `nolte-claude-dev:claude-plugin-developer`: one bullet in op 5 after the
  T8 bullet, delegating the form to the static tier. Checks: `validate_skills.py` no new
  finding for the file (pre-existing Info: description 1004/1024); markdownlint green.
- **Refutation:** none.
