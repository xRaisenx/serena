# SPDX-License-Identifier: GPL-3.0-or-later
"""Fail-closed peer health and independent bounded-recovery policy.

This module never starts or stops any process. It makes no claims of live
Commander interoperability until the peer implements the attested contract.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

# Dedicated SCC peer identity. Never accept a different Windows Commander service.
SCC_COMMANDER_IDENTITY = "SCC.WindowsCommander"


@dataclass(frozen=True)
class PeerStatus:
    ready: bool
    reason: str
    authenticated: bool = False


class CommanderHealthProbe:
    """Require an authenticated, challenge-bound response from a local peer."""

    def __init__(
        self,
        url: str,
        bearer_token: str,
        *,
        transport: Callable[[Request, float], bytes] | None = None,
    ) -> None:
        parts = urlsplit(url)
        if parts.scheme != "http" or parts.hostname not in {"127.0.0.1", "::1"}:
            raise ValueError("Peer endpoint must use loopback HTTP")
        if parts.username or parts.password or parts.fragment or parts.query or not parts.port:
            raise ValueError("Peer endpoint contains forbidden URL fields")
        if parts.path != "/codemind/health":
            raise ValueError("Peer endpoint must be the scoped CODEMIND health path")
        if not bearer_token or len(bearer_token) < 32 or "\r" in bearer_token or "\n" in bearer_token:
            raise ValueError("A strong peer authentication token is required")
        self._url = url
        self._token = bearer_token
        self._transport = transport or self._fetch

    @staticmethod
    def _fetch(request: Request, timeout: float) -> bytes:
        with urlopen(request, timeout=timeout) as response:
            if response.status != 200:
                raise ConnectionError("peer response status is not 200")
            data = response.read(4097)
            if len(data) > 4096:
                raise ValueError("peer health response is too large")
            return data

    def check(self) -> PeerStatus:
        nonce = secrets.token_hex(20)
        req = Request(
            self._url,
            headers={"Authorization": "Bearer " + self._token, "X-Codemind-Challenge": nonce},
            method="GET",
        )
        try:
            raw = self._transport(req, 3.0)
            if len(raw) > 4096:
                return PeerStatus(False, "response_too_large")
            obj = json.loads(raw)
            if not isinstance(obj, dict):
                return PeerStatus(False, "invalid_shape")
            if not secrets.compare_digest(str(obj.get("nonce", "")), nonce):
                return PeerStatus(False, "challenge_mismatch")
            expected_proof = hmac.new(
                self._token.encode("utf-8"), (nonce + ":" + SCC_COMMANDER_IDENTITY + ":v1").encode("utf-8"), hashlib.sha256
            ).hexdigest()
            if not secrets.compare_digest(str(obj.get("proof", "")), expected_proof):
                return PeerStatus(False, "authentication_failed")
            if obj.get("service") != SCC_COMMANDER_IDENTITY:
                return PeerStatus(False, "wrong_service")
            if obj.get("ready") is not True or obj.get("mcp_initialize") is not True:
                return PeerStatus(False, "peer_not_ready", authenticated=True)
            return PeerStatus(True, "ready", authenticated=True)
        except (OSError, TimeoutError, ValueError, TypeError, KeyError, json.JSONDecodeError):
            return PeerStatus(False, "unverified_peer")


class RecoveryAdapter(Protocol):
    """Explicit owner-authorized recovery adapter, implemented outside this module."""

    def restart(self) -> bool: ...


class RecoveryCircuit:
    """Only suggest/authorize bounded recoveries; never restart implicitly."""

    def __init__(self, *, max_attempts: int = 3, cooldown_s: float = 60.0, clock: Callable[[], float] = time.monotonic):
        if not 1 <= max_attempts <= 3 or cooldown_s < 1:
            raise ValueError("unsafe restart policy")
        self._limit = max_attempts
        self._cooldown = cooldown_s
        self._clock = clock
        self._attempts = 0
        self._next_allowed = 0.0

    def plan(self, status: PeerStatus, *, owner_authorized: bool) -> dict[str, object]:
        if status.ready and status.authenticated:
            self._attempts = 0
            self._next_allowed = 0.0
            return {"action": "NO_ACTION", "attempts": 0}
        if not owner_authorized:
            return {"action": "OBSERVE_ONLY", "attempts": self._attempts}
        if self._attempts >= self._limit:
            return {"action": "CIRCUIT_OPEN", "attempts": self._attempts}
        if self._clock() < self._next_allowed:
            return {"action": "COOLDOWN", "attempts": self._attempts}
        return {"action": "RECOVERY_PERMITTED", "attempts": self._attempts}

    def record_restart(self, *, owner_authorized: bool) -> None:
        if not owner_authorized or self._attempts >= self._limit or self._clock() < self._next_allowed:
            raise PermissionError("restart denied by owner policy or circuit")
        self._attempts += 1
        self._next_allowed = self._clock() + self._cooldown * (2 ** (self._attempts - 1))
