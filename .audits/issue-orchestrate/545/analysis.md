---
artifact-type: issue-orchestration-analysis
repo: nolte/claude-shared
issue: 545
classification: spec-change
secondary-classes: [refactor]
route: direct
status: draft
created: 2026-08-16
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #545 — A cause claimed in an artefact is unverified by any rule — the mechanism bar gates changes, not assertions
- **URL**: <https://github.com/nolte/claude-shared/issues/545>
- **Labels**: none
- **Linked items**: none linked. Sibling referenced in the body: #542 (closed, merged as `a786087`) — the test-double half of the same "trusted because never asked to fail" family.
- **Prior art checked**: no `project/features/` entry; no `project/roadmap.md` item; no requirement artefact before this run; the only open PR is `exp/speckit-spike` (#533), unrelated. No merged change closes the issue.
- **Author trust**: `nolte` = repository owner = trusted author per `spec/claude/trusted-author-injection-guard/`. Zero comments, so no untrusted text in the surface.

## Classification

- **Primary class**: spec-change
- **Secondary class(es)**: refactor
- **Rationale**: the issue asks for a corpus rule that does not exist and for its binding into existing artefacts; there is no code defect and no new product capability. The secondary `refactor` reading (lifting the mechanism bar out of §A) was considered and **rejected at the requirements gate** — §A stays where it is.

## Scope

- **In scope**: a new cross-cutting spec under `spec/claude/` owning the provenance of load-bearing repo-factual claims; its application in `spec/project/e2e-failure-diagnosis/` §A; delimiting cross-references from the two sibling `spec/claude/` specs; body-only bindings in the six finding-emitting agents and the five publishing skills; the spec index row; the readiness and prose gates.
- **Out of scope**:
  - Relocating §A out of `e2e-failure-diagnosis` — decided against; §A stays and applies the new owner.
  - Retrofitting existing artefacts that carry unmarked claims (this repo or the portfolio) — a separate tracked issue if wanted.
  - A linter or scanner for the rule — the substance-over-wording decision (R8) means there is nothing deterministic to grep yet; revisit only if a machine-read carrier gains a field.
  - Any `description:` frontmatter growth — forbidden by R10.
  - Test-code falsifiability, repo-external assertion sourcing, and the remediation side of a proven cause — owned by `test-falsifiability`, `research-triangulate`, and the test-cycle specs respectively.

## Requirements basis

`project/requirements/claim-provenance-discipline.md`, elicited 2026-08-16 via `requirements-elicit`.
`U_gate = 0.85 ≥ τ_high = 0.8`; termination by saturation, 4 of 6 budgeted questions used. R1–R10 and R12 are `confirmed` by teach-back; R11 and R13 are `assumed` corpus conventions that discharge at the readiness gate.

The gap this closes, stated against the corpus as it exists:

| Existing rule | What it owns | Why it cannot catch the issue's evidence |
|---|---|---|
| `e2e-failure-diagnosis` §A | mechanism proof, sufficient + necessary | gates a **change**, and is reached only from a red E2E cluster |
| `spec/claude/dispatch-brief/` | hypothesis in a brief must authorise refutation | needs **two parties**; all three false claims were self-directed |
| `spec/claude/research-triangulate/` | assertions about repo-**external** facts | its §Requirements explicitly excludes repo-internal assertions |
| `spec/project/test-falsifiability/` | a test that cannot fail is not a test | scope is **test code**, not prose claims |
| `spec/claude/review-plan/` | finding format, cites the spec requirement | cites the **rule**, never the evidence for the named cause |

## Route

- **Decision**: direct
- **Rationale**: one coherent outcome (the rule exists and is wired), a single PR strand, no new or retargeted roadmap item. This is the same shape and comparable size as PR #531, which lifted `dispatch-brief` out of §E and wired six dispatchers in one strand.
- **Pipeline hand-off**: not applicable.

## Work packages

### P1 — Author the cross-cutting provenance spec

- **Problem statement**: the corpus has no owner for the provenance of a load-bearing factual claim about the working copy. Author one under `spec/claude/`, English-canonical with a synchronised German translation, carrying R2–R8 and R12 as testable requirements and R11 as an explicit §Delimitation.
- **Acceptance criteria**:
  - The spec exists at `spec/claude/claim-provenance/en.md` and `.../de.md` with the corpus house-style section set (Context, Goals, Non-Goals, Requirements, Acceptance Criteria, References, Open Questions) and a `Portfolio-Scope: portfolio` header.
  - The in-scope claim class is defined so a reviewer can decide whether a given sentence is in scope: checkable against the working copy **and** load-bearing for another actor's work; cause, state, existence, and absence all qualify (R2); judgements, proposals, repo-external assertions, and live conversation do not (R3).
  - The carrier set is defined by the "outlives the session" test, with the enumerated examples as illustration rather than a closed list (R4).
  - Exactly two markers are required, each with its own stated obligation: established → name the observation that established it, as a command with output or a `file:line` (R5); unestablished → name the observation that would settle it and state that it was not made (R6).
  - The measure-when-cheap duty is stated as a `MUST` with the cost claim itself required in the artefact (R7).
  - A `MUST` states that the distinction is checked on substance, not on a verbatim token, with a canonical form offered (R8), following the `dispatch-brief` precedent.
  - §Delimitation names all four neighbours and restates none of their rules (R11).
  - Every `§` reference resolves inside its own language file (R13).
  - `task test` passes.
- **Touched files / artifacts**: `spec/claude/claim-provenance/en.md`, `spec/claude/claim-provenance/de.md`
- **Specialist**: `nolte-shared:spec` (skill) — its description names multilingual spec creation with a canonical source and synchronised translations, which is exactly this package.
- **Depends on**: none

### P2 — Wire the sibling specs and the index

- **Problem statement**: three existing specs abut the new one and one of them (§A) currently carries the general form of the rule inside an E2E-routed section. Make §A *apply* the new owner without relocating it, and close the loop from the two `spec/claude/` siblings so a reader arriving at either is routed to the right owner.
- **Acceptance criteria**:
  - `spec/project/e2e-failure-diagnosis/` §A cross-references the new spec and states its E2E-specific application; the sentence at §A that states the sufficient-and-necessary bar is retained, not deleted, so `test-result-analyzer.md:29` ("prove its mechanism before routing (its §A)") keeps resolving.
  - Its §Delimitation and §References gain the new spec.
  - `spec/claude/dispatch-brief/` gains a cross-reference distinguishing the delegated case (two parties) from the self-directed case (new owner), without restating either rule.
  - `spec/claude/research-triangulate/` gains a cross-reference at the point where it excludes repo-internal assertions, naming the new spec as that exclusion's owner.
  - All four edits land in both `en.md` and `de.md`.
  - `spec/README.md` carries an index row for the new spec matching the table's column contract.
  - `task test` passes and `scripts/check_links.py` reports no regression.
- **Touched files / artifacts**: `spec/project/e2e-failure-diagnosis/{en,de}.md`, `spec/claude/dispatch-brief/{en,de}.md`, `spec/claude/research-triangulate/{en,de}.md`, `spec/README.md`
- **Specialist**: `nolte-shared:spec` (skill)
- **Depends on**: P1 — the section anchors and the spec's final name must exist before anything references them.

### P3 — Bind the finding-emitting agents

- **Problem statement**: six reviewer and analyzer agents produce findings whose entire value is the stated cause. Their bodies must require the marker distinction inside the finding itself rather than in a covering note (issue §"What I think should change" 4).
- **Acceptance criteria**:
  - Each of the six agent bodies references the new spec and states that a finding naming a cause carries the distinction in the finding.
  - No `description:` field changes in any of the six (R10) — verifiable by diffing frontmatter.
  - `scripts/validate_skills.py` passes; the summed description budget is unchanged.
- **Touched files / artifacts**: `plugins/nolte-engineering/agents/{python-code-reviewer,frontend-code-reviewer,test-result-analyzer,code-security-reviewer,deployment-change-analyzer,e2e-result-reviewer}.md`
- **Specialist**: `Agent(subagent_type="nolte-claude-dev:claude-plugin-developer")` — its description names drafting and refining a plugin artifact in strict conformance with every spec under `spec/claude/`, which is this package's contract.
- **Depends on**: P1

### P4 — Bind the publishing skills

- **Problem statement**: the three false claims in the issue's evidence landed in an issue body and a commit message — the artefact side, not the finding side. The skills that write durable artefacts must carry the rule where they compose that prose.
- **Acceptance criteria**:
  - Each of the five skill bodies references the new spec at the point where it composes claim-bearing prose.
  - No `description:` field changes (R10).
  - `scripts/validate_skills.py` passes with **no new** `body-token-approaching` warning and no `body-token-cap` Critical.
  - Four of the five targets are already inside the 4,500-token warning band, so every binding except the one in `spec` **MUST** be a replacement edit that is net-neutral or net-negative in body length, not an append. Measured 2026-08-16 with `scripts/validate_skills.py` (the token authority; the 4-char heuristic at `scripts/validate_skills.py:441`):

    | Skill | body tokens (est.) | headroom to the 5,000 cap |
    |---|---|---|
    | `pull-request-create` | 4974 | 26 |
    | `issue-orchestrate` | 4843 | 157 |
    | `feature-decompose` | 4595 | 405 |
    | `lektorat-apply` | 4580 | 420 |
    | `spec` | 3173 | 1827 |

- **Touched files / artifacts**: `skills/{issue-orchestrate,pull-request-create,feature-decompose,spec}/SKILL.md`, `skills/lektorat-apply/SKILL.md`
- **Specialist**: `Agent(subagent_type="nolte-claude-dev:claude-plugin-developer")`
- **Depends on**: P1

### P5 — Readiness and prose gates

- **Problem statement**: the new spec's principal risk is contradicting or silently duplicating one of its four neighbours, and the corpus enforces a Vale gate on `spec/**/en.md`.
- **Acceptance criteria**:
  - `spec-readiness-reviewer` reports no Critical finding for the new topic; every Warning is either fixed or recorded with a rationale.
  - Vale passes on the new `en.md` at the CI-pinned version (3.15.2) with no new alerts attributable to this change.
  - No rule of `dispatch-brief`, `research-triangulate`, `e2e-failure-diagnosis` §A, or `test-falsifiability` is restated in the new spec (R11) — checked explicitly, not assumed.
- **Touched files / artifacts**: read-only over P1/P2 output; any fixes land back in those files.
- **Specialist**: `Agent(subagent_type="nolte-shared:spec-readiness-reviewer")` for the contradiction/completeness dimension; `Agent(subagent_type="nolte-shared:prose-vale-curator")` for the Vale dimension.
- **Depends on**: P1, P2

## Dependency ordering

```
P1 ──┬── P2 ──┬── P5
     ├── P3   │
     └── P4 ──┘
```

P1 first and alone. P2, P3, P4 are mutually independent once P1 lands and may dispatch concurrently. P5 gates the PR and runs after P2.

## Risks

- **The rule is written so broadly that it becomes noise and gets ignored.** This is the failure mode the issue itself names. Mitigation: R12 caps the required output at a marker plus one named observation; P5's readiness review checks the requirement count and the per-requirement cost.
- **The new spec restates a neighbour's rule and forks it.** The corpus has been bitten by this before. Mitigation: R11 is a P1 acceptance criterion and re-checked independently in P5.
- **§A is weakened while being rewired, breaking `test-result-analyzer.md:29`.** Mitigation: P2's criteria require the sufficient-and-necessary sentence to be *retained*, and the reference to be additive.
- **Agent `description` budget regression.** The summed budget sits near the routing ceiling and is treated as a regression watchdog. Mitigation: R10 makes every binding body-only; P3 and P4 both verify frontmatter is untouched.
- **Skill token budget — the tightest constraint in this run.** Measured, not assumed: four of P4's five targets already sit in the 4,500-token warning band, and `pull-request-create` has 26 tokens (~100 characters) of headroom before the enforcing 5,000-token Critical cap. An appended binding is impossible there and tight in three more. Mitigation: P4 binds by *replacing* existing prose with a reference-carrying rewrite, budget-neutral or negative, everywhere except `spec`; the acceptance criterion is a clean `validate_skills.py` run with no new warning. If a target cannot absorb the reference without losing something load-bearing, the fallback is to bind it in `references/` and point at it, per the validator's own advice.
  <!-- This risk was first written from memory, naming `issue-orchestrate` and
       `portfolio-inflight-triage` as "the known tight ones". The measurement
       refuted it: `portfolio-inflight-triage` is not a P4 target at all, and the
       binding constraint is `pull-request-create`. Corrected in place; recorded
       here because it is the failure mode #545 exists to prevent. -->
- **Vale is only locally runnable at the CI-pinned version.** The corpus gate covers `spec/**/en.md`; the asdf shim resolves an older Vale than CI. Mitigation: P5 runs the pinned 3.15.2 binary, and pre-existing alerts in files this change does not touch are not this PR's to fix.
- **Security-sensitive paths**: none. This change touches specification prose, agent bodies, and skill bodies only — no code, no CI configuration, no credentials, no permission surface. `code-security-reviewer` and the `security-review` skill are therefore **not** required before the PR, per `spec/project/issue-orchestration/` operation 6. Recorded explicitly so the omission is a decision rather than an oversight.
- **Bilingual drift.** Six spec files change across two languages. Mitigation: the `spec` skill's translation-sync operation owns this; `task test` and the §-resolvability rule are the check.

## Open questions

1. ~~The spec's folder name is not settled.~~ **Settled 2026-08-16: `spec/claude/claim-provenance/`**, titled "Claim Provenance" / "Herkunft von Behauptungen". `claim-verification` was rejected because the rule deliberately permits publishing an unestablished claim, so the name would overpromise; `assertion-provenance` was rejected because `assertion` is already load-bearing for test code in `test-falsifiability`, the spec this one delimits against.
2. **Whether `spec/claude/review-plan/` gains an optional provenance field for findings.** R8 fixed substance-over-wording for prose; two carriers already have a machine format. Recorded as out of scope for this run in the requirements artefact; raise as a follow-up issue if P3 finds the finding format inadequate without it.

## Dispatch log

2026-08-16 P1 dispatched to skill `nolte-shared:spec` — spec/claude/claim-provenance/ authored EN+DE, exact structural parity, vale clean. Commit 1145aea.
2026-08-16 P2 dispatched to skill `nolte-shared:spec` — four neighbours wired, §A retained and extended, index row added. Commit 51712a8.
2026-08-16 P3 dispatched to `nolte-claude-dev:claude-plugin-developer` — six agents bound, body only. REFUTED four parts of the brief, all accepted: deployment-change-analyzer states no causes at all (:79, :86) so the binding attaches to its existence/absence pairs; python-code-reviewer (:134) and frontend-code-reviewer (:176) already carry a confirmed|suspected flag that nothing required to name an observation, so the binding attaches to the existing flag rather than adding a second vocabulary; e2e-result-reviewer (:32) already asked what the screenshots could not settle but in a covering note, which is the form the spec rules out, so only that delta was bound; test-result-analyzer's §A reference (:29) was scoped to E2E, so the binding generalises it. Commit 88dfeef.
2026-08-16 P4 dispatched to `nolte-claude-dev:claude-plugin-developer` — five skills bound, body only, four paid for out of the same file. REFUTED the net-neutral hypothesis for issue-orchestrate with numbers (operation 3 is 1156 chars, 125 compress losslessly, the shortest conforming wording is 301, hence +176); accepted, the file stays 450 chars under the cap. Narrowed lektorat-apply to the absence claim only, because its findings are judgements (out of scope per §A) already carrying file, line and sample. The specialist marked one claim unestablished (markdownlint on the indented paragraph in skills/spec) and named the settling observation; observation made, markdownlint passes. Commit 300a18d.
2026-08-16 P5 dispatched to `nolte-shared:spec-readiness-reviewer` — zero Critical against the spec; the no-restatement claim held under adversarial cross-check of all five neighbours. Three AC coverage gaps and one Info clarification closed; two pre-existing ghost references of one bug class found in neighbour files, verified, and repaired. Commits 4b1172e, 1cf6a09.

Gate: `task --yes check` exit 0 — vale clean, every pre-commit hook passed, 159 tests passed, link check 0 critical.
Security: no security-sensitive path touched (spec prose, agent bodies, skill bodies only), so `code-security-reviewer` and `security-review` were not required. Recorded as a decision, not an omission.
