"""Diff two scorecards (baseline vs change) to prove an edit's effect on behaviour.

This is the regression engine the harness exists for: run the suite on `develop`
(baseline), run it again on a branch that edits a skill/agent/spec (change), then diff.
A change is justified when targeted scenarios' pass-rate rises with no regression
elsewhere. `compare` exits non-zero when any scenario regresses beyond the tolerance,
so CI can gate on it.

CLI: ``python -m evals.harness.compare base.json head.json [--tolerance 0.0]``
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from evals.harness.scorecard import Scorecard


@dataclass(frozen=True)
class Row:
    scenario_id: str
    base_rate: float | None  # None => scenario absent from baseline (new)
    head_rate: float | None  # None => scenario absent from change (removed)

    @property
    def delta(self) -> float | None:
        if self.base_rate is None or self.head_rate is None:
            return None
        return self.head_rate - self.base_rate

    def status(self, tolerance: float) -> str:
        if self.base_rate is None:
            return "new"
        if self.head_rate is None:
            return "removed"
        d = self.head_rate - self.base_rate
        if d < -tolerance:
            return "regressed"
        if d > tolerance:
            return "improved"
        return "unchanged"


@dataclass(frozen=True)
class Diff:
    rows: tuple[Row, ...]
    tolerance: float

    @property
    def has_regression(self) -> bool:
        # A removed scenario is treated as a regression: coverage was lost.
        return any(r.status(self.tolerance) in ("regressed", "removed") for r in self.rows)


def diff_scorecards(base: Scorecard, head: Scorecard, tolerance: float = 0.0) -> Diff:
    base_rates = {s.id: s.pass_rate for s in base.scenarios}
    head_rates = {s.id: s.pass_rate for s in head.scenarios}
    ids = sorted(set(base_rates) | set(head_rates))
    rows = tuple(
        Row(scenario_id=i, base_rate=base_rates.get(i), head_rate=head_rates.get(i))
        for i in ids
    )
    return Diff(rows=rows, tolerance=tolerance)


def render(diff: Diff) -> str:
    def fmt(x: float | None) -> str:
        return "—" if x is None else f"{x:.0%}"

    lines = [
        f"{'scenario':<48} {'base':>6} {'head':>6} {'delta':>7}  status",
        "-" * 84,
    ]
    for r in diff.rows:
        d = r.delta
        delta = "—" if d is None else f"{d:+.0%}"
        lines.append(
            f"{r.scenario_id:<48} {fmt(r.base_rate):>6} {fmt(r.head_rate):>6} "
            f"{delta:>7}  {r.status(diff.tolerance)}"
        )
    lines.append("-" * 84)
    lines.append(
        "regression detected" if diff.has_regression else "no regression "
        f"(tolerance {diff.tolerance:.0%})"
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base", type=Path, help="baseline scorecard.json")
    parser.add_argument("head", type=Path, help="change scorecard.json")
    parser.add_argument(
        "--tolerance",
        type=float,
        default=0.0,
        help="allowed pass-rate drop before a scenario counts as regressed (0.0–1.0)",
    )
    args = parser.parse_args(argv)

    diff = diff_scorecards(
        Scorecard.read(args.base), Scorecard.read(args.head), tolerance=args.tolerance
    )
    print(render(diff))
    return 1 if diff.has_regression else 0


if __name__ == "__main__":
    sys.exit(main())
