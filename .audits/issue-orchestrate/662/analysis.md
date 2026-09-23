# Pre-analysis: nolte/claude-shared#662

status: awaiting-approval
classification: feature-request
route: implement directly
run: 20260923T094500Z-cre1

## Issue

"Build the executor for the capability reach audit." Author `nolte`, the repository owner,
so the body is trusted input. The issue was filed from #660's closeout as the named
remainder of that work: `spec/project/capability-reach-audit/` landed with 26
requirements and, by its own §Non-Goals line 38, specifies no executor.

## Classification

`feature-request`: a new capability, a skill plus a scanner agent plus a runner. No
secondary class. The classes that require an explicit confirmation gate (`security`,
`spec-change`) do not apply, and nothing in the change touches a credential, a workflow, or
a spec rule.

## Requirements gate

Satisfied by `project/requirements/capability-reach-executor.md`, produced in this run by
a ten-question `requirements-elicit` interview that terminated by saturation with
`U_gate = 0.80 = τ_high`. Twenty requirements, eighteen `confirmed` by teach-back, two
`assumed` and named as risks (R10, R18). Every work package below cites the requirements
it discharges; a package citing none would be scope creep.

## Measured findings that shape the decomposition

- **All four audit precedents in `nolte-engineering` are a single `SKILL.md` plus a
  read-only scanner agent, with no bundled script.** Verified by listing
  `plugins/nolte-engineering/skills/*/scripts/`: none exist. They are stateless
  reporters, so the shape covers derivation and reporting but not execution.
- **The repository does bundle scripts elsewhere**: `nolte-media`'s `image-generate`
  ships `scripts/image_generate.py`, invoked through `${CLAUDE_PLUGIN_ROOT}`, with its
  tests under `tests/`. The runner here has the same character: deterministic logic
  (execute, compare, classify, detect change, render) that must not be re-derived by the
  model each run and must be testable by mutation. It follows that precedent.
- **The probe format has no precedent in the repository.** R1 to R3 fix its fields and
  change mechanism; the schema is new. Governed data in this repository is validated by
  `scripts/validate_schemas.py` against `schemas/`, so the probe schema goes there and the
  pre-commit hook covers it.
- **The five defects the spec's acceptance table names live in `nolte/kamerplanter`.** The
  probes for them belong in that repository's `project/reach-probes/` (R11), not here.
  What this change proves locally is that the runner executes a T0 and a T1 probe end to
  end against local stand-ins, and that the executor can emit all five probe files; the
  three T2 rows are proven by a linked dogfooding run in `kamerplanter` (R19).

## Scope

**In scope**: the runner script and its tests; the probe schema; the scanner agent; the
skill; worked example probes for the five defects; the two authoring reviews.

**Out of scope**: any change to the governing spec; running the T2 probes in this
repository; a scheduled or CI-driven mode; auditing a repository without a local working
copy; the `kamerplanter` dogfooding run itself, which is its own follow-up in that
repository and is linked from the pull request when it exists.

## Work packages

| id | Problem | Acceptance | Files | Specialist | Depends on |
|---|---|---|---|---|---|
| P1 | The runner: load probes, execute observation steps, compare in the runner, classify, detect a changed declaration through git history and a weakened probe, honour the T2 opt-in, obtain environments through Taskfile targets, refuse a non-local target, render the report | R1–R3, R5–R16 each has a test that fails when the rule is removed, negative-verified from a file copy; the probe schema validates under `validate_schemas.py`; a T0 probe against a local git repository and a T1 probe against a loopback server both run end to end | `plugins/nolte-engineering/skills/capability-reach-audit/scripts/reach_audit.py`, `schemas/reach-probe-v1.0.schema.yaml`, `tests/test_reach_audit.py` | agent: `nolte-engineering:fullstack-developer` | — |
| P2 | The scanner agent: inventory the four declaration sources of a local working copy and draft candidate probes in the P1 schema, returning them without writing | R18; the agent is read-only by its tool list; `agent-review` passes | `plugins/nolte-engineering/agents/capability-reach-scanner.md` | agent: `nolte-claude-dev:claude-plugin-developer` | P1 (schema) |
| P3 | The skill: operations `derive`, `approve`, `run`, `report`; dispatches P2, gates on operator approval before persisting, invokes P1 through `${CLAUDE_PLUGIN_ROOT}`, cites the spec and resumable-work, checkpoints after the gate | R4, R5, R8, R13, R17, R20; `skill-review` passes; description within the routing budget | `plugins/nolte-engineering/skills/capability-reach-audit/SKILL.md` and `references/` | agent: `nolte-claude-dev:claude-plugin-developer` | P1, P2 |
| P4 | Worked examples: the five probe files for the spec's acceptance table, in the P1 schema, plus the T0 and T1 execution evidence | R19; all five validate against the schema; the T0 and T1 examples are the ones P1's end-to-end tests execute | `plugins/nolte-engineering/skills/capability-reach-audit/examples/` | agent: `nolte-engineering:fullstack-developer` | P1 |
| P5 | Independent authoring reviews and repair | No Critical from `skill-review` or `agent-review` remains | P2, P3 outputs | skills: `nolte-claude-dev:skill-review`, `nolte-claude-dev:agent-review` | P2, P3, P4 |

**Ordering**: P1 first, then P2 and P4 in parallel (both consume only P1's schema and
CLI), then P3, then P5. P3 cannot name the agent's return shape before P2 exists, and P5
must read finished artefacts.

## Specialist resolution

Resolved at runtime against the four distribution roots. `fullstack-developer` matches the
runner and the examples on its stated responsibility (production-ready code with tests
against the project's own stack). `claude-plugin-developer` matches the skill and the
agent (drafts a plugin artefact in conformance with `spec/claude/`). `skill-review` and
`agent-review` match P5. No package lacks a specialist, so no portfolio gap is recorded.

## Dispatch briefs authorise refutation

Each brief states its package as a hypothesis. The ones most likely to be refuted, and
what a refutation would mean:

- **P1**: that git history alone detects a changed declaration for every in-repository
  anchor. A refutation would be an anchor the runner cannot resolve to a file, which R6
  already routes to "unmonitored", so the runner must handle it rather than fail.
- **P2**: that a read-only agent can draft a T2 probe's observation step without running
  anything. If drafting needs to inspect the target's Taskfile at depth, that is still
  reading; if it needs to execute, the drafting belongs in the skill and R18 is refuted.
- **P3**: that the approval gate fits in one skill turn. If a repository declares hundreds
  of entries, per-probe approval is unusable and the gate needs batching by declaration
  source.

## Risks

- **The probe format is new and load-bearing.** A schema that admits a self-asserting
  probe reintroduces the defect the spec exists to catch. P1's schema must make the
  expected observation a typed count or set and must give the observation step no field
  in which to emit a verdict.
- **T2 is proven outside this repository.** If the `kamerplanter` run does not happen
  before the pull request closes, three of the five acceptance rows are unproven and the
  pull request must say so.
- **Scope is large by operator decision.** All three tiers in one strand. The ordering
  above keeps each dispatch atomic, but the pull request will be the largest of this
  series and the review has to be proportionate.

## Defect-class decision

Not a defect-closing run. The pull request is type `feat` and carries no `## Class sweep`.
