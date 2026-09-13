#!/usr/bin/env python3
"""Resolve cross-references in the spec corpus and the live documentation.

Implements the structural fix `spec/project/spec-readiness/` asks for in
§Dimension 3: a section reference resolves against the headings of the file
in the language that carries it. Resolution reads the target headings; it
doesn't guess where a section name ends.

Blocking classes, each exactly decidable (exit 1):

- section-other-language: a `§` reference in `spec/**/<lang>.md` resolves in
  another language file of its target but not in its own language.
- moved-artifact-path: a backticked `skills/...` or `agents/...` path in live
  documentation is absent at the repository root but exists under
  `plugins/<plugin>/`, the state an artifact is left in after a carve-out.
- heading-contract: an acceptance-criteria heading doesn't use the contract
  form of its language (`## Acceptance Criteria`, `## Akzeptanzkriterien`).

Reported without failing (--report): section-unresolved, a reference that
resolves in no language. That class holds genuine ghosts, but also unquoted
shortenings a resolver can't tell apart from them, so it stays advisory.

How a reference resolves:

- A quoted reference (§"…", §„…") names a heading or a prefix of one.
- An unquoted reference is followed by text that starts with a heading at a
  word boundary, or with the heading minus a trailing parenthetical
  (§Frontmatter validation for "Frontmatter validation (Agent Skills spec)"),
  or by a letter or number label (§H, §2, §2.3).
- The candidate targets are the citing file and the last spec reference
  earlier on the same line (`spec/<topic>/<slug>/`, `slug`, or a relative
  link to `../<slug>/<lang>.md`); any candidate that resolves is enough.
- Fenced code, references inside code spans, `§ 5`-style legal citations
  (a space before the number) and §`name` are not section references.
- A reference to a non-contract acceptance-criteria name (§Abnahmekriterien,
  or §Acceptance Criteria from a German file) is a heading-contract finding.

Exit codes: 0 clean, 1 blocking findings, 2 usage error.
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

LANG_FILE = re.compile(r"^[a-z]{2}$")
FENCE = re.compile(r"^\s*(```|~~~)")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*(?:\{#[^}]*\})?\s*$")
CODE_SPAN = re.compile(r"(`+)(?:(?!\1).)+?\1")
QUOTES = {'"': '"', "„": "“\"”", "“": "”\""}
PARENTHETICAL = re.compile(r"\s*\([^()]*\)\s*$")
REFERENCE = re.compile(
    r"`(?P<path>spec/[\w./-]+?)/?(?:[a-z]{2}\.md)?`"
    r"|`(?P<name>[a-z0-9][\w-]*)`"
    r"|(?<![\w/`-])(?P<bare>[a-z0-9]+(?:-[a-z0-9]+)+)(?![\w/`-])"
    r"|\]\((?:\.\./)+(?P<href>[\w/-]+?)/[a-z]{2}\.md"
)
LABEL = re.compile(r"^([a-z]|\d+(?:\.\d+)*)(?=[\s.,;:/)—-]|$)")
ARTIFACT_PATH = re.compile(r"`((?:skills|agents)/[\w.-]+(?:/[\w./-]*)?)`")

# The contract form of the acceptance-criteria heading per language. Other
# languages aren't checked until a contract names them.
AC_CONTRACT = {"en": "Acceptance Criteria", "de": "Akzeptanzkriterien"}
AC_VARIANTS = {"acceptance criteria", "akzeptanzkriterien", "abnahmekriterien"}

# Live documentation, where a moved path misleads a reader today. `.audits/`
# and `project/` are records of their time and keep the paths they cited.
LIVE_DOCS = ("spec/", "docs/", "skills/", "agents/", "plugins/")


@dataclass(frozen=True)
class Finding:
    cls: str
    file: str
    line: int
    message: str

    @property
    def blocking(self) -> bool:
        return self.cls != "section-unresolved"

    def __str__(self) -> str:
        return f"{self.file}:{self.line}: {self.cls}: {self.message}"


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    for old, new in (("`", ""), ("*", ""), ("’", "'"), ("–", "-"), ("—", "-")):
        text = text.replace(old, new)
    text = re.sub(r"\s*-\s+|\s+-\s*", " - ", text)
    return re.sub(r"\s+", " ", text).strip().casefold()


def markdown_lines(path: Path):
    """Yield (number, line) outside fenced code blocks."""
    in_fence = False
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield number, line


class Corpus:
    def __init__(self, repo: Path):
        self.repo = repo
        self._headings: dict[Path, list[tuple[int, str]]] = {}
        slugs: dict[str, list[Path]] = {}
        for canonical in (repo / "spec").rglob("en.md"):
            slugs.setdefault(canonical.parent.name, []).append(canonical.parent)
        self.slugs = {name: dirs[0] for name, dirs in slugs.items() if len(dirs) == 1}

    def headings(self, path: Path) -> list[tuple[int, str]]:
        if path not in self._headings:
            found = []
            if path.is_file():
                for _, line in markdown_lines(path):
                    if match := HEADING.match(line):
                        found.append((len(match.group(1)), match.group(2)))
            self._headings[path] = found
        return self._headings[path]

    def spec_dir(self, match: re.Match) -> Path | None:
        if match.group("path"):
            directory = self.repo / match.group("path").rstrip("/")
            return directory if directory.is_dir() else None
        name = match.group("name") or match.group("bare")
        if match.group("href"):
            name = match.group("href").rstrip("/").split("/")[-1]
        return self.slugs.get(name)


def resolves(cited: str, headings: list[tuple[int, str]], quoted: bool) -> bool:
    wanted = normalize(cited)
    if not wanted:
        return True
    names = [normalize(text) for _, text in headings]
    if quoted:
        return any(name.startswith(wanted) for name in names)
    for name in names:
        for form in {name, PARENTHETICAL.sub("", name)}:
            if form and wanted.startswith(form) and (len(wanted) == len(form) or not wanted[len(form)].isalnum()):
                return True
    label = LABEL.match(wanted)
    return bool(label) and any(re.match(re.escape(label.group(1)) + r"(?:[.\s)]|$)", name) for name in names)


def counterpart(headings_from, headings_to, cited: str, quoted: bool) -> str | None:
    """The heading at the same structural position in the other language, when both files align."""
    if [level for level, _ in headings_from] != [level for level, _ in headings_to]:
        return None
    for index, (_, text) in enumerate(headings_from):
        if resolves(cited, [(0, text)], quoted):
            return headings_to[index][1]
    return None


def section_findings(corpus: Corpus, path: Path, rel: str) -> list[Finding]:
    lang = path.stem
    siblings = sorted(p.stem for p in path.parent.glob("*.md") if LANG_FILE.match(p.stem))
    findings = []
    for number, line in markdown_lines(path):
        spans = [m.span() for m in CODE_SPAN.finditer(line)]
        for sign in re.finditer("§", line):
            start = sign.start()
            rest = line[start + 1:]
            if any(a <= start < b for a, b in spans) or not rest.strip():
                continue
            if re.match(r"\s\d", rest) or rest.startswith("`"):
                continue
            quoted = rest[0] in QUOTES
            if quoted:
                end = next((i for i in range(1, len(rest)) if rest[i] in QUOTES[rest[0]]), len(rest))
                cited = rest[1:end]
            else:
                cited = rest
            contract = AC_CONTRACT.get(lang)
            named = normalize(cited)
            if contract and any(named.startswith(v) for v in AC_VARIANTS if v != contract.casefold()):
                findings.append(Finding("heading-contract", rel, number,
                                        f"cite the acceptance-criteria section as §{contract}, not §{cited.strip()[:40]!r}"))
                continue
            earlier = [d for d in (corpus.spec_dir(m) for m in REFERENCE.finditer(line[:start])) if d]
            candidates = [path.parent] + earlier[-1:]
            if any(resolves(cited, corpus.headings(c / f"{lang}.md"), quoted) for c in candidates):
                continue
            label = cited.strip()[:60]
            for other in (s for s in siblings if s != lang):
                hit = next((c for c in reversed(candidates) if resolves(cited, corpus.headings(c / f"{other}.md"), quoted)), None)
                if hit is None:
                    continue
                target = hit.relative_to(corpus.repo).as_posix()
                suggestion = counterpart(corpus.headings(hit / f"{other}.md"), corpus.headings(hit / f"{lang}.md"), cited, quoted)
                hint = f"; the {lang} heading at that position is {suggestion!r}" if suggestion else ""
                findings.append(Finding("section-other-language", rel, number,
                                        f"§{label!r} resolves in {target}/{other}.md but not in {target}/{lang}.md{hint}"))
                break
            else:
                findings.append(Finding("section-unresolved", rel, number,
                                        f"§{label!r} resolves in no language of {', '.join(c.relative_to(corpus.repo).as_posix() for c in candidates)}"))
    return findings


def heading_findings(path: Path, rel: str) -> list[Finding]:
    expected = AC_CONTRACT.get(path.stem)
    if expected is None:
        return []
    return [
        Finding("heading-contract", rel, number, f"use '## {expected}' for the acceptance-criteria heading, not {line.strip()!r}")
        for number, line in markdown_lines(path)
        if line.startswith("## ") and line[3:].strip().casefold() in AC_VARIANTS and line[3:].strip() != expected
    ]


def path_findings(repo: Path, path: Path, rel: str) -> list[Finding]:
    plugins = sorted(p.name for p in (repo / "plugins").iterdir() if p.is_dir()) if (repo / "plugins").is_dir() else []
    own_plugin = rel.split("/")[1] if rel.startswith("plugins/") else None
    findings = []
    for number, line in markdown_lines(path):
        for match in ARTIFACT_PATH.finditer(line):
            cited = match.group(1).rstrip("/")
            if (repo / cited).exists():
                continue
            if own_plugin and (repo / "plugins" / own_plugin / cited).exists():
                continue  # relative to the plugin root the file lives in
            moved = [p for p in plugins if (repo / "plugins" / p / cited).exists()]
            if moved:
                findings.append(Finding("moved-artifact-path", rel, number,
                                        f"`{match.group(1)}` no longer exists at the root; it lives at `plugins/{moved[0]}/{match.group(1)}`"))
    return findings


def check(repo: Path) -> list[Finding]:
    corpus = Corpus(repo)
    findings: list[Finding] = []
    for path in sorted(repo.rglob("*.md")):
        rel = path.relative_to(repo).as_posix()
        if not rel.startswith(LIVE_DOCS):
            continue
        if rel.startswith("spec/") and LANG_FILE.match(path.stem):
            findings += section_findings(corpus, path, rel)
            findings += heading_findings(path, rel)
        findings += path_findings(repo, path, rel)
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--report", action="store_true", help="also list references that resolve in no language (never fails)")
    parser.add_argument("--repo", type=Path, default=REPO, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if not (args.repo / "spec").is_dir():
        print(f"usage: no spec/ directory under {args.repo}", file=sys.stderr)
        return 2

    findings = check(args.repo)
    blocking = [f for f in findings if f.blocking]
    for finding in blocking:
        print(finding)
    advisory = [f for f in findings if not f.blocking]
    if args.report:
        for finding in advisory:
            print(finding)
    if blocking:
        print(f"\nSection references: {len(blocking)} blocking finding(s). "
              "See spec/project/spec-readiness/en.md §Dimension 3.", file=sys.stderr)
        return 1
    print(f"Section references: pass ({len(advisory)} unresolved in any language, advisory"
          f"{'' if args.report else '; list them with --report'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
