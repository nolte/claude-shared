#!/usr/bin/env python3
"""PreToolUse guard: refuse to switch onto a feature branch in the primary checkout.

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

Scope (deliberately narrow — only what actually moves HEAD):
  - Acts only on `Bash` commands whose git subcommand is `checkout` or `switch`
    and whose branch operand is feature-prefixed (feat/ fix/ chore/ docs/ exp/).
    The `branch` subcommand is NOT guarded: `git branch feat/x` creates a ref
    without moving HEAD, and `git branch -d/-D/-m` deletes/renames — none of
    these put the primary checkout on a feature branch.
  - A pathspec checkout (`git checkout <ref> -- <path>`) restores files and
    never moves HEAD, so it is allowed even when the path is under docs/ etc.
  - Enforces only in the *primary checkout* (git-dir == git-common-dir). In a
    linked worktree, feature branches are correct, so the hook allows them.
  - Honours an explicit `git -C <path>` (per command segment) so a worktree
    session that drives the primary checkout by path is still guarded — the
    user's parallel-terminal workflow, where HEAD moves between tool calls.

Fail-safe: any parse/IO error returns 0. A guardrail must never block
legitimate work because of its own bug; the pre-commit hook remains the hard
backstop.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys

FEATURE_PREFIXES = ("feat", "fix", "chore", "docs", "exp")
# Matches a feature-prefixed branch operand, e.g. `feat/foo`, `chore/bar-baz`.
_FEATURE_PREFIX = re.compile(r"(?:%s)/" % "|".join(FEATURE_PREFIXES))
# Statement separators inside a single Bash command string (`||` before `|`).
_SEG_SPLIT = re.compile(r"&&|\|\||;|\n|\|")


def _git(args: list[str], cwd: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, timeout=5
    )


def _tokens(segment: str) -> list[str]:
    try:
        return shlex.split(segment, posix=True)
    except ValueError:
        return segment.split()


def _segment_switch(segment: str) -> tuple[str | None, str | None]:
    """Inspect one command segment.

    Return `(branch, cwd_override)` when the segment is a `git checkout|switch`
    that moves HEAD onto a feature-prefixed branch; `cwd_override` is the value
    of an explicit `git -C <path>` in the same segment, else None. Returns
    `(None, None)` for anything else, including:
      - the `git branch` subcommand (never moves HEAD),
      - a pathspec checkout `git checkout [<ref>] -- <path>` (restores files),
      - a `checkout`/`switch` whose branch operand is not feature-prefixed.
    """
    toks = _tokens(segment)
    if "git" not in toks:
        return None, None
    rest = toks[toks.index("git") + 1:]

    cwd_override: str | None = None
    sub: str | None = None
    i = 0
    # Walk git's global options to reach the subcommand; -C and -c take a value.
    while i < len(rest):
        t = rest[i]
        if t == "-C" and i + 1 < len(rest):
            cwd_override = rest[i + 1]
            i += 2
            continue
        if t == "-c" and i + 1 < len(rest):
            i += 2
            continue
        if t.startswith("-"):
            i += 1
            continue
        sub = t
        i += 1
        break

    if sub not in ("checkout", "switch"):
        return None, None
    args = rest[i:]
    if "--" in args:  # pathspec form — restores files, does not move HEAD
        return None, None
    operand = next((a for a in args if not a.startswith("-")), None)
    if operand and _FEATURE_PREFIX.match(operand):
        return operand, cwd_override
    return None, None


def _analyze(cmd: str) -> tuple[str | None, str | None]:
    """Return `(branch, cwd_override)` for the first segment that switches onto a
    feature branch. Per-segment so `git checkout develop && git merge feat/x`
    (segment 2 is a `merge`, not a switch) is correctly allowed."""
    for seg in _SEG_SPLIT.split(cmd):
        branch, cwd_override = _segment_switch(seg)
        if branch:
            return branch, cwd_override
    return None, None


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

    target, cwd_override = _analyze(cmd)
    if not target:
        return 0

    cwd = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    if cwd_override:
        cand = os.path.expanduser(cwd_override)
        if os.path.isdir(cand):
            cwd = cand

    try:
        gd = _git(["rev-parse", "--absolute-git-dir"], cwd)
        cd = _git(["rev-parse", "--git-common-dir"], cwd)
        if gd.returncode or cd.returncode:
            return 0
        git_dir = os.path.realpath(gd.stdout.strip())
        common_dir = os.path.realpath(os.path.join(cwd, cd.stdout.strip()))
    except Exception:
        return 0

    if git_dir != common_dir:
        return 0  # linked worktree — feature-branch work belongs here

    sys.stderr.write(
        f"✖ Blocked: switching onto feature branch '{target}' in the "
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
