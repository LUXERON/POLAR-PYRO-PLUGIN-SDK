# Phased Implementation and Execution Loop

## Phase 0 — Contract kernel

Deliver schemas, canonical digests, lifecycle state machine, capability registry, effect grants, broker, typed receipts, MCP process rules, Git worktree transactions, catalog, documentation, and conformance tests.

Exit: malformed/off-contract inputs, undeclared effects, secret-like fields, empty PASS receipts, duplicate idempotency with changed args, and stale Git promotion all fail closed.

## Phase 1 — Host plugin runtime

Add manifest discovery from a signed local catalog; qualification cache; installer/supervisor; health, drain, restart, rollback and removal; sandboxed UI contribution host; structured RPC; per-plugin logs and resource budgets; TOAM lifecycle journaling.

Exit: a fixture plugin can be installed, activated, crash-recovered, upgraded, rolled back, and removed without restarting or corrupting the host.

## Phase 2 — Extract core surfaces

Create independent Chat, Browser, and Changes repositories. Replace direct Polar Pyro store/component imports with contribution slots and the host RPC SDK. Preserve the existing user experience: project/session rail, embedded browser, code-overlay diff review, and fail-closed promotion.

Exit: each surface can be disabled or replaced independently; host and other surfaces continue operating; UI accessibility and conformance tests pass.

## Phase 3 — Internet service mesh

Package governed adapters for Obscura, Chrome DevTools MCP, Wigolo, Agent Reach, and Sovereign Retrieval Oracle. Implement URL/SSRF policy, channel routing, authority scoring, evidence normalization, transient TOAM, grounding, purge, certified promotion, and backend fallback.

Exit: adversarial pages cannot issue actions or exfiltrate secrets; every promoted claim cites exact captured evidence; sidecar failure falls back or returns NO_RESULT.

## Phase 4 — Compatibility edge

Fork/package the OpenCodex compatibility service. Add DE-PIN installer integration and an off-by-default UI toggle. Translate OpenAI Responses and Anthropic Messages to Polar sessions and streams; preserve client cancellation and errors; route all requests through closed intent, broker, Git, and oracle stages.

Exit: Codex/Claude-compatible clients complete fixture tasks while network binds, authentication, terms disclosure, credentials, and bypass attempts pass security tests.

## Phase 5 — Domain-engine catalog

Publish manifests/adapters for DEMIURGE, Euclid Omega, LOOM, SAE, Web Experience, Android, iOS, Wear OS, watchOS, Three.js/CAD, Reference Perception, Woven create/repair/extend engines, TOAM, and Holographic Memory. Freeze schema hashes and capability compatibility rules.

Exit: deterministic routing selects one compatible engine or abstains; engine failures produce typed residuals; no model-authored executable oracle is accepted.

## Phase 6 — Git long-horizon control plane

Add durable BuildSession restore, attempt branches, dependency/stacked-change graph, conflict/rebase workflow, oracle certificates, signed promotion, cleanup/retention policy, remote origin policy, and repository showcase publishing after authorization.

Exit: crash/restart, concurrent sessions, moved HEAD, revert, branch switch, and multi-engine repair/graft sequences preserve proof and history.

## Phase 7 — Wi-Fi/5G edge delivery

Deploy authenticated plugin gateways behind N3IWF/5GC/MEC. Map subscriber identity to tenant policy, use mTLS service identity, quotas, observability, circuit breakers, and offline/local fallback. Do not expose stdio services directly to the network.

Exit: tenant isolation, handover/interruption recovery, latency/resource budgets, gateway failover, and audit correlation pass on the target network.

## Phase 8 — Autonomy gauntlet

Run five difficult stateless and five difficult stateful projects from clean natural-language briefs. No product-source hand edits are allowed; fixing the generic harness is allowed and must be followed by clean-room regeneration. Validate behavior, mutation adequacy, security, persistence, design conformance, and human UI judgment. Publish only independently passing repositories.

Exit: ten repositories pass machine gates and human review with complete intent, invocation, Git, evidence, certificate, and provenance receipts. Claims of frontier parity are based on measured baselines, not architecture alone.

## Non-stopping execution loop

```text
LOAD durable phase/session state
FREEZE task, schemas, manifests, source commits, budgets, and base Git commit
SELECT the next unsatisfied exit criterion
RUN deterministic preflight
PROPOSE one bounded artifact or repair through the 0.6B model when needed
EXECUTE only through a qualified capability and isolated transaction
VERIFY schema → invariant → tests → mutation/poison → domain oracle
  PASS      journal certificate; promote atomically; advance criterion
  FAIL      map evidence to typed residual; repair in a new attempt
  NO_RESULT retry a bounded alternate backend or abstain honestly
CHECKPOINT only committed attempt state and remaining budget
RESTART from checkpoint after crash only when frozen hashes match
REPEAT until the phase exits or a genuine authority/external-state blocker exists
```

The loop never turns timeouts into success, never reuses a failed candidate unchanged, never promotes before verification, and never broadens authority merely to keep moving.

