# Example: update an existing post

Feature `F-12` (`improve-lix-corridor-tuning`) reached `done`. Its derived
slug already matches a published post in `nolte/blog`, so the skill
suggests Choice 2 (update the existing post) rather than a new one.

## 1. Resolve the trigger event

```
project/features/improve-lix-corridor-tuning.md
  id: F-12
  status: done           # confirmed — feature → done fires
  title: Improve LIX corridor tuning
  description: Widen the developer-docs LIX corridor and add a per-language warn band.
  roadmap_item: R-11
done-transition commit: 9ad42f0
repo: nolte/claude-shared
```

## 2. Derived briefing

| Field | Derived value |
| --- | --- |
| topic-as-thesis | "Tuning the LIX corridor per language gives developer docs a realistic readability target." |
| grounded artefact | `nolte/claude-shared@9ad42f0` |
| slug | `lix-corridor-tuning` (lifecycle prefix dropped) |
| translationKey | `lix-corridor-tuning` |

## 3. Suggestion + choice

Derived slug `lix-corridor-tuning` is **present** in `nolte/blog`'s
existing-post index → the skill suggests **Choice 2 (update existing
post)**, naming that post as the target. The operator confirms Choice 2.

## 4. Execute

- The skill pre-stages `project/blog-triggers/improve-lix-corridor-tuning.briefing.md`
  in `claude-shared`, carrying the target post's existing `slug` and
  `translationKey` (operator-picked from the index) plus an **update
  reason** derived from the feature `title` and a one-line summary of what
  changed (the per-language warn band).
- It surfaces the blog-consumer clone path `~/repos/github/blog` and asks
  the operator to confirm the working-directory switch — no silent
  cross-repo write.
- The operator opens a session in the blog clone and invokes `blog-author`
  with the pre-staged briefing; `blog-author` revises the existing post
  pair rather than drafting a new one.
- Because a real update happened, no deferral artefact is written. Had a
  prior Choice-3 deferral existed for `F-12`, this run would flip its
  `status: deferred → consumed` rather than writing a second artefact.
