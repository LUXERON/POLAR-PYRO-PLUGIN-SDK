# Governed Plugins for a Neurosymbolic Software Forge

## Abstract

Polar Pyro aims to make a 0.6B language model productive on software projects whose size and duration exceed its context, reasoning reliability, and direct tool-use safety. The central mechanism is separation of proposal from authority: the model emits small typed specifications; deterministic systems select capabilities, enforce contracts, synthesize or repair artifacts, verify them, and promote only certified state.

This paper extends that separation to the application platform itself. Chat interfaces, browsers, source review, internet retrieval, compatibility proxies, memory systems, and software-development engines become independently deployable plugins. A versioned manifest, effect-scoped grants, typed receipts, Git transactions, and oracle certificates create a common trust fabric across local processes, MCP services, and future services delivered through a 5G core.

## Problem

Conventional agent plugins equate discoverability with permission: a server advertises tools, an LLM selects one, and the host invokes it. This is inadequate for long-horizon autonomous development. Tool descriptions are mutable text; model routing is probabilistic; retries can duplicate effects; repository state can move after proof; plugins can access credentials or networks not visible in their declared purpose; and a boolean success can hide an empty or failed verification lane.

Large monolithic IDEs add another failure mode. A browser, chat UI, diff viewer, proxy, and synthesis engine import shared private state until no component can be upgraded or audited independently. The result cannot be delivered cleanly across different devices or network boundaries.

## Thesis

An AI plugin should be treated as an untrusted implementation of a frozen, evidence-bearing capability contract. MCP, HTTP, native calls, and UI embedding are interchangeable transports beneath that contract. The host—not the model and not the plugin—owns lifecycle, authorization, isolation, idempotency, verification, and promotion.

The resulting minimum trustworthy chain is:

```text
typed intent → frozen capability → scoped grant → isolated execution
→ typed evidence receipt → independent oracle → signed promotion
```

Removing any edge reintroduces ambiguity about what ran, what it was allowed to change, what evidence exists, or whether the verified artifact is the artifact being promoted.

## Architecture

The platform has five planes:

1. **Experience plane.** Sandboxed UI plugins contribute Chat, Browser, Changes, settings, inspectors, and future domain workbenches.
2. **Control plane.** The registry freezes manifests; the broker resolves closed intents, validates schemas, grants effects, enforces budgets, and journals receipts.
3. **Synthesis plane.** Qwen, ontology compilation, Euclid Omega, DEMIURGE, LOOM, SAE, and other deterministic engines produce candidate artifacts and proof obligations.
4. **Evidence plane.** Git worktrees, tests, mutation gates, browser traces, citations, TOAM provenance, and domain-oracle certificates bind claims to reproducible observations.
5. **Delivery plane.** Local stdio/native services remain device-local; HTTP/MCP services cross authenticated device, MEC, and 5G boundaries without changing the contract semantics.

### Manifest identity

Plugin identity is the tuple `(id, semantic version, canonical manifest digest)`. Source provenance includes an exact repository commit. A transport handshake can confirm runtime identity but cannot mutate the frozen capability set. Update means adding a new immutable tuple and rerunning qualification.

### Effects and grants

Capabilities are classified as observation, workspace mutation, external mutation, credential access, or value transfer. Grants bind a capability and effect to one project, explicit scopes, an issuer, and an expiry. High-impact effects require independent policy and human authorization appropriate to the deployment. No natural-language model output is a grant.

### Receipts and three-valued verdicts

The receipt binds request, arguments, manifest, time, output, evidence, upstream provenance, and Git state. `PASS` requires nonempty evidence and schema-valid output. `FAIL` means the execution produced disconfirming evidence. `NO_RESULT` means no valid result was obtained. Neither failure state carries promotable output.

### Git transaction theorem

If an oracle certificate binds candidate commit `C`, base commit `B`, manifest digest `M`, invocation digest `I`, and oracle version `O`, and canonical `HEAD` still equals `B`, a fast-forward from `B` to `C` promotes exactly the verified tree. If `HEAD` differs from `B`, that property no longer holds; the candidate must be replayed and reverified. This simple invariant is the foundation for safe long-horizon composition.

## Internet capability composition

The internet system is deliberately layered. Wigolo-like retrieval produces cited evidence. Agent Reach supplies channel-specific backend detection and fallback. Obscura supplies a low-footprint browser execution backend. Chrome DevTools supplies inspection and performance evidence for live Chromium targets. The Sovereign Retrieval Oracle treats all returned text as quarantined data, applies authority/ranking/chunking, places it in transient TOAM, performs bounded recall and grounding, purges raw evidence, and promotes only certified facts.

No scraped page, triple extraction, browser cookie, or model synthesis can authorize a software or external action.

## Compatibility clients

An OpenCodex-derived bridge can expose OpenAI- and Anthropic-compatible endpoints on loopback. Its value is adoption: existing coding clients can use the neurosymbolic forge without learning a new wire protocol. Its risk is bypass. Therefore it terminates client protocols into the same closed intent, broker, Git, and oracle pipeline. It is opt-in, authenticated when non-loopback, transparent about upstream service terms, and prohibited from persisting credentials in model context or durable memory.

## 5G-native extension

N3IWF provides Wi-Fi devices with an untrusted non-3GPP access path into a 5G core. Polar Pyro services can be placed behind MEC gateways and discovered through authenticated service catalogs. The plugin ABI remains unchanged; deployment policy adds subscriber/tenant binding, service identity, mTLS, quotas, radio-aware budgets, observability, and offline fallbacks. This yields a distributed forge without conflating network attachment with application trust.

## Prior art and classification

An audit of the LUXERON estate found adjacent foundations rather than an existing complete implementation:

| Prior system | Reused idea | Classification here |
|---|---|---|
| HERMES Sovereign Stack | Independent inference, memory, retrieval, and verification services | Extension |
| HTTP Adapter Makes MCP Server Dual Use | Transport adaptation | Extension |
| CYAN Flame Agent SDK | Agent-facing service abstractions | Adjacent |
| TOAM Memory OS | Durable provenance and certified promotion | Extension |
| Long-Horizon Coding Harness | FSM/BT orchestration and bounded retries | Extension |
| Woven Line engines | Deterministic create/repair/extend domains | Composition |
| POLAR PYRO / PHIME projects | Local inference and platform identity | Adjacent |
| 5G Native Internet / DE-PIN | N3IWF, 5G core, MEC delivery context | Extension |

No strong prior match supplied the combined immutable plugin identity, effect grants, three-valued evidence receipts, Git proof/promotion invariant, replaceable UI surfaces, and 5G delivery model. The contract kernel is therefore new ground assembled from proven local mechanisms.

## Licensing boundary

The SDK is MIT. Adapters retain upstream provenance and license notices. Apache-2.0 components require their license and NOTICE obligations. Wigolo is AGPL-3.0-only and therefore remains a separately installed/executed service; its code is not copied into the permissive core. Modified or network-deployed AGPL distributions require corresponding-source compliance. Model weights, embedding models, browser binaries, and transitive packages need separate audits; an upstream repository license does not cover them automatically.

## Evaluation

The platform is evaluated by adversarial contracts rather than feature counts. Primary metrics are capability routing precision, schema rejection, unauthorized-effect rejection, idempotency, receipt citation precision, stale-proof rejection, mutation adequacy, recovery after crash, warm latency, resource footprint, and successful autonomous project delivery. The ten-project autonomy gauntlet remains the product-level exit gate, but it cannot replace plugin-level security and reproducibility tests.

## North-star outcome

The final machine is a market of replaceable expert services governed by one proof protocol. A small model supplies linguistic compression and slot filling; deterministic engines supply construction and verification; Git supplies durable, composable history; TOAM supplies attributable memory; plugins supply reach and specialization; the host supplies authority. The architecture can grow from one workstation to Wi-Fi/5G edge services without increasing the neural model's privilege.

The executable host lifecycle makes that authority recoverable rather than implicit. Qualified packages enter a content-addressed store, are re-hashed before activation, must pass a fresh evidence-bearing health probe, and record install, health, activation, rollback and removal events in a local hash chain. TOAM may index those events, but the chain and immutable package receipts remain independently verifiable after a memory-service outage or host restart.
