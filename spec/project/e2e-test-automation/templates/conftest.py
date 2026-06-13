"""E2E test configuration — browser fixtures, screenshots, CLI options, protocol.

Reference profile: Selenium + pytest. Realises the binding requirements in
`spec/project/e2e-test-automation/` for the deterministic browser fixture,
screenshot checkpoints, the machine-generated protocol, marker registration,
and crash-resilient checkpointing.

Adapt the marked spots to your application:
  * `--base-url` default — the host of your running app under test
  * `seed_data` — replace the placeholder with your app's idempotent seeding
  * `_login` / `authenticated_session` — wire your app's auth flow, or delete
    both if the app needs no login
Everything else (options, device profiles, browser/screenshot fixtures, the
report hook, JSONL checkpointing) is domain-agnostic and works as-is.
"""

from __future__ import annotations

import importlib.util as _ilu
import os
import shutil
import sys as _sys
from datetime import datetime, timezone
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService

try:
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager
except ImportError:  # webdriver-manager is optional when drivers are on PATH
    ChromeDriverManager = None  # type: ignore[assignment,misc]
    GeckoDriverManager = None  # type: ignore[assignment,misc]


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register custom CLI options for E2E tests."""
    parser.addoption(
        "--browser",
        default="chrome",
        choices=["chrome", "firefox"],
        help="Browser to run E2E tests (default: chrome)",
    )
    parser.addoption(
        "--base-url",
        default=os.environ.get("E2E_BASE_URL", "http://localhost:8080"),
        help="Base URL of the running application (default: http://localhost:8080)",
    )
    parser.addoption(
        "--generate-protocol",
        action="store_true",
        default=False,
        help="Generate a Markdown test protocol under test-reports/e2e/<ts>/",
    )
    parser.addoption(
        "--resume",
        default=None,
        help="Resume an interrupted run: pass its test-reports/e2e/<ts>/ dir.",
    )
    parser.addoption(
        "--device",
        default=os.environ.get("E2E_DEVICE", "desktop"),
        choices=["desktop", "mobile", "tablet"],
        help="Device profile for viewport/user-agent emulation (default: desktop)",
    )


# ── Load the protocol plugin (works in-repo and in a flat container layout) ──
_pp_path = Path(__file__).parent / "protocol_plugin.py"
_pp_spec = _ilu.spec_from_file_location("protocol_plugin", _pp_path)
_pp_mod = _ilu.module_from_spec(_pp_spec)  # type: ignore[arg-type]
_sys.modules["protocol_plugin"] = _pp_mod
_pp_spec.loader.exec_module(_pp_mod)  # type: ignore[union-attr]
ProtocolGenerator = _pp_mod.ProtocolGenerator
ScreenshotEntry = _pp_mod.ScreenshotEntry
TestResult = _pp_mod.TestResult

_protocol_generator: ProtocolGenerator | None = None  # type: ignore[assignment]
_protocol_output_dir: Path | None = None


def pytest_configure(config: pytest.Config) -> None:
    """Register the standard markers (spec: test markers and suites)."""
    config.addinivalue_line(
        "markers", "smoke: core smoke suite — page loads, no crash"
    )
    config.addinivalue_line(
        "markers", "core_crud: core create/read/update/delete behaviour"
    )
    config.addinivalue_line(
        "markers", "requires_auth: needs an authenticated session"
    )
    config.addinivalue_line(
        "markers", "requires_desktop: needs the desktop viewport"
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Auto-skip tests based on device profile and resume state."""
    if config.getoption("--device") != "desktop":
        device = config.getoption("--device")
        skip_mobile = pytest.mark.skip(
            reason=f"requires desktop viewport (running on {device})"
        )
        for item in items:
            if "requires_desktop" in item.keywords:
                item.add_marker(skip_mobile)

    resume_dir = config.getoption("--resume", default=None)
    if resume_dir:
        checkpoint = Path(resume_dir) / "checkpoint.jsonl"
        if checkpoint.exists():
            passed = {r.nodeid for r in _load_checkpoint(checkpoint) if r.outcome == "passed"}
            if passed:
                skip_resume = pytest.mark.skip(reason="already passed (--resume)")
                for item in items:
                    if item.nodeid in passed:
                        item.add_marker(skip_resume)


# ── Device profiles for responsive testing ────────────────────────────────
DEVICE_PROFILES: dict[str, dict] = {
    "desktop": {
        "width": 1920, "height": 1080, "deviceScaleFactor": 1,
        "mobile": False, "userAgent": "",
    },
    "mobile": {
        "width": 393, "height": 852, "deviceScaleFactor": 3, "mobile": True,
        "userAgent": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
            "Mobile/15E148 Safari/604.1"
        ),
    },
    "tablet": {
        "width": 820, "height": 1180, "deviceScaleFactor": 2, "mobile": True,
        "userAgent": (
            "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
            "Mobile/15E148 Safari/604.1"
        ),
    },
}


@pytest.fixture(scope="session")
def device_profile(request: pytest.FixtureRequest) -> dict:
    """Return the active device profile dict (viewport, UA, scale, touch)."""
    name = request.config.getoption("--device")
    return {**DEVICE_PROFILES[name], "name": name}


@pytest.fixture(scope="session")
def base_url(request: pytest.FixtureRequest) -> str:
    """Return the base URL for the application under test.

    ``E2E_BASE_URL`` env var takes precedence over the ``--base-url`` option.
    """
    return os.environ.get("E2E_BASE_URL") or request.config.getoption("--base-url")


# ── Seed data (ADAPT) ─────────────────────────────────────────────────────
@pytest.fixture(scope="session", autouse=True)
def seed_data(base_url: str) -> dict:
    """Idempotent, session-scoped test data seeding — REPLACE THIS BODY.

    The spec requires seeds to be idempotent (check-before-create) and to use
    distinguishable, realistic values. Seed via your app's API or a fixture
    endpoint here and return a dict the browser fixture / tests can read. The
    placeholder returns an empty dict so the suite runs against pre-existing
    data; per-test data should use a unique suffix (see the example test).
    """
    return {}


# ── Browser (deterministic, per-test session) ─────────────────────────────
@pytest.fixture(scope="function")
def browser(
    request: pytest.FixtureRequest, seed_data: dict, device_profile: dict
) -> webdriver.Remote:
    """Create a fresh headless browser per test for deterministic isolation.

    Function scope gives every test a clean cookie/localStorage starting point.
    When ``SELENIUM_REMOTE_URL`` is set, connects to a Selenium Grid; otherwise
    starts a local browser. ``--device`` controls viewport and CDP emulation.
    """
    browser_name = request.config.getoption("--browser")
    remote_url = os.environ.get("SELENIUM_REMOTE_URL")
    dev = device_profile
    win_size = f"{dev['width']},{dev['height']}"

    if remote_url:
        if browser_name == "firefox":
            options = webdriver.FirefoxOptions()
            options.add_argument("--headless")
            options.add_argument(f"--width={dev['width']}")
            options.add_argument(f"--height={dev['height']}")
        else:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument(f"--window-size={win_size}")
        driver = webdriver.Remote(command_executor=remote_url, options=options)
        from selenium.webdriver.remote.file_detector import LocalFileDetector

        driver.file_detector = LocalFileDetector()
    elif browser_name == "firefox":
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        options.add_argument(f"--width={dev['width']}")
        options.add_argument(f"--height={dev['height']}")
        gecko = shutil.which("geckodriver")
        if gecko:
            service = FirefoxService(gecko)
        elif GeckoDriverManager is not None:
            service = FirefoxService(GeckoDriverManager().install())
        else:
            service = FirefoxService()
        driver = webdriver.Firefox(service=service, options=options)
    else:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--remote-debugging-port=0")
        options.add_argument(f"--window-size={win_size}")
        chromium = shutil.which("chromium-browser") or shutil.which("chromium")
        if chromium and not shutil.which("google-chrome"):
            options.binary_location = chromium
        chromedriver = shutil.which("chromedriver") or shutil.which(
            "chromium.chromedriver"
        )
        if chromedriver:
            service = ChromeService(chromedriver)
        elif ChromeDriverManager is not None:
            service = ChromeService(ChromeDriverManager().install())
        else:
            service = ChromeService()
        driver = webdriver.Chrome(service=service, options=options)

    # Device emulation via CDP (Chrome only; Firefox falls back to window size).
    if dev["name"] != "desktop":
        try:
            driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
                "width": dev["width"], "height": dev["height"],
                "deviceScaleFactor": dev["deviceScaleFactor"], "mobile": dev["mobile"],
            })
            if dev["userAgent"]:
                driver.execute_cdp_cmd(
                    "Emulation.setUserAgentOverride", {"userAgent": dev["userAgent"]}
                )
            driver.execute_cdp_cmd(
                "Emulation.setTouchEmulationEnabled", {"enabled": True}
            )
        except Exception:
            pass

    os.environ["E2E_BROWSER"] = browser_name
    os.environ["E2E_DEVICE"] = dev["name"]
    driver.implicitly_wait(10)

    # ADAPT: if your app needs a logged-in session for most tests, navigate to
    # the origin and call your login helper here. Tests marked requires_auth
    # that drive the login flow themselves should manage their own state.
    #   driver.get(base_url := os.environ.get("E2E_BASE_URL")
    #              or request.config.getoption("--base-url"))
    #   if "requires_auth" not in request.node.keywords:
    #       _login(driver, base_url)

    yield driver
    driver.quit()


@pytest.fixture(scope="session")
def screenshot_dir(request: pytest.FixtureRequest) -> Path:
    """Return the screenshot directory, shared with the protocol plugin.

    Under ``--generate-protocol`` screenshots live next to the report in the
    same timestamped folder; otherwise a standalone directory is created.
    """
    protocol_dir: Path | None = getattr(request.config, "_protocol_output_dir", None)
    if protocol_dir is not None:
        path = protocol_dir / "screenshots"
    else:
        timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
        path = Path("test-reports") / "e2e" / timestamp / "screenshots"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _cdp_full_page_screenshot(driver: webdriver.Remote, filepath: Path) -> None:
    """Capture a full-page screenshot via CDP, falling back to viewport-only."""
    import base64

    try:
        result = driver.execute_cdp_cmd(
            "Page.captureScreenshot", {"captureBeyondViewport": True}
        )
        filepath.write_bytes(base64.b64decode(result["data"]))
    except Exception:
        driver.save_screenshot(str(filepath))


@pytest.fixture(autouse=True)
def screenshot(
    request: pytest.FixtureRequest, browser: webdriver.Remote, screenshot_dir: Path
):
    """Provide a callable ``screenshot(name, description)`` for checkpoints.

    Autouse so a failure screenshot is always captured. Usage::

        def test_loads(self, page, screenshot):
            page.open()
            screenshot("TC-001-001_page-loaded", "Page after initial load")
    """
    def _capture(name: str, description: str = "") -> Path:
        filename = f"{name}.png"
        filepath = screenshot_dir / filename
        _cdp_full_page_screenshot(browser, filepath)
        shots = getattr(request.node, "_protocol_screenshots", [])
        shots.append(ScreenshotEntry(
            filename=filename,
            description=description or name.replace("_", " "),
            test_nodeid=request.node.nodeid,
        ))
        request.node._protocol_screenshots = shots  # type: ignore[attr-defined]
        return filepath

    yield _capture

    report = getattr(request.node, "_report", None)
    if report and report.failed:
        test_name = request.node.name.replace("[", "_").replace("]", "_")
        _capture(f"FAILURE_{test_name}", f"Automatic screenshot after failure in {test_name}")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item) -> None:
    """Attach the report to the node (for the failure screenshot) and record it."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call":
        item._report = report  # type: ignore[attr-defined]
        if _protocol_generator is not None:
            outcome_str = "passed" if not report.failed else "failed"
            if report.skipped:
                outcome_str = "skipped"
            message = str(report.longrepr) if report.failed else ""
            docstring = ""
            if item.obj and item.obj.__doc__:
                docstring = item.obj.__doc__.strip().split("\n")[0]
            screenshots = getattr(item, "_protocol_screenshots", [])
            result = TestResult(
                nodeid=item.nodeid, outcome=outcome_str, duration=report.duration,
                message=message, docstring=docstring, screenshots=screenshots,
            )
            _protocol_generator.add_result(result)
            _write_checkpoint(result)


def _write_checkpoint(result: TestResult) -> None:
    """Append one result to the JSONL checkpoint so partial runs survive interrupts."""
    import json

    if _protocol_output_dir is None:
        return
    checkpoint = _protocol_output_dir / "checkpoint.jsonl"
    checkpoint.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "nodeid": result.nodeid,
        "outcome": result.outcome,
        "duration": result.duration,
        "message": result.message[:500] if result.message else "",
        "docstring": result.docstring,
        "screenshots": [
            {"filename": s.filename, "description": s.description}
            for s in result.screenshots
        ],
    }
    with checkpoint.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _load_checkpoint(checkpoint_path: Path) -> list[TestResult]:
    """Load results from a JSONL checkpoint file."""
    import json

    results: list[TestResult] = []
    if not checkpoint_path.exists():
        return results
    for line in checkpoint_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entry = json.loads(line)
        results.append(TestResult(
            nodeid=entry["nodeid"], outcome=entry["outcome"],
            duration=entry.get("duration", 0.0), message=entry.get("message", ""),
            docstring=entry.get("docstring", ""),
            screenshots=[
                ScreenshotEntry(
                    filename=s["filename"], description=s["description"],
                    test_nodeid=entry["nodeid"],
                )
                for s in entry.get("screenshots", [])
            ],
        ))
    return results


def _generate_protocol_safe() -> None:
    """Generate the protocol from whatever results exist — safe on interrupt."""
    if _protocol_generator is not None and _protocol_output_dir is not None:
        try:
            path = _protocol_generator.generate(_protocol_output_dir)
            print(f"\nTest protocol written: {path}")
        except Exception as exc:
            print(f"\nWarning: protocol generation failed: {exc}")


def pytest_sessionstart(session: pytest.Session) -> None:
    """Initialise the protocol generator when --generate-protocol is active."""
    import atexit

    global _protocol_generator, _protocol_output_dir
    if not session.config.getoption("--generate-protocol", default=False):
        return

    resume_dir = session.config.getoption("--resume", default=None)
    if resume_dir:
        resume_path = Path(resume_dir)
        _protocol_output_dir = resume_path
        _protocol_generator = ProtocolGenerator()
        checkpoint = resume_path / "checkpoint.jsonl"
        if checkpoint.exists():
            loaded = _load_checkpoint(checkpoint)
            _protocol_generator.results = loaded
            _protocol_generator.start_time = datetime.now(tz=timezone.utc)
            print(f"\nResumed with {len(loaded)} results from {checkpoint}")
    else:
        timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
        _protocol_output_dir = Path("test-reports") / "e2e" / timestamp
        _protocol_generator = ProtocolGenerator()
        _protocol_generator.start_time = datetime.now(tz=timezone.utc)

    session.config._protocol_output_dir = _protocol_output_dir  # type: ignore[attr-defined]
    atexit.register(_generate_protocol_safe)  # safety net on unclean exit


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Write the test protocol at the end of the session."""
    _generate_protocol_safe()
