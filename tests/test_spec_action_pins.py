"""Guard: every GitHub Action reference shown in a spec is pinned to a full commit digest.

spec/project/github-actions-best-practices/ §A requires a full-length commit digest with a
version comment for every action reference. A spec example that shows a tag is copied into
workflows as-is, so the examples are held to the same rule (#743).
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "spec"

# `uses: owner/repo[/path]@ref`, optionally quoted; local (`./`) and `docker://` references
# don't match because they lack the `owner/repo@` shape.
USES = re.compile(r"""uses:?`?\s*['"`]?([A-Za-z0-9_.-]+/[A-Za-z0-9_./-]+)@([^\s'"`#]+)""")
DIGEST = re.compile(r"[0-9a-f]{40}")


def unpinned(text: str) -> list[tuple[int, str]]:
    hits = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for match in USES.finditer(line):
            ref = match.group(2)
            # A placeholder such as `@<sha>` or `@${{ ... }}` is not a concrete reference.
            if ref[0] in "<${":
                continue
            if not DIGEST.fullmatch(ref):
                hits.append((lineno, match.group(0)))
    return hits


def test_detector_flags_a_tag_and_accepts_a_digest():
    assert unpinned("    uses: docker/metadata-action@v6\n") == [(1, "uses: docker/metadata-action@v6")]
    assert unpinned("    uses: owner/repo/.github/workflows/x.yaml@main\n")
    assert not unpinned(f"    uses: docker/metadata-action@{'a' * 40} # v6.2.0\n")
    assert not unpinned("    uses: owner/repo@<full-commit-sha> # vX.Y.Z\n")
    # Prose forms: inline code after `uses:`, and a code-spanned key.
    assert unpinned("Wire it with uses: `docker/metadata-action@v6`.\n")
    assert unpinned("The `uses:` `docker/metadata-action@v6` line\n")
    assert unpinned("    uses: owner/repo@_rel\n")


def test_every_spec_action_reference_is_digest_pinned():
    files = sorted(SPEC.rglob("*.md"))
    assert files, "no spec files found"
    found = [
        f"{path.relative_to(ROOT)}:{lineno}: {ref}"
        for path in files
        for lineno, ref in unpinned(path.read_text(encoding="utf-8"))
    ]
    assert not found, "tag- or branch-pinned action references in spec/:\n" + "\n".join(found)
