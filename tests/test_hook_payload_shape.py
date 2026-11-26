"""Hook payload shape: a non-object payload takes the hook's fail-open path (#816).

Each hook below reads its event as JSON from stdin and documents a fail-open
contract: a payload it can't use returns the quiet "allow" exit (0) instead of
a traceback. Invalid JSON already does; valid JSON of another shape (`1`, a
list, `null`, a non-object `tool_input`) must do the same.

- scripts/guard_feature_branch_hook.py: PreToolUse, exit 0 allow / 2 block.
- scripts/validate_edited_artifact.py: PostToolUse, exit 0 allow / 2 surface.
- scripts/wip_journal.py: SessionStart/PostToolUse/PreCompact, always exit 0.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"

NON_OBJECT = ["1", "[]", '"x"', "null", "[{\"tool_name\": \"Bash\"}]"]


def _run(script: str, payload: str, tmp_path: Path, *args: str) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k != "CI"}  # the branch guard no-ops under CI
    env["CLAUDE_PROJECT_DIR"] = str(tmp_path)
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        input=payload, capture_output=True, text=True, timeout=60, cwd=tmp_path, env=env,
    )


@pytest.mark.parametrize("payload", NON_OBJECT + [
    json.dumps({"tool_name": "Bash", "tool_input": "git checkout feat/x"}),
    json.dumps({"tool_name": "Bash", "tool_input": ["git checkout feat/x"]}),
    json.dumps({"tool_name": "Bash", "tool_input": {"command": 5}}),
    json.dumps({"tool_name": "Bash", "tool_input": {"command": ["git", "checkout", "feat/x"]}}),
])
def test_branch_guard_fails_open_on_a_non_object_payload(tmp_path, payload):
    result = _run("guard_feature_branch_hook.py", payload, tmp_path)
    assert (result.returncode, "Traceback" in result.stderr) == (0, False), result.stderr


@pytest.mark.parametrize("payload", NON_OBJECT + [
    json.dumps({"tool_name": "Edit", "tool_input": "skills/x/SKILL.md"}),
    json.dumps({"tool_name": "Edit", "tool_input": ["skills/x/SKILL.md"]}),
    json.dumps({"tool_name": "Edit", "tool_input": {"file_path": 5}}),
    json.dumps({"tool_name": "Edit", "tool_input": {"file_path": ["skills/x/SKILL.md"]}}),
])
def test_edit_validator_fails_open_on_a_non_object_payload(tmp_path, payload):
    result = _run("validate_edited_artifact.py", payload, tmp_path)
    assert (result.returncode, "Traceback" in result.stderr) == (0, False), result.stderr


@pytest.mark.parametrize("payload", NON_OBJECT)
@pytest.mark.parametrize("mode", [(), ("--session-start",), ("--compact",)])
def test_journal_fails_open_on_a_non_object_payload(tmp_path, payload, mode):
    result = _run("wip_journal.py", payload, tmp_path, *mode)
    assert (result.returncode, "Traceback" in result.stderr) == (0, False), result.stderr


def test_journal_still_records_a_session_start_on_a_non_object_payload(tmp_path):
    """Same as invalid JSON: the payload is treated as empty, the entry still lands."""
    assert _run("wip_journal.py", "1", tmp_path, "--session-start").returncode == 0
    journal = tmp_path / ".resume" / "session-journal.md"
    assert journal.is_file() and "## Session" in journal.read_text(encoding="utf-8")


def test_branch_guard_still_blocks_a_well_formed_switch_in_a_primary_checkout(tmp_path):
    """Refutation control: the shape checks don't open the guard for a real payload."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, timeout=60)
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": "git checkout feat/x"}})
    result = _run("guard_feature_branch_hook.py", payload, tmp_path)
    assert result.returncode == 2, result.stderr
