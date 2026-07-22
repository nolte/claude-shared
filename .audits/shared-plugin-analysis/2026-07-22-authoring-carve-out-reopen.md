---
artifact-type: plugin-boundary-decision-revision
feature: F-18
roadmap_item: R-11
revises: .audits/shared-plugin-analysis/2026-07-20-authoring-carve-out-decision.md
requirement: project/requirements/claude-authoring-plugin.md
created: "2026-07-22"
decision: split
bound-by: spec/claude/plugin-scoping/
---

# Authoring-slice plugin carve-out — decision revision (F-18 re-open)

**Verdict: split — carve the authoring slice into a fourth plugin
`nolte-claude-dev`.** This revises the 2026-07-20 `keep-and-watch` verdict. The
carve-out is a **consumer-audience** distribution-contract split per
`spec/claude/plugin-scoping/` — the same basis on which `nolte-engineering`
splits — and is **not** justified by topic, specialisation, coherence, or count.

## Why this re-opens now

F-18 (2026-07-20) closed the question as `keep` and named two revision triggers:
(a) a skill-list budget limit/warning appears, or (b) the slice grows materially
past ~10 %. The operator re-opened the decision on **2026-07-22**.

**Honest trigger provenance (measured):** neither original trigger is the basis.

- **Trigger (b) — measured NOT fired.** Live re-measurement on 2026-07-22, same
  method as the F-18 baseline (char count of each skill's `description`
  frontmatter over all 45 `nolte-shared` skills):

  | | F-18 baseline (2026-07-20) | Now (2026-07-22) |
  |---|---:|---:|
  | Skills counted | 45 | 45 |
  | Aggregate skill-description chars | 40,182 | 40,313 |
  | Authoring slice (5 skills) | 4,197 | 4,205 |
  | **Slice share** | **10.4 %** | **10.43 %** |

  The slice is essentially unchanged; the growth trigger has not fired.
- **Trigger (a) — not claimed.** No skill-list budget limit or Claude Code
  warning on the skill surface has been observed.

**The trigger that actually fired — a new one, added here.** The operator, as
decision authority, re-weighed F-18's own cost-benefit and decided that the
**standing ~10.4 % skill-list overhead** every non-authoring consumer carries —
for authoring skills it will never invoke — is now worth the fourth-plugin
lockstep cost. This reverses F-18's "real but not urgent → keep now" judgment on
the **present** overhead, not on any future projection. An operator expectation
that the Claude-plugin-specific authoring skills will **grow** (adding overhead
for other projects) is recorded as an **amplifier**, not the load-bearing reason —
F-18's "pre-empting a limit that has not appeared is speculative" caveat stays
visible and is deliberately not leaned on.

This is a legitimate **consumer-audience** split: F-18 itself conceded the slice
is a genuine consumer-audience category ("most consumers never author") and that
a split would be rule-legitimate; what it judged missing was that the saving
outweighed the standing fourth-plugin cost. That trade-off is an operator call,
and the operator has now made it the other way.

## Amended revision-trigger record

F-18's trigger list is amended to record the trigger that fired:

- (a) a skill-list budget limit/warning — *not observed*;
- (b) slice grows materially past ~10 % — *measured not fired (10.43 %)*;
- **(c) NEW — operator judges the standing non-authoring-consumer overhead worth
  the fourth-plugin cost** — *fired 2026-07-22; the basis for this flip.*

## What the split does

Extract into a new optional plugin `nolte-claude-dev` (structured like
`plugins/nolte-media/`, versioned in lockstep, fourth `marketplace.json` entry):

- **Skills (5):** `skill-management`, `skill-review`, `agent-review`,
  `skills-agents-sweep`, `skill-agent-catalog-apply`.
- **Agent (1):** `claude-plugin-developer`.
- **"Documentation" goal** is served by the existing `skill-agent-catalog-apply`
  moving with the slice — **no** net-new documentation capability is built.

**Explicitly not moved / not done:**

- The `spec/claude/` corpus stays repo-wide (shipped with no plugin).
- The `cookiecutter-template-*` pair stays in `nolte-shared` (F-18 "adjacency,
  not core"; it is project scaffolding, not Claude skill/agent authoring — a
  weaker audience match).
- The separate PB-2 placement question (`gdpr-data-protection-reviewer`,
  `quality-gate-enforcer` living in `nolte-shared/agents/`) is untouched here.

## Accepted standing costs (F-18's against-arguments, now accepted)

- **Permanent manual lockstep-bump surface.** A fourth plugin adds a per-release
  manual version-bump step (marketplace `plugins[].version` deliberately absent).
  Mitigation: declare the new `plugin.json` version in
  `.github/release-automation.yml` so the pre-publish alignment gate catches drift.
- **Ad-hoc review becomes an install decision.** An occasional non-authoring
  consumer that wants a single `skill-review`/`agent-review` must install
  `nolte-claude-dev`. Accepted as the intended audience boundary.

## Traceability

Requirement artifact: `project/requirements/claude-authoring-plugin.md`
(`U_gate = 0.8`, saturation). Governing spec: `spec/claude/plugin-scoping/`.
Supersedes the `keep` verdict in `2026-07-20-authoring-carve-out-decision.md`.
