# Goals

## Vision

`claude-shared` is the Claude Code plugin `nolte-shared`: it bundles reusable skills, agents, and bilingual specifications so Claude Code workflows stay consistent across the nolte portfolio without per-repository reimplementation. The plugin is itself the reference adopter of every spec it ships — what works here, works for every consumer.

## Outcomes

- **O-1** Downstream Claude Code users in portfolio projects invoke the same slash commands and get reproducible, spec-compliant workflows in every repo that installs the plugin.
  - Audiences: Downstream Claude Code users in portfolio projects (primary); GitHub Actions CI for this repo (primary)
- **O-2** The repo maintainer (and Claude Code as co-author) can author skills, agents, and specs in one place, with bilingual prose and Conventional-Commits release discipline preserved across the portfolio.
  - Audiences: Repo maintainer (nolte) (primary); Claude Code itself as co-author (primary)
- **O-3** Every spec the plugin ships is dogfooded against `claude-shared` itself before downstream adoption — the plugin is the first repo where new specs prove they're livable.
  - Audiences: Plugin author dogfooding inside this repo (primary); Repo maintainer (nolte) (primary)

## Source

- Audience artefact: `AUDIENCES.md` at the repo root.
- Authored via inline application of `skills/roadmap-init/SKILL.md` (the plugin runtime hadn't yet loaded the new planning-suite skills as slash commands at the time of writing; operations were followed manually against the merged spec).
