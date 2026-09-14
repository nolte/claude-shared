# Structural findings and process feedback

A group is a set of issues that already share a coupling. That makes it the first
corpus in which a pattern becomes visible that no single issue reveals — and analysing
each member only in isolation throws that evidence away.

## Two cluster shapes

**Symptom cluster** — several issues, one root cause. The plan targets the root cause.
Repairing `n` symptoms and leaving the cause in place guarantees the next report.

**Class cluster** — several issues of one recurring defect class. Bind the class per
`spec/project/defect-class-guards/` §"Binding into the closing process" and carry its
sweep once, at group level. A group admitted on thematic coupling of one defect class
has exactly one predicate by construction; one sweep per member would restate it `n`
times and measure nothing extra.

Record which of the two the group is. Record explicitly when neither applies and no
structural cause was found, so its absence is a statement the operator can challenge
rather than a silent omission.

## Process findings

When the structural cause sits in the **development process** rather than in the
changed artifacts — a rule that permits the defect, a gate that does not catch it, a
check that does not exist — record it as a process finding and file it as its own issue
against the governing spec or gate, referencing the group id.

A process finding **is not resolved when the members are repaired**. Repairing them
leaves the process that produced them untouched, so the class recurs and the next group
looks like new work.

Every process finding names the concrete preventive change: the rule, the guard, or the
check that would have stopped the group from arising. A process finding without a named
preventive change is an observation, not a finding, and is not filed as one.

## Feeding the portfolio loop

Feed every recurring finding class into the loop that
`spec/project/continuous-improvement/` §"Portfolio gap closure (the loop stays alive)"
owns, recording the class and its recurrence count.

Do not restate or re-derive that spec's recurrence threshold here. The division is
deliberate: **the group supplies the evidence, the loop owns the trigger.** A threshold
copied into two places drifts, and the copy is always the one that goes stale.

## A worked shape

A group of three issues all repairing the same repository-settings surface, each merged
as its own pull request, is a class cluster. The members are the symptom. The process
finding is that nothing validated the settings file against the platform's schema
before it shipped, so every malformed field reached production and returned as an
issue. The preventive change is that validation, filed as its own issue — not an
intention recorded in the bundle's body, which is lost at merge.
