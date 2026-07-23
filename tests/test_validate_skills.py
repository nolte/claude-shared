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
    # The cap is enforcing (Critical) now the T2 backlog is split; assert against
    # the constant so the test tracks BODY_TOKEN_CAP_SEVERITY.
    assert findings[0].severity == v.BODY_TOKEN_CAP_SEVERITY


def test_cap_band_beats_warn_band():
    # A body over the cap emits exactly one finding (cap), never both bands.
    body = "x" * (v.BODY_TOKEN_CAP * 4 + 4000)
    assert len(v.check_body_token_estimate(body, "x/SKILL.md", "skill")) == 1


# --- Use-case-metadata field caps (mirror gen_catalog.py, the docs/links gate) ---

def test_dont_use_when_situation_over_cap_flags_critical():
    # This is the exact class that reached the docs build past the fast validator.
    long = "y" * (v.DONT_USE_WHEN_SITUATION_MAX_LEN + 1)
    text = (
        "---\nname: x\ndescription: ok\n"
        f'dont_use_when:\n  - situation: "{long}"\n    alternative: other\n'
        "---\nbody\n"
    )
    findings = v.check_use_case_field_lengths(text, "x/SKILL.md", "skill")
    assert len(findings) == 1
    assert findings[0].severity == "Critical"
    assert findings[0].rule == "skill-management.frontmatter-use-case-field"


def test_use_when_and_summary_within_caps_are_clean():
    text = (
        "---\nname: x\ndescription: ok\n"
        'summary: "a short summary"\n'
        'use_when:\n  - "a reasonable trigger phrase"\n'
        "---\nbody\n"
    )
    assert v.check_use_case_field_lengths(text, "x/SKILL.md", "skill") == []


def test_use_when_over_length_flags_critical():
    long = "z" * (v.USE_WHEN_MAX_LEN + 1)
    text = f'---\nname: x\ndescription: ok\nuse_when:\n  - "{long}"\n---\nb\n'
    findings = v.check_use_case_field_lengths(text, "x/SKILL.md", "skill")
    assert _rules(findings) == {"skill-management.frontmatter-use-case-field"}


# --- R-9 / F-8: per-plugin agent-description budget guardrail ---------------

def test_description_budget_clean_at_frozen_baseline():
    # Every plugin with a recorded baseline sits at/under baseline+headroom, so
    # the gate is silent on the current tree (this is the durable-headroom claim).
    for key in v.AGENT_DESC_BASELINE_CHARS:
        assert v.check_agent_description_budget(v.REPO / key) == [], key


def test_description_budget_fires_on_regression(monkeypatch):
    # Shrink one plugin's frozen baseline so the current aggregate breaches it:
    # the value-verifier must fail on regression (F-8 acceptance-1).
    monkeypatch.setitem(v.AGENT_DESC_BASELINE_CHARS, "agents", 5000)
    findings = v.check_agent_description_budget(v.REPO / "agents")
    assert len(findings) == 1
    assert findings[0].severity == "Critical"
    assert findings[0].rule == "agent-management.description-budget-regression"


def test_description_budget_ungated_dir_noops(monkeypatch):
    # A plugin without a recorded baseline is not gated (no fail-closed on a new
    # plugin before its baseline is captured).
    monkeypatch.delitem(v.AGENT_DESC_BASELINE_CHARS, "agents", raising=False)
    assert v.check_agent_description_budget(v.REPO / "agents") == []


# --- WP-B6: 2026-07 audit guards ------------------------------------------

def test_rationale_heading_missing_is_critical():
    findings = v.check_rationale_heading("# T\n\n## Other\n", "x/SKILL.md", "skill")
    assert _rules(findings) == {"skill-management.rationale-heading-missing"}
    assert findings[0].severity == "Critical"


def test_rationale_heading_exact_wording_passes():
    body = "# T\n\n## Why this is a skill, not an agent\n\n- dimension\n"
    assert v.check_rationale_heading(body, "x/SKILL.md", "skill") == []
    body_a = "# T\n\n## Why this is an agent, not a skill\n\n- dimension\n"
    assert v.check_rationale_heading(body_a, "x.md", "agent") == []


def test_rationale_heading_variant_fails():
    body = "# T\n\n## Skill-vs-agent rationale\n\n- dimension\n"
    assert len(v.check_rationale_heading(body, "x.md", "agent")) == 1


def test_lead_voice_imperative_warns():
    findings = v.check_description_lead_voice("Audit the repo for drift.", "x.md", "skill")
    assert _rules(findings) == {"skill-management.frontmatter-description-lead-voice"}
    assert findings[0].severity == "Warning"


def test_lead_voice_third_person_and_nominal_pass():
    assert v.check_description_lead_voice("Audits the repo.", "x.md", "skill") == []
    assert v.check_description_lead_voice("Read-only scanner dispatched by x.", "x.md", "agent") == []
    assert v.check_description_lead_voice("Visually reviews an E2E run.", "x.md", "agent") == []
    assert v.check_description_lead_voice("Senior full-stack implementation agent.", "x.md", "agent") == []


def test_description_headroom_info_band():
    assert v.check_description_headroom("x" * 900, "x.md", "skill") == []
    findings = v.check_description_headroom("x" * 1000, "x.md", "skill")
    assert _rules(findings) == {"skill-management.frontmatter-description-headroom"}
    assert findings[0].severity == "Info"
    # over-cap is the cap check's job, not headroom's
    assert v.check_description_headroom("x" * 1030, "x.md", "skill") == []


def test_bash_justification_readonly_critical():
    findings = v.check_bash_justification(
        "Read, Bash", "Read-only scanner over the tree.", "# A\n\nbody\n", "x.md")
    assert _rules(findings) == {"agent-management.bash-justification-missing"}
    assert findings[0].severity == "Critical"


def test_bash_justification_write_capable_warning_and_headings_pass():
    findings = v.check_bash_justification(
        ["Read", "Write", "Bash"], "Drafts docs and runs checks.", "# A\n\nbody\n", "x.md")
    assert findings and findings[0].severity == "Warning"
    ok_ro = "# A\n\n## Read-only Bash justification\n\n- `git log`\n"
    assert v.check_bash_justification("Read, Bash", "Read-only scanner.", ok_ro, "x.md") == []
    ok_n = "# A\n\n## Bash justification\n\n- `task test`\n"
    assert v.check_bash_justification("Read, Write, Bash", "Drafts.", ok_n, "x.md") == []
    assert v.check_bash_justification("Read, Grep", "Read-only scanner.", "# A\n", "x.md") == []
