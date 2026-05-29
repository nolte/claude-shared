"""Unit tests for the pure (token-free) parts of the LLM-as-judge helper."""
from __future__ import annotations

import pytest

from evals.harness import judge


def test_build_judge_prompt_embeds_rubric_and_output():
    p = judge.build_judge_prompt(output="the report", rubric="must mention X")
    assert "must mention X" in p
    assert "the report" in p
    assert "PASS or FAIL" in p


def test_build_judge_command_uses_claude_p_without_plugin_or_tools():
    cmd = judge.build_judge_command("grade this", model="claude-sonnet-4-6")
    assert cmd[0:3] == ["claude", "-p", "grade this"]
    assert cmd[cmd.index("--model") + 1] == "claude-sonnet-4-6"
    assert cmd[cmd.index("--permission-mode") + 1] == "plan"
    assert cmd[cmd.index("--output-format") + 1] == "json"
    # the judge only reasons over given text — no plugin, no tool access
    assert "--plugin-dir" not in cmd
    assert "--allowedTools" not in cmd


def test_parse_verdict_pass_fail():
    assert judge.parse_verdict("reasoning here\nPASS") is True
    assert judge.parse_verdict("reasoning here\nFAIL") is False


def test_parse_verdict_tolerates_decoration():
    assert judge.parse_verdict("ok\n**PASS**") is True
    assert judge.parse_verdict("nope\nfail.") is False
    assert judge.parse_verdict("verdict:\n`PASS`") is True


def test_parse_verdict_rejects_ambiguous():
    with pytest.raises(ValueError, match="PASS/FAIL"):
        judge.parse_verdict("I think it is mostly fine")


def test_parse_verdict_rejects_empty():
    with pytest.raises(ValueError, match="empty"):
        judge.parse_verdict("   \n  ")


def test_judge_is_gated(monkeypatch):
    monkeypatch.delenv("RUN_EVALS", raising=False)
    with pytest.raises(RuntimeError, match="RUN_EVALS=1"):
        judge.judge("out", "rubric")
