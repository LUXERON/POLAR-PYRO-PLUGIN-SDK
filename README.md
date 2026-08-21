# Polar Pyro Plugin SDK

Polar Pyro is not a single IDE binary with a growing pile of privileged imports. It is a governed host for independently versioned UI surfaces, services, bridges, and deterministic domain engines. This repository defines the language-neutral contract that lets those parts be installed, swapped, tested, upgraded, and removed without surrendering the neurosymbolic trust model.

The Python package is a zero-runtime-dependency reference implementation of the host rules. The JSON Schemas are the normative cross-language ABI. A Rust, Kotlin, Swift, TypeScript, or Python plugin is compatible when it emits the same canonical artifacts and passes the same conformance cases.

## North star

A user should be able to open Polar Pyro, attach a local directory or GitHub repository, ask for a difficult software system in natural language, and let a small untrusted model coordinate deterministic engines for hours or days. Every mutation occurs in an isolated Git transaction, every effect is explicitly granted, every successful result has live evidence, and the canonical branch changes only after an independent oracle issues a certificate.

Plugins extend that machine without becoming trusted merely because they speak MCP.

## What this SDK controls

| Boundary | Frozen artifact | Rule |
|---|---|---|
| Discovery | `plugin-manifest.schema.json` | Identity, version, upstream commit, license, transport, capabilities, UI contributions |
| Invocation | `invocation.schema.json` | Project/session binding, manifest digest, idempotency, base commit, budget, grants |
| Authorization | `grant.schema.json` | Capability-specific, project-specific, effect-specific, expiring authority |
| Result | `receipt.schema.json` | `PASS \| FAIL \| NO_RESULT`, evidence, hashes, Git/provenance binding |
| Mutation | Git transaction protocol | Clean base → worktree → candidate commit → oracle → fast-forward promotion |
| UI | contribution slots | Sandboxed surface mounted by the host rather than importing private host stores |
| Network | local or authenticated gateway | MCP is a transport; identity, policy, tenancy, and evidence remain host concerns |

`PASS`, `FAIL`, and `NO_RESULT` are deliberately separate. A timeout, unavailable backend, absent evidence, or unsupported domain is not success and cannot be treated as truthy.

## Plugin anatomy

A manifest declares:

- stable reverse-DNS plugin ID and semantic version;
- exact source repository and commit, plus upstream provenance for adapters;
- SPDX-compatible license expression or explicit distribution note;
- one transport: `mcp_stdio`, `mcp_http`, `http`, `native`, or sandboxed `iframe`;
- closed capabilities with input/output schemas;
- effect class: `observe`, `workspace_write`, `external_write`, `credential`, or `value_transfer`;
- grant scopes and evidence classes required for a valid `PASS`;
- optional host contribution slots such as `session.tab` or `settings.integration`.

The host freezes the canonical manifest digest at qualification. Runtime MCP discovery may prove that a declared tool exists, but it cannot add authority. Undeclared tools are rejected.

## Lifecycle

```text
DISCOVERED → QUALIFIED → INSTALLED → ACTIVE → DRAINING → STOPPED → REMOVED
                                         ↑          │
                                         └──────────┘
```

Qualification includes schema validation, source/license verification, dependency and vulnerability review, transport probe, capability conformance, poison tests, and an effect-policy review. Updating a plugin creates a new immutable `(id, version, manifest digest)` tuple and reruns qualification. It never mutates an already-qualified tuple.

## Invocation path

```text
Qwen 0.6B proposal
      │ closed IntentIR; no credentials or executable commands
      ▼
Capability registry ── no unique compatible capability ──► ABSTAIN
      │
      ▼
Policy broker ─ manifest digest · schema · grant · budget · idempotency
      │
      ▼
Transport adapter ─ MCP / HTTP / native / iframe RPC
      │
      ▼
Typed receipt ─ evidence · upstream commit · output hash · Git refs
      │
      ▼
Domain oracle / DEMIURGE ─ PASS ► certificate ► promotion
                         └ FAIL/NO_RESULT ► typed residual or abstention
```

The model chooses neither the executable nor arbitrary tool names. It emits a closed intent. The deterministic registry selects the one compatible capability or abstains. This keeps the 0.6B model useful as an intent-to-spec transducer without making it an authority.

## Git as the long-horizon substrate

Complex game engines, stateful products, and thousand-file repairs cannot safely live only in chat state. Every mutation-capable invocation binds to a base commit and runs in an attempt-scoped worktree:

1. Require a clean canonical checkout and record `base_commit`.
2. Create `polar-pyro/<session>/<attempt>` in a confined transaction root.
3. Let the plugin edit only that worktree.
4. Record the binary-safe diff and candidate commit.
5. Run tests, mutation adequacy, DEMIURGE, or the registered domain oracle.
6. Issue a certificate bound to manifest, invocation, candidate commit, oracle version, and evidence.
7. Fast-forward only when canonical `HEAD` still equals `base_commit`.
8. If `HEAD` moved, rebase/replay and rerun verification; never silently merge stale proof.
9. Journal the attempt in TOAM and retain Git as the canonical source of software truth.

The reference `GitWorkspaceTransaction` implements the core clean-base, confined-worktree, candidate-commit, and fast-forward invariants. Production hosts should additionally sign certificates and enforce OS-level filesystem and process isolation.

## Core Polar Pyro surfaces

Chat, Browser, and Changes are plugins, not special cases:

- **Chat** compiles natural-language requests into closed `TaskIntentIR`, `AppIntentIR`, and `ChangeIntentIR` artifacts. It can be replaced without replacing the broker.
- **Browser** contributes a `session.tab` surface and delegates execution/inspection to qualified browser capabilities.
- **Changes** renders Git receipts and diffs, opens the code-overlay inspector, and requests promotion. It cannot self-certify a candidate.

The initial UI isolation boundary is a sandboxed iframe plus a versioned `postMessage` RPC envelope. Trusted first-party surfaces may later use signed web components, but direct imports from host-private stores are not part of the ABI.

## Internet system integration

These systems are complementary:

| Plugin | Assigned role | Default security posture |
|---|---|---|
| Obscura adapter | Low-footprint headless browser execution and page snapshots | Private networks denied; file access denied; cookies/storage privileged |
| Chrome DevTools MCP adapter | Inspection, console/network evidence, performance, interactive debugging | Explicit target allowlist; local debug endpoints only |
| Wigolo adapter | Search, fetch, crawl, extraction, ranking, source spans | Separate process due to AGPL; fetched content is untrusted data |
| Agent Reach adapter | Channel detection and live backend fallback for public social/video/RSS sources | Personal browser profiles, installs, and cookies denied without a specific grant |
| Sovereign Retrieval Oracle | Authority policy, ranking, provenance, transient TOAM, grounding, purge/promotion | Fail closed; only grounded facts can enter durable memory |

The resulting pipeline is:

```text
query → channel/router → search/fetch/browser backends → quarantine
      → authority/ranking/chunking → transient TOAM → semantic recall
      → bounded synthesis → deterministic grounding → purge
      → certified promotion
```

## OpenCodex compatibility edge

The OpenCodex-derived bridge provides loopback OpenAI Responses and Anthropic Messages compatibility so Codex- and Claude-compatible clients can submit work to the Polar Pyro synthesis platform. It is disabled by default and requires an explicit user toggle. Binding beyond loopback requires authenticated transport.

The bridge translates request/stream formats only. It does not turn provider text into executable tools, skip closed intent compilation, or bypass Git/oracle promotion. Distribution must also show the upstream warning that third-party routing can conflict with provider terms; credentials remain in the user-controlled compatibility process and are never copied into model context, receipts, or TOAM.

## Domain engines are plugins too

The official catalog reserves capability families for DEMIURGE, LOOM, Stateful App Engine, Euclid Omega, Three.js/CAD, Reference Perception, Web Experience, Android, iOS, Wear OS, watchOS, Polymath, Kintsugi, Graft, Crucible, Ariadne, Orrery, TOAM, and Holographic Memory.

[`catalog/domain-engines.json`](catalog/domain-engines.json) makes the distinction
between exact source-pinned engines and architecture-only/planned engines machine
readable. A planned ID is discoverable for design work but is not installable or
routeable until it has a repository, exact commit, manifest, adapter and passing
conformance suite.

Their roles remain precise:

- Qwen compiles bounded intent/specifications.
- Euclid Omega derives mathematical structure and proof obligations.
- DEMIURGE synthesizes/proves artifacts inside supported decidable domains.
- LOOM composes repair, hardening, and extension lanes over repositories.
- SAE owns stateful application synthesis and persistence invariants.
- TOAM journals attempts and promotes certified knowledge; Git remains canonical for source.

## Wi-Fi to 5G delivery

Plugins do not speak raw radio protocols. A Wi-Fi client reaches an authenticated plugin gateway through the N3IWF path:

```text
Wi-Fi UE → IPsec/IKEv2 → N3IWF → 5G Core → MEC/service gateway → plugin service
```

Local stdio plugins stay on the device. Remote services use authenticated HTTPS or streamable MCP behind the gateway with tenant identity, mTLS/service identity, quotas, telemetry, and the same manifest/grant/receipt semantics. N3IWF supplies untrusted non-3GPP access to the 5G core; it does not replace application authorization.

## Quick start

```powershell
py -m unittest discover -s tests -v
$env:PYTHONPATH = "$PWD\src"
py -m polar_pyro_plugin_sdk.conformance examples\manifests\browser.plugin.json
```

No Python dependency installation is required for those checks.

## Repository map

```text
schemas/                    Normative language-neutral ABI
src/polar_pyro_plugin_sdk/  Reference models, registry, broker, MCP and Git boundaries
examples/manifests/         First-party and upstream-adapter examples
catalog/                    Official capability-family registry
tests/                      Contract, security, idempotency and Git transaction tests
docs/                       Architecture, security, rollout and upstream evaluation
```

## Production gates

A plugin is not production-ready until:

- manifest/schema mutation tests pass;
- install, startup, health, drain, restart, update, rollback, and removal are proven;
- all effects are grant-covered and path/network confined;
- secret, prompt-injection, SSRF, shell, traversal, stale-proof, and duplicate-invocation attacks fail closed;
- every `PASS` has live evidence and a reproducible receipt;
- mutation plugins pass copy-on-write and concurrent-HEAD tests;
- crashes leave canonical source and TOAM recoverable;
- license/SBOM/model-weight obligations are recorded;
- latency, resource, and 5G gateway budgets pass on target hardware.

See [WHITEPAPER.md](WHITEPAPER.md), [docs/PHASED_IMPLEMENTATION_PLAN.md](docs/PHASED_IMPLEMENTATION_PLAN.md), and the dated [live adapter qualification](docs/LIVE_ADAPTER_QUALIFICATION_2026-08-21.md).

## Status

Version 0.1 establishes and tests the contract kernel. The example manifests for not-yet-extracted repositories use the sentinel commit `0000000`; that deliberately prevents them from being production-qualified. A plugin becomes installable only after its repository exists, the manifest is updated to an exact reachable commit, and the full qualification suite passes.
