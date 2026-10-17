# CODEMIND Serena Architecture and Acceptance Slices

## Foundation and provenance
- Upstream: oraios/serena, pinned commit d9e4c796fae0207ba6848d1df4b331122a5567b5.
- Fork: xRaisenx/serena. Serena application is GPL-3.0-or-later; SolidLSP remains MIT.
- CODEMIND additions must preserve licensing, original upstream tool contracts and existing Serena LSP.
- Current changes live in the isolated D:/DEV/codemind-serena source snapshot and fork feature branch. The local snapshot was unpacked from a release archive; it is not a Git worktree until Git is operational.

## Two independent runtime owners
1. CODEMIND Serena: upstream semantic MCP, optional declarative skill loading, deterministic strategy guard and reasoning/validation adapters.
2. Windows Commander: existing separately built Windows MCP executable for OS operations and Serena rescue. It owns its startup, recovery and credentials independently of Serena.

Neither is allowed to become the other's sole process supervisor. Heartbeats may be mutual, but Windows Service Control Manager or an independent nonrecursive supervisor must ultimately recover both. A failed peer check is not permission for an uncontrolled restart. Never terminate a GUI to recover a headless service.

## Current slice: anti-loop and skill discovery
- Persist opaque tool-key/error fingerprints across sessions in SQLite.
- After two consecutive equivalent failures, prevent the third equivalent invocation at the Serena MCP dispatch boundary.
- A materially different tool or arguments can proceed. A success resets the key.
- Discover JSON declarative instructions on demand in .codemind/skills without recompilation.
- Expose codemind_list_skills, codemind_failure_status, codemind_commander_status, codemind_skill_route and codemind_next_action.
- Dynamic instructions select a documented skill, never elevate authority or execute arbitrary JSON-supplied code.
- CODEMIND next_action returns conditional advice, not proof of completion or authorization.

## Subsequent acceptance slices
S2: Prove a real Serena initialize, tools/list and symbol/reference/diagnostic tool call on a disposable worktree. Inspect upstream tool compatibility, LSP startup and cancellation. Preserve prior fixes.
S3: Persist proven causal lessons with immutable evidence identity, version applicability, signed review and reversible supersession. Do not mistake matching text for a proven root cause.
S4: Verify authenticated CODEMIND--Commander health and bounded recoveries. Preserve independently functioning Commander if Serena fails, and vice versa. No circular restart storms.
S5: Bridge documented existing NMBV Bot nmbv_skill_route, nmbv_next_action, worker and verification contracts without copying private NMBV project source or bypassing session-bound permissions.
S6: Secure localhost Streamable HTTP and OpenAI tunnel connection: real remote initialization/tool call, denial tests, secrets-in-environment and session continuity. Never claim ChatGPT access merely from a listening port.

## NMBV incidents informing invariants
- Equivalent blind retries caused strategy exhaustion; fail at the executor, not in a prompt alone.
- No regression/test success claim when timed out, skipped, stale, isolated or unauthenticated.
- Avoid session/task drift: an authenticated stable session token must bind every mutation; no global task fallback.
- No cross-worktree writes, no foreign-dirty-file stomping, no duplicate worker/route/handler controllers.
- Reconcile source vs runtime generation before attributing health or promoting a test result.
- Restart only failed language-server child with bounded retry and fencing. Recheck actual language diagnostics before restarting healthy siblings.
- Worker queue fairness and per-resource ownership; maintain resources inside user CPU/RAM budget.
- Preserve original user goal and complete every mandatory acceptance row before announcing completion.

## Evidence classification
PENDING, PASS, FAIL, BLOCKED, NOT_VERIFIED and TIMEOUT_UNVERIFIED are distinct. A successful compile does not prove tool registration. Symbol reads do not prove safe writes. Successful simulation does not prove actual ChatGPT client acceptance.
