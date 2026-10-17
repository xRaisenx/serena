# SPDX-License-Identifier: GPL-3.0-or-later
"""CODEMIND 25-method reference catalog and advisory next-action API contract."""

from __future__ import annotations

import json

import pytest
from flask import Flask

from serena.codemind.dashboard_api import register_codemind_routes
from serena.codemind.futures import classify_intent, preview_actions
from serena.codemind.methods import load_method_catalog, recommend_method_references

_AUTH = {"Authorization": "Bearer " + "f" * 40}


class FakeContext:
    name = "desktop-app"


class FakeAgent:
    version = "2.0-test"

    def get_context(self):
        return FakeContext()

    def get_active_project(self):
        return None

    def get_active_tool_names(self):
        return ["find_symbol", "codemind_skill_route"]

    def get_current_tasks(self):
        return []


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("CODEMIND_DASHBOARD_TOKEN", "f" * 40)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    app = Flask(__name__)
    app.testing = True
    register_codemind_routes(app, FakeAgent(), ["find_symbol"])
    return app.test_client()


def test_catalog_is_complete_and_reference_only():
    data = load_method_catalog()
    assert data["schema"] == 2
    assert data["count"] == 25
    assert data["installed_count"] == 0
    assert data["executed_count"] == 0
    assert len({x["id"] for x in data["methods"]}) == 25
    assert all(x["id"].startswith("codemind-") for x in data["methods"])
    assert all(x["state"] == "REFERENCE_ONLY" and x["loaded"] is False and x["executed"] is False for x in data["methods"])


def test_catalog_authentication(client):
    assert client.get("/codemind/api/v2/methods").status_code == 401
    res = client.get("/codemind/api/v2/methods", headers=_AUTH)
    assert res.status_code == 200
    assert res.get_json()["count"] == 25
    assert res.get_json()["installed_count"] == 0
    assert res.headers["Cache-Control"] == "no-store"


@pytest.mark.parametrize(
    ("text", "kind"),
    [
        ("debug recurring Python errors", "debug"),
        ("audit repository dependencies", "review"),
        ("implement new route", "implement"),
        ("verify regression suite", "validate"),
        ("examine components", "inspect"),
    ],
)
def test_intent_classification(text, kind):
    assert classify_intent(text) == kind


@pytest.mark.parametrize("text", ["", " ", "xx", "a" * 1001, None, 42])
def test_bad_request_not_classified(text):
    with pytest.raises(ValueError):
        classify_intent(text)


def test_preview_is_bounded_and_does_not_grant_permission():
    data = preview_actions("debug recurring Python crashes", project_name="project")
    assert data["schema"] == 2
    assert data["state"] == "ADVISORY_ONLY"
    assert data["canonical"]["authorized"] is False
    assert data["task_binding"] == "UNBOUND"
    assert len(data["preview"]) <= 5
    assert len(data["fu_candidates"]) <= 20
    assert len({x["action"] for x in data["fu_candidates"]}) == len(data["fu_candidates"])
    assert all(x["executable"] is False and x["authorized_by_forecast"] is False for x in data["fu_candidates"])
    assert data["authorization_granted"] is False


def test_repeated_failures_require_change():
    data = preview_actions("fix failed startup", project_name="repo", same_strategy_failures=2)
    assert data["canonical"]["action"] == "CHANGE_STRATEGY"
    assert data["blocker"] == "REPEATED_EQUIVALENT_FAILURE"


def test_no_project_never_infers_owner():
    data = preview_actions("repair code", project_name=None)
    assert data["canonical"]["action"] == "ACTIVATE_PROJECT"
    assert data["authorization_granted"] is False


@pytest.mark.parametrize("count", [-1, 101, 1.3, True])
def test_failure_count_must_be_valid(count):
    with pytest.raises(ValueError):
        preview_actions("repair code", project_name="repo", same_strategy_failures=count)


def test_no_authenticated_canonical_authority(client):
    result = client.get("/codemind/api/v2/actions/next", headers=_AUTH)
    assert result.status_code == 409
    assert result.get_json()["authorization_granted"] is False


def test_preview_requires_auth_and_same_origin(client):
    uri = "/codemind/api/v2/actions/preview"
    payload = {"request_text": "fix recurring error"}
    assert client.post(uri, json=payload).status_code == 401
    assert client.post(uri, headers={**_AUTH, "Origin": "https://malicious.example"}, json=payload).status_code == 403
    valid = client.post(uri, headers={**_AUTH, "Origin": "http://localhost"}, json=payload)
    assert valid.status_code == 200
    result = valid.get_json()
    assert result["canonical"]["authorized"] is False
    assert result["authorization_granted"] is False
    assert result["task_binding"] == "UNBOUND"


@pytest.mark.parametrize(
    "data",
    [
        {},
        {"request_text": "a"},
        {"request_text": "fix bug", "authority": True},
        {"request_text": None},
        {"request_text": "b" * 1001},
    ],
)
def test_preview_rejects_unexpected_payloads(client, data):
    r = client.post("/codemind/api/v2/actions/preview", headers=_AUTH, json=data)
    assert r.status_code in (400, 413)


def test_source_revision_not_attested_by_preview():
    x = preview_actions("review repository", project_name="repo", observed_revision="a" * 40)
    assert x["source_revision_attested"] is False


def test_preview_does_not_echo_user_prompt_or_secrets(client):
    req = "debug sk-proj-" + ("t" * 45) + " errors"
    r = client.post("/codemind/api/v2/actions/preview", headers=_AUTH, json={"request_text": req})
    assert r.status_code == 200
    assert "sk-proj-" not in json.dumps(r.get_json())


def test_post_cannot_mutate_method_catalog(client):
    assert client.post("/codemind/api/v2/methods", headers=_AUTH, json={}).status_code == 405


def test_recommendation_across_25_reference_methods():
    data = recommend_method_references("deterministic debugging of recurring failures")
    assert data["schema"] == 2
    assert data["state"] == "REFERENCE_SELECTION_ONLY"
    assert data["authorization_granted"] is False
    assert data["loaded"] == []
    assert data["executed"] == []
    assert 1 <= len(data["selected_references"]) <= 3
    assert all(x["state"] == "REFERENCE_ONLY" for x in data["selected_references"])
    assert data["selected_references"][0]["id"] == "codemind-deterministic-debugging"


def test_empty_catalog_matches_are_not_invented():
    data = recommend_method_references("xyzzy unknown quux")
    assert data["selected_references"] == []


@pytest.mark.parametrize("text", ["", "x", "a" * 1001, None, 42])
def test_recommendation_rejects_invalid_input(text):
    with pytest.raises(ValueError):
        recommend_method_references(text)


@pytest.mark.parametrize("limit", [0, 6, True, 1.3])
def test_recommendation_rejects_invalid_limit(limit):
    with pytest.raises(ValueError):
        recommend_method_references("debug errors", limit=limit)
