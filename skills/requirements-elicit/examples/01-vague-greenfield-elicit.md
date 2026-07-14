# Example 01 — Vague greenfield request driven to a confidence-scored requirement set

The default case the method is engineered for: the user knows they want
*something* but cannot yet state it precisely. Exercises the `elicit`
operation end to end — the one-question-at-a-time funnel, the live gap
matrix, teach-back before any `confirmed` tag, and the written artifact.

## Input prompt

> I want to build something to keep track of my houseplants, but I'm
> not totally sure what it should do yet.

## Input files

Greenfield — no prior `project/requirements/` docs exist.
`spec/project/requirements-elicitation/en.md` is reachable in the repo.
The surrounding `project/` docs are English, so the artifact will be
English.

## Expected behaviour

1. **Precondition passes.** The methodology spec is reachable, so the
   skill proceeds rather than improvising the dimensions or thresholds.
2. **Name and scope first.** The skill asks for a one-line subject and a
   `<slug>` (`houseplant-tracker`) and pins the bounded context (what is
   being built, for whom, what is out of scope) *before* recording any
   requirement — Hard rule 1.
3. **Funnel opens wide.** It starts with an open-ended "walk me through
   what you're trying to achieve" rather than a scripted questionnaire,
   and narrows only as understanding firms up.
4. **Gap matrix initialised.** All eight dimensions are marked applicable
   or `n/a (reason)`; every applicable `c_d` starts low.
5. **One question per turn, lowest-confidence first.** Each turn lifts the
   weakest required dimension (`U_gate = min_d c_d`). Below `τ_low = 0.4`
   a clarification is mandatory; in between, the skill asks only when
   EVPI exceeds the question's cost, so the user isn't over-questioned.
6. **Teach-back before `confirmed`.** Each understood requirement is
   reflected back in the user's terms and normalised into EARS phrasing
   ("WHEN a plant's watering interval elapses, the system SHALL notify
   the owner"); only an explicit confirmation raises `c_d` to "understood".
7. **Assumptions stay `assumed`.** Anything the user hasn't confirmed —
   e.g. "you probably want push notifications" — is recorded `assumed`,
   never `confirmed`, and surfaced for later confirmation.
8. **Artifact written.** The skill writes
   `project/requirements/houseplant-tracker.md` from the template: the
   normalised requirement list, the filled gap matrix with final `c_d`
   and `U_gate`, the thresholds used, and the surviving assumptions. It
   confirms the path back to the user.
