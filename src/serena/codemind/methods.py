# SPDX-License-Identifier: GPL-3.0-or-later
"""Reference-only source-indexed engineering methods; not installed or executable skills."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class MethodCatalogError(ValueError):
    """The bundled CODEMIND reference catalog does not satisfy its contract."""


def load_method_catalog() -> dict[str, Any]:
    """Read a bounded, versioned static taxonomy; never execute source instructions."""
    path = Path(__file__).with_name("methods_catalog.json")
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 131072:
        raise MethodCatalogError("CODEMIND reference catalog missing, linked or oversized")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise MethodCatalogError("Invalid CODEMIND reference catalog") from exc
    if not isinstance(data, dict) or data.get("schema") != 1 or not isinstance(data.get("methods"), list):
        raise MethodCatalogError("Invalid catalog schema")
    methods = data["methods"]
    if len(methods) != 25:
        raise MethodCatalogError("The expected 25 source-mapped methods are not present")
    ids: set[str] = set()
    safe: list[dict[str, Any]] = []
    for obj in methods:
        if not isinstance(obj, dict):
            raise MethodCatalogError("Catalog entry must be a record")
        if obj.get("state") != "REFERENCE_ONLY" or any(obj.get(k) is not False for k in ("loaded", "executed", "authorization_granted")):
            raise MethodCatalogError("Reference catalog cannot advertise installed or executable skills")
        if any(
            not isinstance(obj.get(k), str) or not (1 <= len(obj[k]) <= 350) for k in ("id", "source_name", "description", "source_path")
        ):
            raise MethodCatalogError("Invalid catalog method metadata")
        if not obj["id"].startswith("codemind-") or obj["id"] in ids:
            raise MethodCatalogError("Duplicate or non-CODEMIND catalog id")
        ids.add(obj["id"])
        safe.append(
            {
                "id": obj["id"],
                "source_name": obj["source_name"],
                "description": obj["description"],
                "source_path": obj["source_path"],
                "state": "REFERENCE_ONLY",
                "loaded": False,
                "executed": False,
                "authorization_granted": False,
            }
        )
    return {
        "schema": 2,
        "state": "REFERENCE_ONLY",
        "count": len(safe),
        "installed_count": 0,
        "executed_count": 0,
        "source": "CODEMIND reference taxonomy mapped from NMBV PR #636",
        "methods": safe,
    }


def recommend_method_references(request_text: str, *, limit: int = 3) -> dict[str, Any]:
    """Deterministic reference suggestions; no skill body is loaded or invoked."""
    import re

    if not isinstance(request_text, str) or not (3 <= len(request_text.strip()) <= 1000):
        raise ValueError("Request text must have 3 to 1000 characters")
    if type(limit) is not int or not (1 <= limit <= 5):
        raise ValueError("Unsupported recommendation limit")
    tokens = set(re.findall(r"[a-z][a-z0-9]*", request_text.lower()))
    stop = {"the", "and", "for", "with", "into", "about", "that", "this", "your", "from"}
    tokens.difference_update(stop)
    scored: list[tuple[int, str, dict[str, Any]]] = []
    for method in load_method_catalog()["methods"]:
        meta = " ".join([method["id"].replace("-", " "), method["source_name"].replace("-", " "), method["description"]])
        matches = tokens.intersection(re.findall(r"[a-z][a-z0-9]*", meta.lower()))
        score = len(matches)
        if method["source_name"].lower().replace("-", " ") in request_text.lower():
            score += 3
        if score:
            scored.append((score, method["id"], method))
    scored.sort(key=lambda item: (-item[0], item[1]))
    return {
        "schema": 2,
        "state": "REFERENCE_SELECTION_ONLY",
        "algorithm": "deterministic_metadata_overlap",
        "selected_references": [
            {"id": method["id"], "source_name": method["source_name"], "score": score, "state": "REFERENCE_ONLY"}
            for score, _, method in scored[:limit]
        ],
        "loaded": [],
        "executed": [],
        "authorization_granted": False,
    }
