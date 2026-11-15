"""Tests for the boot-protocol schemas (#733, v1.1 for #728) and the v1.1 and v1.2 declaration schemas (#740).

Both go through the existing bundled validator
(``plugins/nolte-linux/skills/linux-image-audit/scripts/validate_declaration.py``):
``--kind boot-protocol`` for ``protocol.json``, the default kind for
``image-declaration.yaml``. The negatives pin the contract of
``spec/project/image-boot-verification/`` §G: an uncollectable field takes its
collected type or ``unavailable`` with a reason, never ``null`` and never
omission, and ``exit_status`` matches ``overall_verdict``.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "plugins" / "nolte-linux" / "skills" / "linux-image-audit" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import validate_declaration as vd  # noqa: E402

PROTOCOL_SCHEMA_PATH = REPO_ROOT / "schemas" / "image-boot-protocol-v1.1.schema.yaml"
PROTOCOL_SCHEMA = yaml.safe_load(PROTOCOL_SCHEMA_PATH.read_text(encoding="utf-8"))
PASS, FAIL, NOT_RUN, FAIL_NO_REPORT = PROTOCOL_SCHEMA["examples"]
PROTOCOL_V10_SCHEMA_PATH = REPO_ROOT / "schemas" / "image-boot-protocol-v1.0.schema.yaml"
PROTOCOL_V10_SCHEMA = yaml.safe_load(PROTOCOL_V10_SCHEMA_PATH.read_text(encoding="utf-8"))
PASS_V10, FAIL_V10, NOT_RUN_V10 = PROTOCOL_V10_SCHEMA["examples"]

DECL_V10_PATH = REPO_ROOT / "schemas" / "image-declaration-v1.0.schema.yaml"
DECL_V11_PATH = REPO_ROOT / "schemas" / "image-declaration-v1.1.schema.yaml"
DECL_V10 = yaml.safe_load(DECL_V10_PATH.read_text(encoding="utf-8"))
DECL_V11 = yaml.safe_load(DECL_V11_PATH.read_text(encoding="utf-8"))
UEFI_X86, UBOOT_ARM = DECL_V11["examples"]
DECL_V12_PATH = REPO_ROOT / "schemas" / "image-declaration-v1.2.schema.yaml"
DECL_V12 = yaml.safe_load(DECL_V12_PATH.read_text(encoding="utf-8"))
V12_UEFI, V12_UBOOT_REFLASH, V12_UBOOT_FW_CFG, V12_UBOOT_SYSTEMD = DECL_V12["examples"]


def _run_protocol(tmp_path: Path, doc, capsys, *extra: str) -> tuple[int, dict]:
    path = tmp_path / "protocol.json"
    path.write_text(doc if isinstance(doc, str) else json.dumps(doc, indent=2), encoding="utf-8")
    code = vd.main(["--kind", "boot-protocol", str(path), *extra])
    return code, json.loads(capsys.readouterr().out)


def _run_declaration(tmp_path: Path, doc, capsys) -> tuple[int, dict]:
    path = tmp_path / "image-declaration.yaml"
    path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
    code = vd.main([str(path)])
    return code, json.loads(capsys.readouterr().out)


def _mutate(base: dict, fn) -> dict:
    doc = copy.deepcopy(base)
    fn(doc)
    return doc


def _hits(payload: dict, rule: str, path: str) -> bool:
    return any(v["rule"] == rule and v["path"] == path for v in payload["violations"])


# --------------------------------------------------------------------------- #
# Boot protocol: the four examples validate through the validator
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("example", [PASS, FAIL, NOT_RUN, FAIL_NO_REPORT],
                         ids=["pass", "fail", "not-run", "fail-without-report"])
def test_protocol_examples_are_valid(tmp_path, capsys, example):
    code, payload = _run_protocol(tmp_path, example, capsys)
    assert code == 0, payload
    assert payload["result"] == "valid"
    assert Path(payload["schema"]).resolve() == PROTOCOL_SCHEMA_PATH.resolve()


def test_examples_cover_every_overall_verdict():
    verdicts = [e["outcome"]["overall_verdict"] for e in PROTOCOL_SCHEMA["examples"]]
    assert verdicts == ["pass", "fail", "not-run", "fail"]


def test_not_run_example_marks_uncollected_fields_unavailable():
    assert NOT_RUN["hypervisor"]["name"]["status"] == "unavailable"
    assert NOT_RUN["serial_logs"]["status"] == "unavailable"
    assert all(s["verdict"] == "not-run" and s["not_run_cause"]["reason"] for s in NOT_RUN["scenarios"])


# --------------------------------------------------------------------------- #
# Boot protocol: the negatives of #733 and the §B/§G shape rules
# --------------------------------------------------------------------------- #
def _set_unavailable_reason(doc):
    doc["tpm_emulated"] = {"status": "unavailable", "reason": ""}


def _forward_missing(doc):
    del doc["scenarios"][1]["network"]["forward"]


PROTOCOL_NEGATIVES = {
    "missing firmware": (PASS, lambda d: d.pop("firmware"), "schema.required", "/"),
    "verdict: passed": (PASS, lambda d: d["scenarios"][0].__setitem__("verdict", "passed"),
                        "schema.enum", "/scenarios/0/verdict"),
    "field set to null": (PASS, lambda d: d.__setitem__("tpm_emulated", None), "schema.oneOf", "/tpm_emulated"),
    "nested field set to null": (NOT_RUN, lambda d: d["hypervisor"].__setitem__("version", None),
                                 "schema.oneOf", "/hypervisor/version"),
    "exit_status 0 with overall_verdict fail": (
        FAIL, lambda d: d["outcome"].__setitem__("exit_status", 0), "schema.enum", "/outcome"),
    "uncollectable field omitted": (NOT_RUN, lambda d: d["host"].pop("kernel"), "schema.required", "/host"),
    "unavailable without a reason": (NOT_RUN, _set_unavailable_reason, "schema.oneOf", "/tpm_emulated"),
    "not-run scenario without its cause": (NOT_RUN, lambda d: d["scenarios"][0].pop("not_run_cause"),
                                           "schema.required", "/scenarios/0"),
    "pass scenario with a not-run cause": (
        PASS, lambda d: d["scenarios"][0].__setitem__("not_run_cause", NOT_RUN["scenarios"][0]["not_run_cause"]),
        "schema.not", "/scenarios/0"),
    "restricted network without its endpoint": (PASS, _forward_missing, "schema.oneOf", "/scenarios/1/network"),
    "emulation factor below 5": (FAIL, lambda d: d["acceleration"].__setitem__("timeout_factor", 2),
                                 "schema.oneOf", "/acceleration"),
    "report line without the anchor": (PASS, lambda d: d["scenarios"][0]["report_lines"].__setitem__(
        0, "login: IMAGE-HEALTH-REPORT status=healthy"), "schema.pattern", "/scenarios/0/report_lines/0"),
    "abbreviated commit": (PASS, lambda d: d.__setitem__("image_definition_commit", "605926fb"),
                           "schema.oneOf", "/image_definition_commit"),
    "unknown firmware type": (PASS, lambda d: d["firmware"].__setitem__("type", "coreboot"),
                              "schema.oneOf", "/firmware/type"),
}


@pytest.mark.parametrize("case", list(PROTOCOL_NEGATIVES), ids=list(PROTOCOL_NEGATIVES))
def test_protocol_negatives(tmp_path, capsys, case):
    base, fn, rule, path = PROTOCOL_NEGATIVES[case]
    code, payload = _run_protocol(tmp_path, _mutate(base, fn), capsys)
    assert code == 1 and payload["result"] == "invalid"
    assert _hits(payload, rule, path), payload


def test_protocol_violation_carries_line(tmp_path, capsys):
    code, payload = _run_protocol(tmp_path, _mutate(PASS, lambda d: d["scenarios"][0].__setitem__(
        "verdict", "passed")), capsys)
    assert code == 1
    hit = next(v for v in payload["violations"] if v["path"] == "/scenarios/0/verdict")
    assert isinstance(hit.get("line"), int)


# --------------------------------------------------------------------------- #
# Boot protocol: the shared guards of the validator
# --------------------------------------------------------------------------- #
def test_protocol_duplicate_key_is_invalid(tmp_path, capsys):
    text = json.dumps(FAIL)[:-1] + ', "schema_version": "1.1"}'
    code, payload = _run_protocol(tmp_path, text, capsys)
    assert code == 1 and {v["rule"] for v in payload["violations"]} == {"json.duplicate-key"}


def test_protocol_nan_is_invalid(tmp_path, capsys):
    text = json.dumps(FAIL).replace('"timeout_factor": 5', '"timeout_factor": NaN')
    assert "NaN" in text
    code, payload = _run_protocol(tmp_path, text, capsys)
    assert code == 1 and {v["rule"] for v in payload["violations"]} == {"json.parse"}


def test_protocol_unparseable_is_invalid(tmp_path, capsys):
    code, payload = _run_protocol(tmp_path, '{"schema_version": "1.0",\n', capsys)
    assert code == 1 and payload["violations"][0]["rule"] == "json.parse"
    assert payload["violations"][0]["line"] == 2


def test_protocol_deep_nesting_is_invalid(tmp_path, capsys):
    code, payload = _run_protocol(tmp_path, "[" * 100000 + "]" * 100000, capsys)
    assert code == 1 and {v["rule"] for v in payload["violations"]} <= {"json.depth", "json.parse"}


def test_protocol_oversized_is_invalid(tmp_path, capsys):
    code, payload = _run_protocol(tmp_path, " " * (vd.MAX_BYTES + 1), capsys)
    assert code == 1 and {v["rule"] for v in payload["violations"]} == {"protocol.too-large"}


def test_protocol_unknown_schema_version_is_invalid(tmp_path, capsys):
    code, payload = _run_protocol(tmp_path, _mutate(PASS, lambda d: d.__setitem__("schema_version", "9.9")), capsys)
    assert code == 1 and {v["rule"] for v in payload["violations"]} == {"schema_version.unknown"}


def test_protocol_without_reachable_schema_is_not_decidable(tmp_path, capsys, monkeypatch):
    # A declaration schema alone isn't a protocol schema corpus.
    schemas = tmp_path / "schemas"
    schemas.mkdir()
    (schemas / "image-declaration-v1.0.schema.yaml").write_text(DECL_V10_PATH.read_text(encoding="utf-8"),
                                                                encoding="utf-8")
    monkeypatch.setattr(vd, "installed_schema_dirs", lambda: [schemas])
    code, payload = _run_protocol(tmp_path, PASS, capsys)
    assert code == 2 and payload["result"] == "not-decidable"
    assert "image-boot-protocol" in payload["cause"]


def test_audited_repository_protocol_schema_is_never_used(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "schemas").mkdir()
    (tmp_path / "schemas" / "image-boot-protocol-v1.1.schema.yaml").write_text("{}\n", encoding="utf-8")
    code, payload = _run_protocol(tmp_path, _mutate(PASS, lambda d: d.pop("firmware")), capsys)
    assert code == 1
    assert Path(payload["schema"]).resolve() == PROTOCOL_SCHEMA_PATH.resolve()


# --------------------------------------------------------------------------- #
# Declaration v1.1 (#740 part a)
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("example", [UEFI_X86, UBOOT_ARM], ids=["uefi-x86_64", "u-boot-aarch64"])
def test_v11_examples_are_valid(tmp_path, capsys, example):
    code, payload = _run_declaration(tmp_path, example, capsys)
    assert code == 0, payload
    assert Path(payload["schema"]).resolve() == DECL_V11_PATH.resolve()


@pytest.mark.parametrize("example", DECL_V10["examples"], ids=["field-updated", "reflash-only"])
def test_v10_declarations_still_validate(tmp_path, capsys, example):
    code, payload = _run_declaration(tmp_path, example, capsys)
    assert code == 0, payload
    assert Path(payload["schema"]).resolve() == DECL_V10_PATH.resolve()


V11_NEGATIVES = {
    "unknown firmware": (lambda d: d["image"].__setitem__("firmware", "coreboot"), "schema.enum", "/image/firmware"),
    "missing firmware": (lambda d: d["image"].pop("firmware"), "schema.required", "/image"),
    "missing architectures": (lambda d: d["image"].pop("architectures"), "schema.required", "/image"),
    "empty architectures": (lambda d: d["image"].__setitem__("architectures", []), "schema.minItems",
                            "/image/architectures"),
    "unknown architecture": (lambda d: d["image"].__setitem__("architectures", ["amd64"]), "schema.enum",
                             "/image/architectures/0"),
    "duplicate architecture": (lambda d: d["image"].__setitem__("architectures", ["x86_64", "x86_64"]),
                               "schema.uniqueItems", "/image/architectures"),
}


@pytest.mark.parametrize("case", list(V11_NEGATIVES), ids=list(V11_NEGATIVES))
def test_v11_negatives(tmp_path, capsys, case):
    fn, rule, path = V11_NEGATIVES[case]
    code, payload = _run_declaration(tmp_path, _mutate(UEFI_X86, fn), capsys)
    assert code == 1 and payload["result"] == "invalid"
    assert _hits(payload, rule, path), payload


def test_v11_conditional_rules_still_apply(tmp_path, capsys):
    code, payload = _run_declaration(tmp_path, _mutate(UEFI_X86, lambda d: d.pop("update")), capsys)
    assert code == 1 and _hits(payload, vd.RULE_UPDATE, "/update_model")


def test_v11_firmware_fields_rejected_by_v10(tmp_path, capsys):
    # v1.0 stays untouched: the new fields aren't admitted under schema_version "1.0".
    doc = _mutate(UEFI_X86, lambda d: d.__setitem__("schema_version", "1.0"))
    code, payload = _run_declaration(tmp_path, doc, capsys)
    assert code == 1 and _hits(payload, "schema.additionalProperties", "/image")


# --------------------------------------------------------------------------- #
# Declaration v1.2 (#740 part b): the qemu-fw-cfg switch transport for U-Boot
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("example", DECL_V12["examples"],
                         ids=["uefi-x86_64", "u-boot-reflash-only", "u-boot-qemu-fw-cfg", "u-boot-systemd-credential"])
def test_v12_examples_are_valid(tmp_path, capsys, example):
    # The validator picks v1.2 from schema_version alone: no code change needed.
    code, payload = _run_declaration(tmp_path, example, capsys)
    assert code == 0, payload
    assert payload["result"] == "valid"
    assert Path(payload["schema"]).resolve() == DECL_V12_PATH.resolve()


def test_v12_examples_cover_both_u_boot_switch_types():
    assert V12_UBOOT_FW_CFG["image"]["firmware"] == "u-boot"
    assert {V12_UBOOT_FW_CFG["health"]["failure_switch"]["type"],
            V12_UBOOT_FW_CFG["update"]["source_switch"]["type"]} == {"qemu-fw-cfg"}
    assert V12_UBOOT_SYSTEMD["image"]["firmware"] == "u-boot"
    assert {V12_UBOOT_SYSTEMD["health"]["failure_switch"]["type"],
            V12_UBOOT_SYSTEMD["update"]["source_switch"]["type"]} == {"systemd-credential"}


@pytest.mark.parametrize("example", DECL_V11["examples"], ids=["uefi-x86_64", "u-boot-aarch64"])
def test_v11_declarations_still_validate_next_to_v12(tmp_path, capsys, example):
    code, payload = _run_declaration(tmp_path, example, capsys)
    assert code == 0, payload
    assert Path(payload["schema"]).resolve() == DECL_V11_PATH.resolve()


def _switch(doc: dict, **fields) -> None:
    doc["health"]["failure_switch"].update(fields)


V12_NEGATIVES = {
    "unknown switch type": (lambda d: _switch(d, type="kernel-cmdline"), "schema.enum",
                            "/health/failure_switch/type"),
    "fw_cfg name without opt/ prefix": (lambda d: _switch(d, name="org.example.gateway/fail"), "schema.pattern",
                                        "/health/failure_switch/name"),
    "fw_cfg name under the QEMU-reserved prefix": (lambda d: _switch(d, name="opt/org.qemu/fail"), "schema.pattern",
                                                   "/health/failure_switch/name"),
    "fw_cfg name over 55 characters": (lambda d: _switch(d, name="opt/org.example.gateway/" + "x" * 32),
                                       "schema.maxLength", "/health/failure_switch/name"),
}


@pytest.mark.parametrize("case", list(V12_NEGATIVES), ids=list(V12_NEGATIVES))
def test_v12_negatives(tmp_path, capsys, case):
    fn, rule, path = V12_NEGATIVES[case]
    code, payload = _run_declaration(tmp_path, _mutate(V12_UBOOT_FW_CFG, fn), capsys)
    assert code == 1 and payload["result"] == "invalid"
    assert _hits(payload, rule, path), payload


def test_v12_fw_cfg_name_at_55_characters_is_valid(tmp_path, capsys):
    name = "opt/org.example.gateway/" + "x" * 31
    assert len(name) == 55
    code, payload = _run_declaration(tmp_path, _mutate(V12_UBOOT_FW_CFG, lambda d: _switch(d, name=name)), capsys)
    assert code == 0, payload


def test_v12_name_rules_bind_only_qemu_fw_cfg(tmp_path, capsys):
    # A systemd credential keeps its plain name; the opt/ pattern applies to qemu-fw-cfg only.
    code, payload = _run_declaration(tmp_path, V12_UBOOT_SYSTEMD, capsys)
    assert code == 0, payload
    assert not V12_UBOOT_SYSTEMD["health"]["failure_switch"]["name"].startswith("opt/")


@pytest.mark.parametrize("version,path", [("1.0", DECL_V10_PATH), ("1.1", DECL_V11_PATH)])
def test_qemu_fw_cfg_rejected_by_older_schemas(tmp_path, capsys, version, path):
    base = DECL_V10["examples"][0] if version == "1.0" else UEFI_X86
    doc = _mutate(base, lambda d: _switch(d, type="qemu-fw-cfg", name="opt/org.example.gateway/fail"))
    code, payload = _run_declaration(tmp_path, doc, capsys)
    assert code == 1 and _hits(payload, "schema.enum", "/health/failure_switch/type"), payload
    assert Path(payload["schema"]).resolve() == path.resolve()


# --------------------------------------------------------------------------- #
# Pre-merge review: per-scenario rules the schema now expresses
# --------------------------------------------------------------------------- #
def _scenario(doc: dict, name: str) -> dict:
    return next(s for s in doc["scenarios"] if s["name"] == name)


def test_duplicate_scenario_name_is_invalid(tmp_path, capsys):
    def dup(doc):
        twin = copy.deepcopy(_scenario(doc, "smoke"))
        twin["verdict"] = "fail"
        doc["scenarios"].append(twin)
    code, payload = _run_protocol(tmp_path, _mutate(PASS, dup), capsys)
    assert code == 1 and payload["result"] == "invalid"


def test_pass_with_unavailable_network_is_invalid(tmp_path, capsys):
    def unavailable(doc):
        _scenario(doc, "rollback")["network"] = {"status": "unavailable", "reason": "isolation not established"}
    code, payload = _run_protocol(tmp_path, _mutate(PASS, unavailable), capsys)
    assert code == 1 and payload["result"] == "invalid"


def test_pass_without_report_lines_is_invalid(tmp_path, capsys):
    code, payload = _run_protocol(
        tmp_path, _mutate(PASS, lambda d: _scenario(d, "smoke").__setitem__("report_lines", [])), capsys)
    assert code == 1 and payload["result"] == "invalid"
    assert _hits(payload, "schema.minItems", "/scenarios/0/report_lines"), payload


# --------------------------------------------------------------------------- #
# Protocol v1.1: a fail may carry no report line (§F missing report); v1.0 stays
# accepted against its own schema
# --------------------------------------------------------------------------- #
def test_v11_fail_without_report_lines_is_valid(tmp_path, capsys):
    def no_report(doc):
        smoke = _scenario(doc, "smoke")
        smoke["report_lines"] = []
        smoke["phases"][0]["duration_s"] = {"status": "unavailable", "reason": "no report before the timeout"}
    code, payload = _run_protocol(tmp_path, _mutate(FAIL, no_report), capsys)
    assert code == 0, payload
    assert Path(payload["schema"]).resolve() == PROTOCOL_SCHEMA_PATH.resolve()


def test_v11_fail_example_without_report_is_a_readiness_timeout():
    (smoke,) = FAIL_NO_REPORT["scenarios"]
    assert smoke["verdict"] == "fail" and smoke["report_lines"] == []
    (readiness,) = smoke["phases"]
    assert readiness["name"] == "readiness" and readiness["duration_s"]["status"] == "unavailable"


def test_v11_fail_without_report_lines_still_needs_an_isolated_network(tmp_path, capsys):
    def unavailable(doc):
        _scenario(doc, "smoke")["network"] = {"status": "unavailable", "reason": "isolation not established"}
    code, payload = _run_protocol(tmp_path, _mutate(FAIL_NO_REPORT, unavailable), capsys)
    assert code == 1 and payload["result"] == "invalid"


@pytest.mark.parametrize("example", [PASS_V10, FAIL_V10, NOT_RUN_V10], ids=["pass", "fail", "not-run"])
def test_v10_protocols_still_validate(tmp_path, capsys, example):
    assert example["schema_version"] == "1.0"
    code, payload = _run_protocol(tmp_path, example, capsys)
    assert code == 0, payload
    assert Path(payload["schema"]).resolve() == PROTOCOL_V10_SCHEMA_PATH.resolve()


def test_v10_fail_without_report_lines_stays_invalid_under_v10(tmp_path, capsys):
    # v1.0 is not edited in place: the relaxation exists only under schema_version "1.1".
    code, payload = _run_protocol(
        tmp_path, _mutate(FAIL_V10, lambda d: _scenario(d, "smoke").__setitem__("report_lines", [])), capsys)
    assert code == 1 and payload["result"] == "invalid"
    assert Path(payload["schema"]).resolve() == PROTOCOL_V10_SCHEMA_PATH.resolve()


def test_smoke_with_forwarded_network_is_invalid(tmp_path, capsys):
    def forward(doc):
        _scenario(doc, "smoke")["network"] = copy.deepcopy(_scenario(doc, "rollback")["network"])
    code, payload = _run_protocol(tmp_path, _mutate(PASS, forward), capsys)
    assert code == 1 and payload["result"] == "invalid"


def test_overflowing_float_is_invalid(tmp_path, capsys):
    text = json.dumps(FAIL).replace('"timeout_factor": 5', '"timeout_factor": 1e999')
    assert "1e999" in text
    code, payload = _run_protocol(tmp_path, text, capsys)
    assert code == 1 and payload["result"] == "invalid"
