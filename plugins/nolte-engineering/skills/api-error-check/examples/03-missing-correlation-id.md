# Example 03 — static error id + wrong status → warning findings

The contract-conformance path below the leakage line. The error body
matches the declared shape, but the correlation id is a hard-coded
constant (defeating log correlation) and one handler returns the wrong
status code. Exercises the warning severity, the dynamic-id check, and
the status-semantics table.

## Input prompt

> Does REQ-041's error handling conform?

## Input files

`package.json` depends on `express`. The requirement id `REQ-041`
resolves through the project layout to `src/routes/billing.ts`. A
shared `src/errors/contract.ts` declares the error body
`{ errorId, code, message, path }`. In `billing.ts`:

```ts
// line 30: static id — same value on every occurrence
res.status(409).json({ errorId: "ERR-BILLING", code: "invalid_card", ... });
// line 44: validation failure returned as 500
res.status(500).json({ errorId: "ERR-BILLING", code: "bad_amount", ... });
```

## Expected behaviour

1. **Framework detected** as **Express** (`res.status(...).json(...)`).
   Target resolved from the requirement id `REQ-041` to
   `src/routes/billing.ts` via the project's own layout — never a
   hard-coded path. Inputs resolved from: argument (target) + discovery
   (contract).
2. **Body shape passes.** Both responses match the `contract.ts`
   shape and populate the declared fields — so this is *not* a leakage
   or missing-field case.
3. **Static id — warning.** `src/routes/billing.ts:30` (and :44) use
   the constant `"ERR-BILLING"` for `errorId`; a per-occurrence value
   is required, so a constant defeats correlation. Reported as
   **warning** with file:line.
4. **Wrong status — warning.** Line 44 returns a validation failure as
   `500`; the situation table expects `400`/`422`. Reported as
   **warning** (got 500, expected 400/422).
5. **Verdict: ❌ 2 findings (0 critical, 2 warning).** No critical
   leakage, so the verdict stays below the security-audit pointer. The
   report names the contract and framework it measured against; nothing
   is edited.
