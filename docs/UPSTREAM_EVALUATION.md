# Upstream Plugin Evaluation

Evaluated 2026-08-21 at exact audit commits.

## Obscura

- Upstream: `h4ckf0r0day/obscura@5465ff76abde560c7e9d69b1ca85895562de38e4`
- License: Apache-2.0.
- Adopt: native headless execution, CDP compatibility, MCP surface, snapshots, screenshots, network and console inspection.
- Harden: keep private-network and file access denied, restrict cookie/storage capabilities, origin allowlists, resource/time budgets, receipt normalization.
- Position: execution backend behind Polar Browser; not the retrieval policy authority.

## OpenCodex

- Upstream: `lidge-jun/opencodex@5840591322117f3ee9568b35b135a6d4339f7711`
- License: MIT.
- Adopt: OpenAI Responses and Anthropic Messages protocol compatibility, streaming translation, loopback service topology.
- Harden: disabled by default, explicit toggle and terms notice, authenticated non-loopback binds, secret handles, requests compiled into closed Polar intent before execution.
- Position: client compatibility edge, never the verification or tool-authorization layer.

## Wigolo

- Upstream: `KnockOutEZ/wigolo@c6ad4479da7706945b479786df0121e3cce1ece6`
- License: AGPL-3.0-only.
- Adopt: search/fetch/crawl/research contracts, result fusion, source spans, local-first evidence pipeline.
- Boundary: separately managed process/repository with full license/source compliance; do not copy into the MIT SDK.
- Position: evidence acquisition backend below Sovereign Retrieval Oracle.

## Agent Reach

- Upstream: `Panniantong/Agent-Reach@93ae1d18c37b707dec053c7c4f9d91cd8ef8943d`
- License: MIT.
- Adopt: channel interface, URL capability detection, ordered backend candidates, live probes, diagnostics and dry-run concepts.
- Harden: deny installations and personal-session access to model-driven calls; explicit grants for profiles/cookies; normalize all results to evidence atoms.
- Position: public channel/router plugin for social, video, RSS, and platform-specific retrieval.

## Chrome DevTools MCP

- Adopt as the live Chromium inspection/performance adapter already used by the Polar Pyro development setup.
- Keep separate from Obscura: one is optimized for inspecting a real debug target, the other can execute lightweight headless work.

