# Security policy

`nolte-shared` is a Claude Code plugin. It ships Markdown, YAML, and Python glue that Claude Code and MkDocs consume locally — it is not a network service, does not expose a runtime endpoint, and does not handle user data at runtime.

This policy describes what counts as a security issue for this repository, how to report one, and what support you can expect in return.

## Supported versions

The plugin does not yet cut tagged releases — an automated release process is pending. Until then, only the current `develop` and `main` tip commits are considered supported. Fixes land forward on `develop`; no backports are issued.

## Reporting a vulnerability

- **Preferred**: use GitHub's private vulnerability reporting on this repository (Security tab → "Report a vulnerability"). That routes the report directly to the maintainer without making it public.
- **Alternative**: open a minimal GitHub issue if the problem is non-sensitive (for example a CI misconfiguration that weakens the pipeline without exposing a credential).

Please do **not** disclose vulnerabilities in public issues, discussions, or pull request descriptions.

When you report, include:

- The affected file(s) or skill / agent name.
- A reproduction or the minimum steps that demonstrate the issue.
- The impact you see (credential exposure, arbitrary code execution in a plugin consumer, unsafe default, …).

## Response expectations

Triage is best-effort and performed by a single maintainer (see `CONTRIBUTING.md`). There is no published response-time commitment. Credible reports will receive at least an acknowledgement; valid reports will receive a fix or a documented mitigation on `develop`.

## Scope

In scope for this policy:

- Skills or agents whose default behaviour would exfiltrate credentials, secrets, or repository contents to a third party.
- Hooks, workflows, or instructions in this repository that weaken the security posture of a consuming project without explicit opt-in (for example silently disabling commit signing, skipping required checks, or suppressing secret-scanning).
- Supply-chain risks introduced by this repository's own dependencies (MkDocs extensions, pre-commit hooks, pinned GitHub Actions).

Out of scope:

- The security of a downstream project that consumes this plugin. The plugin is tooling, not a guarantee; downstream release quality and security posture remain the accountability of that project's maintainers (see the "Scope & guarantees" section of `README.md`).
- Issues in Claude Code itself, the Anthropic API, or GitHub. Report those to the respective vendor.
- The security of third-party plugins loaded alongside `nolte-shared`.

## Dependency monitoring

Dependencies that ship with this plugin (docs-build toolchain, pre-commit hooks, pinned Actions versions) are watched by Renovate and the `/nolte-engineering:dependency-audit` skill we dogfood. Findings with a security impact are treated under this policy.
