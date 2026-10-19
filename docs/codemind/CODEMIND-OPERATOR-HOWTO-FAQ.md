# CODEMIND SCC — Operator How-To, About, FAQs & Use-Case Playbooks

**Contract:** SCC Final Unified Architecture v2.0 · **Output:** implemented static guide at `src/serena/resources/dashboard/codemind/guide.html` · **Validation:** sandbox-only until installed-host acceptance. This file describes truthful operating states and explicit deployment gates, not measured uptime or live readiness.

## About CODEMIND SCC

CODEMIND SCC is the governed orchestration/control surface. Serena supplies semantic file/symbol/reference/diagnostic capabilities. `codemind-` project skills are versioned declarative method instructions. Windows Commander remains a separate host operations peer. An enabled skill does not grant tool access; a selected method does not mean an invoked agent.

**What exists today:** semantic tools and deterministic advisory routing, a source-configured Codex hook bridge, read-only inspection, conditional action packets and failure guard. **Not demonstrated:** host trust of the hooks, all encountered file types correctly routed, an actual three-subagent Codex host scheduler, cross-workspace immutability, Python/full MCP parity, or autonomous end-to-end delivery.

**Source/reference counts are not agent capacity.** Twenty-five catalog reference methods are not 25 executing agents; 26 JSON manifests do not prove 26 trusted host plugins. No NMBV-prefixed runtime may be relabeled or copied to fabricate a CODEMIND scheduler.

## Operator How-To — safe shortest path

1. **Pin the task/workspace.** Record the actual source root, task/session ID, source generation and requested acceptance criteria. If the active Serena project changes, stop mutations pending a fresh provider-side ownership check.
2. **Route relevant `codemind-` methods.** Use the existing deterministic matcher; check the exact enabled manifest and trust status. Avoid loading all 25 references or pasting every skill instruction into the model context. `selected ≠ loaded ≠ executed`.
3. **Inspect symbolically.** Use `find_symbol`, references, and scoped diagnostics on supported languages. Do not scan the entire tree if a relevant symbol is known. Missing LSP support triggers explicit safe fallback or denial, not a fabricated semantic match.
4. **Resolve authority.** Before a write, the owning provider verifies task scope, canonical root, revision, expected effect, and approval; Codex lifecycle hooks supplement but do not supersede this enforcement.
5. **Implement in one micro-slice.** Prepare the smallest isolated code or GUI change with an initially failing regression test; preserve existing tool API and unrelated edits.
6. **Freeze and validate.** Hand off focused validation jobs to an actual host-owned queue with **maximum three active Codex subagents**. Wait for terminal host state and process-tree cleanup before releasing a slot and admitting another job. If no such scheduler exists, run checks sequentially and report the gate unverified.
7. **Review & deliver evidence.** Compare the actual diff, red/green runs, negative authorization checks and running-version identity. For unclear or failed checks report `NOT VERIFIED`/`BLOCKED`, never PASS.

### Five-gate deployment checklist

| Gate | Requirement | Required evidence | Current classification |
|---|---|---|---|
| G1 Hooks | Local and/or managed Codex hooks installed, trusted and firing | Host `/hooks` list, exact hash trust, callback receipts, negative test | NOT VERIFIED |
| G2 Serena | Workspace-scoped semantic index and language servers ready | Source identity, real symbol and reference reads, diagnostics | NOT VERIFIED FOR CODEX |
| G3 Filetypes | Every encountered file classified with explicit semantic handler or fallback/denial | Generated extension inventory, handler coverage table, unknown/binary negative tests | NOT VERIFIED |
| G4 Subagents | Real host scheduler admits ≤3 active agents; bounded queue, expiry, reclamation | Stress/crash/timeout/termination/queue-fairness receipts with peak concurrency | NOT IMPLEMENTED IN SCC HOST |
| G5 Safety | Authorization, journal/replay, diff, regression and installed/running parity | Task-bound permission receipts, fresh tests, provider-side effect journal, runtime SHA | NOT VERIFIED |

**Readiness:** all five proven on the actual target host → `READY`. Any missing/unknown gate → `NOT READY` for autonomous Codex deployment. This page cannot mark a gate green or grant permission. Refrain from the unsupported idea that a `SubagentStart` callback alone enforces admission.

### File type routing rule

SCC catalogs every encountered extension or file class, including extensionless and binary files. Language servers support only their declared grammars. Each route must be one of `LSP_SEMANTIC`, `SAFE_TEXT_OR_STRUCTURED_READ`, `BINARY_METADATA_ONLY`, or `DENIED`. `.py`/`.ts`/`.js` are illustrative examples, not a global guarantee. A new extension or disabled language server is a coverage obligation, not permission to execute a guessed parser.

## Real use-case scenarios

| Problem | Minimal route | Proof or blocker |
|---|---|---|
| **Bug fix:** reproducible API failure | Method fit → owning symbol → falsifying test → authorized smallest patch | Fresh green regression + scoped diff |
| **Feature implementation:** new settings toggle | Existing component/API check → one UI slice → error-path test | Semantically correct interaction, accessible focus, real response |
| **New file type** in repository | Inventory extension → registered handler → fallback/deny | Representative read and unknown/binary negative cases |
| **Hook installation** seems inert | Review source config → Codex `/hooks` trust → harmless actual event | Real trusted event receipt, not just file existence |
| **Five verification jobs** | Queue all → three host-owned leases → cleanup → recycle slots | Peak-active ≤3; no orphan/leak/double launch |
| **Failed verification** | Capture failure class → reconcile effects → changed strategy | Fresh test or explicit BLOCKED status |
| **Repeated learning case** | Evidence capture → counterexample analysis → shadow validation | Candidate remains unpromoted until independent governance |

## FAQs

**Q: Does `codemind_skill_route` execute a fix?** No. It chooses applicable methods without granting execution rights. The host must separately invoke an authorized tool and collect its receipt.

**Q: Does deterministic mean zero tokens for every coding task?** No. Metadata matching can make zero model calls. Open-ended diagnosis, novel implementation and code review may need model reasoning; scripted verified transformations can be deterministic within their limited contract.

**Q: How can I verify hook installation?** Confirm the active trusted `.codex/` layer in the exact workspace, review current hook hashes using Codex `/hooks`, trigger a supported benign event, and observe its record. Source presence alone is not host activation.

**Q: Does Serena index all files automatically?** No. It indexes files through configured language servers and project rules. The CODEMIND file-type registry must route unsupported classes explicitly, often to bounded text/metadata read-only operations or denial.

**Q: How can three subagents be truly enforced?** By an authoritative host scheduler with atomic admission leases, a bounded queue, process-tree termination and resource cleanup. A `SubagentStart` hook or unrelated Node worker pool is not enough.

**Q: What happens to a queue job when an agent crashes?** A safe scheduler fences its lease, reconciles uncertain effects, confirms cleanup, records terminal state and only then recycles capacity; it must not blindly relaunch a possibly side-effecting action.

**Q: How do I prevent wrong-project edits?** Bind canonical root/source revision/task ID at the provider execution boundary, check target path and source generation on every write and refuse changes after project switching until revalidated.

**Q: Are all enabled methods executable?** No. An enabled JSON manifest is routing metadata/instructions, not a worker process or tool grant. Catalog reference methods and installed agents must be accounted separately.

**Q: What is an acceptable result if a gate is missing?** A useful diagnostic packet, proposed plan or verified read-only tool call can be delivered as such. Autonomous deployment remains `NOT READY`; no unverified PASS badges.

## Where to find this in the UI

Use **SCC dashboard → About → Operator How-To & FAQs** to open `guide.html`. The page is a static, searchable help surface designed for desktop and mobile, with accessible native details/summary controls and keyboard focus. Its status labels are deliberately not live runtime badges. `guide.js` performs local deterministic filtering only; it sends no prompt or search query to an external service.

## Alignment with the final v2 architecture

This route maps to **P1** context binding, **P2** skill resolver, **P3** plan, **P4** authorization, **P5** actual host dispatch and queues, **P6** evidence, **P7** verification, **P8** effect-aware recovery, **P9** delivery and **P10** candidate learning. The five readiness gates block unsupported P5 automation. The documentation never substitutes simulation for verified runtime integration.

## Source provenance and acceptance limits

The guide/UI change package was produced and locally tested inside CHATIRE's session sandbox. Source retrieval used the GitHub repository `xRaisenx/serena`, branch `codemind/mvp-serena-loop-guard`; other Windows-checkout changes may not be present on that branch. Integrate using the guarded patch only when the target anchor matches, re-run repository tests, inspect diff, confirm Git revision and obtain host proof before claiming deployed readiness.