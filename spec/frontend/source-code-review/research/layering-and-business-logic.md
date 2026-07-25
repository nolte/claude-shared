# Research — Layering and business logic in the client

Research date: 2026-07-25. Feeds dimensions **F1** (layering and business logic) and **F4**
(frontend domain-knowledge duplication).

## R-L1 — "Separate logic from presentation" is the recurring first item of frontend review checklists

**Confidence: verified.**

Independent checklists converge on the same three review questions: does each component have a
single responsibility, is rendering logic separated from business logic, and do dependencies
respect the declared architectural boundaries (correct layer, no cross-feature dependency, no
circular import, imports through a public API rather than a deep path).

- Feature-Sliced Design, *The Ultimate Code Review Checklist for Frontend* —
  <https://feature-sliced.design/blog/code-review-best-practices>
- Pagepro, *18 tips for a better React code review* —
  <https://pagepro.co/blog/18-tips-for-a-better-react-code-review-ts-js/>

**Consequence for the spec:** F1 must distinguish *misplaced* logic (right client, wrong layer)
from logic that must not run in the client at all. Only the first is an extraction finding.

## R-L2 — A component that renders, holds business logic, performs side effects, and owns every UI state is a named anti-pattern

**Confidence: verified.**

Named anti-patterns across sources: one component handling rendering plus business logic plus
side effects plus all UI states; calling APIs directly inside UI components instead of a
service or data-access layer; passing large data objects through several component layers
instead of small, single-purpose props.

- iCodeIt, *React Anti-Patterns* — <https://www.icodeit.com.au/react-anti-patterns>
- DevCom, *React code review checklist* — <https://devcom.com/tech-blog/react-code-review/>

**Consequence:** direct network calls inside a component are an F1 finding whose remediation
names the data-access layer, not a style preference.

## R-L3 — Server state and client state are different categories; conflating them causes duplication

**Confidence: verified.**

Client state exists only inside the application (modal visibility, form drafts, theme). Server
state comes from a backend, lives in a database, and changes independently of the application;
it needs fetching, caching, and synchronisation. Conflating the two produces architectures in
which server data is duplicated across several stores, cache invalidation becomes manual and
error-prone, and loading states scatter unpredictably. The ownership question ("who owns this
data?") is the documented decision rule.

- TanStack Query documentation, *Overview* (server state as a distinct problem class) —
  <https://tanstack.com/query/latest/docs/framework/react/overview>
- React Handbook, *State Management in React Applications* —
  <https://reacthandbook.dev/state-management>

**Consequence:** F1 covers "server state copied into a client store"; F4 covers "the same
fetching and caching logic re-implemented per component".

## R-L4 — Client-side checks are not enforcement

**Confidence: verified.**

Any decision the server must be able to trust cannot be enforced in code the user controls.
Client-side input validation improves the interaction; the server must validate independently.
The same holds for authorization: hiding a control in the UI is not an access-control measure.

- OWASP, *Input Validation Cheat Sheet* (client-side validation is for user experience; server
  side validation is the security control) —
  <https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html>
- MDN, *Client-side form validation* (explicitly: never trust data passed to the server; always
  validate on the server as well) —
  <https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Forms/Form_validation>

**Consequence:** F1 needs a distinct class for authoritative rules implemented client-side, with
the severity depending on whether the server independently enforces the same rule. When it does,
the finding is a *duplication and drift* finding (F4); when it does not, it is a *security* one
that routes to the security audit (F9).

## R-L5 — Backend-shaped work migrating into the client is an architecture smell, not a performance detail

**Confidence: partial.** Well documented as a pattern; less normatively codified than R-L4.

Symptoms named across frontend architecture writing: joining or aggregating data from several
endpoints in the client, pulling a full dataset to sort, filter, or paginate it locally, and
per-list-item request fan-out that a single endpoint should serve.

- System Design Handbook, *Frontend System Design* —
  <https://www.systemdesignhandbook.com/guides/frontend-system-design/>
- Feature-Sliced Design checklist (see R-L1) — dependency direction and layer placement.

**Consequence:** F1 lists the class and requires the finding to name the endpoint or layer change,
so it becomes actionable for a full-stack specialist rather than a complaint.

## R-L6 — Validation rules duplicated between client and server drift

**Confidence: partial.** The drift risk is broadly documented; the remediation (shared schema or
contract-generated types) is ecosystem-specific.

Consequence for the spec: F4 names client/server validation duplication explicitly, requires both
sites to be named, and requires the proposal to point at a single source of truth (a shared
schema package or types generated from the API contract) rather than "keep them in sync".

## Currency addendum

None yet.
