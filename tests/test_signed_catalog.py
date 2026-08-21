from __future__ import annotations

import base64
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from polar_pyro_plugin_sdk.models import ContractError, canonical_json
from polar_pyro_plugin_sdk.signed_catalog import verify_catalog_envelope


def envelope(payload: dict) -> tuple[str, dict[str, str]]:
    private = Ed25519PrivateKey.generate()
    public = private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    signature = private.sign(canonical_json(payload).encode("utf-8"))
    value = {
        "schema_version": "polar.catalog-envelope/v1",
        "algorithm": "Ed25519",
        "key_id": "luxeron-release-1",
        "payload": payload,
        "signature": base64.b64encode(signature).decode("ascii"),
    }
    return json.dumps(value), {"luxeron-release-1": base64.b64encode(public).decode("ascii")}


def payload() -> dict:
    return {
        "issued_at": "2026-08-21T00:00:00Z",
        "expires_at": "2026-09-21T00:00:00Z",
        "plugins": [{
            "plugin_id": "dev.luxeron.polar.chat",
            "version": "0.1.0",
            "manifest_digest": "a" * 64,
            "package_tree_sha256": "b" * 64,
            "artifact_uri": "https://plugins.luxeron.dev/chat-0.1.0.tar.zst",
        }],
    }


class SignedCatalogTests(unittest.TestCase):
    now = datetime(2026, 8, 21, 12, tzinfo=timezone.utc)

    def test_valid_catalog_is_verified_and_sorted(self) -> None:
        text, trust = envelope(payload())
        result = verify_catalog_envelope(text, trust, now=self.now)
        self.assertEqual(result.key_id, "luxeron-release-1")
        self.assertEqual(result.entries[0].plugin_id, "dev.luxeron.polar.chat")

    def test_payload_tampering_fails_signature(self) -> None:
        text, trust = envelope(payload())
        value = json.loads(text)
        value["payload"]["plugins"][0]["version"] = "9.9.9"
        with self.assertRaisesRegex(ContractError, "signature"):
            verify_catalog_envelope(json.dumps(value), trust, now=self.now)

    def test_expired_catalog_fails_closed(self) -> None:
        value = payload()
        value["expires_at"] = "2026-08-21T11:00:00Z"
        text, trust = envelope(value)
        with self.assertRaisesRegex(ContractError, "validity window"):
            verify_catalog_envelope(text, trust, now=self.now)

    def test_duplicate_identity_and_insecure_uri_are_rejected(self) -> None:
        value = payload()
        value["plugins"].append(dict(value["plugins"][0]))
        text, trust = envelope(value)
        with self.assertRaisesRegex(ContractError, "duplicated"):
            verify_catalog_envelope(text, trust, now=self.now)
        value = payload()
        value["plugins"][0]["artifact_uri"] = "http://example.com/plugin.zip"
        text, trust = envelope(value)
        with self.assertRaisesRegex(ContractError, "artifact URI"):
            verify_catalog_envelope(text, trust, now=self.now)


if __name__ == "__main__":
    unittest.main()
