"""Deterministic sample aggregation and scorecard I/O. No LLM calls, no I/O cost.

A *sample* is one headless run of a scenario, reduced to a mapping of assertion name
to a boolean pass/fail. Aggregating N samples yields a `ScenarioResult` carrying the
per-assertion pass-rate and the scenario pass-rate (a sample passes only when *every*
assertion passes). A `Scorecard` bundles scenario results plus the run's model and
timestamp, and serialises to a stable JSON shape that `compare` diffs across runs.
"""
from __future__ import annotations

import datetime
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

SCHEMA_VERSION = 1


@dataclass(frozen=True)
class AssertionResult:
    name: str
    pass_count: int
    n_samples: int

    @property
    def pass_rate(self) -> float:
        return self.pass_count / self.n_samples if self.n_samples else 0.0


@dataclass(frozen=True)
class ScenarioResult:
    id: str
    n_samples: int
    pass_count: int  # samples in which *every* assertion passed
    assertions: tuple[AssertionResult, ...]

    @property
    def pass_rate(self) -> float:
        return self.pass_count / self.n_samples if self.n_samples else 0.0


def aggregate_samples(
    scenario_id: str, samples: Sequence[Mapping[str, bool]]
) -> ScenarioResult:
    """Reduce per-sample assertion booleans into a `ScenarioResult`.

    `samples` is one mapping per run, e.g. ``[{"contains:## Critical": True,
    "judge:rubric": False}, ...]``. Every sample must carry the same assertion names,
    so the aggregate is well-defined; an empty sample list is a programming error.
    """
    if not samples:
        raise ValueError(f"scenario {scenario_id!r}: need at least one sample")

    names = tuple(samples[0].keys())
    name_set = set(names)
    for i, sample in enumerate(samples):
        if set(sample.keys()) != name_set:
            raise ValueError(
                f"scenario {scenario_id!r}: sample {i} has assertion names "
                f"{sorted(sample.keys())}, expected {sorted(names)}"
            )

    n = len(samples)
    assertions = tuple(
        AssertionResult(
            name=name,
            pass_count=sum(1 for s in samples if s[name]),
            n_samples=n,
        )
        for name in names
    )
    pass_count = sum(1 for s in samples if all(s.values()))
    return ScenarioResult(
        id=scenario_id, n_samples=n, pass_count=pass_count, assertions=assertions
    )


@dataclass(frozen=True)
class Scorecard:
    scenarios: tuple[ScenarioResult, ...]
    model: str
    generated: str
    schema_version: int = SCHEMA_VERSION

    @classmethod
    def build(
        cls, scenarios: Sequence[ScenarioResult], model: str, generated: str | None = None
    ) -> "Scorecard":
        ts = generated or datetime.datetime.now(datetime.timezone.utc).isoformat(
            timespec="seconds"
        )
        return cls(scenarios=tuple(scenarios), model=model, generated=ts)

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "generated": self.generated,
            "model": self.model,
            "scenarios": [
                {
                    "id": s.id,
                    "n_samples": s.n_samples,
                    "pass_count": s.pass_count,
                    "pass_rate": round(s.pass_rate, 4),
                    "assertions": [
                        {
                            "name": a.name,
                            "pass_count": a.pass_count,
                            "n_samples": a.n_samples,
                            "pass_rate": round(a.pass_rate, 4),
                        }
                        for a in s.assertions
                    ],
                }
                for s in self.scenarios
            ],
        }

    @classmethod
    def from_dict(cls, data: Mapping) -> "Scorecard":
        version = data.get("schema_version")
        if version != SCHEMA_VERSION:
            raise ValueError(
                f"unsupported scorecard schema_version {version!r} "
                f"(this harness writes v{SCHEMA_VERSION})"
            )
        scenarios = tuple(
            ScenarioResult(
                id=s["id"],
                n_samples=s["n_samples"],
                pass_count=s["pass_count"],
                assertions=tuple(
                    AssertionResult(
                        name=a["name"], pass_count=a["pass_count"], n_samples=a["n_samples"]
                    )
                    for a in s["assertions"]
                ),
            )
            for s in data["scenarios"]
        )
        return cls(scenarios=scenarios, model=data["model"], generated=data["generated"])

    def write(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8")

    @classmethod
    def read(cls, path: str | Path) -> "Scorecard":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))
