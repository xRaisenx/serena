# SCC method routing and semantic work cells

**Purpose:** Turn an operator's concrete engineering request into installed method instructions, a real project-scoped read-only Serena semantic inspection, and a conditional Future Unraveler preview. SCC is not a replacement for Serena's LSP; it is its safety- and evidence-oriented engineering cockpit.

## What the three controls do

1. **Route an engineering task**: Read enabled `.codemind/skills/*.json` manifests from the **active Serena project**; deterministically select at most three matching skills; actually load their validated instruction text and display it. The selection and loading do not grant tool permission. If the project has no matching installed skills, return an explicit `NO_MATCHING_SKILL` response rather than an empty success.
2. **Run read-only Serena symbol inspection**: Supply a project-relative source file under `src/` or `test/` and a symbol name. This step invokes Serena's native `find_symbol` tool once, after checking the operator session, active tool permission, file scope, symlinks and enabled project methods. The response contains the resolved symbols, which method instructions were loaded, and `executed: [{tool: find_symbol, mode: READ_ONLY}]`. It performs no write, worker spawn or code change.
3. **Inspect the next safest engineering step / Future Unraveler**: The same engineering request receives a canonical evidence gate, five-stage conditional preview, bounded future alternatives, and a list of installed SCC methods relevant to that request. This is a falsifiable plan, not an automatic operation.

## Run a reproducible example

Open `http://127.0.0.1:24283/codemind/`, unlock the SCC dashboard, and check that the active Serena project is `serena`. If it is a different project, activate `D:\DEV\codemind-serena` with the Serena `activate_project` tool in **your own Serena session**, not through NMBV Bot.

Open **Skills & routing** and use:

- Request: `Debug repeated SCC MCP connection failure, inspect Python symbols, reproduce the defect, and test the regression`
- Project-relative file: `src/serena/codemind/planner.py`
- Symbol: `SkillRouter/route`

Press **Analyze skill fit**. Observe matched and loaded project instruction manifests. Press **Run read-only Serena symbol inspection**. The expected tool is `find_symbol`, with the matching `SkillRouter/route` source location. This observation is a real Serena tool call, not a proposed action.

Press **Route + build action packet** to obtain a skill-linked Future Unraveler preview. The canonical action is still evidence- or task-bound and requires human authorization for any edit.

## Noetic Fleet distinction

The skill manifests are method instructions, **not live worker processes**. SCC's method-routing work cell can load methods and drive explicitly authorized Serena read-only tools. The native Noetic Fleet (independent specialists, persistent task ownership, actual parallel worker handles, governed writes and handoff) is **NOT_RUNNING** and cannot honestly be called fully adapted merely because method names appear in the dashboard.

The SCC tool boundary applies to the active project's `src/` and `test/` files. Arbitrary file paths, directory traversal, symbolic links, unsupported file types, anonymous requests and cross-origin browser requests are denied. Future forecasts remain non-executable until separate authorization and task ownership are established.
