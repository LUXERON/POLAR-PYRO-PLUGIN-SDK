"""Deterministic plugin catalog and lifecycle state machine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import ContractError, PluginManifest, PluginState


_TRANSITIONS = {
    PluginState.DISCOVERED: {PluginState.QUALIFIED, PluginState.REMOVED},
    PluginState.QUALIFIED: {PluginState.INSTALLED, PluginState.REMOVED},
    PluginState.INSTALLED: {PluginState.ACTIVE, PluginState.REMOVED},
    PluginState.ACTIVE: {PluginState.DRAINING},
    PluginState.DRAINING: {PluginState.STOPPED},
    PluginState.STOPPED: {PluginState.ACTIVE, PluginState.REMOVED},
    PluginState.REMOVED: set(),
}


@dataclass
class RegisteredPlugin:
    manifest: PluginManifest
    state: PluginState = PluginState.DISCOVERED


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: dict[tuple[str, str], RegisteredPlugin] = {}

    def register(self, manifest: PluginManifest) -> RegisteredPlugin:
        key = (manifest.id, manifest.version)
        existing = self._plugins.get(key)
        if existing and existing.manifest.digest != manifest.digest:
            raise ContractError("plugin id/version is already bound to a different manifest digest")
        if existing:
            return existing
        registered = RegisteredPlugin(manifest)
        self._plugins[key] = registered
        return registered

    def get(self, plugin_id: str, version: str) -> RegisteredPlugin:
        try:
            return self._plugins[(plugin_id, version)]
        except KeyError as exc:
            raise ContractError(f"plugin {plugin_id}@{version} is not registered") from exc

    def transition(self, plugin_id: str, version: str, target: PluginState) -> RegisteredPlugin:
        plugin = self.get(plugin_id, version)
        if target not in _TRANSITIONS[plugin.state]:
            raise ContractError(f"invalid lifecycle transition {plugin.state.value} -> {target.value}")
        plugin.state = target
        return plugin

    def active_for(self, capability_id: str) -> tuple[RegisteredPlugin, ...]:
        matches = []
        for plugin in self._plugins.values():
            if plugin.state is PluginState.ACTIVE and any(cap.id == capability_id for cap in plugin.manifest.capabilities):
                matches.append(plugin)
        return tuple(sorted(matches, key=lambda item: (item.manifest.id, item.manifest.version)))

    def manifests(self) -> Iterable[PluginManifest]:
        return tuple(item.manifest for item in self._plugins.values())

