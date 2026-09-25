#!/usr/bin/env python3
"""Execute a repository's stored capability-reach probes and write the report.

The executor half of spec/project/capability-reach-audit/: it reads the approved
probe set from ``<repo>/project/reach-probes/``, decides per probe from the git
history whether the probe may run at all (declaration changed -> stale, probe
changed -> weakened), runs the environment and observation steps of the probes
that may, compares each raw observation against the probe's typed expectation,
and writes ``<repo>/.audits/capability-reach/<YYYY-MM-DD>.md``.

The runner, never the probe, decides the class. A probe file has no field in
which to state a verdict (schemas/reach-probe-v1.2.schema.yaml), and the
observation step's exit code alone is never read as success: only its stdout,
parsed as a count or a set, is the observation.

Deriving probes from declarations is not this script's job. The audited set is
what the derivation left on disk: the probe files, plus the entries of the
not-constructible manifest ``project/reach-probes/_not-constructible.yml``
(schemas/reach-not-constructible-v1.0.schema.yaml), which lists every declared
entry no probe could be constructed for. Each manifest entry is reported not
probed with reason ``not constructible: <code>`` and counts in the headline; an
absent manifest is stated in the headline and the provenance, because the runner
can't tell "every entry was constructible" from "the manifest was never written".

Every file the runner reads from the target's working tree (probe files, the
manifest, spec/.spec-config.yml) must be a regular file that resolves inside the
repository: a symlink is refused and never followed, so a probe set cannot pull
an operator's private files into the committed report. The report itself is
opened with O_NOFOLLOW.

Dependencies: PyYAML and jsonschema. The probe set lives in the audited
repository, which has no pre-commit hook of this repository's, so the runner
validates every probe against the schema itself; a missing validator fails the
run with an install hint instead of skipping validation.

Exit codes:
  0  report written; at least one probe file, every entry classified (any
     class), no finding
  1  runtime error (git failed, report not writable)
  2  usage error: bad arguments, or the target is not a local git working copy
  3  no probe file: project/reach-probes/ is absent or holds no probe file
     besides the manifest, so nothing was executed and it is never a clean
     result. A manifest listing entries does not change the code: the report
     then counts them (every entry not probed) instead of saying there is no
     probe set, but a run whose only entries are not constructible measured
     nothing either.
  4  report written, and it carries findings: weakened or invalid probes
     (a symlinked probe file included), an approval whose observation digest no
     longer matches the observation step, an unreadable manifest or an invalid
     manifest entry, a manifest id listed twice, or an id that is both a probe
     file and a manifest entry. Takes precedence over 3.
  5  PyYAML or jsonschema is not installed

Usage:
  python reach_audit.py --repo ~/repos/github/kamerplanter
  python reach_audit.py --repo . --include-t2
"""
from __future__ import annotations

import argparse
import copy
import errno
import hashlib
import json
import os
import posixpath
import re
import selectors
import shlex
import signal
import subprocess
import sys
import time
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
# The companion manifest of entries no probe could be constructed for. It lives
# in the probe directory, so the probe loader skips exactly this name.
MANIFEST_NAME = "_not-constructible.yml"
MANIFEST_PATH = PROBE_DIR / MANIFEST_NAME
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

# How often a running child is checked while its output is read.
POLL_SECONDS = 0.05
# Bytes read from a child's pipe per system call.
READ_CHUNK = 64 * 1024

# Terminal, bidi, zero-width, and line-separator characters are stripped from
# every string quoted in the report or on stderr: tool output and file names are
# untrusted and must not reorder, hide, or forge report text.
_CONTROL_CHARS = re.compile(
    r"[\x00-\x1f\x7f-\x9f\u061c\u200b-\u200f\u2028-\u202e\u2060\u2066-\u2069\ufeff]"
)
_WHITESPACE_CONTROLS = re.compile(r"[\t\n\v\f\r]")
# Markdown that could open a comment, a raw HTML block, or a link in a report cell.
_MARKDOWN_SPECIALS = re.compile(r"([\\<>\[\]])")
# At most 18 digits: always below int_max_str_digits, and a count that large is
# a runaway command, not a measurement.
_COUNT_RE = re.compile(r"^[0-9]{1,18}$")
_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
# A content anchor (probe schema v1.1): the git blob hash of an in-repository
# declaration file at derivation. It names no commit, so a squash merge that
# discards the derivation commit leaves it resolvable.
BLOB_PREFIX = "blob:"
_BLOB_ANCHOR_RE = re.compile(r"^blob:[0-9a-f]{40}$")
BLOB_FORM = "blob:<40 hex digits>"
# A section anchor (probe schema v1.2): the SHA-256 over the locators and digests
# in declaration.sections (section_anchor()). An edit elsewhere in the Markdown
# declaration leaves every anchored section, and so the probe, unchanged.
SECTIONS_PREFIX = "sections:"
_SECTIONS_ANCHOR_RE = re.compile(r"^sections:[0-9a-f]{64}$")
SECTIONS_FORM = "sections:<64 hex digits>"
SECTION_KINDS = ("heading", "row")
# approval.mode: a re-confirmation re-approves an unchanged probe after its
# declaration changed; anything but the anchor and the approval moving is weakened.
MODE_RECONFIRMED = "reconfirmed"

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
# A manifest entry: no probe exists, so there is nothing to detect a change on.
STATE_NOT_CONSTRUCTIBLE = "not constructible"
# One id is both a probe file and a manifest entry.
STATE_CONTRADICTION = "contradiction"
# The approval's observation digest does not match the current observation step.
STATE_APPROVAL_MISMATCH = "approval mismatch"

DECLARATION_SOURCES = ("requirement", "endpoint", "capability", "inventory")

REASON_NOT_APPROVED = "not approved"
REASON_T2 = "tier T2 not requested"
REASON_STALE = "declaration changed since derivation"
REASON_NOT_CONSTRUCTIBLE = "not constructible"
REASON_DIGEST_MISMATCH = "approval does not cover the current observation step"
NOTE_NO_DIGEST = "approval carries no observation digest"
REASON_SILENT = "observation step printed nothing"
NOTE_RECONFIRMED = "approval is a re-confirmation, not a re-derivation"
PROVENANCE_RECONFIRMED = "Probes whose approval is a re-confirmation rather than a re-derivation"

NOT_CONSTRUCTIBLE_REASONS = (
    "scope_not_countable",
    "needs_model_judgement",
    "effect_in_third_party",
    "missing_environment_target",
    "missing_observation_helper",
)
# Per-tier table bucket of the entries that have no tier because they have no probe.
TIER_NONE = "none (not constructible)"

# The structural part of schemas/reach-probe-v1.2.schema.yaml (annotations
# stripped). The schemas/ tree ships with the nolte-shared payload, not with this
# plugin, so the runner carries its own copy; tests/test_reach_audit.py fails when
# the two drift apart.
_TASK_NAME = {"type": "string", "pattern": "^[A-Za-z0-9_][A-Za-z0-9_:.-]*$"}
PROBE_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://github.com/nolte/claude-shared/blob/main/schemas/reach-probe-v1.2.schema.yaml",
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
            "dependentRequired": {"hub": ["inherited_spec"], "sections": ["path"]},
            "properties": {
                "source": {"type": "string", "enum": list(DECLARATION_SOURCES)},
                "path": {"type": "string", "minLength": 1},
                "inherited_spec": {
                    "type": "string",
                    "pattern": "^([a-z0-9]+(-[a-z0-9]+)*/)?[a-z0-9]+(-[a-z0-9]+)*$",
                },
                "hub": {"type": "string", "minLength": 1},
                "location": {"type": "string", "minLength": 1},
                "sections": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/Section"}},
            },
        },
        "Section": {
            "type": "object",
            "required": ["digest"],
            "additionalProperties": False,
            "oneOf": [{"required": ["heading"]}, {"required": ["row"]}],
            "properties": {
                "heading": {"type": "string", "pattern": r"^[^\s]*[^\s.]$"},
                "row": {"type": "string", "pattern": r"^[^|\s]([^|]*[^|\s])?$"},
                "digest": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
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
                "observation_digest": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "mode": {"type": "string", "enum": ["derived", MODE_RECONFIRMED]},
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

# The manifest's declaration is the probe's without the v1.2 section locators:
# a not-constructible entry has no probe to anchor on sections.
_MANIFEST_DECLARATION: dict[str, Any] = copy.deepcopy(PROBE_SCHEMA["$defs"]["Declaration"])
del _MANIFEST_DECLARATION["properties"]["sections"]
del _MANIFEST_DECLARATION["dependentRequired"]["sections"]

# The structural part of schemas/reach-not-constructible-v1.0.schema.yaml, embedded
# for the same reason as PROBE_SCHEMA and pinned to it by the same parity test.
NOT_CONSTRUCTIBLE_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://github.com/nolte/claude-shared/blob/main/schemas/reach-not-constructible-v1.0.schema.yaml",
    "type": "object",
    "required": ["entries"],
    "additionalProperties": False,
    "properties": {
        "entries": {"type": "array", "items": {"$ref": "#/$defs/NotConstructibleEntry"}},
    },
    "$defs": {
        "NotConstructibleEntry": {
            "type": "object",
            "required": ["id", "declaration", "reason", "derived_from", "recorded_at"],
            "additionalProperties": False,
            "properties": {
                "id": {"type": "string", "pattern": "^[a-z0-9]+(-[a-z0-9]+)*$"},
                "declaration": {"$ref": "#/$defs/Declaration"},
                "reason": {"type": "string", "enum": list(NOT_CONSTRUCTIBLE_REASONS)},
                "detail": {"type": "string", "minLength": 1},
                "derived_from": {"type": "string", "minLength": 1},
                "recorded_at": {
                    "type": "string",
                    "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}(:[0-9]{2})?Z$",
                },
            },
        },
        "Declaration": _MANIFEST_DECLARATION,
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


def md_text(value: object, limit: int = MAX_REASON_CHARS) -> str:
    """Safe text for Markdown prose: ``\\ < > [ ]`` escaped.

    Untrusted text must not open an HTML comment (``<!--`` would swallow the rest
    of the report), a raw HTML block, or a link. The backslash is escaped first,
    so an input backslash cannot cancel the escape added after it.
    """
    return _MARKDOWN_SPECIALS.sub(r"\\\1", safe_text(value, limit))


def cell(value: object) -> str:
    """A markdown table cell: Markdown-safe text with the column separator escaped."""
    return md_text(value).replace("|", "\\|") or "—"


def code_span(text: str, table: bool = False) -> str:
    """``text`` as an inline code span that no backtick inside it can end.

    The fence is one backtick longer than the longest backtick run in the text,
    and padded with a space when the text holds a backtick, so the span's own
    delimiters are the only ones. Backslash escapes are literal inside a code
    span, so only the table's column separator is escaped (``table=True``).
    """
    body = safe_text(text)
    if table:
        body = body.replace("|", "\\|")
    runs = [len(r) for r in re.findall(r"`+", body)]
    fence = "`" * (max(runs, default=0) + 1)
    pad = " " if runs else ""
    return f"{fence}{pad}{body}{pad}{fence}"


def code_cell(command: str) -> str:
    """A command as an inline-code table cell that stays on one row.

    Line breaks inside an argument become a visible ``\\n`` rather than a space, so
    the rendered command does not read as a different one; a backtick in the
    command widens the code-span delimiter instead of ending it.
    """
    return code_span(command.replace("\r", "\\r").replace("\n", "\\n"), table=True)


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


def run_command(argv: list[str], cwd: Path, timeout: float, max_stdout: int | None = None,
                kill_on_overflow: bool = False) -> CommandResult:
    """Run ``argv`` without a shell, bounded in time and in the bytes it may emit.

    Output is read from pipes in chunks and never spooled to disk, so a runaway
    command cannot fill the temp directory. At most ``max_stdout`` bytes of
    stdout and a reason-sized prefix of stderr are kept; the rest is read and
    discarded so the child never blocks on a full pipe. With
    ``kill_on_overflow`` (the observation step, whose stdout is the measurement)
    the process group is killed as soon as stdout passes the bound.

    Reading stops when the direct child exits, not at EOF: an environment target
    that leaves a server running in the background keeps inherited pipe ends open,
    and waiting for EOF would then block for the server's whole lifetime.

    The child runs in its own session, so a Ctrl-C at the terminal does not reach
    it; any exception while it runs, KeyboardInterrupt included, kills its process
    group before propagating instead of orphaning it.
    """
    if max_stdout is None:
        max_stdout = MAX_OBSERVATION_BYTES
    try:
        proc = subprocess.Popen(  # noqa: S603 - argv list, no shell
            argv, cwd=cwd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            start_new_session=True,
        )
    except FileNotFoundError:
        return CommandResult(None, b"", b"", error=f"`{argv[0]}` not found on PATH")
    except OSError as exc:
        return CommandResult(None, b"", b"", error=f"`{argv[0]}` could not be started: {exc.strerror}")
    assert proc.stdout is not None and proc.stderr is not None
    out_fd, err_fd = proc.stdout.fileno(), proc.stderr.fileno()
    kept = {out_fd: bytearray(), err_fd: bytearray()}
    limits = {out_fd: max_stdout + 1, err_fd: MAX_REASON_CHARS * 4}
    seen_stdout = 0
    sel = selectors.DefaultSelector()
    returncode: int | None = None
    error: str | None = None

    def pump(wait: float) -> bool:
        """Read one chunk from each ready pipe; True when anything was kept or closed."""
        nonlocal seen_stdout
        progressed = False
        for key, _ in sel.select(timeout=wait):
            chunk = os.read(key.fd, READ_CHUNK)
            if not chunk:
                sel.unregister(key.fd)
                progressed = True
                continue
            if key.fd == out_fd:
                seen_stdout += len(chunk)
            room = limits[key.fd] - len(kept[key.fd])
            if room > 0:
                kept[key.fd] += chunk[:room]
                progressed = True
        return progressed

    try:
        sel.register(out_fd, selectors.EVENT_READ)
        sel.register(err_fd, selectors.EVENT_READ)
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                _kill_group(proc)
                error = f"timed out after {timeout:g}s"
                break
            if kill_on_overflow and seen_stdout > max_stdout:
                _kill_group(proc)
                error = f"printed more than {max_stdout} bytes"
                break
            wait = min(remaining, POLL_SECONDS)
            if sel.get_map():
                pump(wait)
                wait = 0.0
            try:
                returncode = proc.wait(timeout=wait)
            except subprocess.TimeoutExpired:
                continue
            # The child exited: take what is already buffered, without waiting for
            # an EOF that a background process holding the pipe may never send.
            while sel.get_map() and time.monotonic() < deadline and pump(0):
                pass
            break
    except BaseException:
        _kill_group(proc)
        raise
    finally:
        sel.close()
        proc.stdout.close()
        proc.stderr.close()
    oversized = seen_stdout > max_stdout
    return CommandResult(returncode, bytes(kept[out_fd][:max_stdout]), bytes(kept[err_fd]), error=error,
                         oversized=oversized)


def _kill_group(proc: subprocess.Popen) -> None:
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        if proc.poll() is None:
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
        """Run git read-only. Output is decoded as UTF-8 with replacement: a historical
        probe revision or a path that is not UTF-8 must yield a classified entry, not
        a crash. core.quotePath is off so non-ASCII paths come back verbatim and can
        be passed to ``git show`` again."""
        try:
            return subprocess.run(  # noqa: S603 - fixed argv, no shell
                ["git", "-c", "core.quotePath=false", "-C", str(self.repo), *args],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=GIT_TIMEOUT_SECONDS,
                check=False,
            )
        except FileNotFoundError as exc:
            raise AuditError("`git` not found on PATH; the runner reads the target's history with it.") from exc
        except subprocess.TimeoutExpired as exc:
            raise AuditError(f"`git {safe_text(' '.join(args))}` timed out after {GIT_TIMEOUT_SECONDS}s.") from exc

    def out(self, *args: str) -> str:
        res = self.run(*args)
        if res.returncode != 0:
            # The arguments carry file names from the target's working tree.
            raise AuditError(f"`git {safe_text(' '.join(args))}` failed: {safe_text(res.stderr)}")
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

    def last_commit(self, path: str, rev: str = "HEAD") -> str | None:
        """The latest commit reachable from ``rev`` (a resolved commit) that touched ``path``."""
        return self.out("log", "-1", "--format=%H", rev, "--", path).strip() or None

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

    def entry_at(self, commit: str, path: str) -> tuple[str, str] | None:
        """``(type, hash)`` of the tree entry ``path`` at ``commit``, or None when absent.

        ``ls-tree`` with literal pathspecs rather than ``rev-parse <commit>:<path>``,
        so a path is never parsed as revision syntax; the hash is the same. The type
        is ``blob`` for a file or a symlink (whose blob is the link text), ``tree``
        for a directory and ``commit`` for a submodule.
        """
        res = self.run("--literal-pathspecs", "ls-tree", "-z", commit, "--", path)
        if res.returncode != 0:
            return None
        for record in res.stdout.split("\x00"):
            meta, _, name = record.partition("\t")
            parts = meta.split()
            if name == path and len(parts) == 3:
                return parts[1], parts[2]
        return None

    def blob_at(self, commit: str, path: str) -> str | None:
        """The blob hash of ``path`` at ``commit``, or None when it is absent or no file."""
        entry = self.entry_at(commit, path)
        return entry[1] if entry is not None and entry[0] == "blob" else None

    def show(self, commit: str, path: str) -> str | None:
        res = self.run("show", f"{commit}:{path}")
        return res.stdout if res.returncode == 0 else None

    def read_blob(self, blob: str) -> bytes | None:
        """The exact bytes of ``blob``: a section digest covers line endings too."""
        if not _SHA_RE.match(blob):
            return None
        try:
            res = subprocess.run(  # noqa: S603 - fixed argv, no shell
                ["git", "-C", str(self.repo), "cat-file", "blob", blob],
                capture_output=True,
                timeout=GIT_TIMEOUT_SECONDS,
                check=False,
            )
        except FileNotFoundError as exc:
            raise AuditError("`git` not found on PATH; the runner reads the target's history with it.") from exc
        except subprocess.TimeoutExpired as exc:
            raise AuditError(f"`git cat-file blob {blob}` timed out after {GIT_TIMEOUT_SECONDS}s.") from exc
        return res.stdout if res.returncode == 0 else None

    def file_bytes(self, commit: str, path: str) -> bytes | None:
        """The bytes of the file ``path`` at ``commit``, or None when it is absent or no file."""
        blob = self.blob_at(commit, path)
        return self.read_blob(blob) if blob is not None else None


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
    """One audited entry: a probe file, or an entry of the not-constructible manifest."""

    file: str  # relative to the repository root, posix
    data: dict[str, Any] | None
    errors: list[str] = field(default_factory=list)
    constructible: bool = True  # False: a manifest entry, which has no probe

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
        hint = " (a probe or manifest entry carries no verdict or other undeclared field; the runner decides the class)"
    return f"{loc}: {err.message}{hint}"


class UnsafePathError(Exception):
    """A file the runner must not read: a symlink, or a path resolving outside the repository."""


def read_inside(repo: Path, path: Path) -> str:
    """Read ``path`` only if it is no symlink and resolves inside ``repo``.

    A symlink is refused before anything is opened, so its target is never read:
    a probe linked to a private key would otherwise put the key into the
    committed report through the schema error that quotes the parsed document.
    """
    if path.is_symlink():
        raise UnsafePathError("is a symlink; the runner does not follow links in the audited tree")
    if not path.resolve().is_relative_to(repo):
        raise UnsafePathError("resolves outside the repository; the runner reads only files inside it")
    return path.read_text(encoding="utf-8")


def load_probes(repo: Path, yaml: Any, validator_cls: Any) -> list[Probe]:
    directory = repo / PROBE_DIR
    if not directory.is_dir():
        return []
    validator = validator_cls(PROBE_SCHEMA)
    probes: list[Probe] = []
    for file in sorted(directory.iterdir()):
        if file.name == MANIFEST_NAME:
            continue
        rel = file.relative_to(repo).as_posix()
        if file.is_symlink():
            # Any link under the probe directory is a finding, whatever it is named
            # and wherever it points; it is listed, never read.
            probes.append(Probe(rel, None, ["symlink: refused and not read; a probe file must be a regular file"]))
            continue
        if file.suffix not in PROBE_SUFFIXES or not file.is_file():
            continue
        try:
            data = yaml.safe_load(read_inside(repo, file))
        except UnsafePathError as exc:
            probes.append(Probe(rel, None, [f"refused and not read: {exc}"]))
            continue
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


@dataclass
class Manifest:
    """The not-constructible manifest as read from disk.

    ``entries`` are the rows it contributes to the audited set, one per distinct
    id; ``errors`` are manifest-level findings (unparseable, a top-level schema
    violation, a repeated id). When the document itself is unreadable, ``readable``
    is False and it contributes no row, because no entry in it can be trusted.
    """

    file: str
    entries: list[Probe] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    readable: bool = True


def load_manifest(repo: Path, yaml: Any, validator_cls: Any) -> Manifest | None:
    """Read project/reach-probes/_not-constructible.yml, or None when it is absent.

    Schema errors under ``entries/<i>`` mark only that entry invalid: it still
    counts as not probed, since the derivation recorded it as an entry without a
    probe. Errors anywhere else make the whole document unreadable.
    """
    path = repo / MANIFEST_PATH
    if not path.is_file() and not path.is_symlink():
        return None
    rel = MANIFEST_PATH.as_posix()
    try:
        data = yaml.safe_load(read_inside(repo, path))
    except UnsafePathError as exc:
        return Manifest(rel, errors=[f"refused and not read: {exc}"], readable=False)
    except (yaml.YAMLError, UnicodeDecodeError) as exc:
        return Manifest(rel, errors=[f"not parseable as YAML: {safe_text(exc)}"], readable=False)
    per_entry: dict[int, list[str]] = {}
    document_errors: list[str] = []
    for err in sorted(validator_cls(NOT_CONSTRUCTIBLE_SCHEMA).iter_errors(data), key=lambda e: list(e.absolute_path)):
        where = list(err.absolute_path)
        if len(where) >= 2 and where[0] == "entries" and isinstance(where[1], int):
            per_entry.setdefault(where[1], []).append(_schema_error_text(err))
        else:
            document_errors.append(_schema_error_text(err))
    if document_errors:
        return Manifest(rel, errors=document_errors, readable=False)
    manifest = Manifest(rel)
    seen: set[str] = set()
    for index, item in enumerate(data["entries"]):
        item_data = item if isinstance(item, dict) else None
        entry = Probe(f"{rel}#entries[{index}]", item_data, per_entry.get(index, []), constructible=False)
        if entry.data is None or not isinstance(entry.data.get("id"), str):
            # No usable id: the entry still counts, under its position.
            entry.data = (item_data or {}) | {"id": f"entries-{index}"}
        if entry.pid in seen:
            manifest.errors.append(f"id: {entry.pid!r} is listed more than once; counted once")
            continue
        seen.add(entry.pid)
        manifest.entries.append(entry)
    return manifest


# --------------------------------------------------------------------------- #
# Markdown sections (section anchors, schema v1.2)
# --------------------------------------------------------------------------- #
_FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
_ATX_RE = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?[ \t]*$")
_ATX_CLOSING_RE = re.compile(r"(?:^|[ \t]+)#+$")
_ROW_RE = re.compile(r"^ {0,3}\|(.*)$")
_CELL_SPLIT_RE = re.compile(r"(?<!\\)\|")


def _markdown_structure(lines: list[bytes]) -> tuple[list[tuple[int, int, str]], list[tuple[int, str]]]:
    """``(index, level, first token)`` of each ATX heading and ``(index, first cell)`` of each pipe row.

    Lines inside fenced code blocks and a leading front-matter block are neither.
    A setext heading is no heading here, and a table row must start with a pipe:
    a locator that only hits one of them does not resolve, rather than cutting a
    section by a rule the document's renderer may not share.
    """
    text = [raw.decode("utf-8", "replace").rstrip("\r\n") for raw in lines]
    start = 0
    if text and text[0].rstrip() == "---":
        closing = next((i for i in range(1, len(text)) if text[i].rstrip() in ("---", "...")), None)
        start = closing + 1 if closing is not None else 0
    headings: list[tuple[int, int, str]] = []
    rows: list[tuple[int, str]] = []
    fence: tuple[str, int] | None = None
    for index in range(start, len(text)):
        line = text[index]
        opener = _FENCE_RE.match(line)
        if fence is not None:
            if opener and opener.group(1)[0] == fence[0] and len(opener.group(1)) >= fence[1] \
                    and not opener.group(2).strip():
                fence = None
            continue
        if opener and not (opener.group(1)[0] == "`" and "`" in opener.group(2)):
            fence = (opener.group(1)[0], len(opener.group(1)))
            continue
        heading = _ATX_RE.match(line)
        if heading:
            title = _ATX_CLOSING_RE.sub("", heading.group(2) or "").strip()
            token = title.split()[0].removesuffix(".") if title else ""
            headings.append((index, len(heading.group(1)), token))
            continue
        row = _ROW_RE.match(line)
        if row:
            cells = _CELL_SPLIT_RE.split(row.group(1))
            if len(cells) >= 2:
                rows.append((index, cells[0].strip()))
    return headings, rows


def find_sections(content: bytes, kind: str, locator: str) -> list[bytes]:
    """Every section of the Markdown ``content`` that the locator selects, as exact bytes.

    ``heading``: the ATX heading whose first token, one trailing dot stripped,
    equals ``locator``, through the line before the next ATX heading of the same
    or a higher level (deeper headings stay inside), or the end of the file.
    ``row``: the pipe-table row whose first cell, trimmed, equals ``locator``.
    One element is a resolved locator; none is not found; more is ambiguous.
    Lines keep their line endings, so the bytes are what the digest covers.
    """
    if not locator:
        return []
    lines = content.splitlines(keepends=True)
    headings, rows = _markdown_structure(lines)
    if kind == "heading":
        found = []
        for n, (index, level, token) in enumerate(headings):
            if token != locator:
                continue
            end = next((i for i, lvl, _ in headings[n + 1:] if lvl <= level), len(lines))
            found.append(b"".join(lines[index:end]))
        return found
    if kind == "row":
        return [lines[index] for index, first in rows if first == locator]
    raise ValueError(f"unknown locator kind {kind!r}")


def section_digest(section: bytes) -> str:
    return hashlib.sha256(section).hexdigest()


def _locators(sections: object) -> list[tuple[str, str, str]] | None:
    """``(kind, locator, digest)`` per entry of declaration.sections, or None when malformed.

    Historical probe revisions are not schema-validated, so the shape is checked here.
    """
    if not isinstance(sections, list) or not sections:
        return None
    out = []
    for item in sections:
        if not isinstance(item, dict) or not isinstance(item.get("digest"), str):
            return None
        kinds = [k for k in item if k != "digest"]
        if len(kinds) != 1 or kinds[0] not in SECTION_KINDS or not isinstance(item[kinds[0]], str):
            return None
        out.append((kinds[0], item[kinds[0]], item["digest"]))
    return out


def section_anchor(sections: object) -> str:
    """The derived_from of a section-anchored probe: ``sections:<sha256>``.

    Canonical input: ``[[kind, locator, digest], ...]`` in the order of
    declaration.sections, serialised with ``json.dumps(obj, separators=(",", ":"),
    ensure_ascii=False)`` and encoded UTF-8. Any locator or digest change moves
    it, so the baseline walk sees a re-anchoring as a new derivation.
    """
    locators = _locators(sections)
    if locators is None:
        raise ValueError("declaration.sections is not a list of heading or row locators with a digest")
    canonical = json.dumps([list(entry) for entry in locators], separators=(",", ":"), ensure_ascii=False)
    return SECTIONS_PREFIX + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _is_section_anchor(derived_from: str) -> bool:
    """Whether ``derived_from`` claims the section-anchor form; well-formed or not."""
    return derived_from.startswith(SECTIONS_PREFIX)


def _section_anchor_problem(derived_from: str, sections: object) -> str | None:
    """Why ``derived_from`` and ``declaration.sections`` are no consistent section anchor, or None."""
    shown = safe_text(derived_from[:21], 40)
    if sections is None:
        if _is_section_anchor(derived_from):
            return f"derived_from {shown} is a section anchor, but declaration.sections is absent"
        return None
    if not _is_section_anchor(derived_from):
        return f"declaration.sections needs derived_from of the form {SECTIONS_FORM}, not {shown}"
    if not _SECTIONS_ANCHOR_RE.match(derived_from):
        return f"derived_from {safe_text(derived_from, 80)!r} is not a section anchor of the form {SECTIONS_FORM}"
    locators = _locators(sections)
    if locators is None:
        return "declaration.sections is not a list of heading or row locators with a digest"
    seen: set[tuple[str, str]] = set()
    for kind, locator, _ in locators:
        if (kind, locator) in seen:
            return f"declaration.sections lists {kind} {safe_text(locator, 80)} more than once"
        seen.add((kind, locator))
    if section_anchor(sections) != derived_from:
        return f"derived_from {shown} does not match the digests in declaration.sections"
    return None


def _section_mismatches(git: Git, commit: str, rel: str, locators: list[tuple[str, str, str]]) -> list[str]:
    """Per locator whose section at ``commit`` is not its recorded digest: why, naming the locator."""
    content = git.file_bytes(commit, rel)
    problems = []
    for kind, locator, digest in locators:
        found = find_sections(content, kind, locator) if content is not None else []
        name = f"{kind} {safe_text(locator, 80)}"
        if not found:
            problems.append(f"{name} not found")
        elif len(found) > 1:
            problems.append(f"{name} is ambiguous ({len(found)} matches)")
        elif section_digest(found[0]) != digest:
            problems.append(f"{name} changed")
    return problems


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
    return _anchor_key(doc) if isinstance(doc, dict) else None


def _anchor_key(doc: dict[str, Any]) -> object:
    """What a derivation records: ``derived_from``, and for a content anchor also the path.

    A content anchor names the declaration's content, so a pure rename keeps its
    value; re-deriving after one changes only ``declaration.path``. Keying the
    derivation on the pair lets that commit record a re-derivation (checked by
    _rebaseline_problem) instead of reading as a later probe change. A section
    anchor is keyed the same way; its value covers every locator and digest. A
    commit anchor keys on ``derived_from`` alone, exactly as before v1.1.
    """
    derived_from = doc.get("derived_from")
    if isinstance(derived_from, str) and (_is_content_anchor(derived_from) or _is_section_anchor(derived_from)):
        declaration = doc.get("declaration")
        path = declaration.get("path") if isinstance(declaration, dict) else None
        return (derived_from, path)
    return derived_from


def probe_changes(git: Git, probe: Probe, yaml: Any) -> tuple[str | None, list[str], bool, list[tuple[str, str]]]:
    """The probe's derivation baseline, the commits that touched it since, dirtiness,
    and the revisions before the baseline.

    The baseline is the commit that recorded the probe's current ``derived_from``:
    walking the file's history newest first, the oldest commit of the unbroken run
    carrying today's value. The probe cannot be committed in the commit it was
    derived at, so comparing its latest commit against ``derived_from`` directly
    would flag every freshly committed probe; the recording commit is the approved
    state, and every later commit to the file is an unapproved change.

    The fourth value lists ``(commit, path)`` of the probe's revisions before the
    baseline, newest first; it is empty when the baseline is the probe's first
    commit. When it is not, the baseline commit moved ``derived_from``, and
    detect_change must check that the move was a re-derivation rather than a
    re-baseline; the older revisions let that check prove the previous anchor.
    """
    history = git.file_history(probe.file)
    if not history:
        return None, [], False, []
    current = _anchor_key(probe.data) if probe.data else None
    run: list[str] = []
    for commit, path_then in history:
        if _derived_from_of(git.show(commit, path_then), yaml) != current:
            break
        run.append(commit)
    dirty = git.is_dirty(probe.file)
    if not run:
        # HEAD's version already differs from the working tree's derived_from: the
        # recording itself is uncommitted, and the newest commit is the baseline.
        return history[0][0], [], True, []
    return run[-1], run[:-1], dirty, history[len(run):]


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
    if not config_path.is_file() and not config_path.is_symlink():
        return None, f"{SPEC_CONFIG.as_posix()} not found, so the pinned ref of the inherited spec is unknown"
    try:
        text = read_inside(repo, config_path)
    except UnsafePathError as exc:
        return None, f"{SPEC_CONFIG.as_posix()} {exc}, so the pinned ref of the inherited spec is unknown"
    except UnicodeDecodeError:
        return None, f"{SPEC_CONFIG.as_posix()} is not UTF-8"
    return _pinned_ref(text, declaration, yaml)


def _pinned_ref(text: str | None, declaration: dict[str, Any], yaml: Any) -> tuple[str | None, str]:
    """The inherits[].ref pinning ``declaration``'s inherited spec, read from a config text."""
    if text is None:
        return None, f"{SPEC_CONFIG.as_posix()} not found, so the pinned ref of the inherited spec is unknown"
    try:
        config = yaml.safe_load(text) or {}
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


def _is_content_anchor(derived_from: str) -> bool:
    """Whether ``derived_from`` claims the content-anchor form; well-formed or not."""
    return derived_from.startswith(BLOB_PREFIX)


def _probe_doc(git: Git, revision: tuple[str, str], yaml: Any) -> dict[str, Any] | None:
    """The probe document at ``(commit, path)``, or None when it is unreadable."""
    try:
        doc = yaml.safe_load(git.show(*revision) or "")
    except yaml.YAMLError:
        return None
    return doc if isinstance(doc, dict) else None


def _without(doc: dict[str, Any] | None, *paths: tuple[str, ...]) -> object:
    """``doc`` deep-copied without the (nested) keys named by ``paths``."""
    stripped = copy.deepcopy(doc)
    for path in paths:
        node: object = stripped
        for key in path[:-1]:
            node = node.get(key) if isinstance(node, dict) else None
        if isinstance(node, dict):
            node.pop(path[-1], None)
    return stripped


def _run_length(git: Git, revisions: list[tuple[str, str]], yaml: Any) -> int:
    """How many of ``revisions`` (newest first) carry the anchor key of the first one.

    The last of them is the commit that recorded that derivation.
    """
    key = _derived_from_of(git.show(*revisions[0]), yaml)
    span = 1
    while span < len(revisions) and _derived_from_of(git.show(*revisions[span]), yaml) == key:
        span += 1
    return span


def _continuation_problem(git: Git, moved: str, earlier: list[tuple[str, str]], span: int,
                          yaml: Any) -> str | None:
    """Why a move that re-approves nothing cannot inherit the previous derivation.

    A pure move of the declaration and a pure commit-to-content migration only
    re-label the previous derivation; they are clean exactly when that derivation
    was. So the previous revision must still be the document its derivation
    recorded, and that recording must itself have been a re-derivation. Otherwise
    one relabelling commit would adopt a weakening committed before it.
    """
    recording = earlier[span - 1]
    recording_doc = _probe_doc(git, recording, yaml)
    changed = [c for c, path in earlier[:span - 1] if _probe_doc(git, (c, path), yaml) != recording_doc]
    if changed:
        return (f"{moved}, but the probe changed in {', '.join(c[:12] for c in reversed(changed))} "
                f"after its previous derivation was recorded in {recording[0][:12]}")
    if span < len(earlier) and recording_doc is not None:
        inner = _rebaseline_problem(git, str(recording_doc.get("derived_from")), recording[0], earlier[span:],
                                    yaml, recording_doc)
        if inner:
            return f"{moved}, but its previous derivation was no re-derivation either: {inner}"
    return None


def _prior_anchor(git: Git, moved: str, prev_df: str, prior_doc: dict[str, Any], rel: str, recording: str,
                  baseline: str) -> tuple[str | None, str | None, bool]:
    """Prove the previous anchor where it was recorded; say whether its content moved since.

    Returns ``(problem, before, changed)``: why the previous anchor is unproven
    (or None), the blob of ``rel`` the previous derivation saw, and whether the
    anchored content differs at ``baseline``. A content anchor must be the
    declaration's blob at ``recording``; a commit anchor's blob must equal it, or,
    when a squash merge dropped the commit, the blob at ``recording`` stands in;
    a section anchor's digests must be its sections at ``recording``, and it
    changed when any of them differs at ``baseline`` or no longer resolves.
    An anchor that never matched the declaration shows no change, and accepting
    it would let one commit record a weakening under a made-up anchor and the
    next restore the real one.
    """
    recorded = git.blob_at(recording, rel)
    if _is_section_anchor(prev_df):
        sections = prior_doc.get("declaration", {}).get("sections") if isinstance(
            prior_doc.get("declaration"), dict) else None
        why = _section_anchor_problem(prev_df, sections)
        shown = safe_text(prev_df[:12], 40)
        if why:
            return (f"{moved}, but the previous derived_from {shown} is no consistent section anchor ({why}), "
                    "so no declaration change can be shown"), None, False
        locators = _locators(sections) or []
        if _section_mismatches(git, recording, rel, locators):
            return (f"{moved}, but the previous derived_from {shown} is not the content of its sections of "
                    f"{safe_text(rel)} at {recording[:12]}, where it was recorded, so no declaration change "
                    "can be shown"), None, False
        return None, recorded, bool(_section_mismatches(git, baseline, rel, locators))
    if _is_content_anchor(prev_df):
        if not _BLOB_ANCHOR_RE.match(prev_df):
            return (f"{moved}, but the previous derived_from is not a content anchor of the form {BLOB_FORM}, "
                    "so no declaration change can be shown"), None, False
        before: str | None = prev_df[len(BLOB_PREFIX):]
        if before != recorded:
            return (f"{moved}, but the previous derived_from {safe_text(prev_df[:12], 40)} is not the content of "
                    f"{safe_text(rel)} at {recording[:12]}, where it was recorded, so no declaration change can be "
                    "shown"), None, False
    else:
        prev_commit = git.resolve_commit(prev_df)
        if prev_commit is None:
            # A squash merge drops the commit a v1.0 derivation named, but the
            # commit that recorded it is still here: the declaration's content
            # there is what the derivation saw, and what a change is shown against.
            if recorded is None:
                return (f"{moved}, but the previous derived_from cannot be resolved to a commit and "
                        f"{safe_text(rel)} did not exist at {recording[:12]}, where it was recorded, "
                        "so no declaration change can be shown"), None, False
            before = recorded
        else:
            before = git.blob_at(prev_commit, rel)
            if before != recorded:
                return (f"{moved}, but the content of {safe_text(rel)} at the previous derived_from "
                        f"{prev_commit[:12]} is not its content at {recording[:12]}, where it was recorded, "
                        "so no declaration change can be shown"), None, False
    return None, before, git.blob_at(baseline, rel) != before


def _unchanged_since(prev_df: str, rel: str) -> str:
    what = f"the anchored sections of {safe_text(rel)}" if _is_section_anchor(prev_df) else safe_text(rel)
    return f"{what} did not change in between"


def _content_rebaseline_problem(git: Git, moved: str, prev_df: str, new_df: str, baseline: str, rel: str,
                                earlier: list[tuple[str, str]], yaml: Any, prior_doc: dict[str, Any],
                                new_doc: dict[str, Any]) -> str | None:
    """Why moving ``derived_from`` onto the content anchor ``new_df`` is no re-derivation.

    No commit named by either anchor has to exist, so a squash merge that dropped
    the derivation commits leaves the check intact. The move is a re-derivation
    when the new anchor is the declaration's content at the recording commit and
    the previously anchored content (``rel``, read from the probe's previous
    revision) changed since it was recorded (_prior_anchor proves the previous
    anchor first, whichever form it has).

    Two moves re-approve nothing and so are clean only as continuations of a
    clean previous derivation (_continuation_problem): a pure move of the
    declaration (same blob, new path, nothing else changed but the approval
    stamp its re-derive writes) and a pure migration onto the content anchor
    (from a commit anchor: the old commit's content; from a section anchor:
    no anchored section changed; same path, nothing else changed but the
    approval stamp and, for a section anchor, declaration.sections).
    """
    if not _BLOB_ANCHOR_RE.match(new_df):
        return f"{moved}, but {safe_text(new_df, 60)} is not a content anchor of the form {BLOB_FORM}"
    new_decl = new_doc.get("declaration")
    raw_new = new_decl.get("path") if isinstance(new_decl, dict) else None
    new_rel = _repo_relative(raw_new) if isinstance(raw_new, str) and raw_new else None
    if new_rel is None:
        return f"{moved}, but a content anchor needs a declaration file inside the repository"
    new_blob = new_df[len(BLOB_PREFIX):]
    if git.blob_at(baseline, new_rel) != new_blob:
        return f"{moved}, but {safe_text(new_df[:12], 40)} is not the content of {safe_text(new_rel)} at {baseline[:12]}"
    span = _run_length(git, earlier, yaml)
    recording = earlier[span - 1][0]
    problem, before, changed = _prior_anchor(git, moved, prev_df, prior_doc, rel, recording, baseline)
    if problem:
        return problem
    # `derive` re-stamps the approval on every run, a migration included.
    if _is_section_anchor(prev_df):
        relabel = (("derived_from",), ("approval",), ("declaration", "sections"))
        pure = not changed
    else:
        relabel = (("derived_from",), ("approval",))
        pure = new_blob == before
    if pure and new_rel == rel and _without(new_doc, *relabel) == _without(prior_doc, *relabel):
        return _continuation_problem(git, moved, earlier, span, yaml)
    if not changed:
        return f"{moved}, but {_unchanged_since(prev_df, rel)}"
    if prev_df == new_df:
        return _pure_move_problem(git, moved, earlier, span, yaml, prior_doc, new_doc)
    if new_rel != rel and git.blob_at(recording, new_rel) == new_blob:
        return (f"{moved}, but {safe_text(new_rel)} already held {safe_text(new_df[:12], 40)} when the previous "
                f"derivation was recorded in {recording[:12]}, so re-pointing at it shows no declaration change")
    return None


def _pure_move_problem(git: Git, moved: str, earlier: list[tuple[str, str]], span: int, yaml: Any,
                       prior_doc: dict[str, Any], new_doc: dict[str, Any]) -> str | None:
    """Same anchor, new declaration path: clean only as a continuation that changed nothing else.

    The re-derive that follows a rename re-approves the probe, so the approval
    stamp may move with the path; the observation digest inside it is still
    checked on every run.
    """
    pure_move = (("declaration", "path"), ("approval",))
    if _without(new_doc, *pure_move) != _without(prior_doc, *pure_move):
        return (f"{moved}, but the same commit changed the probe beyond declaration.path, "
                "which a pure move of the declaration does not justify")
    return _continuation_problem(git, moved, earlier, span, yaml)


def _section_rebaseline_problem(git: Git, moved: str, prev_df: str, new_df: str, baseline: str, rel: str,
                                earlier: list[tuple[str, str]], yaml: Any, prior_doc: dict[str, Any],
                                new_doc: dict[str, Any]) -> str | None:
    """Why moving ``derived_from`` onto the section anchor ``new_df`` is no re-derivation.

    The same strength as a content anchor, per section: the new digests must be
    the sections at the recording commit (each locator resolving to exactly one
    section, so an ambiguous locator cannot anchor), the previous anchor must be
    proven where it was recorded (_prior_anchor), and the previously anchored
    content must have changed since. Two moves re-approve nothing and are clean
    only as continuations of a clean previous derivation: the migration of a
    content or commit anchor onto sections while the file is unchanged (only
    derived_from, declaration.sections, and the approval stamp may differ), and
    a pure move of the declaration file with the same sections.
    """
    new_decl = new_doc.get("declaration")
    new_decl = new_decl if isinstance(new_decl, dict) else {}
    raw_new = new_decl.get("path")
    new_rel = _repo_relative(raw_new) if isinstance(raw_new, str) and raw_new else None
    if new_rel is None:
        return f"{moved}, but a section anchor needs a declaration file inside the repository"
    why = _section_anchor_problem(new_df, new_decl.get("sections"))
    if why:
        return f"{moved}, but {why}"
    locators = _locators(new_decl.get("sections")) or []
    mismatches = _section_mismatches(git, baseline, new_rel, locators)
    if mismatches:
        return (f"{moved}, but the recorded sections are not the content of {safe_text(new_rel)} at "
                f"{baseline[:12]}: {'; '.join(mismatches)}")
    span = _run_length(git, earlier, yaml)
    recording = earlier[span - 1][0]
    problem, _, changed = _prior_anchor(git, moved, prev_df, prior_doc, rel, recording, baseline)
    if problem:
        return problem
    relabel = (("derived_from",), ("approval",), ("declaration", "sections"))
    if (not changed and not _is_section_anchor(prev_df) and new_rel == rel
            and _without(new_doc, *relabel) == _without(prior_doc, *relabel)):
        return _continuation_problem(git, moved, earlier, span, yaml)
    if not changed:
        return f"{moved}, but {_unchanged_since(prev_df, rel)}"
    if prev_df == new_df:
        return _pure_move_problem(git, moved, earlier, span, yaml, prior_doc, new_doc)
    if new_rel != rel and not _section_mismatches(git, recording, new_rel, locators):
        return (f"{moved}, but {safe_text(new_rel)} already held these sections when the previous derivation "
                f"was recorded in {recording[:12]}, so re-pointing at it shows no declaration change")
    return None


def _reconfirm_view(doc: dict[str, Any] | None) -> dict[str, Any]:
    """What a re-confirmation must leave as it was: the probe without its anchor, approval, and digests."""
    view = copy.deepcopy(doc) if isinstance(doc, dict) else {}
    view.pop("derived_from", None)
    view.pop("approval", None)
    declaration = view.get("declaration")
    if isinstance(declaration, dict) and isinstance(declaration.get("sections"), list):
        declaration["sections"] = [{k: v for k, v in item.items() if k != "digest"} if isinstance(item, dict)
                                   else item for item in declaration["sections"]]
    return view


def _reconfirmation_problem(git: Git, moved: str, earlier: list[tuple[str, str]], yaml: Any,
                            new_doc: dict[str, Any]) -> str | None:
    """Why the baseline's re-confirmation is more than a re-approval of the previous derivation, or None.

    A re-confirmation (approval.mode reconfirmed) says the probe still holds
    after its declaration changed. So against the derivation it re-confirms,
    only derived_from, the section digests, and the approval may differ; a
    changed expected, observe, tier, environment, or declaration target
    (path, location, locators) is a weakening. It inherits that derivation, so
    it is clean only as a continuation of it (_continuation_problem), which
    also keeps a weakening committed in between from being adopted.
    """
    span = _run_length(git, earlier, yaml)
    recording = earlier[span - 1]
    before, after = _reconfirm_view(_probe_doc(git, recording, yaml)), _reconfirm_view(new_doc)
    changed: list[str] = []
    for key in sorted(set(before) | set(after)):
        old, new = before.get(key), after.get(key)
        if key == "declaration" and isinstance(old, dict) and isinstance(new, dict):
            changed += [f"declaration.{k}" for k in sorted(set(old) | set(new)) if old.get(k) != new.get(k)]
        elif old != new:
            changed.append(key)
    if changed:
        return (f"{moved}, but a re-confirmation may change only derived_from, the section digests and approval, "
                f"and it also changed {safe_text(', '.join(changed), 200)} against the derivation recorded in "
                f"{recording[0][:12]}")
    return _continuation_problem(git, moved, earlier, span, yaml)


def _rebaseline_problem(git: Git, new_df: str, baseline: str, earlier: list[tuple[str, str]], yaml: Any,
                        new_doc: dict[str, Any]) -> str | None:
    """Why the baseline commit's move of ``derived_from`` is no re-derivation, or None.

    Moving ``derived_from`` re-baselines the probe: every change of that commit
    becomes the approved state. That is legitimate only when the declaration the
    probe checked actually changed between the previous ``derived_from`` and the
    new one. Otherwise one commit that lowers the expectation and bumps
    ``derived_from`` to the then-HEAD would launder its own weakening (spec: a
    guard disarmed through its own entry).

    The anchor is read from the probe's *previous* revision (``earlier[0]``; the
    older revisions follow it, newest first), so re-pointing the anchor at some
    other, recently changed file in the same commit proves nothing. A path anchor
    needs its latest commit as of the new ``derived_from`` to lie outside the
    previous one's ancestry; an inherited spec needs the pin in
    spec/.spec-config.yml to have moved to the new value; an external anchor can't
    show a change, so its re-baseline is never accepted. A move onto a content
    anchor is judged by content instead (_content_rebaseline_problem), a move onto
    a section anchor by its sections (_section_rebaseline_problem); ``new_doc``
    is the probe document the baseline recorded. A move recorded as a
    re-confirmation must, on top, leave the probe itself as it was
    (_reconfirmation_problem).
    """
    prior_commit, _ = earlier[0]
    moved = f"{baseline[:12]} moved derived_from"
    prior_doc = _probe_doc(git, earlier[0], yaml)
    prev_df = prior_doc.get("derived_from") if prior_doc else None
    if not isinstance(prev_df, str) or not prev_df or prior_doc is None:
        return (f"{moved} to {safe_text(new_df, 40)}, but the probe's previous revision "
                f"({prior_commit[:12]}) carries no readable derived_from, so no declaration change can justify it")
    decl = prior_doc.get("declaration")
    decl = decl if isinstance(decl, dict) else {}
    new_decl = new_doc.get("declaration")
    if prev_df == new_df:
        # Only a content or section anchor gets here: its key includes declaration.path.
        moved = (f"{baseline[:12]} moved the declaration of {safe_text(new_df[:12], 40)} "
                 f"from {safe_text(decl.get('path'), 80)} to "
                 f"{safe_text(new_decl.get('path') if isinstance(new_decl, dict) else None, 80)}")
    else:
        moved += f" from {safe_text(prev_df[:12], 40)} to {safe_text(new_df[:12], 40)}"
    problem = _anchor_move_problem(git, moved, decl, prior_doc, prev_df, new_df, baseline, earlier, yaml, new_doc)
    approval = new_doc.get("approval")
    if (problem is None and prev_df != new_df and isinstance(approval, dict)
            and approval.get("mode") == MODE_RECONFIRMED):
        # A pure move (prev_df == new_df) is already held to "nothing but the path
        # and the approval changed", whatever mode the approval carries over.
        return _reconfirmation_problem(git, moved, earlier, yaml, new_doc)
    return problem


def _anchor_move_problem(git: Git, moved: str, decl: dict[str, Any], prior_doc: dict[str, Any], prev_df: str,
                         new_df: str, baseline: str, earlier: list[tuple[str, str]], yaml: Any,
                         new_doc: dict[str, Any]) -> str | None:
    """The anchor-specific half of _rebaseline_problem: did the anchored declaration change?"""
    prior_commit, _ = earlier[0]
    if decl.get("inherited_spec"):
        before, _ = _pinned_ref(git.show(prior_commit, SPEC_CONFIG.as_posix()), decl, yaml)
        after, _ = _pinned_ref(git.show(baseline, SPEC_CONFIG.as_posix()), decl, yaml)
        if after == new_df and before != new_df:
            return None
        return f"{moved}, but the pinned ref of {safe_text(decl['inherited_spec'])} did not move to it"
    raw = decl.get("path")
    rel = _repo_relative(raw) if isinstance(raw, str) and raw else None
    if rel is None:
        return f"{moved} for an anchor outside the repository, whose change the runner cannot confirm"
    if _is_content_anchor(new_df):
        return _content_rebaseline_problem(git, moved, prev_df, new_df, baseline, rel, earlier, yaml,
                                           prior_doc, new_doc)
    if _is_section_anchor(new_df):
        return _section_rebaseline_problem(git, moved, prev_df, new_df, baseline, rel, earlier, yaml,
                                           prior_doc, new_doc)
    prev_commit, new_commit = git.resolve_commit(prev_df), git.resolve_commit(new_df)
    if prev_commit is None or new_commit is None:
        return f"{moved}, but the two cannot both be resolved to commits, so no declaration change can be shown"
    last = git.last_commit(rel, new_commit)
    if last is not None and not git.is_ancestor_or_equal(last, prev_commit):
        return None
    return f"{moved}, but {safe_text(rel)} did not change in between"


def detect_change(repo: Path, git: Git, probe: Probe, yaml: Any) -> ChangeState:
    """Classify one valid probe's change state from the target's history."""
    data = probe.data or {}
    derived_from = data["derived_from"]
    baseline, later, dirty, earlier = probe_changes(git, probe, yaml)
    if baseline is None:
        return ChangeState(
            STATE_UNCOMMITTED,
            "probe file is not committed; the approved set must be under version control, "
            "and an uncommitted probe has no derivation to compare against",
        )

    # The probe itself: any change after the recorded derivation is a weakening,
    # whether or not the declaration moved too (spec: "whether or not both changed
    # together"). Checked first so a combined change is surfaced as a finding.
    rebaseline = _rebaseline_problem(git, derived_from, baseline, earlier, yaml, data) if earlier else None
    if later or dirty or rebaseline:
        parts = []
        if rebaseline:
            parts.append(f"re-baselined without a declaration change: {rebaseline}")
        if later:
            parts.append(f"probe changed in {', '.join(c[:12] for c in reversed(later))} after its derivation was recorded in {baseline[:12]}")
        if dirty:
            parts.append("probe file has uncommitted changes")
        return ChangeState(STATE_WEAKENED, "; ".join(parts))

    declaration = data["declaration"]
    content_anchor = _is_content_anchor(derived_from)
    # declaration.sections without a section derived_from is judged here too, as
    # an inconsistent section anchor, never silently as a file or commit anchor.
    section_anchored = _is_section_anchor(derived_from) or "sections" in declaration
    if section_anchored and "inherited_spec" in declaration:
        return ChangeState(STATE_UNRESOLVED, f"derived_from {safe_text(derived_from[:21], 40)} is a section anchor, "
                           "but an inherited spec is anchored by its pinned inherits[].ref")
    if content_anchor and "inherited_spec" in declaration:
        return ChangeState(STATE_UNRESOLVED, f"derived_from {safe_text(derived_from[:17], 40)} is a content anchor, "
                           "but an inherited spec is anchored by its pinned inherits[].ref")
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
        if section_anchored:
            return ChangeState(STATE_UNRESOLVED, f"derived_from {safe_text(derived_from[:21], 40)} is a section "
                               f"anchor, but {where}; a section anchor needs a declaration file inside the repository")
        if content_anchor:
            return ChangeState(STATE_UNRESOLVED, f"derived_from {safe_text(derived_from[:17], 40)} is a content anchor, "
                               f"but {where}; a content anchor needs a declaration file inside the repository")
        return ChangeState(STATE_UNMONITORED, f"{where}; change is not monitored, re-derive on request")
    if section_anchored:
        return _section_change(git, derived_from, declaration.get("sections"), rel)
    if content_anchor:
        return _content_change(git, derived_from, rel)

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


def _content_change(git: Git, derived_from: str, rel: str) -> ChangeState:
    """Change state of an in-repository declaration under a content anchor.

    No ancestry check: the anchor names content, not a commit, so it holds after
    a squash merge. The declaration is stale when its working-tree file carries
    uncommitted changes or its content at HEAD is not the anchored blob; a
    renamed or deleted declaration has no content at HEAD and so reads as
    changed. An edit reverted to the anchored content reads as unchanged.
    """
    if not _BLOB_ANCHOR_RE.match(derived_from):
        return ChangeState(STATE_UNRESOLVED,
                           f"derived_from {safe_text(derived_from, 60)!r} is not a content anchor of the form {BLOB_FORM}")
    if git.last_commit(rel) is None:
        return ChangeState(STATE_UNRESOLVED, f"declaration {rel} has no history in the target repository")
    if git.is_dirty(rel):
        return ChangeState(STATE_STALE, f"{REASON_STALE}: {rel} has uncommitted changes")
    entry = git.entry_at("HEAD", rel)
    if entry is None:
        return ChangeState(STATE_STALE, f"{REASON_STALE}: {rel} no longer exists at HEAD")
    if entry[0] != "blob":
        return ChangeState(STATE_STALE, f"{REASON_STALE}: {rel} is not a regular file at HEAD")
    current = entry[1]
    if current != derived_from[len(BLOB_PREFIX):]:
        return ChangeState(STATE_STALE, f"{REASON_STALE}: the content of {rel} at HEAD is no longer {derived_from[:17]}")
    return ChangeState(STATE_CLEAN)


def _section_change(git: Git, derived_from: str, sections: object, rel: str) -> ChangeState:
    """Change state of a Markdown declaration under a section anchor.

    Like a content anchor it names content, not a commit, so it holds after a
    squash merge; unlike one, only the anchored sections count. Each locator is
    resolved at HEAD and compared with its digest; the probe is stale naming
    every locator whose section changed, is not found, or is ambiguous. The
    runner never follows a renumbered or renamed section. An anchor whose
    derived_from does not match its declaration.sections is unresolved: the
    anchor was edited by hand or is inconsistent, so nothing can be compared.
    """
    why = _section_anchor_problem(derived_from, sections)
    if why:
        return ChangeState(STATE_UNRESOLVED, why)
    if git.last_commit(rel) is None:
        return ChangeState(STATE_UNRESOLVED, f"declaration {rel} has no history in the target repository")
    if git.is_dirty(rel):
        return ChangeState(STATE_STALE, f"{REASON_STALE}: {rel} has uncommitted changes")
    entry = git.entry_at("HEAD", rel)
    if entry is None:
        return ChangeState(STATE_STALE, f"{REASON_STALE}: {rel} no longer exists at HEAD")
    if entry[0] != "blob":
        return ChangeState(STATE_STALE, f"{REASON_STALE}: {rel} is not a regular file at HEAD")
    mismatches = _section_mismatches(git, "HEAD", rel, _locators(sections) or [])
    if mismatches:
        return ChangeState(STATE_STALE, f"{REASON_STALE}: in {rel}, {'; '.join(mismatches)}")
    return ChangeState(STATE_CLEAN)


def is_reconfirmed(data: dict[str, Any] | None) -> bool:
    """Whether the probe's approval is a re-confirmation rather than a re-derivation (R6)."""
    approval = (data or {}).get("approval")
    return isinstance(approval, dict) and approval.get("mode") == MODE_RECONFIRMED


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
    if not text.strip():
        # A command that fails silently with exit 0 has observed nothing, for a
        # set as much as for a count; an empty set is never read as "none reached".
        return None, REASON_SILENT
    if kind == "count":
        value = text.strip()
        if not _COUNT_RE.match(value):
            if value.isascii() and value.isdigit():
                return None, f"observation has {len(value)} digits; a count has at most 18"
            return None, f"observation {safe_text(value, 80)!r} is not a single non-negative integer"
        try:
            return int(value), ""
        except ValueError as exc:
            return None, f"observation is not a usable integer: {safe_text(exc, 120)}"
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


def observation_digest(data: dict[str, Any]) -> str:
    """The digest an approval binds to: what the runner will actually execute.

    Canonical input: a JSON object with exactly the keys ``observe``,
    ``environment`` and ``teardown`` (an absent list taken as ``[]``), serialised
    with ``json.dumps(obj, sort_keys=True, separators=(",", ":"),
    ensure_ascii=False)``, encoded UTF-8, hashed with SHA-256, written as 64
    lowercase hex digits. ``approval.observation_digest`` carries this value, so
    an approval stops covering a probe whose argv, timeout, or targets changed.
    """
    canonical = {
        "observe": data["observe"],
        "environment": data.get("environment", []),
        "teardown": data.get("teardown", []),
    }
    text = json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


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
        res = run_command(argv, repo, observe.get("timeout_seconds", DEFAULT_OBSERVE_TIMEOUT_SECONDS),
                          kill_on_overflow=True)
        if res.oversized:
            return Outcome(NOT_PROBED, reason=f"observation exceeds {MAX_OBSERVATION_BYTES} bytes"), notes
        if res.returncode is None:
            return Outcome(NOT_PROBED, reason=f"observation step {res.error}"), notes
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


def not_constructible_entry(item: Probe) -> Entry:
    """A manifest entry: not probed, never executed, no change detection."""
    if item.errors:
        return Entry(item, ChangeState(STATE_INVALID), Outcome(
            NOT_PROBED, reason="manifest entry fails the not-constructible schema: " + "; ".join(item.errors)))
    data = item.data or {}
    reason = f"{REASON_NOT_CONSTRUCTIBLE}: {data['reason']}"
    if data.get("detail"):
        reason += f": {data['detail']}"
    return Entry(item, ChangeState(STATE_NOT_CONSTRUCTIBLE), Outcome(NOT_PROBED, reason=reason))


def contradiction_entry(probe: Probe, listed: Probe) -> Entry:
    """An id that is both a probe file and a manifest entry: one row, not probed, a finding.

    The probe is not executed: the derivation said no probe could be built for this
    entry, so a probe file under its id is unexplained, and running it would let
    an unapproved claim of constructibility produce a class.
    """
    code = (listed.data or {}).get("reason", "invalid entry")
    why = (
        f"id is both the probe file {probe.file} and a not-constructible manifest entry "
        f"({code}); re-derive the entry to decide which is true"
    )
    return Entry(probe, ChangeState(STATE_CONTRADICTION, why), Outcome(NOT_PROBED, reason=f"contradiction: {why}"))


def evaluate(repo: Path, git: Git, probe: Probe, yaml: Any, include_t2: bool, env_timeout: float, clock: Callable[[], datetime]) -> Entry:
    if not probe.constructible:
        return not_constructible_entry(probe)
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
    approved_digest = data["approval"].get("observation_digest")
    if approved_digest is not None and approved_digest != observation_digest(data):
        why = f"{REASON_DIGEST_MISMATCH}: the approval's observation_digest {approved_digest[:12]} does not match observe, environment and teardown as committed"
        return Entry(probe, ChangeState(STATE_APPROVAL_MISMATCH, why), Outcome(NOT_PROBED, reason=REASON_DIGEST_MISMATCH))
    if data["tier"] == "T2" and not include_t2:
        return Entry(probe, change, Outcome(NOT_PROBED, reason=REASON_T2))
    executed_at = clock().strftime("%Y-%m-%dT%H:%M:%SZ")
    outcome, notes = execute(repo, data, env_timeout)
    if approved_digest is None:
        notes = [NOTE_NO_DIGEST, *notes]
    if is_reconfirmed(data):
        notes = [*notes, NOTE_RECONFIRMED]
    return Entry(probe, change, outcome, executed_at, notes)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def report_path(repo: Path, today: str) -> Path:
    """R12: the one file the runner writes. A symlinked ``.audits`` must not redirect it."""
    resolved_parent = (repo / REPORT_DIR).resolve()
    if not resolved_parent.is_relative_to(repo):
        raise AuditError(
            f"{REPORT_DIR.as_posix()} resolves outside the repository ({safe_text(resolved_parent)}); "
            "refusing to write there."
        )
    return resolved_parent / f"{today}.md"


def write_report(out: Path, text: str) -> None:
    """Write the report without following a symlink at the file itself.

    report_path resolved the directory; O_NOFOLLOW closes the remaining gap, a
    ``<date>.md`` that is itself a link to a file elsewhere.
    """
    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(out, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o644)
    except OSError as exc:
        if exc.errno == errno.ELOOP:
            raise AuditError(
                f"the report path {safe_text(out)} is a symlink; refusing to write through it. "
                "Remove the link and run again."
            ) from exc
        raise AuditError(f"cannot write the report {safe_text(out)}: {exc.strerror}") from exc
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
    except OSError as exc:
        raise AuditError(f"cannot write the report {safe_text(out)}: {exc.strerror}") from exc


FINDING_STATES = (STATE_WEAKENED, STATE_INVALID, STATE_CONTRADICTION, STATE_APPROVAL_MISMATCH)


def _tier_bucket(e: Entry) -> str:
    if not e.probe.constructible:
        return TIER_NONE
    if e.probe.errors and e.change.state != STATE_CONTRADICTION:
        return "invalid"
    return str((e.probe.data or {}).get("tier", "invalid"))


def _source_counts(entries: list[Entry]) -> dict[str, int]:
    counts = {s: 0 for s in DECLARATION_SOURCES}
    for e in entries:
        decl = (e.probe.data or {}).get("declaration")
        src = decl.get("source") if isinstance(decl, dict) else None
        if src in counts:
            counts[src] += 1
    return counts


def _manifest_provenance(manifest: Manifest | None, listed: int) -> str:
    where = f"`{MANIFEST_PATH.as_posix()}`"
    if manifest is None:
        return (
            f"The not-constructible manifest {where} is absent: either every declared entry received a "
            "probe, or the derivation never recorded the entries it could not probe. This audit did not "
            "check which, so entries without a probe are not counted."
        )
    if not manifest.readable:
        return f"The not-constructible manifest {where} is present but unreadable (see Findings); none of its entries is counted."
    if listed == 0:
        return f"The not-constructible manifest {where} lists 0 entries: the derivation recorded no entry it could not probe."
    return f"The not-constructible manifest {where} lists {listed} entr{'y' if listed == 1 else 'ies'} no probe could be constructed for; each is not probed."


def _headline(not_probed: int, total: int, listed: int, manifest: Manifest | None) -> str:
    if manifest is None:
        return (
            f"**Not probed: {not_probed} of {total} probes.** No not-constructible manifest, so entries "
            "the derivation could not probe are not counted here."
        )
    if not manifest.readable:
        return (
            f"**Not probed: {not_probed} of {total} probes.** The not-constructible manifest is unreadable, "
            "so entries the derivation could not probe are not counted here."
        )
    return f"**Not probed: {not_probed} of {total} entries, {listed} of them not constructible.**"


def render(repo: Path, head: str, entries: list[Entry], include_t2: bool, run_at: str, empty_reason: str | None,
           manifest: Manifest | None = None, manifest_findings: list[str] | None = None) -> str:
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
            f"- {_manifest_provenance(manifest, 0)}",
            f"- Run at: {run_at} (UTC), HEAD {head[:12]}",
        ]
        return "\n".join(lines) + "\n"

    probe_rows = [e for e in entries if e.probe.constructible]
    listed = total - len(probe_rows)
    lines += [_headline(not_probed, total, listed, manifest), ""]
    lines += ["## Provenance", ""]
    lines.append(
        f"- Audited set: the {len(probe_rows)} probe file(s) on disk under `{PROBE_DIR.as_posix()}/` plus "
        f"{listed} not-constructible manifest entr{'y' if listed == 1 else 'ies'}, {total} in all, at HEAD "
        f"{head[:12]}. This run executed stored probes; it read no declaration to find new entries."
    )
    lines.append(f"- {_manifest_provenance(manifest, listed)}")
    by_source = _source_counts(probe_rows)
    covered = ", ".join(f"{s} ({n})" for s, n in by_source.items() if n)
    uncovered = [s for s, n in by_source.items() if not n]
    lines.append(f"- Declaration sources covered by the probe set: {covered or 'none'}.")
    if uncovered:
        lines.append(f"- Declaration sources with no probe: {', '.join(uncovered)}. This audit can't speak about them.")
    unprobeable = ", ".join(f"{s} ({n})" for s, n in _source_counts([e for e in entries if not e.probe.constructible]).items() if n)
    if unprobeable:
        lines.append(f"- Declaration sources with not-constructible entries: {unprobeable}.")
    reconfirmed = [e.probe.pid for e in probe_rows if not e.probe.errors and is_reconfirmed(e.probe.data)]
    if reconfirmed:
        lines.append(f"- {PROVENANCE_RECONFIRMED}: {len(reconfirmed)} ({md_text(', '.join(reconfirmed))}).")
    lines.append(f"- Tier T2: {'requested (--include-t2)' if include_t2 else 'not requested; every T2 probe is not probed'}.")
    lines.append(f"- Run at: {run_at} (UTC).")
    lines.append("")

    lines += ["## Reach per tier", "", "| Tier | reached | partially reached | not reached | not probed |", "|---|---|---|---|---|"]
    for tier in ("T0", "T1", "T2", "invalid", TIER_NONE):
        subset = [e for e in entries if _tier_bucket(e) == tier]
        if tier in ("invalid", TIER_NONE) and not subset:
            continue
        counts = [sum(1 for e in subset if e.outcome.cls == c) for c in CLASSES]
        lines.append(f"| {tier} | " + " | ".join(str(c) for c in counts) + " |")
    lines.append("")

    findings = [e for e in entries if e.change.state in FINDING_STATES]
    lines += ["## Findings", ""]
    for text in manifest_findings or []:
        lines.append(f"- **invalid manifest** ({cell(MANIFEST_PATH.as_posix())}): {md_text(text)}")
    for e in findings:
        if e.change.state == STATE_WEAKENED:
            kind, detail = "weakened", e.change.reason
        elif e.change.state == STATE_CONTRADICTION:
            kind, detail = "contradiction", e.change.reason
        elif e.change.state == STATE_APPROVAL_MISMATCH:
            kind, detail = "approval mismatch", e.change.reason
        else:
            kind = "invalid probe" if e.probe.constructible else "invalid manifest entry"
            detail = "; ".join(e.probe.errors)
        lines.append(f"- **{kind}** {code_span(e.probe.pid)} ({cell(e.probe.file)}): {md_text(detail)}")
    if not findings and not manifest_findings:
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
            cell(data.get("tier", "—") if e.probe.constructible else "none"), e.executed_at or "not executed",
            cell(derived), cell(change),
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
    manifest = load_manifest(repo, yaml, validator_cls)
    listed = {e.pid: e for e in manifest.entries} if manifest else {}
    manifest_findings = list(manifest.errors) if manifest else []
    empty_reason = None
    if not (repo / PROBE_DIR).is_dir():
        empty_reason = f"`{PROBE_DIR.as_posix()}/` does not exist in this repository."
    elif not probes and not listed and not manifest_findings:
        empty_reason = f"`{PROBE_DIR.as_posix()}/` holds no probe file (*.yml, *.yaml besides `{MANIFEST_NAME}`)."

    entries: list[Entry] = []
    for probe in probes:
        twin = listed.pop(probe.pid, None)
        if twin is not None:
            # Counted once, as not probed; the manifest row is folded into this one.
            entries.append(contradiction_entry(probe, twin))
        else:
            entries.append(evaluate(repo, git, probe, yaml, include_t2, env_timeout, clock))
    entries += [not_constructible_entry(item) for item in listed.values()]
    text = render(repo, head, entries, include_t2, run_at, empty_reason, manifest, manifest_findings)
    write_report(out, text)

    if manifest_findings or any(e.change.state in FINDING_STATES for e in entries):
        return EXIT_FINDINGS, out
    if not probes:
        # Nothing was executed, whether or not the manifest lists entries.
        return EXIT_NO_PROBES, out
    return EXIT_OK, out


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Execute the stored capability-reach probes of a local repository and write the report.",
        epilog="Exit codes: 0 report written, 1 runtime error, 2 usage error or non-local target, "
        "3 no probe file (nothing executed), 4 report written with findings, 5 PyYAML/jsonschema missing.",
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
        EXIT_NO_PROBES: "no probe file, nothing executed; the report says so (not a clean result)",
        EXIT_FINDINGS: "report written with findings (weakened, invalid, or unapproved-content probes, or a manifest finding)",
    }
    print(f"reach_audit: {messages[code]}: {out}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
