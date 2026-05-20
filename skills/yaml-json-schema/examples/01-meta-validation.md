Worked example for running meta-validation on a new schema file for the first time.

## Context

Repository: `nolte/project-x`
Schema file: `schemas/release-config-v1.0.schema.yaml`
Validator available: `check-jsonschema` (installed via `pip install check-jsonschema`)
`Taskfile.yml` has a `lint` target that calls `check-jsonschema`.

## Steps

1. **User triggers meta-validation**

   > "Run meta-validation on `schemas/release-config-v1.0.schema.yaml`."

2. **Skill checks preconditions**

   - Confirms git repo: `git rev-parse --is-inside-work-tree` → OK
   - Locates spec at `spec/project/yaml-json-schema/en.md` → found
   - Checks `Taskfile.yml` for `lint` target → found, calls `check-jsonschema`
   - Validator precedence: `task lint` is available → selected

3. **Skill runs meta-validation via `task lint`**

   ```
   $ task lint
   check-jsonschema --check-metaschema schemas/release-config-v1.0.schema.yaml
   ok -- schema is valid
   ```

   Validator used: **`task lint` → `check-jsonschema --check-metaschema`**

4. **Skill presents result table**

   | File | Validator | Result |
   |------|-----------|--------|
   | `schemas/release-config-v1.0.schema.yaml` | `task lint` (check-jsonschema) | **pass** |

5. **Drift scenario: re-run after switching to `ajv`**

   If `task lint` is removed and `ajv` becomes the active validator, the result
   table will show `ajv compile --spec=draft2020` as the validator. The change
   in the validator column signals drift and prompts investigation — e.g., `ajv`
   may enforce `format` keywords that `check-jsonschema` treats as annotations.

6. **Failure path**

   If the schema contains a syntax error (e.g., `$schema` URI misspelled):

   ```
   $ task lint
   check-jsonschema --check-metaschema schemas/release-config-v1.0.schema.yaml
   FAILED: schema is not valid: ...
   ```

   The skill reports `fail` and the verbatim error output. It never silences
   the failure with `|| true` or `--no-fail`. The user must fix and re-run.
