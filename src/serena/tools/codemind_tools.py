# SPDX-License-Identifier: GPL-3.0-or-later
"""Opt-in CODEMIND runtime inspection tools."""

import json
from pathlib import Path

from serena.codemind.learning import FailureGuard
from serena.codemind.modules import SkillManifestRegistry
from serena.tools.tools_base import Tool


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
            raise ValueError("arguments_json must be an object")
        result = FailureGuard().status(self.get_project_root(), tool_name, arguments)
        return json.dumps(result, sort_keys=True)


class CodemindCommanderStatusTool(Tool):
    """Observe the independent Windows Commander process without restarting it."""

    def apply(self) -> str:
        """Return Commander process presence; process presence is not MCP health."""
        import psutil

        entries = []
        for process in psutil.process_iter(attrs=["pid", "name"]):
            name = (process.info["name"] or "").lower()
            if name == "windowscommander.mcpserver.exe":
                entries.append({"pid": process.info["pid"]})
        return json.dumps(
            {"commander_process_present": bool(entries),
             "processes": entries, "mcp_health_verified": False},
            sort_keys=True
        )

class CodemindSkillRouteTool(Tool):
    """Select existing declared skills for the incoming engineering request."""

    def apply(self, request: str) -> str:
        """Return a deterministic skill match; selection does not authorize execution.

        :param request: Engineering objective to classify.
        """
        from serena.codemind.planner import SkillRouter

        registry = SkillManifestRegistry(Path(self.get_project_root()) / ".codemind" / "skills")
        return json.dumps(SkillRouter(registry).route(request), sort_keys=True)


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
            raise ValueError("arguments_json must be an object")
        action = NextActionPlanner(FailureGuard()).recommend(
            self.get_project_root(), tool_name, arguments
        )
        return json.dumps(action, sort_keys=True)