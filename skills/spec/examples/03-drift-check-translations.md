# Example 03 — Drift check across all translations

## Input prompt

> Bitte einen Drift-Check über alle Specs unter `spec/` laufen lassen. Ich habe den Verdacht, dass mindestens eine deutsche Übersetzung nicht mehr zur kanonischen Version passt — wir hatten neulich Hand-Edits direkt in `de.md`-Dateien.

## Input files

- `spec/.spec-config.yml`:

  ```yaml
  canonical_language: en
  languages: [en, de]
  spec_root: spec
  ```

- Multiple spec folders, e.g.:
  - `spec/api/rate-limiting/{en.md, de.md}` — in sync.
  - `spec/api/authentication/{en.md, de.md}` — `de.md` has an extra requirement bullet (`R-4`) that does not exist in `en.md` — direct translation edit, never lifted into canonical.
  - `spec/claude/skill-management/{en.md, de.md}` — `de.md` is missing the last acceptance-criterion checkbox; heading "## Hard rules" is present in EN but mistranslated as "## Strenge Regeln" with one fewer subsection.

## Expected behaviour

1. Skill detects German user language and replies in German.
2. Skill walks every spec folder under `spec_root` and, for each, compares each translation file against the canonical (operation 3) on three dimensions:
   - same headings in the same order;
   - same count of requirement bullets and acceptance-criteria checkboxes;
   - same requirement IDs and ordering.
3. Skill produces a per-spec drift report in German, e.g.:
   - `spec/api/rate-limiting/` — **in sync**.
   - `spec/api/authentication/de.md` — **drift**: extra requirement `R-4` not present in canonical `en.md`. Likely a direct translation edit. Options offered: (a) lift `R-4` semantically into the canonical and regenerate every translation, or (b) discard the translation edit and regenerate `de.md` from the canonical.
   - `spec/claude/skill-management/de.md` — **drift**: missing one acceptance-criterion checkbox under `## Hard rules`; heading subsection count mismatch. Same (a)/(b) options offered.
4. For each drift, the skill **negotiates the resolution interactively** — does not silently overwrite. If the user picks (a) for one spec and (b) for another, the skill applies each choice independently.
5. After all chosen resolutions are applied, the skill re-runs the drift check on the affected specs to verify zero remaining drift, and regenerates `spec/README.md` so `Last updated` reflects the new git timestamps.
6. Final report in German confirms which specs are now in sync and which still need user input (e.g. user deferred a decision).

Skill does NOT:
- auto-apply resolution (a) or (b) without asking — the negotiation IS the load-bearing flow that justifies this being a skill, not an agent;
- declare the drift check "passed" while any spec has unresolved mismatches;
- modify `spec/.spec-config.yml`.
