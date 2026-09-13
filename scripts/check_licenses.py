#!/usr/bin/env python3
"""License-drift gate over the CycloneDX SBOM.

Implements the continuous-CI slice of ``spec/project/license-check`` §Triggers,
cadence, and CI: on changes touching a dependency manifest, a lockfile, the
``LICENSE`` file, or committed AI-generated artifacts, the license inventory is
re-derived and compared against the **adjudicated baseline** — the set of
license identifiers the latest full license-check run (the LLM-driven
``license-check`` skill, persisted under ``.audits/license-check/``) already
classified through the allow/review/deny policy.

The gate is deliberately a *drift detector*, not a re-classifier: SPDX
classification, policy tiers, and exception handling stay with the skill and
its record. A license identifier that the baseline doesn't carry means the
change introduced an obligation nobody has adjudicated yet — the gate fails
and points at the skill.

The baseline is a guard allowlist, so it follows spec/project/defect-class-guards/
G4: every identifier carries the reason it is allowed, and an identifier the SBOM
no longer contains is stale and fails the gate, because a reason that outlives
its component would silently excuse the next one (#591). `--prune` removes stale
entries; `--update` adds new identifiers with an empty reason, which fails until
someone writes the reason from the fresh record.

Guard origin (spec/project/defect-class-guards/ G5): #496, staleness and reasons #591.

Usage:
    python3 scripts/check_licenses.py [--sbom sbom.cdx.json] [--update | --prune]

``--update`` rewrites the baseline from the current SBOM (do this only in the
same change that commits a fresh full license-check record).

Exit codes: 0 = clean, 1 = unadjudicated, stale, or reasonless identifiers,
2 = SBOM or baseline missing/unreadable.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BASELINE = REPO_ROOT / ".audits" / "license-check" / "license-baseline.json"


def sbom_license_ids(sbom_path: Path) -> set[str]:
    doc = json.loads(sbom_path.read_text(encoding="utf-8"))
    ids: set[str] = set()
    for component in doc.get("components", []):
        licenses = component.get("licenses") or []
        if not licenses:
            ids.add("NOASSERTION")
            continue
        for entry in licenses:
            lic = entry.get("license") or {}
            expression = entry.get("expression")
            ids.add(expression or lic.get("id") or lic.get("name") or "NOASSERTION")
    return ids


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sbom", type=Path, default=REPO_ROOT / "sbom.cdx.json")
    parser.add_argument("--baseline", type=Path, default=BASELINE)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--update",
        action="store_true",
        help="Rewrite the baseline from the current SBOM, keeping existing reasons.",
    )
    mode.add_argument(
        "--prune",
        action="store_true",
        help="Remove baseline entries the current SBOM no longer contains.",
    )
    args = parser.parse_args(argv)

    if not args.sbom.exists():
        sys.stderr.write(
            f"license gate: SBOM {args.sbom} missing — run `task license:sbom` first.\n"
        )
        return 2
    current = sbom_license_ids(args.sbom)

    if args.update:
        previous = _load_baseline(args.baseline) if args.baseline.exists() else {}
        _write_baseline(args.baseline, {ident: previous.get(ident, "") for ident in current})
        print(f"license gate: baseline rewritten with {len(current)} identifiers; "
              "write a reason for every empty entry")
        return 0

    if not args.baseline.exists():
        sys.stderr.write(
            f"license gate: baseline {args.baseline} missing — run a full "
            "license-check (the license-check skill) and commit the baseline "
            "via --update alongside its record.\n"
        )
        return 2
    adjudicated = _load_baseline(args.baseline)

    if args.prune:
        kept = {ident: reason for ident, reason in adjudicated.items() if ident in current}
        _write_baseline(args.baseline, kept)
        print(f"license gate: pruned {len(adjudicated) - len(kept)} stale identifier(s)")
        return 0

    failures = []
    for ident in sorted(current - set(adjudicated)):
        failures.append(f"  - unadjudicated: {ident}")
    for ident in sorted(set(adjudicated) - current):
        failures.append(f"  - stale (no longer in the SBOM): {ident}")
    for ident, reason in sorted(adjudicated.items()):
        if ident in current and not str(reason).strip():
            failures.append(f"  - no reason recorded: {ident}")
    if failures:
        sys.stderr.write("license gate: the adjudicated baseline doesn't match the SBOM:\n")
        sys.stderr.write("\n".join(failures) + "\n")
        sys.stderr.write(
            "Run the full license-check skill for new identifiers and record the verdict "
            "under .audits/license-check/, --prune stale ones, and give every entry a reason.\n"
        )
        return 1

    print(
        f"license gate: {len(current)} identifier(s) in the SBOM, all covered "
        f"by the adjudicated baseline, each with a reason"
    )
    return 0


def _load_baseline(path: Path) -> dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))["adjudicated"]
    if not isinstance(data, dict):
        raise SystemExit(f"license gate: {path} must map each identifier to its reason")
    return data


def _write_baseline(path: Path, entries: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = {"_comment": json.loads(path.read_text(encoding="utf-8"))["_comment"]} if path.exists() else {}
    doc["adjudicated"] = dict(sorted(entries.items()))
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
