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

import pytest

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


def test_described_but_typeless_property_fails(tmp_path):
    # #591 / F130: the lint used to check only `description` per property, so a
    # described property with no shape keyword passed as clean.
    root = tmp_path
    text = VALID_SCHEMA.replace("    description: The widget's unique name.\n", "    description: The widget's unique name.\n", 1)
    lines = text.split("\n")
    idx = next(i for i, l in enumerate(lines) if l.strip() == "description: The widget's unique name.")
    prop_indent = len(lines[idx]) - len(lines[idx].lstrip())
    kept = [l for i, l in enumerate(lines) if not (l.strip().startswith("type:") and len(l) - len(l.lstrip()) == prop_indent and abs(i - idx) <= 3)]
    assert len(kept) == len(lines) - 1, "fixture no longer has a typed, described property to strip"
    write_schema(root, "\n".join(kept))
    assert run(root) == 1


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


def test_non_utf8_schema_is_a_failure_not_a_crash(tmp_path):
    path = tmp_path / "schemas" / "widget-v1.0.schema.yaml"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"x: \xff\n")
    assert run(tmp_path) == 1


def test_non_utf8_mapped_data_file_is_a_failure_not_a_crash(tmp_path, capsys):
    write_schema(tmp_path, VALID_SCHEMA)
    (tmp_path / ".schemas-config.yaml").write_text(
        "mappings:\n  'widgets/*.yaml': schemas/widget-v1.0.schema.yaml\n", encoding="utf-8"
    )
    (tmp_path / "widgets").mkdir()
    (tmp_path / "widgets" / "w.yaml").write_bytes(b"name: \xff\n")
    assert run(tmp_path) == 1
    captured = capsys.readouterr()
    assert "widgets/w.yaml: not parseable" in captured.out + captured.err


@pytest.mark.parametrize(
    "config",
    [b"mappings: \xff\n", b"- widgets/*.yaml\n", b"mappings:\n  - widgets/*.yaml\n", b"mappings: []\n", b'mappings: ""\n'],
)
def test_unusable_schemas_config_is_a_failure_not_a_crash(tmp_path, capsys, config):
    write_schema(tmp_path, VALID_SCHEMA)
    (tmp_path / ".schemas-config.yaml").write_bytes(config)
    assert run(tmp_path) == 1
    captured = capsys.readouterr()
    assert ".schemas-config.yaml" in captured.out + captured.err


def test_null_mappings_still_pass(tmp_path):
    write_schema(tmp_path, VALID_SCHEMA)
    (tmp_path / ".schemas-config.yaml").write_text("mappings:\n", encoding="utf-8")
    assert run(tmp_path) == 0


def test_unreadable_schema_is_a_failure_not_a_crash(tmp_path):
    path = tmp_path / "schemas" / "widget-v1.0.schema.yaml"
    path.parent.mkdir(parents=True)
    path.symlink_to(tmp_path / "missing.yaml")
    assert run(tmp_path) == 1


# --- #816: every `mappings` entry is validated before use ---------------------
# A malformed entry is a failure line naming .schemas-config.yaml and the
# pattern (exit 1), never a traceback and never a binding outside the root.

@pytest.mark.parametrize(
    "entry, needle",
    [
        ("'widgets/*.yaml': null", "widgets/*.yaml"),
        ("'widgets/*.yaml': ''", "widgets/*.yaml"),
        ("'widgets/*.yaml': 5", "widgets/*.yaml"),
        ("'widgets/*.yaml': /etc/widget.schema.yaml", "widgets/*.yaml"),
        ("'widgets/*.yaml': ../outside.schema.yaml", "widgets/*.yaml"),
        ("'/tmp/*.yaml': schemas/widget-v1.0.schema.yaml", "/tmp/*.yaml"),
        ("'../*.yaml': schemas/widget-v1.0.schema.yaml", "../*.yaml"),
        ("'widgets/../../*.yaml': schemas/widget-v1.0.schema.yaml", "widgets/../../*.yaml"),
        ("'': schemas/widget-v1.0.schema.yaml", "''"),
        ("5: schemas/widget-v1.0.schema.yaml", "5"),
        ("null: schemas/widget-v1.0.schema.yaml", "None"),
    ],
)
def test_malformed_mapping_entry_is_a_failure_naming_config_and_pattern(tmp_path, capsys, entry, needle):
    root = tmp_path / "repo"
    write_schema(root, VALID_SCHEMA)
    (root / "widgets").mkdir()
    (root / "widgets" / "w.yaml").write_text("name: sprocket\n", encoding="utf-8")
    # A file outside the root that a `..` pattern would otherwise bind.
    (tmp_path / "x.yaml").write_text("name: 5\n", encoding="utf-8")
    (root / ".schemas-config.yaml").write_text(f"mappings:\n  {entry}\n", encoding="utf-8")
    assert run(root) == 1
    captured = capsys.readouterr()
    lines = [line for line in (captured.out + captured.err).splitlines()
             if ".schemas-config.yaml" in line and needle in line]
    assert lines, captured.out + captured.err
    assert "Traceback" not in captured.err


def test_valid_mapping_entry_still_binds(tmp_path):
    """Refutation control: a conformant relative mapping keeps binding and validating."""
    write_schema(tmp_path, VALID_SCHEMA)
    (tmp_path / "widgets").mkdir()
    (tmp_path / "widgets" / "w.yaml").write_text("name: 5\n", encoding="utf-8")
    (tmp_path / ".schemas-config.yaml").write_text(
        "mappings:\n  'widgets/[!_]*.yaml': schemas/widget-v1.0.schema.yaml\n", encoding="utf-8")
    assert run(tmp_path) == 1  # the bound file is invalid: proves the binding happened
