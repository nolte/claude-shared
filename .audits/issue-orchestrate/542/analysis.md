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

- 2026-08-16 P1 — `nolte-shared:spec`. `T9` authored in `test-falsifiability/{en,de}.md` with the kamerplanter worked example, the distinguishing property against T2/T8, a review-only detection route, and the reason negative verification can't reach it; fourth review question added; Non-Goals delimitation against the foundation added; `#542` recorded in References. EN/DE parity 17 headings / 10 AC / 9 categories.
- 2026-08-16 P2 — `nolte-shared:spec`. Fidelity MUST plus declared-divergence MUST plus per-tier-expression delegation added to `test-pyramid-foundation/` §"Test-double taxonomy"; `[R20]` reused for the `T9` cross-reference. Parity 20/14.
- 2026-08-16 P3 — `nolte-shared:spec`. Tier expressions added to unit (persistence boundary named as the recurring offender), component (the existing `MAY use a fake` bounded to cost rather than refusals), and integration (delimited against the in-memory-fake ban that governs the one real seam). New reference entries `[R12]`/`[R16]`/`[R13]` respectively. Parity verified per pair.
- 2026-08-16 Prose gate — Vale 3.15.2 (CI-pinned) reported four errors from the new text, all fixed: `unclosable` is not a word (three acceptance criteria reworded), and a `Microsoft.Quotes` violation from a period following a closing `§"…"` quote (sentence restructured). Re-run clean: 0 errors across the five EN files.
- 2026-08-16 P6 — `nolte-claude-dev:claude-plugin-developer`. Double-fidelity gate added to `test-code-adapter.md` phase 2, before the generalisation heuristic, so it fires before any production attribution is formed. Confirmed the file previously carried **no** falsifiability binding at all (17 other nolte-engineering artefacts cite the spec; this one did not), which validates the issue's suspicion in its point 4. **Brief corrected by the specialist, accepted:** the brief said the double is "fixed", which collides with the agent's own scope ("does not write or repair the test") and its Hard Rule 5 ("never edit an existing test"); the specialist routed the repair through the reviewable-case-change channel the file already defines, and recorded why making a double *stricter* doesn't breach the no-cheating invariant (it turns the case red and exposes the real defect). Frontmatter untouched; `validate_skills.py` exit 0.
- 2026-08-16 P6b (added mid-run, not in the original decomposition) — `nolte-claude-dev:claude-plugin-developer`. Found while auditing consumers: `test-result-analyzer.md:82` enumerates the mechanisms that make a green test suspect once a defect is confirmed, and a permissive double was absent from that list — despite the T9 worked example being exactly that shape (six green tests over a shipped defect). Dispatched to extend the enumeration. `test-pyramid-check` was checked and deliberately **not** changed: its falsifiability sweep is grep-level, and T9 is review-only by operator decision 3, so a grep entry there would misrepresent the detection route.
- 2026-08-16 P4 — `nolte-claude-dev:claude-plugin-developer`. T9 inlined into all four tier reviewers with tier-specific phrasing, plus the fidelity question as a separate sentence. One change per file, line 75 only; `git diff` confirms no frontmatter hunk; `validate_skills.py` exit 0 with the routing budget intact. Two judgement calls the specialist made and justified: the existing "three review questions" count was left alone because the spec itself frames the fidelity question as an *additional* one (`MUST additionally`), and the **polarity inversion** was stated explicitly — for the first three questions the *absence* of an answer is the finding, for the fidelity question an *easy* answer is the finding, and without that note the trailing "when no answer exists, file a finding" clause would have governed the new question backwards. **Refutation returned and accepted:** `test-tier-contract/` carries no fidelity expression at all (zero hits for `fidelity`, `more permissive`, `T9`), so a bare tier-spec reference from the contract reviewer would dangle. The specialist cited `test-pyramid-foundation/` directly in that one file and noted the tier spec doesn't restate the rule — a deliberate asymmetry against the other three. Whether the contract tier should carry a delimitation sentence is escalated to the spec-readiness audit rather than decided by the specialist.
- 2026-08-16 P5 — `nolte-claude-dev:claude-plugin-developer`. Fidelity wired into all four tier generators, each in the phase that actually chooses and builds the doubles (phase 2 for unit/component/integration; phase 3 for contract, because its phase 2 only maps the consumer-used subset and builds nothing), plus the refusal half added to each file's closest quantity-only numbered rule. Frontmatter untouched in all four; `validate_skills.py` exit 0. Correction to the brief: only `unit-test-generator` actually contains the phrase "disciplined doubles" — the other three carry differently-worded quantity-only rules, which were the ones extended. **Refutation returned and accepted, and it improves the result:** pasting the unit-tier wording into `contract-test-generator` would have restated the contract tier's own purpose, since `test-tier-contract/en.md:47` already makes consumer-double-versus-real-provider agreement a MUST and provider verification is the machine-checked mechanism enforcing it. Instead the specialist wrote the residual exposure that verification genuinely doesn't reach: **provider state**, which seeds the real provider before the replay and can arrange data the provider itself would reject (a supplied identifier the provider generates, a value its validation refuses, a duplicate its uniqueness constraint forbids). Same T9 shape, on the setup side, covered by neither the tier spec nor the agent before this change.
- 2026-08-16 P6b — `nolte-claude-dev:claude-plugin-developer`. Permissive doubles added as a sixth mechanism to the pass-side enumeration in `test-result-analyzer.md:82`, plus a reading cue built on the spec's own fidelity question pair. All three premises of the brief verified before editing; no refutation. The specialist confirmed the existing read-only boundary needs no exception for T9 — and noted independently that it's the *only* correct handling, since the spec forbids relying on negative verification for this category. One line changed; `description` byte-identical.
- 2026-08-16 P7 (spec dimension) — `nolte-shared:spec-readiness-reviewer`. **0 Critical, 1 Warning, 2 Info.** Both contradiction seams the brief flagged came back clean and explicitly refuted as risks: the integration rule delimits itself against the in-memory-fake ban in its own text, and the component rule is a coherent narrowing of the `MAY` rather than a conflict. Single-sourcing passed, with an Info note that the ~20-word opening clause recurs across four files — judged bounded and necessary so each tier carries a locally citable MUST NOT, matching how the corpus already handles the Meszaros vocabulary. Reference resolvability passed per language, verified by locating each target heading rather than pattern-matching, including the three new `[Rn]` identifiers. AC coverage and EN/DE semantic parity passed, including correct file-local RFC-2119 gloss mirroring.
- 2026-08-16 P3b (added in response to the P7 Warning) — `nolte-shared:spec`. The Warning was the contract-tier gap that P4 and P5 had each raised independently: the foundation's new delegation MUST implies universal per-tier coverage, and `test-tier-contract/` carried nothing, leaving a defensible omission undocumented. Closed in both directions rather than deferred to an Open Question, because the answer is known: (a) a Non-Goals entry records that the tier's existing exact-result-equivalence MUST (`en.md:47`) is *strictly stronger* than the portfolio floor and is enforced mechanically by provider verification, so restating the weaker rule would blur which guarantee applies; (b) a new MUST NOT covers the residual exposure P5 identified — a **provider state** that arranges data the real provider would itself reject, which provider verification structurally cannot catch because it checks the recorded interactions and never the setup preceding them. This also anchors in spec what P5 had written into `contract-test-generator`, closing the same agent-ahead-of-spec pattern P4 had flagged for the reviewer.
- 2026-08-16 Final gates — Vale 3.15.2 across all 115 EN files: **0 errors** (two further violations from the P3b text fixed: a comma outside a closing `§"…"` quote, and an `it is` the Microsoft contraction rule requires as `it's`). `validate_skills.py` exit 0. Agent-description budget **21869 / 21869 — unchanged**, and no frontmatter line appears anywhere in the agent diff. EN/DE parity verified across all six spec pairs. `check_links.py --offline` at 152 Critical, the known pre-build baseline, so no regression.
