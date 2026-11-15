#!/usr/bin/env python3
"""Decide whether a boot protocol is current evidence for an image definition.

A ``protocol.json`` from ``image-boot-verify`` records the commit of the image
definition the artifact was built from. It's current evidence for the audited
revision only when no path that belongs to the image changed after that commit
(``spec/project/linux-image-best-practices/`` §A: the build configuration, every
overlay or extra tree, every package list, and every lock or manifest file).

The caller passes the path set: the declaration, its ``image.definition``, the
declaration's directory, and every definition file the scanner reports (overlay
trees, unit files, package lists, lock files, the build entry point). For each
path the helper runs::

    git -C <repo> log -1 --format=%H <protocol-commit>..<revision> -- <path>

and also checks that the protocol commit is an ancestor of the revision
(``git merge-base --is-ancestor``) and, when the revision is ``HEAD``, that the
path has no uncommitted change (``git status --porcelain``).

Guards, each yielding ``not-decidable`` rather than ``fresh``: the protocol
commit must be a full hexadecimal object name (a symbolic name such as ``HEAD``
or a branch would resolve to the audited revision itself); every path must exist
at the revision (``git cat-file -e``), since ``git log`` on a path that never
existed is silently empty; and no path may be or contain a symbolic link
(``git ls-tree -r``), since history follows the link, not its target. Paths are
literal pathspecs (``GIT_LITERAL_PATHSPECS=1``).

Output, one line per finding on stdout:
  ``fresh``                                    every path unchanged since the commit
  ``stale: <path> changed in <sha>``           a commit after the protocol touched it
  ``stale: <path> has uncommitted changes``    the working tree differs
  ``stale: <commit> isn't an ancestor of <rev>``
  ``not-decidable: <reason>``                  git, the commit, or a path is unusable

Exit codes: 0 fresh, 1 stale, 2 not decidable.

Usage:
  python3 "${CLAUDE_PLUGIN_ROOT}/skills/linux-image-audit/scripts/protocol_freshness.py" \\
      --repo . --commit <protocol image-definition commit> [--rev HEAD] -- <path> [<path> ...]
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path


FULL_SHA = re.compile(r"[0-9a-f]{40}(?:[0-9a-f]{24})?")


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo), "-c", "core.quotepath=off", *args],
        capture_output=True, text=True, check=False,
        env={**os.environ, "GIT_LITERAL_PATHSPECS": "1"},
    )


def _verify_commit(repo: Path, ref: str) -> str | None:
    proc = _git(repo, "rev-parse", "--verify", "--quiet", "--end-of-options", f"{ref}^{{commit}}")
    return proc.stdout.strip() if proc.returncode == 0 and proc.stdout.strip() else None


def check(repo: Path, commit: str, rev: str, paths: list[str]) -> tuple[int, list[str]]:
    if not paths:
        return 2, ["not-decidable: empty path set"]
    if not FULL_SHA.fullmatch(commit):
        return 2, [f"not-decidable: protocol commit {commit!r} isn't a full commit id"]
    try:
        protocol_sha = _verify_commit(repo, commit)
    except FileNotFoundError:
        return 2, ["not-decidable: git isn't installed"]
    if protocol_sha is None:
        return 2, [f"not-decidable: protocol commit {commit} isn't a commit in {repo}"]
    rev_sha = _verify_commit(repo, rev)
    if rev_sha is None:
        return 2, [f"not-decidable: revision {rev} isn't a commit in {repo}"]

    ancestor = _git(repo, "merge-base", "--is-ancestor", protocol_sha, rev_sha)
    if ancestor.returncode == 1:
        return 1, [f"stale: {commit} isn't an ancestor of {rev}"]
    if ancestor.returncode != 0:
        return 2, [f"not-decidable: git merge-base failed: {ancestor.stderr.strip()}"]

    for path in paths:
        if _git(repo, "cat-file", "-e", f"{rev_sha}:{path}").returncode != 0:
            return 2, [f"not-decidable: {path} doesn't exist at {rev}"]
        tree = _git(repo, "ls-tree", "-r", rev_sha, "--", path)
        if tree.returncode != 0:
            return 2, [f"not-decidable: git ls-tree failed for {path}: {tree.stderr.strip()}"]
        links = [line.split("\t", 1)[1] for line in tree.stdout.splitlines() if line.startswith("120000 ")]
        if links:
            return 2, [f"not-decidable: {links[0]} is a symbolic link; its target's history isn't covered"]

    findings: list[str] = []
    for path in paths:
        log = _git(repo, "log", "-1", "--format=%H", f"{protocol_sha}..{rev_sha}", "--", path)
        if log.returncode != 0:
            return 2, [f"not-decidable: git log failed for {path}: {log.stderr.strip()}"]
        sha = log.stdout.strip()
        if sha:
            findings.append(f"stale: {path} changed in {sha}")
            continue
        if rev == "HEAD":
            status = _git(repo, "status", "--porcelain", "--", path)
            if status.returncode != 0:
                return 2, [f"not-decidable: git status failed for {path}: {status.stderr.strip()}"]
            if status.stdout.strip():
                findings.append(f"stale: {path} has uncommitted changes")
    if findings:
        return 1, findings
    return 0, ["fresh"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check a boot protocol's freshness.")
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Repository root.")
    parser.add_argument("--commit", required=True,
                        help="The image-definition commit the protocol records.")
    parser.add_argument("--rev", default="HEAD", help="The audited revision (default HEAD).")
    parser.add_argument("paths", nargs="+", help="The image's path set.")
    args = parser.parse_args(argv)
    code, lines = check(args.repo, args.commit, args.rev, args.paths)
    for line in lines:
        print(line)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
