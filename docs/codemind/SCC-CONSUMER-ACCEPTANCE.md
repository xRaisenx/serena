# SCC ChatGPT MCP consumer acceptance

SCC separates three observed states:

1. **MCP listener** — Serena answers on `127.0.0.1:8765`.
2. **Tunnel transport** — the SCC-managed official tunnel-client runs and its loopback `/readyz` returns HTTP 200.
3. **Recent MCP consumer call** — a caller completes a one-time, operator-issued 40-hex-character challenge by invoking the `codemind_consumer_proof` Serena tool.

## Run the verification

Open SCC at `http://127.0.0.1:24283/codemind/`, unlock with its local operator token, and open **Connections & tunnel**.

After the tunnel is client-ready, click **Verify an MCP consumer call**. The dashboard returns a challenge valid for 90 seconds. In ChatGPT, ask the connected **Serena Code Commander** to call `codemind_consumer_proof` with that exact challenge. Then click **Refresh** in SCC.

The receipt is stored only in the running Serena process and expires after 600 seconds. It is one-time use and invalidates on managed tunnel stop/start. It does not include or disclose tunnel credentials.

**Trust boundary:** This verifies that an authenticated operator-issued challenge reached an SCC MCP tool and got a successful response. The code does **not cryptographically authenticate a ChatGPT cloud caller's identity**. Remote origin is corroborated separately by the actual external ChatGPT tool invocation and its response, not inferred merely from a tunnel ID or local process.

The security dashboard distinguishes `CLIENT READY` from `MCP CALL SEEN` and from a release-level cryptographic origin attestation. A receipt expiring is expected, not a tunnel disconnection.

The distinct **Autonomous dual-watchdog recovery** acceptance gate remains blocked until separate recovery supervisors and independent fault-injection tests are actually delivered. No unrelated Windows Commander, NMBV process, or API key is controlled by this acceptance path.
