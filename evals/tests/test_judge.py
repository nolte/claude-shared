"""Unit tests for the pure (token-free) parts of the LLM-as-judge helper."""
from __future__ import annotations

import pytest

from evals.harness import judge


def test_build_judge_prompt_embeds_rubric_and_output():
    p = judge.build_judge_prompt(output="the report", rubric="must mention X")
    assert "must mention X" in p
    assert "the report" in p
    # the new template asks for a numeric score on the final line
    assert "0.00 to 1.00" in p


def test_build_judge_command_uses_claude_p_without_plugin_or_tools():
    cmd = judge.build_judge_command("grade this", model="claude-sonnet-4-6")
    assert cmd[0:3] == ["claude", "-p", "grade this"]
    assert cmd[cmd.index("--model") + 1] == "claude-sonnet-4-6"
    assert cmd[cmd.index("--permission-mode") + 1] == "plan"
    assert cmd[cmd.index("--output-format") + 1] == "json"
    assert "--plugin-dir" not in cmd
    assert "--allowedTools" not in cmd


def test_parse_score_simple():
    assert judge.parse_score("Item 1: ok\nItem 2: ok\n0.83") == pytest.approx(0.83)
    assert judge.parse_score("everything met\n1.0") == 1.0
    assert judge.parse_score("nothing met\n0") == 0.0


def test_parse_score_tolerates_decoration():
    assert judge.parse_score("ok\n**0.5**") == 0.5
    assert judge.parse_score("ok\n`0.42`") == pytest.approx(0.42)
    assert judge.parse_score("ok\n0.7.") == pytest.approx(0.7)


def test_parse_score_rejects_non_numeric():
    with pytest.raises(ValueError, match="numeric score"):
        judge.parse_score("ok\nGOOD ENOUGH")


def test_parse_score_rejects_out_of_range():
    with pytest.raises(ValueError, match=r"outside \[0, 1\]"):
        judge.parse_score("ok\n1.5")
    with pytest.raises(ValueError, match=r"outside \[0, 1\]"):
        judge.parse_score("ok\n-0.1")


def test_parse_score_rejects_empty():
    with pytest.raises(ValueError, match="empty"):
        judge.parse_score("   \n  ")


def test_judge_score_is_gated(monkeypatch):
    monkeypatch.delenv("RUN_EVALS", raising=False)
    with pytest.raises(RuntimeError, match="RUN_EVALS=1"):
        judge.judge_score("out", "rubric")


def test_judge_bool_wrapper_is_gated(monkeypatch):
    monkeypatch.delenv("RUN_EVALS", raising=False)
    with pytest.raises(RuntimeError, match="RUN_EVALS=1"):
        judge.judge("out", "rubric")
