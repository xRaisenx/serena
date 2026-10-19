# CODEMIND Serena MVP: baseline and current acceptance

Upstream: oraios/serena
Pinned upstream commit: d9e4c796fae0207ba6848d1df4b331122a5567b5
Distribution license: GPL-3.0-or-later for Serena application; preserve original notices. SolidLSP is MIT.

## Verified on the Windows host

- Clean isolated CODEMIND checkout obtained from pinned upstream source archive.
- Existing Windows Commander continued to run as an independent process during source edits.
- New source files: persistent SQLite failure guard, schema-limited declarative JSON skill registry, optional CODEMIND MCP inspection tools, read-only Commander process monitor.
- Existing Serena MCP dispatch modified to enforce strategy-change guard before tool execution.
- A demonstrative JSON module added, loaded on demand without recompilation.
- No existing NMBV repository source files were modified during this task.

## Not verified

- Python runtime compile/test (Windows host timed out executing Python with code, despite python --version working).
- Serena MCP startup, tool discovery, symbol lookup and real LSP operations from this fork.
- Git remote fork and Git commit: Git and GitHub CLI fork commands timed out; downloaded pinned archive is not a Git checkout.
- Persistent lesson promotion / causal similarity across different tool signatures.
- Commander-to-CODEMIND automatic recovery, Windows service restart registration, crash/reboot test.
- ChatGPT tunnel connection and authentication.
- Performance bounds and clean packaging.

## Behavior

The dispatch guard tracks a SHA-256 of normalized invocation keys and a SHA-256 error fingerprint in SQLite.
First equivalent failure is recorded, second equivalent failure arms the block, third equivalent attempt is rejected before execution.
A different tool/argument signature can proceed. Successful execution resets its failure counter.

All local CODEMIND tools are separate from the existing NMBV Bot.
No CODEMIND code may bypass authenticated task ownership or NMBV governance.
Commander presence is not interpreted as service health, nor is a listening socket accepted as application proof.

## Next validation gates

1. Diagnose or replace failing Windows Python code-execution runtime without killing unrelated programs.
2. Run the new focused tests, Serena tool-registry tests and a real MCP initialize/list-tools/call-tool sequence.
3. Recover a functioning Git client, initialize/reconcile the fork, verify upstream provenance and push only owned files.
4. Integrate a verified durable duplex health protocol and SCM-independent recovery safeguards (avoid mutual restart storms).
5. Provision a permitted authenticated tunnel and verify ChatGPT tool call over a fresh connection.
