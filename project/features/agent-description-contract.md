---
id: F-6
title: Agent-description contract
status: done
roadmap_item: R-9
sprint: 5
created: 2026-07-11
ended: 2026-07-19
verifies_sprint_value: null
consistency_check:
  performed_at: 2026-07-11
  agent_version: feature-consistency-reviewer@5784336
  findings:
    - kind: prior-art
      target: spec/claude/skill-agent-frontmatter/en.md and spec/claude/agent-management/en.md
      resolution: proceed
---

## Description

Plugin authors get one documented, minimal contract for what an agent `description` must contain, so descriptions stay cheap to load and reliably routable. Descriptions have drifted — some carry embedded `user:`/`assistant:`/`<commentary>` example blocks that belong in the agent body, and some carry over-long `don't use for … (use Z)` delimitation chains — and there is no single place that states the intended shape. This feature writes that contract so F-7's remediation has a target to normalise against and F-8's guardrail has a rationale for why the budget stays bounded.

The contract specifies the required description shape ("what it does / when to activate / don't use for X → use Y"), keeps descriptions EN-canonical, bans example/commentary blocks inside a `description`, and states the delimitation-chain tightening rule (prefer a cheap cross-reference over an enumerated chain). It extends the partial rules that already live in `spec/claude/skill-agent-frontmatter/` and `spec/claude/agent-management/` rather than contradicting them.

## Acceptance criteria

- [x] **acceptance-1** A specification documents the required agent-`description` shape ("what it does / when to activate / don't use for X → use Y"), EN-canonical, and is present in both configured languages.
- [x] **acceptance-2** The contract forbids embedded `user:`/`assistant:`/`<commentary>` example blocks in any `description`, directing such content to the agent body.
- [x] **acceptance-3** The contract states the delimitation-chain tightening rule: prefer a cheap cross-reference over an enumerated `don't use for …` chain where the cross-reference suffices.
- [x] **acceptance-4** `task validate:skills` passes with the contract's spec added and its translations in sync.

## Test hooks

- **acceptance-1** — manual: confirm the spec file exists in every configured language and states the description shape — `passing`
- **acceptance-2** — manual: confirm the spec carries an explicit rule banning `user:`/`assistant:`/`<commentary>` blocks in a `description` — `passing`
- **acceptance-3** — manual: confirm the spec states the delimitation-chain tightening rule — `passing`
- **acceptance-4** — CLI: `task validate:skills` exits `0` with the new spec present — `passing`

## Consistency notes

The consistency check ran via the `feature-consistency-reviewer` agent (`agent_version: feature-consistency-reviewer@5784336`) and returned one non-blocking finding for this feature.

- **prior-art** (`spec/claude/skill-agent-frontmatter/en.md` and `spec/claude/agent-management/en.md`; resolution `proceed`): a partial description contract already exists — `skill-agent-frontmatter` says a description "states what and when; no XML tags", and `agent-management` carries the "don't use for …" pattern, concrete-trigger guidance, and the single-responsibility rule. F-6's assumed home is one of these two specs (requirement A1 leaves the exact placement open). F-6 formalises and tightens the existing rules — the `<commentary>`-block ban is a specialisation of the existing "no XML tags" rule — without contradicting any existing MUST, so this is extension, not `duplication` or `drift`. `prior-art` is a non-blocking kind; F-6 clears the consistency gate. The live operator decision is placement (extend `skill-agent-frontmatter` vs. `agent-management`), a home-selection choice, not a consistency conflict.

## Risks

- **Placement ambiguity.** Requirement A1 leaves the contract's home open (extend `skill-agent-frontmatter` vs. `agent-management` vs. a new spec). Choosing wrong forces a later move; mitigation: decide placement at the start of this feature and record it, since both candidate specs already carry description rules.
- **Over-strict contract harms routing.** A contract that trims too aggressively could strip the "when to activate / don't use for X → use Y" routing signal F-7 relies on. Mitigation: the contract keeps the routing signal mandatory; F-7's spot-check (via `agent-review`) is the standing guard.
