# Example 03 — `patch` a single missing-`site_url` finding additively

`mkdocs.yml` is present and mostly conformant, but a prior audit
surfaced one critical finding: `site_url` is absent under a
two-language i18n config. Exercises the additive `patch` operation —
one finding, one proposed edit, one approval — plus the derivation
rule's org-pages exception and the post-write strict build.

## Input prompt

> Fix the missing site_url the audit flagged.

## Input files

`spec/.spec-config.yml` lists `languages: [en, de]`. `mkdocs.yml` has
Material, the full plugin baseline, and the seven nav sections, but no
`site_url`. The repo root holds a `CNAME` file containing
`docs.example.dev`. The rest of the setup passed the earlier audit.

## Expected behaviour

1. **Operation is `patch`** — `mkdocs.yml` present; only the one
   flagged finding is in scope. Patch mode is additive, never
   destructive; untouched keys are carried over verbatim.
2. **Derivation honours the `CNAME` exception.** A bare coordinate
   derivation would propose `https://nolte.github.io/<repo>/`, but the
   `CNAME` file signals a custom domain, so the skill proposes
   `site_url: https://docs.example.dev/` instead — and surfaces *why*
   (custom-domain signal beats the github.io path).
3. **Single-finding approval gate.** The skill shows the one-line
   `site_url:` insertion and its spec citation, then waits. It does not
   bundle any other change; unrelated drift would be its own approval.
4. **Post-write strict build.** After the operator approves and the key
   is written, `mkdocs build --strict` re-runs to confirm the i18n
   switcher links now resolve; the summary line is reported.
5. **Caller follow-ups only.** The skill commits nothing and opens no
   PR — it hands those back to `pull-request-create`.
