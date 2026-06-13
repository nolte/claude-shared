# Scenario 03 — Tech Radar JSON from a tech inventory

## Input prompt

"Generiere ein Tech-Radar-JSON aus unserem Tech-Stack." (secondary output path)

## Input fixture

A short tech inventory, e.g. a `portfolio.yml` `tech_stack:` block or an operator-supplied list:
`TypeScript (adopt), Go (trial), Backstage (assess), jQuery (hold)`, grouped into quadrants Languages / Frameworks / Infrastructure / Process.

## Expected behaviour

- Emits a **`TechRadarLoaderResponse` JSON file** (e.g. `tech-radar.json`) — **not** a `catalog-info.yaml`, and **never** a catalog entity (no `apiVersion`/`kind`/`metadata`/`spec`).
- Top-level shape: `{ quadrants: [...], rings: [...], entries: [...] }`.
  - `rings`: `adopt`/`trial`/`assess`/`hold` with `id`, `name`, `color`.
  - `quadrants`: `id`/`name` per category.
  - each `entry`: `key`, `id`, `quadrant` (a quadrant id), `title`, and a `timeline` array — ring placement is expressed through a snapshot `{ date, ringId }`, **not** a direct field.
- `date` values are emitted as ISO strings a consumer can coerce to a JS `Date`.
- Targets the `@backstage-community` model; **no** reference to the deprecated `@backstage` Tech Radar package or `backstage.io/docs/features/techradar/` URLs.
- The skill states that the radar is a separate plugin, not wired to the Software Catalog.
