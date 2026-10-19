# Fresh-session restart

Read at operation 5, and when the operator picks a refresh policy at the gate.

## Why

A long run fills the context with lane summaries and merge logs that no later step needs. The state file already holds what a later step does need, so restarting costs one re-read and keeps quality flat.

## Policy

- `never` (default): no restart.
- `per-merge`: restart after every merge.
- `every=<N>`: restart after every N-th merge.

A restart is only offered at a **boundary**: a merge is verified, the checkpoint is written, and no lane agent is running. Never mid-round.

## What the skill does

A session can't restart itself. At the boundary it sets `phase: ready-to-restart`, writes the checkpoint, and ends the turn with exactly this:

```
Run <run_id> is saved (phase ready-to-restart, <n> PRs merged, <m> lanes open).
Start a fresh session and paste:

  cd <primary-checkout> && claude
  /nolte-shared:backlog-delivery-orchestrate --resume <run_id>
```

## What the new session does

`--resume` is the explicit non-interactive choice, so it doesn't prompt. It re-hydrates `decisions:` (the gate is **not** asked again, the authorisation stands), then re-reads GitHub for every lane PR before acting. A PR the file calls open but GitHub reports merged is recorded as merged. A file with a newer `schema_version` or broken YAML is refused with `start-new` or `discard` as the only follow-ups.
