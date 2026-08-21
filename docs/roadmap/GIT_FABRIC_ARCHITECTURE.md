# Polar Pyro Proof-Gated Git Fabric

## Decision

The attached Git proposal is approved in direction—Git should become a transactional proof and provenance substrate—but not as a from-scratch reimplementation of object storage, Smart HTTP, SSH, packfiles, and cryptography. The MVP composes a mature Git implementation (`gix` or libgit2 for client operations and an established self-hosted server) with a new Polar Pyro proof gateway. Protocol replacement is justified only by a demonstrated missing invariant and interoperability tests.

The product has three separately deployable plugins:

1. **Git Engine:** deterministic repository operations over typed intents.
2. **Proof Gateway:** policy, verification, attestations, merge authorization, and TOAM linkage.
3. **Git Service Adapter:** repository hosting, identity, access control, Smart HTTP/SSH, object storage, hooks, and replication through a pinned upstream server.

## Typed operations

Qwen emits `GitIntentIR` such as inspect, branch, apply verified diff, commit, merge, revert, bisect, or publish. The engine binds repository UUID, worktree token, branch/ref, expected head, path scope, and effect class. It never accepts arbitrary shell Git commands or force options.

Each candidate commit is produced in an isolated worktree. A `ChangeSetIR` records blob-level and semantic diffs, generators, tests, engine receipts, dataset/model versions, and task evidence. The proof gateway evaluates branch policy, oracle coverage, non-regression, secret/license scans, authorship/authorization, and stale-head checks.

Proofs are stored as portable signed attestations referenced by commit SHA—Git notes or an external content-addressed transparency store, using in-toto/Sigstore-compatible envelopes where practical. Custom commit headers are avoided because they harm interoperability and do not replace independent verification.

## Merge semantics

Textual three-way merge is a fallback. Language-aware adapters from ROSETTA/KINTSUGI may propose structural merges and DEMIURGE may prove domain invariants. Structural merge is not assumed to be a universal semilattice: ordering, side effects, schema migrations, generated files, and behavior can conflict. An unresolved conflict remains a typed residual; it is never hidden behind a syntactically clean result.

## Server posture

Start with a pinned Gitea/Forgejo-class service or existing organizational GitHub remote for transport, identity, repository lifecycle, and webhooks. The Proof Gateway runs as protected status checks and pre-receive policy where server control permits. Client-side hooks are convenience only. Branch protection must make proof status non-bypassable for protected branches.

## Independent UI modules

The Git Engine UI shows repository/worktree state, semantic and textual diffs, attempt lineage, conflicts, and reversible actions. The Proof Gateway UI shows required gates, attestations, failures, provenance graph, policy version, and promotion decision. The Service UI covers repository administration and health. All are sandboxed plugin surfaces and share only host-issued project/session/repository tokens.

## Phased implementation

### G0 — Repository and proof contracts
Freeze IDs, refs, optimistic concurrency, change sets, attestations, policies, verdicts, and audit events. **Exit:** hash/branch/path ambiguity tests and threat model pass.

### G1 — Safe local Git Engine
Implement inspect/diff/branch/commit/revert in isolated worktrees through `gix`/libgit2; capture exact object IDs. **Exit:** no shell invocation; dirty/untracked/symlink/submodule/LFS cases have explicit semantics.

### G2 — Workspace transaction binding
Bind sandbox before/after trees to Git blobs, apply only admitted diffs, and reject stale heads. **Exit:** concurrent-update and crash tests cannot lose or silently overwrite work.

### G3 — Proof Gateway
Compile repository policy, invoke tests/domain oracles/security/license gates, issue signed attestations, and journal TOAM decisions. **Exit:** a commit without a live non-vacuous check cannot receive a promotion certificate.

### G4 — Structural diff and merge adapters
Integrate ROSETTA facts, KINTSUGI diagnostics, and language-specific formatters/migration checkers. **Exit:** mutation fixtures show behavioral conflicts are rejected even when text merges cleanly.

### G5 — Server integration
Deploy the pinned Git service, protected branches, identity/ACLs, webhooks, backup, replication, and proof enforcement. **Exit:** transport interoperability and authorization tests pass; bypass attempts are rejected server-side.

### G6 — Supply-chain provenance
Emit SLSA/in-toto-style provenance, SBOM and artifact links, keyless or managed signing, revocation, and transparency records. **Exit:** every release maps source commit to build inputs and verification receipts.

### G7 — Scale and resilience
Pack/GC stress, large-file policy, monorepo and submodule fixtures, disaster recovery, high availability, and audit retention. **Exit:** published recovery point/time, performance, and integrity results meet policy.

## Repository relationship to TOAM

Git remains the source-of-truth for code and TOAM remains the canonical conversational/decision memory. They cross-reference immutable IDs. Neither is overloaded to emulate the other. Semantica may project their provenance graph and is always rebuildable.
