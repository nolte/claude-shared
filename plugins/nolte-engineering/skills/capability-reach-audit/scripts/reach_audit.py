#!/usr/bin/env python3
"""Execute a repository's stored capability-reach probes and write the report.

The executor half of spec/project/capability-reach-audit/: it reads the approved
probe set from ``<repo>/project/reach-probes/``, decides per probe from the git
history whether the probe may run at all (declaration changed -> stale, probe
changed -> weakened), runs the environment and observation steps of the probes
that may, compares each raw observation against the probe's typed expectation,
and writes ``<repo>/.audits/capability-reach/<YYYY-MM-DD>.md``.

The runner, never the probe, decides the class. A probe file has no field in
which to state a verdict (schemas/reach-probe-v1.0.schema.yaml), and the
observation step's exit code alone is never read as success: only its stdout,
parsed as a count or a set, is the observation.

Deriving probes from declarations is not this script's job. The audited set is
the probe set on disk.

Dependencies: PyYAML and jsonschema. The probe set lives in the audited
repository, which has no pre-commit hook of this repository's, so the runner
validates every probe against the schema itself; a missing validator fails the
run with an install hint instead of skipping validation.

Exit codes:
  0  report written; every probe was classified (any class)
  1  runtime error (git failed, report not writable)
  2  usage error: bad arguments, or the target is not a local git working copy
  3  no probe set: project/reach-probes/ is absent or holds no probe file;
     the report says so, and it is never a clean result
  4  report written, and it carries findings (weakened or invalid probes)
  5  PyYAML or jsonschema is not installed

Usage:
  python reach_audit.py --repo ~/repos/github/kamerplanter
  python reach_audit.py --repo . --include-t2
"""
from __future__ import annotations

import argparse
import os
import posixpath
import re
import shlex
import signal
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

# --------------------------------------------------------------------------- #
# Paths inside the audited repository (R11, R12). Nothing else is ever written.
# --------------------------------------------------------------------------- #
PROBE_DIR = Path("project") / "reach-probes"
# Both suffixes are read: a probe saved as .yaml and silently skipped would drop an
# entry from the audited set, which the spec forbids.
PROBE_SUFFIXES = (".yml", ".yaml")
REPORT_DIR = Path(".audits") / "capability-reach"
SPEC_CONFIG = Path("spec") / ".spec-config.yml"

# --------------------------------------------------------------------------- #
# Bounds on everything the runner executes or reads back
# --------------------------------------------------------------------------- #
# git answers local history queries in milliseconds; a hang means a lock or a
# credential prompt, and waiting longer would not help.
GIT_TIMEOUT_SECONDS = 30
# An environment target may pull and start a container; a cold image pull on a slow
# link takes minutes, so the default is generous. Overridable per run.
DEFAULT_ENVIRONMENT_TIMEOUT_SECONDS = 900
# Default wall-clock bound on an observation step when the probe sets none.
DEFAULT_OBSERVE_TIMEOUT_SECONDS = 300
# An observation is a count or a set of names. Even a 10k-member set of long
# identifiers stays far below this; anything above it is a runaway command, so the
# probe is refused rather than parsed from a truncated stream.
MAX_OBSERVATION_BYTES = 4 * 1024 * 1024
# Cap on any tool output quoted in the report (a failed environment target's log).
MAX_REASON_CHARS = 600
TRUNCATION_MARKER = " [truncated]"
# How many missing set members a reason lists before summarising the rest.
MAX_LISTED_MEMBERS = 10

# Terminal and bidi control characters are stripped from every string quoted in
# the report: tool output is untrusted and must not reorder or forge report text.
_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f-\x9f\u202a-\u202e\u2066-\u2069]")
_WHITESPACE_CONTROLS = re.compile(r"[\t\n\v\f\r]")
_COUNT_RE = re.compile(r"^[0-9]+$")
_SHA_RE = re.compile(r"^[0-9a-f]{40}$")

# Exit codes
EXIT_OK = 0
EXIT_ERROR = 1
EXIT_USAGE = 2  # argparse's own code for a bad invocation; reused for semantic misuse
EXIT_NO_PROBES = 3
EXIT_FINDINGS = 4
EXIT_MISSING_DEPENDENCY = 5

INSTALL_HINT = (
    "reach_audit: dependency missing ({err}). The runner validates every probe "
    "against the probe schema and cannot do so without PyYAML and jsonschema.\n"
    "Install them with:  pip install 'PyYAML>=6' 'jsonschema>=4.21'"
)

# Classes (spec §Reporting: exactly one per entry).
REACHED = "reached"
PARTIAL = "partially reached"
NOT_REACHED = "not reached"
NOT_PROBED = "not probed"
CLASSES = (REACHED, PARTIAL, NOT_REACHED, NOT_PROBED)

# Change-detection states.
STATE_CLEAN = "clean"
STATE_STALE = "stale"
STATE_WEAKENED = "weakened"
STATE_UNMONITORED = "unmonitored"
# The anchor or the recorded derivation cannot be resolved against the history
# (unknown derived_from, a declaration path git never saw, no inherits[] entry).
STATE_UNRESOLVED = "unresolved"
# The probe file is not under version control, so it has no derivation baseline.
STATE_UNCOMMITTED = "uncommitted"
STATE_INVALID = "invalid"

DECLARATION_SOURCES = ("requirement", "endpoint", "capability", "inventory")

REASON_NOT_APPROVED = "not approved"
REASON_T2 = "tier T2 not requested"
REASON_STALE = "declaration changed since derivation"

# The structural part of schemas/reach-probe-v1.0.schema.yaml (annotations
# stripped). The schemas/ tree ships with the nolte-shared payload, not with this
# plugin, so the runner carries its own copy; tests/test_reach_audit.py fails when
# the two drift apart.
_TASK_NAME = {"type": "string", "pattern": "^[A-Za-z0-9_][A-Za-z0-9_:.-]*$"}
PROBE_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://github.com/nolte/claude-shared/blob/main/schemas/reach-probe-v1.0.schema.yaml",
    "type": "object",
    "required": ["id", "declaration", "tier", "expected", "derived_from", "observe"],
    "additionalProperties": False,
    "properties": {
        "id": {"type": "string", "pattern": "^[a-z0-9]+(-[a-z0-9]+)*$"},
        "summary": {"type": "string", "minLength": 1},
        "declaration": {"$ref": "#/$defs/Declaration"},
        "tier": {"type": "string", "enum": ["T0", "T1", "T2"]},
        "expected": {
            "oneOf": [
                {"$ref": "#/$defs/CountExpectation"},
                {"$ref": "#/$defs/SetExpectation"},
            ]
        },
        "approval": {"$ref": "#/$defs/Approval"},
        "derived_from": {"type": "string", "minLength": 1},
        "environment": {"type": "array", "uniqueItems": True, "items": {"$ref": "#/$defs/TaskName"}},
        "teardown": {"type": "array", "uniqueItems": True, "items": {"$ref": "#/$defs/TaskName"}},
        "observe": {"$ref": "#/$defs/Observe"},
    },
    "$defs": {
        "Declaration": {
            "type": "object",
            "required": ["source", "location"],
            "additionalProperties": False,
            "not": {"required": ["path", "inherited_spec"]},
            "dependentRequired": {"hub": ["inherited_spec"]},
            "properties": {
                "source": {"type": "string", "enum": list(DECLARATION_SOURCES)},
                "path": {"type": "string", "minLength": 1},
                "inherited_spec": {
                    "type": "string",
                    "pattern": "^([a-z0-9]+(-[a-z0-9]+)*/)?[a-z0-9]+(-[a-z0-9]+)*$",
                },
                "hub": {"type": "string", "minLength": 1},
                "location": {"type": "string", "minLength": 1},
            },
        },
        "CountExpectation": {
            "type": "object",
            "required": ["kind", "value", "unit"],
            "additionalProperties": False,
            "properties": {
                "kind": {"const": "count"},
                "value": {"type": "integer", "minimum": 1},
                "unit": {"type": "string", "minLength": 1},
            },
        },
        "SetExpectation": {
            "type": "object",
            "required": ["kind", "values"],
            "additionalProperties": False,
            "properties": {
                "kind": {"const": "set"},
                "values": {
                    "type": "array",
                    "minItems": 1,
                    "uniqueItems": True,
                    "items": {"type": "string", "minLength": 1},
                },
                "unit": {"type": "string", "minLength": 1},
            },
        },
        "Approval": {
            "type": "object",
            "required": ["approved_at", "approved_by"],
            "additionalProperties": False,
            "properties": {
                "approved_at": {
                    "type": "string",
                    "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}(:[0-9]{2})?Z$",
                },
                "approved_by": {"type": "string", "minLength": 1},
            },
        },
        "Observe": {
            "type": "object",
            "required": ["argv"],
            "additionalProperties": False,
            "properties": {
                "argv": {"type": "array", "minItems": 1, "items": {"type": "string", "minLength": 1}},
                "timeout_seconds": {"type": "integer", "minimum": 1, "maximum": 3600},
            },
        },
        "TaskName": _TASK_NAME,
    },
}


class AuditError(Exception):
    """Terminal error carrying an operator-facing message and an exit code."""

    def __init__(self, message: str, code: int = EXIT_ERROR) -> None:
        super().__init__(message)
        self.code = code


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #
def safe_text(value: object, limit: int = MAX_REASON_CHARS) -> str:
    """One line of untrusted text, control characters removed, length capped."""
    text = _WHITESPACE_CONTROLS.sub(" ", value if isinstance(value, str) else str(value))
    text = _CONTROL_CHARS.sub("", text)
    text = re.sub(r" {2,}", " ", text).strip()
    if len(text) > limit:
        text = text[:limit].rstrip() + TRUNCATION_MARKER
    return text


def cell(value: object) -> str:
    """A markdown table cell: safe text with the column separator escaped."""
    return safe_text(value).replace("|", "\\|") or "—"


def code_cell(command: str) -> str:
    """A command as an inline-code table cell that stays on one row.

    Line breaks inside an argument become a visible ``\\n`` rather than a space, so
    the rendered command does not read as a different one; a backtick in the
    command widens the code-span delimiter instead of ending it.
    """
    text = cell(command.replace("\r", "\\r").replace("\n", "\\n"))
    fence = "``" if "`" in text else "`"
    pad = " " if fence == "``" else ""
    return f"{fence}{pad}{text}{pad}{fence}"


def _load_dependencies() -> tuple[Any, Any]:
    try:
        import yaml
        from jsonschema import Draft202012Validator
    except ImportError as err:
        raise AuditError(INSTALL_HINT.format(err=err), code=EXIT_MISSING_DEPENDENCY) from err
    return yaml, Draft202012Validator


@dataclass
class CommandResult:
    returncode: int | None  # None: timed out or could not be started
    stdout: bytes
    stderr: bytes
    error: str | None = None  # why returncode is None
    oversized: bool = False


def run_command(argv: list[str], cwd: Path, timeout: float, max_stdout: int | None = None) -> CommandResult:
    """Run ``argv`` without a shell, bounded in time and in the bytes read back.

    Output goes to temporary files, not pipes: an environment target that leaves a
    server running in the background keeps inherited pipe ends open, and reading a
    pipe until EOF would then block for the server's whole lifetime.
    """
    if max_stdout is None:
        max_stdout = MAX_OBSERVATION_BYTES
    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
        try:
            proc = subprocess.Popen(  # noqa: S603 - argv list, no shell
                argv, cwd=cwd, stdin=subprocess.DEVNULL, stdout=out, stderr=err, start_new_session=True
            )
        except FileNotFoundError:
            return CommandResult(None, b"", b"", error=f"`{argv[0]}` not found on PATH")
        except OSError as exc:
            return CommandResult(None, b"", b"", error=f"`{argv[0]}` could not be started: {exc.strerror}")
        try:
            returncode: int | None = proc.wait(timeout=timeout)
            error = None
        except subprocess.TimeoutExpired:
            _kill_group(proc)
            returncode, error = None, f"timed out after {timeout:g}s"
        out.seek(0)
        stdout = out.read(max_stdout + 1)
        err.seek(0)
        stderr = err.read(MAX_REASON_CHARS * 4)
    oversized = len(stdout) > max_stdout
    return CommandResult(returncode, stdout[:max_stdout], stderr, error=error, oversized=oversized)


def _kill_group(proc: subprocess.Popen) -> None:
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        proc.kill()
    proc.wait()


def _output_tail(result: CommandResult) -> str:
    text = (result.stderr or b"").decode("utf-8", "replace").strip()
    if not text:
        text = result.stdout.decode("utf-8", "replace").strip()
    if len(text) > MAX_REASON_CHARS:
        text = "…" + text[-MAX_REASON_CHARS:]
    return safe_text(text) if text else "(no output)"


# --------------------------------------------------------------------------- #
# Git access (read-only)
# --------------------------------------------------------------------------- #
class Git:
    def __init__(self, repo: Path) -> None:
        self.repo = repo

    def run(self, *args: str) -> subprocess.CompletedProcess:
        try:
            return subprocess.run(  # noqa: S603 - fixed argv, no shell
                ["git", "-C", str(self.repo), *args],
                capture_output=True,
                text=True,
                timeout=GIT_TIMEOUT_SECONDS,
                check=False,
            )
        except FileNotFoundError as exc:
            raise AuditError("`git` not found on PATH; the runner reads the target's history with it.") from exc
        except subprocess.TimeoutExpired as exc:
            raise AuditError(f"`git {' '.join(args)}` timed out after {GIT_TIMEOUT_SECONDS}s.") from exc

    def out(self, *args: str) -> str:
        res = self.run(*args)
        if res.returncode != 0:
            raise AuditError(f"`git {' '.join(args)}` failed: {safe_text(res.stderr)}")
        return res.stdout

    def resolve_commit(self, rev: str) -> str | None:
        if rev.startswith("-"):
            return None
        res = self.run("rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}")
        return res.stdout.strip() if res.returncode == 0 else None

    def is_ancestor_or_equal(self, older: str, newer: str) -> bool:
        res = self.run("merge-base", "--is-ancestor", older, newer)
        if res.returncode not in (0, 1):
            raise AuditError(f"`git merge-base` failed: {safe_text(res.stderr)}")
        return res.returncode == 0

    def last_commit(self, path: str) -> str | None:
        return self.out("log", "-1", "--format=%H", "--", path).strip() or None

    def is_dirty(self, path: str) -> bool:
        return bool(self.out("status", "--porcelain", "--untracked-files=no", "--", path).strip())

    def file_history(self, path: str) -> list[tuple[str, str]]:
        """(commit, path at that commit), newest first, following renames.

        Following renames matters: without it, renaming a weakened probe would make
        the rename commit look like the probe's first appearance.
        """
        raw = self.out("log", "--follow", "--format=%x00%H", "--name-only", "--", path)
        history: list[tuple[str, str]] = []
        for block in raw.split("\x00")[1:]:
            lines = [ln for ln in block.splitlines() if ln.strip()]
            if lines:
                history.append((lines[0], lines[1] if len(lines) > 1 else path))
        return history

    def show(self, commit: str, path: str) -> str | None:
        res = self.run("show", f"{commit}:{path}")
        return res.stdout if res.returncode == 0 else None


def require_local_working_copy(raw: str) -> Path:
    """R13: the target must be a local git working copy, checked out, with history."""
    path = Path(raw).expanduser()
    if re.match(r"^[a-z][a-z0-9+.-]*://", raw) or re.match(r"^[\w.-]+@[\w.-]+:", raw):
        raise AuditError(
            f"--repo {raw!r} is a remote address. The audit executes probes against the "
            "checked-out system, so it needs a local working copy; clone the repository "
            "and pass its path.",
            code=EXIT_USAGE,
        )
    if not path.is_dir():
        raise AuditError(
            f"--repo {raw!r} is not a local directory. The audit runs only against a "
            "local working copy (there is no remote mode); clone the repository and pass its path.",
            code=EXIT_USAGE,
        )
    path = path.resolve()
    if not (path / ".git").exists():
        raise AuditError(
            f"--repo {raw!r} has no .git: it is not the root of a git working copy "
            "(a bare repository or a subdirectory is not accepted).",
            code=EXIT_USAGE,
        )
    git = Git(path)
    res = git.run("rev-parse", "--show-toplevel")
    if res.returncode != 0 or Path(res.stdout.strip()).resolve() != path:
        raise AuditError(
            f"--repo {raw!r}: `git rev-parse --show-toplevel` does not resolve to this "
            f"directory ({safe_text(res.stderr or res.stdout)}).",
            code=EXIT_USAGE,
        )
    if git.resolve_commit("HEAD") is None:
        raise AuditError(
            f"--repo {raw!r} has no commit yet; change detection reads the history, so "
            "the probe set must be committed first.",
            code=EXIT_USAGE,
        )
    return path


# --------------------------------------------------------------------------- #
# Probe loading and validation
# --------------------------------------------------------------------------- #
@dataclass
class Probe:
    file: str  # relative to the repository root, posix
    data: dict[str, Any] | None
    errors: list[str] = field(default_factory=list)

    @property
    def pid(self) -> str:
        if self.data and isinstance(self.data.get("id"), str):
            return self.data["id"]
        return Path(self.file).stem


def _schema_error_text(err: Any) -> str:
    loc = "/".join(str(p) for p in err.absolute_path) or "<root>"
    hint = ""
    if err.validator == "type" and err.validator_value == "string" and not isinstance(err.instance, str):
        hint = " (YAML reads unquoted timestamps and all-digit values as non-strings; quote the value)"
    if err.validator == "additionalProperties":
        hint = " (a probe carries no verdict or other undeclared field; the runner decides the class)"
    return f"{loc}: {err.message}{hint}"


def load_probes(repo: Path, yaml: Any, validator_cls: Any) -> list[Probe]:
    directory = repo / PROBE_DIR
    if not directory.is_dir():
        return []
    validator = validator_cls(PROBE_SCHEMA)
    probes: list[Probe] = []
    for file in sorted(p for p in directory.iterdir() if p.suffix in PROBE_SUFFIXES and p.is_file()):
        rel = file.relative_to(repo).as_posix()
        try:
            data = yaml.safe_load(file.read_text(encoding="utf-8"))
        except (yaml.YAMLError, UnicodeDecodeError) as exc:
            probes.append(Probe(rel, None, [f"not parseable as YAML: {safe_text(exc)}"]))
            continue
        errors = [
            _schema_error_text(e) for e in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
        ]
        if not errors and data["tier"] == "T0" and data.get("environment"):
            errors.append("environment: a T0 probe runs against what already exists and declares no environment")
        probes.append(Probe(rel, data if isinstance(data, dict) else None, errors))
    seen: dict[str, str] = {}
    for probe in probes:
        if probe.errors or not probe.data:
            continue
        if probe.pid in seen:
            probe.errors.append(f"id: duplicate probe id, already used by {seen[probe.pid]}")
        else:
            seen[probe.pid] = probe.file
    return probes


# --------------------------------------------------------------------------- #
# Change detection (R2, R3, R6)
# --------------------------------------------------------------------------- #
@dataclass
class ChangeState:
    state: str
    reason: str = ""


def _derived_from_of(text: str | None, yaml: Any) -> object:
    if text is None:
        return None
    try:
        doc = yaml.safe_load(text)
    except yaml.YAMLError:
        return None
    return doc.get("derived_from") if isinstance(doc, dict) else None


def probe_changes(git: Git, probe: Probe, yaml: Any) -> tuple[str | None, list[str], bool]:
    """The probe's derivation baseline, the commits that touched it since, and dirtiness.

    The baseline is the commit that recorded the probe's current ``derived_from``:
    walking the file's history newest first, the oldest commit of the unbroken run
    carrying today's value. The probe cannot be committed in the commit it was
    derived at, so comparing its latest commit against ``derived_from`` directly
    would flag every freshly committed probe; the recording commit is the approved
    state, and every later commit to the file is an unapproved change.
    """
    history = git.file_history(probe.file)
    if not history:
        return None, [], False
    current = probe.data["derived_from"] if probe.data else None
    run: list[str] = []
    for commit, path_then in history:
        if _derived_from_of(git.show(commit, path_then), yaml) != current:
            break
        run.append(commit)
    dirty = git.is_dirty(probe.file)
    if not run:
        # HEAD's version already differs from the working tree's derived_from: the
        # recording itself is uncommitted, and the newest commit is the baseline.
        return history[0][0], [], True
    return run[-1], run[:-1], dirty


def _repo_relative(path: str) -> str | None:
    """A normalised repository-relative path, or None when it leaves the repository."""
    if path.startswith("/") or re.match(r"^[a-z][a-z0-9+.-]*://", path):
        return None
    norm = posixpath.normpath(path)
    if norm == ".." or norm.startswith("../") or norm == ".":
        return None
    return norm


def _inherited_ref(repo: Path, declaration: dict[str, Any], yaml: Any) -> tuple[str | None, str]:
    config_path = repo / SPEC_CONFIG
    if not config_path.is_file():
        return None, f"{SPEC_CONFIG.as_posix()} not found, so the pinned ref of the inherited spec is unknown"
    try:
        config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        return None, f"{SPEC_CONFIG.as_posix()} is not parseable: {safe_text(exc)}"
    inherits = config.get("inherits") if isinstance(config, dict) else None
    entries = [e for e in inherits or [] if isinstance(e, dict)]
    hub = declaration.get("hub")
    if hub is not None:
        entries = [e for e in entries if e.get("source") == hub]
    if not entries:
        where = f" for hub {hub!r}" if hub else ""
        return None, f"{SPEC_CONFIG.as_posix()} declares no inherits[] entry{where}"
    if len(entries) > 1:
        return None, f"{SPEC_CONFIG.as_posix()} lists several inherits[] entries; set declaration.hub"
    ref = entries[0].get("ref")
    if not isinstance(ref, str) or not ref:
        return None, f"{SPEC_CONFIG.as_posix()} inherits[] entry carries no ref"
    return ref, ""


def detect_change(repo: Path, git: Git, probe: Probe, yaml: Any) -> ChangeState:
    """Classify one valid probe's change state from the target's history."""
    data = probe.data or {}
    derived_from = data["derived_from"]
    baseline, later, dirty = probe_changes(git, probe, yaml)
    if baseline is None:
        return ChangeState(
            STATE_UNCOMMITTED,
            "probe file is not committed; the approved set must be under version control, "
            "and an uncommitted probe has no derivation to compare against",
        )

    # The probe itself: any change after the recorded derivation is a weakening,
    # whether or not the declaration moved too (spec: "whether or not both changed
    # together"). Checked first so a combined change is surfaced as a finding.
    if later or dirty:
        parts = []
        if later:
            parts.append(f"probe changed in {', '.join(c[:12] for c in reversed(later))} after its derivation was recorded in {baseline[:12]}")
        if dirty:
            parts.append("probe file has uncommitted changes")
        return ChangeState(STATE_WEAKENED, "; ".join(parts))

    declaration = data["declaration"]
    if "inherited_spec" in declaration:
        ref, why = _inherited_ref(repo, declaration, yaml)
        if ref is None:
            return ChangeState(STATE_UNRESOLVED, why)
        if ref != derived_from:
            return ChangeState(STATE_STALE, f"{REASON_STALE}: pinned ref moved from {derived_from} to {ref}")
        return ChangeState(STATE_CLEAN)

    raw_path = declaration.get("path")
    rel = _repo_relative(raw_path) if raw_path else None
    if rel is None:
        where = f"anchor {raw_path!r} lies outside the repository" if raw_path else "anchor has no path"
        return ChangeState(STATE_UNMONITORED, f"{where}; change is not monitored, re-derive on request")

    derived_commit = git.resolve_commit(derived_from)
    if derived_commit is None:
        return ChangeState(STATE_UNRESOLVED, f"derived_from {derived_from!r} is not a commit of the target repository")
    if not git.is_ancestor_or_equal(derived_commit, "HEAD"):
        return ChangeState(STATE_UNRESOLVED, f"derived_from {derived_from[:12]} is not in the history of HEAD")
    declaration_commit = git.last_commit(rel)
    if declaration_commit is None:
        return ChangeState(STATE_UNRESOLVED, f"declaration {rel} has no history in the target repository")
    if git.is_dirty(rel):
        return ChangeState(STATE_STALE, f"{REASON_STALE}: {rel} has uncommitted changes")
    # A rename or a deletion is itself the declaration's latest commit, so a moved
    # or split declaration reads as changed, which is the safe answer.
    if not git.is_ancestor_or_equal(declaration_commit, derived_commit):
        return ChangeState(STATE_STALE, f"{REASON_STALE}: {rel} last changed in {declaration_commit[:12]}")
    return ChangeState(STATE_CLEAN)


# --------------------------------------------------------------------------- #
# Observation and classification
# --------------------------------------------------------------------------- #
@dataclass
class Outcome:
    cls: str
    reach: str = ""
    reason: str = ""


def parse_observation(stdout: bytes, kind: str) -> tuple[int | set[str] | None, str]:
    try:
        text = stdout.decode("utf-8")
    except UnicodeDecodeError:
        return None, "observation is not UTF-8 text"
    if kind == "count":
        value = text.strip()
        if not _COUNT_RE.match(value):
            return None, f"observation {safe_text(value, 80)!r} is not a single non-negative integer"
        return int(value), ""
    return {ln.strip() for ln in text.splitlines() if ln.strip()}, ""


def classify(expected: dict[str, Any], observed: int | set[str]) -> Outcome:
    """Compare a raw observation with the typed expectation. Only the runner does this."""
    if expected["kind"] == "count":
        want, unit = expected["value"], expected["unit"]
        assert isinstance(observed, int)
        reach = f"{observed}/{want} {unit}"
        if observed > want:
            # More than was declared is no verdict about the declaration: the probe
            # measures something else, or the declaration is out of date.
            return Outcome(NOT_PROBED, reach, f"observation {observed} exceeds the declared {want}; re-derive the probe")
        if observed == want:
            return Outcome(REACHED, reach)
        if observed == 0:
            return Outcome(NOT_REACHED, reach)
        return Outcome(PARTIAL, reach)
    want_set = set(expected["values"])
    unit = expected.get("unit", "members")
    assert isinstance(observed, set)
    hit = want_set & observed
    reach = f"{len(hit)}/{len(want_set)} {unit}"
    missing = sorted(want_set - observed)
    listed = ", ".join(missing[:MAX_LISTED_MEMBERS]) + (" …" if len(missing) > MAX_LISTED_MEMBERS else "")
    if not missing:
        return Outcome(REACHED, reach)
    if not hit:
        return Outcome(NOT_REACHED, reach, f"missing: {listed}")
    return Outcome(PARTIAL, reach, f"missing: {listed}")


def execute(repo: Path, data: dict[str, Any], env_timeout: float) -> tuple[Outcome, list[str]]:
    """Environment, observation, teardown. Returns the outcome and teardown notes."""
    notes: list[str] = []
    try:
        for name in data.get("environment", []):
            res = run_command(["task", name], repo, env_timeout, max_stdout=MAX_REASON_CHARS * 4)
            if res.returncode != 0:
                status = res.error or f"exit {res.returncode}"
                detail = "" if res.returncode is None and not (res.stderr or res.stdout) else f": {_output_tail(res)}"
                # R10: an environment that did not come up says nothing about reach.
                return Outcome(NOT_PROBED, reason=f"environment target `{name}` failed ({status}){detail}"), notes
        observe = data["observe"]
        argv = observe["argv"]
        res = run_command(argv, repo, observe.get("timeout_seconds", DEFAULT_OBSERVE_TIMEOUT_SECONDS))
        if res.returncode is None:
            return Outcome(NOT_PROBED, reason=f"observation step {res.error}"), notes
        if res.oversized:
            return Outcome(NOT_PROBED, reason=f"observation exceeds {MAX_OBSERVATION_BYTES} bytes"), notes
        if res.returncode != 0:
            return Outcome(NOT_PROBED, reason=f"observation step exited {res.returncode}: {_output_tail(res)}"), notes
        observed, why = parse_observation(res.stdout, data["expected"]["kind"])
        if observed is None:
            return Outcome(NOT_PROBED, reason=why), notes
        return classify(data["expected"], observed), notes
    finally:
        for name in data.get("teardown", []):
            res = run_command(["task", name], repo, env_timeout, max_stdout=MAX_REASON_CHARS * 4)
            if res.returncode != 0:
                notes.append(f"teardown `{name}` failed ({res.error or f'exit {res.returncode}'}): {_output_tail(res)}")


# --------------------------------------------------------------------------- #
# The run
# --------------------------------------------------------------------------- #
@dataclass
class Entry:
    probe: Probe
    change: ChangeState
    outcome: Outcome
    executed_at: str | None = None
    notes: list[str] = field(default_factory=list)


def evaluate(repo: Path, git: Git, probe: Probe, yaml: Any, include_t2: bool, env_timeout: float, clock: Callable[[], datetime]) -> Entry:
    if probe.errors:
        return Entry(probe, ChangeState(STATE_INVALID), Outcome(NOT_PROBED, reason="probe fails the probe schema: " + "; ".join(probe.errors)))
    data = probe.data or {}
    change = detect_change(repo, git, probe, yaml)
    if change.state == STATE_WEAKENED:
        return Entry(probe, change, Outcome(NOT_PROBED, reason=f"weakened: {change.reason}"))
    if change.state in (STATE_STALE, STATE_UNRESOLVED, STATE_UNCOMMITTED):
        return Entry(probe, change, Outcome(NOT_PROBED, reason=change.reason))
    if "approval" not in data:
        return Entry(probe, change, Outcome(NOT_PROBED, reason=REASON_NOT_APPROVED))
    if data["tier"] == "T2" and not include_t2:
        return Entry(probe, change, Outcome(NOT_PROBED, reason=REASON_T2))
    executed_at = clock().strftime("%Y-%m-%dT%H:%M:%SZ")
    outcome, notes = execute(repo, data, env_timeout)
    return Entry(probe, change, outcome, executed_at, notes)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def report_path(repo: Path, today: str) -> Path:
    """R12: the one file the runner writes. A symlinked ``.audits`` must not redirect it."""
    resolved_parent = (repo / REPORT_DIR).resolve()
    if not resolved_parent.is_relative_to(repo):
        raise AuditError(
            f"{REPORT_DIR.as_posix()} resolves outside the repository ({resolved_parent}); refusing to write there."
        )
    return resolved_parent / f"{today}.md"


def render(repo: Path, head: str, entries: list[Entry], include_t2: bool, run_at: str, empty_reason: str | None) -> str:
    lines = [f"# Capability reach audit — {repo.name}", ""]
    lines.append(
        "<!-- Generated by reach_audit.py on every run; never edit by hand "
        "(spec/project/capability-reach-audit/). -->"
    )
    lines.append("")
    total = len(entries)
    not_probed = sum(1 for e in entries if e.outcome.cls == NOT_PROBED)
    if empty_reason is not None:
        lines += [
            "**Not probed: all. No probe set.**",
            "",
            f"{empty_reason} The audited set is the probe set, so this run measured nothing. "
            "This is not a clean result: derive and approve probes from the repository's "
            "declarations (requirements, endpoints, documented capabilities, inventories) first.",
            "",
            f"- Run at: {run_at} (UTC), HEAD {head[:12]}",
        ]
        return "\n".join(lines) + "\n"

    lines += [f"**Not probed: {not_probed} of {total} probes.**", ""]
    lines += ["## Provenance", ""]
    lines.append(
        f"- Audited set: the {total} probe file(s) on disk under `{PROBE_DIR.as_posix()}/` at HEAD "
        f"{head[:12]}. This run executed stored probes; it read no declaration to find new entries."
    )
    by_source = {s: 0 for s in DECLARATION_SOURCES}
    for e in entries:
        src = (e.probe.data or {}).get("declaration", {}).get("source") if isinstance((e.probe.data or {}).get("declaration"), dict) else None
        if src in by_source:
            by_source[src] += 1
    covered = ", ".join(f"{s} ({n})" for s, n in by_source.items() if n)
    uncovered = [s for s, n in by_source.items() if not n]
    lines.append(f"- Declaration sources covered by the probe set: {covered or 'none'}.")
    if uncovered:
        lines.append(f"- Declaration sources with no probe: {', '.join(uncovered)}. This audit can't speak about them.")
    lines.append(f"- Tier T2: {'requested (--include-t2)' if include_t2 else 'not requested; every T2 probe is not probed'}.")
    lines.append(f"- Run at: {run_at} (UTC).")
    lines.append("")

    lines += ["## Reach per tier", "", "| Tier | reached | partially reached | not reached | not probed |", "|---|---|---|---|---|"]
    for tier in ("T0", "T1", "T2", "invalid"):
        subset = [e for e in entries if ((e.probe.data or {}).get("tier") if not e.probe.errors else "invalid") == tier]
        if tier == "invalid" and not subset:
            continue
        counts = [sum(1 for e in subset if e.outcome.cls == c) for c in CLASSES]
        lines.append(f"| {tier} | " + " | ".join(str(c) for c in counts) + " |")
    lines.append("")

    findings = [e for e in entries if e.change.state in (STATE_WEAKENED, STATE_INVALID)]
    lines += ["## Findings", ""]
    if findings:
        for e in findings:
            kind = "weakened" if e.change.state == STATE_WEAKENED else "invalid probe"
            detail = e.change.reason if e.change.state == STATE_WEAKENED else "; ".join(e.probe.errors)
            lines.append(f"- **{kind}** `{cell(e.probe.pid)}` ({cell(e.probe.file)}): {safe_text(detail)}")
    else:
        lines.append("- none")
    lines.append("")

    lines += [
        "## Probes",
        "",
        "| Probe | Class | Reach | Measured by | Tier | Executed (UTC) | derived_from | Change detection | Declaration | Reason |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for e in entries:
        data = e.probe.data or {}
        decl = data.get("declaration") if isinstance(data.get("declaration"), dict) else {}
        anchor = decl.get("path") or (f"inherited {decl['inherited_spec']}" if decl.get("inherited_spec") else "external")
        declaration = f"{decl.get('source', '?')}: {anchor} ({decl.get('location', '?')})" if decl else "—"
        observe = data.get("observe") if isinstance(data.get("observe"), dict) else {}
        argv = observe.get("argv") if isinstance(observe.get("argv"), list) else None
        measured = code_cell(shlex.join(str(a) for a in argv)) if argv else "—"
        change = e.change.state + (f": {e.change.reason}" if e.change.reason and e.change.state in (STATE_UNMONITORED,) else "")
        reason = "; ".join([r for r in [e.outcome.reason, *e.notes] if r])
        derived = str(data.get("derived_from", "—"))
        derived = derived[:12] if _SHA_RE.match(derived) else derived
        row = [
            cell(e.probe.pid), e.outcome.cls, cell(e.outcome.reach), measured,
            cell(data.get("tier", "—")), e.executed_at or "not executed", cell(derived), cell(change),
            cell(declaration), cell(reason),
        ]
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines) + "\n"


def run(repo_arg: str, include_t2: bool = False, env_timeout: float = DEFAULT_ENVIRONMENT_TIMEOUT_SECONDS,
        clock: Callable[[], datetime] = _utc_now) -> tuple[int, Path]:
    yaml, validator_cls = _load_dependencies()
    repo = require_local_working_copy(repo_arg)
    git = Git(repo)
    head = git.resolve_commit("HEAD") or ""
    now = clock()
    run_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    out = report_path(repo, now.strftime("%Y-%m-%d"))

    probes = load_probes(repo, yaml, validator_cls)
    empty_reason = None
    if not (repo / PROBE_DIR).is_dir():
        empty_reason = f"`{PROBE_DIR.as_posix()}/` does not exist in this repository."
    elif not probes:
        empty_reason = f"`{PROBE_DIR.as_posix()}/` holds no probe file (*.yml, *.yaml)."

    entries = [evaluate(repo, git, p, yaml, include_t2, env_timeout, clock) for p in probes]
    text = render(repo, head, entries, include_t2, run_at, empty_reason)
    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    except OSError as exc:
        raise AuditError(f"cannot write the report {out}: {exc.strerror}") from exc

    if empty_reason is not None:
        return EXIT_NO_PROBES, out
    if any(e.change.state in (STATE_WEAKENED, STATE_INVALID) for e in entries):
        return EXIT_FINDINGS, out
    return EXIT_OK, out


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Execute the stored capability-reach probes of a local repository and write the report.",
        epilog="Exit codes: 0 report written, 1 runtime error, 2 usage error or non-local target, "
        "3 no probe set, 4 report written with findings, 5 PyYAML/jsonschema missing.",
    )
    parser.add_argument("--repo", required=True, help="Path to the local git working copy to audit (R13: no remote mode).")
    parser.add_argument("--include-t2", action="store_true", help="Also execute T2 probes (full stack with seeded data).")
    parser.add_argument(
        "--environment-timeout",
        type=float,
        default=DEFAULT_ENVIRONMENT_TIMEOUT_SECONDS,
        metavar="SECONDS",
        help=f"Wall-clock bound per environment or teardown target (default {DEFAULT_ENVIRONMENT_TIMEOUT_SECONDS}).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.environment_timeout <= 0:
        sys.stderr.write("reach_audit: --environment-timeout must be positive.\n")
        return EXIT_USAGE
    try:
        code, out = run(args.repo, args.include_t2, args.environment_timeout)
    except AuditError as exc:
        sys.stderr.write(f"reach_audit: {exc}\n")
        return exc.code
    messages = {
        EXIT_OK: "report written",
        EXIT_NO_PROBES: "no probe set; the report says so (not a clean result)",
        EXIT_FINDINGS: "report written with findings (weakened or invalid probes)",
    }
    print(f"reach_audit: {messages[code]}: {out}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
