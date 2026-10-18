# SPDX-License-Identifier: GPL-3.0-or-later
"""The SCC Commander tool must never count NMBV's separate process."""

from __future__ import annotations

import json
from types import SimpleNamespace

import psutil

from serena.tools.codemind_tools import CodemindCommanderStatusTool


def test_commander_discovery_only_counts_scc_owned_node(monkeypatch):
    processes = [
        SimpleNamespace(info={"pid": 100, "name": "WindowsCommander.McpServer.exe", "cmdline": ["nmbv.exe"]}),
        SimpleNamespace(
            info={
                "pid": 101,
                "name": "node.exe",
                "cmdline": ["node.exe", "D:\\DEV\\codemind-serena\\tools\\scc_commander\\server.cjs"],
            }
        ),
        SimpleNamespace(info={"pid": 102, "name": "node.exe", "cmdline": ["node.exe", "other-project.js"]}),
    ]
    monkeypatch.setattr(psutil, "process_iter", lambda attrs: iter(processes))
    monkeypatch.delenv("CODEMIND_COMMANDER_HEALTH_URL", raising=False)
    monkeypatch.delenv("CODEMIND_COMMANDER_HEALTH_TOKEN", raising=False)

    status = json.loads(CodemindCommanderStatusTool.apply(None))
    assert status["commander_process_present"] is True
    assert status["processes"] == [{"pid": 101}]
    assert status["mcp_health_verified"] is False
    assert status["peer_health"]["reason"] == "not_configured"


def test_nmbv_commander_presence_alone_never_counts(monkeypatch):
    process = SimpleNamespace(info={"pid": 200, "name": "WindowsCommander.McpServer.exe", "cmdline": []})
    monkeypatch.setattr(psutil, "process_iter", lambda attrs: iter([process]))
    monkeypatch.delenv("CODEMIND_COMMANDER_HEALTH_URL", raising=False)
    monkeypatch.delenv("CODEMIND_COMMANDER_HEALTH_TOKEN", raising=False)

    status = json.loads(CodemindCommanderStatusTool.apply(None))
    assert status["commander_process_present"] is False
    assert status["processes"] == []
