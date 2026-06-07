# Spec Readiness

Status: draft

## Context
Specifications under `spec/<topic>/<slug>/` are the source of truth for downstream work in the portfolio—implementation, review plans, tooling, documentation, audits. A spec that's internally contradictory, silent about its intended readers, or riddled with gaps forces every downstream step to guess. The cost compounds: contradictions surface as bug reports during implementation, audience mismatches surface as "this wasn't written for us," and completeness gaps surface as ad-hoc decisions that then contradict the spec they were supposed to follow. Today the portfolio has adjacent audits: `spec/project/spec-drift-audit/` reconciles spec against implementation, the `spec` skill deduplicates across translations, `audience-identify` builds audience artifacts for modules that don't yet have one, but none of them audits whether a spec is **ready to be consumed downstream**. This spec defines that readiness practice: what the audit checks, when it runs, how findings are classified, and how a spec graduates from draft to an implementable source of truth.

## Goals
- Every spec in scope is audited along three dimensions—contradictions, audience fit, domain completeness—before it's relied on for downstream work
- Findings are classified by a shared severity scale so the same issue gets the same response across the portfolio
- Readiness is a precondition for promoting a spec out of `Status: draft` into a stable-contract state (the portfolio's accepted-equivalent status)
- The audit is read-only and delegated to a specialised agent so the practice stays repeatable and free of ad-hoc prose judgement
- The audit is clearly distinct from the spec skill's dedup / drift / translation checks, from `spec-drift-audit`'s spec-versus-implementation reconciliation, and from `audience-identify`'s module-level audience generation

## Non-Goals
- Authoring, translating, or restructuring specs—those stay with the `spec` skill
- Validating implementation against a spec—that's `spec/project/spec-drift-audit/`
- Producing a fresh audience artifact for a module that has none—that's `audience-identify` + `audience-review`
- Prose correctness, vocabulary, style enforcement—those belong to `spec/project/prose-style/` and `prose-vale-curator`
- Declaring the operational details of the agent that implements the audit (`agents/spec-readiness-reviewer.md`)—those can evolve without a spec change
- Defining a universal "acceptance" status label beyond what this spec already declares; portfolio status machinery lives in the spec artifact format, not here

## Requirements

### Scope
- **MUST** apply to every spec at `spec/<topic>/<slug>/<canonical_language>.md` whose `## Requirements` or `## Acceptance Criteria` section is non-empty
- **MUST** include specs with `Status: draft`, since drafts are the primary readiness target, not an exemption
- **MUST** cover both intra-spec (inside one spec) and cross-spec (between two or more specs) concerns
- **MAY** narrow a run to a single spec or a single topic when the trigger is itself narrow (for example a PR that changes one spec)

### Dimension 1—Contradiction detection
- **MUST** flag as Critical any MUST / MUST NOT pair inside the same spec that covers the same subject but declares opposite requirements
- **MUST** flag as Critical any MUST in spec A that can't simultaneously hold with a MUST in spec B; pairs that depend on scope carve-outs are resolved by making the carve-out explicit, not by ignoring the contradiction
- **MUST** flag as Warning any MUST versus SHOULD pair inside the same spec that points in opposite directions; the MUST always wins, but the SHOULD is misleading to readers and is a finding
- **MUST** flag as Warning any Goal that directly contradicts a Non-Goal inside the same spec (for example a goal implying outputs that the non-goals explicitly disclaim)
- **SHOULD** flag as Info chains of softening (a MAY that effectively reverses a SHOULD which was already conditional) when they make the rule-set opaque to a reader
- **MAY** propose a resolution direction per finding—strengthen one rule, weaken the other, split the scope—without prescribing the final choice
- **MUST** report a cross-spec contradiction symmetrically (both specs named, neither preferred); any preferred resolution direction is the advisory MAY above, never an automatic verdict that picks a winner by spec age, stability, or topic—choosing the winner is the human reviewer's call (see §Delimitation)
- **MUST NOT** declare a contradiction based on prose alone when no RFC-2119 verb is in play; plain prose inconsistencies are prose-lint concerns, not readiness concerns
- Cross-spec contradiction detection is **emergent** from the in-scope spec set; the audit derives candidate pairs dynamically and a maintained "contradiction corpus" is explicitly out of scope until accumulated `Recurring` findings prove the dynamic check misses recurring tension pairs (Info)

### Dimension 2—Audience fit
- **MUST** derive each spec's implicit readers from its prose (typical sets: implementers, reviewers, tooling authors, release managers, product owners, operators); the derivation is observation, not a blank-sheet audience analysis
- **MUST** check that for every derived audience there is content the audience can act on—Requirements for implementers, Acceptance Criteria for reviewers, interface-level MUSTs for tooling authors, Open Questions surfaced for product owners
- **MUST** flag as Warning a spec whose audience can't be derived ("who is this written for?") or whose Requirements don't address the derived audience's decisions
- **SHOULD** cross-reference an existing `audience-identify` artifact when the spec's module has one; if the spec addresses an audience the artifact names but the spec's Requirements don't meet it, the finding is a Warning, not Critical. Severity here is decided by substance, not by the bare reference: an artifact-named audience the spec doesn't serve is a Warning, whereas merely not citing an artifact while still serving the derived audience is at most an Info hint (see the §Dimension 2 Info rule below)
- **SHOULD** flag as Info a spec whose audience is implicit but derivable only with effort; the fix is usually a one-line "readers:" hint, not a restructure
- **MAY** point at `audience-identify` as the follow-up tool when a spec's module has no audience artifact and the readiness audit can't derive audiences confidently
- **MUST NOT** create or author audience artifacts as part of this audit; that's out of scope (see §Delimitation)

### Dimension 3—Domain completeness
- **MUST** verify that every Requirement has at least one Acceptance Criterion that's testable (measurable outcome, observable state, or enforceable gate)—a Requirement without a testable AC is a Warning; "at least one per Requirement" is the deliberate bar and a per-MUST AC quota is out of scope, because finer quotas invite gaming (splitting one AC into N trivial ones) without improving real coverage
- **MUST** verify that every Acceptance Criterion traces back to a Requirement or a Goal—an orphan AC (can't be tied to any Requirement or Goal) is a Warning
- **MUST** classify every Open Question as either **load-bearing** (implementation or downstream work can't responsibly proceed without an answer) or **parking-lot** (nice-to-have refinement, downstream can proceed with a reasonable default); a load-bearing OQ in a spec that's being considered for promotion is a Critical finding
- **MUST** flag as Critical any reference from spec A to spec B where spec B doesn't exist, or exists but doesn't contain the section the reference implies
- **SHOULD** flag as Warning every Goal without at least one matching Requirement—a Goal the spec then never operationalises is a misleading promise
- **SHOULD** flag as Info when the scope of a spec is ambiguous and no Non-Goals section carves it; the fix is usually adding three to five explicit non-goals
- **MAY** flag as Info Acceptance Criteria that are testable in principle but require infrastructure the portfolio doesn't yet have; these aren't Critical-class, but they warn consumers

### Severity scale
- **MUST** use the canonical four-level severity scale defined in `spec/claude/review-plan/<canonical_language>.md` §Severity scale: `Critical` / `Warning` / `Suggestion` / `Info`, in Title Case
- **MUST** map readiness findings to the scale per the patterns documented in §Dimension 1, 2, and 3 above:
  - **Critical**: direct MUST / MUST NOT contradiction inside or across specs; load-bearing Open Question in a spec being considered for promotion; reference to a non-existent spec section; cross-spec contradiction between two accepted specs
  - **Warning**: MUST vs SHOULD contradiction; unidentifiable audience; derived audience whose needs aren't addressed; Goal without a matching Requirement; Requirement without a testable Acceptance Criterion; orphan Acceptance Criterion
  - **Info**: softening-chain opacity; implicit but derivable audience; ambiguous scope with no Non-Goals; AC that requires not-yet-portfolio infrastructure
- **MAY** populate the `Suggestion` bucket from the canonical scale when a finding identifies a one-line fix or stylistic improvement that doesn't fit the three readiness patterns above; readiness audits typically produce only `Critical` / `Warning` / `Info`, but the bucket exists in the canonical scale and remains available
- **MUST NOT** invent additional severity levels beyond the canonical four; consistency across audit-producing specs is the single reason this scale lives in `review-plan` rather than being redefined per spec
- **MUST NOT** downgrade a severity on local judgement alone; disagreement with the classification is a documented waiver recorded in the audit artifact, not a silent reclassification

### Triggers
- **MUST** run before promoting any spec out of `Status: draft`; a spec with unresolved Critical readiness findings **MUST NOT** be promoted until those findings are resolved or explicitly waived. This promotion gate is enforced by the operator at promotion time, NOT by CI; spec-readiness stays an advisory periodic audit (parallel to `spec/project/spec-drift-audit/` §Delimitation, which is the periodic deep dive while `spec/project/workflow-health/` owns the continuous-CI lane). CI enforcement is revisited only once at least four completed quarterly audits under `.audits/spec-readiness/` show a measured false-Critical rate below 10% AND a single-spec promotion run has produced a stable `review-plan`-format artifact (AC line 102)
- **MUST** run at least once per calendar quarter for every spec whose status is still `draft`; drafts that age without reassessment drift
- **SHOULD** run as a same-merge or follow-up partial audit when a PR modifies a spec (new MUST, modified AC, new scope); the partial audit scope matches the PR's touched specs
- **MAY** run across the entire portfolio on the same cadence as `spec-drift-audit`; the two are complementary quarterly passes and can share the audit ritual without sharing scope

### Read-only discipline
- **MUST** be read-only: the audit reports findings; fixes (rewording, strengthening, adding missing ACs, resolving OQs) are a separate, opt-in step the caller takes with the `spec` skill or by hand
- **MUST NOT** modify, create, or delete any spec file during the audit—even when the fix seems obvious
- **MUST NOT** hit the network; all information needed for the audit lives in the working tree (specs, audience artifacts, git history)

### Audit artifact
- **MUST** persist the result of every audit as a commit, issue, or file in the repository; the artifact location **SHOULD** be consistent per repository (for example `.audits/spec-readiness/YYYY-Q<n>.md` or a GitHub issue with label `spec-readiness`)
- **MUST** include in the artifact: date, trigger (quarterly, pre-promotion, PR-change), scope (which specs were audited, which were narrowed out), the Git revision audited, per-spec severity counts, and the full finding list sorted by severity
- **SHOULD** link to the prior audit artifact so the portfolio's readiness trajectory is traceable across quarters
- **SHOULD** follow the `review-plan` artifact format when the audit targets a single spec ahead of a promotion decision, so the output slots into the same audit machinery as skill-review and agent-review
- **SHOULD** consult `spec/project/parallel-working-copies/` §Audit artefacts in multiple worktrees when the audit is run inside a worktree rather than the primary checkout, since the artifact's per-repository uniqueness is only observable inside one working tree at a time and the worktree-local commit, transfer, and cleanup rules live there

### Delimitation
- **MUST** stay separate from the `spec` skill: that skill creates, translates, indexes, deduplicates translations, and checks translation drift; this audit checks readiness of the **content**
- **MUST** stay separate from `spec/project/spec-drift-audit/`: that audit reconciles spec vs **implementation** (code and config); this one reconciles a spec against **itself** and against **other specs**
- **MUST** stay separate from `spec/project/audience-identification/`: that skill produces an audience artifact for a module; this audit checks whether an existing spec **serves** its derivable audience
- **MUST** stay separate from `spec/project/prose-style/`: Vale owns prose correctness and vocabulary; this audit is indifferent to prose style unless it directly causes a contradiction or an unparseable RFC verb
- **MUST NOT** replace peer review—this audit surfaces the mechanical findings, and a human reviewer still owns the judgement calls the audit surfaces (which direction to resolve a contradiction, whether a Non-Goal is missing)

## Acceptance Criteria
- [ ] Every spec in the portfolio with a non-empty `## Requirements` or `## Acceptance Criteria` section has at least one readiness-audit entry in the repository's audit history since this spec was introduced, or a documented exception
- [ ] No spec with unresolved Critical readiness findings has been promoted out of `Status: draft` since this spec was introduced—either the finding is resolved, or the promotion is blocked, or a waiver is recorded in the audit artifact
- [ ] The audit artifact for any readiness run records the scope (spec slugs audited), the Git revision audited, the per-spec severity counts, and the full finding list
- [ ] No cross-spec contradiction between two specs that are both promoted out of draft remains in the most recent audit without a documented resolution—either the contradiction is resolved in the source specs or a waiver is recorded in the audit artifact's `## Processing log` per `spec/claude/review-plan/` §Severity scale
- [ ] The agent `agents/spec-readiness-reviewer.md` produces findings that map 1-to-1 onto the three dimensions and the canonical severity scale this spec cites (defined in `spec/claude/review-plan/` §Severity scale), so audit artifacts can be generated mechanically
- [ ] No audit run in any repository modified any spec file; the read-only discipline holds in practice, not just in this spec
- [ ] Readiness-audit artifacts for single-spec promotion runs conform to the `review-plan` artifact format, so they're consumable by the same review-closure machinery as skill- and agent-review

## Open Questions

_All previously deferred open questions were settled on 2026-06-06: each provisional default is now the standing rule. See `.audits/decisions/2026-06-06-settle-open-questions.md` for the per-item decisions and rationale._
