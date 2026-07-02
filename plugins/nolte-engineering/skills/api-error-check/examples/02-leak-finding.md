# Example 02 — internal-detail leakage → critical finding

The security-relevant path. A handler puts a raw driver exception
message into the response body, and a second route has no error
handler at all, so it falls through to the framework default.
Exercises the leakage scan, the critical severity, the file:line
attribution, and the pointer into the security audit.

## Input prompt

> Audit the error responses in `services/orders/` before we ship.

## Input files

`requirements.txt` depends on `flask`. `services/orders/api.py`:

```python
@app.route("/orders/<oid>", methods=["POST"])
def create_order(oid):
    try:
        return place(oid)
    except DBError as e:
        abort(500, description=str(e))     # line 22: raw driver message
```

`services/orders/refunds.py` defines a `POST /refunds` route with **no**
try/except and **no** registered `@app.errorhandler` — an unhandled
`DBError` propagates to Flask's default handler.

## Expected behaviour

1. **Framework detected** as **Flask** (`abort(...)`, `@app.route`).
   Target resolved to the `services/orders/` directory.
2. **Leakage hit — critical.** `services/orders/api.py:22` passes
   `str(e)` (a raw driver message) into the response body. Reported as
   **critical**, attributed to file:line, flagged as a pointer into
   `spec/project/code-security-audit/` — this check surfaces leakage,
   it does not replace the whole-codebase security audit.
3. **Missing handler — critical.** `POST /refunds` has no error path,
   so an exception falls through to Flask's default, which renders a
   stack trace outside production. Reported as **critical** — a missing
   handler is worse than a wrong one, not "no findings."
4. **Verdict: ❌ 2 findings (2 critical).** The summary row shows the
   leakage hit count; the report is sorted severity-then-path so it
   diffs cleanly. No handler code is edited — fixes are the
   developer's follow-up.
