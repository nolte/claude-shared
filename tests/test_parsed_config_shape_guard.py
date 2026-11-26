"""Class guard: a parsed YAML/JSON value is shape-checked before it is used (#816).

Guard origin (spec/project/defect-class-guards/ G5): #816, whose class is
"parsed YAML/JSON used without a shape check", which ends in an
AttributeError/TypeError traceback or a silent default instead of a message
that names the file.

Predicate (G3). Over every ``*.py`` file below ``scripts/`` (the selector is the
recursive glob, not a file list; G6), take each call to a loader:
``yaml.safe_load``, ``yaml.load``, ``yaml.full_load``, ``yaml.unsafe_load``,
``json.load`` or ``json.loads``. Module aliases (``import json as j``) and
imported names (``from json import loads``) resolve to the same loaders. The
parsed value is the call itself, or the smallest ``... or ...`` /
``... if ... else ...`` expression that can evaluate to it (``yaml.safe_load(x)
or {}``). The site is a class member, and the guard fails on it, when:

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
   or it flows anywhere else unchecked (an argument, a ``return``).

A loader call whose result is discarded (an expression statement, used only to
see whether the text parses) isn't a member.

A member that is correct as written goes in ALLOWLIST with the reason it is
safe. An entry that matches no site fails the guard, so a reason can't outlive
its site (G4). Every entry covers a site that was checked and is safe; none
covers an unrepaired member (G7).

Not covered: loaders other than the six above, and Python files outside
``scripts/`` (plugin-bundled scripts, evals/). The issue records those.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

LOADERS = {
    ("yaml", "safe_load"), ("yaml", "load"), ("yaml", "full_load"), ("yaml", "unsafe_load"),
    ("json", "load"), ("json", "loads"),
}

# (path relative to scripts/, enclosing function, assignment target or "<expr>") -> reason.
ALLOWLIST: dict[tuple[str, str, str], str] = {
    ("validate_schemas.py", "main", "data"):
        "a governed data file may have any JSON shape; it is passed only to "
        "Draft202012Validator.iter_errors, which validates it against the bound schema",
    ("docs/gen_catalog.py", "parse_frontmatter", "meta[key]"):
        "a value-level load of one frontmatter key; every consumed key is shape-checked "
        "where it is read (_validate_phase, _normalize_tags, _validate_summary, "
        "_validate_use_when, _validate_dont_use_when, _validate_see_also, "
        "_validate_examples; name/description via the folder-name equality check and str())",
}


@dataclass(frozen=True)
class Member:
    path: str
    line: int
    scope: str
    target: str
    problem: str

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.path, self.scope, self.target)

    def __str__(self) -> str:
        return f"scripts/{self.path}:{self.line} ({self.scope}, {self.target}): {self.problem}"


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


def find_members(scripts_root: Path) -> list[Member]:
    members: list[Member] = []
    for path in sorted(scripts_root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(scripts_root).as_posix()
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


def test_every_parsed_value_is_shape_checked_before_use():
    unexplained = [m for m in find_members(SCRIPTS) if m.key not in ALLOWLIST]
    assert not unexplained, "parsed YAML/JSON used without a shape check:\n" + "\n".join(map(str, unexplained))


def test_every_allowlist_entry_matches_a_site_and_carries_a_reason():
    keys = {m.key for m in find_members(SCRIPTS)}
    stale = sorted(k for k in ALLOWLIST if k not in keys)
    assert not stale, f"allowlist entries that match no site (remove them): {stale}"
    assert all(reason.strip() for reason in ALLOWLIST.values())


# --- the predicate itself, on synthetic sources --------------------------------

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
    )
    found = {(m.scope, m.target) for m in _members_of(tmp_path, source)}
    assert found == {("direct", "<expr>"), ("direct_or", "<expr>"), ("unchecked", "d"),
                     ("late", "d"), ("escapes", "<expr>"), ("subscript_target", "m['k']")}


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
