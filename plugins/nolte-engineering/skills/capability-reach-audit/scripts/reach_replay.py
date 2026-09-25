#!/usr/bin/env python3
"""Replay a Markdown declaration's history: file-anchor versus section-anchor stale events.

Measurement aid for section anchors (spec/project/capability-reach-audit/,
schemas/reach-probe-v1.2.schema.yaml): given a declaration file and the
locators a set of probes would anchor on, walk the commits that touched the
file, oldest first, along the first-parent history of ``--rev``, and print per
commit whether the file's content changed and which locators' sections changed,
then the totals. A probe anchored on the whole file (``derived_from: blob:``)
goes stale on every content change; a probe anchored on sections goes stale only
when one of its sections changed, stopped resolving, or became ambiguous, which
is exactly what reach_audit.py checks.

The replay is hypothetical: it assumes every probe existed from the file's first
commit. It reads the history only, writes nothing, and does not follow a rename
of the declaration (the history ends where the path does).

Output is deterministic text:

  replay of <path> at <rev12>: <N> commits, <M> probes
  <sha12> first
  <sha12> file changed; sections changed: heading:3.1; stale probes: file 3, section 2
  ...
  file-anchor stale events: <total>
  section-anchor stale events: <total>

Exit codes: 0 replay printed, 1 git failed, 2 usage error (bad locator, not a
local working copy, a declaration without history at ``--rev``).

Usage:
  python reach_replay.py --repo ~/repos/github/kamerplanter \\
      --declaration spec/req/REQ-025_Datenschutz-Betroffenenrechte.md \\
      --probe erasure=heading:3.1.1,row:AK-OS-07 --probe export=heading:3.5
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import reach_audit as ra  # noqa: E402 - the runner ships next to this script

PROBE_FORM = "NAME=KIND:LOCATOR[,KIND:LOCATOR...] with KIND heading or row"

Locator = tuple[str, str]


def parse_probe(raw: str) -> tuple[str, list[Locator]]:
    """``NAME=heading:3.1,row:AK-OS-07`` as ``(name, [(kind, locator), ...])``; ValueError when malformed."""
    name, sep, spec = raw.partition("=")
    if not sep or not name or not spec:
        raise ValueError(raw)
    locators: list[Locator] = []
    for part in spec.split(","):
        kind, sep, locator = part.partition(":")
        if not sep or kind not in ra.SECTION_KINDS or not locator or (kind, locator) in locators:
            raise ValueError(raw)
        locators.append((kind, locator))
    return name, locators


def section_state(content: bytes | None, kind: str, locator: str) -> str:
    """The section's digest, or why it has none: what a section anchor compares."""
    found = ra.find_sections(content, kind, locator) if content is not None else []
    if not found:
        return "not found"
    if len(found) > 1:
        return f"ambiguous ({len(found)} matches)"
    return ra.section_digest(found[0])


def replay(git: ra.Git, declaration: str, probes: list[tuple[str, list[Locator]]], rev: str) -> list[str]:
    """The replay's output lines; ``rev`` is a resolved commit."""
    commits = git.out("--literal-pathspecs", "log", "--reverse", "--first-parent", "--format=%H", rev,
                      "--", declaration).split()
    if not commits:
        raise ra.AuditError(f"{ra.safe_text(declaration)} has no history at {rev[:12]}", code=ra.EXIT_USAGE)
    locators = list(dict.fromkeys(loc for _, locs in probes for loc in locs))
    lines = [f"replay of {ra.safe_text(declaration)} at {rev[:12]}: {len(commits)} commits, {len(probes)} probes"]
    file_total = section_total = 0
    previous: tuple[str | None, dict[Locator, str]] | None = None
    for commit in commits:
        blob = git.blob_at(commit, declaration)
        content = git.read_blob(blob) if blob is not None else None
        states = {loc: section_state(content, *loc) for loc in locators}
        if previous is None:
            lines.append(f"{commit[:12]} first")
        else:
            file_changed = blob != previous[0]
            changed = [loc for loc in locators if states[loc] != previous[1][loc]]
            file_events = len(probes) if file_changed else 0
            section_events = sum(1 for _, locs in probes if any(loc in changed for loc in locs))
            file_total += file_events
            section_total += section_events
            named = ", ".join(
                f"{kind}:{ra.safe_text(locator, 80)}" + ("" if ra._DIGEST_RE.match(states[(kind, locator)])
                                                          else f" ({states[(kind, locator)]})")
                for kind, locator in changed) or "none"
            lines.append(f"{commit[:12]} file {'changed' if file_changed else 'unchanged'}; "
                         f"sections changed: {named}; stale probes: file {file_events}, section {section_events}")
        previous = (blob, states)
    lines += [f"file-anchor stale events: {file_total}", f"section-anchor stale events: {section_total}"]
    return lines


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Count file-anchor versus section-anchor stale events over a Markdown declaration's history.",
        epilog="Exit codes: 0 replay printed, 1 git failed, 2 usage error.",
    )
    parser.add_argument("--repo", required=True, help="Path to the local git working copy.")
    parser.add_argument("--declaration", required=True, help="The Markdown declaration, relative to the repository root.")
    parser.add_argument("--probe", action="append", required=True, metavar="NAME=KIND:LOCATOR[,...]",
                        help="A probe and the locators it would anchor on; repeat per probe.")
    parser.add_argument("--rev", default="HEAD", help="Replay the first-parent history up to this commit (default HEAD).")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    probes: list[tuple[str, list[Locator]]] = []
    for raw in args.probe:
        try:
            probe = parse_probe(raw)
        except ValueError:
            sys.stderr.write(f"reach_replay: --probe {ra.safe_text(raw)!r} is not {PROBE_FORM}.\n")
            return ra.EXIT_USAGE
        if probe[0] in (name for name, _ in probes):
            sys.stderr.write(f"reach_replay: probe name {ra.safe_text(probe[0])!r} is given twice.\n")
            return ra.EXIT_USAGE
        probes.append(probe)
    declaration = ra._repo_relative(args.declaration)
    if declaration is None:
        sys.stderr.write(f"reach_replay: --declaration {ra.safe_text(args.declaration)!r} lies outside the repository.\n")
        return ra.EXIT_USAGE
    try:
        repo = ra.require_local_working_copy(args.repo)
        git = ra.Git(repo)
        rev = git.resolve_commit(args.rev)
        if rev is None:
            raise ra.AuditError(f"--rev {ra.safe_text(args.rev)!r} is not a commit", code=ra.EXIT_USAGE)
        lines = replay(git, declaration, probes, rev)
    except ra.AuditError as exc:
        sys.stderr.write(f"reach_replay: {exc}\n")
        return exc.code
    print("\n".join(lines))
    return ra.EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
