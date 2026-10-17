# SPDX-License-Identifier: GPL-3.0-or-later
"""Deterministic skill selection and evidence-gated next action hints."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from serena.codemind.learning import FailureGuard
    from serena.codemind.modules import SkillManifestRegistry

_WORD = re.compile(r"[a-z][a-z0-9]*")
_STOP = frozenset(
    {
        "the",
        "and",
        "for",
        "that",
        "with",
        "this",
        "from",
        "your",
        "into",
        "after",
        "before",
    }
)


class SkillRouter:
    """Select applicable declarative skills by transparent metadata matching."""

    def __init__(self, registry: SkillManifestRegistry):
        self.registry = registry

    def route(self, request: str) -> dict[str, Any]:
        if not isinstance(request, str) or not request.strip():
            raise ValueError("A nonempty engineering request is required")
        words = set(_WORD.findall(request.lower())) - _STOP
        scored: list[tuple[int, str]] = []
        for module in self.registry.list_skills():
            metadata = module["id"].replace("-", " ") + " " + module["description"]
            tokens = set(_WORD.findall(metadata.lower())) - _STOP
            score = len(words & tokens)
            if score:
                scored.append((score, module["id"]))
        scored.sort(key=lambda x: (-x[0], x[1]))
        return {
            "selected": [{"skill_id": name, "score": score} for score, name in scored[:3]],
            "mode": "deterministic_metadata_match",
            "authorization_granted": False,
        }


class NextActionPlanner:
    """Recommend a different diagnostic step after repeat failure; never execute it."""

    def __init__(self, guard: FailureGuard):
        self.guard = guard

    def recommend(self, workspace: str, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        status = self.guard.status(workspace, tool_name, arguments)
        if status["strategy_change_required"]:
            return {
                "action": "CHANGE_STRATEGY",
                "repeat_count": status["consecutive_failures"],
                "blocked_same_call": True,
                "alternatives": [
                    "inspect the observed error and exact current source",
                    "trace the target symbol and its references",
                    "compare runtime identity, configuration, and source revision",
                    "construct a minimum falsifying reproducer",
                ],
                "authorization_granted": False,
                "future_steps_are_predictions": True,
            }
        return {
            "action": "INSPECT_CURRENT_EVIDENCE",
            "repeat_count": status["consecutive_failures"],
            "blocked_same_call": False,
            "authorization_granted": False,
            "future_steps_are_predictions": True,
        }
