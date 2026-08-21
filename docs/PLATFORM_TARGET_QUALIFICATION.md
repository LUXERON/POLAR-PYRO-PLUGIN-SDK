# Polar Pyro Platform Target Qualification

**Date:** 2026-08-21  
**Scope:** closed compiler, plugin ABI, live discovery, DE-PIN host integration and deterministic source qualification  
**Verdict:** `SOURCE_PINNED`; not yet `RELEASE_CERTIFIED`

## Exact target set

| Target | Plugin | Pinned commit | Native capability |
| --- | --- | --- | --- |
| Web | `dev.luxeron.engine.web-experience` | `b8ee1ccbde972142ca0af319bff659442e8cf2fa` | `web.compile_experience` |
| Android | `dev.luxeron.engine.android` | `e6d0e4dbfa51310ad86cd0c135970d6a6c92fdbc` | `android.compile_build_plan` |
| iOS | `dev.luxeron.engine.ios` | `1e2b20722bb5404d1c73de671321487ec4437df4` | `ios.compile_build_plan` |
| Wear OS | `dev.luxeron.engine.wear-os` | `466bb43ea58f1f68895bfafd193f809bf913584d` | `wear.compile_build_plan` |
| Apple Watch | `dev.luxeron.engine.watch-os` | `3759589df307d79e61e24e6e7222fa64d919cc25` | `watch.compile_build_plan` |

## Replayed gates

| Gate | Result |
| --- | --- |
| Plugin SDK unit/lifecycle suite | 38 passed |
| Web Experience compiler/renderer suite | 48 passed |
| Android closed compiler suite | 4 passed |
| iOS closed compiler suite | 4 passed |
| Wear OS closed compiler suite | 4 passed |
| Apple Watch closed compiler suite | 4 passed |
| Polar host, workspace and plugin binding suite | 25 passed |
| SDK manifest conformance, all five targets | PASS |
| Clean Polar host live discovery | all five configured, source pinned, exact commits matched |
| DE-PIN Svelte diagnostics | 0 errors; 3 unrelated pre-existing warnings |
| DE-PIN production Vite build | PASS; pre-existing chunk-size warning retained |
| LUXERON repository directory | 493 repositories, 48 sections, coverage PASS |

## Authority invariants now enforced

1. A session selects a target by frozen plugin ID, not by executable name authored by Qwen.
2. The host binds plugin version, adapter commit, capability set and descriptor hash into the session receipt before inference.
3. An unlisted target is rejected before the model runs.
4. Android and iOS bind to shared Web Experience semantics rather than forking the product ontology.
5. Wear OS rejects Tauri/WebView and uses a native Kotlin/Compose surface algebra.
6. Apple Watch rejects React/Tauri/WebView/embedded Axum and uses native SwiftUI/WidgetKit/HealthKit authority.
7. Axum remains a remote service boundary on watches and a deliberate network boundary on phone targets.
8. Compiler PASS is non-vacuous and evidence-bearing but never promotes itself to a release verdict.

## 5G and service boundary

The plugin ABI is transport-neutral. An N3IWF/5G edge deployment may move an MCP/HTTP adapter, retrieval service, Axum backend or build worker across the network, but it does not change authorization. Tenant/session binding, manifest digest, effect grant, idempotency key, evidence receipt, Git candidate and oracle verdict remain mandatory. UI metadata never becomes execution authority.

## Remaining release gates

The following are intentionally unresolved and therefore return `NO_RESULT` if requested today:

- owned Android/iOS/Wear/watchOS source renderers beyond the planning compilers;
- Android Gradle/emulator and physical-device qualification;
- macOS/Xcode worker, Simulator/device, signing and TestFlight qualification;
- Wear OS rotary, Tile, complication, energy and OEM-device evidence;
- Apple Watch WidgetKit, HealthKit, lifecycle, energy and device evidence;
- full Euclid/SAE/DEMIURGE/LOOM/ISTHMUS execution for generated platform candidates;
- critical mutation suites for every generated platform seam;
- unattended difficult application gauntlets and human UX approval.

No repository or host response may label these target plugins production-ready until those release gates pass for an exact candidate commit.
