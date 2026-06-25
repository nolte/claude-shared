#!/usr/bin/env python3
"""Local-vs-inherited spec drift check.

Operationalises the CI-enforcement MUST of
`spec/project/portfolio-inherited-spec-layer/` §"Audit and CI integration":
"undeclared divergence MUST be a CI error ... the Local-vs-Inherited drift pass
ends with non-zero exit on any open Critical." The schema validator
(`validate_schemas.py`) already hard-fails the PARSE class of a malformed
`inherits:` block; this script adds the SEMANTIC class the schema deliberately
leaves to the drift check (§"Drift detection").

It composes with — does not replace — the `spec` skill's interactive
Local-vs-Inherited pass (`skills/spec/SKILL.md` §"Local-vs-inherited drift");
this is the automated, non-interactive CI gate.

Resolution. The inherited corpus is read from the installed hub plugin's
bundled `spec/` payload at the consumer's pinned `ref`, i.e.
`${CLAUDE_PLUGIN_ROOT}/spec/` per the spec's §"Tooling and enforcement". For
local runs and tests an explicit `--hub-spec-root <path>` overrides that. When
neither is available the content-dependent checks are skipped with a Warning;
the structural checks (tag-pinned ref, non-empty reason, declared override file
present) still run.

On the hub itself (`spec/.spec-config.yml` carries no `inherits:`) there is
nothing to inherit: the script validates that every local `Portfolio-Scope:`
header is well-formed and exits 0.

Exit codes:
  0  no Critical findings
  1  at least one Critical finding (per `review-plan` §Severity scale)
  2  internal error (config unreadable, YAML unrecoverable, etc.)

Usage:
  python3 scripts/check_spec_inheritance.py
  python3 scripts/check_spec_inheritance.py --repo path/to/consumer --hub-spec-root path/to/hub/spec

Output is one finding per line, prefixed with severity in Title Case so
downstream tooling can grep deterministically.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - environment guard
    print("Critical    .spec-config.yml  [internal] PyYAML is required", file=sys.stderr)
    sys.exit(2)

REPO = Path(__file__).resolve().parent.parent

# A tag-pinned ref looks like a release tag (v1.2.3 / 1.2.3), never a floating
# branch name. §"The inheritance manifest": a floating or absent ref is Warning.
TAG_REF_RE = re.compile(r"^v?\d+\.\d+\.\d+")
SCOPE_RE = re.compile(r"^Portfolio-Scope:\s*(.+?)\s*$", re.M)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$", re.M)
# Cross-reference form the corpus uses: spec/<topic>/<slug>/ (one nesting level).
CROSSREF_RE = re.compile(r"spec/([a-z0-9][a-z0-9-]*)/([a-z0-9][a-z0-9-]*)/")
# Markdown heading anchors (`## Title {#id}`) are stripped before matching a §Section.
ANCHOR_RE = re.compile(r"\s*\{#[^}]*\}\s*$")
VALID_SCOPES = {"portfolio", "local"}
# Top-level directories under spec/ that are not spec topics; excluded from both
# the resolvable spec set and the cross-reference namespace so a prose reference
# to e.g. spec/schemas/ is not mistaken for a ghost reference.
EXCLUDED_TOPICS = {"schemas"}


@dataclass
class Finding:
    severity: str  # Critical | Warning | Suggestion | Info
    target: str
    rule: str
    message: str

    def __str__(self) -> str:
        return f"{self.severity:11s} {self.target}  [{self.rule}] {self.message}"


# --- parsing helpers -------------------------------------------------------

def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def portfolio_scope(text: str) -> str:
    """The declared Portfolio-Scope of a canonical spec; default 'local'."""
    m = SCOPE_RE.search(text)
    return m.group(1).strip() if m else "local"


def collect_specs(spec_root: Path, lang: str) -> dict[str, Path]:
    """Map every canonical-language spec's logical key <topic>/<slug> to its file.

    Specs live at <spec_root>/[<topic>/]<slug>/<lang>.md (one nesting level).
    The logical key is the directory path under spec_root, '/'-joined.
    """
    out: dict[str, Path] = {}
    if not spec_root.is_dir():
        return out
    for canon in spec_root.rglob(f"{lang}.md"):
        rel = canon.parent.relative_to(spec_root)
        parts = rel.parts
        if not parts or parts[0] in EXCLUDED_TOPICS:
            continue
        out["/".join(parts)] = canon
    return out


def section_body(text: str, section: str) -> str | None:
    """Body of the heading matching `section` (the §<Section> form), or None.

    Returns the text from just after the heading line up to the next heading of
    the same or higher level.
    """
    want = ANCHOR_RE.sub("", section.lstrip("§")).strip().casefold()
    headings = list(HEADING_RE.finditer(text))
    for i, h in enumerate(headings):
        if ANCHOR_RE.sub("", h.group(2)).strip().casefold() == want:
            level = len(h.group(1))
            start = h.end()
            end = len(text)
            for nxt in headings[i + 1:]:
                if len(nxt.group(1)) <= level:
                    end = nxt.start()
                    break
            return text[start:end]
    return None


def has_locked(body: str) -> bool:
    """Whether a section body carries a portfolio-locked invariant marker."""
    return "[locked]" in body


def cross_refs(text: str) -> set[str]:
    """Every spec/<topic>/<slug>/ cross-reference as a logical key.

    Non-topic directories (EXCLUDED_TOPICS, e.g. schemas) are dropped so a prose
    reference to spec/schemas/ is not later mistaken for a ghost reference.
    """
    return {
        f"{m.group(1)}/{m.group(2)}"
        for m in CROSSREF_RE.finditer(text)
        if m.group(1) not in EXCLUDED_TOPICS
    }


# --- resolution ------------------------------------------------------------

def own_plugin_name(repo: Path) -> str | None:
    """The repository's own plugin identifier, from .claude-plugin/plugin.json.

    Used to detect a cyclic inheritance declaration (a source resolving back to
    this repository). Returns None when no plugin manifest is present.
    """
    manifest = repo / ".claude-plugin" / "plugin.json"
    if manifest.is_file():
        try:
            return json.loads(_read(manifest)).get("name")
        except (json.JSONDecodeError, OSError):
            return None
    return None


def resolve_hub_spec_root(cli_value: str | None) -> Path | None:
    if cli_value:
        return Path(cli_value)
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if plugin_root:
        return Path(plugin_root) / "spec"
    return None


def hub_canonical_lang(hub_spec_root: Path) -> str:
    cfg = hub_spec_root / ".spec-config.yml"
    if cfg.is_file():
        try:
            data = yaml.safe_load(_read(cfg)) or {}
            return data.get("canonical_language", "en")
        except yaml.YAMLError:
            pass
    return "en"


# --- checks ----------------------------------------------------------------

def check_local_scope_headers(local: dict[str, Path]) -> list[Finding]:
    """Hub / local-only mode: every Portfolio-Scope header value is valid."""
    findings: list[Finding] = []
    for key, path in sorted(local.items()):
        m = SCOPE_RE.search(_read(path))
        if m and m.group(1).strip() not in VALID_SCOPES:
            findings.append(Finding(
                "Warning", key, "scope-header-malformed",
                f"Portfolio-Scope: '{m.group(1).strip()}' is not one of {sorted(VALID_SCOPES)}",
            ))
    return findings


def check_source(
    repo: Path,
    source: dict,
    local: dict[str, Path],
    canonical_lang: str,
    own_source: str | None,
    hub_spec_root: Path | None,
) -> list[Finding]:
    findings: list[Finding] = []
    if not isinstance(source, dict):
        return [Finding("Warning", "inherits[]", "malformed-source",
                        "inherits entry is not a mapping; schema validation should have caught this")]
    src_name = source.get("source", "<unknown>")
    ref = source.get("ref", "")
    target = f"inherits[{src_name}]"

    # Structural checks (no inherited corpus required).
    if not ref or not TAG_REF_RE.match(str(ref)):
        findings.append(Finding(
            "Warning", target, "floating-ref",
            f"ref '{ref}' is not a tag-pinned release; pin to an explicit tag (e.g. v0.1.9)",
        ))
    if own_source and src_name == own_source:
        findings.append(Finding(
            "Critical", target, "cyclic-inheritance",
            f"source '{src_name}' resolves back to this repository (cycle)",
        ))

    raw_overrides = source.get("overrides") or []
    if not isinstance(raw_overrides, list):
        findings.append(Finding("Warning", target, "malformed-overrides",
                                "overrides: is not a list; schema validation should have caught this"))
        raw_overrides = []
    overrides = [o for o in raw_overrides if isinstance(o, dict)]
    declared_keys = {o.get("spec") for o in overrides}

    for ov in overrides:
        spec_key = ov.get("spec", "<missing>")
        otarget = f"{target} override {spec_key}"
        if not (ov.get("reason") or "").strip():
            findings.append(Finding(
                "Warning", otarget, "empty-reason",
                "override reason is empty or missing",
            ))
        local_path = ov.get("local")
        if local_path and not (repo / local_path).is_file():
            findings.append(Finding(
                "Warning", otarget, "missing-override-file",
                f"declared local override file '{local_path}' does not exist",
            ))

    # Content-dependent checks require the inherited corpus.
    if hub_spec_root is None or not hub_spec_root.is_dir():
        findings.append(Finding(
            "Warning", target, "inherited-corpus-unresolved",
            "inherited corpus not found (set --hub-spec-root or $CLAUDE_PLUGIN_ROOT); "
            "skipping undeclared-divergence, locked-section, ghost-reference and "
            "override-section checks",
        ))
        return findings

    hub_lang = hub_canonical_lang(hub_spec_root)
    hub_all = collect_specs(hub_spec_root, hub_lang)
    inherited = {
        key: path for key, path in hub_all.items()
        if portfolio_scope(_read(path)) == "portfolio"
    }

    # Override validity against the inherited corpus.
    for ov in overrides:
        spec_key = ov.get("spec", "<missing>")
        otarget = f"{target} override {spec_key}"
        sec = ov.get("section", "")
        if spec_key not in inherited:
            findings.append(Finding(
                "Warning", otarget, "broken-override-ref",
                f"override target '{spec_key}' is not a portfolio-scope spec at {ref}",
            ))
            continue
        body = section_body(_read(inherited[spec_key]), sec)
        if body is None:
            findings.append(Finding(
                "Warning", otarget, "stale-override",
                f"overridden section '{sec}' no longer exists in '{spec_key}' at {ref}",
            ))
            continue
        if has_locked(body):
            findings.append(Finding(
                "Critical", otarget, "locked-section-override",
                f"section '{sec}' of '{spec_key}' carries a [locked] invariant and cannot be overridden",
            ))

    # Undeclared divergence: a local spec sharing a logical key with an inherited
    # portfolio-scope spec, without a declared override, is a forbidden silent fork.
    for key in sorted(set(local) & set(inherited)):
        if key not in declared_keys:
            findings.append(Finding(
                "Critical", key, "undeclared-divergence",
                f"local spec shadows inherited portfolio-scope spec '{key}' with no declared override "
                "(delete the local copy to inherit, or declare an overrides: record)",
            ))

    # Ghost references in the combined namespace local ∪ inherited.
    combined = set(local) | set(inherited)
    for key, path in sorted(local.items()):
        for ref_key in sorted(cross_refs(_read(path))):
            if ref_key not in combined:
                findings.append(Finding(
                    "Critical", key, "ghost-reference",
                    f"cross-reference to 'spec/{ref_key}/' resolves in neither the local nor the inherited set",
                ))
    return findings


def run(repo: Path, hub_spec_root: Path | None) -> list[Finding]:
    cfg_path = repo / "spec" / ".spec-config.yml"
    if not cfg_path.is_file():
        return [Finding("Warning", str(cfg_path), "no-config",
                        "no spec/.spec-config.yml; nothing to check")]
    config = yaml.safe_load(_read(cfg_path)) or {}
    canonical_lang = config.get("canonical_language", "en")
    spec_root = repo / config.get("spec_root", "spec")
    local = collect_specs(spec_root, canonical_lang)

    inherits = config.get("inherits")
    if not inherits:
        # Hub root or local-only repo: validate header hygiene only.
        return check_local_scope_headers(local)
    if not isinstance(inherits, list):
        return [Finding("Warning", str(cfg_path), "malformed-inherits",
                        "inherits: is not a list; schema validation should have caught this")]

    # A source resolving back to this repository's own plugin identity is a cycle.
    own_source = own_plugin_name(repo)
    findings: list[Finding] = []
    for source in inherits:
        findings.extend(
            check_source(repo, source, local, canonical_lang, own_source, hub_spec_root)
        )
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=str(REPO), help="repository root (default: this repo)")
    parser.add_argument("--hub-spec-root", default=None,
                        help="path to the inherited hub's spec/ tree (overrides $CLAUDE_PLUGIN_ROOT/spec)")
    args = parser.parse_args(argv)

    repo = Path(args.repo).resolve()
    hub_spec_root = resolve_hub_spec_root(args.hub_spec_root)

    try:
        findings = run(repo, hub_spec_root)
    except yaml.YAMLError as exc:
        print(f"Critical    spec/.spec-config.yml  [internal] unparseable YAML: {exc}", file=sys.stderr)
        return 2

    by_severity = {"Critical": 0, "Warning": 0, "Suggestion": 0, "Info": 0}
    for f in findings:
        by_severity[f.severity] = by_severity.get(f.severity, 0) + 1
        print(f)
    if not findings:
        print("check_spec_inheritance: no findings")

    print(
        f"\ncheck_spec_inheritance: "
        f"{by_severity['Critical']}C / {by_severity['Warning']}W / "
        f"{by_severity['Suggestion']}S / {by_severity['Info']}I",
        file=sys.stderr,
    )
    return 1 if by_severity["Critical"] else 0


if __name__ == "__main__":
    sys.exit(main())
