#!/usr/bin/env bash
# Regenerate the skill-agent catalog and stage the resulting changes so
# they land in the same commit that touched skills/<name>/SKILL.md or
# agents/<name>.md.
#
# Wired in .pre-commit-config.yaml as the `docs-catalog-fresh` hook.
# Triggered by pre-commit's `files:` filter; runs once per commit even
# when multiple skill/agent files are staged (the hook declares
# `pass_filenames: false`).
#
# Operationalises spec/claude/skill-agent-catalog/ §Generation mechanism
# and closes the workflow-health defect surfaced in PR #112 (the
# `Verify committed catalog is fresh` CI gate caught a missing regen
# that the author had to fix-forward; this hook prevents the same
# foot-gun locally).
set -euo pipefail

# Regenerate. The Taskfile target runs scripts/docs/gen_catalog.py.
task docs:catalog

# Catalog output paths owned by scripts/docs/gen_catalog.py. Keep this
# list in sync with the CI `Verify committed catalog is fresh` step in
# .github/workflows/ci.yml — both lists govern the same surface.
CATALOG_PATHS=(
  docs/de/skills
  docs/de/agents
  docs/de/tags.md
  docs/en/skills
  docs/en/agents
  docs/en/tags.md
)

# Stage every regenerated catalog file so it joins the in-flight commit.
# `git add` with `--` so a literal path that starts with `-` can't fool
# the shell. Missing paths (the repo doesn't have agents yet, etc.) are
# a no-op — `git add` ignores them without erroring when they don't
# exist on disk.
git add -- "${CATALOG_PATHS[@]}" 2>/dev/null || true

# Safety net: if the generator wrote files outside the declared
# CATALOG_PATHS list (a future generator change without a hook update),
# pre-commit's built-in "files were modified by this hook" detection
# blocks the commit and the author sees the unexpected paths. Don't
# replicate that check here.
