# Requirements Elicitation Interview

Status: draft

## Context
<!-- Why does this spec exist? What problem, user need, or constraint drives it? -->

When an AI agent is asked to build, change, or specify something, the request it receives is almost never a complete, unambiguous specification. The requester is a human operating under three structural handicaps that requirements-engineering research treats as the norm, not the exception:

- **They often don't know what they want** until they see a candidate—the *IKIWISI* problem ("I'll know it when I see it"). Much of what a user needs is *tacit knowledge* (Polanyi): real, load-bearing, but never volunteered because the user doesn't consciously hold it as an explicit fact. Boehm names this the IKIWISI syndrome and prescribes concurrent prototyping over full up-front requirements [R13].
- **They express themselves imperfectly.** Natural-language requests are riddled with optionality, subjectivity, vagueness, weak words, dangling pronouns, and silent under-specification. Empirical NLP-for-RE studies show these defects are pervasive and frequently *unacknowledged*: each party is confident in its own reading while the readings differ [R8].
- **They're misunderstood.** Even a well-formed request can be misread by the agent. The dangerous case is the *confident misread*: the agent proceeds as if it understood, produces a plausible artifact, and the gap only surfaces after expensive work is done. An interpretation that's internally acceptable but wrong is recorded silently: unless a consistency check contradicts it, the misread goes undetected [R14].

An agent that simply pattern-matches the request to the nearest plausible solution amplifies all three failures. The cheap, high-leverage intervention is a **disciplined elicitation interview**: a bounded, adaptive dialogue that drives the agent's *understanding* up to a measured threshold before it commits to building anything, paired with a **quantified understanding KPI** that tells the agent, per requirement dimension, how well it actually understands, so it can ask *targeted* clarifying questions exactly where understanding is weak and stop asking where it's strong.

This spec defines that interview method and that KPI. The KPI is a **confidence score per requirement dimension** plus a **gap matrix** over a closed set of dimensions; together they gate whether the agent asks a clarifying question, which question it asks, and when the interview is complete. The method is model- and domain-agnostic: it prescribes the *form* of the interview and the *shape* of the metric, not a particular ML implementation or prompt. The realizing capability in this plugin is the `requirements-elicit` skill, which runs the interview, maintains the gap matrix, applies the gating, and writes the artifact.

The model is grounded in established literature, not invented: the empirical typology of elicitation-interview questions and the open→specific sequencing heuristic [R1]; the measured baseline that an LLM interviewer reaches ~74% requirement recall at a human-comparable error rate (a single simulated study; parity, not superiority) and that lightweight one-question-at-a-time prompting beats heavy procedural scripting [R3]; clarification-question selection as Bayesian experimental design maximizing expected information gain over the *solution space* [R4]; the separation of *specification uncertainty* (what the user wants) from *model uncertainty* (what the agent predicts) and EVPI-scored, cost-aware question selection [R5], [R12]; the behavioral self-consistency proxy for ambiguity—sample multiple interpretations, treat divergence as the ambiguity signal [R6]; controlled-natural-language target structures (EARS, Rimay) that force atomic, unambiguous, complete requirements [R7], [R9]; and the recall-favored ambiguity-detection trade-off with its named, trigger-word-backed defect-trigger list [R8], [R10]; the IKIWISI syndrome with concurrent prototyping as its remedy (Boehm [R13]); and ambiguity treated as a *resource* that surfaces tacit knowledge, with misunderstanding caught as a consistency check against the analyst's knowledge base (Ferrari, Spoletini, Gnesi [R14]).

Readers: authors of the `requirements-elicit` skill and the downstream planning gates (roadmap-plan, feature-decompose, issue-orchestrate) that consume its artifact, and reviewers judging whether a captured requirement is precise enough to build against.

## Goals
<!-- What this spec aims to achieve. Bullet points, outcome-oriented. -->
- Define a repeatable, adaptive interview procedure an AI agent runs to elicit a user's requirements as precisely as possible
- Treat the user's not-knowing, mis-expression, and being-misunderstood as the default case the method is engineered against, not an edge case
- Define a quantified understanding KPI—a per-dimension **confidence score** plus a **gap matrix** over a closed set of requirement dimensions
- Make clarification *confidence-gated*: ask only where understanding is measurably weak, and ask the single most informative question, balancing misunderstanding risk against user fatigue
- Define an explicit saturation / stopping criterion so the interview ends when understanding is sufficient, not when the agent runs out of obvious questions
- Require the agent to validate understanding by reflecting it back (teach-back) before treating a requirement as understood
- Produce a structured, auditable output: the requirement list, the filled gap matrix with final confidences, and the explicit list of surviving assumptions

## Non-Goals
<!-- Explicitly out of scope. Prevents creep. -->
- A full requirements-engineering process: prioritization, negotiation between conflicting stakeholders, backlog grooming, change management, and traceability-to-tests beyond the elicited set are out of scope
- Stakeholder / audience identification—which is `spec/project/audience-identification/`; this spec assumes the party being interviewed is already known
- Decomposing the elicited requirements into features, sprints, or an implementation plan—which is `spec/project/feature/` and `spec/project/spec-driven-development/`
- Prescribing a specific uncertainty-quantification algorithm, calibration model, or prompt. This spec defines the *shape* of the confidence score and gap matrix and the *rules* that govern them; the estimator is an implementation choice
- UI prototyping tooling. Prototypes and examples are named as elicitation *techniques*, but building a prototyping tool is out of scope
- Replacing human domain expertise. When a question requires authority the user doesn't hold, the method surfaces the gap; it doesn't fabricate an answer
- Authoring the downstream specification document itself (namely the `spec` skill / `spec-driven-development`); elicitation feeds specification, it isn't specification

## Requirements
<!-- Use RFC 2119 keywords: MUST, SHOULD, MAY. One atomic requirement per bullet. -->

### A. Interview structure and questioning

- **MUST** run the interview as an adaptive dialogue, posing **one question (or one tightly-coupled question group) per turn** rather than a long upfront questionnaire; lightweight one-question-at-a-time pacing empirically elicits more, not fewer, requirements than heavy procedural scripting [R3]
- **MUST** follow a **funnel sequence**: open the interview with broad, open-ended questions and progressively narrow to specific, closed questions as understanding firms up [R1]
- **MUST** use **probing questions** (questions asked in direct response to a prior answer) as the primary instrument for deepening understanding, drawing from the established probe types: *elaboration* ("say more about X"), *interpreting* ("so you mean Y?"), *reason-seeking* ("why does that matter?"), and *consistency* ("earlier you said A—how does that fit B?") [R1]
- **MUST** classify each question it asks by objective so the interview stays balanced: *coverage* (open a new dimension), *deepening* (probe an opened dimension), or *validation* (confirm an understood dimension via teach-back)
- **SHOULD** use **scenario- and example-driven questions** (concrete cases, step-by-step examples, and "show me what good looks like") to surface requirements the user struggles to state abstractly (the IKIWISI mechanism)
- **SHOULD** keep adaptive, context-specific follow-ups ahead of any rigid pre-written script; the script defines coverage obligations, not a fixed turn order [R3]

### B. Handling tacit knowledge, IKIWISI, and want-versus-need

- **MUST** make its working **assumptions explicit** and present them for confirmation rather than silently building on them; an unconfirmed assumption is recorded as `assumed`, never as `confirmed`
- **MUST** offer **concrete examples, counter-examples, and negative scenarios** ("would it be acceptable if …?" and "what should *never* happen?") to elicit boundaries the user is unable to volunteer abstractly
- **MUST** probe **edge cases, error states, and "what-if" conditions** before treating a functional dimension as understood—these are the dimensions users most reliably omit
- **SHOULD** separate **want from need** by laddering on rationale (reason-seeking probes): trace a stated solution back to the underlying goal, so the agent solves the need rather than transcribing the first-proposed solution
- **SHOULD** treat the user's first formulation as a hypothesis to be tested, not a specification to be transcribed

### C. Ambiguity and misunderstanding detection

- **MUST** screen every user utterance against a **non-exhaustive trigger-word checklist** of named ambiguity classes (extensible per project, and never treated as a complete classification of misunderstanding), and flag any hit for clarification or teach-back: *optionality* (can/may/optionally), *subjectivity* (similar/better/user-friendly), *vagueness* (significant/adequate/fast), *weakness* (could/should/may), *implicit reference* (pronouns, indirect references), *multiplicity* (more than one main verb/subject/object in one requirement), and *under-specification* (a referenced quantity, unit, actor, or condition is missing) [R8], [R10]
- **MUST** normalize each understood requirement into an **atomic, unambiguous target structure**: an EARS-style template ("WHEN <trigger>, the <system> SHALL <response>") or equivalent controlled natural language; flag any requirement that resists normalization as not-yet-understood [R7], [R9]
- **MUST** validate understanding by **teach-back**: reflect the agent's interpretation back to the user in the user's terms and obtain explicit confirmation before a requirement's confidence may cross the "understood" threshold (§D). A requirement the user hasn't confirmed via teach-back MUST NOT be reported as `confirmed`
- **SHOULD** favor **recall over precision** when deciding whether something is ambiguous: a needless clarification is cheap, a missed ambiguity propagates into the built artifact. When in doubt, flag it [R8], [R10]
- **SHOULD** detect *unacknowledged* ambiguity—cases where the utterance reads as clear but admits more than one defensible interpretation—by the self-consistency check in §D, not only by surface trigger words [R6], [R8]

### D. Understanding KPI: Confidence score and gap matrix

- **MUST** model understanding as a **gap matrix** over a closed set of **requirement dimensions**, marking each either applicable or explicitly "n/a (reason)":
  - `functional`: what the system must do
  - `non_functional`: performance, security, usability, and other quality attributes
  - `constraints`: technology, budget, regulatory, compatibility, and platform limits
  - `domain_objects`: the entities, data, and domain vocabulary involved
  - `actors`: who/what interacts with the system
  - `acceptance_criteria`: how "done" and "correct" are judged
  - `edge_cases`: error states, boundaries, and exceptional conditions
  - `scope_boundaries`: what's explicitly in and out of scope
- **MUST** carry, per applicable dimension, a **confidence score** `c_d ∈ [0,1]` expressing how well the agent believes it understands that dimension. This score is an *uncertainty proxy* (a self-consistency-derived signal), not a calibrated probability; it MUST drive gating as a relative ordering and MUST NOT be reported as a literal likelihood of correctness [R6]
- **MUST** separate two uncertainty sources when estimating `c_d` and keep them distinguishable in the matrix: **specification uncertainty** (the user hasn't determined or stated what they want) versus **interpretation uncertainty** (the user may have been clear, but the agent is unsure it read them correctly). The two demand different remedies—specification uncertainty needs a decision-eliciting question to the user; interpretation uncertainty needs a teach-back confirmation [R5], [R12]
- **MUST** calibrate `c_d` against a **behavioral signal, not self-report alone**: the reference mechanism is *self-consistency*, generating `k ≥ 2` independent interpretations (or candidate solution sketches) for the dimension; the more they diverge, the lower `c_d` and the stronger the ambiguity signal. Verbalized/self-reported confidence MAY supplement this but MUST NOT be the sole input, because uncalibrated self-confidence systematically overstates understanding [R6]
- **MUST** define an **aggregate gating score** `U` over the applicable required dimensions. Because a single severe misunderstanding is more damaging than broad mild uncertainty, the gate MUST be governed by the **weakest required dimension** (`U_gate = min_d c_d` over required dimensions), even if a weighted mean is also reported for transparency
- **MUST** define and apply two thresholds, with documented defaults that are project- and risk-adjustable:
  - `τ_low` (default **0.4**): any dimension with `c_d < τ_low` **MUST** trigger a clarification before the interview may proceed past it
  - `τ_high` (default **0.8**): a dimension is treated as "understood" only once `c_d ≥ τ_high` *and* (for `functional`, `acceptance_criteria`, and any user-facing dimension) a teach-back confirmation has been obtained
  - the band `τ_low ≤ c_d < τ_high` is the **discretionary zone**: clarify only if the expected information gain justifies the question cost (§E)
- **SHOULD** make the gap matrix **visible to the user** on request—a plain "here's what I understand / here's what's still unclear" view—so the human can correct a wrongly calibrated cell directly
- **MUST** raise `c_d` only through evidence (a user answer, a confirmed assumption, a successful teach-back), never through the mere passage of interview turns

### E. Selecting the next (clarifying) question

- **MUST** decide **whether** to ask—pose a clarifying question only when the **expected reduction in uncertainty** (expected information gain, or expected value of perfect information, EVPI) exceeds the **cost** of asking (the user-fatigue and latency cost of one more turn). Below `τ_low` the gain dominates and a question is mandatory; in the discretionary zone the EVPI/cost comparison decides [R4], [R5]
- **MUST** choose **which** question to ask by maximizing information gain **over the space of viable interpretations/solutions**, not merely over the space of candidate questions—that is, prefer the question that most shrinks the set of distinct viable readings of the requirement; selecting by reasoning over the solution space empirically beats selecting by reasoning over questions alone [R4]
- **MUST** target the question at the **lowest-confidence required dimension** first (the dimension setting `U_gate`), so each turn lifts the binding constraint on overall understanding
- **MUST** suppress **redundant questions** (questions whose answer is already implied by a confirmed cell) via an aspect/coverage check before asking [R5]
- **SHOULD** phrase the clarification to expose the *specific* ambiguity detected (offer the divergent interpretations as options) rather than an open-ended "can you clarify?" request, so the user's answer resolves the most ambiguity [R6]
- **SHOULD** balance over-questioning (user fatigue, abandonment) against under-questioning (confident misread) explicitly; the EVPI/cost rule is the balancing instrument, and the per-interview question budget (§F) is its backstop

### F. Saturation and stopping

- **MUST** terminate the interview when **all** of the following hold, and report completion: every required, applicable dimension has `c_d ≥ τ_high` (with teach-back where §D requires it), **and** no remaining candidate question has positive net EVPI (saturation—further questions would not change the elicited set) [R5]. No research-validated termination criterion exists for elicitation interviews; this rule is an engineering construction over the confidence/EVPI machinery, not a literature result
- **MUST** enforce a **hard question budget** per interview as a backstop against non-terminating dialogues; on reaching it, the agent MUST stop and hand off with every below-`τ_high` cell explicitly flagged as a residual risk rather than silently treated as understood
- **MUST**, on any stop (saturated or budget-capped), surface the **surviving assumptions and below-threshold cells** as named open risks attached to the output
- **SHOULD** prefer stopping over one more low-value question once saturation is reached: a confidently-understood smaller set beats a fatigued user and a padded one

### G. Output artifact

- **MUST** emit, as the interview's deliverable: (1) the elicited **requirement list** in the normalized target structure (§C), (2) the **filled gap matrix** with final per-dimension confidences and the aggregate `U_gate`, and (3) the explicit list of **surviving assumptions / open risks** (§F)
- **MUST** persist the artifact at `project/requirements/<slug>.md`, pluralized like `project/features/` so multiple requirement sets (per scope, outcome, or feature) coexist and a downstream consumer can reference exactly one deterministically
- **MUST** tag every requirement `confirmed` (validated via teach-back or an authoritative user answer) or `assumed` (inferred and not yet confirmed), mirroring the matrix
- **SHOULD** attach **traceability** from each elicited requirement back to the user utterances that produced it, so a reviewer can audit how an interpretation arose
- **SHOULD** hand the artifact to the downstream consumer (feature decomposition, spec authoring) in a form those consumers can reference rather than re-eliciting

### H. Consumer contract

- **MUST** apply to the downstream planning capabilities that presuppose requirements, at minimum `roadmap-plan`, `feature-decompose`, and `issue-orchestrate`: before substantive decomposition each MUST check whether a requirement artifact (§G) exists for the work at hand and whether its `U_gate` meets `τ_high`. When no artifact exists, or `U_gate` is below `τ_high`, the consumer MUST dispatch `requirements-elicit` first, or record an explicit operator override, rather than decomposing against unstated or weakly-understood requirements. This mirrors the upstream gate that `audience-identification` places on audience-claiming artifacts.
- **MUST NOT** treat the gate as hard-blocking once the operator explicitly accepts the surviving gaps; the gate surfaces weak understanding, it doesn't forbid proceeding, and the override is recorded rather than silent.
- **SHOULD** reference the artifact by its path (`project/requirements/<slug>.md`) rather than re-eliciting, so one elicitation feeds roadmap planning, feature decomposition, and issue orchestration alike.

## Acceptance Criteria
<!-- Testable, checkable conditions. A reviewer should be able to mark each as done/not done. -->
- [ ] A worked example exists applying the method to one concrete elicitation in this repository (for example, eliciting the requirements for a new skill before `skill-management` scaffolds it)
- [ ] The interview transcript shows one-question-per-turn pacing and a visible open→specific funnel
- [ ] Every elicited requirement is rendered in the normalized EARS/CNL target structure, or is flagged as not-yet-understood
- [ ] The output includes a gap matrix covering every dimension in §D, each marked applicable-with-`c_d` or "n/a (reason)"
- [ ] Each `c_d` is justified by a named evidence event (user answer / confirmed assumption / successful teach-back), and at least one `c_d` was derived from a `k ≥ 2` self-consistency check rather than self-report
- [ ] The transcript shows at least one clarification that was *withheld* because its EVPI didn't exceed its cost (discretionary-zone restraint), and at least one that was *forced* because a dimension was below `τ_low`
- [ ] Every clarifying question targets the lowest-confidence required dimension at the moment it's asked
- [ ] The interview terminated by an explicit, recorded criterion—saturation (`min_d c_d ≥ τ_high` and no positive-EVPI question remains) or the question-budget cap—and never by the agent simply running out of ideas
- [ ] On a budget-capped stop, every below-`τ_high` cell appears in the output as a named residual risk
- [ ] Each output requirement is tagged `confirmed` / `assumed` consistently with its matrix cell
- [ ] The thresholds `τ_low`, `τ_high`, the self-consistency `k`, and the question budget are stated explicitly in the artifact and are overridable per project with a recorded rationale
- [ ] The elicited artifact is written to `project/requirements/<slug>.md`
- [ ] At least one downstream consumer (`roadmap-plan`, `feature-decompose`, or `issue-orchestrate`) gates on the artifact's presence and `U_gate`, dispatching `requirements-elicit` when it's missing or below `τ_high`, with any operator override recorded

## References
<!-- Cited sources from the deep-research pass. Adversarial verification didn't complete (session-limit abstention), so claims are sourced but not independently triangulated; treat methods as well-attested primary-source reports, thresholds as defaults to calibrate. -->

- [R1] *On the Nature of Requirements Elicitation Interview Questions* (RE2021, York University)—typology of interview questions (content, style, probing style, sequence, objective); probing questions as the most efficient type with >10 subtypes; open→specific sequencing heuristic: <https://www.yorku.ca/liaskos/Papers/RE2021/RE2021.pdf>
- [R2] *A study of elicitation techniques and their performance* (Information & Software Technology, 2020)—completeness as the share of reference-solution requirements covered; quality as percentage agreement; questions-asked / relevant-questions / quality-per-time efficiency metrics: <https://www.uv.es/joigpana/Files/Journals/IST_2020Requirements_elicitation.pdf>
- [R3] *LLMREI: Automating Requirements Elicitation Interviews with LLMs* (arXiv 2507.02564)—LLM interviewer reaches ~60.9% complete + 12.8% partial (≈73.7% recall) of ground-truth requirements; minimal one-question-at-a-time prompting outperforms a five-step structured-guideline prompt: <https://arxiv.org/html/2507.02564v1>
- [R4] *Active Task Disambiguation with LLMs* (arXiv 2502.04485)—clarifying-question generation as Bayesian experimental design maximizing expected information gain over the space of viable solutions; reasoning over the solution space beats reasoning over candidate questions: <https://arxiv.org/pdf/2502.04485>
- [R5] *SAGE-Agent: structured uncertainty-guided clarification* (OpenReview dc8ebScygC)—separates specification uncertainty from model uncertainty; EVPI-scored question value with aspect-based cost modeling to suppress redundant questions; stopping criterion derived from the uncertainty/EVPI formulation: <https://openreview.net/forum?id=dc8ebScygC>
- [R6] *ClarifyGPT* (ACM TOSEM, 10.1145/3660810)—decides *when* to clarify via a code-consistency check: sample n solutions, treat the requirement as ambiguous if and only if sampled outputs diverge (behavioral self-consistency proxy, not self-reported confidence); reasoning-based question generation from the divergent implementations: <https://dl.acm.org/doi/full/10.1145/3660810>
- [R7] *Easy Approach to Requirements Syntax* (EARS)—controlled requirement-syntax templates that constrain natural language toward atomic, unambiguous requirements: <https://en.wikipedia.org/wiki/Easy_Approach_to_Requirements_Syntax>
- [R8] *On the detection of unacknowledged anaphoric ambiguity / TAPHSIR* (arXiv 2206.10227)—unacknowledged ambiguity: distinct confident readings of the same text; recall-favored detection (TAPHSIR ≈100% recall, ~60% precision) as a deliberate threshold heuristic: <https://arxiv.org/pdf/2206.10227>
- [R9] *Rimay: a controlled natural language for requirements* (arXiv 2305.07097)—CNL with controlled grammar/vocabulary forcing precise, unambiguous, complete, atomic requirements; nine detectable "smells" mapped to four quality attributes (completeness, clarity, atomicity, correctness) as a checkable gap taxonomy: <https://arxiv.org/pdf/2305.07097>
- [R10] *Comparative evaluation of NLP ambiguity detectors* (NLP4RE, CEUR Vol-3122, paper 3)—named lexical/syntactic ambiguity categories with trigger-word lists (optionality, subjectivity, vagueness, weakness, implicit reference, multiplicity, under-specification); Precision/Recall scaffold; the high-recall/low-precision trade-off of pattern matching: <https://ceur-ws.org/Vol-3122/NLP4RE-paper-3.pdf>
- [R11] `spec/project/audience-identification/`: identifies the party being interviewed; this spec assumes that party is already known
- [R12] *SAGE (uncertainty separation over structured parameters)* (arXiv 2511.08798)—separating specification uncertainty from model uncertainty over structured tool parameters and their value domains rather than free text: <https://arxiv.org/abs/2511.08798>
- [R13] B. Boehm, *Spiral Development: Experience, Principles, and Refinements* (CMU/SEI-2000-SR-008)—names the IKIWISI syndrome (requirements for new user-interactive systems aren't knowable up front) and prescribes concurrent prototyping/requirements/architecture over full up-front specification: <https://www.sei.cmu.edu/documents/5439/2000_003_001_13655.pdf>
- [R14] A. Ferrari, P. Spoletini, S. Gnesi, *Ambiguity and tacit knowledge in requirements elicitation interviews* (Requirements Engineering journal, 2016)—a 34-interview study that treats ambiguity as a *resource* that surfaces tacit knowledge, and modelling misunderstanding as a consistency check against the analyst's knowledge base, where an internally-acceptable wrong reading fails silently: <https://link.springer.com/article/10.1007/s00766-016-0249-3>

## Open Questions
<!-- Unresolved decisions. Each should be actionable. -->

- The default thresholds (`τ_low = 0.4`, `τ_high = 0.8`, self-consistency `k`, question budget) are seeded from literature heuristics and engineering judgment, not from a calibration study on this portfolio's own interviews. They should be revisited once enough real elicitation transcripts exist to calibrate them empirically.
- The originating deep-research run's adversarial verification (3 votes per claim, 2 refutations to kill) confirmed the load-bearing methods: the funnel and probing typology [R1], self-consistency as the ambiguity signal [R6], information-gain / EVPI question selection [R4], [R5], the specification-versus-model-uncertainty split [R5], [R12], IKIWISI [R13], and ambiguity-as-resource with consistency-check misunderstanding [R14] all survived. Four claims were refuted and deliberately kept out of this spec: SAGE-Agent's quantitative magnitude figures, a closed four-type ambiguity taxonomy, the claim that unstructured interviews are categorically worst, and implied-scenario exhaustion as a saturation rule.
- No surveyed source supplies a calibrated threshold for `τ_low`, `τ_high`, the self-consistency `k`, the output-divergence fraction, or the EVPI-to-cost ratio; every numeric value in §D/§E is an engineering default, not a measured constant.
- No surveyed source validates a saturation/termination criterion for elicitation interviews; §F's rule is constructed over the confidence/EVPI machinery rather than measured.
- Whether a calibrated LLM confidence measure can be fused with the self-consistency proxy and stay well-calibrated for *requirements understanding* specifically is unaddressed in the literature; until then, `c_d` stays a proxy (§D).
- The gap-matrix artifact and its per-turn KPI mechanics have no worked schema in any surveyed source; the schema in §D/§G is original to this spec and should be validated against real elicitation transcripts.
- How does the gap matrix interact with multi-party elicitation (several users with conflicting requirements)? This spec scopes a single interviewed party; conflict reconciliation is deferred to a future spec.
