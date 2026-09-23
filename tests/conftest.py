"""Shared pytest fixtures for the eval harness.

Behavioural tests (marked ``behavioural``) drive a real skill/agent via the Anthropic
API and are skipped unless ``RUN_EVALS=1``. When they do run, each test appends its
`ScenarioResult` via the `record_scorecard` fixture; the session writes a single
`scorecard.json` at teardown, which `evals.harness.compare` then diffs across runs.
"""
from __future__ import annotations

import os
import shutil
import signal
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

from evals.harness import runner
from evals.harness.scorecard import Scorecard

REPO_ROOT = Path(__file__).resolve().parents[1]  # the plugin dir (contains .claude-plugin)

# Shared with tests/test_reach_audit.py and tests/test_reach_audit_examples.py: both
# import reach_audit against the shipped script, so the path setup happens once here.
SCRIPTS = REPO_ROOT / "plugins" / "nolte-engineering" / "skills" / "capability-reach-audit" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import reach_audit as ra  # noqa: E402


def pytest_collection_modifyitems(config, items):
    if os.environ.get("RUN_EVALS") == "1":
        return
    skip = pytest.mark.skip(reason="behavioural eval; set RUN_EVALS=1 to run (incurs API cost)")
    for item in items:
        if "behavioural" in item.keywords:
            item.add_marker(skip)


@pytest.fixture
def plugin_dir() -> str:
    return str(REPO_ROOT)


@pytest.fixture
def fixture_repo(tmp_path):
    """Copy a scenario's ``fixture/`` mini-repo into a fresh tmp dir; return its path.

    Copying (never the live tree) is what lets a file-mutating skill scribble freely and
    lets the test assert on the *resulting* files without touching the real repo.
    """

    def _make(scenario_dir) -> Path:
        src = Path(scenario_dir) / "fixture"
        dst = tmp_path / "repo"
        shutil.copytree(src, dst)
        return dst

    return _make


@pytest.fixture(scope="session")
def _scorecard_collector():
    results: list = []
    yield results
    if not results:
        return
    out = Path(
        os.environ.get("EVAL_SCORECARD", str(REPO_ROOT / "evals" / "out" / "scorecard.json"))
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    Scorecard.build(results, model=runner.eval_model()).write(out)


@pytest.fixture
def record_scorecard(_scorecard_collector):
    """Return a callable that records a `ScenarioResult` into the session scorecard."""
    return _scorecard_collector.append


@pytest.fixture
def n_samples() -> int:
    return int(os.environ.get("EVAL_SAMPLES", "3"))


@pytest.fixture
def threshold() -> float:
    return float(os.environ.get("EVAL_THRESHOLD", "0.6"))


# --------------------------------------------------------------------------- #
# Shared with tests/test_reach_audit.py and tests/test_reach_audit_examples.py
# --------------------------------------------------------------------------- #
# Consolidated here (SCR-007) so neither module cross-imports from the other.
REACH_PY = sys.executable


@pytest.fixture(autouse=True)
def _isolated_git(tmp_path_factory, monkeypatch, request):
    """Git identity for test commits, without touching the operator's config.

    Only active for the reach-audit test modules, which are the only ones that
    commit into throwaway git repositories; other tests only read git state.
    """
    if request.module.__name__ not in ("tests.test_reach_audit", "tests.test_reach_audit_examples"):
        return
    cfg = tmp_path_factory.mktemp("gitcfg") / "gitconfig"
    cfg.write_text(
        "[user]\n\tname = Reach Test\n\temail = reach@example.invalid\n"
        "[commit]\n\tgpgsign = false\n[init]\n\tdefaultBranch = main\n"
    )
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(cfg))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")


class Target:
    """A real git working copy standing in for an audited repository."""

    def __init__(self, path: Path) -> None:
        self.path = path
        path.mkdir(parents=True, exist_ok=True)
        self.git("init", "-q")

    def git(self, *args: str) -> str:
        return subprocess.run(
            ["git", "-C", str(self.path), *args], check=True, capture_output=True, text=True
        ).stdout.strip()

    def write(self, rel: str, text: str) -> None:
        f = self.path / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text)

    def commit(self, msg: str = "change") -> str:
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", msg)
        return self.git("rev-parse", "HEAD")

    def write_probe(self, data: dict, name: str | None = None) -> str:
        rel = f"project/reach-probes/{name or data['id']}.yml"
        self.write(rel, yaml.safe_dump(data, sort_keys=False))
        return rel

    def report(self) -> str:
        files = sorted((self.path / ".audits" / "capability-reach").glob("*.md"))
        assert len(files) == 1, files
        return files[0].read_text()


def row_of(report: str, pid: str) -> list[str]:
    for line in report.splitlines():
        if line.startswith(f"| {pid} |"):
            return [c.strip() for c in line.strip("|").split(" | ")]
    raise AssertionError(f"no row for {pid} in report:\n{report}")


def validate(probe: object) -> list[str]:
    return [e.message for e in Draft202012Validator(ra.PROBE_SCHEMA).iter_errors(probe)]


def install_shim(bin_dir: Path, name: str, script: str) -> Path:
    """Write an executable test-double script named ``name`` into ``bin_dir``."""
    bin_dir.mkdir(exist_ok=True)
    shim = bin_dir / name
    shim.write_text(script)
    shim.chmod(0o755)
    return shim


# Test double for go-task 3.52.0: `task [--silent] <name>` reads Taskfile.yml in the
# working directory and fails the way the real binary does, both measured directly
# against it -- no Taskfile in the directory tree (stderr, exit 100) and an unknown
# task name (stderr, exit 200).
TASK_SHIM = textwrap.dedent(
    f"""\
    #!{REACH_PY}
    import subprocess, sys, yaml
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    try:
        tasks = (yaml.safe_load(open("Taskfile.yml")) or {{}}).get("tasks", {{}})
    except FileNotFoundError:
        sys.stderr.write(
            'task: No Taskfile found at "" (or any of the parent directories until '
            "ownership changed). Run `task --init` to create a new Taskfile.\\n"
        )
        sys.exit(100)
    for name in args:
        if name not in tasks:
            sys.stderr.write(f'task: Task "{{name}}" does not exist\\n')
            sys.exit(200)
        for cmd in tasks[name].get("cmds", []):
            rc = subprocess.call(cmd, shell=True)
            if rc:
                sys.stderr.write(f'task: Failed to run task "{{name}}": exit status {{rc}}\\n')
                sys.exit(201)
    """
)


# Loopback stand-in for a T1 dependency: `up` starts a detached HTTP server and
# returns once it listens; `down` stops it. State lives in REACH_STATE.
SERVER = textwrap.dedent(
    """\
    import http.server, os, signal, subprocess, sys, time
    state = os.environ["REACH_STATE"]
    port_file, pid_file = os.path.join(state, "port"), os.path.join(state, "pid")
    cmd = sys.argv[1]
    if cmd == "up":
        subprocess.Popen([sys.executable, __file__, "serve"], start_new_session=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(200):
            if os.path.exists(port_file):
                sys.exit(0)
            time.sleep(0.02)
        sys.exit("server did not come up")
    if cmd == "serve":
        class H(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                body = open(os.path.join(state, "items")).read().encode()
                self.send_response(200); self.end_headers(); self.wfile.write(body)
            def log_message(self, *a):
                pass
        srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
        open(pid_file, "w").write(str(os.getpid()))
        open(port_file + ".tmp", "w").write(str(srv.server_address[1]))
        os.replace(port_file + ".tmp", port_file)
        srv.serve_forever(poll_interval=0.05)
    if cmd == "down":
        os.kill(int(open(pid_file).read()), signal.SIGTERM)
        os.remove(port_file)
    """
)


@pytest.fixture
def task_shim(tmp_path, monkeypatch):
    """Put the `task` double first on PATH; yield the state dir; stop any server."""
    bin_dir = tmp_path / "bin"
    install_shim(bin_dir, "task", TASK_SHIM)
    state = tmp_path / "state"
    state.mkdir()
    (state / "server.py").write_text(SERVER)
    (state / "items").write_text("alpha\nbeta\n")
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("REACH_STATE", str(state))
    yield state
    pid_file = state / "pid"
    if pid_file.exists():
        try:
            os.kill(int(pid_file.read_text()), signal.SIGKILL)
        except ProcessLookupError:
            pass


# Test double for the GitHub CLI's `gh run list`: same argv, same exit codes, same
# JSON on stdout, no network. Runs come from the JSON file GH_RUNS (newest first,
# each carrying workflowName, event, headBranch, conclusion); the filters and
# --limit apply the way gh applies them. An unknown `--workflow` value fails with
# gh's own HTTP 404 wording, and an unknown `--json` field is rejected with gh's
# own message and field list -- both measured against gh 2.96.0 on a live repo.
GH_SHIM = textwrap.dedent(
    f"""\
    #!{REACH_PY}
    import json, os, sys
    args = sys.argv[1:]
    if args[:2] != ["run", "list"]:
        sys.stderr.write(f"unknown command {{' '.join(args[:2])!r}} for gh\\n")
        sys.exit(1)
    opts, i = {{}}, 2
    while i < len(args):
        if not args[i].startswith("--") or i + 1 >= len(args):
            sys.stderr.write(f"unknown argument {{args[i]!r}}\\n")
            sys.exit(1)
        opts[args[i][2:]] = args[i + 1]
        i += 2
    runs = json.load(open(os.environ["GH_RUNS"]))
    workflow = opts.get("workflow")
    if workflow is not None and workflow not in {{r["workflowName"] for r in runs}}:
        sys.stderr.write(
            f"HTTP 404: workflow {{workflow}} not found on the default branch "
            f"(https://api.github.com/repos/OWNER/REPO/actions/workflows/{{workflow}})\\n"
        )
        sys.exit(1)
    for key, field in (("workflow", "workflowName"), ("event", "event"), ("branch", "headBranch")):
        if key in opts:
            runs = [r for r in runs if r[field] == opts[key]]
    runs = runs[: int(opts.get("limit", "20"))]
    if "json" not in opts:
        sys.stderr.write("this shim only emulates --json output\\n")
        sys.exit(1)
    fields = opts["json"].split(",")
    available = ["attempt", "conclusion", "createdAt", "databaseId", "displayTitle", "event",
                 "headBranch", "headSha", "name", "number", "startedAt", "status", "updatedAt",
                 "url", "workflowDatabaseId", "workflowName"]
    unknown = [f for f in fields if f not in available]
    if unknown:
        sys.stderr.write(f'Unknown JSON field: "{{unknown[0]}}"\\n')
        sys.stderr.write("Available fields:\\n")
        for f in available:
            sys.stderr.write(f"  {{f}}\\n")
        sys.exit(1)
    print(json.dumps([{{f: r.get(f) for f in fields}} for r in runs]))
    """
)


@pytest.fixture
def gh_shim(tmp_path, monkeypatch) -> Path:
    """Put the `gh` double first on PATH; return the run-history file it serves."""
    bin_dir = tmp_path / "ghbin"
    install_shim(bin_dir, "gh", GH_SHIM)
    history = tmp_path / "runs.json"
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("GH_RUNS", str(history))
    return history
