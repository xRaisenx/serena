# CODEMIND Serena V2 — Design package

**Prepared:** 2026-10-18. **Artifact type:** Version-controlled implementation specification, not a runtime release.  
**System:** CODEMIND Serena, based on \`oraios/serena\` under existing upstream GPL-3.0-or-later terms.  
**Branch:** \`codemind/mvp-serena-loop-guard\` in \`xRaisenx/serena\` (existing draft PR #1).  
**Evidence rule:** NMBV methods are source references and optional adapters. Existing NMBV project repo, data and task authority are not copied or modified by these documents.

## Reading order

1. [00-MVP-CHARTER.md](00-MVP-CHARTER.md) — product promise, current source truth, P0/P1 scope, invariants, full exit contract.
2. [01-ARCHITECTURE-SPEC.md](01-ARCHITECTURE-SPEC.md) — semantic execution/authority planes, naming/prefix policy, typed model, router/learning/FU, API v2, Commander and security.
3. [02-MISSION-CONTROL-UX.md](02-MISSION-CONTROL-UX.md) — professional GUI geometry and navigation, each view's actual data, errors, accessibility and clickable-controls test.
4. [03-IMPLEMENTATION-SLICES.md](03-IMPLEMENTATION-SLICES.md) — S0–S9, first complete Overview/Skills/Connections vertical slice, dependencies, per-slice DoD.
5. [04-DELIVERY-AND-ACCEPTANCE.md](04-DELIVERY-AND-ACCEPTANCE.md) — milestone gates, C01–C30 validation, incident/runbook, resource budgets and release-level proof.
6. [05-NMBV-TO-CODEMIND-CROSSWALK.md](05-NMBV-TO-CODEMIND-CROSSWALK.md) — exact NMBV 25-skill source names/paths, proposed CODEMIND method translations, native coordinator mappings, CODEMIND-100 metadata, FU and independent Commander.
7. [06-UI-API-BINDINGS.json](06-UI-API-BINDINGS.json) — machine-readable v1/v2 route and frontend action mapping with explicit feature availability.

## Immediate work directive

Start at **S0**, validate current checkout + running version and v1 API tests, then implement **S1-A**: versioned read-only v2 overview contract with actual source/freshness/unknown fields, followed by professional Overview/Skills/Connections UI. Every enabled control must be tested through its backend, including negative states. Continue to S2 only after S1 acceptance.

**Do not** global-find-and-replace \`nmbv\`→\`codemind\`; introduce new \`codemind_*\` APIs while preserving NMBV-specific connector names at the compatibility boundary. Do not import client records or bypass NMBV's task/page/source authorization. No first-run automatic Commander restart.

## Verified vs proposed

- The v1 Serena/code intelligence and CODEMIND status/tunnel dashboard sources were inspected in the feature branch. The NMBV capability inventory and routing/anti-loop/forecast source were inspected through NMBV Bot. CODEMIND-100 persona task wiring was read from its installed skill.
- The named documents here have been **authored/committed**, but **no new v2 engine API, 25-module import or redesigned GUI** is claimed implemented from this documentation work.
- The 30 test cases are acceptance targets; no \`PASS\` is implied by their presence.
- The existing NMBV v3 client's installed hooks, FU live remote runtime, governance and persistent lessons remain independent systems with their own test/evidence gates.
- The next agent should establish branch HEAD, task ownership, exact source generation and current client first; never resume using only historical "passed" messages.

## Conflict resolution

Real latest code + independently observed tests outrank these proposed interfaces. A source mismatch requires revising the plan before implementation, not editing unrelated runtime to fit a slide/mockup. Source-only, test fixture, Git merge, deployed runtime, and actual ChatGPT consumer proofs must stay distinct.
