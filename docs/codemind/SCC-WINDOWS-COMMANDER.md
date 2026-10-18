# SCC Windows Commander — independent service

SCC (Secucko) has its **own** Windows Commander, not a copy of the NMBV
Commander installation. Its implementation, credentials, process, MCP endpoint
and health proof belong to D:\DEV\codemind-serena.

## Start it

Open a new PowerShell window:

    cd D:\DEV\codemind-serena
    .\scripts\start-scc-commander.ps1

Keep the window open. The commander binds **127.0.0.1:8767** and serves:

- POST http://127.0.0.1:8767/mcp — MCP JSON-RPC initialize, tools/list and tools/call.
- GET http://127.0.0.1:8767/codemind/health — nonce-bound authenticated readiness.

Credentials live in the user's ACL-restricted file:
%LOCALAPPDATA%\CODEMIND-Serena\scc-commander\peer-token.txt.
Never paste this token into an issue, web page or chat. The SCC Commander
launcher creates the token if missing; it does not use NMBV credentials.
-CheckOnly runs a non-mutating launcher preflight.

In a **second** PowerShell window, start Serena:

    cd D:\DEV\codemind-serena
    .\scripts\start-codemind-serena.ps1

If the SCC token file exists when Serena starts, its launcher automatically
supplies CODEMIND_COMMANDER_HEALTH_URL and CODEMIND_COMMANDER_HEALTH_TOKEN
to the Serena process. Existing custom environment values are preserved.
A Serena process started before this configuration will continue to report
its old loaded state until explicitly restarted at an authorized maintenance window.

## What actually works

The MCP catalog contains seven bounded, read-only tools:

| Tool | Purpose |
| --- | --- |
| scc_system_info | OS, machine, uptime, memory |
| scc_list_processes | Bounded Windows process observation |
| scc_list_services | Bounded Windows service observation |
| scc_list_listeners | Bounded TCP listening sockets |
| scc_process_details | Read details for a numeric PID |
| scc_read_project_file | Read a small file within the configured SCC root |
| scc_runtime_status | Verify SCC instance identity and capability inventory |

MCP clients must use the dedicated bearer token. The service listens on
loopback only. It has no generic PowerShell execution, writes, task scheduling,
process termination, privileged recovery or automatic service management.
The native Serena health probe requires a fresh 40-hex-character challenge,
a matching nonce, service identity SCC.WindowsCommander, and HMAC-SHA256
over the nonce, colon, SCC.WindowsCommander:v1. It rejects the unrelated
service identity WindowsCommander.McpServer.

**Not yet claimed:** one-to-one parity with NMBV Windows Commander MC's
larger toolset, an externally accessible SCC Commander tunnel, a live
ChatGPT-origin tools/call, dual-watchdog recovery, or unrestricted Windows
execution. Each is a separate implementation and acceptance gate. The local
MCP port is **not** a public URL.

## Ownership boundaries

Never stop, overwrite, reconfigure, re-key, rehost or take over NMBV's
WindowsCommander.McpServer.exe or tunnel-client. SCC has separate files,
credentials and service identity. NMBV Bot is not called or depended upon.

## Verification and rollback

    node --test test\serena\test_scc_commander.cjs
    .\scripts\start-scc-commander.ps1 -CheckOnly
    Get-NetTCPConnection -LocalPort 8767 -State Listen

Existing source files modified by this slice are preserved under
D:\DEV\codemind-serena\.codemind\scc-dedicated-commander-20261018.
Stop **only the SCC-owned Node process** before reverting those files.
The token and NMBV installation are not part of source rollback.
