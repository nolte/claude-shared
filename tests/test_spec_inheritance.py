"""Unit tests for scripts/check_spec_inheritance.py.

Exercises the SEMANTIC Local-vs-Inherited drift checks from
spec/project/portfolio-inherited-spec-layer/ §"Drift detection" against
synthetic local + inherited spec trees, so the CI-error MUST of §"Audit and CI
integration" is verifiable without a real installed plugin.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest
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


def write_plugin(repo: Path, name: str) -> None:
    d = repo / ".claude-plugin"
    d.mkdir(parents=True, exist_ok=True)
    (d / "plugin.json").write_text(json.dumps({"name": name}), encoding="utf-8")


def test_cyclic_inheritance_is_critical(tmp_path):
    hub = make_hub(tmp_path)
    consumer = tmp_path / "consumer"
    write_plugin(consumer, "myself")  # own plugin identity
    write_config(consumer, inherits=[{"source": "myself", "ref": "v0.1.9"}])
    findings = csi.run(consumer, hub)
    assert "cyclic-inheritance" in codes(findings)
    assert "Critical" in severities(findings)


def test_broken_override_ref_is_warning(tmp_path):
    hub = make_hub(tmp_path)
    consumer = tmp_path / "consumer"
    ov = consumer / "spec" / "project" / "absent" / "override.md"
    ov.parent.mkdir(parents=True, exist_ok=True)
    ov.write_text("## X\n\nbody\n", encoding="utf-8")
    write_config(consumer, inherits=[{
        "source": "nolte-shared", "ref": "v0.1.9",
        "overrides": [{
            "spec": "project/absent", "section": "§X",
            "reason": "n/a", "local": "spec/project/absent/override.md",
        }],
    }])
    findings = csi.run(consumer, hub)
    assert "broken-override-ref" in codes(findings)
    assert "Critical" not in severities(findings)


def test_stale_override_is_warning(tmp_path):
    hub = make_hub(tmp_path)
    consumer = tmp_path / "consumer"
    ov = consumer / "spec" / "project" / "branching-model" / "override.md"
    ov.parent.mkdir(parents=True, exist_ok=True)
    ov.write_text("## Gone\n\nbody\n", encoding="utf-8")
    write_config(consumer, inherits=[{
        "source": "nolte-shared", "ref": "v0.1.9",
        "overrides": [{
            "spec": "project/branching-model", "section": "§Vanished Section",
            "reason": "n/a", "local": "spec/project/branching-model/override.md",
        }],
    }])
    findings = csi.run(consumer, hub)
    assert "stale-override" in codes(findings)
    assert "Critical" not in severities(findings)


def test_section_with_anchor_resolves(tmp_path):
    """An overridden section whose hub heading carries a {#anchor} still matches."""
    hub = tmp_path / "hub" / "spec"
    hub.mkdir(parents=True, exist_ok=True)
    (hub / ".spec-config.yml").write_text(
        yaml.safe_dump({"canonical_language": "en", "languages": ["en"], "spec_root": "spec"}),
        encoding="utf-8",
    )
    d = hub / "project" / "anchored"
    d.mkdir(parents=True, exist_ok=True)
    (d / "en.md").write_text(
        "# anchored\n\nStatus: draft\nPortfolio-Scope: portfolio\n\n## Roles {#roles}\n\n- **MUST** do it.\n",
        encoding="utf-8",
    )
    consumer = tmp_path / "consumer"
    ov = consumer / "spec" / "project" / "anchored" / "override.md"
    ov.parent.mkdir(parents=True, exist_ok=True)
    ov.write_text("## Roles\n\nlocal\n", encoding="utf-8")
    write_config(consumer, inherits=[{
        "source": "nolte-shared", "ref": "v0.1.9",
        "overrides": [{
            "spec": "project/anchored", "section": "§Roles",
            "reason": "differ", "local": "spec/project/anchored/override.md",
        }],
    }])
    findings = csi.run(consumer, hub)
    assert "stale-override" not in codes(findings)


def test_schemas_reference_is_not_ghost(tmp_path):
    hub = make_hub(tmp_path)
    consumer = tmp_path / "consumer"
    write_config(consumer, inherits=[{"source": "nolte-shared", "ref": "v0.1.9"}])
    make_spec(consumer / "spec", "project/mine", scope="local",
              body="See spec/schemas/spec-config/ for the schema.")
    findings = csi.run(consumer, hub)
    assert "ghost-reference" not in codes(findings)


def test_hub_itself_passes(tmp_path):
    """The real hub repo (this checkout) has no inherits and clean headers."""
    repo = Path(__file__).resolve().parents[1]
    assert csi.main(["--repo", str(repo)]) == 0


def test_non_utf8_spec_file_exits_2_not_a_traceback(tmp_path, capsys):
    hub = make_hub(tmp_path)
    consumer = tmp_path / "consumer"
    write_config(consumer, inherits=[{"source": "nolte-shared", "ref": "v0.1.9"}])
    make_spec(consumer / "spec", "project/mine", scope="local")
    (consumer / "spec" / "project" / "mine" / "en.md").write_bytes(b"# Mine\n\n\xff\n")
    assert csi.main(["--repo", str(consumer), "--hub-spec-root", str(hub)]) == 2
    assert "isn't valid UTF-8" in capsys.readouterr().err


def test_non_mapping_consumer_config_is_a_critical_finding_not_a_traceback(tmp_path):
    consumer = tmp_path / "consumer"
    (consumer / "spec").mkdir(parents=True)
    (consumer / "spec" / ".spec-config.yml").write_text("- inherits\n", encoding="utf-8")
    assert codes(csi.run(consumer, None)) == {"malformed-config"}
    assert csi.main(["--repo", str(consumer)]) == 1


def test_non_utf8_error_names_the_file(tmp_path, capsys):
    hub = make_hub(tmp_path)
    bad = hub / "project" / "repo-only" / "en.md"
    bad.write_bytes(b"# Repo only\n\n\xff\n")
    consumer = tmp_path / "consumer"
    write_config(consumer, inherits=[{"source": "nolte-shared", "ref": "v0.1.9"}])
    make_spec(consumer / "spec", "project/mine", scope="local")
    assert csi.main(["--repo", str(consumer), "--hub-spec-root", str(hub)]) == 2
    assert str(bad) in capsys.readouterr().err


def test_unreadable_hub_config_exits_2_instead_of_checking_in_english(tmp_path, capsys):
    """A hub config that can't be read must not silently fall back to "en" (#812 review)."""
    if os.geteuid() == 0:
        pytest.skip("root reads a mode-000 file")
    hub = make_hub(tmp_path)
    cfg = hub / ".spec-config.yml"
    cfg.chmod(0)
    consumer = tmp_path / "consumer"
    write_config(consumer, inherits=[{"source": "nolte-shared", "ref": "v0.1.9"}])
    make_spec(consumer / "spec", "project/mine", scope="local")
    try:
        assert csi.main(["--repo", str(consumer), "--hub-spec-root", str(hub)]) == 2
    finally:
        cfg.chmod(0o644)
    assert "can't be read" in capsys.readouterr().err


@pytest.mark.parametrize("which", ["plugin", "hub"])
def test_non_utf8_manifest_or_hub_config_exits_2_instead_of_a_silent_default(tmp_path, capsys, which):
    """Neither a silent None (cyclic check off) nor a silent "en" (#812 review)."""
    hub = make_hub(tmp_path)
    consumer = tmp_path / "consumer"
    write_config(consumer, inherits=[{"source": "nolte-shared", "ref": "v0.1.9"}])
    make_spec(consumer / "spec", "project/mine", scope="local")
    if which == "plugin":
        bad = consumer / ".claude-plugin" / "plugin.json"
        bad.parent.mkdir()
    else:
        bad = hub / ".spec-config.yml"
    bad.write_bytes(b"\xff\xfe{}")
    assert csi.main(["--repo", str(consumer), "--hub-spec-root", str(hub)]) == 2
    assert str(bad) in capsys.readouterr().err


# --- #816: a malformed config shape fails closed, naming file and key ---------
# Missing files and missing keys keep their defaults; a present-but-malformed
# value is a Critical `malformed-config` finding (exit 1), never a silent default
# and never a traceback.

def _consumer_with_hub(tmp_path: Path) -> tuple[Path, Path]:
    hub = make_hub(tmp_path)
    consumer = tmp_path / "consumer"
    write_config(consumer, inherits=[{"source": "nolte-shared", "ref": "v0.1.9"}])
    make_spec(consumer / "spec", "project/mine", scope="local")
    return consumer, hub


def _malformed(findings, needle: str) -> list:
    return [f for f in findings
            if f.rule == "malformed-config" and f.severity == "Critical"
            and needle in f"{f.target} {f.message}"]


@pytest.mark.parametrize("manifest, key", [
    ("{bad", "plugin.json"),
    ("[1]", "plugin.json"),
    ('{"name": 5}', "name"),
    ('{"name": ""}', "name"),
])
def test_malformed_plugin_manifest_is_critical_not_a_silent_none(tmp_path, capsys, manifest, key):
    """A broken manifest must not switch the cyclic-inheritance check off."""
    consumer, hub = _consumer_with_hub(tmp_path)
    bad = consumer / ".claude-plugin" / "plugin.json"
    bad.parent.mkdir()
    bad.write_text(manifest, encoding="utf-8")
    findings = csi.run(consumer, hub)
    hits = _malformed(findings, key)
    assert hits, findings
    assert str(bad) in hits[0].target
    assert csi.main(["--repo", str(consumer), "--hub-spec-root", str(hub)]) == 1
    assert "Traceback" not in capsys.readouterr().err


@pytest.mark.parametrize("config, key", [
    ("a: [\n", ".spec-config.yml"),
    ("- a\n", ".spec-config.yml"),
    ("canonical_language: 5\n", "canonical_language"),
    ("canonical_language: ''\n", "canonical_language"),
    ("canonical_language:\n", "canonical_language"),
])
def test_malformed_hub_config_is_critical_not_a_silent_english(tmp_path, capsys, config, key):
    consumer, hub = _consumer_with_hub(tmp_path)
    cfg = hub / ".spec-config.yml"
    cfg.write_text(config, encoding="utf-8")
    findings = csi.run(consumer, hub)
    hits = _malformed(findings, key)
    assert hits, findings
    assert str(cfg) in hits[0].target
    assert csi.main(["--repo", str(consumer), "--hub-spec-root", str(hub)]) == 1
    assert "Traceback" not in capsys.readouterr().err


@pytest.mark.parametrize("extra, key", [
    ({"canonical_language": None}, "canonical_language"),
    ({"canonical_language": ""}, "canonical_language"),
    ({"canonical_language": 5}, "canonical_language"),
    ({"spec_root": 1}, "spec_root"),
    ({"spec_root": ""}, "spec_root"),
    ({"spec_root": None}, "spec_root"),
    ({"spec_root": "/abs/spec"}, "spec_root"),
])
def test_malformed_consumer_config_value_is_critical(tmp_path, capsys, extra, key):
    consumer = tmp_path / "consumer"
    (consumer / "spec").mkdir(parents=True)
    cfg = {"canonical_language": "en", "spec_root": "spec", **extra}
    (consumer / "spec" / ".spec-config.yml").write_text(yaml.safe_dump(cfg), encoding="utf-8")
    findings = csi.run(consumer, None)
    hits = _malformed(findings, key)
    assert hits, findings
    assert csi.main(["--repo", str(consumer)]) == 1
    assert "Traceback" not in capsys.readouterr().err


def test_absent_keys_keep_their_defaults(tmp_path):
    """Refutation control: absent manifest name, hub language, consumer keys stay defaults."""
    hub = make_hub(tmp_path)
    (hub / ".spec-config.yml").write_text("languages: [en]\n", encoding="utf-8")
    consumer = tmp_path / "consumer"
    (consumer / "spec").mkdir(parents=True)
    (consumer / "spec" / ".spec-config.yml").write_text(
        yaml.safe_dump({"inherits": [{"source": "nolte-shared", "ref": "v0.1.9"}]}), encoding="utf-8")
    (consumer / ".claude-plugin").mkdir()
    (consumer / ".claude-plugin" / "plugin.json").write_text("{}", encoding="utf-8")
    make_spec(consumer / "spec", "project/branching-model", scope="local", section="Branch roles")
    findings = csi.run(consumer, hub)
    assert "malformed-config" not in codes(findings)
    # The default "en" still finds the shadowing spec on both sides.
    assert "undeclared-divergence" in codes(findings)
