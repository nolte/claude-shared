---
triage-type: continuous-improvement
repo-revision: ""
created: ""
scope: portfolio
triggers: []
status: open
---

# Continuous Improvement Triage

<!-- Replace YYYY-QN with the calendar quarter this cycle covers, e.g. 2026-Q2 -->
<!-- Replace REPO-NAME with the repository slug, e.g. nolte/claude-shared -->

## Scope

- **Repository**: <!-- REPO-NAME -->
- **Quarter**: <!-- YYYY-QN -->
- **Audit sources in scope**: spec-drift-audit, workflow-health, project-structure-apply, vocab-drift-audit, prose-style lint, manual review Issues, ad-hoc contributor observations
- **Coverage review mode**: <!-- folded into spec-drift-audit artifact | standalone -->

## Findings

<!-- One entry per finding class. Copy the block below for each finding. -->

<!--
### F<N> — <finding-class-label>

- **Source**: <!-- audit source name + link or artifact path -->
- **First observed**: <!-- YYYY-MM-DD or quarter label -->
- **Recurrence count (generalist-handled)**: <!-- N -->
- **Threshold met**: <!-- yes (≥3) | no (N=1 or 2) | pre-threshold early-create justified -->
- **Current specialist match**: <!-- <plugin>:<agent-name> | none -->
- **Decision**: <!-- pending | dispatched to <specialist> | deferred (<reason>, owner: <@who>, target: <quarter>) | gap-closure initiated -->
- **Fix PR**: <!-- #<number> | n/a -->
- **Notes**: <!-- any additional context -->
-->

## Decisions

<!-- Append one block per dispatch or gap-closure decision. -->

<!--
### D<N> — <YYYY-MM-DD>

- **Finding**: F<N>
- **Action**: <!-- dispatched to <subagent_type> | generalist (no matching specialist) | gap-closure: authored <new-specialist> | gap-closure: extended <specialist> description -->
- **Originating source**: <!-- named finding source for PR Risk / rollout notes -->
- **Fix PR Risk/rollout note (verbatim)**:
  - Originating source: <!-- named finding source -->
  - Dispatched specialist: <!-- subagent_type literal, or "no matching specialised agent—generalist remediation" -->
-->

## Processing log

<!-- Append one line per operation: audit / update / close -->

<!--
- <YYYY-MM-DD> `audit` — cycle opened; <N> findings identified across <M> finding classes
- <YYYY-MM-DD> `update` — <N> decisions recorded; <M> specialists dispatched; <K> gap-closures initiated
- <YYYY-MM-DD> `close` — cycle closed; <N> dispatched / <M> deferred / <K> gap-closure; next review due <YYYY-QN>
-->
