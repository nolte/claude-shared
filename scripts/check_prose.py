#!/usr/bin/env python3
"""Run Vale on the prose release-drafter publishes: pull-request titles and release notes.

Guard origin (spec/project/defect-class-guards/ G5): #582.

Implements spec/project/prose-style/ §"Pull-request titles and release notes".

--title checks the pull-request title, read with its author from PR_TITLE and
PR_AUTHOR. The Conventional-Commits prefix `type(scope)!:` is masked as a code
span first, because its lowercase type and scope are machine vocabulary the Vale
term rules would flag; the summary after it is checked in full. A title from an
allowlisted dependency bot is skipped, since it embeds package identifiers
verbatim. Any error-level alert exits 1. Pull-request descriptions are not
checked: release-drafter never publishes them.

--release-notes TAG (read through `gh`) or --file PATH checks a release-notes
body. Each release-drafter entry has its prefix, pull-request reference and
author mention masked, and a dependency bot's entry also its package name.
Findings are printed and never fail the run, because the verification is
advisory and must never block a publish.

The text reaches Vale only as a temporary Markdown file written inside the
repository, so .vale.ini's `[*.md]` section applies and no shell ever sees it.

Exit codes: 0 pass or advisory report, 1 title alerts, 2 usage error or a check
that could not run (no Vale, a Vale runtime error, no `gh` access, an unreadable
file). A check that could not run never reads as a pass.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Dependency bots whose pull-request titles skip the Vale check, keyed by the
# author login GitHub puts in the event payload. Every entry needs a reason (spec
# §PR preconditions). The body checks in nolte/gh-plumbing's reusable-pr-lint.yaml
# carry the same logins for the body; a new bot goes into both. Matching is exact,
# never on the account type, so an unlisted bot stays subject to every rule.
EXEMPT_BOT_AUTHORS: dict[str, str] = {
    "renovate[bot]": (
        "Renovate's titles embed package identifiers verbatim (for example "
        "`update dependency mkdocs-material to v9.7.7`), which the Vale term and "
        "spelling rules would flag as prose errors. Its title form is still checked "
        "as Conventional Commits by the body check in gh-plumbing."
    ),
}

REPO = Path(__file__).resolve().parent.parent
TICK = "`"
TITLE_PREFIX = re.compile(r"^([a-z][a-z-]*(?:\([^()]*\))?!?:)\s*")
ENTRY_PREFIX = re.compile(r"^(\s*[*-]\s+)([a-z][a-z-]*(?:\([^()]*\))?!?:)")
PR_REFERENCE = re.compile(r"\(#\d+\)")
# `@[renovate[bot]](https://...)` nests one bracket pair inside the link text.
AUTHOR = re.compile(r"@\[(?:[^\[\]]|\[[^\]]*\])*\]\([^)]*\)|@[A-Za-z0-9-]+(?:\[bot\])?")
# Only a bot entry embeds a package identifier; a human title keeps every word checked.
BOT_AUTHOR = re.compile(r"@\[?[A-Za-z0-9-]+\[bot\]")
DEPENDENCY = re.compile(
    r"\b((?:update|pin|bump)(?: pre-commit hook| dependency| dependencies| action| module| image)?) "
    r"([A-Za-z0-9@/._-]+)"
)


class CheckUnavailable(Exception):
    """The check could not run, which must never read as a pass."""


def _code(text: str) -> str:
    return f"{TICK}{text}{TICK}"


def mask_title(title: str) -> str:
    return TITLE_PREFIX.sub(lambda m: _code(m.group(1)) + " ", title.strip(), count=1)


def mask_release_notes(body: str) -> str:
    lines = []
    for line in body.splitlines():
        if ENTRY_PREFIX.match(line):
            line = ENTRY_PREFIX.sub(lambda m: m.group(1) + _code(m.group(2)), line, count=1)
            line = PR_REFERENCE.sub(lambda m: _code(m.group(0)), line)
            line = AUTHOR.sub(lambda m: _code(m.group(0)), line)
            if BOT_AUTHOR.search(line):
                line = DEPENDENCY.sub(lambda m: f"{m.group(1)} {_code(m.group(2))}", line)
        lines.append(line)
    return "\n".join(lines) + "\n"


def run_vale(text: str, runner=subprocess.run) -> list[dict]:
    vale = shutil.which("vale")
    if vale is None:
        raise CheckUnavailable(
            "vale is not on PATH; install the version pinned in .github/workflows/ci.yml and run `vale sync`"
        )
    tmpdir = tempfile.mkdtemp(prefix="prose-check-", dir=REPO)
    try:
        path = Path(tmpdir, "prose.md")
        path.write_text(text, encoding="utf-8")
        proc = runner([vale, "--output=JSON", str(path)], cwd=REPO, capture_output=True, text=True)
        try:
            data = json.loads(proc.stdout or "{}")
        except json.JSONDecodeError as exc:
            detail = (proc.stdout or proc.stderr or "").strip()[:300]
            raise CheckUnavailable(f"vale exited {proc.returncode} without a JSON report: {detail}") from exc
        # A Vale runtime error (unsynced styles, a broken .vale.ini) is also JSON, but a
        # single object with `Code` and `Text` instead of a map of file -> alert list.
        if not isinstance(data, dict) or not all(
            isinstance(alerts, list) and all(isinstance(a, dict) for a in alerts) for alerts in data.values()
        ):
            detail = data.get("Text", data) if isinstance(data, dict) else data
            raise CheckUnavailable(f"vale exited {proc.returncode} with a runtime error: {str(detail)[:300]}")
        return [a for alerts in data.values() for a in alerts if a.get("Severity") == "error"]
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def _release_body(tag: str, runner) -> str:
    proc = runner(["gh", "release", "view", tag, "--json", "body", "--jq", ".body"],
                  cwd=REPO, capture_output=True, text=True)
    if proc.returncode != 0:
        raise CheckUnavailable(
            f"gh could not read release {tag}: {proc.stderr.strip()[:200]} "
            "(a draft is only visible to an account with push access)"
        )
    return proc.stdout


def main(argv: list[str] | None = None, runner=subprocess.run) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--title", action="store_true", help="check $PR_TITLE; fails on error-level alerts")
    mode.add_argument("--release-notes", metavar="TAG", help="advisory check of release TAG's notes, read through gh")
    mode.add_argument("--file", metavar="PATH", help="advisory check of a release-notes body saved to PATH")
    args = parser.parse_args(argv)

    try:
        if args.title:
            title = os.environ.get("PR_TITLE")
            if title is None:
                print("usage: set PR_TITLE (and PR_AUTHOR) for --title", file=sys.stderr)
                return 2
            author = os.environ.get("PR_AUTHOR")
            if author in EXEMPT_BOT_AUTHORS:
                print(f"PR title prose: skipped for the allowlisted dependency bot {author}")
                return 0
            alerts = run_vale(mask_title(title) + "\n", runner)
            if alerts:
                print(f"PR title prose: {len(alerts)} Vale error(s) in {title!r}\n")
                for alert in alerts:
                    print(f"  - {alert.get('Check')}: {alert.get('Message')} (match {alert.get('Match')!r})")
                print('\nSee spec/project/prose-style/en.md §"Pull-request titles and release notes".')
                return 1
            print("PR title prose: pass")
            return 0

        label = args.file or args.release_notes
        if args.file:
            try:
                body = Path(args.file).read_text(encoding="utf-8")
            except OSError as exc:
                raise CheckUnavailable(f"cannot read {args.file}: {exc}") from exc
        else:
            body = _release_body(args.release_notes, runner)
        alerts = run_vale(mask_release_notes(body), runner)
        if alerts:
            print(f"Release notes prose (advisory, never blocking): {len(alerts)} Vale error(s) in {label}\n")
            for alert in alerts:
                print(f"  - line {alert.get('Line')}: {alert.get('Check')}: {alert.get('Message')}")
        else:
            print(f"Release notes prose (advisory): no Vale errors in {label}")
        return 0
    except CheckUnavailable as exc:
        print(f"prose check could not run: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
