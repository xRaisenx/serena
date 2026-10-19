# CODEMIND Serena V2 — MVP Charter and Source-Baseline Contract

**Document status:** DESIGN BASELINE — not implementation or deployment acceptance  
**Date:** 2026-10-18  
**Owner:** CODEMIND product / single accountable CODEMIND-Serena engineering owner  
**Base:** existing `xRaisenx/serena` draft PR #1, branch `codemind/mvp-serena-loop-guard`, reviewed HEAD `e3bc28f006897988022096f155b2d93af1b958e9`  
**Upstream:** `oraios/serena`; preserve SPDX, copyright, redistribution and GPL-3.0-or-later obligations. SolidLSP is MIT; do not mislabel the combined derivative as proprietary/MIT.

## 1. Product promise

CODEMIND is a **project-agnostic, locally owned semantic engineering control plane**. It couples Serena's symbol-aware code intelligence to evidence-constrained routing, deterministic diagnosis, governed failure learning, verified execution ownership, Codex lifecycle advice, FU-style *conditional* lookahead and an operational Windows console. It makes an AI-assisted coding session easier to understand, safer to operate, and less likely to repeat a disproven tactic.

It is **not** a new LLM, a magical 100-agent swarm, a promise of zero defects, or a replacement for Windows Commander. A CODEMIND-100 expert means a **reference profile and methodology selected by evidence**; selection does not create a process or independently validate code.

Core user journey:

1. User opens Mission Control, unlocks with a **separate** operator credential and selects an activated project.
2. UI reports actual Serena/MCP/LSP states, installed CODEMIND modules, tool availability, connection provenance and guards. Unknown is rendered unknown, not healthy.
3. User submits a scoped coding objective. CODEMIND classifies the work and selects 1 primary method plus only necessary supporting specialist references.
4. Host agent uses Serena's existing semantic overview/references/diagnostics. Mutation requires the *original* Serena and repository ownership permissions; no rerouting through Commander to bypass denial.
5. The owner establishes a reproducer/falsifier, performs the minimal authorized edit, collects post-edit diagnostics and actual tests. Timeout/inconclusive != PASS.
6. A failure is fingerprinted and correlated to task/source generation; an unchanged equivalent strategy is prevented after the policy threshold; distinct hypotheses remain eligible.
7. The owner requests the **canonical next action**; future actions are advisory and may not execute or authorize work.
8. Only independently evidenced current-generation tests, review, remote delivery and consumer verification can close the requested acceptance gate.

## 2. Proof baseline on this design date

| Surface | Source-observed condition | Acceptance |
|---|---|---|
| Serena fork | Existing MCP, LSP, symbols, CODEMIND tools; 35 callable Serena Code Commander tools exposed through current connector | Source / prior runtime observations, not V2 completion |
| Mission Control | Flask blueprint `src/serena/codemind/dashboard_api.py`; HTML/CSS/JS `src/serena/resources/dashboard/codemind/` | Current v1 UI, not V2 implementation |
| API v1 | `GET /codemind/api/overview`; `/tunnel/status`, `/tunnel/key`, `/tunnel/doctor`, `/tunnel/start`, `/tunnel/stop` | Code exists; individual live calls previously tested, not blanket PASS |
| Skills | `SkillManifestRegistry` reads `.codemind/skills`; `SkillRouter` token overlap, max 3 | One CODEMIND skill observed, not 25 NMBV skills copied |
| Anti-loop | `FailureGuard` SQLite call-signature protection; `NextActionPlanner` limited local recommendation | Exists; not NMBV governed lesson promotion |
| Commander | `CommanderHealthProbe` nonce/HMAC peer contract in CODEMIND; independent Commander code/process owned elsewhere | Process presence observed; authenticated readiness not yet proven |
| Codex hooks | Project-scoped `.codex/hooks.json` and JS handler; isolated tests | Trusted normal-session invocation still independent gate |
| Remote ChatGPT | Tunnel-client profile/credentials and readiness checked in prior work | ChatGPT remote `tools/list` and `tools/call` end-to-end not independently proven |
| NMBV method library | 25 skills and `nmbv_skill_route`, `nmbv_next_action` callable on NMBV Bot | **Reference/adapter source**, not native CODEMIND runtime |
| NMBV runtime | Latest inspected coordinator `UNBOUND`, dirty separate checkout | Do not mutate NMBV or infer task authority |

Historical acceptance may be superseded by fresh runtime evidence. All progress reporting must label source, test, current installed bytes, active runtime and client observations separately.

## 3. MVP in-scope

**P0 product:**
- Preserve upstream Serena's semantic operations, MCP, active project and LSP lifecycle.
- Project-independent `codemind_capabilities` + schema-versioned `codemind_overview` observable on the same-origin dashboard.
- Professional Mission Control layout and functional navigation; no placeholder buttons or fabricated counts.
- Local authenticated token session; separate DPAPI-sealed tunnel key; secrets never logged/exported.
- Declarative project skill discovery; guarded, provenance-bearing skill router with `selected != loaded != executed`. CODEMIND-100 task-wiring/cortex reference metadata and its ten councils are eligible in MVP S2; individual expert profiles are displayed only if packaged, attributed and validated as **reference profiles**, not workers.
- Task + source-aware fault fingerprints; third unchanged failed call denied under configured guard; independent hypothesis may proceed; scoped diagnostic packets after edits.
- Canonical next action, 5-stage preview, up to 20 **non-executable** FU advisory candidates.
- Read-only learning registry, captured/assessed/candidate/applied outcome states with proof, rollback and privacy boundaries. Actual promotion gated behind independent implementation and authorization.
- Process/peer health and circuit-breaker observability for independently owned Windows Commander; no cross-process kill button.
- 11 Codex event specs only where host actually advertises and trusts that event. No hook installation by merely viewing dashboard.
- Windows installer/startup/repair/runbook, versioned migration, failure/negative integration tests.

**P1 after MVP evidence:**
- Optional authenticated native NMBV Bot adapter plus advanced expert-profile scoring beyond the source-backed reference-only MVP catalog; never duplicate task ownership.
- Authorized worker task execution with per-resource ownership and consumer proof.
- Long-running 24-hour health/durability, crash-recovery and ChatGPT consumer connection verification.
- Full CODEMIND expert scoring beyond the existing lexical, declarative first-pass classifier; no claims of general intelligence.

**Out of scope:** client NMBV business tables/permissions, copying customer records, changing production databases, replacing NMBV's governance/controller, duplicate supervisors, automatic protected-Git merges, undocumented third-party credentials, public unauthenticated RPC, claiming all 100 expert profiles are independently executing.

## 4. Non-negotiable invariants

- **One canonical writer per owned resource.** NMBV task/page/session authority is never granted by CODEMIND routing; source changes use host-validated scope and CAS/JIT.
- **Two independent services.** CODEMIND Serena and Windows Commander have separate process ownership, persistent state, restart policy and watchdog authority. Mutual health observation cannot form a synchronized restart storm.
- **Evidence provenance.** Every status includes `observed_at`, `source`, `revision` when available and `state`. Listening PID, key-present, cached green, artifact SHA, Git merge and live remote call are distinct.
- **Anti-loop.** After two comparable confirmed failures at same task/source/operation/target, stop unchanged strategy; allow a materially different falsifying test. Intentionally failing negative tests aren't regressions; timeout is not success.
- **No false learning.** `CAPTURED` != `ASSESSED` != `CANDIDATE` != `APPLIED`; only applied/rolled-back lessons enter reusable policy.
- **No secret exposure.** Dashboard/operator/peer/control-plane credentials live in separate stores and never travel in exported telemetry or URL query strings.
- **Bounded overhead.** No eager full-100-persona prompt or all-25-skill context dump. Hooks load compact session guidance, selected bodies only.
- **Observe, don't assume.** Unknown or unavailable backend capabilities render as `UNVERIFIED` or `NOT_IMPLEMENTED`. No optimistic readiness badges.

## 5. End-to-end MVP definition of done

1. Source-aware implementation matches approved specs at an immutable review SHA.
2. Windows clean build/start yields successful authenticated MCP `initialize`, `tools/list`, a Serena symbol tool call and a CODEMIND route/next-action call.
3. GUI all visible actions tested against actual endpoint response contracts, including failure/denied/retry states, keyboard navigation, and narrow/mobile viewport.
4. Fault/learning data survive controlled CODEMIND process restart; no loss of unrelated Commander service state.
5. Guard denies unchanged third attempt and denies unbound/unauthorized mutation; genuine alternate strategy still works.
6. Native CODEMIND specialist selection wired to loaded reference/body where licensed and installed; report IDs/source/evidence, not imaginary expert workers.
7. Negative security checks: malformed inputs, CSRF, path escape/symlinks, wrong identity, stale revision, credential leak, duplicate actions.
8. Independent Commander peer handshake and fault-isolation tests; no repeated restart loop.
9. Tunnel diagnostics, local ready state and fresh **ChatGPT remote tool call** separately evidenced.
10. Reproducible tests and benchmark evidence (latency, P95/P99, CPU/RAM trend, crash/reconnect) recorded without arbitrary pass inference; 24h soak remains a separate acceptance gate if not run.
11. Protected Git review/delivery, independently verified running revision, sign-off or typed blocker; no `COMPLETE` while required gates are unverified.

**Detailed contracts:** `01-ARCHITECTURE-SPEC.md`; **GUI:** `02-MISSION-CONTROL-UX.md`; **slices:** `03-IMPLEMENTATION-SLICES.md`; **plan:** `04-DELIVERY-AND-ACCEPTANCE.md`; **skill/capability source map:** `05-NMBV-TO-CODEMIND-CROSSWALK.md`.

**Status of these documents:** approved implementation targets remain **PROPOSED**, not software shipped.
