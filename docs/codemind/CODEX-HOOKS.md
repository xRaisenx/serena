# CODEMIND / Serena / Windows Commander — Codex hooks (October 2026)

## Scope and source of truth

Codex CLI tested version: 0.163.0. CODEMIND project hook registry: \`.codex/hooks.json\`. Handler: \`.codex/hooks/codemind-hooks.cjs\` (Node 18+, no third-party modules). This is project-scoped. It does **not** install global hooks, modify the NMBV source tree, restart Commander, or grant permissions.

Codex only executes non-managed command hooks after the user reviews and trusts the exact definition via **/hooks**. Trust is hash-based; changes require re-review. A direct script test proves hook behavior but not that a live Codex session has loaded or trusted it. Live worktrees lacking a local Git repository may require an explicit trusted project context.

## Eleven hook events and exact behavior

| Event | Purpose | Decision / side effect |
|---|---|---|
| SessionStart | Inject <= 1050 characters of stable CODEMIND coding contract, Serena semantic-first operation, independence of Commander, no false PASS. Handles startup/resume/clear/compact without loading all expert profiles. | Context only; event metadata hash stored. |
| UserPromptSubmit | Derive top 3 matches from activated \`.codemind/skills/*.json\` through the same token-overlap + tie-break algorithm used by existing CODEMIND \`SkillRouter.route\`. | Bounded advisory context; **does not** claim that an external NMBV Bot or 100-expert selector was invoked; no source permissions. |
| PreToolUse | Detect shell destruction, protected Commander/Serena process stops, and destructive MCP tools. Count recent equivalent failed calls for that session. | Advisory warning for destructive operations; after 2 equivalent evidenced failures, **deny** the third unchanged input and require strategy change. Not a universal enforcement boundary. |
| PermissionRequest | Highlight high-risk approval prompts. | Advisory; never auto-approve/deny ordinary prompts. |
| PostToolUse | Record a SHA-256 signature of tool name/arguments/workspace, output classification and current session hash. | Do not log raw arguments, prompts, credentials or response bodies. Timeout/error never PASS; repeated failures require new approach. Unrecognized responses are \`unknown\`, not success. |
| Stop | Detect categorical 100%/all-tests-pass claims that contradict unresolved errors/timeouts recorded in this session. | At most one continuation; \`stop_hook_active\` avoids infinite Stop loops. Otherwise no interference. |
| SubagentStart | Initialize a small, scoped agent contract. | Context only. |
| SubagentStop | Apply the same stop honesty check, bounded to one continuation. | No false completion claims. |
| PreCompact | Record lifecycle event without blocking compaction. | No large context injection. |
| PostCompact | Record lifecycle event; SessionStart with source \`compact\` reintroduces bounded contract where supported. | No blocking. |
| SessionEnd | Record minimal lifecycle metadata; no application mutation. | Advisory, no attempt to prolong the session. |

Evidence file: under \`%LOCALAPPDATA%\CODEMIND-Serena\hooks\evidence-v1.jsonl\` (or \`CODEMIND_HOOK_STATE_DIR\` override). It rotates after 256 KB, keeps at most 600 JSONL entries, stores only hash/enum/timestamp/session metadata, and is not a proven causal learning system.

## Compatibility and safety

- Actual Codex tool hook coverage includes Bash/unified exec, apply_patch and supported MCP/local-function paths. Some hosted/specialized tools bypass hooks, so repository governance and tool-side permissions are independently necessary.
- Only documented Codex hook output shapes are emitted. Unsupported fields like \`permissionDecision: ask\` or \`continue:false\` in PreToolUse are deliberately avoided.
- No raw secret is written to the ledger or returned to the model. Hook errors return \`{}\` to avoid corrupting the conversation.
- Lifecycle validation on Node is distinct from live Codex event delivery. Project hooks must be reviewed/trusted after installation, and reload may require a new Codex session.
- Do not install the same hook source both globally and locally: duplicated hooks can waste context and duplicate telemetry.
- The local mirror selects **manifest skills** and does not implement all CODEMIND-100 expert profiles or run a remote CODEMIND/NMBV selector service. If full expert-selector integration becomes available, it must be separately authenticated, bounded and tested.

## Validation checklist

1. Run \`node --check .codex/hooks/codemind-hooks.cjs\` and \`node --test test/serena/test_codemind_hooks.cjs\`.
2. Inspect the repo's \`.codex/hooks.json\` source. Use \`/hooks\` in a new Codex session to review/trust definitions.
3. Verify SessionStart in that new session receives bounded context; check no startup warnings.
4. Submit a debugging prompt; verify the selector yields the manifest match.
5. Run a read-only tool, then simulate two tool failures in an isolated session. Verify a third identical call is denied. Alternative arguments should remain usable.
6. Verify process-stop command triggers advisory only; no actual kill/restart.
7. End a turn with an unsupported categorical completion claim after a logged failure; verify one bounded continuation, no endless loop.
8. Confirm the Windows Commander process remains independent and Serena MCP continues serving.
