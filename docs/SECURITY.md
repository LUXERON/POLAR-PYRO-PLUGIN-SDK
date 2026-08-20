# Security Model

## Assets

Canonical source, Git identity, credentials, user data, TOAM records, oracle keys, 5G subscriber/tenant identity, compute budgets, and external accounts are protected assets.

## Threats and mandatory controls

| Threat | Control |
|---|---|
| Prompt injection in fetched content | Quarantine as attributed data; closed extraction schemas; no tool/effect authorization from content |
| MCP server advertises extra tools | Manifest allowlist; reject undeclared tool names |
| Shell injection | Argument vectors only; `shell=False`; no model-authored acceptance commands |
| Path traversal | Resolved project roots; attempt-scoped worktrees; no symlink escape |
| SSRF | Scheme/host/IP validation; DNS rebinding checks; private/link-local/metadata networks denied by default |
| Credential exfiltration | Secret-like input rejection; brokered credential handles; never place secret values in prompts, receipts, or TOAM |
| Cookie/profile theft | Personal browser profiles and storage-state tools require credential-class grants |
| Duplicate external effect | Idempotency keys persisted before execution; provider receipt correlation |
| Stale proof | Certificate binds base/candidate commits; reject promotion when canonical HEAD moved |
| Vacuous verification | `PASS` requires nonempty live evidence; poison witness must fail in the same invocation |
| Plugin substitution | Canonical manifest digest and exact source commit; signed packages in production |
| Tenant leakage | Tenant/project filter before capability invocation and evidence traversal |
| Malicious UI | Sandboxed origin, CSP, structured RPC, no raw host object exposure |
| Supply-chain compromise | Exact pins, lockfiles, SBOM, signature/provenance, vulnerability and license scan |

Production deployment additionally requires OS sandboxing, resource quotas, signed certificates, encrypted journals, key rotation, audit export, and incident-response/rollback drills.

