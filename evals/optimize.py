"""Local iterative optimiser: improve a target skill/agent/spec against the eval suite.

Closed loop (per the operator's design):

    baseline = score_target(scenario)         # continuous, in [0, 1]
    repeat up to --max-iters:
        1. report agent   (claude -p, read-only): diagnose why the suite underperforms
        2. optimiser agent (claude -p, edits an ISOLATED COPY of the target only)
        3. log the diff (current -> candidate) for full transparency
        4. re-score the suite
        5. accept iff the score strictly improved; otherwise revert and retry
    stop early once score >= --quality

Design notes (informed by the first live run, which plateaued on a 33%-resolution rauschen
floor with a binary judge and N=3):

  * The score is **continuous** in [0, 1]. The scenario module's per-assertion booleans
    land as 0.0/1.0; the LLM judge contributes its own continuous score (0.00–1.00). The
    mean over assertions and samples gives a real gradient to climb.
  * Each iteration logs the **unified diff** of the optimiser's edit. If the optimiser
    didn't actually change the file, we see "(no changes)" rather than guessing why the
    score didn't move.
  * The optimiser edits an isolated copy in a temp dir; the orchestrator alone writes the
    result back. No way to touch the eval scenarios, fixtures, or harness.
  * Nothing is committed. The target is left edited-but-uncommitted in the worktree;
    `git checkout -- <target>` restores the original.
  * main() refuses to run without RUN_EVALS=1.

Run (the degrade-and-recover demo):

    RUN_EVALS=1 .venv/bin/python -m evals.optimize \\
        --target agents/spec-readiness-reviewer.md \\
        --scenario-module tests.e2e.spec_readiness_reviewer.scenario \\
        --desc "Audit a spec for readiness; flag the planted MUST-vs-MUST-NOT caching \\
                contradiction as Critical and the orphan AC as Warning." \\
        --max-iters 5 --samples 5 --quality 0.9 --model sonnet
"""
from __future__ import annotations

import argparse
import difflib
import importlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from statistics import mean

from evals.harness.runner import parse_json_result

REPO_ROOT = Path(__file__).resolve().parents[1]


# --------------------------------------------------------------------------- pure logic
def decide(best: float, candidate: float) -> str:
    """Hill-climb: keep a candidate only when it strictly beats the best score so far."""
    return "accept" if candidate > best else "revert"


def should_stop(score: float, quality: float) -> bool:
    return score >= quality


# ------------------------------------------------------------------------------- scoring
def score_target(scenario_module, plugin_dir: str, fixture_dir: Path, *,
                 samples: int, model: str) -> tuple[float, list[dict]]:
    """Drive `samples` live runs and return (continuous mean score in [0, 1], raw samples)."""
    raw = [scenario_module.run_one_sample(plugin_dir, fixture_dir, model=model)
           for _ in range(samples)]
    scenario_scores = [scenario_module.continuous_score(s) for s in raw]
    return mean(scenario_scores) if scenario_scores else 0.0, raw


# -------------------------------------------------------------------------------- agents
def _claude(prompt: str, *, allowed_tools, permission_mode: str, model: str,
            cwd: str | None = None, timeout: int = 900) -> str:
    cmd = [
        "claude", "-p", prompt,
        "--model", model,
        "--permission-mode", permission_mode,
        "--allowedTools", ",".join(allowed_tools),
        "--output-format", "json",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=timeout, check=False)
    return parse_json_result(proc.stdout) if proc.stdout else ""


def run_report_agent(target_text: str, scenario_desc: str,
                     last_samples: list[dict], model: str) -> str:
    sample_lines = "\n".join(f"  sample {i + 1}: {s}" for i, s in enumerate(last_samples))
    prompt = (
        "You are an eval-report analyst. Given a scenario's intent, the last N sample "
        "scores (per-assertion, in [0, 1] where 1.0 = met), and the artifact under test, "
        "write a concise, actionable diagnosis of WHY the suite underperforms and WHAT is "
        "missing, weak, or misleading in the artifact. Be specific: when relevant, quote "
        "text from the artifact. Do not rewrite the artifact; only diagnose.\n\n"
        f"SCENARIO INTENT:\n{scenario_desc}\n\n"
        f"LAST SAMPLE SCORES (judge:rubric is continuous; the rest are 0/1):\n{sample_lines}\n\n"
        f"ARTIFACT UNDER TEST:\n<<<\n{target_text}\n>>>"
    )
    return _claude(prompt, allowed_tools=(), permission_mode="plan", model=model)


def run_optimizer_agent(target_copy: Path, report: str, model: str) -> None:
    prompt = (
        f"You improve a single artifact file named `{target_copy.name}` in the current "
        "directory. Read it, then apply a FOCUSED edit that addresses the diagnosis below. "
        f"Edit ONLY `{target_copy.name}`. Preserve the file's existing format, structure, "
        "and conventions. Do not add unrelated content. If the diagnosis identifies a "
        "misleading or contradictory directive inside the file, REMOVE or NEUTRALISE it.\n\n"
        f"DIAGNOSIS:\n{report}"
    )
    _claude(
        prompt,
        allowed_tools=("Read", "Edit", "Write"),
        permission_mode="acceptEdits",
        model=model,
        cwd=str(target_copy.parent),
    )


def _diff(before: str, after: str, label: str) -> str:
    lines = list(difflib.unified_diff(
        before.splitlines(keepends=True),
        after.splitlines(keepends=True),
        fromfile=f"{label}/before",
        tofile=f"{label}/after",
    ))
    return "".join(lines) if lines else "(no changes)\n"


# ---------------------------------------------------------------------------------- loop
def optimize(target_rel: str, scenario_module_path: str, scenario_desc: str, *,
             max_iters: int, quality: float, samples: int, model: str) -> list[tuple[str, float]]:
    scenario_module = importlib.import_module(scenario_module_path)
    target = REPO_ROOT / target_rel
    best_text = target.read_text()

    # Fixture is read-only across samples for this kind of scenario; prepare once.
    with tempfile.TemporaryDirectory() as fixture_root:
        fixture_dir = scenario_module.prepare_fixture(Path(fixture_root))

        best_score, last_samples = score_target(
            scenario_module, str(REPO_ROOT), fixture_dir, samples=samples, model=model
        )
        history: list[tuple[str, float]] = [("baseline", best_score)]
        print(f"[optimise] baseline score = {best_score:.3f}", flush=True)
        print(f"[optimise] baseline samples = {last_samples}", flush=True)

        if should_stop(best_score, quality):
            print(f"[optimise] baseline already meets quality {quality:.2f}; nothing to do.", flush=True)
            return history

        for i in range(1, max_iters + 1):
            print(f"[optimise] --- iter {i} ---", flush=True)
            current_text = target.read_text()
            report = run_report_agent(current_text, scenario_desc, last_samples, model)
            print(f"[optimise] iter {i} REPORT (truncated to 800 chars):\n{report[:800]}", flush=True)

            with tempfile.TemporaryDirectory() as td:
                copy = Path(td) / target.name
                copy.write_text(current_text)
                run_optimizer_agent(copy, report, model)
                candidate_text = copy.read_text()

            diff_text = _diff(current_text, candidate_text, label=f"iter{i}")
            print(f"[optimise] iter {i} DIFF (current -> candidate):\n{diff_text}", flush=True)

            target.write_text(candidate_text)
            candidate_score, last_samples = score_target(
                scenario_module, str(REPO_ROOT), fixture_dir, samples=samples, model=model
            )
            verdict = decide(best_score, candidate_score)
            print(f"[optimise] iter {i}: score = {candidate_score:.3f} -> {verdict}", flush=True)
            print(f"[optimise] iter {i} samples = {last_samples}", flush=True)

            if verdict == "accept":
                best_score, best_text = candidate_score, candidate_text
                history.append((f"iter{i}-accept", candidate_score))
                if should_stop(best_score, quality):
                    print(f"[optimise] reached quality {quality:.2f} at iter {i}; early exit.", flush=True)
                    break
            else:
                target.write_text(best_text)
                history.append((f"iter{i}-revert", candidate_score))

        target.write_text(best_text)
        print(f"[optimise] done. best score = {best_score:.3f}", flush=True)
        print(f"[optimise] history = {history}", flush=True)
        print(f"[optimise] target left edited-but-uncommitted: {target_rel}", flush=True)
        print(f"[optimise] restore the original with: git checkout -- {target_rel}", flush=True)
        return history


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--target", required=True, help="repo-relative path of the artifact to optimise")
    parser.add_argument(
        "--scenario-module", required=True,
        help="dotted Python module path; must expose prepare_fixture, run_one_sample, continuous_score",
    )
    parser.add_argument("--desc", required=True, help="one-paragraph scenario intent for the report agent")
    parser.add_argument("--max-iters", type=int, default=5)
    parser.add_argument("--quality", type=float, default=0.9,
                        help="early-exit continuous score threshold (0..1)")
    parser.add_argument("--samples", type=int, default=5)
    parser.add_argument("--model", default="sonnet")
    args = parser.parse_args(argv)

    if os.environ.get("RUN_EVALS") != "1":
        print("optimise requires RUN_EVALS=1 (every iteration spends live calls).", file=sys.stderr)
        return 2

    optimize(
        args.target, args.scenario_module, args.desc,
        max_iters=args.max_iters, quality=args.quality, samples=args.samples, model=args.model,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
