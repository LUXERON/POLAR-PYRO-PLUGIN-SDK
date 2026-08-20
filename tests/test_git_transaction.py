from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from polar_pyro_plugin_sdk.git_transaction import GitWorkspaceTransaction
from polar_pyro_plugin_sdk.models import ContractError


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True, shell=False)
    return result.stdout.strip()


class GitTransactionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        git(self.repo, "init")
        git(self.repo, "config", "user.email", "polar-test@luxeron.dev")
        git(self.repo, "config", "user.name", "Polar Test")
        (self.repo / "artifact.txt").write_text("base\n", encoding="utf-8")
        git(self.repo, "add", "artifact.txt")
        git(self.repo, "commit", "-m", "base")

    def tearDown(self):
        subprocess.run(["git", "-C", str(self.repo), "worktree", "prune"], check=False, capture_output=True)
        self.temp.cleanup()

    def test_candidate_is_isolated_until_fast_forward_promotion(self):
        tx = GitWorkspaceTransaction.begin(self.repo, self.root / "transactions", "s1", "a1")
        (tx.worktree / "artifact.txt").write_text("candidate\n", encoding="utf-8")
        candidate = tx.commit_candidate("candidate")
        self.assertEqual((self.repo / "artifact.txt").read_text(encoding="utf-8"), "base\n")
        promoted = tx.promote_fast_forward(candidate, "certificate-1")
        self.assertEqual(promoted, candidate)
        self.assertEqual((self.repo / "artifact.txt").read_text(encoding="utf-8"), "candidate\n")

    def test_moved_head_rejects_stale_proof(self):
        tx = GitWorkspaceTransaction.begin(self.repo, self.root / "transactions", "s1", "a1")
        (tx.worktree / "artifact.txt").write_text("candidate\n", encoding="utf-8")
        candidate = tx.commit_candidate("candidate")
        (self.repo / "other.txt").write_text("concurrent\n", encoding="utf-8")
        git(self.repo, "add", "other.txt")
        git(self.repo, "commit", "-m", "concurrent")
        with self.assertRaisesRegex(ContractError, "HEAD moved"):
            tx.promote_fast_forward(candidate, "certificate-1")

    def test_dirty_canonical_checkout_is_rejected(self):
        (self.repo / "artifact.txt").write_text("dirty\n", encoding="utf-8")
        with self.assertRaisesRegex(ContractError, "must be clean"):
            GitWorkspaceTransaction.begin(self.repo, self.root / "transactions", "s1", "a1")

    def test_path_unsafe_attempt_identifier_is_rejected(self):
        with self.assertRaisesRegex(ContractError, "path-safe"):
            GitWorkspaceTransaction.begin(self.repo, self.root / "transactions", "../escape", "a1")


if __name__ == "__main__":
    unittest.main()

