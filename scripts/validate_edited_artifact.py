#!/usr/bin/env python3
"""PostToolUse hook: validate a just-edited skill/agent artifact immediately.

Wired in `.claude/settings.json` as a `PostToolUse` hook matching
`Write|Edit|MultiEdit|NotebookEdit`. When the edited file is a skill
(`skills/.../SKILL.md` or `plugins/.../skills/.../SKILL.md`) or an agent
(`agents/<name>.md` or `plugins/.../agents/<name>.md`), it runs
`scripts/validate_skills.py` against just that file and surfaces any
Critical-grade frontmatter finding back to Claude (exit 2) — so a broken
`name`/`description`/`phase`/`resumable` is caught at edit time, not later at
`task test` or in CI.

This is the deterministic "verify the change" guardrail from the Claude Code
best practices, scoped to the moment and file of the edit. It deliberately does
NOT run the whole suite on every stop: a blocking Stop gate over the full tree
can trap a session on a pre-existing or unrelated Critical, and formatting is
already owned by `.pre-commit-config.yaml`.

Only Critical findings (validate_skills exit 1) are surfaced; Warning- and
Suggestion-grade findings are advisory by design and left for `task test` / CI
so a passing edit-time check never blocks on non-load-bearing nits.

Exit codes: 2 -> surface findings to Claude; 0 -> allow / not an artifact.
Fail-safe: any parse/IO error returns 0 (a guardrail must never wedge on its
own bug; `task test` + CI remain the hard backstop).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

REPO = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()

# A source skill/agent the validator actually governs, anchored to the plugin
# roots exactly as the `validate-skills` pre-commit hook's `files:` filter is.
# The `^` anchor is load-bearing: it excludes the generated MkDocs catalog under
# docs/<lang>/{skills,agents}/** (whose files would otherwise be misread as
# frontmatter-less agents and wrongly blocked).
_ARTIFACT_RE = re.compile(
    r"^(?:skills/.+/SKILL\.md"
    r"|agents/.+\.md"
    r"|plugins/[^/]+/skills/.+/SKILL\.md"
    r"|plugins/[^/]+/agents/.+\.md)$"
)


def is_artifact(rel: str) -> bool:
    return bool(_ARTIFACT_RE.match(rel.replace("\\", "/")))


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except Exception:
        return 0
    ti = event.get("tool_input") or {}
    fp = ti.get("file_path") or ti.get("notebook_path") or ""
    if not fp:
        return 0

    rel = os.path.relpath(fp, REPO) if os.path.isabs(fp) else fp
    if not is_artifact(rel):
        return 0
    validator = os.path.join(REPO, "scripts", "validate_skills.py")
    if not os.path.exists(validator):
        return 0
    try:
        result = subprocess.run(
            [sys.executable, validator, rel],
            cwd=REPO, capture_output=True, text=True, timeout=30,
        )
    except Exception:
        return 0

    # validate_skills.py exits 1 when there is at least one Critical finding.
    if result.returncode == 1:
        sys.stderr.write(
            "validate_skills flagged the artifact you just edited "
            f"({rel}):\n{result.stdout}{result.stderr}"
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
