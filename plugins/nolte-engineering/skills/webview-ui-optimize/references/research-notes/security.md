# Security & Sandboxing — Research notes for the webview-ui stack

## Contents

- [Methodology](#methodology)
- [Best practices](#best-practices)
- [Anti-patterns to avoid](#anti-patterns-to-avoid)
- [Open questions / topics needing follow-up](#open-questions--topics-needing-follow-up)
- [Spec-input summary](#spec-input-summary)
- [Currency addendum (2026-07-24)](#currency-addendum-2026-07-24)

Scope: Plain HTML/CSS, React 19, Vite 8, MUI v9, Redux Toolkit + react-redux,
React Router v7, axios, react-hook-form + zod, notistack, react-i18next,
qrcode.react, nginx (`nginx-security-headers.inc`). Browser-context token-bearer
auth over HTTPS.

## Methodology

- Two-source rule: every practice cites at least two independent authoritative
  sources (OWASP, MDN, W3C/WHATWG, official library docs, web.dev, Mozilla
  Observatory). Single-source claims are marked `unverified`.
- Confidence levels: `high` (two or more first-party / standards sources),
  `medium` (one first-party source plus a strong corroborating secondary),
  `unverified` (single source or weak corroboration — kept for traceability,
  must be re-checked before normative use).
- Sources are linked directly; blogs (Medium / dev.to / personal posts) are
  excluded from the load-bearing slot but may appear as supporting examples.

---

## Best practices

### 1. Deploy a strict, nonce-based CSP with `'strict-dynamic'`

- **Practice:** Serve a strict Content Security Policy whose `script-src`
  combines a per-response cryptographic nonce with `'strict-dynamic'`, e.g.
  `script-src 'nonce-{random}' 'strict-dynamic'; object-src 'none'; base-uri 'none'; require-trusted-types-for 'script'`.
  Avoid host allowlists — they are bypassable and brittle.
- **Why:** Strict CSP defends against the largest class of XSS by refusing
  any script the server did not nonce. `'strict-dynamic'` lets bundler-emitted
  loaders dynamically inject further scripts they trust, so React 19 + Vite 8
  chunk-splitting keeps working without enumerating every chunk URL.
- **Applies to:** nginx `add_header Content-Security-Policy`, Vite asset
  pipeline (nonce injection into the rendered `index.html`).
- **Sources:**
  - <https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html>
  - <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy>
  - <https://web.dev/articles/strict-csp>
- **Confidence:** high.

### 2. Forbid `'unsafe-inline'` and `'unsafe-eval'` in `script-src` and `style-src`

- **Practice:** Never include `'unsafe-inline'` or `'unsafe-eval'` in
  `script-src`. For styles, prefer nonces/hashes over `'unsafe-inline'`; if
  MUI emotion-injected styles force an allowance, use a per-response nonce
  bound to emotion's `cache.nonce`.
- **Why:** Both keywords defeat CSP's XSS-mitigation properties.
  `unsafe-eval` is what makes `eval`, `Function()`, and `setTimeout(string)`
  callable; modern React, Redux Toolkit and Vite output do not require it.
- **Applies to:** nginx CSP header, Vite production build flags (`build.minify`
  defaults are safe; avoid plugins that emit `new Function(...)`).
- **Sources:**
  - <https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html>
  - <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/script-src>
- **Confidence:** high.

### 3. Enable Trusted Types via `require-trusted-types-for 'script'`

- **Practice:** Send `Content-Security-Policy: require-trusted-types-for 'script'; trusted-types default dompurify#html;`.
  Wrap every `dangerouslySetInnerHTML` (or DOM-injection) consumer in a named
  Trusted Types policy that sanitises via DOMPurify before yielding a
  `TrustedHTML`.
- **Why:** Trusted Types make DOM-XSS sinks (`innerHTML`, `outerHTML`,
  `document.write`, `Element.insertAdjacentHTML`) refuse plain strings,
  shrinking the auditable XSS surface to the named policies. Chrome ships
  enforcement; Firefox/Safari ignore the directive without breaking pages.
- **Applies to:** React 19 `dangerouslySetInnerHTML`, MUI components that
  accept HTML strings, react-i18next when `interpolation.escapeValue` is
  intentionally turned off.
- **Sources:**
  - <https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/require-trusted-types-for>
  - <https://developer.mozilla.org/en-US/docs/Web/API/Trusted_Types_API>
  - <https://w3c.github.io/trusted-types/dist/spec/>
- **Confidence:** high.

### 4. Pin `frame-ancestors 'none'` (or `'self'`) alongside `X-Frame-Options: DENY`

- **Practice:** Prefer CSP `frame-ancestors 'none'` when the app must never be
  framed (the default for a token-bearer SPA). Keep `X-Frame-Options: DENY`
  as a belt-and-braces fallback for the small set of older crawlers/clients
  that ignore CSP.
- **Why:** `frame-ancestors` supersedes `X-Frame-Options` per CSP Level 2, but
  legacy software still honours only XFO; serving both is the OWASP-recommended
  posture. Prevents clickjacking and UI-redress attacks.
- **Applies to:** nginx `nginx-security-headers.inc`.
- **Sources:**
  - <https://cheatsheetseries.owasp.org/cheatsheets/Clickjacking_Defense_Cheat_Sheet.html>
  - <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options>
- **Confidence:** high.

### 5. Send `Referrer-Policy: strict-origin-when-cross-origin` (or stricter)

- **Practice:** Set `Referrer-Policy: strict-origin-when-cross-origin` as the
  app default; downgrade to `no-referrer` for routes that carry tokens in the
  URL (auth callback, password reset).
- **Why:** Prevents leaking full request URLs (which may contain tokens,
  identifiers, or capability URLs) to third-party hosts and to HTTP downgrade
  targets. `strict-origin-when-cross-origin` is the modern browser default
  but should be set explicitly so the policy is auditable.
- **Applies to:** nginx headers, `<meta name="referrer">` is a fallback only.
- **Sources:**
  - <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy>
  - <https://www.w3.org/TR/referrer-policy/>
- **Confidence:** high.

### 6. Send `X-Content-Type-Options: nosniff`

- **Practice:** Always send `X-Content-Type-Options: nosniff` from nginx.
  Verify that the build pipeline emits the correct `Content-Type` for every
  asset (`application/javascript` for `.js`, `text/css` for `.css`).
- **Why:** Without `nosniff`, browsers may MIME-sniff a `text/plain` upload as
  HTML or JavaScript and execute it in the page's origin. With `nosniff`,
  script/style requests are also strictly typed: a script served with a
  non-JS MIME type is refused, blocking a class of XSS-via-upload attacks.
- **Applies to:** nginx, asset-pipeline content-type configuration.
- **Sources:**
  - <https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/X-Content-Type-Options>
  - <https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html>
- **Confidence:** high.

### 7. Send `Strict-Transport-Security` with at least one year and `includeSubDomains`; preload only when the rollout is irreversible

- **Practice:** Send `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload`
  once the operator is certain that every subdomain can serve HTTPS
  indefinitely. Until then, start with `max-age=31536000; includeSubDomains`
  and omit `preload`. The site is then a candidate for the HSTS preload list.
- **Why:** HSTS prevents protocol-downgrade and SSL-strip MITM. Preload makes
  the policy effective on the first request, but a wrong preload entry is
  effectively un-reversible — browsers ship the list compiled in.
- **Applies to:** nginx headers, HTTPS terminator.
- **Sources:**
  - <https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Strict_Transport_Security_Cheat_Sheet.html>
  - <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security>
  - <https://hstspreload.org/>
- **Confidence:** high.

### 8. Send `Cross-Origin-Opener-Policy: same-origin` and `Cross-Origin-Resource-Policy: same-origin`

- **Practice:** Send `Cross-Origin-Opener-Policy: same-origin` (or
  `same-origin-allow-popups` when the SPA opens trusted OAuth popups) and
  `Cross-Origin-Resource-Policy: same-origin` for app-owned assets. Only add
  `Cross-Origin-Embedder-Policy: require-corp` if the app actually needs
  cross-origin isolation (SharedArrayBuffer, high-resolution timers, WASM
  threads); COEP is opt-in because it breaks naïvely embedded resources.
- **Why:** COOP isolates the top-level window from cross-origin openers,
  closing the `window.opener` and Spectre-class side-channel attack surface
  even without COEP. CORP prevents app-owned resources from being embedded by
  attacker-controlled origins.
- **Applies to:** nginx headers.
- **Sources:**
  - <https://web.dev/articles/coop-coep>
  - <https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cross-Origin-Opener-Policy>
  - <https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cross-Origin-Resource-Policy>
- **Confidence:** high.

### 9. Lock down `Permissions-Policy` to an explicit allowlist

- **Practice:** Send `Permissions-Policy` with every powerful feature
  disabled by default and only the features the app demonstrably uses
  opted in to `'self'`. Example:
  `Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=(), serial=(), bluetooth=(), accelerometer=(), gyroscope=(), magnetometer=(), midi=(), fullscreen=(self)`.
- **Why:** Reduces the blast radius of an XSS or compromised third-party
  script — a stolen execution context cannot silently turn on the camera or
  read geolocation if the policy denies it.
- **Applies to:** nginx headers, `<iframe allow>` attributes for any embedded
  content.
- **Sources:**
  - <https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Permissions-Policy>
  - <https://w3c.github.io/webappsec-permissions-policy/>
- **Confidence:** high.

### 10. Use Subresource Integrity for every third-party-served asset (and prefer self-hosting)

- **Practice:** If a CDN asset is genuinely necessary, attach an SRI hash
  (`integrity="sha384-..." crossorigin="anonymous"`) to every `<script>` and
  `<link rel="stylesheet">` from a foreign origin. The default posture in
  this stack is to self-host all assets via Vite so SRI is moot.
- **Why:** SRI gives the browser a cryptographic guarantee that the bytes it
  executes match what the operator vetted, blocking a CDN compromise from
  pivoting into the app's origin.
- **Applies to:** any `index.html`-level CDN reference, font CDNs, MUI icon
  CDNs.
- **Sources:**
  - <https://developer.mozilla.org/en-US/docs/Web/Security/Subresource_Integrity>
  - <https://www.w3.org/TR/SRI/>
- **Confidence:** high.

### 11. Default React rendering is safe — quarantine `dangerouslySetInnerHTML`

- **Practice:** Treat `dangerouslySetInnerHTML` as a privileged escape hatch.
  Allow it only in a small, code-owned set of components, always wrapped in a
  Trusted Types policy that pipes input through DOMPurify with an explicit
  allow-list of tags and attributes. Lint-forbid the prop everywhere else
  (e.g. `react/no-danger`).
- **Why:** React 19's JSX runtime escapes interpolated children by default,
  so the surface area for stored / reflected XSS is limited to
  `dangerouslySetInnerHTML`, refs that touch `innerHTML`, and `href` / `src`
  attributes set from user-controlled strings.
- **Applies to:** React component code, ESLint config, code-review checklist.
- **Sources:**
  - <https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html>
  - <https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html>
  - <https://react.dev/reference/react-dom/components/common#dangerously-setting-the-inner-html>
- **Confidence:** high.

### 12. Validate untrusted URLs before assigning to `href`, `src`, or `navigate(...)`

- **Practice:** Before rendering an `<a href={url}>`, `<MUI Link href={url}>`,
  or calling React Router `navigate(url)` / `redirect(url)` with a
  user-controlled value, parse the URL and reject `javascript:`, `data:`,
  `vbscript:`, and absolute URLs whose origin is not on an allowlist. For
  internal routing, prefer passing route-relative paths.
- **Why:** `href="javascript:..."` is a classic DOM-XSS sink; arbitrary
  absolute URLs enable open-redirect phishing (especially on login-callback
  routes that read `?returnTo=`).
- **Applies to:** React Router v7 navigation helpers, MUI `Link`, any
  user-driven redirect (deep links, OAuth `state`/`returnTo`).
- **Sources:**
  - <https://cheatsheetseries.owasp.org/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.html>
  - <https://reactrouter.com/api/utils/redirect>
  - <https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/XSS>
- **Confidence:** high.

### 13. Never store auth tokens in `localStorage` / `sessionStorage` — prefer `HttpOnly; Secure; SameSite=Strict` cookies or in-memory + silent refresh

- **Practice:** Keep bearer tokens out of `localStorage`, `sessionStorage`,
  IndexedDB and Redux state that is persisted (redux-persist). Use an
  HttpOnly + Secure + SameSite cookie issued by the auth backend, OR keep
  the access token in JavaScript memory only and refresh it via a
  same-origin cookie-protected refresh endpoint.
- **Why:** Any XSS gives the attacker `document.cookie` access only if cookies
  are not HttpOnly. Web Storage values are always JavaScript-readable, so a
  single XSS exfiltrates every token. OWASP explicitly warns against the
  Web-Storage-for-tokens pattern.
- **Applies to:** axios interceptors, Redux Toolkit auth slice, redux-persist
  whitelist/blacklist config.
- **Sources:**
  - <https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html>
  - <https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html>
- **Confidence:** high.

### 14. Restrict `redux-persist` to non-sensitive UI state

- **Practice:** Configure `redux-persist` with an explicit `whitelist` of
  slices that hold UI preferences (theme, language, table column order) only.
  Blacklist or omit any slice that stores tokens, PII, or per-user secrets.
  If encryption-at-rest in storage is required, never embed the encryption
  key in the client bundle.
- **Why:** redux-persist writes the whitelisted Redux state into Web Storage,
  inheriting all the XSS exfiltration risks of localStorage; encrypting with
  a hard-coded client-side key offers no protection because the key ships in
  the bundle.
- **Applies to:** Redux Toolkit + react-redux store configuration.
- **Sources:**
  - <https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html>
  - <https://github.com/rt2zz/redux-persist#nested-persists> (official docs:
    whitelist/blacklist API)
- **Confidence:** medium (second source is the library's own README, which is
  authoritative for the API but not independent for the security claim; the
  XSS-storage risk is corroborated by OWASP).

### 15. Treat Vite `VITE_*` env vars as public; keep secrets out of the client bundle

- **Practice:** Only place values intended for the browser bundle behind the
  `VITE_` prefix. Forbid pushing API keys, signing secrets, OAuth client
  secrets, or backend URLs that bypass the BFF into `.env*` files with the
  `VITE_` prefix. Never override `envPrefix` to an empty string. Audit the
  built bundle (e.g. `grep -R 'VITE_' dist/`) for leaked values in CI.
- **Why:** `import.meta.env.VITE_*` values are statically inlined at build
  time and ship to every browser. Treating them as secret has led to
  publicly disclosed AWS keys and CI tokens in real incidents.
- **Applies to:** Vite build config, `.env.*` hygiene, CI bundle scan.
- **Sources:**
  - <https://vite.dev/guide/env-and-mode>
  - <https://owasp.org/Top10/A02_2021-Cryptographic_Failures/>
- **Confidence:** high.

### 16. Suppress public source maps in production (or upload privately to error-tracking)

- **Practice:** Set Vite `build.sourcemap` to `false` for production
  artefacts that ship to the browser. If error tracking (Sentry / Datadog)
  requires symbolication, use `'hidden'` and upload the maps to the tracking
  backend out-of-band — never serve `*.js.map` from nginx publicly. Block
  `*.map` at the nginx layer as defence-in-depth.
- **Why:** Public source maps reverse the minifier and reveal the full
  source tree, comments, internal endpoints, and sometimes hard-coded
  identifiers. They make every other defence easier to bypass for an attacker.
- **Applies to:** `vite.config.ts`, nginx location rules.
- **Sources:**
  - <https://vite.dev/config/build-options#build-sourcemap>
  - <https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/01-Information_Gathering/05-Review_Webpage_Content_for_Information_Leakage>
- **Confidence:** high.

### 17. Add `rel="noopener noreferrer"` to every external `target="_blank"` link

- **Practice:** Author external links as
  `<a href="…" target="_blank" rel="noopener noreferrer">…</a>`. For MUI
  `<Link>` / `<Button component="a">`, pass `rel` explicitly; rely on the
  same rule for any programmatically generated link. Lint-enforce via
  `react/jsx-no-target-blank`.
- **Why:** Without `noopener`, the opened page receives a `window.opener`
  reference and can navigate the originating tab (reverse tabnabbing).
  `noreferrer` additionally strips the `Referer` header. Modern browsers
  imply `noopener` for `target="_blank"` since 2021, but older browsers
  and embedded webviews do not — the explicit attribute is still the
  defensive default.
- **Applies to:** All anchor tags, MUI Link components, any code that calls
  `window.open(...)` (use the `noopener,noreferrer` features string).
- **Sources:**
  - <https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Attributes/rel/noopener>
  - <https://owasp.org/www-community/attacks/Reverse_Tabnabbing>
- **Confidence:** high.

### 18. Render translation values as data — use `Trans` with element placeholders, never inline HTML

- **Practice:** Keep `react-i18next`'s default `interpolation.escapeValue:
  true`. For translations that need markup (a link, bold, an icon), use the
  `<Trans>` component with explicit React-element children rather than
  embedding HTML in the translation string. Forbid `{{value}}` insertions
  into `dangerouslySetInnerHTML` and forbid `escapeValue: false` globally.
- **Why:** Disabling i18next escaping or letting translations contain raw
  HTML makes every translator (or a compromised translation pipeline) a
  potential XSS author. The `<Trans>` component lets the translation
  describe structure without escaping JSX children.
- **Applies to:** i18next config, every Trans usage, translation file
  review checklist.
- **Sources:**
  - <https://www.i18next.com/translation-function/interpolation>
  - <https://react.i18next.com/latest/trans-component>
  - <https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html>
- **Confidence:** high.

### 19. Pass plain strings to notistack; never use `dangerouslySetInnerHTML` in custom snackbars

- **Practice:** Call `enqueueSnackbar(message, ...)` with strings (or React
  elements you construct yourself, not user-supplied HTML). Custom variant
  components must render the message via JSX children, not via
  `dangerouslySetInnerHTML`. Treat the `message` argument as untrusted by
  default.
- **Why:** notistack delegates rendering to React, which escapes children;
  the vulnerability surface is custom variants that bypass JSX escaping.
- **Applies to:** notistack provider + custom variant components.
- **Sources:**
  - <https://notistack.com/api-reference>
  - <https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html>
- **Confidence:** medium (notistack docs cover the rendering contract; OWASP
  covers the general React-children rule. No notistack-specific CVE/security
  advisory was located.)

### 20. Centralise axios in a single instance with `baseURL`, explicit `timeout`, and an auth interceptor

- **Practice:** Create one axios instance per backend, configure
  `baseURL`, `timeout` (e.g. 10–30 s), and a request interceptor that
  injects the in-memory token. Set `withCredentials` only on the
  endpoints that truly need to send cookies (refresh-token endpoint).
  Configure `xsrfCookieName` / `xsrfHeaderName` only if the backend
  expects the double-submit pattern; otherwise leave the defaults and rely
  on `SameSite` + the `Authorization` header.
- **Why:** Without a default `timeout`, axios hangs forever on a stalled
  socket, blocking UI threads and enabling slow-loris-style local DoS.
  Centralising `baseURL` prevents leaking the API origin via accidental
  absolute URLs, and a single auth interceptor avoids per-call mistakes.
- **Applies to:** `src/api/client.ts` (or equivalent), every axios call.
- **Sources:**
  - <https://axios-http.com/docs/req_config>
  - <https://axios-http.com/docs/instance>
- **Confidence:** high.

### 21. Mirror every Zod input schema server-side — client validation is UX, not security

- **Practice:** The `react-hook-form` + `zod` schemas guard the UI. The
  backend must independently validate every field against an equivalent
  schema (positive validation, allow-list, length bounds, type bounds).
  Surface backend validation errors back into the form via `setError`.
- **Why:** Client validation is bypassable (browser dev tools, scripted
  requests). OWASP ASVS V5 / OWASP Top 10:2021 A04 (Insecure Design) and
  A03 (Injection) require server-side validation as the authoritative gate.
- **Applies to:** Both layers; this spec is the frontend half of the rule.
- **Sources:**
  - <https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html>
  - <https://owasp.org/www-project-application-security-verification-standard/>
- **Confidence:** high.

### 22. Treat QR-code payloads as data — validate length and scheme before encoding

- **Practice:** Before passing a user-controlled string into `qrcode.react`,
  enforce a max length (≤ 2953 chars per QR spec, often much tighter for
  scannability) and reject payloads whose URL scheme is not on an
  allow-list (`https:`, `mailto:`, app-specific schemes). The QR library
  itself does not display HTML, but downstream scanners follow whatever
  URL the QR encodes.
- **Why:** A QR code is a redirect primitive. Encoding `javascript:`,
  `intent:` malicious deep-links, or oversize payloads creates phishing and
  client-side DoS risk for the scanner's device.
- **Applies to:** Any feature that turns user input into a QR.
- **Sources:**
  - <https://www.qrcode.com/en/about/standards.html>
  - <https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html>
- **Confidence:** medium (the size limit is from the QR spec; the
  scheme-allow-list rule is the standard URL-validation pattern applied to
  QR payloads).

### 23. When iframes are unavoidable, use a maximally restrictive `sandbox`

- **Practice:** If the SPA must embed third-party content (payment iframe,
  preview), set `<iframe sandbox="…">` with the smallest token set required
  and never combine `allow-same-origin` with `allow-scripts` when the
  embedded origin is the SPA's own. Combine with CSP `frame-src` allowlist
  and `Permissions-Policy` constraints on the embedded context.
- **Why:** `sandbox` is the WHATWG-defined per-iframe lockdown
  (no scripts, no forms, no top-level navigation, opaque origin).
  Combining `allow-same-origin` + `allow-scripts` lets the embedded page
  programmatically remove its own sandbox attribute and break out.
- **Applies to:** Any iframe in the SPA (payments, third-party widgets).
- **Sources:**
  - <https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/iframe#sandbox>
  - <https://html.spec.whatwg.org/multipage/iframe-embed-object.html#attr-iframe-sandbox>
- **Confidence:** high.

### 24. Apply autocomplete hints intentionally on sensitive forms

- **Practice:** Set `autocomplete="new-password"` on registration and
  password-change inputs (so password managers offer a generated value, not
  an existing one). Use `autocomplete="current-password"` on login.
  Add `autocomplete="one-time-code"` on TOTP fields. Avoid blanket
  `autocomplete="off"` on credential fields — modern browsers ignore it for
  passwords and the result is broken UX with no security benefit.
- **Why:** Modern browsers (Chrome, Firefox, Safari) explicitly ignore
  `autocomplete="off"` on password fields for accessibility / password-
  manager reasons. The right tool is the specific `autocomplete` token,
  which steers password managers correctly.
- **Applies to:** Login, registration, password reset, MFA forms.
- **Sources:**
  - <https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Attributes/autocomplete>
  - <https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html>
- **Confidence:** high.

### 25. Lock the dependency tree: `npm ci` from a committed lockfile, audit on every PR

- **Practice:** Commit `package-lock.json` (or `pnpm-lock.yaml`). Install
  with `npm ci` / `pnpm install --frozen-lockfile` in CI so installs fail
  on lockfile drift. Run `npm audit --omit=dev` (or `pnpm audit`) on every
  pull request and on a scheduled cadence; gate releases on
  zero-known-high-or-critical CVEs in production dependencies. Enable
  Dependabot / Renovate to ship patch updates promptly.
- **Why:** The 2024–2025 npm supply-chain incidents (XZ-style typosquats,
  `event-stream`, repeated `ua-parser-js` compromises) demonstrate that
  unpinned installs and stale lockfiles are the primary attack vector for
  frontend supply-chain compromise.
- **Applies to:** CI pipeline, Renovate config, release gate.
- **Sources:**
  - <https://cheatsheetseries.owasp.org/cheatsheets/NPM_Security_Cheat_Sheet.html>
  - <https://owasp.org/Top10/A06_2021-Vulnerable_and_Outdated_Components/>
- **Confidence:** high.

### 26. Verify the deployed header set against Mozilla Observatory as part of CI / release

- **Practice:** After each production deploy (and as a quarterly drift
  check), scan the production hostname with the MDN HTTP Observatory.
  Aim for grade A or A+ (CSP, HSTS, X-Content-Type-Options, COOP,
  Referrer-Policy, X-Frame-Options/frame-ancestors). Treat any drop in
  grade as a release blocker.
- **Why:** Observatory codifies the same OWASP / MDN header rules into a
  reproducible scoring rubric, surfacing missing or weakened headers that
  diff-review can miss when nginx config is edited.
- **Applies to:** Release pipeline, nginx config reviews.
- **Sources:**
  - <https://developer.mozilla.org/en-US/observatory>
  - <https://developer.mozilla.org/en-US/observatory/docs/tests_and_scoring>
- **Confidence:** high.

### 27. Author cookies with the `__Host-` prefix, `Secure`, `HttpOnly`, `SameSite=Strict`

- **Practice:** Any cookie the SPA depends on (refresh token, CSRF token,
  session cookie) must be issued by the backend as
  `Set-Cookie: __Host-<name>=<value>; Path=/; Secure; HttpOnly; SameSite=Strict`.
  Use `SameSite=Lax` only when a third-party top-level navigation must
  carry the cookie (OAuth callback) and never `SameSite=None` without
  `Secure`. The SPA never reads or writes these cookies via JavaScript.
- **Why:** `__Host-` binds the cookie to the exact host with a root path
  and forbids the `Domain` attribute, closing subdomain-takeover cookie
  shadows. `Secure` + `HttpOnly` + `SameSite=Strict` together blunt CSRF
  and XSS exfiltration.
- **Applies to:** Backend (this is what the frontend depends on), CSRF
  flow design.
- **Sources:**
  - <https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html>
  - <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie>
- **Confidence:** high.

### 28. Validate uploaded files in the browser as a UX hint and re-validate (authoritatively) on the server

- **Practice:** In React form code, gate file pickers by `accept="..."` and
  by client-side MIME / size / extension checks for fast feedback. Never
  trust the result: the backend must validate magic bytes (file signature),
  enforce a hard max size, store outside the web root, and scan with an
  AV/CDR engine before the file is served back. Render filenames as text,
  never as HTML.
- **Why:** Client-side checks are bypassable; only server-side validation
  is authoritative. OWASP's File Upload Cheat Sheet is explicit that
  `Content-Type` headers and extensions are not trustworthy.
- **Applies to:** Any upload form in the SPA + backend pipeline.
- **Sources:**
  - <https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html>
  - <https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload>
- **Confidence:** high.

---

## Anti-patterns to avoid

- **`script-src 'self' 'unsafe-inline'`** — sometimes added to "make MUI
  emotion work." Use a nonce bound to emotion's cache nonce instead.
- **`script-src *` or host-allowlist CSP** — bypassable via open JSONP
  endpoints, Angular templates on the allowlisted host, etc. Switch to
  nonce + `'strict-dynamic'`.
- **Storing JWTs in `localStorage` "because cookies are hard."** Single XSS
  exfiltrates the lot; OWASP explicitly warns against this.
- **`dangerouslySetInnerHTML={{ __html: t('news.body') }}`** — translation
  files become an XSS sink. Use `<Trans>` instead.
- **`navigate(searchParams.get('returnTo'))` without validation** — classic
  open redirect.
- **`window.open(url, '_blank')` without `noopener,noreferrer` features.**
- **Publishing `*.js.map` to production** — gives attackers the full source
  tree.
- **`build.sourcemap: 'inline'` in production** — same as above, plus
  bloats the bundle.
- **`envPrefix: ''` in `vite.config.ts`** — leaks every env var into the
  client bundle.
- **`SameSite=None` without `Secure`** — modern browsers reject the
  attribute silently, falling back to the unsafe default.
- **`<iframe sandbox="allow-scripts allow-same-origin">` for SPA-origin
  content** — equivalent to no sandbox at all.
- **Disabling `escapeValue` in i18next globally** — turns every translation
  string into a potential HTML injection point.
- **Encrypting `redux-persist` with a hard-coded key shipped in the bundle**
  — security theatre; the key is in the source map.
- **Generic `Permissions-Policy` with only camera/mic disabled** — also
  deny `usb`, `serial`, `bluetooth`, `payment`, `accelerometer`,
  `gyroscope`, `magnetometer`, `midi`, `xr-spatial-tracking`.

---

## Open questions / topics needing follow-up

- **Trusted Types adoption in MUI v9 + emotion:** confirm whether emotion's
  runtime style insertion is compatible with `require-trusted-types-for
  'script'`; if not, document the policy override (`trusted-types
  emotion-style dompurify#html`).
- **`react-router` v7 specific open-redirect helpers:** no first-party
  React Router doc currently prescribes URL validation in `redirect` /
  `Navigate`. The OWASP "Unvalidated Redirects and Forwards" cheat sheet
  was used as the load-bearing source; a react-router-native helper would
  be preferable if/when it ships.
- **qrcode.react upstream guidance on size limits:** the QR spec source is
  authoritative for the character ceiling, but the library does not
  surface its own input-validation API. Practice #22 is therefore framed
  as the caller's responsibility.
- **redux-persist independent security source:** the second source under
  Practice #14 is the library's own README. If a normative spec requires
  two independent sources, this entry should be downgraded or rephrased.
- **COEP `require-corp` rollout:** worth a separate spec entry once
  cross-origin isolation is needed for `SharedArrayBuffer` or precise
  timers. Today the cost (third-party CORP headers) usually outweighs the
  benefit for a token-bearer SPA.

---

## Spec-input summary

Load-bearing rules for the normative spec:

1. **Strict CSP** with nonce + `'strict-dynamic'`, no `unsafe-inline`,
   no `unsafe-eval`, `object-src 'none'`, `base-uri 'none'`,
   `frame-ancestors 'none'`, `require-trusted-types-for 'script'`.
2. **Full nginx header set:** CSP, HSTS (`max-age=63072000;
   includeSubDomains; preload` once verified), `X-Content-Type-Options:
   nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, COOP
   `same-origin`, CORP `same-origin`, `Permissions-Policy` denying every
   feature the SPA does not actively use, `X-Frame-Options: DENY` as XFO
   fallback.
3. **No tokens in Web Storage; no secrets in `VITE_*`.** Tokens live in
   `HttpOnly; Secure; SameSite=Strict` cookies, or in memory + silent
   refresh against a cookie-protected endpoint. `redux-persist` whitelist
   is UI-state only.
4. **No public source maps**, `build.sourcemap: false` (or `'hidden'`).
   nginx blocks `*.map`.
5. **Quarantine `dangerouslySetInnerHTML`** behind a Trusted Types policy
   that runs DOMPurify; lint-forbid elsewhere.
6. **Validate every user-controlled URL** before `href`, `src`, or
   `navigate()`; allow-list schemes (`https:`, `mailto:`) and origins.
7. **`rel="noopener noreferrer"`** on every external `target="_blank"`
   link.
8. **`autocomplete="new-password"` / `"current-password"` /
   `"one-time-code"`** on auth inputs; never blanket `autocomplete="off"`.
9. **Server-side validation parity** with every Zod schema.
10. **Supply-chain hygiene:** committed lockfile, `npm ci` in CI,
    vulnerability gate on PRs, Renovate enabled.
11. **Release gate:** Mozilla Observatory grade A or better against the
    deployed origin.

Each rule maps to one or more of the numbered practices above and to two
or more independent authoritative sources.

## Currency addendum (2026-07-24)

- Trusted Types browser support is stale above: Firefox ships enforcement by default since Firefox 133 (late 2024) and WebKit/Safari followed in 2025. Broad availability strengthens the spec's Trusted-Types MUST.
- **Emotion + Trusted Types open question resolved (2026-07-24):** the Emotion runtime operates cleanly under an enforced `require-trusted-types-for 'script'` CSP with MUI v9. The directive guards script/HTML DOM-XSS sinks only (`innerHTML`, `script.src`, `document.write`); the W3C Trusted Types work has not extended `'script'` to CSS/style sinks. Emotion (still MUI v9's default styling engine) injects via `<style>` tags governed by the `style-src` / `style-src-elem` nonce bound to `cache.nonce`, not by a script sink, so it's out of scope. Held to the volatile-external ≥ 3-source tier per `spec/claude/research-triangulate/` §Author-time assertions: [1] MUI CSP guide `mui.com/material-ui/guides/content-security-policy/` (Emotion → `style-src-elem` nonce); [2] W3C Trusted Types explainer `github.com/w3c/trusted-types/blob/main/explainer.md` + MDN `require-trusted-types-for` (`'script'`-sink scope; CSS sinks explicitly future work); [3] `content-security-policy.com/require-trusted-types-for/`; [4] MUI v9 keeps Emotion default `npmjs.com/package/@mui/material`. The spec's §Security CSP MUST is qualified so an audit does not flag Emotion/MUI styling as a Trusted-Types-for-`script` violation.
- The HTTP Observatory reference is the MDN-hosted successor (`developer.mozilla.org/en-US/observatory`); the retired `observatory.mozilla.org` endpoint must not be targeted by release-gate tooling.
- Practice #14 (redux-persist) still lacks a second independent source; the spec keeps the rule and records the convention-level exceptions in its Sources section.
