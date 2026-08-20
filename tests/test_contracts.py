from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from polar_pyro_plugin_sdk.broker import Broker
from polar_pyro_plugin_sdk.models import (
    ContractError,
    EffectClass,
    Grant,
    Invocation,
    PluginManifest,
    PluginState,
    Receipt,
    ReceiptStatus,
)
from polar_pyro_plugin_sdk.registry import PluginRegistry


ROOT = Path(__file__).parents[1]


class StaticAdapter:
    def __init__(self, manifest: PluginManifest, status: ReceiptStatus = ReceiptStatus.PASS, evidence=True):
        self.manifest = manifest
        self.status = status
        self.with_evidence = evidence
        self.calls = 0

    def invoke(self, invocation: Invocation) -> Receipt:
        self.calls += 1
        now = datetime.now(timezone.utc).isoformat()
        output = {"promoted_commit": "b" * 40} if self.status is ReceiptStatus.PASS else None
        return Receipt(
            schema_version="polar.receipt/v1",
            request_id=invocation.request_id,
            plugin_id=invocation.plugin_id,
            capability_id=invocation.capability_id,
            status=self.status,
            manifest_digest=self.manifest.digest,
            args_digest=invocation.args_digest,
            output=output,
            evidence=({"class": "oracle.certificate", "id": "cert-1"},) if self.with_evidence else (),
            started_at=now,
            finished_at=now,
        )


def active_changes():
    manifest = PluginManifest.from_json((ROOT / "examples/manifests/changes.plugin.json").read_text(encoding="utf-8"))
    registry = PluginRegistry()
    registry.register(manifest)
    for state in (PluginState.QUALIFIED, PluginState.INSTALLED, PluginState.ACTIVE):
        registry.transition(manifest.id, manifest.version, state)
    return manifest, registry


def invocation(manifest: PluginManifest, *, args=None, key="idem-1", grants=("grant-1",)) -> Invocation:
    return Invocation(
        schema_version="polar.invocation/v1",
        request_id="request-1",
        session_id="session-1",
        project_id="project-1",
        plugin_id=manifest.id,
        plugin_version=manifest.version,
        manifest_digest=manifest.digest,
        capability_id="changes.promote_candidate",
        idempotency_key=key,
        args=args or {"candidate_commit": "a" * 40, "certificate_id": "cert-1"},
        grant_ids=grants,
        base_commit="0" * 40,
    )


class ContractTests(unittest.TestCase):
    def test_all_example_manifests_parse_and_have_stable_digest(self):
        for path in sorted((ROOT / "examples/manifests").glob("*.json")):
            manifest = PluginManifest.from_json(path.read_text(encoding="utf-8"))
            self.assertEqual(len(manifest.digest), 64, path.name)
            self.assertEqual(manifest.digest, PluginManifest.from_dict(manifest.to_dict()).digest)

    def test_id_version_cannot_drift(self):
        manifest, registry = active_changes()
        changed = dict(manifest.to_dict())
        changed["name"] = "Substituted"
        with self.assertRaisesRegex(ContractError, "different manifest digest"):
            registry.register(PluginManifest.from_dict(changed))

    def test_invalid_lifecycle_transition_is_rejected(self):
        manifest = PluginManifest.from_json((ROOT / "examples/manifests/chat.plugin.json").read_text(encoding="utf-8"))
        registry = PluginRegistry()
        registry.register(manifest)
        with self.assertRaisesRegex(ContractError, "invalid lifecycle"):
            registry.transition(manifest.id, manifest.version, PluginState.ACTIVE)

    def test_mutation_requires_matching_unexpired_grant(self):
        manifest, registry = active_changes()
        broker = Broker(registry)
        with self.assertRaisesRegex(ContractError, "missing grant scopes"):
            broker.invoke(invocation(manifest, grants=()), StaticAdapter(manifest))

    def test_pass_requires_live_evidence(self):
        manifest, registry = active_changes()
        broker = Broker(registry)
        broker.add_grant(self._grant(manifest))
        with self.assertRaisesRegex(ContractError, "non-empty evidence"):
            broker.invoke(invocation(manifest), StaticAdapter(manifest, evidence=False))

    def test_no_result_has_no_promotable_output(self):
        manifest, registry = active_changes()
        broker = Broker(registry)
        broker.add_grant(self._grant(manifest))
        receipt = broker.invoke(invocation(manifest), StaticAdapter(manifest, ReceiptStatus.NO_RESULT))
        self.assertIs(receipt.status, ReceiptStatus.NO_RESULT)
        self.assertIsNone(receipt.output)

    def test_idempotent_replay_does_not_invoke_twice(self):
        manifest, registry = active_changes()
        broker = Broker(registry)
        broker.add_grant(self._grant(manifest))
        adapter = StaticAdapter(manifest)
        first = broker.invoke(invocation(manifest), adapter)
        second = broker.invoke(invocation(manifest), adapter)
        self.assertIs(first, second)
        self.assertEqual(adapter.calls, 1)

    def test_idempotency_key_reuse_with_changed_args_is_rejected(self):
        manifest, registry = active_changes()
        broker = Broker(registry)
        broker.add_grant(self._grant(manifest))
        broker.invoke(invocation(manifest), StaticAdapter(manifest))
        changed = invocation(manifest, args={"candidate_commit": "c" * 40, "certificate_id": "cert-1"})
        with self.assertRaisesRegex(ContractError, "different arguments"):
            broker.invoke(changed, StaticAdapter(manifest))

    def test_manifest_digest_mismatch_is_rejected(self):
        manifest, registry = active_changes()
        broker = Broker(registry)
        bad = replace(invocation(manifest), manifest_digest="0" * 64)
        with self.assertRaisesRegex(ContractError, "manifest digest mismatch"):
            broker.invoke(bad, StaticAdapter(manifest))

    def test_secret_like_argument_is_rejected_before_adapter(self):
        manifest, registry = active_changes()
        broker = Broker(registry)
        broker.add_grant(self._grant(manifest))
        bad = invocation(manifest, args={"candidate_commit": "a" * 40, "certificate_id": "cert-1", "api_token": "leak"})
        with self.assertRaisesRegex(ContractError, "secret-like field"):
            broker.invoke(bad, StaticAdapter(manifest))

    def test_unknown_argument_is_rejected(self):
        manifest, registry = active_changes()
        broker = Broker(registry)
        broker.add_grant(self._grant(manifest))
        bad = invocation(manifest, args={"candidate_commit": "a" * 40, "certificate_id": "cert-1", "extra": 1})
        with self.assertRaisesRegex(ContractError, "unknown fields"):
            broker.invoke(bad, StaticAdapter(manifest))

    @staticmethod
    def _grant(manifest: PluginManifest) -> Grant:
        now = datetime.now(timezone.utc)
        return Grant(
            id="grant-1",
            plugin_id=manifest.id,
            capability_id="changes.promote_candidate",
            project_id="project-1",
            effects=(EffectClass.WORKSPACE_WRITE,),
            scopes=("git.promote",),
            issued_at=now.isoformat(),
            expires_at=(now + timedelta(minutes=5)).isoformat(),
            issuer="test",
        )


if __name__ == "__main__":
    unittest.main()

