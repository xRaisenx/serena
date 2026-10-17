# SPDX-License-Identifier: GPL-3.0-or-later
"""Owner-scoped OpenAI tunnel credential and lifecycle control.

No API key is returned through HTTP, CLI arguments, logging, or diagnostics.
The tunnel remains a distinct process and is never interpreted as ChatGPT app acceptance.
"""

from __future__ import annotations

import ctypes
import os
import re
import subprocess
import threading
from ctypes import wintypes
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import urlopen

PROFILE = "serena-code-commander"
TUNNEL_ID = "tunnel_6ad3458efdd4819188d0f9ae6db8c264"
KEY_NAME = "control-plane-key.dpapi"
_SECRET_PATTERN = re.compile(r"^sk-[A-Za-z0-9_-]{29,250}$")
_LOCK = threading.RLock()


class TunnelControlError(Exception):
    """Safe-to-display tunnel controller error without credential content."""


class _Blob(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_byte))]


def _dpapi(data: bytes, *, decrypt: bool) -> bytes:
    if os.name != "nt":
        raise TunnelControlError("Encrypted key storage requires Windows DPAPI")
    crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    crypt = crypt32.CryptUnprotectData if decrypt else crypt32.CryptProtectData
    crypt.argtypes = (
        [ctypes.POINTER(_Blob), ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(_Blob)]
        if decrypt
        else [
            ctypes.POINTER(_Blob),
            wintypes.LPCWSTR,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            wintypes.DWORD,
            ctypes.POINTER(_Blob),
        ]
    )
    crypt.restype = wintypes.BOOL
    kernel32.LocalFree.argtypes = [ctypes.c_void_p]
    kernel32.LocalFree.restype = ctypes.c_void_p
    buffer = ctypes.create_string_buffer(data)
    incoming = _Blob(len(data), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_byte)))
    outgoing = _Blob()
    # CRYPTPROTECT_UI_FORBIDDEN = 0x1, user-scoped; never use LOCAL_MACHINE.
    label = None if decrypt else "CODEMIND tunnel runtime credential"
    try:
        if not crypt(ctypes.byref(incoming), label, None, None, None, 1, ctypes.byref(outgoing)):
            raise TunnelControlError("Windows credential protection failed")
        return ctypes.string_at(outgoing.pbData, outgoing.cbData)
    finally:
        if outgoing.pbData:
            kernel32.LocalFree(ctypes.cast(outgoing.pbData, ctypes.c_void_p))


class TunnelController:
    def __init__(self, data_dir: Path | None = None, executable: Path | None = None):
        root = Path(__file__).resolve().parents[3]
        self._data_dir = Path(data_dir) if data_dir else Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "CODEMIND-Serena"
        self._secret_path = self._data_dir / KEY_NAME
        self._health_url_file = self._data_dir / "tunnel-health-url.txt"
        self._binary = executable or (root / ".codemind" / "bin" / "tunnel-client-v0.0.16" / "tunnel-client.exe")
        self._process: subprocess.Popen[bytes] | None = None

    def _read_secret(self) -> str:
        try:
            if not self._secret_path.is_file() or self._secret_path.is_symlink():
                raise TunnelControlError("Runtime API key is not configured")
            return _dpapi(self._secret_path.read_bytes(), decrypt=True).decode("utf-8")
        except (OSError, UnicodeError) as exc:
            raise TunnelControlError("Encrypted credential is unavailable to this Windows user") from exc

    def save_key(self, key: str) -> None:
        if not isinstance(key, str) or len(key) > 253 or not _SECRET_PATTERN.fullmatch(key):
            raise TunnelControlError("Enter a valid, unmasked project API key")
        ciphertext = _dpapi(key.encode("utf-8"), decrypt=False)
        with _LOCK:
            self._data_dir.mkdir(parents=True, exist_ok=True)
            tmp = self._secret_path.with_suffix(".tmp")
            try:
                with open(tmp, "xb") as handle:
                    handle.write(ciphertext)
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(tmp, self._secret_path)
            finally:
                if tmp.exists():
                    tmp.unlink()

    def remove_key(self) -> None:
        with _LOCK:
            if self._process and self._process.poll() is None:
                raise TunnelControlError("Stop the managed tunnel before removing its credential")
            self._secret_path.unlink(missing_ok=True)

    def _binary_ready(self) -> bool:
        return self._binary.is_file() and not self._binary.is_symlink() and self._binary.name.lower() == "tunnel-client.exe"

    def _secret_env(self) -> dict[str, str]:
        if not self._binary_ready():
            raise TunnelControlError("Official tunnel-client executable is missing")
        env = os.environ.copy()
        env["CONTROL_PLANE_API_KEY"] = self._read_secret()
        return env

    def doctor(self) -> dict[str, object]:
        env = self._secret_env()
        try:
            result = subprocess.run(
                [str(self._binary), "doctor", "--profile", PROFILE, "--explain", "--health.listen-addr", "127.0.0.1:0"],
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=30,
                check=False,
            )
            return {
                "passed": result.returncode == 0,
                "exit_code": result.returncode,
                "message": "Tunnel diagnostics passed"
                if result.returncode == 0
                else "Tunnel diagnostics failed; verify key role, tunnel association and local MCP",
            }
        except subprocess.TimeoutExpired:
            return {"passed": False, "exit_code": None, "message": "Tunnel diagnostics timed out"}
        except OSError:
            return {"passed": False, "exit_code": None, "message": "Tunnel-client could not be started"}

    def _readiness(self) -> dict[str, object]:
        try:
            if self._health_url_file.is_symlink() or not self._health_url_file.is_file():
                return {"ready": False, "health": "not_reported"}
            url = self._health_url_file.read_text(encoding="utf-8").strip()
            parts = urlsplit(url)
            if parts.scheme != "http" or parts.hostname != "127.0.0.1" or not parts.port or parts.username or parts.password:
                return {"ready": False, "health": "invalid_local_health_url"}
            with urlopen(url.rstrip("/") + "/readyz", timeout=1.2) as reply:
                ready = reply.status == 200
            return {"ready": ready, "health": "ready" if ready else "not_ready"}
        except (OSError, ValueError):
            return {"ready": False, "health": "unreachable"}

    def status(self) -> dict[str, object]:
        with _LOCK:
            proc = self._process
            running = bool(proc and proc.poll() is None)
            readiness = self._readiness() if running else {"ready": False, "health": "not_running"}
            return {
                "id": TUNNEL_ID,
                "profile": PROFILE,
                "binary_installed": self._binary_ready(),
                "key_configured": self._secret_path.is_file() and not self._secret_path.is_symlink(),
                "managed_process_running": running,
                "client_ready": bool(readiness["ready"]),
                "health": readiness["health"],
                # ChatGPT consumer acceptance requires a real remote tool call.
                "connection_verified": False,
                "chatgpt_tool_call_verified": False,
            }

    def start(self) -> dict[str, object]:
        with _LOCK:
            if self._process and self._process.poll() is None:
                return self.status()
            checked = self.doctor()
            if not checked["passed"]:
                raise TunnelControlError(str(checked["message"]))
            self._data_dir.mkdir(parents=True, exist_ok=True)
            self._health_url_file.unlink(missing_ok=True)
            env = self._secret_env()
            flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            try:
                self._process = subprocess.Popen(
                    [
                        str(self._binary),
                        "run",
                        "--profile",
                        PROFILE,
                        "--health.listen-addr",
                        "127.0.0.1:0",
                        "--health.url-file",
                        str(self._health_url_file),
                    ],
                    env=env,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=flags,
                )
            except OSError as exc:
                raise TunnelControlError("Could not launch the tunnel client") from exc
            return self.status()

    def stop(self) -> dict[str, object]:
        with _LOCK:
            if self._process and self._process.poll() is None:
                self._process.terminate()
                try:
                    self._process.wait(timeout=5)
                except subprocess.TimeoutExpired as exc:
                    raise TunnelControlError("Managed tunnel did not stop in time; no unrelated process was terminated") from exc
            self._process = None
            return self.status()


controller = TunnelController()
