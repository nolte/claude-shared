"""Tests for the nolte-linux image-declaration validator and protocol freshness helper.

- ``validate_declaration.py`` (#730): the schema half (Draft 2020-12), the three
  §F conditional rules, stable rule ids, and the fail-closed exit 2 when
  jsonschema/PyYAML can't be imported.
- ``protocol_freshness.py`` (#735): a protocol recorded before a change to any
  path of the image (here an overlay health unit) is stale.
- linux-image-scanner's tool surface (#731): no write or execution tool.
"""
from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "plugins" / "nolte-linux" / "skills" / "linux-image-audit" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import protocol_freshness as pf  # noqa: E402
import validate_declaration as vd  # noqa: E402

VALIDATOR = SCRIPTS / "validate_declaration.py"
SCHEMA_PATH = REPO_ROOT / "schemas" / "image-declaration-v1.0.schema.yaml"
SCHEMA = yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))
FIELD_UPDATED, REFLASH_ONLY = SCHEMA["examples"]
SCANNER = REPO_ROOT / "plugins" / "nolte-linux" / "agents" / "linux-image-scanner.md"


def _run(tmp_path: Path, doc, capsys, *extra: str) -> tuple[int, dict]:
    path = tmp_path / "image-declaration.yaml"
    if isinstance(doc, str):
        path.write_text(doc, encoding="utf-8")
    else:
        path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
    code = vd.main([str(path), *extra])
    return code, json.loads(capsys.readouterr().out)


def _rules(payload: dict) -> set[str]:
    return {v["rule"] for v in payload["violations"]}


# --------------------------------------------------------------------------- #
# Valid examples
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("example", [FIELD_UPDATED, REFLASH_ONLY], ids=["field-updated", "reflash-only"])
def test_schema_examples_are_valid(tmp_path, capsys, example):
    code, payload = _run(tmp_path, example, capsys)
    assert code == 0
    assert payload["result"] == "valid"
    assert payload["violations"] == []
    assert Path(payload["schema"]).resolve() == SCHEMA_PATH.resolve()


def test_explicit_schema_argument(tmp_path, capsys):
    code, payload = _run(tmp_path, FIELD_UPDATED, capsys, "--schema", str(SCHEMA_PATH))
    assert code == 0 and payload["result"] == "valid"


# --------------------------------------------------------------------------- #
# The seven mutation cases of #730
# --------------------------------------------------------------------------- #
def _mutate(base: dict, fn) -> dict:
    doc = copy.deepcopy(base)
    fn(doc)
    return doc


MUTATIONS = {
    "max_boot_attempts=0": (FIELD_UPDATED, lambda d: d["update"].__setitem__("max_boot_attempts", 0),
                            "schema.minimum", "/update/max_boot_attempts"),
    "empty image.name": (FIELD_UPDATED, lambda d: d["image"].__setitem__("name", ""),
                         "schema.minLength", "/image/name"),
    "extra key in $ref HostSwitch": (FIELD_UPDATED, lambda d: d["update"]["source_switch"].__setitem__("extra", "x"),
                                     "schema.additionalProperties", "/update/source_switch"),
    "max_boot_attempts as string": (FIELD_UPDATED, lambda d: d["update"].__setitem__("max_boot_attempts", "3"),
                                    "schema.type", "/update/max_boot_attempts"),
    "field-updated without update": (FIELD_UPDATED, lambda d: d.pop("update"),
                                     vd.RULE_UPDATE, "/update_model"),
    "field-updated without failure_switch": (FIELD_UPDATED, lambda d: d["health"].pop("failure_switch"),
                                             vd.RULE_FAILURE_SWITCH, "/health"),
    "reflash-only with update": (REFLASH_ONLY, lambda d: d.__setitem__("update", copy.deepcopy(FIELD_UPDATED["update"])),
                                 vd.RULE_REFLASH, "/update"),
}


@pytest.mark.parametrize("case", list(MUTATIONS), ids=list(MUTATIONS))
def test_mutation_cases_are_invalid_with_rule_id(tmp_path, capsys, case):
    base, fn, rule, path = MUTATIONS[case]
    code, payload = _run(tmp_path, _mutate(base, fn), capsys)
    assert code == 1
    assert payload["result"] == "invalid"
    hits = [v for v in payload["violations"] if v["rule"] == rule]
    assert hits, payload
    assert hits[0]["path"] == path
    assert isinstance(hits[0].get("line"), int)


# --------------------------------------------------------------------------- #
# One negative per remaining constraint class
# --------------------------------------------------------------------------- #
NEGATIVES = {
    "required": (lambda d: d.pop("boot_chain"), "schema.required", "/"),
    "enum": (lambda d: d["image"].__setitem__("toolchain", "gentoo"), "schema.enum", "/image/toolchain"),
    "type": (lambda d: d.__setitem__("boot_chain", "implemented"), "schema.type", "/boot_chain"),
    "minLength": (lambda d: d["health"]["definition"].__setitem__("name", ""), "schema.minLength",
                  "/health/definition/name"),
    "minimum": (lambda d: d["update"].__setitem__("max_boot_attempts", -1), "schema.minimum",
                "/update/max_boot_attempts"),
    "additionalProperties top level": (lambda d: d.__setitem__("notes", "x"), "schema.additionalProperties", "/"),
    "additionalProperties via $ref": (lambda d: d["health"]["failure_switch"].__setitem__("default", "1"),
                                      "schema.additionalProperties", "/health/failure_switch"),
}
# `const` needs the explicit schema, since the lookup follows schema_version: see test_const_violation.


@pytest.mark.parametrize("case", list(NEGATIVES), ids=list(NEGATIVES))
def test_constraint_class_negatives(tmp_path, capsys, case):
    fn, rule, path = NEGATIVES[case]
    code, payload = _run(tmp_path, _mutate(FIELD_UPDATED, fn), capsys)
    assert code == 1 and payload["result"] == "invalid"
    assert any(v["rule"] == rule and v["path"] == path for v in payload["violations"]), payload


def test_const_violation(tmp_path, capsys):
    # The lookup would pick a v1.1 schema; pinning v1.0 exercises its const.
    doc = _mutate(FIELD_UPDATED, lambda d: d.__setitem__("schema_version", "1.1"))
    code, payload = _run(tmp_path, doc, capsys, "--schema", str(SCHEMA_PATH))
    assert code == 1
    assert any(v["rule"] == "schema.const" and v["path"] == "/schema_version" for v in payload["violations"])


def test_unknown_schema_version_is_invalid(tmp_path, capsys):
    doc = _mutate(FIELD_UPDATED, lambda d: d.__setitem__("schema_version", "9.9"))
    code, payload = _run(tmp_path, doc, capsys)
    assert code == 1
    assert "schema_version.unknown" in _rules(payload)


def test_unquoted_schema_version_is_invalid(tmp_path, capsys):
    text = yaml.safe_dump(FIELD_UPDATED, sort_keys=False).replace("schema_version: '1.0'", "schema_version: 1.0")
    code, payload = _run(tmp_path, text, capsys)
    assert code == 1
    assert "schema_version.unknown" in _rules(payload)


def test_schema_picked_from_schema_version(tmp_path, capsys, monkeypatch):
    # A v1.1 schema in the installed schema tree is used without a new code path.
    repo = tmp_path / "repo"
    (repo / "schemas").mkdir(parents=True)
    v11 = copy.deepcopy(SCHEMA)
    v11["properties"]["schema_version"]["const"] = "1.1"
    (repo / "schemas" / "image-declaration-v1.1.schema.yaml").write_text(yaml.safe_dump(v11), encoding="utf-8")
    doc = _mutate(FIELD_UPDATED, lambda d: d.__setitem__("schema_version", "1.1"))
    decl = tmp_path / "image-declaration.yaml"
    decl.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
    monkeypatch.setattr(vd, "installed_schema_dirs", lambda: [repo / "schemas"])
    code = vd.main([str(decl)])
    payload = json.loads(capsys.readouterr().out)
    assert code == 0 and payload["result"] == "valid"
    assert payload["schema"].endswith("image-declaration-v1.1.schema.yaml")


def test_no_schema_reachable_is_not_decidable(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(vd, "installed_schema_dirs", lambda: [])
    code, payload = _run(tmp_path, FIELD_UPDATED, capsys)
    assert code == 2
    assert payload["result"] == "not-decidable"


def test_audited_repository_schema_is_never_used(tmp_path, capsys, monkeypatch):
    # A permissive schema shipped by the audited repository must not judge its own declaration.
    monkeypatch.chdir(tmp_path)
    (tmp_path / "schemas").mkdir()
    for version in ("1.0", "7.0"):
        (tmp_path / "schemas" / f"image-declaration-v{version}.schema.yaml").write_text("{}\n", encoding="utf-8")
    doc = _mutate(REFLASH_ONLY, lambda d: d.__setitem__("anything", "goes"))
    code, payload = _run(tmp_path, doc, capsys)
    assert code == 1 and "schema.additionalProperties" in _rules(payload)
    assert Path(payload["schema"]).resolve() == SCHEMA_PATH.resolve()
    code, payload = _run(tmp_path, _mutate(doc, lambda d: d.__setitem__("schema_version", "7.0")), capsys)
    assert code == 1 and "schema_version.unknown" in _rules(payload)


def test_yaml_alias_is_rejected(tmp_path, capsys):
    bomb = "a0: &a0 [x, x, x, x, x, x, x, x, x, x]\n" + "".join(
        f"a{i}: &a{i} [{', '.join([f'*a{i - 1}'] * 10)}]\n" for i in range(1, 8))
    code, payload = _run(tmp_path, bomb, capsys)
    assert code == 1 and _rules(payload) == {"yaml.alias"}


def test_deep_nesting_is_invalid_with_json(tmp_path, capsys):
    code, payload = _run(tmp_path, "x: " + "[" * 5000 + "]" * 5000 + "\n", capsys)
    assert code == 1 and payload["result"] == "invalid"
    assert _rules(payload) <= {"yaml.depth", "yaml.parse"}


def test_oversized_declaration_is_invalid(tmp_path, capsys):
    code, payload = _run(tmp_path, "# " + "x" * (vd.MAX_BYTES + 1) + "\n", capsys)
    assert code == 1 and _rules(payload) == {"declaration.too-large"}


# --------------------------------------------------------------------------- #
# Unparseable and missing input
# --------------------------------------------------------------------------- #
def test_unparseable_yaml_is_invalid(tmp_path, capsys):
    code, payload = _run(tmp_path, "image: [unclosed\n  name: x\n", capsys)
    assert code == 1
    assert payload["result"] == "invalid"
    assert _rules(payload) == {"yaml.parse"}


def test_missing_file_is_invalid(tmp_path, capsys):
    code = vd.main([str(tmp_path / "absent.yaml")])
    payload = json.loads(capsys.readouterr().out)
    assert code == 1
    assert _rules(payload) == {"declaration.unreadable"}


# --------------------------------------------------------------------------- #
# Fail closed without the validator dependencies
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("blocked", ["yaml", "jsonschema"])
def test_missing_dependencies_exit_2_never_valid(tmp_path, blocked):
    decl = tmp_path / "image-declaration.yaml"
    decl.write_text(yaml.safe_dump(FIELD_UPDATED, sort_keys=False), encoding="utf-8")
    # `-I` drops PYTHONPATH and user site-packages; the sys.modules block makes
    # the import fail even where the modules live in the system site-packages (CI).
    bootstrap = (
        "import runpy, sys\n"
        f"sys.modules[{blocked!r}] = None\n"
        f"sys.argv = [{str(VALIDATOR)!r}, {str(decl)!r}]\n"
        f"runpy.run_path({str(VALIDATOR)!r}, run_name='__main__')\n"
    )
    proc = subprocess.run(
        [sys.executable, "-I", "-c", bootstrap],
        capture_output=True, text=True, check=False, env={"PYTHONPATH": "", "PATH": "/usr/bin:/bin"},
    )
    assert proc.returncode == 2, proc.stderr
    assert "valid" not in proc.stdout
    assert json.loads(proc.stdout)["result"] == "not-decidable"
    assert "pip install jsonschema pyyaml" in proc.stderr


# --------------------------------------------------------------------------- #
# Protocol freshness (#735)
# --------------------------------------------------------------------------- #
def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True,
        env={"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
             "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid",
             "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null",
             "PATH": "/usr/bin:/bin"},
    ).stdout.strip()


UNIT = "images/edge-appliance/mkosi.extra/usr/lib/systemd/system/appliance-health.service"
DECL = "images/edge-appliance/image-declaration.yaml"
CONF = "images/edge-appliance/mkosi.conf"


@pytest.fixture
def image_repo(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    for rel, body in {
        DECL: yaml.safe_dump(FIELD_UPDATED, sort_keys=False),
        CONF: "[Output]\nImageId=edge-appliance\n",
        UNIT: "[Unit]\nBefore=boot-complete.target\n",
    }.items():
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_text(body, encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "X")
    return repo, _git(repo, "rev-parse", "HEAD")


def _path_set() -> list[str]:
    # declaration, its definition, the declaration's directory, the scanner's definition files
    return [DECL, CONF, "images/edge-appliance", UNIT]


def test_protocol_without_later_change_is_fresh(image_repo):
    repo, x = image_repo
    assert pf.check(repo, x, "HEAD", _path_set()) == (0, ["fresh"])


def test_overlay_unit_change_makes_protocol_stale(image_repo):
    repo, x = image_repo
    (repo / UNIT).write_text("[Unit]\n", encoding="utf-8")
    _git(repo, "commit", "-q", "-am", "Y")
    y = _git(repo, "rev-parse", "HEAD")
    # The old rule (`git log -1 -- <declaration> <definition>`) still names X.
    assert _git(repo, "log", "-1", "--format=%H", "--", DECL, CONF) == x
    code, lines = pf.check(repo, x, "HEAD", _path_set())
    assert code == 1
    assert f"stale: {UNIT} changed in {y}" in lines
    assert f"stale: images/edge-appliance changed in {y}" in lines
    assert not any(line.startswith(f"stale: {CONF} ") for line in lines)


def test_uncommitted_change_makes_protocol_stale(image_repo):
    repo, x = image_repo
    (repo / UNIT).write_text("[Unit]\n", encoding="utf-8")
    code, lines = pf.check(repo, x, "HEAD", [UNIT])
    assert code == 1 and lines == [f"stale: {UNIT} has uncommitted changes"]


def test_unknown_protocol_commit_is_not_decidable(image_repo):
    repo, _ = image_repo
    code, lines = pf.check(repo, "0" * 40, "HEAD", _path_set())
    assert code == 2 and lines[0].startswith("not-decidable:")


@pytest.mark.parametrize("symbolic", ["HEAD", "main", "HEAD~0", "@"])
def test_symbolic_protocol_commit_is_not_decidable(image_repo, symbolic):
    repo, x = image_repo
    (repo / CONF).write_text("[Output]\n", encoding="utf-8")
    _git(repo, "commit", "-q", "-am", "Y")
    assert pf.check(repo, x, "HEAD", [CONF])[0] == 1
    code, lines = pf.check(repo, symbolic, "HEAD", [CONF])
    assert code == 2 and lines[0].startswith("not-decidable:")


def test_non_ancestor_protocol_commit_is_stale(image_repo):
    repo, x = image_repo
    _git(repo, "checkout", "-q", "-b", "side")
    (repo / CONF).write_text("[Output]\nside\n", encoding="utf-8")
    _git(repo, "commit", "-q", "-am", "side")
    side = _git(repo, "rev-parse", "HEAD")
    _git(repo, "checkout", "-q", "main")
    code, lines = pf.check(repo, side, "HEAD", [CONF])
    assert code == 1 and "isn't an ancestor" in lines[0]


def test_explicit_revision_is_judged(image_repo):
    repo, x = image_repo
    (repo / CONF).write_text("[Output]\n", encoding="utf-8")
    _git(repo, "commit", "-q", "-am", "Y")
    assert pf.check(repo, x, x, [CONF]) == (0, ["fresh"])
    assert pf.check(repo, x, "HEAD", [CONF])[0] == 1


def test_path_missing_at_revision_is_not_decidable(image_repo):
    repo, x = image_repo
    code, lines = pf.check(repo, x, "HEAD", ["images/edge-appliance/mkosi.cnf"])
    assert code == 2 and "doesn't exist" in lines[0]


def test_symlinked_overlay_is_not_decidable(image_repo):
    repo, x = image_repo
    (repo / "shared").mkdir()
    (repo / "shared" / "unit.service").write_text("[Unit]\n", encoding="utf-8")
    (repo / "images/edge-appliance/extra").symlink_to("../../shared")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "link")
    head = _git(repo, "rev-parse", "HEAD")
    code, lines = pf.check(repo, head, "HEAD", ["images/edge-appliance"])
    assert code == 2 and "symbolic link" in lines[0]


def test_freshness_cli_prints_result(image_repo, capsys):
    repo, x = image_repo
    assert pf.main(["--repo", str(repo), "--commit", x, "--", *_path_set()]) == 0
    assert capsys.readouterr().out.strip() == "fresh"


# --------------------------------------------------------------------------- #
# linux-image-scanner tool surface (#731)
# --------------------------------------------------------------------------- #
def test_scanner_declares_no_write_or_execution_tool():
    text = SCANNER.read_text(encoding="utf-8")
    front = yaml.safe_load(text.split("---", 2)[1])
    tools = [t.strip() for t in str(front["tools"]).split(",")]
    assert tools == ["Read", "Glob", "Grep"]
    for forbidden in ("Bash", "Write", "Edit", "NotebookEdit"):
        assert forbidden not in tools
    body = text.split("---", 2)[2]
    assert not re.search(r"\bpython3\b|`Bash`|Read-only Bash justification", body)
