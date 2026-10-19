# SPDX-License-Identifier: GPL-3.0-or-later
"""Unit tests for secure tunnel credential storage and service ownership."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

SRC = Path(__file__).resolve().parents[2] / "src" / "serena" / "codemind" / "tunnel_control.py"
SPEC = importlib.util.spec_from_file_location("codemind_tunnel_control_test", SRC)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


@pytest.fixture
def ctl(tmp_path, monkeypatch):
    # Deterministic test surrogate for DPAPI; actual Windows DPAPI is
    # independently tested on the Windows host.
    def fake_dpapi(data, *, decrypt):
        # Reversible deterministic stand-in; the plaintext must not remain
        # directly visible in the persisted bytes. Real DPAPI is Windows-only.
        return bytes(value ^ 0xA5 for value in data)

    monkeypatch.setattr(MODULE, "_dpapi", fake_dpapi)
    exe = tmp_path / "tunnel-client.exe"
    exe.write_bytes(b"dummy")
    return MODULE.TunnelController(data_dir=tmp_path / "secret", executable=exe)


def test_key_persisted_ciphertext_only(ctl):
    key = "sk-proj-" + "a" * 60
    ctl.save_key(key)
    saved = (ctl._data_dir / MODULE.KEY_NAME).read_bytes()
    assert key.encode() not in saved
    assert ctl.status()["key_configured"] is True
    assert ctl._read_secret() == key


def test_key_never_in_status(ctl):
    key = "sk-proj-" + "z" * 60
    ctl.save_key(key)
    assert key not in str(ctl.status())
    assert ctl.status()["connection_verified"] is False


@pytest.mark.parametrize("key", ["", "sk-proj-***", "not-a-key", "sk-a", "sk-proj-" + "a" * 260])
def test_bad_keys_denied(ctl, key):
    with pytest.raises(MODULE.TunnelControlError):
        ctl.save_key(key)
    assert ctl.status()["key_configured"] is False


def test_key_removal_and_symlink_protection(ctl):
    ctl.save_key("sk-proj-" + "a" * 50)
    ctl.remove_key()
    assert ctl.status()["key_configured"] is False
    with pytest.raises(MODULE.TunnelControlError):
        ctl._read_secret()


def test_missing_key_blocks_doctor(ctl):
    with pytest.raises(MODULE.TunnelControlError):
        ctl.doctor()


def test_doctor_never_logs_or_returns_secret(ctl, monkeypatch):
    key = "sk-proj-" + "a" * 50
    ctl.save_key(key)

    def fake_run(args, env, stdout, stderr, timeout, check):
        assert key == env["CONTROL_PLANE_API_KEY"]
        assert key not in repr(args)
        assert args[-2:] == ["--health.listen-addr", "127.0.0.1:0"]
        assert stdout == subprocess.DEVNULL
        assert stderr == subprocess.DEVNULL
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(MODULE.subprocess, "run", fake_run)
    result = ctl.doctor()
    assert result["passed"] is True
    assert key not in str(result)


def test_nonzero_doctor_is_not_pass(ctl, monkeypatch):
    ctl.save_key("sk-proj-" + "a" * 50)
    monkeypatch.setattr(MODULE.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=17))
    assert ctl.doctor()["passed"] is False


def test_timeout_is_not_pass(ctl, monkeypatch):
    ctl.save_key("sk-proj-" + "a" * 50)

    def timeout(*a, **k):
        raise subprocess.TimeoutExpired(cmd="doctor", timeout=30)

    monkeypatch.setattr(MODULE.subprocess, "run", timeout)
    assert ctl.doctor()["passed"] is False


def test_start_only_after_doctor_success(ctl, monkeypatch):
    ctl.save_key("sk-proj-" + "a" * 50)
    monkeypatch.setattr(ctl, "doctor", lambda: {"passed": False, "message": "Not authorized"})
    with pytest.raises(MODULE.TunnelControlError):
        ctl.start()


def test_start_status_stop_only_owned_child(ctl, monkeypatch):
    ctl.save_key("sk-proj-" + "a" * 50)
    monkeypatch.setattr(ctl, "doctor", lambda: {"passed": True})
    observed = {}

    class FakeProc:
        def __init__(self):
            self.stopped = False

        def poll(self):
            return 0 if self.stopped else None

        def terminate(self):
            self.stopped = True

        def wait(self, timeout):
            assert timeout == 5

    def spawn(args, env, stdin, stdout, stderr, creationflags):
        assert args[1:4] == ["run", "--profile", MODULE.PROFILE]
        assert env["CONTROL_PLANE_API_KEY"].startswith("sk-proj-")
        assert stdout == subprocess.DEVNULL
        assert stderr == subprocess.DEVNULL
        observed["proc"] = FakeProc()
        return observed["proc"]

    monkeypatch.setattr(MODULE.subprocess, "Popen", spawn)
    assert ctl.start()["managed_process_running"] is True
    assert ctl.stop()["managed_process_running"] is False
    assert observed["proc"].stopped is True


def test_health_url_cannot_escape_loopback(ctl):
    ctl._data_dir.mkdir()
    ctl._health_url_file.write_text("http://attacker.example:8123", encoding="utf-8")
    assert ctl._readiness()["ready"] is False
    assert ctl._readiness()["health"] == "invalid_local_health_url"


def test_remove_key_blocked_when_client_running(ctl):
    ctl.save_key("sk-proj-" + "a" * 50)
    ctl._process = SimpleNamespace(poll=lambda: None)
    with pytest.raises(MODULE.TunnelControlError):
        ctl.remove_key()


def test_consumer_challenge_requires_managed_ready_tunnel(ctl, monkeypatch):
    with pytest.raises(MODULE.TunnelControlError):
        ctl.issue_consumer_challenge()
    ctl._process = SimpleNamespace(poll=lambda: None)
    monkeypatch.setattr(ctl, "_readiness", lambda: {"ready": True, "health": "ready"})
    challenge = ctl.issue_consumer_challenge()
    assert len(challenge["challenge"]) == 40
    assert challenge["authorization_granted"] is False
    assert ctl.status()["connection_verified"] is False
    with pytest.raises(MODULE.TunnelControlError):
        ctl.accept_consumer_receipt("0" * 40)
    result = ctl.accept_consumer_receipt(challenge["challenge"])
    assert result["accepted"] is True
    assert result["origin_cryptographically_attested"] is False
    assert ctl.status()["connection_verified"] is True
    assert ctl.status()["chatgpt_tool_call_verified"] is True
    assert challenge["challenge"] not in str(ctl.status())
    with pytest.raises(MODULE.TunnelControlError):
        ctl.accept_consumer_receipt(challenge["challenge"])


def test_consumer_receipt_is_bounded_and_expires(ctl, monkeypatch):
    clock = [1000.0]
    monkeypatch.setattr(MODULE.time, "monotonic", lambda: clock[0])
    ctl._process = SimpleNamespace(poll=lambda: None)
    monkeypatch.setattr(ctl, "_readiness", lambda: {"ready": True, "health": "ready"})
    challenge = ctl.issue_consumer_challenge()["challenge"]
    clock[0] += 91
    with pytest.raises(MODULE.TunnelControlError):
        ctl.accept_consumer_receipt(challenge)
    challenge = ctl.issue_consumer_challenge()["challenge"]
    assert ctl.accept_consumer_receipt(challenge)["accepted"] is True
    assert ctl.status()["connection_verified"] is True
    clock[0] += 601
    assert ctl.status()["connection_verified"] is False


def test_consumer_receipt_fails_closed_when_client_stops(ctl, monkeypatch):
    ctl._process = SimpleNamespace(poll=lambda: None)
    monkeypatch.setattr(ctl, "_readiness", lambda: {"ready": True, "health": "ready"})
    challenge = ctl.issue_consumer_challenge()["challenge"]
    ctl.accept_consumer_receipt(challenge)
    ctl._process = SimpleNamespace(poll=lambda: 0)
    assert ctl.status()["connection_verified"] is False
    with pytest.raises(MODULE.TunnelControlError):
        ctl.issue_consumer_challenge()


@pytest.mark.skipif(MODULE.os.name != "nt", reason="Real DPAPI only exists on Windows")
def test_real_windows_dpapi_roundtrip():
    key = b"sk-proj-" + b"r" * 80
    encrypted = MODULE._dpapi(key, decrypt=False)
    assert encrypted != key
    assert key not in encrypted
    assert MODULE._dpapi(encrypted, decrypt=True) == key
