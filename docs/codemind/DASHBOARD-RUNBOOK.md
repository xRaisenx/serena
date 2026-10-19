# CODEMIND Serena — Dashboard operation

This authenticated operations dashboard is integrated into upstream Serena's existing Flask dashboard.

## Security
- Console URL: /codemind/ (or /dashboard/codemind/index.html) on the active local Serena dashboard port.
- Telemetry requires a strong separate environment variable CODEMIND_DASHBOARD_TOKEN (32 or more characters), injected into the Serena SERVER process.
- The browser retains the token in memory only; not in URL, localStorage or exported JSON.
- Never use or paste an OpenAI API key into the dashboard token form.
- Core CODEMIND observability remains read-only. Scoped tunnel settings POST/DELETE routes require an operator token and same-origin checks; they cannot mutate repositories or Commander.
- Enter the tunnel API key only in the Connections panel after unlock; never in the dashboard unlock form. It is encrypted with current-user Windows DPAPI under LOCALAPPDATA/CODEMIND-Serena/control-plane-key.dpapi and never returned over HTTP.
- Existing Serena dashboard remains available at /dashboard/.

## Start with a verified fork checkout
With uv available, from the repo root:
  uv sync --locked
  uv run --no-sync serena start-mcp-server --transport streamable-http --host 127.0.0.1 --port 8765 --agent-interface tools --enable-web-dashboard true --open-web-dashboard false --project D:/DEV/codemind-serena

Use the dashboard URL actually announced in the Serena logs; port 8765 is the MCP port, not necessarily the dashboard port. Configure a strong CODEMIND_DASHBOARD_TOKEN in the SAME Serena process environment BEFORE starting. The dashboard shows an unlock form and does not reveal the server-side token.

## Implemented views
Overview shows observed tool counts, workspace, language backend, tool state, failure counters, Commander and tunnel topology.
Semantic Tools lists and searches actually exposed Serena operations.
Skills shows enabled validated project-local .codemind/skills JSON manifests.
Learning displays SQLite fingerprint counts, blocked strategies, and anti-loop policy.
Execution shows bounded observed Serena tasks (not speculative NMBV workers).
Windows Commander separates process presence and authenticated MCP attestation. It cannot restart processes from the dashboard.
Connections now includes saving/removing an encrypted runtime key, diagnostics, managed tunnel start/stop, and key/process/readiness state. It remains UNVERIFIED until remote ChatGPT tool calls are proven.
Security displays an explicit acceptance ledger with unresolved gates.
Keyboard navigation, responsive mobile layout, theme switching, auto-refresh while visible, and sanitized read-only JSON export are implemented.

## Commander attestation
A separate local Commander implementation must provide a nonce/HMAC attested read-only endpoint. Its address and shared secret come from CODEMIND_COMMANDER_HEALTH_URL and CODEMIND_COMMANDER_HEALTH_TOKEN. Do not configure an endpoint without having tested its implementation. A PID is not an MCP handshake.

## OpenAI Secure MCP Tunnel
User-provided tunnel name is serena-code-commander. The tunnel ID is injected from CODEMIND_TUNNEL_ID; it is not hard-coded in source.
A masked sk-proj string is NOT a working runtime API key. Enter a complete key with Tunnels Read + Use into the secure Connections panel. Only the tunnel-client subprocess receives the decrypted runtime key as its environment variable.
Official setup: https://developers.openai.com/api/docs/guides/secure-mcp-tunnels
Use latest supported tunnel-client, inspect tunnel-client help quickstart, configure init, validate doctor --explain, run the client, then verify ChatGPT Tunnel-mode plugin discovery and a real tool call. Do not expose MCP to a public interface.

## Acceptance boundaries
Passing isolated Flask and MCP contract tests is not proof that the user's Windows machine, Commander dual-watchdog, full NMBV worker orchestration, or the ChatGPT tunnel have completed an actual end-to-end session. They remain separately evidence-gated.

## Verified control-panel deployment on Windows
- Authenticated GET /codemind/api/tunnel/status returned HTTP 200: key_configured=false and client_ready=false.
- Unauthorized API-key save returned HTTP 401; cross-origin start returned HTTP 403; missing-key doctor returned HTTP 409.
- The new static console returned HTTP 200, MCP remained listening, and Windows Commander remained independently running.
- Windows CI passed 39 isolated tests (including native Windows DPAPI), 86 Serena integration tests, and 1 MCP subprocess smoke.
- A real unmasked runtime key and an authenticated ChatGPT tunnel round-trip are still required to prove remote connection.
