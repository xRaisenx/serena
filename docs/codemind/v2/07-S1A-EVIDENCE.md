# CODEMIND V2 — S1-A Source and Live Windows Evidence

**Captured:** 2026-10-18 (local host Windows + GitHub CI)  
**Classification:** BOUNDED S1-A evidence only. Not an MVP release certificate.  
**Source head tested:** `89d2e463ba4337622fa06b7cc10da6dfeb9e0718`  
**Repository PR:** https://github.com/xRaisenx/serena/pull/1

## Implemented code

- `src/serena/codemind/read_model.py`: typed `schema:2`, observation timestamp, source revision **not attested**, null unknown metrics and distinct Commander/tunnel capability states.
- `src/serena/codemind/dashboard_api.py`: existing V1 contract preserved; authenticated V2 overview and capabilities; project-scoped advisory skill-route POST with validation and same-origin check.
- `src/serena/resources/dashboard/codemind/{index.html,console.js,console.css}`: visible skill-routing form, real backend request, typed error/denied states, revision indicator and responsive input.
- `test/serena/test_codemind_v2.py`: V1 compatibility, V2 schema/null/status, missing project, actual project skill manifest selection, unauthenticated/cross-origin/invalid payload refusal.

## GitHub runner evidence

`CODEMIND Windows Slice` on the current feature branch:

| Test/validation | Observation |
|---|---|
| Isolated guard, DPAPI and module tests | 39 passed |
| Serena MCP/dashboard/v2 integration tests | 101 passed |
| MCP subprocess handshake | 1 passed |
| PowerShell 5.1 and 7 launcher | Preflight passed |
| Node console.js check + hooks | Passed |
| Pinned Ruff lint/format locally before Git push | Passed after repairing three Python files |
| Docs build, Codespell, Python versions, CodeQL | GitHub checks passed on source SHA above |
| Full upstream Serena 13-job matrix | Still running at evidence capture; **not counted PASS** |

The direct local Windows Python pytest command timed out while testing staged source. **That timeout is not a PASS.** CI ran the same V2 file in the pinned runner environment. Do not treat the CI runner as proof of the local interpreter issue being fixed.

## Independent live Windows S1-A validation instance

**Method:** Stage GitHub-sourced files under `D:\DEV\codemind-serena` only after matching known base blob SHAs; save original files under `.codemind\backups\v2-s1a-20261018`. Keep existing Serena 8765 and Windows Commander running. Start a separate one-time Serena on 127.0.0.1:8766 with dashboard on 127.0.0.1:24284.

| Actual HTTP/runtime check | Observed |
|---|---|
| V1 `/codemind/api/overview` | Schema 1 |
| V2 `/codemind/api/v2/overview` | Schema 2, observed timestamp |
| V2 `/codemind/api/v2/capabilities` | `fu_20_candidate_horizon: NOT_IMPLEMENTED`; CODEMIND expert runtime `NOT_IMPLEMENTED` |
| Runtime active Serena tool count | 35 |
| Runtime enabled CODEMIND skill count | 1 |
| `POST /codemind/api/v2/skills/route` | HTTP 200; selected `deterministic-debugging` |
| Route execution authority | `authorization_granted:false`, `executed:[]` |
| Unauthorized V2 GET | HTTP 401 |
| Cross-origin route POST | HTTP 403 |
| New HTML/skill-route form served | HTTP 200; form present |
| Existing main Serena port 8765 | Preserved and listening |
| Independent Windows Commander | Preserved |
| Temporary test sidecar | **Stopped** after testing; port 8766 freed |

The **running main application on 8765 was not restarted**, because its existing encrypted-key tunnel was active and ready. Main runtime parity with V2 source therefore remains **NOT VERIFIED**. The sidecar is proof that the staged V2 Python+Flask process works in isolation, not that the end-user UI was visually or interactively tested in a real browser.

## Acceptance verdict

`S1-A SOURCE_AND_SIDECAR_PASS; PRIMARY_RUNTIME_PARITY_UNVERIFIED; COMPLETE_V2_MVP_INCOMPLETE`

**Next bounded action:** conduct owned, reversible main service switchover that preserves the active tunnel, then browser-click/viewport/accessibility acceptance for the three S1 screens. Continue the remaining S2–S9 gates only after scoped evidence. Do not modify NMBV data or restart Windows Commander as a side effect.
