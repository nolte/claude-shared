"""Conformance tests for the two frontmatter gates added in
`fix/skill-frontmatter-yaml-gates`, closing T1/T2 of the 2026-07-01 sweep
(.audits/skills-agents-sweep/).

- `check_frontmatter_yaml` — the strict-YAML parse gate. Pins the exact defect
  class it guards: an unquoted `description:` whose value embeds `: ` (colon-space)
  is a YAML mapping-indicator and fails a standard parser (the Claude Code loader),
  even though the lenient regex parser tolerates it.
- `check_body_token_estimate` — the 5,000-token body cap (4-char/token heuristic).
  The ≥5,000 band ships at Warning (BODY_TOKEN_CAP_SEVERITY) until the pre-existing
  over-cap skills are split; this test locks the band boundaries and the rule ids.
"""
from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import validate_skills as v  # noqa: E402


def _rules(findings):
    return {f.rule for f in findings}


# --- T1: strict-YAML parse gate -------------------------------------------

def test_unquoted_colon_space_description_fails_yaml():
    # `Read-only: reports` — the colon-space makes the plain scalar a mapping.
    text = "---\nname: x\ndescription: Read-only: reports things\n---\nbody\n"
    findings = v.check_frontmatter_yaml(text, "x/SKILL.md", "skill")
    assert len(findings) == 1
    assert findings[0].severity == "Critical"
    assert findings[0].rule == "skill-management.frontmatter-yaml-invalid"


def test_double_quoted_description_passes_yaml():
    text = '---\nname: x\ndescription: "Read-only: reports things"\n---\nbody\n'
    assert v.check_frontmatter_yaml(text, "x/SKILL.md", "skill") == []


def test_single_quoted_description_with_escaped_apostrophe_passes():
    # The cookiecutter/api-error-check shape: embeds `"` and `'` -> single-quote wrap.
    text = "---\nname: x\ndescription: 'Manages a template: don''t use for Y'\n---\nb\n"
    assert v.check_frontmatter_yaml(text, "x/SKILL.md", "skill") == []


def test_yaml_gate_uses_kind_in_rule_id():
    text = "---\nname: x\ndescription: bad: value\n---\nb\n"
    findings = v.check_frontmatter_yaml(text, "x.md", "agent")
    assert findings[0].rule == "agent-management.frontmatter-yaml-invalid"


def test_yaml_gate_noop_without_frontmatter():
    assert v.check_frontmatter_yaml("no frontmatter here\n", "x/SKILL.md", "skill") == []


# --- T2: body token estimate ----------------------------------------------

def test_body_below_warn_is_clean():
    body = "x" * (v.BODY_TOKEN_WARN * 4 - 40)  # ~ (WARN - 10) tokens
    assert v.check_body_token_estimate(body, "x/SKILL.md", "skill") == []


def test_body_in_warn_band_flags_approaching():
    body = "x" * (v.BODY_TOKEN_WARN * 4)  # exactly WARN tokens
    findings = v.check_body_token_estimate(body, "x/SKILL.md", "skill")
    assert _rules(findings) == {"skill-management.body-token-approaching"}
    assert findings[0].severity == "Warning"


def test_body_over_cap_flags_cap_at_configured_severity():
    body = "x" * (v.BODY_TOKEN_CAP * 4)  # exactly CAP tokens
    findings = v.check_body_token_estimate(body, "x/SKILL.md", "skill")
    assert _rules(findings) == {"skill-management.body-token-cap"}
    # Staged rollout: Warning today so CI stays green; the body-split PR flips it.
    assert findings[0].severity == v.BODY_TOKEN_CAP_SEVERITY


def test_cap_band_beats_warn_band():
    # A body over the cap emits exactly one finding (cap), never both bands.
    body = "x" * (v.BODY_TOKEN_CAP * 4 + 4000)
    assert len(v.check_body_token_estimate(body, "x/SKILL.md", "skill")) == 1
