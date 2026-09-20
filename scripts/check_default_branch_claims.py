#!/usr/bin/env python3
"""Refuse prose that names a default branch the repository configuration contradicts.

Guard origin (spec/project/defect-class-guards/ G5): #652.

The class: a spec, skill, or agent states a repository-specific configuration
value that the configuration itself contradicts, narrowed here to the
default-branch case. `spec/project/pull-request-workflow/` claimed this
repository's default branch is `main` while `.github/settings.yml` sets
`default_branch: develop`, and every downstream instruction that reasoned from
that premise inherited the error.

Predicate (G3 — the class, not the sites where the defect was found):

1. The expected branch is **read** from `.github/settings.yml` (`default_branch:`).
   It is never hard-coded here, so changing the configuration changes the verdict
   without a code edit; an absent key is a usage error, not a guessed default.
2. Every tracked `*.md` file is scanned, except the generated catalog under
   `docs/<lang>/skills/` and `docs/<lang>/agents/` (prose checked at its source)
   and `.audits/`, whose dated records quote the configuration of the day they
   were written. `project/` is in scope: it was excluded in this guard's first
   draft on the assumption that it is a record tree too, and measuring it refuted
   that — its tracked files produce no hits, and mission, roadmap, feature and
   sprint prose is live prose that can acquire the claim. The scope
   is expressed as an **exclusion**, so a new file or a new top-level directory
   is in scope by default rather than by being named correctly (G6). Fenced
   content is scanned like prose, because an operator-visible template inside a
   fence states the claim to a reader who never opens the file; measured over
   both the pre-fix and the repaired tree, scanning fences adds one true positive
   and no false positive.
3. Lines are joined into logical units (a blank line, a heading, or a fence
   boundary ends one), and units are split into sentences on `[.!?;]` followed by
   whitespace. The unit join is load-bearing: the line-by-line form of this
   predicate was measured against the five known sites and missed three of them,
   because a claim wrapped across two source lines is one sentence, not two
   (a G6 selector failure — the selector must match the property's scope).
4. A sentence is a finding when it carries a default-branch marker
   (`default branch`, `default-branch`, `default is`, `defaults to`, `default:`,
   `Standard-Branch` — case-insensitive, German included) **and** a backticked
   branch literal from {main, master, trunk, develop} that differs from the
   configured branch. The literal's backtick delimiters may be backslash-escaped,
   so a claim inside a shell heredoc or a `gh --comment` template is seen too.

Exceptions are the allowlist below (G4): one entry per excused sentence, each
naming its reason, matched by path plus a distinctive substring so that an entry
whose sentence changed no longer matches. An entry that matches nothing fails the
run, so the list cannot outlive its reason.

What this guard cannot decide (G7 — it must not certify the part of the class the
fix did not repair). A green run means no *stated* wrong default branch, not full
coverage of the wrong-default-branch class:

- **Consequence-form claims.** A site can state the same wrong premise through
  its consequence, naming no default branch at all. Two such sentences existed in
  `skills/pull-request-merge/references/issue-closure.md` — "waiting for the next
  `release-cd-refresh-master.yml` fast-forward of `main`" and "because `main` was
  fast-forwarded between the merge and this step" — and were repaired by hand.
  This predicate reports zero there, and that zero is not a check.
- **Branch names in non-literal delimiters.** The literal is matched inside
  backticks, with the delimiters optionally backslash-escaped (the shape a shell
  heredoc or a `gh --comment` template carries; that widening was measured to add
  one true positive and no false positive). A branch named in plain prose, in a
  URL, or under any other quoting is still invisible to it.

Both shapes were repaired by hand in the pull request that introduced this guard;
neither is certified by a green run.

Exit codes: 0 clean, 1 findings (stated claims or a stale allowlist entry),
2 usage error.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

SETTINGS = Path(".github/settings.yml")
DEFAULT_BRANCH_KEY = re.compile(r"^\s*default_branch:\s*['\"]?([\w./-]+)['\"]?\s*(?:#.*)?$", re.MULTILINE)

# Out of scope, as an exclusion so that new live prose is covered by default:
# the generated skill/agent catalog (its source prose is checked where it lives)
# and `.audits/`, whose records quote the configuration of the day they were
# written and must not be rewritten to today's.
#
# `project/` is deliberately NOT excluded. It was excluded in the first draft of
# this guard on the assumption that it is a record tree too; measuring it refuted
# that — its 60-odd tracked files produce zero hits, and mission, roadmap, feature
# and sprint prose is live prose that can acquire the claim. Excluding a tree that
# no measurement implicated is the selector-too-narrow failure of
# `spec/project/defect-class-guards/` G6, which this guard exists to enforce.
OUT_OF_SCOPE = re.compile(r"^(docs/[a-z]{2}/(skills|agents)/|\.audits/)")

FENCE = re.compile(r"^\s*(```|~~~)")
HEADING = re.compile(r"^\s*#{1,6}\s")
SENTENCE_SPLIT = re.compile(r"(?<=[.!?;])\s+")

BRANCH_NAMES = ("main", "master", "trunk", "develop")
# `\\`main\\`` inside a shell heredoc or a `gh --comment` template is the same
# claim with escaped delimiters, so the escape is optional on both sides.
BRANCH_LITERAL = re.compile(r"\\?`(" + "|".join(BRANCH_NAMES) + r")\\?`")
MARKER = re.compile(
    r"default[  -]branch|standard[ -]?branch|default is|defaults to|default:",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Allowed:
    """One excused sentence: its file, a distinctive substring of it, and why."""

    path: str
    substring: str
    reason: str


ALLOWLIST = (
    Allowed(
        path="skills/issue-orchestrate/references/verification-scoping.md",
        substring="a repo whose default is `main` while `develop` integrates",
        reason=(
            "describes a hypothetical other repository, to explain why a built-in "
            "review reads the wrong diff; it is not a claim about this repository"
        ),
    ),
)


@dataclass(frozen=True)
class Finding:
    cls: str
    file: str
    line: int
    message: str

    def __str__(self) -> str:
        return f"{self.file}:{self.line}: {self.cls}: {self.message}"


def configured_branch(repo: Path) -> str:
    """The default branch the repository configuration declares."""
    settings = repo / SETTINGS
    if not settings.is_file():
        raise LookupError(f"{SETTINGS.as_posix()} is missing; the expected branch is read from it, never assumed")
    match = DEFAULT_BRANCH_KEY.search(settings.read_text(encoding="utf-8"))
    if not match:
        raise LookupError(f"{SETTINGS.as_posix()} declares no `default_branch:`; the expected branch cannot be read")
    return match.group(1)


def markdown_files(repo: Path) -> list[Path]:
    """Tracked `*.md` files, minus the generated catalog."""
    try:
        listed = subprocess.run(
            ["git", "-C", str(repo), "ls-files", "-z", "--", "*.md"],
            capture_output=True, check=True, text=True,
        ).stdout
        rels = [r for r in listed.split("\0") if r]
    except (OSError, subprocess.CalledProcessError):
        rels = sorted(p.relative_to(repo).as_posix() for p in repo.rglob("*.md") if ".git/" not in p.as_posix())
    return [repo / rel for rel in rels if not OUT_OF_SCOPE.match(rel)]


def units(text: str):
    """Yield (first line number, joined text) for each logical unit.

    A blank line, a heading, or a fence delimiter ends a unit. Fenced content is
    scanned like prose rather than skipped: an operator-visible template inside a
    fence (a `gh issue close --comment` string) states the claim to a reader who
    never opens the file.
    """
    buffer: list[str] = []
    start = 0
    for number, line in enumerate(text.splitlines(), 1):
        if FENCE.match(line) or not line.strip() or HEADING.match(line):
            if buffer:
                yield start, " ".join(buffer)
                buffer = []
            continue
        if not buffer:
            start = number
        buffer.append(line.strip())
    if buffer:
        yield start, " ".join(buffer)


def sentences(unit: str):
    for sentence in SENTENCE_SPLIT.split(unit):
        stripped = sentence.strip()
        if stripped:
            yield stripped


def check(repo: Path) -> list[Finding]:
    expected = configured_branch(repo)
    findings: list[Finding] = []
    used: set[Allowed] = set()
    for path in markdown_files(repo):
        rel = path.relative_to(repo).as_posix()
        for line, unit in units(path.read_text(encoding="utf-8")):
            for sentence in sentences(unit):
                if not MARKER.search(sentence):
                    continue
                wrong = [b for b in BRANCH_LITERAL.findall(sentence) if b != expected]
                if not wrong:
                    continue
                excuse = next((a for a in ALLOWLIST if a.path == rel and a.substring in sentence), None)
                if excuse is not None:
                    used.add(excuse)
                    continue
                findings.append(Finding(
                    "default-branch-claim", rel, line,
                    f"names `{wrong[0]}` where {SETTINGS.as_posix()} configures `{expected}`: {sentence}",
                ))
    for entry in ALLOWLIST:
        if entry not in used:
            findings.append(Finding(
                "stale-allowlist-entry", entry.path, 0,
                f"the excused sentence is gone ({entry.substring!r}); drop the entry — its reason has outlived it",
            ))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--report", action="store_true", help="also list the allowlist entries and what they excuse")
    parser.add_argument("--repo", type=Path, default=REPO, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    try:
        expected = configured_branch(args.repo)
        findings = check(args.repo)
    except LookupError as error:
        print(f"usage: {error}", file=sys.stderr)
        return 2

    if args.report:
        for entry in ALLOWLIST:
            print(f"allowlist: {entry.path}: {entry.substring!r} — {entry.reason}")
    for finding in findings:
        print(finding)
    if findings:
        print(f"\nDefault-branch claims: {len(findings)} finding(s) against the configured branch `{expected}`. "
              "See spec/project/defect-class-guards/en.md §\"The rules\" (#652).", file=sys.stderr)
        return 1
    print(f"Default-branch claims: pass (configured branch `{expected}`, {len(ALLOWLIST)} allowlist entr(y/ies) live)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
