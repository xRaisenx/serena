/* CODEMIND Serena Mission Control. Same-origin, read-only. No secrets on disk. */
"use strict";
(() => {
  const state = { token: "", snapshot: null, v2: null, catalog: null, view: "overview", theme: "dark", busy: false };
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

  function categorizeTool(name) {
    if (/symbol|reference|implementation|declaration|diagnostic|language_server/.test(name)) return "SEMANTIC INTELLIGENCE";
    if (/memory|onboarding/.test(name)) return "MEMORY";
    if (/codemind|skill/.test(name)) return "CODEMIND EXTENSION";
    if (/file|dir|search|pattern|content/.test(name)) return "FILES & SEARCH";
    if (/execute|shell|task/.test(name)) return "EXECUTION";
    return "SERENA CORE";
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
        snapshot.skills?.state === "validation_failed" ? "Skill manifests failed validation. Inspect configuration in Serena." :
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
    const ledger = [
      ["Dashboard authentication", "Valid operator token accepted on loopback", "PASS", "good"],
      ["Serena live dashboard API", "Authenticated response from the runtime", "PASS", "good"],
      ["Active project", snapshot.project?.name || "Project not activated", snapshot.project?.state === "activated" ? "OBSERVED" : "NOT ACTIVE", snapshot.project?.state === "activated" ? "good" : "warn"],
      ["Semantic registry", "Names provided by the active Serena toolset", Array.isArray(snapshot.tools?.active) ? "OBSERVED" : "UNVERIFIED", Array.isArray(snapshot.tools?.active) ? "good" : "warn"],
      ["Declarative skill validation", skills.state || "No project data", skills.state === "available" ? "OBSERVED" : "UNVERIFIED", skills.state === "available" ? "good" : "warn"],
      ["Persistent failure database", "Strategy fingerprint counters", learning.state === "available" ? "OBSERVED" : "UNVERIFIED", learning.state === "available" ? "good" : "warn"],
      ["Commander process", commander.processes?.length ? commander.processes.length + " process(es) found" : "No local process observation", commander.processes?.length ? "PRESENT" : "UNVERIFIED", commander.processes?.length ? "good" : "warn"],
      ["Commander authenticated MCP readiness", commander.peer_status || "No attestation", commander.ready && commander.authenticated ? "VERIFIED" : "UNVERIFIED", commander.ready && commander.authenticated ? "good" : "warn"],
      ["Autonomous dual-watchdog recovery", "Independent fault-injection tests required", "UNVERIFIED", "warn"],
      ["NMBV Bot worker bridge", snapshot.integrations?.nmbv_bot || "No runtime attestation", "UNVERIFIED", "warn"],
      ["OpenAI tunnel transport", tunnel.state || "No connection evidence", tunnel.connection_verified ? "VERIFIED" : "UNVERIFIED", tunnel.connection_verified ? "good" : "warn"],
      ["ChatGPT end-to-end tool call", "Not proven by a configured tunnel ID", "UNVERIFIED", "warn"],
    ];
    ledger.forEach(([title, explanation, status, grade]) => node.append(cardStatus(title, explanation, status, grade)));
  }

  function render(snapshot) {
    text("side-state", "Dashboard telemetry received");
    text("overview-live", "Authenticated telemetry");
    text("today-display", dateLabel());
    text("last-refresh", "Updated " + new Intl.DateTimeFormat(undefined, { hour: "2-digit", minute: "2-digit" }).format(new Date()));
    text("runtime-provenance", state.v2?.source?.revision_attested ?
      "BUILD VERIFIED " + state.v2.source.revision?.slice(0, 9) : "REVISION NOT ATTESTED");
    text("hero-title", snapshot.project?.state === "activated" ? "Workspace telemetry is available" : "Serena is reporting — no project active");
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
    text("topo-serena", snapshot.project?.name ? "Project: " + snapshot.project.name : "Serena dashboard API responding");
    setIndicator("status-serena", "Reporting", "good");
    const peer = snapshot.commander || {};
    text("topo-commander", peer.peer_status === "ready" ? "Authenticated MCP peer" : "Peer: " + phrase(peer.peer_status));
    setIndicator("status-commander", peer.ready && peer.authenticated ? "Verified" : "Unverified", peer.ready && peer.authenticated ? "good" : "warn");
    text("topo-tunnel", snapshot.tunnel?.state === "configured_unverified" ? "Tunnel identifier configured; not proven live" : "No verified connection");
    setIndicator("status-tunnel", snapshot.tunnel?.connection_verified ? "Verified" : "Unverified", snapshot.tunnel?.connection_verified ? "good" : "warn");
    details("workspace-details", [
      ["Project", snapshot.project?.name || "None activated"],
      ["Languages", snapshot.project?.languages?.join(", ") || "Not reported"],
      ["Serena version", snapshot.serena_version],
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
    text("tunnel-chip", tunnel.connection_verified ? "CONNECTED" : "UNVERIFIED");
    details("connection-details", [
      ["Tunnel ID", tunnel.id || "Not configured in runtime"],
      ["Configured", tunnel.state === "configured_unverified" ? "Yes, not verified live" : "No"],
      ["ChatGPT tool call", tunnel.connection_verified ? "Observed" : "Unverified"],
    ]);
    renderTools();
    renderSkills(snapshot);
    renderTasks(snapshot);
    renderAcceptance(snapshot);
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
    text("method-count", selected.length + " OF " + data.count + " REFERENCES");
    if (!selected.length) {
      node.append(element("p", "empty-state", "No matching reference methods."));
      return;
    }
    for (const method of selected) {
      const card = element("article", "method-reference");
      card.append(element("span", "tool-type", "REFERENCE ONLY • NOT INSTALLED"),
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
    text("forecast-status", "Computing a bounded evidence-gated preview…");
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 11000);
    const currentToken = state.token;
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
      if (state.token === currentToken) renderForecast(result);
    } catch (error) {
      if (state.token === currentToken)
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
    state.busy = true;
    byId("refresh-btn").disabled = true;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 9000);
    try {
      const response = await fetch("/codemind/api/overview", {
        method: "GET", credentials: "same-origin", cache: "no-store",
        headers: { "Authorization": "Bearer " + state.token, "Accept": "application/json" },
        signal: controller.signal,
      });
      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          state.token = "";
          state.snapshot = null;
          byId("workspace").hidden = true;
          byId("unlock").hidden = false;
          byId("operator-token").focus();
          throw new Error("Authentication rejected. Use a separate CODEMIND dashboard token, not your OpenAI API key.");
        }
        throw new Error("Runtime returned HTTP " + response.status + ".");
      }
      const data = await response.json();
      if (data.schema !== 1 || data.application !== "CODEMIND Serena") throw new Error("Unexpected dashboard data contract.");
      state.snapshot = data;
      state.v2 = null;
      // V1 remains the compatibility API. V2 is evidence enrichment only.
      // If the v2 API is unavailable, continue displaying observed v1 values
      // without pretending the installed V2 slice is present.
      try {
        const v2response = await fetch("/codemind/api/v2/overview", {
          method: "GET", credentials: "same-origin", cache: "no-store",
          headers: { Authorization: "Bearer " + state.token, Accept: "application/json" },
          signal: controller.signal,
        });
        if (v2response.ok) {
          const v2 = await v2response.json();
          if (v2.schema === 2 && v2.application === "CODEMIND Serena") state.v2 = v2;
        }
      } catch { /* V1 compatibility mode; no inferred V2 health. */ }
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
    button.disabled = true;
    target.textContent = "Analyzing the active project's installed skill manifests…";
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 9000);
    try {
      const response = await fetch("/codemind/api/v2/skills/route", {
        method: "POST", credentials: "same-origin", cache: "no-store",
        headers: {
          Authorization: "Bearer " + state.token,
          Accept: "application/json", "Content-Type": "application/json",
        },
        body: JSON.stringify({ request_text: requestText }),
        signal: controller.signal,
      });
      const result = await response.json();
      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          target.textContent = "Operator authorization denied. Lock and reauthenticate.";
        } else if (response.status === 409) {
          target.textContent = "No active project. Activate a Serena project before routing.";
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
      const names = Array.isArray(result.selected) ?
        result.selected.slice(0, 3).map(item => String(item.skill_id) + " (score " + Number(item.score) + ")") : [];
      target.textContent = names.length ?
        "Selected: " + names.join(", ") + ". Loaded: 0; executed: 0; permission granted: NO." :
        "No matching project skill. Loaded: 0; executed: 0; permission granted: NO.";
    } catch (error) {
      target.textContent = error.name === "AbortError" ?
        "Routing timed out; no selection or execution is confirmed." :
        "Routing request failed; no selection or execution is confirmed.";
    } finally {
      clearTimeout(timeout);
      button.disabled = false;
    }
  }

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
    state.token = ""; state.snapshot = null; state.v2 = null; state.catalog = null;
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
    a.download = "codemind-observations-" + new Date().toISOString().slice(0, 10) + ".json";
    document.body.append(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    notify("Exported the observed runtime snapshot. No API or dashboard tokens were included.");
  });
  setInterval(() => {
    if (state.token && !document.hidden && !state.busy) refresh();
  }, 30000);
})();
