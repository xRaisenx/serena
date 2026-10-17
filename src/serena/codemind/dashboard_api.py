# SPDX-License-Identifier: GPL-3.0-or-later
"""Authenticated read-only CODEMIND operations console for Serena's Flask dashboard.

No process mutation, shell execution, token persistence or remote health bypass.
"""
from __future__ import annotations

import hmac
import os
import sqlite3
from pathlib import Path
from typing import Any

import psutil
from flask import Blueprint, abort, jsonify, make_response, redirect, request

from serena.codemind.health import CommanderHealthProbe
from serena.codemind.learning import FailureGuard
from serena.codemind.modules import SkillManifestRegistry


def register_codemind_routes(app: Any, agent: Any, tool_names: list[str], tool_usage_stats: Any = None) -> None:
    """Register safe, token-authenticated operator endpoints on the existing dashboard."""
    bp = Blueprint("codemind_ops", __name__)

    @bp.before_request
    def require_operator() -> None:
        if request.remote_addr not in ("127.0.0.1", "::1"):
            abort(403)
        expected = os.getenv("CODEMIND_DASHBOARD_TOKEN", "")
        provided = request.headers.get("Authorization", "")
        if len(expected) < 32 or not hmac.compare_digest(provided, "Bearer " + expected):
            abort(401)

    @bp.after_request
    def secure(response: Any) -> Any:
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    def project_info() -> tuple[Any, dict[str, Any]]:
        try:
            project = agent.get_active_project()
            if project is None:
                return None, {"name": None, "state": "not_activated", "languages": []}
            return project, {
                "name": str(project.project_name),
                "state": "activated",
                "languages": [x.get_key() for x in project.project_config.language_servers],
            }
        except Exception:
            return None, {"name": None, "state": "unverified", "languages": []}

    def inspect_skills(project: Any) -> dict[str, Any]:
        if project is None:
            return {"state": "no_project", "items": []}
        try:
            directory = Path(project.project_root) / ".codemind" / "skills"
            items = SkillManifestRegistry(directory).list_skills()
            # Do not send instruction bodies or local filesystem details to the browser.
            return {"state": "available", "items": [
                {"id": skill["id"], "description": skill["description"], "version": skill["version"]}
                for skill in items
            ]}
        except (ValueError, TypeError, OSError):
            return {"state": "validation_failed", "items": []}

    def inspect_learning() -> dict[str, Any]:
        try:
            guard = FailureGuard()
            with sqlite3.connect(guard._db_path, timeout=2) as db:
                incidents, blocked = db.execute(
                    "SELECT COUNT(*), COALESCE(SUM(CASE WHEN consecutive >= 2 THEN 1 ELSE 0 END), 0) FROM attempts"
                ).fetchone()
            return {"state": "available", "tracked_strategies": incidents, "blocked_strategies": blocked}
        except (sqlite3.Error, OSError, ValueError):
            return {"state": "unavailable", "tracked_strategies": None, "blocked_strategies": None}

    def inspect_tasks() -> dict[str, Any]:
        try:
            items = []
            for task in list(agent.get_current_tasks())[:80]:
                items.append({
                    "id": task.task_id, "name": str(task.name)[:120],
                    "running": bool(task.is_running),
                    "finished_successfully": bool(task.finished_successfully()),
                })
            return {"state": "available", "items": items}
        except Exception:
            return {"state": "unavailable", "items": []}

    def inspect_commander() -> dict[str, Any]:
        processes = []
        try:
            for proc in psutil.process_iter(attrs=["pid", "name"]):
                if str(proc.info.get("name") or "").lower() == "windowscommander.mcpserver.exe":
                    processes.append({"pid": proc.info["pid"]})
        except (OSError, psutil.Error):
            pass
        result: dict[str, Any] = {
            "processes": processes, "peer_status": "not_configured", "authenticated": False,
            "ready": False, "process_is_health_proof": False,
        }
        url, token = os.getenv("CODEMIND_COMMANDER_HEALTH_URL"), os.getenv("CODEMIND_COMMANDER_HEALTH_TOKEN")
        if url and token:
            try:
                observation = CommanderHealthProbe(url, token).check()
                result.update(peer_status=observation.reason, authenticated=observation.authenticated, ready=observation.ready)
            except (ValueError, OSError):
                result["peer_status"] = "invalid_configuration"
        elif url or token:
            result["peer_status"] = "incomplete_configuration"
        return result

    @bp.get("/overview")
    def overview() -> Any:
        project, project_status = project_info()
        try:
            active_names = list(agent.get_active_tool_names())
        except Exception:
            active_names = []
        try:
            mode = agent.get_context().name
        except Exception:
            mode = "unverified"
        try:
            version = str(agent.version)
        except Exception:
            version = "unverified"
        try:
            stats = tool_usage_stats.get_tool_stats_dict() if tool_usage_stats else {}
        except Exception:
            stats = {}
        payload = {
            "schema": 1, "application": "CODEMIND Serena", "serena_version": version,
            "context": mode, "project": project_status,
            "tools": {"registered_count": len(tool_names), "active_count": len(active_names), "active": sorted(active_names)},
            "skills": inspect_skills(project), "learning": inspect_learning(),
            "tasks": inspect_tasks(), "commander": inspect_commander(),
            "usage": {"state": "available" if tool_usage_stats else "not_configured", "stats": stats},
            "tunnel": {
                "id": os.getenv("CODEMIND_TUNNEL_ID") or None,
                "state": "configured_unverified" if os.getenv("CODEMIND_TUNNEL_ID") else "not_configured",
                "connection_verified": False,
            },
            "integrations": {
                "nmbv_bot": "not_verified",
                "supervisor": "not_verified",
                "client_connection": "not_verified",
            },
            "security": {"operator_authenticated": True, "write_actions_enabled": False},
        }
        return jsonify(payload)

    app.register_blueprint(bp, url_prefix="/codemind/api")

    @app.get("/codemind/")
    def codemind_console() -> Any:
        return redirect("/dashboard/codemind/index.html", code=302)
