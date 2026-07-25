#!/usr/bin/env python3
"""Validate JSON Schema files and the data they govern.

Implements the validation contract of ``spec/project/yaml-json-schema``:

- **Meta-validation** (§Validation contract MUST): every ``*.schema.yaml`` file
  in the repository is validated against the JSON Schema 2020-12 meta-schema. A
  schema that does not pass meta-validation fails the gate; there is no soft-fail
  path. Each schema's ``examples:`` are validated against the schema itself
  (§Structural skeleton MUST: every example must validate).
- **Skeleton validation** (§Document skeleton / §Identity / §References /
  §Documentation and discovery): the ten ordered top-level keys with no extras,
  the exact 2020-12 ``$schema`` URI, an ``$id`` whose ``/blob/main/`` path
  matches the file's repository-relative location, a ``description`` carrying
  the literal ``Refs spec/`` traceability string, PascalCase ``$defs`` names,
  a ``description`` on every top-level (and variant-level) property, no
  relative-path ``$ref`` targets, and ``unevaluatedProperties: false`` instead
  of ``additionalProperties: false`` on ``allOf``-composed closed shapes.
- **Data-validation** (§Validation contract MUST): every data file bound to a
  schema is validated against it. A file declares its schema with a sidecar
  ``# yaml-language-server: $schema=<path>`` comment in its first lines, or via a
  repository-level ``.schemas-config.yaml`` mapping (``glob: schema-path``).
- **No silent skip** (§Validation contract MUST NOT): if the validator
  dependencies are not installed the gate fails with an install hint rather than
  passing vacuously.

With zero schema files in the repository the gate passes cleanly, but it is live:
the moment the first ``*.schema.yaml`` lands it is meta-validated, and the moment
the first data file binds to a schema it is data-validated.

Exit codes: 0 = clean, 1 = validation failure, 2 = validator missing.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_GLOB = "**/*.schema.yaml"
SIDECAR_RE = re.compile(r"#\s*yaml-language-server:\s*\$schema=(?P<ref>\S+)")
CONFIG_NAME = ".schemas-config.yaml"
# Directories that never carry source schemas or governed data.
EXCLUDED_PARTS = {".git", "site", "node_modules", ".audits"}

INSTALL_HINT = (
    "yaml-json-schema gate: validator dependencies missing ({err}).\n"
    "Install them with:  pip install jsonschema pyyaml\n"
    "(per spec/project/yaml-json-schema/ §Validation contract: a missing "
    "validator MUST fail the gate, not skip it.)\n"
)

# §Document skeleton: the ordered top-level keys. `type` shares its slot with a
# top-level `oneOf`/`anyOf` union, and `additionalProperties` with the
# `unevaluatedProperties` form required for allOf-composed closed shapes.
SKELETON_SLOTS: dict[str, int] = {
    "$schema": 0,
    "$id": 1,
    "title": 2,
    "description": 3,
    "type": 4,
    "oneOf": 4,
    "anyOf": 4,
    "required": 5,
    "additionalProperties": 6,
    "unevaluatedProperties": 6,
    "properties": 7,
    "$defs": 8,
    "examples": 9,
}
DIALECT_URI = "https://json-schema.org/draft/2020-12/schema"
ID_PREFIX = "https://github.com/nolte/"
PASCAL_CASE_RE = re.compile(r"^[A-Z][A-Za-z0-9]*$")


def _excluded(path: Path, root: Path) -> bool:
    return any(part in EXCLUDED_PARTS for part in path.relative_to(root).parts)


def _iter_subschemas(node):
    """Yield every dict node of a schema document, depth-first."""
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _iter_subschemas(value)
    elif isinstance(node, list):
        for item in node:
            yield from _iter_subschemas(item)


def _ref_description(schema: dict, sub: dict) -> str | None:
    """A property's description, following one level of local $ref."""
    if "description" in sub:
        return sub["description"]
    ref = sub.get("$ref", "")
    if isinstance(ref, str) and ref.startswith("#/$defs/"):
        target = schema.get("$defs", {}).get(ref.rsplit("/", 1)[-1], {})
        if isinstance(target, dict):
            return target.get("description")
    return None


def check_skeleton(schema: dict, rel: Path) -> list[str]:
    """§Document skeleton, §Identity, §References, §Documentation checks."""
    problems: list[str] = []
    keys = list(schema.keys())

    # -- Extra keys and key order.
    unknown = [k for k in keys if k not in SKELETON_SLOTS]
    for key in unknown:
        problems.append(
            f"{rel}: top-level key `{key}` is outside the §Document skeleton"
        )
    slots = [SKELETON_SLOTS[k] for k in keys if k in SKELETON_SLOTS]
    if slots != sorted(slots):
        problems.append(
            f"{rel}: top-level keys out of §Document skeleton order: {keys}"
        )

    # -- Required entries and their values.
    if keys[:1] != ["$schema"] or schema.get("$schema") != DIALECT_URI:
        problems.append(
            f"{rel}: first key must be `$schema: {DIALECT_URI}` (§Dialect)"
        )
    schema_id = schema.get("$id")
    if len(keys) < 2 or keys[1] != "$id" or not isinstance(schema_id, str):
        problems.append(f"{rel}: second key must be `$id` (§Identity)")
    else:
        if not schema_id.startswith(ID_PREFIX):
            problems.append(
                f"{rel}: $id must live under {ID_PREFIX} (§Identity)"
            )
        _, sep, id_path = schema_id.partition("/blob/main/")
        if not sep or id_path != rel.as_posix():
            problems.append(
                f"{rel}: $id path `{id_path or schema_id}` does not match the "
                "file's repository-relative path (§Identity)"
            )
    if not isinstance(schema.get("title"), str) or not schema.get("title"):
        problems.append(f"{rel}: missing top-level `title` (§Document skeleton)")
    description = schema.get("description")
    if not isinstance(description, str) or "Refs spec/" not in description:
        problems.append(
            f"{rel}: top-level `description` must carry the literal "
            "`Refs spec/` traceability string (§Documentation and discovery)"
        )
    if not any(k in schema for k in ("type", "oneOf", "anyOf")):
        problems.append(
            f"{rel}: top level needs `type` or a `oneOf`/`anyOf` union "
            "(§Document skeleton)"
        )
    examples = schema.get("examples")
    if not isinstance(examples, list) or not examples:
        problems.append(
            f"{rel}: `examples` must list at least one valid example "
            "(§Document skeleton)"
        )

    # -- $defs naming and property descriptions.
    defs = schema.get("$defs", {})
    if isinstance(defs, dict):
        for def_name in defs:
            if not PASCAL_CASE_RE.match(def_name):
                problems.append(
                    f"{rel}: $defs entry `{def_name}` is not PascalCase "
                    "(§References)"
                )
    described_scopes = [("", schema)] + [
        (f"$defs/{name}/", sub)
        for name, sub in (defs.items() if isinstance(defs, dict) else [])
        if isinstance(sub, dict)
    ]
    for prefix, scope in described_scopes:
        properties = scope.get("properties", {})
        if not isinstance(properties, dict):
            continue
        for prop_name, sub in properties.items():
            if isinstance(sub, dict) and not _ref_description(schema, sub):
                problems.append(
                    f"{rel}: property `{prefix}properties/{prop_name}` carries "
                    "no description (§Property sub-schemas)"
                )

    # -- Reference rules and allOf closed-shape rule, document-wide.
    for node in _iter_subschemas(schema):
        ref = node.get("$ref")
        if isinstance(ref, str) and (
            ref.startswith("..") or "../" in ref
        ):
            problems.append(
                f"{rel}: relative-path $ref `{ref}` is forbidden (§References)"
            )
        if (
            "allOf" in node
            and node.get("additionalProperties") is False
            and "unevaluatedProperties" not in node
        ):
            problems.append(
                f"{rel}: allOf-composed schema must close its shape with "
                "`unevaluatedProperties: false`, not `additionalProperties: "
                "false` (§Document skeleton)"
            )
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=REPO_ROOT,
        help="Repository root to scan (default: this checkout).",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()

    try:
        import yaml
        from jsonschema import Draft202012Validator
        from jsonschema.exceptions import SchemaError
    except ImportError as err:  # §MUST NOT treat absence of a validator as a pass
        sys.stderr.write(INSTALL_HINT.format(err=err))
        return 2

    failures: list[str] = []
    schema_files = sorted(
        p for p in root.glob(SCHEMA_GLOB) if not _excluded(p, root)
    )

    # ---- Meta-validation: every *.schema.yaml against its 2020-12 meta-schema.
    loaded: dict[Path, dict] = {}
    for schema_path in schema_files:
        rel = schema_path.relative_to(root)
        try:
            schema = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            failures.append(f"{rel}: not parseable as YAML — {exc}")
            continue
        if not isinstance(schema, dict):
            failures.append(f"{rel}: schema document is not a mapping")
            continue
        try:
            Draft202012Validator.check_schema(schema)
        except SchemaError as exc:
            failures.append(f"{rel}: meta-validation failed — {exc.message}")
            continue
        failures.extend(check_skeleton(schema, rel))
        loaded[schema_path] = schema
        # Examples MUST validate against the schema (§Structural skeleton).
        validator = Draft202012Validator(schema)
        for i, example in enumerate(schema.get("examples", []) or []):
            errs = sorted(validator.iter_errors(example), key=lambda e: e.path)
            for err in errs:
                failures.append(
                    f"{rel}: examples[{i}] does not validate — {err.message}"
                )

    # ---- Build the data-file -> schema binding map.
    bindings: list[tuple[Path, Path]] = []  # (data_file, schema_file)

    config_path = root / CONFIG_NAME
    if config_path.exists():
        config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        for pattern, schema_ref in (config.get("mappings", {}) or {}).items():
            schema_file = (root / schema_ref).resolve()
            for data_file in root.glob(pattern):
                if not _excluded(data_file, root):
                    bindings.append((data_file, schema_file))

    # Sidecar comments on any *.yaml / *.json (excluding the schemas themselves).
    for ext in ("**/*.yaml", "**/*.yml", "**/*.json"):
        for data_file in root.glob(ext):
            if _excluded(data_file, root) or data_file.name.endswith(
                ".schema.yaml"
            ):
                continue
            try:
                head = "\n".join(
                    data_file.read_text(encoding="utf-8").splitlines()[:10]
                )
            except (UnicodeDecodeError, OSError):
                continue
            m = SIDECAR_RE.search(head)
            if not m:
                continue
            ref = m.group("ref")
            if ref.startswith(("http://", "https://")):
                # External $id URI: resolution is validator-config's job; skip.
                continue
            schema_file = (data_file.parent / ref).resolve()
            bindings.append((data_file, schema_file))

    # ---- Data-validation.
    for data_file, schema_file in bindings:
        rel_data = data_file.relative_to(root)
        if schema_file not in loaded:
            if schema_file.exists():
                # Was excluded or failed meta-validation above; surface clearly.
                failures.append(
                    f"{rel_data}: bound schema {schema_file.name} did not pass "
                    "meta-validation"
                )
            else:
                failures.append(
                    f"{rel_data}: bound schema {schema_file} does not exist"
                )
            continue
        try:
            data = yaml.safe_load(data_file.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            failures.append(f"{rel_data}: not parseable — {exc}")
            continue
        validator = Draft202012Validator(loaded[schema_file])
        for err in sorted(validator.iter_errors(data), key=lambda e: e.path):
            loc = "/".join(str(p) for p in err.path) or "<root>"
            failures.append(f"{rel_data}: {loc}: {err.message}")

    if failures:
        sys.stderr.write("yaml-json-schema gate: validation failed\n")
        for line in failures:
            sys.stderr.write(f"  - {line}\n")
        return 1

    print(
        f"yaml-json-schema gate: {len(schema_files)} schema(s) meta-validated, "
        f"{len(bindings)} data binding(s) validated — clean"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
