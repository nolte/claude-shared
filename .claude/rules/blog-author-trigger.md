---
paths:
  - "project/features/**"
  - "project/sprints/**"
  - "project/blog-triggers/**"
---

# Blog-author trigger (feature → done)

Path-scoped rule: this loads only while working under `project/features/`,
`project/sprints/`, or `project/blog-triggers/` — the surfaces where the
`in_progress → done` transition that fires the trigger happens. The
authoritative contract lives in `spec/project/blog-author-trigger/`.

Per `spec/project/blog-author-trigger/` §Consumer contract, this repository
declares its trigger roles:

- **Source consumer:** `nolte/claude-shared` (this repository). It hosts
  features under `project/features/<slug>.md` and drives transitions via
  `/nolte-shared:sprint-execute`. The `in_progress → done` transition is the
  trigger event.
- **Blog consumer:** `nolte/blog` (the bilingual Astro blog), clone path
  `~/repos/github/blog`. It receives derived briefings; the portfolio mapping
  (`nolte/claude-shared` → `portfolioProject: claude-shared`) is declared in
  the blog consumer's own `CLAUDE.md`.

`sprint-execute` Operation C step 6 automatically dispatches
`/nolte-shared:blog-author-trigger` after marking a feature `done`; the
operator then chooses new post / update / defer. Deferrals are written under
`project/blog-triggers/<feature-slug>.yml`. Cross-repository writes into
`~/repos/github/blog` require explicit operator confirmation — the trigger
never writes there silently.
