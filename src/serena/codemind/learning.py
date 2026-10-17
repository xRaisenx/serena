# SPDX-License-Identifier: GPL-3.0-or-later
"""Persistent, fail-closed repeated-strategy protection for MCP tool calls."""

from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import threading
from pathlib import Path
from typing import Any


class StrategyChangeRequired(RuntimeError):
    """Raised before an exhausted tool strategy can execute again."""


class FailureGuard:
    """Stores opaque failure fingerprints without logging source code or tool arguments."""

    _lock = threading.RLock()

    def __init__(self, db_path: Path | None = None):
        default_dir = Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "CodemindSerena"
        self._db_path = Path(db_path) if db_path is not None else default_dir / "failures.sqlite3"
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS attempts("
                "key TEXT PRIMARY KEY, fingerprint TEXT NOT NULL, "
                "consecutive INTEGER NOT NULL CHECK(consecutive >= 1), "
                "updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._db_path, timeout=10)
        connection.execute("PRAGMA busy_timeout=10000")
        return connection

    @staticmethod
    def _digest(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    @classmethod
    def _key(cls, workspace: str, tool_name: str, arguments: dict[str, Any]) -> str:
        # Do not persist source code, credentials, arguments, or file names.
        serialized = json.dumps(
            {"workspace": str(Path(workspace).resolve()).lower(),
             "tool": tool_name, "args": arguments},
            sort_keys=True, separators=(",", ":"), default=str
        )
        return cls._digest(serialized)

    @classmethod
    def _failure(cls, exception: BaseException) -> str:
        message = str(exception).lower()
        message = re.sub(r"[0-9a-f]{8}-[0-9a-f-]{27,}", "<id>", message)
        message = re.sub(r"\b\d+\b", "<n>", message)
        # Hash rather than storing sensitive error text or stack frames.
        return cls._digest(type(exception).__name__ + ":" + message[:2000])

    def check(self, workspace: str, tool_name: str, arguments: dict[str, Any]) -> None:
        key = self._key(workspace, tool_name, arguments)
        with self._lock, self._connect() as db:
            row = db.execute(
                "SELECT consecutive FROM attempts WHERE key=?", (key,)
            ).fetchone()
            if row is not None and row[0] >= 2:
                raise StrategyChangeRequired(
                    "STRATEGY_CHANGE_REQUIRED: two consecutive equivalent failures. "
                    "Change the operation, inputs, or diagnostic hypothesis based on new evidence."
                )

    def failure(self, workspace: str, tool_name: str, arguments: dict[str, Any],
                error: BaseException) -> int:
        key, fingerprint = self._key(workspace, tool_name, arguments), self._failure(error)
        with self._lock, self._connect() as db:
            row = db.execute(
                "SELECT fingerprint, consecutive FROM attempts WHERE key=?", (key,)
            ).fetchone()
            count = row[1] + 1 if row and row[0] == fingerprint else 1
            db.execute(
                "INSERT INTO attempts(key,fingerprint,consecutive) VALUES(?,?,?) "
                "ON CONFLICT(key) DO UPDATE SET fingerprint=excluded.fingerprint, "
                "consecutive=excluded.consecutive, updated_at=CURRENT_TIMESTAMP",
                (key, fingerprint, count)
            )
            return count

    def success(self, workspace: str, tool_name: str, arguments: dict[str, Any]) -> None:
        with self._lock, self._connect() as db:
            db.execute(
                "DELETE FROM attempts WHERE key=?",
                (self._key(workspace, tool_name, arguments),)
            )

    def status(self, workspace: str, tool_name: str,
               arguments: dict[str, Any]) -> dict[str, Any]:
        with self._lock, self._connect() as db:
            row = db.execute(
                "SELECT consecutive, updated_at FROM attempts WHERE key=?",
                (self._key(workspace, tool_name, arguments),)
            ).fetchone()
        return {
            "consecutive_failures": row[0] if row else 0,
            "strategy_change_required": bool(row and row[0] >= 2),
            "updated_at": row[1] if row else None,
        }
