"""LLM-as-judge: grade a run's output against a rubric derived from a spec's ACs.

The rubric text is the fuzzy half of an assertion (the deterministic half is plain
string/structure checks in the scenario test). The judge is told to answer with a single
final ``PASS`` or ``FAIL`` line so the verdict parses unambiguously; a malformed verdict
raises rather than silently passing.

Cost discipline: `judge` calls the Anthropic API and is gated behind RUN_EVALS=1. The
prompt builder and verdict parser are pure and unit-tested directly.
"""
from __future__ import annotations

import os

DEFAULT_JUDGE_MODEL = "claude-sonnet-4-6"

_TEMPLATE = """\
You are a strict evaluator. Judge whether the OUTPUT satisfies every item in the RUBRIC.
Be literal: if any rubric item is unmet, the verdict is FAIL.

RUBRIC:
{rubric}

OUTPUT:
<<<
{output}
>>>

Explain briefly, then on the FINAL line write exactly one word: PASS or FAIL."""


def judge_model() -> str:
    return os.environ.get("EVAL_JUDGE_MODEL", DEFAULT_JUDGE_MODEL)


def build_judge_prompt(output: str, rubric: str) -> str:
    return _TEMPLATE.format(rubric=rubric.strip(), output=output.strip())


def parse_verdict(text: str) -> bool:
    """Return True for a PASS verdict. Raise on a missing/ambiguous verdict."""
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    if not lines:
        raise ValueError("empty judge response")
    last = lines[-1].upper().strip(".:*` ")
    if last == "PASS":
        return True
    if last == "FAIL":
        return False
    raise ValueError(f"judge response did not end with PASS/FAIL: {lines[-1]!r}")


def judge(output: str, rubric: str, model: str | None = None) -> bool:
    """Grade `output` against `rubric` via the Anthropic API. Gated behind RUN_EVALS=1."""
    if os.environ.get("RUN_EVALS") != "1":
        raise RuntimeError("judge requires RUN_EVALS=1 (live LLM call has a cost)")
    import anthropic  # lazy: only needed for live runs

    client = anthropic.Anthropic()
    message = client.messages.create(
        model=model or judge_model(),
        max_tokens=1024,
        messages=[{"role": "user", "content": build_judge_prompt(output, rubric)}],
    )
    text = "".join(block.text for block in message.content if block.type == "text")
    return parse_verdict(text)
