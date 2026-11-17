---
artifact-type: issue-orchestration-analysis
repo: nolte/claude-shared
issue: "780"
classification: bug
secondary-classes: []
route: direct
status: approved
created: 2026-11-17
---

# Issue Orchestration — Pre-analysis (#780)

## Issue metadata

- **Issue**: #780 — vale: cover plugin skill and agent paths in the opt-outs and harden the config guard
- **Labels**: bug, test; **Linked**: #779 (merged 08fdb51f); no comments, no PR
- **Requirement gate**: operator override 2026-11-17 (issue ACs concrete)

## Classification

- **Primary**: bug — **Asserted causes verified**:
  1. confirmed: `vale --output=line plugins/nolte-claude-dev/skills/agent-review/SKILL.md` reports `Vale.Terms` alerts; 37 plugin `SKILL.md`, 47 plugin agents, 24 plugin `templates|examples` dirs unmatched by `.vale.ini` root-relative opt-outs; gate unaffected (`.pre-commit-config.yaml:39` fixed-scope `task lint:prose`)
  2. from the #779 review's mutation table (inline comment false failure, partial `BasedOnStyles`, rules from other sections) — re-measured during P2
  3. confirmed: without vale on PATH the preflight's `installed` is empty → "too old" message

## Work packages

- **P1** `.vale.ini`: opt-out sections for `plugins/*/skills/**/SKILL.md`, `plugins/*/skills/**/templates/**`, `plugins/*/skills/**/examples/**`, `plugins/*/agents/*.md`, mirroring root (incl. `Microsoft.BiasFree = NO`); AC: real Vale reports nothing on those paths, positive control elsewhere
- **P2** `tests/test_vale_config.py`: inline comments; partial `BasedOnStyles` (a dropped package's named rules must be `NO`); named rules from every non-opt-out section; mutation probe per case
- **P3** `Taskfile.yml` `lint:prose` preflight: missing vale reported as such
- **Specialist (all)**: no matching specialised agent (nolte-engineering not loaded) — generalist remediation; fresh read-only review before PR

## Dependency ordering

P1, P3 independent; P2 after P1 (guard must pass on the new sections)

## Findings

| Finding | Source | Outcome | Reproduction | Issue |
|---|---|---|---|---|

## Dispatch log
