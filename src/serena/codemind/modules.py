# SPDX-License-Identifier: GPL-3.0-or-later
"""Validated declarative skill manifests, reloaded on each listing."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_SKILL_ID = re.compile(r"^[a-z][a-z0-9_-]{1,63}$")


class SkillManifestRegistry:
    """Load declarative skills without importing executable code."""

    def __init__(self, directory: Path):
        self.directory = Path(directory)

    def list_skills(self) -> list[dict[str, Any]]:
        if not self.directory.exists():
            return []
        if self.directory.is_symlink() or not self.directory.is_dir():
            raise ValueError("Skill directory must be a real directory")
        result: list[dict[str, Any]] = []
        seen: set[str] = set()
        for path in sorted(self.directory.glob("*.json")):
            if path.is_symlink() or not path.is_file():
                raise ValueError("Symbolic links are not supported for skill manifests")
            if path.stat().st_size > 65536:
                raise ValueError("Skill manifest exceeds 64 KiB")
            obj = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(obj, dict):
                raise TypeError("Skill manifest must be a JSON object")
            if set(obj) != {"id", "version", "description", "instructions", "enabled"}:
                raise ValueError("Invalid skill manifest fields")
            if not isinstance(obj["id"], str) or not _SKILL_ID.fullmatch(obj["id"]):
                raise ValueError("Invalid skill id")
            if obj["id"] in seen:
                raise ValueError("Duplicate skill id")
            seen.add(obj["id"])
            if type(obj["enabled"]) is not bool:
                raise ValueError("enabled must be boolean")
            for field in ("version", "description", "instructions"):
                if not isinstance(obj[field], str) or len(obj[field]) > 16000:
                    raise ValueError("Invalid field: " + field)
            if obj["enabled"]:
                result.append(obj)
        return result
