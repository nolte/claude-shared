#!/usr/bin/env python3
"""Execute a repository's stored capability-reach probes and write the report.

The executor half of spec/project/capability-reach-audit/: it reads the approved
probe set from ``<repo>/project/reach-probes/``, decides per probe from the git
history whether the probe may run at all (declaration changed -> stale, probe
changed -> weakened), runs the environment and observation steps of the probes
that may, compares each raw observation against the probe's typed expectation,
and writes ``<repo>/.audits/capability-reach/<YYYY-MM-DD>.md``.

The runner, never the probe, decides the class. A probe file has no field in
which to state a verdict (schemas/reach-probe-v1.3.schema.yaml), and the
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

The probe set also has to answer for what it no longer contains. Every probe id
that a committed file under ``project/reach-probes/`` carried anywhere in the
history of HEAD (merges included) and that no probe file carries now is reported
``removed``, and so is the earlier probe of an exchange under the same id (an id
whose current file's own history took it only after another file had it). The
one exit is an approved, committed record in the retirement manifest
``project/reach-probes/_retired.yml`` (schemas/reach-retired-v1.0.schema.yaml);
every report lists the retired ids. The runner writes neither manifest.

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
  2  usage error: bad arguments, the target is not a local git working copy, or
     its probe directory (or project/ above it) is a symlink
  3  no probe file: project/reach-probes/ is absent or holds no probe file
     besides the manifest, so nothing was executed and it is never a clean
     result. A manifest listing entries does not change the code: the report
     then counts them (every entry not probed) instead of saying there is no
     probe set, but a run whose only entries are not constructible measured
     nothing either.
  4  report written, and it carries findings: weakened or invalid probes
     (a symlinked probe file included), an approval whose observation digest no
     longer matches the observation step, an unreadable manifest or an invalid
     manifest entry, a manifest id listed twice, an id that is both a probe
     file and a manifest entry, an invalid supersedes record, a removed probe
     id, or a retirement record that is invalid, contradicts a probe file, or
     sits in an unreadable retirement manifest. A superseded or a retired
     probe is no finding. Takes precedence over 3.
  5  PyYAML or jsonschema is not installed
  6  --check-migration only: a migration candidate is not clean (stale,
     weakened, invalid, also a manifest entry, carrying an invalid supersedes
     record, or otherwise not executable as approved) or the manifest is
     unreadable, so the migration to section anchors is refused; a superseded
     probe is no candidate; nothing is written

Usage:
  python reach_audit.py --repo ~/repos/github/kamerplanter
  python reach_audit.py --repo . --include-t2
  python reach_audit.py --repo . --check-migration
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
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterator

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
# The retirement manifest (schemas/reach-retired-v1.0.schema.yaml): the probe ids
# that left the probe set through an approved record. The probe loader and the
# history scan skip both manifest names.
RETIRED_NAME = "_retired.yml"
RETIRED_PATH = PROBE_DIR / RETIRED_NAME
MANIFEST_NAMES = (MANIFEST_NAME, RETIRED_NAME)
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
# How many bytes of historical probe revisions one `git cat-file --batch` call
# returns. Every revision is read and parsed for its id, whatever its size (as the
# probe loader reads a file at HEAD); the bound only keeps the runner from holding
# a long history in memory at once. A revision larger than it is read on its own.
MAX_HISTORY_BATCH_BYTES = 1024 * 1024
# Git modes of the tree entries the probe loader would read: regular files (by
# suffix) and symlinks (any name, reported and never read).
_FILE_MODES = ("100644", "100755")
_SYMLINK_MODE = "120000"
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
# A git object id: SHA-1 (40 hex) or SHA-256 (64 hex). Reading accepts both, so a
# section anchor, which hashes bytes rather than git objects, works in either repository.
_OBJECT_ID_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
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
EXIT_MIGRATION_REFUSED = 6

INSTALL_HINT = (
    "reach_audit: dependency missing ({err}). The runner validates every probe "
    "against the probe schema and cannot do so without PyYAML and jsonschema.\n"
    "Install them with:  pip install 'PyYAML>=6' 'jsonschema>=4.21'"
)

# Ids one probe may supersede (schema maxItems): a replacement covers one
# declaration entry, so a few weakened predecessors at most; the cap bounds the
# record graph the runner resolves.
MAX_SUPERSEDES = 8

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
# A weakened probe that a clean, approved probe lists in ``supersedes`` (v1.3).
STATE_SUPERSEDED = "superseded"
# The finding kind of a supersedes record that takes no effect for a reason the
# record itself carries (no such probe, itself, a cycle, not weakened, another entry).
FINDING_SUPERSEDE = "invalid supersede"
# A probe id that left the probe set without an effective retirement record: a
# committed probe file carried it in HEAD's history and no probe file carries it
# now, or the file carrying it now took it over from another one (an exchange).
STATE_REMOVED = "removed"
# The finding kinds of the retirement manifest: a record for an id a probe file
# still carries; a record that fails the schema, repeats an id, or names an id no
# committed probe file ever carried; a manifest that can't be read at all.
FINDING_RETIRED_CONTRADICTION = "retirement contradiction"
FINDING_RETIRED_INVALID = "invalid retirement record"
FINDING_RETIRED_MANIFEST = "invalid retirement manifest"
RETIREMENT_REASONS = ("capability-removed", "declaration-removed", "duplicate", "derived-in-error")

DECLARATION_SOURCES = ("requirement", "endpoint", "capability", "inventory")

REASON_NOT_APPROVED = "not approved"
REASON_INVALID_PROBE = "probe fails the probe schema"
REASON_T2 = "tier T2 not requested"
REASON_STALE = "declaration changed since derivation"
REASON_NOT_CONSTRUCTIBLE = "not constructible"
REASON_DIGEST_MISMATCH = "approval does not cover the current observation step"
NOTE_NO_DIGEST = "approval carries no observation digest"
REASON_SILENT = "observation step printed nothing"
NOTE_RECONFIRMED = "approval is a re-confirmation, not a re-derivation"
PROVENANCE_RECONFIRMED = "Probes whose approval is a re-confirmation rather than a re-derivation"
PROVENANCE_SUPERSEDED = "Weakened probes superseded by a clean, approved probe, not executed"
NEW_SINCE_PREVIOUS = "new since the manifest's previous commit"

NOT_CONSTRUCTIBLE_REASONS = (
    "scope_not_countable",
    "needs_model_judgement",
    "effect_in_third_party",
    "missing_environment_target",
    "missing_observation_helper",
)
# Per-tier table bucket of the entries that have no tier because they have no probe.
TIER_NONE = "none (not constructible)"
# Per-tier table bucket of the removed probe ids: no probe file is left to run.
TIER_REMOVED = "none (removed)"

# The structural part of schemas/reach-probe-v1.3.schema.yaml (annotations
# stripped). The schemas/ tree ships with the nolte-shared payload, not with this
# plugin, so the runner carries its own copy; tests/test_reach_audit.py fails when
# the two drift apart.
_TASK_NAME = {"type": "string", "pattern": "^[A-Za-z0-9_][A-Za-z0-9_:.-]*$"}
PROBE_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://github.com/nolte/claude-shared/blob/main/schemas/reach-probe-v1.3.schema.yaml",
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
        "supersedes": {
            "type": "array",
            "minItems": 1,
            "uniqueItems": True,
            "maxItems": MAX_SUPERSEDES,
            "items": {"type": "string", "pattern": "^[a-z0-9]+(-[a-z0-9]+)*$"},
        },
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


# The structural part of schemas/reach-retired-v1.0.schema.yaml, embedded for the
# same reason as PROBE_SCHEMA and pinned to it by the same parity test. The
# approval is the probe's Approval definition.
RETIRED_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://github.com/nolte/claude-shared/blob/main/schemas/reach-retired-v1.0.schema.yaml",
    "type": "object",
    "required": ["entries"],
    "additionalProperties": False,
    "properties": {
        "entries": {"type": "array", "items": {"$ref": "#/$defs/RetiredEntry"}},
    },
    "$defs": {
        "RetiredEntry": {
            "type": "object",
            "required": ["id", "reason", "detail", "recorded_at", "last_revision"],
            "additionalProperties": False,
            "properties": {
                "id": {"type": "string", "minLength": 1},
                "reason": {"type": "string", "enum": list(RETIREMENT_REASONS)},
                "detail": {"type": "string", "minLength": 1},
                "recorded_at": {
                    "type": "string",
                    "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}(:[0-9]{2})?Z$",
                },
                "last_revision": {"type": "string", "pattern": "^(?:[0-9a-f]{40}|[0-9a-f]{64})$"},
                "approval": {"$ref": "#/$defs/Approval"},
            },
        },
        "Approval": copy.deepcopy(PROBE_SCHEMA["$defs"]["Approval"]),
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


def load_yaml(yaml: Any, text: str) -> Any:
    """Parse ``text`` with the one YAML loader of this runner, for every document it reads.

    libyaml's safe loader where PyYAML has it, the pure-Python safe loader
    otherwise; both build only plain data. The two disagree on some input (a tab
    after ``id:`` is an error to one and a separator to the other), so a probe's
    id read from history and the id read from the working tree must come from
    the same loader, or one file could carry two ids at once and hide a removal.
    """
    return yaml.load(text, Loader=getattr(yaml, "CSafeLoader", yaml.SafeLoader))  # noqa: S506 - a safe loader


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
        # file_log() per path: the history does not change during a run, and the
        # removal check reads the same followed histories as change detection.
        self._file_logs: dict[str, list[tuple[str, str, str, str]]] = {}
        # probe_set_history() per HEAD commit (shared_probe_set_history()): one
        # walk of the probe directory serves the copy cut and the removal check.
        self.probe_sets: dict[str, "ProbeHistory"] = {}

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
        return self.out("--literal-pathspecs", "log", "-1", "--format=%H", rev, "--", path).strip() or None

    def is_dirty(self, path: str) -> bool:
        """Uncommitted changes to ``path``; literal pathspecs keep a name like ``w[x].yml`` from matching ``wx.yml``."""
        return bool(self.out("--literal-pathspecs", "status", "--porcelain", "--untracked-files=no", "--",
                             path).strip())

    def file_history(self, path: str) -> list[tuple[str, str]]:
        """(commit, path at that commit), newest first, following renames.

        Following renames matters: without it, renaming a weakened probe would make
        the rename commit look like the probe's first appearance.

        ``--no-merges`` pins the walk to non-merge commits on every git version. Up to
        git 2.55 ``--follow`` never diffed a merge, so a file a merge commit adds had no
        history and a merge was never a creating commit (SEC-101). Git 2.56 runs copy
        detection on merges while following: a probe added in a merge silently took
        over the history of a similar kept probe, without the merge itself, and so
        escaped the supersede cut.

        The walk is therefore blind to a merge commit whose result for the probe
        differs from every parent (an "evil merge": a conflict resolution, or an
        edit made while merging). ``--follow`` never listed such a merge on any
        version, so it falls between two listed revisions unseen. Every check that
        relies on "no probe change between these revisions" asks merges_changing()
        about that span instead (_merges_changing).

        Nor does the walk follow a rename made inside a merge, or start at a file a
        merge created: the history then begins at a later plain commit that edits
        the file, or renames it out of a path that merge made. file_log() keeps the
        status git reports for each listed revision, and _origin_problem() reports
        a history whose oldest revision is no addition as incomplete instead of
        reading that commit as the probe's first.
        """
        return [(commit, path_then) for commit, path_then, _, _ in self.file_log(path)]

    def file_log(self, path: str) -> list[tuple[str, str, str, str]]:
        """file_history() with git's status per revision: ``(commit, path, status, source)``.

        ``status`` is the letter ``--name-status`` reports for the followed file
        (``A`` added, ``M`` modified, ``R``/``C`` renamed or copied, ``D``
        deleted, ``T`` type change; empty when the commit lists no change of it),
        and ``source`` the path a rename or copy came from. ``--follow`` reports
        the status of the comparison it used to follow the file, so an ``A`` at
        the oldest listed revision means the walk reached the commit that brought
        the file into being; a root commit is compared against the empty tree and
        reports ``A`` as well. So would every boundary commit of a shallow clone,
        which require_local_working_copy() therefore refuses. Only
        lines carrying a tab are file lines; ``--no-show-signature`` and
        ``--no-color`` keep the repository's log configuration out of them, and
        literal pathspecs keep a probe named like ``w[x].yml`` from matching the
        history of ``wx.yml``.
        """
        if path in self._file_logs:
            return list(self._file_logs[path])
        raw = self.out("--literal-pathspecs", "log", "--follow", "--no-merges", "--no-show-signature", "--no-color", "--format=%x00%H",
                       "--name-status", "--", path)
        history: list[tuple[str, str, str, str]] = []
        for block in raw.split("\x00")[1:]:
            lines = [ln for ln in block.splitlines() if ln.strip()]
            if not lines:
                continue
            files = [ln.split("\t") for ln in lines[1:] if "\t" in ln]
            if not files:
                history.append((lines[0].strip(), path, "", ""))
                continue
            fields = files[0]
            status = fields[0][:1]
            source = fields[1] if status in ("R", "C") and len(fields) > 2 else ""
            history.append((lines[0].strip(), fields[-1], status, source))
        self._file_logs[path] = history
        return list(history)

    def probe_dir_log(self) -> str:
        """Every change under the probe directory in HEAD's history, merges included, newest first.

        One walk, read by probe_set_history(): ``-z`` records, each commit as
        ``\\x01<commit> <parents>`` followed by raw diff records
        ``:<old mode> <new mode> <old blob> <new blob> <status>`` and the path.
        ``--full-history`` walks every parent of every merge, so a probe that
        lived only on a merged side branch is seen; ``--diff-merges=separate``
        diffs a merge against each parent it differs from, so a file a merge
        added, changed, or dropped is seen too; ``--root`` diffs the root commit
        whatever ``log.showRoot`` says. ``--no-renames`` reports a rename as a
        deletion and an addition (identity is the id, not the path),
        ``--no-follow`` keeps ``log.follow`` out, ``--topo-order`` lists every
        commit before its parents, and literal pathspecs keep the directory name
        from being read as a pattern.
        """
        return self.out("--literal-pathspecs", "log", "-z", "--no-follow", "--full-history", "--topo-order",
                        "--diff-merges=separate", "--root", "--no-renames", "--raw", "--no-abbrev",
                        "--no-show-signature", "--no-color", "--format=%x01%H %P", "HEAD", "--",
                        PROBE_DIR.as_posix())

    def tree_entries(self, commit: str, directory: str) -> list[tuple[str, str, str, str]]:
        """``(mode, type, hash, path)`` of each entry directly under ``directory`` at ``commit``."""
        if commit.startswith("-"):
            raise AuditError(f"refusing the revision {safe_text(commit)}")
        res = self.run("--literal-pathspecs", "ls-tree", "-z", commit, "--", directory.rstrip("/") + "/")
        if res.returncode != 0:
            return []
        entries = []
        for record in res.stdout.split("\x00"):
            meta, _, name = record.partition("\t")
            parts = meta.split()
            if name and len(parts) == 3:
                entries.append((parts[0], parts[1], parts[2], name))
        return entries

    def parents(self, commit: str) -> list[str]:
        """The parents of ``commit``, first parent first."""
        if commit.startswith("-"):
            raise AuditError(f"refusing the revision {safe_text(commit)}")
        return self.out("rev-list", "--parents", "-n", "1", commit, "--").split()[1:]

    def iter_blobs(self, blobs: list[str], batch_bytes: int) -> Iterator[tuple[str, bytes]]:
        """``(blob, bytes)`` for each blob, every one of them, a bounded batch at a time.

        The sizes come first (``cat-file --batch-check``); a blob the repository
        does not have, as in a partial clone, stops the run (AuditError): an id
        read from the file name in its place could hide a removal. Blobs are then
        read in batches of at most ``batch_bytes`` (``cat-file --batch``), one
        larger than that on its own, so the caller can parse and drop each batch
        instead of holding the whole history. The ids go through stdin, never
        through argv.
        """
        wanted = [b for b in dict.fromkeys(blobs) if _OBJECT_ID_RE.match(b)]
        if not wanted:
            return
        sizes: dict[str, int] = {}
        listing = self._batch(["cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize)"], wanted)
        for line in listing.decode("ascii", "replace").splitlines():
            parts = line.split()
            if len(parts) == 3 and parts[1] == "blob" and parts[2].isdigit():
                sizes[parts[0]] = int(parts[2])
        missing = [b for b in wanted if b not in sizes]
        if missing:
            raise AuditError(
                f"the history of {PROBE_DIR.as_posix()}/ names {len(missing)} probe revision(s) this repository "
                f"does not hold (first: {missing[0]}); a partial or incomplete clone hides which probe ids existed. "
                "Fetch the full history and objects (`git fetch --refetch`, or a clone without --filter) and run again."
            )
        chunk: list[str] = []
        total = 0
        for blob in wanted + [""]:
            if blob and sizes[blob] > batch_bytes:
                content = self.read_blob(blob)
                if content is None:
                    raise AuditError(f"`git cat-file blob {blob}` failed")
                yield blob, content
                continue
            if chunk and (not blob or total + sizes[blob] > batch_bytes):
                yield from self._read_batch(chunk)
                chunk, total = [], 0
            if blob:
                chunk.append(blob)
                total += sizes[blob]

    def _read_batch(self, blobs: list[str]) -> Iterator[tuple[str, bytes]]:
        data = self._batch(["cat-file", "--batch"], blobs)
        pos = 0
        for blob in blobs:
            end = data.find(b"\n", pos)
            header = data[pos:end].split() if end >= 0 else []
            if len(header) != 3 or header[0].decode("ascii", "replace") != blob or not header[2].isdigit():
                raise AuditError(f"`git cat-file --batch` returned an unexpected record for {blob}")
            size = int(header[2])
            yield blob, data[end + 1:end + 1 + size]
            pos = end + 1 + size + 1

    def _batch(self, args: list[str], ids: list[str]) -> bytes:
        try:
            res = subprocess.run(  # noqa: S603 - fixed argv, no shell
                ["git", "-C", str(self.repo), *args],
                input=("\n".join(ids) + "\n").encode("ascii"),
                capture_output=True,
                timeout=GIT_TIMEOUT_SECONDS,
                check=False,
            )
        except FileNotFoundError as exc:
            raise AuditError("`git` not found on PATH; the runner reads the target's history with it.") from exc
        except subprocess.TimeoutExpired as exc:
            raise AuditError(f"`git {' '.join(args)}` timed out after {GIT_TIMEOUT_SECONDS}s.") from exc
        if res.returncode != 0:
            raise AuditError(f"`git {' '.join(args)}` failed: {safe_text(res.stderr.decode('utf-8', 'replace'))}")
        return res.stdout

    def merges_changing(self, since: str, until: str, path: str) -> list[str]:
        """Merge commits in ``since..until`` whose ``path`` differs from every parent, newest first.

        ``--full-history`` walks every parent of every merge: default history
        simplification follows only the parent a merge is TREESAME to, and so
        drops a side branch whose net result for ``path`` matches the main line,
        an evil merge on it included. The combined diff (``-c``) names ``path``
        for a merge exactly when its result differs from every parent; a merge
        that took one side's version names nothing and is skipped, since that
        side's own commit is in file_history(). ``--no-follow``,
        ``--no-show-signature``, ``--no-color`` and ``--no-renames`` keep the
        repository's log and diff configuration from changing the output, and
        literal pathspecs keep ``path`` from matching other files.

        ``since..until`` is empty when ``since`` is not an ancestor of ``until``.
        file_history() orders by committer date, which the author sets, so a
        listed "older" revision can be a descendant of a newer one. The search
        then fails closed: it covers every merge reachable from ``until``.
        """
        if since.startswith("-") or until.startswith("-"):
            raise AuditError(f"refusing the revision range {safe_text(since)}..{safe_text(until)}")
        revisions = f"{since}..{until}" if self.is_ancestor_or_equal(since, until) else until
        raw = self.out("--literal-pathspecs", "log", "--no-follow", "--full-history", "--merges",
                       "--no-show-signature", "--no-color", "--no-renames", "-c", "--name-only",
                       "--format=%x00%H", revisions, "--", path)
        merges: list[str] = []
        for block in raw.split("\x00")[1:]:
            lines = [ln for ln in block.splitlines() if ln.strip()]
            if len(lines) > 1:
                merges.append(lines[0].strip())
        return merges

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
        if not _OBJECT_ID_RE.match(blob):
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


def require_real_probe_dir(repo: Path) -> None:
    """Refuse a probe directory reached through a symlink (exit 2).

    load_probes() would read the files the link points to, while git records the
    link and nothing under project/reach-probes/: the history scan would see
    every probe deleted, and the files on disk would carry no history to judge.
    Any symlink among ``project`` and ``project/reach-probes`` is refused before
    anything is read, whatever it points to.
    """
    current = repo
    for part in PROBE_DIR.parts:
        current = current / part
        if current.is_symlink():
            raise AuditError(
                f"{safe_text(current.relative_to(repo).as_posix())} is a symlink. The probe set must live in "
                f"{PROBE_DIR.as_posix()}/ as a real directory under version control; the runner does not follow "
                "links in the audited tree. Replace the link with the directory and commit it.",
                code=EXIT_USAGE,
            )


def require_local_working_copy(raw: str) -> Path:
    """R13: the target must be a local git working copy, checked out, with its full history (not shallow)."""
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
    # A shallow clone's boundary commits are compared against the empty tree, so
    # every file reads as added there: at depth 1 each probe's history is HEAD
    # alone and no later change to it can be seen. Refused before any change
    # detection; anything but a plain "false" (an old git echoing the option)
    # fails closed.
    shallow = git.run("rev-parse", "--is-shallow-repository")
    if shallow.returncode != 0 or shallow.stdout.strip() != "false":
        raise AuditError(
            f"--repo {raw!r} is a shallow clone (or its shallowness can't be determined: "
            f"{safe_text(shallow.stdout.strip() or shallow.stderr.strip(), 80)}). Change detection reads each "
            "probe's full history, and a shallow clone hides every change before its boundary; fetch the full "
            "history (`git fetch --unshallow`, or `fetch-depth: 0` in CI) and run again.",
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
        if file.name in MANIFEST_NAMES:
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
            data = load_yaml(yaml, read_inside(repo, file))
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
        data = load_yaml(yaml, read_inside(repo, path))
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
_COMMENT_RE = re.compile(r"^ {0,3}<!--")
_CELL_SPLIT_RE = re.compile(r"(?<!\\)\|")


def _markdown_structure(lines: list[bytes]) -> tuple[list[tuple[int, int, str]], list[tuple[int, str]]]:
    """``(index, level, first token)`` of each ATX heading and ``(index, first cell)`` of each pipe row.

    Lines inside fenced code blocks, inside an HTML comment block (from a line
    opening with ``<!--`` through the line holding ``-->``), and in a leading
    front-matter block are neither. Front matter opens on the first line, after a
    UTF-8 byte order mark if there is one, and needs a closing ``---`` or ``...``
    line; without one, the first line is a thematic break. A setext heading is no
    heading here, and a table row must start with a pipe: a locator that only
    hits one of them does not resolve, rather than cutting a section by a rule
    the document's renderer may not share.
    """
    text = [raw.decode("utf-8", "replace").rstrip("\r\n") for raw in lines]
    if text:
        text[0] = text[0].removeprefix("\ufeff")
    start = 0
    if text and text[0].rstrip() == "---":
        closing = next((i for i in range(1, len(text)) if text[i].rstrip() in ("---", "...")), None)
        start = closing + 1 if closing is not None else 0
    headings: list[tuple[int, int, str]] = []
    rows: list[tuple[int, str]] = []
    fence: tuple[str, int] | None = None
    comment = False
    for index in range(start, len(text)):
        line = text[index]
        if comment:
            comment = "-->" not in line
            continue
        opener = _FENCE_RE.match(line)
        if fence is not None:
            if opener and opener.group(1)[0] == fence[0] and len(opener.group(1)) >= fence[1] \
                    and not opener.group(2).strip():
                fence = None
            continue
        if opener and not (opener.group(1)[0] == "`" and "`" in opener.group(2)):
            fence = (opener.group(1)[0], len(opener.group(1)))
            continue
        if _COMMENT_RE.match(line):
            comment = "-->" not in line[line.index("<!--") + 4:]
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
        doc = load_yaml(yaml, text)
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


def probe_changes(git: Git, probe: Probe, yaml: Any, cut: frozenset[tuple[str, str]] = frozenset(),
                  ) -> tuple[str | None, list[str], bool, list[tuple[str, str]], list[str], str | None]:
    """The probe's derivation baseline, the commits that touched it since, dirtiness,
    the revisions before the baseline, the merge commits that changed it since, and
    why its listed history does not reach its origin (or None).

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

    The history is the probe's own (_own_log): git --follow pairs a new file
    with a similar one that stays in place as a copy and walks on into that
    file's revisions, so a probe written from the same template as an earlier
    one would take over the earlier probe's chain. The history therefore ends
    at the revision that created the probe as a copy of another file, and the
    probe is judged from there; a rename keeps the history.

    ``cut`` holds the ``(commit, path)`` revisions of the probes this one
    supersedes (supersede_cut()). The history ends before the first of them as
    well, since a replacement must be judged on its own derivation, not on the
    chain of the probe it replaces. Only those revisions end it, so the
    replacement's own revisions, under any earlier name, stay in the walk.

    The fifth value lists the merge commits after the baseline whose result for
    the probe differs from every parent (_merges_changing): file_history() never
    lists them, and each is as much an unapproved change as a later commit.

    The sixth value says why the listed history is incomplete (_origin_problem,
    _own_log): its oldest revision does not create the probe's path, so the
    probe came into being, or under this path, in a merge the walk can't follow;
    or the probe was copied onto a path that held an earlier file. A copy that
    ends the history is a complete origin. A history the supersede cut ended is
    exempt: it ends at the cut on purpose, and the cut is only made after
    _lineage_problem() proved the kept part ends at the commit that added the
    replacement's path.
    """
    own, origin = _own_log(git, probe, git.file_log(probe.file), yaml)
    history = [(commit, path_then) for commit, path_then, _, _ in own]
    if cut:
        history = history[:next((i for i, rev in enumerate(history) if rev in cut), len(history))]
    if not history:
        return None, [], False, [], [], None
    if len(history) < len(own):
        origin = None
    current = _anchor_key(probe.data) if probe.data else None
    run: list[str] = []
    for commit, path_then in history:
        if _derived_from_of(git.show(commit, path_then), yaml) != current:
            break
        run.append(commit)
    dirty = git.is_dirty(probe.file)
    if not run:
        # The newest listed revision already carries another derived_from than the
        # working tree: either the recording is uncommitted, or a merge after that
        # revision changed the probe, which file_history() cannot list. The newest
        # commit is the baseline; with neither found, fail closed as uncommitted.
        merges = [m for m, _ in _merges_changing(git, history[:1], "HEAD")]
        return history[0][0], [], dirty or not merges, [], merges, origin
    merges = [m for m, _ in _merges_changing(git, history[:len(run)], "HEAD")]
    return run[-1], run[:-1], dirty, history[len(run):], merges, origin


def _own_log(git: Git, probe: Probe, log: list[tuple[str, str, str, str]], yaml: Any,
             ) -> tuple[list[tuple[str, str, str, str]], str | None]:
    """The probe's own part of its followed ``log`` (Git.file_log()), and why it does not reach its origin, or None.

    git --follow reports a file created beside a similar one that stays in place
    as a copy (``C``) and walks on into the revisions of that source. A probe
    created as a copy of another probe file starts its own history there: it
    inherits neither the source's revisions nor its findings, and the source
    answers for its own. The log ends at the newest such revision, which is
    kept as the probe's origin. A copy ends it only when it is one:

    - the source is left untouched by the copying commit, as in its single
      parent. git reports a file whose source left in that commit as a rename
      (``R``), which keeps the history; a ``C`` whose source is gone or was
      rewritten in place in the same commit is read the same way, since the
      new file may then be the probe moved away from a path given to another
      file (as _lineage_problem() requires of a supersede cut).
    - every id the probe carried from the copy on is new there: no probe file
      carried it in any commit of HEAD's history outside the probe's own kept
      revisions, except in commits that descend from the copying one
      (ProbeHistory.writes, from shared_probe_set_history(), which reads every
      probe revision under the probe directory, merges and revisions --follow
      never lists included, with the file name stem standing in for a missing
      id as Probe.pid does). Otherwise the id was carried before: the copy may
      be that probe moved to a new file, or re-created after a deletion that
      hid its earlier revisions from the walk, and its history goes on.
    - the copy's path held no file in any commit before the copying one. A file
      deleted and re-added at the same path keeps its history (git --follow
      walks on through the deletion), but one re-added as a copy of another file
      sends the walk into that file instead, so the path's earlier revisions are
      not listed. That is reported as an incomplete history rather than read as
      a fresh probe.

    Without a copy that ends it, the whole log is the probe's own, and its
    oldest revision must create the probe's path (_origin_problem).
    """
    for i, (commit, path, status, source) in enumerate(log):
        if status != "C" or not source:
            continue
        parents = git.parents(commit)
        kept = git.blob_at(commit, source)
        if len(parents) != 1 or kept is None or kept != git.blob_at(parents[0], source):
            continue
        own = log[:i + 1]
        if not _ids_new_at(git, shared_probe_set_history(git, yaml), commit, probe.pid,
                           {(c, p) for c, p, _, _ in own}):
            continue
        earlier = git.out("--literal-pathspecs", "rev-list", "-n", "1", "--full-history", parents[0], "--",
                          path).strip()
        if earlier:
            return own, (f"the probe was created in {commit[:12]} as a copy of {safe_text(source)} at "
                         f"{safe_text(path)}, which already held a file in {earlier[:12]}: git follows the copy "
                         "instead of that path, so the path's earlier revisions are not in the listed history and "
                         "can't be judged; derive the probe under a path no earlier file used")
        return own, None
    return log, _origin_problem(*log[-1]) if log else None


def _ids_new_at(git: Git, history: "ProbeHistory", copying: str, pid: str, own: set[tuple[str, str]]) -> bool:
    """Whether every id the probe carried in ``own`` (and ``pid``, its id now) is new at ``copying``.

    New: each write of the id (ProbeHistory.writes) is one of ``own``, the
    probe's kept ``(commit, path)`` revisions, or lies in a commit that
    descends from ``copying`` (or is it). A write anywhere else, an ancestor or
    a side line merged later, means some probe file carried the id outside the
    probe's own history, so a copy cut could hide that file's revisions.
    """
    ids = {pid} | {carried for carried, writes in history.writes.items() if any(w in own for w in writes)}
    for carried in ids:
        for commit, path in history.writes.get(carried, []):
            if (commit, path) not in own and not git.is_ancestor_or_equal(copying, commit):
                return False
    return True


def _origin_problem(commit: str, path: str, status: str, source: str) -> str | None:
    """Why the probe's oldest listed revision is not where it came into being, or None.

    file_history() lists non-merge commits only and follows no rename made
    inside a merge, so a probe created in a merge, or moved there in one (with
    any edit made in the same merge), has a history that starts at a later
    plain commit. Read as the first commit, that commit would become the
    derivation baseline and launder the merge.

    The oldest listed revision is complete only when git reports it as an
    addition (``status`` ``A``, from Git.file_log()): a commit that brought the
    file into being from nothing, or a root commit. A shallow clone's boundary
    reports ``A`` for every file too and would hide any change before it, so a
    shallow clone is refused before change detection runs
    (require_local_working_copy()). A modification or a
    deletion means the file already existed before it. A rename or copy means
    ``--follow`` switched to ``source`` and found no listed commit of it, so
    ``source`` came from a merge: checking only that the commit adds ``path``
    would accept a plain rename out of a path a merge created. A copy reaches
    this check only when it does not end the probe's own history (_own_log):
    the probe's id came from its source, or the source left in that commit.
    """
    if status == "A":
        return None
    what = {
        "M": "a change to it",
        "R": f"a rename from {safe_text(source)}",
        "C": f"a copy from {safe_text(source)}",
        "D": "its deletion",
        "T": "a change of its type",
    }.get(status, "no change to it")
    return (f"the probe's oldest listed revision {commit[:12]} does not create {safe_text(path)} but records {what}: "
            "the probe's origin isn't in its listed history but in a merge the walk can't follow, and a "
            "derivation recorded in a merge cannot be judged")


def _merges_changing(git: Git, revisions: list[tuple[str, str]], until: str) -> list[tuple[str, str]]:
    """``(merge, path)`` for each merge commit that changed the probe in the span of ``revisions``.

    ``revisions`` are probe revisions ``(commit, path)`` newest first, as
    file_history() lists them; the span runs from the oldest of them up to
    ``until`` (a later revision, or HEAD). A merge whose result for the probe
    differs from every parent sits between two listed revisions unseen, so a
    check that relies on "no probe change in between" asks here.

    The path changes with a rename, so the span is cut where it does: each run
    of consecutive revisions under one path is searched from its oldest revision
    up to the next newer revision, the one that moved the probe away (or
    ``until`` for the newest run). A merge on that path before the move is
    found; one on a path the probe had already left, such as an unrelated file
    later placed there, is not the probe's change. A rename made inside a merge
    is not searched here: file_history() does not follow it, so the probe's
    revisions under its earlier name are not listed in the first place. It is
    caught by the history's start instead: git then reports the oldest listed
    revision as no addition (a change, or a rename out of the merge's path), and
    probe_changes() reports the history as incomplete (_origin_problem), which
    detect_change() surfaces as weakened.
    """
    segments: list[tuple[str, str, str]] = []  # (path, oldest commit, upper bound)
    upper = until
    for i, (commit, path) in enumerate(revisions):
        if i == 0 or path != revisions[i - 1][1]:
            if i:
                upper = revisions[i - 1][0]
            segments.append((path, commit, upper))
        else:
            segments[-1] = (path, commit, upper)
    found: list[tuple[str, str]] = []
    for path, start, end in segments:
        for merge in git.merges_changing(start, end, path):
            if merge not in (m for m, _ in found):
                found.append((merge, path))
    return found


def _merge_names(merges: list[str]) -> str:
    """The merge commits for a reason, each marked as a merge, oldest first per path searched."""
    return ", ".join(f"merge {m[:12]}" for m in reversed(merges))


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
        config = load_yaml(yaml, text) or {}
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
        doc = load_yaml(yaml, git.show(*revision) or "")
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


def _continuation_problem(git: Git, moved: str, baseline: str, earlier: list[tuple[str, str]], span: int,
                          yaml: Any) -> str | None:
    """Why the move cannot build on the previous derivation, or None.

    Every move of a content or section anchor (a re-derivation, a
    re-confirmation, a migration, a relabel) and of an inherited pin builds on
    the derivation it replaces. So the probe must still be the document that
    derivation recorded (no commit in between changed it: an intermediate plain
    probe change is never adopted), and that recording must itself have been
    legitimate, checked by the same rule, back to the probe's first commit or to
    a commit-anchor derivation, which keeps its pre-v1.1 rules. Otherwise one
    commit could weaken the probe under a self-made anchor and the next move,
    though justified on its own, would adopt that weakening.

    "No commit in between" includes merge commits: a merge that changed the probe
    anywhere from the recording up to ``baseline`` (the commit that made the
    move) is a probe change as well (_merges_changing), since file_history()
    lists none of them.
    """
    recording = earlier[span - 1]
    recording_doc = _probe_doc(git, recording, yaml)
    changed = [c for c, path in earlier[:span - 1] if _probe_doc(git, (c, path), yaml) != recording_doc]
    merges = [m for m, _ in _merges_changing(git, earlier[:span], baseline)]
    if changed or merges:
        names = [c[:12] for c in reversed(changed)] + ([_merge_names(merges)] if merges else [])
        return (f"{moved}, but the probe changed in {', '.join(names)} "
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
        return None  # a relabel: _rebaseline_problem holds it to the previous derivation
    if not changed:
        return f"{moved}, but {_unchanged_since(prev_df, rel)}"
    if prev_df == new_df:
        return _pure_move_problem(moved, prior_doc, new_doc)
    # The move must answer to a change of what the new anchor anchors on, not
    # only of something the previous anchor happened to cite.
    if git.blob_at(recording, new_rel) == new_blob:
        return (f"{moved}, but {safe_text(new_rel)} already held {safe_text(new_df[:12], 40)} when the previous "
                f"derivation was recorded in {recording[:12]}, so re-pointing at it shows no declaration change")
    return None


def _pure_move_problem(moved: str, prior_doc: dict[str, Any], new_doc: dict[str, Any]) -> str | None:
    """Same anchor, new declaration path: clean only when it changed nothing else.

    Like every move it is also held to the previous derivation (_continuation_problem).

    The re-derive that follows a rename re-approves the probe, so the approval
    stamp may move with the path; the observation digest inside it is still
    checked on every run.
    """
    pure_move = (("declaration", "path"), ("approval",))
    if _without(new_doc, *pure_move) != _without(prior_doc, *pure_move):
        return (f"{moved}, but the same commit changed the probe beyond declaration.path, "
                "which a pure move of the declaration does not justify")
    return None


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
        return None  # a relabel: _rebaseline_problem holds it to the previous derivation
    if not changed:
        return f"{moved}, but {_unchanged_since(prev_df, rel)}"
    if prev_df == new_df:
        return _pure_move_problem(moved, prior_doc, new_doc)
    # The move must answer to a change of what the new anchor anchors on: at
    # least one of its sections differs from the recording commit.
    if not _section_mismatches(git, recording, new_rel, locators):
        if new_rel != rel:
            return (f"{moved}, but {safe_text(new_rel)} already held these sections when the previous derivation "
                    f"was recorded in {recording[:12]}, so re-pointing at it shows no declaration change")
        return (f"{moved}, but none of the sections it now anchors on changed since the previous derivation "
                f"was recorded in {recording[:12]}")
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
    (path, location, locators) is a weakening. Like every move it is also held
    to the previous derivation (_continuation_problem).
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
    return None


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
    (_reconfirmation_problem). Every move but one onto a commit anchor must
    finally build on a legitimate previous derivation with no probe change in
    between (_continuation_problem).

    All of this presumes the baseline itself made the move, and the revisions
    file_history() lists hold no merge. A merge that changed the anchor key
    between the previous derivation's revisions and the baseline recorded a
    derivation the walk cannot see, so the move is attributed to the wrong
    commit and the later commit's own changes would ride on it: that is refused
    for every anchor kind (_key_moving_merges). A merge that changed only the
    rest of the probe is a plain probe change, held to the same rule as a
    non-merge one: refused by _continuation_problem, accepted with a move onto
    a commit anchor as before v1.1.
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
    key_moving = _key_moving_merges(git, baseline, earlier, yaml)
    if key_moving:
        return (f"{moved}, but {_merge_names(key_moving)} changed derived_from after the previous derivation was "
                f"recorded and before {baseline[:12]}, and a derivation recorded in a merge cannot be judged")
    problem = _anchor_move_problem(git, moved, decl, prior_doc, prev_df, new_df, baseline, earlier, yaml, new_doc)
    if problem:
        return problem
    approval = new_doc.get("approval")
    reconfirmed = isinstance(approval, dict) and approval.get("mode") == MODE_RECONFIRMED
    if reconfirmed and prev_df != new_df:
        # A pure move (prev_df == new_df) is already held to "nothing but the path
        # and the approval changed", whatever mode the approval carries over.
        problem = _reconfirmation_problem(git, moved, earlier, yaml, new_doc)
        if problem:
            return problem
    if not (reconfirmed or decl.get("inherited_spec") or _is_content_anchor(new_df) or _is_section_anchor(new_df)):
        return None  # a move onto a commit anchor keeps the pre-v1.1 rules
    return _continuation_problem(git, moved, baseline, earlier, _run_length(git, earlier, yaml), yaml)


def _key_moving_merges(git: Git, baseline: str, earlier: list[tuple[str, str]], yaml: Any) -> list[str]:
    """Merges from the previous derivation's recording up to ``baseline`` that changed the anchor key.

    The previous derivation is the run of ``earlier`` carrying the anchor key of
    ``earlier[0]`` (_run_length); every listed revision in it carries that key,
    so a merge in that span whose probe carries another key (or no readable
    probe) recorded a derivation of its own that file_history() never lists.
    """
    key = _derived_from_of(git.show(*earlier[0]), yaml)
    span = _run_length(git, earlier, yaml)
    return [merge for merge, path in _merges_changing(git, earlier[:span], baseline)
            if _derived_from_of(git.show(merge, path), yaml) != key]


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
    if _is_content_anchor(prev_df) or _is_section_anchor(prev_df):
        # A content or section anchor names no commit, so a move from it back onto
        # a commit anchor is refused, as before v1.2. The recording-commit fallback
        # below stands in only for a commit anchor a squash merge dropped; applied
        # here it would compare the whole file for an anchor that never covered it
        # and skip proving the previous anchor, which launders a weakening.
        return f"{moved}, but the two cannot both be resolved to commits, so no declaration change can be shown"
    prev_commit, new_commit = git.resolve_commit(prev_df), git.resolve_commit(new_df)
    if prev_commit is not None and new_commit is not None:
        last = git.last_commit(rel, new_commit)
        if last is not None and not git.is_ancestor_or_equal(last, prev_commit):
            return None
        return f"{moved}, but {safe_text(rel)} did not change in between"
    # A squash merge drops the commits a v1.0 derivation named, but the commits
    # that recorded them are still here (as in _prior_anchor): the declaration's
    # content there stands in for an anchor that no longer resolves. The walk
    # back over earlier derivations (_continuation_problem) reaches such moves.
    recording = earlier[_run_length(git, earlier, yaml) - 1][0]
    before = git.blob_at(prev_commit or recording, rel)
    after = git.blob_at(new_commit or baseline, rel)
    if before is None or after is None:
        return f"{moved}, but the two cannot both be resolved to commits, so no declaration change can be shown"
    if before != after:
        return None
    return f"{moved}, but {safe_text(rel)} did not change in between"


def detect_change(repo: Path, git: Git, probe: Probe, yaml: Any,
                  cut: frozenset[tuple[str, str]] = frozenset()) -> ChangeState:
    """Classify one valid probe's change state from the target's history (``cut``: see probe_changes)."""
    data = probe.data or {}
    derived_from = data["derived_from"]
    baseline, later, dirty, earlier, merges, origin = probe_changes(git, probe, yaml, cut)
    if baseline is None:
        return ChangeState(
            STATE_UNCOMMITTED,
            "probe file is not committed; the approved set must be under version control, "
            "and an uncommitted probe has no derivation to compare against",
        )

    # The probe itself: any change after the recorded derivation is a weakening,
    # whether or not the declaration moved too (spec: "whether or not both changed
    # together"). Checked first so a combined change is surfaced as a finding.
    # A history that does not reach the probe's origin (_origin_problem) can't
    # show which state was approved, so it fails closed the same way.
    rebaseline = _rebaseline_problem(git, derived_from, baseline, earlier, yaml, data) if earlier else None
    if later or merges or dirty or rebaseline or origin:
        parts = [origin] if origin else []
        if rebaseline:
            parts.append(f"re-baselined without a declaration change: {rebaseline}")
        if later or merges:
            changes = [c[:12] for c in reversed(later)] + ([_merge_names(merges)] if merges else [])
            parts.append(f"probe changed in {', '.join(changes)} after its derivation was recorded in {baseline[:12]}")
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


def evaluate(repo: Path, git: Git, probe: Probe, yaml: Any, include_t2: bool, env_timeout: float,
             clock: Callable[[], datetime], change: ChangeState | None = None) -> Entry:
    """Judge and, when it may run, execute one entry; ``change``: its change state when already known."""
    if not probe.constructible:
        return not_constructible_entry(probe)
    if probe.errors:
        return Entry(probe, ChangeState(STATE_INVALID), Outcome(NOT_PROBED, reason=f"{REASON_INVALID_PROBE}: " + "; ".join(probe.errors)))
    data = probe.data or {}
    if change is None:
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


def superseded_entry(probe: Probe, change: ChangeState, by: list[str], unmet: list[str] | None = None) -> Entry:
    """A weakened probe replaced by a clean, approved probe: not probed, not executed, no finding.

    The reason keeps the weakening, so the report still says what was replaced
    and why; ``unmet`` notes the other records on it that take no effect.
    """
    why = f"superseded by {safe_text(', '.join(by), 200)}; it was weakened: {change.reason}"
    return Entry(probe, ChangeState(STATE_SUPERSEDED, why), Outcome(NOT_PROBED, reason=why), notes=list(unmet or []))


@dataclass
class Supersession:
    """The ``supersedes`` records of a probe set, resolved against the history (schema v1.3).

    ``replaced_by`` maps each superseded id to the ids of its clean, approved
    replacements; ``findings`` lists ``(probe, why)`` per record that takes no
    effect for a reason of its own; ``unmet`` notes, per weakened probe, a
    replacement that is not clean or approved, so the probe stays weakened;
    ``changes`` is each valid probe's change state as run judges it;
    ``notes`` has one line per effective record, with both expectations and tiers;
    ``probes`` maps each id to the valid probe file the records were resolved on.
    """

    replaced_by: dict[str, list[str]] = field(default_factory=dict)
    findings: list[tuple[Probe, str]] = field(default_factory=list)
    unmet: dict[str, list[str]] = field(default_factory=dict)
    changes: dict[str, ChangeState] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    probes: dict[str, Probe] = field(default_factory=dict)

    def superseded(self, probe: Probe) -> bool:
        """Whether this very probe file is superseded: not another file that only shares its id."""
        return self.probes.get(probe.pid) is probe and probe.pid in self.replaced_by


def _claims(probe: Probe) -> list[str]:
    """The ids a schema-valid probe file lists in ``supersedes``."""
    if probe.errors or not probe.constructible or not isinstance(probe.data, dict):
        return []
    return list(probe.data.get("supersedes") or [])


def _approved_state(data: dict[str, Any], change: ChangeState) -> ChangeState:
    """``change`` when it is clean and the approval covers the observation step, else why not."""
    if change.state != STATE_CLEAN:
        return change
    if "approval" not in data:
        return ChangeState(REASON_NOT_APPROVED, "the probe was never approved through the gate")
    approved_digest = data["approval"].get("observation_digest")
    if approved_digest is not None and approved_digest != observation_digest(data):
        return ChangeState(STATE_APPROVAL_MISMATCH, REASON_DIGEST_MISMATCH)
    return change


def _entry_key(data: dict[str, Any]) -> tuple[object, ...]:
    """The declaration entry a probe answers to: source, location, and the anchor it reads."""
    declaration = data.get("declaration")
    declaration = declaration if isinstance(declaration, dict) else {}
    return tuple(declaration.get(k) for k in ("source", "location", "path", "inherited_spec", "hub"))


def _lineage_problem(git: Git, claimant: str, history: list[tuple[str, str]], target: list[tuple[str, str]],
                     doc_of: Callable[[tuple[str, str]], dict[str, Any] | None]) -> str | None:
    """Why ending ``history`` (the claimant's, uncut) before ``target``'s revisions would cut its own, or None.

    The cut is sound only one way: the claimant was created as a copy of the
    superseded probe, which stays in place untouched. So the kept part must be
    nonempty and end at a single-parent commit that added the claimant's path;
    the path of the first cut revision must hold the same blob there as in the
    parent (a true copy: not a rename into the claimant, not a file rewritten
    in the creating commit); no cut revision may carry the claimant's id; and
    the target's history must not hold any path the claimant itself had.
    Otherwise the target descends from the claimant or sits on its earlier
    path, and its history holds the claimant's own revisions.
    """
    cut = set(target)
    kept = history[:next((i for i, rev in enumerate(history) if rev in cut), len(history))]
    if len(kept) == len(history):
        return None  # git pairs nothing: there is nothing to cut
    descends = ("whose history git pairs with this probe's own revisions (it descends from this probe or "
                "sits on its earlier path), so the record can't end this probe's history there")
    if not kept:
        return descends
    own_paths = {path for _, path in kept}
    created, path = kept[-1]
    _, source = history[len(kept)]
    parents = git.out("rev-list", "--parents", "-n", "1", created).split()[1:]
    if (len(parents) != 1 or any(p in own_paths for _, p in target)
            or git.entry_at(parents[0], path) is not None
            or git.blob_at(created, source) != git.blob_at(parents[0], source)):
        return descends
    for revision in history[len(kept):]:
        doc = doc_of(revision)
        if doc is not None and doc.get("id") == claimant:
            return descends
    return None


MAX_NOTE_VALUE_CHARS = 120


def _members(values: list[str]) -> str:
    """Up to MAX_LISTED_MEMBERS values as code spans, the rest counted and marked shortened."""
    shown = ", ".join(code_span(safe_text(v, MAX_NOTE_VALUE_CHARS)) for v in values[:MAX_LISTED_MEMBERS])
    rest = len(values) - MAX_LISTED_MEMBERS
    return (shown or "none") + (f" … and {rest} more (shortened)" if rest > 0 else "")


def _expected_side(data: dict[str, Any]) -> tuple[str, list[str] | None]:
    """One side of a supersede note: its expectation in short form, and its set members if it is a set."""
    expected = data.get("expected")
    expected = expected if isinstance(expected, dict) else {}
    tier = safe_text(data.get("tier"), 8)
    if expected.get("kind") == "count":
        unit = code_span(safe_text(expected.get("unit"), MAX_NOTE_VALUE_CHARS))
        return f"expected count {safe_text(expected.get('value'), 20)} {unit}, tier {tier}", None
    values = sorted(str(v) for v in expected.get("values") or [] if isinstance(expected.get("values"), list))
    unit = code_span(safe_text(expected.get("unit", "members"), MAX_NOTE_VALUE_CHARS))
    return f"expected set of {len(values)} {unit}, tier {tier}", values


def _supersede_note(old_id: str, old: dict[str, Any], new_id: str, new: dict[str, Any]) -> str:
    """The Provenance line of an effective record: the new side first, each side with its own budget.

    Values are code spans, so a comma inside a member can't read as a separator;
    a list longer than MAX_LISTED_MEMBERS is marked shortened. The line is
    built from safe parts and is never cut as a whole, so the new expectation
    can't vanish behind a long old one.
    """
    now, now_values = _expected_side(new)
    before, before_values = _expected_side(old)
    if now_values is not None and before_values is not None:
        added = [v for v in now_values if v not in set(before_values)]
        removed = [v for v in before_values if v not in set(now_values)]
        members = f"; members added: {_members(added)}; removed: {_members(removed)}"
    else:
        members = "".join(f"; {label} members: {_members(values)}"
                          for label, values in (("new", now_values), ("old", before_values)) if values is not None)
    return (f"Supersede {safe_text(old_id, 120)} by {safe_text(new_id, 120)}: now {now}; before {before}"
            f"{members}; the replacement's approval is the only check of this change.")


def _components(edges: dict[str, list[str]]) -> dict[str, int]:
    """Strongly connected component per node (iterative Tarjan): an edge inside one is part of a cycle."""
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    component: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    for root in edges:
        if root in index:
            continue
        work = [(root, 0)]
        while work:
            node, child = work.pop()
            if child == 0:
                index[node] = low[node] = len(index)
                stack.append(node)
                on_stack.add(node)
            successors = edges.get(node, [])
            if child < len(successors):
                work.append((node, child + 1))
                nxt = successors[child]
                if nxt not in index:
                    work.append((nxt, 0))
                elif nxt in on_stack:
                    low[node] = min(low[node], index[nxt])
                continue
            for succ in successors:
                if succ in on_stack:
                    low[node] = min(low[node], low[succ])
            if low[node] == index[node]:
                while True:
                    member = stack.pop()
                    on_stack.discard(member)
                    component[member] = index[node]
                    if member == node:
                        break
    return component


def _post_order(edges: dict[str, list[str]]) -> list[str]:
    """Every node after the nodes it reaches, except along a cycle (iterative depth-first search)."""
    order: list[str] = []
    seen: set[str] = set()
    for root in edges:
        if root in seen:
            continue
        seen.add(root)
        work = [(root, iter(edges.get(root, [])))]
        while work:
            node, successors = work[-1]
            nxt = next((s for s in successors if s not in seen), None)
            if nxt is None:
                work.pop()
                order.append(node)
            else:
                seen.add(nxt)
                work.append((nxt, iter(edges.get(nxt, []))))
    return order


TIER_T2 = "T2"


def resolve_supersedes(repo: Path, git: Git, probes: list[Probe], listed: set[str], yaml: Any) -> Supersession:
    """Decide which ``supersedes`` records take effect; the chain rule itself is untouched.

    Every probe is first judged on its uncut history. A record of probe R
    listing id W passes only when W is another valid probe file on disk, no
    cycle runs back from W to R, both answer to the same declaration entry
    (_entry_key), R's approval is a derivation (not a re-confirmation), R
    does not move the entry to T2 (the tier a default run withholds) unless W
    was T2, W's own verdict is weakened, and the cut is a one-way lineage
    (_lineage_problem); each failure is a finding. Only then is R judged on its
    history ended before W's revisions (probe_changes), since git --follow
    pairs a similar new file with the kept one (a copy that is R's own already
    ends there, _own_log; the cut also covers one that is not); the records take effect when R
    is then clean, approved, and its approval carries a matching observation
    digest, and are otherwise noted on W, which stays weakened. A record that
    takes no effect never changes R's verdict: R keeps its uncut one. Every
    effective record is listed with both expectations and tiers, since the
    replacement's approval is the only check of what changed.

    Iterative throughout: records are resolved in post order, so a target's
    verdict is known before its claimant's, and cycles are found as strongly
    connected components, so a long chain neither recurses nor repeats work.
    """
    by_id = {p.pid: p for p in probes if p.constructible and not p.errors and isinstance(p.data, dict)}
    result = Supersession(probes=by_id)
    edges = {pid: [t for t in _claims(p) if t != pid and t in by_id] for pid, p in by_id.items()}
    component = _components(edges)
    histories: dict[str, list[tuple[str, str]]] = {}

    def history(pid: str) -> list[tuple[str, str]]:
        if pid not in histories:
            histories[pid] = git.file_history(by_id[pid].file)
        return histories[pid]

    docs: dict[tuple[str, str], dict[str, Any] | None] = {}

    def doc_of(revision: tuple[str, str]) -> dict[str, Any] | None:
        if revision not in docs:
            docs[revision] = _probe_doc(git, revision, yaml)
        return docs[revision]

    for pid in _post_order(edges):
        probe = by_id[pid]
        data = probe.data
        uncut = detect_change(repo, git, probe, yaml)
        passed: list[str] = []
        for target in _claims(probe):
            shown = safe_text(target, 120)
            other = by_id.get(target)
            if target == pid:
                result.findings.append((probe, "supersedes lists the probe's own id"))
            elif other is None:
                what = "a not-constructible manifest entry" if target in listed else "no valid probe file"
                result.findings.append((probe, f"supersedes {shown}, which is {what} under "
                                               f"{PROBE_DIR.as_posix()}/; keep the superseded probe file, it is "
                                               "the record of what was replaced"))
            elif target in listed:
                result.findings.append((probe, f"supersedes {shown}, which is also a not-constructible manifest "
                                               "entry (a contradiction, reported as such)"))
            elif component[target] == component[pid]:
                result.findings.append((probe, f"supersedes {shown}, which leads back to it through supersedes "
                                               "(a cycle); no record in the cycle takes effect"))
            elif _entry_key(data) != _entry_key(other.data):
                result.findings.append((probe, f"supersedes {shown}, which declares another entry "
                                               "(declaration.source, location, path, inherited_spec or hub differ); "
                                               "a replacement answers to the same declaration entry"))
            elif is_reconfirmed(data):
                result.findings.append((probe, f"supersedes {shown} under approval.mode reconfirmed; a "
                                               "replacement is a new derivation and is approved as one"))
            elif data.get("tier") == TIER_T2 and other.data.get("tier") != TIER_T2:
                result.findings.append((probe, f"supersedes {shown} at tier T2, but {shown} is "
                                               f"{safe_text(other.data.get('tier'), 8)}; a default run withholds "
                                               "T2, so the replacement would drop the entry from it"))
            elif (replaced := result.changes[target]).state != STATE_WEAKENED:
                result.findings.append((probe, f"supersedes {shown}, which is {replaced.state}, not weakened; "
                                               "only a weakened probe can be superseded, and it keeps running"))
            elif lineage := _lineage_problem(git, pid, history(pid), history(target), doc_of):
                result.findings.append((probe, f"supersedes {shown}, {lineage}"))
            else:
                passed.append(target)
        result.changes[pid] = uncut
        if not passed:
            continue
        cut = frozenset(rev for target in passed for rev in history(target))
        cut_change = detect_change(repo, git, probe, yaml, cut)
        state = _approved_state(data, cut_change)
        why = None
        if pid in listed:
            why = f"it is a {STATE_CONTRADICTION} (also a not-constructible manifest entry) and never runs"
        elif state.state != STATE_CLEAN:
            why = f"it is {state.state}"
        elif not data["approval"].get("observation_digest"):
            why = "its approval carries no observation digest"  # SEC-003: bound to what runs
        for target in passed:
            if why:
                result.unmet.setdefault(target, []).append(f"supersede by {safe_text(pid, 120)} not in effect: {why}")
                continue
            result.replaced_by.setdefault(target, []).append(pid)
            result.notes.append(_supersede_note(target, by_id[target].data, pid, data))
        if why is None:
            result.changes[pid] = cut_change
    return result


# --------------------------------------------------------------------------- #
# Removal and retirement (spec §"Derivation, approval, and durability")
# --------------------------------------------------------------------------- #
# Why a removed id has no effective retirement record; the last part of its reason.
WHY_NO_RECORD = "no retirement record accounts for it"
WHY_MANIFEST_UNREADABLE = "the retirement manifest is unreadable (see Findings), so no record in it takes effect"
WHY_RECORD_INVALID = "its retirement record is invalid (see Findings), so it takes no effect"
WHY_RECORD_UNAPPROVED = "its retirement record carries no approval, so it takes no effect"
WHY_RECORD_UNCOMMITTED = "its retirement record is not committed, so it takes no effect"
WHY_REMOVAL_UNCOMMITTED = "a retirement record can't account for a removal that is not committed"
EXCHANGE_EXIT = ("a retirement record can't account for an exchange under the same id: give the replacement a "
                 "new id and retire this one, or restore the earlier file and supersede it")


@dataclass
class Removal:
    """One change that took an id off a probe path.

    ``commit`` changed ``path`` so that it no longer carries the id (deleted it,
    replaced it, or edited the id); ``carrier`` is the parent of ``commit`` in
    which ``path`` still carried it, so the last commit in which the probe existed.
    """

    commit: str
    path: str
    carrier: str


@dataclass
class ProbeHistory:
    """Every probe id a committed file under the probe directory carried in HEAD's history.

    ``writes`` lists per id the ``(commit, path)`` changes whose result carries
    it; ``removals`` the changes that took it off a path, newest first
    (``--topo-order``: a commit before its parents); ``at_head`` the paths that
    carry it in HEAD's own tree. ``commits`` and ``blobs`` count what the walk
    read, for the measurement of its cost.
    """

    head: str
    writes: dict[str, list[tuple[str, str]]] = field(default_factory=dict)
    removals: dict[str, list[Removal]] = field(default_factory=dict)
    at_head: dict[str, list[str]] = field(default_factory=dict)
    commits: int = 0
    blobs: int = 0

    @property
    def ids(self) -> set[str]:
        return set(self.writes) | set(self.removals) | set(self.at_head)

    def last(self, pid: str, paths: set[str] | None = None) -> tuple[str, str, bool] | None:
        """``(commit, path, uncommitted)``: where ``pid`` last existed, on ``paths`` only when given.

        HEAD itself when its tree still carries the id (the removal is then only
        in the working tree), otherwise the carrier of the newest removal.
        """
        for path in self.at_head.get(pid, []):
            if paths is None or path in paths:
                return self.head, path, True
        for removal in self.removals.get(pid, []):
            if paths is None or removal.path in paths:
                return removal.carrier, removal.path, False
        return None


def _probe_path(mode: str, path: str) -> bool:
    """Whether the tree entry ``(mode, path)`` is one the probe loader reads as a probe file.

    A regular file directly under the probe directory with a probe suffix, or a
    symlink there under any name (load_probes() lists it as a finding), and
    never one of the two manifests.
    """
    directory, _, name = path.rpartition("/")
    if directory != PROBE_DIR.as_posix() or name in MANIFEST_NAMES:
        return False
    if mode == _SYMLINK_MODE:
        return True
    return mode in _FILE_MODES and posixpath.splitext(name)[1] in PROBE_SUFFIXES


def _declared_id(content: bytes, yaml: Any) -> str | None:
    """The ``id`` a probe revision declares, or None when the file name stem stands in (R11).

    None exactly where Probe.pid falls back to the stem: content that is not
    UTF-8 YAML of a mapping with a string ``id``. Parsed with load_yaml(), the
    loader load_probes() uses at HEAD, and never cut off by size, so a revision
    reads as the same id in history as in the working tree.
    """
    try:
        doc = load_yaml(yaml, content.decode("utf-8"))
    except (yaml.YAMLError, UnicodeDecodeError, ValueError, RecursionError):
        return None
    return doc["id"] if isinstance(doc, dict) and isinstance(doc.get("id"), str) else None


_ZERO_OBJECT = re.compile(r"^0+$")


def shared_probe_set_history(git: Git, yaml: Any) -> ProbeHistory:
    """probe_set_history() at HEAD, read once per run and Git instance (Git.probe_sets)."""
    head = git.resolve_commit("HEAD") or ""
    if head not in git.probe_sets:
        git.probe_sets[head] = probe_set_history(git, yaml, head)
    return git.probe_sets[head]


def probe_set_history(git: Git, yaml: Any, head: str) -> ProbeHistory:
    """Read every probe id ever carried in HEAD's history from one walk and two blob reads.

    Git.probe_dir_log() lists each change under the probe directory with the
    blob before and after it, merges diffed against every parent they differ
    from. Every blob a probe path held at any commit of the history is the
    result of one of those changes, so their union is every probe revision that
    ever existed; each distinct blob is read once (Git.iter_blobs()). A change
    whose earlier blob carried an id that its later blob does not carry (or that
    deleted the path) is a removal of that id at that path; its carrier is the
    parent holding the earlier blob, which for a merge is looked up per parent.
    """
    raw = git.probe_dir_log()
    tokens = raw.split("\x00")
    changes: list[tuple[str, list[str], str, str, str, str, str]] = []
    commits: set[str] = set()
    commit, parents = "", []
    i = 0
    while i < len(tokens):
        token = tokens[i].lstrip("\n")
        if token.startswith("\x01"):
            fields = token[1:].split()
            commit, parents = (fields[0], fields[1:]) if fields else ("", [])
            commits.add(commit)
            i += 1
        elif token.startswith(":") and i + 1 < len(tokens):
            meta = token[1:].split()
            if len(meta) >= 5 and commit:
                changes.append((commit, parents, meta[0], meta[1], meta[2], meta[3], tokens[i + 1]))
            i += 2
        else:
            i += 1
    head_entries = [(mode, blob, path) for mode, kind, blob, path in git.tree_entries(head, PROBE_DIR.as_posix())
                    if kind == "blob" and _probe_path(mode, path)]

    def present(mode: str, blob: str, path: str) -> bool:
        return not _ZERO_OBJECT.match(blob) and _probe_path(mode, path)

    wanted = [blob for _, _, old_mode, new_mode, old, new, path in changes
              for mode, blob in ((old_mode, old), (new_mode, new))
              if present(mode, blob, path) and mode != _SYMLINK_MODE]
    wanted += [blob for mode, blob, _ in head_entries if mode != _SYMLINK_MODE]
    # Per blob the id its content declares, or None when the stem stands in; the
    # bytes themselves are dropped batch by batch.
    declared: dict[str, str | None] = {}
    for blob, content in git.iter_blobs(wanted, MAX_HISTORY_BATCH_BYTES):
        declared[blob] = _declared_id(content, yaml)
    history = ProbeHistory(head, commits=len(commits), blobs=len(declared))

    def carried(mode: str, blob: str, path: str) -> str:
        """A symlink is never read (load_probes() lists it under its stem)."""
        found = declared.get(blob) if mode != _SYMLINK_MODE else None
        return found if found is not None else PurePosixPath(path).stem

    for commit, parents, old_mode, new_mode, old, new, path in changes:
        before = carried(old_mode, old, path) if present(old_mode, old, path) else None
        after = carried(new_mode, new, path) if present(new_mode, new, path) else None
        if after is not None and (commit, path) not in history.writes.setdefault(after, []):
            history.writes[after].append((commit, path))
        if before is None or before == after:
            continue
        carrier = parents[0] if parents else commit
        if len(parents) > 1:
            carrier = next((p for p in parents if git.blob_at(p, path) == old), parents[0])
        removal = Removal(commit, path, carrier)
        if removal not in history.removals.setdefault(before, []):
            history.removals[before].append(removal)
    for mode, blob, path in head_entries:
        history.at_head.setdefault(carried(mode, blob, path), []).append(path)
    return history


@dataclass
class RetiredManifest:
    """The retirement manifest as read from the working tree.

    ``records`` holds the first schema-valid record per id; ``invalid`` the ids
    whose first record fails the schema; ``findings`` lists ``(kind, id, text)``
    per defect. When the document itself is unreadable, ``readable`` is False
    and no record in it takes effect.
    """

    file: str
    records: dict[str, dict[str, Any]] = field(default_factory=dict)
    invalid: set[str] = field(default_factory=set)
    findings: list[tuple[str, str, str]] = field(default_factory=list)
    readable: bool = True


def load_retired(repo: Path, yaml: Any, validator_cls: Any) -> RetiredManifest | None:
    """Read project/reach-probes/_retired.yml, or None when it is absent."""
    path = repo / RETIRED_PATH
    if not path.is_file() and not path.is_symlink():
        return None
    rel = RETIRED_PATH.as_posix()
    try:
        data = load_yaml(yaml, read_inside(repo, path))
    except UnsafePathError as exc:
        return RetiredManifest(rel, findings=[(FINDING_RETIRED_MANIFEST, "", f"refused and not read: {exc}")],
                               readable=False)
    except (yaml.YAMLError, UnicodeDecodeError, ValueError) as exc:
        return RetiredManifest(rel, findings=[(FINDING_RETIRED_MANIFEST, "", f"not parseable as YAML: {safe_text(exc)}")],
                               readable=False)
    per_entry: dict[int, list[str]] = {}
    document_errors: list[str] = []
    for err in sorted(validator_cls(RETIRED_SCHEMA).iter_errors(data), key=lambda e: list(e.absolute_path)):
        where = list(err.absolute_path)
        if len(where) >= 2 and where[0] == "entries" and isinstance(where[1], int):
            per_entry.setdefault(where[1], []).append(_schema_error_text(err))
        else:
            document_errors.append(_schema_error_text(err))
    if document_errors:
        return RetiredManifest(rel, findings=[(FINDING_RETIRED_MANIFEST, "", e) for e in document_errors],
                               readable=False)
    manifest = RetiredManifest(rel)
    seen: set[str] = set()
    for index, item in enumerate(data["entries"]):
        pid = item.get("id") if isinstance(item, dict) and isinstance(item.get("id"), str) else f"entries-{index}"
        if pid in seen:
            manifest.findings.append((FINDING_RETIRED_INVALID, pid, "listed more than once; only the first record is read"))
            continue
        seen.add(pid)
        if index in per_entry:
            manifest.invalid.add(pid)
            manifest.findings.append((FINDING_RETIRED_INVALID, pid,
                                      "fails the retirement schema: " + "; ".join(per_entry[index])))
            continue
        manifest.records[pid] = item
    return manifest


def _records_at(git: Git, commit: str, yaml: Any) -> dict[str, Any] | None:
    """The first record per id in the retirement manifest at ``commit``.

    Empty when the manifest is absent there; None when it is present but can't
    be read as a mapping with an ``entries`` list, so nobody can tell which
    records it held.
    """
    text = git.show(commit, RETIRED_PATH.as_posix())
    if text is None:
        return {}
    try:
        data = load_yaml(yaml, text)
    except (yaml.YAMLError, ValueError, RecursionError):
        return None
    entries = data.get("entries") if isinstance(data, dict) else None
    if not isinstance(entries, list):
        return None
    records: dict[str, Any] = {}
    for item in entries:
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            records.setdefault(item["id"], item)
    return records


@dataclass
class Retirement:
    """What the probe set no longer contains, judged against the retirement manifest.

    ``entries`` holds one ``removed`` row per probe id that left the set without
    an effective record (and per earlier probe of an exchange); ``retired`` one
    ``(id, record, new)`` per effective record, ``new`` when the manifest's
    previous commit did not hold that record; ``findings`` one ``(kind, id,
    text)`` per defect of the manifest or of a record in it.
    """

    manifest: RetiredManifest | None
    history: ProbeHistory
    entries: list[Entry] = field(default_factory=list)
    retired: list[tuple[str, dict[str, Any], bool]] = field(default_factory=list)
    findings: list[tuple[str, str, str]] = field(default_factory=list)


def removed_entry(pid: str, path: str, reason: str) -> Entry:
    """A probe id that left the set: not probed, never executed, a finding."""
    return Entry(Probe(path, {"id": pid}), ChangeState(STATE_REMOVED, reason), Outcome(NOT_PROBED, reason=f"removed: {reason}"))


def _exchange(git: Git, history: ProbeHistory, pid: str, holders: list[Probe]) -> tuple[Probe, str | None, set[str]] | None:
    """The file that took ``pid`` over from another one, when ``pid`` was exchanged under the same id.

    A file carrying ``pid`` now keeps it as its own when every other committed
    revision that carried ``pid`` lies on its own followed history
    (Git.file_log(), so a rename that git pairs keeps the id), or was written
    after the file first carried it (a later duplicate, since removed). Otherwise
    the id was carried elsewhere before or beside it, by a file that is gone:
    the file now carrying it took it over. "First carried" is the oldest
    revision of the file's followed history whose content carries the id; a file
    with no such revision (uncommitted, or created in a merge, which the walk
    does not list) took it over from any other carrier at all. Returns the file,
    that revision (or None), and the other paths that carried the id.
    """
    writes = history.writes.get(pid, [])
    own = {holder.file for holder in holders}
    if all(path in own for _, path in writes):
        return None
    logs = {holder.file: git.file_log(holder.file) for holder in holders}
    for log in logs.values():
        own |= {path for _, path, _, _ in log}
    foreign = [(commit, path) for commit, path in writes if path not in own]
    if not foreign:
        return None
    written = set(writes)
    for holder in holders:
        revisions = [commit for commit, path, _, _ in logs[holder.file] if (commit, path) in written]
        adopted = revisions[-1] if revisions else None
        if adopted is None or any(not git.is_ancestor_or_equal(adopted, commit) for commit, _ in foreign):
            return holder, adopted, {path for _, path in foreign}
    return None


def _where(last: tuple[str, str, bool] | None) -> str:
    """Where a removed probe last existed, as the reason states it."""
    if last is None:
        return "no commit that removed it was found"
    commit, path, uncommitted = last
    if uncommitted:
        return f"it last existed in {safe_text(path)} at HEAD {commit}, and its removal is not committed"
    return f"it last existed in {safe_text(path)} at {commit}"


def _retirement_problem(git: Git, history: ProbeHistory, manifest: RetiredManifest | None,
                        records: dict[str, dict[str, Any]], committed: dict[str, Any], pid: str,
                        yaml: Any) -> str | None:
    """Why no retirement record takes effect for the removed ``pid``, or None when one does.

    A record takes effect only when it is schema-valid, approved, committed
    (identical in HEAD's manifest, as an uncommitted probe is never run either),
    the removal itself is committed, and no removal of the id happened while the
    manifest already held this very record: a record can't account for a removal
    it predates, so a probe retired once, restored, and removed again needs a
    record of its own.
    """
    if manifest is None:
        return WHY_NO_RECORD
    if not manifest.readable:
        return WHY_MANIFEST_UNREADABLE
    if pid in manifest.invalid:
        return WHY_RECORD_INVALID
    record = records.get(pid)
    if record is None:
        return WHY_NO_RECORD
    if "approval" not in record:
        return WHY_RECORD_UNAPPROVED
    if committed.get(pid) != record:
        return WHY_RECORD_UNCOMMITTED
    if pid in history.at_head:
        return WHY_REMOVAL_UNCOMMITTED
    cache: dict[str, dict[str, Any] | None] = {}
    for removal in history.removals.get(pid, []):
        if removal.carrier not in cache:
            cache[removal.carrier] = _records_at(git, removal.carrier, yaml)
        before = cache[removal.carrier]
        if before is None:
            # Fail closed: the record may have been there already.
            return (f"{RETIRED_PATH.as_posix()} can't be read at {removal.carrier[:12]}, before the removal in "
                    f"{removal.commit[:12]}, so it can't be shown that the record postdates that removal")
        if before.get(pid) == record:
            return (f"its retirement record was already in {RETIRED_PATH.as_posix()} at {removal.carrier[:12]}, "
                    f"before the removal in {removal.commit[:12]}, so it can't account for that removal")
    return None


def judge_removals(repo: Path, git: Git, probes: list[Probe], yaml: Any, validator_cls: Any) -> Retirement:
    """Report every probe id that left the set without an effective retirement record (R1, R2, R4-R8).

    The probe set at HEAD is what load_probes() read, every file under any id
    (an invalid or unparseable one carries its file name stem, as Probe.pid
    says). Ids a committed probe file carried in HEAD's history but no file
    carries now are removed unless a record takes effect
    (_retirement_problem()); an id a file carries now that it took over from
    another file (_exchange()) reports the earlier probe removed, whatever the
    manifest says, since a record for an id still carried is a contradiction.
    A record for an id never carried is invalid.
    """
    history = shared_probe_set_history(git, yaml)
    manifest = load_retired(repo, yaml, validator_cls)
    result = Retirement(manifest, history)
    holders: dict[str, list[Probe]] = {}
    for probe in probes:
        holders.setdefault(probe.pid, []).append(probe)
    seen = history.ids
    records: dict[str, dict[str, Any]] = {}
    if manifest is not None:
        result.findings += manifest.findings
        for pid, record in manifest.records.items():
            if pid in holders:
                files = ", ".join(safe_text(p.file) for p in holders[pid])
                result.findings.append((FINDING_RETIRED_CONTRADICTION, pid, (
                    f"the probe file {files} still carries this id; a retirement record accounts only for a probe "
                    "that left the set, and an exchange under the same id can't be retired: the replacement takes "
                    "a new id")))
            elif pid not in seen:
                result.findings.append((FINDING_RETIRED_INVALID, pid, (
                    f"no committed probe file under {PROBE_DIR.as_posix()}/ in the history of HEAD ever carried "
                    "this id")))
            else:
                records[pid] = record
    committed = (_records_at(git, "HEAD", yaml) or {}) if records else {}
    previous: dict[str, Any] = {}
    if records:
        last_change = git.last_commit(RETIRED_PATH.as_posix())
        parents = git.parents(last_change) if last_change else []
        previous = (_records_at(git, parents[0], yaml) or {}) if parents else {}
    for pid in sorted(seen - set(holders)):
        why = _retirement_problem(git, history, manifest, records, committed, pid, yaml)
        if why is None:
            result.retired.append((pid, records[pid], previous.get(pid) != records[pid]))
            continue
        last = history.last(pid)
        reason = f"no probe file carries this id any more; {_where(last)}; {why}"
        result.entries.append(removed_entry(pid, last[1] if last else PROBE_DIR.as_posix(), reason))
    for pid in sorted(set(holders) & seen):
        exchange = _exchange(git, history, pid, holders[pid])
        if exchange is None:
            continue
        holder, adopted, paths = exchange
        last = history.last(pid, paths)
        since = (f"first carries it in {adopted[:12]}" if adopted else
                 "holds no committed revision that carries it")
        reason = (f"exchange under the same id: {_where(last)}, and {safe_text(holder.file)} carries it now, but "
                  f"that file's own history {since}; {EXCHANGE_EXIT}")
        result.entries.append(removed_entry(pid, last[1] if last else sorted(paths)[0], reason))
    return result


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


FINDING_STATES = (STATE_WEAKENED, STATE_INVALID, STATE_CONTRADICTION, STATE_APPROVAL_MISMATCH, STATE_REMOVED)


def _tier_bucket(e: Entry) -> str:
    if e.change.state == STATE_REMOVED:
        return TIER_REMOVED
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


def _headline(not_probed: int, total: int, listed: int, manifest: Manifest | None, removed: int = 0) -> str:
    gone = f", {removed} of them removed" if removed else ""
    if manifest is None:
        return (
            f"**Not probed: {not_probed} of {total} probes{gone}.** No not-constructible manifest, so entries "
            "the derivation could not probe are not counted here."
        )
    if not manifest.readable:
        return (
            f"**Not probed: {not_probed} of {total} probes{gone}.** The not-constructible manifest is unreadable, "
            "so entries the derivation could not probe are not counted here."
        )
    return (f"**Not probed: {not_probed} of {total} entries, {listed} of them not constructible"
            f"{f', {removed} removed' if removed else ''}.**")


def _retired_provenance(retirement: Retirement | None) -> list[str]:
    """The Provenance lines of the retirement manifest: one per retired id, new records marked (R8)."""
    if retirement is None:
        return []
    where = f"`{RETIRED_PATH.as_posix()}`"
    manifest = retirement.manifest
    if manifest is None:
        return [f"- No retirement manifest {where}: no probe id is retired."]
    if not manifest.readable:
        return [f"- The retirement manifest {where} is present but unreadable (see Findings); no record in it takes effect."]
    fresh = sum(1 for _, _, new in retirement.retired if new)
    lines = [f"- Retired probe ids in {where}: {len(retirement.retired)}, {fresh} of them {NEW_SINCE_PREVIOUS}."]
    for pid, record, new in retirement.retired:
        approval = record.get("approval") or {}
        mark = f", **{NEW_SINCE_PREVIOUS}**" if new else ""
        lines.append(
            f"- Retired {code_span(pid)} ({md_text(record.get('reason'), 40)}){mark}: {md_text(record.get('detail'), 300)}; "
            f"last existed at {md_text(str(record.get('last_revision'))[:12], 20)}; approved by "
            f"{md_text(approval.get('approved_by'), 80)} at {md_text(approval.get('approved_at'), 40)}."
        )
    return lines


def render(repo: Path, head: str, entries: list[Entry], include_t2: bool, run_at: str, empty_reason: str | None,
           manifest: Manifest | None = None, manifest_findings: list[str] | None = None,
           supersede_findings: list[tuple[Probe, str]] | None = None,
           supersede_notes: list[str] | None = None, retirement: Retirement | None = None) -> str:
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
            *_retired_provenance(retirement),
            f"- Run at: {run_at} (UTC), HEAD {head[:12]}",
        ]
        return "\n".join(lines) + "\n"

    removed = sum(1 for e in entries if e.change.state == STATE_REMOVED)
    probe_rows = [e for e in entries if e.probe.constructible and e.change.state != STATE_REMOVED]
    listed = total - len(probe_rows) - removed
    lines += [_headline(not_probed, total, listed, manifest, removed), ""]
    lines += ["## Provenance", ""]
    gone = (f", plus {removed} removed probe id(s) that no effective retirement record accounts for"
            if removed else "")
    lines.append(
        f"- Audited set: the {len(probe_rows)} probe file(s) on disk under `{PROBE_DIR.as_posix()}/` plus "
        f"{listed} not-constructible manifest entr{'y' if listed == 1 else 'ies'}{gone}, {total} in all, at HEAD "
        f"{head[:12]}. This run executed stored probes; it read no declaration to find new entries."
    )
    lines.append(f"- {_manifest_provenance(manifest, listed)}")
    lines += _retired_provenance(retirement)
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
    superseded = [e.probe.pid for e in probe_rows if e.change.state == STATE_SUPERSEDED]
    if superseded:
        lines.append(f"- {PROVENANCE_SUPERSEDED}: {len(superseded)} ({md_text(', '.join(superseded))}).")
    lines += [f"- {note}" for note in supersede_notes or []]  # built from safe_text and code spans
    lines.append(f"- Tier T2: {'requested (--include-t2)' if include_t2 else 'not requested; every T2 probe is not probed'}.")
    lines.append(f"- Run at: {run_at} (UTC).")
    lines.append("")

    lines += ["## Reach per tier", "", "| Tier | reached | partially reached | not reached | not probed |", "|---|---|---|---|---|"]
    for tier in ("T0", "T1", "T2", "invalid", TIER_NONE, TIER_REMOVED):
        subset = [e for e in entries if _tier_bucket(e) == tier]
        if tier in ("invalid", TIER_NONE, TIER_REMOVED) and not subset:
            continue
        counts = [sum(1 for e in subset if e.outcome.cls == c) for c in CLASSES]
        lines.append(f"| {tier} | " + " | ".join(str(c) for c in counts) + " |")
    lines.append("")

    findings = [e for e in entries if e.change.state in FINDING_STATES]
    lines += ["## Findings", ""]
    for text in manifest_findings or []:
        lines.append(f"- **invalid manifest** ({cell(MANIFEST_PATH.as_posix())}): {md_text(text)}")
    for probe, text in supersede_findings or []:
        lines.append(f"- **{FINDING_SUPERSEDE}** {code_span(probe.pid)} ({cell(probe.file)}): {md_text(text)}")
    retirement_findings = retirement.findings if retirement is not None else []
    for kind, pid, text in retirement_findings:
        named = f" {code_span(pid)}" if pid else ""
        lines.append(f"- **{kind}**{named} ({cell(RETIRED_PATH.as_posix())}): {md_text(text)}")
    for e in findings:
        if e.change.state in (STATE_WEAKENED, STATE_REMOVED):
            kind, detail = e.change.state, e.change.reason
        elif e.change.state == STATE_CONTRADICTION:
            kind, detail = "contradiction", e.change.reason
        elif e.change.state == STATE_APPROVAL_MISMATCH:
            kind, detail = "approval mismatch", e.change.reason
        else:
            kind = "invalid probe" if e.probe.constructible else "invalid manifest entry"
            detail = "; ".join(e.probe.errors)
        lines.append(f"- **{kind}** {code_span(e.probe.pid)} ({cell(e.probe.file)}): {md_text(detail)}")
    if not findings and not manifest_findings and not supersede_findings and not retirement_findings:
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
    require_real_probe_dir(repo)
    git = Git(repo)
    head = git.resolve_commit("HEAD") or ""
    now = clock()
    run_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    out = report_path(repo, now.strftime("%Y-%m-%d"))

    probes = load_probes(repo, yaml, validator_cls)
    manifest = load_manifest(repo, yaml, validator_cls)
    listed = {e.pid: e for e in manifest.entries} if manifest else {}
    manifest_findings = list(manifest.errors) if manifest else []
    # What the set no longer contains is judged before anything runs: a probe set
    # that lost every file still reports each removed id instead of "no probe set".
    retirement = judge_removals(repo, git, probes, yaml, validator_cls)
    empty_reason = None
    if not probes and not listed and not manifest_findings and not retirement.entries and not retirement.findings:
        if not (repo / PROBE_DIR).is_dir():
            empty_reason = f"`{PROBE_DIR.as_posix()}/` does not exist in this repository."
        else:
            empty_reason = (f"`{PROBE_DIR.as_posix()}/` holds no probe file (*.yml, *.yaml besides `{MANIFEST_NAME}` "
                            f"and `{RETIRED_NAME}`).")

    supersession = resolve_supersedes(repo, git, probes, set(listed), yaml)
    entries: list[Entry] = []
    for probe in probes:
        twin = listed.pop(probe.pid, None)
        if twin is not None:
            # Counted once, as not probed; the manifest row is folded into this one.
            entries.append(contradiction_entry(probe, twin))
        elif supersession.superseded(probe):
            entries.append(superseded_entry(probe, supersession.changes[probe.pid],
                                            supersession.replaced_by[probe.pid],
                                            supersession.unmet.get(probe.pid)))
        else:
            known = supersession.changes.get(probe.pid) if supersession.probes.get(probe.pid) is probe else None
            entry = evaluate(repo, git, probe, yaml, include_t2, env_timeout, clock, known)
            if supersession.probes.get(probe.pid) is probe:
                entry.notes += supersession.unmet.get(probe.pid, [])
            entries.append(entry)
    entries += [not_constructible_entry(item) for item in listed.values()]
    entries += retirement.entries
    text = render(repo, head, entries, include_t2, run_at, empty_reason, manifest, manifest_findings,
                  supersession.findings, supersession.notes, retirement)
    write_report(out, text)

    if (manifest_findings or supersession.findings or retirement.findings
            or any(e.change.state in FINDING_STATES for e in entries)):
        return EXIT_FINDINGS, out
    if not probes:
        # Nothing was executed, whether or not the manifest lists entries.
        return EXIT_NO_PROBES, out
    return EXIT_OK, out


# --------------------------------------------------------------------------- #
# Migration gate (reconfirm-and-migrate.md §Migration step 1)
# --------------------------------------------------------------------------- #
ROUTE_STALE = ("reconfirm it after the diff (references/reconfirm-and-migrate.md §Re-confirmation) "
               "or derive it again, then check again; a migration must not hide a declaration change")
ROUTE_WEAKENED = ("not healable in place: neither a re-confirmation nor a migration clears it; "
                  "keep it, derive and approve a replacement under a new id that lists it in supersedes "
                  "(references/runner-exit-codes.md §Re-baseline rule)")
ROUTE_REDERIVE = "re-derive the entry (references/runner-exit-codes.md §Findings), then check again"
ROUTE_OTHER = "resolve it as references/runner-exit-codes.md routes this reason, then check again"


def is_migration_candidate(probe: Probe) -> bool:
    """A probe file on a Markdown declaration that is not yet section-anchored.

    An invalid probe file is a candidate too, so the gate refuses it as ``run``
    flags it; one whose declaration can't be read at all (unparseable, a
    symlink) can't be ruled out and is a candidate as well (fail closed).
    """
    if not probe.constructible:
        return False
    declaration = probe.data.get("declaration") if isinstance(probe.data, dict) else None
    if not isinstance(declaration, dict):
        return bool(probe.errors)
    path = declaration.get("path")
    return isinstance(path, str) and path.endswith(".md") and "sections" not in declaration


def migration_state(repo: Path, git: Git, probe: Probe, yaml: Any,
                    change: ChangeState | None = None) -> ChangeState:
    """The candidate's state as ``run`` would judge it before executing; only clean may migrate.

    Reuses detect_change and the approval check of evaluate(), so this gate has
    no definition of stale or weakened of its own. ``change``: the state
    resolve_supersedes() already computed, on the history ``run`` uses.
    """
    return _approved_state(probe.data or {}, change or detect_change(repo, git, probe, yaml))


def check_migration(repo_arg: str) -> tuple[int, list[str]]:
    """Refuse the migration while any candidate is not clean; write nothing.

    Returns the exit code and the lines to print: one ``refused`` line per
    candidate that is not clean (id, state, reason, route), otherwise one
    ``migratable`` line per candidate.
    """
    yaml, validator_cls = _load_dependencies()
    repo = require_local_working_copy(repo_arg)
    require_real_probe_dir(repo)
    git = Git(repo)
    probes = load_probes(repo, yaml, validator_cls)
    # As in run(): an id that is also a manifest entry is a contradiction, judged
    # before the probe itself; an unreadable manifest can't rule one out.
    manifest = load_manifest(repo, yaml, validator_cls)
    listed = {e.pid: e for e in manifest.entries} if manifest else {}
    # As in run(): a superseded probe is not executed, so it is no candidate; an
    # invalid supersedes record is a finding there, so it refuses here.
    supersession = resolve_supersedes(repo, git, probes, set(listed), yaml)
    invalid_records: dict[str, list[str]] = {}
    for claimant, why in supersession.findings:
        invalid_records.setdefault(claimant.pid, []).append(why)
    candidates = [p for p in probes if is_migration_candidate(p)
                  and (p.pid in listed or not supersession.superseded(p))]
    refused: list[str] = []
    if manifest is not None and not manifest.readable:
        refused.append(f"refused {manifest.file}: invalid manifest: {safe_text('; '.join(manifest.errors))}; "
                       f"route: {ROUTE_REDERIVE}")
    migratable: list[str] = []
    for probe in candidates:
        if probe.pid in listed:
            state = contradiction_entry(probe, listed[probe.pid]).change
        elif probe.errors:
            state = ChangeState(STATE_INVALID, f"{REASON_INVALID_PROBE}: " + "; ".join(probe.errors))
        elif probe.pid in invalid_records and supersession.probes.get(probe.pid) is probe:
            state = ChangeState(FINDING_SUPERSEDE, "; ".join(invalid_records[probe.pid]))
        else:
            state = migration_state(repo, git, probe, yaml, supersession.changes.get(probe.pid)
                                    if supersession.probes.get(probe.pid) is probe else None)
        pid = safe_text(probe.pid, 120)
        if state.state == STATE_CLEAN:
            migratable.append(f"migratable {pid}")
            continue
        route = {STATE_STALE: ROUTE_STALE, STATE_WEAKENED: ROUTE_WEAKENED, STATE_INVALID: ROUTE_REDERIVE,
                 STATE_CONTRADICTION: ROUTE_REDERIVE, FINDING_SUPERSEDE: ROUTE_REDERIVE}.get(state.state, ROUTE_OTHER)
        refused.append(f"refused {pid}: {state.state}: {safe_text(state.reason)}; route: {route}")
    if refused:
        return EXIT_MIGRATION_REFUSED, refused
    return EXIT_OK, migratable


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Execute the stored capability-reach probes of a local repository and write the report.",
        epilog="Exit codes: 0 report written, 1 runtime error, 2 usage error, non-local or shallow target or "
        "symlinked probe directory, "
        "3 no probe file (nothing executed), 4 report written with findings, 5 PyYAML/jsonschema missing, "
        "6 --check-migration refused: a migration candidate is not clean (nothing written).",
    )
    parser.add_argument("--repo", required=True, help="Path to the local git working copy to audit (R13: no remote mode).")
    parser.add_argument("--include-t2", action="store_true", help="Also execute T2 probes (full stack with seeded data).")
    parser.add_argument(
        "--check-migration",
        action="store_true",
        help="Execute nothing and write nothing: judge every probe on a Markdown declaration without "
        "declaration.sections; list them as migratable when all are clean, otherwise refuse with each "
        "probe's state, reason, and route (exit 6).",
    )
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
    if args.check_migration:
        try:
            code, lines = check_migration(args.repo)
        except AuditError as exc:
            sys.stderr.write(f"reach_audit: {exc}\n")
            return exc.code
        for line in lines:
            print(line)
        if code == EXIT_MIGRATION_REFUSED:
            print(f"reach_audit: migration refused: {len(lines)} candidate(s) not clean; nothing written")
        else:
            print(f"reach_audit: migration check passed: {len(lines)} candidate(s) migratable; nothing written")
        return code
    try:
        code, out = run(args.repo, args.include_t2, args.environment_timeout)
    except AuditError as exc:
        sys.stderr.write(f"reach_audit: {exc}\n")
        return exc.code
    messages = {
        EXIT_OK: "report written",
        EXIT_NO_PROBES: "no probe file, nothing executed; the report says so (not a clean result)",
        EXIT_FINDINGS: "report written with findings (weakened, invalid, removed, or unapproved-content probes, "
                       "a manifest finding, an invalid supersedes record, or a retirement-manifest finding)",
    }
    print(f"reach_audit: {messages[code]}: {out}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
