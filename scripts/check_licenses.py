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
and points at the skill. Removing identifiers never fails the gate (shrinking
surface is safe); refresh the baseline together with the next full record.

Usage:
    python3 scripts/check_licenses.py [--sbom sbom.cdx.json] [--update]

``--update`` rewrites the baseline from the current SBOM (do this only in the
same change that commits a fresh full license-check record).

Exit codes: 0 = clean, 1 = unadjudicated license identifiers found,
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
    parser.add_argument(
        "--update",
        action="store_true",
        help="Rewrite the baseline from the current SBOM.",
    )
    args = parser.parse_args(argv)

    if not args.sbom.exists():
        sys.stderr.write(
            f"license gate: SBOM {args.sbom} missing — run `task license:sbom` first.\n"
        )
        return 2
    current = sbom_license_ids(args.sbom)

    if args.update:
        args.baseline.parent.mkdir(parents=True, exist_ok=True)
        args.baseline.write_text(
            json.dumps(
                {
                    "_comment": (
                        "License identifiers adjudicated by the latest full "
                        "license-check record in this directory; consumed by "
                        "scripts/check_licenses.py. Refresh only together with "
                        "a fresh record (--update)."
                    ),
                    "adjudicated": sorted(current),
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"license gate: baseline rewritten with {len(current)} identifiers")
        return 0

    if not args.baseline.exists():
        sys.stderr.write(
            f"license gate: baseline {args.baseline} missing — run a full "
            "license-check (the license-check skill) and commit the baseline "
            "via --update alongside its record.\n"
        )
        return 2
    adjudicated = set(json.loads(args.baseline.read_text(encoding="utf-8"))["adjudicated"])

    new = sorted(current - adjudicated)
    if new:
        sys.stderr.write(
            "license gate: unadjudicated license identifier(s) introduced:\n"
        )
        for ident in new:
            sys.stderr.write(f"  - {ident}\n")
        sys.stderr.write(
            "Run the full license-check skill, record the verdict under "
            ".audits/license-check/, and refresh the baseline (--update) in "
            "the same change.\n"
        )
        return 1

    print(
        f"license gate: {len(current)} identifier(s) in the SBOM, all covered "
        f"by the adjudicated baseline ({len(adjudicated)})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
