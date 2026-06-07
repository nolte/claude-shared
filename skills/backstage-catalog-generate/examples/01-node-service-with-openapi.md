# Scenario 01 — Node service with an OpenAPI spec

## Input prompt

"Erzeuge eine catalog-info.yaml für dieses Repo." (run inside the service repo)

## Repo fixture (signals)

- `package.json` with `"name": "payments-api"`, an Express dependency → primary language Node/TypeScript, structure = service
- `git remote origin` → `git@github.com:acme/payments-api.git`
- `CODEOWNERS` → `* @acme/payments-team`
- `openapi.yaml` at repo root
- colocated `docs/` + `mkdocs.yml`

## Expected behaviour

- Emits **two** entities in one `catalog-info.yaml` at the repo root, separated by `---`:
  - a `Component` (`spec.type: service` *inferred*, `spec.lifecycle` *needs-confirm*, `spec.owner: group:default/payments-team` *inferred* from CODEOWNERS, `providesApis: [payments-api-openapi]`)
  - an `API` (`spec.type: openapi`, `spec.definition: { $text: ./openapi.yaml }`, same `owner`, `spec.lifecycle` *needs-confirm*)
- Annotations on the Component: `github.com/project-slug: acme/payments-api`, `backstage.io/source-location: url:https://github.com/acme/payments-api/`, `backstage.io/techdocs-ref: dir:.`
- Marks `spec.lifecycle` and any `spec.system` as **needs-confirm**; does not guess a system.
- Self-validates (offline `@roadiehq/backstage-entity-validator`); reports the owner reference as a claim to confirm against the target catalog.
- Authors **no** `managed-by-location` / `orphan` / `uid` / `relations` / `status`.
