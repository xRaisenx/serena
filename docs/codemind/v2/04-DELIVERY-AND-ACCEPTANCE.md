# CODEMIND Serena V2 — Execution, Validation and Release Plan

**Date:** 2026-10-18  
**Status:** Implementation plan / acceptance matrix; no V2 runtime completion claim.  
**Scope:** CODEMIND Serena fork only until independently authorized Commander peer updates. NMBV business app, its production databases and owned worktrees remain untouched.

## 1. Governance / working protocol

1. Read CODEMIND fork's project instructions, check HEAD + dirty status, preserve original upstream notices and current running service identity.
2. The owner starts from S0 evidence and works the *first incomplete bounded slice* of `03-IMPLEMENTATION-SLICES.md`. Route expert methodologies based on relevant source and domain, not 100 simultaneous agent prompts.
3. Use Serena semantic overview/symbol/reference/diagnostics to localize owning code; edit only owned files through guarded/CAS/JIT code path.
4. Tests are **red before fix** where possible, **green at changed revision** afterward. Require failure/negative cases, missing/outdated source and independent consumer test appropriate to change.
5. Repeated equivalent failure -> explicit strategy change, competing hypothesis/falsifier, no attempt masquerading via renamed timeout or tool arguments.
6. For a command returning timeout, error, incomplete log, skipped case or unknown state, record exact result and **do not** mark passed.
7. Only verified scoped diffs go through GitHub with correct expected HEAD and check policy. No destructive reset, broad git clean/stash or force push; no remote-main-only success claim.
8. No parallel CODEMIND/NMBV controller or second Windows Commander watchdog. Need an approved separate Commander owner before patching Commander binary/recovery service.

## 2. Ordered milestone gates (no calendar fiction)

| Milestone | Owned slices | Evidence required | Status at plan creation |
|---|---|---|---|
| M0 Baseline locked | S0 | Current checkout/runtime SHA, v1 tests, observed feature inventory | NOT YET REVALIDATED for V2 |
| M1 Professional GUI functional | S1 | v1 compatibility, v2 read model, all clickable actions, visual/a11y tests | NOT IMPLEMENTED |
| M2 Expert and skills | S2 | Source-backed method catalog, deterministic routing, loaded skill proof | NOT IMPLEMENTED |
| M3 Debug + FU intelligence | S3 + S4 | Task-scoped anti-loop/guard tests, forecast permission negative tests | NOT IMPLEMENTED |
| M4 Governed learning | S5 | Sanitized provenance, stage transition and runtime restart readback | NOT IMPLEMENTED |
| M5 Reliable independent services | S6 | Peer nonce/HMAC, Commander owner check, safe independent recovery | NOT VERIFIED |
| M6 Host + tunnel integration | S7 + S8 | Real trusted Codex events, post-edit diagnostics, client `tools/call` | NOT VERIFIED |
| M7 Release acceptance | S9 | Endurance/security/perf/consumer + installed revision + owner sign-off | NOT VERIFIED |

Milestones may overlap on independent *read-only* validation only. A milestone is **not** given an arbitrary percentage from number of authored files. Use status matrix by test case.

## 3. Master acceptance matrix

| ID | Scenario / gate | Required observation |
|---|---|---|
| C01 | Clean bootstrap | Windows start + authenticated Serena MCP initialize/list/call; correct dashboard URL and revision |
| C02 | Source parity | SHA of reviewed CODEMIND commit equals deployed files/running observed generation or is explicitly reconciled |
| C03 | v1 backward compatibility | Existing Serena symbols/refactoring and CODEMIND key/doctor/start/stop routes preserved |
| C04 | Task ownership and authorization | UNBOUND/wrong scope/stale task/foreign owner denied, valid owner remains usable |
| C05 | Skill manifest discovery | Invalid, duplicate, symlink/escape rejected; only installed enabled module reported |
| C06 | CODEMIND-100 expertise | Registry and task-wiring provenance; one primary council, supporting methods only, no phantom agents |
| C07 | Router materialization | Actual `codemind_skill_route` result, selected body read only if authorized; selected != executed |
| C08 | Anti-loop first/second/third | First and second equivalent confirmed failures observed; third unchanged blocked; alternate tested input allowed |
| C09 | Failure fingerprint | Volatile time/PID/line/duration normalized; real causal differences not collapsed |
| C10 | Post-edit diagnostics | Real targeted Serena symbol/file diagnostics; current source; diagnostics alone not test pass |
| C11 | Focused regression | Reproducer RED pre-edit, GREEN on current revision, affected tests, negative role/path cases |
| C12 | Next-action safety | Exactly one canonical next, preview <=5, FU <=20, future candidates never authorized/executable |
| C13 | Learning stage integrity | Captured/assessed/candidate do not appear applied; applied requires review/proof/delivery |
| C14 | Durable learning | Readback through runtime across approved restart/reconnect; tamper and corruption rejection |
| C15 | Independent Commander | Authenticated peer proof distinct from process presence; Commander continues if CODEMIND fails |
| C16 | Recovery fault injection | Owner-approved separate test instance, bounded retries/cooldown, no mutual restarts and no lost task |
| C17 | Trusted Codex SessionStart | New normal session event observed with correct cwd/source and bounded context; no startup warnings |
| C18 | Real PostToolUse | Actual edit/shell/MCP nested error/timeout processed; negative test intent classified; no false PASS |
| C19 | Hook recursion and overflow | Stop cannot loop; compaction bounds context; secrets not recorded |
| C20 | GUI navigation | Every enabled button/route/link/keyboard action works against real endpoint or is disabled with explanation |
| C21 | GUI visual/responsive | 320/390/768/1024/1440/1920, 200% zoom, no clipping/overlap, WCAG 2.2 AA targeted |
| C22 | GUI error states | 401/403/409/429/500/timeouts, offline/reconnect, empty/large-data states, stale indicators |
| C23 | Credential safety | DPAPI encrypted key, user-scoped access, no plaintext/echo/log, distinct peer/operator/tunnel keys |
| C24 | Tunnel doctor | Wrong key/scope/org, occupied health port, MCP offline, timeout return precise typed cause |
| C25 | Tunnel consumer | Local client ready AND actual authenticated remote ChatGPT tools/list + tools/call at correct revision |
| C26 | Performance and resource budget | Bounded latency, P50/P95/P99 CPU/RAM and queue metrics vs measured baseline; no made-up thresholds |
| C27 | Multi-hour soak | Real clocked window, reconnect, resource drift and alert coverage; 24h if required by release contract |
| C28 | Protected Git delivery | Diff ownership, exact commit/push/PR merge, actual remote main + local/installed runtime check |
| C29 | Operator evidence export | Bounded sanitized JSON, accurate timestamps/fields; no secrets or customer source |
| C30 | Full source/license review | GPL notices preserved, NMBV proprietary/client data not transplanted, no duplicate controller |

All are acceptance **requirements**, not reported green tests. A numeric PASS must cite actual executed command/log artifact and source identity.

## 4. Test matrix by execution level

**Level L0 – static:** schema checks, Python/Node syntax, frontend lint, security scanning for unsafe DOM/secret handling, dependency SPDX and minimum version. *Not runtime acceptance*.

**Level L1 – deterministic unit:** skill registry, router, strategy normalization, anti-loop, staged lessons, FU candidates, typed status components and app reducers; zero skip or timeout.

**Level L2 – contract integration:** Flask/Serena MCP auth, read-only vs write policy, runtime source version, SQLite migrations, mock Commander HMAC negative tests, tunnel doctor error mapping, Codex hook event format.

**Level L3 – live Windows:** installed Serena process + LSP tool call, actual CODEMIND API and GUI clicks in Windows browser; real Commander peer, protected task ID, DPAPI, process isolation, runtime recovery.

**Level L4 – cross-boundary consumer:** ChatGPT tunnel caller + MCP actual tool response; real Codex normal trusted hook session; no false consumer success from control-plane poll-only state.

**Level L5 – durability/release:** benchmark representative workload, failure storm, controlled two-service crash/reboot recovery, 24h uninterrupted service if specified; source/deployment hash parity and sign-off.

Always emit which level each gate passed. L1 fixture does not satisfy L4 or L5.

## 5. Risk register with prevention and falsifier

| Risk / historical lesson | Guard / preventive implementation | Falsifier |
|---|---|---|
| Windows PowerShell 5.1 crashes on ordinary `uv` stderr or missing modern .NET RNG APIs | Keep checked launcher compatibility and exit-code authority | Fresh PS 5.1/7 installation/start under real stdout/stderr |
| CODEMIND key configured but tunnel doctor fails due port conflict | Ephemeral loopback health port; typed cause-specific errors | Occupy 8080 and prove doctor still succeeds/fails for correct cause |
| Service presence mislabeled healthy | Separate PID, nonce/HMAC, MCP initialized, observed-at | Spoof process; readiness remains unverified |
| Codex hooks defined but never trusted/loaded | Host event support/trust and observed trace, bounded context | Normal startup without hook event must fail C17 |
| Source HEAD different from running application | Installed-revision endpoint, source checksums, explicit rollout | Deliberately run old build; dashboard flags mismatch |
| NMBV rule copies leak client task permissions | Own CODEMIND task namespace and denied NMBV adapter mutation | UNBOUND route cannot become a write permission |
| Repetitive failed repairs thrash | Two-equivalent-failure guard, true strategy signature, varied hypothesis | Third changed-timeout-only attempt denied |
| "Smart learning" equals saved note | Captured/assessed/apply proof states | Captured-only lesson absent from applied registry |
| 100 experts equals 100 workers | Registry says reference profiles; loaded/executed separately | No process/job created solely by expert selection |
| UX fake "working" controls | Generated action inventory vs actual endpoints | Every enabled control has successful or explicit denied request evidence |
| Two watchdogs repeatedly restart each other | Single owner per service, circuit breaker, cooldown | Fault injection shows bounded recovery not storm |
| Dirty owner worktree or Git cache mismatch | CAS/JIT on exact resource, safe Git reconciliation | Concurrent foreign edits never overwritten |
| Overloading 100 skills into model context | one selected method, <=3 relevant profiles, compact hooks | Count context tokens and verify upper bound |
| Tests mistaken for live deployment | Source/runner/runtime/consumer separate | Fake source-only pass cannot satisfy C25/C28 |

## 6. Execution artifacts and status model

Per completed slice produce:
- `decision.md`: exact scope, owner, current source HEAD, selected skill methods and falsifier.
- `verification.json`: test ID, command/environment, input identity, started/finished timestamps, exit code, retries/timeouts/skips, pass-or-inconclusive and log SHA; no secret content.
- `ui-interactions.json`: if GUI affected, action ID -> backend method -> observed expected/negative, viewport screenshot refs.
- `diff-review.md`: files changed and why, rollback plan, license source and no foreign hunks.
- `delivery.md`: local commit, pushed ref, PR, merged remote commit, installed build SHA, consumer status **independently**.
- Learning capture *after* verified result, using existing approved registry and task owner (not duplicate status ledger).

Store under the existing CODEMIND repository docs/test artifact convention; do not create a new live NMBV source-of-truth file. Include a machine-readable current gate status in CODEMIND UI only if server has real persisted evidence.

## 7. First bounded work queue

**Next eligible action:** S0 source/runtime census, then S1-A contract-driven dashboard v2 read model. The following are not authority to execute by merely appearing in this plan:

1. Reconcile feature branch HEAD vs local checkout and current Serena process source.
2. Establish baseline for overview, skills, tunnel, Commander and existing tests.
3. Add failing v2 contract test around `observed_at/source_revision/stale` and `null vs 0`.
4. Implement only those fields from available data or return `UNVERIFIED`.
5. Connect Overview/Skills/Connections components to real responses with typed error states.
6. Execute Windows browser/keyboard/mobile click audit, no visual placeholders.
7. Verify no new log-secret disclosures or Commander process interference.
8. Record fresh tested revision and review owned diff before milestone promotion.
9. Then begin CODEMIND expert/skill catalog import as S2.
10. Branch to deterministic diagnosis if a step fails twice with equivalent fingerprint; don't blindly repeat it.

**Release decision:** any required C01–C30 gate marked `FAIL`, `BLOCKED`, `UNVERIFIED` or `TIMEOUT` means full V2 remains INCOMPLETE; evidence of one implemented slice may still be reported accurately.
