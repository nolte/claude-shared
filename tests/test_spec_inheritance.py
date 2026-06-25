"""Unit tests for scripts/check_spec_inheritance.py.

Exercises the SEMANTIC Local-vs-Inherited drift checks from
spec/project/portfolio-inherited-spec-layer/ §"Drift detection" against
synthetic local + inherited spec trees, so the CI-error MUST of §"Audit and CI
integration" is verifiable without a real installed plugin.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import check_spec_inheritance as csi  # noqa: E402


# --- builders --------------------------------------------------------------

def make_spec(root: Path, key: str, *, lang="en", scope="local",
              section: str | None = None, locked: bool = False, body: str = "") -> None:
    d = root / key
    d.mkdir(parents=True, exist_ok=True)
    lines = [f"# {key}", "", "Status: draft"]
    if scope is not None:
        lines.append(f"Portfolio-Scope: {scope}")
    lines.append("")
    if section:
        lines += [f"## {section}", ""]
        lines.append("- **MUST** [locked] never weaken this." if locked else "- **MUST** do the thing.")
        lines.append("")
    lines.append(body)
    (d / f"{lang}.md").write_text("\n".join(lines), encoding="utf-8")


def write_config(repo: Path, *, inherits=None, canonical="en") -> None:
    sd = repo / "spec"
    sd.mkdir(parents=True, exist_ok=True)
    cfg = {"canonical_language": canonical, "languages": [canonical], "spec_root": "spec"}
    if inherits is not None:
        cfg["inherits"] = inherits
    (sd / ".spec-config.yml").write_text(yaml.safe_dump(cfg), encoding="utf-8")


def make_hub(tmp_path: Path) -> Path:
    """A hub spec/ tree with one portfolio-scope spec and one local spec."""
    hub = tmp_path / "hub" / "spec"
    hub.mkdir(parents=True, exist_ok=True)
    (hub / ".spec-config.yml").write_text(
        yaml.safe_dump({"canonical_language": "en", "languages": ["en"], "spec_root": "spec"}),
        encoding="utf-8",
    )
    make_spec(hub, "project/branching-model", scope="portfolio", section="Branch roles")
    make_spec(hub, "project/locked-rule", scope="portfolio", section="Invariants", locked=True)
    make_spec(hub, "project/repo-only", scope="local", section="Local")
    return hub


def severities(findings):
    return [f.severity for f in findings]


def codes(findings):
    return {f.rule for f in findings}


# --- tests -----------------------------------------------------------------

def test_no_config_is_warning_not_critical(tmp_path):
    findings = csi.run(tmp_path, None)
    assert "Critical" not in severities(findings)


def test_hub_mode_no_inherits_clean(tmp_path):
    write_config(tmp_path, inherits=None)
    make_spec(tmp_path / "spec", "project/foo", scope="portfolio")
    make_spec(tmp_path / "spec", "project/bar", scope="local")
    findings = csi.run(tmp_path, None)
    assert findings == []


def test_hub_mode_malformed_scope_is_warning(tmp_path):
    write_config(tmp_path, inherits=None)
    make_spec(tmp_path / "spec", "project/foo", scope="global")  # invalid value
    findings = csi.run(tmp_path, None)
    assert "Critical" not in severities(findings)
    assert "scope-header-malformed" in codes(findings)


def test_clean_inherit_no_local_copy(tmp_path):
    hub = make_hub(tmp_path)
    consumer = tmp_path / "consumer"
    write_config(consumer, inherits=[{"source": "nolte-shared", "ref": "v0.1.9"}])
    findings = csi.run(consumer, hub)
    assert "Critical" not in severities(findings)


def test_undeclared_divergence_is_critical(tmp_path):
    hub = make_hub(tmp_path)
    consumer = tmp_path / "consumer"
    write_config(consumer, inherits=[{"source": "nolte-shared", "ref": "v0.1.9"}])
    # local copy shadowing an inherited portfolio-scope spec, no override declared
    make_spec(consumer / "spec", "project/branching-model", scope="local", section="Branch roles")
    findings = csi.run(consumer, hub)
    assert "undeclared-divergence" in codes(findings)
    assert "Critical" in severities(findings)
    assert csi.main(["--repo", str(consumer), "--hub-spec-root", str(hub)]) == 1


def test_locked_section_override_is_critical(tmp_path):
    hub = make_hub(tmp_path)
    consumer = tmp_path / "consumer"
    ov_file = consumer / "spec" / "project" / "locked-rule" / "override.md"
    ov_file.parent.mkdir(parents=True, exist_ok=True)
    ov_file.write_text("## Invariants\n\n- **MUST** do it differently.\n", encoding="utf-8")
    write_config(consumer, inherits=[{
        "source": "nolte-shared", "ref": "v0.1.9",
        "overrides": [{
            "spec": "project/locked-rule", "section": "§Invariants",
            "reason": "we differ", "local": "spec/project/locked-rule/override.md",
        }],
    }])
    findings = csi.run(consumer, hub)
    assert "locked-section-override" in codes(findings)
    assert "Critical" in severities(findings)


def test_clean_override_no_critical(tmp_path):
    hub = make_hub(tmp_path)
    consumer = tmp_path / "consumer"
    ov_file = consumer / "spec" / "project" / "branching-model" / "override.md"
    ov_file.parent.mkdir(parents=True, exist_ok=True)
    ov_file.write_text("## Branch roles\n\nTrunk-based.\n", encoding="utf-8")
    write_config(consumer, inherits=[{
        "source": "nolte-shared", "ref": "v0.1.9",
        "overrides": [{
            "spec": "project/branching-model", "section": "§Branch roles",
            "reason": "trunk-based repo", "local": "spec/project/branching-model/override.md",
        }],
    }])
    findings = csi.run(consumer, hub)
    assert "Critical" not in severities(findings)


def test_empty_reason_and_missing_file_are_warnings(tmp_path):
    hub = make_hub(tmp_path)
    consumer = tmp_path / "consumer"
    write_config(consumer, inherits=[{
        "source": "nolte-shared", "ref": "v0.1.9",
        "overrides": [{
            "spec": "project/branching-model", "section": "§Branch roles",
            "reason": "", "local": "spec/project/branching-model/override.md",
        }],
    }])
    findings = csi.run(consumer, hub)
    assert "empty-reason" in codes(findings)
    assert "missing-override-file" in codes(findings)
    assert "Critical" not in severities(findings)


def test_ghost_reference_is_critical(tmp_path):
    hub = make_hub(tmp_path)
    consumer = tmp_path / "consumer"
    write_config(consumer, inherits=[{"source": "nolte-shared", "ref": "v0.1.9"}])
    make_spec(consumer / "spec", "project/mine", scope="local",
              body="See spec/project/does-not-exist/ for details.")
    findings = csi.run(consumer, hub)
    assert "ghost-reference" in codes(findings)
    assert "Critical" in severities(findings)


def test_cross_ref_to_inherited_resolves(tmp_path):
    hub = make_hub(tmp_path)
    consumer = tmp_path / "consumer"
    write_config(consumer, inherits=[{"source": "nolte-shared", "ref": "v0.1.9"}])
    make_spec(consumer / "spec", "project/mine", scope="local",
              body="Follows spec/project/branching-model/ from the hub.")
    findings = csi.run(consumer, hub)
    assert "ghost-reference" not in codes(findings)


def test_floating_ref_is_warning(tmp_path):
    hub = make_hub(tmp_path)
    consumer = tmp_path / "consumer"
    write_config(consumer, inherits=[{"source": "nolte-shared", "ref": "develop"}])
    findings = csi.run(consumer, hub)
    assert "floating-ref" in codes(findings)
    assert "Critical" not in severities(findings)


def test_unresolved_corpus_is_warning_only(tmp_path):
    consumer = tmp_path / "consumer"
    write_config(consumer, inherits=[{"source": "nolte-shared", "ref": "v0.1.9"}])
    findings = csi.run(consumer, None)  # no hub spec root
    assert "inherited-corpus-unresolved" in codes(findings)
    assert "Critical" not in severities(findings)


def test_hub_itself_passes(tmp_path):
    """The real hub repo (this checkout) has no inherits and clean headers."""
    repo = Path(__file__).resolve().parents[1]
    assert csi.main(["--repo", str(repo)]) == 0
