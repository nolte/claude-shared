"""Tests for scripts/resume_sessions.py's transcript reader (#816).

`first_user_prompt` is lenient by design: a line it can't use is skipped. A
line that is valid JSON but not an object (or whose `message` isn't one) must
be skipped the same way as an undecodable one, not abort the scan and hide a
later prompt behind "(no readable prompt)".
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("resume_sessions", ROOT / "scripts" / "resume_sessions.py")
rs = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = rs
assert _spec.loader is not None
_spec.loader.exec_module(rs)

PROMPT = json.dumps({"type": "user", "message": {"content": "fix the flaky test"}})


@pytest.mark.parametrize("noise", [
    "{not json",
    "1",
    '"a string"',
    "[1, 2]",
    "null",
    json.dumps({"type": "user", "message": "not an object"}),
    json.dumps({"type": "user", "message": ["not", "an", "object"]}),
])
def test_unusable_line_is_skipped_and_a_later_prompt_still_found(tmp_path, noise):
    transcript = tmp_path / "s.jsonl"
    transcript.write_text(f"{noise}\n{PROMPT}\n", encoding="utf-8")
    assert rs.first_user_prompt(transcript) == "fix the flaky test"
