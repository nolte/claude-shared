#!/usr/bin/env python3
"""Validate an image-declaration.yaml deterministically, failing closed.

One validator decides both halves of the declaration contract of
``spec/project/linux-image-best-practices/`` §A and §F:

- the JSON Schema ``schemas/image-declaration-v<schema_version>.schema.yaml``
  (Draft 2020-12), picked from the declaration's own ``schema_version`` so a
  later schema version needs no new code path;
- the three §F conditional rules the schema deliberately leaves out:
  ``field-updated`` requires the ``update`` block and ``health.failure_switch``,
  and ``reflash-only`` forbids the ``update`` block.

Schema lookup order: ``--schema <file>``; else ``schemas/`` under
``--repo-root`` (default: the current directory); else the installed
``nolte-shared`` plugin's ``schemas/`` tree, found next to this plugin (the
monorepo layout and the marketplace cache layout).

Output: one JSON object on stdout,
``{"result": "valid|invalid|not-decidable", "violations": [...], ...}``, where
each violation carries a stable ``rule`` identifier (``schema.<keyword>``,
``conditional.<rule>``, ``schema_version.unknown``, ``yaml.parse``,
``declaration.unreadable``), the JSON-pointer ``path``, a ``message``, and the
1-based ``line`` in the declaration when it's known.

Exit codes (mirroring scripts/validate_schemas.py):
  0  valid
  1  invalid
  2  not decidable: jsonschema/PyYAML missing (install hint on stderr) or no
     image-declaration schema reachable. Never reported as valid
     (spec/project/yaml-json-schema/ §Validation contract).

Usage:
  python3 "${CLAUDE_PLUGIN_ROOT}/skills/linux-image-audit/scripts/validate_declaration.py" \\
      images/edge-appliance/image-declaration.yaml [--repo-root .] [--schema FILE]
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
    "The declaration check stays not-decidable until they're installed; it is "
    "never reported as passing (spec/project/yaml-json-schema/ §Validation contract).\n"
)
SCHEMA_NAME = "image-declaration-v{version}.schema.yaml"
SCHEMA_GLOB = "image-declaration-v*.schema.yaml"
VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+$")

# scripts/ -> linux-image-audit/ -> skills/ -> <nolte-linux plugin root>
PLUGIN_ROOT = Path(__file__).resolve().parents[3]

RULE_UPDATE = "conditional.field-updated-requires-update"
RULE_FAILURE_SWITCH = "conditional.field-updated-requires-failure-switch"
RULE_REFLASH = "conditional.reflash-only-forbids-update"


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


def resolve_schema(version: str, repo_root: Path, extra_dirs: list[Path]) -> tuple[Path | None, bool]:
    """Return (schema file, any schema corpus seen) for ``version``."""
    corpus_seen = False
    for directory in [repo_root / "schemas", *extra_dirs]:
        if not directory.is_dir():
            continue
        if any(directory.glob(SCHEMA_GLOB)):
            corpus_seen = True
        candidate = directory / SCHEMA_NAME.format(version=version)
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate an image-declaration.yaml.")
    parser.add_argument("declaration", type=Path, help="Path of the image-declaration.yaml.")
    parser.add_argument("--schema", type=Path, default=None,
                        help="Explicit schema file; skips the lookup.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(),
                        help="Audited repository root whose schemas/ is searched first.")
    args = parser.parse_args(argv)

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
        _emit("invalid", [{"rule": "declaration.unreadable", "path": "/",
                           "message": f"can't read {args.declaration}: {exc}"}])
        return 1
    try:
        doc = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        entry = {"rule": "yaml.parse", "path": "/",
                 "message": str(exc).splitlines()[0] if str(exc) else "YAML parse error"}
        if mark is not None:
            entry["line"] = mark.line + 1
        _emit("invalid", [entry])
        return 1
    index = _line_index(yaml, text)

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
                f"schema_version {version!r} names no declaration schema; expected a "
                "quoted string such as \"1.0\"", index)]
            if isinstance(doc, dict):
                violations.extend(conditional_violations(doc, index))
            _emit("invalid", violations)
            return 1
        schema_path, corpus_seen = resolve_schema(
            version, args.repo_root.resolve(), installed_schema_dirs())
        if schema_path is None:
            if corpus_seen:
                violations = [_violation(
                    "schema_version.unknown", ("schema_version",),
                    f"no schema {SCHEMA_NAME.format(version=version)} exists for "
                    f"schema_version {version!r}", index)]
                violations.extend(conditional_violations(doc, index))
                _emit("invalid", violations)
                return 1
            cause = "no image-declaration schema reachable (repository schemas/ or the installed nolte-shared plugin)"
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

    # ---- §F conditional half.
    if isinstance(doc, dict):
        violations.extend(conditional_violations(doc, index))

    result = "invalid" if violations else "valid"
    _emit(result, violations, schema=str(schema_path))
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
