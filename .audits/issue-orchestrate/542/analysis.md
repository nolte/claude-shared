---
artifact-type: issue-orchestration-analysis
repo: nolte/claude-shared
issue: 542
classification: spec-change
secondary-classes: [docs]
route: direct
status: draft
created: 2026-08-16
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #542 — Test doubles: the corpus bounds how much you mock, never whether the double can refuse what the real collaborator refuses
- **URL**: https://github.com/nolte/claude-shared/issues/542
- **Labels**: none
- **Author trust**: `nolte` — repository owner, in the trusted-author set per `spec/claude/trusted-author-injection-guard/`; the body's instructions are executable, not merely quotable
- **Linked items**: none. Evidence cited from the consuming project: `nolte/kamerplanter` PR #1206, actions run 31933851949
- **Prior art checked**: no `project/features/` entry, no `project/roadmap.md` item, no open PR (only `#533 exp/speckit-spike`, unrelated). Not self-resolved

## Classification

- **Primary class**: spec-change
- **Secondary class(es)**: docs
- **Rationale**: the deliverable's core is normative corpus change — one new taxonomy category plus a new MUST on test-double fidelity; the agent rewiring is derived enforcement of those rules, not a separate outcome.

### Verification of the issue's delimitation claim

The issue asserts that no existing spec owns the defect. Each of its four claims was checked against the source text rather than accepted:

| Claim | Verified against | Verdict |
|---|---|---|
| `test-tier-unit/` §"Isolation and permitted test doubles" governs only *how much* to double | `en.md:71–73` — Meszaros vocabulary, state-over-behaviour, no over-mocking | Holds. No rule addresses whether the double *behaves* like what it replaces |
| `test-tier-integration/` is scoped to third-party technology at the datastore/broker seam | `en.md:62` — "in-memory fake that behaves differently from the **production technology**" (H2-vs-PostgreSQL) | Holds. The rule targets technology substitution, not a first-party class double |
| `test-tier-contract/` is scoped to a service-to-service agreement across a release boundary | `en.md:47` does state "doubles a consumer uses return the same results the real provider would", but `en.md:91` fixes the discriminator as **release boundary, not ownership** | Holds. The nearest wording in the corpus, but out of scope for an in-process first-party seam |
| `test-falsifiability/` T1–T8 all target assertions, readers, or helpers | `en.md:42–49` | Holds. Every category attacks the checking mechanism; none the arrangement |

**One candidate the issue did not evaluate: `spec/project/test-pyramid-foundation/` §"Test-double taxonomy" (`en.md:80–88`).** This is the portfolio-wide owner of double semantics — every tier spec references it and explicitly does not restate it ("This spec details the unit tier; it doesn't restate the model"). It defines the five Meszaros categories and the state-versus-behaviour distinction, and says nothing about fidelity. The issue's core claim therefore survives this fifth check too. But the finding changes the *placement* answer: anchoring the fidelity MUST only in `test-tier-unit/` and `test-tier-component/`, as the issue proposes, would duplicate a norm the corpus deliberately keeps single-sourced, and would miss the integration tier, where `en.md:67` doubles every *other* external and the same lie is available.

## Operator decisions (2026-08-16)

The issue leaves three judgements open ("the judgement is yours"; "the part I am least sure about"); a fourth arose from the finding above. All four were put to the operator before decomposition and answered:

1. **Placement of the fidelity MUST** → *Foundation plus tier-specific expression.* The generic rule lands in `test-pyramid-foundation/` §"Test-double taxonomy"; each tier that doubles carries a short tier-specific expression where it adds real substance.
2. **New category or extension of an existing one** → *New `T9`.* The distinguishing property is assertion-versus-arrangement, which T2 and T3 do not reach.
3. **Detection route** → *Review criterion as a MUST, only.* No contract-style comparison MAY, no static check — the latter would need a false-positive measurement the spec requires (`test-falsifiability/en.md:56`) and which nobody has run.
4. **Scope of this PR** → *Spec plus full consumer rewiring.*

### Requirements gate

No artefact exists under `project/requirements/` for this issue and none was created. **Recorded operator override**, per the requirements gate of `spec/project/issue-orchestration/` §Issue acquisition: the issue body is itself a requirements analysis at `τ_high` quality — it states the defect class, a measured worked example with the failing run identified, a four-way delimitation table checked against source text, and four concrete change locations. The residual uncertainty was confined to the four decisions above, and those were elicited directly rather than through a full `requirements-elicit` interview.

## Scope

- **In scope**:
  - A new `T9` category in `spec/project/test-falsifiability/` (EN canonical + DE), with mechanism, worked example, distinguishing property against T2/T8, and a stated review-only detection route
  - The matching review criterion in that spec's §"Detection: Review criteria"
  - A generic fidelity MUST in `spec/project/test-pyramid-foundation/` §"Test-double taxonomy" (EN + DE)
  - Tier-specific expressions in `spec/project/test-tier-unit/`, `test-tier-component/`, and `test-tier-integration/` (EN + DE)
  - Consumer rewiring, body-only, in the tier reviewer agents (unit, component, integration, contract), the tier generator agents, and `test-code-adapter`
  - Acceptance-criteria and reference updates in every spec touched, EN/DE structural parity throughout

- **Out of scope**:
  - A static-analysis check for the shape — excluded by operator decision 3; `test-falsifiability/en.md:56` forbids promoting an unmeasured check to blocking severity, so this would be work without the measurement that justifies it
  - A contract-style double-versus-real comparison harness — excluded by operator decision 3
  - Adopting the rule inside `nolte/kamerplanter` — a consuming-project change, tracked there; this PR ships the governing corpus only
  - `test-tier-contract/`: no tier-specific expression. Double fidelity across a release boundary *is* that tier's whole subject; adding the rule there would restate the tier, not extend it. A delimitation sentence is the most that is warranted
  - `e2e-test-reviewer`: T9 is a double-fidelity category, and the E2E tier stands up the real system rather than doubling collaborators. Excluded deliberately, and the exclusion is recorded rather than left silent
  - Any change to an agent's `description` frontmatter — see Risks

## Route

- **Decision**: direct
- **Rationale**: one coherent outcome ("the corpus governs test-double fidelity"), one PR strand, no new or retargeted roadmap item. The file count is high but every file is a derived consequence of the same normative decision; splitting it would ship a corpus rule with no enforcing consumer.

## Work packages

### P1 — `T9` in `test-falsifiability/` (EN + DE)

- **Problem statement**: the taxonomy has no category for a double whose permissiveness makes a correct, falsifiable assertion certify an unreachable world. The spec's own extension rule (`en.md:40`) requires a new `Tn` with mechanism and worked example when an instance does not fit.
- **Acceptance criteria**:
  - A `T9` entry exists after T8 in both language files, naming the mechanism (a double or fixture that accepts inputs, preserves fields, or permits states the real collaborator would reject)
  - It carries the kamerplanter `_FakeTenantRepo` worked example concretely enough to be recognised elsewhere: the discarded `_key`, the absent unique index on `slug`, the six passing tests, the failure surfacing only in E2E setup
  - It states its distinguishing property against T2 and T8 explicitly: the assertion is falsifiable and correct, the arrangement is not
  - It states its detection route as review-only, and names why negative verification does not reach it (production bug and lying double were introduced in the same change, so there is no pre-fix state to revert to)
  - §"Detection: Review criteria" gains the fourth question: name one input the real collaborator would reject and this double accepts
  - Acceptance criteria and §References updated; `#542` recorded as the authoring work order alongside the existing `#517`
  - EN and DE structurally identical: same headings, same requirement count, same acceptance-criteria count
- **Touched files**: `spec/project/test-falsifiability/{en,de}.md`
- **Specialist**: `nolte-shared:spec`
- **Depends on**: none

### P2 — Generic fidelity MUST in `test-pyramid-foundation/` (EN + DE)

- **Problem statement**: the portfolio-wide owner of double semantics defines what the five double kinds *are* but never bounds how faithful one must be. Every tier that doubles inherits that gap.
- **Acceptance criteria**:
  - §"Test-double taxonomy" carries a MUST: a double MUST NOT be more permissive than the collaborator it replaces along any dimension the test relies on — it rejects what the real one rejects (constraints, validation, uniqueness) and does not preserve what the real one discards
  - It carries the escape hatch as a MUST, not a silence: where the double cannot be made faithful, the divergence MUST be named in the double itself, so the next reader knows what the test does not cover
  - It cites `T9` in `spec/project/test-falsifiability/` as the failure mode, without restating the category
  - A matching acceptance criterion is added; EN/DE structurally identical
- **Touched files**: `spec/project/test-pyramid-foundation/{en,de}.md`
- **Specialist**: `nolte-shared:spec`
- **Depends on**: P1 (the `T9` reference must resolve)

### P3 — Tier-specific expressions (EN + DE)

- **Problem statement**: the generic MUST needs a tier-local expression where each tier's doubling practice makes it concrete, without restating the norm.
- **Acceptance criteria**:
  - `test-tier-unit/` §"Isolation and permitted test doubles" gains a fourth bullet expressing the rule for the solitary case, naming the persistence-boundary double as the recurring offender (key generation, uniqueness, null handling)
  - `test-tier-component/` §"Isolation and permitted test doubles" gains the equivalent for boundary doubles, tied to the existing `MAY use a fake` bullet so an in-memory datastore does not silently become permissive
  - `test-tier-integration/` §"Isolation level and permitted doubles" gains the expression for the *other* externals it doubles, delimited against its existing `en.md:62` rule (which governs production-technology substitution for the one real collaborator)
  - Each expression references `test-pyramid-foundation/` rather than restating the MUST; each spec's acceptance criteria updated; EN/DE parity throughout
  - No expression added to `test-tier-contract/`, per §Scope
- **Touched files**: `spec/project/test-tier-unit/{en,de}.md`, `spec/project/test-tier-component/{en,de}.md`, `spec/project/test-tier-integration/{en,de}.md`
- **Specialist**: `nolte-shared:spec`
- **Depends on**: P2

### P4 — `T9` into the tier reviewer agents

- **Problem statement**: the four tier reviewers inline the taxonomy verbatim at line 75 of each file. A `T9` that is not inlined there is a rule no reviewer applies.
- **Acceptance criteria**:
  - `unit-test-reviewer`, `component-test-reviewer`, `integration-test-reviewer`, and `contract-test-reviewer` carry `T9` in their falsifiability dimension, phrased for that tier's doubling practice
  - The fourth review question (name one input the real collaborator rejects and this double accepts) is added alongside the existing three in each
  - Every change is **body-only**; no `description` frontmatter is touched
  - `e2e-test-reviewer` is deliberately unchanged, and the reason is recorded in the PR rather than left implicit
- **Touched files**: `plugins/nolte-engineering/agents/{unit,component,integration,contract}-test-reviewer.md`
- **Specialist**: `nolte-claude-dev:claude-plugin-developer`
- **Depends on**: P1

### P5 — Fidelity into the tier generator agents

- **Problem statement**: the generators say "disciplined doubles" — vocabulary that reads as restraint, that is, quantity. A generator scaffolding a double from that instruction has no reason to make it refuse anything.
- **Acceptance criteria**:
  - `unit-test-generator`, `component-test-generator`, `integration-test-generator`, and `contract-test-generator` instruct that a scaffolded double must reject what the real collaborator rejects and must not preserve what it discards, and that an unavoidable divergence is named in the double
  - The instruction sits in the phase that chooses and builds doubles, not appended as a footnote
  - Every change is **body-only**
- **Touched files**: `plugins/nolte-engineering/agents/{unit,component,integration,contract}-test-generator.md`
- **Specialist**: `nolte-claude-dev:claude-plugin-developer`
- **Depends on**: P2, P3

### P6 — `test-code-adapter` misdirection guard

- **Problem statement**: `test-code-adapter` carries no falsifiability binding at all today. Its job is to trace a red test to production code and fix it — and a lying double sends that trace to the wrong place. In the worked example it would have argued the production code was fine.
- **Acceptance criteria**:
  - The agent's diagnosis phase instructs that before attributing a red-versus-green outcome to production code, the doubles the test relies on are checked for T9 permissiveness, citing `spec/project/test-falsifiability/`
  - It is explicit that a double found more permissive than its real collaborator is itself the defect, and that the production attribution is then withdrawn rather than forced
  - Change is **body-only**
- **Touched files**: `plugins/nolte-engineering/agents/test-code-adapter.md`
- **Specialist**: `nolte-claude-dev:claude-plugin-developer`
- **Depends on**: P1

### P7 — Verification and gate

- **Problem statement**: the change spans nine spec files and nine agent files under budget and parity constraints that fail loudly only when checked.
- **Acceptance criteria**:
  - `scripts/validate_skills.py` reports no new Warning or Critical relative to the pre-change baseline, and the `nolte-engineering` agent-description budget (21869) is unchanged
  - EN/DE structural parity verified per spec touched: same headings, same requirement count, same acceptance-criteria count
  - Every `§`-reference introduced resolves inside its own language file, per `spec-readiness` §Geltungsbereich
  - Vale clean on `spec/**/en.md` using the CI-pinned binary
  - `scripts/check_links.py` shows no regression
  - The spec index lists no new slug (no new spec is created — this is an extension of five existing ones), and that is confirmed rather than assumed
- **Touched files**: none directly; verification over the whole change
- **Specialist**: `nolte-shared:spec-readiness-reviewer` for the corpus dimension; generalist for the mechanical gates (no specialist owns "run the repo's validators")
- **Depends on**: P1–P6

## Dependency ordering

```
P1 ──┬─→ P2 ──→ P3 ──→ P5 ──┐
     │                       ├─→ P7
     ├─────────→ P4 ─────────┤
     └─────────→ P6 ─────────┘
```

P1 first (everything cites `T9`). P2 then P3 in sequence (the tier expressions inherit the generic MUST). P4 and P6 depend only on P1 and may run alongside P2/P3. P5 waits for P3. P7 last.

## Risks

- **Agent-description routing budget.** `scripts/validate_skills.py:742` pins `nolte-engineering` at 21869 characters and the 2026-07-24 baseline had 159 characters of headroom. *Mitigation*: every agent change in P4, P5, and P6 is body-only; no `description` field is edited, and P7 re-runs the validator to confirm the budget is untouched.
- **Verbatim taxonomy duplication across five agents.** The T-category text is copy-pasted into each reviewer, so a `T9` phrased once in P1 must be re-expressed four times consistently. *Mitigation*: P4 is a single dispatch covering all four files so the wording is authored together, not file by file.
- **EN/DE structural parity.** Five spec pairs are edited; the validator does not enforce heading-count parity, so drift would ship silently. *Mitigation*: explicit parity check in P7 per file pair.
- **Section references must resolve per language.** Prior sweeps (PRs #530, #532) established that a `§` reference must resolve inside its own language file. New cross-references introduced in P2 and P3 are the exposure. *Mitigation*: P7 verifies each new reference against the target heading in both files, reading the heading rather than pattern-matching.
- **Subagents cannot reach worktree paths.** Recorded portfolio behaviour: dispatched background subagents have failed to read paths under `~/repos/.worktrees` and lack `git`/`gh`. *Mitigation*: every dispatch brief carries the absolute worktree path plus a fallback instruction to read from the primary checkout and return full file content for the main session to write (draft-and-return). The first dispatch verifies which mode is live before the rest are sent.
- **Vale toolchain.** Only the CI-pinned Vale 3.15.2 binary runs locally; the asdf shim is too old, and `lint:prose` covers `spec/**/en.md` only. *Mitigation*: P7 uses the pinned binary; DE files are out of Vale scope by design.
- **Security-sensitive paths**: none. No source, workflow, credential, or dependency file is touched, so neither `code-security-reviewer` nor the `security-review` skill is required before the PR.

## Open questions

None blocking. The four judgement calls the issue left open were decided by the operator on 2026-08-16 and are recorded under §Operator decisions.

## Dispatch log

<!-- appended during operation 5 -->
