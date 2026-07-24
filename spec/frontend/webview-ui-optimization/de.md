# Web-View-UI-Optimierung

Status: draft

## Kontext

Jede browsergehostete UI im Portfolio baut auf denselben Primitiven auf — schlichtem HTML und CSS plus einem JavaScript-Framework, das in ein einziges DOM rendert — und wird letztlich an denselben fünf Fragen gemessen: Kommt der erste Paint schnell, ist die Interaktionsfläche sicher, kann jeder Nutzer sie bedienen, funktioniert sie in jeder angebotenen Sprache, und fühlt sie sich unter dem Finger oder Zeiger richtig an? Die aktuelle Referenzimplementierung ist das kamerplanter-Frontend: React 19, TypeScript strict, Vite 8 als Bundler, MUI v9 mit Emotion, Redux Toolkit, React Router v7, react-hook-form mit Zod, react-i18next, notistack, Recharts, `qrcode.react`, Vitest mit `vitest-axe`, ausgeliefert als statische Assets hinter nginx mit einem `nginx-security-headers.inc`-Partial. Neue Produktfeatures, Refactorings und Audits berühren alle diese Fläche, aber die Regeln, die sie einhalten müssen, sind verstreut über Vendor-Docs, OWASP-Cheat-Sheets, WCAG-Kriterien und Ad-hoc-Team-Konventionen. Die Kosten sind zweifach: Beitragende leiten dieselben Checklisten jedes Mal neu ab, und Reviewer können nicht aus dem Diff allein erkennen, ob ein PR auslieferungsfähig ist. Diese Spec sammelt die Regeln, die diese Fläche regieren — ausschließlich load-bearing, vendor-verifiziert, je Aussage durch ≥ 2 unabhängige autoritative Quellen verankert — sodass die Regeln einheitlich auf Audits, neuen Code und den `webview-ui-optimize`-Skill / `webview-ui-expert`-Agent angewendet werden, die sie konsumieren.

## Ziele

- Eine Beitragende an einem Portfolio-Frontend kann eine beliebige Seite oder Komponente gegen eine Spec auditieren und normative MUSS/SOLLTE/DARF-NICHT-Regeln für Performance, Security, Accessibility, Internationalisierung und UX finden.
- Jede normative Regel ist durch ≥ 2 unabhängige autoritative Quellen (Vendor-Docs, W3C-/WHATWG-Specs, OWASP-Cheat-Sheets, MDN, WebAIM, web.dev, Nielsen Norman Group) verankert, festgehalten im Research-Audit-Trail unter `spec/frontend/webview-ui-optimization/research/`.
- Die Regeln sind stack-spezifisch, wo der Stack festliegt (React 19, Vite 8, MUI v9, RTK, react-router v7, react-hook-form, react-i18next, notistack, Recharts, nginx), und plattformgenerisch sonst (HTML, CSS, Browser-APIs).
- Die Spec ist die einzige Quelle der Wahrheit, die der `webview-ui-optimize`-Skill (Audit-+-Patch-Workflow) und der `webview-ui-expert`-Agent (read-only Tiefen-Reviewer) konsumieren.
- Drift zwischen Spec und Ziel-Repository ist erkennbar: Der Skill kann eine Zeile pro Regel mit `pass` / `fail` / `n/a` produzieren.

## Nicht-Ziele

- Einen anderen Stack wählen (Vue, Svelte, Angular, Solid) — diese Spec gilt für die React-/Vite-/MUI-Basis und bräuchte eine Schwester-Spec je Stack.
- Visuelle / Brand-Design-Regeln (Typografie-Skala, Illustrationsstil, Voice and Tone) — die leben in einem Produkt-Design-System, nicht hier.
- Native-Shell-Belange (Tauri, Electron, iOS WKWebView, Android WebView) — nur Browser-Kontext-Optimierung ist im Scope. „Web-View" in dieser Spec bezeichnet den browsergerenderten View, nicht den nativen Container.
- Server-Side Rendering (SSR), Server Components, Edge-Runtimes oder statische Site-Generierung — der Referenz-Stack liefert eine CSR-SPA hinter nginx aus.
- Test-Suite-Inhalte (welche Assertions zu schreiben sind, Coverage-Schwellen) — nur Test-Infrastruktur, die für a11y- / Performance-Gating relevant ist, ist im Scope.
- Release-Automation, Dependency-Upgrade-Strategie und CI-Pipeline-Form — die leben in `spec/project/release-automation/`, `spec/project/dependency-audit/` und `spec/project/workflow-health/`.

## Anforderungen

### Performance und Rendering

#### Core-Web-Vitals-Zielwerte

- **MUSS** die Field-Data-p75-Schwellen als harte Ziele behandeln: LCP ≤ 2,5 s, INP ≤ 200 ms, CLS ≤ 0,1, gemessen aus Real-User-Metriken (CrUX oder ein RUM-Anbieter), nicht synthetisch allein.
- **MUSS** `<meta name="viewport" content="width=device-width, initial-scale=1">` im Wurzel-`index.html` ausliefern und **DARF NICHT** `user-scalable=no` oder hartkodierte Pixel-Breiten in diesem Meta-Tag senden.

#### Kritischer Pfad und Assets

- **MUSS** `font-display: swap` (oder `optional`) auf jeder `@font-face`-Regel deklarieren, inklusive MUI-generierter Typografie.
- **MUSS** die LCP-kritische Typografie als `<link rel="preload" as="font" type="font/woff2" href="…" crossorigin>` vorladen (das `crossorigin`-Attribut ist verpflichtend — ohne es wird die Preload zweimal gefetcht).
- **SOLLTE** `fetchpriority="high"` auf das LCP-Bild (oder dessen `rel="preload" as="image"`-Link) auf Routen setzen, deren LCP-Kandidat ein Bild ist; **DARF NICHT** auf mehr als ein Element pro Route angewendet werden. (Das Research schlägt ein MUSS vor; bleibt SOLLTE, weil der LCP-Kandidat der Referenz-SPA in der Regel Text ist, kein Bild.)
- **MUSS** `loading="lazy"` und `decoding="async"` auf jedem off-screen `<img>` deklarieren und intrinsische `width`/`height` (oder CSS `aspect-ratio`) bereitstellen.
- **MUSS** Vites content-gehashte Dateinamen für `/assets/*`-Output beibehalten.
- **MUSS** die `<link rel="modulepreload">`-Tags, die Vite in `index.html` emittiert, beibehalten; Backend-integrierte Setups **MÜSSEN** sie aus dem Build-Manifest replizieren.
- **DARF NICHT** synchrone `<script>`-Tags vor dem Vite-Modul-Entry einfügen; jedes spät geladene Script **MUSS** `defer`, `async` oder `type="module"` tragen.
- **MUSS** first-paint-kritisches CSS klein halten: nur die Styles inlinen, die das initiale Rendering braucht, und alles Weitere über die von Vite emittierte Stylesheet-Kette laden; zusätzliche render-blockierende Stylesheets vor dieser Kette sind verboten.
- **SOLLTE** sich auf Vites Default-per-Modul-Code-Splitting verlassen und Chunking nur tunen, wenn Bundle-Analyse einen Long-Tail-Vendor-Chunk zeigt; getunt wird über die `output.codeSplitting`-Option des Bundlers (das Rollup-zeitliche `manualChunks` und das Zwischenformat `advancedChunks` sind in Vite 8 beide deprecated). **DARF NICHT** ganz `node_modules` in einen einzigen Vendor-Mega-Chunk pinnen.

#### React-19-Rendering

- **MUSS** den React Compiler (`babel-plugin-react-compiler` 1.x) in der Vite-Pipeline aktivieren und `eslint-plugin-react-compiler` verdrahten (portfolioweit ratifiziert am 29.05.2026; der Compiler ist stable, der Referenz-Stack pinnt React 19 + Vite 8, und `eslint-plugin-react-compiler` ist das erzwungene Guardrail, daher bleibt das MUSS ein MUSS); manuelle `useMemo` / `useCallback` / `React.memo` **MÜSSEN** als reine Escape-Hatches behandelt werden.
- **MUSS** State-Updates, die teure Re-Renders auslösen (Filterwechsel, Tab-Switches, Chart-Eingaben), in `startTransition` wickeln; das resultierende `isPending` wird mit einem nicht blockierenden Indikator gepaart, nie mit einem ganzseitigen Skeleton.
- **SOLLTE** `useDeferredValue` auf Props anwenden, die `memo()`-gewrappte langsame Kinder speisen, wenn der Quell-Setter nicht in eine Transition verschoben werden kann.
- **MUSS** Routen via React-Router-v7-Lazy-Route-Module code-splitten und jede asynchrone Daten-Boundary mit `<Suspense>` + einer `<ErrorBoundary>` paaren, die eine Retry-Aktion exponiert.

#### MUI und Emotion

- **MUSS** MUI-Icons via Deep-Path importieren (`@mui/icons-material/<Name>`); ESLint `no-restricted-imports` **MUSS** Barrel-Importe von `@mui/icons-material` verbieten. Dieselbe Regel gilt für andere weite MUI-Barrels (`@mui/lab`).
- **MUSS** das MUI-Theme auf Modulebene (oder per `useMemo` mit stabilen Inputs) memoisieren und es an einen einzigen Root-`ThemeProvider` übergeben.
- **SOLLTE** `sx` nur für einmalige Styles verwenden und wiederverwendete Styles zu `styled()` befördern; **DARF NICHT** einen `sx`-Wert in Objektform übergeben, dessen Identität sich pro Render ändert (stattdessen CSS-Variablen oder Theme-Tokens nutzen).
- **MUSS** die MUI-v9-`colorSchemes`-API + `cssVariables` statt imperatives `palette.mode`-Umschalten verwenden.

#### State und Daten

- **MUSS** Redux-Selektoren, die neue Referenzen ableiten, mit `createSelector` memoisieren; **DARF NICHT** einen Selektor wrappen, der bereits eine stabile Slice-Referenz zurückgibt.
- **SOLLTE** Read-seitigen Server-State in RTK-Query-Endpoints mit expliziten `tagTypes` / `providesTags` / `invalidatesTags` verschieben; das Default-`keepUnusedDataFor` von 60 s bleibt, außer Profiling zeigt anderes.
- **MUSS** uncontrolled `react-hook-form`-Inputs bevorzugen, registriert via `register`; **MUSS** `useWatch` (pro-Komponenten-Subscription) statt `watch` (Root-Re-Render) verwenden, wenn auf einzelne Felder reagiert wird.
- **MUSS** dayjs-Locales per Deep-Path importieren (`dayjs/locale/<code>`) und nur Locales ausliefern, die das Produkt tatsächlich anbietet.
- **MUSS** `AbortController().signal` an jeden abbrechbaren `axios`-Call übergeben und `controller.abort()` aus dem Cleanup des konsumierenden Hooks oder bei Routenwechsel aufrufen; das veraltete `CancelToken` **DARF** in neuem Code **NICHT** erscheinen.

#### Charts und lange Listen

- **SOLLTE** Listen/Grids, die mehr als ≈ 100 simultan gerenderte Zeilen mounten können, virtualisieren (`react-window` `FixedSizeList`/`VariableSizeList` oder MUI-X-Virtualised-Modi) mit einem kleinen `overscanCount` (≈ 5).
- **SOLLTE** Recharts-Charts via `React.lazy` + Suspense lazy laden; **SOLLTE** sie für off-screen-Widgets über `IntersectionObserver` gaten.

#### nginx und HTTP-Caching

- **MUSS** `/assets/*` mit `Cache-Control: public, max-age=31536000, immutable` ausliefern.
- **MUSS** `index.html` mit `Cache-Control: no-cache` (oder `no-store`, wenn sensible Daten inline gerendert werden) ausliefern.
- **MUSS** `gzip_static on;` aktivieren; **SOLLTE** `brotli_static on;` via `ngx_brotli` aktivieren, wenn verfügbar, und `.gz`/`.br`-Geschwister während `vite build` emittieren.

### Security und Sandboxing

#### Content Security Policy und Trusted Types

- **MUSS** eine strikte Content Security Policy mit einem per-Response-Krypto-Nonce auf `script-src` plus `'strict-dynamic'` ausliefern, z. B. `script-src 'nonce-<random>' 'strict-dynamic'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; require-trusted-types-for 'script';`.
- **DARF NICHT** `'unsafe-inline'` oder `'unsafe-eval'` in `script-src` führen; für `style-src` ist ein an Emotions `cache.nonce` gebundener Nonce gegenüber `'unsafe-inline'` zu bevorzugen.
- **DARF NICHT** Host-Allowlist-CSPs verwenden (umgehbar über offene JSONP-Endpoints auf gelisteten Hosts).
- **MUSS** `require-trusted-types-for 'script'` senden und eine benannte `trusted-types`-Policy, die jede HTML-Einfügung durch DOMPurify pipet. Diese Direktive schützt ausschließlich Script-/HTML-DOM-XSS-Sinks (`innerHTML`, `script.src`, `document.write`); Emotions `<style>`-Tag-Injektion ist kein `'script'`-Sink und arbeitet sauber darunter (sie wird stattdessen durch den oben genannten `style-src`-Nonce gesteuert, der an Emotions `cache.nonce` gebunden ist), sodass ein Audit Emotion- oder MUI-v9-Styling **NICHT** als Trusted-Types-für-`script`-Verletzung melden **DARF**.
- **MUSS** eingebettete Drittanbieter-Inhalte sandboxen: `<iframe sandbox>` mit dem kleinsten funktionierenden Token-Satz plus einer `frame-src`-Allow-List in der CSP. Die Kombination `sandbox="allow-scripts allow-same-origin"` auf same-origin-Inhalt **DARF NICHT** vorkommen — sie erlaubt dem Frame, seine eigene Sandbox aufzuheben.

#### nginx-Security-Header

- **MUSS** den vollen Header-Satz aus `nginx-security-headers.inc` senden:
  - `Content-Security-Policy: <strenge Policy wie oben>`.
  - `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload` (`preload` weglassen, bis der Betreiber sicher ist, dass jede Subdomain dauerhaft HTTPS ausliefert).
  - `X-Content-Type-Options: nosniff`.
  - `Referrer-Policy: strict-origin-when-cross-origin` (auf `no-referrer` herabstufen für Routen, die Tokens in der URL führen).
  - `Cross-Origin-Opener-Policy: same-origin` (`same-origin-allow-popups` nur, wenn die SPA vertrauenswürdige OAuth-Popups öffnet).
  - `Cross-Origin-Resource-Policy: same-origin` auf app-eigenen Assets.
  - `Permissions-Policy`, das jedes mächtige Feature ablehnt, das die SPA nicht aktiv nutzt (Kamera, Mikrofon, Geolocation, Payment, USB, Serial, Bluetooth, Accelerometer, Gyroscope, Magnetometer, MIDI usw.) und nur die Features auf `'self'` opt-in setzt, die tatsächlich benötigt werden.
  - `X-Frame-Options: DENY` als Belt-and-Braces-Fallback zu `frame-ancestors 'none'`.
- **SOLLTE** `Cross-Origin-Embedder-Policy: require-corp` nur dann hinzufügen, wenn die SPA Cross-Origin-Isolation braucht (SharedArrayBuffer, hochauflösende Timer); COEP ist opt-in, weil es naiv eingebettete Ressourcen bricht. Sobald Cross-Origin-Isolation tatsächlich benötigt wird, **MUSS** COEP `require-corp` (gepaart mit `Cross-Origin-Opener-Policy: same-origin`) für diese Fläche gesetzt werden.

#### React-Rendering-Sicherheit

- **MUSS** `dangerouslySetInnerHTML` als privilegierten Escape-Hatch behandeln: nur in einem kleinen, code-eigentumsverwalteten Satz von Komponenten erlaubt, immer eingeschlossen in eine Trusted-Types-Policy, die DOMPurify mit expliziter Allow-List für Tags und Attribute fährt. Lint-verbieten via `react/no-danger` überall sonst.
- **MUSS** jede nutzerkontrollierte URL validieren, bevor sie an `href`, `src` oder React Router `navigate(...)` / `redirect(...)` übergeben wird: URL parsen, `javascript:`, `data:`, `vbscript:` ablehnen, Schemes (`https:`, `mailto:`) und Origins per Allow-List filtern, route-relative Pfade bevorzugen.
- **MUSS** `rel="noopener noreferrer"` auf jeden externen `target="_blank"`-Link setzen (sowie auf jeden `window.open(url, '_blank')`-Features-String); Lint-Enforcement via `react/jsx-no-target-blank`.

#### HTTP-Client-Disziplin

- **MUSS** API-Traffic durch eine konfigurierte `axios`-Instanz pro Backend leiten — `baseURL`, ein explizites `timeout` und ein Request-Interceptor, der das In-Memory-Token injiziert; Ad-hoc-`axios.get(url)`-Aufrufe mit hand-gebauten Auth-Headern sind verboten.
- **MUSS** `withCredentials` nur auf Endpoints aktivieren, die tatsächlich Cookies brauchen, nie als globaler Default.

#### Auth, Storage und Secrets

- **DARF** Auth-Tokens (Access, Refresh, Session) **NICHT** in `localStorage`, `sessionStorage`, IndexedDB oder persistiertem Redux-State speichern; **MUSS** Tokens in einem `HttpOnly; Secure; SameSite=Strict`-Cookie führen, das vom Backend ausgestellt wird, ODER im Memory plus Silent-Refresh gegen einen cookie-geschützten Refresh-Endpoint.
- **MUSS** Auth-Cookies unter dem `__Host-`-Prefix ausstellen (`Path=/`, kein `Domain`-Attribut); `SameSite=Lax` ist nur für OAuth-Callback-Flows akzeptabel, und `SameSite=None` ohne `Secure` **DARF NICHT** ausgestellt werden (Browser verwerfen es stillschweigend).
- **MUSS** `redux-persist` (wenn vorhanden) mit einer expliziten `whitelist` von Slices konfigurieren, die ausschließlich nicht-sensiblen UI-State enthalten (Theme, Sprache, Tabellenspalten-Reihenfolge). Encryption-at-Rest mit einem Key, der im Bundle ausgeliefert wird, ist verboten.
- **MUSS** jeden `import.meta.env.VITE_*`-Wert als öffentlich behandeln. API-Keys, Signing-Secrets, OAuth-Client-Secrets und BFF-umgehende URLs **DÜRFEN NICHT** hinter einem `VITE_`-Prefix abgelegt werden; **DARF NICHT** `envPrefix` auf den leeren String überschrieben werden.
- **MUSS** Vite `build.sourcemap` auf `false` (oder `'hidden'`, wenn Error-Tracking Symbolisierung mit privatem Upload braucht) setzen; **DARF NICHT** `*.js.map` öffentlich aus nginx ausliefern, und **SOLLTE** `*.map` auf der nginx-Ebene blockieren.

#### Formular- und Upload-Validierung

- **MUSS** jedes Zod-Schema serverseitig spiegeln: Client-Validierung ist UX, niemals das autoritative Gate. Backend validiert Positive-Allow-List, Längenschranken, Typschranken; Client surfacet Backend-Fehler via `setError`.
- **MUSS** File-Uploads im Browser validieren (`accept`, MIME, Größe, Extension) ausschließlich zur UX; das Backend **MUSS** Magic-Bytes validieren, ein hartes Max-Size erzwingen, außerhalb des Web-Roots speichern und scannen.
- **MUSS** `autocomplete`-Hints absichtlich auf sensiblen Formularen setzen (`new-password`, `current-password`, `one-time-code`); **DARF NICHT** ein pauschales `autocomplete="off"` auf Credential-Feldern setzen (moderne Browser ignorieren es für Passwörter).
- **MUSS** die Länge deckeln und das URL-Scheme per Allow-List filtern, bevor ein nutzerkontrollierter String als QR-Code gerendert wird (`qrcode.react`); ein gescanntes `javascript:`- oder `data:`-Payload wird auf dem scannenden Gerät ausgeführt.

#### Supply-Chain und Verifikation

- Supply-Chain-Hygiene — Lockfile-Commit, Frozen-Lockfile-Installation in CI, CVE-Schweregrad-Klassifizierung und release-blockierende Schwellen — wird von `spec/project/dependency-audit/` geregelt; diese Spec verweist auf diesen Eigentümer und fügt nur die frontend-spezifischen SRI-, HTTP-Observatory- und Source-Map-Regeln unten hinzu, anstatt Lockfile- oder Audit-Schwellen erneut festzuschreiben.
- **MUSS** den ausgelieferten Header-Satz nach jedem Produktions-Deploy gegen Mozilla HTTP Observatory verifizieren; jeder Grade-Abfall blockiert das Release.
- **MUSS** Subresource Integrity (`integrity` + `crossorigin="anonymous"`) auf jeden `<script>` und `<link rel="stylesheet">` von einer fremden Origin anwenden; die Default-Haltung ist Self-Hosting via Vite, sodass SRI gegenstandslos wird.

### Accessibility (WCAG 2.2 Level AA)

#### Dokumentstruktur

- **MUSS** Top-Level-Seitenbereiche in semantische HTML5-Sectioning-Elemente wickeln (`<header>`, `<nav>`, `<main>`, `<footer>`, `<aside>`); jedes `<nav>`, das nicht das einzige ist, **MUSS** `aria-label` / `aria-labelledby` tragen.
- **MUSS** genau ein sichtbares `<h1>` pro Route rendern und **DARF NICHT** Heading-Levels überspringen.
- **MUSS** `<html lang>` und `<html dir>` synchron zur aktiven i18next-Sprache halten, indem `document.documentElement.lang` (BCP-47-Tag) und `document.documentElement.dir` (über `i18next.dir(lng)`) bei jedem `languageChanged`-Event gesetzt werden.
- **MUSS** fremdsprachige Passagen innerhalb der Seite mit `lang="…"` auf einem umhüllenden Element markieren (WCAG 3.1.2).

#### Focus-Management

- **MUSS** einen „Skip to main content"-Link als erstes fokussierbares Element ausliefern; visuell versteckt, aber fokussierbar, niemals `display:none`; **MUSS** den Fokus auf `<main>` oder ein `tabindex="-1"`-Element darin verschieben.
- **MUSS** den Fokus bei jedem Routenwechsel entweder (a) auf den Hauptinhalts-Container mit `tabindex="-1"` oder (b) auf das neue `<h1>` mit `tabindex="-1"` verschieben; **DARF NICHT** ein Landmark-Element fokussiert werden, und **DARF NICHT** ein beliebiger Input autofokussiert werden.
- **DARF NICHT** `outline: 0` / `outline: none` ohne einen gleichwertigen Ersatz setzen; **MUSS** `:focus-visible` für angepasste Fokus-Styles verwenden und das 3:1-Non-Text-Kontrast- und WCAG-2.4.13-Focus-Appearance-Perimeter-Limit erfüllen (2.4.13 ist Level AAA, bewusst über den AA-Boden hinaus adoptiert).
- **MUSS** sicherstellen, dass der Fokus nicht von sticky Chrome verdeckt wird (WCAG 2.4.11): `scroll-margin-top` / `scroll-padding` gleich der Bar-Höhe.
- **DARF NICHT** `tabindex`-Werte größer als `0` verwenden; nur `0` und `-1` sind zulässig.

#### Komponenten

- **MUSS** die Focus-Trap-, Initial-Focus- und Return-Focus-Defaults von MUI `Dialog` / `Modal` beibehalten: `disableEnforceFocus`, `disableAutoFocus`, `disableRestoreFocus` für reguläre Dialoge nicht setzen. **MUSS** `aria-labelledby` tragen, das auf den Titel verweist; **SOLLTE** zusätzlich `aria-describedby` für längeren Inhalt tragen.
- **MUSS** jeden Icon-only `IconButton` mit `aria-label` (oder visuell verstecktem Text) beschriften; `<Tooltip>` liefert eine Beschreibung, keinen Namen, und **DARF** das Label **NICHT** ersetzen.
- **MUSS** den Accessible Name einer Steuerung mit ihrem sichtbaren Label ausrichten: Wo `aria-label` und sichtbarer Text koexistieren, **MUSS** der Accessible Name den sichtbaren Text enthalten (WCAG 2.5.3 Label in Name); ein `aria-label`, das dem sichtbaren Label widerspricht, ist verboten.
- **MUSS** react-hook-form-Fehler mit dem Triple `aria-invalid={!!errors.x}` + `aria-describedby="<error-id>"` + `role="alert"` auf dem Fehlerelement verdrahten.
- **MUSS** Input-IDs via React 19 `useId()` (oder MUIs auto-generierte IDs) erzeugen, damit `<label htmlFor>` und `aria-describedby` über Re-Renders hinweg stabil auflösen.
- **MUSS** `@mui/x-tree-view` (`SimpleTreeView` / `RichTreeView`) mit `aria-label` oder `aria-labelledby` beschriften; **DARF** die eingebaute WAI-ARIA-APG-Tree-Keyboard-Vereinbarung **NICHT** überschreiben.
- **MUSS** `@mui/x-date-pickers`-Popup-Views als Dialoge behandeln: alle Dialog-Regeln gelten (labelled-by, Focus-Trap, Return-Focus); ein custom `<TextField>`-Slot **MUSS** die ARIA-Props des Pickers weiterreichen.
- **MUSS** einen echten `<button type="button">` (oder MUI `Button` / `IconButton`) für jede klickbare Steuerung verwenden; **DARF** `onClick` **NICHT** an einen `<div>` oder `<span>` hängen, um einen Button vorzutäuschen.

#### Toasts und Live-Regionen

- **MUSS** notistack-Nachrichten via einer Live-Region announcen; Default ist `role="status"` / `aria-live="polite"`, `role="alert"` / `aria-live="assertive"` bleibt echten Fehlern (fehlgeschlagener Save, Auth-Expiry) vorbehalten.
- **MUSS** die Schließen-Steuerung eines dismissbaren Toasts als echten `<button>` mit Accessible Name ausführen; ein Toast **DARF** beim Erscheinen den Fokus **NICHT** stehlen.
- **MUSS** Routenwechsel via einer `aria-live="polite"`-Region oder via Focus-auf-H1-Mechanismus announcen; **DARF NICHT** beide für dasselbe Event stapeln.

#### Visuelles

- **MUSS** MUIs `palette.contrastThreshold` auf `4.5` setzen, damit von der Palette abgeleitete `contrastText`-Wahlen WCAG 1.4.3 AA (Body-Text 4,5:1) zielen; angepasste Paletten via WebAIM-Contrast-Checker verifizieren. Die Einstellung greift weiterhin unter MUI v9 `colorSchemes` + `cssVariables`: jede Scheme-Palette durchläuft dieselbe `augmentColor`-/`createPalette`-Ableitung zur Theme-Erzeugungszeit, und CSS-Variablen ändern nur, wie aufgelöste Werte emittiert werden, nicht wie `contrastText` berechnet wird. Sie wirkt aber nur auf **angepasste** Palettenfarben (MUIs eingebaute Defaults liefern festes `contrastText` und bleiben unverändert) und reitet auf einer groben nicht-linearen Kurve, vor der MUI selbst als kontraproduktiv warnt, sodass der WebAIM-/manuelle Kontrast-Durchlauf das eigentliche Gate ist, nicht der Schwellenwert allein.
- **MUSS** nicht-essenzielle Motion in `@media (prefers-reduced-motion: no-preference)` wickeln (Opt-out-Pattern); Transitions reduzieren oder entfernen, wenn der Nutzer eine Reduce-Präferenz ausgedrückt hat (das zugrunde liegende WCAG-Kriterium 2.3.3 ist Level AAA, bewusst über den AA-Boden hinaus adoptiert).
- **SOLLTE** `prefers-color-scheme` für das Initial-Theme respektieren, wenn der Nutzer noch keine explizite Wahl getroffen hat; eine persistierte Nutzerwahl **MUSS** die OS-Präferenz danach überschreiben.
- **MUSS** Layout-Reflow bei 320 CSS px Viewport-Breite ohne horizontales Scrollen ermöglichen (WCAG 1.4.10); inhärent zweidimensionaler Inhalt (Tabellen, Charts) **MUSS** in seinem eigenen Container scrollen, nicht auf der Seitenebene.
- **SOLLTE** `aria-disabled="true"` gegenüber dem nativen `disabled` für Steuerungen bevorzugen, deren Disabled-State eine Erklärung braucht (Formular-Gating, Paywall), damit ein zugeordneter `aria-describedby`-Grund erkennbar bleibt.

#### Zielgröße

- **MUSS** jeder interaktiven Steuerung eine Tap-Target-Fläche von mindestens 24 × 24 CSS-Pixeln geben (WCAG 2.5.8); **SOLLTE** in touch-first-Kontexten auf 44 × 44 CSS-Pixel (Apple HIG) bis 48 × 48 CSS-Pixel (Material Design) zielen. Spacing **SOLLTE** ≥ 8 px zwischen benachbarten Zielen lassen.

#### Charts

- **MUSS** jedem Recharts-Chart eine programmatisch ermittelbare Textalternative geben: `role="img"` + `aria-label` / `aria-labelledby` auf dem Container, eine eingebettete Klartext-Zusammenfassung UND einen Datentabellen-Fallback (sichtbar oder visuell versteckt, aber semantisch ausgezeichnet).
- **MUSS** Recharts' `accessibilityLayer` auf jedem Chart aktiviert lassen (seit Recharts 3 per Default an; nie deaktivieren).

#### Tests

- **MUSS** pro Page-Level-Komponente `vitest-axe`-Smoke-Tests hinzufügen, die `expect(await axe(container)).toHaveNoViolations()` zusichern; axe ist als Boden (~ 30 % der Issues), nicht als Decke zu behandeln. Color-Contrast-Checks sind unter JSDOM deaktiviert und **MÜSSEN** separat verifiziert werden (Browser-Mode, Storybook-a11y-Addon oder manuell).
- **SOLLTE** `@testing-library/user-event` (nicht `fireEvent`) für tastatur-, fokus- und pointer-getriebene a11y-Assertions verwenden.

### Internationalisierung

#### Locale-Primitiven

- **MUSS** jede locale-sensitive Zahl via `Intl.NumberFormat` formatieren (Währungen verwenden `style: 'currency'` + ISO-4217-Code); **DARF NICHT** Separatoren hand-bauen oder `toFixed` für die Darstellung verwenden.
- **MUSS** jedes locale-sensitive Datum / jede Uhrzeit via `Intl.DateTimeFormat` formatieren und relative Zeitspannen via `Intl.RelativeTimeFormat`; hand-gebaute Datums-Strings sind verboten.
- **MUSS** `Intl.Collator` für jegliches locale-bewusste Sortieren verwenden; die Default-Unicode-Code-Point-Reihenfolge von `Array.sort()` ist verboten.
- **MUSS** konjunktive / disjunktive lesbare Listen via `Intl.ListFormat` formatieren; hand-gerolltes `arr.join(', ')` ist verboten.

#### Übersetzungsfunktion

- **MUSS** Plural-Varianten mit der i18next-JSON-v4-Suffix-Grammatik schreiben (`_one`, `_other`, plus voller CLDR-Satz, wo die Sprache es erfordert); **DARF NICHT** im Komponenten-Code auf `count === 1` verzweigen.
- **MUSS** jeden übersetzten Satz als einzelnen Key mit benannten Platzhaltern komponieren (`t('welcome', { name })`); Fragment-Konkatenation (`t('hello') + ' ' + name`) ist verboten.
- **MUSS** die `<Trans>`-Komponente mit expliziten React-Element-Kindern für Übersetzungen verwenden, die Inline-Markup enthalten; **DARF NICHT** `interpolation.escapeValue` global deaktivieren; **DARF NICHT** `{{value}}` in `dangerouslySetInnerHTML` einsetzen.

#### Erkennung, Persistenz, Routing

- **MUSS** `i18next-browser-languagedetector` mit expliziter `order` (`['querystring', 'cookie', 'localStorage', 'navigator', 'htmlTag']`) und expliziten `caches` (`['cookie', 'localStorage']`) konfigurieren; deterministischer Cookie-Name (`i18next`) und Storage-Key (`i18nextLng`).
- **MUSS** eine persistierte Nutzerwahl immer die automatische Erkennung schlagen lassen: `i18n.changeLanguage(lng)` schreibt in die Caches, aus denen der Detector liest.
- **MUSS** `supportedLngs` (kanonische Sprache zuerst) und `fallbackLng` explizit in `i18n.init` deklarieren; Resource-Path-Injection über den Querystring-Slot wird nur durch diese Allow-List entschärft.
- **MUSS** die Locale in der URL via einem React-Router-v7-Dynamiksegment (`/:locale/*`) oder einer `prefix(...)`-Route kodieren; der Router ist die einzige Quelle der Wahrheit für die aktive Locale und **MUSS** i18next bei jeder Navigation synchronisieren. Die kanonische Locale **DARF** prefix-los an der `x-default`-Wurzel ausgeliefert werden, während jede nicht-kanonische Locale ihren Prefix trägt; Cookies bleiben ausschließlich ein Erkennungs-Input und **DÜRFEN NICHT** die alleinige Locale-Quelle sein.
- **MUSS** `Content-Language: <locale>` aus nginx auf jeder lokalisierten Response senden; **SOLLTE** einen bestehenden `i18next`-Cookie vor `Accept-Language`-basierten Root-Redirects respektieren. `Accept-Language`-Negotiation **MUSS** ausschließlich an der locale-losen Wurzel stattfinden (Exact-Match-`location =`-Block); Deep Links **DÜRFEN NICHT** auf Basis von `Accept-Language` umgeschrieben oder redirected werden.
- **MUSS** statische `<link rel="alternate" hreflang="…" href="…">`-Tags (einer pro Locale plus `x-default`) im initialen `index.html` server-side oder zur Build-Zeit emittieren, bidirektional. React-Runtime-Injektion von `hreflang` ist verboten.

#### Laden, RTL und Picker

- **MUSS** Übersetzungen in einen Namespace pro Feature organisieren (`auth`, `plants`, `settings`, `common`) und Namespaces pro Route via `i18next-resources-to-backend` (Vite-Dynamic-Imports) oder `i18next-http-backend` lazy laden.
- **MUSS** die kanonische Locale plus die aktive Locale vorbündeln; den Rest als Vite-Chunks pro `(locale, namespace)`-Paar deferren.
- **SOLLTE** einen Preload-Hint für den initialen Namespace-Chunk der aktiven Locale emittieren, wenn die Locale zur Build-Zeit oder mit der ersten Response bekannt ist.
- **MUSS** den React-Baum in `<Suspense>` wickeln, damit der erste Paint keine rohen Keys zeigt; `react.useSuspense: true` ist Default und **MUSS** aktiv bleiben, außer jeder Konsument gatet explizit auf `ready`.
- **MUSS** MUI-v9-RTL via `createTheme({ direction: 'rtl' })` UND einem Emotion-`CacheProvider`, dessen Cache `[prefixer, rtlPlugin]` aus `@mui/stylis-plugin-rtl` verwendet, verdrahten, wenn die aktive Locale RTL ist.
- **MUSS** MUI-X `LocalizationProvider` mit drei Dingen im Gleichschritt verdrahten: dayjs-Locale (`dayjs.locale('de')`), `adapterLocale="de"` und `localeText` aus `@mui/x-date-pickers/locales`.
- **MUSS** dayjs-Locales als Default-Export-Imports einbinden und sie bei jedem `languageChanged`-Event umschalten; bare Side-Effect-Imports (`import 'dayjs/locale/de'`) **DÜRFEN NICHT** erscheinen, weil einige Bundler sie verwerfen.
- **MUSS** Zod-Validierungsfehler über eine zentrale, locale-bewusste Error-Map übersetzen, die i18n-Keys auflöst — Zod 3: `z.setErrorMap` oder `zodResolver(schema, { errorMap })`; Zod 4: der vereinheitlichte `error`-Parameter oder `z.config({ customError })` (`setErrorMap` existiert dort nicht mehr); **DARF NICHT** `t()`-Aufrufe innerhalb von Schema-Definitionen einbetten.
- **MUSS** Übersetzungen für `notistack`-Nachrichten an der Call-Site auflösen (`enqueueSnackbar(t('errors.savePlant'), …)`), damit Nachrichten über die Toast-Lebensdauer stabil bleiben.

#### Drift-Erkennung

- **MUSS** einen i18next-Missing-Key-Reporter aktivieren: `debug: true` und `saveMissing: true` + ein `missingKeyHandler` in Development; ein gesampelter Error-Reporter (Sentry / Äquivalent) in Production mit `saveMissing: false`.
- **SOLLTE** einen Pseudo-Locale-Test (z. B. `i18next-pseudo`) in CI fahren, um fehlende Keys, Truncation und hartkodierte englische Strings zu fangen, bevor ein echter Übersetzer sie sieht.
- **MUSS** Keys als stabile, kleingeschriebene, punktierte Identifier schreiben (`plants.list.empty`); Text-als-Key ist verboten, weil jede englische Anpassung jede Übersetzung bricht.

### UX und Native-Feel

#### Lade- und Feedback-Hierarchie

- **MUSS** den Feedback-Indikator nach erwarteter Wartezeit wählen:
  - < ≈ 100 ms: kein Indikator.
  - 100 ms – 1 s: optimistisch / kein Spinner.
  - 1 s – 10 s: Skeleton-Screen, der das finale Layout abbildet.
  - > 10 s: determinierter Progress-Bar mit Abbrechen-Affordanz.
- **DARF NICHT** länger als 300 ms nach einer Navigation einen leeren Screen zeigen; Skeletons oder `<Suspense>`-Fallbacks überbrücken die Lücke.
- **MUSS** die Spinner-Anzeige um 200 – 300 ms debouncen, damit kurze Loads keinen Spinner aufblitzen lassen; die gewählte projektweite Schwelle **MUSS** konsistent angewendet werden. (Die konkreten Millisekunden-Werte in diesen beiden Regeln sind Projekt-Konventionen auf Basis der Nielsen-Norman-Group-Response-Time-Bänder, keine vendor-zitierten Schwellen.)
- **MUSS** pro View einen `<XxxSkeleton/>` bauen, der das finale Layout abbildet (Form, Anzahl, ungefähre Größe); generische Shimmer-Boxen, die beim Hydrate Layout-Shift verursachen, sind verboten.

#### Mutations und Recovery

- **SOLLTE** Optimistic-UI nur auf risikoarme Mutations anwenden (Favorisieren, Toggeln, Umsortieren, Umbenennen); **DARF NICHT** auf finanzielle Transaktionen, irreversible Löschungen ohne Undo-Schonfrist oder irgendetwas, das nachgelagerte Side-Effects (E-Mail, Payment) auslöst.
- **MUSS** jedes optimistische Update bei Fehlschlag zurückrollen (RTK Query: `patchResult.undo()` im `queryFulfilled`-Catch) und eine inline Recovery-Affordanz zeigen; ein stillschweigend beibehaltener optimistischer State ist verboten.
- **SOLLTE** einen optimistischen Commit + Undo-Snackbar gegenüber einem unterbrechenden „Sind Sie sicher?"-Dialog für reversible destruktive Aktionen bevorzugen; einen echten `<Dialog>` nur dann verwenden, wenn die Aktion irreversibel oder mehrstufig ist.
- **MUSS** Fehler-Surfaces unterscheiden:
  - Inline-Fehler (neben Feld oder Komponente) — Formularvalidierung, „diese Karte ließ sich nicht laden — retry", fehlende Berechtigung.
  - Snackbar / Toast — transiente, nicht-aktionable Netzwerkfehler, Hintergrund-Save-Fehler.
  - Dialog — state-korrumpierende Fehler, die eine Entscheidung erfordern (Session abgelaufen).

#### Snackbar-Disziplin

- **MUSS** höchstens einen Snackbar gleichzeitig zeigen; falls Stacken unvermeidbar, `maxSnack` ≤ 3 deckeln.
- **MUSS** Variant-Semantik anwenden: `success` für bestätigten Write, `error` für fehlgeschlagenen Write oder nicht-recoverbaren Netzwerkfehler, `warning` für weiche Validierung, `info` für nicht-aktionable State, `default` für Undo-Affordanzen.
- **DARF NICHT** Snackbars für Inline-Formularvalidierung nutzen; die gehören neben das Feld.
- **MUSS** `autoHideDuration` von ≥ 4 s (Default 5 s) verwenden und `persist: true`-Snackbars mit einer expliziten Dismiss- oder Action-Schaltfläche paaren.
- **MUSS** den Snackbar an eine feste Ecke pro App verankern (Desktop bottom-left, Mobile bottom-center gemäß Material-Empfehlung); **DARF NICHT** den Anker pro Route variieren.

#### Navigation und Back-Verhalten

- **MUSS** React Router v7 `<ScrollRestoration/>` einmal am Layout-Root mounten.
- **MUSS** einen globalen Pending-Indikator (subtiler Top-of-Layout-Progress-Bar) zeigen, der von `useNavigation().state` getrieben wird, erst nach einer Verzögerung von ≥ 200 ms, damit schnelle Navigationen nicht aufblitzen.
- **DARF** den Browser-Back-Button **NICHT** abfangen: Modal-Close bindet ESC und einen expliziten Close-Button; Route-Guards redirecten via `<Navigate replace />`, damit die geschützte URL nicht zweimal im Back-Stack steht.
- **SOLLTE** `<NavLink prefetch="intent">` für Navigations-Links innerhalb der Hauptschale verwenden, wenn im Framework-Mode betrieben; **DARF NICHT** `prefetch="render"` oder `prefetch="viewport"` auf großen Listen nutzen. Jede nur-im-Framework-Mode-geltende Regel **MUSS** den Qualifikator `wenn im Framework-Mode betrieben` tragen; der Referenz-Stack liefert eine CSR-SPA aus, daher ist eine routing-spezifische Schwester-Spec aufgeschoben, bis ein Portfolio-Repo den React-Router-Framework-Mode in größerem Umfang adoptiert.

#### Formulare

- **MUSS** react-hook-form mit `mode: 'onTouched'`, `reValidateMode: 'onChange'`, `shouldFocusError: true` konfigurieren.
- **MUSS** eine Fehler-Zusammenfassung oberhalb des Formulars rendern, wenn > 1 Feld ungültig ist: ein `role="alert"`-Container mit Überschrift und Liste von Links, die zu jedem ungültigen Feld springen. Rendert die Zusammenfassung, erhält sie — nicht das erste ungültige Feld — den Fokus; `shouldFocusError` deckt nur den Ein-Fehler-Fall (niemals beide fokussieren).
- **MUSS** `aria-disabled="true"` (nicht natives `disabled`) auf dem Submit-Button setzen, während das Formular pendet, damit Screen-Reader-Nutzer ihn weiterhin tabbar erreichen und seinen Status hören; die Submit-Logik im Handler abschotten, nicht via `disabled`.
- **DARF NICHT** Button-States allein über Farbe kommunizieren (WCAG 1.4.1): Farbe wird mit Inline-Nachricht / Icon / `aria-live`-Update gepaart.

#### Theming und Motion

- **MUSS** jede Farbe, jeden Spacing-Wert und jeden Border-Radius aus Theme-Tokens auflösen; hartkodierte Hex- / `rgb()`-Werte innerhalb von Komponenten sind verboten (eine Projekt-Konvention auf Basis der MUI-Theming-Leitlinien).
- **MUSS** Light-/Dark-Mode via MUI v9 `colorSchemes` + `cssVariables` steuern; **DARF NICHT** via `palette.mode`-Konditionalen flippen (das verursacht FOUC).
- **MUSS** ein winziges `<head>`-Script einbetten, das den persistierten Theme-Key liest und ein `data-color-scheme`-Attribut auf `<html>` setzt, bevor der React-Baum mountet (MUIs `InitColorSchemeScript`).
- **SOLLTE** Live-Wechseln des OS-Themes über einen `matchMedia('(prefers-color-scheme: dark)')`-Change-Listener folgen, solange der Nutzer keinen expliziten Override gesetzt hat; sobald ein Override existiert, gewinnt er.
- **MUSS** nicht-essenzielle Motion in `@media (prefers-reduced-motion: no-preference)` wickeln; essenzielle Motion (Lade-Spinner) **SOLLTE** auf Opacity / Dissolve reduziert werden, wenn Reduce-Motion gesetzt ist.

#### Viewport und Plattform-Passform

- **MUSS** `svh`, `dvh`, `lvh` gegenüber `vh` für Full-Screen-Layouts bevorzugen:
  - `svh` für „Bildschirm füllen, nie unter Chrome verstecken".
  - `lvh` für „maximalen retraktierten Viewport füllen".
  - `dvh` nur, wenn Live-Tracking essenziell ist (selten auf scrollendem Inhalt).
- **MUSS** `env(safe-area-inset-*)`-Padding auf dem Layout-Root für Notch- / Home-Indicator-Freiraum anwenden, mit `max(env(…), <Minimum>)`-Boden; `viewport-fit=cover` **MUSS** im Viewport-Meta gesetzt sein, damit Safe-Area-Insets ungleich null werden.

#### Dialoge und Popovers

- **MUSS** MUI `Dialog` verwenden (eine `Modal`-basierte Implementierung mit eigenem Focus-Trap — sie rendert kein natives `<dialog>`) oder, außerhalb von MUI-Flächen, das Plattform-`<dialog>` via `.showModal()` öffnen, dessen Focus-Trap, ESC-Handling, `aria-modal`, `::backdrop`, Top-Layer und Inertness gratis mitkommen; selbstgebaute Modal-Div-Bäume sind verboten.
- **SOLLTE** die native Popover-API (`popover="auto"`) auf stabilen Engines für Tooltips / Menüs bevorzugen; auf MUI `Popover` / `Menu` für ältere Browser zurückfallen.

#### Charts und Viewport

- **MUSS** jeden Recharts-Chart in `<ResponsiveContainer width="100%" aspect={…}>` (oder mit festem `minWidth` / `minHeight`) wickeln; nackte Charts, die in schmalen Spalten kollabieren, sind verboten.
- **MUSS** Chart-Tooltips jede gerenderte Serie plus den formatierten x-Achsen-Wert tragen lassen und sie so positionieren, dass Touch-Eingabe sie nie unter dem Finger verdeckt.
- **MUSS** `accessibilityLayer` auf jedem Chart aktiviert lassen (Querverweis auf die a11y-MUSS-Regel in §Accessibility › Charts).

### Übergreifende Verifikation

- **MUSS** `vitest-axe`-Smoke-Tests, ein Vite-+-nginx-Static-Asset-Audit (immutable Headers, Source-Map-Absenz), einen Mozilla-HTTP-Observatory-Check und einen Core-Web-Vitals-RUM-Snapshot ins Release-Gate verdrahten; ein Release **DARF NICHT** ausgeliefert werden, solange eines davon rot ist.
- **SOLLTE** das Vitest-`environment` per Default auf `node` setzen und DOM-abhängige Dateien über eine per-File-Kommentar-Direktive in `jsdom` / `happy-dom` opt-in nehmen (Test-Assertion-Inhalte bleiben per Nicht-Ziele außer Scope; diese Regel deckt nur Infrastruktur).
- **MUSS** den Research-Audit-Trail unter `spec/frontend/webview-ui-optimization/research/<domain>.md` synchron mit dieser Spec halten; jede normative Regel oben ist mindestens an einen Eintrag dort verankert, der seinerseits ≥ 2 unabhängige autoritative Quellen zitiert. Eine **volatile externe Aussage** (ein Upstream-Versions-Pin, die API-Signatur / der Default / das Laufzeitverhalten einer Drittanbieter-Bibliothek oder ein Default eines externen Tools), die den `webview-ui-optimize`-Skill oder `webview-ui-expert`-Agent zu einem Schreibvorgang oder einem Audit-`fail` in einem Consumer-Repo lenkt, wird am strengeren **Release/dispatch-Tier** von drei unabhängigen Quellen gemäß `spec/claude/research-triangulate/` §Author-time assertions gehalten; der Zwei-Quellen-Floor bleibt die Baseline für langlebige Standards-Level-Aussagen (W3C / WCAG / ARIA / MDN), bei denen eine zweite autoritative Quelle die Halluzinations-Risiko-Schwelle des Triangulations-Gates bereits übersteigt.

## Akzeptanzkriterien

- [ ] Jede Page-Level-Komponente in einem Ziel-Repository rendert innerhalb des LCP ≤ 2,5 s / INP ≤ 200 ms / CLS ≤ 0,1 p75-Budgets auf einer repräsentativen Device-Klasse.
- [ ] `nginx-security-headers.inc` erzielt einen Mozilla-HTTP-Observatory-Grade A oder A+; jeder Abfall blockiert das Release.
- [ ] Keine Produktions-Response trägt `*.js.map`; nginx blockiert `*.map` auf der Location-Ebene.
- [ ] Kein `dangerouslySetInnerHTML` existiert außerhalb einer code-eigentumsverwalteten Allow-List von Komponenten, die in eine Trusted-Types-DOMPurify-Policy gewickelt sind.
- [ ] ESLint `no-restricted-imports` lehnt Barrel-Importe von `@mui/icons-material` (und jeden äquivalenten weiten Barrel) repository-weit ab.
- [ ] `react-i18next` ist mit `supportedLngs`, `fallbackLng`, expliziter Detector-`order` und -`caches` sowie `react.useSuspense: true` initialisiert; ein automatisierter Check bestätigt, dass `<html lang>` / `<html dir>` bei `languageChanged` mutiert werden.
- [ ] Jeder Recharts-Chart im Repository rendert eine Textalternative und einen Datentabellen-Fallback und aktiviert `accessibilityLayer`.
- [ ] `vitest-axe` läuft in CI und meldet null Violations pro Page-Level-Komponente; die JSDOM-Contrast-Rule-Beschränkung ist dokumentiert und wird durch einen Browser-Mode- oder manuellen Contrast-Pass verifiziert.
- [ ] Jede Route nutzt React-Router-v7-Lazy-Module mit `<Suspense>`-+-`<ErrorBoundary>`-Paaren, und das Layout mountet `<ScrollRestoration/>`.
- [ ] CVE-Schwellen des Produktions-Dependency-Baums und das Lockfile-Drift-Gate gehören `spec/project/dependency-audit/` und werden dort verifiziert (laut §Nicht-Ziele); diese Spec verweist auf diesen Eigentümer, statt hier eine eigene Schwelle festzuschreiben.
- [ ] Der `webview-ui-optimize`-Skill produziert eine Zeile-pro-Regel-Audit-Tabelle für das Repository mit `pass` / `fail` / `n/a` und den betreffenden Dateipfaden für jeden `fail`.

## Offene Fragen

- ~~Emotion + Trusted Types: Ob die Emotion-Runtime unter einer erzwungenen `require-trusted-types-for 'script'`-CSP mit MUI v9 sauber arbeitet, ist unverifiziert; vor der Behandlung von Audit-`fail`-Zeilen zur Trusted-Types-MUSS-Regel gegen den Referenz-Stack verifizieren.~~ **Entschieden (2026-07-24):** sie arbeitet sauber. `require-trusted-types-for 'script'` schützt nur Script-/HTML-DOM-XSS-Sinks (`innerHTML`, `script.src`, `document.write`), die die W3C-Trusted-Types-Arbeit noch nicht auf CSS-/Style-Sinks ausgeweitet hat; Emotion (weiterhin MUI v9s Default-Engine) injiziert via `<style>`-Tags, die durch den `style-src`-Nonce gesteuert werden, nicht durch einen Script-Sink, und liegt damit außerhalb des Direktiven-Scopes. Die MUSS-Regel unter §Sicherheit › CSP wird entsprechend qualifiziert: sie bindet HTML-Einfüge-Sinks, und ein Audit **DARF** kein Trusted-Types-für-`script`-`fail` gegen Emotion-/MUI-Styling erheben. Quellen (≥ 3, Volatile-External-Tier gemäß `spec/claude/research-triangulate/` §Author-time assertions): MUI-CSP-Guide (`mui.com/material-ui/guides/content-security-policy/`, Emotion→`style-src-elem`-Nonce); W3C-Trusted-Types-Explainer (`github.com/w3c/trusted-types`, `'script'`-Sink-Scope, CSS noch nicht abgedeckt); `content-security-policy.com/require-trusted-types-for/`; MUI v9 behält Emotion-Default (`npmjs.com/package/@mui/material` v9). Festgehalten im Aktualitäts-Nachtrag von `research/security.md`.
- CSS Scroll Snap (Research `ux.md`, Praktik #25) bleibt nicht-normativ, bis eine zweite unabhängige Quelle sie stützt; beim nächsten Research-Refresh übernehmen oder verwerfen.
- Der Wartungsstatus von `vitest-axe` und die `@vitest/browser`-+-axe-core-Route (die die JSDOM-Color-Contrast-Beschränkung aufheben würde) sind ungeklärt; beim nächsten Test-Infrastruktur-Bump neu bewerten.
- ~~Ob sich `palette.contrastThreshold` unter der MUI-v9-`colorSchemes`-+-`cssVariables`-API identisch verhält (und ob v9 die Dark-Mode-Kontrast-Defaults verschärft), ist unverifiziert; vor der Durchsetzung der 4.5-Schwelle als hartes Audit-Gate erneut prüfen.~~ **Entschieden (2026-07-24):** sie greift weiterhin unter `colorSchemes` + `cssVariables`, weil jede Scheme-Palette durch dieselbe `augmentColor`-/`createPalette`-Ableitung zur Theme-Erzeugungszeit verarbeitet wird (Default-`contrastThreshold` bleibt `3`); CSS-Variablen ändern nur, wie aufgelöste Tokens emittiert werden, nicht wie `contrastText` berechnet wird. Zwei Vorbehalte machen die Schwelle zu einer Heuristik, nicht zu einer Garantie, sodass der 4.5-Wert **kein** eigenständiges hartes Audit-Gate ist: sie wirkt nur auf **angepasste** Palettenfarben (eingebaute Defaults tragen festes `contrastText`), und MUI dokumentiert die Kurve als nicht-linear und warnt, sie könne kontraproduktiv sein, mit Empfehlung zur Kontrast-Verifikation. Die MUSS-Regel unter §Visuell wird qualifiziert, sodass der WebAIM-/manuelle Kontrast-Durchlauf das eigentliche Gate ist. Quellen (≥ 3, Volatile-External-Tier gemäß `spec/claude/research-triangulate/` §Author-time assertions): MUI-Palette-Doc (`mui.com/material-ui/customization/palette/` — Schwellen-Semantik, Nur-angepasste-Farben, Nicht-linear-Warnung); MUI-CSS-Theme-Variables-Doc (`mui.com/material-ui/customization/css-theme-variables/overview/` — `colorSchemes` emittieren aufgelöste Palette als Variablen); MUI-v9-Release, der die `colorSchemes`-API bestätigt (`mui.com/blog/introducing-mui-v9/`). Festgehalten im Aktualitäts-Nachtrag von `research/accessibility.md`.

## Quellen

Jede normative Regel oben ist an die per-Domäne-Research-Notes unter `spec/frontend/webview-ui-optimization/research/` verankert; jeder Eintrag dort zitiert mindestens zwei unabhängige autoritative Quellen. Regeln, die explizit als Projekt-Konventionen markiert sind, sind bewusste Hausregeln und von der Zwei-Quellen-Verankerung ausgenommen. Volatile externe Aussagen (Upstream-Versions-Pins, Drittanbieter-API-Signaturen / -Defaults / -Laufzeitverhalten, Defaults externer Tools), die einen konsumierenden Skill oder Agent zu einem repo-externen Schreibvorgang oder Audit-`fail` lenken, werden am ≥-3-Quellen-Release/dispatch-Tier gemäß `spec/claude/research-triangulate/` §Author-time assertions gehalten—die beiden OQ-Auflösungen oben sind die durchgearbeiteten Beispiele—während langlebige Standards-Level-Aussagen den Zwei-Quellen-Floor behalten. Nachträgliche Aktualitäts-Korrekturen (Recharts-3-`accessibilityLayer`-Default, Vite-8-`output.codeSplitting`, Zod-4-Fehler-API, MUI-`Dialog`-Implementierung, Trusted-Types- und Popover-API-Browser-Support, RFC 9110) sind im datierten Aktualitäts-Nachtrag jeder Research-Datei festgehalten (zuletzt: 2026-07-24):

- `spec/frontend/webview-ui-optimization/research/performance.md` — 27 Praktiken + 9 Anti-Patterns (web.dev, react.dev, vitejs.dev, mui.com, redux.js.org, reactrouter.com, react-hook-form.com, MDN, nginx.org, day.js.org, axios-http.com, vitest.dev, RFC 8246).
- `spec/frontend/webview-ui-optimization/research/security.md` — 28 Praktiken (OWASP Cheat Sheets, MDN, W3C Trusted Types, web.dev, Mozilla HTTP Observatory, Vendor-Docs).
- `spec/frontend/webview-ui-optimization/research/accessibility.md` — 24 Praktiken (W3C WAI WCAG 2.2, ARIA Authoring Practices Guide, MDN, WebAIM, Deque, A11y Project, Vendor-Docs).
- `spec/frontend/webview-ui-optimization/research/i18n.md` — 26 Praktiken (W3C i18n WG, Unicode CLDR / TR10, ICU, MDN, Google Search Central, RFC 7231, Vendor-Docs).
- `spec/frontend/webview-ui-optimization/research/ux.md` — 30 Praktiken (Nielsen Norman Group, web.dev, MDN, W3C, WHATWG, Material Design, Apple HIG, Vendor-Docs).
