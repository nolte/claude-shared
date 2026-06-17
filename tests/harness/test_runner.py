"""Unit tests for the pure (token-free) parts of the headless runner."""
from __future__ import annotations

import pytest

from evals.harness import runner


def test_build_cli_command_shape():
    cmd = runner.build_cli_command(
        "/nolte-shared:readme-structure-apply audit",
        "/repo",
        allowed_tools=("Read", "Glob", "Grep"),
        permission_mode="plan",
        model="claude-sonnet-4-6",
    )
    assert cmd[0:3] == ["claude", "-p", "/nolte-shared:readme-structure-apply audit"]
    assert "--plugin-dir" in cmd and cmd[cmd.index("--plugin-dir") + 1] == "/repo"
    assert cmd[cmd.index("--allowedTools") + 1] == "Read,Glob,Grep"
    assert cmd[cmd.index("--permission-mode") + 1] == "plan"
    assert cmd[cmd.index("--model") + 1] == "claude-sonnet-4-6"
    assert cmd[cmd.index("--output-format") + 1] == "json"


def test_build_cli_command_defaults_model_from_env(monkeypatch):
    monkeypatch.setenv("EVAL_MODEL", "claude-opus-4-7")
    cmd = runner.build_cli_command(
        "x", "/repo", allowed_tools=("Read",), permission_mode="plan"
    )
    assert cmd[cmd.index("--model") + 1] == "claude-opus-4-7"


def test_skill_prompt():
    assert (
        runner.skill_prompt("nolte-shared:readme-structure-apply", "audit")
        == "/nolte-shared:readme-structure-apply audit"
    )
    assert runner.skill_prompt("nolte-shared:spec") == "/nolte-shared:spec"


def test_agent_prompt_names_agent_and_forbids_self_doing():
    p = runner.agent_prompt("spec-readiness-reviewer", "audit spec/project/quality-gate.")
    assert "spec-readiness-reviewer agent" in p
    assert "do not perform the task yourself" in p.lower()


def test_parse_json_result_ok():
    assert runner.parse_json_result('{"result": "hello", "total_cost_usd": 0.01}') == "hello"


def test_parse_json_result_missing_field():
    with pytest.raises(ValueError, match="no 'result' field"):
        runner.parse_json_result('{"session_id": "abc"}')


def test_parse_json_result_bad_json():
    with pytest.raises(ValueError, match="could not parse"):
        runner.parse_json_result("not json")


def test_parse_cost():
    assert runner.parse_cost('{"result": "x", "total_cost_usd": 0.42}') == 0.42
    assert runner.parse_cost("garbage") is None


def test_run_headless_is_gated(monkeypatch):
    monkeypatch.delenv("RUN_EVALS", raising=False)
    with pytest.raises(RuntimeError, match="RUN_EVALS=1"):
        runner.run_headless("x", "/repo")


def test_multiturn_stub_raises():
    with pytest.raises(NotImplementedError, match="Claude Agent SDK"):
        runner.run_skill_multiturn()
