# CODEMIND Serena V2 — MVP Vertical Slice and Implementation Slices

**Contract:** These are delivery slices, not completed functionality. A slice is closed only when its backend, visible GUI actions, negative paths, tests, source revision and installed runtime agree. Each slice has one primary source owner; no simultaneous uncontrolled writers.

## Slice 0 — Freeze the verified baseline and source identity (P0 foundation)

**Goal:** Determine exactly what code/runtime is running and ensure no feature regression during redesign.

Inputs:
- CODEMIND PR #1 source, Serena upstream license/provenance, current \`dashboard_api.py\` and v1 HTML/CSS/JS, active Serena MCP and separate Windows Commander.
- Current NMBV Bot capabilities read-only; its project worktree and permissions remain out of scope.

Owned surfaces: documentation, source manifest/acceptance fixtures, CODEMIND test utilities; **not** NMBV repo.

Work:
1. Capture repo HEAD/tree SHA/dirty paths, existing Flask routes and tool classes; baseline screenshot and navigation.
2. Test existing v1 dashboard lock, overview, tunnel controls, LSP symbol lookup, MCP initialize/list/call.
3. Inventory CODEMIND module and profile manifests; classify as implemented/installed/verified. Record tool/skill count from source/runtime, never hardcode 35/1 as everlasting.
4. Run focused tests first; note red failures and unchanged foreign files.
5. Keep upstream Serena source/docs notice and GPL obligations.

Exit evidence: named baseline SHA, actual running-revision identity, v1 regression commands/results, screenshot, preserved independent Commander. No green-from-stale-logs.

## Slice 1 — FIRST COMPLETE V2 VERTICAL SLICE: professional GUI + true API state (P0)

**Goal:** Produce a user-visible, production-quality **Overview / Skills / Connections** flow, with no unimplemented active buttons.

Touchpoints:
- Backend \`src/serena/codemind/dashboard_api.py\` → proposed \`src/serena/codemind/api_v2.py\` (read-model only).
- Current frontend \`src/serena/resources/dashboard/codemind/{index.html,console.css,console.js}\`; modularize only if tested.
- Existing \`SkillManifestRegistry\`, \`SkillRouter\`, \`TunnelController\`.

**User journey test:**
1. Operator visits \`/codemind/\` → sees polished locked screen; wrong token rejects; right token loads real version, project and tools.
2. Overview shows authenticated Serena, exactly observed skill count, separate Commander PID vs HMAC peer status, tunnel status and last evidence time.
3. Skills view lists actual validated project skills; no fake 25 NMBV skills. Route a read-only request with provenance, \`selected != loaded != executed\`.
4. Connections shows DPAPI key configured indicator only; doctor identifies typed root cause (occupied port vs invalid permission), starts only its managed client, reports local-ready vs ChatGPT-verified separately.
5. Refresh, Escape, keyboard, light/dark, export, stale, timeout, error and mobile viewport all work.
6. CODEMIND back-end route remains same-origin, bounded and authorization-enforced.

**Exit proof:** authenticated live Windows browser plus MCP API contract; 320/390/768/1440 viewport images; click inventory 100% of enabled controls, zero unhandled errors; negative 401/403/409/timeout; no credentials in logs/exports; Commander untouched. **If any visible interaction is inert, slice fails.**

## Slice 2 — Project-wide CODEMIND capability / expert mapping (P0)

**Goal:** Adapt source-backed NMBV method catalog into project-independent CODEMIND **reference modules** without accidentally importing client-specific execution authority.

Owned surfaces: CODEMIND manifest schema, \`modules.py\`, \`planner.py\` or new module, project-local \`.codemind/skills\` package, CODEMIND-100 reference adapter.

Work:
- Source-map 25 NMBV skills (see crosswalk); import generic permitted methods into \`codemind-*\` manifests, preserve origin/license/version/description.
- Expert reference selector reads CODEMIND-100 \`task-wiring.json\` and \`neurosymbolic-cortex.json\`, with 10 council groups and up to 100 profile metadata entries when actually packaged and validated.
- Route \`request_text + source/diagnostic context\` to one primary method + bounded supporting methods; no persona process start.
- Compare deterministic lexical fallback vs source evidence; validate malformed path, content injection, duplicate skill ID, unrelated project, unavailable domain.
- UI shows catalog available, project installed, selected, loaded, executed as **different counts**.

Exit: source inventory/hash, machine-readable manifests + tests, real \`codemind_skill_route\` tool result, confirmed loaded skill-body provenance and correct keyboard/UI route explanation; no NMBV coordinator write.

## Slice 3 — Task/source scoped deterministic diagnosis and anti-loop (P0)

**Goal:** Reuse the proven reasoning from \`noetic-action-review.mjs\` rather than building another uncontrolled repair executor.

Owned surfaces: \`learning.py\` migration and proposed \`action_review.py\`; dispatch preflight; Failure Lab read API; tests.

Work:
- Define strategy identity excluding volatile timeouts/PIDs, including project, task, generation, tool and canonical target.
- Normalize error fingerprints while preserving causal differences. Capture expected-negative-test intent.
- Policy: first confirmed equivalent failure → triage; second → require different hypothesis; third unchanged → deny before tool dispatch.
- Allow distinct tested alternative; correctly handle stale generation, concurrent workers, SQLite locks/corruption, reset-on-observed success.
- No raw prompts/credentials in SQLite. Read-only UI shows source/fingerprint/attempt count and evidence, not sensitive inputs.

Exit: unit/property/concurrency/negative tests; actual MCP third-call refusal; strategy change permitted; database integrity + controlled restart persistence; UI actual live counts.

## Slice 4 — Canonical next action and FU with no authority leakage (P0)

**Goal:** CODEMIND-native forecast semantics, not a renamed NMBV coordinator RPC with hidden business permissions.

Owned surfaces: \`NextActionPlanner\` evolution, \`next_action.py\`, \`fu_forecast.py\`, tasks/forecast API and view.

Work:
- Canonical current action conditioned on task/source/owner/failed tests/governance.
- 0–5 core stages, 0–20 distinct FU branches, always \`executable:false\` for future items.
- Handle COMPLETE (no further candidates), no task binding (blocked), source mismatch (reconcile identity), recurring failure (different diagnostic hypothesis), competing owner (no mutation).
- Use CODEMIND-100 expert methodology for falsifiers; reference optional FU plugin instruction evidence separately from native forecast.
- UI graph displays prerequisite/evidence/falsifier/contingency and last recomputation timestamp.

Exit: deterministic forecast snapshots for case families; false authorization impossible in tests; no execution originating from forecast click, provenance verified.

## Slice 5 — Learning registry and evidence-based promotion (P0 scoped read/write)

**Goal:** Make CODEMIND learn from verified outcomes rather than store unlabeled errors.

Owned: governed lesson registry, application-local storage and API, source-owner approval workflow; NMBV native data unmodified.

Work:
- States CAPTURED/ASSESSED/DISMISSED/CANDIDATE/SHADOW_TESTED/APPLIED/ROLLED_BACK.
- Dedupe against existing applied safeguards; immutable links to source revision, red/green outcome, scope and rollback.
- No automatic promotions, task authorization upgrades or project secret capture.
- Restart/reconnect readback, tampered evidence refusal, retention and backup of local-only state; test corrupt/partial and multi-writer cases.
- UI keeps proposal versus applied distinction, viewer read-only unless a separate authorized write workflow is proven.

Exit: one successful authorized learning lifecycle in isolated fixture and installed runtime, correct applied registry after restart; negative promotion tests.

## Slice 6 — Independent Commander and bounded recovery (P0)

**Goal:** Credible two-service resilience without coupling lifecycles.

Owned: CODEMIND peer client; Commander protocol/SCM changes require **separate** Commander owner/release.

Work:
- Implement/authenticate nonce+HMAC health protocol, replay controls, peer-side MCP initialize probe and source identity.
- Service A monitors B for observation; B may monitor A without automatic reciprocal restart.
- Recovery permissions owner-bound, cooldown and circuit breaker max three, no background busy loop.
- Fault injection: kill only isolated CODEMIND test service; ensure Commander survives; and vice versa under independent, explicitly approved test instance. Verify recovery after Windows logon/reboot with controlled SLO.
- UI shows \`UNKNOWN\`, \`PROCESS_PRESENT\`, \`AUTHENTICATED\`, \`READY\`, \`DEGRADED\`, \`CIRCUIT_OPEN\` from measured state.

Exit: authenticated readiness + negative spoof/replay + crash recovery telemetry; Commander build/release SHA separately verified; no mutual restart storm.

## Slice 7 — Codex hooks + semantic post-edit proof (P0)

**Goal:** Trustable host events rather than installing unverified hooks.

Owned: existing CODEMIND \`.codex/hooks.json\`, handler and tests; native Serena diagnostics wrapper.

Work:
- Verify Codex installed version, exact event schema, \`/hooks\` trust source, event trace and no startup warning.
- SessionStart bounded; UserPromptSubmit actual source-backed routing; PreToolUse warning/unchanged strategy denial; PostToolUse parse nested MCP errors/timeouts with bounded recursion.
- After code edits invoke real Serena diagnostics and targeted syntax/build/test at actual generation through the owning host executor; a JS syntax check is not a JSX/TS verifier.
- Stop claim guard avoids recursion and does not claim false full-suite pass. Hooks cannot bypass Serena's authorization.
- No all-skills prompt flood; actual CODEMIND-100 selected expert source read only when needed.

Exit: direct unit + real Codex startup/resume/compact/tool/edit trace; no warnings, normal trust proven, independent post-edit red/green.

## Slice 8 — Provider settings, tunnel and ChatGPT consumer proof (P0 integration)

**Goal:** API configuration fully functional and secure across restart, without conflating tunnel readiness with consumer tool acceptance.

Owned: existing \`tunnel_control.py\`, backend settings surface, UI settings, official tunnel profile; no changes to user secret store except approved migrator.

Work:
- Current-user DPAPI store for tunnel key; operator/peer secrets isolated. No plaintext \`.env\` migration by default.
- Existing local tunnel endpoints exercised with correct real key permissions and typed diagnostics, dynamic health port (avoid conflict at 8080).
- Restart, secret rotation, wrong-org/wrong-scope/401/403/409/timeout.
- Actual ChatGPT connector \`tools/list\` and \`tools/call\` from external client, compare revision and response; no synthetic status.
- UI never echoes key and does not persist raw key after save.

Exit: independent consumer tool call evidence and zero credentials in network-visible telemetry/logs.

## Slice 9 — Delivery, durability, release parity (P0 exit)

**Goal:** Claim completion only when product actually runs against approved Windows environment and remains reliable.

Work:
- Tests: all targeted, compatibility, public API, negative auth, unknown states, actor/source owner, restart/repair, visual and keyboard, link/button audit.
- 1k/10k synthetic stress; P50/P95/P99, CPU/RAM (respect <= 25% of host resources when doing background work if owner policy applies), load/drop/restart; *real clocked 24-hour soak is a separate gate*.
- Generate immutable evidence manifest with SHA; protected commit/push/PR/merge only within owned scope; compare remote main to installed files/runtime.
- Independent no-regression review and user-facing runbook. UI can display accepted vs blocked gates without hiding unresolved ones.

Exit: all P0 acceptance gates current and green for actual target; no timeout/skip counted pass; signed-off residuals classified. Otherwise typed INCOMPLETE/BLOCKED with one concrete next action.

## Dependency and sequence

\`\`\`text
S0 Baseline
    |
    +-> S1 GUI/API working vertical slice -> S2 skill/expert routing -> S3 anti-loop
                                            |                      |
                                            +-> S4 next/FU <---------+
                                            |
                                            +-> S5 governed learning
    +-> S6 Commander authenticated peer
    +-> S7 Codex trusted hooks/post-edit diagnostics
    +-> S8 API/settings/tunnel live consumer
    \----> S9 full exit (requires S1–S8 evidence)
\`\`\`

Parallelize read-only inspection, fixture design and **disjoint owned files** only. One author per resource, guarded source generation, no extra NMBV worktree, no cross-executor bypass.

## First developer task (immediately executable when authorized)

**S1-A: Lock API v1 and build a verified read-model adapter.** Owner inspects \`dashboard_api.py\` and \`console.js\`, adds a versioned read-only response with \`observed_at\`, \`source_revision\`, explicit availability states and test fixture; updates UI to consume only the real fields. No new worker/learning writer, no unrelated Commander or NMBV changes.

Red tests: missing version, null count, stale data, wrong auth, failure to initialize, wrong Commander peer, stale tunnel. Green after targeted code and Windows browser check. This is the lowest-risk complete vertical slice from the current codebase.

**Closure definition:** completing this task is NOT completing the whole product; only S1-A may be labeled green with its own evidence.
