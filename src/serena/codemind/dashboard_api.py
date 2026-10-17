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
from flask import Blueprint, abort, jsonify, redirect, request

from serena.codemind.futures import preview_actions
from serena.codemind.health import CommanderHealthProbe
from serena.codemind.learning import FailureGuard
from serena.codemind.methods import MethodCatalogError, load_method_catalog, recommend_method_references
from serena.codemind.modules import SkillManifestRegistry
from serena.codemind.planner import SkillRouter
from serena.codemind.read_model import build_v2_overview
from serena.codemind.tunnel_control import TunnelControlError
from serena.codemind.tunnel_control import controller as tunnel_controller


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
            return {
                "state": "available",
                "items": [{"id": skill["id"], "description": skill["description"], "version": skill["version"]} for skill in items],
            }
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
                items.append(
                    {
                        "id": task.task_id,
                        "name": str(task.name)[:120],
                        "running": bool(task.is_running),
                        "finished_successfully": bool(task.finished_successfully()),
                    }
                )
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
            "processes": processes,
            "peer_status": "not_configured",
            "authenticated": False,
            "ready": False,
            "process_is_health_proof": False,
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

    def require_same_origin() -> None:
        # A bearer token is still required by the blueprint guard.
        # Cross-origin browser POST requests must never mutate tunnel state.
        from urllib.parse import urlsplit

        origin = request.headers.get("Origin", "")
        if origin:
            parts = urlsplit(origin)
            if parts.scheme != "http" or parts.netloc != request.host:
                abort(403)
        if request.headers.get("Sec-Fetch-Site", "same-origin") not in ("same-origin", "none"):
            abort(403)
        if request.content_length is not None and request.content_length > 1024:
            abort(413)

    @bp.get("/tunnel/status")
    def tunnel_status() -> Any:
        return jsonify(tunnel_controller.status())

    @bp.post("/tunnel/key")
    def tunnel_set_key() -> Any:
        require_same_origin()
        body = request.get_json(silent=True)
        if not isinstance(body, dict) or set(body) != {"api_key"}:
            abort(400)
        try:
            tunnel_controller.save_key(body["api_key"])
        except TunnelControlError as exc:
            return jsonify({"ok": False, "error": str(exc)}), 400
        return jsonify({"ok": True, "key_configured": True})

    @bp.delete("/tunnel/key")
    def tunnel_delete_key() -> Any:
        require_same_origin()
        try:
            tunnel_controller.remove_key()
        except TunnelControlError as exc:
            return jsonify({"ok": False, "error": str(exc)}), 409
        return jsonify({"ok": True, "key_configured": False})

    @bp.post("/tunnel/doctor")
    def tunnel_doctor() -> Any:
        require_same_origin()
        try:
            result = tunnel_controller.doctor()
        except TunnelControlError as exc:
            return jsonify({"passed": False, "message": str(exc)}), 409
        return jsonify(result), 200 if result["passed"] else 409

    @bp.post("/tunnel/start")
    def tunnel_start() -> Any:
        require_same_origin()
        try:
            status = tunnel_controller.start()
        except TunnelControlError as exc:
            return jsonify({"ok": False, "error": str(exc)}), 409
        return jsonify({"ok": True, "tunnel": status}), 200

    @bp.post("/tunnel/stop")
    def tunnel_stop() -> Any:
        require_same_origin()
        try:
            status = tunnel_controller.stop()
        except TunnelControlError as exc:
            return jsonify({"ok": False, "error": str(exc)}), 409
        return jsonify({"ok": True, "tunnel": status}), 200

    def collect_overview() -> dict[str, Any]:
        project, project_status = project_info()
        try:
            active_names = list(agent.get_active_tool_names())
            tools_state = "available"
        except Exception:
            active_names = []
            tools_state = "unavailable"
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
        tunnel_status = tunnel_controller.status()
        payload = {
            "schema": 1,
            "application": "CODEMIND Serena",
            "serena_version": version,
            "context": mode,
            "project": project_status,
            "tools": {
                "state": tools_state,
                "registered_count": len(tool_names),
                "active_count": len(active_names) if tools_state == "available" else None,
                "active": sorted(active_names),
            },
            "skills": inspect_skills(project),
            "learning": inspect_learning(),
            "tasks": inspect_tasks(),
            "commander": inspect_commander(),
            "usage": {"state": "available" if tool_usage_stats else "not_configured", "stats": stats},
            "tunnel": {
                "id": os.getenv("CODEMIND_TUNNEL_ID") or tunnel_status["id"],
                "state": "client_ready_unverified" if tunnel_status["client_ready"] else "configured_unverified",
                "connection_verified": False,
                "key_configured": tunnel_status["key_configured"],
                "managed_process_running": tunnel_status["managed_process_running"],
                "client_ready": tunnel_status["client_ready"],
                "health": tunnel_status["health"],
                "profile": tunnel_status["profile"],
            },
            "integrations": {
                "nmbv_bot": "not_verified",
                "supervisor": "not_verified",
                "client_connection": "not_verified",
            },
            "security": {"operator_authenticated": True, "write_actions_enabled": False, "tunnel_settings_enabled": True},
        }
        return payload

    @bp.get("/overview")
    def overview() -> Any:
        return jsonify(collect_overview())

    @bp.get("/v2/overview")
    def overview_v2() -> Any:
        return jsonify(build_v2_overview(collect_overview()))

    @bp.get("/v2/capabilities")
    def capabilities_v2() -> Any:
        current = build_v2_overview(collect_overview())
        return jsonify(
            {
                "schema": 2,
                "observed_at": current["observed_at"],
                "source": current["source"],
                "capabilities": current["capabilities"],
            }
        )

    @bp.post("/v2/skills/route")
    def route_skills_v2() -> Any:
        require_same_origin()
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict) or set(payload) != {"request_text"}:
            abort(400)
        task = payload["request_text"]
        if not isinstance(task, str) or not (3 <= len(task.strip()) <= 1000):
            abort(400)
        project, project_status = project_info()
        if project is None:
            return jsonify(
                {"schema": 2, "state": "NO_ACTIVE_PROJECT", "selected": [], "loaded": [], "executed": [], "authorization_granted": False}
            ), 409
        try:
            registry = SkillManifestRegistry(Path(project.project_root) / ".codemind" / "skills")
            routed = SkillRouter(registry).route(task)
            suggestions = recommend_method_references(task)["selected_references"]
        except (OSError, ValueError, TypeError, MethodCatalogError):
            return jsonify(
                {
                    "schema": 2,
                    "state": "SKILL_VALIDATION_FAILED",
                    "selected": [],
                    "loaded": [],
                    "executed": [],
                    "authorization_granted": False,
                }
            ), 422
        return jsonify(
            {
                "schema": 2,
                "state": "ROUTED",
                "project": project_status["name"],
                "mode": routed["mode"],
                "selected": routed["selected"],
                "reference_suggestions": suggestions,
                "loaded": [],
                "executed": [],
                "authorization_granted": False,
            }
        )

    @bp.get("/v2/methods")
    def methods_v2() -> Any:
        """Reference catalog; these methods are NOT installed or executing workers."""
        try:
            return jsonify(load_method_catalog())
        except MethodCatalogError:
            return jsonify({"schema": 2, "state": "UNAVAILABLE", "count": None, "methods": []}), 503

    @bp.get("/v2/actions/next")
    def next_action_v2() -> Any:
        # Serena's dashboard is not a task-authorization service. The
        # active project alone cannot prove a bound task/owning actor.
        return jsonify(
            {
                "schema": 2,
                "state": "TASK_SESSION_UNBOUND",
                "canonical": None,
                "authorization_granted": False,
                "reason": "Bind an actual host task and verified owner before canonical execution",
            }
        ), 409

    @bp.post("/v2/actions/preview")
    def preview_actions_v2() -> Any:
        """Deterministic non-executable advisory forecast for a scoped request."""
        require_same_origin()
        body = request.get_json(silent=True)
        if not isinstance(body, dict) or set(body) != {"request_text"}:
            abort(400)
        task = body["request_text"]
        if not isinstance(task, str) or not (3 <= len(task.strip()) <= 1000):
            abort(400)
        project, project_status = project_info()
        # Do not infer a task/session binding from an activated project.
        result = preview_actions(task, project_name=project_status["name"] if project is not None else None)
        return jsonify(result)

    app.register_blueprint(bp, url_prefix="/codemind/api")

    @app.get("/codemind/")
    def codemind_console() -> Any:
        return redirect("/dashboard/codemind/index.html", code=302)
