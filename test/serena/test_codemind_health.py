# SPDX-License-Identifier: GPL-3.0-or-later
"""Security/behavior tests for peer health and bounded recovery."""

import hashlib
import hmac
import importlib.util
import json
import sys
from pathlib import Path

import pytest

PATH = Path(__file__).resolve().parents[2] / "src" / "serena" / "codemind" / "health.py"
SPEC = importlib.util.spec_from_file_location("codemind_health_isolated", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def mk_probe(transport):
    return MODULE.CommanderHealthProbe("http://127.0.0.1:9881/codemind/health", "x" * 40, transport=transport)


def healthy_response(request, timeout):
    nonce = request.get_header("X-codemind-challenge")
    proof = hmac.new(("x" * 40).encode(), (nonce + ":SCC.WindowsCommander:v1").encode(), hashlib.sha256).hexdigest()
    return json.dumps({"service": "SCC.WindowsCommander", "ready": True, "mcp_initialize": True, "nonce": nonce, "proof": proof}).encode()


def test_genuine_challenge_response_is_accepted():
    assert mk_probe(healthy_response).check() == MODULE.PeerStatus(True, "ready", True)


def test_stale_challenge_is_rejected():
    assert (
        mk_probe(
            lambda req, timeout: json.dumps(
                {"nonce": "old", "service": "SCC.WindowsCommander", "ready": True, "mcp_initialize": True}
            ).encode()
        )
        .check()
        .ready
        is False
    )


def test_running_process_is_not_sufficient():
    def response(req, timeout):
        payload = json.loads(healthy_response(req, timeout))
        payload["mcp_initialize"] = False
        return json.dumps(payload).encode()

    assert mk_probe(response).check().reason == "peer_not_ready"


@pytest.mark.parametrize(
    "url",
    [
        "http://evil.example:99/codemind/health",
        "https://127.0.0.1:9881/codemind/health",
        "http://127.0.0.1:9881/",
        "http://127.0.0.1:9881/codemind/health?u=1",
        "http://name:pass@127.0.0.1:9881/codemind/health",
    ],
)
def test_remote_or_unsafe_endpoints_denied(url):
    with pytest.raises(ValueError):
        MODULE.CommanderHealthProbe(url, "x" * 40)


def test_unsigned_fake_health_is_rejected():
    assert (
        mk_probe(
            lambda req, timeout: json.dumps(
                {
                    "nonce": req.get_header("X-codemind-challenge"),
                    "service": "SCC.WindowsCommander",
                    "ready": True,
                    "mcp_initialize": True,
                }
            ).encode()
        )
        .check()
        .reason
        == "authentication_failed"
    )


def test_oversized_response_fails_closed():
    assert mk_probe(lambda req, timeout: b"x" * 4097).check().ready is False


def test_missing_or_weak_auth_denied():
    with pytest.raises(ValueError):
        MODULE.CommanderHealthProbe("http://127.0.0.1:9881/codemind/health", "short")


def test_bad_peer_response_returns_unverified():
    assert mk_probe(lambda req, timeout: b"not json").check().reason == "unverified_peer"


def test_no_unauthorized_recovery():
    circuit = MODULE.RecoveryCircuit(clock=lambda: 0.0)
    assert circuit.plan(MODULE.PeerStatus(False, "down"), owner_authorized=False)["action"] == "OBSERVE_ONLY"
    with pytest.raises(PermissionError):
        circuit.record_restart(owner_authorized=False)


def test_backoff_and_circuit_breaker():
    state = [0.0]
    circuit = MODULE.RecoveryCircuit(clock=lambda: state[0], cooldown_s=10)
    down = MODULE.PeerStatus(False, "down")
    for step in (0, 10, 30):
        state[0] = step
        assert circuit.plan(down, owner_authorized=True)["action"] == "RECOVERY_PERMITTED"
        circuit.record_restart(owner_authorized=True)
        assert circuit.plan(down, owner_authorized=True)["action"] in {"COOLDOWN", "CIRCUIT_OPEN"}
    state[0] = 100
    assert circuit.plan(down, owner_authorized=True)["action"] == "CIRCUIT_OPEN"
    assert circuit.plan(MODULE.PeerStatus(True, "ready", True), owner_authorized=False)["action"] == "NO_ACTION"
    assert circuit.plan(down, owner_authorized=True)["action"] == "RECOVERY_PERMITTED"


def test_foreign_windows_commander_identity_is_never_accepted():
    def foreign_response(req, timeout):
        nonce = req.get_header("X-codemind-challenge")
        proof = hmac.new(("x" * 40).encode(), (nonce + ":WindowsCommander.McpServer:v1").encode(), hashlib.sha256).hexdigest()
        return json.dumps(
            {
                "service": "WindowsCommander.McpServer",
                "ready": True,
                "mcp_initialize": True,
                "nonce": nonce,
                "proof": proof,
            }
        ).encode()

    assert mk_probe(foreign_response).check().ready is False
