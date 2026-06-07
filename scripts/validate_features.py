#!/usr/bin/env python3
"""Lightweight feature-file frontmatter validator.

Implements the structural checks named in `spec/project/feature/` §"Frontmatter
schema", §"Body sections", §"Acceptance-criteria contract", §"Consistency
check", and §"Directory layout and file shape" (the post-draft slug-rename
gate). This is the feature-side analogue of `scripts/validate_skills.py`.

Exit codes:
  0  every checked feature passes (0 files = pass)
  1  at least one error (`Critical`-grade per `review-plan` §Severity scale)
  2  internal error (file unreadable, YAML unrecoverable, etc.)

Usage:
  python scripts/validate_features.py                       # checks every feature
  python scripts/validate_features.py project/features/x.md # checks one target

Output is one finding per line, prefixed with severity in Title Case so
downstream tooling can grep deterministically.
"""
from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FEATURES_DIR = REPO / "project" / "features"

# Frontmatter schema per spec/project/feature/ §Frontmatter schema.
SCHEMA_ORDER = [
    "id", "title", "status", "roadmap_item", "sprint", "created",
    "ended", "verifies_sprint_value", "consistency_check",
]
SCHEMA_KEYS = set(SCHEMA_ORDER)
STATUS_ENUM = {"draft", "ready", "in_progress", "done", "cancelled"}
ID_RE = re.compile(r"^F-\d+$")
ROADMAP_RE = re.compile(r"^R-\d+$")
ACCEPTANCE_REF_RE = re.compile(r"^acceptance-\d+$")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SLUG_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")

# Body sections per spec/project/feature/ §Body sections, in declared order.
REQUIRED_SECTIONS = [
    "Description", "Acceptance criteria", "Test hooks",
    "Consistency notes", "Risks",
]

# Test-hook status vocabulary per §Body sections.
HOOK_STATUS = {"pending", "passing", "skipped", "failing"}
HOOK_RESOLVED = {"passing", "skipped"}

# Acceptance-criterion bullet: `- [ ] **acceptance-<n>** ...` (state x or space).
AC_BULLET_RE = re.compile(r"^- \[[ xX]\]\s+\*\*acceptance-(\d+)\*\*\s+\S")
# Test-hook entry header: `- **acceptance-<n>** — <mechanism> — <status>`.
# The entry MUST open with the `acceptance-<n>` pin; the mechanism and status
# follow after em-dash / hyphen separators. The status token MAY be wrapped in
# backticks and MAY be followed by a trailing parenthetical rationale, so it is
# matched as one of the closed-vocabulary tokens rather than positionally.
HOOK_PIN_RE = re.compile(r"^- \*\*acceptance-(\d+)\*\*\s+[—-]\s+(.+)$")

# consistency_check.findings finding kinds / resolutions per §Consistency check.
FINDING_KINDS = {"overlap", "duplication", "drift", "prior-art", "clean"}


@dataclass
class Finding:
    severity: str  # Critical | Warning | Suggestion | Info
    target: str
    rule: str
    message: str

    def __str__(self) -> str:
        return f"{self.severity:11s} {self.target}  [{self.rule}] {self.message}"


def _split(text: str) -> tuple[str, str] | None:
    """Return (frontmatter, body) or None when no `---` fence opens the file."""
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    return parts[1], parts[2]


def _top_level_keys(fm: str) -> list[str]:
    """Top-level frontmatter keys in document order (skip nested / list lines)."""
    keys: list[str] = []
    for line in fm.splitlines():
        if not line.strip() or line.startswith((" ", "\t", "-")):
            continue
        m = re.match(r"^([A-Za-z_][\w-]*):", line)
        if m:
            keys.append(m.group(1))
    return keys


def _scalar(fm: str, key: str) -> str | None:
    m = re.search(rf"^{re.escape(key)}:\s*(.*)$", fm, re.M)
    if not m:
        return None
    raw = m.group(1).strip()
    if raw.startswith(('"', "'")) and raw.endswith(('"', "'")) and len(raw) >= 2:
        raw = raw[1:-1]
    return raw


def check_slug(path: Path, target: str) -> list[Finding]:
    slug = path.stem
    if not SLUG_RE.match(slug):
        return [Finding("Critical", target, "feature.slug-charset",
                        f"slug `{slug}` is not ASCII kebab-case")]
    if len(slug.split("-")) > 6:
        return [Finding("Warning", target, "feature.slug-length",
                        f"slug `{slug}` exceeds the ≤ 6-word readability target")]
    return []


def check_frontmatter(fm: str, target: str) -> tuple[list[Finding], dict]:
    findings: list[Finding] = []
    scalars: dict = {}

    keys = _top_level_keys(fm)
    present = [k for k in keys if k in SCHEMA_KEYS]

    # `closed` was the rejected name for `ended` — flag it explicitly.
    if "closed" in keys:
        findings.append(Finding("Critical", target, "feature.frontmatter-rejected-key",
                                "`closed` is not a valid frontmatter field; the field is named `ended`"))

    for key in SCHEMA_ORDER:
        if key not in keys:
            findings.append(Finding("Critical", target, "feature.frontmatter-missing-field",
                                    f"required frontmatter field `{key}` is missing"))

    unknown = [k for k in keys if k not in SCHEMA_KEYS and k != "closed"]
    for k in unknown:
        findings.append(Finding("Critical", target, "feature.frontmatter-unknown-key",
                                f"unknown frontmatter key `{k}`; only the nine schema fields are allowed"))

    # Order check (only over schema keys that are actually present).
    expected_order = [k for k in SCHEMA_ORDER if k in present]
    if present != expected_order:
        findings.append(Finding("Critical", target, "feature.frontmatter-field-order",
                                f"frontmatter fields out of declared order: got {present}, expected {expected_order}"))

    fid = _scalar(fm, "id")
    scalars["id"] = fid
    if fid is not None and not ID_RE.match(fid):
        findings.append(Finding("Critical", target, "feature.id-pattern",
                                f"`id` `{fid}` does not match the `F-<n>` pattern"))

    title = _scalar(fm, "title")
    if title is not None and not title.strip():
        findings.append(Finding("Critical", target, "feature.title-empty",
                                "`title` is empty"))

    status = _scalar(fm, "status")
    scalars["status"] = status
    if status is not None and status not in STATUS_ENUM:
        findings.append(Finding("Critical", target, "feature.status-enum",
                                f"`status` `{status}` is not in {sorted(STATUS_ENUM)}"))

    roadmap = _scalar(fm, "roadmap_item")
    if roadmap is not None and not ROADMAP_RE.match(roadmap):
        findings.append(Finding("Critical", target, "feature.roadmap-item-pattern",
                                f"`roadmap_item` `{roadmap}` does not match the `R-<n>` pattern"))

    sprint = _scalar(fm, "sprint")
    if sprint is not None and sprint != "null" and not re.fullmatch(r"\d+", sprint):
        findings.append(Finding("Critical", target, "feature.sprint-type",
                                f"`sprint` must be an integer or `null`, got `{sprint}`"))

    created = _scalar(fm, "created")
    if created is not None and not ISO_DATE_RE.match(created):
        findings.append(Finding("Critical", target, "feature.created-date",
                                f"`created` `{created}` is not an ISO date (YYYY-MM-DD)"))

    ended = _scalar(fm, "ended")
    if ended is not None and ended != "null" and not ISO_DATE_RE.match(ended):
        findings.append(Finding("Critical", target, "feature.ended-date",
                                f"`ended` must be an ISO date or `null`, got `{ended}`"))

    vsv = _scalar(fm, "verifies_sprint_value")
    if vsv is not None and vsv != "null" and not ACCEPTANCE_REF_RE.match(vsv):
        findings.append(Finding("Critical", target, "feature.verifies-sprint-value-pattern",
                                f"`verifies_sprint_value` must be `acceptance-<n>` or `null`, got `{vsv}`"))

    # consistency_check object must carry performed_at + a non-empty findings list.
    cc_block = re.search(r"^consistency_check:\s*\n((?:[ \t]+.*\n?)+)", fm, re.M)
    if cc_block:
        block = cc_block.group(1)
        if "performed_at:" not in block:
            findings.append(Finding("Critical", target, "feature.consistency-check-performed-at",
                                    "`consistency_check` is missing the required `performed_at` field"))
        finding_kinds = re.findall(r"kind:\s*([a-z-]+)", block)
        if not finding_kinds:
            findings.append(Finding("Critical", target, "feature.consistency-check-findings-empty",
                                    "`consistency_check.findings` is empty; a clean run still records `kind: clean`"))
        for k in finding_kinds:
            if k not in FINDING_KINDS:
                findings.append(Finding("Critical", target, "feature.consistency-check-finding-kind",
                                        f"finding `kind: {k}` is not in {sorted(FINDING_KINDS)}"))

    return findings, scalars


def check_body(body: str, target: str) -> list[Finding]:
    findings: list[Finding] = []
    headings = re.findall(r"^##\s+(.+?)\s*$", body, re.M)

    present_required = [h for h in headings if h in REQUIRED_SECTIONS]
    for sec in REQUIRED_SECTIONS:
        if sec not in headings:
            findings.append(Finding("Critical", target, "feature.body-section-missing",
                                    f"required `## {sec}` section is missing"))
    expected = [s for s in REQUIRED_SECTIONS if s in present_required]
    if present_required != expected:
        findings.append(Finding("Critical", target, "feature.body-section-order",
                                f"required sections out of declared order: got {present_required}, expected {expected}"))

    # Acceptance-criteria bullets.
    lines = body.splitlines()
    ac_ids: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- [") and "acceptance-" in stripped:
            m = AC_BULLET_RE.match(stripped)
            if m:
                ac_ids.append(f"acceptance-{m.group(1)}")
            elif re.match(r"^- \[[ xX]\]", stripped):
                findings.append(Finding("Critical", target, "feature.acceptance-bullet-shape",
                                        f"acceptance bullet does not match `- [ ] **acceptance-<n>** ...`: {stripped[:60]!r}"))

    if not ac_ids:
        findings.append(Finding("Critical", target, "feature.acceptance-none",
                                "no `**acceptance-<n>**` criterion bullets found"))

    # Test-hook entries: parse the `## Test hooks` section only. Each entry
    # MUST carry three components per §Body sections: (a) the `acceptance-<n>`
    # pin, (b) a verification mechanism, (c) a closed-vocabulary status token.
    hooks_section = _section_body(body, "Test hooks")
    for line in _coalesce_bullets(hooks_section):
        m = HOOK_PIN_RE.match(line)
        if not m:
            findings.append(Finding("Critical", target, "feature.test-hook-shape",
                                    f"test-hook entry does not match `- **acceptance-<n>** — <mechanism> — <status>`: {line[:70]!r}"))
            continue
        rest = m.group(2)
        tokens = set(re.findall(r"`?\b([a-z]+)\b`?", rest))
        status_tokens = tokens & HOOK_STATUS
        if not status_tokens:
            findings.append(Finding("Critical", target, "feature.test-hook-status",
                                    f"test-hook entry carries no status token from {sorted(HOOK_STATUS)}: {line[:70]!r}"))

    return findings


def _coalesce_bullets(section: str) -> list[str]:
    """Join soft-wrapped continuation lines into one logical bullet each.

    A markdown bullet (`- ...`) may wrap across several physical lines that are
    indented under it; the test-hook contract is evaluated per logical bullet.
    """
    bullets: list[str] = []
    current: str | None = None
    for raw in section.splitlines():
        stripped = raw.strip()
        if stripped.startswith("- "):
            if current is not None:
                bullets.append(current)
            current = stripped
        elif current is not None and (raw.startswith((" ", "\t")) and stripped):
            current += " " + stripped
        elif not stripped:
            continue
    if current is not None:
        bullets.append(current)
    return bullets


def _section_body(body: str, heading: str) -> str:
    m = re.search(rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s+|\Z)",
                  body, re.M | re.S)
    return m.group(1) if m else ""


def check_feature(path: Path) -> list[Finding]:
    rel = path.relative_to(REPO).as_posix()
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:  # pragma: no cover
        return [Finding("Critical", rel, "feature.unreadable", str(exc))]
    split = _split(text)
    if split is None:
        return [Finding("Critical", rel, "feature.frontmatter-missing", "no YAML frontmatter fence")]
    fm, body = split
    findings = check_slug(path, rel)
    fm_findings, _ = check_frontmatter(fm, rel)
    findings += fm_findings
    findings += check_body(body, rel)
    return findings


def _git(*args: str) -> str:
    try:
        return subprocess.run(
            ["git", *args], cwd=REPO, capture_output=True, text=True, check=False
        ).stdout
    except OSError:  # pragma: no cover - git missing
        return ""


def check_slug_rename_gate() -> list[Finding]:
    """Flag a staged rename of a feature whose old file was past `draft`.

    Per spec/project/feature/ §Directory layout: a slug MUST NOT be renamed
    after the feature leaves `draft`; renames silently break sprint and roadmap
    back-references. We read the *old* path's content from the index/HEAD to
    determine the pre-rename status; only renames of post-draft features are
    blockers.
    """
    findings: list[Finding] = []
    out = _git("diff", "--cached", "--name-status", "-M", "--", "project/features/")
    for line in out.splitlines():
        parts = line.split("\t")
        if not parts or not parts[0].startswith("R"):
            continue
        if len(parts) < 3:
            continue
        old_path, new_path = parts[1], parts[2]
        old_content = _git("show", f":{old_path}") or _git("show", f"HEAD:{old_path}")
        status = _scalar(old_content.split("---", 2)[1], "status") if old_content.startswith("---") else None
        if status and status != "draft":
            findings.append(Finding(
                "Critical", new_path, "feature.slug-rename-gate",
                f"feature slug renamed from `{Path(old_path).stem}` to `{Path(new_path).stem}` "
                f"while status is `{status}` (not `draft`); renaming a post-draft slug breaks "
                f"sprint/roadmap back-references (spec/project/feature/ §Directory layout)",
            ))
    return findings


def main() -> int:
    args = sys.argv[1:]
    if args:
        paths = [REPO / a for a in args]
        for p in paths:
            if not p.exists():
                print(f"ERROR: path not found: {p}", file=sys.stderr)
                return 2
    elif FEATURES_DIR.is_dir():
        paths = sorted(FEATURES_DIR.glob("*.md"))
    else:
        paths = []

    all_findings: list[Finding] = []
    for path in paths:
        if path.suffix != ".md":
            continue
        all_findings.extend(check_feature(path))

    # Slug-rename gate runs against the git index whenever the working tree
    # is a git repo; it is a no-op outside one or with no staged renames.
    if (REPO / ".git").exists():
        all_findings.extend(check_slug_rename_gate())

    n = len([p for p in paths if p.suffix == ".md"])
    if not all_findings:
        print(f"validate_features: {n} feature file(s) checked, no findings")
        return 0

    by_severity = {"Critical": 0, "Warning": 0, "Suggestion": 0, "Info": 0}
    for f in all_findings:
        by_severity[f.severity] = by_severity.get(f.severity, 0) + 1
        print(f)

    print(
        f"\nvalidate_features: {n} feature file(s); "
        f"{by_severity['Critical']}C / {by_severity['Warning']}W / "
        f"{by_severity['Suggestion']}S / {by_severity['Info']}I",
        file=sys.stderr,
    )
    return 1 if by_severity["Critical"] else 0


if __name__ == "__main__":
    sys.exit(main())
