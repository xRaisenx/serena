# CODEMIND Serena V2 — Architecture and Integration Specification

**Classification:** PROPOSED interface and behavioral contract, not runtime deployment proof.  
**Reviewed existing owners:** \`src/serena/codemind/{dashboard_api.py,learning.py,modules.py,planner.py,health.py,tunnel_control.py}\`, \`src/serena/tools/codemind_tools.py\`, \`src/serena/resources/dashboard/codemind\`; NMBV reference \`.serena/fleet/{noetic-skill-routing,noetic-action-review,noetic-predictive-horizon}.mjs\`.

## 1. Five strictly separated planes

\`\`\`text
  ChatGPT/Codex/user/IDE
      | explicit task + authenticated client identity
      v
  CODEMIND Serena API (host process)
   [MCP tools + LSP/symbols + project context]
      |    |             |               |
      |    v             v               v
      | project route    guard+learning  evidence+FU
      | (codemind_*)     (task scoped)   (no execution)
      v
  Authorized owner/editor --> diag --> focused tests --> reviewer
      |                                |
      +-- permitted tool boundary ----+
       (not a forecast-derived permission)

  Separate Windows Commander process (own host/SCM + watchdog)
      <---- challenge/response, read-only health ---->
  Optional Commander execution via existing authenticated tool contract
      (never route around a Serena/NMBV denial)

  Same-host Mission Control UI (local dashboard port)
      <---- authenticated, schema-versioned HTTPS-or-loopback JSON ---->
      no direct credentials in localStorage/URL/logs
      +-- optional outbound official tunnel-client process
            <- existing OpenAI control plane; remote tool proof distinct
\`\`\`

**Authority:** CODEMIND only owns its own policy/registry/status. The original repository/project's Serena authorization, NMBV session/page/task gates where applicable, and external Commander service ACLs remain authoritative. A browser operator session is not an editor grant.

## 2. Component boundary / proposed source modules

| Source owner | Existing baseline | V2 evolution | Guard |
|---|---|---|---|
| Serena MCP | \`src/serena/mcp.py\`, Serena tool registry | Register opt-in \`Codemind*Tool\` classes without renaming upstream tools | Preserve \`tools/list\` contract, project permissions |
| Skills | \`codemind/modules.py\`, \`planner.py\` | \`codemind/routing.py\`: declared source-backed modules, suitability, capability availability, selected vs loaded | Untrusted manifest path, length, schema, version, provenance |
| Code intelligence | Serena LSP/symbol tools | \`codemind/diagnostics.py\` consumer of existing diagnostics; no parallel LSP | Do not mistake diagnostics packet for tests |
| Failure guard | \`codemind/learning.py\` (SQLite, call signature) | \`codemind/action_review.py\` normalizes semantic strategy and failure signature; project/task/generation scope | No secret arguments in evidence, negative-test classifications |
| Governed lessons | Not implemented as full native NMBV promotion | \`codemind/lesson_registry.py\` staged capture/assess/candidate/applied/rollback; preserve NMBV naming only in its adapter | Promotion needs proof SHA, authorized owner and rollback |
| Forecast | \`planner.py\` local recommendation | \`codemind/next_action.py\` with canonical owner step; \`codemind/fu_forecast.py\` nonexecuting 5+20 candidates | No \`authorized_by_forecast=true\` |
| Expert profiles | CODEMIND-100 persona reference data, not active worker | \`codemind/expertise.py\` read-only metadata for ten councils/100 reference profiles; link selected profile to concrete evidence | Don't represent methods as workers |
| Windows Commander | \`health.py\` probe contract; other service separately hosted | \`codemind/peer.py\` authenticated health client and recovery telemetry; Commander changes via separate owned release | No PID-only or port-only readiness |
| Hooks | project \`.codex/hooks.json\`, JS advice | \`codemind/hooks.py\` *visibility adapter only* to host trusted hook trace; no auto-install global hooks | Trust hash/event coverage runtime-proven |
| Dashboard | \`dashboard_api.py\` plus v1 HTML/JS/CSS | New read-model \`codemind/api_v2.py\` + source-aligned frontend modules | No frontend state invention |
| Tunnel | \`tunnel_control.py\` current-user DPAPI secret + managed official client | Versioned controls, typed diagnostics, observed local poll age | ChatGPT \`tools/call\` requires separate remote proof |
| NMBV compatibility | Existing \`mcp__NMBV_Bot__nmbv_*\` methods | Optional \`codemind/adapters/nmbv.py\` read-only bridged provenance and capability inventory | NMBV method names unchanged; no shadow authority |
| Worker | No generic CODEMIND coordinator | \`codemind/work.py\` adapter to existing vetted executor; single task owner | No second scheduler or privileged shell by default |

Modules are **proposals** until source-tested and committed. Existing working modules stay the only authority until replacement is proven.

## 3. Prefix policy — copy capability, NOT an unsafe global rename

CODEMIND-owned public names use \`codemind_*\`: \`codemind_capabilities\`, \`codemind_skill_route\`, \`codemind_next_action\`, \`codemind_action_review\`, \`codemind_learning_status\`, \`codemind_lesson_capture\`, \`codemind_lesson_assess\`, \`codemind_lesson_candidate\`, \`codemind_lesson_outcome\`, \`codemind_learning_registry\`, \`codemind_health\`, \`codemind_execution_status\`.

These must NOT be automatically renamed:
- Upstream Serena \`find_symbol\`, \`find_referencing_symbols\`, \`get_diagnostics_for_file\`, \`replace_symbol_body\` and other MCP/Serena contracts.
- Existing NMBV Bot \`nmbv_capabilities\`, \`nmbv_skill_route\`, \`nmbv_next_action\`, learning and task-bound tools. An adapter may display a normalized CODEMIND view but must preserve the backing call and its project authority.
- Windows Commander API names or independently deployed service identity.
- Historical log IDs, source hashes, git branches, database schema rows and code references carrying \`nmbv_\`.

**Porting process:** license/ownership check -> source-backed behavior map -> data/permission normalization -> bounded new tests -> implementation -> compare current evidence -> deprecate only with consumer proof. No copying client-specific NMBV customers/roles/DB workflows.

## 4. Contracts and state machines

### 4.1 Task and action context

\`\`\`json
{
  "schema": 2,
  "task": {"id": "task-scoped-id", "kind": "debug", "project": "active-project",
    "session_binding": "BOUND|UNBOUND|UNKNOWN", "owner": "assigned|unassigned",
    "source": {"git_sha": null, "tree_sha": null, "dirty": null, "captured_at": null}},
  "routing": {"selected": [], "loaded": [], "executed": [], "permission_granted": false},
  "next": {"canonical": {"name": "INSPECT", "authorized": false, "evidence_gate": "source identity"},
    "preview": [], "fu_candidates": [], "max_preview": 5, "max_fu": 20},
  "evidence": {"state": "UNVERIFIED", "observed_at": null, "source": "runtime"},
  "version": {"api": 2, "engine_revision": null}
}
\`\`\`

IDs shown here are example *shape*, not a live task. \`UNBOUND\` never inherits authority from a cached task ID. Source identity checks happen at mutation time, not solely at task creation.

### 4.2 Strategy fingerprint + guard

Identity input: \`projectId + taskId + generation + owning tool + canonical target + normalized meaningful arguments\`. Drop volatile timestamps/PIDs/timeouts/cursors; hash large payloads; redact secrets before hashing/storage. Failure input: normalized error class/message after stripping incidental line numbers, durations, UUIDs and private tokens. Different errors under the same action do not necessarily represent identical root cause. Explicitly exclude expected negative-test failures from automatic recurrence counts until test-intent classification is validated.

State machine:
\`\`\`text
UNKNOWN -> OBSERVED_FAILURE(1) -> CONFIRMED_EQUIVALENT_FAILURE(2)
      -> STRATEGY_CHANGE_REQUIRED / SAME_CALL_DENIED
      -> NEW_HYPOTHESIS/OWNER/TARGET VALIDATED -> ALLOWED_ALTERNATE_ATTEMPT
      -> NEW_OBSERVED_RESULT -> (VERIFIED_SUCCESS | FAILED | UNKNOWN)
\`\`\`
- Stored success requires independent tool/test oracle and current generation. A raw HTTP 200/exit 0 without intended assertions is not completion proof.
- Stale strategy key cannot accidentally block new source revision unless correlation explicitly warrants it.
- Failure histories remain bounded, audited and privacy-reviewed. No automatic reset of project history on UI refresh.
- If storage is corrupt/unavailable, do **not** claim guard healthy; enforce safe host tool-side boundaries for protected edits and degrade to \`GUARD_UNAVAILABLE\`.

### 4.3 Skill routing

Input: \`{request_text, project_id, evidence, explicit_requested_skill?, mutation_authorized?}\`; output includes:
\`{available, eligible, selected, loaded, executed, primary_owner, supporting_methods, rejected_with_reason, provenance, permission_granted:false}\`.
- First pass may reuse the current metadata token match, but show \`algorithm=lexical_fallback\` (never pretend semantic certainty).
- Enhanced CODEMIND routing can use task intent/changed files/symbols/failure history to rank candidate skills with explicit evidence and transparent deterministic tie-breaking.
- Load only selected \`SKILL.md\` bodies after manifest path and allowed-root validation; their prose never authorizes tools.
- NMBV reference's 25 skills are a **catalog-to-CODEMIND import**, separately activated by a compatibility adapter/approved packaged methodology; zero automatic NMBV project mutation.

### 4.4 Governed learning

\`CAPTURED -> ASSESSED | DISMISSED -> CANDIDATE -> SHADOW_TESTED -> REVIEWED -> APPLIED -> REGISTRY_ELIGIBLE\`; applied lessons may become \`ROLLED_BACK\`. Every transition records task/owner/source snapshot, evidence hashes, counterexamples and independent review. A candidate cannot be committed, executed or promoted from a forecast, UI toggle or markdown memory alone. The ledger is not a replacement for Serena project memories. Native NMBV learning remains in NMBV coordinator.

### 4.5 Canonical action and FU

- One canonical \`codemind_next_action\` at source snapshot; owner authorization evaluated separately.
- Preview returns \`0..5\` ordered conditional stage descriptions, first matching canonical step, else none on complete.
- FU overlay returns \`0..20\` distinct *advisory* candidates. Every future item requires \`{branch, prereq, evidence_gate, safety_flags, disconfirming_test, fallback, verdict:"PENDING_EVIDENCE", executable:false, authorized_by_forecast:false}\`.
- A changed source SHA/task/observed failure invalidates and recomputes the forecast. No automatic task loop initiated by rendering forecast.

## 5. Mission Control API v2 (proposed additions)

Preserve existing:
\`GET /codemind/api/overview\` and \`GET /codemind/api/tunnel/status\`, plus scoped tunnel key/doctor/start/stop mutation endpoints. Do not change v1 responses in place.

Propose \`/codemind/api/v2\`:

| Method + path | Output / action | Authorization | Behavior when not implemented |
|---|---|---|---|
| GET \`/capabilities\` | Advertised, connected, permitted, tested states per capability | Authenticated operator | Explicit unavailable |
| GET \`/overview\` | Versioned aggregate telemetry with per-source freshness | Operator | No synthetic values |
| GET \`/projects\` | Serena known and active projects, redacted paths | Operator | Empty not error when none |
| GET \`/tools\` | Actual active tool registry + source + permission flags | Operator | Report backend unavailable |
| POST \`/skills/route\` | Advisory selection for a bounded task | Operator + CSRF/origin + limits | No dispatch |
| GET \`/skills\` | Modules installed/eligible/selected by project | Operator | Never imply installed from catalog |
| GET \`/experts\` | Available CODEMIND-100 metadata and sourced obligations | Operator | No agent-liveness badges |
| GET \`/tasks\` | Actually observed tasks with owner/status | Operator | No phantom tasks |
| GET \`/actions/next\` | Canonical current action if identity-bound | Operator | Return \`NOT_BOUND\` if unbound |
| GET \`/actions/forecast\` | Preview and FU with provenance | Operator | \`PENDING_EVIDENCE\` |
| GET \`/failures\` | Sanitized task/source failure cohorts | Operator | Clear unavailable state |
| GET \`/learning\` | Stage-aware lessons; only applied policies reusable | Operator | No false promoted state |
| GET \`/diagnostics\` | Serena native diagnostics + test statuses (separate) | Operator | No \`PASS\` without test |
| GET \`/commander/peer\` | Nonce-authenticated peer status, age, circuit state | Operator | \`UNVERIFIED\` if not configured |
| GET \`/hooks\` | Host event support/trust/last observed fires | Operator | Not installed/unverified |
| GET \`/connections\` | Tunnel metadata, poll age, ChatGPT call proof | Operator | No secrets |
| GET \`/audit\` | Bounded redacted activity, source provenance | Operator | No raw prompts, credentials |
| GET \`/acceptance\` | Evidence/test gate and installed SHA matrix | Operator | \`UNVERIFIED\` rather than success |

All endpoints: local loopback or separately approved secure transport, operator token, \`Cache-Control:no-store\`, strong input/output validation, bounded body/rate limits, safe error details, no raw secret fields. POST needs CSRF/origin mitigation. For future remote access, a browser-only bearer token and trust in \`remote_addr\` are insufficient; bind authentication and trusted proxy topology explicitly.

### 5.1 Representative response

\`\`\`json
{
  "schema": 2,
  "revision": "unknown",
  "observed_at": "2026-10-18T00:00:00Z",
  "systems": [
    {"id": "serena", "state": "OBSERVED", "capability": "semantic", "evidence": "authenticated_mcp_initialize"},
    {"id": "commander", "state": "UNVERIFIED", "capability": "peer", "evidence": "process_presence_only"},
    {"id": "tunnel", "state": "UNVERIFIED", "capability": "consumer", "evidence": "local_client_ready_only"}
  ],
  "features": [{"id": "codemind_next_action", "implementation": "PROPOSED", "execution_authorized": false}]
}
\`\`\`
This is an example schema. Never render its timestamps as real telemetry.

## 6. Commander peer + recovery ownership

- Commander remains a standalone Windows service/process with its own SCM/watchdog. CODEMIND may issue a challenge+nonce/HMAC health read against its **published authenticated endpoint**; that endpoint implementation must be verified in the Commander owner's source.
- Authenticate both service identities, require replay window, rate limit, bounded timeouts; report \`observed_at\`, \`nonce_valid\`, \`auth_valid\`, \`mcp_initialize_valid\`, \`pid_seen\` independently.
- Commander should be able to observe CODEMIND through a separately owned authenticated health surface. Recovery permissions remain unilateral and bounded per service, never two mutually recursive restarts. Max 3 attempts with cooldown and terminal circuit-open state; recovery test uses approved fault injection.
- If one fails, the other enters \`DEGRADED\` and preserves queued work; do not issue production mutations through a bypass executor.

## 7. Storage, secrets, migration

- Current existing \`FailureGuard\` SQLite remains under per-user local storage. For V2, migrate transactionally to source/task/generation-aware schema with version marker, tests on copied DB, integrity check, explicit rollback file and retention.
- Serena memory and CODEMIND learning are different stores; no cross-project silent data merge.
- Operator token, Commander peer secret and OpenAI control-plane key each have distinct purpose, scope and lifecycle; control-plane key remains current-user DPAPI encrypted at rest.
- No \`.env\` plaintext-credential migration automatically; any existing env values are explicit compatibility inputs, detected and validated without displaying values. Provide controlled GUI-backed configuration by capability and backend ownership only after safe migration proof.
- Installation/update must not overwrite dirty NMBV checkout or modify independent Commander runtime configuration.

## 8. Proof requirements

- Unit: normalizer equivalence/negative cases; router ordering, malformed skill manifests; candidate pruning/authorization false.
- Contract: actual MCP \`initialize/tools/list/tools/call\`, Serena LSP symbol read, command rejection and versioned dashboard JSON.
- Security: wrong token, no same-origin, cross-project path, symlinks, unbound task, stale source, secret redaction, replayed nonce.
- Mutation: one authorized symbolic edit with original red/green and matching source identity; no forced dirty checkout overwrite.
- Learning: capture→assess→candidate cannot masquerade as applied; approved applied registry readback across restart, rollback.
- Reliability: network loss, Commander absent, stale tunnel health, SQLite lock/corruption, timeout, two simultaneous writers, restart/reconnect.
- Consumer: browser mobile/keyboard/accessibility, tool and setting controls; actual ChatGPT remote method round-trip.
- Acceptance is *per gate*, not by general statement. Do not mark V2 done from source-only tests.
