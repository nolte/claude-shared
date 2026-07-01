# Example 01 — FastAPI surface that conforms → clean verdict

The happy path. A FastAPI router whose error handling matches the
project's declared error contract: uniform body shape, a
dynamically-generated correlation id, correct status codes, and no
internal-detail leakage. Exercises framework detection, contract
discovery, and the ✅ Conformant verdict.

## Input prompt

> Check the error handling in `app/api/plants.py`.

## Input files

`pyproject.toml` depends on `fastapi`. A shared
`app/errors.py` declares an `ErrorBody` model with fields
`error_id`, `error_code`, `message`, `path`, `timestamp`, and a
global `@app.exception_handler` that fills `error_id` with
`uuid4().hex` per occurrence. `app/api/plants.py`:

```python
if plant is None:
    raise NotFoundError(code="plant_not_found", message="Plant not found")  # -> 404
if not owns(user, plant):
    raise ForbiddenError(code="not_owner", message="Not your plant")        # -> 403
```

## Expected behaviour

1. **Target resolved** to `app/api/plants.py` (path argument, not a
   requirement id). Framework detected as **FastAPI** from the
   `fastapi` dependency plus `APIRouter` imports.
2. **Contract discovered** at `app/errors.py` — the `ErrorBody` model
   is recorded as the required shape; `error_id` is the correlation
   field. Inputs resolved from: discovery.
3. **Body uniformity passes.** Every error path routes through the
   global handler, so all responses carry the full `ErrorBody` shape
   with populated required fields.
4. **Correlation id is dynamic.** `uuid4().hex` per occurrence — not a
   static constant; passes the dynamic-id check.
5. **Status semantics pass.** Not-found → 404, forbidden → 403 match
   the situation table.
6. **Leakage scan clean.** No `traceback`, `str(exception)`, or
   rendered query reaches a response body; every path has a handler.
7. **Verdict: ✅ Conformant.** The report states the framework, the
   contract path, and the severity floor; the summary row shows all
   endpoints conforming, zero leakage hits. Nothing is edited.
