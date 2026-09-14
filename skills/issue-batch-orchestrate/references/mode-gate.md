# The mode gate

Two strand modes exist. The choice is deterministic, not a matter of taste, and it is
recorded in the group artifact with its reason before the first member is implemented.

## The criterion: removability

**Choose Mode B when any member is likely to need removal from the bundle.** That is
the case when its acceptance is uncertain, when it depends on something outside the
group's control, or when a review that could reject it is still outstanding — most
commonly a member classified `security`.

**Otherwise choose Mode A.**

Removability is the criterion because it names the property Mode B actually buys: a
Mode B member can be removed by dropping one merge, while a Mode A member is entangled
in a shared commit strand and has to be unpicked commit by commit.

Deliberately *not* the criterion:

- **Member count.** A size threshold is a proxy nobody has calibrated. It is deferred
  as an open question in the governing spec, not adopted silently here.
- **Overlapping touch surface.** This inverts the benefit. Members editing the same
  files profit from a shared strand; separate sub-branches would only manufacture
  merge conflicts between them.

## Mode A — single strand

Every member is implemented directly on the integration branch, in that branch's
worktree. One commit strand, one diff, the simplest possible shape.

## Mode B — sub-branch per member

Each member gets its own sub-branch created **off the integration branch tip**, in its
own worktree — a branch is checked out at most once, per
`spec/project/parallel-working-copies/` §"Branch-to-worktree mapping".

Each sub-branch merges back into the integration branch **without a pull request**, and
its worktree and branch are retired immediately afterwards.

Sub-branches rebase onto the **integration branch**, never onto `develop`. Only the
integration branch tracks `develop`.

## Why no group-internal pull request

`spec/project/pull-request-workflow/` §"PR preconditions" requires every pull request to
target `develop`. A pull request based on the integration branch would violate that, so
the bundle pull request is the group's single review surface.

The accepted cost: a member gets no review gate of its own. The governing spec records
this as an open question rather than pretending it is free. If a member's defect ever
survives the collective review, that is the evidence that reopens the question.

## Changing mode mid-flight

If a member turns out to need removal after Mode A was chosen, that is a **structural
regression** per `spec/claude/research-plan-implement/` §"Re-planning is explicit":
stop, name the assumption that failed, and return to the plan operation. Either extract
that member onto its own branch or remove it from the group.

A removed member returns to individual processing under `issue-orchestrate`, the
artifact records the removal, and the member is not closed at operation 7.

If the bundle pull request is already open, remove the member's changes from the branch
— in Mode B by dropping its merge — and update both the artifact and the pull-request
body. A bundle must never merge while claiming a member it no longer carries.
