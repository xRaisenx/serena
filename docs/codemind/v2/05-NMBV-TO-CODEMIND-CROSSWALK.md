# NMBV V3 → CODEMIND Serena V2 — Full Source and Capability Crosswalk

**Purpose:** source-backed transplantation of GENERIC engineering methods into project-independent CODEMIND names. **Status: design, not actual 25-skill installation.**  
**Upstream CODEMIND:** `xRaisenx/serena`; **reference NMBV:** `xRaisenx/nmbv-management-system-v3`, merged PR #636 implementation `ff46f05ec7647222a9cc44a9cea5df850acde48f`, merge `e2a21d992407f1b2a776fc99f161c94f4b4b3b19`, as reported in NMBV source contract. Verify source hashes at import time.

## 1. Twenty-five distinct source-indexed NMBV skills

The **source inventory** below must not be confused with installed CODEMIND project modules, loaded task skills, expert profiles or executing agents. The `codemind-*` target is proposed when the method is portable; NMBV-specific adapters retain source-specific context.

| # | Source skill and path | Proposed CODEMIND capability | Activation owner / handling |
|---:|---|---|---|
| 1 | `ai-psychiatry` — `.agents/skills/ai-psychiatry/SKILL.md` | `codemind-executive-discipline` | Evidence/control guard when necessary; retain attribution and upstream method |
| 2 | `all-the-medicine` — `.agents/skills/ai-psychiatry/upstream/all-the-medicine.SKILL.md` | `codemind-single-control` | One applicable diagnostic control, not all controls concurrently |
| 3 | `architecture-compass` — `.agents/skills/stark-ai-developer/upstream/architecture-compass.SKILL.md` | `codemind-architecture-review` | ADR and architecture drift |
| 4 | `autonomous-engineering` — `.agents/skills/autonomous-engineering/SKILL.md` | `codemind-autonomous-workflow` | Long work, checkpointed tasks, no authority grant |
| 5 | `bug-triage` — `.agents/skills/bug-triage/SKILL.md` | `codemind-bug-triage` | First unresolved observed defect |
| 6 | `codex-spec-interviewer` — `.agents/skills/stark-ai-developer/upstream/codex-spec-interviewer.SKILL.md` | `codemind-spec-interviewer` | Ambiguous interface/requirements, not every task |
| 7 | `deterministic-debugging` — `.agents/skills/deterministic-debugging/SKILL.md` | `codemind-deterministic-debugging` | Repeated equivalent fault/source contradiction |
| 8 | `future-unraveler` — `NMBV-Worker/skills/future-unraveler/SKILL.md` | `codemind-future-unraveler` | Advisory forecast, never executor |
| 9 | `guarded-git-delivery` — `NMBV-Worker/skills/guarded-git-delivery/SKILL.md` | `codemind-guarded-git-delivery` | Protected source delivery under actual Git owner |
| 10 | `job-completion` — `.agents/skills/job-completion/SKILL.md` | `codemind-job-completion` | Honest exit/blocked criteria |
| 11 | `neurosymbolic-implementation` — `NMBV-Worker/skills/neurosymbolic-implementation/SKILL.md` | `codemind-neurosymbolic-implementation` | Native Serena symbol-first owner + constrained LLM |
| 12 | `neurosymbolic-validation` — `.agents/skills/neurosymbolic-validation/SKILL.md` | `codemind-neurosymbolic-validation` | Invariants/falsifiers/source proof |
| 13 | `nmbv-engineering-agency` — `.agents/skills/nmbv-engineering-agency/SKILL.md` | `codemind-engineering-coordination` | Only portable disjoint-ownership worker principles; no NMBV task grants |
| 14 | `nmbv-fullstack-specialist` — `.agents/skills/nmbv-fullstack-specialist/SKILL.md` | `codemind-fullstack-specialist` | Generic web/DB/desktop boundaries; NMBV-only QuickBooks contract stays adapter |
| 15 | `nmbv-worker` — `.agents/skills/nmbv-worker/SKILL.md` | `codemind-worker-method` | Work packet discipline, not a new worker runtime |
| 16 | `no-regression-closure` — `NMBV-Worker/skills/no-regression-closure/SKILL.md` | `codemind-no-regression-closure` | Independent closure proof, affected chain |
| 17 | `real-world-durability` — `NMBV-Worker/skills/real-world-durability/SKILL.md` | `codemind-durability-validation` | Actor/outage/benchmark cases |
| 18 | `release-validation` — `.agents/skills/release-validation/SKILL.md` | `codemind-release-validation` | Source/runtime/consumer separation |
| 19 | `repository-audit` — `.agents/skills/repository-audit/SKILL.md` | `codemind-repository-audit` | Bounded read-only discovery |
| 20 | `stark-ai-developer` — `.agents/skills/stark-ai-developer/SKILL.md` | `codemind-stark-methods` | Select referenced architecture/spec children, no duplicated invocation |
| 21 | `superpowers` — `.agents/skills/superpowers/SKILL.md` | `codemind-superpowers-methods` | Method wrapper, no duplicate child execution |
| 22 | `systematic-debugging` — `.agents/skills/superpowers/upstream/systematic-debugging.SKILL.md` | `codemind-systematic-debugging` | Debug submethod inside primary deterministic owner |
| 23 | `targeted-fix` — `.agents/skills/targeted-fix/SKILL.md` | `codemind-targeted-fix` | Small authorized owner-scoped change |
| 24 | `test-driven-development` — `.agents/skills/superpowers/upstream/test-driven-development.SKILL.md` | `codemind-test-driven-development` | Red -> minimal edit -> green |
| 25 | `verification-before-completion` — `.agents/skills/superpowers/upstream/verification-before-completion.SKILL.md` | `codemind-verification-before-completion` | Fresh proof before DONE |

Inventory count check: 14 top-level NMBV `.agents/skills` + 5 `NMBV-Worker/skills` + 3 nested Superpowers + 2 nested Stark + 1 nested AI Psychiatry = 25.

Each packaged target manifest requires: `id`, `name`, `source_repo`, `source_path`, `source_sha256`, `upstream_license`, `applicability`, `constraints`, `dependencies`, `instructions_path`, `version`, `enabled`, `permissions_required`. Prevent path traversal/symlink escapes; include license and attribution before copying text or source. NMBV business-sensitive policies are references to opt-in adapters, not free-standing CODEMIND default guidance.

## 2. NMBV native tools mapped to CODEMIND generic methods

NMBV's live 94 callable tool definitions include 68 named coordinator capabilities and separate Serena semantic tools. Exposed != authorization. **NMBV remains the owning implementation** of its original method names; CODEMIND's proposed methods are new interfaces with independent project capability checks, not aliases that claim an NMBV session.

| NMBV capabilities | Proposed CODEMIND namespace | Porting contract |
|---|---|---|
| `nmbv_capabilities`, `nmbv_runtime_status`, `nmbv_session_status` | `codemind_capabilities`, `codemind_runtime_status`, `codemind_session_status` | Actual project/source/task identity; UNBOUND explicit |
| `nmbv_skill_route` | `codemind_skill_route` | One primary method, evidence-triggered supporting references |
| `nmbv_next_action`, `nmbv_action_history` | `codemind_next_action`, `codemind_action_history` | Real canonical action; <=5 previews; <=20 FU advisory |
| `execute_triage_and_repair`, native error review | `codemind_triage`, `codemind_deterministic_debugging` | Bounded, owner-authorized repair; no blind retry |
| `nmbv_proof_plan`, proof records | `codemind_proof_plan`, `codemind_proof_record` | Only actual source/runtime results, no placeholders |
| `nmbv_checkpoint_*` | `codemind_checkpoint_*` | Task/project scoped persistence/recovery |
| `nmbv_process_*`, `nmbv_search_*` | `codemind_operation_*` | Existing tool executor owner; status handles, no shell bypass |
| `nmbv_work_packet_status`, `nmbv_worker_pool_status`, `nmbv_parallel_eval` | `codemind_work_status`, `codemind_worker_pool_status` | Actual worker pool only; no 100 fake worker processes |
| `nmbv_governance_start/status`, session routing | `codemind_governance_status` and task-owner binding | Never upgrade actor rights from route result |
| `nmbv_candidate_*`, `nmbv_macro_*` | `codemind_candidate_*`, `codemind_validated_operation_*` | Shadow/test/proof review, source JIT, rollback, protected commit |
| `nmbv_lesson_capture/assess/candidate/outcome/rollback` | `codemind_lesson_*` | Applied proof stage gating; no captured==applied |
| `nmbv_learning_registry/status/finalize` | `codemind_learning_*` | Only proven applied/rolled-back lesson in policy |
| `nmbv_check_remote_main` and delivery tools | `codemind_delivery_status` | Independent remote SHA / installed bytes / runtime parity |
| `nmbv_validate_routes/booking/collection` | **No generic copy** | NMBV-only business validation; optional project adapter |
| native `write_memory/read_memory/list_memories` | retain Serena native memory names | Source memory, task lessons and learning separate |

**Native source map (read-only reference):**
- `.serena/fleet/noetic-skill-routing.mjs` → CODEMIND routing policy + provenance.
- `.serena/fleet/noetic-action-review.mjs` → normalized strategies/repeated failure guard.
- `.serena/fleet/noetic-predictive-horizon.mjs` → 5 canonical preview + 20 FU conditional slots.
- `.serena/fleet/noetic-post-mutation-diagnostics.mjs` → Serena native diagnostics packet (not automatic repair).
- `.serena/fleet/resolve-phase4/learning-tools.mjs` and `learning-authority.mjs` → staged lesson promotion.
- `tools/nmbv-codex-hooks` → source event models; **NMBV portable package has two hooks**, not the CODEMIND project's 11-event source config.
- `NMBV-Worker/references/CAPABILITY_MATRIX.md` → skills source identities. No wholesale client-private data copy.

## 3. CODEMIND-100 expert reference integration

CODEMIND-100 skill currently supplies persona-level `references/task-wiring.json`, `references/neurosymbolic-cortex.json`, 10 council JSON reference sets and up to 100 historical engineering profiles, not 100 processes.

`codemind_select_expertise(request, context)` (PROPOSED) returns:
```json
{
  "scope": "SOURCE_BACKED_EXPERT_REFERENCE",
  "intent": "debug",
  "primary_council": "C07",
  "supporting_councils": ["C06", "C09"],
  "selected_profiles": [],
  "interface_wiring": ["UI to API auth and error propagation"],
  "symbolic_obligations": ["reproducer", "authorization", "negative test"],
  "execution_authorized": false,
  "source": "versioned local CODEMIND-100 reference archive",
  "profile_execution": "NOT_APPLICABLE"
}
```
Load one council and up to 3 matching reference profiles unless evidence supports a multi-layer expansion. If profile JSON is not packaged/licensed in the runtime, report **NOT_INSTALLED** and use deterministic task-intent fallback. No "expert online" dot without a real external worker.

## 4. FU and worker exposure truth

FU ChatGPT plugin: six skills (`fu-core`, `fu-futures`, `fu-architecture`, `fu-security`, `fu-validation`, `fu-watch`) are available as methodology. No independently callable FU execution namespace observed. CODEMIND's **native** forecast implementation, when added, uses source-backed requirements and can incorporate FU methodology without a second scheduler.

CRUX, WOLF, JAX, PTSSD, PINTADOR, MAPYA, WINTANA, UNBUGGER and AEGIS are available through skills/methods; they are not independently running workers absent authenticated task/result APIs. Don't duplicate services for persona labels.

Windows Commander exposes 73 callable Windows and CodeIntel methods through its existing connector. Its process lifecycle and recovery service are **not CODEMIND-owned**. CODEMIND uses only approved authenticated cooperation. Historic observation: Commander `get_runtime_status` returned a connector envelope validation error (missing required `content`), and CODEMIND peer status was `not_configured`; treat these as integration defects, not capabilities to reimplement.

## 5. Copy/port checklist and explicit exclusions

1. Identify source filename and pinned Git SHA; verify component license and client/private content rights.
2. Copy the **algorithm/method** into CODEMIND-owned semantics where licensed; avoid importing production NMBV DB, client addresses, API keys, page role matrix or task-bound work records.
3. Prefix new runtime/tool/API/skill names `codemind_*` / `codemind-*`; maintain upstream Serena and original `nmbv_*` for external connector compatibility.
4. Reimplement generic source/task/owner/authorization with explicit project identity rather than implicit `D:\DEV\nmbv-v3-clean`.
5. Unit-test original observable invariants, positive/negative inputs and source fingerprint/candidate proof at new CODEMIND generation.
6. Validate actual MCP `tools/list` exposes only capabilities installed; update GUI `capabilities` endpoint and status badges together with code.
7. Preserve original tests and code provenance notices in CODEMIND docs. No NMBV repo mutation is needed to build CODEMIND generic feature.
8. After owner-approved implementation, prove clean start, independent Commander health, hooks, ChatGPT consumer and running revision; only then label the imported capability `VERIFIED`.

**Import result as of this spec:** mapped **25/25 reference skill names and key native methods**, **0/25 V2 modules claimed installed**, and **no V2 runtime capability claimed complete**. Source design is not an installation script.
