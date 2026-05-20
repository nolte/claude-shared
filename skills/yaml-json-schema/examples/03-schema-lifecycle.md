Worked example for revising an existing schema — a minor backward-compatible bump and a breaking major bump.

## Context

Repository: `nolte/project-x`
Existing schema: `schemas/release-config-v1.0.schema.yaml`
Scenario A: add an optional property → minor bump (`v1.1`)
Scenario B: remove a required property → major bump (`v2.0`)

## Scenario A — Minor bump (backward-compatible)

1. **User requests a schema revision**

   > "Add an optional `notifySlack` boolean property to `schemas/release-config-v1.0.schema.yaml`."

2. **Skill classifies the change**

   - `notifySlack` is not in `required` → existing data files remain valid → **minor bump**.
   - New filename: `schemas/release-config-v1.1.schema.yaml`
   - New `$id`: `https://github.com/nolte/project-x/blob/main/schemas/release-config-v1.1.schema.yaml`

3. **Skill shows the diff and asks for confirmation**

   ```yaml
   # Added to properties:
   notifySlack:
     type: boolean
     description: "When true, post a Slack notification on release. Refs spec/project/release-config/en.md"
   ```

4. **User approves; skill writes the new file alongside the old one**

   ```
   schemas/
     release-config-v1.0.schema.yaml   # unchanged
     release-config-v1.1.schema.yaml   # new
   ```

   The v1.0 file is **never edited in place** because its `$id` may be
   referenced externally.

5. **Skill identifies consumers and surfaces migration list**

   - `config/release.yaml` sidecar comment still points to `v1.0` → not broken.
   - Skill suggests updating the sidecar comment to `v1.1` as a separate
     approved edit if the user wants the new property to be validated.

6. **Skill delegates release-note entry**

   > "Delegate release-note entry to `release-notes-curate`."

---

## Scenario B — Major bump (breaking change)

1. **User requests a breaking revision**

   > "Remove `targetBranch` from `schemas/release-config-v1.0.schema.yaml` — it's now inferred."

2. **Skill classifies the change**

   - `targetBranch` is in `required` → existing data files with this property
     may fail if the property is removed from `required` and `properties` → **major bump**.
   - New filename: `schemas/release-config-v2.0.schema.yaml`
   - New `$id`: `https://github.com/nolte/project-x/blob/main/schemas/release-config-v2.0.schema.yaml`

3. **Skill shows the diff and consumer impact**

   ```
   Breaking change: 'targetBranch' removed from required and properties.
   Consumers referencing v1.0 by $id are unaffected.
   Consumers using the sidecar comment must update to v2.0 manually.
   ```

4. **User approves; skill writes `v2.0` alongside `v1.0`**

5. **Migration list surfaced**

   | Data file | Current schema | Action needed |
   |-----------|---------------|---------------|
   | `config/release.yaml` | `v1.0` | Update sidecar to `v2.0`; remove `targetBranch` key |
   | `config/hotfix.yaml` | `v1.0` | Same |

   Each migration step requires separate user confirmation.
