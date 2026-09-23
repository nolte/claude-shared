"""Tests for the five worked-example probes shipped with capability-reach-audit.

The examples under ``plugins/nolte-engineering/skills/capability-reach-audit/examples/``
encode spec/project/capability-reach-audit/ §"Worked acceptance: The five defects",
one probe per table row. Requirement ids refer to
project/requirements/capability-reach-executor.md; R19 is the one under test.

What is pinned here:

* every example is a valid probe, ships without approval, and is refused by the
  runner (``not probed``, reason ``not approved``) until an operator approves it;
* each example's typed expectation classifies the spec table's defect
  observation the way the table implies, and the declared value as reached;
* the T0 (scan lane) and T1 (ranking service) examples run end to end through
  ``main`` against a real git repository in ``tmp_path``, T0 against a ``gh``
  double serving a platform run history, T1 against a loopback server; the three T2 examples
  are proven by a dogfooding run in the target repository, not here (R19);
* each example fails the closed schema once a verdict line is appended.

The doubles are the same honest ones ``tests/test_reach_audit.py`` uses: real git
repositories (git is never mocked) and that module's ``task`` shim, which reads
the target's ``Taskfile.yml`` and runs the named target's commands. Beside it, a
``gh`` shim of the same shape answers ``gh run list`` with gh's argv, exit codes
and JSON, from a run-history file instead of the network.
"""
from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import sys
import textwrap
import time
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

from tests.test_reach_audit import TASK_SHIM, Target, row_of

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "plugins" / "nolte-engineering" / "skills" / "capability-reach-audit" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import reach_audit as ra  # noqa: E402

EXAMPLES = SCRIPTS.parent / "examples"
PY = sys.executable
PLACEHOLDER = "0" * 40
APPROVAL = 'approval:\n  approved_at: "2026-09-23T10:00:00Z"\n  approved_by: reach-test\n'

# The spec table's measurement per row, as the raw observation the defect
# produced and the class the runner must derive from it.
DEFECT = {
    "scan-lane-runs.yml": (0, ra.NOT_REACHED, "0/300 runs executed"),
    "ranking-endpoint-answers.yml": (0, ra.NOT_REACHED, "0/1 endpoints answer"),
    "data-export-populated.yml": (set(), ra.NOT_REACHED, "0/23 collections and edges populated"),
    "erasure-finalisation.yml": (0, ra.NOT_REACHED, "0/52 checks passed (26 erased, 26 redacted)"),
    "personal-data-inventories.yml": (
        {"export-manifest"}, ra.PARTIAL, "1/2 declared inventories matching the executing one",
    ),
}
TIERS = {
    "scan-lane-runs.yml": "T0",
    "ranking-endpoint-answers.yml": "T1",
    "data-export-populated.yml": "T2",
    "erasure-finalisation.yml": "T2",
    "personal-data-inventories.yml": "T2",
}
NAMES = sorted(DEFECT)


@pytest.fixture(autouse=True)
def _isolated_git(tmp_path_factory, monkeypatch):
    """Git identity for test commits, without touching the operator's config."""
    cfg = tmp_path_factory.mktemp("gitcfg") / "gitconfig"
    cfg.write_text(
        "[user]\n\tname = Reach Test\n\temail = reach@example.invalid\n"
        "[commit]\n\tgpgsign = false\n[init]\n\tdefaultBranch = main\n"
    )
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(cfg))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")


def example_text(name: str) -> str:
    return (EXAMPLES / name).read_text(encoding="utf-8")


def example(name: str) -> dict:
    return yaml.safe_load(example_text(name))


def validate(probe: object) -> list[str]:
    return [e.message for e in Draft202012Validator(ra.PROBE_SCHEMA).iter_errors(probe)]


def derive(target: Target, name: str, *, approve: bool = False) -> str:
    """Derive the example in ``target`` the way a consumer would.

    Commits a stand-in for the declaration at the example's anchor path, then
    commits the example verbatim except for the placeholder ``derived_from``
    (replaced with the derivation commit) and, when asked, an appended approval.
    Returns the probe id.
    """
    data = example(name)
    decl = data["declaration"]["path"]
    if not (target.path / decl).exists():
        target.write(decl, f"# declaration stand-in for {data['id']}\n")
        target.commit(f"declare {data['id']}")
    sha = target.git("rev-parse", "HEAD")
    text, n = re.subn(rf'^derived_from: "{PLACEHOLDER}"$', f'derived_from: "{sha}"', example_text(name), flags=re.M)
    assert n == 1, f"{name}: placeholder derived_from line not found"
    if approve:
        text += APPROVAL
    target.write(f"project/reach-probes/{name}", text)
    target.commit(f"probe {data['id']}")
    return data["id"]


def run_main(target: Target, *extra: str) -> tuple[int, str]:
    code = ra.main(["--repo", str(target.path), *extra])
    return code, target.report()


# --------------------------------------------------------------------------- #
# The set as shipped (R19)
# --------------------------------------------------------------------------- #
def test_the_example_directory_holds_exactly_the_five_rows():
    assert sorted(p.name for p in EXAMPLES.iterdir() if p.name != ra.MANIFEST_NAME) == NAMES


@pytest.mark.parametrize("name", NAMES)
def test_example_matches_its_spec_row_and_ships_unapproved(name):
    data = example(name)
    assert validate(data) == []
    assert data["tier"] == TIERS[name]
    assert "approval" not in data, "examples ship unapproved; a consumer approves consciously"
    assert data["derived_from"] == PLACEHOLDER
    text = example_text(name)
    for marker in ("ILLUSTRATIVE TARGET", "PLACEHOLDER derived_from", "UNAPPROVED ON PURPOSE"):
        assert marker in text, f"{name}: leading comment lacks {marker!r}"
    if data["tier"] == "T0":
        assert "environment" not in data
    else:
        assert data["environment"] and data["teardown"], "a started container needs a teardown"


@pytest.mark.parametrize("name", NAMES)
def test_example_loads_validates_and_is_refused_until_approved(tmp_path, name):
    """The unapproved-by-default rule, on the real examples, through main."""
    target = Target(tmp_path / "target")
    verbatim = Target(tmp_path / "verbatim")
    verbatim.write(f"project/reach-probes/{name}", example_text(name))
    verbatim.commit("verbatim example")
    probes = ra.load_probes(verbatim.path, yaml, Draft202012Validator)
    assert [(p.pid, p.errors) for p in probes] == [(example(name)["id"], [])]

    pid = derive(target, name)
    code, report = run_main(target, "--include-t2")
    row = row_of(report, pid)
    assert code == ra.EXIT_OK
    assert row[1] == ra.NOT_PROBED
    assert row[5] == "not executed"
    assert row[9] == ra.REASON_NOT_APPROVED
    assert "**Not probed: 1 of 1 probes.**" in report


# --------------------------------------------------------------------------- #
# Classification as the spec table implies
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("name", NAMES)
def test_example_expectation_classifies_as_the_spec_table_implies(name):
    probe = yaml.safe_load(example_text(name) + APPROVAL)
    assert validate(probe) == []
    expected = probe["expected"]
    zero: int | set[str] = 0 if expected["kind"] == "count" else set()
    declared: int | set[str] = expected["value"] if expected["kind"] == "count" else set(expected["values"])

    assert ra.classify(expected, zero).cls == ra.NOT_REACHED
    assert ra.classify(expected, declared).cls == ra.REACHED
    observed, cls, reach = DEFECT[name]
    outcome = ra.classify(expected, observed)
    assert (outcome.cls, outcome.reach) == (cls, reach)


def test_export_example_keeps_fifteen_collections_and_eight_edges_apart():
    values = example("data-export-populated.yml")["expected"]["values"]
    assert sum(v.startswith("collection/") for v in values) == 15
    assert sum(v.startswith("edge/") for v in values) == 8
    outcome = ra.classify(example("data-export-populated.yml")["expected"], {v for v in values if v.startswith("edge/")})
    assert (outcome.cls, outcome.reach) == (ra.PARTIAL, "8/23 collections and edges populated")
    assert "collection/auth_providers" in outcome.reason


# --------------------------------------------------------------------------- #
# Negative: the examples exercise the closed schema
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("name", NAMES)
def test_example_with_a_verdict_line_fails_the_schema(name):
    mutated = yaml.safe_load(example_text(name) + "status: passed\n")
    errors = validate(mutated)
    assert any("Additional properties" in m and "'status'" in m for m in errors), errors


# --------------------------------------------------------------------------- #
# End to end: T0 scan lane
# --------------------------------------------------------------------------- #
GH_SHIM = textwrap.dedent(
    f"""\
    #!{PY}
    # Test double for the GitHub CLI's `gh run list`: same argv, same exit codes,
    # same JSON on stdout, no network. Runs come from the JSON file GH_RUNS
    # (newest first, each carrying workflow, event, branch, conclusion); the
    # filters and --limit apply the way gh applies them, and an unknown workflow
    # or a missing --json fails the way gh does.
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
    if workflow is not None and workflow not in {{r["workflow"] for r in runs}}:
        sys.stderr.write(f"could not find any workflows named {{workflow}}\\n")
        sys.exit(1)
    for key, field in (("workflow", "workflow"), ("event", "event"), ("branch", "branch")):
        if key in opts:
            runs = [r for r in runs if r[field] == opts[key]]
    runs = runs[: int(opts.get("limit", "20"))]
    if "json" not in opts:
        sys.stderr.write("this shim only emulates --json output\\n")
        sys.exit(1)
    fields = opts["json"].split(",")
    print(json.dumps([{{f: r.get(f) for f in fields}} for r in runs]))
    """
)
SCAN_DECL = ".github/workflows/security-zap-postmerge.yml"
SCAN_WORKFLOW = "security-zap-postmerge.yml"


def _runs(executed: int) -> list[dict]:
    """A run history, newest first, whose last 300 push runs of the lane on
    develop hold ``executed`` executed ones; the rest of those 300 never executed
    the job. Every other run executed: 50 older ones of the lane, and 40 each of
    another trigger, another branch and another workflow, interleaved with the
    newest. A probe that drops a filter or the limit over-counts and fails."""
    not_run = [None, "skipped", "cancelled", "startup_failure"]
    foreign = [
        {"workflow": SCAN_WORKFLOW, "event": "workflow_dispatch", "branch": "develop", "conclusion": "success"},
        {"workflow": SCAN_WORKFLOW, "event": "push", "branch": "main", "conclusion": "success"},
        {"workflow": "backend.yml", "event": "push", "branch": "develop", "conclusion": "success"},
    ]
    runs = []
    for i in range(300):
        if i < 120:
            runs.append(foreign[i % 3])
        conclusion = ("success", "failure")[i % 2] if i < executed else not_run[i % len(not_run)]
        runs.append({"workflow": SCAN_WORKFLOW, "event": "push", "branch": "develop", "conclusion": conclusion})
    runs += [{"workflow": SCAN_WORKFLOW, "event": "push", "branch": "develop", "conclusion": "success"}] * 50
    return runs


@pytest.fixture
def gh_shim(tmp_path, monkeypatch) -> Path:
    """Put the `gh` double first on PATH; return the run-history file it serves."""
    bin_dir = tmp_path / "ghbin"
    bin_dir.mkdir()
    shim = bin_dir / "gh"
    shim.write_text(GH_SHIM)
    shim.chmod(0o755)
    history = tmp_path / "runs.json"
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("GH_RUNS", str(history))
    return history


def test_end_to_end_T0_scan_lane_classifies_the_platform_run_history(tmp_path, gh_shim):
    target = Target(tmp_path / "target")
    target.write(SCAN_DECL, "on:\n  push:\n    branches: [develop]\n")
    target.commit("declare the lane")
    pid = derive(target, "scan-lane-runs.yml", approve=True)

    started = time.monotonic()
    seen = []
    for executed, cls in ((0, ra.NOT_REACHED), (120, ra.PARTIAL), (300, ra.REACHED)):
        gh_shim.write_text(json.dumps(_runs(executed)))
        code, report = run_main(target)
        row = row_of(report, pid)
        assert code == ra.EXIT_OK
        assert row[1:3] == [cls, f"{executed}/300 runs executed"]
        assert row[7] == ra.STATE_CLEAN
        seen.append(row[1])
    elapsed = time.monotonic() - started
    assert seen == [ra.NOT_REACHED, ra.PARTIAL, ra.REACHED]
    assert elapsed < 30
    print(json.dumps({"t0_end_to_end_seconds_three_runs": round(elapsed, 2)}))


def test_T0_scan_lane_failing_gh_is_not_probed_never_zero_runs(tmp_path, gh_shim):
    """An unreachable platform says nothing about reach: not probed, with gh's error."""
    target = Target(tmp_path / "target")
    target.write(SCAN_DECL, "on:\n  push:\n    branches: [develop]\n")
    target.commit("declare the lane")
    pid = derive(target, "scan-lane-runs.yml", approve=True)
    gh_shim.write_text(json.dumps([{"workflow": "backend.yml", "event": "push", "branch": "develop",
                                    "conclusion": "success"}]))
    _, report = run_main(target)
    row = row_of(report, pid)
    assert row[1] == ra.NOT_PROBED
    assert "could not find any workflows named security-zap-postmerge.yml" in row[9]


# --------------------------------------------------------------------------- #
# End to end: T1 ranking service
# --------------------------------------------------------------------------- #
RANKING_SERVER = textwrap.dedent(
    """\
    # Loopback stand-in for the ranking container. `up` starts a detached server
    # and returns once it listens, writing its base URL to .reach/ranking.url as
    # the example's leading comment requires; `down` stops it. RANKING_MODE
    # `honest` ranks documents by word overlap with the query; `constant` returns
    # one fixed ordering whatever is asked, the stub a probe must not pass.
    import http.server, json, os, re, signal, subprocess, sys, time
    state = ".reach"
    url_file, pid_file = os.path.join(state, "ranking.url"), os.path.join(state, "ranking.pid")
    cmd = sys.argv[1]
    if cmd == "up":
        os.makedirs(state, exist_ok=True)
        subprocess.Popen([sys.executable, __file__, "serve"], start_new_session=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(200):
            if os.path.exists(url_file):
                sys.exit(0)
            time.sleep(0.02)
        sys.exit("ranking server did not come up")
    if cmd == "serve":
        words = lambda s: set(re.findall(r"[a-z]+", s.lower()))
        class H(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                req = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                docs = req["documents"]
                if os.environ.get("RANKING_MODE") == "constant":
                    order = list(range(len(docs)))
                else:
                    q = words(req["query"])
                    order = sorted(range(len(docs)), key=lambda i: (-len(q & words(docs[i])), i))
                body = json.dumps({"order": order}).encode()
                self.send_response(200); self.end_headers(); self.wfile.write(body)
            def log_message(self, *a):
                pass
        srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
        open(pid_file, "w").write(str(os.getpid()))
        open(url_file + ".tmp", "w").write(f"http://127.0.0.1:{srv.server_address[1]}")
        os.replace(url_file + ".tmp", url_file)
        srv.serve_forever(poll_interval=0.05)
    if cmd == "down":
        os.kill(int(open(pid_file).read()), signal.SIGTERM)
        os.remove(url_file)
        os.remove(pid_file)
    """
)


@pytest.fixture
def ranking_target(tmp_path, monkeypatch):
    """A target with the `task` shim on PATH and the two ranking targets declared."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    shim = bin_dir / "task"
    shim.write_text(TASK_SHIM)
    shim.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    server = tmp_path / "ranking_server.py"
    server.write_text(RANKING_SERVER)
    target = Target(tmp_path / "target")
    tasks = {
        "reach:ranking:up": {"cmds": [f"{PY} {server} up"]},
        "reach:ranking:down": {"cmds": [f"{PY} {server} down"]},
    }
    target.write("Taskfile.yml", yaml.safe_dump({"version": "3", "tasks": tasks}))
    target.write(".gitignore", ".reach/\n.audits/\n")
    target.commit("taskfile")
    yield target
    pid_file = target.path / ".reach" / "ranking.pid"
    if pid_file.exists():
        try:
            os.kill(int(pid_file.read_text()), signal.SIGKILL)
        except ProcessLookupError:
            pass


@pytest.mark.parametrize(
    ("mode", "cls", "reach"),
    [("honest", ra.REACHED, "1/1 endpoints answer"), ("constant", ra.NOT_REACHED, "0/1 endpoints answer")],
)
def test_end_to_end_T1_ranking_service(ranking_target, monkeypatch, mode, cls, reach):
    """A real ranker reaches; a constant answer fails, so a stub cannot pass."""
    monkeypatch.setenv("RANKING_MODE", mode)
    pid = derive(ranking_target, "ranking-endpoint-answers.yml", approve=True)
    started = time.monotonic()
    code, report = run_main(ranking_target)
    elapsed = time.monotonic() - started
    row = row_of(report, pid)
    assert code == ra.EXIT_OK
    assert row[1:3] == [cls, reach]
    assert row[5] != "not executed"
    assert not (ranking_target.path / ".reach" / "ranking.url").exists(), "teardown must have stopped the server"
    assert elapsed < 20
    print(json.dumps({f"t1_end_to_end_seconds_{mode}": round(elapsed, 2)}))
