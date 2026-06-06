#!/usr/bin/env python3
"""Validate JSON Schema files and the data they govern.

Implements the validation contract of ``spec/project/yaml-json-schema``:

- **Meta-validation** (§Validation contract MUST): every ``*.schema.yaml`` file
  in the repository is validated against the JSON Schema 2020-12 meta-schema. A
  schema that does not pass meta-validation fails the gate; there is no soft-fail
  path. Each schema's ``examples:`` are validated against the schema itself
  (§Structural skeleton MUST: every example must validate).
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


def _excluded(path: Path) -> bool:
    return any(part in EXCLUDED_PARTS for part in path.relative_to(REPO_ROOT).parts)


def main() -> int:
    try:
        import yaml
        from jsonschema import Draft202012Validator
        from jsonschema.exceptions import SchemaError, ValidationError
    except ImportError as err:  # §MUST NOT treat absence of a validator as a pass
        sys.stderr.write(INSTALL_HINT.format(err=err))
        return 2

    failures: list[str] = []
    schema_files = sorted(
        p for p in REPO_ROOT.glob(SCHEMA_GLOB) if not _excluded(p)
    )

    # ---- Meta-validation: every *.schema.yaml against its 2020-12 meta-schema.
    loaded: dict[Path, dict] = {}
    for schema_path in schema_files:
        rel = schema_path.relative_to(REPO_ROOT)
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

    config_path = REPO_ROOT / CONFIG_NAME
    if config_path.exists():
        config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        for pattern, schema_ref in (config.get("mappings", {}) or {}).items():
            schema_file = (REPO_ROOT / schema_ref).resolve()
            for data_file in REPO_ROOT.glob(pattern):
                if not _excluded(data_file):
                    bindings.append((data_file, schema_file))

    # Sidecar comments on any *.yaml / *.json (excluding the schemas themselves).
    for ext in ("**/*.yaml", "**/*.yml", "**/*.json"):
        for data_file in REPO_ROOT.glob(ext):
            if _excluded(data_file) or data_file.name.endswith(".schema.yaml"):
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
        rel_data = data_file.relative_to(REPO_ROOT)
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
