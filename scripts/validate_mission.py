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
  1  at least one error (`Critical`-grade per `review-plan` §Severity scale);
     an unreadable or non-UTF-8 input file (the mission, goals.md, AUDIENCES.md,
     or a feature file) or a non-UTF-8 committed mission version is such a
     `Critical` finding (`mission.unreadable`); an unreadable goals.md,
     AUDIENCES.md, or feature file doesn't stop the other checks
  2  path not found, or failed self-test

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
import os
import subprocess
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


def _display(path: Path) -> str:
    """`path` relative to the repository when it lies inside it, else as given."""
    return path.relative_to(REPO).as_posix() if path.is_relative_to(REPO) else path.as_posix()


def _undecodable(target: str, source: str, exc: UnicodeDecodeError) -> Finding:
    """The Critical finding for an input that isn't valid UTF-8, naming `source`."""
    return Finding("Critical", target, "mission.unreadable", f"{source} is not valid UTF-8 ({exc})")


def _unreadable(target: str, source: str, exc: OSError | UnicodeDecodeError) -> Finding:
    """The Critical finding for an input that can't be read or decoded, naming `source`."""
    if isinstance(exc, UnicodeDecodeError):
        return _undecodable(target, source, exc)
    return Finding("Critical", target, "mission.unreadable", f"{source} can't be read ({exc})")


def _read_ids(path: Path, parse, target: str, findings: list[Finding]) -> set[str] | None:
    """IDs parsed from `path`, or None when it is absent, unreadable, or undecodable.

    An unreadable or undecodable file resolves nothing (like an absent one) and appends a
    `mission.unreadable` finding naming it, so the caller's other checks still run.
    """
    if not path.exists():
        return None
    try:
        return parse(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as exc:
        findings.append(_unreadable(target, _display(path), exc))
        return None


def _feature_index(target: str) -> tuple[dict[str, str | None], list[Finding]]:
    """Map feature id (`F-<n>`) -> its `verifies_sprint_value` scalar (or None).

    Read from project/features/*.md frontmatter so `verifies_via` can be resolved
    to both an existing feature file and the acceptance identifier it names. A
    feature file that can't be read or isn't valid UTF-8 yields a
    `mission.unreadable` finding naming it; the other feature files are still indexed.
    """
    index: dict[str, str | None] = {}
    findings: list[Finding] = []
    if not FEATURES_DIR.is_dir():
        return index, findings
    for path in sorted(FEATURES_DIR.glob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            findings.append(_unreadable(target, _display(path), exc))
            continue
        split = _split(text)
        if split is None:
            continue
        fm = split[0]
        fid = re.search(r"^id:\s*(\S+)\s*$", fm, re.M)
        if not fid:
            continue
        vsv = re.search(r"^verifies_sprint_value:\s*(\S+)\s*$", fm, re.M)
        index[fid.group(1)] = vsv.group(1) if vsv else None
    return index, findings


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
    goals_ids = _read_ids(GOALS_PATH, _outcome_ids, target, findings)
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
    aud_ids = _read_ids(AUDIENCES_PATH, _audience_ids, target, findings)
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
    index, findings = _feature_index(target)
    if not index:
        return findings  # no readable feature corpus on disk — nothing to resolve against
    if feature_id not in index:
        return findings + [Finding("Critical", target, "mission.verifies-via-feature-missing",
                                   f"`verifies_via` names feature `{feature_id}`, but no file under "
                                   f"project/features/ declares `id: {feature_id}`")]
    declared = index[feature_id]
    if declared is not None and declared != acceptance_id:
        return findings + [Finding("Critical", target, "mission.verifies-via-acceptance-mismatch",
                                   f"`verifies_via` names `{acceptance_id}` on `{feature_id}`, but that "
                                   f"feature's `verifies_sprint_value` is `{declared}`")]
    return findings


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


def _source_section(body_text: str) -> str:
    """The text of the `## Source` section, or "" when there is none."""
    parts = body_text.split("\n## Source", 1)
    if len(parts) < 2:
        return ""
    return parts[1].split("\n## ", 1)[0]


def check_revision_rationale(old_text: str, new_text: str, target: str) -> list[Finding]:
    """spec/project/mission/ §Revision: a revision after stabilisation carries a rationale.

    Guard origin (spec/project/defect-class-guards/ G5): #591. The file alone
    can't show that a revision happened, so this compares two versions: when the
    earlier one was already `mvp_status: stabilised` and anything outside
    `## Source` changed, `## Source` has to change too.
    """
    old, new = _split(old_text), _split(new_text)
    if old is None or new is None or old_text == new_text:
        return []
    if not re.search(r"^mvp_status:\s*stabilised\s*$", old[0], re.MULTILINE):
        return []
    old_source, new_source = _source_section(old[1]), _source_section(new[1])
    outside_changed = (old[0], old[1].replace(old_source, "")) != (new[0], new[1].replace(new_source, ""))
    if outside_changed and old_source == new_source:
        return [Finding("Critical", target, "mission.post-stabilisation-rationale",
                        "the mission changed after `mvp_status: stabilised` without a rationale paragraph in `## Source`")]
    return []


_STABILISED_RE = re.compile(r"""^mvp_status:\s*["']?stabilised["']?\s*(?:#.*)?$""", re.MULTILINE)
_ISO_DATE_IN_TEXT_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
# Fixed evidence vocabulary (EN + DE, since `## Source` follows the file's language).
# A sentence names the subsequent sprint when it carries a subsequent-sprint marker
# (`subsequent sprint`, `subsequent-sprint`, `Folgesprint`, `Folge-Sprint`, or the
# `+ 1` of "MVP-closing + 1") and a sprint number (`sprint <n>`, `Sprint `0002``).
_SUBSEQUENT_MARKER_RE = re.compile(r"subsequent[- ]sprint|folge-?\s*sprint|(?:closing|\d)\W{0,3}\+\s*1\b", re.IGNORECASE)
_SUBSEQUENT_NUMBER_RE = re.compile(r"sprint\W{0,3}\d+", re.IGNORECASE)  # no \b: `Folgesprint 2`
_SENTENCE_SPLIT_RE = re.compile(r"(?<!\be\.g\.)(?<!\bi\.e\.)(?<!\bz\.B\.)(?<=[.!?])\s+(?=[A-Z`*(\-])|\n")
_EXEMPTION_NAMED_RE = re.compile(r"(?=.*\b(?:retroactive|rückwirkend))(?=.*(?:exemption|ausnahme))",
                                 re.IGNORECASE | re.DOTALL)
_SPRINT_NUMBER_RE = re.compile(r"\bsprint\W{0,3}\d+", re.IGNORECASE)
_ENDED_DATE_RE = re.compile(r"\b(?:ended|endete)\b[^0-9\n]{0,15}\d{4}-\d{2}-\d{2}", re.IGNORECASE)
_COMMIT_RE = re.compile(r"\b(?=[0-9a-f]{0,39}\d)[0-9a-f]{7,40}\b")  # a SHA, not a hex-only word like "defaced"


def _names_subsequent_sprint(text: str) -> bool:
    """True when one sentence of `text` carries a subsequent-sprint marker and a sprint number."""
    # Unwrap hard-wrapped lines; a blank line or a new list item still ends the sentence.
    joined = re.sub(r"[ \t]*(?<!\n)\n(?!\n|\s*[-*+] )[ \t]*", " ", text)
    return any(_SUBSEQUENT_MARKER_RE.search(sentence) and _SUBSEQUENT_NUMBER_RE.search(sentence)
               for sentence in _SENTENCE_SPLIT_RE.split(joined))


def check_stabilisation_evidence(old_text: str, new_text: str, target: str) -> list[Finding]:
    """spec/project/mission/ §Stabilisation gate: a flip to `stabilised` records its evidence.

    Guard origin (spec/project/defect-class-guards/ G5): #750. Predicate (G3): every
    change whose earlier version isn't `mvp_status: stabilised` and whose later
    version is. The lines that change adds to `## Source` must carry one of:

    - the retroactive-MVP exemption rationale: once the added text names the
      exemption (`retroactive`/`rückwirkend` plus `exemption`/`Ausnahme`), it must
      carry every evidence field the spec's MUST lists: the MVP-closing sprint's
      number (`sprint <n>`) and `ended` date (`ended`/`endete`, then an ISO date),
      the commit that first added `project/mission.md` (a 7-40 char hex SHA), and
      the operator decision date (a second ISO date);
    - otherwise the subsequent-sprint evidence: one sentence carrying a
      subsequent-sprint marker (`subsequent sprint`, `subsequent-sprint`,
      `Folgesprint`, `Folge-Sprint`, or `+ 1`) and the sprint's number
      (`sprint <n>`), plus the operator decision date (an ISO date).

    Like `check_revision_rationale`, it compares two versions, because the file
    alone can't show that the flip happened in this change.
    """
    old, new = _split(old_text), _split(new_text)
    if old is None or new is None:
        return []
    if _STABILISED_RE.search(old[0]) or not _STABILISED_RE.search(new[0]):
        return []
    old_lines = set(_source_section(old[1]).splitlines())
    added = "\n".join(line for line in _source_section(new[1]).splitlines() if line not in old_lines)
    dates = len(_ISO_DATE_IN_TEXT_RE.findall(added))

    if _EXEMPTION_NAMED_RE.search(added):
        missing = []
        if not _SPRINT_NUMBER_RE.search(added):
            missing.append("the MVP-closing sprint's number")
        if not _ENDED_DATE_RE.search(added):
            missing.append("that sprint's `ended` date")
        if not _COMMIT_RE.search(added):
            missing.append("the commit that first added project/mission.md")
        if dates < 2:
            missing.append("the operator decision date")
        if missing:
            return [Finding("Critical", target, "mission.stabilisation-exemption-evidence",
                            "the flip to `mvp_status: stabilised` names the retroactive-MVP exemption, but its "
                            "`## Source` rationale lacks " + "; ".join(missing))]
        return []

    if _names_subsequent_sprint(added) and dates >= 1:
        return []
    return [Finding("Critical", target, "mission.stabilisation-evidence-missing",
                    "the flip to `mvp_status: stabilised` adds to `## Source` neither path's evidence: "
                    "for the normal path, one sentence naming the subsequent sprint (`subsequent sprint`, "
                    "`Folgesprint` or `MVP-closing + 1`) with its number (`sprint <n>`), plus the decision "
                    "date; for the retroactive-MVP exemption, a rationale naming it (`retroactive`/"
                    "`rückwirkend` and `exemption`/`Ausnahme`) with the MVP-closing sprint's number and "
                    "`ended` date, the commit that first added project/mission.md, and the decision date")]


def _committed_version(path: Path, ref: str) -> str | None:
    """`path` as committed at `ref`, or None when git has no such version.

    The output is decoded as strict UTF-8; content that isn't valid UTF-8 raises
    `UnicodeDecodeError` for the caller to report, never "no committed version".
    """
    try:
        rel = path.resolve().relative_to(REPO).as_posix()
    except ValueError:
        return None
    # Text mode keeps the universal-newline translation the working-tree read gets;
    # `encoding` makes the decode strict UTF-8 regardless of the locale.
    proc = subprocess.run(["git", "show", f"{ref}:{rel}"], cwd=REPO, capture_output=True,
                          text=True, encoding="utf-8")
    return proc.stdout if proc.returncode == 0 else None


def check_mission(path: Path) -> list[Finding]:
    rel = _display(path)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:  # pragma: no cover
        return [Finding("Critical", rel, "mission.unreadable", str(exc))]
    except UnicodeDecodeError as exc:
        return [_undecodable(rel, rel, exc)]
    findings = check_mission_text(text, rel)
    base = os.environ.get("MISSION_BASE_REF", "").strip()
    ref = base or "HEAD"
    try:
        committed = _committed_version(path, ref)
    except UnicodeDecodeError as exc:
        # The revision and stabilisation checks can't compare against it; say so.
        findings.append(_undecodable(rel, f"{ref}:{path.resolve().relative_to(REPO).as_posix()}", exc))
        return findings
    if committed is None and base:
        # An explicitly configured base that can't be read would make the check
        # vacuous in exactly the run meant to enforce it (a shallow CI checkout).
        findings.append(Finding("Critical", rel, "mission.base-ref-unreadable",
                                f"MISSION_BASE_REF={base} names no readable version of {rel}; fetch full history"))
    elif committed is not None:
        findings.extend(check_revision_rationale(committed, text, rel))
        findings.extend(check_stabilisation_evidence(committed, text, rel))
    return findings


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
