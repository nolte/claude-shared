#!/usr/bin/env python3
"""Lint a pull request's title and body against spec/project/pull-request-workflow/.

Implements the checks that spec §"PR lint workflow" declares as a required status
check: the Conventional-Commits title form, the five required body sections in
order, the non-empty rule for Summary / Changes / Testing, and the
type-conditional `## Class sweep` section that §"Class sweep (Conventional-Commits
type `fix`)" requires on type `fix` and forbids on every other type.

Reads the title and body from the environment (PR_TITLE / PR_BODY) or from
--title / --body-file, so a workflow never interpolates untrusted pull-request
text into a shell command.

Exit code 0 when every rule holds, 1 when any fails, 2 on a usage error.
"""

from __future__ import annotations

import argparse
import os
import re
import sys

TYPES = ("feat", "fix", "chore", "docs", "exp")
TITLE_RE = re.compile(r"^(?P<type>[a-z]+)(?:\((?P<scope>[^()]+)\))?: (?P<summary>.+)$")

REQUIRED_SECTIONS = ("Summary", "Changes", "Linked issues", "Testing", "Risk / rollout notes")
NON_EMPTY_SECTIONS = ("Summary", "Changes", "Testing")
SWEEP_SECTION = "Class sweep"
SWEEP_FIELDS = ("Predicate", "Hits", "Repaired", "Guard")
INTEGER_FIELDS = ("Hits", "Repaired")

HEADING_RE = re.compile(r"^##[ \t]+(?P<name>.+?)[ \t]*$", re.MULTILINE)


def split_sections(body: str) -> list[tuple[str, str]]:
    """Return [(heading, content)] for every level-2 heading, in document order."""
    matches = list(HEADING_RE.finditer(body))
    out = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        out.append((m.group("name"), body[m.end():end]))
    return out


def strip_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def is_empty(content: str) -> bool:
    stripped = strip_comments(content).strip()
    return not stripped or stripped == "None"


def field_value(content: str, field: str) -> str | None:
    """Value of a `- <Field>: <value>` line, or None when the line is absent."""
    pattern = re.compile(rf"^[-*][ \t]+{re.escape(field)}:[ \t]*(?P<value>.*)$", re.MULTILINE)
    m = pattern.search(strip_comments(content))
    if m is None:
        return None
    return m.group("value").strip()


def check(title: str, body: str) -> list[str]:
    failures: list[str] = []

    title_match = TITLE_RE.match(title.strip())
    if title_match is None:
        failures.append(
            f"title {title.strip()!r} does not match the Conventional Commits form "
            "`<type>(<scope>)?: <summary>` (spec §PR preconditions)"
        )
        pr_type = None
    else:
        pr_type = title_match.group("type")
        if pr_type not in TYPES:
            failures.append(
                f"title type {pr_type!r} is outside the closed vocabulary "
                f"{{{', '.join(TYPES)}}} (spec §PR preconditions)"
            )
            pr_type = None

    sections = split_sections(body)
    headings = [name for name, _ in sections]
    by_name = {name: content for name, content in sections}

    missing = [s for s in REQUIRED_SECTIONS if s not in by_name]
    if missing:
        failures.append(
            "body is missing the required section(s) "
            + ", ".join(f"`## {s}`" for s in missing)
            + " (spec §PR description structure)"
        )
    else:
        positions = [headings.index(s) for s in REQUIRED_SECTIONS]
        if positions != sorted(positions):
            failures.append(
                "the five required sections are present but out of order; expected "
                + " → ".join(REQUIRED_SECTIONS)
                + " (spec §PR description structure)"
            )

    for name in NON_EMPTY_SECTIONS:
        if name in by_name and is_empty(by_name[name]):
            failures.append(
                f"section `## {name}` is empty or contains only `None`; only "
                "Linked issues and Risk / rollout notes may be `None` "
                "(spec §PR description structure)"
            )

    if pr_type == "fix":
        if SWEEP_SECTION not in by_name:
            failures.append(
                f"a `fix` pull request must carry a `## {SWEEP_SECTION}` section stating the "
                "defect class it swept, in numbers "
                '(spec §"Class sweep (Conventional-Commits type `fix`)")'
            )
        else:
            content = by_name[SWEEP_SECTION]
            for field in SWEEP_FIELDS:
                value = field_value(content, field)
                if value is None:
                    failures.append(
                        f"`## {SWEEP_SECTION}` is missing the field `- {field}:` "
                        '(spec §"Class sweep (Conventional-Commits type `fix`)")'
                    )
                    continue
                if not value or value.startswith("<"):
                    failures.append(
                        f"`## {SWEEP_SECTION}` field `{field}` is empty or still carries its "
                        "placeholder "
                        '(spec §"Class sweep (Conventional-Commits type `fix`)")'
                    )
                    continue
                if field in INTEGER_FIELDS and not re.fullmatch(r"\d+", value):
                    failures.append(
                        f"`## {SWEEP_SECTION}` field `{field}` is {value!r}, which is not an "
                        "integer; the section states counts, not prose "
                        '(spec §"Class sweep (Conventional-Commits type `fix`)")'
                    )

    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", default=None, help="PR title; defaults to $PR_TITLE")
    parser.add_argument("--body-file", default=None, help="file holding the PR body; defaults to $PR_BODY")
    args = parser.parse_args(argv)

    title = args.title if args.title is not None else os.environ.get("PR_TITLE")
    if args.body_file is not None:
        with open(args.body_file, encoding="utf-8") as handle:
            body = handle.read()
    else:
        body = os.environ.get("PR_BODY")

    if title is None or body is None:
        print("usage: provide --title/--body-file or set PR_TITLE/PR_BODY", file=sys.stderr)
        return 2

    failures = check(title, body)
    if failures:
        print(f"PR body lint: {len(failures)} failure(s)\n")
        for failure in failures:
            print(f"  - {failure}")
        print(
            "\nSee spec/project/pull-request-workflow/en.md "
            '§"PR description structure" and §"PR lint workflow".'
        )
        return 1
    print("PR body lint: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
