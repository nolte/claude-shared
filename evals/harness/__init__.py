"""Behavioural-eval harness for the nolte-shared plugin's skills and agents.

Layers:
- Deterministic, token-free core (`scorecard`, `compare`) — unit-tested, always runs.
- LLM-driving layer (`runner`, `judge`) — every real model call is gated behind the
  `RUN_EVALS=1` environment switch so the default `task test` stays free and green.

See `runner` for the headless-invocation mechanics and their known limitations.
"""
