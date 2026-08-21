# Polar Pyro Superior Shell Engine

## Decision

Build a typed command-planning and execution plugin, not a more articulate shell-prompt generator. The 0.6B model emits `CommandIntentIR`; a deterministic compiler selects registered executables, validates arguments, constructs an argv/pipeline graph, calculates effects, and submits it to the Sandbox Engine. Raw shell is an export format for inspected scripts, never the default authority path.

This preserves the attached proposal's strongest idea—shell work as algebra over streams, files, processes, effects, and postconditions—while removing unsafe assumptions. `set -euo pipefail` is a useful Bash policy profile, not a universal proof. Quoting rules vary by PowerShell, POSIX shell, `cmd.exe`, and remote transports. Many commands have no meaningful dry-run flag. Isolation and observation must therefore live below the shell language.

## Core IR

`CommandIntentIR` describes goal, workspace, platform, allowed capability family, inputs, outputs, postconditions, and effect ceiling. `ProcessIR` carries an executable identity from the frozen registry, argv array, environment allowlist, stdin/stdout/stderr bindings, working directory token, resource budget, and expected exit semantics. `PipelineIR` connects typed byte/text/JSON/file streams. `FileEffectIR`, `NetworkEffectIR`, and `ProcessEffectIR` form the predicted effect set. `ExecutionReceipt` records actual effects, hashes, timings, resource use, output truncation, and sandbox identity.

The model cannot emit executable paths, shell metacharacters, environment variable names, redirections, privilege changes, or network destinations unless the active capability schema explicitly admits them. Secrets are opaque broker handles and are never prompt fields.

## Compiler and verifier

The compiler performs executable resolution, platform compatibility, argument schema validation, path confinement, stream type checking, effect inference, idempotency classification, determinism classification, and postcondition compilation. It rejects ambiguous executable names and unsupported compositions.

The verifier compares predicted and observed effects, checks exit policy and postconditions, detects unexpected children/network/files, scans outputs for secret leakage, and returns `PASS | FAIL | NO_RESULT`. A zero exit status is evidence, not proof of the requested outcome.

## Independent UI module

The plugin UI is a command-plan inspector embedded by Polar Pyro. It shows the intent, argv graph, predicted effect diff, grants, sandbox profile, live bounded output, postcondition receipts, and promotion status. It may request a grant through the host but cannot execute outside the broker. Script export is clearly marked as a portability artifact and displays the exact target shell and escaping profile.

## Phased implementation

### S0 — Platform and threat contracts
Freeze Windows/Linux/macOS process semantics, effect taxonomy, safe path tokens, executable registry, secret handles, and three-valued verdicts. **Exit:** adversarial schema/property tests reject metacharacter smuggling, path traversal, environment injection, unknown binaries, and model-authored grants.

### S1 — Direct-process kernel
Implement argv-only subprocess execution behind the Sandbox Engine with bounded output and cancellation. **Exit:** no `shell=True`; executable digests and actual process trees appear in every receipt.

### S2 — Typed pipelines
Add stream codecs, explicit redirection nodes, fan-in/fan-out rules, pipe failure semantics, and deterministic temporary artifacts. **Exit:** property tests cover backpressure, broken pipes, binary/text confusion, and partial failure.

### S3 — Files, network, and secrets
Add copy-on-write workspace tokens, declared network destinations, opaque secret injection, and effect reconciliation. **Exit:** undeclared writes/egress/secret output fail in the same invocation.

### S4 — Postconditions and repair
Compile assertions over files, JSON, services, ports, tests, and domain receipts. Convert failures to bounded residuals for Qwen. **Exit:** retry changes only admitted nodes and cannot weaken postconditions or expand effects.

### S5 — Cross-shell export
Generate inspected Bash/PowerShell scripts from `ProcessIR`, with shell-specific lint and golden tests. **Exit:** exported scripts reproduce direct-execution semantics for the supported subset; unsupported constructs abstain.

### S6 — Long-horizon integration
Connect TOAM attempt journaling, WorkspaceTransaction, Git proof promotion, and per-step budgets. **Exit:** crash/resume and replay preserve exact command/effect hashes; failed attempts never reach the canonical workspace.

### S7 — Security and performance gauntlet
Run command injection, symlink/junction, race, decompression bomb, fork bomb, output flood, network pivot, credential, and denial-of-service fixtures. **Exit:** all critical poisons rejected; latency/throughput budgets and platform matrices published.

## Required non-vacuous tests

No command supplied by model text is executed directly; every executable and argument is admitted; predicted effects cover observed effects; `NO_RESULT` is never truthy; cancellation kills the full process tree; output limits cannot deadlock; copy-on-write promotion is atomic; resume does not replay non-idempotent work without an idempotency receipt; and every UI action is authorization-checked by the host.
