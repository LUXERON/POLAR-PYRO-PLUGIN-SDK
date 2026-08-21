"""Journaled composition of plugin installation, activation and rollback.

The lower-level store and supervisor deliberately remain independently usable.
This runtime is the host-facing authority boundary: no package becomes active
without a fresh, non-vacuous health probe and every transition enters a
hash-chained local ledger that can be projected into TOAM.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import threading
import uuid
from typing import Any

from .models import ContractError, PluginManifest, canonical_json
from .package_store import InstallReceipt, PackageStore


HealthProbe = Callable[[PluginManifest, Path], Mapping[str, Any]]
EventSink = Callable[[Mapping[str, Any]], None]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class LifecycleJournal:
    """Append-only hash chain for recovery and TOAM projection."""

    def __init__(self, path: Path, *, sink: EventSink | None = None) -> None:
        self.path = path.resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.sink = sink
        self.last_projection_error: str | None = None
        self._lock = threading.Lock()
        records = self.verify()
        self._sequence = len(records)
        self._head = records[-1]["event_sha256"] if records else "0" * 64

    def verify(self) -> tuple[dict[str, Any], ...]:
        if not self.path.exists():
            return ()
        records: list[dict[str, Any]] = []
        previous = "0" * 64
        for number, line in enumerate(self.path.read_text(encoding="utf-8").splitlines(), start=1):
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ContractError(f"invalid lifecycle journal record {number}") from exc
            if not isinstance(record, dict) or record.get("sequence") != number:
                raise ContractError("lifecycle journal sequence is invalid")
            if record.get("previous_sha256") != previous:
                raise ContractError("lifecycle journal hash chain is broken")
            claimed = record.get("event_sha256")
            unsigned = {key: value for key, value in record.items() if key != "event_sha256"}
            actual = hashlib.sha256(canonical_json(unsigned).encode("utf-8")).hexdigest()
            if claimed != actual:
                raise ContractError("lifecycle journal record digest is invalid")
            previous = actual
            records.append(record)
        return tuple(records)

    def append(self, event: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        if not event or any(character in event for character in "\r\n"):
            raise ContractError("invalid lifecycle event")
        with self._lock:
            unsigned: dict[str, Any] = {
                "schema_version": "polar.lifecycle-event/v1",
                "event_id": str(uuid.uuid4()),
                "sequence": self._sequence + 1,
                "timestamp": _utc_now(),
                "event": event,
                "previous_sha256": self._head,
                "payload": dict(payload),
            }
            record = dict(unsigned)
            record["event_sha256"] = hashlib.sha256(canonical_json(unsigned).encode("utf-8")).hexdigest()
            with self.path.open("a", encoding="utf-8", newline="\n") as handle:
                handle.write(canonical_json(record) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            self._sequence += 1
            self._head = record["event_sha256"]
        if self.sink is not None:
            try:
                self.sink(dict(record))
                self.last_projection_error = None
            except Exception as exc:  # the local chain is the recovery authority
                self.last_projection_error = type(exc).__name__
        return record


class PluginRuntime:
    """Fail-closed host lifecycle over the content-addressed package store."""

    def __init__(
        self,
        store: PackageStore,
        journal: LifecycleJournal,
        *,
        health_probes: Mapping[str, HealthProbe] | None = None,
    ) -> None:
        self.store = store
        self.journal = journal
        self.health_probes = dict(health_probes or {})

    def install(self, source: Path, qualification: Mapping[str, Any]) -> InstallReceipt:
        receipt = self.store.install(source, qualification)
        self.journal.append("plugin.installed", receipt.to_dict())
        return receipt

    def _probe(self, manifest: PluginManifest) -> dict[str, Any]:
        probe = self.health_probes.get(manifest.id)
        if probe is None:
            raise ContractError(f"plugin {manifest.id} has no qualified activation probe")
        active = self.store.state(manifest.id).get("active")
        package_path = Path(active["package_path"]) if isinstance(active, dict) and active.get("package_path") else None
        if package_path is None or not package_path.is_dir() or active.get("manifest_digest") != manifest.digest:
            # The new version is not active yet; derive its immutable path from
            # the integrity-checked installed manifest location.
            candidates = list((self.store.root / "packages" / manifest.id / manifest.version).glob(f"{manifest.digest}"))
            if len(candidates) != 1:
                raise ContractError("installed package path did not resolve uniquely")
            package_path = candidates[0]
        result = dict(probe(manifest, package_path))
        evidence = result.get("evidence")
        if result.get("status") != "PASS" or not isinstance(evidence, list) or not evidence:
            self.journal.append("plugin.activation_rejected", {
                "plugin_id": manifest.id,
                "version": manifest.version,
                "manifest_digest": manifest.digest,
                "probe": result,
            })
            raise ContractError("plugin activation probe did not return PASS with evidence")
        self.journal.append("plugin.health_passed", {
            "plugin_id": manifest.id,
            "version": manifest.version,
            "manifest_digest": manifest.digest,
            "probe": result,
        })
        return result

    def activate(self, plugin_id: str, version: str | None = None) -> dict[str, Any]:
        manifest = self.store.manifest(plugin_id, version)
        probe = self._probe(manifest)
        state = self.store.activate(manifest)
        self.journal.append("plugin.activated", {
            "plugin_id": manifest.id,
            "version": manifest.version,
            "manifest_digest": manifest.digest,
            "probe_evidence": probe["evidence"],
            "state": state,
        })
        return state

    def rollback(self, plugin_id: str) -> dict[str, Any]:
        manifest = self.store.rollback_manifest(plugin_id)
        probe = self._probe(manifest)
        state = self.store.activate(manifest)
        self.journal.append("plugin.rolled_back", {
            "plugin_id": manifest.id,
            "version": manifest.version,
            "manifest_digest": manifest.digest,
            "probe_evidence": probe["evidence"],
            "state": state,
        })
        return state

    def remove(self, plugin_id: str, version: str) -> Path:
        manifest = self.store.manifest(plugin_id, version)
        destination = self.store.remove(manifest)
        self.journal.append("plugin.removed", {
            "plugin_id": manifest.id,
            "version": manifest.version,
            "manifest_digest": manifest.digest,
            "recoverable_path": str(destination),
        })
        return destination

    def snapshot(self) -> dict[str, Any]:
        manifests = self.store.installed_manifests()
        states = {manifest.id: self.store.state(manifest.id) for manifest in manifests}
        return {
            "schema_version": "polar.runtime-snapshot/v1",
            "plugins": [
                {
                    "plugin_id": manifest.id,
                    "version": manifest.version,
                    "manifest_digest": manifest.digest,
                    "kind": manifest.kind,
                    "transport": manifest.transport.get("kind"),
                    "active": states[manifest.id].get("active", {}).get("manifest_digest") == manifest.digest,
                }
                for manifest in manifests
            ],
            "journal_head": self.journal.verify()[-1]["event_sha256"] if self.journal.verify() else "0" * 64,
            "projection": {
                "status": "PASS" if self.journal.last_projection_error is None else "NO_RESULT",
                "error_type": self.journal.last_projection_error,
            },
        }
