# Example 01 — `audit` a repo with an existing MkDocs setup

A read-only conformance check against `spec/project/mkdocs-structure/`.
`mkdocs.yml` is present, so the default apply operation would be `patch`,
but the operator explicitly asks for a read-only report first. Exercises
the eleven-group audit table and the critical missing-`site_url` finding
under multi-language i18n.

## Input prompt

> Audit our MkDocs setup against the spec — don't change anything yet.

## Input files

`spec/.spec-config.yml` lists `languages: [en, de]`. `mkdocs.yml`:

```yaml
site_name: Example Service
theme: { name: material }
plugins:
  - i18n:
      docs_structure: folder
      languages: [{locale: en, default: true}, {locale: de}]
```

No `site_url` key. `docs/en/` and `docs/de/` both exist, but
`docs/de/index.md` has no counterpart under `docs/en/`. The `search`
plugin is not declared, and `include-markdown` is absent.

## Expected behaviour

1. **Preconditions pass.** cwd is a git repo; the spec is read from the
   target repo (no plugin fallback needed); language list `[en, de]`
   resolves from `spec/.spec-config.yml`.
2. **Operation is `audit`** — read-only, no writes proposed.
3. **Findings grouped by the eleven spec areas.** Notable rows:
   - **Site identity (`site_url`)** → `missing`, and because i18n
     declares two languages, escalated to **critical** (switcher /
     `hreflang` links break on the Pages subpath).
   - **Plugin baseline** → `missing` for both the explicit `search`
     declaration (silently dropped once any plugin is listed) and
     `include-markdown`.
   - **i18n parity** → `drift`: `docs/de/index.md` has no `docs/en/`
     counterpart, a strict-build failure.
4. **No autofix.** The audit reports every finding with a one-line
   evidence snippet and routes the operator to re-run in `patch` mode
   to apply fixes per approval. Nothing is written.
