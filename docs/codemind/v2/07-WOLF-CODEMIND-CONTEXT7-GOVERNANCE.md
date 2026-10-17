# CODEMIND V2 — WOLF governance, CODEMIND-100 and Context7 code evidence

**Review:** 2026-10-18 | **State:** maintained engineering reference, not release acceptance  
**Repo:** `xRaisenx/serena`, draft feature PR #1. **Independent system:** Windows Commander MC and NMBV Bot retain their existing service/task authority.

## Review owners and boundaries

- **WOLF governance (skills-only):** accountable delivery, final independent acceptance, evidence classification, source ownership, reversibility and targeted red-team falsifiers. WOLF does not launch a second agent, bypass permissions, or certify an unattended job.
- **CODEMIND-100 (skills-only):** automatically classify coding intent and select one primary engineering council plus at most three useful expert reference profiles when available. The ten councils/100 profiles are **method references, not automatically created agents** or running workers.
- **Context7 (live documentation lookup):** use authoritative library docs to confirm actual Python/Flask/MCP interfaces rather than assuming training-era APIs. Document verified **installed dependency version** separately from the version of the retrieved docs.
- **Serena:** upstream symbol/refactoring and tool authorization boundary. **CODEMIND:** advisory skill routing, telemetry, guarded execution preflight, local anti-loop, future preview. **NMBV Bot:** separate session-bound task/lesson capabilities. **Commander:** separate Windows process/recovery boundary.

## Source and installed-version anchors

At review, CODEMIND's `pyproject.toml` pins:
- `flask==3.1.3` (consulted Pallets Flask 3.1.x docs).
- `mcp==2.2.0` (consulted MCP Python SDK **v2.3.0** docs for nearby 2.x interfaces; **NOT exact pinned v2.2.0 proof**).
- `ruff==0.12.5` and `ty==0.0.24`.

Consulted documentation, via Context7:

1. [Flask request JSON/body limits](https://github.com/pallets/flask/blob/main/src/flask/wrappers.py): `request.get_json` parses but does **not validate schema**, so CODEMIND must still bound and validate JSON object keys/types/length.
2. [Flask before_request lifecycle](https://github.com/pallets/flask/blob/main/src/flask/sansio/scaffold.py): authorization gate can reject before a view executes; scope must be correct for each Blueprint.
3. [Flask error handling 3.1](https://github.com/pallets/flask/blob/3_1_1/docs/errorhandling.rst): API JSON errors should keep correct status/headers; no raw exception/tokens.
4. [MCP Python SDK 2.x migration](https://github.com/modelcontextprotocol/python-sdk/blob/v2.3.0/docs/migration.md): v2 changes streamable HTTP client stream shape and exposes session metadata differently than v1; do not paste a v1 client example into pinned v2.2.0.
5. [MCP v2 server quickstart](https://github.com/modelcontextprotocol/python-sdk/blob/main/examples/snippets/servers/mcpserver_quickstart.py): v2 may use `MCPServer` rather than historical `FastMCP`. Existing Serena registry is *its own* implementation; do not rewrite it without local compatibility evidence.
6. [MCP Python client and tool result](https://github.com/modelcontextprotocol/python-sdk/blob/v1.12.4/README.md): `initialize`, `list_tools`, `call_tool`, `structuredContent` and `isError` are useful concepts, **but v1 syntax must not be mistaken for v2 runtime proof**.

## WOLF live falsification: reference != installation

Earlier Mission Control UI labeled all catalog entries `REFERENCE ONLY • NOT INSTALLED` even after those methods were installed as project skill manifests. The source catalog remains 25 reference identities, but the runtime skill endpoint is the authority for project installation.

**Repair rule:** derive the visible installation badge from authenticated live `GET /codemind/api/overview` `skills.state` and `skills.items[].id`, matched to the immutable 25-reference catalog. Do not infer selected/loaded/executed/authorized from installation. If live skill telemetry fails, display `INSTALLATION UNVERIFIED`, never make a false negative or positive claim.

**Observed gate at review:** 25 generic CODEMIND skills plus the preserved legacy skill were copied from source-reviewed GitHub blobs into the independent CODEMIND host. Authenticated Serena MCP `codemind_list_skills` returned **26**; `codemind_skill_route` selected a relevant method with `authorization_granted:false`, `loaded:[]`, `executed:[]`. Authenticated dashboard overview returned 26 and reference catalog 25, and anonymous catalog access returned HTTP 401. No Serena/Commander restart required. Source commit and installed manifest proof are not a whole-running-build hash attestation.

## Required independent release checks

| Gate | Acceptance | Status at document creation |
|---|---|---|
| Skill packaging | Exactly 25 CODEMIND method manifests plus one preserved original; valid schemas and file digests | LIVE READBACK OBSERVED |
| Native dynamic discovery | `codemind_list_skills` returns 26 with actual IDs and nonexecuted selection | LIVE OBSERVED |
| Mission Control truth | Each method badge derives from live skill telemetry; missing snapshots display UNKNOWN | FIX COMMITTED; live UI and browser click not yet verified |
| HTTP auth | Anonymous requests fail; operator auth and origin checks preserved for writes | FOCUSED LIVE VERIFIED |
| MCP transport | Normal client initializes and calls tool on **current installed code** | Further consumer proof needed |
| CODEMIND-100 routing | Selected reference profile read, source version, bounded context and actual proof | NOT VERIFIED; persona not worker |
| Commander dual peer | Authenticated nonce handshake and independent recovery with no restart storm | NOT VERIFIED |
| Codex hooks | Host actually trusts and fires events on normal session | NOT VERIFIED |
| Governed learning | Captured→assessed→applied with actual promotion/delivery/readback | NOT VERIFIED |
| FU horizon | Bounded nonexecuting preview; no permission from forecast | Source/runtime smoke proved; live remote ChatGPT call unverified |
| Full CI / deployment | Final SHA checks, Windows build parity, UI responsiveness, source/main delivery and consumer | NOT ACCEPTED |

**Immediate WOLF stop/go:** No merge or blanket production claim while required gates remain unverified. Preserve the already working tunnel/Serena/Commander services. Correct only source-backed contradictions, run focused red/green tests, then independent live consumer checks. A timed-out test cannot become PASS.
