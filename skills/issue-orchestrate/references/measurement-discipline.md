# Measurement discipline

Per `spec/claude/claim-provenance/` and `spec/claude/dispatch-brief/` — the three
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
