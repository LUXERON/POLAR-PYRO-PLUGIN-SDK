"""MCP transport descriptors with shell-free process construction."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Sequence

from .models import ContractError


@dataclass(frozen=True)
class McpStdioDescriptor:
    executable: str
    args: tuple[str, ...] = ()
    cwd: str | None = None

    def command(self) -> tuple[str, ...]:
        if not self.executable or any(char in self.executable for char in "\r\n"):
            raise ContractError("invalid MCP executable")
        if any("\x00" in arg or "\r" in arg or "\n" in arg for arg in self.args):
            raise ContractError("invalid MCP argument")
        if self.cwd is not None and not Path(self.cwd).is_absolute():
            raise ContractError("MCP cwd must be absolute")
        return (self.executable, *self.args)

    def spawn(self, *, env: dict[str, str] | None = None) -> subprocess.Popen[bytes]:
        return subprocess.Popen(
            self.command(),
            cwd=self.cwd,
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )


def require_tool_subset(advertised: Sequence[str], allowed: Sequence[str]) -> tuple[str, ...]:
    denied = sorted(set(advertised) - set(allowed))
    if denied:
        raise ContractError(f"MCP advertised undeclared tools: {denied}")
    return tuple(sorted(set(advertised)))

