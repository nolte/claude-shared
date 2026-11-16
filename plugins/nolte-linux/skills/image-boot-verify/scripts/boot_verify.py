#!/usr/bin/env python3
"""Non-interactive boot-verification runner (nolte/claude-shared#728).

Boots a built Linux image under QEMU per ``spec/project/image-boot-verification/``
and exposes the verdict two ways: ``protocol.json`` in the run directory
(``schemas/image-boot-protocol-v1.2.schema.yaml``, validated before hand-off) and
the process exit status (§H): ``0`` pass, ``1`` fail, ``2`` not-run. For an image
updated in the field it also drives the update-security scenarios of §I:
downgrade, signature-rejection, commit-boundary, and interrupted-update.

The run checks every §H precondition first. A missing hypervisor, firmware, TPM
emulator, input, or isolation guarantee makes the affected scenario ``not-run``
with the cause and an install hint; it never boots with open networking and
never returns ``pass`` for a scenario it couldn't verify.

Only a normalised serial-console line that begins with ``IMAGE-HEALTH-REPORT``
and a space is interpreted, and only its key-value fields (§F). Every other
console line is untrusted guest output: it's stored in the serial log and never
acted on.

Stdlib only. The declaration and the protocol are validated by the bundled
``linux-image-audit/scripts/validate_declaration.py`` (a subprocess); the
declaration is loaded with PyYAML only after that validator, which itself needs
PyYAML, has accepted it.

Usage (see ../references/runner.md):
  python3 "${CLAUDE_PLUGIN_ROOT}/skills/image-boot-verify/scripts/boot_verify.py" \\
      --declaration images/app/image-declaration.yaml \\
      --artifact build/app_1.4.0.raw --expected-version 1.4.0 \\
      --commit <40-hex image-definition commit> [--next-artifact ... --next-expected-version ...] \\
      [--previous-artifact ... --previous-expected-version ...] \\
      [--untrusted-payload ... --untrusted-payload-version ... --untrusted-payload-production ... \\
       --untrusted-key-id ...] [--unsigned-payload ... | --unsigned-not-producible REASON]
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import hashlib
import http.server
import json
import os
import platform
import re
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse
import uuid
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = PLUGIN_ROOT / "skills" / "linux-image-audit" / "scripts" / "validate_declaration.py"

UPDATE_SECURITY = ("downgrade", "signature-rejection", "commit-boundary", "interrupted-update")
SCENARIOS = ("smoke", "rollback", "positive", "identity", *UPDATE_SECURITY)
# Every scenario that sets a host switch, so the switch-transport preconditions apply (§H).
SWITCH_SCENARIOS = ("rollback", "positive", *UPDATE_SECURITY)
DEFAULT_TRACE_IDS = {
    "smoke": "linux-image-best-practices §A health definition",
    "rollback": "linux-image-best-practices §F rollback",
    "positive": "linux-image-best-practices §F update",
    "identity": "linux-image-best-practices §D machine identity",
    "downgrade": "linux-image-best-practices §F downgrade refusal",
    "signature-rejection": "linux-image-best-practices §F payload signature",
    "commit-boundary": "linux-image-best-practices §F failure switch ignored once committed",
    "interrupted-update": "linux-image-best-practices §F atomic update",
}
SIGNATURE_VARIANTS = ("untrusted-key", "unsigned")
REPORT_PREFIX = "IMAGE-HEALTH-REPORT "
REPORT_KEYS = ("status", "image_id", "image_version", "system_state", "failed_units", "machine_id_app")
MAX_REPORT_CHARS = 4096
MAX_PARTIAL_LINE = 1 << 16
POLL_INTERVAL_S = 0.2  # condition polling while waiting for a report, not a fixed delay (§C)

# §L reference profile.
QEMU_TARGET = {"x86_64": "x86_64", "aarch64": "aarch64", "armv7l": "arm", "riscv64": "riscv64",
               "ppc64le": "ppc64", "s390x": "s390x"}
MACHINE_TYPE = {"x86_64": "q35", "aarch64": "virt", "armv7l": "virt", "riscv64": "virt",
                "ppc64le": "pseries", "s390x": "s390-ccw-virtio"}
QEMU_PACKAGE = {"x86_64": "qemu-system-x86", "aarch64": "qemu-system-arm", "armv7l": "qemu-system-arm",
                "riscv64": "qemu-system-misc", "ppc64le": "qemu-system-ppc", "s390x": "qemu-system-s390x"}
UEFI_FIRMWARE = {  # (code, vars template) candidates, Debian/Ubuntu, Fedora, Arch layouts
    "x86_64": [("/usr/share/OVMF/OVMF_CODE_4M.fd", "/usr/share/OVMF/OVMF_VARS_4M.fd"),
               ("/usr/share/OVMF/OVMF_CODE.fd", "/usr/share/OVMF/OVMF_VARS.fd"),
               ("/usr/share/edk2/ovmf/OVMF_CODE.fd", "/usr/share/edk2/ovmf/OVMF_VARS.fd"),
               ("/usr/share/edk2/x64/OVMF_CODE.4m.fd", "/usr/share/edk2/x64/OVMF_VARS.4m.fd")],
    "aarch64": [("/usr/share/AAVMF/AAVMF_CODE.fd", "/usr/share/AAVMF/AAVMF_VARS.fd"),
                ("/usr/share/edk2/aarch64/QEMU_EFI-pflash.raw", "/usr/share/edk2/aarch64/vars-template-pflash.raw")],
    "armv7l": [("/usr/share/AAVMF/AAVMF32_CODE.fd", "/usr/share/AAVMF/AAVMF32_VARS.fd")],
    "riscv64": [("/usr/share/qemu-efi-riscv64/RISCV_VIRT_CODE.fd", "/usr/share/qemu-efi-riscv64/RISCV_VIRT_VARS.fd")],
}
UEFI_PACKAGE = {"x86_64": "ovmf", "aarch64": "qemu-efi-aarch64", "armv7l": "qemu-efi-arm",
                "riscv64": "qemu-efi-riscv64"}
UBOOT_FIRMWARE = {"aarch64": ["/usr/lib/u-boot/qemu_arm64/u-boot.bin"],
                  "armv7l": ["/usr/lib/u-boot/qemu_arm/u-boot.bin"]}
GUEST_FORWARD = ("10.0.2.100", 8080)
DEFAULT_TIMEOUTS = {"readiness": 300.0, "update_installation": 600.0, "update_window": 600.0, "total_margin": 120.0}
MIN_EMULATION_FACTOR = 5.0
EXIT_STATUS = {"pass": 0, "fail": 1, "not-run": 2}
VERDICT_RANK = {"pass": 0, "not-run": 1, "fail": 2}
COMMIT_RE = re.compile(r"^([0-9a-f]{40}|[0-9a-f]{64})$")
MACHINE_ID_RE = re.compile(r"[0-9a-f]{32}|-")
QCOW2_MAGIC = b"QFI\xfb"
QCOW2_EXTERNAL_DATA_FILE = 1 << 2  # incompatible-feature bit, header version 3
STOP_GRACE_S = 10.0  # after QMP quit, before SIGTERM to the process group
STOP_TERM_S = 5.0  # after SIGTERM, before SIGKILL
INTERRUPT_SIGNALS = (signal.SIGTERM, signal.SIGHUP)
_received_signals: list[int] = []  # filled by the signal handler, read at the polling points
# §H switch-transport check 5: the QEMU fw_cfg transport is prepared but no real
# run has confirmed it yet, so no verdict rests on it.
SWITCH_UNVERIFIED_REASON = ("switch transport unverified until a real run confirms it (#728) "
                            "(spec/project/image-boot-verification/ §H)")
UBOOT_SWITCH_REASON = SWITCH_UNVERIFIED_REASON
UBOOT_UUID_REASON = ("no machine-UUID transport is established for u-boot firmware "
                     "(spec/project/image-boot-verification/ §H, §I, #740)")
NO_TOOL = "no tool closes the gap"
# §H, §I: the not-run cases the update-security scenarios name, verbatim.
NO_CONTROL_REASON = "no positive control: neither rollback nor positive passed"
NOT_CONTACTED_REASON = "update source not contacted within the update window"
NO_COMMIT_REASON = "no committed version: positive scenario didn't pass"


def unavailable(reason: str) -> dict:
    return {"status": "unavailable", "reason": reason}


# --------------------------------------------------------------------------- #
# Pure: report-line parsing (§F)
# --------------------------------------------------------------------------- #
_ESCAPES = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)|\x1b[@-_]")
_CONTROL = re.compile(r"[\x00-\x1f\x7f]")


def normalise_line(raw: str) -> str:
    """Strip terminal escape sequences, a trailing CR, and other control characters."""
    return _CONTROL.sub("", _ESCAPES.sub("", raw).rstrip("\r"))


@dataclasses.dataclass(frozen=True)
class Report:
    line: str
    fields: dict
    error: str | None = None

    def get(self, key: str) -> str | None:
        return self.fields.get(key)


def parse_report_line(line: str) -> Report | None:
    """Return the report a normalised line carries, or None when it isn't one.

    A line is a report only when it *begins* with ``IMAGE-HEALTH-REPORT `` (§F);
    the string anywhere else is console text. A report that lacks a field or
    repeats one is still a report, with ``error`` set, so it fails rather than
    being silently skipped.
    """
    if not line.startswith(REPORT_PREFIX):
        return None
    if len(line) > MAX_REPORT_CHARS:
        return Report(line[:MAX_REPORT_CHARS], {}, f"report line longer than {MAX_REPORT_CHARS} characters")
    fields: dict[str, str] = {}
    for token in line[len(REPORT_PREFIX):].split():
        key, sep, value = token.partition("=")
        if not sep or not key:
            return Report(line, fields, f"malformed token {token!r}")
        if key in fields:
            return Report(line, fields, f"field {key!r} repeated")
        fields[key] = value
    missing = [k for k in REPORT_KEYS if not fields.get(k)]
    if missing:
        return Report(line, fields, f"missing field(s) {', '.join(missing)}")
    if fields["status"] not in ("healthy", "unhealthy"):
        return Report(line, fields, f"status {fields['status']!r} is neither healthy nor unhealthy")
    return Report(line, fields)


def extract_reports(lines) -> list[Report]:
    """The reports among raw console lines, in order; everything else is ignored."""
    out = []
    for raw in lines:
        report = parse_report_line(normalise_line(raw))
        if report is not None:
            out.append(report)
    return out


def check_report(report: Report, *, image_name: str, expected_version: str,
                 tolerated_units=(), framework_hook: bool = False,
                 expect_status: str = "healthy") -> list[str]:
    """The §F assertions on one report; an empty list means they hold."""
    if report.error:
        return [f"malformed report: {report.error}"]
    problems = []
    if report.get("status") != expect_status:
        problems.append(f"status={report.get('status')}, expected {expect_status}")
    if report.get("image_id") != image_name:
        problems.append(f"image_id={report.get('image_id')}, expected {image_name}")
    if report.get("image_version") != expected_version:
        problems.append(f"image_version={report.get('image_version')}, expected {expected_version}")
    if expect_status != "healthy" or problems:
        return problems
    state = report.get("system_state")
    if state == "-":
        if not framework_hook:
            problems.append("system_state=- is accepted only for a framework-hook health definition")
    elif state not in ("starting", "running", "degraded"):
        problems.append(f"system_state={state} isn't starting, running, or degraded")
    failed = report.get("failed_units")
    if failed != "-":
        intolerable = [u for u in failed.split(",") if u not in set(tolerated_units)]
        if intolerable:
            problems.append(f"failed unit(s) not tolerated: {', '.join(intolerable)}")
    return problems


# --------------------------------------------------------------------------- #
# Pure: network isolation (§B) and the QEMU command line (§L)
# --------------------------------------------------------------------------- #
@dataclasses.dataclass(frozen=True)
class Forward:
    host_port: int
    guest_address: str = GUEST_FORWARD[0]
    guest_port: int = GUEST_FORWARD[1]
    host_address: str = "127.0.0.1"

    @property
    def guestfwd(self) -> str:
        return f"tcp:{self.guest_address}:{self.guest_port}-tcp:{self.host_address}:{self.host_port}"

    @property
    def url(self) -> str:
        return f"http://{self.guest_address}:{self.guest_port}/"

    def record(self) -> dict:
        return {"protocol": "tcp", "guest_address": self.guest_address, "guest_port": self.guest_port,
                "host_address": self.host_address, "host_port": self.host_port}


def build_network_args(forward: Forward | None) -> list[str]:
    if forward is None:
        return ["-nic", "none"]
    return ["-netdev", f"user,id=n0,restrict=on,guestfwd={forward.guestfwd}",
            "-device", "virtio-net-pci,netdev=n0"]


def _option_values(argv: list[str], name: str) -> list[str]:
    return [argv[i + 1] for i in range(len(argv) - 1) if argv[i] == name]


def assert_network_isolation(argv: list[str], forward: Forward | None) -> tuple[bool, str]:
    """Assert the network configuration of a hypervisor command line before boot (§B).

    Without an update source: ``-nic none`` and no other network option. With one:
    exactly one ``-netdev user`` with ``restrict=on`` and exactly one ``guestfwd``
    equal to the declared endpoint, nothing else. ``-nodefaults`` is required in
    both cases so QEMU can't add a default network device, and ``-no-user-config``
    so it can't read a host configuration file that adds one.
    """
    for opaque in ("-readconfig", "-set"):
        if opaque in argv:
            return False, f"{opaque} hides configuration the assertion can't check"
    if "-nodefaults" not in argv:
        return False, "-nodefaults missing, so the hypervisor may add a default network device"
    if "-no-user-config" not in argv:
        return False, "-no-user-config missing, so the hypervisor may read a host configuration file"
    nics, nets, netdevs = (_option_values(argv, o) for o in ("-nic", "-net", "-netdev"))
    attached = [d for d in _option_values(argv, "-device") if "netdev=" in d]
    if nets:
        return False, "-net isn't admitted"
    if forward is None:
        if nics != ["none"] or netdevs or attached:
            return False, "a scenario without an update source needs exactly `-nic none` and no other network option"
        return True, ""
    if nics:
        return False, "-nic isn't admitted with an update source; one restricted -netdev user is"
    if len(netdevs) != 1:
        return False, f"expected exactly one -netdev, found {len(netdevs)}"
    value = netdevs[0]
    if ",," in value:
        return False, "escaped commas in the -netdev value can't be asserted"
    backend, *parts = value.split(",")
    if backend != "user":
        return False, f"the netdev backend is {backend!r}, not restricted user-mode networking"
    opts: dict[str, str] = {}
    forwards: list[str] = []
    for part in parts:
        key, _, val = part.partition("=")
        if key == "guestfwd":
            forwards.append(val)
        elif key in opts:
            return False, f"netdev option {key!r} repeated"
        else:
            opts[key] = val
    extra = sorted(set(opts) - {"id", "restrict"})
    if extra:
        return False, f"netdev option(s) {', '.join(extra)} not admitted"
    if opts.get("restrict") != "on":
        return False, "restrict=on missing from the user-mode netdev"
    if len(forwards) != 1:
        return False, f"expected exactly one guestfwd, found {len(forwards)}"
    if forwards[0] != forward.guestfwd:
        return False, f"guestfwd {forwards[0]!r} isn't the declared endpoint {forward.guestfwd!r}"
    netdev_id = opts.get("id")
    if len(attached) > 1 or any(f"netdev={netdev_id}" not in d.split(",") for d in attached):
        return False, "a network device is attached to something other than the one restricted netdev"
    return True, ""


def network_record(forward: Forward | None) -> dict:
    args = build_network_args(forward)
    if forward is None:
        return {"mode": "none", "config": " ".join(args)}
    return {"mode": "restricted-forward", "config": " ".join(args[:2]), "forward": forward.record()}


def _qemu_escape(value: str) -> str:
    return value.replace(",", ",,")


def declared_switches(decl: dict) -> list[dict]:
    """The host switches a declaration names (source and failure switch)."""
    found = [(decl.get("update") or {}).get("source_switch"), (decl.get("health") or {}).get("failure_switch")]
    return [s for s in found if isinstance(s, dict)]


# Which host switch each scenario sets (§I): the source switch, the failure switch, or both.
SOURCE_SWITCH_SCENARIOS = ("rollback", "positive", "downgrade", "signature-rejection", "interrupted-update")
FAILURE_SWITCH_SCENARIOS = ("rollback", "commit-boundary")


def fw_cfg_switch_scenarios(decl: dict) -> tuple[str, ...]:
    """The scenarios that set a declared qemu-fw-cfg switch."""
    source = ((decl.get("update") or {}).get("source_switch") or {}).get("type") == "qemu-fw-cfg"
    failure = ((decl.get("health") or {}).get("failure_switch") or {}).get("type") == "qemu-fw-cfg"
    return tuple(name for name in SWITCH_SCENARIOS
                 if (source and name in SOURCE_SWITCH_SCENARIOS) or (failure and name in FAILURE_SWITCH_SCENARIOS))


def switch_value(switch: dict, value: str) -> str:
    """The SMBIOS Type 11 string for a declared host switch (§L)."""
    if switch["type"] == "systemd-credential":
        return f"io.systemd.credential:{switch['name']}={value}"
    return f"{switch['name']}={value}"


@dataclasses.dataclass
class BootSpec:
    binary: str
    arch: str
    machine_type: str
    accel: str  # "kvm" or "tcg"
    memory_mb: int
    firmware_type: str  # "uefi" or "u-boot"
    firmware_code: str
    firmware_vars: str | None
    secure_boot: bool
    drive: str
    drive_format: str
    serial_log: str
    qmp_socket: str | None
    network: list[str]
    smbios: list[str] = dataclasses.field(default_factory=list)
    machine_uuid: str | None = None
    tpm_socket: str | None = None
    # False only for the run's own copy-on-write overlay that carries the positive
    # scenario's committed state to the commit-boundary scenario (§I, §L); the
    # artifact itself is always attached with snapshot=on.
    drive_snapshot: bool = True


def build_qemu_command(spec: BootSpec) -> list[str]:
    """The QEMU argv for one boot. The artifact is attached with snapshot=on (§B);
    the run's own overlay, whose backing file QEMU opens read-only, without it.

    ``-nodefaults`` keeps QEMU from adding a default network device, and
    ``-no-user-config`` from reading a host configuration file the isolation
    assertion can't see.
    """
    machine = spec.machine_type
    x86_secure = spec.secure_boot and spec.arch == "x86_64" and spec.firmware_type == "uefi"
    if x86_secure:
        machine += ",smm=on"
    argv = [spec.binary, "-nodefaults", "-no-user-config", "-machine", machine, "-accel", spec.accel,
            "-cpu", "host" if spec.accel == "kvm" else "max", "-m", str(spec.memory_mb),
            "-display", "none", "-serial", f"file:{spec.serial_log}"]
    if spec.qmp_socket:
        argv += ["-qmp", f"unix:{_qemu_escape(spec.qmp_socket)},server=on,wait=off"]
    if spec.firmware_type == "uefi":
        argv += ["-drive", f"if=pflash,format=raw,unit=0,readonly=on,file={_qemu_escape(spec.firmware_code)}"]
        if spec.firmware_vars:
            argv += ["-drive", f"if=pflash,format=raw,unit=1,file={_qemu_escape(spec.firmware_vars)}"]
        if x86_secure:
            argv += ["-global", "driver=cfi.pflash01,property=secure,value=on"]
    else:
        argv += ["-bios", spec.firmware_code]
    drive = f"file={_qemu_escape(spec.drive)},format={spec.drive_format},if=virtio"
    argv += ["-drive", drive + (",snapshot=on" if spec.drive_snapshot else "")]
    argv += spec.network
    for value in spec.smbios:
        argv += ["-smbios", f"type=11,value={_qemu_escape(value)}"]
    if spec.machine_uuid:
        argv += ["-uuid", spec.machine_uuid]
    if spec.tpm_socket:
        device = "tpm-tis" if spec.arch == "x86_64" else "tpm-tis-device"
        argv += ["-chardev", f"socket,id=chrtpm,path={_qemu_escape(spec.tpm_socket)}",
                 "-tpmdev", "emulator,id=tpm0,chardev=chrtpm", "-device", f"{device},tpmdev=tpm0"]
    return argv


# --------------------------------------------------------------------------- #
# Pure: timeouts (§J) and verdicts (§H)
# --------------------------------------------------------------------------- #
def compute_timeouts(overrides: dict, factor: float, max_boot_attempts: int | None,
                     field_updated: bool) -> tuple[dict, dict]:
    """Return (protocol record, seconds) for the six §J timeouts after the factor."""
    record: dict = {}
    seconds: dict = {}

    def put(name: str, base: float | None, reason: str = "") -> None:
        if overrides.get(name) is not None:
            base, source = float(overrides[name]), "override"
        else:
            source = "default"
        if base is None:
            record[name] = unavailable(reason)
            seconds[name] = None
        else:
            seconds[name] = base * factor
            record[name] = {"seconds": seconds[name], "source": source}

    readiness = float(overrides.get("readiness") or DEFAULT_TIMEOUTS["readiness"])
    put("readiness", DEFAULT_TIMEOUTS["readiness"])
    if field_updated:
        per_boot = None if max_boot_attempts is None else (max_boot_attempts + 1) * readiness
        put("update_installation", DEFAULT_TIMEOUTS["update_installation"])
        put("rollback", per_boot, "no update.max_boot_attempts in the declaration")
        put("update_window", DEFAULT_TIMEOUTS["update_window"])
        put("recovery", per_boot, "no update.max_boot_attempts in the declaration")
    else:
        for name in ("update_installation", "rollback", "update_window", "recovery"):
            put(name, None, "update_model isn't field-updated")
    put("total_margin", DEFAULT_TIMEOUTS["total_margin"])
    return record, seconds


def aggregate_verdict(scenarios: list[dict]) -> tuple[str, int]:
    """Worst required verdict (fail > not-run > pass); a recommended one only by failing."""
    required = [s["verdict"] for s in scenarios if s["required"]]
    if not required:
        return "not-run", EXIT_STATUS["not-run"]
    worst = max(required, key=VERDICT_RANK.__getitem__)
    if any(not s["required"] and s["verdict"] == "fail" for s in scenarios):
        worst = "fail"
    return worst, EXIT_STATUS[worst]


def plan_scenarios(field_updated: bool | None, selected: set[str]) -> list[tuple[str, bool, bool]]:
    """(name, required, excluded) per planned scenario.

    A dropped required scenario stays planned as excluded (it is recorded
    not-run); a dropped recommended one isn't planned.
    """
    plan = [("smoke", True, "smoke" not in selected)]
    if field_updated:
        plan.append(("rollback", True, "rollback" not in selected))
        if "positive" in selected:
            plan.append(("positive", False, False))
    if "identity" in selected:
        plan.append(("identity", False, False))
    if field_updated:  # §I: downgrade and signature-rejection required, the other two recommended
        plan += [(name, True, name not in selected) for name in ("downgrade", "signature-rejection")]
        plan += [(name, False, False) for name in ("commit-boundary", "interrupted-update") if name in selected]
    return plan


_NUMERIC_VERSION = re.compile(r"\d+(?:\.\d+)*")


def compare_versions(a: str | None, b: str | None) -> int | None:
    """-1, 0, or 1 for two dotted numeric versions; None when either doesn't parse."""
    if not a or not b or not (_NUMERIC_VERSION.fullmatch(a) and _NUMERIC_VERSION.fullmatch(b)):
        return None
    left, right = ([int(x) for x in v.split(".")] for v in (a, b))
    width = max(len(left), len(right))
    left, right = left + [0] * (width - len(left)), right + [0] * (width - len(right))
    return (left > right) - (left < right)


def new_scenario(name: str, required: bool, trace_ids: list[str]) -> dict:
    entry = {"name": name, "required": required, "verdict": "not-run", "flaky": False, "attempt": 1,
             "network": unavailable("no boot was attempted"), "phases": [], "report_lines": [],
             "trace_ids": trace_ids}
    # The per-scenario fields of protocol v1.2, admitted only on their scenarios.
    if name in ("downgrade", "commit-boundary", "interrupted-update"):
        entry["observed_versions"] = unavailable("nothing booted")
    if name in ("downgrade", "interrupted-update"):
        entry["source_requests"] = unavailable("nothing booted")
    if name == "interrupted-update":
        entry["interruption"] = unavailable("the reset wasn't reached")
    if name == "signature-rejection":
        entry["signature_variants"] = unavailable("nothing booted")
    return entry


def mark_not_run(entry: dict, causes: list[tuple[str, str | None]]) -> None:
    entry["verdict"] = "not-run"
    reasons = "; ".join(dict.fromkeys(r for r, _ in causes))
    hints = [h for _, h in causes if h]
    entry["not_run_cause"] = {
        "reason": reasons,
        "install_hint": " ".join(dict.fromkeys(hints)) if hints else unavailable(
            f"{NO_TOOL}; the cause is an input, the declaration, or a missing transport"),
    }


# --------------------------------------------------------------------------- #
# Host helpers
# --------------------------------------------------------------------------- #
def host_arch() -> str:
    machine = platform.machine()
    return {"amd64": "x86_64", "arm64": "aarch64"}.get(machine.lower(), machine)


def host_os() -> str | dict:
    try:
        for line in Path("/etc/os-release").read_text(encoding="utf-8").splitlines():
            if line.startswith("PRETTY_NAME="):
                return line.split("=", 1)[1].strip().strip('"') or platform.system()
    except OSError:
        pass
    return platform.system() or unavailable("the host operating system couldn't be read")


def kvm_usable(arch: str, h_arch: str) -> bool:
    return arch == h_arch and os.access("/dev/kvm", os.R_OK | os.W_OK)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def inspect_drive(path: Path) -> tuple[str, str | None]:
    """(drive format, refusal) for an artifact (§B).

    A qcow2 image can name a backing file (header bytes 8-15, a big-endian
    offset that is 0 when there is none) or, from header version 3 on, an
    external data file (incompatible-feature bit 2 at offset 72). Either makes
    the hypervisor open a host file or fetch a URL the isolation doesn't cover,
    so such an image is refused, never attached.
    """
    with path.open("rb") as handle:
        header = handle.read(80)
    if header[:4] != QCOW2_MAGIC:
        return "raw", None
    version = int.from_bytes(header[4:8], "big")
    if len(header) < (80 if version >= 3 else 72):
        return "qcow2", "the qcow2 header is truncated"
    if int.from_bytes(header[8:16], "big") != 0:
        return "qcow2", "the qcow2 image names a backing file"
    if version >= 3 and int.from_bytes(header[72:80], "big") & QCOW2_EXTERNAL_DATA_FILE:
        return "qcow2", "the qcow2 image uses an external data file"
    return "qcow2", None


def run_validator(path: Path, kind: str = "declaration") -> tuple[int, dict]:
    try:
        proc = subprocess.run([sys.executable, str(VALIDATOR), "--kind", kind, str(path)],
                              capture_output=True, text=True, timeout=120, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 2, {"result": "not-decidable", "cause": f"validator couldn't run: {exc}"}
    try:
        payload = json.loads(proc.stdout)
    except ValueError:
        payload = {"result": "not-decidable", "cause": proc.stderr.strip() or "validator gave no JSON"}
    return proc.returncode, payload


def qmp(socket_path: str | None, command: str, timeout: float = 5.0) -> bool:
    """Send one QMP command; True when the hypervisor acknowledged it."""
    if not socket_path:
        return False
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect(socket_path)
            stream = sock.makefile("rwb")
            stream.readline()  # greeting
            for execute in ("qmp_capabilities", command):
                stream.write(json.dumps({"execute": execute}).encode() + b"\n")
                stream.flush()
                while True:
                    reply = json.loads(stream.readline() or b"{}")
                    if "event" not in reply:
                        break
                if "return" not in reply:
                    return False
            return True
    except (OSError, ValueError):
        return False


class HypervisorExited(Exception):
    def __init__(self, status: int, console_output: bool):
        super().__init__(status)
        self.status = status
        self.console_output = console_output


class NotRun(Exception):
    def __init__(self, reason: str, hint: str | None = None):
        super().__init__(reason)
        self.reason = reason
        self.hint = hint


def interrupt_reason() -> str:
    return f"run interrupted by {signal.Signals(_received_signals[0]).name}; nothing was verified after it"


class Interrupted(NotRun):
    """SIGTERM or SIGHUP arrived; raised at a polling point so every boot is stopped."""

    def __init__(self):
        super().__init__(interrupt_reason())


def _on_signal(signum, _frame) -> None:
    _received_signals.append(signum)


class SerialReader:
    """Reads a serial log as it grows and yields only health reports."""

    def __init__(self, path: Path):
        self.path = path
        self.offset = 0
        self.partial = b""
        self.pending: list[Report] = []

    def _feed(self, raw: bytes) -> None:
        report = parse_report_line(normalise_line(raw.decode("utf-8", "replace")))
        if report is not None:
            self.pending.append(report)

    def poll(self, flush: bool = False) -> None:
        try:
            with self.path.open("rb") as handle:
                handle.seek(self.offset)
                data = handle.read(1 << 20)
        except FileNotFoundError:
            data = b""
        self.offset += len(data)
        *lines, self.partial = (self.partial + data).split(b"\n")
        for raw in lines:
            self._feed(raw)
        if flush or len(self.partial) > MAX_PARTIAL_LINE:
            if self.partial:
                self._feed(self.partial)
            self.partial = b""

    def discard(self) -> None:
        """Drop everything read or buffered so far; later reports come from later output."""
        self.poll()
        self.pending.clear()
        self.partial = b""

    def next_report(self, deadline: float, proc: subprocess.Popen) -> Report | None:
        while True:
            if _received_signals:
                raise Interrupted()
            self.poll()
            if self.pending:
                return self.pending.pop(0)
            if proc.poll() is not None:
                self.poll(flush=True)
                if self.pending:
                    return self.pending.pop(0)
                raise HypervisorExited(proc.returncode, self.offset > 0)
            if time.monotonic() >= deadline:
                return None
            time.sleep(POLL_INTERVAL_S)


class Boot:
    """One hypervisor process: started once, stopped from the host."""

    def __init__(self, argv: list[str], serial_log: Path, hypervisor_log: Path, qmp_socket: str | None):
        self.argv = argv
        self.serial = SerialReader(serial_log)
        self.hypervisor_log = hypervisor_log
        self.qmp_socket = qmp_socket
        self.proc: subprocess.Popen | None = None
        self.extra: list[subprocess.Popen] = []

    def start(self) -> None:
        # A session of its own, so it is stopped through its process group, and a
        # signal to the runner's group reaches only the runner, which then stops it.
        with self.hypervisor_log.open("wb") as log:
            self.proc = subprocess.Popen(self.argv, stdin=subprocess.DEVNULL, stdout=log,
                                         stderr=subprocess.STDOUT, start_new_session=True)

    def next_report(self, deadline: float) -> Report | None:
        return self.serial.next_report(deadline, self.proc)

    def stop(self) -> None:
        procs = ([self.proc] if self.proc else []) + self.extra
        if self.proc and self.proc.poll() is None:
            qmp(self.qmp_socket, "quit")
        for proc in procs:
            try:
                proc.wait(timeout=STOP_GRACE_S)
            except subprocess.TimeoutExpired:
                _signal_group(proc, signal.SIGTERM)
                try:
                    proc.wait(timeout=STOP_TERM_S)
                except subprocess.TimeoutExpired:
                    _signal_group(proc, signal.SIGKILL)
                    proc.wait()


def settle_console(boot: Boot, wait: float = 2.0) -> None:
    """Read the console up to the moment of a VM reset without dropping a half-written line.

    A line still lacking its end may be a report being written; wait briefly for
    it to complete, then evaluate whatever is there as output from before the
    reset rather than discarding it (§I).
    """
    boot.serial.poll()
    end = time.monotonic() + wait
    while boot.serial.partial and time.monotonic() < end:
        time.sleep(POLL_INTERVAL_S)
        boot.serial.poll()
    boot.serial.poll(flush=True)


def _signal_group(proc: subprocess.Popen, sig: int) -> None:
    try:
        os.killpg(proc.pid, sig)
    except ProcessLookupError:
        pass


class _ArtifactHandler(http.server.BaseHTTPRequestHandler):
    """Serves exactly one file at one fixed path; everything else is 404, with no listing."""

    def _serve(self, body: bool) -> None:
        server = self.server
        if urllib.parse.urlsplit(self.path).path != server.served_path:
            self.send_error(404)  # logged, but no contact: nothing was offered to the guest (§I)
            return
        server.requests.append(self.command)  # a request for the served file
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(server.served_size))
        self.end_headers()
        offset = 0
        while body and offset < server.served_size:
            chunk = os.pread(server.served_fd, 1 << 20, offset)
            if not chunk:
                break
            self.wfile.write(chunk)
            offset += len(chunk)
        if body and offset >= server.served_size and not server.delivered.is_set():
            server.delivered_at = time.monotonic()  # the whole file was sent (§I interrupted-update)
            server.delivered.set()

    def do_GET(self):  # noqa: N802 - name of the base-class hook
        self._serve(True)

    def do_HEAD(self):  # noqa: N802 - name of the base-class hook
        self._serve(False)

    def log_message(self, format, *args):  # noqa: A002 - signature of the base class
        self.server.request_log.append(format % args)


# --------------------------------------------------------------------------- #
# The run
# --------------------------------------------------------------------------- #
class Run:
    def __init__(self, args: argparse.Namespace, out_dir: Path):
        self.args = args
        self.out = out_dir
        self.started = dt.datetime.now(dt.timezone.utc)
        self.notes: dict[str, list[str]] = {}
        self.serial_logs: list[str] = []
        self.global_causes: list[tuple[str, str | None]] = []
        self.causes: dict[str, list[tuple[str, str | None]]] = {n: [] for n in SCENARIOS}
        self.decl: dict | None = None
        self.booted = False
        self.secure_boot_ran: bool | None = None
        self.tpm_used = False
        self.rollback_versions: list[str] | None = None
        self.identity_boots: list[dict] | None = None
        self.sock_dir = Path(tempfile.mkdtemp(prefix="ibv-"))
        # Set by execute() once the preconditions are known; a scenario only boots when all are.
        self.arch = self.hypervisor = self.machine_type = self.accel = None
        self.fw_type = self.fw_code = self.fw_vars = self.qemu_hint = None
        self.artifact_format = "raw"
        self.next_digest: str | None = None
        self.prev_digest: str | None = None
        # Per signature-rejection variant: {"path", "digest"} when servable, else
        # {"cause"} or {"not_producible"} (§H, §I).
        self.payloads: dict[str, dict] = {}
        self.secure = self.need_tpm = False
        self.t: dict = {}
        self.verdicts: dict[str, str] = {}  # finished scenarios, for the positive controls of §I
        self.qemu_img: str | None = None
        self.keep_positive_state = False  # commit-boundary planned and an overlay can be made
        self.positive_state: Path | None = None  # the positive scenario's kept overlay
        self.state_cause: str | None = None

    # ---- inputs and declaration -------------------------------------------
    def _cause(self, reason: str, hint: str | None = None, scenarios=None) -> None:
        if scenarios is None:
            self.global_causes.append((reason, hint))
        else:
            for name in scenarios:
                self.causes[name].append((reason, hint))

    def read_declaration(self) -> dict:
        record = {k: unavailable("no declaration path given") for k in
                  ("path", "digest", "schema_version", "image_name")}
        path = self.args.declaration
        if path is None:
            self._cause("missing input: --declaration")
            return record
        record["path"] = str(path)
        try:  # read once: the digest, the validated copy, and the loaded document are the same bytes
            content = path.read_bytes()
            validated = self.sock_dir / "declaration.yaml"
            validated.write_bytes(content)
            record["digest"] = "sha256:" + hashlib.sha256(content).hexdigest()
        except OSError as exc:
            reason = f"declaration unreadable: {exc}"
            self._cause(reason)
            record.update(digest=unavailable(reason), schema_version=unavailable(reason),
                          image_name=unavailable(reason))
            return record
        code, payload = run_validator(validated)
        violations = payload.get("violations", [])
        hard = [v for v in violations if not v.get("rule", "").startswith("conditional.")]
        if code == 2 or payload.get("result") == "not-decidable":
            reason = f"declaration not decidable: {payload.get('cause', 'validator unavailable')}"
            self._cause(reason, "pip install jsonschema pyyaml")
        elif hard:
            first = "; ".join(f"{v.get('path')}: {v.get('message')}" for v in hard[:3])
            self._cause(f"declaration invalid: {first}")
        else:
            import yaml  # the validator accepted the file, so PyYAML is installed and safe here

            self.decl = yaml.safe_load(content.decode("utf-8"))
            rules = {v.get("rule") for v in violations}
            if "conditional.field-updated-requires-update" in rules:
                self._cause("declaration lacks the update block despite update_model field-updated",
                            scenarios=("rollback", "positive", "downgrade", "signature-rejection",
                                       "interrupted-update"))
            if "conditional.field-updated-requires-failure-switch" in rules:
                self._cause("declaration lacks health.failure_switch despite update_model field-updated",
                            scenarios=("rollback", "commit-boundary"))
        if self.decl is None:
            reason = "declaration not usable, so not read"
            record.update(schema_version=unavailable(reason), image_name=unavailable(reason))
        else:
            record["schema_version"] = self.decl["schema_version"]
            record["image_name"] = self.decl["image"]["name"]
        return record

    def artifact_record(self, path: Path | None, version: str | None, label: str, scenarios=None):
        if path is None or not version:
            missing = "--" + label if path is None else f"--{label.replace('artifact', 'expected-version')}"
            reason = f"missing input: {missing}"
            self._cause(reason, scenarios=scenarios)
            return unavailable(reason)
        try:
            return {"path": str(path), "digest": sha256_file(path), "expected_version": version}
        except OSError as exc:
            reason = f"{label} unreadable: {exc}"
            self._cause(reason, scenarios=scenarios)
            return unavailable(reason)

    def payload_record(self, variant: str) -> dict:
        """The top-level record of one signature-rejection test payload (§G, §H).

        Only the key's identifier enters the protocol, never key material (§I). A
        missing or unusable payload makes only its variant not-run.
        """
        a = self.args
        if variant == "untrusted-key":
            flag, path, version, production = ("--untrusted-payload", a.untrusted_payload,
                                               a.untrusted_payload_version, a.untrusted_payload_production)
            extra = (("--untrusted-key-id", a.untrusted_key_id),)
        else:
            if a.unsigned_not_producible:
                mechanism = ((self.decl or {}).get("update") or {}).get("mechanism", "unknown")
                reason = (f"not producible: the payload format of update.mechanism {mechanism} admits no "
                          f"unsigned payload: {a.unsigned_not_producible}")
                self.payloads[variant] = {"not_producible": reason}
                return unavailable(reason)
            flag, path, version, production = ("--unsigned-payload", a.unsigned_payload,
                                               a.unsigned_payload_version, a.unsigned_payload_production)
            extra = ()
        if path is None:
            reason = f"missing input: {flag}" + (" or --unsigned-not-producible" if variant == "unsigned" else "")
            self.payloads[variant] = {"cause": reason}
            return unavailable(reason)
        missing = [name for name, value in ((f"{flag}-version", version), (f"{flag}-production", production),
                                            *extra) if not value]
        if missing:
            reason = f"missing input: {', '.join(missing)}"
            self.payloads[variant] = {"cause": reason}
            return unavailable(reason)
        try:
            digest = sha256_file(path)
            _, refusal = inspect_drive(path)
        except OSError as exc:
            reason = f"{variant} test payload unreadable: {exc}"
            self.payloads[variant] = {"cause": reason}
            return unavailable(reason)
        if refusal:
            self.payloads[variant] = {"cause": f"{variant} test payload refused: {refusal}, which could reach a "
                                               "host file or URL (§B)"}
        elif (cause := self._payload_version_problem(variant, version)) is not None:
            # An installed payload of a version that isn't newer couldn't be told apart from a
            # refusal, or would be refused for its version instead of its signature (§I).
            self.payloads[variant] = {"cause": cause}
        else:
            self.payloads[variant] = {"path": path, "digest": digest}
        if compare_versions(version, a.expected_version) is None and version != a.expected_version:
            production = (f"{production} (versions {version} and {a.expected_version} aren't dotted numeric, so "
                          "the runner can't compare them: newness over N rests on the operator)")
        record = {"path": str(path), "digest": digest, "expected_version": version}
        if variant == "untrusted-key":
            record["signing_key"] = a.untrusted_key_id
        record["production"] = production
        return record

    def _payload_version_problem(self, variant: str, version: str) -> str | None:
        """Why a test payload's offered version isn't usable, or None (§I: newer than N)."""
        n, previous = self.args.expected_version, self.args.previous_expected_version
        if version == n:
            return f"the {variant} test payload offers N's version {version}; it must offer a newer one (§I)"
        if previous and (version == previous or compare_versions(version, previous) == 0):
            return (f"the {variant} test payload offers the previous-version artifact's version {version}; it "
                    "must offer one newer than N (§I)")
        order = compare_versions(version, n)  # zero-padded, so 1.4 equals 1.4.0
        if order is not None and order <= 0:
            return f"the {variant} test payload's version {version} isn't newer than N's version {n} (§I)"
        return None

    # ---- preconditions ----------------------------------------------------
    def resolve_arch(self) -> dict:
        declared = (self.decl or {}).get("image", {}).get("architectures")
        wanted = self.args.arch
        if declared:
            if wanted:
                if wanted not in declared:
                    self._cause(f"--arch {wanted} isn't among the declared architectures {declared}")
                    return unavailable("operator input not among the declared architectures")
                return {"name": wanted, "source": "operator-input"}
            if len(declared) == 1:
                return {"name": declared[0], "source": "declaration"}
            self._cause(f"the declaration names several architectures {declared}; pass --arch")
            return unavailable("several declared architectures and no --arch")
        if wanted:
            return {"name": wanted, "source": "operator-input"}
        self._cause("no guest architecture: the declaration names none and no --arch was given")
        return unavailable("no guest architecture from the declaration or --arch")

    def find_firmware(self, arch: str, fw_type: str, secure: bool) -> tuple[str | None, str | None]:
        code, vars_ = self.args.firmware_code, self.args.firmware_vars
        if fw_type == "uefi":
            if secure:
                if not (code and vars_):
                    self._cause("secure_boot is implemented, so --firmware-code and --firmware-vars with only "
                                "the image's own keys enrolled are required",
                                "Prepare a variables file with only the image's keys (for example with "
                                "virt-fw-vars) and pass --firmware-code and --firmware-vars.")
                    return None, None
            elif not code:
                for cand_code, cand_vars in UEFI_FIRMWARE.get(arch, []):
                    if Path(cand_code).is_file() and Path(cand_vars).is_file():
                        code, vars_ = cand_code, cand_vars
                        break
            if not code:
                self._cause(f"no UEFI firmware found for {arch}",
                            f"Install {UEFI_PACKAGE.get(arch, 'UEFI firmware for ' + arch)} or pass "
                            "--firmware-code and --firmware-vars.")
                return None, None
        else:
            if not code and not secure:
                code = next((c for c in UBOOT_FIRMWARE.get(arch, []) if Path(c).is_file()), None)
            if not code:
                self._cause(f"no U-Boot build for the {MACHINE_TYPE.get(arch)} machine type of {arch}"
                            + (" trusting only the image's keys" if secure else ""),
                            "Install u-boot-qemu or pass --firmware-code with a U-Boot build for the board.")
                return None, None
        for item in (code, vars_):
            if item and not Path(item).is_file():
                self._cause(f"firmware file {item} not found", "Pass an existing --firmware-code/--firmware-vars.")
                return None, None
        return code, vars_

    # ---- scenarios --------------------------------------------------------
    def _launch(self, entry: dict, name: str, *, forward: Forward | None = None,
                smbios: list[str] | None = None, machine_uuid: str | None = None,
                overlay: Path | None = None, state_from: str | None = None) -> Boot:
        """Start one boot. Every boot goes through here: build_qemu_command, then
        assert_network_isolation before the process starts (§B).

        ``overlay`` boots the run's own copy-on-write overlay instead of the
        artifact under snapshot=on; ``state_from`` continues the firmware
        variables and TPM state of that earlier boot (commit-boundary, §I).
        """
        if overlay is not None and overlay.parent != self.sock_dir:
            raise NotRun(f"refused to boot {overlay} writable: only the run's own overlay may be (§B)")
        serial = self.out / f"{name}.serial.log"
        vars_copy = None
        if self.fw_vars:
            vars_copy = self.out / f"{name}.vars.fd"
            shutil.copyfile(self.out / f"{state_from}.vars.fd" if state_from else self.fw_vars, vars_copy)
        tpm_socket = None
        extra = []
        if self.need_tpm:
            state = self.sock_dir / f"{name}-tpm"
            if state_from:
                shutil.copytree(self.sock_dir / f"{state_from}-tpm", state,
                                ignore=shutil.ignore_patterns("*.sock"))
            else:
                state.mkdir()
            tpm_socket = str(state / "swtpm.sock")
            try:
                extra.append(subprocess.Popen(
                    ["swtpm", "socket", "--tpm2", "--tpmstate", f"dir={state}",
                     "--ctrl", f"type=unixio,path={tpm_socket}", "--terminate"],
                    stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    start_new_session=True))
            except OSError as exc:
                raise NotRun(f"TPM emulator couldn't start: {exc}", "Install swtpm.") from exc
        qmp_socket = str(self.sock_dir / f"{name}.qmp")
        argv = build_qemu_command(BootSpec(
            binary=self.hypervisor, arch=self.arch, machine_type=self.machine_type, accel=self.accel,
            memory_mb=self.args.memory, firmware_type=self.fw_type, firmware_code=self.fw_code,
            firmware_vars=str(vars_copy) if vars_copy else None, secure_boot=self.secure,
            drive=str(overlay or self.args.artifact), drive_format="qcow2" if overlay else self.artifact_format,
            serial_log=str(serial), qmp_socket=qmp_socket, network=build_network_args(forward),
            smbios=smbios or [], machine_uuid=machine_uuid, tpm_socket=tpm_socket,
            drive_snapshot=overlay is None))
        ok, reason = assert_network_isolation(argv, forward)
        if not ok:
            for proc in extra:
                proc.kill()
            raise NotRun(f"network isolation rejected before boot: {reason}")
        entry["network"] = network_record(forward)
        boot = Boot(argv, serial, self.out / f"{name}.hypervisor.log", qmp_socket)
        boot.extra = extra
        try:
            boot.start()
        except OSError as exc:
            boot.stop()
            raise NotRun(f"hypervisor couldn't start: {exc}", self.qemu_hint) from exc
        self.booted = True
        self.secure_boot_ran = self.secure
        self.tpm_used = self.tpm_used or self.need_tpm
        self.serial_logs.append(serial.name)
        return boot

    def _await(self, boot: Boot, entry: dict, phase: str, timeout: float, total_deadline: float):
        start = time.monotonic()
        report = boot.next_report(min(start + timeout, total_deadline))
        duration = round(time.monotonic() - start, 3)
        entry["phases"].append({"name": phase, "timeout_s": timeout,
                                "duration_s": duration if report else unavailable("no report before the timeout")})
        if report is not None:
            entry["report_lines"].append(report.line)
        return report

    def _check(self, report, version, expect_status="healthy") -> list[str]:
        health = self.decl["health"]
        return check_report(report, image_name=self.decl["image"]["name"], expected_version=version,
                            tolerated_units=health.get("tolerated_units") or [],
                            framework_hook=health["definition"]["kind"] == "framework-hook",
                            expect_status=expect_status)

    def _total(self, *phases: str) -> float:
        return time.monotonic() + sum(self.t[p] for p in phases) + self.t["total_margin"]

    def _boot_to_report(self, entry: dict, name: str, phase: str, version: str, **launch) -> tuple[Report | None, list[str]]:
        boot = self._launch(entry, name, **launch)
        try:
            report = self._await(boot, entry, phase, self.t["readiness"], self._total("readiness"))
        finally:
            boot.stop()
        if report is None:
            return None, ["no health report before the readiness timeout"]
        return report, self._check(report, version)

    def run_smoke(self, entry: dict) -> tuple[str, list[str]]:
        _, problems = self._boot_to_report(entry, "smoke", "readiness", self.args.expected_version)
        return ("fail" if problems else "pass"), problems

    def run_identity(self, entry: dict) -> tuple[str, list[str]]:
        boots, problems = [], []
        for i, phase in ((1, "readiness"), (2, "second-readiness")):
            machine_uuid = str(uuid.uuid4())
            report, issues = self._boot_to_report(entry, f"identity-{i}", phase, self.args.expected_version,
                                                  machine_uuid=machine_uuid)
            mid = report.get("machine_id_app") if report and not report.error else None
            if mid is not None and not MACHINE_ID_RE.fullmatch(mid):
                issues = [*issues, f"malformed report: machine_id_app={mid!r} is neither 32 lowercase hex "
                                   "characters nor -"]
                mid = None
            boots.append({"machine_uuid": machine_uuid, "machine_id_app": mid or unavailable(
                "no well-formed machine_id_app in this boot's report")})
            problems += [f"boot {i}: {p}" for p in issues]
        self.identity_boots = boots
        if problems:
            return "fail", problems
        values = [b["machine_id_app"] for b in boots]
        if "-" in values:
            raise NotRun("a report carries machine_id_app=- (§I)")
        if values[0] == values[1]:
            return "fail", ["both boots report the same machine_id_app: the image ships a fixed identity"]
        return "pass", []

    def _open_source_file(self, path: Path, digest: str | None, label: str) -> tuple[int, int]:
        """Open a file to serve once, without following a symlink, and check its digest (§B)."""
        try:
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        except OSError as exc:
            raise NotRun(f"{label} not served: {path} can't be opened without following a symlink "
                         f"({exc})") from exc
        try:
            hasher = hashlib.sha256()
            size = 0
            while chunk := os.pread(fd, 1 << 20, size):
                hasher.update(chunk)
                size += len(chunk)
        except OSError as exc:
            os.close(fd)
            raise NotRun(f"local update source couldn't read the {label}: {exc}") from exc
        if "sha256:" + hasher.hexdigest() != digest:
            os.close(fd)
            raise NotRun(f"{label} changed after its digest was recorded; not served")
        return fd, size

    @staticmethod
    def _point_source(server, path: Path, fd: int, size: int) -> None:
        """Serve this file from now on, with a fresh request record."""
        old = getattr(server, "served_fd", None)
        server.served_path = "/" + urllib.parse.quote(path.name)
        server.served_fd, server.served_size = fd, size
        server.request_log, server.requests = [], []
        server.delivered, server.delivered_at = threading.Event(), None
        if old is not None:
            os.close(old)

    def _start_source(self, path: Path, digest: str | None, label: str):
        """Serve the one file whose digest the protocol records (§B); every request reads that open file."""
        fd, size = self._open_source_file(path, digest, label)
        try:
            server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _ArtifactHandler)
        except OSError as exc:
            os.close(fd)
            raise NotRun(f"local update source couldn't start: {exc}") from exc
        self._point_source(server, path, fd, size)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        return Forward(host_port=server.server_address[1]), server

    def _serve_next(self) -> tuple[Forward, http.server.ThreadingHTTPServer]:
        return self._start_source(self.args.next_artifact, self.next_digest, "next artifact")

    def _write_source_log(self, server, name: str) -> None:
        (self.out / f"{name}.update-source.log").write_text("\n".join(server.request_log) + "\n", encoding="utf-8")

    def _stop_source(self, server, name: str) -> None:
        server.shutdown()
        server.server_close()
        os.close(server.served_fd)
        self._write_source_log(server, name)

    def _update_flow(self, entry: dict, name: str, failure: bool,
                     overlay: Path | None = None) -> tuple[str, list[str]]:
        n, n1 = self.args.expected_version, self.args.next_expected_version
        update = self.decl["update"]
        forward, server = self._serve_next()
        smbios = [switch_value(update["source_switch"], forward.url)]
        if failure:
            smbios.append(switch_value(self.decl["health"]["failure_switch"], n1))
        versions: list[str] = []
        try:
            boot = self._launch(entry, name, forward=forward, smbios=smbios, overlay=overlay)
            try:
                return self._drive_update(boot, entry, failure, n, n1, update["max_boot_attempts"], versions)
            finally:
                boot.stop()
        finally:
            self._stop_source(server, name)
            if failure:
                self.rollback_versions = versions or None

    def _drive_update(self, boot, entry, failure, n, n1, max_attempts, versions) -> tuple[str, list[str]]:
        last = "rollback" if failure else "readiness"
        total = self._total("readiness", "update_installation", last)
        report = self._await(boot, entry, "readiness", self.t["readiness"], total)
        if report is None:
            return "fail", [f"no report of version {n} before the readiness timeout"]
        versions.append(report.get("image_version") or "?")
        problems = self._check(report, n)
        if problems:
            return "fail", [f"version {n}: {p}" for p in problems]
        start, deadline = time.monotonic(), min(time.monotonic() + self.t["update_installation"], total)
        while True:  # §I step 2: wait for the first report of N+1
            report = boot.next_report(deadline)
            if report is None:
                entry["phases"].append({"name": "update-installation", "timeout_s": self.t["update_installation"],
                                        "duration_s": unavailable("no report of N+1 before the timeout")})
                return "fail", [f"no report of version {n1} before the update-installation timeout"]
            entry["report_lines"].append(report.line)
            versions.append(report.get("image_version") or "?")
            if report.error:
                return "fail", [f"malformed report: {report.error}"]
            if report.get("image_version") != n:
                break
        entry["phases"].append({"name": "update-installation", "timeout_s": self.t["update_installation"],
                                "duration_s": round(time.monotonic() - start, 3)})
        problems = self._check(report, n1, "unhealthy" if failure else "healthy")
        if problems:
            return "fail", [f"first report after the update: {p}" for p in problems]
        if failure:
            return self._await_rollback(boot, entry, n, n1, max_attempts, versions, total)
        boot.serial.discard()  # only a report printed after the reset counts for the reset boot
        if not qmp(boot.qmp_socket, "system_reset"):
            raise NotRun("the hypervisor didn't acknowledge the VM reset (QMP system_reset)")
        report = self._await(boot, entry, "reset-readiness", self.t["readiness"], total)
        if report is None:
            return "fail", [f"no report after the reset of version {n1}"]
        versions.append(report.get("image_version") or "?")
        problems = self._check(report, n1)
        return ("fail", [f"after the reset: {p}" for p in problems]) if problems else ("pass", [])

    def _await_rollback(self, boot, entry, n, n1, max_attempts, versions, total) -> tuple[str, list[str]]:
        unhealthy = 1
        start = time.monotonic()
        deadline = min(start + self.t["rollback"], total)
        while True:
            report = boot.next_report(deadline)
            phase_done = report is not None and report.get("status") == "healthy"
            if report is None or phase_done:
                entry["phases"].append({"name": "rollback", "timeout_s": self.t["rollback"], "duration_s": round(
                    time.monotonic() - start, 3) if report else unavailable("no healthy report before the timeout")})
            if report is None:
                return "fail", [f"no healthy report of version {n} before the rollback timeout"]
            entry["report_lines"].append(report.line)
            versions.append(report.get("image_version") or "?")
            if report.error:
                return "fail", [f"malformed report: {report.error}"]
            if report.get("status") == "unhealthy":
                if report.get("image_version") != n1:
                    return "fail", [f"version {report.get('image_version')} reported unhealthy during rollback"]
                unhealthy += 1
                if unhealthy > max_attempts:
                    return "fail", [f"{unhealthy} unhealthy reports of {n1} exceed max_boot_attempts={max_attempts}"]
                continue
            problems = self._check(report, n)
            return ("fail", [f"first healthy report after the update: {p}" for p in problems]) if problems \
                else ("pass", [])

    def run_rollback(self, entry: dict) -> tuple[str, list[str]]:
        return self._update_flow(entry, "rollback", failure=True)

    def run_positive(self, entry: dict) -> tuple[str, list[str]]:
        """§I positive scenario. When commit-boundary is planned, it boots an overlay
        file and keeps it, since -snapshot discards its writes with the process (§L)."""
        overlay = None
        if self.keep_positive_state:
            try:
                overlay = self._create_overlay("positive")
            except NotRun as exc:
                self.state_cause = exc.reason
        verdict, notes = self._update_flow(entry, "positive", failure=False, overlay=overlay)
        if overlay is not None and verdict == "pass":
            self.positive_state = overlay
        return verdict, notes

    def _create_overlay(self, name: str) -> Path:
        """A copy-on-write overlay on the artifact, which QEMU opens read-only as its backing file."""
        overlay = self.sock_dir / f"{name}.overlay.qcow2"
        try:
            proc = subprocess.run([self.qemu_img, "create", "-q", "-f", "qcow2", "-F", self.artifact_format,
                                   "-b", str(Path(self.args.artifact).resolve()), str(overlay)],
                                  capture_output=True, text=True, timeout=60, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise NotRun(f"committed state can't be kept: the overlay couldn't be created ({exc})") from exc
        if proc.returncode != 0 or not overlay.is_file():
            raise NotRun("committed state can't be kept: the overlay couldn't be created "
                         f"({proc.stderr.strip() or f'qemu-img exit {proc.returncode}'})")
        return overlay

    def _positive_control(self) -> bool:
        """§I: a rollback or positive pass in this run shows the source arrangement installs a valid N+1."""
        return any(self.verdicts.get(name) == "pass" for name in ("rollback", "positive"))

    def _observe_refusal(self, boot: Boot, entry: dict, server, obs: dict, prefix: str = "") -> tuple[str, list[str]]:
        """§I downgrade steps 1-4, shared by each signature-rejection variant.

        Returns the verdict without the positive control, which the caller applies.
        ``obs`` collects the versions every report named and the requests for the
        served file within the update window. The source counts as contacted only
        when it sent the whole payload within the window: a 404, a HEAD, or an
        aborted download offered the guest nothing to refuse.
        """
        n = self.args.expected_version
        total = self._total("readiness", "update_window", "readiness")

        def take(report: Report, when: str) -> list[str]:
            obs["versions"].append(report.get("image_version") or "?")
            return [f"{when}: {p}" for p in self._check(report, n)]

        report = self._await(boot, entry, prefix + "readiness", self.t["readiness"], total)
        obs["requests"] = len(server.requests)
        if report is None:
            return "fail", [f"no report of version {n} before the readiness timeout"]
        problems = take(report, "first report")
        if problems:
            return "fail", problems
        # Step 2: keep reading reports until the update window, counted from N's first report, has passed.
        start = time.monotonic()
        window_end = min(start + self.t["update_window"], total)
        while (report := boot.next_report(window_end)) is not None:
            entry["report_lines"].append(report.line)
            problems = take(report, "during the update window")
            if problems:
                obs["requests"] = len(server.requests)
                return "fail", problems
        entry["phases"].append({"name": prefix + "update-window", "timeout_s": self.t["update_window"],
                                "duration_s": round(time.monotonic() - start, 3)})
        obs["requests"] = len(server.requests)
        delivered = server.delivered.is_set()
        settle_console(boot)  # a report printed after the window but before the reset still counts
        while boot.serial.pending:
            report = boot.serial.pending.pop(0)
            entry["report_lines"].append(report.line)
            problems = take(report, "after the update window")
            if problems:
                return "fail", problems
        if not qmp(boot.qmp_socket, "system_reset"):
            raise NotRun("the hypervisor didn't acknowledge the VM reset (QMP system_reset)")
        report = self._await(boot, entry, prefix + "reset-readiness", self.t["readiness"], total)
        if report is None:
            return "fail", [f"no report of version {n} after the reset"]
        problems = take(report, "after the reset")
        if problems:
            return "fail", problems
        if not delivered:  # step 4: nothing about the refusal was verified
            return "not-run", [NOT_CONTACTED_REASON]
        return "pass", []

    def _refusal_boot(self, entry: dict, name: str, forward: Forward, server, obs: dict,
                      prefix: str = "") -> tuple[str, list[str]]:
        """Boot N from a fresh copy with the source switch only, no failure switch (§I)."""
        smbios = [switch_value(self.decl["update"]["source_switch"], forward.url)]
        boot = self._launch(entry, name, forward=forward, smbios=smbios)
        obs["launched"] = True
        try:
            return self._observe_refusal(boot, entry, server, obs, prefix)
        finally:
            boot.stop()

    def run_downgrade(self, entry: dict) -> tuple[str, list[str]]:
        """§I downgrade: the source serves the previous-version artifact, every report stays N."""
        obs: dict = {"versions": [], "requests": 0}
        forward, server = self._start_source(self.args.previous_artifact, self.prev_digest,
                                             "previous-version artifact")
        try:
            verdict, notes = self._refusal_boot(entry, "downgrade", forward, server, obs)
        finally:
            self._stop_source(server, "downgrade")
            entry["observed_versions"] = obs["versions"] or unavailable("no report observed")
            entry["source_requests"] = obs["requests"]
        if verdict == "not-run":
            raise NotRun(notes[0])
        if verdict == "pass" and not self._positive_control():
            raise NotRun(NO_CONTROL_REASON)  # §H: a failed assertion is fail regardless of the control
        return verdict, notes

    def _signature_variant(self, entry: dict, variant: str, source: dict) -> dict:
        """One signature-rejection variant from its own fresh copy, behind the shared endpoint."""
        record = {"name": variant, "verdict": "not-run", "observed_versions": unavailable("variant not booted"),
                  "source_requests": unavailable("variant not booted")}
        payload = self.payloads.get(variant) or {"cause": f"missing input: the {variant} test payload"}
        if "not_producible" in payload:
            record.update(verdict="not-producible", reason=payload["not_producible"])
            return record
        if "cause" in payload:
            record["reason"] = payload["cause"]
            return record
        label = f"{variant} test payload"
        obs: dict = {"versions": [], "requests": 0}
        name = f"signature-rejection-{variant}"
        try:
            if source.get("server") is None:  # one forwarded endpoint and network entry for both (§I)
                source["forward"], source["server"] = self._start_source(payload["path"], payload["digest"], label)
            else:
                fd, size = self._open_source_file(payload["path"], payload["digest"], label)
                self._point_source(source["server"], payload["path"], fd, size)
            try:
                verdict, notes = self._refusal_boot(entry, name, source["forward"], source["server"], obs,
                                                    prefix=f"{variant}/")
            finally:
                self._write_source_log(source["server"], name)
        except Interrupted:
            raise  # SIGTERM/SIGHUP: stop here, don't boot the next variant
        except NotRun as exc:
            verdict, notes = "not-run", [exc.reason]
        except HypervisorExited as exc:
            verdict = "fail" if exc.console_output else "not-run"
            notes = [f"hypervisor exited with status {exc.status}"
                     + (" before a report" if exc.console_output else " before any console output")]
        except Exception as exc:  # noqa: BLE001 - an infrastructure error verifies nothing
            verdict, notes = "not-run", [f"runner error: {type(exc).__name__}: {exc}"]
        if obs.get("launched"):
            record["observed_versions"] = obs["versions"] or unavailable("no report observed")
            record["source_requests"] = obs["requests"]
        record["verdict"] = verdict
        if verdict == "not-run":
            record["reason"] = notes[0]
        elif notes:
            self.notes.setdefault("signature-rejection", []).extend(f"{variant}: {n}" for n in notes)
        return record

    def run_signature_rejection(self, entry: dict) -> tuple[str, list[str]]:
        """§I signature-rejection: two variants; the scenario verdict follows them."""
        source: dict = {}
        try:
            variants = []
            for variant in SIGNATURE_VARIANTS:
                if _received_signals:
                    raise Interrupted()
                variants.append(self._signature_variant(entry, variant, source))
        finally:
            if source.get("server") is not None:
                server = source["server"]
                server.shutdown()
                server.server_close()
                os.close(server.served_fd)
        entry["signature_variants"] = variants
        by_name = {v["name"]: v for v in variants}
        unsigned = by_name["unsigned"]
        if unsigned["verdict"] == "not-producible":
            warning = (f"WARNING: signature-rejection unsigned variant is not-producible ({unsigned['reason']}); "
                       "a pass rests on the untrusted-key variant alone and needs human review (§I).")
            print(warning, file=sys.stderr)
            self.notes.setdefault("warnings", []).append(warning)
        notes = self.notes.pop("signature-rejection", [])
        if any(v["verdict"] == "fail" for v in variants):
            return "fail", notes
        if by_name["untrusted-key"]["verdict"] == "pass" and unsigned["verdict"] in ("pass", "not-producible"):
            if self._positive_control():
                return "pass", notes
            raise NotRun(NO_CONTROL_REASON)
        # A not-producible unsigned variant never makes the scenario pass on its own.
        raise NotRun("; ".join(f"{v['name']}: {v['reason']}" for v in variants if v["verdict"] == "not-run"))

    def run_commit_boundary(self, entry: dict) -> tuple[str, list[str]]:
        """§I commit-boundary: boot the positive scenario's kept state with the failure switch set to N+1."""
        if self.verdicts.get("positive") != "pass":
            raise NotRun(NO_COMMIT_REASON)
        if self.positive_state is None:
            raise NotRun(self.state_cause or "committed state not kept: the positive scenario booted under "
                                              "-snapshot, which discards its writes with the process (§L)")
        n1 = self.args.next_expected_version
        smbios = [switch_value(self.decl["health"]["failure_switch"], n1)]
        versions: list[str] = []
        try:
            boot = self._launch(entry, "commit-boundary", smbios=smbios, overlay=self.positive_state,
                                state_from="positive")
            try:
                total = self._total("readiness", "readiness")
                for phase in ("readiness", "reset-readiness"):
                    if phase == "reset-readiness":
                        boot.serial.discard()  # only a report printed after the reset counts for it
                        if not qmp(boot.qmp_socket, "system_reset"):
                            raise NotRun("the hypervisor didn't acknowledge the VM reset (QMP system_reset)")
                    report = self._await(boot, entry, phase, self.t["readiness"], total)
                    if report is None:
                        return "fail", [f"no report of version {n1} ({phase}): a rollback or a failed boot"]
                    versions.append(report.get("image_version") or "?")
                    problems = self._check(report, n1)
                    if problems:
                        return "fail", [f"{phase}: {p}" for p in problems]
                return "pass", []
            finally:
                boot.stop()
        finally:
            entry["observed_versions"] = versions or unavailable("no report observed")
            self.positive_state.unlink(missing_ok=True)  # power off and discard the state (§I step 3)
            self.positive_state = None

    def run_interrupted_update(self, entry: dict) -> tuple[str, list[str]]:
        """§I interrupted-update: reset once N+1 is delivered, then a complete version must come back."""
        obs: dict = {"versions": [], "requests": 0}
        forward, server = self._serve_next()
        smbios = [switch_value(self.decl["update"]["source_switch"], forward.url)]
        try:
            boot = self._launch(entry, "interrupted-update", forward=forward, smbios=smbios)
            try:
                return self._drive_interruption(boot, entry, server, obs)
            finally:
                boot.stop()
        finally:
            obs["requests"] = len(server.requests)
            self._stop_source(server, "interrupted-update")
            entry["observed_versions"] = obs["versions"] or unavailable("no report observed")
            entry["source_requests"] = obs["requests"]

    def _drive_interruption(self, boot: Boot, entry: dict, server, obs: dict) -> tuple[str, list[str]]:
        n, n1 = self.args.expected_version, self.args.next_expected_version
        total = self._total("readiness", "update_installation", "recovery")
        report = self._await(boot, entry, "readiness", self.t["readiness"], total)
        if report is None:
            return "fail", [f"no report of version {n} before the readiness timeout"]
        obs["versions"].append(report.get("image_version") or "?")
        problems = self._check(report, n)
        if problems:
            return "fail", [f"version {n}: {p}" for p in problems]

        def before_reset(report: Report) -> list[str]:
            entry["report_lines"].append(report.line)
            obs["versions"].append(report.get("image_version") or "?")
            if report.get("image_version") == n1:  # also from a report cut short at the reset
                raise NotRun(f"version {n1} reported before the run could reset the VM")
            return [f"before the reset: {p}" for p in self._check(report, n)]

        # Step 2: wait until the source has sent the whole next-version artifact.
        start = time.monotonic()
        deadline = min(start + self.t["update_installation"], total)
        while not server.delivered.is_set():
            if time.monotonic() >= deadline:
                entry["phases"].append({"name": "payload-delivery", "timeout_s": self.t["update_installation"],
                                        "duration_s": unavailable("the payload wasn't delivered before the timeout")})
                raise NotRun("the local source hadn't finished sending the next-version artifact within the "
                              "update-installation timeout")
            report = boot.next_report(min(time.monotonic() + POLL_INTERVAL_S, deadline))
            if report is not None and (problems := before_reset(report)):
                return "fail", problems
        entry["phases"].append({"name": "payload-delivery", "timeout_s": self.t["update_installation"],
                                "duration_s": round(time.monotonic() - start, 3)})
        settle_console(boot)
        while boot.serial.pending:
            if problems := before_reset(boot.serial.pending.pop(0)):
                return "fail", problems
        if not qmp(boot.qmp_socket, "system_reset"):
            raise NotRun("the hypervisor didn't acknowledge the VM reset (QMP system_reset)")
        reset_at = time.monotonic()
        entry["interruption"] = {"trigger": "payload-delivered",
                                 "after_s": round(max(0.0, reset_at - server.delivered_at), 3)}
        # Step 3: within the recovery timeout, a healthy report of N or N+1; unhealthy ones before it are allowed.
        deadline = min(reset_at + self.t["recovery"], total)
        while True:
            report = boot.next_report(deadline)
            if report is None:
                entry["phases"].append({"name": "recovery", "timeout_s": self.t["recovery"],
                                        "duration_s": unavailable("no healthy report before the timeout")})
                return "fail", [f"no healthy report of {n} or {n1} within the recovery timeout: a failed boot loop"]
            entry["report_lines"].append(report.line)
            version = report.get("image_version")
            obs["versions"].append(version or "?")
            if report.error:
                return "fail", [f"after the reset: malformed report: {report.error}"]
            if version not in (n, n1):
                return "fail", [f"after the reset: version {version} is neither {n} nor {n1}"]
            if report.get("status") == "unhealthy":
                problems = self._check(report, version, "unhealthy")
                if problems:
                    return "fail", [f"after the reset: {p}" for p in problems]
                continue
            entry["phases"].append({"name": "recovery", "timeout_s": self.t["recovery"],
                                    "duration_s": round(time.monotonic() - reset_at, 3)})
            problems = self._check(report, version)
            return ("fail", [f"after the reset: {p}" for p in problems]) if problems else ("pass", [])

    def run_scenario(self, entry: dict) -> None:
        fn = getattr(self, f"run_{entry['name'].replace('-', '_')}")
        try:
            verdict, notes = fn(entry)
            entry["verdict"] = verdict
            self.notes[entry["name"]] = notes
        except NotRun as exc:
            mark_not_run(entry, [(exc.reason, exc.hint)])
        except HypervisorExited as exc:
            if exc.console_output:
                entry["verdict"] = "fail"
                self.notes[entry["name"]] = [f"the VM stopped (hypervisor status {exc.status}) before a report"]
            else:
                mark_not_run(entry, [(f"hypervisor exited with status {exc.status} before any console output; "
                                      f"see {entry['name']}*.hypervisor.log", self.qemu_hint)])
        except Exception as exc:  # noqa: BLE001 - an infrastructure error verifies nothing
            mark_not_run(entry, [(f"runner error: {type(exc).__name__}: {exc}", None)])

    # ---- orchestration ----------------------------------------------------
    def execute(self) -> dict:
        args = self.args
        declaration = self.read_declaration()
        decl = self.decl or {}
        fw_type = decl.get("image", {}).get("firmware", "uefi") if self.decl else None
        field_updated = decl.get("update_model") == "field-updated" if self.decl else None
        artifact = self.artifact_record(args.artifact, args.expected_version, "artifact")
        commit = args.commit
        if not commit:
            self._cause("missing input: --commit")
            commit = unavailable("no image-definition commit given")
        elif not COMMIT_RE.match(commit):
            self._cause("--commit must be the full commit id of the image definition")
            commit = unavailable("the given commit isn't a full commit id")
        if field_updated:
            next_artifact = self.artifact_record(args.next_artifact, args.next_expected_version, "next-artifact",
                                                 scenarios=("rollback", "positive", "interrupted-update"))
            previous_artifact = self.artifact_record(args.previous_artifact, args.previous_expected_version,
                                                     "previous-artifact", scenarios=("downgrade",))
            test_payload, unsigned_payload = (self.payload_record(v) for v in SIGNATURE_VARIANTS)
        else:
            next_artifact = previous_artifact = test_payload = unsigned_payload = unavailable(
                "update_model isn't field-updated" if self.decl else "declaration not usable")

        arch_record = self.resolve_arch() if self.decl else unavailable("declaration not usable")
        self.arch = arch_record.get("name") if "name" in arch_record else None
        h_arch = host_arch()
        hyp = {"name": unavailable("no guest architecture"), "version": unavailable("no hypervisor found")}
        machine_type: str | dict = unavailable("no hypervisor found")
        acceleration: dict = unavailable("no hypervisor found; acceleration wasn't probed")
        firmware = {"type": fw_type or unavailable("declaration not usable"),
                    "build": unavailable("no firmware was selected"), "secure_boot": unavailable("nothing booted")}
        self.secure = decl.get("boot_chain", {}).get("secure_boot") == "implemented"
        self.need_tpm = decl.get("boot_chain", {}).get("measured_boot") == "implemented"
        self.hypervisor = None
        factor = 1.0
        self.qemu_hint = None

        if fw_type in ("bios", "other"):
            self._cause(f"firmware {fw_type} is out of scope of boot verification (§A)")
        elif self.arch:
            binary = f"qemu-system-{QEMU_TARGET[self.arch]}"
            self.qemu_hint = f"Install the QEMU system emulator for {self.arch} (for example {QEMU_PACKAGE[self.arch]})."
            self.hypervisor = shutil.which(binary)
            if fw_type == "u-boot":
                self._cause(f"precondition failed: {UBOOT_SWITCH_REASON}", scenarios=SWITCH_SCENARIOS)
                self._cause(f"precondition failed: {UBOOT_UUID_REASON}", scenarios=("identity",))
            else:
                # A qemu-fw-cfg switch under UEFI travels over the same unconfirmed fw_cfg (§H), which
                # blocks only a scenario that sets that switch.
                self._cause(f"precondition failed: {SWITCH_UNVERIFIED_REASON}",
                            scenarios=fw_cfg_switch_scenarios(self.decl))
            if field_updated and "commit-boundary" in args.scenarios:
                # §L: -snapshot discards the positive scenario's writes with its process, so the
                # committed state needs an overlay file, which qemu-img creates.
                self.qemu_img = shutil.which("qemu-img")
                if self.qemu_img is None:
                    self._cause("precondition failed: committed state can't be kept: qemu-img not found to create "
                                "an overlay, and -snapshot discards the positive scenario's writes (§L)",
                                "Install qemu-img (for example qemu-utils).", scenarios=("commit-boundary",))
            if self.hypervisor is None:
                hyp["name"] = unavailable(f"{binary} not found on PATH")
                self._cause(f"precondition failed: hypervisor {binary} not found", self.qemu_hint)
            else:
                hyp["name"] = self.hypervisor
                hyp["version"] = self._qemu_version()
                machine_type = self.machine_type = MACHINE_TYPE[self.arch]
                kvm = kvm_usable(self.arch, h_arch)
                self.accel = "kvm" if kvm else "tcg"
                if kvm:
                    acceleration = {"mode": "hardware"}
                else:
                    factor = max(MIN_EMULATION_FACTOR, args.emulation_factor)
                    why = "cross-architecture guest" if self.arch != h_arch else "no usable /dev/kvm"
                    acceleration = {"mode": "emulation", "timeout_factor": factor,
                                    "warning": f"Emulated boot ({why}); every timeout scaled by {factor:g}."}
                    print(f"WARNING: {acceleration['warning']}", file=sys.stderr)
                if "identity" in args.scenarios and fw_type == "uefi" and not self._supports_uuid():
                    self._cause("precondition failed: the hypervisor can't assign a machine UUID (-uuid)",
                                self.qemu_hint, scenarios=("identity",))
            self.fw_type = fw_type
            if fw_type in ("uefi", "u-boot"):
                self.fw_code, self.fw_vars = self.find_firmware(self.arch, fw_type, self.secure)
                if self.fw_code:
                    firmware["build"] = " + ".join(p for p in (self.fw_code, self.fw_vars) if p)
            if self.need_tpm and shutil.which("swtpm") is None:
                self._cause("precondition failed: TPM emulator swtpm not found (measured_boot implemented)",
                            "Install swtpm.")
        if "digest" in artifact:
            self.artifact_format, refusal = inspect_drive(args.artifact)
            if refusal:
                self._cause(f"artifact refused: {refusal}, which could reach a host file or URL (§B)")
        if field_updated and "digest" in next_artifact:
            self.next_digest = next_artifact["digest"]
            _, refusal = inspect_drive(args.next_artifact)
            if refusal:
                self._cause(f"next artifact refused: {refusal}, which could reach a host file or URL (§B)",
                            scenarios=("rollback", "positive", "interrupted-update"))
        if field_updated and "digest" in previous_artifact:
            self.prev_digest = previous_artifact["digest"]
            if (compare_versions(args.previous_expected_version, args.expected_version) or 0) > 0:
                self._cause(f"precondition failed: the previous-version artifact's version "
                            f"{args.previous_expected_version} is newer than N's version {args.expected_version}; "
                            "the downgrade scenario needs one that isn't newer (§H)", scenarios=("downgrade",))
            _, refusal = inspect_drive(args.previous_artifact)
            if refusal:
                self._cause(f"previous-version artifact refused: {refusal}, which could reach a host file or URL "
                            "(§B)", scenarios=("downgrade",))

        update = decl.get("update") or {}
        timeouts, self.t = compute_timeouts(
            {"readiness": args.timeout_readiness, "update_installation": args.timeout_update,
             "rollback": args.timeout_rollback, "update_window": args.timeout_update_window,
             "recovery": args.timeout_recovery, "total_margin": args.timeout_margin},
            factor, update.get("max_boot_attempts"), bool(field_updated))
        if field_updated and self.t["rollback"] is None:
            self._cause("no update.max_boot_attempts, so no rollback timeout", scenarios=("rollback",))
        if field_updated and self.t["recovery"] is None:
            self._cause("no update.max_boot_attempts, so no recovery timeout", scenarios=("interrupted-update",))
        selected = set(args.scenarios)
        self.keep_positive_state = bool(self.qemu_img) and {"positive", "commit-boundary"} <= selected

        trace = dict(DEFAULT_TRACE_IDS)
        for item in args.trace_id:
            name, _, value = item.partition("=")
            if name in trace and value:
                trace[name] = value
        scenarios = []
        for name, required, excluded in plan_scenarios(field_updated, selected):
            entry = new_scenario(name, required, [trace[name]])
            causes = list(self.global_causes) + self.causes[name]
            if excluded:
                causes.insert(0, ("excluded by the operator", None))
            if _received_signals:
                causes.append((interrupt_reason(), None))
            if causes:
                mark_not_run(entry, causes)
            else:
                self.run_scenario(entry)
            self.verdicts[name] = entry["verdict"]
            scenarios.append(entry)

        verdict, exit_status = aggregate_verdict(scenarios)
        if self.booted:
            firmware["secure_boot"] = bool(self.secure_boot_ran)
        names = [s["name"] for s in scenarios]
        return {
            # v1.2 for every run: §G requires it for a field-updated image and for any run that
            # plans an update-security scenario, and the v1.2 schema admits a run without them.
            "schema_version": "1.2",
            "run_timestamp": self.started.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "outcome": {"overall_verdict": verdict, "exit_status": exit_status},
            "host": {"os": host_os(), "kernel": platform.release() or unavailable("kernel release unknown"),
                     "architecture": h_arch or unavailable("host architecture unknown")},
            "artifact": artifact,
            "next_artifact": next_artifact,
            "previous_artifact": previous_artifact,
            "test_payload": test_payload,
            "unsigned_payload": unsigned_payload,
            "image_definition_commit": commit,
            "declaration": declaration,
            "firmware": firmware,
            "tpm_emulated": self.tpm_used if self.booted else unavailable("nothing booted"),
            "hypervisor": hyp,
            "machine": {"architecture": arch_record, "machine_type": machine_type,
                        "cross_architecture": (self.arch != h_arch) if self.arch else unavailable(
                            "no guest architecture")},
            "acceleration": acceleration,
            "timeouts": timeouts,
            "scenarios": scenarios,
            "rollback_observed_versions": self.rollback_versions or unavailable(
                "rollback scenario didn't boot" if "rollback" in names else "rollback scenario not planned"),
            "identity_boots": self.identity_boots or unavailable(
                "identity scenario didn't boot" if "identity" in names else "identity scenario excluded by the operator"),
            "serial_logs": self.serial_logs or unavailable("no boot started"),
        }

    def _qemu_version(self) -> str | dict:
        try:
            out = subprocess.run([self.hypervisor, "-version"], capture_output=True, text=True,
                                 timeout=30, check=False).stdout
        except (OSError, subprocess.TimeoutExpired) as exc:
            return unavailable(f"version query failed: {exc}")
        first = out.strip().splitlines()[0] if out.strip() else ""
        return first or unavailable("the hypervisor printed no version")

    def _supports_uuid(self) -> bool:
        try:
            out = subprocess.run([self.hypervisor, "-help"], capture_output=True, text=True,
                                 timeout=30, check=False).stdout
        except (OSError, subprocess.TimeoutExpired):
            return False
        return re.search(r"^-uuid\b", out, re.MULTILINE) is not None


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def parse_args(argv: list[str] | None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Non-interactive image boot verification "
                                            "(spec/project/image-boot-verification/).")
    p.add_argument("--declaration", type=Path, help="image-declaration.yaml of the image")
    p.add_argument("--artifact", type=Path, help="artifact under test (version N)")
    p.add_argument("--expected-version", help="image_version the artifact must report")
    p.add_argument("--commit", help="full commit id of the image definition the artifact was built from")
    p.add_argument("--next-artifact", type=Path,
                   help="next-version artifact (N+1) for rollback, positive, and interrupted-update")
    p.add_argument("--next-expected-version", help="image_version N+1 must report")
    p.add_argument("--previous-artifact", type=Path,
                   help="artifact not newer than N for the downgrade scenario (N-1, or N itself)")
    p.add_argument("--previous-expected-version", help="image_version of the previous-version artifact")
    p.add_argument("--untrusted-payload", type=Path,
                   help="signature-rejection test payload signed with a throwaway key the image doesn't trust")
    p.add_argument("--untrusted-payload-version", help="the newer version the untrusted-key payload offers")
    p.add_argument("--untrusted-payload-production", help="how the untrusted-key payload was produced")
    p.add_argument("--untrusted-key-id", help="identifier or fingerprint of the throwaway key; never key material")
    p.add_argument("--unsigned-payload", type=Path, help="signature-rejection test payload with no signature")
    p.add_argument("--unsigned-payload-version", help="the newer version the unsigned payload offers")
    p.add_argument("--unsigned-payload-production", help="how the unsigned payload was produced")
    p.add_argument("--unsigned-not-producible", metavar="REASON",
                   help="why the update.mechanism's payload format can't carry an unsigned payload")
    p.add_argument("--arch", choices=sorted(QEMU_TARGET), help="guest architecture (§A)")
    p.add_argument("--scenarios", type=lambda s: [x.strip() for x in s.split(",") if x.strip()],
                   default=list(SCENARIOS), help=f"comma-separated subset of {','.join(SCENARIOS)}")
    p.add_argument("--trace-id", action="append", default=[], metavar="SCENARIO=ID",
                   help="requirement or TC-ID per scenario (§E); repeatable")
    p.add_argument("--out", type=Path, help="new or empty run directory (default .image-boot-verify/<YYYY-MM-DD-HHMM>/)")
    p.add_argument("--firmware-code", help="firmware code image (UEFI) or U-Boot build (-bios)")
    p.add_argument("--firmware-vars", help="UEFI variables template; copied per boot")
    p.add_argument("--memory", type=int, default=2048, help="guest memory in MiB (default 2048)")
    for name, dest in (("readiness", "timeout_readiness"), ("update", "timeout_update"),
                       ("rollback", "timeout_rollback"), ("update-window", "timeout_update_window"),
                       ("recovery", "timeout_recovery"), ("margin", "timeout_margin")):
        p.add_argument(f"--timeout-{name}", dest=dest, type=float, help=f"override the §J {name} timeout (s)")
    p.add_argument("--emulation-factor", type=float, default=MIN_EMULATION_FACTOR,
                   help="timeout factor under emulation (§J, at least 5)")
    args = p.parse_args(argv)
    unknown = sorted(set(args.scenarios) - set(SCENARIOS))
    if unknown:
        p.error(f"unknown scenario(s): {', '.join(unknown)}")
    for dest in ("timeout_readiness", "timeout_update", "timeout_rollback", "timeout_update_window",
                 "timeout_recovery", "timeout_margin"):
        value = getattr(args, dest)
        if value is not None and value <= 0:
            p.error(f"--{dest.replace('_', '-')} must be positive")
    if args.unsigned_payload is not None and args.unsigned_not_producible is not None:
        p.error("pass either --unsigned-payload or --unsigned-not-producible, not both")
    if args.unsigned_not_producible is not None and not args.unsigned_not_producible.strip():
        p.error("--unsigned-not-producible needs the reason the payload format admits no unsigned payload")
    for dest in ("untrusted_key_id", "untrusted_payload_production", "unsigned_payload_production"):
        value = getattr(args, dest)
        if value is not None and looks_like_key_material(value, identifier=dest == "untrusted_key_id"):
            # The value isn't echoed: only an identifier may reach the protocol or any log (§I).
            p.error(f"--{dest.replace('_', '-')} looks like key material; pass only the key's identifier or "
                    "fingerprint and a description of how the payload was produced")
    return args


_HEX_FINGERPRINT = re.compile(r"(?:[0-9A-Fa-f]{2}[:\s]?)+")
# A digest-prefixed fingerprint as ssh-keygen -l prints it: SHA256:<base64 or hex>, MD5:<hex pairs>.
_DIGEST_FINGERPRINT = re.compile(r"(?:SHA256|SHA384|SHA512):(?:[A-Za-z0-9+/]{43}|[A-Za-z0-9+/]{64}|"
                                 r"[A-Za-z0-9+/]{86}|[0-9A-Fa-f]{40,128})=*|MD5:[0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2}){15}")
_BASE64_BLOB = re.compile(r"[A-Za-z0-9+/=]{40,}")


def looks_like_key_material(value: str, identifier: bool = True) -> bool:
    """True for a value that may carry key material (§I: only the key's identifier is recorded).

    Refuses a PEM marker, a line break, an over-long identifier, and any
    whitespace-free token of 40 or more base64 characters that isn't a plain hex
    fingerprint or a digest-prefixed one (SHA256:..., MD5:...), so a pasted public
    or private key never reaches the protocol.
    """
    if any(c in value for c in "\r\n") or "-----BEGIN" in value or "PRIVATE KEY" in value.upper():
        return True
    if identifier and len(value) > 256:
        return True
    return any(_BASE64_BLOB.fullmatch(part) and not _HEX_FINGERPRINT.fullmatch(part)
               for token in value.split() if not _DIGEST_FINGERPRINT.fullmatch(token)
               for part in token.split(":"))


def _run_dir(args: argparse.Namespace) -> Path:
    if args.out is not None:
        if args.out.is_dir() and any(args.out.iterdir()):
            raise FileExistsError(f"--out {args.out} isn't empty; pass a new or empty directory so no earlier "
                                  "protocol is taken for this run's")
        args.out.mkdir(parents=True, exist_ok=True)
        return args.out
    base = Path(".image-boot-verify") / dt.datetime.now().strftime("%Y-%m-%d-%H%M")
    candidate, n = base, 1
    while candidate.exists():
        n += 1
        candidate = base.with_name(f"{base.name}-{n}")
    candidate.mkdir(parents=True)
    if shutil.which("git"):
        ignored = subprocess.run(["git", "check-ignore", "-q", str(candidate)], capture_output=True, check=False)
        if ignored.returncode == 1:
            print(f"WARNING: {candidate} isn't git-ignored; add .image-boot-verify/ to .gitignore (§G).",
                  file=sys.stderr)
    return candidate


def finalise(protocol: dict, out: Path, notes: dict) -> int:
    """Validate the protocol, publish it as protocol.json only when valid, return the exit status."""
    candidate = out / "protocol.candidate.json"
    candidate.write_text(json.dumps(protocol, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    code, payload = run_validator(candidate, "boot-protocol")
    verdict, exit_status = protocol["outcome"]["overall_verdict"], protocol["outcome"]["exit_status"]
    if code == 0:
        final = out / "protocol.json"
    else:
        final = out / ("protocol.invalid.json" if code == 1 else "protocol.unvalidated.json")
        print(f"ERROR: the protocol {'failed validation' if code == 1 else 'could not be validated'}; "
              f"kept as {final.name}, not handed on as evidence (§G): "
              f"{json.dumps(payload.get('violations') or payload.get('cause'))}", file=sys.stderr)
        if exit_status == 0:
            exit_status = 2  # never a green exit without a valid protocol
    candidate.replace(final)
    summary = {"overall_verdict": verdict, "exit_status": exit_status, "protocol": str(final),
               "protocol_valid": code == 0,
               "scenarios": {s["name"]: s["verdict"] for s in protocol["scenarios"]},
               "notes": {k: v for k, v in notes.items() if v}}
    print(json.dumps(summary, indent=2))
    return exit_status


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        out = _run_dir(args)
    except OSError as exc:
        print(f"ERROR: run directory unusable: {exc}; nothing verified", file=sys.stderr)
        return EXIT_STATUS["not-run"]
    # SIGTERM/SIGHUP only record the signal; the run raises at its next polling
    # point, stops the boot, and still writes the protocol with the rest not-run.
    _received_signals.clear()
    previous = {sig: signal.signal(sig, _on_signal) for sig in INTERRUPT_SIGNALS}
    try:
        run = Run(args, out)
        try:
            protocol = run.execute()
        finally:
            shutil.rmtree(run.sock_dir, ignore_errors=True)
        return finalise(protocol, out, run.notes)
    finally:
        for sig, handler in previous.items():
            signal.signal(sig, handler)


if __name__ == "__main__":
    raise SystemExit(main())
