# Accessibility (a11y) Research — Webview-UI Stack

## Methodology

- **Target standard:** WCAG 2.2 Level AA (the conformance level most regulators reference). All "MUST" practices below are anchored either to a numbered WCAG 2.2 success criterion or to a normative ARIA Authoring Practices Guide (APG) pattern.
- **Source rule:** every practice cites at least two independent authoritative sources. Acceptable sources used here are W3C/WAI (WCAG, APG, ACT-rules), MDN, WebAIM, Deque, web.dev, the A11y Project, official MUI / MUI X / React / React Router / react-hook-form / i18next / recharts / vitest-axe project docs and issue trackers. Where two sources could not be obtained the entry is marked `unverified` or dropped.
- **Stack scope:** React 19, Vite 8 (client-only), MUI v9, `@mui/x-date-pickers`, `@mui/x-tree-view`, React Router v7, `react-hook-form` + `zod`, `notistack`, `react-i18next`, `recharts`, `vitest-axe` + `@testing-library/user-event`. Browser context only — no SSR concerns.
- **Confidence labels:** `verified` = two or more independent authoritative sources cited. `partial` = a normative source plus a single library-doc / community-doc source. `unverified` = single source or only inference; flagged for spec-input review.
- **Out of scope:** native mobile a11y, PDF a11y, video captioning workflows, design-token color systems beyond MUI's `contrastThreshold` knob.

## Best practices

### BP-01 — Use semantic HTML landmarks (`<header>`, `<nav>`, `<main>`, `<footer>`, `<aside>`) once per page

**MUST.** Wrap top-level page regions in the corresponding HTML5 sectioning element instead of generic `<div>`s. Screen-reader users navigate by landmark; the landmarks must be present, unique, and direct children of `<body>` (or otherwise top-level in the document) for assistive tech to expose them. When there is more than one `<nav>`, each MUST carry an `aria-label` / `aria-labelledby` to disambiguate.

- W3C WCAG 2.1 technique H101 — "Using semantic HTML elements to identify regions of a page" (https://www.w3.org/WAI/WCAG21/Techniques/html/H101)
- WebAIM — "Semantic Structure: Regions, Headings, and Lists" (https://webaim.org/techniques/semanticstructure/)
- MDN — "Using HTML landmark roles to improve accessibility" (https://developer.mozilla.org/en-US/blog/aria-accessibility-html-landmark-roles/)

Confidence: verified.

### BP-02 — Exactly one visible `<h1>` per route, no skipped heading levels

**MUST.** Each route/page renders a single `<h1>` that names the page; sub-sections use `<h2>` … `<h6>` in document order without gaps. Screen-reader users navigate by heading; missing or duplicated H1s and skipped levels break the page outline.

- MDN — Heading elements reference: "A page should generally have a single `<h1>` element … Do not skip heading levels: always start from `<h1>`, followed by `<h2>` and so on." (https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/Heading_Elements)
- WebAIM — "Semantic Structure: Regions, Headings, and Lists" (https://webaim.org/techniques/semanticstructure/)
- The A11y Project — "How to use headings in HTML" (https://www.a11yproject.com/posts/how-to-accessible-heading-structure/)

Confidence: verified.

### BP-03 — Keep `<html lang>` and `<html dir>` in sync with the i18next active language

**MUST.** Set `lang` to a BCP-47 tag on the `<html>` element (WCAG 2.2 SC 3.1.1 Language of Page, Level A). When the user switches language via react-i18next, mutate `document.documentElement.lang` and `document.documentElement.dir` (use `i18next.dir(lng)`) on every `languageChanged` event. Without this, screen readers mispronounce content and RTL languages render LTR.

- W3C WCAG 2.1 H57 — "Using the language attribute on the HTML element" (https://www.w3.org/WAI/WCAG21/Techniques/html/H57)
- W3C — "Understanding Success Criterion 3.1.1: Language of Page" (https://www.w3.org/WAI/WCAG21/Understanding/language-of-page.html)
- i18next — `react-i18next` issue #925 on syncing `<html lang>` / `<html dir>` via `i18n.dir()` and the `languageChanged` event (https://github.com/i18next/react-i18next/issues/925)

Confidence: verified.

### BP-04 — Provide a "skip to main content" link as the first focusable element

**MUST.** A skip link, visually hidden but focusable, must be the first item in the tab order. It must move focus to `<main>` (or an element with `tabindex="-1"` inside it). Hiding via `display:none` or the `hidden` attribute removes it from the tab order and is forbidden; offscreen positioning that re-appears on `:focus` is the canonical pattern.

- WebAIM — "Skip Navigation Links" (https://webaim.org/techniques/skipnav/)
- The A11y Project — "How-to: Use skip navigation links" (https://www.a11yproject.com/posts/skip-nav-links/)
- W3C WCAG 2.2 SC 2.4.1 Bypass Blocks (https://www.w3.org/WAI/WCAG22/Understanding/bypass-blocks.html)

Confidence: verified.

### BP-05 — Move focus on React Router v7 route change (shift focus to a non-landmark element near the new `<h1>`)

**MUST.** SPA navigation does not naturally reset focus the way full-page loads do, leaving keyboard and screen-reader users stranded. On every route change, focus must move either to (a) the main content container with `tabindex="-1"`, or (b) the new `<h1>` with `tabindex="-1"`. Do NOT focus a landmark element (the SR will read its entire contents). Do NOT focus a link/button (it triggers spurious announcements).

- React Router discussion #9863 — "SPA Accessibility - focus not reset when route changed" (https://github.com/remix-run/react-router/discussions/9863)
- Up Your A11y — "Handling Focus on Route Change in React" (https://www.upyoura11y.com/handling-focus/)
- WCAG 2.2 SC 2.4.3 Focus Order, Level A (https://www.w3.org/WAI/WCAG22/Understanding/focus-order.html)

Confidence: verified.

### BP-06 — Never set `outline: none` (or `outline: 0`) on focusable elements; use `:focus-visible` for custom styling

**MUST.** Removing the default focus ring without supplying a replacement is the canonical WCAG 2.4.7 failure (technique F78). Use `:focus-visible` to scope custom focus styling to keyboard-induced focus and keep mouse focus quiet; the replacement indicator must meet 3:1 non-text contrast (1.4.11) and the WCAG 2.2 SC 2.4.13 Focus Appearance perimeter rule.

- W3C — Understanding SC 2.4.7 Focus Visible (https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html)
- W3C — F78 Failure technique (https://www.w3.org/WAI/WCAG21/Techniques/failures/F78)
- MDN — `:focus-visible` reference: "The `:focus-visible` pseudo-class respects user agents' selective focus indication behavior while still allowing focus indicator customization." (https://developer.mozilla.org/en-US/docs/Web/CSS/:focus-visible)

Confidence: verified.

### BP-07 — MUI `Dialog`/`Modal` MUST carry `aria-labelledby` (and ideally `aria-describedby`); leave focus trap and return-focus enabled

**MUST.** The MUI Dialog trap-focus, initial-focus and return-focus machinery is on by default — do NOT set `disableEnforceFocus`, `disableAutoFocus`, or `disableRestoreFocus` for routine dialogs. The dialog must reference its own title via `aria-labelledby="<title-id>"`; long-form dialog body content should be referenced via `aria-describedby="<body-id>"`. After close, focus must return to the triggering control.

- MUI — `Modal` React component docs (accessibility section: "You should add `aria-labelledby="id..."`, referencing the modal title, to the Modal. Additionally, you may give a description of your modal with the `aria-describedby="id..."` prop") (https://mui.com/material-ui/react-modal/)
- W3C APG — Dialog (Modal) pattern (focus trap, initial focus, return focus rules) (https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/)
- MUI issue #46682 — known return-focus regressions; reinforces that the default focus-restore behavior is the supported a11y path (https://github.com/mui/material-ui/issues/46682)

Confidence: verified.

### BP-08 — Icon-only MUI `IconButton` MUST carry `aria-label`; `Tooltip` is not a replacement for the label

**MUST.** Every `IconButton` whose visible content is only an icon needs an `aria-label` describing the action (or wraps text via `<VisuallyHidden>`). A `Tooltip` provides a *description*, not a *name*; setting only `title`/tooltip text without `aria-label` leaves the control nameless for screen-reader users in many AT/browser combinations. WCAG 4.1.2 Name, Role, Value (Level A) requires a programmatic accessible name for all UI controls.

- MUI — Button / IconButton docs: "All Buttons must have a meaningful aria-label so their purpose can be understood by users who require assistive technology" (https://mui.com/material-ui/react-button/)
- W3C — Understanding SC 4.1.2 Name, Role, Value (https://www.w3.org/WAI/WCAG21/Understanding/name-role-value.html)
- Deque — "Building Accessible Buttons with ARIA" (https://www.deque.com/blog/accessible-aria-buttons/)

Confidence: verified.

### BP-09 — Wire react-hook-form errors into inputs via `aria-invalid` + `aria-describedby` + `role="alert"` on the error node

**MUST.** For every controlled or registered input:
1. Set `aria-invalid={!!errors.field}`.
2. Set `aria-describedby` to the id of the error element (preferably generated via `useId()`).
3. Render the error element with `role="alert"` (which implies `aria-live="assertive"` + `aria-atomic="true"`) so that newly-rendered messages are announced.

`shouldUseNativeValidation` is NOT enabled by default in react-hook-form, so these attributes must be authored manually.

- react-hook-form — Advanced Usage / FAQs on `aria-invalid` and accessibility (https://react-hook-form.com/advanced-usage)
- W3C ARIA19 — "Using ARIA role=alert or Live Regions to Identify Errors" (https://www.w3.org/WAI/WCAG22/Techniques/aria/ARIA19)
- MDN — `aria-describedby` reference (https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-describedby)

Confidence: verified.

### BP-10 — Generate input IDs via React 19 `useId()` so `<label htmlFor>` always binds to the right input

**MUST.** Hand-rolled `Math.random()`/counter IDs collide across re-renders and across SSR boundaries. `useId()` returns a stable, unique id; it is the React-canonical way to bind a `<label>` to its input. Even with MUI's `TextField` that auto-generates internal IDs, hand-authored helper text and error nodes still need stable IDs to reference via `aria-describedby`.

- React — `useId` reference: "`useId` lets a component associate a unique ID with itself, typically used with accessibility APIs" (https://react.dev/reference/react/useId)
- MDN — `<label>` element reference; explicit association via `for`/`id` is preferred (https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/label)
- W3C — Understanding SC 3.3.2 Labels or Instructions (https://www.w3.org/WAI/WCAG21/Understanding/labels-or-instructions.html)

Confidence: verified.

### BP-11 — Use notistack as a polite live region (`role="status"` / `aria-live="polite"`), reserve `role="alert"` for true errors

**SHOULD.** Toast notifications must be programmatically announced (WCAG 2.2 SC 4.1.3 Status Messages, Level AA). Most toasts (save success, info) are non-urgent — use `role="status"` or `aria-live="polite"`. Reserve `role="alert"` (which implies `aria-live="assertive"`) for messages that must interrupt the screen reader (e.g. failed save, destructive action confirmation). When a toast is dismissable, the close control must be a real `<button>` with an `aria-label="Dismiss"` and focus must NOT be auto-stolen by the toast.

- W3C — Understanding SC 4.1.3 Status Messages (https://www.w3.org/WAI/WCAG21/Understanding/status-messages.html)
- MDN — ARIA live regions guide (https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Guides/Live_regions)
- MDN — `role="alert"`: "Setting role=\"alert\" is equivalent to setting aria-live=\"assertive\" and aria-atomic=\"true\"" (https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Roles/alert_role)

Confidence: verified.

### BP-12 — Configure the MUI theme's `palette.contrastThreshold` to target WCAG AA (≥ 4.5:1 for body text)

**SHOULD.** MUI's default `contrastThreshold` of `3` only enforces a 3:1 ratio between `*.main` and `*.contrastText`, which is *not enough* for body-size text (WCAG 1.4.3 demands 4.5:1). Set `palette.contrastThreshold: 4.5` in the theme, and verify the resulting `contrastText` choices against WebAIM's contrast checker. Even after that, custom palettes need spot-checking — MUI documents that the threshold is heuristic, not guaranteed.

- MUI — Palette docs: "Material UI currently only enforces a 3:1 contrast ratio. If you would like to meet WCAG 2.2 Level AA compliance, you can increase your minimum contrast ratio" (https://mui.com/material-ui/customization/palette/)
- W3C — Understanding SC 1.4.3 Contrast (Minimum) (https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html)
- WebAIM — Contrast and Color Accessibility article (https://webaim.org/articles/contrast/)

Confidence: verified.

### BP-13 — Respect `prefers-reduced-motion` for every CSS / JS animation; treat motion as opt-out

**MUST.** Wrap non-essential motion (page transitions, parallax, large MUI `Slide`/`Grow`/`Zoom` transitions, recharts animation defaults) in `@media (prefers-reduced-motion: reduce)` blocks that disable or dampen the motion (e.g. swap to opacity-only transitions or `transition: none`). WCAG 2.2 SC 2.3.3 Animation from Interactions and the broader vestibular-disorder guidance require this. For MUI components that accept transition props, pass `TransitionProps={{ timeout: 0 }}` (or substitute a reduced-motion-aware transition).

- W3C — Understanding SC 2.3.3 Animation from Interactions (https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html)
- W3C C39 — "Using the CSS prefers-reduced-motion query to prevent motion" (https://www.w3.org/WAI/WCAG22/Techniques/css/C39)
- MDN — `prefers-reduced-motion`: "Such animations can trigger discomfort for those with vestibular motion disorders" (https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion)

Confidence: verified.

### BP-14 — Honor `prefers-color-scheme` when the user has not explicitly chosen a theme

**SHOULD.** When the app has no user-selected theme preference yet, derive the initial MUI palette mode from `prefers-color-scheme` via `useMediaQuery('(prefers-color-scheme: dark)')` (or the equivalent CSS variables flow with MUI's `CssVarsProvider`). Once the user explicitly picks a theme, store it and stop following the OS preference. This avoids ambushing users who have set OS-level dark mode for low-vision or photophobia reasons.

- MDN — `prefers-color-scheme` reference (https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme)
- MUI — Dark mode / `useMediaQuery` integration guidance (https://mui.com/material-ui/customization/dark-mode/)
- web.dev — "Improve accessibility with prefers-color-scheme" / theming guide (https://web.dev/articles/prefers-color-scheme)

Confidence: verified.

### BP-15 — Never attach `onClick` to a `<div>` / `<span>` to fake a button; use `<button>` (or `<MuiButton>`)

**MUST.** A `div` with `onClick` is not in the tab order, does not fire on Enter/Space, has no implicit role, and trips axe rule `button-name`. Use a real `<button type="button">` or MUI's `Button` / `IconButton` so keyboard interaction, focus management, and the implicit `role="button"` are free. If the design absolutely requires a non-button host, `role="button"` + `tabindex="0"` + explicit `keydown` handlers for Enter and Space are all mandatory — and even then, the native element remains preferred.

- MDN — ARIA `button` role: "`role=\"button\"` controls don't work with the Enter AND Spacebar keys … because they only have a mouse-dependent onclick JavaScript event" (https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Roles/button_role)
- web.dev — Learn Accessibility: JavaScript module (https://web.dev/learn/accessibility/javascript)
- W3C — Understanding SC 2.1.1 Keyboard (Level A) (https://www.w3.org/WAI/WCAG21/Understanding/keyboard.html)

Confidence: verified.

### BP-16 — Pointer target size ≥ 24 × 24 CSS pixels (WCAG 2.2 SC 2.5.8)

**MUST.** Every interactive control's clickable/tappable area must be at least 24×24 CSS pixels, OR be spaced so a 24-pixel diameter circle centered on each undersized target does not intersect another target. MUI's default `IconButton size="small"` is borderline; verify with browser tools. The exception list (inline link in a sentence, user-agent-controlled targets, essential presentation) is short and rarely applies in app chrome.

- W3C — Understanding SC 2.5.8 Target Size (Minimum) (https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html)
- WebAIM — WCAG 2.2 Overview and Feedback (target size discussion) (https://webaim.org/blog/wcag-2-2-overview-and-feedback/)
- W3C technique C42 — Using `min-height`/`min-width` for target spacing (https://www.w3.org/WAI/WCAG22/Techniques/css/C42)

Confidence: verified.

### BP-17 — Ensure focus is not obscured by sticky headers/footers (WCAG 2.2 SC 2.4.11)

**MUST.** SC 2.4.11 Focus Not Obscured (Minimum) is Level AA. When tabbing through long forms, the focused control must remain visible and not be hidden by a sticky `AppBar`, fixed footer, or `Dialog` backdrop. Practically: ensure sticky elements use `scroll-margin-top`/`scroll-padding` equal to the bar height so that the browser scrolls focused elements into the visible portion of the viewport.

- W3C — Understanding SC 2.4.11 Focus Not Obscured (Minimum) (https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html)
- WebAIM — WCAG 2.2 Overview (focus-not-obscured rationale) (https://webaim.org/blog/wcag-2-2-overview-and-feedback/)
- MDN — `scroll-margin-top` reference (https://developer.mozilla.org/en-US/docs/Web/CSS/scroll-margin-top)

Confidence: verified.

### BP-18 — `@mui/x-tree-view` MUST carry an `aria-label` or `aria-labelledby`; rely on the built-in tree role + arrow-key navigation

**MUST.** The `<SimpleTreeView>` / `<RichTreeView>` root must be labelled — without it, screen readers announce only the generic "tree" role. The component implements the W3C APG tree pattern (arrow keys move between items, Right expands, Left collapses, Home/End jump). Do NOT swap in custom keydown handlers that override these defaults; they are spec-conforming and tested.

- MUI X — Tree View accessibility docs: "you must use aria-labelledby or aria-label to reference or provide a label on the TreeView, otherwise screen readers will announce it as 'tree'" (https://mui.com/x/react-tree-view/accessibility/)
- W3C APG — Tree View pattern (keyboard interaction & ARIA contract) (https://www.w3.org/WAI/ARIA/apg/patterns/treeview/)
- MDN — `role="tree"` reference (https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Roles/tree_role)

Confidence: verified.

### BP-19 — `@mui/x-date-pickers` — preserve built-in keyboard nav, treat picker popups as Dialog descendants

**MUST.** The pickers ship WAI-ARIA-compliant keyboard support (arrow keys to navigate days, Page Up/Down to change month/year, etc.) and the popup view uses `role="dialog"`. That means **all Dialog accessibility rules from BP-07 apply** — labelled-by, focus trap, return-focus on close. Do NOT supply a custom `<TextField>` that drops `aria-invalid` or `aria-describedby` from the picker's field slot; if customising, propagate the existing ARIA props.

- MUI X — Date and Time Pickers accessibility page (https://mui.com/x/react-date-pickers/accessibility/)
- W3C APG — Dialog (Modal) pattern (https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/)
- W3C APG — Date Picker Dialog example (referenced pattern) (https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/examples/datepicker-dialog/)

Confidence: verified.

### BP-20 — Recharts: every chart MUST have a text alternative (visible summary AND data-table fallback) and `accessibilityLayer` enabled

**MUST.** SVG charts are inert to most screen readers. Use Recharts' `accessibilityLayer` prop (added so data points become keyboard-reachable with arrow keys and read announcements), set `role="img"` and `aria-label`/`aria-labelledby` on the chart container, and render a visually accessible (or visually-hidden + `<table>`-marked-up) data-table fallback near the chart. The summary names the takeaway in plain language; the table contains the actual values.

- Recharts wiki — "Recharts and accessibility" (`accessibilityLayer`, keyboard nav, ARIA) (https://github.com/recharts/recharts/wiki/Recharts-and-accessibility)
- Deque — "How to make interactive charts accessible" (https://www.deque.com/blog/how-to-make-interactive-charts-accessible/)
- W3C — Complex Images tutorial (data-table alternative) (https://www.w3.org/WAI/tutorials/images/complex/)

Confidence: verified.

### BP-21 — Layout MUST reflow without horizontal scroll at 320 CSS px width (WCAG 2.2 SC 1.4.10)

**MUST.** At a viewport width of 320 CSS pixels (≈ 400 % zoom on a 1280-px screen) the app must not require horizontal scrolling. Use MUI's responsive Grid/Stack with `xs`-first layouts; avoid fixed-px widths on containers; allow tables and recharts containers to overflow individually rather than the whole page. Exceptions exist for inherently 2-D content (data tables, maps, charts), but they MUST be confined to their own scroll container, not the body.

- W3C — Understanding SC 1.4.10 Reflow (https://www.w3.org/WAI/WCAG21/Understanding/reflow.html)
- WebAIM — "Responsive Design and Reflow" (https://webaim.org/techniques/reflow/)
- W3C technique C32 — Using media queries and grid CSS to reflow columns (https://www.w3.org/WAI/WCAG21/Techniques/css/C32)

Confidence: verified.

### BP-22 — Disabled MUI controls are NOT exempt from being *discoverable*; prefer `aria-disabled="true"` over native `disabled` when the control should remain in the tab order

**SHOULD.** WCAG 1.4.3 explicitly exempts inactive (disabled) controls from the 4.5:1 text-contrast minimum, so MUI's washed-out disabled palette is conformant *for contrast*. However, native `disabled` removes the control from the tab order AND removes its tooltip from screen-reader announcement, so reasons-why-disabled are hidden. For controls whose disabled state needs an explanation (form gating, paywall), prefer `aria-disabled="true"` plus a styled non-interactive state plus an associated `aria-describedby` reason, instead of `disabled`.

- W3C — Understanding SC 1.4.3 Contrast (Minimum): "Text or images of text that are part of an inactive user interface component … have no contrast requirement" (https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html)
- Sarah Higley — "Disabled buttons accessibility" (canonical reference, widely cited) (https://www.sarahmhigley.com/writing/disabled-buttons/)
- MDN — `aria-disabled` attribute (https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-disabled)

Confidence: verified.

### BP-23 — Automated `vitest-axe` smoke tests on every page/component; treat them as a *floor*, not a *ceiling*

**MUST.** Add a `vitest-axe` test per page-level component that renders the component and asserts `expect(await axe(container)).toHaveNoViolations()`. This catches the bulk of structural/ARIA/label/role errors at PR time. **Critical limitation:** axe-core's color-contrast rule is disabled in JSDOM (rendered styles aren't computed), so contrast must be checked separately (Storybook a11y addon, Playwright with `@axe-core/playwright`, or manual review). Automated tools find roughly ~30 % of issues; manual keyboard / screen-reader passes are still required.

- vitest-axe — README & npm page (drop-in for jest-axe) (https://github.com/chaance/vitest-axe)
- jest-axe — README: "color contrast checks don't work in JSDOM so are turned off in jest-axe" (https://www.npmjs.com/package/jest-axe)
- Deque axe-core — rule documentation (https://github.com/dequelabs/axe-core/blob/develop/doc/rule-descriptions.md)

Confidence: verified.

### BP-24 — Use `@testing-library/user-event` (not `fireEvent`) for interactive a11y tests

**SHOULD.** `user-event` simulates the full browser input pipeline (focus/blur, pointer + keyboard, IME, hover, paste). `fireEvent` just dispatches a single synthetic event. Only `user-event` exercises the keyboard pathways and focus moves that a11y assertions depend on (`{Tab}`, `{Enter}`, `{Space}`, `{Escape}`), so it is the right tool for verifying BP-15 (keyboard activation), BP-04 (skip-link focus), BP-07 (dialog focus trap & escape), BP-18 (tree arrow keys).

- Testing Library — `user-event` introduction (https://testing-library.com/docs/user-event/intro/)
- Kent C. Dodds — "Common mistakes with React Testing Library" (recommending `user-event` over `fireEvent`) (https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
- Testing Library — `user-event` keyboard reference (https://testing-library.com/docs/user-event/keyboard/)

Confidence: verified.

## Anti-patterns

- **`outline: 0` / `outline: none` without a replacement focus indicator.** Documented WCAG 2.4.7 failure (F78). Trips axe rule `focus-order-semantics`. See BP-06.
- **`<div onClick={...}>` or `<span onClick={...}>` for interactive controls.** Not focusable, no Enter/Space behavior, no implicit role. See BP-15.
- **Using `<Tooltip>` as a substitute for `aria-label` on an icon button.** Tooltip text is a description, not a name; ATs may not surface it. See BP-08.
- **Disabling MUI Dialog's focus-trap props (`disableEnforceFocus`, `disableAutoFocus`, `disableRestoreFocus`) without an explicit a11y rationale.** Breaks the WAI-ARIA Dialog contract. See BP-07.
- **Toasting via notistack with `role="alert"` for every message.** Spams assertive announcements and drowns out real errors; use `polite`/`status` by default. See BP-11.
- **Multiple visible `<h1>` elements per route, or jumping from `<h1>` straight to `<h3>`.** Breaks the heading outline screen-reader users navigate with. See BP-02.
- **Setting `<html lang>` only at app boot, then ignoring `i18next.changeLanguage` events.** Screen-reader pronunciation diverges from the visible content. See BP-03.
- **Focusing a `<main>` or `<section>` landmark on route change.** SRs read the entire container; focus a `tabindex="-1"` element near the new H1 instead. See BP-05.
- **Treating axe-core's "0 violations" pass as proof of accessibility.** axe finds ~30 % of issues at best and skips contrast in JSDOM. See BP-23.
- **`disabled` on a control that the user needs to *understand* (e.g. a CTA gated by validation) — the explanation becomes invisible to AT.** Prefer `aria-disabled="true"` + an `aria-describedby` reason. See BP-22.
- **Fixed-width MUI containers (`width: 1200px`) that overflow horizontally at 320 CSS px.** Violates SC 1.4.10 Reflow. See BP-21.
- **Animating `transform`/`translate` for every route or modal entrance without a `prefers-reduced-motion` guard.** Vestibular-disorder trigger and SC 2.3.3 failure. See BP-13.
- **Setting `aria-label` AND visible label text that disagree.** axe rule `aria-command-name` will not catch the mismatch; SRs read `aria-label`, sighted users read the visible label.
- **Using `tabindex` greater than `0`.** Breaks the natural tab order. Only `0` (in document order) and `-1` (programmatic focus only) are acceptable. (https://webaim.org/techniques/keyboard/tabindex)

## Open questions

- **OQ-1 — MUI v9 dark-mode contrast defaults.** The default MUI dark-mode palette does not always satisfy 4.5:1 contrast for `text.secondary` on `background.default`. Need to confirm whether MUI v9 ships a tightened default or whether every project must override `palette.text.secondary`. Couldn't find an authoritative MUI announcement; tentative finding from the contrast-issue tracker (mui/material-ui#46319) only.
- **OQ-2 — `notistack` built-in ARIA wiring.** The library does not document whether its default `SnackbarProvider` outputs `role="status"`, `role="alert"`, or neither. Empirically each variant (`success` / `error` / `info` / `warning`) seems to need an explicit `role` mapping. Marked `partial` until verified against the latest notistack release notes.
- **OQ-3 — Recharts `accessibilityLayer` keyboard pattern stability.** The wiki page describes the feature but the per-chart-type keyboard map (Bar vs Line vs Pie vs Scatter) is under-documented. A spec should require the per-chart-type behavior to be tested rather than assumed.
- **OQ-4 — React Router v7 ScrollRestoration vs focus restoration.** RR v7 ships `ScrollRestoration` but no focus-restoration primitive; the canonical "focus the H1 on route change" pattern is community-authored. A spec should pin one implementation (likely a `useFocusOnRouteChange` hook backed by `useNavigationType()`).
- **OQ-5 — Vitest browser mode for contrast.** Vitest supports a Playwright-backed browser environment which *could* lift the JSDOM contrast limitation in BP-23. Need to verify the maturity of `@vitest/browser` + `axe-core` integration before requiring it.

## Spec-input summary

Practices to encode as **normative MUSTs** in the resulting spec (WCAG-anchored, high-confidence, broad-impact):

1. **Landmark structure + single H1** (BP-01, BP-02) — anchored to WCAG 1.3.1, 2.4.6, 2.4.10.
2. **`<html lang>` + `<html dir>` synced to i18next** (BP-03) — anchored to WCAG 3.1.1.
3. **Skip-link + focus shift on route change** (BP-04, BP-05) — anchored to WCAG 2.4.1, 2.4.3.
4. **`:focus-visible` + no `outline: 0` (BP-06), focus not obscured by sticky chrome (BP-17)** — anchored to WCAG 2.4.7, 2.4.11, 2.4.13.
5. **Dialog ARIA + focus-trap defaults preserved** (BP-07) — anchored to WAI-ARIA APG Dialog pattern.
6. **IconButton `aria-label`** (BP-08) — anchored to WCAG 4.1.2.
7. **Form a11y triple: `aria-invalid` + `aria-describedby` + `role="alert"`** (BP-09), **`useId()` for label↔input binding** (BP-10) — anchored to WCAG 3.3.1, 3.3.2, 4.1.3.
8. **Live regions: polite by default, alert for true errors** (BP-11) — anchored to WCAG 4.1.3.
9. **Theme contrast threshold ≥ 4.5** (BP-12) — anchored to WCAG 1.4.3.
10. **`prefers-reduced-motion` opt-out for all non-essential motion** (BP-13) — anchored to WCAG 2.3.3.
11. **No `onClick` on `<div>`/`<span>`; semantic `<button>` everywhere** (BP-15) — anchored to WCAG 2.1.1.
12. **Target size ≥ 24 × 24 CSS px** (BP-16) — anchored to WCAG 2.5.8.
13. **Tree view labelled + APG keyboard contract intact** (BP-18) — anchored to WAI-ARIA APG Tree pattern.
14. **Date-picker popups behave as Dialogs** (BP-19) — anchored to WAI-ARIA APG.
15. **Recharts text alternative + data-table fallback + `accessibilityLayer`** (BP-20) — anchored to WCAG 1.1.1.
16. **320-px reflow** (BP-21) — anchored to WCAG 1.4.10.
17. **vitest-axe smoke per page-level component, with JSDOM contrast caveat documented** (BP-23, BP-24) — testing gate.

Practices to encode as **SHOULDs** (high-value but with legitimate opt-out scenarios):

- **`prefers-color-scheme` initial-theme default** (BP-14) — SHOULD because explicit user preference rightly overrides.
- **`aria-disabled` over native `disabled` for "needs-an-explanation" controls** (BP-22) — SHOULD because purely-decorative-disabled is fine native.

Items deferred to **OQ resolution** before turning into normative text: OQ-1 (MUI v9 dark-mode contrast defaults), OQ-2 (notistack ARIA wiring), OQ-3 (Recharts per-chart-type keyboard map), OQ-4 (canonical RR-v7 focus-restoration hook), OQ-5 (Vitest browser-mode contrast lift).
