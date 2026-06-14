# Example 03: Conveyed GPL component → deny with remediation

## Input prompt

"Run a license check on this service before we ship it."

## Input files (optional)

- `LICENSE` — MIT (outbound anchor); the project is a shipped product / SaaS, not a dev tool
- `package.json` + lockfile — declares a runtime dependency that resolves to a GPL-3.0-only library linked into the shipped service
- `Taskfile.yml` — declares `license:sbom`

## Expected behaviour

1. Read the outbound `LICENSE` (`MIT`) and set it as the anchor. Detect the trigger as a pre-release gate on a conveyed product.
2. Generate the SBOM via `task license:sbom` (per-stack for Node), then dispatch `license-check-scanner` with the SBOM path. The agent maps the runtime dependency to `GPL-3.0-only` and classifies it as strong copyleft.
3. Determine the use context per §Scope: the component is linked into and shipped with the service — it is *conveyed*, not arm's-length. Record the use-context as `conveyed`.
4. Run the compatibility check against the MIT anchor: a GPL-3.0 component conveyed into an MIT-licensed product forces the combined work under the GPL, which the permissive-leaning, partly-SaaS portfolio cannot absorb. (Note in the artifact that the FSF static=dynamic-linking position is the conservative default, not settled case law.)
5. Apply the policy gate: strong copyleft in a conveyed component is `deny` (fails automatically). Do not place it in `allow` or `review`.
6. Remediate with confirmation — exactly one of:
   - `replace`: swap the dependency for a compatibly-licensed (permissive) alternative — the preferred response for a `deny` finding;
   - `exception with rationale`: only with explicit sign-off, a named, time-bounded deny-tier override (`valid-until`, approver, one-line rationale), revisited on its `valid-until` date;
   - never silence it by editing the allowlist or reclassifying the license.
7. Persist the artifact with the `deny` finding, its `conveyed` use-context, and the chosen response; report the verdict `blocked` until the component is replaced or sits under a signed-off, time-bounded exception.
