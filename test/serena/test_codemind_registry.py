# SPDX-License-Identifier: GPL-3.0-or-later
"""Integration check for CODEMIND tools registered in real Serena."""

from serena.tools import ToolRegistry


def test_codemind_tools_are_registered_by_serena() -> None:
    registered = set(ToolRegistry().get_tool_names())
    expected = {
        "codemind_list_skills",
        "codemind_failure_status",
        "codemind_commander_status",
        "codemind_skill_route",
        "codemind_next_action",
        "codemind_method_catalog",
        "codemind_forecast",
    }
    assert expected <= registered
