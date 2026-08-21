# Polar Pyro live adapter qualification — 2026-08-21

This is an evidence record, not a marketing readiness claim. A source pin, a passing wrapper policy test, an upstream test run, an MCP handshake, and permission to enable a capability are distinct states. `configured` means only that a runtime is discoverable; `qualified` requires all relevant gates below.

## Verdict matrix

| Adapter | Exact upstream | Evidence obtained | Current verdict |
|---|---|---|---|
| Obscura | `h4ckf0r0day/obscura@5465ff76abde560c7e9d69b1ca85895562de38e4` | `cargo test -p obscura-mcp`: 13/13 pass. `cargo test -p obscura-cli --test mcp_client`: 15/16 pass; initialize, tools, resources, prompts, ping, evaluate, waits and error handling passed. The loopback navigation fixture failed twice. | **PARTIAL / DISABLED FOR AUTONOMOUS NAVIGATION.** The wrapper command was corrected from the nonexistent `obscura-mcp` executable to upstream's documented `obscura mcp`. Private networks and files remain denied. Requalify navigation against an admitted public fixture and add redirect/DNS-rebinding tests before enablement. |
| Agent Reach | `Panniantong/Agent-Reach@93ae1d18c37b707dec053c7c4f9d91cd8ef8943d` | Declared dependencies installed. Portable suite excluding the Windows/Git-Bash Xiaoyuzhou fixture: 556 passed, 15 skipped. The initial all-platform run produced 564 passed, 15 skipped and 7 failed: one missing declared dependency plus six path-sensitive shell fixtures. | **ROUTE COMPILER ONLY.** Audit proved Agent Reach has no MCP server or `mcp` subcommand. Its Polar adapter is now host-native and may only choose a frozen public channel; each downstream CLI/MCP backend requires its own pin, grant and qualification. |
| Wigolo | `KnockOutEZ/wigolo@c6ad4479da7706945b479786df0121e3cce1ece6` | Exact lockfile installed; TypeScript `tsc --noEmit` passed. After rebuilding the declared native SQLite binding, unit suite: 7,745 passed, 8 failed, 19 skipped, 7 todo across 627 files. All eight failures are Windows readline/NDJSON shell tests. `npm audit` reported 17 vulnerabilities: 2 low, 3 moderate, 11 high, 1 critical. | **BLOCKED / SEPARATE AGPL SERVICE.** Functional breadth is substantial, but neither a red unit suite nor a critical dependency advisory is admissible. Do not embed, auto-install, or enable. Patch/upgrade dependencies, obtain a clean production audit, and pass an MCP handshake and citation quarantine gauntlet first. |
| OpenCodex | `lidge-jun/opencodex@5840591322117f3ee9568b35b135a6d4339f7711` | Wrapper policy tests pass. The required Bun runtime is absent on this machine, so no upstream process or protocol handshake was run. | **BLOCKED / OFF BY DEFAULT.** Keep the compatibility proxy loopback-only, disabled, credential-handle-only and without execution authority. Installation is a separate administrative action. |
| Sovereign Retrieval Oracle | LUXERON standalone repository | 13 tests pass for quarantine, ranking, grounding, transient memory hygiene and certified promotion. | **POLICY-QUALIFIED, LIVE PROVIDERS PENDING.** It may normalize already-admitted fixtures; live SearXNG/ddgs/fetch/TOAM process qualification is still required. |

## Wrapper corrections produced by this qualification

1. Obscura transport is now the shell-free tuple `("obscura", "mcp")`.
2. Agent Reach transport is now `native`, capability `reach.route_public_channel`; the fictional `agent-reach mcp` boundary was removed.
3. Catalog discovery now checks the real `obscura` binary.
4. None of these corrections grants Qwen direct process, network, credential or promotion authority.

## Enablement gates

An adapter becomes routeable only when all applicable items are green:

1. repository and upstream commits are immutable and match the install receipt;
2. license and distribution topology are accepted;
3. lockfile/image digest and SBOM are captured;
4. production dependency audit has no unwaived critical/high finding;
5. wrapper policy and upstream tests pass on the target OS;
6. transport handshake returns the expected identity and exact declared tool set;
7. SSRF, redirect, DNS rebinding, credential, personal-profile, prompt-injection and resource-limit gauntlets pass;
8. results normalize to typed evidence with source spans and hashes;
9. content remains quarantined until the Sovereign Retrieval Oracle and relevant domain oracle pass;
10. crash, timeout and stale-service behavior returns `NO_RESULT` without weakening native TOAM recall or Git safety.

No failing or unrun item is converted to PASS by configuration presence.
