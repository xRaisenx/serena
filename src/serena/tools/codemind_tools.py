# SPDX-License-Identifier: GPL-3.0-or-later
"""Opt-in CODEMIND runtime inspection tools."""

import json
from pathlib import Path

from serena.codemind.learning import FailureGuard
from serena.codemind.modules import SkillManifestRegistry
from serena.tools.tools_base import Tool, ToolMarkerDoesNotRequireActiveProject


class CodemindListSkillsTool(Tool):
    """List validated JSON instruction modules for this project."""

    def apply(self) -> str:
        """List enabled declarative skills under .codemind/skills without executing them."""
        path = Path(self.get_project_root()) / ".codemind" / "skills"
        skills = SkillManifestRegistry(path).list_skills()
        return json.dumps({"skills": skills}, sort_keys=True)


class CodemindFailureStatusTool(Tool):
    """Inspect repeated-failure protection for a specific semantic tool invocation."""

    def apply(self, tool_name: str, arguments_json: str = "{}") -> str:
        """Inspect current strategy protection, without changing repository files.

        :param tool_name: Exact MCP tool name.
        :param arguments_json: JSON object of the tool inputs to check.
        """
        arguments = json.loads(arguments_json)
        if not isinstance(arguments, dict):
            raise TypeError("arguments_json must be an object")
        result = FailureGuard().status(self.get_project_root(), tool_name, arguments)
        return json.dumps(result, sort_keys=True)


class CodemindCommanderStatusTool(Tool, ToolMarkerDoesNotRequireActiveProject):
    """Observe the independent Windows Commander process without restarting it."""

    def apply(self) -> str:
        """Return Commander process presence; process presence is not MCP health."""
        import os

        import psutil

        from serena.codemind.health import CommanderHealthProbe

        entries = []
        for process in psutil.process_iter(attrs=["pid", "name"]):
            name = (process.info["name"] or "").lower()
            if name == "windowscommander.mcpserver.exe":
                entries.append({"pid": process.info["pid"]})

        endpoint = os.environ.get("CODEMIND_COMMANDER_HEALTH_URL")
        token = os.environ.get("CODEMIND_COMMANDER_HEALTH_TOKEN")
        health = {"ready": False, "authenticated": False, "reason": "not_configured"}
        if endpoint and token:
            status = CommanderHealthProbe(endpoint, token).check()
            health = {"ready": status.ready, "authenticated": status.authenticated, "reason": status.reason}
        elif endpoint or token:
            health["reason"] = "incomplete_peer_configuration"
        return json.dumps(
            {
                "commander_process_present": bool(entries),
                "processes": entries,
                "mcp_health_verified": health["ready"] and health["authenticated"],
                "peer_health": health,
            },
            sort_keys=True,
        )


class CodemindSkillRouteTool(Tool):
    """Select existing declared skills for the incoming engineering request."""

    def apply(self, request: str) -> str:
        """Return a deterministic skill match; selection does not authorize execution.

        :param request: Engineering objective to classify.
        """
        from serena.codemind.planner import SkillRouter

        from serena.codemind.methods import recommend_method_references

        registry = SkillManifestRegistry(Path(self.get_project_root()) / ".codemind" / "skills")
        route = SkillRouter(registry).route(request)
        route["reference_suggestions"] = recommend_method_references(request)["selected_references"]
        route["loaded"] = []
        route["executed"] = []
        return json.dumps(route, sort_keys=True)


class CodemindNextActionTool(Tool):
    """Choose an evidence-constrained diagnostic action without executing it."""

    def apply(self, tool_name: str, arguments_json: str = "{}") -> str:
        """Suggest a changed approach based on stored equivalent failure evidence.

        :param tool_name: Exact tool whose strategy is being evaluated.
        :param arguments_json: JSON object of the original tool parameters.
        """
        from serena.codemind.planner import NextActionPlanner

        arguments = json.loads(arguments_json)
        if not isinstance(arguments, dict):
            raise TypeError("arguments_json must be an object")
        action = NextActionPlanner(FailureGuard()).recommend(self.get_project_root(), tool_name, arguments)
        return json.dumps(action, sort_keys=True)


class CodemindMethodCatalogTool(Tool, ToolMarkerDoesNotRequireActiveProject):
    """Discover CODEMIND's 25 source-backed reference methods, not installed skills."""

    def apply(self) -> str:
        """List CODEMIND method references without loading methods or starting workers."""
        from serena.codemind.methods import load_method_catalog

        return json.dumps(load_method_catalog(), sort_keys=True)


class CodemindForecastTool(Tool):
    """Read-only conditional next-action and FU engineering preview."""

    def apply(self, request: str) -> str:
        """Preview the safest conditional engineering path without executing tools.

        :param request: Engineering objective (3–1,000 characters).
        """
        from serena.codemind.futures import preview_actions

        return json.dumps(preview_actions(request, project_name=Path(self.get_project_root()).name), sort_keys=True)



class CodemindCapabilitiesTool(Tool, ToolMarkerDoesNotRequireActiveProject):
    """Report actual CODEMIND module contracts separately from live service proof."""

    def apply(self) -> str:
        """Return available local CODEMIND methods and honest capability boundaries."""
        from serena.codemind.methods import load_method_catalog

        catalog = load_method_catalog()
        return json.dumps(
            {
                "schema": 2,
                "application": "CODEMIND Serena",
                "method_reference_catalog": {"state": "REFERENCE_ONLY", "count": catalog["count"]},
                "skill_discovery": "PROJECT_MANIFEST_REQUIRED",
                "skill_router": "DETERMINISTIC_ADVISORY",
                "fu_next_action": "DETERMINISTIC_ADVISORY",
                "failure_guard": "PERSISTED_INVOCATION_PRECHECK",
                "governed_learning_promotion": "NOT_IMPLEMENTED",
                "codemind_100_expert_workers": "NOT_IMPLEMENTED",
                "commander_peer": "NOT_ATTESTED_BY_THIS_TOOL",
                "chatgpt_remote_acceptance": "NOT_ATTESTED_BY_THIS_TOOL",
                "authorization_granted": False,
            },
            sort_keys=True,
        )
