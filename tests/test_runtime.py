from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from polar_pyro_plugin_sdk.models import ContractError
from polar_pyro_plugin_sdk.package_store import PackageStore
from polar_pyro_plugin_sdk.runtime import LifecycleJournal, PluginRuntime

from test_package_store import attestation, write_package


class RuntimeTests(unittest.TestCase):
    @staticmethod
    def healthy(_manifest, package_path: Path) -> dict:
        return {
            "status": "PASS",
            "evidence": [{"class": "fixture.health", "package_path": str(package_path)}],
        }

    def test_install_activate_upgrade_and_probe_gated_rollback_are_journaled(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            one = base / "one"
            two = base / "two"
            manifest_one = write_package(one, "1.0.0")
            manifest_two = write_package(two, "1.1.0", "export default 2")
            journal = LifecycleJournal(base / "lifecycle.jsonl")
            runtime = PluginRuntime(
                PackageStore(base / "store"),
                journal,
                health_probes={manifest_one.id: self.healthy},
            )

            runtime.install(one, attestation(one, manifest_one))
            runtime.activate(manifest_one.id, manifest_one.version)
            runtime.install(two, attestation(two, manifest_two))
            runtime.activate(manifest_two.id, manifest_two.version)
            state = runtime.rollback(manifest_one.id)

            self.assertEqual(state["active"]["version"], "1.0.0")
            records = journal.verify()
            self.assertEqual([item["sequence"] for item in records], list(range(1, len(records) + 1)))
            self.assertEqual(records[-1]["event"], "plugin.rolled_back")
            self.assertEqual(runtime.snapshot()["journal_head"], records[-1]["event_sha256"])

    def test_missing_or_vacuous_health_probe_cannot_activate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "source"
            manifest = write_package(source, "1.0.0")
            store = PackageStore(base / "store")
            runtime = PluginRuntime(store, LifecycleJournal(base / "lifecycle.jsonl"))
            runtime.install(source, attestation(source, manifest))
            with self.assertRaisesRegex(ContractError, "no qualified activation probe"):
                runtime.activate(manifest.id, manifest.version)
            self.assertIsNone(store.state(manifest.id)["active"])

            runtime.health_probes[manifest.id] = lambda *_: {"status": "PASS", "evidence": []}
            with self.assertRaisesRegex(ContractError, "PASS with evidence"):
                runtime.activate(manifest.id, manifest.version)
            self.assertEqual(runtime.journal.verify()[-1]["event"], "plugin.activation_rejected")
            self.assertIsNone(store.state(manifest.id)["active"])

    def test_journal_tampering_is_detected_on_recovery(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "lifecycle.jsonl"
            journal = LifecycleJournal(path)
            journal.append("plugin.fixture", {"status": "PASS"})
            record = json.loads(path.read_text(encoding="utf-8"))
            record["payload"]["status"] = "FAIL"
            path.write_text(json.dumps(record) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ContractError, "digest"):
                LifecycleJournal(path)


if __name__ == "__main__":
    unittest.main()
