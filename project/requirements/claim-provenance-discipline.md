# Requirements — Provenance discipline for load-bearing claims in durable artefacts

<!--
Produced via the `requirements-elicit` skill, following
spec/project/requirements-elicitation/.
Do not record a requirement before declaring the bounded context below.
`c_d` is an uncertainty proxy (self-consistency-derived), not a calibrated
probability. A requirement is `confirmed` only after an explicit teach-back.
-->

Source issue: [nolte/claude-shared#545](https://github.com/nolte/claude-shared/issues/545)
Elicited: 2026-08-16 · Classification: `spec-change`

## Bounded context

- **What is being built.** A cross-cutting corpus rule that binds a *load-bearing
  factual claim about the working copy* to its provenance: either the observation
  that established it, or an explicit mark that no such observation was made,
  naming the observation that would settle it.
- **For whom.** Every agent or skill that emits such a claim into an artefact that
  outlives the session, and every later reader who inherits the claim as the
  premise of their own work.
- **Why now.** Three claims published in one session in `nolte/kamerplanter` were
  confident, plausible, consistent with the symptom, wrong, and each refutable in
  under five minutes. One sat in issue #1207 for a day as suggested work that did
  not exist. No corpus rule could have caught any of them.
- **Explicitly out of scope.**
  - The remediation side — what is *done* about a cause once established
    (`spec/project/e2e-failure-diagnosis/` §A gates that for E2E clusters, and the
    test-cycle specs own the change itself).
  - Falsifiability of *test code* (`spec/project/test-falsifiability/`); this rule
    governs prose claims, not assertions in a test.
  - Assertions about things **not** verifiable in the working copy — versions, third-party
    API signatures, sister-repo paths (`spec/claude/research-triangulate/`, which
    excludes repo-internal assertions at its §Requirements line 34, leaving exactly
    the gap this rule fills).
  - Claims made in live conversation with the operator, where a correction is one
    reply away.
  - Judgements ("this is ugly") and proposals ("we should do Y"); neither is a
    checkable statement about the working copy.

## Understanding KPI

- Thresholds: `τ_low = 0.4`, `τ_high = 0.8`, self-consistency `k = 2`, question budget = `6`
  <!-- spec defaults, unchanged; budget set at 6 because the issue body supplied the
       gap statement, three measured examples, four framing proposals and an
       over-correction caution, leaving only the genuinely undecided forks to ask -->
- `U_gate = min_d c_d` over required dimensions = **0.85**
- Termination: `saturation` — 4 of 6 budgeted questions used; every applicable
  dimension is at or above `τ_high` and no positive-EVPI question remains that the
  decomposition would not answer more cheaply by reading the corpus.

### Gap matrix

| Dimension | Applicable | `c_d` | Uncertainty source | Evidence event |
|---|---|---|---|---|
| `functional` | yes | 0.9 | specification | Turn 3 + 4: operator selected the two-marker obligation with a per-marker observation, and the measure-when-cheap duty, each via its rendered concrete form |
| `non_functional` | yes | 0.9 | specification | Issue §"A caution about the fix" states the cost bar directly and names the failure mode it must avoid (a noisy check gets disabled) |
| `constraints` | yes | 0.9 | interpretation | Read from the corpus, not asked: EN-canonical + DE translation, `Portfolio-Scope`, delimitation against three sisters, the agent-`description` budget guard |
| `domain_objects` | yes | 0.85 | specification | Turn 2 + 3: claim classes (cause / state / existence / absence) and the two markers with their obligations, all teach-backed through worked examples |
| `actors` | yes | 0.9 | specification | Turn 4: operator widened the binding set from the six issue-named reviewers to include the five publishing skills |
| `acceptance_criteria` | yes | 0.85 | interpretation | Derived from the confirmed MUSTs; each is stated as a reviewer-checkable question. Not separately teach-backed — carried as a decomposition-gate item |
| `edge_cases` | yes | 0.85 | specification | Turn 4 settled the load-bearing one (the "suspected" escape hatch). Residual cases listed under open risks |
| `scope_boundaries` | yes | 0.95 | specification | Turn 1 + 2: rule home (new `spec/claude/` owner, §A stays and applies it) and reach (any load-bearing repo-factual claim, in any durable artefact) |

## Requirements

<!-- Each requirement in EARS/CNL form, tagged confirmed/assumed, with
     traceability to the user utterance(s) that produced it. -->

- **R1** — WHEN a rule governing the provenance of claimed causes is introduced, the
  corpus SHALL own it in a new cross-cutting spec under `spec/claude/`, and
  `spec/project/e2e-failure-diagnosis/` §A SHALL remain in place and *apply* it
  rather than being relocated into it.
  - _dimension_: `scope_boundaries` · _status_: `confirmed` · _source_: Turn 1, option
    "Neue spec/claude/-Spec", preview showing §A retained with a reference
  - _rationale carried_: `test-result-analyzer.md:29` binds "prove its mechanism
    before routing (its §A)" by name, and `spec/claude/dispatch-brief/` references
    the spec at four points; relocation would break both. The lift-and-apply shape
    is the precedent `dispatch-brief` itself set when it was lifted out of §E.

- **R2** — WHEN an agent or skill states a checkable claim about the working copy
  that another actor's work will build upon — a cause, a state, an existence, or an
  absence — the claim SHALL be in scope of the rule.
  - _dimension_: `scope_boundaries`, `domain_objects` · _status_: `confirmed` ·
    _source_: Turn 2, option "Belastbare Repo-Tatsachenaussage"
  - _rationale carried_: the issue title says "a cause", but only one of its three
    measured examples is causal; the other two are a state claim ("`PlantCountStep`
    is unreachable UI") and an existence claim ("the harness already has a working
    version of this helper"). A cause-only rule would miss both, including the one
    that cost real work.

- **R3** — The rule SHALL NOT apply to judgements, to proposals, to assertions about
  things not verifiable in the working copy, or to claims made in live conversation
  with the operator.
  - _dimension_: `scope_boundaries` · _status_: `confirmed` · _source_: Turn 2,
    preview "NICHT ausgelöst von" and "NICHT gebunden"; the separating question is
    whether the carrier outlives the session

- **R4** — WHEN a claim in scope of R2 is written into an artefact that outlives the
  session, the artefact SHALL carry that claim as exactly one of *established* or
  *unestablished*.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: Turn 3, option
    "Marker + je eigene Beobachtung"
  - _in-scope carriers_: issue body and comment, commit message, pull-request
    description, review finding, plan file, audit report, spec prose, feature and
    sprint files. _Out_: live operator conversation.

- **R5** — WHEN a claim is carried as *established*, the artefact SHALL name the
  observation that established it — a command and its output, or a `file:line`
  anchor a reader can re-run or open.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: Turn 3, preview
    line "belegt → MUSS die Beobachtung nennen, die es feststellte"
  - _rationale carried_: all three published false claims were confidently worded;
    a marker with no anchor would have relabelled them, not stopped them.

- **R6** — WHEN a claim is carried as *unestablished*, the artefact SHALL name the
  observation that would settle it and SHALL state that the observation was not made.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: Turn 3, preview
    line "unbelegt → MUSS die Beobachtung nennen, die es entscheiden würde"
  - _worked form taken from the issue_: "The likely cause is recorded on #1178 rather
    than guessed at here. Plausible, unverified, and not something to rewrite blind."

- **R7** — WHEN the observation named under R6 is cheap with the means already at
  hand, the author SHALL make it rather than publish the claim as unestablished;
  *unestablished* is available only when the observation is not cheap, and the
  artefact SHALL say what makes it expensive.
  - _dimension_: `functional`, `edge_cases` · _status_: `confirmed` · _source_:
    Turn 4, option "Ja, wenn billig — Autor benennt Kosten"
  - _rationale carried_: without this duty *unestablished* is a free exit, every
    claim degrades to "suspected", and the marker stops carrying signal. All three
    of the issue's examples were "measurable in under five minutes", so the rule
    must fail them rather than wave them through.
  - _threshold ownership_: the cheapness judgement stays with the author; what the
    rule requires is that the judgement be **stated**, which is what makes the exit
    reviewable instead of free.

- **R8** — The distinction required by R4 SHALL be checked on substance, not on
  wording; the rule SHALL NOT prescribe a verbatim token.
  - _dimension_: `functional`, `constraints` · _status_: `confirmed` · _source_:
    Turn 3, option "Substanz geprüft, Form frei"
  - _reviewer's check_: can a reader tell from the artefact whether the author
    measured or guessed? If not, the artefact is non-conformant.
  - _precedent_: `spec/claude/dispatch-brief/` line 29 states a canonical form and
    checks the authorisation, not the phrasing.

- **R9** — The rule SHALL be bound into the artefacts that emit or publish
  claims: the six reviewer and analyzer agents that produce findings whose value is
  the stated cause, and the skills that write durable artefacts.
  - _dimension_: `actors` · _status_: `confirmed` · _source_: Turn 4, option
    "Zusätzlich die publizierenden Skills"
  - _finding side_: `python-code-reviewer`, `frontend-code-reviewer`,
    `test-result-analyzer`, `code-security-reviewer`, `deployment-change-analyzer`,
    `e2e-result-reviewer`
  - _artefact side_: `issue-orchestrate`, `pull-request-create`, `feature-decompose`,
    `spec`, `lektorat-apply`

- **R10** — Every binding under R9 SHALL be made in the artefact body, and no
  `description:` frontmatter field SHALL be enlarged by this work.
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: Turn 4, question
    text stated the budget guard and the operator selected an option scoped to body
    bindings; consistent with the standing portfolio constraint
  - _rationale carried_: the summed agent `description` budget sits near the routing
    ceiling and is treated as a regression watchdog.

- **R11** — The new spec SHALL delimit itself explicitly against
  `spec/claude/dispatch-brief/` (the delegated half, two parties),
  `spec/claude/research-triangulate/` (repo-external assertions, source-count based),
  `spec/project/e2e-failure-diagnosis/` §A (the E2E-routed mechanism bar that gates
  changes), and `spec/project/test-falsifiability/` (test code), and SHALL NOT
  restate any of their rules.
  - _dimension_: `constraints` · _status_: `assumed` · _source_: not asked; read from
    the corpus. Every recent cross-cutting spec carries a §Delimitation and the
    `spec-readiness` reviewer checks for restated rules.

- **R12** — The rule SHALL be cheap enough at the point of writing that it is not
  disabled in practice: it SHALL NOT require proof for every sentence, and its
  required output SHALL be the marker plus one named observation.
  - _dimension_: `non_functional` · _status_: `confirmed` · _source_: issue
    §"A caution about the fix", which names the failure mode verbatim — "a noisy
    check gets disabled and is worse than none" (quoting `test-falsifiability`)

- **R13** — The spec SHALL be authored English-canonical with a synchronised German
  translation, and every `§` reference SHALL resolve within its own language file.
  - _dimension_: `constraints` · _status_: `assumed` · _source_: not asked; standing
    corpus convention, enforced by `spec-readiness` §Geltungsbereich.

## Surviving assumptions / open risks

- **The spec's name is not settled.** `claim-provenance` is the working name and reads
  well beside `dispatch-brief` and `research-triangulate`, but it was not put to the
  operator. Confirm at the decomposition gate before the folder is created; renaming a
  spec folder after it is referenced is the expensive direction.
  <!-- R1, assumed -->

- **R11 and R13 are `assumed`, not teach-backed.** Both were read off the corpus rather
  than asked, to stay inside the question budget. Neither is contested by anything in
  the issue, and both are mechanically checkable once drafted, so the risk is low and
  discharges at the `spec-readiness` review rather than needing a turn now.

- **The marker vocabulary in machine-read carriers is unresolved.** R8 fixes
  substance-over-wording for prose. Two carriers already have a machine format —
  `spec/claude/review-plan/` findings (Title-Case severities, greppable) and the
  scanner JSON of the editorial specs. Whether a provenance marker becomes a field
  there, or stays prose inside the finding, is a decomposition-time question. The
  operator declined the split-regime option in Turn 3, which argues for prose; it does
  not settle whether `review-plan` gains an optional field.

- **`acceptance_criteria` sits at 0.85 on derivation, not on a teach-back.** The
  criteria were normalised from the confirmed MUSTs rather than elicited. Each is
  reviewer-checkable by construction, so the exposure is that a criterion is
  redundant or missing, not that it is wrong. It discharges when the pre-analysis
  artefact is approved.

- **R7's cheapness judgement is author-owned by design.** The operator rejected a
  corpus-fixed threshold. This is a deliberate accepted risk: an author who
  systematically overstates cost can still take the unestablished exit, but must now
  write down a cost claim that a reviewer can dispute. The residual is a *reviewable*
  gap, not a silent one.

- **No adoption or retrofit is in scope.** The rule binds the artefacts listed in R9
  going forward. Existing artefacts in this repo and across the portfolio carry
  unmarked claims and are not swept by this work. If a retrofit is wanted, it is a
  separate tracked issue.
