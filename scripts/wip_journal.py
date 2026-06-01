#!/usr/bin/env python3
"""Always-on session journal hook.

Wired from .claude/settings.json as a SessionStart + PostToolUse hook. It appends
a human-readable "where was I" trail to .resume/session-journal.md so that a
notebook crash, terminal close, or session expiry never wipes the in-flight
context of free-form work — the part no resumable skill governs.

Design constraints:
- MUST NOT ever fail the triggering tool call: every path exits 0, all errors
  are swallowed. A broken journal must never block real work.
- Writes only inside the working copy's gitignored .resume/ tree (per
  spec/claude/resumable-work/ §Persistence location), so it never pollutes git.
- Reads the hook payload from stdin as JSON; tolerates a missing/empty payload
  so it also works when invoked by hand.

The journal is scratch state, not a committed artefact. `cat .resume/session-journal.md`
is the supported way to read it; `task resume` surfaces resumable sessions.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _project_dir(payload: dict) -> Path:
    # CLAUDE_PROJECT_DIR is the worktree root the hook fires in; fall back to the
    # payload cwd, then the process cwd.
    for candidate in (os.environ.get("CLAUDE_PROJECT_DIR"), payload.get("cwd"), os.getcwd()):
        if candidate:
            return Path(candidate)
    return Path.cwd()


def _encode_cwd(path: Path) -> str:
    # Mirror Claude Code's project-dir encoding: every "/" and "." becomes "-".
    return re.sub(r"[/.]", "-", str(path.resolve()))


def _journal_path(project_dir: Path, global_mode: bool) -> Path:
    # Repo-local mode writes into the gitignored .resume/ tree (dogfood, per
    # spec/claude/resumable-work/). Global mode (the portfolio-wide hook in
    # ~/.claude/settings.json) writes under ~/.claude/session-journals/<cwd>/
    # instead, so it never creates untracked files in repos that don't yet
    # gitignore .resume/.
    if global_mode:
        return Path.home() / ".claude" / "session-journals" / _encode_cwd(project_dir) / "session-journal.md"
    return project_dir / ".resume" / "session-journal.md"


def _git_branch(project_dir: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=3,
        )
        return out.stdout.strip() or "(detached)"
    except Exception:
        return "(unknown)"


def _append(journal: Path, text: str) -> None:
    journal.parent.mkdir(parents=True, exist_ok=True)
    with journal.open("a", encoding="utf-8") as fh:
        fh.write(text)


def _rel(project_dir: Path, file_path: str) -> str:
    try:
        return str(Path(file_path).resolve().relative_to(project_dir.resolve()))
    except Exception:
        return file_path


def _first_user_prompt(payload: dict) -> str:
    """Best-effort: the prompt that opened this session, for the session header."""
    prompt = payload.get("prompt") or ""
    if isinstance(prompt, str) and prompt.strip():
        line = " ".join(prompt.split())
        return line[:160]
    return ""


def handle_session_start(payload: dict, project_dir: Path, journal: Path) -> None:
    branch = _git_branch(project_dir)
    session = payload.get("session_id", "?")
    source = payload.get("source", "")  # startup | resume | clear | compact
    header = (
        f"\n## Session {session} — {_now()}"
        f" · branch `{branch}`"
        + (f" · {source}" if source else "")
        + "\n"
    )
    prompt = _first_user_prompt(payload)
    if prompt:
        header += f"- opening prompt: {prompt}\n"
    _append(journal, header)


def handle_tool_event(payload: dict, project_dir: Path, journal: Path) -> None:
    tool = payload.get("tool_name", "?")
    tool_input = payload.get("tool_input") or {}
    target = (
        tool_input.get("file_path")
        or tool_input.get("notebook_path")
        or tool_input.get("path")
        or ""
    )
    if not target:
        return  # only journal file-mutating events; skip toolless payloads
    _append(journal, f"- {_now()} · {tool} · {_rel(project_dir, str(target))}\n")


def handle_compact(payload: dict, project_dir: Path, journal: Path) -> None:
    trigger = payload.get("trigger", "")  # manual | auto
    _append(journal, f"- {_now()} · context compacted ({trigger or 'auto'})\n")


def main() -> int:
    try:
        raw = sys.stdin.read() if not sys.stdin.isatty() else ""
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        payload = {}

    args = sys.argv[1:]
    global_mode = "--global" in args
    mode = next((a for a in args if a != "--global"), "")
    event = payload.get("hook_event_name", "")

    try:
        project_dir = _project_dir(payload)
        journal = _journal_path(project_dir, global_mode)
        if mode == "--session-start" or event == "SessionStart":
            handle_session_start(payload, project_dir, journal)
        elif mode == "--compact" or event == "PreCompact":
            handle_compact(payload, project_dir, journal)
        else:
            handle_tool_event(payload, project_dir, journal)
    except Exception:
        # Never block the triggering tool call.
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
