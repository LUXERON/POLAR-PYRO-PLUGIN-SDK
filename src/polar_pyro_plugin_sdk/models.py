"""Dependency-free canonical models used at every plugin trust boundary."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from typing import Any, Mapping


class ContractError(ValueError):
    """Raised when an artifact violates the frozen plugin contract."""


class EffectClass(str, Enum):
    OBSERVE = "observe"
    WORKSPACE_WRITE = "workspace_write"
    EXTERNAL_WRITE = "external_write"
    CREDENTIAL = "credential"
    VALUE_TRANSFER = "value_transfer"


class PluginState(str, Enum):
    DISCOVERED = "discovered"
    QUALIFIED = "qualified"
    INSTALLED = "installed"
    ACTIVE = "active"
    DRAINING = "draining"
    STOPPED = "stopped"
    REMOVED = "removed"


class ReceiptStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NO_RESULT = "NO_RESULT"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _need(data: Mapping[str, Any], name: str, expected: type) -> Any:
    value = data.get(name)
    if not isinstance(value, expected):
        raise ContractError(f"{name} must be {expected.__name__}")
    return value


@dataclass(frozen=True)
class CapabilitySpec:
    id: str
    effect: EffectClass
    input_schema: Mapping[str, Any]
    output_schema: Mapping[str, Any]
    required_grants: tuple[str, ...] = ()
    evidence_classes: tuple[str, ...] = ()
    timeout_ms: int = 30_000

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "CapabilitySpec":
        timeout = data.get("timeout_ms", 30_000)
        if not isinstance(timeout, int) or timeout < 1 or timeout > 3_600_000:
            raise ContractError("timeout_ms must be between 1 and 3600000")
        try:
            effect = EffectClass(_need(data, "effect", str))
        except ValueError as exc:
            raise ContractError(str(exc)) from exc
        return cls(
            id=_need(data, "id", str),
            effect=effect,
            input_schema=_need(data, "input_schema", dict),
            output_schema=_need(data, "output_schema", dict),
            required_grants=tuple(data.get("required_grants", ())),
            evidence_classes=tuple(data.get("evidence_classes", ())),
            timeout_ms=timeout,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "effect": self.effect.value,
            "input_schema": dict(self.input_schema),
            "output_schema": dict(self.output_schema),
            "required_grants": list(self.required_grants),
            "evidence_classes": list(self.evidence_classes),
            "timeout_ms": self.timeout_ms,
        }


@dataclass(frozen=True)
class PluginManifest:
    schema_version: str
    id: str
    version: str
    name: str
    kind: str
    publisher: str
    license: str
    source: Mapping[str, str]
    transport: Mapping[str, Any]
    capabilities: tuple[CapabilitySpec, ...]
    contributions: tuple[Mapping[str, Any], ...] = ()
    compatibility: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "PluginManifest":
        capabilities = tuple(CapabilitySpec.from_dict(item) for item in _need(data, "capabilities", list))
        ids = [cap.id for cap in capabilities]
        if not capabilities or len(ids) != len(set(ids)):
            raise ContractError("capabilities must be non-empty and have unique ids")
        kind = _need(data, "kind", str)
        if kind not in {"ui", "service", "engine", "bridge", "composite"}:
            raise ContractError(f"unsupported plugin kind: {kind}")
        source = _need(data, "source", dict)
        if not all(isinstance(source.get(key), str) and source[key] for key in ("repository", "commit")):
            raise ContractError("source.repository and source.commit are required")
        transport = _need(data, "transport", dict)
        if transport.get("kind") not in {"mcp_stdio", "mcp_http", "http", "native", "iframe"}:
            raise ContractError("unsupported transport.kind")
        return cls(
            schema_version=_need(data, "schema_version", str),
            id=_need(data, "id", str),
            version=_need(data, "version", str),
            name=_need(data, "name", str),
            kind=kind,
            publisher=_need(data, "publisher", str),
            license=_need(data, "license", str),
            source=source,
            transport=transport,
            capabilities=capabilities,
            contributions=tuple(data.get("contributions", ())),
            compatibility=dict(data.get("compatibility", {})),
        )

    @classmethod
    def from_json(cls, text: str) -> "PluginManifest":
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ContractError("manifest root must be an object")
        return cls.from_dict(data)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "id": self.id,
            "version": self.version,
            "name": self.name,
            "kind": self.kind,
            "publisher": self.publisher,
            "license": self.license,
            "source": dict(self.source),
            "transport": dict(self.transport),
            "capabilities": [cap.to_dict() for cap in self.capabilities],
            "contributions": [dict(item) for item in self.contributions],
            "compatibility": dict(self.compatibility),
        }

    @property
    def digest(self) -> str:
        return sha256_digest(self.to_dict())

    def capability(self, capability_id: str) -> CapabilitySpec:
        for capability in self.capabilities:
            if capability.id == capability_id:
                return capability
        raise ContractError(f"unknown capability {capability_id!r} for {self.id}")


@dataclass(frozen=True)
class Grant:
    id: str
    plugin_id: str
    capability_id: str
    project_id: str
    effects: tuple[EffectClass, ...]
    scopes: tuple[str, ...]
    issued_at: str
    expires_at: str
    issuer: str


@dataclass(frozen=True)
class Invocation:
    schema_version: str
    request_id: str
    session_id: str
    project_id: str
    plugin_id: str
    plugin_version: str
    manifest_digest: str
    capability_id: str
    idempotency_key: str
    args: Mapping[str, Any]
    grant_ids: tuple[str, ...]
    base_commit: str | None = None
    deadline: str | None = None
    budget: Mapping[str, int] = field(default_factory=dict)

    @property
    def args_digest(self) -> str:
        return sha256_digest(self.args)


@dataclass(frozen=True)
class Receipt:
    schema_version: str
    request_id: str
    plugin_id: str
    capability_id: str
    status: ReceiptStatus
    manifest_digest: str
    args_digest: str
    output: Mapping[str, Any] | None
    evidence: tuple[Mapping[str, Any], ...]
    started_at: str
    finished_at: str
    error: Mapping[str, Any] | None = None
    git: Mapping[str, Any] | None = None
    upstream: Mapping[str, Any] | None = None

