# Example 02 — Local entries that aren't yet upstream

## Input prompt

> Diff the local Vale vocab against `nolte/vale-style` and tell me what I should PR upstream.

## Input files

`.vale.ini` (repo root):

```ini
StylesPath = docs/.vale-styles
MinAlertLevel = suggestion

Packages = https://github.com/nolte/vale-style/releases/download/v0.42.0/nolte-styles.zip

[*.md]
BasedOnStyles = Vale, nolte
```

`docs/.vale-styles/config/vocabularies/project/accept.txt` (git-tracked):

```
# Project-specific terms not yet upstream
boring-cyborg
WireGuard
Tailscale
```

Upstream `nolte/vale-style@v0.42.0` vocabularies (fetched via `gh api`):

- `technical/accept.txt` does not contain `boring-cyborg`, `WireGuard`, or `Tailscale`
- `esphome/accept.txt` does not contain any of them
- `technical-de/accept.txt` does not contain any of them

`gh api repos/nolte/vale-style/releases/latest --jq .tag_name` returns `v0.42.0`.

## Expected behaviour

The skill reads `.vale.ini`, resolves `StylesPath` to `docs/.vale-styles`, and fetches the upstream vocabulary directories at `v0.42.0`. It normalises the local file (drops the `#` comment line and the blank line) and computes the diff.

The `## Duplicates to remove` section is empty (or rendered with a "_none_" placeholder). The `## Upstream PR candidates` section lists all three local entries with a best-guess target vocabulary annotation:

```
## Upstream PR candidates
docs/.vale-styles/config/vocabularies/project/accept.txt
- boring-cyborg  (suggested upstream vocab: technical)
- WireGuard  (suggested upstream vocab: technical)
- Tailscale  (suggested upstream vocab: technical)
```

The `## Health` block reports `Duplicates: 0`, `PR candidates: 3`, and confirms the pin matches the latest release.

After the report, the skill offers to draft a single PR body for `nolte/vale-style` that lists all three candidates grouped under `technical/accept.txt` with a one-line justification placeholder per entry. It waits for explicit user confirmation before drafting and does not open the upstream PR itself in this turn.
