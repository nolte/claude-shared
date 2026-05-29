# Blog triggers

This directory holds the on-disk artefacts of the `feature → done` blog trigger, per `spec/project/blog-author-trigger/`. It is written by the `/nolte-shared:blog-author-trigger` skill (automatically dispatched from `sprint-execute` Operation C step 6).

Two artefact kinds live here:

## `<feature-slug>.yml` — deferral artefact

Written when the operator chooses **defer to backlog** (Choice 3). Schema (per the trigger spec §Deferral artefact):

```yaml
id: F-9                         # feature id
slug: wire-renovate-automerge-exclusion
title: Wire Renovate automerge exclusion
description: <feature description body>
acceptance_criteria:
  - "<criterion>"
roadmap_item: R-3               # when present on the feature
repo: nolte/claude-shared
done_commit: a2936de            # SHA of the in_progress → done transition
deferred_at: 2026-05-29T10:14:00Z
deferral_reason: "<operator-supplied>"
status: deferred                # deferred | consumed | cancelled
```

- A later trigger-run on the same feature `id` **consumes** this file (`status: deferred → consumed`) rather than creating a second one.
- `status: cancelled` is operator-set only; the trigger never sets it.
- `sprint-review` surfaces unconsumed (`status: deferred`) entries at sprint close.

## `<feature-slug>.briefing.md` — pre-staged briefing

Written when the operator chooses **new post** (Choice 1) or **update** (Choice 2) and the blog consumer is a separate repository. It carries the derived briefing in the shape `blog-author` §Briefing inputs expects, so the operator can open it in the blog consumer's session (`~/repos/github/blog`) and hand it to `/nolte-shared:blog-author`. The trigger never writes into the blog consumer's working tree itself.
