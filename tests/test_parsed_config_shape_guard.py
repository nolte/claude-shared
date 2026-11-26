"""Class guard: a parsed YAML/JSON value is shape-checked before it is used (#816).

Guard origin (spec/project/defect-class-guards/ G5): #816, whose class is
"parsed YAML/JSON used without a shape check", which ends in an
AttributeError/TypeError traceback or a silent default instead of a message
that names the file.

Selector (G6). Every ``*.py`` file the repository holds, found by
``ROOT.rglob("*.py")``: the shipped scripts (``scripts/``), the plugin- and
skill-bundled scripts (``plugins/*/skills/*/scripts/``, ``skills/*/scripts/``),
the eval harness (``evals/``), the spec templates handed to consumers
(``spec/**/templates/``) and ``design/``. A new file joins by existing, not by
being named. Excluded, each for a stated reason:

- ``tests/`` (top level): the test suite. Its fixtures parse synthetic input
  freely, and this guard's own self-tests write members on purpose.
- any path with a ``.git``, ``.venv``, ``venv``, ``node_modules``, ``site`` or
  ``__pycache__`` segment: version-control internals, installed third-party
  packages, the built MkDocs site, and bytecode caches. None is authored here;
  all are gitignored or git-internal. Measured on this tree they hold no
  ``*.py`` at all, so the exclusion only keeps a local virtualenv or build from
  flooding the guard with code this repository doesn't own.

Predicate (G3). In each selected file, take each call to a loader:
``yaml.safe_load``, ``yaml.load``, ``yaml.full_load``, ``yaml.unsafe_load``,
``yaml.safe_load_all``, ``yaml.load_all``, ``json.load`` or ``json.loads``.
Module aliases (``import json as j``) and imported names (``from json import
loads``) resolve to the same loaders. The parsed value is the call itself, or
the smallest ``... or ...`` / ``... if ... else ...`` expression that can
evaluate to it (``yaml.safe_load(x) or {}``). The site is a class member when:

1. the parsed value is used directly, with an attribute or subscript applied to
   it (``json.loads(x)["key"]``, ``yaml.safe_load(x).get("k")``); or
2. it is assigned to a single name, and that name is never passed as the first
   argument of ``isinstance(...)`` in the same function (module level for
   top-level code) at or after the assignment line; or the name has an
   attribute or subscript applied at a line after the assignment and before
   the first such ``isinstance``. Same-line uses count as checked, so
   ``x.get(k) if isinstance(x, dict) else None`` passes. Order is lexical
   (line numbers), not control flow; or
3. it is assigned to anything other than a single name (``meta[key] = ...``),
   or it flows anywhere else unchecked (an argument, a ``return``, a ``for``).

A loader call whose result is discarded (an expression statement, used only to
see whether the text parses) isn't a member.

Every member must be covered by exactly one entry, keyed by (file, enclosing
function, assignment target or ``<expr>``) and carrying the exact number of
sites it covers (G4): a second matching site, or a site that disappears, fails
the guard, so an entry can't silently cover a new member or outlive its site.

- ALLOWLIST: members that are correct as written, each with the reason.
- KNOWN_UNREPAIRED: members #816 measured but deliberately didn't repair (G7).
  The guard skips them explicitly, never asserts them as intended, and carries
  FOLLOW_UP_ISSUE at each entry. Repairing one makes its entry stale, which
  fails until the entry is removed.

Not covered (a reader deciding whether a new case is caught should check these
by hand):

- ``isinstance`` with any type counts as the check: ``isinstance(x, str)``
  satisfies rule 2 even where the code then needs a mapping.
- uses other than attribute or subscript before the check (iterating the name,
  passing it as an argument, ``len(x)``) aren't seen as early uses.
- loads inside a lambda or nested function are judged only within their own
  scope; the flow from there into the enclosing function isn't followed (a
  ``return`` of the parsed value is itself a member, rule 3).
- loader aliases by assignment (``load = json.loads``), ``json.JSONDecoder().
  decode``, ``tomllib.load``/``loads`` (whose top level is always a table, but
  whose values aren't), and any other parser.
- reassignment of the name between the load and the check.
- the shape below the top level (``doc["components"][0]``).
"""
from __future__ import annotations

import ast
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXCLUDED_TOP = {"tests"}
EXCLUDED_PARTS = {".git", ".venv", "venv", "node_modules", "site", "__pycache__"}

LOADERS = {
    ("yaml", "safe_load"), ("yaml", "load"), ("yaml", "full_load"), ("yaml", "unsafe_load"),
    ("yaml", "safe_load_all"), ("yaml", "load_all"),
    ("json", "load"), ("json", "loads"),
}

# The issue that repairs the KNOWN_UNREPAIRED members.
FOLLOW_UP_ISSUE = "#TBD"

Key = tuple[str, str, str]  # (path relative to ROOT, enclosing function, target or "<expr>")

# key -> (exact number of sites, reason it is safe)
ALLOWLIST: dict[Key, tuple[int, str]] = {
    ("scripts/validate_schemas.py", "main", "data"): (
        1,
        "a governed data file may have any JSON shape; it is passed only to "
        "Draft202012Validator.iter_errors, which validates it against the bound schema",
    ),
    ("scripts/docs/gen_catalog.py", "parse_frontmatter", "meta[key]"): (
        2,
        "value-level loads of one frontmatter key (flow list, block value); each key "
        "discover_skills/discover_agents consume is checked where it is read: name by "
        "equality with the folder name / file stem; description by isinstance(str); "
        "distribution by membership in ('plugin', 'project'); phase by _validate_phase; "
        "tags by _normalize_tags; summary and summary_<lang> (via _collect_summaries) by "
        "_validate_summary; use_when, dont_use_when, see_also and examples by their "
        "_validate_* functions. No other key is read",
    ),
}

# key -> exact number of sites; measured in #816, not repaired there (FOLLOW_UP_ISSUE).
KNOWN_UNREPAIRED: dict[Key, int] = {
    ("evals/harness/runner.py", "parse_json_result", "data"): 1,
    ("evals/harness/runner.py", "parse_cost", "<expr>"): 1,
    ("evals/harness/scorecard.py", "read", "<expr>"): 1,
    ("plugins/nolte-engineering/skills/capability-reach-audit/scripts/reach_audit.py", "load_yaml", "<expr>"): 1,
    ("plugins/nolte-linux/skills/image-boot-verify/scripts/boot_verify.py", "run_validator", "payload"): 1,
    ("plugins/nolte-linux/skills/image-boot-verify/scripts/boot_verify.py", "qmp", "reply"): 1,
    ("plugins/nolte-linux/skills/image-boot-verify/scripts/boot_verify.py", "read_declaration", "self.decl"): 1,
    ("plugins/nolte-linux/skills/linux-image-audit/scripts/validate_declaration.py", "_load_json", "<expr>"): 1,
    ("plugins/nolte-linux/skills/linux-image-audit/scripts/validate_declaration.py", "_validate", "doc"): 1,
    ("plugins/nolte-linux/skills/linux-image-audit/scripts/validate_declaration.py", "_check", "schema"): 1,
    ("plugins/nolte-media/skills/image-generate/scripts/image_generate.py", "_api_error_detail", "<expr>"): 1,
    ("plugins/nolte-media/skills/image-generate/scripts/image_generate.py", "_post_json", "<expr>"): 1,
    ("skills/pull-request-merge-order/scripts/merge_order.py", "main", "snapshot"): 1,
    # Found by widening the selector to spec/ templates (round 4), after the 13 above.
    ("spec/project/e2e-test-automation/templates/conftest.py", "_load_checkpoint", "entry"): 1,
}


@dataclass(frozen=True)
class Member:
    path: str
    line: int
    scope: str
    target: str
    problem: str

    @property
    def key(self) -> Key:
        return (self.path, self.scope, self.target)

    def __str__(self) -> str:
        return f"{self.path}:{self.line} ({self.scope}, {self.target}): {self.problem}"


def python_files(root: Path) -> list[Path]:
    """The selector: every *.py below `root` outside the excluded segments."""
    out = []
    for path in sorted(root.rglob("*.py")):
        parts = path.relative_to(root).parts
        if parts[0] in EXCLUDED_TOP or EXCLUDED_PARTS.intersection(parts):
            continue
        out.append(path)
    return out


def _loader_names(tree: ast.Module) -> tuple[dict[str, str], dict[str, tuple[str, str]]]:
    """Module aliases (`j` -> json) and imported loader names (`loads` -> (json, loads))."""
    modules: dict[str, str] = {}
    funcs: dict[str, tuple[str, str]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in ("yaml", "json"):
                    modules[alias.asname or alias.name] = alias.name
        elif isinstance(node, ast.ImportFrom) and node.module in ("yaml", "json"):
            for alias in node.names:
                if (node.module, alias.name) in LOADERS:
                    funcs[alias.asname or alias.name] = (node.module, alias.name)
    return modules, funcs


def _is_loader(call: ast.Call, modules: dict[str, str], funcs: dict[str, tuple[str, str]]) -> bool:
    f = call.func
    if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
        return (modules.get(f.value.id), f.attr) in LOADERS
    return isinstance(f, ast.Name) and f.id in funcs


def _scope_nodes(scope: ast.AST):
    """Every node lexically inside `scope`, not descending into nested scopes."""
    stack = list(ast.iter_child_nodes(scope))
    while stack:
        node = stack.pop()
        yield node
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            stack.extend(ast.iter_child_nodes(node))


def _name_problem(scope: ast.AST, name: str, assign: ast.stmt) -> str | None:
    checks: list[int] = []
    uses: list[int] = []
    for node in _scope_nodes(scope):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "isinstance" and node.args
                and isinstance(node.args[0], ast.Name) and node.args[0].id == name
                and node.lineno >= assign.lineno):
            checks.append(node.lineno)
        elif (isinstance(node, (ast.Attribute, ast.Subscript))
              and isinstance(node.value, ast.Name) and node.value.id == name
              and node.lineno > (assign.end_lineno or assign.lineno)):
            uses.append(node.lineno)
    if not checks:
        return f"`{name}` is never passed to isinstance() after it is parsed"
    early = sorted(line for line in uses if line < min(checks))
    if early:
        return f"`{name}` is used at line {early[0]} before its isinstance() check at line {min(checks)}"
    return None


def find_members(root: Path) -> list[Member]:
    members: list[Member] = []
    for path in python_files(root):
        rel = path.relative_to(root).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        modules, funcs = _loader_names(tree)
        parents: dict[ast.AST, ast.AST] = {}
        scopes: dict[ast.AST, ast.AST] = {}

        def index(node: ast.AST, scope: ast.AST) -> None:
            for child in ast.iter_child_nodes(node):
                parents[child] = node
                scopes[child] = scope
                inner = child if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)) else scope
                index(child, inner)

        index(tree, tree)
        for call in [n for n in parents if isinstance(n, ast.Call) and _is_loader(n, modules, funcs)]:
            node: ast.AST = call
            parent = parents[node]
            while (isinstance(parent, ast.BoolOp)
                   or (isinstance(parent, ast.IfExp) and node is not parent.test)):
                node, parent = parent, parents[parent]
            scope = scopes[call]
            scope_name = getattr(scope, "name", "<module>")

            def member(target: str, problem: str) -> Member:
                return Member(rel, call.lineno, scope_name, target, problem)

            if isinstance(parent, ast.Expr):
                continue  # discarded: parsed only to see whether it parses
            if isinstance(parent, (ast.Attribute, ast.Subscript)) and parent.value is node:
                members.append(member("<expr>", f"`{ast.unparse(parent)[:60]}` uses the parsed value directly"))
            elif isinstance(parent, (ast.Assign, ast.AnnAssign)) and parent.value is node:
                targets = parent.targets if isinstance(parent, ast.Assign) else [parent.target]
                if len(targets) == 1 and isinstance(targets[0], ast.Name):
                    problem = _name_problem(scope, targets[0].id, parent)
                    if problem:
                        members.append(member(targets[0].id, problem))
                else:
                    text = ", ".join(ast.unparse(t) for t in targets)
                    members.append(member(text, "the parsed value is bound to a non-name target, unchecked"))
            else:
                members.append(member("<expr>", f"the parsed value flows into a {type(parent).__name__} unchecked"))
    return members


def evaluate(members: list[Member], allowlist: dict[Key, tuple[int, str]],
             known: dict[Key, int]) -> list[str]:
    """Every problem: an uncovered member, or an entry whose site count is off."""
    counts = Counter(m.key for m in members)
    problems = [f"new member: {m}" for m in members if m.key not in allowlist and m.key not in known]
    expected = {**{k: n for k, (n, _) in allowlist.items()}, **known}
    for key, n in sorted(expected.items()):
        if counts[key] != n:
            kind = "allowlist" if key in allowlist else "known-unrepaired"
            sites = [str(m) for m in members if m.key == key]
            problems.append(f"{kind} entry {key} expects {n} site(s), matches {counts[key]}: {sites}")
    return problems


def test_every_parsed_value_is_shape_checked_or_explicitly_listed():
    problems = evaluate(find_members(ROOT), ALLOWLIST, KNOWN_UNREPAIRED)
    assert not problems, "parsed YAML/JSON used without a shape check:\n" + "\n".join(problems)


def test_entries_carry_a_reason_and_the_follow_up_issue():
    assert all(reason.strip() for _, reason in ALLOWLIST.values())
    assert FOLLOW_UP_ISSUE.startswith("#")
    assert not set(ALLOWLIST) & set(KNOWN_UNREPAIRED)


def test_selector_reaches_every_tree_that_holds_python():
    """G6: the selector is derived, so every authored tree is in it and tests/ is not."""
    tops = {p.relative_to(ROOT).parts[0] for p in python_files(ROOT)}
    assert {"scripts", "plugins", "skills", "evals", "spec"} <= tops
    assert "tests" not in tops


# --- the predicate and the count rule, on synthetic sources --------------------

def _members_of(tmp_path: Path, source: str) -> list[Member]:
    (tmp_path / "mod.py").write_text(source, encoding="utf-8")
    return find_members(tmp_path)


def test_guard_flags_each_member_shape(tmp_path):
    source = (
        "import json\n"
        "import yaml as y\n"
        "from json import loads as jl\n"
        "def direct(t):\n    return json.loads(t)['k']\n"
        "def direct_or(t):\n    return (y.safe_load(t) or {}).get('k')\n"
        "def unchecked(t):\n    d = jl(t)\n    return d.get('k')\n"
        "def late(t):\n    d = y.safe_load(t) or {}\n    v = d['k']\n    if not isinstance(d, dict):\n"
        "        raise SystemExit(1)\n    return v\n"
        "def escapes(t):\n    return json.loads(t)\n"
        "def subscript_target(t, m):\n    m['k'] = y.safe_load(t)\n"
        "def each(t):\n    for doc in y.safe_load_all(t):\n        doc.get('k')\n"
    )
    found = {(m.scope, m.target) for m in _members_of(tmp_path, source)}
    assert found == {("direct", "<expr>"), ("direct_or", "<expr>"), ("unchecked", "d"),
                     ("late", "d"), ("escapes", "<expr>"), ("subscript_target", "m['k']"),
                     ("each", "<expr>")}


def test_guard_passes_checked_and_discarded_loads(tmp_path):
    source = (
        "import json, yaml\n"
        "def checked(t):\n    d = yaml.safe_load(t) or {}\n    if not isinstance(d, dict):\n"
        "        raise SystemExit(1)\n    return d.get('k')\n"
        "def same_line(t):\n    d = json.loads(t)\n    return d.get('k') if isinstance(d, dict) else None\n"
        "def ifexp(t):\n    d = json.loads(t) if t else {}\n    if not isinstance(d, dict):\n        d = {}\n"
        "    return d.get('k')\n"
        "def discarded(t):\n    yaml.safe_load(t)\n"
        "def other(t):\n    return t.loads()\n"
    )
    assert _members_of(tmp_path, source) == []


def test_a_second_site_under_an_allowlisted_key_fails(tmp_path):
    """G4: the validate_schemas.main entry covers one load; a second identical one fails."""
    key = ("scripts/validate_schemas.py", "main", "data")
    original = (ROOT / key[0]).read_text(encoding="utf-8")
    line = '            data = yaml.safe_load(data_file.read_text(encoding="utf-8"))\n'
    assert original.count(line) == 1
    copy = tmp_path / key[0]
    copy.parent.mkdir(parents=True)
    copy.write_text(original, encoding="utf-8")
    assert evaluate(find_members(tmp_path), {key: ALLOWLIST[key]}, {}) == []
    copy.write_text(original.replace(line, line + line), encoding="utf-8")
    problems = evaluate(find_members(tmp_path), {key: ALLOWLIST[key]}, {})
    assert len(problems) == 1 and "expects 1 site(s), matches 2" in problems[0]


def test_a_repaired_known_unrepaired_entry_goes_stale(tmp_path):
    key = ("mod.py", "f", "d")
    broken = "import json\ndef f(t):\n    d = json.loads(t)\n    return d.get('k')\n"
    assert evaluate(_members_of(tmp_path, broken), {}, {key: 1}) == []
    fixed = broken.replace("    return", "    if not isinstance(d, dict):\n        return None\n    return")
    problems = evaluate(_members_of(tmp_path, fixed), {}, {key: 1})
    assert len(problems) == 1 and "known-unrepaired entry" in problems[0] and "matches 0" in problems[0]


def test_a_new_member_beside_known_ones_fails(tmp_path):
    source = ("import json\ndef f(t):\n    d = json.loads(t)\n    return d.get('k')\n"
              "def g(t):\n    return json.loads(t)['k']\n")
    problems = evaluate(_members_of(tmp_path, source), {}, {("mod.py", "f", "d"): 1})
    assert len(problems) == 1 and problems[0].startswith("new member: mod.py:6 (g, <expr>)")
