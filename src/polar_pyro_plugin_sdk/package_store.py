"""Transactional, content-addressed plugin installation and rollback.

The store deliberately accepts only an already staged local package. Fetching,
archive expansion, signature verification and vulnerability scanning happen
outside this boundary; their PASS attestation is required here.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import uuid
from typing import Any, Mapping

from .models import ContractError, PluginManifest, PluginState, canonical_json
from .registry import PluginRegistry


_SAFE_SEGMENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(canonical_json(value) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def package_tree_digest(directory: Path) -> str:
    """Hash regular files by relative POSIX path and byte content.

    Symlinks and junctions are rejected so a package cannot smuggle content
    outside its admitted staging directory during the copy.
    """

    root = directory.resolve(strict=True)
    if not root.is_dir():
        raise ContractError("package source must be a directory")
    entries: list[dict[str, str]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        if path.is_symlink() or (hasattr(os.path, "isjunction") and os.path.isjunction(path)):
            raise ContractError("package source cannot contain symlinks or junctions")
        if path.is_dir():
            continue
        if not path.is_file():
            raise ContractError("package source can contain regular files only")
        relative = path.relative_to(root).as_posix()
        if relative == ".git" or relative.startswith(".git/"):
            raise ContractError("package source cannot contain Git metadata")
        entries.append({"path": relative, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    if not entries:
        raise ContractError("package source cannot be empty")
    return hashlib.sha256(canonical_json(entries).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class InstallReceipt:
    plugin_id: str
    version: str
    manifest_digest: str
    package_tree_sha256: str
    suite_digest: str
    installed_at: str
    package_path: str

    def to_dict(self) -> dict[str, str]:
        return {
            "schema_version": "polar.install-receipt/v1",
            "plugin_id": self.plugin_id,
            "version": self.version,
            "manifest_digest": self.manifest_digest,
            "package_tree_sha256": self.package_tree_sha256,
            "suite_digest": self.suite_digest,
            "installed_at": self.installed_at,
            "package_path": self.package_path,
        }


class PackageStore:
    """Content-addressed package store with atomic activation and rollback."""

    def __init__(self, root: Path, registry: PluginRegistry | None = None) -> None:
        self.root = root.resolve()
        self.registry = registry or PluginRegistry()
        for name in ("packages", "state", ".staging", "trash"):
            (self.root / name).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _segment(value: str, label: str) -> str:
        if not _SAFE_SEGMENT.fullmatch(value):
            raise ContractError(f"unsafe {label}")
        return value

    def _package_path(self, manifest: PluginManifest) -> Path:
        plugin_id = self._segment(manifest.id, "plugin id")
        version = self._segment(manifest.version, "plugin version")
        return self.root / "packages" / plugin_id / version / manifest.digest

    def _state_path(self, plugin_id: str) -> Path:
        return self.root / "state" / f"{self._segment(plugin_id, 'plugin id')}.json"

    def _read_state(self, plugin_id: str) -> dict[str, Any]:
        path = self._state_path(plugin_id)
        if not path.exists():
            return {"schema_version": "polar.package-state/v1", "plugin_id": plugin_id, "active": None, "history": []}
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict) or value.get("plugin_id") != plugin_id or not isinstance(value.get("history"), list):
            raise ContractError("invalid package activation state")
        return value

    def install(self, source: Path, qualification: Mapping[str, Any]) -> InstallReceipt:
        source = source.resolve(strict=True)
        manifest_path = source / "plugin.manifest.json"
        if not manifest_path.is_file():
            raise ContractError("package is missing plugin.manifest.json")
        manifest = PluginManifest.from_json(manifest_path.read_text(encoding="utf-8"))
        tree_digest = package_tree_digest(source)
        suite_digest = qualification.get("suite_digest")
        if qualification.get("status") != "PASS":
            raise ContractError("package qualification must PASS")
        if qualification.get("manifest_digest") != manifest.digest:
            raise ContractError("qualification manifest digest mismatch")
        if qualification.get("package_tree_sha256") != tree_digest:
            raise ContractError("qualification package digest mismatch")
        if not isinstance(suite_digest, str) or not re.fullmatch(r"[a-f0-9]{64}", suite_digest):
            raise ContractError("qualification suite_digest must be sha256")

        target = self._package_path(manifest)
        receipt_path = target / ".polar-install-receipt.json"
        if target.exists():
            if not receipt_path.is_file():
                raise ContractError("existing package has no install receipt")
            stored = json.loads(receipt_path.read_text(encoding="utf-8"))
            if stored.get("package_tree_sha256") != tree_digest or stored.get("manifest_digest") != manifest.digest:
                raise ContractError("existing package receipt does not match admitted content")
            return InstallReceipt(
                plugin_id=manifest.id,
                version=manifest.version,
                manifest_digest=manifest.digest,
                package_tree_sha256=tree_digest,
                suite_digest=str(stored["suite_digest"]),
                installed_at=str(stored["installed_at"]),
                package_path=str(target),
            )

        stage = self.root / ".staging" / uuid.uuid4().hex
        try:
            shutil.copytree(source, stage)
            if package_tree_digest(stage) != tree_digest:
                raise ContractError("staged package digest changed during copy")
            receipt = InstallReceipt(
                plugin_id=manifest.id,
                version=manifest.version,
                manifest_digest=manifest.digest,
                package_tree_sha256=tree_digest,
                suite_digest=suite_digest,
                installed_at=_utc_now(),
                package_path=str(target),
            )
            _atomic_json(stage / ".polar-install-receipt.json", receipt.to_dict())
            target.parent.mkdir(parents=True, exist_ok=True)
            os.replace(stage, target)
        finally:
            if stage.exists():
                shutil.rmtree(stage)

        registered = self.registry.register(manifest)
        if registered.state is PluginState.DISCOVERED:
            self.registry.transition(manifest.id, manifest.version, PluginState.QUALIFIED)
            self.registry.transition(manifest.id, manifest.version, PluginState.INSTALLED)
        return receipt

    def activate(self, manifest: PluginManifest) -> dict[str, Any]:
        target = self._package_path(manifest)
        receipt_path = target / ".polar-install-receipt.json"
        if not receipt_path.is_file():
            raise ContractError("plugin package is not installed")
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        if receipt.get("manifest_digest") != manifest.digest:
            raise ContractError("installed manifest digest mismatch")

        state = self._read_state(manifest.id)
        next_active = {"version": manifest.version, "manifest_digest": manifest.digest, "package_path": str(target)}
        current = state.get("active")
        if current == next_active:
            return state

        if current:
            history = [current, *[item for item in state["history"] if item != current and item != next_active]]
        else:
            history = [item for item in state["history"] if item != next_active]
        next_state = {
            "schema_version": "polar.package-state/v1",
            "plugin_id": manifest.id,
            "active": next_active,
            "history": history,
            "activated_at": _utc_now(),
        }
        _atomic_json(self._state_path(manifest.id), next_state)

        registered = self.registry.register(manifest)
        if registered.state is PluginState.DISCOVERED:
            self.registry.transition(manifest.id, manifest.version, PluginState.QUALIFIED)
            self.registry.transition(manifest.id, manifest.version, PluginState.INSTALLED)
        for prior in tuple(self.registry.manifests()):
            if prior.id == manifest.id and prior.version != manifest.version:
                item = self.registry.get(prior.id, prior.version)
                if item.state is PluginState.ACTIVE:
                    self.registry.transition(prior.id, prior.version, PluginState.DRAINING)
                    self.registry.transition(prior.id, prior.version, PluginState.STOPPED)
        item = self.registry.get(manifest.id, manifest.version)
        if item.state in {PluginState.INSTALLED, PluginState.STOPPED}:
            self.registry.transition(manifest.id, manifest.version, PluginState.ACTIVE)
        return next_state

    def rollback(self, plugin_id: str) -> dict[str, Any]:
        state = self._read_state(plugin_id)
        history = state.get("history", [])
        if not history:
            raise ContractError("no rollback target is available")
        target = history[0]
        package_path = Path(str(target.get("package_path", "")))
        manifest_path = package_path / "plugin.manifest.json"
        if not manifest_path.is_file():
            raise ContractError("rollback target package is unavailable")
        return self.activate(PluginManifest.from_json(manifest_path.read_text(encoding="utf-8")))

    def remove(self, manifest: PluginManifest) -> Path:
        state = self._read_state(manifest.id)
        active = state.get("active")
        if isinstance(active, dict) and active.get("manifest_digest") == manifest.digest:
            raise ContractError("active plugin must be rolled back or stopped before removal")
        target = self._package_path(manifest)
        if not target.is_dir():
            raise ContractError("plugin package is not installed")
        trash = self.root / "trash" / manifest.id / f"{manifest.version}-{manifest.digest}-{uuid.uuid4().hex}"
        trash.parent.mkdir(parents=True, exist_ok=True)
        os.replace(target, trash)
        return trash
