# DE-PIN Platform Plugin Decomposition

## Governing rule

Each protocol or substantial module in a DE-PIN section is independently versioned and published when it has its own domain contract, lifecycle, security boundary, or reusable UI. A plugin repository owns its engine/adapter, schemas, oracle tests, independent UI module, documentation, provenance, and release evidence. The DE-PIN application is a host/composition shell; it does not become the hidden implementation repository for every protocol.

The independent UI is both a portable product surface and a development boundary. It must run in isolation with fixture data, declare host slots, use the Polar Pyro UI handshake, and request all data/actions through brokered capabilities. The host controls navigation, project/session identity, permissions, tokens, telemetry policy, and cross-plugin composition.

## Software-directory organization

Under the master software directory, create a top-level **DE-PIN Platform** group with these sections and plugin families:

| Section | Candidate plugin families |
|---|---|
| Discover / Explorer | globe renderer, MapLibre/H3 map, ECVC node registry, density/coverage oracle, mint-location workflow |
| Trading Terminal | market-data adapter, order book, execution/order entry, CYAN spot, CYAN-Watt perps, JHX hashrate perps, bandwidth futures, reserve swaps, slashing insurance, TBP-JIT liquidity |
| FLUX · Energy-DeFi | electricity-meter protocol, meter oracle, volatility/SVI, energy perps, prediction markets |
| Agent OS / Polar Pyro | harness core, plugin SDK/host, TOAM adapter, sovereign retrieval, Prose Orchestrator, Shell Engine, Sandbox Engine, Git Fabric, cybersecurity, target compilers |
| Juronant Explorer | Kate L1 RPC/indexer, block/transaction/account/mempool/holder explorer UI |
| Passpoint | proof-of-presence, staking tiers, burn lottery, TDI-bound DID, wallet/identity adapters |
| Data Bundles | ERC-1155 bundle schema, minting, catalog, provenance/access policy |
| BRSA / Origination / Meter | BRSA, take-or-pay origination, meter portal, underwriting/risk oracles |
| Studio · MXP Music | offtake vault, sentiment market, chart perps, fan-network DePIN, rights/provenance adapters |
| Shared infrastructure | wallet, identity, notification, audit, charts, design tokens, accessibility, observability |

Existing repositories such as the electricity-meter protocol or DOCC remain canonical when they already implement a family. The first task is discovery and contract classification, not duplication. Thin presentation-only elements stay in the host until they acquire a genuine independent lifecycle.

## Plugin contract

Every repository must include `plugin.manifest.json`, frozen JSON Schemas, effect/grant declarations, version compatibility, UI contribution slots, deterministic fixtures, contract/property/security tests, a threat model, third-party notices, SBOM/provenance instructions, and a release gate. Protocol plugins also require state-machine invariants, upgrade/migration rules, chain/network identity, replay protection, finality assumptions, and testnet/local simulator fixtures.

## Phased implementation

### D0 — Estate inventory
Query the LUXERON directory and DE-PIN source graph, map modules to existing repos, owners, protocols, state, routes, and UI components. **Exit:** one authoritative inventory with no guessed repository ownership.

### D1 — Bounded contexts
Classify each module as host shell, shared primitive, protocol engine, chain adapter, data adapter, workflow, or UI composition. Record dependencies and split/retain decisions. **Exit:** circular ownership and duplicated protocol truth are eliminated.

### D2 — Contract extraction
Freeze schemas, events, commands, effects, grants, state machines, and oracle obligations for each selected plugin. **Exit:** host and plugin can be tested independently through fixtures.

### D3 — Independent UI extraction
Package each plugin surface with fixture mode, design tokens, accessibility, responsive behavior, sandbox handshake, and explicit host slots. **Exit:** each UI runs alone and embedded without direct host imports.

### D4 — Repository publication
Create or adopt repos, retain provenance/licenses, add CI/SBOM/security, publish exact commits, and register under the correct directory section. **Exit:** directory coverage generator passes and every catalog entry resolves.

### D5 — Host composition
Install pinned plugins through the SDK, add route contributions, capability mediation, shared session/project context, and failure isolation. **Exit:** one plugin can be disabled/rolled back without breaking unrelated sections.

### D6 — Protocol and UI gauntlets
Run state-machine, economic invariant, authorization, chain reorg/finality, data freshness, accessibility, visual regression, browser, performance, and disaster-recovery suites. **Exit:** claims are backed by receipts; human UI approval remains a separate final gate.

## Near-term registration priority

Register already published Polar Pyro target plugins first, then Prose Orchestrator, Sandbox, Shell, Git Fabric, and defensive Cybersecurity. Next inventory existing electricity-meter and DOCC repositories before creating replacements. Repository creation is gated on an actual bounded context and prior-art check.
