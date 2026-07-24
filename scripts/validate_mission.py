#!/usr/bin/env python3
"""Lightweight `project/mission.md` frontmatter validator.

Implements the structural checks named in `spec/project/mission/` §"Frontmatter
schema", §"Body sections", §"SMART contract" (the individually-checkable
cross-references), and the acceptance criteria that say "lints flag unknown
keys" / "fails validation". This is the mission-side analogue of
`scripts/validate_skills.py` and `scripts/validate_features.py`; the spec carries
no explicit MUST for automated linting (the enforcement is SHOULD-class), so this
script turns those repeated "lints flag" phrasings into a real gate.

The mission file MAY be absent in a repository that hasn't adopted the planning
suite (per the spec §"Directory layout and file shape"); a missing file is a pass.

Exit codes:
  0  the mission passes (0 files = pass)
  1  at least one error (`Critical`-grade per `review-plan` §Severity scale)
  2  internal error (file unreadable, YAML unrecoverable, self-test failed, etc.)

Usage:
  python scripts/validate_mission.py                    # checks project/mission.md
  python scripts/validate_mission.py path/to/mission.md # checks one target
  python scripts/validate_mission.py --self-test        # run the negative-proof fixtures

Output is one finding per line, prefixed with severity in Title Case so
downstream tooling can grep deterministically.
"""
from __future__ import annotations

import datetime
import re
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - PyYAML is a pinned dev dependency
    yaml = None

REPO = Path(__file__).resolve().parent.parent
MISSION_PATH = REPO / "project" / "mission.md"
GOALS_PATH = REPO / "project" / "goals.md"
AUDIENCES_PATH = REPO / "AUDIENCES.md"
FEATURES_DIR = REPO / "project" / "features"

# Frontmatter schema per spec/project/mission/ §Frontmatter schema, in order.
SCHEMA_ORDER = [
    "mission_statement", "relevant_outcomes", "audiences", "verifies_via",
    "time_bound", "mvp_status", "created", "revised_at",
]
SCHEMA_KEYS = set(SCHEMA_ORDER)

# Required level-2 body sections per §Body sections, in declared order.
REQUIRED_SECTIONS = ["Statement", "Audiences", "Verification", "Source"]

MVP_STATUS_ENUM = {"defining", "in_progress", "achieved", "stabilised"}
OUTCOME_RE = re.compile(r"^O-\d+$")
VERIFIES_VIA_RE = re.compile(r"^(F-\d+):(acceptance-\d+)$")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _is_iso_date(value) -> bool:
    """Accept both a YAML-native date (`created: 2026-05-09` deserialises to a
    `datetime.date`) and an ISO-shaped string. A `datetime` also subclasses
    `date`, but the mission schema carries plain dates, so either is fine here."""
    if isinstance(value, datetime.date):
        return True
    return isinstance(value, str) and bool(ISO_DATE_RE.match(value))


@dataclass
class Finding:
    severity: str  # Critical | Warning | Suggestion | Info
    target: str
    rule: str
    message: str

    def __str__(self) -> str:
        return f"{self.severity:11s} {self.target}  [{self.rule}] {self.message}"


def _split(text: str) -> tuple[str, str] | None:
    """Return (frontmatter, body) or None when no `---` fence opens the file."""
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    return parts[1], parts[2]


def _top_level_keys(fm: str) -> list[str]:
    """Top-level frontmatter keys in document order (skip nested / list lines)."""
    keys: list[str] = []
    for line in fm.splitlines():
        if not line.strip() or line.startswith((" ", "\t", "-")):
            continue
        m = re.match(r"^([A-Za-z_][\w-]*):", line)
        if m:
            keys.append(m.group(1))
    return keys


def _outcome_ids(goals_text: str) -> set[str]:
    """Outcome IDs declared in project/goals.md as `- **O-<n>**` bullets."""
    return set(re.findall(r"^\s*-\s*\*\*(O-\d+)\*\*", goals_text, re.M))


def _audience_ids(audiences_text: str) -> set[str]:
    """Audience identifiers declared in AUDIENCES.md as `_id_: \\`<id>\\`` tokens."""
    return set(re.findall(r"_id_:\s*`([a-z0-9][a-z0-9-]*)`", audiences_text))


def _feature_index() -> dict[str, str | None]:
    """Map feature id (`F-<n>`) -> its `verifies_sprint_value` scalar (or None).

    Read from project/features/*.md frontmatter so `verifies_via` can be resolved
    to both an existing feature file and the acceptance identifier it names.
    """
    index: dict[str, str | None] = {}
    if not FEATURES_DIR.is_dir():
        return index
    for path in sorted(FEATURES_DIR.glob("*.md")):
        split = _split(path.read_text(encoding="utf-8"))
        if split is None:
            continue
        fm = split[0]
        fid = re.search(r"^id:\s*(\S+)\s*$", fm, re.M)
        if not fid:
            continue
        vsv = re.search(r"^verifies_sprint_value:\s*(\S+)\s*$", fm, re.M)
        index[fid.group(1)] = vsv.group(1) if vsv else None
    return index


def check_frontmatter_order_and_keys(fm: str, target: str) -> list[Finding]:
    findings: list[Finding] = []
    keys = _top_level_keys(fm)

    for key in SCHEMA_ORDER:
        if key not in keys:
            findings.append(Finding("Critical", target, "mission.frontmatter-missing-field",
                                    f"required frontmatter field `{key}` is missing"))

    unknown = [k for k in keys if k not in SCHEMA_KEYS]
    for k in unknown:
        findings.append(Finding("Critical", target, "mission.frontmatter-unknown-key",
                                f"unknown frontmatter key `{k}`; only the eight schema fields "
                                f"are allowed (spec §Frontmatter schema rejects unknown keys)"))

    present = [k for k in keys if k in SCHEMA_KEYS]
    expected_order = [k for k in SCHEMA_ORDER if k in present]
    if present != expected_order:
        findings.append(Finding("Critical", target, "mission.frontmatter-field-order",
                                f"frontmatter fields out of declared order: got {present}, "
                                f"expected {expected_order}"))
    return findings


def check_frontmatter_values(data: dict, target: str) -> list[Finding]:
    findings: list[Finding] = []

    statement = data.get("mission_statement")
    if not isinstance(statement, str) or not statement.strip():
        findings.append(Finding("Critical", target, "mission.mission-statement-empty",
                                "`mission_statement` must be a non-empty string"))

    outcomes = data.get("relevant_outcomes")
    goals_ids = _outcome_ids(GOALS_PATH.read_text(encoding="utf-8")) if GOALS_PATH.exists() else None
    if not isinstance(outcomes, list) or not outcomes:
        findings.append(Finding("Critical", target, "mission.relevant-outcomes-empty",
                                "`relevant_outcomes` must be a non-empty list of `O-<n>` IDs"))
    else:
        for o in outcomes:
            if not isinstance(o, str) or not OUTCOME_RE.match(o):
                findings.append(Finding("Critical", target, "mission.relevant-outcome-pattern",
                                        f"`relevant_outcomes` entry `{o}` is not an `O-<n>` ID"))
            elif goals_ids is not None and o not in goals_ids:
                findings.append(Finding("Critical", target, "mission.relevant-outcome-unresolved",
                                        f"`relevant_outcomes` entry `{o}` does not resolve to an "
                                        f"outcome in project/goals.md"))

    audiences = data.get("audiences")
    aud_ids = _audience_ids(AUDIENCES_PATH.read_text(encoding="utf-8")) if AUDIENCES_PATH.exists() else None
    if not isinstance(audiences, list) or not audiences:
        findings.append(Finding("Critical", target, "mission.audiences-empty",
                                "`audiences` must be a non-empty list of audience identifiers"))
    else:
        for a in audiences:
            if aud_ids is not None and a not in aud_ids:
                findings.append(Finding("Critical", target, "mission.audience-unresolved",
                                        f"`audiences` entry `{a}` does not resolve to an audience "
                                        f"identifier in AUDIENCES.md"))

    findings += check_verifies_via(data.get("verifies_via"), target)
    findings += check_time_bound(data.get("time_bound"), target, data.get("relevant_outcomes"))

    mvp_status = data.get("mvp_status")
    if mvp_status not in MVP_STATUS_ENUM:
        findings.append(Finding("Critical", target, "mission.mvp-status-enum",
                                f"`mvp_status` `{mvp_status}` is not in {sorted(MVP_STATUS_ENUM)}"))

    created = data.get("created")
    if not _is_iso_date(created):
        findings.append(Finding("Critical", target, "mission.created-date",
                                f"`created` `{created}` is not an ISO date (YYYY-MM-DD)"))

    revised_at = data.get("revised_at")
    if revised_at is not None and not _is_iso_date(revised_at):
        findings.append(Finding("Critical", target, "mission.revised-at-date",
                                f"`revised_at` must be an ISO date or null, got `{revised_at}`"))

    return findings


def check_verifies_via(verifies_via, target: str) -> list[Finding]:
    if not isinstance(verifies_via, str) or not VERIFIES_VIA_RE.match(verifies_via):
        return [Finding("Critical", target, "mission.verifies-via-pattern",
                        f"`verifies_via` must match `<feature-id>:acceptance-<n>` "
                        f"(e.g. `F-3:acceptance-2`), got `{verifies_via}`")]
    m = VERIFIES_VIA_RE.match(verifies_via)
    feature_id, acceptance_id = m.group(1), m.group(2)
    index = _feature_index()
    if not index:
        return []  # no feature corpus on disk — nothing to resolve against
    if feature_id not in index:
        return [Finding("Critical", target, "mission.verifies-via-feature-missing",
                        f"`verifies_via` names feature `{feature_id}`, but no file under "
                        f"project/features/ declares `id: {feature_id}`")]
    declared = index[feature_id]
    if declared is not None and declared != acceptance_id:
        return [Finding("Critical", target, "mission.verifies-via-acceptance-mismatch",
                        f"`verifies_via` names `{acceptance_id}` on `{feature_id}`, but that "
                        f"feature's `verifies_sprint_value` is `{declared}`")]
    return []


def check_time_bound(time_bound, target: str, outcomes) -> list[Finding]:
    if not isinstance(time_bound, dict):
        return [Finding("Critical", target, "mission.time-bound-shape",
                        "`time_bound` must be a mapping `{kind: mvp_completion}` or "
                        f"`{{kind: outcome, ref: O-<n>}}`, got `{time_bound!r}`")]
    kind = time_bound.get("kind")
    if kind == "mvp_completion":
        extra = set(time_bound) - {"kind"}
        if extra:
            return [Finding("Critical", target, "mission.time-bound-shape",
                            f"`time_bound` kind `mvp_completion` carries unexpected keys {sorted(extra)}; "
                            f"the only permitted shape is `{{kind: mvp_completion}}`")]
        return []
    if kind == "outcome":
        ref = time_bound.get("ref")
        extra = set(time_bound) - {"kind", "ref"}
        findings: list[Finding] = []
        if extra:
            findings.append(Finding("Critical", target, "mission.time-bound-shape",
                                    f"`time_bound` kind `outcome` carries unexpected keys {sorted(extra)}; "
                                    f"the only permitted shape is `{{kind: outcome, ref: O-<n>}}`"))
        if not (isinstance(ref, str) and OUTCOME_RE.match(ref)):
            findings.append(Finding("Critical", target, "mission.time-bound-ref",
                                    f"`time_bound.ref` must be an `O-<n>` outcome ID, got `{ref}`"))
        return findings
    return [Finding("Critical", target, "mission.time-bound-kind",
                    f"`time_bound.kind` must be `mvp_completion` or `outcome`, got `{kind!r}`; "
                    f"calendar-date and free-text deadlines are rejected by the spec")]


def check_body(body: str, target: str) -> list[Finding]:
    findings: list[Finding] = []
    headings = re.findall(r"^##\s+(.+?)\s*$", body, re.M)
    present = [h for h in headings if h in REQUIRED_SECTIONS]
    for sec in REQUIRED_SECTIONS:
        if sec not in headings:
            findings.append(Finding("Critical", target, "mission.body-section-missing",
                                    f"required `## {sec}` section is missing"))
    expected = [s for s in REQUIRED_SECTIONS if s in present]
    if present != expected:
        findings.append(Finding("Critical", target, "mission.body-section-order",
                                f"required sections out of declared order: got {present}, "
                                f"expected {expected}"))
    return findings


def check_mission_text(text: str, target: str) -> list[Finding]:
    """Run every check over a mission file's raw text. Shared by the CLI and the
    self-test so the negative-proof fixtures exercise exactly the CLI path."""
    split = _split(text)
    if split is None:
        return [Finding("Critical", target, "mission.frontmatter-missing", "no YAML frontmatter fence")]
    fm, body = split

    findings = check_frontmatter_order_and_keys(fm, target)

    if yaml is None:
        # Without PyYAML the value-level checks can't run; the order/key checks
        # above still fire. Degrade rather than crash.
        return findings + check_body(body, target)
    try:
        data = yaml.safe_load(fm)
    except (yaml.YAMLError, ValueError) as exc:  # noqa: BLE001 - YAMLError, plus ValueError from an out-of-range native date
        detail = str(getattr(exc, "problem", None) or exc).strip().splitlines()[0]
        return findings + [Finding("Critical", target, "mission.frontmatter-yaml-invalid",
                                   f"frontmatter is not valid YAML ({detail})")]
    if not isinstance(data, dict):
        return findings + [Finding("Critical", target, "mission.frontmatter-not-mapping",
                                   "frontmatter is not a YAML mapping")]

    findings += check_frontmatter_values(data, target)
    findings += check_body(body, target)
    return findings


def check_mission(path: Path) -> list[Finding]:
    rel = path.relative_to(REPO).as_posix() if path.is_relative_to(REPO) else path.as_posix()
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:  # pragma: no cover
        return [Finding("Critical", rel, "mission.unreadable", str(exc))]
    return check_mission_text(text, rel)


# --- Negative-proof self-test ---------------------------------------------
# A deliberately broken mission fixture: the linter MUST fire on each planted
# defect. This is the on-disk proof that the gate isn't inert. Kept in the script
# (rather than only in tests/) so `validate_mission.py --self-test` is runnable in
# any environment without pytest.
_BROKEN_FIXTURE = """---
mission_statement: ""
audiences:
  - not-a-real-audience
relevant_outcomes: []
verifies_via: not-a-valid-ref
time_bound:
  kind: "2026-12-31"
mvp_status: shipping
created: someday
revised_at: "later"
bogus_key: nope
---

# Mission

## Statement

x

## Verification

x

## Audiences

x
"""

# Rule ids the broken fixture MUST provoke (a representative subset — each names a
# distinct planted defect: empty statement, unresolved audience, empty outcomes,
# bad verifies_via, calendar time_bound, bad enum, bad date, unknown key,
# field-order violation, section-order violation).
_SELF_TEST_EXPECTED = {
    "mission.mission-statement-empty",
    "mission.audience-unresolved",
    "mission.relevant-outcomes-empty",
    "mission.verifies-via-pattern",
    "mission.time-bound-kind",
    "mission.mvp-status-enum",
    "mission.created-date",
    "mission.revised-at-date",
    "mission.frontmatter-unknown-key",
    "mission.frontmatter-field-order",
    "mission.body-section-order",
}


def run_self_test() -> int:
    findings = check_mission_text(_BROKEN_FIXTURE, "<self-test fixture>")
    fired = {f.rule for f in findings}
    missing = _SELF_TEST_EXPECTED - fired
    if missing:
        print("SELF-TEST FAILED: the linter did not fire on planted defects:", file=sys.stderr)
        for rule in sorted(missing):
            print(f"  expected-but-missing: {rule}", file=sys.stderr)
        return 2
    # A well-formed mission (the repo's own) MUST pass, so a green file isn't
    # falsely failed. Only checked when the real file exists.
    if MISSION_PATH.exists():
        real = check_mission(MISSION_PATH)
        criticals = [f for f in real if f.severity == "Critical"]
        if criticals:
            print("SELF-TEST FAILED: the live project/mission.md has Critical findings:", file=sys.stderr)
            for f in criticals:
                print(f"  {f}", file=sys.stderr)
            return 2
    print(f"validate_mission --self-test: linter fired on {len(_SELF_TEST_EXPECTED)} "
          f"planted defects; live mission (if present) is clean")
    return 0


def main() -> int:
    args = sys.argv[1:]
    if args and args[0] == "--self-test":
        return run_self_test()

    if args:
        paths = [REPO / a if not Path(a).is_absolute() else Path(a) for a in args]
        for p in paths:
            if not p.exists():
                print(f"ERROR: path not found: {p}", file=sys.stderr)
                return 2
    elif MISSION_PATH.exists():
        paths = [MISSION_PATH]
    else:
        # A repository that hasn't adopted the mission file is a pass, not an error.
        print("validate_mission: project/mission.md absent (permitted), no findings")
        return 0

    all_findings: list[Finding] = []
    for path in paths:
        all_findings.extend(check_mission(path))

    if not all_findings:
        print(f"validate_mission: {len(paths)} mission file(s) checked, no findings")
        return 0

    by_severity = {"Critical": 0, "Warning": 0, "Suggestion": 0, "Info": 0}
    for f in all_findings:
        by_severity[f.severity] = by_severity.get(f.severity, 0) + 1
        print(f)

    print(
        f"\nvalidate_mission: {len(paths)} mission file(s); "
        f"{by_severity['Critical']}C / {by_severity['Warning']}W / "
        f"{by_severity['Suggestion']}S / {by_severity['Info']}I",
        file=sys.stderr,
    )
    return 1 if by_severity["Critical"] else 0


if __name__ == "__main__":
    sys.exit(main())
