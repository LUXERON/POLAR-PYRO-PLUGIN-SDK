"""Bounded lifecycle supervision for shell-free plugin processes."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import os
import subprocess
from typing import Callable, Mapping, Protocol

from .mcp import McpStdioDescriptor
from .models import ContractError


class ManagedProcess(Protocol):
    pid: int

    def poll(self) -> int | None: ...
    def terminate(self) -> None: ...
    def kill(self) -> None: ...
    def wait(self, timeout: float | None = None) -> int: ...


class SupervisorState(str, Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    DEGRADED = "degraded"
    FAILED = "failed"


@dataclass(frozen=True)
class SupervisorReceipt:
    plugin_id: str
    state: SupervisorState
    generation: int
    restart_count: int
    pid: int | None
    last_exit_code: int | None
    event: str


_BASE_ENV = ("PATH", "PATHEXT", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "LANG", "LC_ALL")


def sanitized_environment(extra: Mapping[str, str] | None = None, *, allowed_extra: tuple[str, ...] = ()) -> dict[str, str]:
    """Construct a minimal environment and reject unapproved injected names."""

    result = {key: os.environ[key] for key in _BASE_ENV if key in os.environ}
    for key, value in (extra or {}).items():
        if key not in allowed_extra:
            raise ContractError(f"environment variable {key!r} is not allowlisted")
        if not isinstance(value, str) or "\x00" in value:
            raise ContractError("environment values must be NUL-free strings")
        result[key] = value
    return result


class ProcessSupervisor:
    """Reconcile one process with a bounded restart budget.

    The host owns the polling cadence. This class never starts a background
    thread and never treats process liveness as capability correctness; an MCP
    handshake and capability conformance remain separate gates.
    """

    def __init__(
        self,
        plugin_id: str,
        descriptor: McpStdioDescriptor,
        *,
        max_restarts: int = 3,
        env: Mapping[str, str] | None = None,
        allowed_env: tuple[str, ...] = (),
        spawn: Callable[[dict[str, str]], ManagedProcess] | None = None,
    ) -> None:
        if not plugin_id or max_restarts < 0 or max_restarts > 100:
            raise ContractError("invalid supervisor configuration")
        descriptor.command()
        self.plugin_id = plugin_id
        self.descriptor = descriptor
        self.max_restarts = max_restarts
        self.environment = sanitized_environment(env, allowed_extra=allowed_env)
        self._spawn = spawn or (lambda clean_env: descriptor.spawn(env=clean_env))
        self._process: ManagedProcess | None = None
        self.state = SupervisorState.STOPPED
        self.generation = 0
        self.restart_count = 0
        self.last_exit_code: int | None = None

    def _receipt(self, event: str) -> SupervisorReceipt:
        return SupervisorReceipt(
            plugin_id=self.plugin_id,
            state=self.state,
            generation=self.generation,
            restart_count=self.restart_count,
            pid=self._process.pid if self._process and self._process.poll() is None else None,
            last_exit_code=self.last_exit_code,
            event=event,
        )

    def start(self) -> SupervisorReceipt:
        if self._process and self._process.poll() is None:
            return self._receipt("already-running")
        self._process = self._spawn(dict(self.environment))
        self.generation += 1
        self.state = SupervisorState.RUNNING
        return self._receipt("started")

    def reconcile(self) -> SupervisorReceipt:
        if self._process is None:
            return self.start()
        exit_code = self._process.poll()
        if exit_code is None:
            self.state = SupervisorState.RUNNING
            return self._receipt("healthy-process")
        self.last_exit_code = exit_code
        if self.restart_count >= self.max_restarts:
            self.state = SupervisorState.FAILED
            return self._receipt("restart-budget-exhausted")
        self.restart_count += 1
        self.state = SupervisorState.DEGRADED
        restarted = self.start()
        return SupervisorReceipt(
            plugin_id=restarted.plugin_id,
            state=restarted.state,
            generation=restarted.generation,
            restart_count=self.restart_count,
            pid=restarted.pid,
            last_exit_code=exit_code,
            event="crash-restarted",
        )

    def drain(self, timeout_seconds: float = 5.0) -> SupervisorReceipt:
        if timeout_seconds < 0 or timeout_seconds > 300:
            raise ContractError("invalid drain timeout")
        if self._process is None or self._process.poll() is not None:
            self.state = SupervisorState.STOPPED
            return self._receipt("already-stopped")
        self._process.terminate()
        try:
            self.last_exit_code = self._process.wait(timeout=timeout_seconds)
            event = "drained"
        except (TimeoutError, subprocess.TimeoutExpired):
            self._process.kill()
            self.last_exit_code = self._process.wait(timeout=5.0)
            event = "killed-after-drain-timeout"
        self.state = SupervisorState.STOPPED
        return self._receipt(event)
