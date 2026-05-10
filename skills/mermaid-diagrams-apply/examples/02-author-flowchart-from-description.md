# Example 02 — Author a flowchart from a hand description

## Input prompt

> Draft a flowchart for `docs/de/architektur/request-flow.md` that shows how a browser request hits our reverse proxy, then the API, then either Postgres or Redis depending on cache hit. User-described, not derived.

## Input files

`mkdocs.yml` already conforms to the spec (`pymdownx.superfences` with the Mermaid `custom_fence` is present, `theme.name: material`, `mkdocs-static-i18n` configured with `docs_structure: folder` and languages `en`, `de`).

`docs/requirements.txt` lists `pymdown-extensions>=10`.

`docs/de/architektur/request-flow.md` exists with German prose:

```markdown
# Request Flow

Dieses Dokument beschreibt, wie ein Browser-Request durch unsere Infrastruktur fließt.
```

The user's conversation language is German.

## Expected behaviour

1. **Preconditions pass**; setup audit (operation 1) is **not** re-run because the user's request is scoped to authoring.
2. **Authoring dialogue** (operation 3, user-described mode) confirms:
   - Conceptual structure: browser → reverse proxy → API → {Postgres on miss, Redis on hit}.
   - Target file: `docs/de/architektur/request-flow.md` (exists, language is `de`).
   - Diagram type: `flowchart` — validates the type against the catalog (runtime workflow with branching → `flowchart` is correct; would propose `sequenceDiagram` if the user had emphasized actor turn-taking, but here the structure is request routing).
3. **Direction default**: `LR` (pipeline / request-routing flow), declared explicitly on the first line of the fence.
4. **Language split** is honored:
   - The lead-in sentence and any heading or bold caption use **German** (matches the hosting markdown).
   - The `<!-- diagram-source: user-described—... -->` summary uses **German**.
   - Every node identifier, node label, and edge label inside the fence is **English** (`Browser`, `Reverse Proxy`, `API`, `Postgres`, `Redis`, `cache hit`, `cache miss`).
5. **Proposed insertion** is shown to the user in full before any write. It looks roughly like:

   ````markdown
   ## Request-Pfad

   Der folgende Flowchart zeigt den Lebenszyklus eines eingehenden HTTP-Requests bis zur Datenquelle.

   <!-- diagram-source: user-described—Browser-Request über Reverse Proxy zur API; Cache-Lookup gegen Redis, Fallback auf Postgres -->
   ```mermaid
   flowchart LR
     Browser --> ReverseProxy
     ReverseProxy --> API
     API -->|cache hit| Redis
     API -->|cache miss| Postgres
   ```
   ````

6. **Writes only after explicit user approval**, into `docs/de/architektur/request-flow.md`, appending the new section without disturbing existing prose.
7. **Refuses** to emit `style`, `linkStyle`, or `classDef` with hard-coded colors; **refuses** to emit `gitGraph`; **refuses** to write the block without the `<!-- diagram-source: ... -->` marker; **refuses** to translate the in-fence labels into German even though the file is under `docs/de/`.
8. **Does not** modify any other markdown file as a side-effect, and **does not** create a pre-rendered SVG or PNG asset.
