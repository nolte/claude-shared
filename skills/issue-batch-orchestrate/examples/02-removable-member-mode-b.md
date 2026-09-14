# Example 02 — a removable member forces Mode B

## Operator prompt

> "Group #801, #802 and #805 — they all touch the token-refresh path."

## 1. admit

Admitted on **shared touch surface**: all three change `auth/refresh.py`. #805 is
additionally classified `security`.

One-sentence logical change: *"Make the token-refresh path correct under concurrent
renewal."* Group id `2026-09-14-token-refresh`.

## 2. analyze

**Symptom cluster**: all three reports trace to one root cause — the refresh lock is
released before the new token is persisted. The plan therefore targets the lock
ordering once, rather than patching three call sites.

## 3. plan

Artifact written; Tier 3, because the fix changes a published contract (the refresh
endpoint's concurrency guarantee). Tier 3 obligations apply:

- the design question is settled first — the lock moves into the persistence
  transaction, decided with the operator **before** the plan describes how
- the plan is decomposed into independently verifiable slices, one per member
- a verification pass is run by a context that did not produce the change

Operator approves. **Write gate crossed.**

## 4. branch

Issue #805 carries an outstanding security review that could reject it, so it is
**likely to need removal** → **Mode B**.

Integration branch `fix/2026-09-14-token-refresh`. Each member gets a sub-branch off
the integration branch tip in its own worktree, merged back **without a pull request**.
Sub-branches rebase onto the integration branch, never onto `develop`.

## 5. implement

Members are implemented in dependency order: #801 lands the lock reordering, with #802
and #805 building on it.

The security review then rejects #805's approach. That invalidates no admission
predicate, no mode decision and no ordering, so it is recorded as a **local
adaptation** — not a structural regression — and #805's merge is dropped from the
integration branch. #805 returns to individual processing under `issue-orchestrate`.

Mode B is what makes this cheap: one merge is dropped, and #801 and #802 are untouched.
Under Mode A the same removal would mean unpicking commits from a shared strand.

## 6. bundle

The bundle now carries two members. Both the artifact and the pull-request body are
updated to drop #805 **before** the merge — a bundle must never merge while claiming a
member it no longer carries.

## 7. close

Issues #801 and #802 are closed with cross-references after the merge. **#805 is not
closed**: it was dropped, and closing it would falsely mark it resolved.
