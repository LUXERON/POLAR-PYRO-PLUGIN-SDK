from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from polar_pyro_plugin_sdk.models import ContractError, PluginManifest, PluginState
from polar_pyro_plugin_sdk.package_store import PackageStore, package_tree_digest


def write_package(root: Path, version: str, body: str = "export default 1") -> PluginManifest:
    manifest = {
        "schema_version": "polar.plugin/v1",
        "id": "dev.luxeron.fixture",
        "version": version,
        "name": "Fixture",
        "kind": "ui",
        "publisher": "LUXERON",
        "license": "MIT",
        "source": {"repository": "https://github.com/LUXERON/FIXTURE", "commit": "a" * 40},
        "transport": {"kind": "iframe", "url": "https://plugins.example/fixture"},
        "capabilities": [{
            "id": "fixture.observe",
            "effect": "observe",
            "input_schema": {"type": "object"},
            "output_schema": {"type": "object"},
        }],
    }
    root.mkdir(parents=True)
    (root / "plugin.manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (root / "index.js").write_text(body, encoding="utf-8")
    return PluginManifest.from_dict(manifest)


def attestation(source: Path, manifest: PluginManifest) -> dict[str, str]:
    return {
        "status": "PASS",
        "manifest_digest": manifest.digest,
        "package_tree_sha256": package_tree_digest(source),
        "suite_digest": hashlib.sha256(b"qualified-suite").hexdigest(),
    }


class PackageStoreTests(unittest.TestCase):
    def test_install_activate_upgrade_and_rollback(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source_one = base / "source-one"
            source_two = base / "source-two"
            manifest_one = write_package(source_one, "1.0.0")
            manifest_two = write_package(source_two, "1.1.0", "export default 2")
            store = PackageStore(base / "store")

            receipt_one = store.install(source_one, attestation(source_one, manifest_one))
            self.assertTrue(Path(receipt_one.package_path).is_dir())
            self.assertEqual(store.registry.get(manifest_one.id, manifest_one.version).state, PluginState.INSTALLED)
            store.activate(manifest_one)
            self.assertEqual(store.registry.get(manifest_one.id, manifest_one.version).state, PluginState.ACTIVE)

            store.install(source_two, attestation(source_two, manifest_two))
            upgraded = store.activate(manifest_two)
            self.assertEqual(upgraded["active"]["version"], "1.1.0")
            self.assertEqual(store.registry.get(manifest_one.id, manifest_one.version).state, PluginState.STOPPED)
            rolled_back = store.rollback(manifest_one.id)
            self.assertEqual(rolled_back["active"]["version"], "1.0.0")
            self.assertEqual(store.registry.get(manifest_one.id, manifest_one.version).state, PluginState.ACTIVE)

    def test_install_is_idempotent_and_tampered_attestation_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "source"
            manifest = write_package(source, "1.0.0")
            store = PackageStore(base / "store")
            proof = attestation(source, manifest)
            first = store.install(source, proof)
            second = store.install(source, proof)
            self.assertEqual(first.installed_at, second.installed_at)
            bad = dict(proof, package_tree_sha256="0" * 64)
            with self.assertRaisesRegex(ContractError, "package digest mismatch"):
                PackageStore(base / "other-store").install(source, bad)

    def test_active_removal_is_denied_and_inactive_removal_is_recoverable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source_one = base / "source-one"
            source_two = base / "source-two"
            manifest_one = write_package(source_one, "1.0.0")
            manifest_two = write_package(source_two, "1.1.0", "export default 2")
            store = PackageStore(base / "store")
            store.install(source_one, attestation(source_one, manifest_one))
            store.activate(manifest_one)
            with self.assertRaisesRegex(ContractError, "active plugin"):
                store.remove(manifest_one)
            store.install(source_two, attestation(source_two, manifest_two))
            store.activate(manifest_two)
            trash = store.remove(manifest_one)
            self.assertTrue(trash.is_dir())
            self.assertIn("trash", trash.parts)

    def test_symlink_package_content_is_denied(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "source"
            write_package(source, "1.0.0")
            outside = base / "outside.txt"
            outside.write_text("secret", encoding="utf-8")
            link = source / "escape.txt"
            try:
                link.symlink_to(outside)
            except OSError:
                self.skipTest("symlink creation is unavailable")
            with self.assertRaisesRegex(ContractError, "symlinks"):
                package_tree_digest(source)


if __name__ == "__main__":
    unittest.main()
