Worked example for validating a YAML data file against its schema using sidecar-comment association.

## Context

Repository: `nolte/project-x`
Schema file: `schemas/release-config-v1.0.schema.yaml`
Data file: `config/release.yaml` — needs to be validated against the schema above.
Association method: sidecar comment at the top of the data file.

## Steps

1. **User requests data validation**

   > "Validate `config/release.yaml` against `schemas/release-config-v1.0.schema.yaml`."

2. **Skill checks for an existing schema association**

   The skill reads `config/release.yaml` and looks for a sidecar comment:

   ```yaml
   # yaml-language-server: $schema=../schemas/release-config-v1.0.schema.yaml
   ```

   Not found → skill proposes adding the sidecar comment before validating.

3. **User approves; skill writes the association**

   ```yaml
   # yaml-language-server: $schema=../schemas/release-config-v1.0.schema.yaml
   # Refs spec/project/release-config/en.md
   releaseTag: "v1.2.0"
   draftMode: false
   targetBranch: main
   ```

   The skill shows the diff and asks for confirmation before writing.

4. **Skill runs data validation**

   Validator precedence: `task lint` → found (includes data validation step).

   ```
   $ task lint
   check-jsonschema --schemafile schemas/release-config-v1.0.schema.yaml config/release.yaml
   ok -- validation passed
   ```

5. **Skill presents result table**

   | Data file | Schema | Association | Validator | Result |
   |-----------|--------|-------------|-----------|--------|
   | `config/release.yaml` | `schemas/release-config-v1.0.schema.yaml` | sidecar comment | `task lint` (check-jsonschema) | **pass** |

6. **Failure path: missing required property**

   If `targetBranch` is absent and the schema marks it `required`:

   ```
   ValidationError: 'targetBranch' is a required property
   ```

   The skill surfaces the verbatim error and the failing property path. No
   auto-fix is applied; the user must correct the data file manually.

7. **Unassociated file handling**

   If a second file `config/hotfix.yaml` has no sidecar comment and no entry
   in `.schemas-config.yaml`, the result table shows `unassociated`. The skill
   never invents an association; it asks the user which schema applies.
