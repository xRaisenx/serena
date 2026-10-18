# SPDX-License-Identifier: GPL-3.0-or-later
"""Real CODEMIND v2 read-model and advisory route regression contracts."""

from __future__ import annotations

import json

import pytest
from flask import Flask

from serena.codemind.dashboard_api import register_codemind_routes
from serena.codemind.modules import SkillManifestRegistry
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

    def __init__(self, project=None, broken_tools=False, semantic_tool=None):
        self.project = project
        self.broken_tools = broken_tools
        self.semantic_tool = semantic_tool

    def get_tool_by_name(self, name):
        if self.semantic_tool is None:
            raise AssertionError("Unexpected semantic tool invocation")
        assert name == "find_symbol"
        return self.semantic_tool

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
    assert result["metrics"] == {"active_tools": None, "enabled_skills": None, "tracked_failures": None, "blocked_loops": None}
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
    assert data["capabilities"]["fu_20_candidate_horizon"] == "AVAILABLE_ADVISORY"
    assert data["capabilities"]["method_reference_catalog"] == "AVAILABLE_REFERENCE_ONLY"
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
    (skills / "debug.json").write_text(
        json.dumps(
            {
                "id": "deterministic-debugging",
                "version": "1",
                "description": "reproduce and debug errors",
                "instructions": "Inspect source",
                "enabled": True,
            }
        ),
        encoding="utf-8",
    )
    client = build_client(monkeypatch, FakeAgent(FakeProject(tmp_path)))
    response = client.post(
        "/codemind/api/v2/skills/route", headers={**_TOKEN, "Origin": "http://localhost"}, json={"request_text": "debug recurring errors"}
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["state"] == "ROUTED"
    assert payload["selected"][0]["skill_id"] == "deterministic-debugging"
    assert payload["loaded"] == ["deterministic-debugging"]
    assert payload["skill_playbooks"] == [{"skill_id": "deterministic-debugging", "instructions": "Inspect source"}]
    assert payload["executed"] == []
    assert payload["authorization_granted"] is False


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"request_text": ""},
        {"request_text": 32},
        {"request_text": "aa"},
        {"request_text": "a" * 1001},
        {"request_text": "debug", "grant": True},
    ],
)
def test_invalid_route_payload_rejected(client, payload):
    response = client.post("/codemind/api/v2/skills/route", headers=_TOKEN, json=payload)
    assert response.status_code in (400, 413)


def test_cross_origin_cannot_route(client):
    response = client.post(
        "/codemind/api/v2/skills/route",
        headers={**_TOKEN, "Origin": "https://attacker.example"},
        json={"request_text": "debug recurring errors"},
    )
    assert response.status_code == 403


def test_routed_skill_method_runs_bounded_serena_symbol_lookup(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "runtime"))
    skills = tmp_path / ".codemind" / "skills"
    skills.mkdir(parents=True)
    (skills / "debug.json").write_text(
        json.dumps(
            {
                "id": "deterministic-debugging",
                "version": "1",
                "description": "reproduce and debug errors",
                "instructions": "Inspect source, form a falsifier, and test it",
                "enabled": True,
            }
        ),
        encoding="utf-8",
    )
    source = tmp_path / "src" / "domain"
    source.mkdir(parents=True)
    (source / "planner.py").write_text("class Planner: pass\n", encoding="utf-8")
    observed = []

    class FakeSymbolTool:
        def apply(self, **kwargs):
            observed.append(kwargs)
            return json.dumps(
                [
                    {
                        "name_path": "Planner",
                        "relative_path": "src/domain/planner.py",
                        "body_location": {"start_line": 0, "end_line": 0},
                    }
                ]
            )

    agent = FakeAgent(FakeProject(tmp_path), semantic_tool=FakeSymbolTool())
    client = build_client(monkeypatch, agent)
    result = client.post(
        "/codemind/api/v2/skills/inspect",
        headers=_TOKEN,
        json={
            "request_text": "debug recurring errors",
            "relative_path": "src/domain/planner.py",
            "symbol": "Planner",
        },
    )
    assert result.status_code == 200
    payload = result.get_json()
    assert payload["state"] == "INSPECTED"
    assert payload["loaded"][0]["instructions"] == "Inspect source, form a falsifier, and test it"
    assert payload["symbols"][0]["name_path"] == "Planner"
    assert payload["executed"] == [{"tool": "find_symbol", "mode": "READ_ONLY", "path": "src/domain/planner.py", "symbol": "Planner"}]
    assert payload["authorization_granted"] is False
    assert payload["noetic_fleet"] == "NOT_RUNNING"
    assert observed == [
        {
            "name_path_pattern": "Planner",
            "relative_path": "src/domain/planner.py",
            "include_body": False,
            "max_matches": 10,
            "max_answer_chars": 4500,
        }
    ]
    for path in ("../secret.py", "src/../secret.py", ".codemind/skills/debug.json"):
        denied = client.post(
            "/codemind/api/v2/skills/inspect",
            headers=_TOKEN,
            json={"request_text": "debug recurring errors", "relative_path": path, "symbol": "Planner"},
        )
        assert denied.status_code == 400
    assert len(observed) == 1


@pytest.mark.parametrize("endpoint", ["route", "inspect"])
def test_skill_route_remains_coherent_if_registry_changes_mid_request(monkeypatch, tmp_path, endpoint):
    """Both the router and its instructions must come from the same snapshot."""
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "runtime"))
    source_dir = tmp_path / "src" / "serena"
    source_dir.mkdir(parents=True)
    (source_dir / "planner.py").write_text("class Planner: pass\n", encoding="utf-8")
    skill = {
        "id": "deterministic-debugging",
        "version": "1",
        "description": "debug regression",
        "instructions": "Inspect evidence and test the regression",
        "enabled": True,
    }
    reads = []

    def changing_registry(self):
        reads.append(1)
        return [skill] if len(reads) == 1 else []

    class FakeSymbolTool:
        def apply(self, **kwargs):
            return json.dumps([{"name_path": "Planner", "relative_path": "src/serena/planner.py"}])

    monkeypatch.setattr(SkillManifestRegistry, "list_skills", changing_registry)
    client = build_client(monkeypatch, FakeAgent(FakeProject(tmp_path), semantic_tool=FakeSymbolTool()))
    payload = {"request_text": "debug regression"}
    if endpoint == "inspect":
        payload.update({"relative_path": "src/serena/planner.py", "symbol": "Planner"})
    response = client.post("/codemind/api/v2/skills/" + endpoint, headers=_TOKEN, json=payload)
    assert response.status_code == 200
    result = response.get_json()
    assert result["state"] == ("INSPECTED" if endpoint == "inspect" else "ROUTED")
    if endpoint == "route":
        assert result["loaded"] == [skill["id"]]
        assert result["skill_playbooks"][0]["instructions"] == skill["instructions"]
        assert result["executed"] == []
    else:
        assert result["loaded"][0]["instructions"] == skill["instructions"]
        assert result["executed"][0]["tool"] == "find_symbol"
        assert result["symbols"][0]["name_path"] == "Planner"
    assert reads


def test_project_without_skills_cannot_start_semantic_fleet(monkeypatch, tmp_path):
    agent = FakeAgent(FakeProject(tmp_path))
    client = build_client(monkeypatch, agent)
    response = client.post("/codemind/api/v2/skills/route", headers=_TOKEN, json={"request_text": "debug recurring errors"})
    assert response.status_code == 409
    assert response.get_json()["state"] == "NO_MATCHING_SKILL"
    assert response.get_json()["loaded"] == []


def test_v1_overview_schema_unchanged(client):
    payload = client.get("/codemind/api/overview", headers=_TOKEN).get_json()
    assert payload["schema"] == 1
    assert payload["application"] == "CODEMIND Serena"
    assert payload["tools"]["active_count"] == 2
