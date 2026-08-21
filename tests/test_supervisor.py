from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from polar_pyro_plugin_sdk.mcp import McpStdioDescriptor
from polar_pyro_plugin_sdk.models import ContractError
from polar_pyro_plugin_sdk.supervisor import ProcessSupervisor, SupervisorState, sanitized_environment


class FakeProcess:
    next_pid = 100

    def __init__(self) -> None:
        self.pid = FakeProcess.next_pid
        FakeProcess.next_pid += 1
        self.exit_code = None

    def poll(self):
        return self.exit_code

    def terminate(self):
        self.exit_code = 0

    def kill(self):
        self.exit_code = -9

    def wait(self, timeout=None):
        if self.exit_code is None:
            raise TimeoutError
        return self.exit_code


class SupervisorTests(unittest.TestCase):
    def test_crash_restart_is_bounded(self) -> None:
        processes = []

        def spawn(_env):
            process = FakeProcess()
            processes.append(process)
            return process

        supervisor = ProcessSupervisor("dev.luxeron.test", McpStdioDescriptor("fixture"), max_restarts=1, spawn=spawn)
        started = supervisor.start()
        self.assertEqual(started.state, SupervisorState.RUNNING)
        processes[-1].exit_code = 17
        restarted = supervisor.reconcile()
        self.assertEqual(restarted.event, "crash-restarted")
        self.assertEqual(restarted.last_exit_code, 17)
        processes[-1].exit_code = 18
        failed = supervisor.reconcile()
        self.assertEqual(failed.state, SupervisorState.FAILED)
        self.assertEqual(failed.event, "restart-budget-exhausted")

    def test_drain_is_idempotent(self) -> None:
        supervisor = ProcessSupervisor("dev.luxeron.test", McpStdioDescriptor("fixture"), spawn=lambda _env: FakeProcess())
        supervisor.start()
        self.assertEqual(supervisor.drain().event, "drained")
        self.assertEqual(supervisor.drain().event, "already-stopped")

    def test_environment_is_deny_by_default(self) -> None:
        with self.assertRaisesRegex(ContractError, "not allowlisted"):
            sanitized_environment({"HF_TOKEN": "secret"})
        env = sanitized_environment({"PLUGIN_MODE": "stdio"}, allowed_extra=("PLUGIN_MODE",))
        self.assertEqual(env["PLUGIN_MODE"], "stdio")


if __name__ == "__main__":
    unittest.main()
