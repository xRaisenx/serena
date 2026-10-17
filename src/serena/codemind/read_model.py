# SPDX-License-Identifier: GPL-3.0-or-later
"""CODEMIND v2 read model. No state mutation and no inferred acceptance."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


def build_v2_overview(v1: dict[str, Any], *, observed_at: str | None = None) -> dict[str, Any]:
    """Normalize observed v1 facts into an explicitly unverified v2 model.

    Snapshot timestamp means HTTP observation time, not deployment attestation.
    A listening peer, running process or local tunnel readiness is never a
    substitute for an authenticated end-to-end consumer tool call.
    """
    when = observed_at or datetime.now(UTC).isoformat().replace("+00:00", "Z")
    tools = v1.get("tools") or {}
    skills = v1.get("skills") or {}
    learning = v1.get("learning") or {}
    commander = v1.get("commander") or {}
    tunnel = v1.get("tunnel") or {}
    project = v1.get("project") or {}

    def integer_or_none(value: Any) -> int | None:
        return value if type(value) is int and value >= 0 else None

    active_count = integer_or_none(tools.get("active_count")) if tools.get("state") != "unavailable" else None
    skill_count = len(skills.get("items")) if skills.get("state") == "available" and isinstance(skills.get("items"), list) else None
    return {
        "schema": 2,
        "application": "CODEMIND Serena",
        "observed_at": when,
        "source": {
            "engine": "Serena MCP",
            "engine_version_reported": v1.get("serena_version"),
            "revision": None,
            "revision_attested": False,
            "installed_build_parity": "UNVERIFIED",
        },
        "workspace": {
            "name": project.get("name"),
            "state": project.get("state", "unverified"),
            "languages": project.get("languages") or [],
        },
        "metrics": {
            "active_tools": active_count,
            "enabled_skills": skill_count,
            "tracked_failures": integer_or_none(learning.get("tracked_strategies")),
            "blocked_loops": integer_or_none(learning.get("blocked_strategies")),
        },
        "services": {
            "serena": {
                "state": "REPORTING",
                "evidence": "authenticated_dashboard_response",
                "mcp_roundtrip": "UNVERIFIED",
            },
            "commander": {
                "state": "VERIFIED_PEER" if commander.get("ready") is True and commander.get("authenticated") is True else "UNVERIFIED",
                "processes_seen": len(commander.get("processes") or []),
                "authenticated": commander.get("authenticated") is True,
                "ready": commander.get("ready") is True,
                "reason": commander.get("peer_status", "not_reported"),
            },
            "tunnel": {
                "state": "CLIENT_READY" if tunnel.get("client_ready") is True else "UNVERIFIED",
                "client_ready": tunnel.get("client_ready") is True,
                "remote_tool_call_verified": tunnel.get("connection_verified") is True,
                "key_configured": tunnel.get("key_configured") is True,
                "reason": tunnel.get("health", "not_reported"),
            },
        },
        "capabilities": {
            "skill_router": "AVAILABLE" if skills.get("state") == "available" else "UNVERIFIED",
            "native_learning_promotion": "NOT_IMPLEMENTED",
            "fu_20_candidate_horizon": "NOT_IMPLEMENTED",
            "commander_dual_watchdog": "UNVERIFIED",
            "codemind_100_expert_runtime": "NOT_IMPLEMENTED",
            "chatgpt_remote_acceptance": "VERIFIED" if tunnel.get("connection_verified") is True else "UNVERIFIED",
        },
    }
