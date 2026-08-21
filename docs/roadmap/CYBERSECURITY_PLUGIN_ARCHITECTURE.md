# Polar Pyro Defensive Cybersecurity Plugin

## Scope

This plugin gives the 0.6B harness a closed, defensive security workflow over explicitly authorized assets. It may inspect, model threats, scan code/configuration/dependencies, reproduce vulnerabilities in disposable fixtures, recommend and apply repairs in copy-on-write transactions, and verify remediation. It is not an unrestricted penetration agent, persistence framework, credential harvester, or autonomous attack system.

`mukul975/Anthropic-Cybersecurity-Skills` is treated as untrusted prior-art content. Individual skills may be mapped into typed playbooks only after license, provenance, command, network, secret, data-handling, and destructive-action review. Natural-language instructions never become executable policy.

## Architecture

An `AuthorizationEnvelope` freezes owner, assets, time window, allowed techniques, data policy, network range, effect ceiling, and emergency stop. A deterministic capability registry maps a `SecurityIntentIR` to an admitted playbook. Qwen fills bounded slots: asset class, suspected weakness, evidence references, and requested observation. The broker selects tools; the Sandbox Engine executes them; the Shell Engine supplies typed process plans; Graphify/ROSETTA/SBOM engines supply static evidence; TOAM journals findings and remediation; DEMIURGE/domain oracles prove applicable security invariants.

All findings use `FindingIR` with weakness taxonomy, affected component/version, evidence, reproduction safety, exploitability uncertainty, impact, remediation, and validation. Severity is computed by a pinned policy—not free-form model rhetoric. Failed or unavailable confirmation yields `NO_RESULT`.

## Independent UI module

The UI shows authorization scope, asset inventory, attack-surface graph, scans, evidence-backed findings, remediation transactions, retest status, and audit export. Dangerous capabilities are absent unless the host injects a matching grant. Raw secrets and exploit payloads are redacted by default. Human approval is required for any activity outside local disposable fixtures or passive analysis.

## Phased implementation

### C0 — Governance and authorization
Freeze rules of engagement, capability taxonomy, data classes, audit/retention, emergency stop, and legal/owner assertions. **Exit:** out-of-scope targets and model-authored authorization fail before tool selection.

### C1 — Static defensive lane
Implement dependency/SBOM/license/vulnerability, secret, configuration, IaC, permissions, and code-pattern analysis through pinned tools. **Exit:** seeded fixtures achieve declared precision/recall; every finding cites raw evidence.

### C2 — Sandboxed validation lane
Reproduce admitted weaknesses only inside disposable local targets with default-deny network. **Exit:** fixtures prove containment, timeout, output limits, and cleanup.

### C3 — Repair lane
Use KINTSUGI/LOOM/SAE to propose repairs in isolated workspaces; run regression and security oracles before Git promotion. **Exit:** vulnerable mutants fail before and pass after repair without functional regression.

### C4 — Web and supply-chain lane
Add passive web checks, SSRF-safe fetch, browser evidence, provenance/SLSA policy, artifact signatures, and dependency graph analysis. **Exit:** no active test can exceed its authorization envelope.

### C5 — Incident-evidence lane
Add read-only log/timeline/IOC correlation with chain-of-custody hashes and privacy controls. **Exit:** replay is deterministic and original evidence remains immutable.

### C6 — Skill refinery
Quarantine upstream security skill repositories, extract candidate playbooks, compile schemas, mutation-test predicates, and publish only reviewed capabilities. **Exit:** no prose instruction or embedded command bypasses the registry/sandbox.

### C7 — Adversarial gauntlet and release
Run prompt injection, tool poisoning, target-scope confusion, symlink/SSRF, secret exfiltration, false-positive/negative, denial-of-service, and audit-tamper tests. **Exit:** critical controls pass and measured capability claims replace parameter-parity marketing.
