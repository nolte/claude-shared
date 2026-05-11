# Example 01 — Local entries that are now upstream

## Input prompt

> Audit the Vale vocabulary against `nolte/vale-style` and tell me which local entries I can retire.

## Input files

`.vale.ini` (repo root):

```ini
StylesPath = .vale-styles
MinAlertLevel = suggestion

Packages = https://github.com/nolte/vale-style/releases/download/v0.42.0/nolte-styles.zip

[*.md]
BasedOnStyles = Vale, nolte
```

`.vale-styles/config/vocabularies/project/accept.txt` (git-tracked):

```
ESPHome
MkDocs
Renovate
pyproject
Taskfile
boring-cyborg
release-drafter
WireGuard
```

Upstream `nolte/vale-style@v0.42.0` vocabularies (fetched via `gh api`):

- `technical/accept.txt` contains `MkDocs`, `Renovate`, `pyproject`, `Taskfile`, `release-drafter`
- `esphome/accept.txt` contains `ESPHome`
- `technical-de/accept.txt` does not contain any of the local entries

`gh api repos/nolte/vale-style/releases/latest --jq .tag_name` returns `v0.42.0`.

## Expected behaviour

The skill reads `.vale.ini`, extracts the pin (`v0.42.0`) and `StylesPath` (`.vale-styles`), fetches the upstream vocabulary directories at that ref, and produces a report whose `## Duplicates to remove` section lists six of the eight local entries with their matching upstream vocab annotation:

```
## Duplicates to remove
.vale-styles/config/vocabularies/project/accept.txt
- ESPHome  (also in upstream: esphome)
- MkDocs  (also in upstream: technical)
- Renovate  (also in upstream: technical)
- pyproject  (also in upstream: technical)
- Taskfile  (also in upstream: technical)
- release-drafter  (also in upstream: technical)
```

The `## Upstream PR candidates` section lists the remaining two local entries (`boring-cyborg`, `WireGuard`) that aren't yet upstream. The `## Health` block reports `Duplicates: 6`, `PR candidates: 2`, and notes that the pin matches the latest release (`v0.42.0`).

After the report, the skill offers to delete the six duplicate lines from `accept.txt` as a follow-up action and waits for explicit user confirmation. It does not modify any file in this turn and does not bump the pin (the pin is already on the latest release).
