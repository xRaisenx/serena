# SPDX-License-Identifier: GPL-3.0-or-later
"""Real CODEMIND v2 read-model and advisory route regression contracts."""
from __future__ import annotations

import json

import pytest
from flask import Flask

from serena.codemind.dashboard_api import register_codemind_routes
from serena.codemind.read_model import build_v2_overview

_TOKEN = {"Authorization": "Bearer " + "a" * 40}


class FakeContext:
    name = "desktop-app"


class FakeConfig:
    language_servers = []


class FakeProject:
    def __init__(self, root):
        self.project_root = root
        self.project_name = "codemind-test"
        self.project_config = FakeConfig()


class FakeAgent:
    version = "2.0-test"

    def __init__(self, project=None, broken_tools=False):
        self.project = project
        self.broken_tools = broken_tools

    def get_active_project(self):
        return self.project

    def get_active_tool_names(self):
        if self.broken_tools:
            raise RuntimeError("Simulated discovery failure")
        return ["find_symbol", "codemind_skill_route"]

    def get_context(self):
        return FakeContext()

    def get_current_tasks(self):
        return []


def build_client(monkeypatch, agent):
    monkeypatch.setenv("CODEMIND_DASHBOARD_TOKEN", "a" * 40)
    monkeypatch.delenv("CODEMIND_COMMANDER_HEALTH_URL", raising=False)
    monkeypatch.delenv("CODEMIND_COMMANDER_HEALTH_TOKEN", raising=False)
    app = Flask(__name__)
    app.testing = True
    register_codemind_routes(app, agent, ["find_symbol", "codemind_skill_route"])
    return app.test_client()


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    return build_client(monkeypatch, FakeAgent())


def test_v2_requires_operator_token(client):
    assert client.get("/codemind/api/v2/overview").status_code == 401
    assert client.get("/codemind/api/v2/capabilities").status_code == 401
    assert client.post("/codemind/api/v2/skills/route", json={"request_text": "review Python"}).status_code == 401


def test_v2_overview_reports_source_identity_unknown(client):
    res = client.get("/codemind/api/v2/overview", headers=_TOKEN)
    assert res.status_code == 200
    data = res.get_json()
    assert data["schema"] == 2
    assert data["source"]["revision"] is None
    assert data["source"]["revision_attested"] is False
    assert data["source"]["installed_build_parity"] == "UNVERIFIED"
    assert data["services"]["commander"]["state"] == "UNVERIFIED"
    assert data["services"]["tunnel"]["remote_tool_call_verified"] is False
    assert data["metrics"]["active_tools"] == 2
    assert data["metrics"]["enabled_skills"] is None
    assert data["observed_at"].endswith("Z")
    assert res.headers["Cache-Control"] == "no-store"


def test_v2_unknown_counts_never_become_zero():
    snapshot = {
        "tools": {"state": "unavailable", "active_count": 0},
        "skills": {"state": "no_project", "items": []},
        "learning": {"state": "unavailable", "tracked_strategies": None, "blocked_strategies": None},
        "commander": {"processes": [{"pid": 123}], "ready": False, "authenticated": False},
        "tunnel": {"client_ready": False, "connection_verified": False},
    }
    result = build_v2_overview(snapshot, observed_at="2026-10-18T00:00:00Z")
    assert result["metrics"] == {
        "active_tools": None, "enabled_skills": None, "tracked_failures": None, "blocked_loops": None
    }
    assert result["services"]["commander"]["processes_seen"] == 1
    assert result["services"]["commander"]["state"] == "UNVERIFIED"


def test_discovery_failure_is_unknown_not_no_tools(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    client = build_client(monkeypatch, FakeAgent(broken_tools=True))
    v1 = client.get("/codemind/api/overview", headers=_TOKEN).get_json()
    v2 = client.get("/codemind/api/v2/overview", headers=_TOKEN).get_json()
    assert v1["tools"]["state"] == "unavailable"
    assert v1["tools"]["active_count"] is None
    assert v2["metrics"]["active_tools"] is None


def test_capabilities_never_mark_fu_or_experts_implemented(client):
    data = client.get("/codemind/api/v2/capabilities", headers=_TOKEN).get_json()
    assert data["schema"] == 2
    assert data["capabilities"]["fu_20_candidate_horizon"] == "NOT_IMPLEMENTED"
    assert data["capabilities"]["codemind_100_expert_runtime"] == "NOT_IMPLEMENTED"
    assert data["capabilities"]["commander_dual_watchdog"] == "UNVERIFIED"


def test_no_active_project_denies_route(client):
    response = client.post("/codemind/api/v2/skills/route", headers=_TOKEN, json={"request_text": "debug source"})
    assert response.status_code == 409
    assert response.get_json()["authorization_granted"] is False


def test_routing_real_project_manifests_and_no_execution(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "runtime"))
    skills = tmp_path / ".codemind" / "skills"
    skills.mkdir(parents=True)
    (skills / "debug.json").write_text(json.dumps({
        "id": "deterministic-debugging", "version": "1",
        "description": "reproduce and debug errors", "instructions": "Inspect source",
        "enabled": True
    }), encoding="utf-8")
    client = build_client(monkeypatch, FakeAgent(FakeProject(tmp_path)))
    response = client.post("/codemind/api/v2/skills/route",
                           headers={**_TOKEN, "Origin": "http://localhost"},
                           json={"request_text": "debug recurring errors"})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["state"] == "ROUTED"
    assert payload["selected"][0]["skill_id"] == "deterministic-debugging"
    assert payload["loaded"] == []
    assert payload["executed"] == []
    assert payload["authorization_granted"] is False


@pytest.mark.parametrize("payload", [{}, {"request_text": ""}, {"request_text": 32},
                                      {"request_text": "aa"}, {"request_text": "a" * 1001},
                                      {"request_text": "debug", "grant": True}])
def test_invalid_route_payload_rejected(client, payload):
    response = client.post("/codemind/api/v2/skills/route", headers=_TOKEN, json=payload)
    assert response.status_code in (400, 413)


def test_cross_origin_cannot_route(client):
    response = client.post("/codemind/api/v2/skills/route",
                           headers={**_TOKEN, "Origin": "https://attacker.example"},
                           json={"request_text": "debug recurring errors"})
    assert response.status_code == 403


def test_v1_overview_schema_unchanged(client):
    payload = client.get("/codemind/api/overview", headers=_TOKEN).get_json()
    assert payload["schema"] == 1
    assert payload["application"] == "CODEMIND Serena"
    assert payload["tools"]["active_count"] == 2
