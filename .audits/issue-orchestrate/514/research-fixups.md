# Research fixups — issue #514 (re-run of §3/§4/§5 + §2-Selenium)

> Supersedes the §3 stub in research-dossier.md; §4/§5 were retry-cap failures in the workflow.

## §3 Instrumentation-first debugging (settled)

**Summary:** When static code/DOM analysis cannot decide *why* an E2E test failed, make the test louder, not guess. pytest rewrites `assert` at import time (shows both operands + producing sub-expressions + type-aware diffs) automatically; Playwright `expect()` and Cypress `.should()` auto-retry and emit matcher+locator+timeout+expected/received+call-log. Generic context (operands, diff, retried locator, timeout) is framework-automatic; **semantic** context (which mechanism, surrounding UI state) must be hand-written into the assertion message or a self-reporting helper. Good-failure-message rubric (testable, 4 parts): Expected / Found (read back from live subject) / Surrounding UI state / Most-likely-cause (names a mechanism). Prefer permanent in-suite instrumentation (custom matchers, self-reporting helpers, `register_assert_rewrite`d helper libs, `expect.configure` defaults) over throwaway probe code.

Key sourced facts:
- pytest assertion rewriting: introspection auto-added, structural (`assert 3 == 4` `+ where 3 = f()`), type-aware diffs — https://docs.pytest.org/en/stable/how-to/assert.html
- Introspection only reaches test modules; extracted helper libs go silent unless `register_assert_rewrite(*names)` — https://docs.pytest.org/en/stable/reference/reference.html
- Hand-written message is additive (prints alongside auto introspection) — assert.html
- `pytest_assertion_pass` hook (experimental, `enable_assertion_pass_hook=true`) for passing-assert telemetry — reference.html
- pytest-icdiff (side-by-side diff, zero code), pytest-clarity (only under -vv, opt-in verbosity)
- Playwright `expect()` web-first matchers auto-retry (5s default, independent timeout); failure msg includes matcher/locator/timeout/expected-received/call-log; `expect(locator,'cause')` msg arg; `expect.poll`/`expect.toPass` for custom conditions; `expect.soft` multi-finding — https://playwright.dev/docs/test-assertions
- Playwright actionability (visible/stable/enabled/receives-events/editable) → timeout = "which precondition never became true" — https://playwright.dev/docs/actionability
- Cypress retry-ability: re-runs query chain until pass or defaultCommandTimeout (4s); queries+`.should` retry, `.click` one-shot; `expect(value,'label')`; `.should(cb)` for self-reporting helper reading back live subject — https://docs.cypress.io/app/core-concepts/retry-ability

Good-message rubric — useless: "Option 'FREQ=WEEKLY' not found in the open dropdown" (3 mechanisms produce it); good: "expected 'FREQ=WEEKLY', field holds 'FREQ=MONTHLY' — the click most likely landed on a neighbouring option" (reports found-state + names mechanism).

Open questions: Playwright call-log exact structure undocumented (revisit vs real transcript); `pytest_assertion_pass` still experimental (may-use not must); Cypress lacks `register_assert_rewrite` equivalent; whether rubric needs a 5th mandatory screenshot/DOM-snapshot field.

## §4 Hunt vacuous assertions and silent-empty readers (settled)

**Summary:** Highest-consequence class — suite green while verifying nothing. Layered detection: (1) cheap AST/lint every PR catches syntactic patterns; (2) custom Semgrep taint/AST rule catches empty-default-reader→assert chains; (3) mutation gate on changed files proves falsifiability dynamically (a *surviving mutant* = proof an assertion never fails). Coverage cannot see this defect (a called-but-unchecked return still counts as covered) — mutation score, not coverage, is the credibility gate.

Mechanical detectors (sourced):
- Ruff `S110` try-except-pass / `S112` try-except-continue (= Bandit `B110`/`B112`) — bare except around waits/postconditions — https://docs.astral.sh/ruff/rules/try-except-pass/ , https://bandit.readthedocs.io/en/latest/plugins/b110_try_except_pass.html
- Ruff `PT017` pytest-assert-in-except (assert on error path silently never runs) — https://docs.astral.sh/ruff/rules/pytest-assert-in-except/
- Ruff `F631` assert-tuple (`assert (cond,"msg")` always truthy → "never fails") — proves AST-tautology category detectable — https://docs.astral.sh/ruff/rules/assert-tuple/
- Semgrep custom taint rule: source = `return ""`/`[]`/`None` readers, sink = `assert $X == ""` — https://semgrep.dev/docs/writing-rules/rule-ideas
- Mutation testing = "test your tests": surviving mutant = weak/missing assertion. Python mutmut/cosmic-ray (cosmic-ray classifies killed-by-assertion vs killed-by-exception); JS Stryker (score = detected/(detected+survived+no-coverage)); Java PIT — https://qaskills.sh/blog/mutmut-python-mutation-testing-guide , https://stryker-mutator.io/docs/General/faq/
- Coverage-vs-mutation gap formally studied — https://arxiv.org/pdf/2309.02395
- "Never-failed-in-CI" signal obtainable from flaky-test history (Datadog/CircleCI/etc.) → tautology candidate — https://www.datadoghq.com/knowledge-center/flaky-tests/
- "Assertionless"/"Empty Test" is a catalogued smell; TestSmellDetector flags statically — https://testsmells.org/pages/testsmells.html

Detection procedure (ordered, testable): 1) syntactic lint sweep (S110/S112/PT017/F631); 2) enumerate empty-default readers (AST: FunctionDef with literal-empty Return on non-exceptional path); 3) trace `assert ==""/[]/None` operand origin to a step-2 reader (Semgrep taint or AST join); 4) require every reader to distinguish empty-vs-not-found (terminal `raise` on "could not look"); 5) mutation gate on changed files (fail below score floor, prefer killed-by-assertion); 6) intersect with never-failed-in-CI history; 7) record finding with its detector id.

Open questions: mutation-score floor value/scope; dataflow precision through page-object indirection; CI history retention; equivalent-mutant / legitimately-empty-result false positives; JS/Java arm wiring.

## §5 Parallel multi-channel triage (settled)

**Summary:** Dispatch 2+ read-only analyses of the same run simultaneously, each restricted to ONE evidence modality (CODE: source/node_modules/tracebacks; PIXEL: screenshots-as-images), each required to report what it settled AND what it structurally could NOT. Channels chosen for disjoint reachable evidence → structurally decorrelated error (unlike same-modality ensembles whose error stays correlated, r≈0.53–0.69). Third channel = server/request log; fourth = browser console/network. Orchestrator value = composition: corroborate on convergence, stop-and-surface on conflict (never vote), carry every could-not-settle back as residual open question.

Sourced facts:
- Denzin data-source/methodological triangulation — https://scholarworks.waldenu.edu/cgi/viewcontent.cgi?article=1187&context=jsc
- In-repo `spec/claude/research-triangulate/en.md`: independent provenance, conflict→stop-and-surface not vote, unreachable→`unverified`+hand-back — the triage orchestrator reuses these three rules
- Channel independence buys decorrelation; must be engineered by partitioning evidence not cloning agents (inter-agent error r≈0.53–0.69 same-modality) — https://arxiv.org/html/2511.16708
- Blind-to-other-modality mirrors LLM-council blind design — https://www.mindstudio.ai/blog/how-to-build-llm-council-ensemble-agents
- CODE settles: which path threw, library defaults/roles from source, wait/locator logic; cannot see rendered state. PIXEL settles visual truth ("dialog still open while test times out", overlay z-order, horizontal overflow) — e2e-test-stability: "what the app showed" ← screenshot. SERVER/REQUEST-LOG settles "was the server even asked" (count diffs), 4xx/5xx, concurrency defects — "what the server did" ← request log. CONSOLE/NETWORK settles client crash vs backend, client-observed timing — https://testdino.com/blog/debug-playwright-tests
- Cost: fan-out ~halves wall-clock but token cost rises steeply (~up to 7× single thread); pays off because channels independent — https://blog.logrocket.com/splitting-across-ai-agents/
- Run artifacts must be retained per run (e2e-test-automation mandates screenshot trail + protocol)

Dispatch recipe (testable): min 2 mandatory (CODE+PIXEL); +channel3 (server/req log) when symptom is timeout/state-change/data-mismatch; +channel4 (console/network) when no-op interaction/suspected client crash; cap 4, one per modality, never 2 on same modality. All dispatched in one fan-out, read-only. Per-channel brief: (a) test id + one-line symptom; (b) exactly one modality named + explicit instruction NOT to reason about others (code brief carries no image; pixel brief carries no source path); (c) return schema `{verdict, evidence[] (cite modality-owned artifact), could_not_settle[] (non-empty or "nothing outstanding"), confidence}`. Merge: attribute each claim to owning modality; convergence=corroboration; uncovered could_not_settle=residual OQ; conflict→stop-and-surface record, no auto-verdict. Testable-on-dispatch assertions: code brief has no image, pixel brief no source path; every return has non-empty could_not_settle; "what app showed" attributed to pixel, "what server did" to request-log; disagreement emits conflict record.

Open questions: is 4 the ceiling (DOM-snapshot/video as distinct channels?); auto vs operator channel-selection; real cross-channel error correlation; token-cost break-even for 3rd/4th channel.

**Dispatch-brief refutation requirement (comment H — placed here as authoritative home).** Every analysis/remediation brief states its hypothesis AND explicitly authorises + expects the specialist to REFUTE it: "if the evidence contradicts this, say so and change nothing rather than forcing the fix to fit." Grounded in the campaign (specialists corrected the orchestrator ~10 times, substantively). Not E2E-specific; this spec is the single authoritative statement, cross-referenced from the dispatch locus. Testable: a brief without the refutation clause is a defect; a channel's `could_not_settle` / contradiction return is a first-class outcome, not a failure to complete.

## §2 Selenium supplement — evidence channels (settled)

**Summary:** Selenium/Grid exposes four native channels — WebDriver BiDi (console+network events), the legacy CDP bridge (Chromium-only, deprecated), Grid `selenium/video` MP4 session recording, `get_screenshot_as_*` stills — plus a bolt-on HAR proxy (no native HAR). Fragmented and browser-dependent: BiDi is standards-track but binding coverage is uneven (Java/C#/JS still missing for logging), CDP is deprecated + Chromium-only, full-page screenshots native only on Firefox. **Load-bearing foreclosure: Selenium has NO native time-travel DOM-snapshot channel** (no Trace Viewer equivalent) — "what was the DOM at step N" needs external instrumentation (per-step page_source/outerHTML dump).

Sourced facts:
- BiDi logging: `add_console_message_handler()` + `add_javascript_error_handler()` (real-time, replaces pull-based get_log) — https://www.selenium.dev/documentation/webdriver/bidi/logging/
- BiDi network: `beforeRequestSent`/`responseStarted`/`responseCompleted`/`authRequired` → URL/method/status/headers + intercept; but NO response-body / per-request timing documented — https://www.selenium.dev/documentation/webdriver/bidi/w3c/network/
- CDP bridge: richer (interception, Performance metrics) but "will eventually be removed when WebDriver BiDi implemented", Chromium-only — https://www.selenium.dev/documentation/webdriver/bidi/cdp/network/
- No native HAR → external proxy (BrowserMob unmaintained / mitmproxy active)
- Grid `selenium/video` MP4 via FFmpeg, `se:recordVideo` capability, `/videos` dir, `se:retainOnFailure` — https://github.com/SeleniumHQ/docker-selenium ; video answers "over time / races/timing", screenshot answers pixel-addressable exact step
- `get_screenshot_as_*` = viewport only; full-page browser-split (Firefox native / Chrome via CDP captureBeyondViewport) — https://www.testsmith.io/en/blog/selenium-4-full-page-screenshots

Selenium channel → question: BiDi console/JS-error → "what logged / did app throw"; BiDi network → "did request fire, URL/method/status/headers" (forecloses body+timing+HAR); CDP → interception+Performance (forecloses cross-browser+durability); proxy → HAR (extra infra); Grid video → "what over time" (forecloses pixel-addressable step assert); screenshots → "what at step N" (forecloses one cross-browser full-page primitive); **time-travel DOM snapshot → NONE native (needs external instrumentation)**.

Open questions: BiDi response-body/timing in later revision?; CDP removal release?; Grid video event-vs-polling reliability/fallback; concrete DOM-time-travel workaround to name; which HAR proxy is portfolio standard.
