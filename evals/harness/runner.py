"""Headless invocation of plugin skills and agents via `claude -p`.

Mechanics (per the Claude Code headless docs):
- ``claude -p "<prompt>" --output-format json`` prints one JSON object; its ``result``
  field is the final assistant text. Tool calls are NOT in the json output — only in
  ``--output-format stream-json``.
- ``--plugin-dir <repo>`` loads the local plugin's skills/agents into the run.
- A *skill* is triggered by passing its slash command as the prompt, e.g.
  ``/nolte-shared:readme-structure-apply audit``.
- An *agent* cannot be force-dispatched from the CLI; we instruct the top-level
  assistant to use it. Dispatch is therefore best-effort — acceptable for a read-only
  report agent because the graded artefact is the report text the run returns.
- Read-only runs use ``--permission-mode plan --allowedTools "Read,Glob,Grep"``.

Cost discipline: every function that actually spawns ``claude`` (or the API, in
``judge``) is gated behind ``RUN_EVALS=1``. The pure helpers below (command building,
result parsing, prompt shaping) take no cost and are unit-tested directly.

Not yet live-verified: multi-turn skills that pause for mid-flow approval need the
Claude Agent SDK (`ClaudeSDKClient`), whose local-plugin loading is under-documented.
`run_skill_multiturn` is a structured stub raising `NotImplementedError` until the SDK
path is verified live; the v1 anchors use read-only single-shot operations instead.
"""
from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass

DEFAULT_MODEL = "claude-sonnet-4-6"
READONLY_TOOLS = ("Read", "Glob", "Grep")


def evals_enabled() -> bool:
    return os.environ.get("RUN_EVALS") == "1"


def eval_model() -> str:
    return os.environ.get("EVAL_MODEL", DEFAULT_MODEL)


def skill_prompt(skill: str, args: str = "") -> str:
    """Slash-command prompt that triggers a named skill, e.g.
    ``skill_prompt("nolte-shared:readme-structure-apply", "audit")``."""
    return f"/{skill} {args}".strip()


def agent_prompt(agent_name: str, instruction: str) -> str:
    """Prompt that asks the top-level assistant to dispatch a specific agent."""
    return (
        f"Use the {agent_name} agent to {instruction} "
        f"Dispatch that agent; do not perform the task yourself."
    )


def build_cli_command(
    prompt: str,
    plugin_dir: str,
    *,
    allowed_tools: tuple[str, ...] | list[str],
    permission_mode: str,
    model: str | None = None,
    output_format: str = "json",
) -> list[str]:
    """Pure construction of the ``claude -p`` argv (no execution)."""
    return [
        "claude",
        "-p",
        prompt,
        "--plugin-dir",
        plugin_dir,
        "--permission-mode",
        permission_mode,
        "--allowedTools",
        ",".join(allowed_tools),
        "--model",
        model or eval_model(),
        "--output-format",
        output_format,
    ]


def parse_json_result(stdout: str) -> str:
    """Extract the final assistant text from ``--output-format json`` output."""
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise ValueError(f"could not parse claude json output: {exc}") from exc
    if "result" not in data:
        raise ValueError(f"claude json output has no 'result' field: keys={list(data)}")
    return data["result"]


def parse_cost(stdout: str) -> float | None:
    try:
        return json.loads(stdout).get("total_cost_usd")
    except json.JSONDecodeError:
        return None


@dataclass(frozen=True)
class RunResult:
    text: str
    returncode: int
    cost_usd: float | None
    raw_stdout: str


def run_headless(
    prompt: str,
    plugin_dir: str,
    *,
    allowed_tools: tuple[str, ...] | list[str] = READONLY_TOOLS,
    permission_mode: str = "plan",
    model: str | None = None,
    cwd: str | None = None,
    timeout: int = 600,
) -> RunResult:
    """Execute one headless ``claude -p`` run. Gated behind RUN_EVALS=1."""
    if not evals_enabled():
        raise RuntimeError("run_headless requires RUN_EVALS=1 (live LLM call has a cost)")
    cmd = build_cli_command(
        prompt,
        plugin_dir,
        allowed_tools=allowed_tools,
        permission_mode=permission_mode,
        model=model,
    )
    proc = subprocess.run(
        cmd, capture_output=True, text=True, cwd=cwd, timeout=timeout, check=False
    )
    return RunResult(
        text=parse_json_result(proc.stdout) if proc.stdout else "",
        returncode=proc.returncode,
        cost_usd=parse_cost(proc.stdout) if proc.stdout else None,
        raw_stdout=proc.stdout,
    )


def run_skill_multiturn(*args, **kwargs):  # pragma: no cover - stub for the SDK path
    raise NotImplementedError(
        "Multi-turn skills with mid-flow approval need the Claude Agent SDK "
        "(ClaudeSDKClient); its local-plugin loading is not yet live-verified. "
        "v1 anchors use read-only single-shot operations via run_headless."
    )
