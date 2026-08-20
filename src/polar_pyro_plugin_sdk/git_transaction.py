"""Copy-on-write Git worktree transaction used by mutation-capable plugins."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import subprocess

from .models import ContractError


_SAFE_ID = re.compile(r"^[A-Za-z0-9._-]+$")


def _run(repo: Path, args: list[str]) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
        shell=False,
    )
    if completed.returncode != 0:
        raise ContractError(f"git {' '.join(args)} failed: {completed.stderr.strip()}")
    return completed.stdout.strip()


@dataclass
class GitWorkspaceTransaction:
    repository: Path
    transaction_root: Path
    session_id: str
    attempt_id: str
    base_commit: str
    branch: str
    worktree: Path

    @classmethod
    def begin(cls, repository: Path, transaction_root: Path, session_id: str, attempt_id: str) -> "GitWorkspaceTransaction":
        repository = repository.resolve()
        transaction_root = transaction_root.resolve()
        if not repository.is_dir() or not (repository / ".git").exists():
            raise ContractError("repository must be a Git working tree root")
        if not _SAFE_ID.fullmatch(session_id) or not _SAFE_ID.fullmatch(attempt_id):
            raise ContractError("session_id and attempt_id must be path-safe")
        if _run(repository, ["status", "--porcelain"]):
            raise ContractError("canonical repository must be clean before transaction")
        base = _run(repository, ["rev-parse", "HEAD"])
        transaction_root.mkdir(parents=True, exist_ok=True)
        worktree = (transaction_root / session_id / attempt_id).resolve()
        if transaction_root not in worktree.parents:
            raise ContractError("transaction path escaped transaction root")
        branch = f"polar-pyro/{session_id}/{attempt_id}"
        _run(repository, ["worktree", "add", "-b", branch, str(worktree), base])
        return cls(repository, transaction_root, session_id, attempt_id, base, branch, worktree)

    def diff(self) -> str:
        return _run(self.worktree, ["diff", "--no-ext-diff", "--binary", self.base_commit])

    def commit_candidate(self, message: str) -> str:
        if not message.strip():
            raise ContractError("commit message is required")
        _run(self.worktree, ["add", "--all"])
        if not _run(self.worktree, ["diff", "--cached", "--name-only"]):
            raise ContractError("candidate has no changes")
        _run(self.worktree, ["commit", "-m", message])
        return _run(self.worktree, ["rev-parse", "HEAD"])

    def promote_fast_forward(self, candidate_commit: str, certificate_id: str) -> str:
        if not _SAFE_ID.fullmatch(certificate_id):
            raise ContractError("certificate id must be path-safe")
        if _run(self.repository, ["rev-parse", "HEAD"]) != self.base_commit:
            raise ContractError("canonical HEAD moved; transaction must be rebased and reverified")
        _run(self.repository, ["merge", "--ff-only", candidate_commit])
        return _run(self.repository, ["rev-parse", "HEAD"])

