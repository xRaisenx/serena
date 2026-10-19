/* Secucko SCC Mission Control. Existing authenticated CODEMIND APIs remain unchanged. */
"use strict";
(() => {
  const state = { token: "", snapshot: null, v2: null, catalog: null, view: "overview", theme: "dark", busy: false, epoch: 0, skillRoute: null, forecast: null, goal: "" };
  const byId = id => document.getElementById(id);
  const all = selector => Array.from(document.querySelectorAll(selector));
  const text = (id, value) => { const node = byId(id); if (node) node.textContent = value == null ? "—" : String(value); };
  const phrase = (value, fallback = "Unverified") => value === undefined || value === null || value === "" ? fallback : String(value);
  const element = (tag, className, content) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (content !== undefined) node.textContent = String(content);
    return node;
  };
  const notify = message => {
    const region = byId("notice");
    region.textContent = message;
    region.classList.add("visible");
    clearTimeout(notify.timer);
    notify.timer = setTimeout(() => region.classList.remove("visible"), 5500);
  };
  const setIndicator = (id, label, grade) => {
    const node = byId(id);
    node.textContent = label;
    node.classList.remove("good", "warn", "bad");
    if (grade) node.classList.add(grade);
  };
  const formatNumber = value => Number.isFinite(Number(value)) && value !== null && value !== undefined ? Number(value).toLocaleString() : "—";
  const bool = value => value === true ? "Yes" : value === false ? "No" : "Unverified";
  const dateLabel = () => new Intl.DateTimeFormat(undefined, { year: "numeric", month: "long", day: "numeric" }).format(new Date());

  function details(target, values) {
    const node = byId(target);
    node.replaceChildren();
    for (const [label, value] of values) {
      const row = element("div");
      row.append(element("dt", "", label), element("dd", "", phrase(value)));
      node.append(row);
    }
  }

  function cardStatus(heading, note, label, grade) {
    const row = element("div", "acceptance-row");
    const stack = element("div");
    stack.append(element("strong", "", heading), element("p", "", note));
    const badge = element("span", "state " + (grade || ""), label);
    row.append(stack, badge);
    return row;
  }

  function currentView(name) {
    if (!all('[data-page="' + name + '"]').length) return;
    state.view = name;
    all(".page-section").forEach(s => s.classList.toggle("active", s.dataset.page === name));
    all(".nav-link").forEach(link => {
      const selected = link.dataset.view === name;
      link.classList.toggle("active", selected);
      if (selected) link.setAttribute("aria-current", "page");
      else link.removeAttribute("aria-current");
    });
    const active = all(".nav-link").find(a => a.dataset.view === name);
    text("breadcrumb", active ? active.textContent.trim().replace(/\s+—$/, "") : name);
    byId("sidebar").classList.remove("open");
    byId("menu-btn").setAttribute("aria-expanded", "false");
    const header = document.querySelector('.page-section[data-page="' + name + '"] h1');
    if (header) header.focus({ preventScroll: true });
    if (name === "tools") renderTools();
    if (name === "skills") loadMethodCatalog();
  }

  function projectDisplayName(name) {
    const actual = typeof name === "string" ? name.trim() : "";
    return actual.toLowerCase() === "serena" ? "SCC workspace" : actual;
  }

  function categorizeTool(name) {
    if (/symbol|reference|implementation|declaration|diagnostic|language_server/.test(name)) return "SEMANTIC INTELLIGENCE";
    if (/memory|onboarding/.test(name)) return "MEMORY";
    if (/codemind|skill/.test(name)) return "SCC ENGINE";
    if (/file|dir|search|pattern|content/.test(name)) return "FILES & SEARCH";
    if (/execute|shell|task/.test(name)) return "EXECUTION";
    return "SCC SEMANTIC CORE";
  }


  function downloadJSON(filename, payload) {
    const url = URL.createObjectURL(new Blob([JSON.stringify(payload, null, 2)], {type:"application/json"}));
    const anchor = document.createElement("a");
    anchor.href = url; anchor.download = filename;
    document.body.append(anchor); anchor.click(); anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  function sanitizedTasks() {
    return Array.isArray(state.snapshot?.tasks?.items) ?
      state.snapshot.tasks.items.map(t => ({
        id: String(t.id ?? ""), name: String(t.name ?? ""),
        running: t.running === true, finished_successfully: t.finished_successfully === true
      })) : [];
  }

  function renderOperatorActions(snapshot) {
    const node = byId("operator-actions");
    if (!node) return;
    node.replaceChildren();
    const missing = [];
    if (snapshot.project?.state !== "activated") missing.push(["Activate an SCC workspace", "tools", "No project is activated."]);
    if (snapshot.commander?.ready !== true || snapshot.commander?.authenticated !== true)
      missing.push(["Verify Commander peer", "commander", "Independent Commander health has not been authenticated."]);
    if (snapshot.tunnel?.connection_verified !== true)
      missing.push(["Validate remote tunnel consumer", "connections", "Client process readiness cannot prove a ChatGPT tool round-trip."]);
    if (state.v2?.source?.revision_attested !== true)
      missing.push(["Inspect runtime generation", "security", "The running Python build revision has not been attested."]);
    if (snapshot.skills?.state === "available") missing.push(["Route a coding task", "skills", "Use validated project skills to prepare a bounded engineering packet."]);
    if (!missing.length) missing.push(["Inspect accepted evidence", "security", "Review which release gates are independently verified."]);
    missing.slice(0, 5).forEach(([label,view,description]) => {
      const row=element("div","scc-action-row");
      const copy=element("span");copy.append(element("strong","",label),element("small","",description));
      const button=element("button","button secondary compact","Open →");button.type="button";button.dataset.actionView=view;
      row.append(copy,button);node.append(row);
    });
  }

  async function copyToolName(name) {
    try {
      if (!navigator.clipboard?.writeText) throw new Error("Clipboard permission unavailable");
      await navigator.clipboard.writeText(name);
      notify("Copied tool name: " + name + ". SCC has not invoked it.");
    } catch { notify("Clipboard unavailable. Select the visible tool name to copy manually."); }
  }

  function renderTools() {
    const node = byId("tools-list");
    node.replaceChildren();
    const tools = state.snapshot?.tools?.active;
    if (!Array.isArray(tools)) {
      node.append(element("p", "empty-state", "Tool registry unavailable. Authenticate and refresh to inspect."));
      return;
    }
    const term = byId("tool-search").value.trim().toLowerCase();
    const matching = tools.filter(name => name.toLowerCase().includes(term) || categorizeTool(name).toLowerCase().includes(term));
    text("tools-count", matching.length + " matching / " + tools.length + " active");
    if (!matching.length) {
      node.append(element("p", "empty-state", term ? "No tools match this search." : "No active tools reported."));
      return;
    }
    const fragment = document.createDocumentFragment();
    for (const name of matching) {
      const card = element("div", "tool-item");
      card.append(element("span", "tool-type", categorizeTool(name)), element("strong", "", name));
      const copy = element("button", "button secondary compact", "Copy tool name");
      copy.type = "button"; copy.dataset.copyTool = name; copy.setAttribute("aria-label", "Copy " + name + " tool name");
      card.append(copy);
      fragment.append(card);
    }
    node.append(fragment);
  }

  function renderSkills(snapshot) {
    const node = byId("skills-list");
    const items = snapshot.skills?.items || [];
    node.replaceChildren();
    text("skill-state", (snapshot.skills?.state || "unverified").toUpperCase().replaceAll("_", " "));
    if (!items.length) {
      node.append(element("p", "empty-state",
        snapshot.skills?.state === "no_project" ? "Activate a project to discover its .codemind/skills manifests." :
        snapshot.skills?.state === "validation_failed" ? "Skill manifests failed validation. Inspect SCC workspace configuration." :
        "No enabled skills are reported for this project."));
      return;
    }
    for (const skill of items) {
      const card = element("div", "skill-item");
      card.append(element("span", "tool-type", "v" + phrase(skill.version, "?")), element("strong", "", phrase(skill.id)));
      card.append(element("p", "", phrase(skill.description, "No description")));
      node.append(card);
    }
  }

  function renderTasks(snapshot) {
    const tbody = byId("tasks-list");
    tbody.replaceChildren();
    const tasks = snapshot.tasks?.items || [];
    text("task-count", tasks.length + " TASKS");
    if (!tasks.length) {
      const tr = element("tr");
      const td = element("td", "", snapshot.tasks?.state === "unavailable" ? "Task telemetry unavailable." : "No queued or running tasks.");
      td.colSpan = 3;
      tr.append(td);
      tbody.append(tr);
      return;
    }
    for (const task of tasks) {
      const tr = element("tr");
      tr.append(element("td", "", phrase(task.name)), element("td", "", phrase(task.id)));
      const status = task.running ? "Running" : task.finished_successfully ? "Completed" : "Not verified";
      tr.append(element("td", "", status));
      tbody.append(tr);
    }
  }

  function renderAcceptance(snapshot) {
    const node = byId("acceptance-list");
    node.replaceChildren();
    const skills = snapshot.skills || {};
    const learning = snapshot.learning || {};
    const commander = snapshot.commander || {};
    const tunnel = snapshot.tunnel || {};
    const tunnelReady = tunnel.managed_process_running === true && tunnel.client_ready === true && tunnel.health === "ready";
    const ledger = [
      ["Dashboard authentication", "Valid operator token accepted on loopback", "PASS", "good"],
      ["SCC authenticated dashboard API", "Authenticated response from the runtime", "PASS", "good"],
      ["Active project", snapshot.project?.name || "Project not activated", snapshot.project?.state === "activated" ? "OBSERVED" : "NOT ACTIVE", snapshot.project?.state === "activated" ? "good" : "warn"],
      ["Semantic registry", "Names provided by the active SCC toolset", Array.isArray(snapshot.tools?.active) ? "OBSERVED" : "UNVERIFIED", Array.isArray(snapshot.tools?.active) ? "good" : "warn"],
      ["Declarative skill validation", skills.state || "No project data", skills.state === "available" ? "OBSERVED" : "UNVERIFIED", skills.state === "available" ? "good" : "warn"],
      ["Persistent failure database", "Strategy fingerprint counters", learning.state === "available" ? "OBSERVED" : "UNVERIFIED", learning.state === "available" ? "good" : "warn"],
      ["Commander process", commander.processes?.length ? commander.processes.length + " process(es) found" : "No local process observation", commander.processes?.length ? "PRESENT" : "UNVERIFIED", commander.processes?.length ? "good" : "warn"],
      ["Commander authenticated MCP readiness", commander.peer_status || "No attestation", commander.ready && commander.authenticated ? "VERIFIED" : "UNVERIFIED", commander.ready && commander.authenticated ? "good" : "warn"],
      ["Autonomous dual-watchdog recovery", "Independent fault-injection tests required", "UNVERIFIED", "warn"],
      ["Installed SCC skill methods", skills.state === "available" ? String((skills.items || []).length) + " project manifests; routing is advisory" : "No verified skill manifest", skills.state === "available" ? "OBSERVED" : "UNVERIFIED", skills.state === "available" ? "good" : "warn"],
      ["OpenAI tunnel transport", tunnelReady ? "Managed tunnel-client returned local /readyz 200" : phrase(tunnel.health, "Tunnel not ready"), tunnelReady ? "CLIENT READY" : "UNVERIFIED", tunnelReady ? "good" : "warn"],
      ["ChatGPT end-to-end tool call", tunnel.connection_verified ? "Recent operator-challenged MCP tool call observed; remote origin is not cryptographically attested" : "Use the one-time consumer challenge and call SCC from ChatGPT", tunnel.connection_verified ? "MCP CALL SEEN" : "UNVERIFIED", tunnel.connection_verified ? "good" : "warn"],
    ];
    ledger.forEach(([title, explanation, status, grade]) => node.append(cardStatus(title, explanation, status, grade)));
    state.acceptance = ledger.map(([title, explanation, status]) => ({ title, explanation, status }));
  }

  function render(snapshot) {
    text("side-state", "Dashboard telemetry received");
    text("overview-live", "Authenticated telemetry");
    text("today-display", dateLabel());
    text("last-refresh", "Updated " + new Intl.DateTimeFormat(undefined, { hour: "2-digit", minute: "2-digit" }).format(new Date()));
    text("runtime-provenance", state.v2?.source?.revision_attested ?
      "BUILD VERIFIED " + state.v2.source.revision?.slice(0, 9) : "REVISION NOT ATTESTED");
    text("hero-title", snapshot.project?.state === "activated" ? "Workspace telemetry is available" : "SCC engine reporting — no workspace active");
    text("hero-desc", "The dashboard is responding. Individual services remain unverified until their own authenticated readiness checks succeed.");
    text("metric-tools", formatNumber(snapshot.tools?.active_count));
    text("metric-tools-note", formatNumber(snapshot.tools?.registered_count) + " names registered by engine");
    text("metric-skills", formatNumber(snapshot.skills?.items?.length));
    text("metric-failures", formatNumber(snapshot.learning?.tracked_strategies));
    text("metric-blocked", formatNumber(snapshot.learning?.blocked_strategies));
    text("learn-tracked", formatNumber(snapshot.learning?.tracked_strategies));
    text("learn-blocked", formatNumber(snapshot.learning?.blocked_strategies));
    text("learning-state", phrase(snapshot.learning?.state).toUpperCase());
    text("nav-tool-count", formatNumber(snapshot.tools?.active_count));
    text("topo-serena", snapshot.project?.name ? "Workspace: " + projectDisplayName(snapshot.project.name) : "SCC engine reporting");
    setIndicator("status-serena", "Reporting", "good");
    const peer = snapshot.commander || {};
    text("topo-commander", peer.peer_status === "ready" ? "Authenticated MCP peer" : "Peer: " + phrase(peer.peer_status));
    setIndicator("status-commander", peer.ready && peer.authenticated ? "Verified" : "Unverified", peer.ready && peer.authenticated ? "good" : "warn");
    const tunnelReady = snapshot.tunnel?.managed_process_running === true &&
      snapshot.tunnel?.client_ready === true && snapshot.tunnel?.health === "ready";
    text("topo-tunnel", snapshot.tunnel?.connection_verified ? "Recent authenticated MCP consumer proof" :
      tunnelReady ? "SCC tunnel client ready; consumer proof pending" : "Tunnel client not verified ready");
    setIndicator("status-tunnel", tunnelReady ? "Client ready" : "Unverified", tunnelReady ? "good" : "warn");
    details("workspace-details", [
      ["Workspace", projectDisplayName(snapshot.project?.name) || "None activated"],
      ["Languages", snapshot.project?.languages?.join(", ") || "Not reported"],
      ["SCC engine version", snapshot.serena_version],
      ["Context", snapshot.context],
    ]);
    details("commander-details", [
      ["Process observed", peer.processes?.length ? peer.processes.length + " process(es)" : "No process reported"],
      ["MCP peer ready", bool(peer.ready)],
      ["Authentication", bool(peer.authenticated)],
      ["Health proof", phrase(peer.peer_status)],
    ]);
    text("commander-health-chip", peer.ready && peer.authenticated ? "VERIFIED READY" : "NOT VERIFIED");
    const tunnel = snapshot.tunnel || {};
    text("key-status-chip", tunnel.key_configured ? "ENCRYPTED KEY SAVED" : "KEY MISSING");
    details("tunnel-settings-details", [
      ["Key stored for this Windows user", bool(tunnel.key_configured)],
      ["Managed tunnel process", bool(tunnel.managed_process_running)],
      ["Client ready", bool(tunnel.client_ready)],
      ["Local readiness signal", phrase(tunnel.health)],
      ["ChatGPT round-trip", tunnel.connection_verified ? "Verified" : "Not verified"],
    ]);
    text("tunnel-chip", tunnel.connection_verified ? "RECENT MCP CALL" : tunnelReady ? "CLIENT READY" : "UNVERIFIED");
    details("connection-details", [
      ["Tunnel ID", tunnel.id || "Not configured in runtime"],
      ["Transport ready", tunnelReady ? "Yes; local /readyz returned 200" : "Not verified"],
      ["MCP consumer proof", tunnel.connection_verified ? "Recent operator challenge accepted" : "Not attested"],
    ]);
    renderTools();
    renderSkills(snapshot);
    renderTasks(snapshot);
    renderAcceptance(snapshot);
    renderOperatorActions(snapshot);
  }


  function renderMethodCatalog() {
    const node = byId("method-list");
    node.replaceChildren();
    const data = state.catalog;
    if (!data || data.state !== "REFERENCE_ONLY" || !Array.isArray(data.methods)) {
      text("method-count", "CATALOG UNAVAILABLE");
      node.append(element("p", "empty-state", "This runtime does not expose a verified method reference catalog."));
      return;
    }
    const q = byId("method-search").value.trim().toLowerCase();
    const selected = data.methods.filter(item =>
      [item.id, item.description, item.source_name].some(x => String(x || "").toLowerCase().includes(q)));
    const skillTelemetryReady = state.snapshot?.skills?.state === "available" && Array.isArray(state.snapshot.skills.items);
    const installedIds = new Set(skillTelemetryReady ? state.snapshot.skills.items.map(item => item.id) : []);
    const installedCount = data.methods.filter(item => installedIds.has(item.id)).length;
    text("method-count", selected.length + " OF " + data.count + " REFERENCES • " +
      (skillTelemetryReady ? installedCount + " INSTALLED" : "INSTALLATION UNVERIFIED"));
    if (!selected.length) {
      node.append(element("p", "empty-state", "No matching reference methods."));
      return;
    }
    for (const method of selected) {
      const card = element("article", "method-reference");
      const installation = !skillTelemetryReady ? "INSTALLATION UNVERIFIED" :
        installedIds.has(method.id) ? "PROJECT SKILL INSTALLED • NOT EXECUTED" : "REFERENCE ONLY • NOT INSTALLED";
      card.append(element("span", "tool-type", installation),
        element("strong", "", method.id),
        element("p", "", method.description),
        element("small", "method-source", "Origin: " + method.source_name));
      node.append(card);
    }
  }

  async function loadMethodCatalog() {
    if (!state.token || state.catalog) { renderMethodCatalog(); return; }
    const currentToken = state.token;
    try {
      const response = await fetch("/codemind/api/v2/methods", {
        method: "GET", credentials: "same-origin", cache: "no-store",
        headers: { Authorization: "Bearer " + currentToken, Accept: "application/json" },
      });
      if (!response.ok) throw new Error("Catalog HTTP " + response.status);
      const data = await response.json();
      if (data.schema !== 2 || data.state !== "REFERENCE_ONLY" || data.count !== 25 ||
          !Array.isArray(data.methods) || data.methods.length !== 25 ||
          data.methods.some(x => x.state !== "REFERENCE_ONLY" || x.loaded !== false || x.executed !== false)) {
        throw new Error("Catalog contains unsupported installation claims.");
      }
      if (currentToken !== state.token) return;
      state.catalog = data;
      renderMethodCatalog();
    } catch {
      if (currentToken === state.token) renderMethodCatalog();
    }
  }

  function renderForecast(result) {
    const target = byId("forecast-preview");
    const future = byId("forecast-futures");
    target.replaceChildren();
    future.replaceChildren();
    details("forecast-canonical", [
      ["Action", result.canonical.action],
      ["Evidence gate", result.canonical.evidence_gate],
      ["Task binding", result.task_binding],
      ["Selected intent", result.intent],
      ["Installed SCC methods", Array.isArray(result.skill_context?.selected) && result.skill_context.selected.length ?
        result.skill_context.selected.join(", ") : "No task-matching project skill"],
      ["First real read-only action", result.skill_context?.next_read_only_tool === "find_symbol" ?
        "Skills & routing → inspect a project-relative source symbol" : "Unavailable until workspace methods and SCC tools are verified"],
      ["Noetic Fleet", result.skill_context?.noetic_fleet || "NOT_RUNNING"],
      ["Execution authorization", "NOT GRANTED"],
    ]);
    const renderList = (node, items) => {
      if (!items.length) { node.append(element("li", "", "No grounded future actions.")); return; }
      for (const candidate of items) {
        const li = element("li");
        li.append(element("span", "advisory-tag", candidate.verdict + " • NON-EXECUTABLE"),
          element("strong", "", candidate.action),
          element("small", "", candidate.evidence_gate));
        node.append(li);
      }
    };
    renderList(target, result.preview);
    renderList(future, result.fu_candidates);
    text("forecast-count", result.fu_candidates.length + " CONDITIONAL CANDIDATES");
    text("forecast-status", "Advisory preview generated. " + result.blocker +
      ". No task was scheduled; no tools were invoked; all future candidates require new evidence.");
  }

  async function requestForecast(event) {
    event.preventDefault();
    const input = byId("forecast-input");
    const goal = input.value.trim();
    const submit = byId("forecast-submit");
    if (!state.token || state.busy) {
      text("forecast-status", "Authenticate and finish the current request first.");
      return;
    }
    if (goal.length < 3 || goal.length > 1000) {
      text("forecast-status", "Enter 3 to 1,000 characters.");
      return;
    }
    submit.disabled = true;
    state.forecast = null;
    byId("packet-download").disabled = true;
    text("forecast-status", "Computing a bounded evidence-gated preview…");
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 11000);
    const currentToken = state.token;
    const currentEpoch = state.epoch;
    try {
      const response = await fetch("/codemind/api/v2/actions/preview", {
        method: "POST", credentials: "same-origin", cache: "no-store",
        headers: { Authorization: "Bearer " + currentToken, Accept: "application/json", "Content-Type": "application/json" },
        body: JSON.stringify({ request_text: goal }), signal: controller.signal,
      });
      if (!response.ok) throw new Error("Preview unavailable: HTTP " + response.status);
      const result = await response.json();
      if (result.schema !== 2 || result.state !== "ADVISORY_ONLY" ||
          result.authorization_granted !== false || result.canonical?.authorized !== false ||
          !Array.isArray(result.preview) || result.preview.length > 5 ||
          !Array.isArray(result.fu_candidates) || result.fu_candidates.length > 20 ||
          result.fu_candidates.some(x => x.executable !== false || x.authorized_by_forecast !== false)) {
        throw new Error("Unsafe or invalid preview response. Nothing executed.");
      }
      if (state.token === currentToken && state.epoch === currentEpoch) {
        state.forecast = result;
        state.goal = goal;
        byId("packet-download").disabled = false;
        renderForecast(result);
      }
    } catch (error) {
      if (state.token === currentToken && state.epoch === currentEpoch)
        text("forecast-status", error.name === "AbortError" ?
          "Forecast timed out; no result has been accepted." :
          "Preview failed: " + error.message + ". Nothing executed.");
    } finally {
      clearTimeout(timeout);
      submit.disabled = false;
    }
  }

  async function refresh() {
    if (state.busy || !state.token) return;
    const currentToken = state.token;
    const currentEpoch = state.epoch;
    state.busy = true;
    byId("refresh-btn").disabled = true;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 9000);
    try {
      const response = await fetch("/codemind/api/overview", {
        method: "GET", credentials: "same-origin", cache: "no-store",
        headers: { "Authorization": "Bearer " + currentToken, "Accept": "application/json" },
        signal: controller.signal,
      });
      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          state.epoch += 1;
          state.token = "";
          state.snapshot = null;
          byId("workspace").hidden = true;
          byId("unlock").hidden = false;
          byId("operator-token").focus();
          throw new Error("Authentication rejected. Use your SCC operator token, not an OpenAI API key.");
        }
        throw new Error("Runtime returned HTTP " + response.status + ".");
      }
      const data = await response.json();
      if (data.schema !== 1 || data.application !== "CODEMIND Serena") throw new Error("Unexpected dashboard data contract.");
      let v2Model = null;
      // V1 remains the compatibility API. V2 is evidence enrichment only.
      // If the v2 API is unavailable, continue displaying observed v1 values
      // without pretending the installed V2 slice is present.
      try {
        const v2response = await fetch("/codemind/api/v2/overview", {
          method: "GET", credentials: "same-origin", cache: "no-store",
          headers: { Authorization: "Bearer " + currentToken, Accept: "application/json" },
          signal: controller.signal,
        });
        if (v2response.ok) {
          const v2 = await v2response.json();
          if (v2.schema === 2 && v2.application === "CODEMIND Serena") v2Model = v2;
        }
      } catch { /* V1 compatibility mode; no inferred V2 health. */ }
      if (state.epoch !== currentEpoch || state.token !== currentToken) return false;
      state.snapshot = data;
      state.v2 = v2Model;
      render(data);
      byId("unlock").hidden = true;
      byId("workspace").hidden = false;
      byId("operator-token").value = "";
      return true;
    } catch (error) {
      text("side-state", "Connection unverified");
      text("last-refresh", "Telemetry unavailable");
      notify(error.name === "AbortError" ? "Request timed out. No success has been inferred." : error.message);
      return false;
    } finally {
      clearTimeout(timeout);
      state.busy = false;
      byId("refresh-btn").disabled = false;
    }
  }

  async function tunnelAction(path, method = "POST", body) {
    if (!state.token || state.busy) {
      notify("Unlock the dashboard and wait for the current request to finish.");
      return;
    }
    const display = byId("tunnel-result");
    display.textContent = "Processing " + path.split("/").pop() + "…";
    const controls = all("#tunnel-key-form button, .connection-actions button");
    controls.forEach(control => control.disabled = true);
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 44000);
    try {
      const response = await fetch("/codemind/api/tunnel/" + path, {
        method, credentials: "same-origin", cache: "no-store",
        headers: {
          Authorization: "Bearer " + state.token,
          Accept: "application/json",
          ...(body ? { "Content-Type": "application/json" } : {}),
        },
        body: body ? JSON.stringify(body) : undefined,
        signal: controller.signal,
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || result.message || "Request failed (HTTP " + response.status + ")");
      const message = path === "key" ? "API key encrypted and stored for this Windows user. Run diagnostics next." :
        path === "doctor" ? (result.passed ? "Tunnel doctor PASS. You may now start the client." : "Tunnel doctor did not pass.") :
        path === "start" ? (result.tunnel?.client_ready ? "Tunnel client reports ready. Verify ChatGPT next." :
          "Tunnel process was launched. Waiting for live readiness; refresh.") :
        path === "stop" ? "Managed tunnel stopped." : "Action completed.";
      display.textContent = message;
      notify(message);
      await refresh();
    } catch (error) {
      const message = error.name === "AbortError" ? "Action timed out; status is unverified." : error.message;
      display.textContent = message;
      notify(message);
      await refresh();
    } finally {
      clearTimeout(timeout);
      controls.forEach(control => control.disabled = false);
    }
  }

  byId("tunnel-key-form").addEventListener("submit", event => {
    event.preventDefault();
    const input = byId("tunnel-api-key");
    const key = input.value;
    input.value = ""; // Never retain raw secret in the DOM after submission.
    if (!/^sk-[A-Za-z0-9_-]{29,250}$/.test(key)) {
      notify("Enter a complete, unmasked OpenAI Platform API key.");
      return;
    }
    tunnelAction("key", "POST", { api_key: key });
  });
  byId("tunnel-doctor").addEventListener("click", () => tunnelAction("doctor"));
  byId("tunnel-start").addEventListener("click", () => tunnelAction("start"));
  byId("tunnel-stop").addEventListener("click", () => tunnelAction("stop"));
  byId("tunnel-remove-key").addEventListener("click", () => {
    if (window.confirm("Remove the encrypted tunnel runtime API key for this Windows account?")) {
      tunnelAction("key", "DELETE");
    }
  });


  async function routeSkillRequest(event) {
    event.preventDefault();
    const input = byId("skill-route-input");
    const target = byId("skill-route-result");
    const button = byId("skill-route-submit");
    const requestText = input.value.trim();
    if (requestText.length < 3 || requestText.length > 1000) {
      target.textContent = "Enter a request between 3 and 1,000 characters.";
      return;
    }
    if (!state.token || state.busy) {
      target.textContent = "Unlock the dashboard and finish the current request first.";
      return;
    }
    const routedToken = state.token;
    const routedEpoch = state.epoch;
    button.disabled = true;
    state.skillRoute = null;
    target.textContent = "Analyzing the active project's installed skill manifests…";
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 9000);
    try {
      const response = await fetch("/codemind/api/v2/skills/route", {
        method: "POST", credentials: "same-origin", cache: "no-store",
        headers: {
          Authorization: "Bearer " + routedToken,
          Accept: "application/json", "Content-Type": "application/json",
        },
        body: JSON.stringify({ request_text: requestText }),
        signal: controller.signal,
      });
      const result = await response.json();
      if (state.token !== routedToken || state.epoch !== routedEpoch) return;
      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          target.textContent = "Operator authorization denied. Lock and reauthenticate.";
        } else if (response.status === 409) {
          target.textContent = result.state === "NO_MATCHING_SKILL" ?
            "This SCC workspace has no matching enabled skill. Check the active project and install applicable SCC manifests." :
            "No active project. Activate your SCC workspace before routing.";
        } else if (response.status === 422) {
          target.textContent = "Installed skill manifests failed validation; no skill selected.";
        } else {
          target.textContent = "Routing is unavailable (HTTP " + response.status + ").";
        }
        return;
      }
      if (result.schema !== 2 || result.state !== "ROUTED" || result.authorization_granted !== false) {
        target.textContent = "Invalid or unsafe routing response. Nothing was executed.";
        return;
      }
      if (!Array.isArray(result.loaded) || !Array.isArray(result.skill_playbooks) ||
          result.skill_playbooks.some(item => !result.loaded.includes(item.skill_id) ||
            typeof item.instructions !== "string")) {
        target.textContent = "Skill loading proof is missing; nothing was executed.";
        return;
      }
      state.skillRoute = {request_text: requestText, selected: Array.isArray(result.selected) ?
        result.selected.slice(0,3).map(item => ({skill_id:String(item.skill_id),score:Number(item.score)})) : [],
        loaded: result.loaded.slice(0,3)};
      const names = Array.isArray(result.selected) ?
        result.selected.slice(0, 3).map(item => String(item.skill_id) + " (score " + Number(item.score) + ")") : [];
      const referenceNames = Array.isArray(result.reference_suggestions) ?
        result.reference_suggestions.slice(0, 3).filter(item => item.state === "REFERENCE_ONLY")
          .map(item => String(item.id)) : [];
      target.textContent =
        (names.length ? "Installed skill selection: " + names.join(", ") + ". " :
          "No matching installed project skill. ") +
        (referenceNames.length ? "Method references (not installed): " + referenceNames.join(", ") + ". " :
          "No matching reference method. ") +
        "Loaded: " + result.loaded.length + " method instruction(s). Executed: 0. Fleet workers running: NO. " +
        "Use the source-symbol form below for a real read-only SCC semantic call.\n\n" +
        result.skill_playbooks.map(item => item.skill_id + ": " + item.instructions).join("\n\n");
    } catch (error) {
      target.textContent = error.name === "AbortError" ?
        "Routing timed out; no selection or execution is confirmed." :
        "Routing request failed; no selection or execution is confirmed.";
    } finally {
      clearTimeout(timeout);
      button.disabled = false;
    }
  }


  async function inspectSkillRequest(event) {
    event.preventDefault();
    const requestText = byId("skill-route-input").value.trim();
    const relativePath = byId("skill-inspect-path").value.trim();
    const symbol = byId("skill-inspect-symbol").value.trim();
    const target = byId("skill-inspect-result");
    const button = byId("skill-inspect-submit");
    if (!state.token || state.busy || requestText.length < 3 || requestText.length > 1000 ||
        !/^[A-Za-z_][A-Za-z0-9_./-]{0,95}$/.test(symbol) || !relativePath) {
      target.textContent = "Unlock SCC, enter an engineering request, source path and valid symbol.";
      return;
    }
    if (!state.skillRoute || state.skillRoute.request_text !== requestText) {
      await routeSkillRequest({preventDefault() {}});
      if (!state.skillRoute) {
        target.textContent = "Skill routing must succeed before semantic inspection.";
        return;
      }
    }
    const currentToken = state.token, currentEpoch = state.epoch;
    button.disabled = true;
    target.textContent = "Running one explicitly requested read-only SCC symbol lookup…";
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 14000);
    try {
      const response = await fetch("/codemind/api/v2/skills/inspect", {
        method: "POST", credentials: "same-origin", cache: "no-store",
        headers: {Authorization: "Bearer " + currentToken, "Content-Type": "application/json"},
        body: JSON.stringify({request_text: requestText, relative_path: relativePath, symbol}),
        signal: controller.signal,
      });
      const payload = await response.json();
      if (currentToken !== state.token || currentEpoch !== state.epoch) return;
      if (!response.ok || payload.state !== "INSPECTED" ||
          payload.authorization_granted !== false || !Array.isArray(payload.symbols) ||
          !Array.isArray(payload.loaded) || !Array.isArray(payload.executed) ||
          payload.executed.length !== 1 || payload.executed[0].tool !== "find_symbol") {
        target.textContent = "Semantic inspection blocked or failed (" + (payload.state || response.status) +
          "). No source was modified.";
        return;
      }
      const located = payload.symbols.map(item => String(item.name_path || "?") + " @ " +
        String(item.relative_path || relativePath) + ":" +
        String(item.body_location?.start_line ?? "?")).join("; ");
      target.textContent = "LIVE READ-ONLY SCC SEMANTIC TOOL: find_symbol. Loaded method instructions: " +
        payload.loaded.map(item => String(item.skill_id)).join(", ") +
        ". Symbols found: " + payload.symbols.length + ". " +
        (located || "No matching symbols; refine the name or inspect the actual source.") +
        ". Noetic Fleet workers: NOT RUNNING. Source changes: NONE.";
    } catch (error) {
      if (currentToken === state.token && currentEpoch === state.epoch) {
        target.textContent = error.name === "AbortError" ?
          "Semantic inspection timed out; no execution was confirmed." :
          "SCC symbol inspection failed; no source was modified.";
      }
    } finally {
      clearTimeout(timeout);
      button.disabled = false;
    }
  }
  byId("skill-inspect-form").addEventListener("submit", inspectSkillRequest);

  byId("operator-actions").addEventListener("click", event => {
    const button = event.target.closest("[data-action-view]");
    if (button) currentView(button.dataset.actionView);
  });
  byId("tools-list").addEventListener("click", event => {
    const button = event.target.closest("[data-copy-tool]");
    if (button && state.snapshot) copyToolName(button.dataset.copyTool);
  });
  byId("skill-packet-next").addEventListener("click", async () => {
    if (!byId("skill-route-form").reportValidity() || !state.token || state.busy) return;
    const goal = byId("skill-route-input").value.trim();
    await routeSkillRequest({preventDefault() {}});
    if (!state.skillRoute || state.skillRoute.request_text !== goal) return;
    byId("forecast-input").value = goal;
    currentView("forecast");
    await requestForecast({preventDefault() {}});
  });
  byId("packet-skill-link").addEventListener("click", () => {
    if (byId("forecast-input").value.trim()) byId("skill-route-input").value = byId("forecast-input").value.trim();
    currentView("skills"); byId("skill-route-input").focus();
  });
  byId("packet-download").addEventListener("click", () => {
    if (!state.token || !state.forecast || !state.goal) return;
    const f = state.forecast;
    downloadJSON("scc-engineering-packet.json",{
      schema:"scc-engineering-packet-v1",created_at:new Date().toISOString(),
      status:"ADVISORY_ONLY",authorization_granted:false,
      project:state.snapshot?.project?.name || null,goal:state.goal,
      installed_skills:state.skillRoute?.request_text === state.goal ? state.skillRoute.selected : [],
      canonical:f.canonical,preview:f.preview,conditional_futures:f.fu_candidates,
      source_revision:state.v2?.source?.revision_attested === true ? state.v2.source.revision : null,
      release_note:"No commands run, work authorized, or acceptance proved by this packet."
    });
    notify("Engineering packet downloaded; no commands executed.");
  });
  byId("learning-investigate").addEventListener("click", () => {
    const n=state.snapshot?.learning?.tracked_strategies;
    byId("forecast-input").value="Investigate "+(Number.isFinite(Number(n))?Number(n):"observed")+" SCC failure strategy fingerprint(s). Find the first reproducible defect, switch strategy after repeated identical failures, and require new test evidence.";
    currentView("forecast");
  });
  byId("learning-export").addEventListener("click", () => {
    if (!state.snapshot) return notify("Authenticate and refresh before exporting.");
    const l=state.snapshot.learning || {};
    downloadJSON("scc-guard-observation.json",{schema:"scc-guard-observation-v1",captured_at:new Date().toISOString(),project:state.snapshot.project?.name,tracked_strategies:l.tracked_strategies,blocked_strategies:l.blocked_strategies,state:l.state,acceptance:"OBSERVATION_ONLY"});
  });
  byId("task-export").addEventListener("click", () => {
    if (!state.snapshot) return notify("Authenticate and refresh before exporting.");
    downloadJSON("scc-task-observations.json",{schema:"scc-task-observations-v1",captured_at:new Date().toISOString(),project:state.snapshot.project?.name,tasks:sanitizedTasks(),status:"OBSERVATION_ONLY"});
  });
  byId("task-plan").addEventListener("click", () => {
    const tasks=sanitizedTasks();
    const first=tasks.find(t=>t.running)||tasks[0];
    byId("forecast-input").value=first?"Investigate task "+first.name+" ("+first.id+"). Determine current evidence, missing acceptance gate and safe next engineering action.":"Inspect the current SCC task queue, identify the first missing acceptance criterion and propose an evidence-backed action.";
    currentView("forecast");
  });
  byId("commander-check").addEventListener("click", async () => {
    if (!state.token) return notify("Unlock SCC before checking the peer.");
    text("commander-check-result","Requesting fresh authenticated SCC runtime evidence…");
    if (!await refresh()) {text("commander-check-result","Peer refresh failed. No readiness inferred.");return;}
    const c=state.snapshot?.commander||{};
    text("commander-check-result",c.ready === true && c.authenticated === true?
      "Authenticated Commander peer verified ready.":
      "NOT VERIFIED: "+phrase(c.peer_status,"not_configured")+". Configure CODEMIND_COMMANDER_HEALTH_URL and CODEMIND_COMMANDER_HEALTH_TOKEN in SCC, and implement the compatible independent peer. No restart was attempted.");
  });
  byId("tunnel-consumer-challenge").addEventListener("click", async () => {
    if (!state.token || state.busy) return notify("Unlock SCC first.");
    const currentToken=state.token, currentEpoch=state.epoch;
    text("tunnel-consumer-result","Issuing a one-time MCP acceptance challenge…");
    try {
      const response=await fetch("/codemind/api/tunnel/acceptance/challenge",{
        method:"POST",credentials:"same-origin",cache:"no-store",
        headers:{"Authorization":"Bearer "+currentToken,"Content-Type":"application/json"},
        body:"{}",
      });
      const body=await response.json();
      if(state.token!==currentToken||state.epoch!==currentEpoch)return;
      if(!response.ok||!/^[a-f0-9]{40}$/.test(body.challenge||""))throw Error(body.error||"Challenge unavailable");
      text("tunnel-consumer-result","Challenge (90 seconds): "+body.challenge+
        " — Ask ChatGPT to call codemind_consumer_proof with this exact challenge, then press Refresh. The proof expires after 10 minutes and does not attest cloud caller identity.");
    }catch{
      if(state.token===currentToken)text("tunnel-consumer-result","Challenge unavailable: verify the SCC-managed tunnel is ready and retry.");
    }
  });
  byId("tunnel-evidence").addEventListener("click", () => {
    if (!state.snapshot) return notify("Authenticate and refresh before exporting.");
    const t=state.snapshot.tunnel||{};
    downloadJSON("scc-tunnel-observation.json",{schema:"scc-tunnel-observation-v1",captured_at:new Date().toISOString(),state:t.state||"unverified",managed_process_running:t.managed_process_running===true,client_ready:t.client_ready===true,connection_verified:t.connection_verified===true,health:t.health||"not_reported",notice:"No tunnel key or connection secret is exported."});
  });
  byId("security-export").addEventListener("click", () => {
    if (!state.snapshot) return notify("Authenticate and refresh before exporting.");
    downloadJSON("scc-acceptance-evidence.json",{schema:"scc-acceptance-evidence-v1",captured_at:new Date().toISOString(),project:state.snapshot.project?.name,revision_attested:state.v2?.source?.revision_attested===true,gates:state.acceptance||[],notice:"Observed telemetry is not an independent runtime or consumer acceptance certificate."});
  });
  byId("security-next").addEventListener("click", () => {
    const c=state.snapshot?.commander||{},t=state.snapshot?.tunnel||{};
    if (!(c.ready===true&&c.authenticated===true))currentView("commander");
    else if(t.connection_verified!==true)currentView("connections");
    else if(state.v2?.source?.revision_attested!==true)currentView("tools");
    else currentView("forecast");
  });

  byId("skill-route-form").addEventListener("submit", routeSkillRequest);
  byId("forecast-form").addEventListener("submit", requestForecast);
  byId("method-search").addEventListener("input", renderMethodCatalog);
  byId("clear-methods").addEventListener("click", () => {
    byId("method-search").value = ""; renderMethodCatalog(); byId("method-search").focus();
  });
  byId("unlock-form").addEventListener("submit", async event => {
    event.preventDefault();
    const token = byId("operator-token").value;
    if (token.length < 32) { notify("Operator token must have at least 32 characters."); return; }
    state.token = token;
    await refresh();
  });
  byId("lock-btn").addEventListener("click", () => {
    state.epoch += 1;
    state.token = ""; state.snapshot = null; state.v2 = null; state.catalog = null;
    state.skillRoute = null; state.forecast = null; state.goal = ""; state.acceptance = [];
    byId("packet-download").disabled = true;
    byId("workspace").hidden = true; byId("unlock").hidden = false;
    byId("operator-token").focus(); notify("Session locked; no operator token retained.");
  });
  byId("refresh-btn").addEventListener("click", refresh);
  byId("tool-search").addEventListener("input", renderTools);
  byId("clear-tools").addEventListener("click", () => { byId("tool-search").value = ""; renderTools(); byId("tool-search").focus(); });
  byId("navigation").addEventListener("click", event => {
    const target = event.target.closest("[data-view]");
    if (target) currentView(target.dataset.view);
  });
  all("[data-go]").forEach(link => link.addEventListener("click", () => currentView(link.dataset.go)));
  byId("theme-btn").addEventListener("click", () => {
    state.theme = state.theme === "dark" ? "light" : "dark";
    document.body.classList.toggle("light", state.theme === "light");
    byId("theme-btn").setAttribute("aria-label", "Activate " + (state.theme === "light" ? "dark" : "light") + " theme");
  });
  byId("menu-btn").addEventListener("click", () => {
    const opened = byId("sidebar").classList.toggle("open");
    byId("menu-btn").setAttribute("aria-expanded", String(opened));
  });
  document.addEventListener("keydown", event => {
    if (event.key === "Escape" && byId("sidebar").classList.contains("open")) {
      byId("sidebar").classList.remove("open");
      byId("menu-btn").setAttribute("aria-expanded", "false");
      byId("menu-btn").focus();
    }
  });
  byId("export-btn").addEventListener("click", () => {
    if (!state.snapshot) { notify("There is no authenticated telemetry to export."); return; }
    const blob = new Blob([JSON.stringify({ exported_at: new Date().toISOString(), snapshot: state.snapshot }, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "scc-observations-" + new Date().toISOString().slice(0, 10) + ".json";
    document.body.append(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    notify("Exported the observed runtime snapshot. No API or dashboard tokens were included.");
  });
  setInterval(() => {
    if (state.token && !document.hidden && !state.busy) refresh();
  }, 30000);
})();
