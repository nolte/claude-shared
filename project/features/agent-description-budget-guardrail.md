---
id: F-8
title: Agent-description budget guardrail
status: done
roadmap_item: R-9
sprint: 5
created: 2026-07-11
ended: 2026-07-19
verifies_sprint_value: acceptance-1
consistency_check:
  performed_at: 2026-07-11
  agent_version: feature-consistency-reviewer@5784336
  findings:
    - kind: prior-art
      target: scripts/validate_skills.py (lines 258, 304, 427-447)
      resolution: proceed
    - kind: overlap
      target: F-7 (shared-agent-description-remediation) and F-5 (shared-plugin-structural-analysis)
      resolution: proceed
---

## Description

Consumers keep their regained agent-description headroom permanently, because a test-gate check fails whenever the shared side's aggregate description budget regresses. F-7 trims the descriptions once; without an automated guard, the budget would creep back toward the ~15k ceiling as new agents land. This feature installs that guard so the win is durable.

`scripts/validate_skills.py` gains a check that measures the per-plugin aggregate agent-description token weight, holds the post-remediation baseline that F-7 records, and fails when a plugin regresses above it. The check runs inside `task test` — and therefore the existing CI gate — with no new standalone workflow, and documents its measurement method so the number is reproducible. This is the value-verifying feature for sprint 0005: it is the artefact that proves consumers keep their headroom.

## Acceptance criteria

- [x] **acceptance-1** `scripts/validate_skills.py` measures the per-plugin aggregate agent-description token weight, holds the post-remediation baseline recorded by F-7, and fails when a plugin's aggregate regresses above that baseline.
- [x] **acceptance-2** The check runs inside `task test` (and therefore the existing CI gate) with no new standalone workflow.
- [x] **acceptance-3** The measurement method (the tokenization proxy) is documented so the reported number is reproducible.

## Test hooks

- **acceptance-1** — CLI: raise one plugin's aggregate description weight above the baseline in a scratch run; assert `validate_skills.py` fails — `passing`
- **acceptance-2** — CLI: `task test` invokes the new check; assert it runs without a new workflow file — `passing`
- **acceptance-3** — manual: confirm the measurement method is documented alongside the check — `passing`

## Consistency notes

The consistency check ran via the `feature-consistency-reviewer` agent (`agent_version: feature-consistency-reviewer@5784336`) and returned two findings — one non-blocking, one blocking.

- **prior-art** (`scripts/validate_skills.py` lines 258, 304, 427–447; resolution `proceed`): the script already carries a per-`description` 1024-char cap (:258), a `description`+`when_to_use` 1536-char combined cap (:304), and a skill-*body* 5k-token estimate (:427–447). None measures a per-plugin *aggregate* description-token weight, so F-8's check is net-new and can reuse the existing 4-characters-per-token helper. `proceed`; not `duplication`.
- **overlap → F-7 and F-5** (resolution `proceed`, blocking — **rationale below clears the `draft → ready` gate**): F-8's acceptance-1 shares the "per-plugin aggregate agent-description token weight" subject with F-5's analysis snapshot and F-7's recorded baseline. The three measure the same quantity at different lifecycle points — F-5 defines the method and takes the pre-remediation snapshot, F-7 records the frozen post-remediation baseline, F-8 enforces it on every run — so the work is non-redundant and `merge-into`/`split-out` are rejected. **Committed resolution:** F-8's guardrail uses the single tokenization method F-5's analysis documents (per requirement A4) — a 4-characters-per-token estimate over the concatenated `description` frontmatter values of every agent under each plugin's `agents/` root, reusing the char-based helper already present in `scripts/validate_skills.py` — and freezes the exact number F-7 records as the baseline. Because the enforced ceiling, F-7's recorded baseline, and F-5's published figure are produced by one identical method, they reconcile by construction. With this single-method commitment written here and mirrored in F-7, the blocking overlap is resolved and F-8 may leave `draft`.

## Risks

- **Baseline drift (A3).** A regression-only guardrail freezes whatever F-7 achieves; a weak remediation locks in a weak ceiling. Mitigation: set the baseline only after F-7's full pass and record the number in F-5's analysis for review.
- **Proxy vs. real tokenizer.** The 4-char/token proxy is an estimate, not Claude Code's actual tokenization; a future tokenizer change could shift the true budget under a stable proxy number. Mitigation: acceptance-3 documents the method so the proxy is explicit and can be revised deliberately, matching the estimate `validate_skills.py` already uses for body tokens.
