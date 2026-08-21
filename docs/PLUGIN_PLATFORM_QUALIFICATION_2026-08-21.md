# Polar Pyro plugin-platform qualification — 2026-08-21

## Verdict

The modular plugin substrate is implemented and reproducible. Core UI surfaces, internet adapters, the compatibility edge, Prose, Retrieval and five target compilers are independent repositories with source pins, manifests, documentation, tests and repository-owned UI modules. This verdict certifies the **plugin boundary**, not autonomous software-production readiness.

## Published release set

| Plugin repository | Exact release | UI boundary | Qualification |
|---|---|---:|---|
| `POLAR-PYRO-CHAT` | `5ba7712a685a97b5c5a364d85fd099138d434e7b` | `web/` | 3 tests pass |
| `POLAR-PYRO-BROWSER` | `db12ad803d3784b69be0b36778cc560685e55abd` | `web/` | 4 tests pass |
| `POLAR-PYRO-CHANGES` | `0176b3a5fbb8c76b709c166d77350d436bc682d8` | `web/` | 4 tests pass |
| `POLAR-PYRO-PLUGIN-SDK` | `6ed9f992e8a5f2cf57fad9c7aaea5c38ec9d3154` | host ABI | 38 tests; all 14 example manifests conform |
| `POLAR-PYRO-OBSCURA-PLUGIN` | `8eaf0bd782b2a7543b5590a488fadb0983281d4e` | `ui/index.html` | 8 wrapper tests; snapshot capability only |
| `POLAR-PYRO-WIGOLO-PLUGIN` | `3202d629accf828a9035d7d98d56706034baeddf` | `ui/index.html` | 3 wrapper tests; upstream blocked |
| `POLAR-PYRO-AGENT-REACH-PLUGIN` | `aa01ddb2b9a47113962722da055a433a853d48d9` | `ui/index.html` | 11 route-policy tests |
| `POLAR-PYRO-OPENCODEX-BRIDGE` | `440e7d856ec0e49e85b75ac88b75b40ce47f9d34` | `ui/index.html` | 6 tests plus live OFF→ON→OFF lifecycle |
| `POLAR-PYRO-WEB-EXPERIENCE-PLUGIN` | `3178a4f657193adfd483bc5080cade44dda33ede` | `ui/index.html` | 47 tests |
| `POLAR-PYRO-ANDROID-PLUGIN` | `73a9bd5a14821b88945da7bf7cd2bc80ddbd4707` | `ui/index.html` | 4 tests |
| `POLAR-PYRO-IOS-PLUGIN` | `f82b3c95a5695b4e2d638e453865c169514702e7` | `ui/index.html` | 4 tests |
| `POLAR-PYRO-WEAR-OS-PLUGIN` | `519e76f8a9bfdeec33a4ece69189e223100e1190` | `ui/index.html` | 4 tests |
| `POLAR-PYRO-WATCH-OS-PLUGIN` | `fa83be943dde3f3ef4ebf3b64ee7e3d78dbde7bc` | `ui/index.html` | 4 tests |
| `POLAR-PYRO-PROSE-ORCHESTRATOR` | `5f79d60da17845e718af786d14fc7d43e8e905a6` | `ui/index.html` | 5 tests; white paper published |
| `SOVEREIGN-RETRIEVAL-ORACLE` | `e10ff9dac6f615ba2687798ffcd4b2b1b3288c82` | `ui/index.html` | 17 tests; live DDGS and TOAM/nomic receipts |

The aggregate run produced 162 passing repository tests. The Polar host integration added another 16 passing focused tests. The DE-PIN Svelte application passed `svelte-check` with zero errors and its production Vite build completed.

## OpenCodex installation proof

DE-PIN owns `infra/polar-pyro/plugins.lock.json`, which pins the bridge at `440e7d856ec0e49e85b75ac88b75b40ce47f9d34`. The installer fetched that Git object, built and installed the wheel, resolved `polar-opencodex-bridge.exe`, emitted a `polar.install-receipt/v1`, and left it disabled. The Polar host then proved an explicit OFF → healthy ON → OFF lifecycle on loopback. The DE-PIN UI shows install, health, endpoint, protocol and provider-warning state.

## Independent UI invariant

Every executable plugin in the release set owns a `web/` or `ui/` module. Adapter and engine manifests contribute those modules through a governed host slot. Each module sends `polar.ui-ready/v1` and receives no direct filesystem, credential, network or memory authority. The host may provide scoped receipts through the versioned message ABI.

## Git and long-horizon invariant

The SDK's Git transaction protocol remains the mutation substrate: a model proposes intent, the broker creates an isolated attempt, engines produce candidates, gates emit typed evidence, and only a passing transaction is promoted. Chat, Browser, Changes and compatibility clients never become alternate mutation paths. TOAM records durable semantic history; Git records project state and reversible candidate history.

## Explicit non-certifications

- Polar host mutation is still fail-closed (`execution_enabled: false`).
- The ten-project autonomy gauntlet is not complete.
- Wigolo upstream remains blocked by failing Windows tests and dependency vulnerabilities.
- Agent Reach is a route compiler, not an MCP server; every backend needs its own grant and pin.
- Obscura is admitted for the qualified snapshot surface, not unrestricted autonomous navigation.
- OpenCodex does not yet claim complete official-client, cancellation or bidirectional tool-stream fidelity.
- SearXNG-primary, Crawl4AI containment, authenticated remote retrieval and full DNS-rebinding controls remain release gates.
- N3IWF/5G transport is an architecture target; no carrier-grade deployment is certified by these local tests.
- Android/iOS/watch target repositories currently certify closed build-plan compilation, not signed-store release.

These residuals must remain visible. None is converted to PASS by the existence of a plugin manifest or UI.
