# Example 02 — `scaffold` MkDocs in a greenfield repo

`mkdocs.yml` is absent, so the skill defaults to the `scaffold`
operation. Exercises the full greenfield skeleton: Material engine,
baseline plugins, derived `site_url`, seven nav sections, the
`nav_translations` skeleton, and symmetric per-language docs trees —
all behind per-file approval.

## Input prompt

> Set up MkDocs for this repo from scratch.

## Input files

`spec/.spec-config.yml` lists `languages: [en, de]`. No `mkdocs.yml`,
no `docs/` tree. `git remote get-url origin` resolves to
`git@github.com:nolte/example-service.git`. A `uv.lock` is present
(so `uv` is the detected package manager). No `CNAME` file.

## Expected behaviour

1. **Operation is `scaffold`** — `mkdocs.yml` is absent.
2. **`site_url` derived, not guessed.** From the `origin` coordinates
   the skill proposes `https://nolte.github.io/example-service/`
   (project-site subpath, trailing slash). It is not an
   `<owner>.github.io` repo and ships no `CNAME`, so no exception
   applies; the value is proposed for confirmation, not written blind.
3. **Skeleton proposed per file, awaiting approval:**
   - `mkdocs.yml` — Material theme, baseline plugins (`search`
     declared **explicitly**, `i18n`, `include-markdown`), the seven
     standard nav sections, and a `nav_translations` skeleton.
   - `docs/en/` **and** `docs/de/` trees scaffolded symmetrically in
     one operation — each section folder gets an `index.md` stub with
     per-page frontmatter; a partial single-language scaffold would
     break `mkdocs build --strict`.
   - Proposed dep-manifest pins plus the `uv pip install` command
     (matching the detected `uv.lock`) for the operator to run.
4. **Approval gate.** Nothing is written until the operator confirms;
   each file is a separate approval.
5. **Build verification.** After the writes, `mkdocs build --strict`
   runs; on success only the build summary line is reported. The skill
   never installs packages or commits — those stay caller follow-ups.
