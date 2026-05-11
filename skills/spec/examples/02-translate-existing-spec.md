# Example 02 — Sync DE translation after canonical EN update

## Input prompt

> Ich habe gerade `spec/api/rate-limiting/en.md` erweitert: neue Anforderung, dass Burst-Traffic bis zum doppelten Limit für 10 Sekunden toleriert wird, danach greift der Bucket. Bring die deutsche Übersetzung wieder in Sync.

## Input files

- `spec/.spec-config.yml`:

  ```yaml
  canonical_language: en
  languages: [en, de]
  spec_root: spec
  ```

- `spec/api/rate-limiting/en.md` — **canonical, just edited by the user**, now contains a new requirement bullet (e.g. `R-3: Burst traffic up to 2× the limit MUST be tolerated for 10 s before the bucket enforces.`) and a corresponding acceptance-criterion checkbox.
- `spec/api/rate-limiting/de.md` — **stale**, reflects the previous version without the burst-tolerance requirement.

## Expected behaviour

1. Skill detects German user language and replies in German.
2. Skill confirms the canonical was edited (per operation 2: "the canonical version is the only source of truth"). No warning fires because the edit landed in the canonical EN file, not in the translation.
3. Skill `Read`s the current `en.md` to extract the full updated structure: heading order, requirement IDs (`R-1`, `R-2`, `R-3`, …), acceptance-criteria checkboxes, RFC 2119 keywords.
4. Skill `Read`s the current `de.md` to identify the drift: missing `R-3`, missing matching acceptance-criterion, possibly shifted bullet counts.
5. Skill **regenerates `de.md` from the canonical** rather than patching in place — guarantees structural parity. The regeneration preserves:
   - same heading order and wording (translated);
   - same requirement IDs (`R-3` keeps its ID in the DE file);
   - same count of requirement bullets and acceptance-criteria checkboxes;
   - RFC 2119 glossed in-language (`MUSS [MUST]`, `SOLLTE [SHOULD]`).
6. Skill writes `spec/api/rate-limiting/de.md` and reports the diff in German: which sections changed, which new requirement was added, that structural parity is now restored.
7. Skill regenerates `spec/README.md` if `Last updated` for the canonical changed (it did — git timestamp on `en.md` is fresh).

Skill does NOT:
- ask the user to manually translate the new bullet — the skill owns the translation;
- patch only the new bullet into `de.md` without verifying the rest of the file is still in structural sync;
- touch `en.md` (canonical is already authoritative).
