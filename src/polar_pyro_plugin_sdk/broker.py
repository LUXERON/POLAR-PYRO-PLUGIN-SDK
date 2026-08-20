"""Host-mediated invocation broker. Plugin output is evidence, never authority."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping, Protocol, Any

from .models import (
    ContractError,
    EffectClass,
    Grant,
    Invocation,
    PluginState,
    Receipt,
    ReceiptStatus,
)
from .registry import PluginRegistry
from .schema import validate


class InvocationAdapter(Protocol):
    def invoke(self, invocation: Invocation) -> Receipt: ...


@dataclass(frozen=True)
class BrokerPolicy:
    allowed_transport_kinds: tuple[str, ...] = ("mcp_stdio", "mcp_http", "http", "native", "iframe")
    deny_secret_fields: tuple[str, ...] = ("password", "secret", "token", "api_key", "cookie", "authorization")
    require_evidence_for_pass: bool = True


class Broker:
    def __init__(self, registry: PluginRegistry, policy: BrokerPolicy | None = None) -> None:
        self.registry = registry
        self.policy = policy or BrokerPolicy()
        self._grants: dict[str, Grant] = {}
        self._receipts: dict[str, Receipt] = {}

    def add_grant(self, grant: Grant) -> None:
        self._grants[grant.id] = grant

    def _reject_secrets(self, value: Any, path: str = "$") -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                lowered = key.lower()
                if any(fragment in lowered for fragment in self.policy.deny_secret_fields):
                    raise ContractError(f"secret-like field rejected at {path}.{key}")
                self._reject_secrets(child, f"{path}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                self._reject_secrets(child, f"{path}[{index}]")

    def _authorize(self, invocation: Invocation, effect: EffectClass, required: tuple[str, ...]) -> None:
        if effect is EffectClass.OBSERVE and not required:
            return
        matching: set[str] = set()
        now = datetime.now(timezone.utc)
        for grant_id in invocation.grant_ids:
            grant = self._grants.get(grant_id)
            if not grant:
                continue
            expires = datetime.fromisoformat(grant.expires_at.replace("Z", "+00:00"))
            if (
                grant.plugin_id == invocation.plugin_id
                and grant.capability_id == invocation.capability_id
                and grant.project_id == invocation.project_id
                and effect in grant.effects
                and expires > now
            ):
                matching.update(grant.scopes)
        missing = set(required) - matching
        if missing:
            raise ContractError(f"missing grant scopes: {sorted(missing)}")

    def invoke(self, invocation: Invocation, adapter: InvocationAdapter) -> Receipt:
        prior = self._receipts.get(invocation.idempotency_key)
        if prior:
            if prior.args_digest != invocation.args_digest:
                raise ContractError("idempotency key was reused with different arguments")
            return prior
        registered = self.registry.get(invocation.plugin_id, invocation.plugin_version)
        if registered.state is not PluginState.ACTIVE:
            raise ContractError("plugin is not active")
        manifest = registered.manifest
        if invocation.manifest_digest != manifest.digest:
            raise ContractError("manifest digest mismatch")
        if manifest.transport.get("kind") not in self.policy.allowed_transport_kinds:
            raise ContractError("transport is denied by broker policy")
        capability = manifest.capability(invocation.capability_id)
        self._reject_secrets(invocation.args)
        validate(invocation.args, capability.input_schema)
        self._authorize(invocation, capability.effect, capability.required_grants)
        receipt = adapter.invoke(invocation)
        if receipt.request_id != invocation.request_id or receipt.args_digest != invocation.args_digest:
            raise ContractError("receipt does not bind to invocation")
        if receipt.manifest_digest != manifest.digest:
            raise ContractError("receipt manifest digest mismatch")
        if receipt.status is ReceiptStatus.PASS:
            if receipt.output is None:
                raise ContractError("PASS receipt requires output")
            validate(receipt.output, capability.output_schema)
            if self.policy.require_evidence_for_pass and not receipt.evidence:
                raise ContractError("PASS receipt requires non-empty evidence")
        elif receipt.output is not None:
            raise ContractError("FAIL and NO_RESULT receipts cannot carry promoted output")
        self._receipts[invocation.idempotency_key] = receipt
        return receipt

