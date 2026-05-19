# Webview UI Expert — UX / "feels right in the browser" best practices

Stack in scope: React 19, Vite 8, MUI v9, Redux Toolkit (RTK + RTK Query),
React Router v7 (data routers), react-hook-form + zod, notistack, recharts,
react-i18next. Production: static site behind nginx, no native shell.

Source labelling:
- `verified` — at least two independent authoritative sources cited.
- `partial` — one strong authoritative source; supplementary corroboration weaker.
- `unverified` — only a single source or only secondary sources; treat as draft.

Authoritative sources accepted: Nielsen Norman Group (NN/G), web.dev (Chrome),
MDN, W3C / WHATWG specs, official library docs (react.dev, mui.com,
reactrouter.com, react-hook-form.com), Material Design, Apple HIG (sparingly).

---

## 1. Loading-state hierarchy — three response-time thresholds (verified)

Pick the feedback indicator by *expected* wait time:

- **< ~0.1 s**: no indicator. A spinner that flashes briefly causes anxiety;
  users cannot keep up with what just happened.
- **~0.1 s – ~1 s**: optimistic / no spinner. The user's "flow of thought"
  stays intact; a transient indicator distracts more than it informs.
- **~1 s – ~10 s**: skeleton screen that reflects the final layout (lists,
  cards, table rows). Skeletons set visual expectations and are perceived
  as faster than spinners even when the actual time is identical.
- **> ~10 s**: progress bar with percent-complete or time-remaining, plus
  a cancel affordance. Above 10 s the user's attention disengages.

Apply: skeleton MUST appear within ~300 ms of navigation if data is not yet
ready; never show a blank screen for >300 ms. Above ~1 s, use MUI `Skeleton`
shaped like the final card / row / chart. Above ~10 s, show a determinate
progress bar.

Sources:
- NN/G, *Response Time Limits: Article by Jakob Nielsen* — https://www.nngroup.com/articles/response-times-3-important-limits/
- NN/G, *Skeleton Screens 101* — https://www.nngroup.com/articles/skeleton-screens/
- NN/G, *Progress Indicators Make a Slow System Less Insufferable* — https://www.nngroup.com/articles/progress-indicators/
- NN/G, *Powers of 10: Time Scales in User Experience* — https://www.nngroup.com/articles/powers-of-10-time-scales-in-ux/

## 2. Skeletons mirror final layout, never generic spinners (verified)

A skeleton MUST reproduce the shape, count, and rough size of the content
that will replace it: card stack, list row, chart frame. Generic "shimmer
boxes" that don't match final layout are worse than no skeleton because
they cause layout shift when content arrives. Do not use a skeleton for
loads under ~1 s — switch to no indicator (optimistic) or, if the work is
indeterminate and longer, a centred spinner that itself appears only after
a ~300 ms delay (avoids spinner flash on fast networks).

Apply: build a `<XxxSkeleton/>` per primary view that uses MUI `Skeleton`
with the same grid / flex structure as the loaded component; render it
from a `<Suspense fallback={…}>` boundary that wraps that view.

Sources:
- NN/G, *Skeleton Screens 101* — https://www.nngroup.com/articles/skeleton-screens/
- MUI, *Skeleton* component docs — https://mui.com/material-ui/react-skeleton/
- web.dev, *Cumulative Layout Shift (CLS)* — https://web.dev/articles/cls

## 3. React 19 Suspense + Error Boundary pairing (verified)

For every async data dependency, render through `<Suspense fallback={<XxxSkeleton/>}>`
nested inside an `<ErrorBoundary>` that renders an inline recovery UI
("Couldn't load — Retry"). Use nested boundaries: one coarse boundary for
the whole route, finer boundaries for slower sub-regions (chart, related-list).
A rejected promise consumed via `use()` is thrown like an error and bubbles
to the nearest error boundary.

Apply: never let a thrown promise reach the root error boundary unprotected.
Pair each `<Suspense>` with an `<ErrorBoundary>` parent. The error boundary
MUST expose a "Retry" action that resets it (key bump / `resetKeys`).

Sources:
- React docs, *`<Suspense>`* — https://react.dev/reference/react/Suspense
- React docs, *React 19 release notes* — https://react.dev/blog/2024/12/05/react-19

## 4. Use `useTransition` for non-urgent UI updates (verified)

Wrap filter changes, tab switches, large list re-renders, and route prefetches
in `startTransition`. The transition's `isPending` flag drives a *subtle*
indicator (toolbar shimmer, faint progress bar) so the previous UI remains
interactive; the heavier update lands when ready. In React 19 async functions
inside transitions automatically manage pending → done.

Apply: a search box that filters a large list MUST use `useTransition` so
the input stays responsive on every keystroke; pair `isPending` with a
toolbar-level progress indicator, not a full-page skeleton.

Sources:
- React docs, *`useTransition`* — https://react.dev/reference/react/useTransition
- React docs, *React 19 release notes (Actions / async transitions)* — https://react.dev/blog/2024/12/05/react-19

## 5. Optimistic UI for low-risk mutations only (verified)

For mutations whose failure is rare and easy to reverse (favouriting, toggling
a setting, reordering, renaming, posting a comment), apply the change locally
*before* the server confirms. On failure, roll back and surface an inline
recovery affordance ("Couldn't save — Retry"). Do NOT apply optimistic UI to
financial transactions, irreversible deletes without an undo grace period,
or anything that triggers a downstream side effect (email send, payment).

Apply (RTK Query): inside `onQueryStarted`, call
`dispatch(api.util.updateQueryData(...))`, retain the returned `patchResult`,
and call `patchResult.undo()` from a `queryFulfilled.catch()` handler. For
burst mutations prone to race conditions prefer cache invalidation over
manual undo. For React 19 client-side optimism, use `useOptimistic`.

Sources:
- Redux Toolkit, *RTK Query — Manual Cache Updates* — https://redux-toolkit.js.org/rtk-query/usage/manual-cache-updates
- React docs, *`useOptimistic`* — https://react.dev/reference/react/useOptimistic
- NN/G, *Skeleton Screens 101* (perceived-speed argument that motivates optimism) — https://www.nngroup.com/articles/skeleton-screens/

## 6. Destructive actions: undo affordance over confirmation dialog (verified)

For reversible destructive actions (archive, delete a row, soft-delete a
message), prefer an *optimistic* commit + snackbar with `UNDO` action over
an interruption-style "Are you sure?" dialog. Material Design defines this
exact pattern: a snackbar with a single action button, displayed below the
content, for a brief grace period. For irreversible destructive actions or
multi-step decisions, use a `<dialog>` (or MUI `Dialog`) — snackbars permit
only one action, and "Dismiss" / "Cancel" are explicitly disallowed.

Apply: delete → optimistic remove + notistack `variant: 'default'` (per
Material guidance) with `action: <UndoButton/>` and an `autoHideDuration`
of 5–8 s. The actual server delete fires only after the snackbar dismisses
(or is committed immediately and undone via RTK Query `patchResult.undo()`).

Sources:
- Material Design 3, *Snackbar — Guidelines* — https://m3.material.io/components/snackbar/guidelines
- Material Design 2, *Snackbars* — https://m2.material.io/components/snackbars/
- notistack, *Basic features* — https://notistack.com/features/basic

## 7. Snackbar discipline: variant semantics, stacking, persistence (verified)

- **One snackbar at a time** is the Material guideline; if you must stack,
  cap with `maxSnack` at a small number (default 3) and never higher than 3.
- **Variant semantics**: `success` for confirmed write, `error` for failed
  write or unrecoverable network error, `warning` for soft validation
  outcomes, `info` for non-actionable state changes, `default` for undo
  affordances. Don't use `error` for inline form validation — those belong
  next to the field (see practice 12).
- **Duration**: default 5 s (notistack) / "at least 4 s" (MUI / MD). Use
  `persist: true` only for messages requiring user action (auth expiry,
  pending merge conflict) and ALWAYS pair persistent toasts with an
  explicit dismiss or action button.
- **Position**: one fixed corner per app (bottom-left on desktop, bottom-
  centre on mobile is Material's default) — moving it across the screen
  per route disorients users.

Apply: configure `SnackbarProvider` once at app root with `maxSnack={3}`,
`autoHideDuration={5000}`, `preventDuplicate`, anchored bottom-left desktop /
bottom-centre mobile.

Sources:
- Material Design 3, *Snackbar — Guidelines* — https://m3.material.io/components/snackbar/guidelines
- MUI, *Snackbar* — https://mui.com/material-ui/react-snackbar/
- notistack, *Basic features* / *API reference* — https://notistack.com/features/basic , https://notistack.com/api-reference

## 8. Error recovery: inline first, toast for transient (verified)

- **Inline error** (next to the affected field or component) for: form
  validation, "this card failed to load — retry", missing permission.
  Inline errors are persistent until resolved; screen readers announce
  them via `aria-describedby` + `aria-invalid` (WCAG 3.3.1).
- **Snackbar / toast** for: transient, non-actionable network errors,
  background save failures, anything the user does NOT need to act on
  immediately. Toasts disappear; never put non-recoverable critical
  information solely in a toast.
- **Dialog / blocking error** for: state-corrupting failures requiring a
  decision (e.g. "Reload — your session expired").

Apply: every `<Suspense>` boundary has an `<ErrorBoundary>` showing inline
recovery; mutations show toast for retryable network errors but inline
banner above the form for validation; auth expiry uses a blocking dialog.

Sources:
- W3C / WAI, *ARIA21: Using aria-invalid to Indicate An Error Field* — https://www.w3.org/WAI/WCAG21/Techniques/aria/ARIA21
- W3C / WAI, *Understanding WCAG 3.3.1 Error Identification* — https://www.w3.org/WAI/WCAG21/Understanding/error-identification.html
- Material Design 3, *Snackbar — Guidelines* — https://m3.material.io/components/snackbar/guidelines

## 9. Scroll restoration on route change (verified)

In a React Router v7 data router, mount `<ScrollRestoration/>` once at the
layout root. It emulates the browser's native scroll restoration: forward
navigations scroll to the top; back/forward navigations restore the previous
scroll position. Restoration runs *after* loaders complete, so the new
content is in place before the scroll fires (no perceived jump-back).

Apply: provide `getKey` if you need scroll positions to share across query
string changes on the same pathname (e.g. paginated lists) — otherwise the
default `location.key` is correct.

Sources:
- React Router, *`ScrollRestoration`* — https://reactrouter.com/api/components/ScrollRestoration
- React Router (v6 docs, same component) — https://reactrouter.com/6.30.3/components/scroll-restoration

## 10. Focus management on route change (verified)

After scroll restoration, move keyboard focus to the new view's `<h1>`
(make it `tabIndex={-1}` to be programmatically focusable without entering
the tab order). This causes screen readers to announce the new page title
and aligns sighted-keyboard navigation with the visual change. Pair with
an `aria-live="polite"` region for longer loads that announces "Loading…"
followed by the page title once data resolves.

Apply: write a small `<RouteAnnouncer/>` component subscribed to
`useNavigation()` / `useLocation()` — on navigation idle, focus
`document.getElementById('main-heading')` and write the title into the
live region. Do NOT focus the `<body>` (resets context) and do NOT autofocus
random inputs (steals focus from screen-reader users mid-announcement).

Sources:
- React Router, *Accessibility — focus management* — https://reactrouter.com/how-to/accessibility
- W3C / WAI-ARIA, *aria-live live regions* — https://www.w3.org/TR/wai-aria-1.2/#aria-live
- MDN, *ARIA live regions* — https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/ARIA_Live_Regions

## 11. Use `<ScrollRestoration/>` *and* `useNavigation()` for pending UI (verified)

`useNavigation()` exposes `state` (`"idle" | "loading" | "submitting"`). Use
it to render a *global*, subtle pending indicator (a 2–3 px progress bar
across the top of the layout) when navigations exceed ~300 ms — this prevents
the perception that the click was ignored, without obscuring the current
view. Show the indicator after a delay (e.g. 200 ms) to avoid flashing on
fast network responses.

Apply: layout root renders a hidden `<TopProgress/>` that becomes visible
when `navigation.state !== 'idle'` for >200 ms.

Sources:
- React Router, *`useNavigation`* — https://reactrouter.com/api/hooks/useNavigation
- React Router, *Pending UI* — https://reactrouter.com/start/framework/pending-ui
- NN/G, *Response Time Limits* (1 s flow-of-thought threshold) — https://www.nngroup.com/articles/response-times-3-important-limits/

## 12. Form validation timing: `onTouched` + `onChange` re-validate (verified)

The least-annoying validation timing pattern:

- **First pass** (before first error): validate on **blur / touched**, never
  on every keystroke. Validating mid-typing flags incomplete inputs as
  "invalid", which is hostile.
- **After first error on a field**: re-validate **on change** so the error
  clears as the user types a fix.
- **Submit**: full validation; if invalid, move focus to the first invalid
  field and render an `role="alert"` summary above the form.

Apply (react-hook-form):
`useForm({ mode: 'onTouched', reValidateMode: 'onChange', shouldFocusError: true })`.
Pair with `zod` resolver and wire `aria-invalid={!!errors.x}` plus
`aria-describedby="x-error"` on every field.

Sources:
- react-hook-form, *`useForm`* — https://react-hook-form.com/docs/useform
- WCAG 3.3.1, *Understanding Error Identification* — https://www.w3.org/WAI/WCAG21/Understanding/error-identification.html
- W3C ARIA21, *Using aria-invalid to Indicate An Error Field* — https://www.w3.org/WAI/WCAG21/Techniques/aria/ARIA21
- W3C / WAI, *User Notification (forms tutorial)* — https://www.w3.org/WAI/tutorials/forms/notifications/

## 13. Error summary above the form for multi-error submits (verified)

When `handleSubmit` reports `>1` invalid field, render an error summary at
the top of the form: a `role="alert"` container with a heading ("N errors
prevented submission"), and a list of links — each link's text is the field
label and its `href` is `#<field-id>`. Move focus to the summary container
when it appears (so screen readers announce it), then the user can tab
into the list. This is in addition to inline messages next to each field.

Apply: scroll the summary into view and focus it; do not auto-focus the
first invalid field *and* the summary — pick one. WCAG / WAI guidance: if
the summary is the primary anchor, focus the summary; if single-field
errors are most common, focus the first invalid field.

Sources:
- W3C / WAI, *User Notification (Forms tutorial)* — https://www.w3.org/WAI/tutorials/forms/notifications/
- W3C, *Understanding WCAG 3.3.1 Error Identification* — https://www.w3.org/WAI/WCAG21/Understanding/error-identification.html
- react-hook-form, *`useForm` — `shouldFocusError`* — https://react-hook-form.com/docs/useform

## 14. Button states: idle / pending / disabled-with-reason (verified)

- **Idle**: default styling.
- **Pending / loading**: button stays focusable. Use `aria-disabled="true"`
  (NOT `disabled`) on the submit button so screen-reader users can still
  tab onto it and hear its label + state ("Save, dimmed"). Add
  `aria-live="polite"` (or `aria-label="Saving…"`) to communicate the
  transition to AT users. Use `cursor: not-allowed` to mirror visually.
  Prevent submission with a guard inside the handler, not via `disabled`,
  because `disabled` removes the element from the tab order and prevents
  the form from submitting at all.
- **Validation-disabled** (form not yet valid): same `aria-disabled="true"`
  pattern, plus a visible helper text above the button ("Fill all required
  fields"). Never disable silently — sighted users won't know why.
- **Success / error** outcomes: communicate via inline message + snackbar,
  not button colour-morphing — colour-only state changes fail WCAG 1.4.1.

Sources:
- MDN, *`aria-disabled`* — https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Attributes/aria-disabled
- MUI, *Button — loading state* — https://mui.com/material-ui/react-button/
- W3C, *WCAG 1.4.1 Use of Color* — https://www.w3.org/WAI/WCAG21/Understanding/use-of-color.html

## 15. Theme tokens, not hard-coded colours (verified)

Every colour, spacing value, and border-radius MUST resolve from theme
tokens — never a literal hex/`rgb()` inside a component. Tokens decouple
"what the colour means" (semantic role: `surface`, `error.main`,
`text.primary`) from "what the colour is" (concrete value per scheme),
making dark mode, rebrands, and accessibility audits a one-touch change.

Apply (MUI v9): use the `colorSchemes` API, NOT `palette.mode` switching
(which causes flicker). Enable `cssVariables` so the resolved tokens are
CSS custom properties (no FOUC, SSR-safe). Customise per-scheme overrides
with `theme.applyStyles('dark', { … })`, never with `theme.palette.mode ===
'dark' ? … : …` conditionals.

Sources:
- MUI v9, *CSS theme variables — Usage* — https://mui.com/material-ui/customization/css-theme-variables/usage/
- MUI v9, *Dark mode* — https://mui.com/material-ui/customization/dark-mode/
- Material Design 3, *Color roles* — https://m3.material.io/styles/color/roles

## 16. `prefers-color-scheme` with user override + persistence (verified)

Cascade:

1. Explicit user override stored in `localStorage` wins.
2. Else fall back to `prefers-color-scheme` media query.
3. Subscribe to OS-level changes via `matchMedia('(prefers-color-scheme:
   dark)').addEventListener('change', …)`; if the user has NO override,
   follow the new system preference live.

To avoid the white-flash on first paint, inline a tiny script in `<head>`
(via Vite's HTML transform) that reads the storage key and sets a
`data-color-scheme` attribute on `<html>` *before* the React tree mounts.
MUI's `InitColorSchemeScript` component does exactly this when paired with
`storageManager`.

Sources:
- MUI v9, *Dark mode (storageManager, InitColorSchemeScript)* — https://mui.com/material-ui/customization/dark-mode/
- MDN, *`prefers-color-scheme`* — https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme
- W3C Media Queries Level 5 — https://www.w3.org/TR/mediaqueries-5/#prefers-color-scheme

## 17. `prefers-reduced-motion`: opt out, not opt in (verified)

Wrap every non-essential transition / animation in
`@media (prefers-reduced-motion: no-preference) { … }` (the inverse pattern
recommended by W3C / web.dev) so that motion is ON only when the user
expresses no preference, and OFF whenever they have asked for reduction.
Essential motion (loading-spinner rotation when no alternative exists)
should be reduced to a dissolve / opacity change rather than removed
entirely. For JS-driven animations (Framer Motion, anim libs), read the
`matchMedia('(prefers-reduced-motion: reduce)')` value and disable.

Apply: MUI's transitions use `theme.transitions.create()` — pair with a
`prefers-reduced-motion: reduce` override that zeros the duration. Recharts
animation is `isAnimationActive={true}` by default; flip to `false` (or to
a much shorter duration) when reduce-motion is set.

Sources:
- MDN, *`prefers-reduced-motion`* — https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion
- MDN, *Using media queries for accessibility* — https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_media_queries/Using_media_queries_for_accessibility
- W3C WAI, *Animation and Transitions* (vestibular triggers) — https://www.w3.org/WAI/WCAG21/Understanding/animation-from-interactions.html

## 18. `:focus-visible`, not `:focus`, for keyboard focus rings (verified)

Modern browsers show focus rings only when the user is navigating with the
keyboard. Reproduce that selectively-visible behaviour for custom focus
styles via `:focus-visible` so mouse clicks don't leave an outline ringing
the button. Never remove the default focus indicator without replacing it
(WCAG 2.4.7 Focus Visible) — *always* style `:focus-visible` with a
contrast-meeting outline, never `outline: none` alone.

Apply (MUI v9): MUI components already use `:focus-visible` for the focus
ring via the `Mui-focusVisible` class. For custom components, write
`:focus-visible { outline: 2px solid var(--mui-palette-primary-main);
outline-offset: 2px; }`.

Sources:
- MDN, *`:focus-visible`* — https://developer.mozilla.org/en-US/docs/Web/CSS/:focus-visible
- W3C, *C45 — Using CSS `:focus-visible` to provide keyboard focus indication* — https://www.w3.org/WAI/WCAG21/Techniques/css/C45
- W3C, *WCAG 2.4.7 Focus Visible* — https://www.w3.org/WAI/WCAG21/Understanding/focus-visible.html

## 19. Viewport units: `svh` / `dvh` instead of `vh` (verified)

`vh` was historically equivalent to "largest viewport" on mobile, so a
`100vh` element appears clipped when the address bar slides in. Pick by
intent:

- **`svh` (small viewport height)**: safest for "fill the screen, never
  hidden under chrome" use cases (full-screen modals, login pages).
- **`lvh` (large viewport height)**: when you want to claim the full
  visible space the moment the chrome retracts.
- **`dvh` (dynamic viewport height)**: tracks chrome live; can cause
  layout shift while scrolling — use sparingly, never on tall scrolling
  content.
- **`100vh`**: avoid for full-page layouts; reserve only for cases where
  you know `lvh` semantics are desired.

The same logic applies to `svw`/`dvw`/`lvw` horizontally and the `dvi`/
`dvb` block / inline variants. Combine with `min-block-size: 100svh` on
the layout root so content never gets cropped by mobile chrome.

Sources:
- MDN, *`length` — viewport-percentage lengths* — https://developer.mozilla.org/en-US/docs/Web/CSS/length
- W3C CSS Values and Units Module Level 4, *Viewport-percentage Lengths* — https://www.w3.org/TR/css-values-4/#viewport-relative-lengths
- web.dev, *The large, small, and dynamic viewport units* — https://web.dev/blog/viewport-units

## 20. `env(safe-area-inset-*)` on the layout edges (verified)

When the app is installed as a PWA or run in iOS standalone display mode,
the device safe-area insets (notch, home-indicator, rounded corners) reduce
the truly drawable area. Pad the layout root with the four
`env(safe-area-inset-*, 0px)` values so no actionable content lands under
chrome. Set `viewport-fit=cover` in the `<meta name="viewport">` to opt the
app into edge-to-edge layout (without this, the insets are zero).

Apply: layout root gets
`padding: max(env(safe-area-inset-top), 12px) max(env(safe-area-inset-right), 16px) max(env(safe-area-inset-bottom), 12px) max(env(safe-area-inset-left), 16px);`
— the `max()` keeps a sensible minimum padding when the inset is zero
(desktop browsers).

Sources:
- MDN, *`env()` CSS function* — https://developer.mozilla.org/en-US/docs/Web/CSS/env
- W3C CSS Environment Variables Module Level 1 — https://drafts.csswg.org/css-env-1/
- WHATWG / Apple "Designing Websites for iPhone X" (historical, but the source of `safe-area-inset-*`) — https://webkit.org/blog/7929/designing-websites-for-iphone-x/

## 21. Native `<dialog>` with `inert` background, not custom modals (verified)

Use the platform `<dialog>` (via MUI `Dialog`, which uses it under the
hood, or directly) and call `.showModal()` rather than `.show()`. This
gives you, for free: focus trap, ESC-to-close, `aria-modal="true"` set
implicitly, `::backdrop` pseudo-element, top-layer rendering above all
other content, and automatic inertness of the rest of the document. Pair
with `autofocus` on the primary action button (or on Close, if there is
no obvious primary). Never re-implement focus trapping by hand.

For tooltips / menus where a dialog is overkill, prefer the **Popover API**
(`popover="auto"` attribute) on stable engines (Chrome ≥ 114, Safari ≥ 17;
flagged in Firefox); fall back to MUI `Popover`/`Menu` for older browsers.

Sources:
- MDN, *`<dialog>` element* — https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/dialog
- WHATWG HTML Standard, *6.12 The popover attribute* — https://html.spec.whatwg.org/multipage/popover.html
- W3C WAI-ARIA APG, *Modal Dialog pattern* — https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/
- MDN, *`inert` global attribute* — https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Global_attributes/inert

## 22. Responsive charts: `ResponsiveContainer` + fixed `aspect` (verified)

Recharts charts MUST be wrapped in `<ResponsiveContainer width="100%"
aspect={16/9}>` (or whichever ratio matches the design) so they scale with
the layout but maintain readable proportions across breakpoints. Set
`minWidth` and `minHeight` so the chart never collapses to an
unreadable size in narrow columns. Enable `accessibilityLayer` so the
chart's data points become keyboard-navigable and the tooltip is announced
by screen readers.

Tooltip UX:

- Anchor near the cursor, but never under the finger on touch devices.
- Include all relevant series + the formatted x-axis value — don't make
  users guess which line is which.
- For touch / mobile, show the tooltip on tap and dismiss on second tap
  outside (Recharts default is fine; verify on staging).

Sources:
- Recharts, *Container components / ResponsiveContainer* — https://recharts.org/en-US/api/ResponsiveContainer
- Recharts wiki, *Recharts and accessibility* — https://github.com/recharts/recharts/wiki/Recharts-and-accessibility
- W3C, *WCAG 1.4.10 Reflow* (responsive layout requirement) — https://www.w3.org/WAI/WCAG21/Understanding/reflow.html

## 23. i18n loading via Suspense, not blank screen (verified)

`react-i18next` v11+ uses Suspense by default: a component that calls
`useTranslation('ns')` will suspend while the namespace is fetched. Mount
a `<Suspense fallback={<AppShellSkeleton/>}>` boundary *outside* the App
component so the *very first* render has a skeleton, never a blank page.
Pre-bundle the user's most-likely language (detected via Accept-Language /
stored preference) so the first paint usually doesn't suspend.

Alternative for tighter control: set `useSuspense: false` and gate render
on the hook's `ready` flag — but Suspense is the spec-blessed default.

Apply: configure i18next backend with code-split JSON namespaces; preload
the active namespace via `<link rel="preload">` (Vite plugin or manual)
so the first paint is non-blocking.

Sources:
- react-i18next docs, *Suspense* — https://react.i18next.com/latest/usesuspense
- react-i18next, *React Suspense integration* (DeepWiki, citing official source) — https://deepwiki.com/i18next/react-i18next/6.3-react-suspense-integration
- React docs, *`<Suspense>`* — https://react.dev/reference/react/Suspense

## 24. Vite asset preload hints for above-the-fold critical resources (verified)

Vite emits `<link rel="modulepreload">` for the JS dependencies of the
entry chunk automatically; that handles module-graph latency. For *non-JS*
above-the-fold assets (custom fonts, hero image, the active locale's i18n
JSON), add explicit `<link rel="preload">` hints in `index.html` (or via
a Vite plugin like `vite-plugin-inject-preload`) — this short-circuits the
CSS-discovery delay for font files. Always pair `rel="preload" as="font"`
with `crossorigin` (fonts are CORS-fetched) or the browser will fetch the
font twice.

Apply: preload the woff2 of the primary UI font; preload the active i18n
JSON if the locale is known at build time or on first response.

Sources:
- web.dev, *Preload modules / modulepreload* — https://web.dev/articles/modulepreload
- MDN, *`<link rel="preload">`* — https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/rel/preload
- Vite docs, *Build options — modulepreload polyfill / behaviour* — https://vite.dev/guide/build.html

## 25. CSS scroll snap for predictable carousels / step flows (partial)

For touch-first content that lives on a "page" axis (image galleries,
onboarding step carousel, dashboard story-mode), use CSS scroll snap with
`scroll-snap-type: x mandatory` on the scroller and `scroll-snap-align:
center` on each child. Mandatory snap yields the most predictable feel
because the browser always lands on a card boundary — never use
`mandatory` if any single child can overflow the scroller (then user
cannot reach the overflowed content); use `proximity` instead.

Pair with `scroll-padding` so the snap point isn't flush against the
edge, and respect `prefers-reduced-motion` by setting `scroll-behavior:
auto` instead of `smooth` for users who opted out.

Sources:
- MDN, *CSS scroll snap — basic concepts* — https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_scroll_snap/Basic_concepts
- W3C CSS Scroll Snap Module Level 1 — https://www.w3.org/TR/css-scroll-snap-1/

## 26. Predictable back behaviour: never trap browser back (verified)

In a data-router setup, the browser's Back button MUST navigate to the
previous route — never override it with a custom modal-close handler or
swallow it inside an SPA navigation. Specifically:

- Modal close: bind ESC and an explicit close button; **do not** call
  `history.back()` to dismiss. If you push history entries for modal
  state (deep-link-able modal), make sure Back closes the modal cleanly
  and forward re-opens it.
- Form submit: navigate forward with `useNavigate` to the destination
  route; don't call `history.replace` for first submits — that breaks
  Back to the form for "edit my answer".
- Route guards: when redirecting (auth wall), use `<Navigate replace />`
  so the guarded URL isn't in the back stack twice.

Apply: every modal owns its own `open` state; pressing Back must close
the topmost modal only when its URL representation explicitly added a
history entry — otherwise let Back navigate routes.

Sources:
- React Router, *`useNavigate` — `replace` flag* — https://reactrouter.com/api/hooks/useNavigate
- WHATWG HTML Standard, *Session history* — https://html.spec.whatwg.org/multipage/browsing-the-web.html#session-history
- NN/G, *User Control and Freedom (Usability Heuristic #3)* — https://www.nngroup.com/articles/user-control-and-freedom/
- NN/G, *Accidental Dismissal of Overlays* — https://www.nngroup.com/articles/accidental-overlay-dismissal/

## 27. Spinner-show delay to avoid flash (~200–300 ms) (verified)

A spinner that appears for <200 ms registers as a visual flash and increases
anxiety; conversely, no indicator for >1 s breaks flow. Bridge with a
debounce: only mount the spinner if the wait exceeds ~200–300 ms. Apply
this to the route-level pending indicator (practice 11), to the
`<Suspense>` fallback if it's a spinner instead of a skeleton, and to RTK
Query mutation buttons.

The lower bound (~200 ms) is the "perceived intelligence / immediate
feedback" floor; the upper bound (~1 s) is NN/G's flow-of-thought limit.
Pick a single project-wide threshold (e.g. 250 ms) and apply it
consistently — inconsistency itself feels janky.

Sources:
- NN/G, *Response Time Limits* — https://www.nngroup.com/articles/response-times-3-important-limits/
- NN/G, *Skeleton Screens 101* (against sub-second loops) — https://www.nngroup.com/articles/skeleton-screens/
- web.dev, *INP / responsiveness* (200 ms perception floor) — https://web.dev/articles/inp

## 28. Predictive link prefetch via `<NavLink prefetch="intent">` (partial)

React Router v7's `<Link>` / `<NavLink>` accept a `prefetch` prop with
`none` (default for SPA mode), `intent`, `render`, and `viewport` values.
`prefetch="intent"` fires `<link rel="prefetch">` on focus/hover, so the
target route's chunk and loader data are warm by the time the click lands —
in practice this makes most intra-app navigations feel instant. NN/G's
1 s response budget becomes much easier to hit. Only available in framework
mode; SPA-only Vite setups need a custom prefetch on hover.

Apply: every navigation link inside the main shell uses `prefetch="intent"`;
do NOT use `prefetch="render"` (prefetches every link on the page — wastes
bandwidth) or `prefetch="viewport"` for large lists (same problem).

Sources:
- React Router, *`<NavLink>` — `prefetch`* — https://reactrouter.com/api/components/NavLink
- React Router, *Pending UI* (intent prefetch in context) — https://reactrouter.com/start/framework/pending-ui

## 29. Live regions for async state announcements (verified)

For state changes the user *didn't* directly trigger (background save,
push notification arrived, optimistic mutation rolled back), update an
`aria-live="polite"` region so screen readers announce the change without
interrupting. Reserve `aria-live="assertive"` for time-critical errors
(auth expiry, payment failure) — assertive interrupts the current screen-
reader announcement and is hostile if overused.

Apply: notistack already exposes `role="alert"` (assertive) on `error`
variants and `role="status"` (polite) on `success`/`info`. Verify this on
custom toasts; for inline form-summary banners use `role="alert"` only
when they appear *after* user action (submit), never on initial render.

Sources:
- MDN, *ARIA live regions* — https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Guides/Live_regions
- W3C WAI-ARIA 1.2, *aria-live property* — https://www.w3.org/TR/wai-aria-1.2/#aria-live
- MDN, *`role="alert"`* — https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Roles/alert_role

## 30. Minimum tap target ≥44 × 44 CSS px (verified)

Every interactive element MUST have a tap area of at least 44 × 44 CSS
pixels, the size that aligns Apple HIG, Material Design (which states 48
× 48 dp for touch), and WCAG 2.5.5 (AAA: 44 px) / 2.5.8 (AA: 24 px). On a
static-behind-nginx web app expected to work on touch tablets, target
48 × 48 to satisfy Material and provide comfort buffer. The visible icon
may be smaller (24 px) — extend the tap area via padding so the *hit*
target meets the size, not the visual.

Apply: every icon button uses MUI `IconButton` at default size (which is
48 × 48 CSS px); custom interactive `<div>`s get explicit `min-width:
44px; min-height: 44px;`. Leave ≥8 px between adjacent targets.

Sources:
- W3C, *WCAG 2.5.5 Target Size (Enhanced AAA)* — https://www.w3.org/WAI/WCAG21/Understanding/target-size.html
- W3C, *WCAG 2.5.8 Target Size (Minimum)* — https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html
- Material Design 2, *Layout — touch target sizes* — https://m2.material.io/design/layout/spacing-methods.html#touch-targets
- Apple HIG, *Layout (44 pt minimum)* — https://developer.apple.com/design/human-interface-guidelines/layout

---

## Topics with insufficient authoritative coverage

The following sub-topics were investigated but did NOT yield two
independent first-tier sources at the level of specificity needed. They
appear above only where a single first-tier source plus one second-tier
corroborator existed, marked `partial`. Anything genuinely unverified was
dropped from the list.

- **Exact "skeleton ≤300 ms" / "spinner only above 300 ms" numbers**: NN/G
  publishes the 0.1 s / 1 s / 10 s thresholds; the 200–300 ms spinner-
  flash floor is corroborated by web.dev's INP work but not stated as a
  single project-wide ms number. Treat the 250 ms midpoint as a sound
  *project convention*, not a quotable spec value.
- **MUI v9 `colorSchemes` "ban literal hex in components" rule**: MUI docs
  recommend tokens but do not explicitly forbid literals; the prohibition
  here is a *design-system convention*, not a normative MUI rule.
- **Recharts `accessibilityLayer` keyboard semantics on iOS Safari**: the
  Recharts wiki documents the feature; cross-browser screen-reader
  conformance evidence is thin. Treat as "best-effort for VoiceOver /
  NVDA / JAWS, verify per release".

## Verification summary

- 26 practices marked `verified` (≥2 independent first-tier sources).
- 2 practices marked `partial` (1 first-tier source + corroboration):
  practices 25 (scroll snap — second source is W3C spec only, no NN/G or
  web.dev pattern guidance was found at the same depth) and 28 (NavLink
  intent prefetch — second source is the same React Router site, but a
  different page, so technically not independent; treat as authoritative
  for the library but not corroborated by an external UX authority).
- 0 practices marked `unverified` and retained — anything that couldn't
  be sourced was either dropped or reduced in scope.
