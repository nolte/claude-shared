"""LLM-as-judge: grade a run's output against a rubric derived from a spec's ACs.

The judge returns a **continuous score in [0, 1]** so the optimiser has a real gradient
to climb (rather than the coarser pass/fail signal that resolves only to 0/1 per sample
and produced a 33%-resolution rauschen plateau in the first live run).

Cost discipline: `judge_score` drives the model through `claude -p` (the same auth as
the runner — your Claude Code login, no separate Anthropic API key), gated behind
RUN_EVALS=1. The prompt builder, command builder, and score parser are pure and
unit-tested directly. A thin `judge()` wrapper (score >= 0.5) keeps existing pass/fail
call-sites working.
"""
from __future__ import annotations

import os
import re

DEFAULT_JUDGE_MODEL = "claude-sonnet-4-6"

_TEMPLATE = """\
You are a strict evaluator. Score how well the OUTPUT satisfies the RUBRIC.

RUBRIC:
{rubric}

OUTPUT:
<<<
{output}
>>>

Score on a continuous scale from 0.00 to 1.00, where:
  - 1.00 means EVERY rubric item is fully met
  - 0.00 means NO rubric item is met
  - intermediate values reflect partial coverage (1 item satisfied out of N → ~ 1/N etc.)

Briefly justify per rubric item, then on the FINAL line write exactly the numeric score
(e.g. `0.83`) with no other characters."""

_NUMERIC = re.compile(r"-?\d+(?:\.\d+)?")


def judge_model() -> str:
    return os.environ.get("EVAL_JUDGE_MODEL", DEFAULT_JUDGE_MODEL)


def build_judge_prompt(output: str, rubric: str) -> str:
    return _TEMPLATE.format(rubric=rubric.strip(), output=output.strip())


def parse_score(text: str) -> float:
    """Extract a numeric score in [0, 1] from the judge's final line.

    Raise on a missing/non-numeric/out-of-range verdict — silent fallback to 0/1 would let
    the optimiser climb noise rather than signal.
    """
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    if not lines:
        raise ValueError("empty judge response")
    last = lines[-1].strip().strip("*`. ")
    match = _NUMERIC.search(last)
    if not match:
        raise ValueError(f"judge response did not end with a numeric score: {lines[-1]!r}")
    score = float(match.group(0))
    if not 0.0 <= score <= 1.0:
        raise ValueError(f"judge score {score} is outside [0, 1]")
    return score


def build_judge_command(prompt: str, model: str | None = None) -> list[str]:
    """Pure construction of the ``claude -p`` argv for a judge call (no plugin, no tools)."""
    return [
        "claude",
        "-p",
        prompt,
        "--model",
        model or judge_model(),
        "--permission-mode",
        "plan",
        "--output-format",
        "json",
    ]


def judge_score(output: str, rubric: str, model: str | None = None, timeout: int = 300) -> float:
    """Grade `output` against `rubric` via ``claude -p``; return a float in [0, 1].

    Uses the same auth as the runner — your Claude Code login (a Pro/Max subscription or
    an API key) — so no separate Anthropic API key or Console account is required.
    Gated behind RUN_EVALS=1.
    """
    if os.environ.get("RUN_EVALS") != "1":
        raise RuntimeError("judge_score requires RUN_EVALS=1 (live LLM call has a cost)")
    import subprocess

    from evals.harness.runner import parse_json_result

    cmd = build_judge_command(build_judge_prompt(output, rubric), model)
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
    return parse_score(parse_json_result(proc.stdout))


def judge(output: str, rubric: str, model: str | None = None, timeout: int = 300) -> bool:
    """Back-compat boolean wrapper: PASS iff the continuous score is at least 0.5."""
    return judge_score(output, rubric, model=model, timeout=timeout) >= 0.5
