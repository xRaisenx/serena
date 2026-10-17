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
