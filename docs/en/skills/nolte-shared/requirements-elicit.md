---
title: requirements-elicit
audience: [maintainer]
content_mode: reference
track: developer-docs
last_updated: generated
---

# requirements-elicit

> Runs the requirements-elicitation interview and produces an authoritative requirement artifact gated by a confidence/gap-matrix KPI.

_Runs the requirements-elicitation interview methodology from spec/project/requirements-elicitation/ to capture a user's requirements precisely, assuming the user often does not know exactly what they want, expresses it imperfectly, or is misread. Drives a one-question-at-a-time funnel interview, maintains a per-dimension confidence score plus a gap matrix, asks confidence-gated clarifying questions only where understanding is weak, and writes an authoritative artifact to project/requirements/<slug>.md. Invoke when the user says things like "elicit the requirements for X" or "I want to build something but I'm not sure what exactly", or equivalent German-language requests. Also triggers as the upstream gate of roadmap-plan, feature-decompose, and issue-orchestrate when a requirement artifact is missing or below threshold. Don't use to decompose an existing requirement set (use feature-decompose) or author the downstream spec (use spec). Supports resume per `spec/claude/resumable-work/`._

- **Plugin:** `nolte-shared`
- **Phase:** 2 Plan (`plan`)
- **Tags:** `requirements`
- **Source:** [skills/requirements-elicit/SKILL.md](https://github.com/nolte/claude-shared/blob/main/skills/requirements-elicit/SKILL.md)

## Use when

- you want to elicit a user's requirements before building, planning, or specifying
- the user knows they want something but cannot yet state it precisely
- roadmap-plan, feature-decompose, or issue-orchestrate needs a requirement artifact that does not exist yet

## Don't use when

- **You already have a requirement set and want to break it into features** → [`feature-decompose`](feature-decompose.md)
- **You want to author the downstream specification document** → [`spec`](spec.md)

## See also

- [`feature-decompose`](feature-decompose.md)
- [`roadmap-plan`](roadmap-plan.md)
- [`audience-identify`](audience-identify.md)

## Referenced by

- [`feature-decompose`](feature-decompose.md)
- [`issue-orchestrate`](issue-orchestrate.md)
- [`roadmap-plan`](roadmap-plan.md)
- [`working-copy-start`](working-copy-start.md)

---

## Requirements Elicitation Skill

Operationalizes `spec/project/requirements-elicitation/` so a development request becomes a precise, confidence-scored requirement set instead of the agent's first plausible guess. The method is engineered against the default case: the user often **does not know exactly what they want**, **expresses it imperfectly**, or **is misread**. It drives understanding up to a measured threshold *before* anything downstream is built.

### Why this is a skill, not an agent

- **Mid-flow interactivity is the contract** — the spec mandates a one-question-at-a-time funnel interview with teach-back confirmation per requirement. Each turn shows one question, reads the user's answer, and lifts the lowest-confidence dimension; an agent's isolated, non-interactive context cannot run that dialogue.
- **Persistent on-disk artifact** — the result (requirement list + filled gap matrix + surviving assumptions) lives at `project/requirements/<slug>.md` and is read by downstream consumers ([`roadmap-plan`](roadmap-plan.md), [`feature-decompose`](feature-decompose.md), [`issue-orchestrate`](issue-orchestrate.md)). A skill owns persistent state; an agent returns a report and forgets.
- **`confirmed` vs `assumed` and teach-back need the user in the loop** — the spec forbids marking a requirement `confirmed` without an explicit teach-back confirmation; that signal can only be gathered interactively.
- Counter-dimension considered: a read-only agent could later score the gap matrix on a finished artifact (a `validate`-style audit), but the load-bearing dimension here is interactivity, not isolated computation — skill wins. The narrow scoring agent is a possible future companion, not this skill's core.

### User-language policy

- Detect the user's language from their message and conduct the interview in that language — the dialogue must feel natural to the person being interviewed.
- The written requirement artifact uses the surrounding repository's primary language (English by default, unless the repo's existing `project/` docs show otherwise — follow the precedent).
- The eight requirement-dimension keys (`functional`, `non_functional`, `constraints`, `domain_objects`, `actors`, `acceptance_criteria`, `edge_cases`, `scope_boundaries`) stay verbatim from the spec (canonical EN wins), regardless of interview language.

### German trigger phrases

The frontmatter `description` keeps the trigger lexicon English-only per `spec/claude/skill-management/` §Structure (plugin-distributed skills). Treat the following German paraphrases as equivalent and discoverable through this skill:

- "Anforderungen für X erfassen / aufnehmen"
- "interviewe mich zu diesem Feature, bevor wir bauen"
- "ich will etwas bauen, weiß aber noch nicht genau was"
- "hilf mir herauszufinden, was ich eigentlich brauche"
- "Anforderungen klären, bevor wir loslegen"

### Precondition

Before any operation, verify that `spec/project/requirements-elicitation/<canonical_language>.md` is reachable in the current project. If the spec is missing, stop and tell the user the methodology spec is the input to this skill — without it there is no authoritative definition of the dimensions, the KPI, or the gating thresholds. Do not improvise a replacement.

### The understanding KPI (load-bearing)

The interview is driven by the spec's KPI, maintained live across turns:

- **Gap matrix** over the eight closed dimensions; each is either applicable (with a confidence score `c_d ∈ [0,1]`) or explicitly `n/a (reason)`.
- `c_d` is an **uncertainty proxy**, not a calibrated probability. Estimate it primarily by **self-consistency** (per the spec, the strongest training-free signal): privately generate `k ≥ 2` independent interpretations or solution sketches for the dimension; the more they diverge, the lower `c_d`. Verbalized confidence MAY supplement this but is never the sole input.
- **Separate the two uncertainty sources** per dimension: *specification uncertainty* (the user has not decided/stated what they want — remedy: a decision-eliciting question) versus *interpretation uncertainty* (the user was clear, but the agent is unsure it read them right — remedy: a teach-back confirmation).
- **Gate** on the weakest required dimension: `U_gate = min_d c_d`. Default thresholds (spec defaults, project-overridable with a recorded rationale): `τ_low = 0.4`, `τ_high = 0.8`.
  - `c_d < τ_low` → a clarification is **mandatory** before proceeding past that dimension.
  - `c_d ≥ τ_high` **and** teach-back confirmed → the dimension is "understood".
  - in between → clarify only when expected information gain (EVPI) exceeds the question's cost.

### Operations

#### 1. `elicit` — run the interview and write the artifact

Interactive walk-through. **One question (or one tightly-coupled group) per turn — never a batched questionnaire.** Surface each step and let the user correct before moving on.

1. **Name and scope the elicitation.** Prompt for a one-line subject and a `<slug>` for the artifact. Capture the bounded context (what is being built, for whom, what is explicitly out of scope) before any requirement is recorded.
2. **Open the funnel wide.** Begin with broad, open-ended questions ("walk me through what you're trying to achieve"); narrow to specific, closed questions only as understanding firms up. Resist scripting a fixed turn order — adapt to the answers.
3. **Initialize the gap matrix.** Mark each of the eight dimensions applicable or `n/a (reason)`; set every applicable `c_d` low until evidence raises it.
4. **Loop until saturation (see Hard rules), each turn:**
   - Identify the lowest-confidence required dimension (`U_gate`).
   - Decide *whether* to ask: below `τ_low` a question is mandatory; otherwise ask only if EVPI > cost (don't fatigue the user with low-value questions).
   - Choose *which* question by what most shrinks the space of viable interpretations — offer the divergent readings as options rather than an open "can you clarify?".
   - Use probing types deliberately: *elaboration*, *interpreting*, *reason-seeking* (separate want from need — ladder a proposed solution back to its underlying goal), *consistency*.
   - For tacit/IKIWISI gaps, offer concrete examples, counter-examples, negative scenarios ("what should *never* happen?"), and edge/error cases — these are the dimensions users most reliably omit.
   - **Teach-back before raising `c_d` to "understood":** reflect your interpretation back in the user's terms and get explicit confirmation. Only then may the requirement be tagged `confirmed`.
   - Screen each utterance against the non-exhaustive trigger-word checklist (optionality, subjectivity, vagueness, weakness, implicit reference, multiplicity, under-specification); when in doubt, flag it (recall over precision).
   - Normalize each understood requirement into an EARS-style target structure ("WHEN <trigger>, the <system> SHALL <response>") or equivalent controlled phrasing; a requirement that resists normalization is not yet understood.
   - Update `c_d` only from evidence (an answer, a confirmed assumption, a successful teach-back) — never from the mere passage of turns.
5. **Make assumptions explicit.** Any inference the user has not confirmed is recorded `assumed`, never `confirmed`, and surfaced for confirmation.
6. **Write the artifact** to `project/requirements/<slug>.md` using `templates/requirements.template.md`: the normalized requirement list (each tagged `confirmed`/`assumed` with traceability to the triggering utterance), the filled gap matrix with final `c_d` and `U_gate`, the thresholds used, and the surviving assumptions / open risks. Confirm the path back to the user.

#### 2. `validate` — audit an existing requirement artifact

Run this checklist against a given `project/requirements/<slug>.md`:

- [ ] Bounded context (what / for whom / out of scope) is declared before any requirement
- [ ] Gap matrix covers all eight dimensions, each applicable-with-`c_d` or `n/a (reason)`
- [ ] Each `c_d` is justified by a named evidence event; at least one derives from a `k ≥ 2` self-consistency check, not self-report
- [ ] Every requirement is in the normalized EARS/CNL structure or flagged not-yet-understood
- [ ] Every requirement is tagged `confirmed` (teach-back/authoritative answer) or `assumed`, consistent with its matrix cell
- [ ] Specification vs interpretation uncertainty is distinguishable per dimension
- [ ] `U_gate`, `τ_low`, `τ_high`, the self-consistency `k`, and the question budget are stated explicitly
- [ ] Surviving assumptions / below-`τ_high` cells are listed as named open risks

Report pass/fail per item. Offer to fix mechanical gaps (missing tags, missing dimension placeholders) in place. Never invent `confirmed` tags, requirements, or `c_d` values while fixing.

#### 3. `revisit` — update after a scope change

Triggered when the user signals a material scope change (new actor, new constraint, new out-of-scope boundary, a built prototype that changed their mind — the IKIWISI feedback loop). Re-run `elicit` steps 2–5 as a diff against the existing artifact: show which requirements stay, which need re-validation (reset their `c_d`), which become irrelevant. Persist only after the user accepts each diff item.

### Gotchas

- **`c_d` is a proxy, not a probability.** Per the spec it drives gating as a relative ordering; never present it to the user as a literal "I'm 80 % sure this is correct." It says "this dimension is the weakest link," not "this is calibrated truth."
- **Specification uncertainty and interpretation uncertainty need different questions.** A low `c_d` because the *user hasn't decided* calls for a decision-eliciting question; a low `c_d` because *you might have misread* calls for a teach-back. Conflating them wastes turns and fatigues the user.
- **Over-questioning is a failure mode too.** The EVPI/cost rule and the question budget exist to stop the interview interrogating the user past the point of value. A confidently-understood smaller set beats an exhausted user and a padded one.
- **Teach-back is not optional flavor.** It is the only mechanism that catches the *confident misread* — an interpretation that is internally acceptable but wrong fails silently unless reflected back. No `confirmed` tag without it.
- **The German trigger phrases ship in the body, not the description.** The frontmatter `description` is English-only per `agent-management` §Structure (plugin-distributed); German operator-voice triggers live in `## German trigger phrases` so they stay greppable in an open conversation.

### Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/requirements-elicit/<run-id>.yml` after every teach-back confirmation and at each named phase boundary, carrying the live gap matrix and `c_d` values so an interrupted interview resumes without re-asking confirmed dimensions. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot (the `<slug>` and bounded context) matches the current invocation; if one matches, prompt `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope and fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

### Hard rules

- Never record a requirement before the bounded context (what / for whom / out of scope) is declared in writing — this is the load-bearing rule of the underlying spec.
- Never tag a requirement `confirmed` without an explicit teach-back confirmation from the user. `assumed` is always the safe default.
- Never batch the interview into a single questionnaire. One question (or one tightly-coupled group) per turn; the funnel and the per-turn gate are the method.
- Never raise a `c_d` from the passage of turns; only evidence raises confidence.
- Never invent requirements, acceptance criteria, or `c_d` values. Missing information is an open question or an `assumed` entry, not a plausible fill-in.
- Never terminate by running out of ideas. Stop only by the recorded criterion — saturation (`min_d c_d ≥ τ_high` and no positive-EVPI question remains) or the question-budget cap — and on a budget-capped stop, surface every below-`τ_high` cell as a named residual risk.
- The default thresholds (`τ_low`, `τ_high`, `k`, question budget) are spec defaults and engineering values, not calibrated constants; state them in the artifact and let the operator override with a recorded rationale.
- When `spec/project/requirements-elicitation/` disagrees with this skill, the spec wins. Propose updating this skill rather than diverging silently.
