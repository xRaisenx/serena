# SPDX-License-Identifier: GPL-3.0-or-later
"""Authorization, response and read-only contract for the CODEMIND console."""

from __future__ import annotations

from pathlib import Path

import pytest
from flask import Flask

from serena.codemind.dashboard_api import register_codemind_routes


class DummyContext:
    name = "codemind-test"


class DummyAgent:
    version = "2.0-test"

    def get_active_project(self):
        return None

    def get_context(self):
        return DummyContext()

    def get_active_tool_names(self):
        return ["find_symbol", "codemind_list_skills"]

    def get_current_tasks(self):
        return []


@pytest.fixture
def console(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setenv("CODEMIND_DASHBOARD_TOKEN", "c" * 40)
    monkeypatch.delenv("CODEMIND_COMMANDER_HEALTH_URL", raising=False)
    monkeypatch.delenv("CODEMIND_COMMANDER_HEALTH_TOKEN", raising=False)
    monkeypatch.delenv("CODEMIND_TUNNEL_ID", raising=False)
    app = Flask(__name__)
    app.testing = True
    register_codemind_routes(app, DummyAgent(), ["find_symbol", "codemind_list_skills"])
    return app.test_client()


def test_denies_anonymous_request(console):
    assert console.get("/codemind/api/overview").status_code == 401


def test_denies_wrong_token(console):
    assert console.get("/codemind/api/overview", headers={"Authorization": "Bearer " + "w" * 40}).status_code == 401


def test_denies_remote_clients(console):
    response = console.get(
        "/codemind/api/overview",
        headers={"Authorization": "Bearer " + "c" * 40},
        environ_overrides={"REMOTE_ADDR": "203.0.113.10"},
    )
    assert response.status_code == 403


def test_denies_when_token_not_configured(console, monkeypatch):
    monkeypatch.delenv("CODEMIND_DASHBOARD_TOKEN")
    assert console.get("/codemind/api/overview", headers={"Authorization": "Bearer " + "c" * 40}).status_code == 401


def test_authenticated_snapshot_does_not_claim_tunnel_or_watchdog_health(console):
    response = console.get("/codemind/api/overview", headers={"Authorization": "Bearer " + "c" * 40})
    assert response.status_code == 200
    data = response.get_json()
    assert data["schema"] == 1
    assert data["tools"]["active_count"] == 2
    assert data["learning"]["tracked_strategies"] == 0
    assert data["commander"]["ready"] is False
    assert data["commander"]["peer_status"] == "not_configured"
    assert data["tunnel"]["connection_verified"] is False
    assert data["integrations"]["supervisor"] == "not_verified"
    assert data["security"]["write_actions_enabled"] is False
    assert response.headers["Cache-Control"] == "no-store"
    assert "c" * 40 not in response.get_data(as_text=True)


def test_tunnel_id_only_means_configured_not_ready(console, monkeypatch):
    monkeypatch.setenv("CODEMIND_TUNNEL_ID", "tunnel_test_example")
    data = console.get("/codemind/api/overview", headers={"Authorization": "Bearer " + "c" * 40}).get_json()
    assert data["tunnel"]["id"] == "tunnel_test_example"
    assert data["tunnel"]["connection_verified"] is False


def test_no_mutating_dashboard_api_routes(console):
    response = console.post("/codemind/api/overview", headers={"Authorization": "Bearer " + "c" * 40})
    assert response.status_code == 405


def test_static_console_artifacts_present():
    root = Path(__file__).resolve().parents[2] / "src" / "serena" / "resources" / "dashboard" / "codemind"
    assert all((root / name).is_file() for name in ("index.html", "console.js", "console.css"))
    html = (root / "index.html").read_text(encoding="utf-8")
    assert "https://cdn.jsdelivr.net" not in html
    assert "operator-token" in html
    assert 'data-page="security"' in html
