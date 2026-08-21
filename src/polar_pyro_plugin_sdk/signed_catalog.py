"""Ed25519 verification for immutable local plugin catalog envelopes."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import re
from typing import Any, Mapping
from urllib.parse import urlparse

from .models import ContractError, PluginManifest, canonical_json, sha256_digest


_SHA256 = re.compile(r"^[a-f0-9]{64}$")


def _instant(value: Any, field: str) -> datetime:
    if not isinstance(value, str):
        raise ContractError(f"catalog {field} must be an RFC3339 string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContractError(f"catalog {field} is invalid") from exc
    if parsed.tzinfo is None:
        raise ContractError(f"catalog {field} must include a timezone")
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class CatalogEntry:
    plugin_id: str
    version: str
    manifest_digest: str
    package_tree_sha256: str
    artifact_uri: str


@dataclass(frozen=True)
class VerifiedCatalog:
    key_id: str
    payload_digest: str
    issued_at: str
    expires_at: str
    entries: tuple[CatalogEntry, ...]

    def admit(self, manifest: PluginManifest, package_tree_sha256: str) -> CatalogEntry:
        for entry in self.entries:
            if entry.plugin_id == manifest.id and entry.version == manifest.version:
                if entry.manifest_digest != manifest.digest or entry.package_tree_sha256 != package_tree_sha256:
                    raise ContractError("catalog entry does not bind the admitted package")
                return entry
        raise ContractError("plugin version is absent from the verified catalog")


def verify_catalog_envelope(
    text: str,
    trust_store: Mapping[str, str],
    *,
    now: datetime | None = None,
) -> VerifiedCatalog:
    """Verify a detached Ed25519 signature and validate its frozen payload."""

    try:
        envelope = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ContractError("catalog envelope is not valid JSON") from exc
    if not isinstance(envelope, dict) or envelope.get("schema_version") != "polar.catalog-envelope/v1":
        raise ContractError("unsupported catalog envelope")
    if envelope.get("algorithm") != "Ed25519":
        raise ContractError("catalog algorithm must be Ed25519")
    key_id = envelope.get("key_id")
    payload = envelope.get("payload")
    if not isinstance(key_id, str) or key_id not in trust_store or not isinstance(payload, dict):
        raise ContractError("catalog signing key is not trusted")
    try:
        signature = base64.b64decode(str(envelope.get("signature", "")), validate=True)
        public_key = base64.b64decode(trust_store[key_id], validate=True)
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

        Ed25519PublicKey.from_public_bytes(public_key).verify(signature, canonical_json(payload).encode("utf-8"))
    except ImportError as exc:
        raise ContractError("Ed25519 verification requires the 'signatures' extra") from exc
    except Exception as exc:
        raise ContractError("catalog signature verification failed") from exc

    issued = _instant(payload.get("issued_at"), "issued_at")
    expires = _instant(payload.get("expires_at"), "expires_at")
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if issued > current or expires <= current or expires <= issued:
        raise ContractError("catalog validity window is not current")
    plugins = payload.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        raise ContractError("catalog plugins must be a non-empty array")
    entries: list[CatalogEntry] = []
    identities: set[tuple[str, str]] = set()
    for value in plugins:
        if not isinstance(value, dict):
            raise ContractError("catalog plugin entries must be objects")
        fields = tuple(value.get(name) for name in ("plugin_id", "version", "manifest_digest", "package_tree_sha256", "artifact_uri"))
        if not all(isinstance(item, str) and item for item in fields):
            raise ContractError("catalog plugin entry is incomplete")
        plugin_id, version, manifest_digest, package_digest, artifact_uri = fields
        identity = (plugin_id, version)
        if identity in identities:
            raise ContractError("catalog plugin identity is duplicated")
        identities.add(identity)
        if not _SHA256.fullmatch(manifest_digest) or not _SHA256.fullmatch(package_digest):
            raise ContractError("catalog package digests must be sha256")
        uri = urlparse(artifact_uri)
        loopback = uri.hostname in {"127.0.0.1", "localhost", "::1"}
        if uri.username or uri.password or uri.fragment or not uri.hostname or (uri.scheme != "https" and not (uri.scheme == "http" and loopback)):
            raise ContractError("catalog artifact URI must be credential-free HTTPS or loopback HTTP")
        entries.append(CatalogEntry(plugin_id, version, manifest_digest, package_digest, artifact_uri))
    entries.sort(key=lambda item: (item.plugin_id, item.version))
    return VerifiedCatalog(
        key_id=key_id,
        payload_digest=sha256_digest(payload),
        issued_at=str(payload["issued_at"]),
        expires_at=str(payload["expires_at"]),
        entries=tuple(entries),
    )
