#!/usr/bin/env python3
"""Compute the LIX readability index for a Markdown file, EN or DE.

Reference implementation of `spec/project/readability-lix/`. Deliberately
**stdlib-only** so it runs in any consumer repository without a `pip install`,
mirroring the bundled-script convention of `skills/image-generate/scripts/`.
The `lektorat-scanner` agent invokes it through `${CLAUDE_PLUGIN_ROOT}` and
consumes its JSON output as the D1 readability finding evidence.

What it does, per the spec:
  - strips Markdown non-prose (fenced code, inline code, HTML comments, YAML
    frontmatter, link/image targets — visible link text is kept) so LIX
    reflects what a human reads;
  - segments sentences on `.`/`!`/`?` (and a colon that introduces an
    independent clause), guarding abbreviations and decimal/version numbers;
  - counts words (A), sentences (B), and long words (C = more than 6 Unicode
    letters, punctuation excluded, `ä ö ü ß` and accented letters counted);
  - computes the canonical LIX = A/B + (C * 100)/A, reported as an integer with
    `asl`/`lwp` and the raw A/B/C retained at full precision;
  - resolves the per-content-mode, per-language corridor (the German columns
    sit a fixed offset Δ = 5 above English) and the dominant lever.

The LIX value is computed from the **canonical** formula, never from a library
docstring (the widely used `textstat` ships a transposed, wrong docstring).

Exit codes:
  0  JSON written to stdout
  1  runtime error (unreadable file)
  2  usage error (bad/missing arguments — argparse default)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Bumped when the computation (stripping, segmentation, counting) changes in a
# way that can move a score; recorded in pipeline_metadata for reproducibility.
VERSION = "1.1.0"
LIBRARY = "nolte-readability-lix"
TOKENIZER = "builtin-unicode-regex"
LONG_WORD_THRESHOLD = 6  # a long word has MORE than 6 letters (7+)

# Per-content-mode, per-language corridors (aim / warn / crit), reproduced from
# spec/project/readability-lix/ §Target corridors. The DE columns are the EN
# columns plus the cross-language offset Δ = 5.
_GROUP_TUTORIAL = {"tutorial", "how-to", "troubleshooting"}
_GROUP_EXPLANATION = {"explanation", "reference", "glossary"}
CORRIDORS: dict[str, dict[str, dict[str, int]]] = {
    "en": {
        "tutorial": {"aim": 40, "warn": 45, "crit": 55},
        "explanation": {"aim": 50, "warn": 55, "crit": 65},
        "blog": {"aim": 45, "warn": 50, "crit": 55},
    },
    "de": {
        "tutorial": {"aim": 45, "warn": 50, "crit": 60},
        "explanation": {"aim": 55, "warn": 60, "crit": 70},
        "blog": {"aim": 50, "warn": 55, "crit": 60},
    },
}

# Abbreviations whose internal/trailing period must not end a sentence (EN + DE).
_ABBREVIATIONS = [
    "e.g.", "i.e.", "etc.", "cf.", "vs.", "al.", "Dr.", "Mr.", "Mrs.", "Ms.",
    "Prof.", "No.", "Nr.", "St.", "Jr.", "Sr.", "Inc.", "Ltd.", "ca.", "approx.",
    "z. B.", "z.B.", "d. h.", "d.h.", "u. a.", "u.a.", "usw.", "bzw.", "ggf.",
    "inkl.", "evtl.", "sog.", "Abb.", "Tab.", "Bd.", "Nr.", "vgl.",
]

_SENT = "\x00"  # placeholder for a period that must not split a sentence
_BREAK = "\x01"  # hard sentence boundary at a structural line end


def strip_markdown(text: str) -> str:
    """Reduce Markdown to the prose a human actually reads.

    Removes frontmatter, fenced code, HTML comments, and inline code; keeps the
    visible text of links while dropping their targets; drops images entirely;
    strips structural markers (headings, list bullets, blockquotes, table pipes)
    and emphasis runs so Markdown syntax never counts as words.
    """
    # YAML frontmatter at the very head of the file.
    text = re.sub(r"\A---\n.*?\n---\n", "\n", text, count=1, flags=re.S)
    # Fenced code blocks (``` or ~~~).
    text = re.sub(r"(?ms)^[ \t]*(```|~~~).*?^[ \t]*\1[ \t]*$", "\n", text)
    # HTML comments.
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    # Images: drop entirely (alt text is not body prose).
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
    # Inline-code spans.
    text = re.sub(r"`[^`]*`", " ", text)
    # Links: keep the visible text, drop the target.
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\[[^\]]*\]", r"\1", text)  # reference-style

    # Emoji / icon shortcodes (:name:) render as symbols, not prose.
    text = re.sub(r"(?<!\w):[a-z0-9_+-]+:(?!\w)", " ", text)

    out_lines: list[str] = []
    structural: list[bool] = []
    for line in text.split("\n"):
        stripped = line.strip()
        # Markdown table separator rows (| --- | --- |) carry no prose.
        if re.fullmatch(r"\|?[\s:|-]*\|[\s:|-]*\|?", stripped) and "-" in stripped:
            continue
        is_structural = bool(
            re.match(r"^[ \t]*#{1,6}[ \t]+", line)
            or re.match(r"^[ \t]*>[ \t]?\S", line)
            or re.match(r"^[ \t]*([-*+]|\d+\.)[ \t]+", line)
            or "|" in line
        )
        # Leading block markers: heading #, blockquote >, list bullets, table pipe.
        line = re.sub(r"^[ \t]*#{1,6}[ \t]+", "", line)
        line = re.sub(r"^[ \t]*>[ \t]?", "", line)
        line = re.sub(r"^[ \t]*([-*+]|\d+\.)[ \t]+", "", line)
        line = line.replace("|", " ")
        out_lines.append(line)
        structural.append(is_structural)

    # Structural boundaries terminate sentences (spec §Word and sentence
    # segmentation): a heading, list item, table row, or blockquote line ends a
    # sentence at its line end, and so does a paragraph break; flattened
    # structure must never concatenate into a synthetic sentence.
    terminated: list[str] = []
    for i, line in enumerate(out_lines):
        body = line.rstrip()
        core = body.rstrip("*_~ \t")
        ends_paragraph = i + 1 >= len(out_lines) or not out_lines[i + 1].strip()
        if core and (structural[i] or ends_paragraph) and core[-1] not in ".!?:;":
            body = body + "."
        terminated.append(body)
    text = "\n".join(terminated)

    # Emphasis / inline markers (keep the words, drop the punctuation).
    text = re.sub(r"[*_~]", "", text)
    return text


def _protect_non_boundaries(text: str) -> str:
    """Replace periods that must not end a sentence with a placeholder."""
    # Decimal and version numbers: the dot sits between digits.
    text = re.sub(r"(?<=\d)\.(?=\d)", _SENT, text)
    # Known abbreviations (longest first so "z. B." wins over "z.").
    for abbr in sorted(_ABBREVIATIONS, key=len, reverse=True):
        text = text.replace(abbr, abbr.replace(".", _SENT))
    return text


def split_sentences(text: str) -> list[str]:
    """Segment prose into sentences with abbreviation/number guards."""
    protected = _protect_non_boundaries(text)
    # A line break after terminal punctuation is a hard boundary (structural
    # lines are terminated in strip_markdown), regardless of what case the
    # next line starts with (spec §Word and sentence segmentation).
    protected = re.sub(r"(?<=[.!?;])[ \t]*\n\s*", _BREAK, protected)
    # A boundary is .!? — or a colon introducing an independent clause —
    # followed by whitespace and an opening uppercase letter/quote, or EOL.
    boundary = re.compile(r'([.!?]|:(?=\s+[A-ZÄÖÜ]))\s+(?=[A-ZÄÖÜ"\'(\[]|$)')
    pieces = boundary.split(protected)
    # re.split keeps the delimiter group; stitch delimiter back onto its clause.
    sentences: list[str] = []
    buf = ""
    for i, piece in enumerate(pieces):
        if i % 2 == 0:
            buf += piece
        else:
            buf += piece
            sentences.append(buf)
            buf = ""
    if buf.strip():
        sentences.append(buf)
    # Expand the hard structural boundaries collected above.
    expanded: list[str] = []
    for s in sentences:
        expanded.extend(part for part in s.split(_BREAK) if part.strip())
    # Trailing terminal punctuation with no following capital still ends the text.
    sentences = [s.replace(_SENT, ".").strip() for s in expanded if s.strip()]
    return sentences


_WORD_RE = re.compile(r"\S+")


def _letter_count(token: str) -> int:
    return sum(1 for ch in token if ch.isalpha())


def count_tokens(text: str) -> tuple[int, int]:
    """Return (A words, C long words). A token counts as a word when it carries
    at least one alphanumeric character; a long word has > 6 letters."""
    words = 0
    long_words = 0
    for raw in _WORD_RE.findall(text):
        # Strip leading/trailing punctuation so it never inflates the length.
        token = raw.strip("\"'()[]{}.,;:!?…—–-«»„“”‚’")
        if not any(ch.isalnum() for ch in token):
            continue
        words += 1
        if _letter_count(token) > LONG_WORD_THRESHOLD:
            long_words += 1
    return words, long_words


def _corridor_key(content_mode: str) -> str | None:
    if content_mode == "meta":
        return None
    if content_mode == "blog":
        return "blog"
    if content_mode in _GROUP_TUTORIAL:
        return "tutorial"
    if content_mode in _GROUP_EXPLANATION:
        return "explanation"
    # Unknown modes default to the denser explanation group.
    return "explanation"


def compute(text: str, language: str, content_mode: str) -> dict:
    """Compute the full LIX result for one document."""
    prose = strip_markdown(text)
    sentences = split_sentences(prose)
    sentence_count = max(1, len(sentences))
    words, long_words = count_tokens(prose)

    if words == 0:
        asl = 0.0
        lwp = 0.0
        lix = 0
    else:
        asl = words / sentence_count
        lwp = (long_words * 100) / words
        lix = round(asl + lwp)

    dominant_lever = "ASL" if asl >= lwp else "LWP"

    result: dict = {
        "lix": lix,
        "asl": round(asl, 2),
        "lwp": round(lwp, 2),
        "words": words,
        "sentences": sentence_count,
        "long_words": long_words,
        "dominant_lever": dominant_lever,
        "language": language,
        "content_mode": content_mode,
        "pipeline_metadata": {
            "library": LIBRARY,
            "library_version": VERSION,
            "tokenizer": TOKENIZER,
            "tokenizer_version": VERSION,
            "long_word_threshold": LONG_WORD_THRESHOLD,
        },
    }
    if language == "de":
        result["pipeline_metadata"]["decompounding"] = False

    key = _corridor_key(content_mode)
    if key is None:
        # meta pages are exempt from D1 per the spec.
        result["exempt"] = True
        result["corridor"] = None
        result["severity"] = "exempt"
        return result

    corridor = CORRIDORS[language][key]
    result["corridor"] = dict(corridor)
    if lix > corridor["crit"]:
        severity = "critical"
    elif lix > corridor["warn"]:
        severity = "warning"
    else:
        severity = "ok"
    result["severity"] = severity
    result["within_corridor"] = lix <= corridor["warn"]
    result["converged"] = lix <= corridor["aim"]
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compute the LIX readability index for a Markdown file (EN or DE).",
    )
    parser.add_argument(
        "--file", required=True,
        help="Path to the Markdown file, or '-' to read prose from stdin.",
    )
    parser.add_argument(
        "--language", required=True, choices=["en", "de"],
        help="Language whose corridor applies (drives the German offset).",
    )
    parser.add_argument(
        "--content-mode", required=True,
        choices=[
            "tutorial", "how-to", "troubleshooting",
            "explanation", "reference", "glossary",
            "blog", "meta",
        ],
        help="content_mode per spec/project/mkdocs-structure/ (meta is exempt).",
    )
    args = parser.parse_args(argv)

    if args.file == "-":
        text = sys.stdin.read()
    else:
        path = Path(args.file)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"readability_lix: cannot read {args.file}: {exc}", file=sys.stderr)
            return 1

    result = compute(text, args.language, args.content_mode)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
