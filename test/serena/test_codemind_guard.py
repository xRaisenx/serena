# SPDX-License-Identifier: GPL-3.0-or-later
"""Behavior-based tests for CODEMIND persistent loop prevention."""

import importlib.util
import json
from pathlib import Path

import pytest


def _load_module(name: str):
    source = Path(__file__).resolve().parents[2] / "src" / "serena" / "codemind" / (name + ".py")
    spec = importlib.util.spec_from_file_location("codemind_test_" + name, source)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_learning = _load_module("learning")
_modules = _load_module("modules")
FailureGuard = _learning.FailureGuard
StrategyChangeRequired = _learning.StrategyChangeRequired
SkillManifestRegistry = _modules.SkillManifestRegistry


def test_two_equivalent_failures_block_third_even_after_restart(tmp_path: Path):
    db = tmp_path / "state.db"
    first = FailureGuard(db)
    for attempt in range(2):
        first.check(str(tmp_path), "find_symbol", {"name_path": "Foo"})
        assert (
            first.failure(
                str(tmp_path),
                "find_symbol",
                {"name_path": "Foo"},
                ValueError("Missing 123"),
            )
            == attempt + 1
        )
    second = FailureGuard(db)
    with pytest.raises(StrategyChangeRequired):
        second.check(str(tmp_path), "find_symbol", {"name_path": "Foo"})


def test_changed_strategy_remains_permitted(tmp_path: Path):
    guard = FailureGuard(tmp_path / "state.db")
    for _ in range(2):
        guard.failure(str(tmp_path), "find_symbol", {"name_path": "Foo"}, ValueError("missing"))
    guard.check(str(tmp_path), "get_symbols_overview", {"relative_path": "x.py"})
    guard.check(str(tmp_path), "find_symbol", {"name_path": "Bar"})


def test_success_resets_strategy(tmp_path: Path):
    guard = FailureGuard(tmp_path / "state.db")
    for _ in range(2):
        guard.failure(str(tmp_path), "find_symbol", {"name_path": "Foo"}, ValueError("missing"))
    guard.success(str(tmp_path), "find_symbol", {"name_path": "Foo"})
    guard.check(str(tmp_path), "find_symbol", {"name_path": "Foo"})


def test_different_error_resets_equivalence_count(tmp_path: Path):
    guard = FailureGuard(tmp_path / "state.db")
    for _ in range(2):
        guard.failure(str(tmp_path), "find_symbol", {"name_path": "Foo"}, ValueError("bad"))
    guard.failure(str(tmp_path), "find_symbol", {"name_path": "Foo"}, RuntimeError("different"))
    assert guard.status(str(tmp_path), "find_symbol", {"name_path": "Foo"})["consecutive_failures"] == 1


def test_skill_manifests_reload_without_recompiling(tmp_path: Path):
    folder = tmp_path / "skills"
    folder.mkdir()
    registry = SkillManifestRegistry(folder)
    assert registry.list_skills() == []
    sample = {
        "id": "debugging",
        "version": "1",
        "description": "Review evidence",
        "instructions": "Reproduce and isolate.",
        "enabled": True,
    }
    (folder / "debugging.json").write_text(json.dumps(sample), encoding="utf-8")
    assert registry.list_skills()[0]["id"] == "debugging"
    sample["enabled"] = False
    (folder / "debugging.json").write_text(json.dumps(sample), encoding="utf-8")
    assert registry.list_skills() == []


def test_invalid_manifests_fail_closed(tmp_path: Path):
    folder = tmp_path / "skills"
    folder.mkdir()
    (folder / "bad.json").write_text('{"id":"bad"}', encoding="utf-8")
    with pytest.raises(ValueError):
        SkillManifestRegistry(folder).list_skills()


def test_routing_matches_manifest_metadata(tmp_path: Path):
    planner = _load_module("planner")
    folder = tmp_path / "skills"
    folder.mkdir()
    manifest = {
        "id": "debugging",
        "version": "1",
        "description": "Inspect a debugging failure",
        "instructions": "Use source evidence.",
        "enabled": True,
    }
    (folder / "debugging.json").write_text(json.dumps(manifest), encoding="utf-8")
    result = planner.SkillRouter(SkillManifestRegistry(folder)).route("debugging failure")
    assert result["selected"][0]["skill_id"] == "debugging"
    assert result["authorization_granted"] is False


def test_next_action_changes_strategy_without_authorizing(tmp_path: Path):
    planner = _load_module("planner")
    guard = FailureGuard(tmp_path / "guard.db")
    action = planner.NextActionPlanner(guard)
    target = {"name_path": "Foo"}
    assert action.recommend(str(tmp_path), "find_symbol", target)["action"] == "INSPECT_CURRENT_EVIDENCE"
    for _ in range(2):
        guard.failure(str(tmp_path), "find_symbol", target, ValueError("absent"))
    result = action.recommend(str(tmp_path), "find_symbol", target)
    assert result["action"] == "CHANGE_STRATEGY"
    assert result["authorization_granted"] is False
    assert result["blocked_same_call"] is True
