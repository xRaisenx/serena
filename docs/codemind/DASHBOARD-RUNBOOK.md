# CODEMIND Serena — Dashboard operation

This authenticated operations dashboard is integrated into upstream Serena's existing Flask dashboard.

## Security
- Console URL: /codemind/ (or /dashboard/codemind/index.html) on the active local Serena dashboard port.
- Telemetry requires a strong separate environment variable CODEMIND_DASHBOARD_TOKEN (32 or more characters), injected into the Serena SERVER process.
- The browser retains the token in memory only; not in URL, localStorage or exported JSON.
- Never use or paste an OpenAI API key into the dashboard token form.
- The dashboard is read-only. Existing Serena dashboard remains available at /dashboard/.

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
Connections shows a configured tunnel ID as UNVERIFIED until remote ChatGPT tool calls are proven.
Security displays an explicit acceptance ledger with unresolved gates.
Keyboard navigation, responsive mobile layout, theme switching, auto-refresh while visible, and sanitized read-only JSON export are implemented.

## Commander attestation
A separate local Commander implementation must provide a nonce/HMAC attested read-only endpoint. Its address and shared secret come from CODEMIND_COMMANDER_HEALTH_URL and CODEMIND_COMMANDER_HEALTH_TOKEN. Do not configure an endpoint without having tested its implementation. A PID is not an MCP handshake.

## OpenAI Secure MCP Tunnel
User-provided tunnel name is serena-code-commander. The tunnel ID is injected from CODEMIND_TUNNEL_ID; it is not hard-coded in source.
A masked sk-proj string is NOT a working runtime API key. Only a correctly scoped CONTROL_PLANE_API_KEY in the tunnel-client process can enable polling.
Official setup: https://developers.openai.com/api/docs/guides/secure-mcp-tunnels
Use latest supported tunnel-client, inspect tunnel-client help quickstart, configure init, validate doctor --explain, run the client, then verify ChatGPT Tunnel-mode plugin discovery and a real tool call. Do not expose MCP to a public interface.

## Acceptance boundaries
Passing isolated Flask and MCP contract tests is not proof that the user's Windows machine, Commander dual-watchdog, full NMBV worker orchestration, or the ChatGPT tunnel have completed an actual end-to-end session. They remain separately evidence-gated.
