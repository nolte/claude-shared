# Web-View UI Optimization

Status: draft

## Context

Every browser-hosted UI in the portfolio is built on the same primitives—plain HTML and CSS plus a JavaScript framework rendering into a single DOM—and is ultimately judged by the same five questions: does the first paint arrive fast, is the interaction surface safe, can every user operate it, does it work in every offered language, and does it feel right under the user's finger or pointer? The current reference implementation is the kamerplanter frontend: React 19, TypeScript strict, Vite 8 as the bundler, MUI v9 with Emotion, Redux Toolkit, React Router v7, react-hook-form with Zod, react-i18next, notistack, Recharts, Vitest with `vitest-axe`, served as static assets behind nginx with an `nginx-security-headers.inc` partial. New product features, refactors, and audits all touch this surface, but the rules they must satisfy are scattered across vendor docs, OWASP cheat sheets, WCAG criteria, and ad-hoc team conventions. The cost is twofold: contributors re-derive the same checklists every time, and reviewers can't tell whether a PR is shippable from the diff alone. This spec collects the rules that govern that surface—load-bearing only, vendor-verified, anchored to ≥2 independent authoritative sources per claim—so the rules apply uniformly across audits, new code, and the `webview-ui-optimize` skill / `webview-ui-expert` agent that consume them.

## Goals

- A contributor working on a portfolio frontend can audit any page or component against one spec and find normative MUST/SHOULD/MUST-NOT rules for Performance, Security, Accessibility, Internationalisation, and UX.
- Every normative rule is anchored to ≥2 independent authoritative sources (vendor docs, W3C / WHATWG specs, OWASP cheat sheets, MDN, WebAIM, web.dev, Nielsen Norman Group), recorded in the research audit trail under `.audits/webview-ui-expert/`.
- The rules are stack-specific where the stack is fixed (React 19, Vite 8, MUI v9, RTK, react-router v7, react-hook-form, react-i18next, notistack, Recharts, nginx) and platform-generic elsewhere (HTML, CSS, browser APIs).
- The spec is the single source of truth consumed by the `webview-ui-optimize` skill (audit + patch workflow) and the `webview-ui-expert` agent (read-only deep-dive reviewer).
- Drift between the spec and a target repository is detectable: the skill can produce a row per rule with `pass` / `fail` / `n/a`.

## Non-Goals

- Picking a different stack (Vue, Svelte, Angular, Solid)—this spec is for the React/Vite/MUI baseline and would need a sibling spec per stack.
- Visual / brand-design rules (typography scale, illustration style, voice and tone)—those live in a product design system, not here.
- Native-shell concerns (Tauri, Electron, iOS WKWebView, Android WebView)—only browser-context optimisation is in scope. "Web-view" in this spec refers to the browser-rendered view, not the native container.
- Server-side rendering (SSR), Server Components, edge runtimes, or static-site generation—the reference stack ships a CSR SPA behind nginx.
- Test-suite content (which assertions to write, coverage thresholds)—only test infrastructure relevant to a11y / performance gating is in scope.
- Release-automation, dependency-upgrade strategy, and CI-pipeline shape—those live in `spec/project/release-automation/`, `spec/project/dependency-audit/`, and `spec/project/workflow-health/`.

## Requirements

### Performance and rendering

#### Core Web Vitals targets

- **MUST** treat the field-data p75 thresholds as hard targets: LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1, measured from real-user metrics (CrUX or a RUM provider), not synthetic alone.
- **MUST** include `<meta name="viewport" content="width=device-width, initial-scale=1">` in the root `index.html` and **MUST NOT** ship `user-scalable=no` or hard-coded pixel widths in that meta tag.

#### Critical path and assets

- **MUST** declare `font-display: swap` (or `optional`) on every `@font-face` rule, including MUI-generated typography.
- **MUST** preload the LCP-critical typography as `<link rel="preload" as="font" type="font/woff2" href="…" crossorigin>` (the `crossorigin` attribute is mandatory—without it the preload is fetched twice).
- **SHOULD** set `fetchpriority="high"` on the LCP image (or its `rel="preload" as="image"` link) on routes whose LCP candidate is an image; **MUST NOT** apply it to more than one element per route.
- **MUST** declare `loading="lazy"` and `decoding="async"` on every off-screen `<img>` and provide intrinsic `width`/`height` (or CSS `aspect-ratio`).
- **MUST** keep Vite's content-hashed filenames for `/assets/*` output.
- **MUST** keep `<link rel="modulepreload">` tags Vite emits into `index.html`; backend-integrated setups **MUST** replicate them from the build manifest.
- **MUST NOT** inject synchronous `<script>` tags ahead of the Vite module entry; every late-loaded script **MUST** carry `defer`, `async`, or `type="module"`.

#### React 19 rendering

- **MUST** enable the React Compiler (`babel-plugin-react-compiler` 1.x) in the Vite pipeline and wire `eslint-plugin-react-compiler`; manual `useMemo` / `useCallback` / `React.memo` **MUST** be treated as escape hatches only.
- **MUST** wrap state updates that drive expensive renders (filter changes, tab switches, chart inputs) in `startTransition`; pair the resulting `isPending` with a non-blocking indicator, never with a full-page skeleton.
- **SHOULD** apply `useDeferredValue` to props feeding `memo()`-wrapped slow children when the source setter can't be moved inside a transition.
- **MUST** code-split routes via React Router v7 lazy route modules and pair every async data boundary with `<Suspense>` + an `<ErrorBoundary>` exposing a Retry action.

#### MUI and Emotion

- **MUST** import MUI icons via deep paths (`@mui/icons-material/<Name>`); ESLint `no-restricted-imports` **MUST** forbid `@mui/icons-material` barrel imports. The same rule applies to other wide MUI barrels (`@mui/lab`).
- **MUST** memoise the MUI theme at module scope (or via `useMemo` on stable inputs) and pass it to a single root `ThemeProvider`.
- **SHOULD** use `sx` only for one-off styles and promote reused styles to `styled()`; **MUST NOT** pass an object-shape `sx` value that changes identity every render (use CSS variables or theme tokens instead).
- **MUST** use the MUI v9 `colorSchemes` API + `cssVariables` instead of imperative `palette.mode` toggling.

#### State and data

- **MUST** memoise Redux selectors that derive new references with `createSelector`; **MUST NOT** wrap a selector that already returns a stable slice reference.
- **SHOULD** move read-side server state into RTK Query endpoints with explicit `tagTypes` / `providesTags` / `invalidatesTags`; the default 60 s `keepUnusedDataFor` stays unless profiling shows otherwise.
- **MUST** prefer uncontrolled `react-hook-form` inputs registered via `register`; **MUST** use `useWatch` (per-component subscription) instead of `watch` (root re-render) when reacting to specific fields.
- **MUST** import dayjs locales by deep path (`dayjs/locale/<code>`) and only ship locales the product actually offers.
- **MUST** pass `AbortController().signal` on every cancellable `axios` call and call `controller.abort()` from the consuming hook's cleanup or on route change; the deprecated `CancelToken` **MUST NOT** appear in new code.

#### Charts and long lists

- **SHOULD** virtualise lists/grids that can mount more than ≈100 simultaneously rendered rows (`react-window` `FixedSizeList`/`VariableSizeList` or MUI X virtualised modes) with a small `overscanCount` (≈ 5).
- **SHOULD** lazy-load Recharts charts via `React.lazy` + Suspense; **SHOULD** gate them on `IntersectionObserver` for off-screen widgets.

#### nginx and HTTP caching

- **MUST** serve `/assets/*` with `Cache-Control: public, max-age=31536000, immutable`.
- **MUST** serve `index.html` with `Cache-Control: no-cache` (or `no-store` when sensitive data is rendered inline).
- **MUST** enable `gzip_static on;`; **SHOULD** enable `brotli_static on;` via `ngx_brotli` when available, and emit `.gz`/`.br` siblings during `vite build`.

### Security and sandboxing

#### Content Security Policy and Trusted Types

- **MUST** serve a strict Content Security Policy with a per-response cryptographic nonce on `script-src` plus `'strict-dynamic'`, for example `script-src 'nonce-<random>' 'strict-dynamic'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; require-trusted-types-for 'script';`.
- **MUST NOT** include `'unsafe-inline'` or `'unsafe-eval'` in `script-src`; for `style-src`, prefer a nonce bound to Emotion's `cache.nonce` over `'unsafe-inline'`.
- **MUST NOT** use host-allowlist CSPs (bypassable via open JSONP endpoints on allowlisted hosts).
- **MUST** send `require-trusted-types-for 'script'` and a named `trusted-types` policy that pipes any HTML insertion through DOMPurify.

#### nginx security headers

- **MUST** send the full header set from `nginx-security-headers.inc`:
  - `Content-Security-Policy: <strict policy as above>`.
  - `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload` (omit `preload` until the operator is certain every subdomain serves HTTPS indefinitely).
  - `X-Content-Type-Options: nosniff`.
  - `Referrer-Policy: strict-origin-when-cross-origin` (downgrade to `no-referrer` for routes that carry tokens in the URL).
  - `Cross-Origin-Opener-Policy: same-origin` (`same-origin-allow-popups` only when the SPA opens trusted OAuth popups).
  - `Cross-Origin-Resource-Policy: same-origin` on app-owned assets.
  - `Permissions-Policy` denying every powerful feature the SPA doesn't actively use (camera, microphone, geolocation, payment, USB, serial, bluetooth, accelerometer, gyroscope, magnetometer, MIDI, and similar) and opting in to `'self'` only for features genuinely needed.
  - `X-Frame-Options: DENY` as a belt-and-braces fallback to `frame-ancestors 'none'`.
- **SHOULD** add `Cross-Origin-Embedder-Policy: require-corp` only when the SPA needs cross-origin isolation (SharedArrayBuffer, high-resolution timers); COEP is opt-in because it breaks naïvely embedded resources.

#### React rendering safety

- **MUST** treat `dangerouslySetInnerHTML` as a privileged escape hatch: allow it only in a small, code-owned set of components, always wrapped in a Trusted Types policy that runs DOMPurify with an explicit allow-list of tags and attributes. Lint-forbid via `react/no-danger` everywhere else.
- **MUST** validate every user-controlled URL before assigning to `href`, `src`, or calling React Router `navigate(...)` / `redirect(...)`: parse the URL, reject `javascript:`, `data:`, `vbscript:`, allow-list schemes (`https:`, `mailto:`) and origins, prefer route-relative paths.
- **MUST** add `rel="noopener noreferrer"` to every external `target="_blank"` link (and to any `window.open(url, '_blank')` features string); lint-enforce via `react/jsx-no-target-blank`.

#### Auth, storage, and secrets

- **MUST NOT** store auth tokens (access, refresh, session) in `localStorage`, `sessionStorage`, IndexedDB, or Redux state that's persisted; **MUST** keep tokens in an `HttpOnly; Secure; SameSite=Strict` cookie issued by the backend, OR in memory plus silent refresh against a cookie-protected refresh endpoint.
- **MUST** configure `redux-persist` (when present) with an explicit `whitelist` of slices that hold non-sensitive UI state only (theme, language, table column order). Encryption-at-rest with a key that ships in the bundle is forbidden.
- **MUST** treat every `import.meta.env.VITE_*` value as public. API keys, signing secrets, OAuth client secrets, and BFF-bypassing URLs **MUST NOT** be put behind a `VITE_` prefix; **MUST NOT** override `envPrefix` to an empty string.
- **MUST** set Vite `build.sourcemap` to `false` (or `'hidden'` when error tracking requires symbolication with private upload); **MUST NOT** serve `*.js.map` publicly from nginx, and **SHOULD** block `*.map` at the nginx layer.

#### Form and upload validation

- **MUST** mirror every Zod schema server-side: client validation is UX, never the authoritative gate. Backend validates positive-allow-list, length bounds, type bounds; client surfaces backend errors via `setError`.
- **MUST** validate file uploads in the browser (`accept`, MIME, size, extension) for UX only; the backend **MUST** validate magic bytes, enforce a hard max size, store outside the web root, and scan.
- **MUST** apply `autocomplete` hints intentionally on sensitive forms (`new-password`, `current-password`, `one-time-code`); **MUST NOT** set blanket `autocomplete="off"` on credential fields (modern browsers ignore it for passwords).

#### Supply chain and verification

- **MUST** commit `package-lock.json` (or `pnpm-lock.yaml`) and install with `npm ci` / `pnpm install --frozen-lockfile` in CI; **MUST** gate releases on zero known high/critical CVEs in production dependencies via `npm audit --omit=dev` (or equivalent).
- **MUST** verify the deployed header set against Mozilla HTTP Observatory after each production deploy; treat any drop in grade as a release blocker.
- **MUST** apply Subresource Integrity (`integrity` + `crossorigin="anonymous"`) to every `<script>` and `<link rel="stylesheet">` from a foreign origin; the default posture is to self-host via Vite so SRI is moot.

### Accessibility (WCAG 2.2 Level AA)

#### Document structure

- **MUST** wrap top-level page regions in semantic HTML5 sectioning elements (`<header>`, `<nav>`, `<main>`, `<footer>`, `<aside>`); each `<nav>` that isn't the sole nav **MUST** carry `aria-label` / `aria-labelledby`.
- **MUST** render exactly one visible `<h1>` per route and **MUST NOT** skip heading levels.
- **MUST** keep `<html lang>` and `<html dir>` synchronised with the active i18next language by mutating `document.documentElement.lang` (BCP-47 tag) and `document.documentElement.dir` (via `i18next.dir(lng)`) on every `languageChanged` event.
- **MUST** mark in-page foreign passages with `lang="…"` on a wrapping element (WCAG 3.1.2).

#### Focus management

- **MUST** ship a "skip to main content" link as the first focusable element; visually hidden but focusable, never `display:none`, **MUST** move focus to `<main>` or a `tabindex="-1"` element inside it.
- **MUST** move focus on every route change to either (a) the main content container with `tabindex="-1"`, or (b) the new `<h1>` with `tabindex="-1"`; **MUST NOT** focus a landmark element or autofocus an arbitrary input.
- **MUST NOT** set `outline: 0` / `outline: none` without an equivalent replacement; **MUST** use `:focus-visible` for custom focus styling and meet the 3:1 non-text contrast and WCAG 2.4.13 Focus Appearance perimeter rule.
- **MUST** ensure focus isn't obscured by sticky chrome (WCAG 2.4.11): use `scroll-margin-top` / `scroll-padding` equal to the bar height.
- **MUST NOT** use `tabindex` values greater than `0`; only `0` and `-1` are acceptable.

#### Components

- **MUST** preserve MUI `Dialog` / `Modal` focus-trap, initial-focus, and return-focus defaults: don't set `disableEnforceFocus`, `disableAutoFocus`, or `disableRestoreFocus` for routine dialogs. **MUST** carry `aria-labelledby` referencing the title; **SHOULD** also carry `aria-describedby` for long-form content.
- **MUST** label every icon-only `IconButton` with `aria-label` (or visually-hidden text); `<Tooltip>` provides a description, not a name, and **MUST NOT** substitute for the label.
- **MUST** wire react-hook-form errors with the triple `aria-invalid={!!errors.x}` + `aria-describedby="<error-id>"` + `role="alert"` on the error element.
- **MUST** generate input IDs via React 19 `useId()` (or MUI's generated IDs) so `<label htmlFor>` and `aria-describedby` resolve stably across renders.
- **MUST** label `@mui/x-tree-view` (`SimpleTreeView` / `RichTreeView`) with `aria-label` or `aria-labelledby`; **MUST NOT** override the built-in WAI-ARIA APG tree keyboard behaviour.
- **MUST** treat `@mui/x-date-pickers` popup views as Dialogs: all dialog rules apply (labelled-by, focus trap, return-focus); custom `<TextField>` slots **MUST** propagate the picker's ARIA props.
- **MUST** use a real `<button type="button">` (or MUI `Button` / `IconButton`) for any clickable control; **MUST NOT** attach `onClick` to a `<div>` or `<span>` to fake one.

#### Toasts and live regions

- **MUST** announce notistack messages via a live region; default to `role="status"` / `aria-live="polite"`, reserve `role="alert"` / `aria-live="assertive"` for true errors (failed save, auth expiry).
- **MUST** announce route changes via an `aria-live="polite"` region or via the focus-on-H1 mechanism; **MUST NOT** stack both for the same event.

#### Visual

- **MUST** configure MUI's `palette.contrastThreshold` to `4.5` so palette-derived `contrastText` choices target WCAG 1.4.3 AA (body text 4.5:1); verify custom palettes via WebAIM contrast checker.
- **MUST** wrap non-essential motion in `@media (prefers-reduced-motion: no-preference)` (opt-out pattern); reduce or remove transitions when the user has expressed a reduce preference.
- **SHOULD** honour `prefers-color-scheme` for the initial theme when the user hasn't explicitly chosen one; persisted user choice **MUST** override the OS preference thereafter.
- **MUST** keep layout reflow at 320 CSS px viewport width without horizontal scroll (WCAG 1.4.10); inherently 2-D content (tables, charts) **MUST** scroll inside its own container, not the page.
- **SHOULD** prefer `aria-disabled="true"` over native `disabled` for controls whose disabled state needs an explanation (form gating, paywall) so an associated `aria-describedby` reason remains discoverable.

#### Target size

- **MUST** make every interactive control's tap target at least 24 × 24 px (WCAG 2.5.8); **SHOULD** target 44 × 44 px on touch-first contexts (Apple HIG / Material Design alignment). Spacing **SHOULD** leave ≥ 8 px between adjacent targets.

#### Charts

- **MUST** give every Recharts chart a programmatically determinable text alternative: `role="img"` + `aria-label` / `aria-labelledby` on the container, an inline plain-language summary, AND a data-table fallback (visible or visually hidden but marked-up).
- **MUST** enable Recharts' `accessibilityLayer` on every chart.

#### Testing

- **MUST** add `vitest-axe` smoke tests per page-level component asserting `expect(await axe(container)).toHaveNoViolations()`; treat axe as a floor (~30 % of issues), not a ceiling. Color-contrast checks are disabled in JSDOM and **MUST** be verified separately (browser-mode, Storybook a11y addon, or manual).
- **SHOULD** use `@testing-library/user-event` (not `fireEvent`) for keyboard-, focus-, and pointer-driven a11y assertions.

### Internationalisation

#### Locale primitives

- **MUST** format every locale-sensitive number via `Intl.NumberFormat` (currencies use `style: 'currency'` + ISO 4217 code); **MUST NOT** hand-build separators or use `toFixed` for display.
- **MUST** format every locale-sensitive date / time via `Intl.DateTimeFormat` and relative spans via `Intl.RelativeTimeFormat`; hand-built date strings are forbidden.
- **MUST** use `Intl.Collator` for any sort of locale-aware data; `Array.sort()`'s default Unicode-code-point order is forbidden.
- **MUST** format conjunctive / disjunctive human-readable lists via `Intl.ListFormat`; hand-rolled `arr.join(', ')` is forbidden.

#### Translation function

- **MUST** author plural variants with the i18next JSON-v4 suffix grammar (`_one`, `_other`, plus full CLDR set where the language requires it); **MUST NOT** branch on `count === 1` in component code.
- **MUST** compose every translated sentence as a single key with named placeholders (`t('welcome', { name })`); fragment concatenation (`t('hello') + ' ' + name`) is forbidden.
- **MUST** use the `<Trans>` component with explicit React-element children for translations containing inline markup; **MUST NOT** disable `interpolation.escapeValue` globally; **MUST NOT** insert `{{value}}` into `dangerouslySetInnerHTML`.

#### Detection, persistence, routing

- **MUST** configure `i18next-browser-languagedetector` with explicit `order` (`['querystring', 'cookie', 'localStorage', 'navigator', 'htmlTag']`) and explicit `caches` (`['cookie', 'localStorage']`); deterministic cookie name (`i18next`) and storage key (`i18nextLng`).
- **MUST** make a persisted user choice always beat automatic detection: `i18n.changeLanguage(lng)` writes through to the caches the detector reads.
- **MUST** declare `supportedLngs` (canonical first) and `fallbackLng` explicitly in `i18n.init`; resource-path injection via the querystring slot is mitigated only by this allow-list.
- **MUST** encode the locale in the URL via a React Router v7 dynamic segment (`/:locale/*`) or a `prefix(...)` route; the router is the single source of truth for the active locale and **MUST** sync i18next on every navigation.
- **MUST** emit `Content-Language: <locale>` from nginx on every localised response; **SHOULD** honour an existing `i18next` cookie ahead of `Accept-Language`-based root redirects.
- **MUST** emit static `<link rel="alternate" hreflang="…" href="…">` tags (one per locale, plus `x-default`) in the initial `index.html` server-side or at build time, bidirectional. React-runtime injection of `hreflang` is forbidden.

#### Loading, RTL, and pickers

- **MUST** organise translations into one namespace per feature (`auth`, `plants`, `settings`, `common`) and lazy-load namespaces per route via `i18next-resources-to-backend` (Vite dynamic imports) or `i18next-http-backend`.
- **MUST** pre-bundle the canonical locale plus the active locale; defer the rest as Vite chunks per `(locale, namespace)` pair.
- **MUST** wrap the React tree in `<Suspense>` so first paint doesn't show raw keys; `react.useSuspense: true` is the default and **MUST** stay enabled unless every consumer explicitly gates on `ready`.
- **MUST** wire MUI v9 RTL via `createTheme({ direction: 'rtl' })` AND an Emotion `CacheProvider` whose cache uses `[prefixer, rtlPlugin]` from `@mui/stylis-plugin-rtl` when the active locale is RTL.
- **MUST** wire MUI-X `LocalizationProvider` with three things in lockstep: dayjs locale (`dayjs.locale('de')`), `adapterLocale="de"`, and `localeText` from `@mui/x-date-pickers/locales`.
- **MUST** drive dayjs locales as default-export imports and switch them on every `languageChanged` event; bare side-effect imports (`import 'dayjs/locale/de'`) **MUST NOT** appear because some bundlers drop them.
- **MUST** translate Zod validation errors via a custom `errorMap` (set via `z.setErrorMap` or `zodResolver(schema, { errorMap })`); **MUST NOT** embed `t()` calls inside schema definitions.
- **MUST** resolve translations for `notistack` messages at the call site (`enqueueSnackbar(t('errors.savePlant'), …)`) so messages stay stable for the toast's lifetime.

#### Drift detection

- **MUST** enable an i18next missing-key reporter: `debug: true` and `saveMissing: true` + a `missingKeyHandler` in development; a sampled error-reporter (Sentry / equivalent) in production with `saveMissing: false`.
- **SHOULD** run a pseudo-locale test (for example `i18next-pseudo`) in CI to catch missing keys, truncation, and hard-coded English strings before a real translator sees them.
- **MUST** author keys as stable, lowercase, dotted identifiers (`plants.list.empty`); text-as-key is forbidden because every English edit breaks every translation.

### UX and native feel

#### Loading and feedback hierarchy

- **MUST** pick the feedback indicator by expected wait time:
  - < ≈ 100 ms: no indicator.
  - 100 ms–1 s: optimistic / no spinner.
  - 1 s–10 s: skeleton screen mirroring the final layout.
  - > 10 s: determinate progress bar with cancel affordance.
- **MUST NOT** show a blank screen for more than 300 ms after a navigation; skeletons or `<Suspense>` fallbacks bridge the gap.
- **MUST** debounce spinner display by 200–300 ms so brief loads don't flash a spinner; the chosen project-wide threshold **MUST** be applied consistently.
- **MUST** build a per-view `<XxxSkeleton/>` that mirrors the final layout (shape, count, rough size); generic shimmer boxes that cause layout shift on hydrate are forbidden.

#### Mutations and recovery

- **SHOULD** apply optimistic UI to low-risk mutations only (favouriting, toggling, reordering, renaming); **MUST NOT** apply it to financial transactions, irreversible deletes without an undo grace period, or anything triggering downstream side effects (email, payment).
- **SHOULD** prefer an optimistic commit + Undo snackbar over an interruption-style "Are you sure?" dialog for reversible destructive actions; use a real `<Dialog>` only when the action is irreversible or multi-step.
- **MUST** distinguish error surfaces:
  - inline error (next to field or component)—form validation, "this card failed to load—retry," missing permission.
  - snackbar / toast—transient, non-actionable network errors, background save failures.
  - dialog—state-corrupting failures requiring a decision (session expired).

#### Snackbar discipline

- **MUST** display at most one snackbar at a time; if stacking is unavoidable, cap `maxSnack` at ≤ 3.
- **MUST** apply variant semantics: `success` for confirmed write, `error` for failed write or unrecoverable network error, `warning` for soft validation, `info` for non-actionable state, `default` for undo affordances.
- **MUST NOT** use snackbars for inline form validation; those belong next to the field.
- **MUST** use `autoHideDuration` of ≥ 4 s (default 5 s) and pair `persist: true` snackbars with an explicit dismiss or action button.
- **MUST** anchor the snackbar to one fixed corner per app (bottom-left desktop, bottom-centre mobile per Material guidance); **MUST NOT** vary anchor per route.

#### Navigation and back behaviour

- **MUST** mount React Router v7 `<ScrollRestoration/>` once at the layout root.
- **MUST** show a global pending indicator (subtle top-of-layout progress bar) driven by `useNavigation().state` only after a ≥ 200 ms delay so fast navigations don't flash.
- **MUST NOT** trap the browser Back button: modal close binds ESC and an explicit close button; route guards redirect via `<Navigate replace />` so the guarded URL isn't in the back stack twice.
- **SHOULD** use `<NavLink prefetch="intent">` for navigation links inside the main shell when running in framework mode; **MUST NOT** use `prefetch="render"` or `prefetch="viewport"` on large lists.

#### Forms

- **MUST** configure react-hook-form with `mode: 'onTouched'`, `reValidateMode: 'onChange'`, `shouldFocusError: true`.
- **MUST** render an error summary above the form when `>1` field is invalid: a `role="alert"` container with a heading and a list of links jumping to each invalid field.
- **MUST** use `aria-disabled="true"` (not native `disabled`) on the submit button while the form is pending so screen-reader users can still tab onto it and hear its state; guard submission inside the handler, not via `disabled`.
- **MUST NOT** communicate button states via colour alone (WCAG 1.4.1): pair colour with inline message / icon / `aria-live` update.

#### Theming and motion

- **MUST** resolve every colour, spacing value, and border-radius from theme tokens; hard-coded hex / `rgb()` inside components is forbidden.
- **MUST** drive light/dark mode via MUI v9 `colorSchemes` + `cssVariables`; **MUST NOT** flip via `palette.mode` conditionals (they cause FOUC).
- **MUST** inline a tiny `<head>` script that reads the persisted theme key and sets a `data-color-scheme` attribute on `<html>` before the React tree mounts (MUI's `InitColorSchemeScript`).
- **MUST** wrap non-essential motion in `@media (prefers-reduced-motion: no-preference)`; essential motion (loading spinner) **SHOULD** be reduced to opacity / dissolve when reduce-motion is set.

#### Viewport and platform fit

- **MUST** prefer `svh`, `dvh`, `lvh` over `vh` for full-screen layouts:
  - `svh` for "fill the screen, never hidden under chrome."
  - `lvh` for "fill the maximally retracted viewport."
  - `dvh` only when live tracking is essential (rarely on scrolling content).
- **MUST** apply `env(safe-area-inset-*)` padding on the layout root for notch / home-indicator clearance, with a `max(env(…), <minimum>)` floor; `viewport-fit=cover` **MUST** be set in the viewport meta for safe-area insets to be non-zero.

#### Dialogs and popovers

- **MUST** prefer the platform `<dialog>` (via MUI `Dialog`, which uses it under the hood, called via `.showModal()`) over hand-rolled modal-div trees: focus trap, ESC, `aria-modal`, `::backdrop`, top-layer, and inertness are then free.
- **SHOULD** prefer the native Popover API (`popover="auto"`) on stable engines for tooltips / menus; fall back to MUI `Popover` / `Menu` for older browsers.

#### Charts and viewport

- **MUST** wrap every Recharts chart in `<ResponsiveContainer width="100%" aspect={…}>` (or fixed `minWidth` / `minHeight`); naked charts that collapse in narrow columns are forbidden.
- **MUST** enable `accessibilityLayer` on every chart (cross-references the a11y MUST in §Accessibility › Charts).

### Cross-cutting verification

- **MUST** wire `vitest-axe` smoke tests, a Vite + nginx static-asset audit (immutable headers, source-map absence), a Mozilla HTTP Observatory check, and a Core-Web-Vitals RUM snapshot into the release gate; a release **MUST NOT** ship while any of those are red.
- **MUST** keep the research audit trail under `.audits/webview-ui-expert/<domain>.md` in lockstep with this spec; every normative rule above is anchored to at least one entry there, which in turn cites ≥ 2 independent authoritative sources.

## Acceptance Criteria

- [ ] Every page-level component in a target repository renders within the LCP ≤ 2.5 s / INP ≤ 200 ms / CLS ≤ 0.1 p75 budget on a representative device class.
- [ ] `nginx-security-headers.inc` produces a Mozilla HTTP Observatory grade of A or A+; any drop blocks the release.
- [ ] No production response carries `*.js.map`; nginx blocks `*.map` at the location level.
- [ ] No `dangerouslySetInnerHTML` exists outside a code-owned allow-list of components wrapped in a Trusted Types DOMPurify policy.
- [ ] ESLint `no-restricted-imports` rejects barrel imports of `@mui/icons-material` (and any equivalent wide barrel) repository-wide.
- [ ] `react-i18next` is initialised with `supportedLngs`, `fallbackLng`, an explicit detector `order` and `caches`, and `react.useSuspense: true`; an automated check confirms `<html lang>` / `<html dir>` mutate on `languageChanged`.
- [ ] Every Recharts chart in the repository renders a text alternative and a data-table fallback, and enables `accessibilityLayer`.
- [ ] `vitest-axe` runs in CI and reports zero violations for every page-level component; the JSDOM contrast-rule limitation is documented and verified by a browser-mode or manual contrast pass.
- [ ] Every route uses React Router v7 lazy modules with `<Suspense>` + `<ErrorBoundary>` pairs, and the layout mounts `<ScrollRestoration/>`.
- [ ] `npm audit --omit=dev` reports zero known high/critical CVEs in the production dependency tree; lockfile drift fails CI.
- [ ] The `webview-ui-optimize` skill produces a row-per-rule audit table for the repository with `pass` / `fail` / `n/a` and the offending file paths for every `fail`.

## Open Questions

- Should the spec mandate the React Compiler today (it's stable but ESLint rule maturity varies), or stay at SHOULD pending a portfolio-wide rollout decision?
- Should `Cross-Origin-Embedder-Policy: require-corp` move to MUST once cross-origin isolation is wanted for high-resolution timers / `SharedArrayBuffer`, or remain explicitly opt-in given third-party CORP friction?
- Should the i18n locale-prefix rule be tightened from MUST to MUST-NOT-USE-COOKIE-ONLY, given that some operator setups deliberately keep canonical-language URLs locale-less?
- Should the spec name a single project-wide spinner-show delay (for example 250 ms) or keep the 200–300 ms range so individual repositories pick within it consistently?
- Where exactly does this spec end and `spec/project/dependency-audit/` begin for supply-chain hygiene—the lockfile and `npm audit` rules currently appear in both; should one cross-reference the other?
- Should React Router v7 framework-mode rules (`<NavLink prefetch="intent">`, route-module file convention) sit in this spec or in a sibling routing-specific spec, given that SPA-mode and framework-mode diverge meaningfully?

## Sources

Every normative rule above is anchored to the per-domain research notes under `.audits/webview-ui-expert/`, each entry of which cites at least two independent authoritative sources:

- `.audits/webview-ui-expert/performance.md`: 27 practices + 9 anti-patterns (`web.dev`, `react.dev`, `vitejs.dev`, `mui.com`, `redux.js.org`, `reactrouter.com`, `react-hook-form.com`, MDN, `nginx.org`, `day.js.org`, `axios-http.com`, `vitest.dev`, RFC 8246).
- `.audits/webview-ui-expert/security.md`: 28 practices (OWASP Cheat Sheets, MDN, W3C Trusted Types, `web.dev`, Mozilla HTTP Observatory, vendor docs).
- `.audits/webview-ui-expert/accessibility.md`: 24 practices (W3C WAI WCAG 2.2, ARIA Authoring Practices Guide, MDN, WebAIM, Deque, A11y Project, vendor docs).
- `.audits/webview-ui-expert/i18n.md`: 26 practices (W3C i18n WG, Unicode CLDR / TR10, ICU, MDN, Google Search Central, RFC 7231, vendor docs).
- `.audits/webview-ui-expert/ux.md`: 30 practices (Nielsen Norman Group, `web.dev`, MDN, W3C, WHATWG, Material Design, Apple HIG, vendor docs).
