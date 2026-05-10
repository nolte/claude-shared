# Example 02: Node project with pnpm-lock.yaml

## Input prompt

"Run a CVE audit on this repo and also check the licenses against our allowlist."

## Expected behaviour

1. Detect project kind by finding `package.json` + `pnpm-lock.yaml` at the repo root (and explicitly **no** `package-lock.json` and no `yarn.lock`), classify as **Node (pnpm)**, record one Node subroot (`.`), and honour the caller's opt-in by flipping the license-audit toggle on; severity floor stays at the default `low`.
2. Probe `Taskfile.yml` for an `audit` / `deps:audit` / `security:audit` target; if none exists, fall back to direct auditor invocation. Critically, do **not** run `npm audit` against the pnpm lockfile — the per-kind table maps `pnpm-lock.yaml` to `pnpm audit --json` and the npm CLI would either ignore the lockfile or rebuild a different graph, so the only correct call here is `pnpm audit --json --prod` (add `--dev` only when the project ships dev tooling at runtime).
3. Run `pnpm audit --json` from the subroot that owns the lockfile, normalise the pnpm-shaped JSON (`advisories` keyed by id, `metadata.vulnerabilities`) into the same internal per-finding structure used by `npm audit` so the report stays uniform; record `package`, `installed_version`, `advisory_id` (GHSA / CVE), `severity`, direct-vs-transitive `path` resolved by walking pnpm's `paths` array back to a top-level `package.json` entry, `fixed_in`, and `summary_url`.
4. Run the license audit via `pnpm licenses list --long --json --prod` (preferred over `npx license-checker` because pnpm already knows the resolved graph); locate the allowlist in declared order — `.license-allowlist.txt`, then `.licenses/allowed.txt`, then a `licenses:` block in `package.json` under `tool.dependency-audit` — and if none exists, flag every non-permissive license (`GPL-*`, `AGPL-*`, `LGPL-*`, `SSPL-*`, `UNKNOWN`) as `review` rather than failing the run, per the spec's "don't invent a policy" rule.
5. Render the report with English section headings (CVE findings sorted severity-then-name, then a `## License review` block listing each `package@version: license — review reason`), and offer follow-ups without executing them: for each `fixed_in` advisory propose the matching `pnpm up <pkg>@<range>` invocation, for unfixable advisories propose adding the id to a future `audit` task wired through `pnpm audit --ignore-cves <id>`, and for `review`-flagged licenses offer to draft an initial `.license-allowlist.txt` from the licenses the user explicitly accepts.
