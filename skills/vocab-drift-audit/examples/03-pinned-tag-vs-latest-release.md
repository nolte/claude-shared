# Example 03 — Pinned tag lags behind the latest upstream release

## Input prompt

> Run the vocab drift audit on this repo before I cut the next release.

## Input files

`.vale.ini` (repo root):

```ini
StylesPath = .vale-styles
MinAlertLevel = suggestion

Packages = https://github.com/nolte/vale-style/releases/download/v0.40.0/nolte-styles.zip

[*.md]
BasedOnStyles = Vale, nolte
```

`.vale-styles/config/vocabularies/project/accept.txt` (git-tracked):

```
ESPHome
boring-cyborg
WireGuard
```

Upstream `nolte/vale-style@v0.40.0` vocabularies (fetched via `gh api`):

- `technical/accept.txt` does not contain any of the local entries
- `esphome/accept.txt` contains `ESPHome`
- `technical-de/accept.txt` does not contain any of the local entries

`gh api repos/nolte/vale-style/releases/latest --jq .tag_name` returns `v0.43.0` (three minor releases ahead of the pin).

## Expected behaviour

The skill reads `.vale.ini`, extracts the pin (`v0.40.0`) and `StylesPath` (`.vale-styles`), and fetches the upstream vocabularies at the pinned ref — not at `latest`, even though `latest` is newer. It computes the diff against the pinned content.

The report shows one duplicate (`ESPHome` from the `esphome` upstream vocab) and two PR candidates (`boring-cyborg`, `WireGuard`). The `## Health` block flags the pin mismatch:

```
## Health
- Local vocabularies: 1 file, 3 entries total
- Upstream vocabularies at v0.40.0: 3 vocabs, <m> entries total
- Duplicates: 1
- PR candidates: 2
- Latest nolte/vale-style release: v0.43.0 (pin is behind by 3 releases)
```

After the report, the skill notes that the pin lags behind the latest release and offers — as a separate, explicitly-gated follow-up action — to bump the `Packages =` URL in `.vale.ini` to `v0.43.0`. It does not bump the pin in this turn, does not re-run the diff against `v0.43.0`, and does not modify any file without explicit user confirmation. Per the skill's hard rules, the audit against the pinned tag stands on its own; the pin bump is a deliberate user decision that may surface additional duplicates once approved.
