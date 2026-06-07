#!/usr/bin/env python3
"""Lightweight skill / agent frontmatter validator.

Implements the structural checks named in `spec/claude/skill-management/`
§"Frontmatter validation" and `spec/claude/agent-management/` §Structure.
This is a stop-gap for the upstream `skills-ref` CLI mentioned in
`spec/claude/skill-review/` §"Checks derived from external skill-structure
validation"; once an official binary ships under `anthropics/skills`, this
script can be retired.

Exit codes:
  0  every checked artifact passes
  1  at least one error (`Critical`-grade per `review-plan` §Severity scale)
  2  internal error (file unreadable, YAML unrecoverable, etc.)

Usage:
  python scripts/validate_skills.py              # checks every skill + agent
  python scripts/validate_skills.py skills/foo/  # checks one target

Output is one finding per line, prefixed with severity in Title Case so
downstream tooling can grep deterministically.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

STARTER_TAGS = {
    "pull-request", "review", "audit", "scaffolding", "prose",
    "audience", "release", "quality-gate", "dependency",
}
RESERVED_TOKENS = {"anthropic", "claude"}
GENERIC_NAMES = {"helper", "utils", "tools", "documents", "data", "files"}
NAME_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
DOUBLE_HYPHEN_RE = re.compile(r"--")
# Match only HTML-shaped tags that the upstream Anthropic platform validator
# rejects: a known HTML-element name (lowercased) optionally followed by
# attributes. Spec-placeholder tokens like `<n>`, `<slug>`, `<topic>`,
# `<canonical_language>` use angle brackets but are documented placeholder
# notation, not XML; the upstream validator accepts them.
HTML_TAG_NAMES = {
    "a", "abbr", "address", "area", "article", "aside", "audio", "b", "base",
    "bdi", "bdo", "blockquote", "body", "br", "button", "canvas", "caption",
    "cite", "code", "col", "colgroup", "data", "datalist", "dd", "del",
    "details", "dfn", "dialog", "div", "dl", "dt", "em", "embed", "fieldset",
    "figcaption", "figure", "footer", "form", "h1", "h2", "h3", "h4", "h5",
    "h6", "head", "header", "hr", "html", "i", "iframe", "img", "input",
    "ins", "kbd", "label", "legend", "li", "link", "main", "map", "mark",
    "menu", "meta", "meter", "nav", "noscript", "object", "ol", "optgroup",
    "option", "output", "p", "param", "picture", "pre", "progress", "q",
    "rp", "rt", "ruby", "s", "samp", "script", "section", "select", "small",
    "source", "span", "strong", "style", "sub", "summary", "sup", "svg",
    "table", "tbody", "td", "template", "textarea", "tfoot", "th", "thead",
    "time", "title", "tr", "track", "u", "ul", "var", "video", "wbr",
}
XML_TAG_RE = re.compile(r"<(/?)([a-z][a-z0-9]*)(\s[^>]*)?/?>")
FORBIDDEN_PRONOUNS_RE = re.compile(r"\b(I|you|your|yours|yourself|we|our|ours|us)\b")

# Strip text inside double-quoted spans (`"..."`) before applying the
# third-person check. Quoted spans are user-trigger phrases or sample
# operator-voice quotes, not author voice; the spec rule bans first /
# second person in *author voice* only (per
# `agentskills.io/skill-creation/best-practices`).
QUOTED_SPAN_RE = re.compile(r'"[^"]*"')


@dataclass
class Finding:
    severity: str  # Critical | Warning | Suggestion | Info
    target: str
    rule: str
    message: str

    def __str__(self) -> str:
        return f"{self.severity:11s} {self.target}  [{self.rule}] {self.message}"


def parse_frontmatter(text: str) -> dict | None:
    """Return a dict of frontmatter scalars, or None when no `---` block exists.

    Hand-rolled to avoid yaml.safe_load tripping on `: ` inside unquoted
    description values. Only handles the keys this validator needs:
    `name`, `description`, `tags`, `distribution`, `tools`, `model`,
    `when_to_use`, `phase`. Block scalars (`>-`) are folded.
    """
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    fm = parts[1]
    out: dict = {}

    # description / name / distribution / model / when_to_use / phase are scalar
    for key in ("name", "description", "distribution", "model", "when_to_use", "phase", "resumable"):
        m = re.search(
            rf'^{key}:\s*(.+?)(?=\n[a-z_-]+:\s|\n---|\Z)',
            fm, re.M | re.S,
        )
        if not m:
            continue
        raw = m.group(1).strip()
        if raw.startswith('"') and raw.endswith('"'):
            raw = raw[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        elif raw.startswith("'") and raw.endswith("'"):
            raw = raw[1:-1]
        elif raw.startswith(">-"):
            body = raw.split("\n", 1)[1] if "\n" in raw else ""
            raw = re.sub(r"\n\s+", " ", body).strip()
        out[key] = raw

    # tags: [..] inline OR multi-line
    m = re.search(r"^tags:\s*\[([^\]]*)\]", fm, re.M)
    if m:
        out["tags"] = [t.strip().strip('"').strip("'") for t in m.group(1).split(",") if t.strip()]
    else:
        m2 = re.search(r"^tags:\s*\n((?:\s+- .+\n)+)", fm, re.M)
        if m2:
            out["tags"] = [
                line.strip().lstrip("- ").strip()
                for line in m2.group(1).split("\n") if line.strip()
            ]

    # tools: comma list OR multi-line
    m = re.search(r"^tools:\s*(.+)$", fm, re.M)
    if m:
        out["tools"] = [t.strip() for t in m.group(1).split(",") if t.strip()]

    return out


def check_name(name: str | None, target: str, kind: str, expected_basename: str, body: str = "") -> list[Finding]:
    findings: list[Finding] = []
    if not name:
        findings.append(Finding("Critical", target, f"{kind}-management.frontmatter-name-missing",
                                "frontmatter `name` is missing"))
        return findings
    if not (1 <= len(name) <= 64):
        findings.append(Finding("Critical", target, f"{kind}-management.frontmatter-name-length",
                                f"`name` length {len(name)} is outside the 1–64 character range"))
    if not NAME_RE.match(name):
        findings.append(Finding("Critical", target, f"{kind}-management.frontmatter-name-charset",
                                f"`name` `{name}` contains characters outside lowercase ASCII letters, digits, and hyphens, or starts/ends with `-`"))
    if DOUBLE_HYPHEN_RE.search(name):
        findings.append(Finding("Critical", target, f"{kind}-management.frontmatter-name-double-hyphen",
                                f"`name` `{name}` contains consecutive hyphens"))
    if any(t in name.lower() for t in RESERVED_TOKENS):
        # Narrow exception per `skill-management` §Frontmatter validation /
        # `agent-management` §Structure: artefacts whose primary
        # responsibility targets the Claude / Anthropic platform surface
        # MAY waive the ban when the body carries a
        # `## Reserved-token rationale` section.
        if "## Reserved-token rationale" in body:
            findings.append(Finding("Info", target, f"{kind}-management.frontmatter-name-reserved-exception",
                                    f"`name` `{name}` contains a reserved token; exception accepted via `## Reserved-token rationale` section in body"))
        else:
            findings.append(Finding("Critical", target, f"{kind}-management.frontmatter-name-reserved",
                                    f"`name` `{name}` contains a reserved token (`anthropic` / `claude`)"))
    if name.lower() in GENERIC_NAMES:
        findings.append(Finding("Critical", target, f"{kind}-management.frontmatter-name-generic",
                                f"`name` `{name}` is in the generic-names blocklist (defeats discovery)"))
    if name != expected_basename:
        findings.append(Finding("Critical", target, f"{kind}-management.frontmatter-name-filename",
                                f"`name` `{name}` does not match expected basename `{expected_basename}`"))
    return findings


def check_description(desc: str | None, target: str, kind: str) -> list[Finding]:
    findings: list[Finding] = []
    if desc is None:
        findings.append(Finding("Critical", target, f"{kind}-management.frontmatter-description-missing",
                                "frontmatter `description` is missing"))
        return findings
    if len(desc) == 0:
        findings.append(Finding("Critical", target, f"{kind}-management.frontmatter-description-empty",
                                "frontmatter `description` is empty"))
    if len(desc) > 1024:
        findings.append(Finding("Critical", target, f"{kind}-management.frontmatter-description-cap",
                                f"`description` length {len(desc)} exceeds the 1024-character platform cap"))
    for m in XML_TAG_RE.finditer(desc):
        if m.group(2) in HTML_TAG_NAMES:
            findings.append(Finding("Critical", target, f"{kind}-management.frontmatter-description-xml",
                                    f"`description` contains an HTML tag (`{m.group(0)}`)"))
            break  # one finding per description is enough
    # Apply the third-person check on author-voice text only: strip every
    # double-quoted span (operator-voice trigger phrases, sample requests)
    # before the search so quoted `I`/`you`/`our` does not fire.
    author_voice = QUOTED_SPAN_RE.sub(" ", desc)
    pron_match = FORBIDDEN_PRONOUNS_RE.search(author_voice)
    if pron_match:
        findings.append(Finding("Critical", target, f"{kind}-management.frontmatter-description-third-person",
                                f"`description` contains the non-third-person token `{pron_match.group(0)}` in author voice"))
    return findings


def check_tags(tags: list[str] | None, target: str, kind: str) -> list[Finding]:
    findings: list[Finding] = []
    if tags is None:
        if kind == "agent":
            findings.append(Finding("Suggestion", target, f"{kind}-management.frontmatter-tags-missing",
                                    "no `tags` field; consider adding 1–2 starter-vocabulary tags"))
        return findings
    if len(tags) > 5:
        findings.append(Finding("Critical", target, f"{kind}-management.frontmatter-tags-too-many",
                                f"`tags` contains {len(tags)} entries; max 5"))
    for t in tags:
        if len(t) > 30:
            findings.append(Finding("Critical", target, f"{kind}-management.frontmatter-tags-length",
                                    f"tag `{t}` is {len(t)} chars; max 30"))
        if not NAME_RE.match(t):
            findings.append(Finding("Critical", target, f"{kind}-management.frontmatter-tags-charset",
                                    f"tag `{t}` is not lowercase ASCII kebab-case"))
    out_of_starter = [t for t in tags if t not in STARTER_TAGS]
    if out_of_starter:
        findings.append(Finding("Warning", target, f"{kind}-management.tag-vocabulary",
                                f"tags outside the starter vocabulary: {out_of_starter}"))
    return findings


def check_when_to_use(desc: str | None, when_to_use: str | None, target: str, kind: str) -> list[Finding]:
    if not when_to_use or not desc:
        return []
    if len(desc) + len(when_to_use) > 1536:
        return [Finding("Warning", target, f"{kind}-management.frontmatter-when-to-use-cap",
                        f"`description` + `when_to_use` combined length {len(desc) + len(when_to_use)} exceeds 1536-char runtime cap")]
    return []


def check_distribution(distribution: str | None, target: str) -> list[Finding]:
    if distribution is None:
        return [Finding("Critical", target, "agent-management.frontmatter-distribution-missing",
                        "agent has no `distribution` field; must be exactly `plugin` or `project`")]
    if distribution not in ("plugin", "project"):
        return [Finding("Critical", target, "agent-management.frontmatter-distribution-value",
                        f"`distribution` is `{distribution}`; must be exactly `plugin` or `project`")]
    return []


# Closed phase vocabulary per spec/claude/skill-agent-catalog/ §Phase classification.
PHASE_VOCABULARY = frozenset({
    "vision", "plan", "design", "build", "review", "quality", "close-release", "cross-cutting",
})


def check_phase(phase: str | None, target: str, kind: str) -> list[Finding]:
    if phase is None or phase == "":
        return [Finding("Critical", target, f"{kind}-management.frontmatter-phase-missing",
                        f"frontmatter `phase` is missing; expected one of {sorted(PHASE_VOCABULARY)}")]
    if phase not in PHASE_VOCABULARY:
        return [Finding("Critical", target, f"{kind}-management.frontmatter-phase-value",
                        f"`phase` value `{phase}` is not in the closed vocabulary {sorted(PHASE_VOCABULARY)}")]
    return []


def _split_body(text: str) -> str:
    """Return the markdown body (everything after the closing `---` of the frontmatter)."""
    parts = text.split("---", 2)
    return parts[2] if len(parts) >= 3 else text


def check_resumable_wiring(
    resumable: str | None,
    description: str | None,
    name: str | None,
    body: str,
    target: str,
    kind: str,
) -> list[Finding]:
    """Guard the resume contract from spec/claude/resumable-work/.

    A `resumable: true` declaration that the body never backs with a concrete
    `.resume/<name>/` checkpoint instruction is exactly the failure that left the
    convention inert (41 skills declared it, zero ever wrote a file). This is the
    static, regression-catching slice: it cannot prove a checkpoint *fires* at
    runtime (the spec notes that has no post-hoc observable — that is the
    behavioural eval's job), but it refuses a flag with no wiring behind it.
    """
    findings: list[Finding] = []
    if (resumable or "").strip().lower() != "true":
        return findings

    expected_path = f".resume/{name}/" if name else ".resume/"
    if expected_path not in body and ".resume/" not in body:
        findings.append(Finding(
            "Critical", target, f"{kind}-management.resumable-no-persistence",
            f"frontmatter declares `resumable: true` but the body never references "
            f"`{expected_path}` per spec/claude/resumable-work/ §Persistence location",
        ))

    if "resume" not in (description or "").lower():
        findings.append(Finding(
            "Critical", target, f"{kind}-management.resumable-description-silent",
            "`resumable: true` requires a resume clause in `description` "
            "(spec/claude/resumable-work/ §Scope of applicability)",
        ))

    if not re.search(r"start-new|discard|resume detection|on re-invocation", body, re.I):
        findings.append(Finding(
            "Warning", target, f"{kind}-management.resumable-no-detection",
            "`resumable: true` body has no resume-detection step "
            "(expected `resume / start-new / discard` prompt on re-invocation)",
        ))
    return findings


def check_skill(path: Path) -> list[Finding]:
    rel = path.relative_to(REPO).as_posix()
    text = path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    if fm is None:
        return [Finding("Critical", rel, "skill-management.frontmatter-missing", "no YAML frontmatter")]
    expected_name = path.parent.name
    body = _split_body(text)
    findings = []
    findings += check_name(fm.get("name"), rel, "skill", expected_name, body)
    findings += check_description(fm.get("description"), rel, "skill")
    findings += check_tags(fm.get("tags"), rel, "skill")
    findings += check_phase(fm.get("phase"), rel, "skill")
    findings += check_when_to_use(fm.get("description"), fm.get("when_to_use"), rel, "skill")
    findings += check_resumable_wiring(
        fm.get("resumable"), fm.get("description"), fm.get("name"), body, rel, "skill")
    return findings


def check_agent(path: Path) -> list[Finding]:
    rel = path.relative_to(REPO).as_posix()
    text = path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    if fm is None:
        return [Finding("Critical", rel, "agent-management.frontmatter-missing", "no YAML frontmatter")]
    expected_name = path.stem
    body = _split_body(text)
    findings = []
    findings += check_name(fm.get("name"), rel, "agent", expected_name, body)
    findings += check_description(fm.get("description"), rel, "agent")
    findings += check_tags(fm.get("tags"), rel, "agent")
    findings += check_distribution(fm.get("distribution"), rel)
    findings += check_phase(fm.get("phase"), rel, "agent")
    findings += check_resumable_wiring(
        fm.get("resumable"), fm.get("description"), fm.get("name"), body, rel, "agent")
    return findings


def check_agent_tree(agents_dir: Path) -> list[Finding]:
    """Flag any markdown nested under `agents/<name>/`.

    Per `spec/claude/agent-management/` §Structure an agent is exactly one
    top-level file `agents/<name>.md`. Claude Code's default agent discovery
    scans `agents/` *recursively*, so a companion markdown file in a sibling
    folder is registered as a phantom, scope-prefixed agent (`<name>:<file>`)
    that — lacking frontmatter — inherits the full tool surface with no `tools`
    restriction. Supporting assets that cannot be inlined live outside the
    `agents/` tree (for example `agent-assets/<name>/`).
    """
    findings: list[Finding] = []
    for md in sorted(agents_dir.rglob("*.md")):
        if md.parent == agents_dir:
            continue  # top-level agent file — the only legitimate shape
        rel = md.relative_to(REPO).as_posix()
        findings.append(Finding(
            "Critical", rel, "agent-management.nested-companion-markdown",
            "markdown nested under agents/ is registered as a phantom all-tools "
            "agent by recursive discovery; inline it into the agent body or move "
            "it outside the agents/ tree (agent-management §Structure)",
        ))
    return findings


def main() -> int:
    targets = sys.argv[1:] or ["skills/", "agents/"]
    paths: list[Path] = []
    for t in targets:
        p = REPO / t
        if not p.exists():
            print(f"ERROR: path not found: {p}", file=sys.stderr)
            return 2
        if p.is_dir():
            if "skills" in p.parts:
                paths.extend(sorted(p.rglob("SKILL.md")))
            elif "agents" in p.parts:
                paths.extend(sorted(p.glob("*.md")))
            else:
                paths.extend(sorted(p.rglob("SKILL.md")))
                paths.extend(sorted(p.glob("*.md")))
        else:
            paths.append(p)

    all_findings: list[Finding] = []
    for path in paths:
        rel = path.relative_to(REPO).as_posix()
        if rel.startswith("skills/") and path.name == "SKILL.md":
            all_findings.extend(check_skill(path))
        elif rel.startswith("agents/") and path.suffix == ".md":
            all_findings.extend(check_agent(path))

    # Phantom-agent leak scan: only the top-level `agents/*.md` glob above visits
    # legitimate agents, so nested companion markdown would slip through. Run the
    # recursive tree check whenever the agents/ directory is in scope.
    agents_dir = REPO / "agents"
    scope_includes_agents = any(
        (REPO / t).resolve() in (agents_dir.resolve(), REPO.resolve()) for t in targets
    )
    if scope_includes_agents and agents_dir.is_dir():
        all_findings.extend(check_agent_tree(agents_dir))

    if not all_findings:
        print(f"validate_skills: {len(paths)} artifacts checked, no findings")
        return 0

    by_severity = {"Critical": 0, "Warning": 0, "Suggestion": 0, "Info": 0}
    for f in all_findings:
        by_severity[f.severity] = by_severity.get(f.severity, 0) + 1
        print(f)

    print(
        f"\nvalidate_skills: {len(paths)} artifacts; "
        f"{by_severity['Critical']}C / {by_severity['Warning']}W / "
        f"{by_severity['Suggestion']}S / {by_severity['Info']}I",
        file=sys.stderr,
    )
    return 1 if by_severity["Critical"] else 0


if __name__ == "__main__":
    sys.exit(main())
