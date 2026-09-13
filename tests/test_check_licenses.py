"""Tests for scripts/check_licenses.py (#591, defect-class-guards G4)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("check_licenses", ROOT / "scripts" / "check_licenses.py")
gate = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = gate
assert _spec.loader is not None
_spec.loader.exec_module(gate)


def sbom(tmp_path, *ids):
    path = tmp_path / "sbom.cdx.json"
    path.write_text(json.dumps({"components": [{"name": f"c{i}", "licenses": [{"license": {"id": x}}]} for i, x in enumerate(ids)]}))
    return path


def baseline(tmp_path, entries):
    path = tmp_path / "baseline.json"
    path.write_text(json.dumps({"_comment": "test", "adjudicated": entries}))
    return path


def run(tmp_path, sbom_path, baseline_path, *extra):
    return gate.main(["--sbom", str(sbom_path), "--baseline", str(baseline_path), *extra])


def test_covered_identifiers_with_reasons_pass(tmp_path):
    assert run(tmp_path, sbom(tmp_path, "MIT"), baseline(tmp_path, {"MIT": "allow tier"})) == 0


def test_new_identifier_fails(tmp_path):
    assert run(tmp_path, sbom(tmp_path, "MIT", "GPL-3.0-only"), baseline(tmp_path, {"MIT": "allow tier"})) == 1


def test_stale_entry_fails(tmp_path, capsys):
    assert run(tmp_path, sbom(tmp_path, "MIT"), baseline(tmp_path, {"MIT": "allow", "ISC": "allow"})) == 1
    assert "stale (no longer in the SBOM): ISC" in capsys.readouterr().err


def test_entry_without_reason_fails(tmp_path):
    assert run(tmp_path, sbom(tmp_path, "MIT"), baseline(tmp_path, {"MIT": " "})) == 1


def test_prune_removes_only_stale_entries(tmp_path):
    b = baseline(tmp_path, {"MIT": "allow", "ISC": "allow"})
    assert run(tmp_path, sbom(tmp_path, "MIT"), b, "--prune") == 0
    assert json.loads(b.read_text())["adjudicated"] == {"MIT": "allow"}
    assert run(tmp_path, sbom(tmp_path, "MIT"), b) == 0


def test_update_keeps_reasons_and_leaves_new_ones_empty(tmp_path):
    b = baseline(tmp_path, {"MIT": "allow"})
    assert run(tmp_path, sbom(tmp_path, "MIT", "ISC"), b, "--update") == 0
    assert json.loads(b.read_text())["adjudicated"] == {"ISC": "", "MIT": "allow"}
    assert run(tmp_path, sbom(tmp_path, "MIT", "ISC"), b) == 1


def test_list_shaped_baseline_is_rejected(tmp_path):
    with pytest.raises(SystemExit):
        run(tmp_path, sbom(tmp_path, "MIT"), baseline(tmp_path, ["MIT"]))


def test_committed_baseline_gives_every_entry_a_reason():
    entries = json.loads((ROOT / ".audits/license-check/license-baseline.json").read_text())["adjudicated"]
    assert isinstance(entries, dict) and all(str(r).strip() for r in entries.values())
