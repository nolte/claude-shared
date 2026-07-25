# Research — Code-level accessibility and the client trust boundary

Research date: 2026-07-25. Feeds dimensions **F8** (accessibility defects visible in code) and
**F9** (frontend security and trust boundary).

## R-A1 — The rules of ARIA use

**Confidence: verified.** Primary normative source, quoted verbatim.

W3C, *Using ARIA*:

1. "If you can use a native HTML element or attribute with the semantics and behavior you
   require already built in, instead of re-purposing an element and adding an ARIA role, state
   or property to make it accessible, then do so."
2. "Do not change native semantics, unless you really have to."
3. "All interactive ARIA controls must be usable with the keyboard."
4. "Do not use `role='presentation'` or `aria-hidden='true'` on a focusable element."

- W3C, *Using ARIA* — <https://www.w3.org/TR/using-aria/>
- MDN, *ARIA — Accessibility* (independent restatement of the same rules) —
  <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>

**Consequence:** each of the four rules maps onto a code-decidable F8 finding. Rule 1 gives
"non-semantic element used as a control"; rule 3 gives "role without the keyboard
implementation"; rule 4 gives "focusable element hidden from assistive technology".

## R-A2 — "No ARIA is better than bad ARIA", and a role is a promise

**Confidence: verified.**

The ARIA Authoring Practices Guide states that no ARIA is better than bad ARIA, because incorrect
ARIA misrepresents content to assistive technology, and that a role is a promise: verbatim,
`<div role="button">Place Order</div>` "is a promise that the author of that `<div>` has also
incorporated JavaScript that provides the keyboard interactions expected for a button."

- W3C ARIA Authoring Practices Guide, *Read Me First* —
  <https://www.w3.org/WAI/ARIA/apg/practices/read-me-first/>
- W3C, *Using ARIA* (see R-A1).

**Consequence:** F8 can classify "ARIA added without the behaviour it promises" as a defect
rather than an improvement — an important asymmetry, because such code usually *looks* more
accessible than the plain markup it replaced.

## R-A3 — `div` with a click handler is the canonical code-level accessibility defect

**Confidence: verified.**

A `div` carrying only a click handler is not focusable, exposes no role, and is not operable by
keyboard; the documented remediation is the native element (`button`, `a` with an `href`), not a
role plus a `tabindex` plus a key handler.

- MDN, *Keyboard-navigable JavaScript widgets* —
  <https://developer.mozilla.org/en-US/docs/Web/Accessibility/Guides/Keyboard-navigable_JavaScript_widgets>
- WCAG 2.2, Success Criterion 2.1.1 Keyboard —
  <https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html>

**Consequence:** F8 lists it explicitly, with the caveat that where the project runs an
accessibility linter the mechanical instances belong to the linter under the tooling-first rule.

## R-A4 — The boundary between a code-level accessibility finding and a conformance audit

**Confidence: partial.**

Accessibility work splits into a technical, code-facing part (correct elements, names, states,
focus behaviour) and an evaluation part (conformance against WCAG success criteria, contrast
measurement, assistive-technology testing with real users). Manual code review confirms that a
site *meets* the guidelines; user testing confirms that it is *usable*.

- UsableNet, *Accessibility testing guide* — <https://info.usablenet.com/accessibility-testing>
- W3C WAI, *Evaluating Web Accessibility Overview* —
  <https://www.w3.org/WAI/test-evaluate/>

**Consequence:** F8 is deliberately capped at what a reviewer can decide from the source. Contrast
ratios, conformance level, target sizes, and screen-reader experience route to
`spec/frontend/webview-ui-optimization/` §Accessibility.

## R-S1 — Frameworks escape by default; the exceptions are the review targets

**Confidence: verified.**

OWASP: modern frameworks have fewer cross-site-scripting bugs because they steer developers
toward safe defaults, but problems occur when the framework is used insecurely — naming React's
`dangerouslySetInnerHTML` without sanitising the HTML, and noting that React cannot handle
`javascript:` or `data:` URLs without specialised validation. For DOM sinks, the documented
remediation is `textContent` instead of `innerHTML`.

- OWASP, *Cross Site Scripting Prevention Cheat Sheet* —
  <https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html>
- OWASP, *DOM based XSS Prevention Cheat Sheet* —
  <https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html>

**Consequence:** F9 enumerates the sinks a reviewer can spot in the diff — HTML sinks with
non-constant input and no sanitiser, and user-controlled `href`/`src` without a scheme
allowlist — and treats them as floors that route to the security audit rather than as an
invitation to conduct that audit here.

## R-S2 — Client-side secrets and client-side authorization

**Confidence: verified.**

Anything bundled into client code is readable by the user, including build-time environment
values inlined by the bundler; access-control decisions must be enforced server-side.

- OWASP, *Secrets Management Cheat Sheet* —
  <https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html>
- OWASP Top 10, *A01:2021 Broken Access Control* (access control enforced in trusted
  server-side code) — <https://owasp.org/Top10/A01_2021-Broken_Access_Control/>

**Consequence:** F9 covers secrets in the bundle and "hidden control treated as an access
control"; the latter is the security face of the F1 trust-boundary class, and the spec must say
which dimension owns which face so a finding is not filed twice.

## R-S3 — Cross-document and cross-origin hazards visible in markup

**Confidence: verified.**

`target="_blank"` without `rel="noopener"` exposes `window.opener` to the opened document;
`postMessage` receivers must verify the sender's origin.

- MDN, *rel=noopener* — <https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Attributes/rel/noopener>
- MDN, *Window: message event / postMessage security concerns* —
  <https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage#security_concerns>

**Consequence:** both are code-decidable F9 floors.

## Currency addendum

None yet.
