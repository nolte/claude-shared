#!/usr/bin/env python3
"""PreToolUse guard: refuse to create/switch onto a feature branch in the primary checkout.

Wired in `.claude/settings.json` as a `PreToolUse` hook matching `Bash`.
Operationalises `spec/project/parallel-working-copies/` §Branch-to-worktree
mapping as a *deterministic, pre-execution* guardrail — the complement to the
`scripts/guard_primary_checkout.sh` pre-commit hook, which only fires at commit
time, i.e. after the feature work is already sitting on the wrong branch in the
primary checkout. This hook blocks the branch switch *before* it happens.

Contract (Claude Code PreToolUse hooks):
  - Reads the event JSON from stdin (`tool_name`, `tool_input.command`).
  - Exit 0  -> allow the tool call (default for anything we don't recognise).
  - Exit 2  -> block the tool call; stderr is surfaced back to Claude.

Scope:
  - Acts only on `Bash` commands whose git subcommand `checkout` / `switch` /
    `branch` targets a feature-prefixed branch (feat/ fix/ chore/ docs/ exp/).
  - Enforces only in the *primary checkout* (git-dir == git-common-dir). In a
    linked worktree, feature branches are correct, so the hook allows them.
  - Honours an explicit `git -C <path>` so a worktree session that drives the
    primary checkout by path is still guarded (matches the user's parallel-
    terminal workflow, where HEAD moves between tool calls).

Fail-safe: any parse/IO error returns 0. A guardrail must never block
legitimate work because of its own bug; the pre-commit hook remains the hard
backstop.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

FEATURE_PREFIXES = ("feat", "fix", "chore", "docs", "exp")
# git subcommands that move or create HEAD onto a branch.
_SWITCHY = re.compile(r"\bgit\b[^\n]*?\b(?:checkout|switch|branch)\b", re.I)
# A feature-prefixed branch token, e.g. `feat/foo`, `chore/bar-baz`.
_FEATURE = re.compile(r"\b(?:%s)/[A-Za-z0-9._/-]+" % "|".join(FEATURE_PREFIXES))
# Statement separators inside a single Bash command string.
_SEG_SPLIT = re.compile(r"&&|\|\||;|\n")


def _git(args: list[str], cwd: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, timeout=5
    )


def _targets_feature_branch(cmd: str) -> str | None:
    """Return the feature branch a switch/create verb targets, else None.

    Scans per statement segment so a legitimate primary-checkout operation that
    merely *names* a feature branch as a non-switch argument
    (`git checkout develop && git merge feat/x`) is not mistaken for a switch
    onto it: segment 1 switches to develop (no feature token), segment 2 is a
    `merge` (not a switch verb).
    """
    for seg in _SEG_SPLIT.split(cmd):
        if _SWITCHY.search(seg):
            m = _FEATURE.search(seg)
            if m:
                return m.group(0)
    return None


def main() -> int:
    if os.environ.get("CI"):
        return 0
    try:
        event = json.load(sys.stdin)
    except Exception:
        return 0
    if event.get("tool_name") != "Bash":
        return 0
    cmd = (event.get("tool_input") or {}).get("command", "")
    if not cmd:
        return 0

    target = _targets_feature_branch(cmd)
    if not target:
        return 0

    # Resolve the directory the git command acts on: honour an explicit
    # `git -C <path>`, otherwise the hook's project dir / cwd.
    cwd = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    m = re.search(r"\bgit\b\s+-C\s+('([^']*)'|\"([^\"]*)\"|(\S+))", cmd)
    if m:
        cand = os.path.expanduser(next(g for g in m.groups()[1:] if g))
        if os.path.isdir(cand):
            cwd = cand

    try:
        gd = _git(["rev-parse", "--git-dir"], cwd)
        cd = _git(["rev-parse", "--git-common-dir"], cwd)
        if gd.returncode or cd.returncode:
            return 0
        git_dir = os.path.realpath(os.path.join(cwd, gd.stdout.strip()))
        common_dir = os.path.realpath(os.path.join(cwd, cd.stdout.strip()))
    except Exception:
        return 0

    if git_dir != common_dir:
        return 0  # linked worktree — feature-branch work belongs here

    sys.stderr.write(
        f"✖ Blocked: switching/creating feature branch '{target}' in the "
        f"PRIMARY checkout.\n\n"
        f"  The primary checkout MUST stay on 'develop' at all times "
        f"(spec/project/parallel-working-copies/ §Branch-to-worktree "
        f"mapping; CLAUDE.md §Parallel working copies). Do the work in a "
        f"dedicated worktree instead:\n\n"
        f"    task worktree:add -- {target}\n\n"
        f"  Then run your git command from inside that worktree. If you are "
        f"intentionally repairing drift, run the git command from a worktree "
        f"or temporarily move this hook aside.\n"
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
