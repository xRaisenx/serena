# CODEMIND Serena V2 — Design package

**Prepared:** 2026-10-18. **Artifact type:** Version-controlled implementation specification, not a runtime release.  
**System:** CODEMIND Serena, based on `oraios/serena` under existing upstream GPL-3.0-or-later terms.  
**Branch:** `codemind/mvp-serena-loop-guard` in `xRaisenx/serena` (existing draft PR #1).  
**Evidence rule:** NMBV methods are source references and optional adapters. Existing NMBV project repo, data and task authority are not copied or modified by these documents.

## Reading order

1. [00-MVP-CHARTER.md](00-MVP-CHARTER.md) — product promise, current source truth, P0/P1 scope, invariants, full exit contract.
2. [01-ARCHITECTURE-SPEC.md](01-ARCHITECTURE-SPEC.md) — semantic execution/authority planes, naming/prefix policy, typed model, router/learning/FU, API v2, Commander and security.
3. [02-MISSION-CONTROL-UX.md](02-MISSION-CONTROL-UX.md) — professional GUI geometry and navigation, each view's actual data, errors, accessibility and clickable-controls test.
4. [03-IMPLEMENTATION-SLICES.md](03-IMPLEMENTATION-SLICES.md) — S0–S9, first complete Overview/Skills/Connections vertical slice, dependencies, per-slice DoD.
5. [04-DELIVERY-AND-ACCEPTANCE.md](04-DELIVERY-AND-ACCEPTANCE.md) — milestone gates, C01–C30 validation, incident/runbook, resource budgets and release-level proof.
6. [05-NMBV-TO-CODEMIND-CROSSWALK.md](05-NMBV-TO-CODEMIND-CROSSWALK.md) — exact NMBV 25-skill source names/paths, proposed CODEMIND method translations, native coordinator mappings, CODEMIND-100 metadata, FU and independent Commander.
7. [06-UI-API-BINDINGS.json](06-UI-API-BINDINGS.json) — machine-readable v1/v2 route and frontend action mapping with explicit feature availability.
8. [07-S1A-EVIDENCE.md](07-S1A-EVIDENCE.md) — current source tests and independent Windows sidecar HTTP verification, with the active primary-runtime parity explicitly unverified.

## Immediate work directive

The feature branch now implements the **S1-A backend** with `/codemind/api/v2/overview`, `/v2/capabilities` and a bounded read-only `/v2/skills/route` endpoint, plus an advisory skill form in the existing console. **Windows CI and a separately launched local Windows Serena instance validated the targeted API implementation; primary running-build parity and full S1 browser interaction evidence remain outstanding.** Revalidate S0 and the entire S1 UI/backend contract before proceeding to S2. Every enabled control must be tested through its backend, including negative states. Continue to S2 only after S1 acceptance.

**Do not** global-find-and-replace `nmbv`→`codemind`; introduce new `codemind_*` APIs while preserving NMBV-specific connector names at the compatibility boundary. Do not import client records or bypass NMBV's task/page/source authorization. No first-run automatic Commander restart.

## Verified vs proposed

- The v1 Serena/code intelligence and CODEMIND status/tunnel dashboard sources were inspected in the feature branch. The NMBV capability inventory and routing/anti-loop/forecast source were inspected through NMBV Bot. CODEMIND-100 persona task wiring was read from its installed skill.
- The named documents here have been **authored/committed**, but **a narrow v2 read-model and skill-routing API is now implemented in source**, but **no 25-module import, complete redesigned GUI, trusted expert activation, or full V2 production acceptance** is claimed.
- The 30 test cases are acceptance targets; no `PASS` is implied by their presence.
- The existing NMBV v3 client's installed hooks, FU live remote runtime, governance and persistent lessons remain independent systems with their own test/evidence gates.
- The next agent should establish branch HEAD, task ownership, exact source generation and current client first; never resume using only historical "passed" messages.


## Current source-versus-runtime checkpoint (2026-10-18)

| Surface | Source branch | Live Windows parity / proof |
|---|---|---|
| V1 Serena API and dashboard | Preserved | Previously observed, running revision not attested |
| `GET /codemind/api/v2/overview` | Implemented; real observed/unknown values | Local sidecar live PASS; primary runtime pending |
| `GET /codemind/api/v2/capabilities` | Implemented; explicit NOT_IMPLEMENTED flags | Local sidecar live PASS; primary runtime pending |
| `POST /codemind/api/v2/skills/route` | Implemented via validated active-project SkillRouter; no execution | Local sidecar live PASS (200/403); primary runtime pending |
| V2 skill-route GUI | Source wired to authenticated API; errors and timeout visible | Pending Windows browser acceptance |
| CODEMIND-100 + full 25-skills | Reference crosswalk only | No installed runtime proof |
| FU 5+20, governed lesson promotion, dual-watchdog | Design contracts only | Not complete |
| ChatGPT tunnel | Local tunnel was previously ready and polling | ChatGPT-origin tool call not proven |
| Full V2 acceptance C01-C30 | Requirements documented | Not complete; do not infer green from documentation |

S1-A focused tests are `test/serena/test_codemind_v2.py`; the Windows CI workflow explicitly executes them. The GitHub checks are evidence about source on a CI runner, not evidence that your existing Serena process was restarted with the same code.

## Conflict resolution

Real latest code + independently observed tests outrank these proposed interfaces. A source mismatch requires revising the plan before implementation, not editing unrelated runtime to fit a slide/mockup. Source-only, test fixture, Git merge, deployed runtime, and actual ChatGPT consumer proofs must stay distinct.
