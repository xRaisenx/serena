# CODEMIND Mission Control V2 — Professional GUI / UX / Backend Contract

**Status:** PRODUCT/INTERACTION DESIGN — not an implemented visual redesign.  
**Source surfaces:** existing Serena Flask dashboard + CODEMIND \`dashboard_api.py\`, \`resources/dashboard/codemind/{index.html,console.css,console.js}\`. Retain existing working runtime until the new UI passes contract/visual/negative tests.

## 1. Design direction

An enterprise developer-operations application, **not an ornamental concept dashboard**:
- Dark neutral foundation, precise typography, restrained jade/teal active accents; light theme equal priority. Avoid neon overload, low-contrast tiny labels, fake activity animations and giant decorative hero graphics that crowd data.
- Dense but breathable desktop workspace, real tables, stable navigation, search, task evidence, accountable statuses and action provenance.
- 8px spacing grid (4px sub-units), 12–16px card radii, 1px semantic borders, subdued shadows, consistent baseline alignment; 44px minimum pointer target on touch.
- Typography: Segoe UI Variable/Inter/system; normal body 14–15px, data 13–14px, page title 25–30px, section title 16–18px, KPI 26–34px. Maintain contrast WCAG 2.2 AA and visible focus.
- Information hierarchy: project/context > service status and source revision > blocked actions and issues > available capability > graphs/trends (only from measured data) > controls.
- Identity: CODEMIND is the application brand; \`Serena\` shown in engine provenance and licensing. \`Windows Commander\` displayed as an independent peer, never subcomponent.

## 2. Responsive information architecture

Sidebar / collapsible navigation, grouped:

**Workspace**
1. Overview — live health, current project, source generation, acceptance blockers.
2. Code intelligence — active Serena tools, project languages, symbols/diagnostics, safe links to upstream Serena where the CODEMIND console has no editor.
3. Tasks & workers — actual task/worker owners, queue, retries, boundaries; no invented task operations.
4. Skill router — installed/eligible/selected/loaded/executed, CODEMIND expert-reference match, reasons and skill provenance.
5. Failure lab — strategy fingerprints, attempts, counterexamples, root-cause/evidence states.
6. Learning registry — captured/assessed/candidate/applied/rolled back, proof identity.
7. Next action & FU — canonical current action, max 5 preview stages, up to 20 conditional future candidates.

**Infrastructure**
8. Services & Commander — separate Serena/Commander process, authenticated peer readiness, supervisory circuit, refusal explanations.
9. Connections & API — tunnel runtime key saved via DPAPI, doctor/start/stop, client ready, control-plane poll, ChatGPT remote proof. Separate API credentials for other providers only when the corresponding adapter is real.
10. Hooks & integrations — actual Codex supported event/trust/last observed and connected NMBV Bot adapter status.
11. Security & evidence — operator auth, scoped permissions, acceptance gates, read-only audit history.
12. Settings — project, editor/engine runtime and supported provider configurations; secret values write-only/never readable from server.

**Nav rule:** only show a *working* navigation destination. When a V2 backend endpoint is not implemented, show an explicit coming-in-slice disabled item with tooltip and a non-clickable info card; never enable dead controls or fill with mocked data.

## 3. Desktop / tablet / mobile geometry

| View | Nav layout | Content and action behavior |
|---|---|---|
| >= 1440px | 248px fixed sidebar, 64px toolbar | 12-column content grid max width 1520px; KPIs in 4 cards; 7/5 section columns |
| 1024–1439px | 232px sidebar | 12-col grid; cards 2 or 4 based actual min width; avoid horizontal charts spilling |
| 768–1023px | collapsed icon rail ~76px or drawer | Header retains project switch and alert summary; tables scroll inside labeled container |
| <= 767px | off-canvas navigation, accessible toggle | Single-column cards, sticky action strip only where useful; forms stack; destructive controls require explicit confirm |

Keep interface labels, timestamps, and status chips legible at 200% zoom and narrow 320px. Native CSS \`prefers-reduced-motion\`; no constant high-CPU chart animation.

## 4. Actual view contracts

| View | Current backing data | V2 requirement / gap | Safe UI if missing |
|---|---|---|---|
| Overview | v1 \`GET /codemind/api/overview\` | API v2 freshness, source revision, blockers, projected vs observed; loading/error/expired | Show v1 observed values only and \`v2 not installed\` |
| Code intelligence | \`overview.tools.active\`, original Serena dashboard | \`GET /v2/tools\`; source/permission/endpoint details | Search existing tool names; link upstream for unsupported actions |
| Skills | \`overview.skills.items\`, \`codemind_list_skills\` | Source-backed catalog and route test \`POST /v2/skills/route\` | One installed skill is displayed as one, not 25/100 |
| Tasks | \`overview.tasks.items\` | \`GET /v2/tasks\` actual worker pool and owner identities | No imaginary queue or start button |
| Learning | \`overview.learning\` counts | \`GET /v2/failures\` / \`/v2/learning\` staged records | Counts with clear evidence limits; no fake trend chart |
| Next action & FU | \`codemind_next_action\` local diagnostic hint | \`GET /v2/actions/next\`, \`/forecast\`; advisory-only | Pending/unsupported, no Execute candidate |
| Commander | \`overview.commander\`; \`codemind_commander_status\` | \`GET /v2/commander/peer\` attested nonce status | Separate \`Process present\` from \`Auth peer unverified\` |
| Connection | \`/codemind/api/tunnel/{status,key,doctor,start,stop}\` | Keep exact routes; v2 adds typed reason/transport/poll-age, ChatGPT round-trip evidence | Diagnostic result can be PASS while remote consumer UNVERIFIED |
| Hooks | Source .codex config, no host trace in dashboard | \`GET /v2/hooks\` live trust/event data | \`Installed source / Not observed in host\`, never \`Active\` from file alone |
| Security | v1 acceptance list assembled client-side | Server-issued \`GET /v2/acceptance\` with revision | Existing static checklist labeled contract assumptions |
| Settings | Existing operator unlock + tunnel key | Provider registry and policy-authorized user settings | Hide unsupported providers and write-only secret controls |

## 5. Components and shared data rules

- \`AppShell\`, \`SidebarNavigation\`, \`TopbarProjectIdentity\`, \`GlobalStatus\`, \`SourceRevisionChip\`.
- \`MetricCard\` handles \`number|null\` with \`state\`; **null must render "—", not 0**.
- \`ServiceCard\` renders \`process_presence\`, \`authenticated\`, \`initialized\`, \`observed_at\`, \`ready\` as distinct fields.
- \`EvidenceTable\` sorting/filter/pagination based on data contract; no unbounded DOM rows.
- \`SkillCard\` source/version/trust/activation with actionable \`Inspect\` only when source truly accessible.
- \`RouteDecision\` shows \`intent\`, \`selected\`, \`loaded\`, \`executed\`, \`primary\` and \`why\`; never displays select as invoke.
- \`NextActionCard\` and \`ForecastTree\` segregate canonical and conditional branches; no Execute controls for forecasts.
- \`SecureCredentialForm\` uses password input, never repopulates it after save; show \`configured:true/false\`; label runtime key scope.
- \`AcceptanceLedger\` uses \`PASS|FAIL|BLOCKED|UNVERIFIED|NOT_APPLICABLE\` plus timestamp/source/dependency.
- \`ErrorState\` identifies distinct \`401 lock expired\`, \`403 scope denied\`, \`409 conflict\`, \`429 slow down\`, \`5xx server unavailable\`, timeout.
- \`CopyEvidence\` exports **sanitized** bounded snapshot, never API keys, prompts, command arguments, customer data or local secret paths.

## 6. Functional interaction matrix (must pass before exposing controls)

| Control / interaction | Backend + expected proof |
|---|---|
| Unlock | v1 authenticated overview; failed token remains locked; no persistence in localStorage |
| Lock | Drop token and data from JS state/DOM; cancel pending requests; lock screen |
| Refresh | Abort/timeout and show stale timestamp; no overlapping requests or optimistic freshness |
| Project switch | Show actual list; re-fetch scoped tools/skills; invalidate stale task/forecast; do not fabricate project activation |
| Tool search/filter | Client filtering of **actual registry**, keyboard and empty-state correct |
| Route prompt | v2 \`POST /skills/route\`, debounce, consent/auth; show selected vs loaded, actual strategy metadata |
| Task detail | v2 \`GET /tasks\`; preserve task ID and source generation in view |
| View failure | v2 \`GET /failures\`; sanitized fingerprint and failed-test evidence, no secret payload |
| Inspect lesson | v2 \`GET /learning\`; APPLIED only after independent delivery proof |
| Request current next action | v2 \`GET /actions/next\`, task-bound, explicit permission disclaimer |
| Expand FU branch | v2 \`GET /actions/forecast\`; conditional read-only, no executable action |
| Commander health refresh | v2 \`GET /commander/peer\`; no restart from read-only view |
| Save key | v1 \`POST /tunnel/key\`, verify response; form cleared; on 401 lock, on 409 preserve state |
| Delete saved key | v1 \`DELETE /tunnel/key\` with confirmation and no running managed client |
| Doctor | v1 \`POST /tunnel/doctor\`; typed reason; never infer invalid key from port conflict |
| Start/stop managed tunnel | v1 \`POST /tunnel/{start,stop}\`; only owned child PID; show poll/readiness separately |
| Hooks trust | Actual Codex host prompt/permission; dashboard cannot grant trust itself |
| Theme | dark/light/system, stored optionally as nonsecret preference; does not change security state |
| Export | JSON with state/provenance, redacted values and exported timestamp |
| Navigation/back/escape | Browser history/deep linking, accessible focus, drawer Escape, active item landmark |
| Retry error | Bounded retry, no re-submission of a mutation after unknown result without idempotency reconciliation |

Avoid inert buttons: if unavailable, render an explanation and its required capability gate instead of an enabled button.

## 7. Professional experience quality and correctness

**Responsive and visual**: snapshot tests at 320, 390, 768, 1024, 1440 and 1920 px; 100%/200% zoom; long skill names, very large numbers, missing tool source, multiline errors. No overlapping buttons, clipped dialogs or horizontal body overflow.

**Accessibility**: semantic landmarks, keyboard-only navigation, skip link, focus return after dialogs, accessible status messages, labels independent of placeholders, non-color-only failure states, aria-live without noisy refresh announcements, WCAG 2.2 AA.

**Security**: defensive encoding of all untrusted text (\`textContent\`, never raw \`innerHTML\`), CSP compatible scripts, form autocomplete controls, no secret echo through export/errors, same-origin writes, origin/CSRF guard, rate-limit/key rotation path. Browser unlock token not an API authorization upgrade.

**Performance**: benchmark warm refresh, cold refresh, 1k/10k row virtualization and 30s passive telemetry interval; report measured P50/P95/P99 and CPU/RAM. Avoid per-character server calls on search, 100-expert preloads and full memory/ledger scans.

**UI design check:** every displayed label must map to an existing source field, an explicitly versioned proposed field, or a hardcoded design label. Every number has \`source, timestamp, definition\`. Never make a source-only capability appear as a deployed/active service.

## 8. Frontend migration plan

1. Freeze v1 HTML, console JS/CSS and backend v1 API tests; capture screenshot/interaction baseline.
2. Add design tokens and a documented component-level state contract; do not rewrite backend solely for appearance.
3. Refactor into small modules (\`api-client.js\`, \`state.js\`, \`render/*\`, \`security.js\`) while preserving existing \`/codemind/\` route and selectors until end-to-end checks pass.
4. Implement Overview + Skills + Connections as the first complete real vertical UI slice. Wire all clicks, errors and empty states.
5. Enable remaining views only after corresponding backend v2 endpoints and tests are real.
6. Validate accessible DOM and visual proof on real Windows browser; source diff, screenshot and task generation recorded. No large CSS-only release without functional verification.

**UI acceptance:** a screenshot is not sufficient. Every enabled interaction must be traced from click -> endpoint -> authenticated backend -> state/render -> relevant negative test.
