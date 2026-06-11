"""Test protocol generator — the machine-generated audit trail.

Reference profile: Selenium + pytest. Realises the `spec/project/e2e-test-automation/`
requirement that a run can emit a readable, machine-generated protocol. Activated
via the ``--generate-protocol`` flag (wired in conftest.py); writes
``test-reports/e2e/<timestamp>/protocol.md`` containing:

  * Metadata (date, git commit, branch, OS, browser, Python version)
  * Pass/fail/skip summary
  * Per-requirement coverage with links to the requirement / test-case specs
  * Failure details with messages and failure screenshots
  * Per-class result tables and an end-of-report screenshot gallery

Spec resolution is configurable so this file is project-agnostic:
  * E2E_SPEC_REQ_DIR   — dir holding requirement specs   (default: spec/req)
  * E2E_SPEC_TC_DIR    — dir holding test-case specs      (default: spec/cases)
  * E2E_REQ_PATTERN    — regex capturing a requirement id (default: req[_-]?(\\d+))
  * E2E_TC_ID_PATTERN  — regex capturing a TC-ID          (default: (TC-[A-Z0-9-]+))
Spec resolution degrades gracefully to "—" when the dirs do not exist.
"""

from __future__ import annotations

import os
import platform
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

# ── Spec resolution (configurable) ───────────────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SPEC_REQ_DIR = _REPO_ROOT / os.environ.get("E2E_SPEC_REQ_DIR", "spec/req")
_SPEC_TC_DIR = _REPO_ROOT / os.environ.get("E2E_SPEC_TC_DIR", "spec/cases")

_REQ_PATTERN = re.compile(os.environ.get("E2E_REQ_PATTERN", r"req[_-]?(\d+)"), re.IGNORECASE)
_TC_ID_PATTERN = re.compile(os.environ.get("E2E_TC_ID_PATTERN", r"(TC-[A-Z0-9-]+)"))


def _find_req_spec(req_num: str) -> tuple[str, str] | None:
    """Find the requirement spec file for a requirement id. Returns (path, title)."""
    if not _SPEC_REQ_DIR.is_dir():
        return None
    for f in _SPEC_REQ_DIR.iterdir():
        if req_num in f.stem and f.suffix == ".md":
            title = f.stem.split("_", 1)[1].replace("-", " ") if "_" in f.stem else f.stem
            return str(f.relative_to(_REPO_ROOT)), title
    return None


def _find_tc_spec(req_num: str) -> tuple[str, str] | None:
    """Find the test-case spec file for a requirement id. Returns (path, title)."""
    if not _SPEC_TC_DIR.is_dir():
        return None
    for f in _SPEC_TC_DIR.iterdir():
        if req_num in f.stem and f.suffix == ".md":
            title = ""
            try:
                for line in f.read_text(encoding="utf-8").splitlines():
                    if line.startswith("title:"):
                        title = line.split(":", 1)[1].strip().strip('"').strip("'")
                        break
            except Exception:
                pass
            return str(f.relative_to(_REPO_ROOT)), title or f.stem
    return None


def _extract_req_num(nodeid: str) -> str | None:
    """Extract a requirement id from a pytest nodeid."""
    m = _REQ_PATTERN.search(nodeid)
    return m.group(1) if m else None


def _extract_tc_id(docstring: str) -> str | None:
    """Extract a TC-ID from a test docstring."""
    m = _TC_ID_PATTERN.search(docstring)
    return m.group(1) if m else None


_req_spec_cache: dict[str, tuple[str, str] | None] = {}
_tc_spec_cache: dict[str, tuple[str, str] | None] = {}


def _get_req_spec(req_num: str) -> tuple[str, str] | None:
    if req_num not in _req_spec_cache:
        _req_spec_cache[req_num] = _find_req_spec(req_num)
    return _req_spec_cache[req_num]


def _get_tc_spec(req_num: str) -> tuple[str, str] | None:
    if req_num not in _tc_spec_cache:
        _tc_spec_cache[req_num] = _find_tc_spec(req_num)
    return _tc_spec_cache[req_num]


# ── Data classes ─────────────────────────────────────────────────────────────
@dataclass
class ScreenshotEntry:
    """A single screenshot checkpoint captured during a test."""

    filename: str
    description: str
    test_nodeid: str


@dataclass
class TestResult:
    nodeid: str
    outcome: str  # "passed", "failed", "skipped"
    duration: float = 0.0
    message: str = ""
    docstring: str = ""
    screenshots: list[ScreenshotEntry] = field(default_factory=list)


@dataclass
class ProtocolGenerator:
    results: list[TestResult] = field(default_factory=list)
    start_time: datetime | None = None

    def add_result(self, result: TestResult) -> None:
        self.results.append(result)

    @staticmethod
    def _class_display_name(nodeid: str) -> str:
        parts = nodeid.split("::")
        return parts[-2] if len(parts) >= 2 else parts[0]

    @staticmethod
    def _test_display_name(nodeid: str) -> str:
        return nodeid.split("::")[-1]

    @staticmethod
    def _file_display(nodeid: str) -> str:
        return nodeid.split("::")[0]

    @staticmethod
    def _outcome_icon(outcome: str) -> str:
        return {"passed": "PASS", "failed": "FAIL", "skipped": "SKIP"}.get(
            outcome, outcome.upper()
        )

    def generate(self, output_dir: Path) -> Path:
        """Write the protocol Markdown file and return its path."""
        output_dir.mkdir(parents=True, exist_ok=True)
        filepath = output_dir / "protocol.md"

        passed = sum(1 for r in self.results if r.outcome == "passed")
        failed = sum(1 for r in self.results if r.outcome == "failed")
        skipped = sum(1 for r in self.results if r.outcome == "skipped")
        total = len(self.results)

        git_commit = _git("rev-parse", "--short", "HEAD")
        git_branch = _git("rev-parse", "--abbrev-ref", "HEAD")
        os_info = f"{platform.system()} {platform.release()}"
        python_version = platform.python_version()
        browser_info = os.environ.get("E2E_BROWSER", "chrome (headless)")
        device_info = os.environ.get("E2E_DEVICE", "desktop")

        lines: list[str] = []
        date_str = (
            f"{self.start_time:%Y-%m-%d %H:%M:%S} UTC" if self.start_time else "n/a"
        )

        # ── Header & metadata ─────────────────────────────────────────────
        lines.extend([
            f"# E2E Test Protocol — {date_str}",
            "",
            "## Metadata",
            "",
            "| Field | Value |",
            "|---|---|",
            f"| **Date** | {date_str} |",
            f"| **Commit** | `{git_commit}` |",
            f"| **Branch** | {git_branch} |",
            f"| **OS** | {os_info} |",
            f"| **Browser** | {browser_info} |",
            f"| **Device** | {device_info} |",
            f"| **Python** | {python_version} |",
            "",
        ])

        # ── Summary ───────────────────────────────────────────────────────
        lines.extend([
            "## Summary",
            "",
            "| Total | Passed | Failed | Skipped |",
            "|-------|--------|--------|---------|",
            f"| {total} | {passed} | {failed} | {skipped} |",
            "",
        ])
        if total > 0:
            lines.extend([f"Pass rate: **{passed / total * 100:.1f}%** ({passed}/{total})", ""])

        # ── Covered requirements ──────────────────────────────────────────
        req_seen: dict[str, int] = {}
        for r in self.results:
            rn = _extract_req_num(r.nodeid)
            if rn:
                req_seen[rn] = req_seen.get(rn, 0) + 1
        if req_seen:
            lines.extend([
                "## Covered requirements",
                "",
                "| Requirement | Spec | Test cases | Tests |",
                "|-------------|------|-----------|-------|",
            ])
            for rn in sorted(req_seen):
                req_spec = _get_req_spec(rn)
                tc_spec = _get_tc_spec(rn)
                req_link = f"[{req_spec[1]}]({req_spec[0]})" if req_spec else "—"
                tc_link = f"[cases]({tc_spec[0]})" if tc_spec else "—"
                lines.append(f"| {rn} | {req_link} | {tc_link} | {req_seen[rn]} |")
            lines.append("")

        # ── Failed tests ──────────────────────────────────────────────────
        failed_results = [r for r in self.results if r.outcome == "failed"]
        if failed_results:
            lines.extend(["## Failed tests", ""])
            for r in failed_results:
                test_name = self._test_display_name(r.nodeid)
                req_num = _extract_req_num(r.nodeid)
                tc_id = _extract_tc_id(r.docstring) if r.docstring else None
                lines.extend([f"### FAIL `{test_name}`", "", f"- **File:** `{self._file_display(r.nodeid)}`"])
                if r.docstring:
                    lines.append(f"- **Description:** {r.docstring}")
                if tc_id:
                    lines.append(f"- **Test case:** {tc_id}")
                if req_num:
                    req_spec = _get_req_spec(req_num)
                    if req_spec:
                        lines.append(f"- **Requirement:** [{req_num} {req_spec[1]}]({req_spec[0]})")
                error_msg = r.message.replace("\n", "\n  ") if r.message else "n/a"
                lines.extend([f"- **Error:**", f"  ```", f"  {error_msg[:500]}", f"  ```"])
                for s in [s for s in r.screenshots if s.filename.startswith("FAILURE_")]:
                    lines.append(f"- **Screenshot:** ![{s.description}](screenshots/{s.filename})")
                lines.append("")

        # ── Per-class detail ──────────────────────────────────────────────
        lines.extend(["## Results in detail", ""])
        class_groups: dict[str, list[TestResult]] = {}
        for r in self.results:
            class_groups.setdefault(self._class_display_name(r.nodeid), []).append(r)

        for cls_name, results in class_groups.items():
            cls_passed = sum(1 for r in results if r.outcome == "passed")
            cls_failed = sum(1 for r in results if r.outcome == "failed")
            cls_skipped = sum(1 for r in results if r.outcome == "skipped")
            cls_total = len(results)
            req_num = _extract_req_num(results[0].nodeid)
            badge = "PASS" if cls_failed == 0 else "FAIL"
            lines.extend([f"### {cls_name} [{badge}]", ""])

            if req_num:
                req_spec = _get_req_spec(req_num)
                tc_spec = _get_tc_spec(req_num)
                refs: list[str] = []
                if req_spec:
                    refs.append(f"**Requirement:** [{req_num} — {req_spec[1]}]({req_spec[0]})")
                if tc_spec:
                    refs.append(f"**Test cases:** [{req_num} — {tc_spec[1]}]({tc_spec[0]})")
                if refs:
                    lines.extend(refs + [""])

            summary = f"*{cls_total} tests: {cls_passed} passed"
            summary += f", {cls_failed} failed" if cls_failed else ""
            summary += f", {cls_skipped} skipped" if cls_skipped else ""
            summary += "*"
            lines.extend([summary, "", f"**File:** `{self._file_display(results[0].nodeid)}`", ""])

            lines.extend([
                "| Test | TC-ID | Result | Duration | Description |",
                "|------|-------|--------|----------|-------------|",
            ])
            for r in results:
                tc_id = _extract_tc_id(r.docstring) if r.docstring else None
                desc = r.docstring
                if desc and tc_id:
                    desc = desc.replace(tc_id, "").lstrip(":").lstrip().lstrip("-").strip()
                desc = desc[:100] if desc else ""
                lines.append(
                    f"| `{self._test_display_name(r.nodeid)}` | {tc_id or ''} | "
                    f"{self._outcome_icon(r.outcome)} | {r.duration:.2f}s | {desc} |"
                )
            lines.append("")

            class_shots = [
                s for r in results for s in r.screenshots
                if not s.filename.startswith("FAILURE_")
            ]
            if class_shots:
                lines.extend(["**Screenshots:**", ""])
                for s in class_shots:
                    lines.extend([f"*{s.description}*", "", f"![{s.description}](screenshots/{s.filename})", ""])

        # ── Screenshot gallery ────────────────────────────────────────────
        shots_dir = output_dir / "screenshots"
        if shots_dir.is_dir():
            all_shots = sorted(shots_dir.iterdir())
            if all_shots:
                lines.extend([
                    "## Screenshot gallery",
                    "",
                    "| No. | File | Description |",
                    "|-----|------|-------------|",
                ])
                desc_map = {s.filename: s.description for r in self.results for s in r.screenshots}
                for i, f in enumerate([f for f in all_shots if f.suffix.lower() == ".png"], 1):
                    desc = desc_map.get(f.name, f.stem.replace("_", " "))
                    lines.append(f"| {i:03d} | ![{f.name}](screenshots/{f.name}) | {desc} |")
                lines.append("")

        lines.extend(["---", f"*Protocol generated automatically at {date_str}*", ""])
        filepath.write_text("\n".join(lines), encoding="utf-8")
        return filepath


def _git(*args: str) -> str:
    """Run a git command and return stripped stdout, or 'n/a' on failure."""
    try:
        result = subprocess.run(
            ["git", *args], capture_output=True, text=True, timeout=5, check=False
        )
        return result.stdout.strip() or "n/a"
    except Exception:
        return "n/a"
