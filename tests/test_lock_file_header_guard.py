"""Class guard: every lock file's header is a command Renovate can re-run (#822).

Guard origin (spec/project/defect-class-guards/ G5): #822. Renovate's
``pip-compile`` manager refreshes a lock file by re-running the command recorded
in its header. For months it parsed none of this repository's lock files: the
headers read ``uv pip compile --python-version 3.14 <src> -o <lock>``, Renovate
rejected both options, logged a warning nobody reads, and skipped the file, so
no transitive pin was ever refreshed (the wcmatch CVE). The class is "a lock
file whose header Renovate's pip-compile manager can't parse", which fails
silently: the lock keeps building, it just never moves.

Selector (G6). The criterion is "a ``*.lock.txt`` file tracked by the
repository", derived from ``git -C ROOT ls-files -z -- '*.lock.txt'``. A new
lock file joins by being committed, not by being named in this guard.

Fallback: when git isn't available or ``ROOT`` isn't a git work tree, or when a
caller forces it (``use_git=False``: the synthetic self-tests below, whose
temporary directory may itself sit inside a work tree and would then list as
empty; they also assert a non-empty selection), the selector is
``ROOT.rglob("*.lock.txt")`` minus any path with a ``.git``, ``.venv*``,
``.sbom-venv``, ``site`` or ``node_modules`` segment. That name list is an
approximation of "tracked"; only the git path is the honest criterion.

Predicate (G3). The rules are Renovate's own, transcribed from
``renovate/dist/modules/manager/pip-compile/common.js`` (``extractHeaderCommand``
and its ``throwFor*`` helpers) and ``utils.js`` (``inferCommandExecDir``) of
renovate 45.3.2. A selected file is a class member when any of these holds:

1. the header doesn't match Renovate's ``constraintLineRegex``: at least one
   ``#`` comment line, then a line ``#`` + four spaces + the command;
2. the command isn't ``uv pip compile`` (this repository generates every lock
   with uv; a ``pip-compile`` or custom header is a different contract);
3. an argument starting with ``-`` is ``--no-header`` (``disallowedPipOptions``);
   or is an option that takes an argument written without ``=``
   (``optionsWithArguments``: ``--python-version 3.14`` is rejected); or its
   name (the part before ``=``) isn't in Renovate's allowed ``uv`` set
   (``allowedOptions.uv``: ``-o`` is rejected);
4. ``--output-file=`` appears other than exactly once (Renovate rejects a
   second one), or its value, normalized, isn't the file's own repository-
   relative path. Renovate itself only demands the same basename and no leading
   ``..``, and infers the working directory from the difference; this guard is
   stricter on purpose so that directory is always the repository root;
5. ``--index-url=`` appears more than once;
6. the command names no source file, or a named source file (resolved from
   the repository root, per rule 4) doesn't exist;
7. Renovate wouldn't read the file with this manager, judged from
   ``renovate.json5``: the top level has ``enabled: false``; a top-level
   ``enabledManagers`` list doesn't name ``'pip-compile'``; there's no
   top-level ``'pip-compile'`` object; that object's ``enabled`` is anything
   but ``true``; its ``managerFilePatterns`` is missing, empty, or holds a value
   that isn't a string in Renovate's ``/regex/`` form (flag ``i`` only) or
   doesn't compile; or the file's repository-relative path matches none of
   those patterns (``re.search`` on the text between the delimiters). A lock
   outside that set is never read by the manager at all, which is this class's
   silent failure by another route.

Rule 7 reads ``renovate.json5`` with a small tokenizer and subset reader in
this file, not a JSON5 library: ``//`` and ``/* */`` comments are dropped
outside strings, single- and double-quoted strings are decoded per JSON5 (so a
commented-out block, or block text inside a string value, isn't a block), and
objects, arrays, strings and bare words are read. What it refuses rather than
passes: a missing file, input outside that subset or not well formed, a
duplicate key, and every case listed under rule 7, each with a message naming
``renovate.json5``. Zero extracted patterns is a failure, never a pass.

Not covered (a reader deciding whether a new case is caught should check these
by hand):

- presets the config ``extends``: a ``managerFilePatterns`` inherited from
  ``github>nolte/gh-plumbing`` is invisible to rule 7 (which then refuses for
  want of a local block), and an ``enabled: false`` or ``enabledManagers`` set
  there isn't seen at all;
- ``packageRules`` that switch the manager off for some files
  (``matchManagers: ['pip-compile'], enabled: false``, or ``matchFileNames`` /
  ``ignoreDeps`` that exclude a lock);
- ``ignorePaths``, which keeps Renovate from reading a matching file with any
  manager: neither a local list nor one inherited through ``extends`` (for
  example ``:ignoreModulesAndTests``, which adds ``**/tests/**``) is checked;
- options Renovate accepts but uv itself would reject or interpret differently;
- the ``--constraint=``/``--override=`` files a header names (Renovate tracks
  them, but this repository uses none);
- whether the lock's pins are what the command would produce today.

Every rule is stated against Renovate 45.3.2; a Renovate upgrade that widens or
narrows the allowed set needs this file re-read against the new ``common.js``.
"""

from __future__ import annotations

import posixpath
import re
import shlex
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Fallback only (no git): segments that hold files this repository doesn't own.
EXCLUDED_PARTS = {".git", ".sbom-venv", "site", "node_modules"}
EXCLUDED_PREFIXES = (".venv",)

# --- Renovate 45.3.2, renovate/dist/modules/manager/pip-compile/common.js ------
# common.js:48  constraintLineRegex =
#   /^(?:#.*?\r?\n)+# {4}(?<command>\S*)(?<arguments> .*?)?\r?\n/
CONSTRAINT_LINE = re.compile(
    r"^(?:#.*?\r?\n)+# {4}(?P<command>\S*)(?P<arguments> .*?)?\r?\n"
)
# common.js:49  disallowedPipOptions
DISALLOWED_OPTIONS = frozenset({"--no-header"})
# common.js:50-54  commonOptionsWithArguments
COMMON_OPTIONS_WITH_ARGUMENTS = ("--output-file", "--extra", "--extra-index-url")
# common.js:55-59  pipOptionsWithArguments
PIP_OPTIONS_WITH_ARGUMENTS = (
    "--resolver",
    "--constraint",
    *COMMON_OPTIONS_WITH_ARGUMENTS,
)
# common.js:60-75  uvOptionsWithArguments
UV_OPTIONS_WITH_ARGUMENTS = (
    "--constraints",
    "--constraint",
    "--python-version",
    "--no-emit-package",
    "--prerelease",
    "--format",
    "--resolution",
    "--fork-strategy",
    "--exclude-newer",
    "--exclude-newer-package",
    "--group",
    "--override",
    "--overrides",
    *COMMON_OPTIONS_WITH_ARGUMENTS,
)
# common.js:76  optionsWithArguments = [...pip, ...uv]; common.js:198-200
# throwForNoEqualSignInOptionWithArgument rejects any of these as a bare argument.
OPTIONS_WITH_ARGUMENTS = frozenset(
    PIP_OPTIONS_WITH_ARGUMENTS + UV_OPTIONS_WITH_ARGUMENTS
)
# common.js:77-83  allowedCommonOptions
ALLOWED_COMMON_OPTIONS = (
    "-v",
    "--generate-hashes",
    "--emit-index-url",
    "--index-url",
    "--all-extras",
)
# common.js:93-98  allowedOptions.uv; common.js:201-208 throwForUnknownOption
# checks the name before "=" (or the bare argument) against it.
ALLOWED_UV_OPTIONS = frozenset(
    (
        "--no-strip-extras",
        "--universal",
        *ALLOWED_COMMON_OPTIONS,
        *UV_OPTIONS_WITH_ARGUMENTS,
    )
)
# common.js:126  for a uv command, the bare words "pip" and "compile" are skipped.
UV_SUBCOMMAND_WORDS = frozenset({"pip", "compile"})
# ------------------------------------------------------------------------------


def lock_files(root: Path, use_git: bool = True) -> list[Path]:
    """The selector: every tracked *.lock.txt below `root` (rglob without git).

    `use_git=False` forces the filesystem path; the synthetic self-tests use it, since
    a temporary directory inside some work tree would otherwise list as empty.
    """
    listed = None
    if use_git:
        try:
            listed = subprocess.run(
                ["git", "-C", str(root), "ls-files", "-z", "--", "*.lock.txt"],
                capture_output=True,
                timeout=60,
            )
        except (OSError, subprocess.TimeoutExpired):
            listed = None
    if listed is not None and listed.returncode == 0:
        candidates = [
            root / rel for rel in listed.stdout.decode("utf-8").split("\0") if rel
        ]
        filtered = False
    else:
        candidates = list(root.rglob("*.lock.txt"))
        filtered = True
    out = []
    for path in sorted(candidates):
        parts = path.relative_to(root).parts
        if filtered and (
            EXCLUDED_PARTS.intersection(parts)
            or any(p.startswith(EXCLUDED_PREFIXES) for p in parts)
        ):
            continue
        if not path.is_file():
            continue  # a tracked file deleted in the working tree has no header to read
        out.append(path)
    return out


def header_problems(root: Path, lock: Path) -> list[str]:
    """Every reason Renovate's pip-compile manager (or rules 4/6) refuses `lock`'s header."""
    rel = lock.relative_to(root).as_posix()
    match = CONSTRAINT_LINE.match(lock.read_text(encoding="utf-8"))
    if match is None:
        return [
            f"{rel}: no header command line ('#' + 4 spaces + command) after a comment line"
        ]
    command = match.group("command")
    if not command:
        return [
            f"{rel}: header command line is indented by more than 4 spaces after '#'"
        ]
    try:
        args = shlex.split(match.group("arguments") or "")
    except ValueError as exc:
        return [f"{rel}: header arguments don't split: {exc}"]
    if command != "uv" or args[:2] != ["pip", "compile"]:
        return [
            f"{rel}: header command is {' '.join([command, *args[:2]])!r}, not 'uv pip compile'"
        ]

    problems: list[str] = []
    sources: list[str] = []
    output_files: list[str] = []
    index_urls = 0
    for arg in args:
        if arg in UV_SUBCOMMAND_WORDS:
            continue
        if not arg.startswith("-"):
            sources.append(arg)
            continue
        if arg in DISALLOWED_OPTIONS:
            problems.append(f"{rel}: option {arg} not allowed for this manager")
            continue
        if arg in OPTIONS_WITH_ARGUMENTS:
            problems.append(
                f"{rel}: option {arg} must have equal sign '=' separating its argument"
            )
            continue
        name, has_value, value = arg.partition("=")
        if name not in ALLOWED_UV_OPTIONS:
            problems.append(
                f"{rel}: option {arg} not supported by Renovate's uv parser"
            )
            continue
        if has_value and name == "--output-file":
            output_files.append(value)
        elif has_value and name == "--index-url":
            index_urls += 1

    if len(output_files) != 1:
        problems.append(
            f"{rel}: expects exactly one --output-file=, found {len(output_files)}"
        )
    elif posixpath.normpath(output_files[0]) != rel:
        problems.append(
            f"{rel}: --output-file={output_files[0]} isn't the file's own path {rel}"
        )
    if index_urls > 1:
        problems.append(f"{rel}: cannot use multiple --index-url options")
    if not sources:
        problems.append(f"{rel}: header names no source file")
    for source in sources:
        if not (root / source).is_file():
            problems.append(
                f"{rel}: source file {source} named in the header doesn't exist"
            )
    return problems


def all_problems(root: Path, use_git: bool = True) -> list[str]:
    selected = lock_files(root, use_git)
    assert selected, f"selector found no *.lock.txt under {root}"
    return [problem for lock in selected for problem in header_problems(root, lock)]


RENOVATE_CONFIG = "renovate.json5"
MANAGER = "pip-compile"

# Rule 7 reads renovate.json5 with the small tokenizer and subset reader below,
# not with a JSON5 library: comments are dropped, single- and double-quoted
# strings are decoded per JSON5, and objects/arrays/strings/bare words
# (true, false, null, numbers, unquoted keys) are read. Anything outside that
# subset, or not well formed, is a problem naming renovate.json5, not a pass.
_PUNCT = frozenset("{}[]:,")
_BARE = re.compile(r"[A-Za-z0-9_$+\-.]+")
_SIMPLE_ESCAPES = {
    "b": "\b",
    "f": "\f",
    "n": "\n",
    "r": "\r",
    "t": "\t",
    "v": "\v",
    "0": "\0",
}
REGEX_FORM = re.compile(r"^/(?P<pattern>.+)/(?P<flags>i?)$")


class Bare(str):
    """An unquoted JSON5 token (true, false, null, a number, an identifier key)."""


def _tokens(text: str) -> list[tuple[str, str]]:
    """(kind, value) tokens of `text`; kind is "punct", "str" or "bare". Comments vanish."""
    out: list[tuple[str, str]] = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c.isspace():
            i += 1
        elif text.startswith("//", i):
            end = text.find("\n", i)
            i = n if end == -1 else end
        elif text.startswith("/*", i):
            end = text.find("*/", i + 2)
            if end == -1:
                raise ValueError(f"unterminated /* comment at offset {i}")
            i = end + 2
        elif c in _PUNCT:
            out.append(("punct", c))
            i += 1
        elif c in "'\"":
            chars: list[str] = []
            i += 1
            while True:
                if i >= n or text[i] == "\n":
                    raise ValueError("unterminated string literal")
                ch = text[i]
                if ch == c:
                    i += 1
                    break
                if ch != "\\":
                    chars.append(ch)
                    i += 1
                    continue
                if i + 1 >= n:
                    raise ValueError("unterminated string literal")
                esc = text[i + 1]
                if esc in "xu":
                    width = 2 if esc == "x" else 4
                    digits = text[i + 2 : i + 2 + width]
                    if not re.fullmatch(f"[0-9A-Fa-f]{{{width}}}", digits):
                        raise ValueError(f"bad \\{esc} escape in string literal")
                    chars.append(chr(int(digits, 16)))
                    i += 2 + width
                elif esc == "\n":
                    i += 2  # line continuation
                else:
                    # JSON5: any other escaped character stands for itself.
                    chars.append(_SIMPLE_ESCAPES.get(esc, esc))
                    i += 2
            out.append(("str", "".join(chars)))
        else:
            m = _BARE.match(text, i)
            if m is None:
                raise ValueError(f"unexpected character {c!r} at offset {i}")
            out.append(("bare", m.group()))
            i = m.end()
    return out


def read_json5_subset(text: str) -> object:
    """The value `text` holds; ValueError on anything outside the subset or a duplicate key."""
    tokens = _tokens(text)
    pos = 0

    def take() -> tuple[str, str]:
        nonlocal pos
        if pos >= len(tokens):
            raise ValueError("unexpected end of input")
        pos += 1
        return tokens[pos - 1]

    def peek(value: str) -> bool:
        return pos < len(tokens) and tokens[pos] == ("punct", value)

    def value() -> object:
        kind, tok = take()
        if kind == "str":
            return tok
        if kind == "bare":
            return Bare(tok)
        if tok == "[":
            items: list[object] = []
            while not peek("]"):
                items.append(value())
                if not peek("]"):
                    if take() != ("punct", ","):
                        raise ValueError("expected ',' or ']' in array")
            take()
            return items
        if tok == "{":
            obj: dict[str, object] = {}
            while not peek("}"):
                kkind, key = take()
                if kkind == "punct":
                    raise ValueError(f"expected a key, found {key!r}")
                if key in obj:
                    raise ValueError(f"duplicate key {key!r}")
                if take() != ("punct", ":"):
                    raise ValueError(f"expected ':' after key {key!r}")
                obj[key] = value()
                if not peek("}"):
                    if take() != ("punct", ","):
                        raise ValueError("expected ',' or '}' in object")
            take()
            return obj
        raise ValueError(f"unexpected {tok!r}")

    result = value()
    if pos != len(tokens):
        raise ValueError(
            f"trailing content after the top-level value: {tokens[pos][1]!r}"
        )
    return result


def _enabled_problems(where: str, value: object, effect: str) -> list[str]:
    """`enabled` counts only as a bare true/false token; anything else is unreadable."""
    if value == "true" and isinstance(value, Bare):
        return []
    if value == "false" and isinstance(value, Bare):
        return [f"{RENOVATE_CONFIG}: {where} enabled: false {effect}"]
    return [
        f"{RENOVATE_CONFIG}: {where} enabled is {value!r}, not a bare true or false"
    ]


def manager_patterns(root: Path) -> tuple[list[re.Pattern[str]], list[str]]:
    """The 'pip-compile' managerFilePatterns of `root`/renovate.json5, or why none apply."""
    config = root / RENOVATE_CONFIG
    if not config.is_file():
        return [], [f"{RENOVATE_CONFIG}: not found under {root}"]
    try:
        doc = read_json5_subset(config.read_text(encoding="utf-8"))
    except ValueError as exc:
        return [], [f"{RENOVATE_CONFIG}: can't read: {exc}"]
    if not isinstance(doc, dict):
        return [], [f"{RENOVATE_CONFIG}: top level isn't an object"]
    problems: list[str] = []
    if "enabled" in doc:
        problems += _enabled_problems("top-level", doc["enabled"], "disables Renovate")
    if "enabledManagers" in doc:
        managers = doc["enabledManagers"]
        # manager/index.js:81-82 (getEnabledManagersList): an empty list means
        # every manager, so only a non-empty list has to name pip-compile.
        if not isinstance(managers, list) or (
            managers and MANAGER not in [m for m in managers if not isinstance(m, Bare)]
        ):
            problems.append(
                f"{RENOVATE_CONFIG}: enabledManagers doesn't list '{MANAGER}'"
            )
    block = doc.get(MANAGER)
    if not isinstance(block, dict):
        problems.append(f"{RENOVATE_CONFIG}: no top-level '{MANAGER}' object")
        return [], problems
    if "enabled" in block:
        problems += _enabled_problems(
            f"'{MANAGER}'", block["enabled"], "disables the manager"
        )
    raw_patterns = block.get("managerFilePatterns")
    if not isinstance(raw_patterns, list) or not raw_patterns:
        problems.append(
            f"{RENOVATE_CONFIG}: '{MANAGER}' managerFilePatterns holds no pattern"
        )
        return [], problems
    patterns: list[re.Pattern[str]] = []
    for raw in raw_patterns:
        form = (
            REGEX_FORM.match(raw)
            if isinstance(raw, str) and not isinstance(raw, Bare)
            else None
        )
        if form is None:
            problems.append(
                f"{RENOVATE_CONFIG}: pattern {raw!r} isn't a string in Renovate's /regex/ form"
            )
            continue
        try:
            patterns.append(
                re.compile(
                    form.group("pattern"), re.IGNORECASE if form.group("flags") else 0
                )
            )
        except re.error as exc:
            problems.append(
                f"{RENOVATE_CONFIG}: pattern {raw!r} doesn't compile: {exc}"
            )
    return patterns, problems


def coverage_problems(root: Path, use_git: bool = True) -> list[str]:
    """Rule 7: every selected lock file is one Renovate's pip-compile manager reads."""
    selected = lock_files(root, use_git)
    assert selected, f"selector found no *.lock.txt under {root}"
    patterns, problems = manager_patterns(root)
    if problems:
        return problems
    for lock in selected:
        rel = lock.relative_to(root).as_posix()
        if not any(p.search(rel) for p in patterns):
            shown = ", ".join(p.pattern for p in patterns)
            problems.append(
                f"{rel}: matches no '{MANAGER}' managerFilePatterns in {RENOVATE_CONFIG} ({shown})"
            )
    return problems


def test_every_tracked_lock_file_is_read_by_the_pip_compile_manager():
    problems = coverage_problems(ROOT)
    assert problems == [], (
        "lock files Renovate's pip-compile manager never reads:\n" + "\n".join(problems)
    )


def test_every_tracked_lock_file_header_is_parseable_by_renovate():
    problems = all_problems(ROOT)
    assert problems == [], (
        "lock-file headers Renovate's pip-compile manager can't re-run:\n"
        + "\n".join(problems)
    )


def test_selector_reaches_the_lock_files_the_repo_tracks():
    """G6 positive control: the derived set is non-empty and holds the root dev lock."""
    rels = {p.relative_to(ROOT).as_posix() for p in lock_files(ROOT)}
    assert rels, "no tracked *.lock.txt found"
    assert "requirements-dev.lock.txt" in rels


# --- the predicate, on synthetic lock files ------------------------------------

GOOD = "uv pip compile --python-version=3.14 reqs/requirements.txt --output-file=reqs/requirements.lock.txt"


def _write_lock(
    tmp_path: Path, header_command: str | None, rel: str = "reqs/requirements.lock.txt"
) -> Path:
    (tmp_path / "reqs").mkdir(exist_ok=True)
    (tmp_path / "reqs" / "requirements.txt").write_text("attrs\n", encoding="utf-8")
    lock = tmp_path / rel
    lock.parent.mkdir(parents=True, exist_ok=True)
    header = (
        ""
        if header_command is None
        else (
            f"# This file was autogenerated by uv via the following command:\n#    {header_command}\n"
        )
    )
    lock.write_text(
        header + "attrs==26.1.0\n    # via -r reqs/requirements.txt\n", encoding="utf-8"
    )
    return lock


def _problems(tmp_path: Path, header_command: str | None) -> list[str]:
    _write_lock(tmp_path, header_command)
    return all_problems(tmp_path, use_git=False)


def test_guard_accepts_the_equal_sign_output_file_form(tmp_path):
    assert _problems(tmp_path, GOOD) == []


def test_guard_rejects_python_version_without_equal_sign(tmp_path):
    problems = _problems(
        tmp_path, GOOD.replace("--python-version=3.14", "--python-version 3.14")
    )
    assert any("option --python-version must have equal sign" in p for p in problems), (
        problems
    )


def test_guard_rejects_short_output_option(tmp_path):
    cmd = GOOD.replace(
        "--output-file=reqs/requirements.lock.txt", "-o reqs/requirements.lock.txt"
    )
    problems = _problems(tmp_path, cmd)
    assert any("option -o not supported" in p for p in problems), problems
    assert any("expects exactly one --output-file=, found 0" in p for p in problems), (
        problems
    )


def test_guard_rejects_the_pre_822_header_verbatim(tmp_path):
    """The exact shape every lock carried before #822."""
    cmd = "uv pip compile --python-version 3.14 reqs/requirements.txt -o reqs/requirements.lock.txt"
    lock = "reqs/requirements.lock.txt"
    # Renovate reads the detached "3.14" and the -o target as source files, as it does.
    assert _problems(tmp_path, cmd) == [
        f"{lock}: option --python-version must have equal sign '=' separating its argument",
        f"{lock}: option -o not supported by Renovate's uv parser",
        f"{lock}: expects exactly one --output-file=, found 0",
        f"{lock}: source file 3.14 named in the header doesn't exist",
    ]


def test_guard_rejects_an_output_file_that_isnt_the_lock_itself(tmp_path):
    problems = _problems(
        tmp_path, GOOD.replace("--output-file=reqs/", "--output-file=other/")
    )
    assert problems == [
        "reqs/requirements.lock.txt: --output-file=other/requirements.lock.txt"
        " isn't the file's own path reqs/requirements.lock.txt"
    ]


def test_guard_rejects_a_lock_without_a_header(tmp_path):
    problems = _problems(tmp_path, None)
    assert len(problems) == 1 and "no header command line" in problems[0], problems


def test_guard_rejects_an_unknown_option_and_a_missing_source(tmp_path):
    cmd = GOOD.replace("reqs/requirements.txt ", "reqs/missing.txt ") + " --upgrade"
    problems = _problems(tmp_path, cmd)
    assert any("option --upgrade not supported" in p for p in problems), problems
    assert any("source file reqs/missing.txt" in p for p in problems), problems


def test_guard_rejects_a_non_uv_command(tmp_path):
    problems = _problems(tmp_path, GOOD.replace("uv pip compile", "pip-compile"))
    assert len(problems) == 1 and "not 'uv pip compile'" in problems[0], problems


def test_fallback_selector_skips_virtualenvs_and_site(tmp_path):
    _write_lock(tmp_path, GOOD)
    for rel in (
        ".venv-docs/x/requirements.lock.txt",
        ".sbom-venv/requirements.lock.txt",
        "site/requirements.lock.txt",
        "node_modules/p/requirements.lock.txt",
    ):
        _write_lock(tmp_path, None, rel)
    selected = [
        p.relative_to(tmp_path).as_posix() for p in lock_files(tmp_path, use_git=False)
    ]
    assert selected == ["reqs/requirements.lock.txt"]


def test_git_selector_skips_untracked_lock_files(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, timeout=60)
    _write_lock(tmp_path, GOOD)
    _write_lock(tmp_path, None, "scratch.lock.txt")
    subprocess.run(["git", "-C", str(tmp_path), "add", "reqs"], check=True, timeout=60)
    selected = [p.relative_to(tmp_path).as_posix() for p in lock_files(tmp_path)]
    assert selected == ["reqs/requirements.lock.txt"]
    assert all_problems(tmp_path) == []


def test_guard_accepts_an_output_file_with_a_leading_dot_segment(tmp_path):
    """Renovate normalizes the value (upath.normalize); so does the guard."""
    assert _problems(tmp_path, GOOD.replace("--output-file=", "--output-file=./")) == []


def test_guard_rejects_two_index_urls(tmp_path):
    cmd = (
        GOOD
        + " --index-url=https://a.example/simple --index-url=https://b.example/simple"
    )
    assert _problems(tmp_path, cmd) == [
        "reqs/requirements.lock.txt: cannot use multiple --index-url options"
    ]


def test_guard_rejects_a_header_without_a_source_file(tmp_path):
    cmd = (
        "uv pip compile --python-version=3.14 --output-file=reqs/requirements.lock.txt"
    )
    assert _problems(tmp_path, cmd) == [
        "reqs/requirements.lock.txt: header names no source file"
    ]


def test_guard_rejects_no_header_with_renovates_first_message(tmp_path):
    """common.js runs throwForDisallowedOption before throwForUnknownOption."""
    assert _problems(tmp_path, GOOD + " --no-header") == [
        "reqs/requirements.lock.txt: option --no-header not allowed for this manager"
    ]


def test_guard_names_an_over_indented_header(tmp_path):
    problems = _problems(tmp_path, " " + GOOD)
    assert problems == [
        "reqs/requirements.lock.txt: header command line is indented by more than 4 spaces after '#'"
    ]


# --- rule 7, on synthetic renovate.json5 files ----------------------------------


def _coverage(tmp_path: Path, config: str | None) -> list[str]:
    _write_lock(tmp_path, GOOD)
    if config is not None:
        (tmp_path / RENOVATE_CONFIG).write_text(config, encoding="utf-8")
    return coverage_problems(tmp_path, use_git=False)


PATTERN = "'/(^|/)requirements(-dev)?\\\\.lock\\\\.txt$/'"
BLOCK = "  'pip-compile': {\n    managerFilePatterns: [" + PATTERN + "],\n  },\n"
MATCHING = "{\n" + BLOCK + "}\n"


def test_coverage_accepts_a_pattern_that_matches_every_lock(tmp_path):
    assert _coverage(tmp_path, MATCHING) == []


def test_coverage_accepts_the_repo_pattern_and_reads_it():
    """Positive control: the repo's own literal is extracted, not skipped."""
    patterns, problems = manager_patterns(ROOT)
    assert problems == []
    assert [p.pattern for p in patterns] == [r"(^|/)requirements(-dev)?\.lock\.txt$"]


def test_coverage_accepts_double_quotes_and_comments_inside_the_block(tmp_path):
    config = (
        '{\n  // a } brace and a { brace in a comment\n  "pip-compile": {\n'
        "    /* the lock files } */\n"
        '    "managerFilePatterns": [\n      // one pattern\n'
        '      "/(^|/)requirements(-dev)?\\\\.lock\\\\.txt$/", // trailing\n    ],\n  },\n}\n'
    )
    assert _coverage(tmp_path, config) == []


def test_coverage_decodes_json5_escapes_like_renovate(tmp_path):
    """JSON5 `\\.` is `.`; the decoded regex still has to match the lock."""
    config = "{'pip-compile': {managerFilePatterns: ['/requirements\\.lock\\.txt$/']}}"
    patterns, problems = manager_patterns(_write_config(tmp_path, config))
    assert problems == [] and [p.pattern for p in patterns] == [
        "requirements.lock.txt$"
    ]


def _write_config(tmp_path: Path, config: str) -> Path:
    (tmp_path / RENOVATE_CONFIG).write_text(config, encoding="utf-8")
    return tmp_path


def test_coverage_rejects_a_lock_the_pattern_misses(tmp_path):
    problems = _coverage(tmp_path, MATCHING.replace("(-dev)?", "-dev"))
    assert len(problems) == 1, problems
    assert problems[0].startswith(
        "reqs/requirements.lock.txt: matches no 'pip-compile' managerFilePatterns"
    )


def test_coverage_rejects_a_block_without_an_extractable_pattern(tmp_path):
    problems = _coverage(
        tmp_path, "{\n  'pip-compile': {\n    managerFilePatterns: [],\n  },\n}\n"
    )
    assert problems == [
        "renovate.json5: 'pip-compile' managerFilePatterns holds no pattern"
    ]


def test_coverage_rejects_a_config_without_a_pip_compile_block(tmp_path):
    problems = _coverage(tmp_path, "{\n  extends: ['config:recommended'],\n}\n")
    assert problems == ["renovate.json5: no top-level 'pip-compile' object"]


def test_coverage_rejects_a_block_commented_out_with_slash_star(tmp_path):
    problems = _coverage(tmp_path, "{\n  extends: [],\n  /*\n" + BLOCK + "  */\n}\n")
    assert problems == ["renovate.json5: no top-level 'pip-compile' object"]


def test_coverage_rejects_a_block_commented_out_line_by_line(tmp_path):
    commented = "".join("  // " + line + "\n" for line in BLOCK.splitlines())
    problems = _coverage(tmp_path, "{\n  extends: [],\n" + commented + "}\n")
    assert problems == ["renovate.json5: no top-level 'pip-compile' object"]


def test_coverage_rejects_a_block_that_appears_only_inside_a_string(tmp_path):
    config = (
        '{\n  description: "' + BLOCK.replace("\n", " ").replace('"', "") + '",\n}\n'
    )
    assert "'pip-compile': {" in config
    problems = _coverage(tmp_path, config)
    assert problems == ["renovate.json5: no top-level 'pip-compile' object"]


def test_coverage_rejects_a_disabled_pip_compile_block(tmp_path):
    problems = _coverage(
        tmp_path,
        MATCHING.replace(
            "  'pip-compile': {\n", "  'pip-compile': {\n    enabled: false,\n"
        ),
    )
    assert problems == [
        "renovate.json5: 'pip-compile' enabled: false disables the manager"
    ]


def test_coverage_rejects_enabled_managers_without_pip_compile(tmp_path):
    problems = _coverage(
        tmp_path, "{\n  enabledManagers: ['pep621'],\n" + BLOCK + "}\n"
    )
    assert problems == ["renovate.json5: enabledManagers doesn't list 'pip-compile'"]


def test_coverage_accepts_enabled_managers_with_pip_compile(tmp_path):
    assert (
        _coverage(
            tmp_path,
            "{\n  enabledManagers: ['pep621', 'pip-compile'],\n" + BLOCK + "}\n",
        )
        == []
    )


def test_coverage_rejects_a_globally_disabled_renovate(tmp_path):
    problems = _coverage(tmp_path, "{\n  enabled: false,\n" + BLOCK + "}\n")
    assert problems == ["renovate.json5: top-level enabled: false disables Renovate"]


def test_coverage_rejects_a_glob_instead_of_a_regex(tmp_path):
    problems = _coverage(tmp_path, MATCHING.replace(PATTERN, "'**/*.lock.txt'"))
    assert problems == [
        "renovate.json5: pattern '**/*.lock.txt' isn't a string in Renovate's /regex/ form"
    ]


def test_coverage_rejects_a_config_it_cannot_read(tmp_path):
    problems = _coverage(
        tmp_path, MATCHING.replace("managerFilePatterns:", "managerFilePatterns")
    )
    assert len(problems) == 1 and problems[0].startswith(
        "renovate.json5: can't read: expected ':'"
    ), problems


def test_coverage_rejects_a_duplicate_pip_compile_key(tmp_path):
    problems = _coverage(tmp_path, "{\n" + BLOCK + BLOCK + "}\n")
    assert problems == ["renovate.json5: can't read: duplicate key 'pip-compile'"]


def test_coverage_rejects_a_missing_config(tmp_path):
    problems = _coverage(tmp_path, None)
    assert len(problems) == 1 and problems[0].startswith("renovate.json5: not found"), (
        problems
    )


def test_coverage_accepts_an_empty_enabled_managers_list(tmp_path):
    """manager/index.js:81-82: `enabledManagers: []` enables every manager."""
    assert _coverage(tmp_path, "{\n  enabledManagers: [],\n" + BLOCK + "}\n") == []


def test_coverage_accepts_a_bare_true_enabled(tmp_path):
    config = (
        "{\n  enabled: true,\n"
        + BLOCK.replace("{\n", "{\n    enabled: true,\n", 1)
        + "}\n"
    )
    assert _coverage(tmp_path, config) == []


def test_coverage_refuses_a_quoted_top_level_enabled(tmp_path):
    problems = _coverage(tmp_path, "{\n  enabled: 'true',\n" + BLOCK + "}\n")
    assert problems == [
        "renovate.json5: top-level enabled is 'true', not a bare true or false"
    ]


def test_coverage_refuses_a_quoted_block_enabled(tmp_path):
    config = "{\n" + BLOCK.replace("{\n", '{\n    enabled: "false",\n', 1) + "}\n"
    assert _coverage(tmp_path, config) == [
        "renovate.json5: 'pip-compile' enabled is 'false', not a bare true or false"
    ]


def _read_error(text: str) -> str:
    try:
        read_json5_subset(text)
    except ValueError as exc:
        return str(exc)
    raise AssertionError(f"read_json5_subset accepted {text!r}")


def test_reader_refuses_a_missing_comma_in_an_array():
    assert _read_error("{a: ['x' 'y']}") == "expected ',' or ']' in array"


def test_reader_refuses_a_missing_comma_in_an_object():
    assert _read_error("{a: 'x' b: 'y'}") == "expected ',' or '}' in object"


def test_reader_refuses_trailing_content_after_the_top_level_value():
    assert (
        _read_error("{a: 'x'} {b: 'y'}")
        == "trailing content after the top-level value: '{'"
    )


def test_reader_refuses_an_unclosed_block_comment():
    assert (
        _read_error("{a: 'x'} /* never closed") == "unterminated /* comment at offset 9"
    )


def test_reader_refuses_a_raw_newline_inside_a_string():
    assert _read_error("{a: 'x\ny'}") == "unterminated string literal"


def test_reader_decodes_hex_and_unicode_escapes():
    assert read_json5_subset("{a: '\\x41\\u00e9\\n'}") == {"a": "A\u00e9\n"}


def test_reader_drops_a_line_continuation():
    assert read_json5_subset("{a: 'ab\\\ncd'}") == {"a": "abcd"}
