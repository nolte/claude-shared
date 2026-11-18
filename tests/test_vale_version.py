"""Every Vale input is pinned to content, from one committed source (#768).

`.vale-version` holds the binary's version and the SHA-256 of its Linux_64-bit
release asset; `scripts/install_vale.sh` is the only installer, and `.vale.ini`
names each style package by a versioned release URL. Renovate bumps
`VALE_VERSION` but can't recompute the checksum, so the checksum line names the
asset file it belongs to and these tests fail until both agree again.
"""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
PIN = REPO / ".vale-version"
INSTALLER = REPO / "scripts" / "install_vale.sh"
WORKFLOWS = REPO / ".github" / "workflows"

VERSION_LINE = re.compile(r"^VALE_VERSION=(\d+\.\d+\.\d+)$", re.M)
CHECKSUM_LINE = re.compile(r"^VALE_SHA256=([0-9a-f]{64})  (vale_(\S+)_Linux_64-bit\.tar\.gz)$", re.M)


def _pins(text: str) -> tuple[str, str]:
    versions = VERSION_LINE.findall(text)
    checksums = CHECKSUM_LINE.findall(text)
    assert len(versions) == 1, f"expected one VALE_VERSION line in .vale-version, found {versions}"
    assert len(checksums) == 1, "expected one 'VALE_SHA256=<sha256>  vale_<x.y.z>_Linux_64-bit.tar.gz' line"
    return versions[0], checksums[0][2]


def test_checksum_belongs_to_the_pinned_version():
    version, checksum_version = _pins(PIN.read_text(encoding="utf-8"))
    assert checksum_version == version, (
        f"VALE_SHA256 is for Vale {checksum_version}, but VALE_VERSION is {version}: copy the "
        f"Linux_64-bit line of vale_{version}_checksums.txt from the v{version} release into .vale-version")


def test_every_style_package_is_a_versioned_release_url():
    text = (REPO / ".vale.ini").read_text(encoding="utf-8")
    packages = re.search(r"^Packages\s*=\s*(.+)$", text, re.M)
    assert packages, ".vale.ini has no Packages line"
    entries = [entry.strip() for entry in packages.group(1).split(",")]
    floating = [entry for entry in entries
                if not re.fullmatch(r"https://github\.com/[^/]+/[^/]+/releases/download/v[0-9.]+/[^/]+\.zip", entry)]
    assert not floating, f"style packages not pinned to a release URL: {floating}"


def test_workflows_install_vale_only_through_the_verifying_script():
    installs = 0
    for workflow in sorted(WORKFLOWS.glob("*.yml")):
        text = workflow.read_text(encoding="utf-8")
        assert "VALE_VERSION" not in text, f"{workflow.name} restates the Vale version; .vale-version is the source"
        assert not re.search(r"releases/download/.*vale_", text), \
            f"{workflow.name} downloads Vale inline instead of through scripts/install_vale.sh"
        installs += text.count("scripts/install_vale.sh")
    assert installs >= 3, "ci.yml (lint, test) and pr-lint.yml install Vale through scripts/install_vale.sh"


@pytest.mark.parametrize("pin, message", [
    pytest.param("VALE_VERSION=9.9.9\nVALE_SHA256=" + "0" * 64 + "  vale_3.15.2_Linux_64-bit.tar.gz\n",
                 "VALE_SHA256 is for", id="checksum-for-another-version"),
    pytest.param("VALE_VERSION=3.15.2\n", "needs one VALE_VERSION", id="checksum-missing"),
    pytest.param("VALE_VERSION=3.15.2\nVALE_SHA256=$(touch pwned)  vale_3.15.2_Linux_64-bit.tar.gz\n",
                 "needs one VALE_VERSION", id="not-a-checksum"),
])
def test_installer_refuses_an_inconsistent_pin_before_downloading(tmp_path, pin, message):
    (tmp_path / "scripts").mkdir()
    shutil.copy2(INSTALLER, tmp_path / "scripts" / "install_vale.sh")
    (tmp_path / ".vale-version").write_text(pin, encoding="utf-8")
    proc = subprocess.run(["bash", str(tmp_path / "scripts" / "install_vale.sh"), str(tmp_path / "bin")],
                          capture_output=True, text=True, check=False, timeout=30)
    assert proc.returncode == 1
    assert message in proc.stderr
    assert not (tmp_path / "bin").exists()
    assert not (tmp_path / "pwned").exists()
