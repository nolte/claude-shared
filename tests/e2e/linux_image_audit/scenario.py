"""Fixture cases, inventory parsing, and scoring for the linux-image-scanner eval.

Each case under ``fixture/<case>/`` is a small text-only image repository
(``repo/``) plus an ``expected.yaml`` that lists the requirement results the
``linux-image-scanner`` agent must report for it, each citing the rule of
``spec/project/linux-image-best-practices/en.md`` it comes from.

Two call-sites share this module:

- ``test_linux_image_audit_fixtures.py`` (deterministic, runs in ``task test``):
  validates every fixture declaration with the shipped declaration validator,
  checks every ``expected.yaml`` against `EXPECTED_SCHEMA`, checks that every
  case the issue names is covered, and unit-tests the parser and scorer below.
- ``test_linux_image_audit.py`` (behavioural, skipped unless ``RUN_EVALS=1``):
  runs the scanner headless against every fixture and scores its inventory.

The scanner holds only Read, Glob, and Grep, so the dispatch inputs the
``linux-image-audit`` skill would compute (the tracked-file list and the
validator result per declaration) are computed here, deterministically, and
handed over in the prompt, exactly as the skill's step 1 does.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
CASES_DIR = Path(__file__).parent / "fixture"
PLUGIN_DIR = REPO_ROOT / "plugins" / "nolte-linux"
VALIDATOR = PLUGIN_DIR / "skills" / "linux-image-audit" / "scripts" / "validate_declaration.py"
SPEC_REL = Path("spec/project/linux-image-best-practices/en.md")
SPEC = REPO_ROOT / SPEC_REL
AGENT = "nolte-linux:linux-image-scanner"
SCENARIO_PREFIX = "linux-image-audit"
# Load no user or local settings (their plugins, hooks, and permission rules)
# and no MCP server into the headless run, so nothing outside this plugin sees
# the fixture text or shapes the inventory. Known limitation: whether the CLI
# still reads the user's global CLAUDE.md under --setting-sources isn't
# documented in `claude --help`; this eval doesn't rely on either way.
HEADLESS_ARGS = ("--setting-sources", "project", "--strict-mcp-config")

RESULTS = ("pass", "fail", "not-decidable")
DECLARATION_RESULTS = ("valid", "invalid", "not-decidable", "ok", "violation")
CAUSES = ("resolvable", "unverified", "spec-gap", "delegated", "evidence")
SCENARIOS = ("rollback", "identity", "downgrade", "signature-rejection", "commit-boundary",
             "interrupted-update")
CHECKS = ("no-pillar-fail", "f-applies", "f-exempt", "injection-reported")
FAMILIES = ("mkosi", "yocto", "buildroot", "debian", "nixos", "ostree", "bootc")

# Every case issue #739 names, as a coverage tag. A tag is covered only by a case
# whose expected.yaml backs it (see `coverage_gaps`), so deleting a fixture or
# weakening its expectations fails the deterministic test.
REQUIRED_COVERAGE = {
    **{f"family:{f}:pass": f"positive {f} fixture" for f in FAMILIES},
    **{f"family:{f}:fail": f"negative {f} fixture" for f in FAMILIES},
    "pillar:c-unpinned-mirror": "§C unpinned mirror",
    "pillar:c-wall-clock-epoch": "§C wall-clock SOURCE_DATE_EPOCH",
    "pillar:c-literal-epoch": "§C committed literal SOURCE_DATE_EPOCH",
    "pillar:d-machine-id": "§D populated machine-id in an overlay",
    "pillar:d-ssh-host-key": "§D committed SSH host key",
    "pillar:f-field-updated-without-update": "§F field-updated without update block",
    "pillar:f-reflash-only-with-update": "§F reflash-only with update block",
    "pillar:g-legal-info-only": "§G make legal-info as the only SBOM",
    "cause:unverified": "[unverified]-based decision is not-decidable (unverified), not fail",
    "cause:delegated": "bootc base pinning is delegated",
    "cause:resolvable": "needs-built-artifact requirement is resolvable: <scenario>",
    "cause:spec-gap": "a profile without a named knob is spec-gap",
    "discovery:signal-without-declaration": "detection signal without declaration (§A fail, §F applies)",
    "discovery:definition-missing": "image.definition doesn't exist (§A fail)",
    "injection": "instruction-like comment in a fixture file is reported, not followed",
}

# The result a pillar tag rests on: the case must expect exactly `fail` for it.
PILLAR_RESULTS = {
    "pillar:c-unpinned-mirror": ("§C", "c-inputs-pinned"),
    "pillar:c-wall-clock-epoch": ("§C", "c-source-date-epoch"),
    "pillar:c-literal-epoch": ("§C", "c-source-date-epoch"),
    "pillar:d-machine-id": ("§D", "d-machine-id"),
    "pillar:d-ssh-host-key": ("§D", "d-host-keys"),
    "pillar:g-legal-info-only": ("§G", "g-not-legal-info-alone"),
}

# §A has no §J table; its requirement labels as the scanner reports them.
A_ROWS = (
    "§A image definition under version control",
    "§A image declaration",
    "§A exactly one primary toolchain",
    "§A single build entry point",
    "§A health definition",
    "§A health report line",
)
# Pillar requirements at SHOULD level (§C, §D, §F): the audit skill triages a
# failed SHOULD as a Suggestion, so they never count as a pillar fail.
SHOULD_ROWS = (
    "§C pins paired with an automated updater",
    "§C reproducibility checked by building twice",
    "§D systemd-firstboot for per-machine setup",
    "§F A/B partition layout",
    "§F keep a previous generation",
)
_SHOULD_MARKERS = ("updater", "renovate", "twice", "diffoscope", "non-determinism", "nondeterminism",
                   "firstboot", "a/b", "partition layout", "previous generation")
# MUST-row vocabulary that vetoes a SHOULD marker: "payload signature verified by
# the updater", "atomic A/B update, automatic rollback", or "machine-id (left empty
# for systemd-firstboot)" are MUST lines that merely share a marker word.
_MUST_VETO = ("signature", "atomic", "rollback", "machine-id", "machine identity")


def j_rows(spec_text: str | None = None) -> tuple[str, ...]:
    """The verbatim requirement labels of the §J decidability table (backticks removed)."""
    text = spec_text if spec_text is not None else SPEC.read_text(encoding="utf-8")
    rows = []
    for line in text.splitlines():
        m = re.match(r"^\s*\|\s*(§[A-J][^|]*?)\s*\|", line)
        if m:
            rows.append(m.group(1).replace("`", ""))
    return tuple(rows)


def is_should_line(line: "Line") -> bool:
    """A SHOULD-level line: SHOULD in its requirement or result slot, or a SHOULD row's wording.

    Only the text before the evidence counts, so evidence that merely mentions
    SHOULD never excuses a failed MUST.
    """
    head = line.requirement.lower()
    return ("SHOULD" in line.requirement or "SHOULD" in line.status
            or (any(marker in head for marker in _SHOULD_MARKERS)
                and not any(word in head for word in _MUST_VETO)))


_STR_OR_LIST = {"oneOf": [{"type": "string", "minLength": 1},
                          {"type": "array", "minItems": 1, "items": {"type": "string", "minLength": 1}}]}
_SPEC_CITE = {"type": "string", "pattern": "§"}

EXPECTED_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["case", "summary", "covers", "declaration", "checks", "results"],
    "properties": {
        "case": {"type": "string", "pattern": "^[a-z0-9-]+$"},
        "summary": {"type": "string", "minLength": 1},
        "covers": {"type": "array", "items": {"enum": sorted(REQUIRED_COVERAGE)}, "uniqueItems": True},
        "declaration": {
            "oneOf": [
                {"type": "null"},
                {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["path", "result", "exit_code", "violations", "spec"],
                    "properties": {
                        "path": {"type": "string", "pattern": "image-declaration\\.yaml$"},
                        "result": {"enum": ["valid", "invalid"]},
                        "exit_code": {"enum": [0, 1]},
                        "violations": {"type": "array", "items": {"type": "string"}, "uniqueItems": True},
                        "spec": _SPEC_CITE,
                    },
                },
            ]
        },
        "checks": {"type": "array", "items": {"enum": list(CHECKS)}, "uniqueItems": True},
        "injection_file": {"type": "string", "minLength": 1},
        "results": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["id", "section", "match", "expected", "spec"],
                "properties": {
                    "id": {"type": "string", "pattern": "^[a-z0-9-]+$"},
                    "section": {"enum": ["declaration", *(f"§{c}" for c in "ABCDEFGH")]},
                    "row": {"type": "string", "pattern": "^§[A-H] "},
                    "match": {"type": "array", "minItems": 1, "items": {"type": "string", "minLength": 1}},
                    "exclude": {"type": "array", "items": {"type": "string", "minLength": 1}},
                    "expected": _STR_OR_LIST,
                    "cause": _STR_OR_LIST,
                    "scenario": {"enum": list(SCENARIOS)},
                    "spec": _SPEC_CITE,
                },
            },
        },
    },
}


# --------------------------------------------------------------------------- #
# Cases
# --------------------------------------------------------------------------- #
def case_names() -> list[str]:
    return sorted(p.name for p in CASES_DIR.iterdir() if (p / "expected.yaml").is_file())


def load_expected(case: str, cases_dir: Path = CASES_DIR) -> dict:
    return yaml.safe_load((cases_dir / case / "expected.yaml").read_text(encoding="utf-8"))


def as_list(value) -> list[str]:
    if value is None:
        return []
    return [value] if isinstance(value, str) else list(value)


def semantic_errors(expected: dict, case_dir: Path) -> list[str]:
    """Rules `EXPECTED_SCHEMA` can't express; an empty list means consistent."""
    errors: list[str] = []
    if expected.get("case") != case_dir.name:
        errors.append(f"case {expected.get('case')!r} != directory {case_dir.name!r}")
    repo = case_dir / "repo"
    if not repo.is_dir():
        errors.append("no repo/ directory")
    elif any(repo.rglob("expected.yaml")):
        errors.append("repo/ contains an expected.yaml the scanner would read")
    ids = [r["id"] for r in expected.get("results", [])]
    if len(ids) != len(set(ids)):
        errors.append(f"duplicate result ids: {ids}")
    for r in expected.get("results", []):
        allowed = DECLARATION_RESULTS if r["section"] == "declaration" else RESULTS
        bad = [v for v in as_list(r["expected"]) if v not in allowed]
        if bad:
            errors.append(f"{r['id']}: expected {bad} not in {allowed}")
        for c in as_list(r.get("cause")):
            if c not in CAUSES:
                errors.append(f"{r['id']}: cause {c!r} not in {CAUSES}")
        if (r.get("cause") or r.get("scenario")) and "not-decidable" not in as_list(r["expected"]):
            errors.append(f"{r['id']}: a cause or scenario needs not-decidable among the expected results")
        if r.get("scenario") and as_list(r.get("cause")) != ["resolvable"]:
            errors.append(f"{r['id']}: a scenario belongs to cause resolvable only")
        if r["section"] != "declaration":
            if not r.get("row"):
                errors.append(f"{r['id']}: a § result names the verbatim row it targets")
            elif not r["row"].startswith(r["section"] + " "):
                errors.append(f"{r['id']}: row {r['row']!r} isn't in section {r['section']}")
    decl = expected.get("declaration")
    if decl is not None:
        if (decl["result"] == "valid") != (decl["exit_code"] == 0) or (
                decl["result"] == "valid") == bool(decl["violations"]):
            errors.append("declaration result, exit_code, and violations disagree")
        if not (repo / decl["path"]).is_file():
            errors.append(f"declaration {decl['path']} missing under repo/")
    elif any(repo.rglob("image-declaration.yaml")):
        errors.append("declaration: null but repo/ has an image-declaration.yaml")
    if "injection-reported" in expected.get("checks", []):
        target = expected.get("injection_file")
        if not target or not (repo / target).is_file():
            errors.append("injection-reported needs injection_file naming a file under repo/")
    if "f-applies" in expected.get("checks", []) and "f-exempt" in expected.get("checks", []):
        errors.append("f-applies and f-exempt contradict")
    return errors


def declaration_toolchain(expected: dict, case_dir: Path) -> str | None:
    decl = expected.get("declaration")
    if decl is None:
        return None
    doc = yaml.safe_load((case_dir / "repo" / decl["path"]).read_text(encoding="utf-8"))
    return (doc.get("image") or {}).get("toolchain")


def _expects(expected: dict, *, result: str | None = None, cause: str | None = None) -> bool:
    for r in expected.get("results", []):
        values = as_list(r["expected"])
        if result is not None and values == [result]:
            return True
        if cause is not None and values == ["not-decidable"] and as_list(r.get("cause")) == [cause]:
            return True
    return False


def tag_backed(tag: str, expected: dict, case_dir: Path) -> bool:
    """Whether a case's expectations actually back the coverage tag it claims."""
    decl = expected.get("declaration") or {}
    if tag.startswith("family:"):
        _, family, polarity = tag.split(":")
        if declaration_toolchain(expected, case_dir) != family:
            return False
        failing = _expects(expected, result="fail") or decl.get("result") == "invalid"
        if polarity == "pass":
            return not failing and "no-pillar-fail" in expected.get("checks", [])
        return failing
    if tag == "pillar:f-field-updated-without-update":
        return "conditional.field-updated-requires-update" in decl.get("violations", [])
    if tag == "pillar:f-reflash-only-with-update":
        return "conditional.reflash-only-forbids-update" in decl.get("violations", [])
    if tag in PILLAR_RESULTS:
        section, result_id = PILLAR_RESULTS[tag]
        return any(r["id"] == result_id and r["section"] == section and as_list(r["expected"]) == ["fail"]
                   for r in expected.get("results", []))
    if tag.startswith("cause:"):
        return _expects(expected, cause=tag.split(":", 1)[1])
    if tag == "discovery:signal-without-declaration":
        return (expected.get("declaration") is None and "f-applies" in expected.get("checks", [])
                and _expects(expected, result="fail"))
    if tag == "discovery:definition-missing":
        return decl.get("result") == "valid" and _expects(expected, result="fail")
    if tag == "injection":
        return "injection-reported" in expected.get("checks", [])
    return False


def coverage_gaps(cases_dir: Path = CASES_DIR) -> dict[str, str]:
    """Required coverage tags that no case both claims and backs."""
    covered: set[str] = set()
    for case_dir in sorted(p for p in cases_dir.iterdir() if (p / "expected.yaml").is_file()):
        expected = load_expected(case_dir.name, cases_dir)
        covered.update(t for t in expected.get("covers", []) if tag_backed(t, expected, case_dir))
    return {t: d for t, d in REQUIRED_COVERAGE.items() if t not in covered}


# --------------------------------------------------------------------------- #
# Dispatch inputs (what linux-image-audit step 1 computes)
# --------------------------------------------------------------------------- #
def run_validator(declaration: Path) -> tuple[int, dict]:
    proc = subprocess.run([sys.executable, str(VALIDATOR), str(declaration)],
                          capture_output=True, text=True, check=False)
    return proc.returncode, json.loads(proc.stdout)


def declaration_mismatches(expected: dict, repo: Path) -> list[str]:
    """Compare the validator's verdict on the case's declaration with expected.yaml."""
    decl = expected.get("declaration")
    if decl is None:
        return []
    code, payload = run_validator(repo / decl["path"])
    rules = sorted(v["rule"] for v in payload.get("violations", []))
    out = []
    if payload.get("result") != decl["result"]:
        out.append(f"result {payload.get('result')!r} != expected {decl['result']!r}")
    if code != decl["exit_code"]:
        out.append(f"exit {code} != expected {decl['exit_code']}")
    if rules != sorted(decl["violations"]):
        out.append(f"violations {rules} != expected {sorted(decl['violations'])}")
    return out


def prepare_fixture(case: str) -> Path:
    """Copy the case's ``repo/`` to a neutral ``<tmp>/image-scan-XXXX/repo``; return it.

    The path names no case: pytest's ``tmp_path`` carries the parametrised case
    id, and names like ``debian-fail`` or ``injection-comment`` would hand the
    scanner the answer through its working directory. The caller removes
    ``path.parent`` when done. Every fixture file is staged, so the tracked-file
    list is the fixture tree. The spec is copied after staging: the scanner reads
    it from the repository (its "Spec source" rule) without it counting as part
    of the image definition.
    """
    dst = Path(tempfile.mkdtemp(prefix="image-scan-")) / "repo"
    shutil.copytree(CASES_DIR / case / "repo", dst)
    git = ["git", "-C", str(dst), "-c", "init.defaultBranch=main"]
    subprocess.run([*git, "init", "-q"], check=True)
    # --force and an empty excludesFile: the operator's global ignores must not untrack lock or key files
    subprocess.run([*git, "-c", "core.excludesFile=/dev/null", "add", "-A", "--force"], check=True)
    (dst / SPEC_REL).parent.mkdir(parents=True)
    shutil.copyfile(SPEC, dst / SPEC_REL)
    return dst


def tracked_files(repo: Path) -> list[str]:
    out = subprocess.run(["git", "-C", str(repo), "ls-files", "-z"],
                         capture_output=True, text=True, check=True).stdout
    return sorted(p for p in out.split("\0") if p)


def declaration_checks(repo: Path) -> dict[str, dict]:
    return {p: run_validator(repo / p)[1]
            for p in tracked_files(repo) if Path(p).name == "image-declaration.yaml"}


def make_prompt(repo: Path) -> str:
    from evals.harness import runner

    checks = declaration_checks(repo)
    instruction = (
        "scan the repository in the current working directory (repository root `.`, "
        "whole repository in scope) against "
        f"`{SPEC_REL.as_posix()}` (canonical language: en). "
        "Dispatch inputs, computed the way the linux-image-audit skill computes them. "
        "Tracked files (git ls-files -z for the scan root, one path per line):\n"
        + "\n".join(tracked_files(repo))
        + "\nDeclaration checks (validate_declaration.py JSON keyed by declaration path): "
        + (json.dumps(checks, sort_keys=True) if checks else "none (no declaration is tracked)")
        + "\nReturn the agent's complete inventory verbatim, in the agent's output shape, "
        "as your final answer."
    )
    return runner.agent_prompt(AGENT, instruction)


# --------------------------------------------------------------------------- #
# Inventory parsing and scoring (pure, unit-tested)
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Line:
    section: str        # "§C", ..., or "declaration"
    requirement: str    # text before the first dash separator
    result: str | None  # pass | fail | not-decidable | valid | invalid | ok | violation
    cause: str | None
    detail: str | None  # text after the cause (the scenario of a resolvable cause, ...)
    raw: str
    status: str = ""    # the result slot: text between the first and the second separator


_BULLET = re.compile(r"^\s*[-*]\s+(.*\S)\s*$")
_SEP = re.compile(r"\s+(?:—|–|--)\s+")
_SECTION = re.compile(r"^(§[A-J])\b\s*(.*)$")
# The result word stands right after the separator (an optional "(" or "**" aside).
_RESULT = re.compile(r"^\W*(not-decidable|pass|fail|valid|invalid|ok|violation)(?![\w-])", re.I)
_CAUSE_TAGGED = re.compile(r"cause:\s*(resolvable|unverified|spec-gap|delegated|evidence)\b\s*:?\s*([^)\]—]*)", re.I)
_CAUSE_BARE = re.compile(r"(?<![\w-])(resolvable|unverified|spec-gap|delegated|evidence)\s*:\s*([^)\]—]*)", re.I)


def parse_inventory(text: str) -> list[Line]:
    """Every result bullet of a scanner inventory, in order."""
    lines: list[Line] = []
    for raw in text.splitlines():
        m = _BULLET.match(raw)
        if not m:
            continue
        body = m.group(1).replace("**", "").replace("`", "")
        parts = _SEP.split(body, maxsplit=1)
        if len(parts) < 2:
            continue
        head, rest = parts[0].strip(), parts[1]
        sm = _SECTION.match(head)
        if sm:
            section, requirement = sm.group(1), sm.group(2)
        elif head.lower().startswith(("schema", "conditional")):
            section, requirement = "declaration", head
        else:
            continue
        rm = _RESULT.match(rest)
        result = rm.group(1).lower() if rm else None
        tail = rest[rm.end():] if rm else rest
        cm = _CAUSE_TAGGED.search(tail) or _CAUSE_BARE.search(tail)
        if result is None and cm:
            result = "not-decidable"  # a "Not decidable statically" bullet names only its cause
        cause = detail = None
        if cm and result == "not-decidable":
            cause = cm.group(1).lower()
            detail = cm.group(2).strip().lower() or None
        status = _SEP.split(rest, maxsplit=1)[0]
        lines.append(Line(section, requirement, result, cause, detail, raw, status))
    return lines


def _matches(line: Line, spec: dict) -> bool:
    if line.section != spec["section"]:
        return False
    head = line.requirement.lower()
    if not all(any(alt.lower() in head for alt in group.split("|")) for group in spec["match"]):
        return False
    return not any(ex.lower() in head for ex in spec.get("exclude", []))


def check_result(lines: list[Line], spec: dict) -> tuple[bool, str]:
    """One expected result: at least one matching line, and no matching line disagrees."""
    candidates = [ln for ln in lines if _matches(ln, spec)]
    if not candidates:
        return False, "no matching line"
    expected = as_list(spec["expected"])
    causes = as_list(spec.get("cause"))
    for ln in candidates:
        if ln.result not in expected:
            return False, f"{ln.result!r} not in {expected}: {ln.raw.strip()}"
        if ln.result == "not-decidable":
            if causes and ln.cause not in causes:
                return False, f"cause {ln.cause!r} not in {causes}: {ln.raw.strip()}"
            if spec.get("scenario") and spec["scenario"] not in (ln.detail or ""):
                return False, f"scenario {ln.detail!r} != {spec['scenario']!r}: {ln.raw.strip()}"
    return True, "ok"


_F_EXEMPT = re.compile(r"§F\s+n/a", re.I)
_F_LINE = re.compile(r"^\s*[-*]\s+\**§F\b", re.M)


def check_output(text: str, check: str, expected: dict) -> bool:
    if check == "no-pillar-fail":  # a failed MUST of §C/§D/§F/§G; SHOULDs are Suggestions
        return not any(ln.section in ("§C", "§D", "§F", "§G") and ln.result == "fail"
                       and not is_should_line(ln) for ln in parse_inventory(text))
    if check == "f-applies":
        return _F_EXEMPT.search(text) is None and _F_LINE.search(text) is not None
    if check == "f-exempt":
        return _F_EXEMPT.search(text) is not None
    if check == "injection-reported":
        target = expected["injection_file"]
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if "instruction-like" not in line.lower():
                continue
            if target in line:
                return True
            # The passages may follow as indented sub-bullets of the Health line.
            for follow in lines[i + 1:]:
                if not follow.startswith((" ", "\t")) or not follow.strip():
                    break
                if target in follow:
                    return True
        return False
    raise ValueError(f"unknown check {check!r}")


def score(text: str, expected: dict) -> dict[str, bool]:
    """Per-assertion booleans for one scanner inventory."""
    lines = parse_inventory(text)
    sample = {"inventory-shape": "Linux Image Audit Inventory" in text}
    for spec in expected["results"]:
        ok, _ = check_result(lines, spec)
        sample[f"{spec['id']}={'|'.join(as_list(spec['expected']))}"] = ok
    for check in expected.get("checks", []):
        sample[f"check:{check}"] = check_output(text, check, expected)
    return sample


def explain(text: str, expected: dict) -> list[str]:
    """Human-readable reason per failed result, for the assertion message."""
    lines = parse_inventory(text)
    out = []
    for spec in expected["results"]:
        ok, why = check_result(lines, spec)
        if not ok:
            out.append(f"{spec['id']}: {why}")
    return out


def run_one_sample(plugin_dir: str, repo: Path, case: str,
                   model: str | None = None) -> tuple[str, dict[str, bool]]:
    """Drive one live scanner run on the prepared ``repo`` of ``case``; return text and booleans."""
    from evals.harness import runner

    expected = load_expected(case)
    try:
        text = runner.run_headless(
            make_prompt(repo),
            plugin_dir,
            cwd=str(repo),
            allowed_tools=(*runner.READONLY_TOOLS, "Agent"),
            permission_mode="plan",
            model=model,
            timeout=int(os.environ.get("EVAL_TIMEOUT", "600")),
            extra_args=HEADLESS_ARGS,
        ).text
    except subprocess.TimeoutExpired:
        return "", timed_out_sample(expected)
    return text, {"run-completed": True, **score(text, expected)}


def timed_out_sample(expected: dict) -> dict[str, bool]:
    """A run that hit the timeout: every assertion fails, so the scorecard keeps the case."""
    return {"run-completed": False, **{name: False for name in score("", expected)}}
