# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure conditional CODEMIND action preview; never task authorization or execution."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any

_INTENT_WORDS: dict[str, tuple[str, ...]] = {
    "debug": ("bug", "debug", "error", "fix", "crash", "failure", "broken", "repair"),
    "review": ("audit", "review", "inspect", "analyze", "read", "explain"),
    "implement": ("build", "implement", "add", "create", "feature", "develop", "design"),
    "validate": ("test", "verify", "validate", "benchmark", "regression", "proof"),
}


def classify_intent(request_text: str) -> str:
    if not isinstance(request_text, str) or not (3 <= len(request_text.strip()) <= 1000):
        raise ValueError("Request must contain 3-1,000 characters")
    words = set(re.findall(r"[a-z][a-z0-9-]*", request_text.lower()))
    scores = {name: len(words.intersection(triggers)) for name, triggers in _INTENT_WORDS.items()}
    best = max(scores.values())
    if best == 0:
        return "inspect"
    # Deterministic tie resolution, never an AI-confidence assertion.
    return next(name for name in ("debug", "validate", "review", "implement") if scores[name] == best)


# Stages are engineering-method advice, not a finite-state autonomous controller.
_STAGE_DEFS: tuple[tuple[str, str], ...] = (
    ("INSPECT_CURRENT_SOURCE", "Observe active source identity, project and symbol owner"),
    ("GATHER_REPRODUCER", "Identify a direct reproducer and strongest falsifier"),
    ("VALIDATE_OWNERSHIP", "Confirm task/session binding and authorized target"),
    ("PROPOSE_MINIMAL_CHANGE", "Describe smallest evidence-backed intervention"),
    ("RUN_FOCUSED_VALIDATION", "Test reproducer and affected regressions at current source"),
    ("REVIEW_SECURITY_BOUNDARY", "Check secrets, operation authorization and negative cases"),
    ("REVIEW_INDEPENDENT_SERVICES", "Verify Commander and Serena do not share restart authority"),
    ("VERIFY_RUNTIME_GENERATION", "Compare installed and running build to reviewed source"),
    ("RUN_DURABILITY_CASES", "Exercise applicable retry, timeout and concurrency scenarios"),
    ("RECONCILE_GIT_DELIVERY", "Verify owned diff, protected review and remote SHA"),
    ("VERIFY_CONSUMER_PATH", "Observe authorized client use and actual output"),
    ("ASSESS_LESSON", "Consider sanitized, reusable safeguard only after evidence"),
    ("RECORD_OUTCOME", "Record actual verified results and remaining blocker"),
    ("COMPLETE_IF_PROVEN", "Close only the exact request with independent evidence"),
)


def preview_actions(
    request_text: str,
    *,
    project_name: str | None,
    task_bound: bool = False,
    same_strategy_failures: int = 0,
    observed_revision: str | None = None,
) -> dict[str, Any]:
    """Return bounded conditional advice. No forecast is executable."""
    intent = classify_intent(request_text)
    if type(same_strategy_failures) is not int or not 0 <= same_strategy_failures <= 100:
        raise ValueError("Invalid observed failure count")
    if project_name is not None and (not isinstance(project_name, str) or len(project_name) > 120):
        raise ValueError("Invalid project name")
    if observed_revision is not None and (
        not isinstance(observed_revision, str) or not re.fullmatch(r"[0-9a-f]{40,64}", observed_revision)
    ):
        raise ValueError("Invalid source revision")
    if not project_name:
        canonical = "ACTIVATE_PROJECT"
        blocker = "NO_ACTIVE_PROJECT"
    elif same_strategy_failures >= 2:
        canonical = "CHANGE_STRATEGY"
        blocker = "REPEATED_EQUIVALENT_FAILURE"
    elif not task_bound:
        canonical = "INSPECT_CURRENT_SOURCE"
        blocker = "TASK_SESSION_UNBOUND"
    else:
        canonical = "INSPECT_CURRENT_SOURCE"
        blocker = "EXECUTION_PERMISSION_NOT_ESTABLISHED"

    stages = [("CANONICAL_NEXT_ACTION", canonical, "Evidence first; do not mutate or execute")]
    for stage, description in _STAGE_DEFS:
        if stage == canonical:
            continue
        stages.append(("CONDITIONAL_FORECAST", stage, description))
    stages = stages[:20]

    def advisory(i: int, kind: str, name: str, explanation: str) -> dict[str, Any]:
        return {
            "id": "F" + str(i + 1).zfill(2),
            "kind": kind,
            "action": name,
            "branch": "recovery" if canonical == "CHANGE_STRATEGY" else "expected",
            "priority": i + 1,
            "prerequisite": "Current task/source and authoritative owner evidence",
            "evidence_gate": explanation,
            "disconfirming_test": "Observed source, task authorization, or focused test contradicts the prerequisite",
            "fallback": "Stop, inspect current evidence and change the hypothesis without bypassing permissions",
            "verdict": "PENDING_EVIDENCE",
            "executable": False,
            "authorized_by_forecast": False,
        }

    candidates = [advisory(i, *stage) for i, stage in enumerate(stages)]
    preview = candidates[:5]
    return {
        "schema": 2,
        "state": "ADVISORY_ONLY",
        "observed_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "project": project_name,
        "task_binding": "BOUND_INPUT_UNVERIFIED" if task_bound else "UNBOUND",
        "intent": intent,
        "canonical": {"action": canonical, "evidence_gate": blocker, "authorized": False},
        "blocker": blocker,
        "algorithm": "bounded_deterministic_method_preview",
        "source_revision": observed_revision,
        "source_revision_attested": False,
        "preview": preview,
        "fu_candidates": candidates,
        "max_preview": 5,
        "max_fu": 20,
        "authorization_granted": False,
    }
