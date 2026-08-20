# Architecture Decisions

## ADR-001 — MCP is below the trust boundary

Tool discovery is informational. Only capabilities declared in the frozen manifest can be invoked. Runtime additions are denied. Model output cannot select an executable or grant itself effects.

## ADR-002 — UI surfaces use host contribution slots

Plugins may contribute `session.tab`, `inspector.overlay`, `settings.integration`, and `command.palette` entries. Version 1 mounts remote UI in a sandboxed iframe and communicates with a structured RPC envelope containing host API version, plugin ID, request ID, project/session scope, and payload. The host supplies theme and accessibility tokens; the plugin receives no raw filesystem or credential access.

## ADR-003 — Mutation is a Git transaction

Workspace-writing capabilities require a clean base commit, confined worktree, explicit diff, candidate commit, independent certificate, and fast-forward promotion. Attempt branches are durable until journaled cleanup. There are no whole-file edits on the canonical checkout.

## ADR-004 — TOAM is the attempt/provenance ledger

TOAM stores typed intent, invocation, evidence receipt, residual, certificate, and promotion records. Git stores source truth. Derived semantic and holographic memories are rebuildable projections and cannot override Git or TOAM records.

## ADR-005 — Transport-specific constraints

- `mcp_stdio`: exact executable/argument vector; `shell=False`; sanitized environment; supervised lifecycle.
- `mcp_http`: loopback by default; authenticated endpoint, TLS and tenant binding when remote.
- `http`: same network policy plus OpenAPI/JSON schema conformance.
- `native`: isolated process boundary preferred; FFI only after ABI and memory-safety review.
- `iframe`: sandbox flags, CSP, origin pinning, no same-origin privilege by default.

## ADR-006 — Browser capability is a family

The Browser UI does not hard-code Chromium. It resolves `browser.navigate`, `browser.snapshot`, `browser.inspect`, and `browser.performance` independently. Obscura, Chrome DevTools MCP, or a future engine can satisfy different members under deterministic policy.

## ADR-007 — Remote delivery preserves local semantics

The 5G/MEC deployment adds transport identity and quotas; it does not relax manifest, grant, receipt, evidence, or oracle checks.

