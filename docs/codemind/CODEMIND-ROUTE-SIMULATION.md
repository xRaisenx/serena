# CODEMIND implementation-route simulation — deterministic advisory study

This comparison is a **design simulation based on known CODEMIND source contracts**, not a benchmark, subagent run, test execution, or measured deployment. Optimize for minimum changes, retained contracts and an achievable vertical slice.

| Route | Dependencies | Friction / operational risk | Outcome |
|---|---|---|---|
| A — Extend native dashboard, add separate linked help page, test static behavior | Existing CSS tokens, stable About link, vanilla JS, current docs | **Lowest**: additive files + one link, no backend/schema change | **Selected for this slice** |
| B — Replace dashboard with new SPA framework | New bundler, new static routes, rebuilt state/auth/telemetry | High: migration risk, more regressions | Rejected |
| C — Build new orchestrator and three-subagent scheduler first | Codex host agent launch API, durable lease store, cancellation, authority | High: host contracts and permissions missing | Deferred to G4 implementation slice |
| D — Present all five gates as green from configuration alone | No independent host proof | Invalid/insecure | Rejected |
| E — Copy unrelated worker pool and relabel it CODEMIND | Unrelated execution context, false portability | Invalid authority and fidelity | Rejected |

## Selected dependency sequence

1. **Now (sandbox UI/doc slice):** read authoritative GitHub branch → add guide.html/css/js and tests → link existing About → operator/FAQ docs → test and review patch. No new backend endpoint, worker, credential or autonomous-execution claim.
2. **G1/G2 provider slice:** verify actual Codex trusted hooks, pin immutable canonical Serena workspace, attest language-server readiness at current source generation.
3. **G3 coverage slice:** enumerate actual project file types, map handler strategies, prove unknown and binary denial/fallback.
4. **G4 host scheduler slice:** integrate the real agent-spawn interface, bound admission to 3 leases, deterministic fair queue, crash/cancel/process cleanup, release/recycle. Do not invoke heavy tests from the builder concurrently.
5. **G5 effect/recovery slice:** operation-specific approval, durable effect journal, idempotency/reconciliation, independent regression and source-runtime identity verification.
6. **Final delivery:** only turn on autonomous Codex deployment when G1–G5 are observed PASS in the actual target environment; record the exact source and running tool revision.

## Definition of done for route A

- Additive, accessible responsive help route accessible from dashboard About.
- How-To, About, scenario-driven FAQs, and use cases explain real workflows and boundaries.
- Deterministic client-only search works; no model call or secret-bearing telemetry.
- Source tests show red → green on new behavior and static link/style checks.
- Patch and source files are exportable with hashes; actual host deployment remains explicitly unverified.

## Do not assume

- Superpowers method selection is equivalent to deployed Superpowers subagents.
- CHATIRE's sandbox test results prove a Windows host is running the patch.
- Static `hooks.json` proves hash trust and callback invocation.
- Existing read-only semantic inspection constitutes full runtime bug-fixing automation.

## Executable offline queue model

`tools/codemind_route_simulation.py` is a pure-Python discrete-event model, not a worker scheduler. Five sample validation jobs with at most three simulated slots result in a peak of **3 modeled active jobs**, two initially queued, and a modeled completion horizon of four abstract time units. A missing cleanup acknowledgment quarantines its simulated lease; it is never silently reused. The model has no process spawning, memory measurement or Codex host API, and its `simulated_schedule_complete` field must never be interpreted as SCC runtime readiness.