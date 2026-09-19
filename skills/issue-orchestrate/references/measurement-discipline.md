# Measurement discipline

Per `spec/claude/claim-provenance/`, `spec/claude/dispatch-brief/`, and
`spec/project/issue-orchestration/` §"Issue acquisition and comprehension" — the four
points in this flow where a claim can travel further than its evidence. Each is
written from a measured failure, not from caution.

## A claim found in prior art is input, not evidence

A measurement stated in an earlier comment, a previous run's analysis, or a merged
pull-request body is an *assertion by another author*. Citing it discharges nothing
unless that artefact presents the claim as established and its anchor still resolves
(`claim-provenance` §B). Re-measure any inherited claim the decomposition will rest
on, or carry it forward explicitly marked unestablished.

Inheriting a prior run's stated cause as fact is how one wrong measurement becomes
three artefacts asserting it: the analysis repeats it, the dispatch brief hands it to
a specialist as a given, and the specialist writes it into documentation.

**Watch the mutable ref.** A value read through a branch name, `HEAD`, a default-
branch alias, or a floating tag answers for the moment the command ran. Resolve it to
a commit SHA or a digest and re-read there before it becomes load-bearing, and check
that two values quoted together came from the *same* revision — values that never
co-existed compose into a false statement whose every part is separately true.

## Verify an asserted cause before the first tracked change

An issue that names a **cause** — "the flake comes from the fixture size", "the gate
rejects because the token is stale" — and not only a defect makes a claim about the
code. That claim is the author's reading, and the author had no more access to the
code than this run has now. Before the first tracked change to the issue's files, the
cause **MUST** be verified against the code: read the cited lines, run the reading or
the check the cause rests on, and record the result in the pre-analysis artifact under
`## Classification` → **Asserted cause verified**. A divergence **MUST** be recorded
with the measurement that showed it, and the measurement wins over the issue text: the
decomposition rests on what was observed, and the refuted cause is named as refuted so
the dispatch brief cannot hand it on as a given.

**What counts as verification.** Reading the cited lines at the cited revision. Running
the reproduction, the query, or the checker the cause rests on and reading its output.
Tracing the code path the issue names to the point where it does or does not do what
the issue says.

**What does not count.** Re-reading the issue, however carefully — it restates the
claim, it does not test it. A green existing check — it may share the author's blind
spot, and in the dependency-sweep case below the checker *was* the defect. A comment
by another author agreeing with the cause — that is prior art, and prior art is input,
not evidence. The absence of an obvious alternative explanation.

**Proportionality.** The obligation binds only where a cause is asserted. A one-line
typo fix, a wording change, or an issue that reports a symptom without explaining it
acquires no ceremony; the verification is then the ordinary comprehension of operation
1. Where a cause is asserted, the cost of verifying it is the cost of reading the lines
it cites — cheaper than any of the outcomes below.

**Background.** Five consumer cases in which following the asserted cause would have
produced no repair, a wrong repair, or a new defect:

- a **fixture-size flake** blamed on the fixture's size, where the size was not the
  variable that flaked;
- a **login gate** whose stated cause pointed at the wrong check, so the fix would have
  loosened a gate that was already correct;
- a **favourites resolver** whose asserted cause was upstream of the real one, so the
  repair would have changed working code and left the defect in place;
- a **favourites error clause** whose named branch was never reached, so the "fix" would
  have added dead code and closed the issue with the defect intact;
- a **dependency sweep** whose evidence was the author's own checker, and the checker
  was the thing that was wrong — a green run of it was the blind spot, not the proof.

## Search the corpus before declaring a correction done

When a work package removed a false factual claim, grep the repository for the
distinctive values of that claim — the version, the identifier, the date — before
reporting the package complete. A statement that reached one document usually reached
its neighbours and its translations too, and each surviving copy is a separate review
round later. One `grep` collapses them into the round you are already in.

## Externally-visible artefacts wait for the gate

Filing a new issue, commenting on the tracked issue, or posting a finding into
another repository publishes a claim under someone else's eyes. When the claim rests
on a measurement this run made, that publication **MUST** wait until the verify gate
has run green on the change carrying it.

A measurement that survives review costs one publication. A measurement published
first and refuted later costs a retraction in every place it landed — and the
retraction is public too.
