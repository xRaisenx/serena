# SPDX-License-Identifier: GPL-3.0-or-later
"""Shipping CODEMIND project skills are implemented, not only taxonomy references."""

from pathlib import Path

from serena.codemind.methods import load_method_catalog
from serena.codemind.modules import SkillManifestRegistry
from serena.codemind.planner import SkillRouter


def _registry() -> SkillManifestRegistry:
    return SkillManifestRegistry(Path(__file__).resolve().parents[2] / ".codemind" / "skills")


def test_complete_generic_method_pack_has_live_manifests() -> None:
    catalog_ids = {method["id"] for method in load_method_catalog()["methods"]}
    installed = _registry().list_skills()
    installed_ids = {skill["id"] for skill in installed}
    # Preserve Serena's original deterministic-debugging skill for compatibility.
    assert "deterministic-debugging" in installed_ids
    assert catalog_ids <= installed_ids
    assert len(catalog_ids) == 25
    assert len(installed_ids) >= 26
    assert len(installed_ids) == len(installed)


def test_each_manifest_has_actual_bounded_instructions() -> None:
    catalog_ids = {method["id"] for method in load_method_catalog()["methods"]}
    installed = {skill["id"]: skill for skill in _registry().list_skills()}
    for skill_id in catalog_ids:
        skill = installed[skill_id]
        assert skill["enabled"] is True
        assert len(skill["instructions"]) >= 90
        assert len(skill["instructions"]) <= 16000
        assert "selected != loaded != executed" in skill["instructions"]


def test_skill_route_selects_project_skill_without_executing() -> None:
    route = SkillRouter(_registry()).route("neurosymbolic implementation using Serena source symbols")
    assert route["selected"]
    assert route["selected"][0]["skill_id"] == "codemind-neurosymbolic-implementation"
    assert route["authorization_granted"] is False
