"""Command-line manifest conformance check."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .models import ContractError, PluginManifest


def check_manifest(path: Path) -> dict[str, object]:
    manifest = PluginManifest.from_json(path.read_text(encoding="utf-8"))
    return {
        "status": "PASS",
        "plugin": f"{manifest.id}@{manifest.version}",
        "manifest_digest": manifest.digest,
        "capabilities": [cap.id for cap in manifest.capabilities],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(check_manifest(args.manifest), indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, ContractError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

