"""Tests for the boot-protocol schemas (#733, v1.1 for #728, v1.2 for #737) and the v1.1 and v1.2 declaration schemas (#740).

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
PROTOCOL_V12_SCHEMA_PATH = REPO_ROOT / "schemas" / "image-boot-protocol-v1.2.schema.yaml"
PROTOCOL_V12_SCHEMA = yaml.safe_load(PROTOCOL_V12_SCHEMA_PATH.read_text(encoding="utf-8"))
PASS_V12, FAIL_V12, NOT_RUN_V12, FAIL_NO_REPORT_V12 = PROTOCOL_V12_SCHEMA["examples"]
UPDATE_SECURITY = ["downgrade", "signature-rejection", "commit-boundary", "interrupted-update"]

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
# Each name below breaks exactly one part of the pattern: the dot in the
# reverse-domain segment, the item segment, the start anchor, the end anchor,
# the per-segment character class, the line-break guard, the ".." guard, and the "."-segment guard.
for _label, _name in {
    "fw_cfg name without a dot in the reverse domain": "opt/example/x",
    "fw_cfg name without an item segment": "opt/org.example",
    "fw_cfg name with text before opt/": "xopt/org.a/b",
    "fw_cfg name with a trailing slash": "opt/org.a/b/",
    "fw_cfg name with a comma": "opt/org.a/b,c",
    "fw_cfg name with a space": "opt/org.a/b c",
    "fw_cfg name with a trailing line break": "opt/org.a/b\n",
    "fw_cfg name with a dot-dot segment": "opt/org.a/../b",
    "fw_cfg name with a single-dot segment": "opt/org.a/./b",
}.items():
    V12_NEGATIVES[_label] = ((lambda n: lambda d: _switch(d, name=n))(_name), "schema.pattern",
                             "/health/failure_switch/name")


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


@pytest.mark.parametrize("name", ["opt/org.example.gateway/sub/fail", "opt/org.example_gw-1/fail.v2"])
def test_v12_fw_cfg_name_character_class_accepts_valid_names(tmp_path, capsys, name):
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


# --------------------------------------------------------------------------- #
# Protocol v1.2 (#737): the update-security scenarios downgrade,
# signature-rejection, commit-boundary, and interrupted-update; v1.0 and v1.1
# stay valid input against their own schemas
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("example", [PASS_V12, FAIL_V12, NOT_RUN_V12, FAIL_NO_REPORT_V12],
                         ids=["pass", "fail", "not-run", "fail-without-report"])
def test_v12_examples_are_valid(tmp_path, capsys, example):
    # The validator picks v1.2 from schema_version alone: no code change needed.
    code, payload = _run_protocol(tmp_path, example, capsys)
    assert code == 0, payload
    assert Path(payload["schema"]).resolve() == PROTOCOL_V12_SCHEMA_PATH.resolve()


def test_v12_pass_example_covers_every_scenario_with_the_required_set_of_section_h():
    required = {s["name"]: s["required"] for s in PASS_V12["scenarios"]}
    assert required == {"smoke": True, "rollback": True, "positive": False, "identity": False,
                        "downgrade": True, "signature-rejection": True,
                        "commit-boundary": False, "interrupted-update": False}


@pytest.mark.parametrize("example", [PASS, FAIL, NOT_RUN, FAIL_NO_REPORT],
                         ids=["pass", "fail", "not-run", "fail-without-report"])
def test_v11_protocols_still_validate_next_to_v12(tmp_path, capsys, example):
    assert example["schema_version"] == "1.1"
    code, payload = _run_protocol(tmp_path, example, capsys)
    assert code == 0, payload
    assert Path(payload["schema"]).resolve() == PROTOCOL_SCHEMA_PATH.resolve()


@pytest.mark.parametrize("name", UPDATE_SECURITY)
def test_update_security_scenarios_rejected_by_v11(tmp_path, capsys, name):
    # v1.1 is not edited in place: the new names exist only under schema_version "1.2".
    def rename(doc):
        _scenario(doc, "identity")["name"] = name
    code, payload = _run_protocol(tmp_path, _mutate(PASS, rename), capsys)
    assert code == 1 and payload["result"] == "invalid"
    assert Path(payload["schema"]).resolve() == PROTOCOL_SCHEMA_PATH.resolve()


def _set(name: str, key: str, value):
    return lambda d: _scenario(d, name).__setitem__(key, value)


def _drop(name: str, key: str):
    return lambda d: _scenario(d, name).pop(key)


def _duplicate(name: str):
    def fn(doc):
        doc["scenarios"].append(copy.deepcopy(_scenario(doc, name)))
    return fn


def _variant(doc: dict, name: str) -> dict:
    return next(v for v in _scenario(doc, "signature-rejection")["signature_variants"] if v["name"] == name)


def _fail_overall(doc: dict, name: str) -> None:
    doc["outcome"] = {"overall_verdict": "fail", "exit_status": 1}
    _scenario(doc, name)["verdict"] = "fail"


def _drop_passes(doc: dict, names: list) -> None:
    # Mark the named scenarios not-run, so the protocol carries no pass of them.
    for name in names:
        s = _scenario(doc, name)
        s.update(verdict="not-run", not_run_cause={"reason": "excluded by the operator",
                                                    "install_hint": {"status": "unavailable", "reason": "n/a"}})
    doc["outcome"] = {"overall_verdict": "not-run", "exit_status": 2}


V12_PROTOCOL_NEGATIVES = {
    "downgrade marked recommended": _set("downgrade", "required", False),
    "signature-rejection marked recommended": _set("signature-rejection", "required", False),
    "commit-boundary marked required": _set("commit-boundary", "required", True),
    "interrupted-update marked required": _set("interrupted-update", "required", True),
    "downgrade without observed versions": _drop("downgrade", "observed_versions"),
    "signature-rejection without its variants": _drop("signature-rejection", "signature_variants"),
    "commit-boundary without observed versions": _drop("commit-boundary", "observed_versions"),
    "interrupted-update without its interruption": _drop("interrupted-update", "interruption"),
    "downgrade pass without a contacted source": _set("downgrade", "source_requests", 0),
    "signature-rejection with scenario-level source requests": _set("signature-rejection", "source_requests", 1),
    "signature variants on downgrade": lambda d: _scenario(d, "downgrade").__setitem__(
        "signature_variants", copy.deepcopy(_scenario(d, "signature-rejection")["signature_variants"])),
    "untrusted-key variant pass without a contacted source": lambda d: _variant(d, "untrusted-key").__setitem__(
        "source_requests", 0),
    "unsigned variant pass with unavailable observed versions": lambda d: _variant(d, "unsigned").__setitem__(
        "observed_versions", {"status": "unavailable", "reason": "log lost"}),
    "signature-rejection pass with the untrusted-key variant not-run": lambda d: _variant(
        d, "untrusted-key").update(verdict="not-run", reason="test payload not given"),
    "signature-rejection pass with the unsigned variant not-run": lambda d: _variant(
        d, "unsigned").update(verdict="not-run", reason="unsigned payload not given"),
    "signature-rejection pass with a failing unsigned variant": lambda d: _variant(d, "unsigned").__setitem__(
        "verdict", "fail"),
    "untrusted-key variant not-producible": lambda d: _variant(d, "untrusted-key").update(
        verdict="not-producible", reason="format"),
    "not-producible variant without a reason": lambda d: _variant(d, "unsigned").__setitem__(
        "verdict", "not-producible"),
    "passing variant with a reason": lambda d: _variant(d, "unsigned").__setitem__("reason", "x"),
    "duplicate untrusted-key variant": lambda d: _scenario(d, "signature-rejection")["signature_variants"].__setitem__(
        1, copy.deepcopy(_variant(d, "untrusted-key"))),
    "single signature variant": lambda d: _scenario(d, "signature-rejection")["signature_variants"].pop(),
    "signature-rejection fail without a failing variant": lambda d: _fail_overall(d, "signature-rejection"),
    "downgrade pass without a positive control": lambda d: _drop_passes(
        d, ["rollback", "positive", "commit-boundary", "signature-rejection"]),
    "signature-rejection pass without a positive control": lambda d: _drop_passes(
        d, ["rollback", "positive", "commit-boundary", "downgrade"]),
    "commit-boundary pass without a positive pass": lambda d: _drop_passes(d, ["positive"]),
    "commit-boundary fail without a positive pass": lambda d: (_drop_passes(d, ["positive"]), _fail_overall(
        d, "commit-boundary")),
    "duplicate signature-rejection": _duplicate("signature-rejection"),
    "duplicate commit-boundary": _duplicate("commit-boundary"),
    "missing unsigned_payload": lambda d: d.pop("unsigned_payload"),
    "unsigned payload without its production": lambda d: d["unsigned_payload"].pop("production"),
    "interrupted-update pass without a contacted source": _set("interrupted-update", "source_requests", 0),
    "downgrade pass with unavailable observed versions": _set(
        "downgrade", "observed_versions", {"status": "unavailable", "reason": "log lost"}),
    "commit-boundary pass with unavailable observed versions": _set(
        "commit-boundary", "observed_versions", {"status": "unavailable", "reason": "log lost"}),
    "commit-boundary with a forwarded network": lambda d: _scenario(d, "commit-boundary").__setitem__(
        "network", copy.deepcopy(_scenario(d, "downgrade")["network"])),
    "downgrade without a network device": _set("downgrade", "network", {"mode": "none", "config": "-nic none"}),
    "commit-boundary with source requests": _set("commit-boundary", "source_requests", 1),
    "interruption on downgrade": _set("downgrade", "interruption", {"trigger": "payload-delivered", "after_s": 0}),
    "observed versions on smoke": _set("smoke", "observed_versions", ["1.4.0"]),
    "source requests on rollback": _set("rollback", "source_requests", 1),
    "duplicate downgrade": _duplicate("downgrade"),
    "duplicate interrupted-update": _duplicate("interrupted-update"),
    "unknown interruption trigger": _set("interrupted-update", "interruption",
                                         {"trigger": "download-started", "after_s": 0}),
    "missing test_payload": lambda d: d.pop("test_payload"),
    "missing previous_artifact": lambda d: d.pop("previous_artifact"),
    "test payload without its production": lambda d: d["test_payload"].pop("production"),
    "test payload without its signing key": lambda d: d["test_payload"].pop("signing_key"),
    "missing update_window timeout": lambda d: d["timeouts"].pop("update_window"),
    "missing recovery timeout": lambda d: d["timeouts"].pop("recovery"),
}


@pytest.mark.parametrize("case", list(V12_PROTOCOL_NEGATIVES), ids=list(V12_PROTOCOL_NEGATIVES))
def test_v12_protocol_negatives(tmp_path, capsys, case):
    code, payload = _run_protocol(tmp_path, _mutate(PASS_V12, V12_PROTOCOL_NEGATIVES[case]), capsys)
    assert code == 1 and payload["result"] == "invalid", payload
    assert Path(payload["schema"]).resolve() == PROTOCOL_V12_SCHEMA_PATH.resolve()


def test_v12_not_run_downgrade_with_unavailable_observations_is_valid(tmp_path, capsys):
    # A not-run update-security scenario records its observations as unavailable.
    (downgrade,) = [s for s in NOT_RUN_V12["scenarios"] if s["name"] == "downgrade"]
    assert downgrade["verdict"] == "not-run"
    assert downgrade["observed_versions"]["status"] == "unavailable"
    code, payload = _run_protocol(tmp_path, NOT_RUN_V12, capsys)
    assert code == 0, payload


def test_v12_fail_downgrade_without_a_contacted_source_is_valid(tmp_path, capsys):
    # The request minimum binds pass only: N may fail its own smoke assertions before any request.
    def fail(doc):
        doc["outcome"] = {"overall_verdict": "fail", "exit_status": 1}
        s = _scenario(doc, "downgrade")
        s["verdict"] = "fail"
        s["source_requests"] = 0
    code, payload = _run_protocol(tmp_path, _mutate(PASS_V12, fail), capsys)
    assert code == 0, payload


def test_v12_test_payload_example_names_its_production():
    payload = PASS_V12["test_payload"]
    assert payload["production"] and payload["signing_key"]
    assert payload["path"] != PASS_V12["next_artifact"]["path"]


def test_v12_unsigned_variant_not_producible_still_lets_signature_rejection_pass(tmp_path, capsys):
    # The unsigned variant may be not-producible with a reason; the untrusted-key variant still has to pass.
    doc = _mutate(PASS_V12, lambda d: _variant(d, "unsigned").update(
        verdict="not-producible", reason="payload format requires a signature",
        observed_versions={"status": "unavailable", "reason": "not produced"},
        source_requests={"status": "unavailable", "reason": "not produced"}))
    code, payload = _run_protocol(tmp_path, doc, capsys)
    assert code == 0, payload


def test_v12_signature_rejection_fail_with_a_failing_variant_is_valid(tmp_path, capsys):
    def fail(doc):
        _fail_overall(doc, "signature-rejection")
        _variant(doc, "unsigned")["verdict"] = "fail"
    code, payload = _run_protocol(tmp_path, _mutate(PASS_V12, fail), capsys)
    assert code == 0, payload


def test_v12_positive_control_from_positive_alone_is_enough(tmp_path, capsys):
    # A rollback not-run leaves the positive pass as the control for downgrade and signature-rejection.
    code, payload = _run_protocol(tmp_path, _mutate(PASS_V12, lambda d: _drop_passes(d, ["rollback"])), capsys)
    assert code == 0, payload
