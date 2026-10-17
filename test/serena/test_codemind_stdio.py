# SPDX-License-Identifier: GPL-3.0-or-later
"""Actual subprocess MCP JSON-RPC smoke (requires the full Serena environment)."""

import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def _smoke() -> None:
    params = StdioServerParameters(
        command=sys.executable,
        args=[
            "-c",
            "from serena.cli import top_level; top_level()",
            "start-mcp-server",
            "--transport",
            "stdio",
            "--enable-web-dashboard",
            "false",
            "--open-web-dashboard",
            "false",
            "--enable-gui-log-window",
            "false",
        ],
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as client:
            initialized = await asyncio.wait_for(client.initialize(), timeout=60)
            assert initialized.serverInfo.name
            tools = await asyncio.wait_for(client.list_tools(), timeout=30)
            names = {tool.name for tool in tools.tools}
            assert "codemind_commander_status" in names
            assert "codemind_failure_status" in names
            assert "find_symbol" in names
            response = await asyncio.wait_for(client.call_tool("codemind_commander_status", arguments={}), timeout=30)
            assert not response.isError
            assert any("mcp_health_verified" in str(block) for block in response.content)


def test_stdio_mcp_initialize_list_and_call() -> None:
    asyncio.run(asyncio.wait_for(_smoke(), timeout=110))
