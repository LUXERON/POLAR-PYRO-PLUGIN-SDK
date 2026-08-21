# Polar Pyro Sandbox Engine

## Decision

Yes, the 0.6B harness requires a dedicated sandbox engine. Grammar constraints prevent malformed intentions; they do not isolate hostile processes, compromised dependencies, generated code, build scripts, browser content, or deterministic engines with implementation defects. The Sandbox Engine is the mandatory execution substrate for Shell, Git hooks, compilers, tests, browsers, cybersecurity tools, LOOM, SAE, and third-party plugins.

## Security boundary

The first production target is Linux isolation because namespaces, cgroups v2, seccomp, Landlock/AppArmor, overlayfs, and mature container/microVM runtimes provide enforceable controls. Windows development uses a hardened adapter—Windows Sandbox/Hyper-V container or WSL2-hosted Linux worker—with explicit acknowledgement that a plain subprocess or Python virtual environment is not a security sandbox.

Profiles are immutable, content-addressed policy bundles. A profile defines image/rootfs digest, UID/GID, filesystem mounts, writable overlay, devices, syscalls, capabilities, process count, CPU/memory/disk/time/output limits, network namespace and egress allowlist, DNS policy, secrets, and evidence collectors. The caller receives a token, never the underlying host path or credential.

## Transaction model

Every attempt receives a read-only source snapshot and a private writable overlay. The engine records the before tree hash, predicted effects, actual filesystem diff, process tree, network flows, resource metrics, exit state, and after tree hash. Promotion is a separate capability invoked only after the relevant oracle stack passes. Promotion applies an explicit diff atomically; sandbox state is disposable.

## Runtime tiers

- **Tier 0, pure:** WASM or in-process pure functions with no I/O, used only for audited deterministic transforms.
- **Tier 1, container:** rootless OCI/container isolation for ordinary builds and tests.
- **Tier 2, hardened:** gVisor/Kata/Firecracker-style boundary for untrusted generated code and parsers.
- **Tier 3, disposable remote:** dedicated ephemeral worker for high-risk cybersecurity and kernel/device tasks.

Risk classification, not the model, selects the minimum admitted tier. An unavailable required tier returns `NO_RESULT`.

## Independent UI module

The Sandbox plugin UI exposes profiles, active runs, resource charts, process/network/file evidence, diff preview, cancellation, and retention/purge state. It never exposes raw secrets or provides an unrestricted terminal. Promotion controls display the exact oracle receipts that authorize them.

## Phased implementation

### X0 — Threat model and policy schema
Freeze assets, attacker capabilities, trust zones, profiles, grants, receipts, retention, and verdicts. **Exit:** external review of escape, confused-deputy, tenant, secret, and supply-chain cases.

### X1 — Rootless container runner
Implement immutable image digests, non-root users, read-only roots, tmpfs, cgroups, process/time/output limits, and full cancellation. **Exit:** escape/limit fixtures and process-tree cleanup pass.

### X2 — Copy-on-write workspace
Implement overlay/snapshot creation, safe relative paths, symlink/junction defense, deterministic diff, and atomic promotion. **Exit:** traversal and race fixtures fail; failed runs leave the canonical workspace byte-identical.

### X3 — Network and secret broker
Default-deny egress, destination/TLS policy, DNS pinning defenses, SSRF controls, opaque short-lived secrets, and output redaction. **Exit:** undeclared egress and credential exfiltration poisons fail.

### X4 — Evidence and TOAM
Hash-chain run receipts, journal lifecycle/idempotency, store bounded logs/artifacts, and implement purge. **Exit:** restart/recovery, duplicate request, and tamper tests pass.

### X5 — Hardened runtime tier
Add a microVM or syscall-interposing runtime and risk router. **Exit:** high-risk workloads cannot fall back silently to the ordinary container tier.

### X6 — Cross-platform adapters
Qualify Linux native, Windows-hosted, macOS/CI, and remote-worker behavior. **Exit:** a published support matrix identifies equivalent and weaker guarantees.

### X7 — Operational readiness
SBOMs, signed images/policies, vulnerability scanning, patch SLAs, audit export, quotas, observability, disaster recovery, and red-team gauntlets. **Exit:** reproducible deployment and rollback; zero critical open escape findings.
