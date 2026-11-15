#!/usr/bin/env python3
"""Validate an image-declaration.yaml or a boot protocol.json, failing closed.

``--kind declaration`` (the default) decides both halves of the declaration
contract of
``spec/project/linux-image-best-practices/`` §A and §F:

- the JSON Schema ``schemas/image-declaration-v<schema_version>.schema.yaml``
  (Draft 2020-12), picked from the declaration's own ``schema_version`` so a
  later schema version needs no new code path;
- the three §F conditional rules the schema deliberately leaves out:
  ``field-updated`` requires the ``update`` block and ``health.failure_switch``,
  and ``reflash-only`` forbids the ``update`` block.

``--kind boot-protocol`` validates the ``protocol.json`` of a boot
verification run against ``schemas/image-boot-protocol-v<schema_version>.schema.yaml``
(``spec/project/image-boot-verification/`` §G), through the same lookup, size,
depth, and exit-code guards; it has no conditional half.

Schema lookup order: ``--schema <file>`` (an operator choice); else the
installed ``nolte-shared`` plugin's ``schemas/`` tree, found next to this plugin
(the monorepo layout and the marketplace cache layout). The audited
repository's own ``schemas/`` is never consulted: a repository can't supply the
schema that judges its own declaration or protocol.

A declaration is read with PyYAML's safe loader after two guards: files over
1 MiB and YAML aliases are rejected as ``invalid`` (an alias can expand a few
hundred bytes into gigabytes), and nesting too deep to load is ``invalid`` too,
always with the JSON output below. A protocol is read as strict JSON: the same
size and depth guards, and a duplicate key or a non-JSON constant (``NaN``,
``Infinity``) is ``invalid``.

Output: one JSON object on stdout,
``{"result": "valid|invalid|not-decidable", "violations": [...], ...}``, where
each violation carries a stable ``rule`` identifier (``schema.<keyword>``,
``conditional.<rule>``, ``schema_version.unknown``, ``yaml.parse``,
``yaml.alias``, ``yaml.depth``, ``declaration.too-large``,
``declaration.unreadable``; for a protocol ``json.parse``,
``json.duplicate-key``, ``json.depth``, ``protocol.too-large``,
``protocol.unreadable``), the JSON-pointer ``path``, a ``message``, and the
1-based ``line`` in the file when it's known.

Exit codes (mirroring scripts/validate_schemas.py):
  0  valid
  1  invalid
  2  not decidable: jsonschema/PyYAML missing (install hint on stderr) or no
     schema of the kind reachable. Never reported as valid
     (spec/project/yaml-json-schema/ §Validation contract).

Usage:
  python3 "${CLAUDE_PLUGIN_ROOT}/skills/linux-image-audit/scripts/validate_declaration.py" \\
      images/edge-appliance/image-declaration.yaml [--schema FILE]
  python3 "${CLAUDE_PLUGIN_ROOT}/skills/linux-image-audit/scripts/validate_declaration.py" \\
      --kind boot-protocol .image-boot-verify/<run>/protocol.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

INSTALL_HINT = (
    "validate_declaration: dependencies missing ({err}).\n"
    "Install them with:  pip install jsonschema pyyaml\n"
    "The check stays not-decidable until they're installed; it is "
    "never reported as passing (spec/project/yaml-json-schema/ §Validation contract).\n"
)
SCHEMA_NAME = "image-declaration-v{version}.schema.yaml"
SCHEMA_GLOB = "image-declaration-v*.schema.yaml"
# Per kind: schema file name and glob, the noun in rule ids and messages, and
# the parser. Only the declaration has the §F conditional half.
KINDS = {
    "declaration": {"name": SCHEMA_NAME, "glob": SCHEMA_GLOB, "label": "image-declaration",
                    "noun": "declaration", "format": "yaml"},
    "boot-protocol": {"name": "image-boot-protocol-v{version}.schema.yaml",
                      "glob": "image-boot-protocol-v*.schema.yaml", "label": "image-boot-protocol",
                      "noun": "protocol", "format": "json"},
}
VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+$")

# scripts/ -> linux-image-audit/ -> skills/ -> <nolte-linux plugin root>
PLUGIN_ROOT = Path(__file__).resolve().parents[3]

RULE_UPDATE = "conditional.field-updated-requires-update"
RULE_FAILURE_SWITCH = "conditional.field-updated-requires-failure-switch"
RULE_REFLASH = "conditional.reflash-only-forbids-update"


MAX_BYTES = 1 << 20


def installed_schema_dirs(plugin_root: Path = PLUGIN_ROOT) -> list[Path]:
    """The installed nolte-shared ``schemas/`` candidates, nearest first.

    Monorepo / ``--plugin-dir`` layout: ``<repo>/plugins/nolte-linux`` beside
    ``<repo>/schemas``. Marketplace cache layout:
    ``<cache>/<marketplace>/nolte-linux/<version>`` beside
    ``<cache>/<marketplace>/nolte-shared/<version>`` (lockstep versions).
    """
    return [
        plugin_root.parent.parent / "schemas",
        plugin_root.parent.parent / "nolte-shared" / plugin_root.name / "schemas",
    ]


def _emit(result: str, violations: list[dict], **extra) -> None:
    payload = {"result": result, "violations": violations}
    payload.update(extra)
    sys.stdout.write(json.dumps(payload, indent=2, sort_keys=False) + "\n")


def _pointer(parts) -> str:
    return "".join(f"/{p}" for p in parts)


def _line_index(yaml_mod, text: str) -> dict[tuple, int]:
    """Map each key path in the document to its 1-based source line."""
    index: dict[tuple, int] = {}
    try:
        root = yaml_mod.compose(text, Loader=yaml_mod.SafeLoader)
    except yaml_mod.YAMLError:
        return index

    def walk(node, path: tuple) -> None:
        if node is None:
            return
        index.setdefault(path, node.start_mark.line + 1)
        if isinstance(node, yaml_mod.MappingNode):
            for key, value in node.value:
                sub = path + (key.value,)
                index[sub] = key.start_mark.line + 1
                walk(value, sub)
        elif isinstance(node, yaml_mod.SequenceNode):
            for i, item in enumerate(node.value):
                walk(item, path + (i,))

    walk(root, ())
    return index


def _line_for(index: dict[tuple, int], parts) -> int | None:
    parts = tuple(parts)
    while parts not in index and parts:
        parts = parts[:-1]
    return index.get(parts)


def _violation(rule: str, parts, message: str, index: dict[tuple, int]) -> dict:
    entry = {"rule": rule, "path": _pointer(parts) or "/", "message": message}
    line = _line_for(index, parts)
    if line is not None:
        entry["line"] = line
    return entry


def resolve_schema(version: str, schema_dirs: list[Path],
                   kind: str = "declaration") -> tuple[Path | None, bool]:
    """Return (schema file, any schema corpus of ``kind`` seen) for ``version``."""
    corpus_seen = False
    for directory in schema_dirs:
        if not directory.is_dir():
            continue
        if any(directory.glob(KINDS[kind]["glob"])):
            corpus_seen = True
        candidate = directory / KINDS[kind]["name"].format(version=version)
        if candidate.is_file():
            return candidate, corpus_seen
    return None, corpus_seen


def conditional_violations(doc: dict, index: dict[tuple, int]) -> list[dict]:
    """The three §F rules the schema can't express."""
    out: list[dict] = []
    model = doc.get("update_model")
    health = doc.get("health") if isinstance(doc.get("health"), dict) else {}
    if model == "field-updated":
        if "update" not in doc:
            out.append(_violation(
                RULE_UPDATE, ("update_model",),
                "update_model field-updated requires the `update` block (§F)", index))
        if "failure_switch" not in health:
            out.append(_violation(
                RULE_FAILURE_SWITCH, ("health",),
                "update_model field-updated requires `health.failure_switch` (§F)", index))
    elif model == "reflash-only" and "update" in doc:
        out.append(_violation(
            RULE_REFLASH, ("update",),
            "update_model reflash-only forbids the `update` block (§F)", index))
    return out


class _DuplicateKey(ValueError):
    pass


def _load_json(text: str):
    """Strict JSON: a duplicate key or NaN/Infinity is an error, not a guess."""
    def pairs(items):
        out: dict = {}
        for key, value in items:
            if key in out:
                raise _DuplicateKey(key)
            out[key] = value
        return out

    def constant(name):
        raise ValueError(f"non-JSON constant {name}")

    return json.loads(text, object_pairs_hook=pairs, parse_constant=constant)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate an image-declaration.yaml or a boot protocol.json.")
    parser.add_argument("declaration", type=Path,
                        help="Path of the image-declaration.yaml, or of the protocol.json "
                             "with --kind boot-protocol.")
    parser.add_argument("--kind", choices=sorted(KINDS), default="declaration",
                        help="What the file is (default: declaration).")
    parser.add_argument("--schema", type=Path, default=None,
                        help="Explicit schema file; skips the lookup.")
    args = parser.parse_args(argv)
    kind = KINDS[args.kind]
    try:
        return _validate(args)
    except RecursionError:
        _emit("invalid", [{"rule": f"{kind['format']}.depth", "path": "/",
                           "message": f"the {kind['noun']} nests too deeply to validate"}])
        return 1


def _validate(args: argparse.Namespace) -> int:
    kind = KINDS[args.kind]
    noun = kind["noun"]

    try:
        import yaml
        from jsonschema import Draft202012Validator
    except ImportError as err:  # a missing validator is never a pass
        sys.stderr.write(INSTALL_HINT.format(err=err))
        _emit("not-decidable", [], cause=f"dependencies missing: {err}")
        return 2

    try:
        text = args.declaration.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        _emit("invalid", [{"rule": f"{noun}.unreadable", "path": "/",
                           "message": f"can't read {args.declaration}: {exc}"}])
        return 1
    if len(text.encode("utf-8")) > MAX_BYTES:
        _emit("invalid", [{"rule": f"{noun}.too-large", "path": "/",
                           "message": f"{noun} exceeds {MAX_BYTES} bytes"}])
        return 1
    if kind["format"] == "json":
        try:
            doc = _load_json(text)
        except _DuplicateKey as exc:
            _emit("invalid", [{"rule": "json.duplicate-key", "path": "/",
                               "message": f"duplicate key {exc.args[0]!r} in the {noun}"}])
            return 1
        except ValueError as exc:  # JSONDecodeError is a ValueError
            entry = {"rule": "json.parse", "path": "/", "message": str(exc).splitlines()[0]}
            if isinstance(exc, json.JSONDecodeError):
                entry["line"] = exc.lineno
            _emit("invalid", [entry])
            return 1
        return _check(args, doc, _line_index(yaml, text), kind, Draft202012Validator, yaml)
    try:
        for event in yaml.parse(text, Loader=yaml.SafeLoader):
            if isinstance(event, yaml.AliasEvent):
                _emit("invalid", [{"rule": "yaml.alias", "path": "/",
                                   "line": event.start_mark.line + 1,
                                   "message": "YAML aliases aren't allowed in a declaration"}])
                return 1
        doc = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        entry = {"rule": "yaml.parse", "path": "/",
                 "message": str(exc).splitlines()[0] if str(exc) else "YAML parse error"}
        if mark is not None:
            entry["line"] = mark.line + 1
        _emit("invalid", [entry])
        return 1
    return _check(args, doc, _line_index(yaml, text), kind, Draft202012Validator, yaml)


def _check(args: argparse.Namespace, doc, index: dict[tuple, int], kind: dict,
           Draft202012Validator, yaml) -> int:
    noun = kind["noun"]
    is_declaration = kind is KINDS["declaration"]

    def conditional(doc_) -> list[dict]:
        return conditional_violations(doc_, index) if is_declaration and isinstance(doc_, dict) else []

    # ---- Pick the schema.
    if args.schema is not None:
        schema_path = args.schema
        if not schema_path.is_file():
            sys.stderr.write(f"validate_declaration: schema file {schema_path} not found\n")
            _emit("not-decidable", [], cause=f"schema file {schema_path} not found")
            return 2
    else:
        version = doc.get("schema_version") if isinstance(doc, dict) else None
        if not isinstance(version, str) or not VERSION_RE.match(version):
            violations = [_violation(
                "schema_version.unknown", ("schema_version",),
                f"schema_version {version!r} names no {noun} schema; expected a "
                "quoted string such as \"1.0\"", index)]
            violations.extend(conditional(doc))
            _emit("invalid", violations)
            return 1
        schema_path, corpus_seen = resolve_schema(version, installed_schema_dirs(), args.kind)
        if schema_path is None:
            if corpus_seen:
                violations = [_violation(
                    "schema_version.unknown", ("schema_version",),
                    f"no schema {kind['name'].format(version=version)} exists for "
                    f"schema_version {version!r}", index)]
                violations.extend(conditional(doc))
                _emit("invalid", violations)
                return 1
            cause = f"no {kind['label']} schema reachable in the installed nolte-shared plugin"
            sys.stderr.write(f"validate_declaration: {cause}; pass --schema <file>\n")
            _emit("not-decidable", [], cause=cause)
            return 2

    try:
        schema = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
    except Exception as exc:  # noqa: BLE001 - an unusable schema decides nothing
        cause = f"schema {schema_path} unusable: {str(exc).splitlines()[0]}"
        sys.stderr.write(f"validate_declaration: {cause}\n")
        _emit("not-decidable", [], cause=cause, schema=str(schema_path))
        return 2

    # ---- Schema half.
    violations: list[dict] = []
    validator = Draft202012Validator(schema)
    for err in sorted(validator.iter_errors(doc), key=lambda e: (list(map(str, e.absolute_path)), e.validator)):
        violations.append(_violation(
            f"schema.{err.validator}", list(err.absolute_path), err.message, index))

    # ---- §F conditional half (declarations only).
    violations.extend(conditional(doc))

    result = "invalid" if violations else "valid"
    _emit(result, violations, schema=str(schema_path))
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
