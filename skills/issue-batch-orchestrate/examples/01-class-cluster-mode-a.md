# Example 01 — class cluster on a single strand (Mode A)

## Operator prompt

> „Die drei Settings-Issues #623, #624 und #625 bitte gebündelt abarbeiten."

## 1. admit

All three issues repair the same repository-settings surface. Each is admitted on
**thematic coupling**, with evidence:

| Issue | Evidence |
|---|---|
| #623 | `.github/settings.yml:12` — `topics` declared as a list |
| #624 | `.github/settings.yml:3` — `_extends` carries an unsupported ref |
| #625 | `.github/settings.yml:31` — same defect in the Boring Cyborg block |

One-sentence logical change: *"Make `.github/settings.yml` loadable by the settings app
by removing every construct the app rejects."*

Group id `2026-09-14-settings-drift`. None is `question`-class, all three are bounded.
Operator confirms membership.

## 2. analyze

Not a symptom cluster — the three are independent edits. It is a **class cluster**: one
recurring defect class, "a settings-file construct the platform app rejects".

Structural cause sits in the process: nothing validates the file against the app's
schema before it ships, so every malformed field reaches production and returns as an
issue. Recorded as a **process finding**, filed as its own issue, with the preventive
change named: a schema validation step in the lint job.

## 3. plan

Artifact written to `.audits/issue-batch-integration/2026-09-14-settings-drift/analysis.md`.
Tier 2. The completeness matrix carries Config, Spec, Docs and Generated-index columns;
Source and Tests are `not applicable — no code path touches the settings file`, with the
reason stated rather than left blank.

Operator approves. **This is the write gate.**

## 4. branch

No member's acceptance is uncertain, nothing external is pending, no review can reject
one → **Mode A**. Dominant Conventional-Commits type is `fix`, so the integration branch
is `fix/2026-09-14-settings-drift`, created with
`task worktree:add -- fix/2026-09-14-settings-drift settings-drift`. Not `exp/`: the
work ships and must appear in the release notes.

## 5. implement

`issue-orchestrate` is dispatched per member, in order, each gated. Every matrix check
is run and its real output recorded — for example the settings-app sync returning
`200 OK` rather than the note "settings applied".

`quality-gate` is run against the integration branch tip, not against any member's
intermediate state.

## 6. bundle

The artifact is removed with a fix-forward `git rm`. One pull request opens against
`develop`, listing all three issues under `## Linked issues`, with the group id,
per-member predicate and mode in **Risk / rollout notes**, and exactly **one**
`## Class sweep` whose predicate matched the whole class — not three sweeps saying the
same thing.

## 7. close

After the squash-commit lands, each of #623, #624 and #625 is closed on operator
confirmation, with a comment naming the bundle pull request and the merge SHA. The
process finding stays open: repairing the members did not add the missing validation.
