---
audit-type: spec-drift-audit
repo-revision: FILL_GIT_SHA
created: YYYY-MM-DD
scope: full | thematic:<topic>
triggers:
  - quarterly | spec-change:<spec-slug> | new-skill:<skill-name>
tools-used:
  - project-structure-apply@<version>
  - vocab-drift-audit@<version>
  - task lint (<output-summary>)
status: open
---

# Spec Drift Audit — YYYY-Q<n>

## Contents

- [Scope](#scope)
- [Summary](#summary)
- [Per-criterion results](#per-criterion-results)
- [Findings](#findings)
- [Decisions](#decisions)
- [Specialist coverage review](#specialist-coverage-review)
- [Processing log](#processing-log)

<!-- For thematic audits: append the topic after the quarter, e.g. "2026-Q2 — pull-request-workflow" -->

## Scope

**Trigger:** <!-- quarterly / spec-change triggered by <spec-slug> / new skill <skill-name> added -->

**In-scope specs:**
<!-- List each spec path evaluated in this audit. For thematic audits, note the narrowing rationale. -->
- `spec/<topic>/<slug>/en.md`

**Excluded specs:**
<!-- List any specs explicitly excluded and the reason (e.g., no Requirements/AC section, not yet applicable). -->

**Implementation surfaces examined:**
- Source code: `src/`, `skills/`, `agents/`
- Configuration: `.github/`, `.claude/`, `Taskfile.yml`, `mkdocs.yml`, dependency manifests
- Documentation: `docs/`, `README.md`, `CLAUDE.md`
- Workflows and hooks: `.github/workflows/`, `.pre-commit-config.yaml`

## Summary

<!-- One-paragraph verdict: overall drift posture, the highest-severity finding, and the go/no-go on the audited surface. Required by spec/project/spec-drift §Artifact contract (## Scope, ## Summary, ## Findings, ## Processing log, in that order); populated after Per-criterion results and Findings are complete. -->

## Per-criterion results

<!-- One row per spec acceptance criterion. Use result values: pass | fail | blocked | not-applicable -->
<!-- blocked = tooling missing or inaccessible; not-applicable requires a reason. -->

| Spec | Criterion (short) | Result | Specialist (fail/blocked only) | Notes |
|------|--------------------|--------|--------------------------------|-------|
| `spec/<topic>/<slug>/` | AC: … | pass / fail / blocked / not-applicable | <specialist + subagent_type / skill, or "no matching specialist exists — generalist handled"; blank for pass/N-A> | |

## Findings

<!-- Only entries with result=fail or result=blocked appear here. -->
<!-- Each finding gets a sequential ID: F1, F2, … -->

### F1 — <Short title>

**Spec:** `spec/<topic>/<slug>/en.md` §<section>
**Criterion:** <Exact acceptance criterion text or requirement clause>
**Result:** fail | blocked
**Observed state:** <What the implementation actually does or has>
**Expected state:** <What the spec requires>
**Severity:** critical (security/release blocker) | standard
**Specialist:** <!-- MANDATORY (continuous-improvement). Either: <display-name> (subagent_type: <plugin>:<agent> | skill: <name>) — OR — "no matching specialist exists — generalist handled". A finding without this field is incomplete. -->

---

<!-- Add F2, F3, … as needed. Remove this section entirely if there are no findings. -->

## Decisions

<!-- Populated by the `update` operation. One entry per finding ID. -->
<!-- Decision values: adjust-impl | adjust-spec | open-question -->

<!-- Example:
### F1 — <Short title>
**Decision:** adjust-impl
**Action:** <What was changed or will be changed>
**Specialist:** <carried forward from the finding — <display-name> (subagent_type: <plugin>:<agent> | skill: <name>) OR "no matching specialist exists — generalist handled">
**PR/Commit:** <link or SHA>
**Resolved:** YYYY-MM-DD
-->

<!-- No decisions recorded yet — audit is open. -->

## Specialist coverage review

<!--
Quarterly specialist-coverage review per spec/project/continuous-improvement/ §"Continuous loop
and quarterly coverage review". Keep this section ONLY when the coverage review is folded into
this drift-audit artifact (the SHOULD default per the spec); delete it when the repository keeps
the coverage review as a standalone artifact under .audits/continuous-improvement/<YYYY-QN>.md.

This section MUST stay full-portfolio in scope even when the hosting drift audit is a thematic
partial audit — partial-audit narrowing applies to drift, not to coverage. A narrowed drift audit
that suppresses this section is itself a finding for the next cycle.

The review itself is produced by the continuous-improvement-triage skill; this is the named landing
spot so it is findable by heading. Populate the table below from the last quarter's merged
remediation PRs (Risk / rollout notes fields), grouped by finding class.
-->

| Finding class | Generalist-handled count | Matching specialist | Gap-closure action |
|---------------|--------------------------|---------------------|--------------------|
| <class label> | <N> | <plugin>:<agent> / skill / none | none / track (1–2) / author-or-extend (≥3) |

## Processing log

<!-- One line per action taken after initial artifact creation. Appended by `update` and `close`. -->
<!-- Format: YYYY-MM-DD — <finding-id> — <decision> — verified: <method> -->

<!-- YYYY-MM-DD — artifact created, status: open -->
