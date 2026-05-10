# Example 01 — Create new spec (EN-canonical + DE translation)

## Input prompt

> Lege bitte eine neue Spec an unter `spec/api/rate-limiting/`. Wir brauchen eine Vorgabe für API-Rate-Limits: pro authentifiziertem Token MUSS ein Token-Bucket mit 100 Requests/Minute durchgesetzt werden, bei Überschreitung wird HTTP 429 mit `Retry-After` zurückgegeben. Anonyme Requests bekommen 20/Minute pro IP. Topic ist `api`, Slug `rate-limiting`.

## Input files

- `spec/.spec-config.yml` (existing):

  ```yaml
  canonical_language: en
  languages: [en, de]
  spec_root: spec
  ```

- `spec/README.md` (existing index, to be regenerated)
- `spec/api/` topic folder exists; `spec/api/rate-limiting/` does NOT yet exist.
- `skills/spec/templates/spec.template.md` (existing template)

## Expected behaviour

1. Skill detects the user's language as German and replies in German for all status/confirmation messages.
2. **Duplicate check (operation 5) runs first** — `Grep` for terms like `rate`, `limit`, `throttle`, `429`, `token bucket` under `spec/`; `Read` every canonical file with >1 keyword hit; report whether `api/rate-limiting` is already covered. Assume no overlap is found.
3. Skill confirms the slug `rate-limiting` and topic `api` (both ASCII kebab-case, derived from the canonical EN title "Rate Limiting").
4. Skill drafts the **canonical EN file** at `spec/api/rate-limiting/en.md` from `templates/spec.template.md`, filling every section from the user's description. RFC 2119 keywords stay in English (`MUST`, `SHOULD`).
5. Skill drafts the **DE translation** at `spec/api/rate-limiting/de.md`, preserving heading order, requirement IDs, and bullet counts. RFC 2119 keywords are glossed in-language (e.g. `MUSS [MUST]`).
6. Both files are written **together in a single operation** — never leave the spec partially written. If either write would fail, neither is created.
7. Skill regenerates `spec/README.md` (operation 4) so the new spec appears in the index table with `Status: draft` (or whatever the canonical header declares) and `Last updated: unversioned` (file is untracked at this moment).
8. Final reply in German lists the two relative paths created plus the index update.

Skill does NOT:
- silently invent acceptance criteria the user didn't describe (marks gaps explicitly);
- create only the EN file and defer the DE translation;
- create or modify `spec/.spec-config.yml` (already exists).
