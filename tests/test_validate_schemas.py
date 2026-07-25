"""Regression tests for scripts/validate_schemas.py.

Prove the yaml-json-schema gate of spec/project/yaml-json-schema/ fails
non-zero on synthetic broken schemas (§Acceptance Criteria: key order, extra
top-level keys, missing property descriptions, meta-invalidity) and on a
synthetic invalid data file bound via sidecar comment — and passes on a
conformant one.
"""
from __future__ import annotations

import sys
import textwrap
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import validate_schemas as vs  # noqa: E402

VALID_SCHEMA = textwrap.dedent(
    """\
    $schema: https://json-schema.org/draft/2020-12/schema
    $id: https://github.com/nolte/claude-shared/blob/main/schemas/widget-v1.0.schema.yaml
    title: Widget
    description: Validates widget manifests. Refs spec/project/yaml-json-schema/.
    type: object
    required:
      - name
    additionalProperties: false
    properties:
      name:
        type: string
        description: The widget's unique name.
    examples:
      - name: sprocket
    """
)


def write_schema(root: Path, text: str, rel: str = "schemas/widget-v1.0.schema.yaml") -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def run(root: Path) -> int:
    return vs.main(["--root", str(root)])


def test_conformant_schema_passes(tmp_path):
    write_schema(tmp_path, VALID_SCHEMA)
    assert run(tmp_path) == 0


def test_empty_repo_passes(tmp_path):
    assert run(tmp_path) == 0


def test_meta_invalid_schema_fails(tmp_path):
    write_schema(tmp_path, VALID_SCHEMA.replace("type: object", "type: 42"))
    assert run(tmp_path) == 1


def test_out_of_order_keys_fail(tmp_path):
    # title before $id: legal YAML, meta-valid, but breaks §Document skeleton.
    broken = VALID_SCHEMA.replace(
        "$id: https://github.com/nolte/claude-shared/blob/main/schemas/widget-v1.0.schema.yaml\ntitle: Widget\n",
        "title: Widget\n$id: https://github.com/nolte/claude-shared/blob/main/schemas/widget-v1.0.schema.yaml\n",
    )
    write_schema(tmp_path, broken)
    assert run(tmp_path) == 1


def test_extra_top_level_key_fails(tmp_path):
    write_schema(tmp_path, VALID_SCHEMA + "x-vendor: true\n")
    assert run(tmp_path) == 1


def test_missing_property_description_fails(tmp_path):
    broken = VALID_SCHEMA.replace(
        "    description: The widget's unique name.\n", ""
    )
    write_schema(tmp_path, broken)
    assert run(tmp_path) == 1


def test_id_path_mismatch_fails(tmp_path):
    write_schema(tmp_path, VALID_SCHEMA, rel="schemas/other-v1.0.schema.yaml")
    assert run(tmp_path) == 1


def test_missing_refs_traceability_fails(tmp_path):
    broken = VALID_SCHEMA.replace(
        "Refs spec/project/yaml-json-schema/.", "No traceability here."
    )
    write_schema(tmp_path, broken)
    assert run(tmp_path) == 1


def test_snake_case_defs_fail(tmp_path):
    broken = VALID_SCHEMA.replace(
        "examples:\n  - name: sprocket\n",
        textwrap.dedent(
            """\
            $defs:
              string_list:
                type: array
                items:
                  type: string
                description: A list of strings.
            examples:
              - name: sprocket
            """
        ),
    )
    write_schema(tmp_path, broken)
    assert run(tmp_path) == 1


def test_wrong_dialect_fails(tmp_path):
    broken = VALID_SCHEMA.replace(
        "https://json-schema.org/draft/2020-12/schema",
        "http://json-schema.org/draft-07/schema#",
    )
    write_schema(tmp_path, broken)
    assert run(tmp_path) == 1


def test_invalid_example_fails(tmp_path):
    broken = VALID_SCHEMA.replace("  - name: sprocket", "  - name: 42")
    write_schema(tmp_path, broken)
    assert run(tmp_path) == 1


def test_invalid_bound_data_file_fails(tmp_path):
    write_schema(tmp_path, VALID_SCHEMA)
    data = tmp_path / "widget.yaml"
    data.write_text(
        "# yaml-language-server: $schema=schemas/widget-v1.0.schema.yaml\n"
        "name: 42\n",
        encoding="utf-8",
    )
    assert run(tmp_path) == 1


def test_valid_bound_data_file_passes(tmp_path):
    write_schema(tmp_path, VALID_SCHEMA)
    data = tmp_path / "widget.yaml"
    data.write_text(
        "# yaml-language-server: $schema=schemas/widget-v1.0.schema.yaml\n"
        "name: sprocket\n",
        encoding="utf-8",
    )
    assert run(tmp_path) == 0


def test_real_repo_is_clean():
    assert vs.main(["--root", str(Path(__file__).resolve().parents[1])]) == 0
