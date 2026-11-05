"""Tests for opt-in GitHub manuscript workflows; use temporary git repositories only."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "skills" / "book-authoring" / "scripts" / "github_workspace.py"


class GitHubBookWorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="github-book-test-")
        self.addCleanup(self.tmp.cleanup)
        self.checkout = Path(self.tmp.name) / "my-books-repo"
        self.checkout.mkdir()
        self.git("init", "-b", "main")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "Book Test")
        (self.checkout / "README.md").write_text("# Sample manuscript repository\n", encoding="utf-8")
        self.git("add", "README.md")
        self.git("commit", "-m", "Base")

    def git(self, *args):
        return subprocess.run(
            ["git", "-C", str(self.checkout), *args],
            check=True, capture_output=True, text=True,
        ).stdout.strip()

    def tool(self, *args, books_dir="books", cwd=None):
        return subprocess.run([
            sys.executable, str(SCRIPT),
            "--checkout", str(self.checkout if cwd is None else cwd),
            "--books-dir", books_dir, *args,
        ], text=True, capture_output=True, check=False)

    def book_file(self, slug="my-book"):
        folder = self.checkout / "books" / slug / "config"
        folder.mkdir(parents=True, exist_ok=True)
        file = folder / "PROJECT.md"
        file.write_text("# Chapter outline\n", encoding="utf-8")
        return file

    def start_book_branch(self):
        result = self.tool("start", "my-book", "--confirm-write")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git("branch", "--show-current"), "book/my-book/draft")

    def test_inspect_is_read_only(self):
        before = self.git("rev-parse", "HEAD")
        result = self.tool("inspect", "my-book")
        self.assertEqual(result.returncode, 0, result.stderr)
        status = json.loads(result.stdout)
        self.assertEqual(status["branch"], "main")
        self.assertEqual(status["book"], "books/my-book")
        self.assertFalse(status["book_exists"])
        self.assertTrue(status["read_only"])
        self.assertEqual(before, self.git("rev-parse", "HEAD"))

    def test_branch_creation_is_explicit_and_requires_clean_checkout(self):
        denied = self.tool("start", "my-book")
        self.assertNotEqual(denied.returncode, 0)
        self.assertEqual(self.git("branch", "--show-current"), "main")

        (self.checkout / "dirty.txt").write_text("uncommitted", encoding="utf-8")
        dirty = self.tool("start", "my-book", "--confirm-write")
        self.assertNotEqual(dirty.returncode, 0)
        self.assertIn("uncommitted", dirty.stderr)
        (self.checkout / "dirty.txt").unlink()

        self.start_book_branch()
        repeated = self.tool("start", "my-book", "--confirm-write")
        self.assertNotEqual(repeated.returncode, 0)

    def test_book_commit_is_scoped_and_never_mutates_main(self):
        self.start_book_branch()
        self.book_file()
        denied = self.tool("commit-book", "my-book", "--message", "Draft")
        self.assertNotEqual(denied.returncode, 0)

        committed = self.tool(
            "commit-book", "my-book", "--message", "Draft", "--confirm-write"
        )
        self.assertEqual(committed.returncode, 0, committed.stderr)
        self.assertIn("books/my-book/config/PROJECT.md",
                      self.git("show", "--pretty=format:", "--name-only", "HEAD"))
        self.assertEqual(self.git("branch", "--show-current"), "book/my-book/draft")
        self.assertNotIn("books/my-book/config/PROJECT.md",
                         self.git("ls-tree", "-r", "--name-only", "main"))
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_commit_refuses_changes_in_other_books(self):
        self.start_book_branch()
        self.book_file()
        other = self.checkout / "books" / "other-book" / "chapter.md"
        other.parent.mkdir(parents=True)
        other.write_text("Not part of this review\n", encoding="utf-8")
        denied = self.tool(
            "commit-book", "my-book", "--message", "Draft", "--confirm-write"
        )
        self.assertNotEqual(denied.returncode, 0)
        self.assertIn("outside this book", denied.stderr)
        self.assertNotIn("books/my-book/config/PROJECT.md",
                         self.git("ls-tree", "-r", "--name-only", "HEAD"))
        other.unlink()
        success = self.tool(
            "commit-book", "my-book", "--message", "Draft", "--confirm-write"
        )
        self.assertEqual(success.returncode, 0, success.stderr)

    def test_refuses_main_branch_commit_and_remote_push_without_approval(self):
        self.book_file()
        denied = self.tool(
            "commit-book", "my-book", "--message", "Draft", "--confirm-write"
        )
        self.assertNotEqual(denied.returncode, 0)
        self.assertIn("not main", denied.stderr)
        no_push = self.tool("push-branch", "my-book")
        self.assertNotEqual(no_push.returncode, 0)
        self.assertIn("--confirm-remote-write", no_push.stderr)

    def test_rejects_traversal_symlinks_and_unrelated_branch(self):
        for slug in ("../escape", ".", "nested/book"):
            bad = self.tool("inspect", slug)
            self.assertNotEqual(bad.returncode, 0)
        escaped = self.tool("inspect", "my-book", books_dir="../outside")
        self.assertNotEqual(escaped.returncode, 0)

        external = Path(self.tmp.name) / "external"
        external.mkdir()
        (self.checkout / "books").mkdir()
        (self.checkout / "books" / "my-book").symlink_to(external, target_is_directory=True)
        unsafe = self.tool("inspect", "my-book")
        self.assertNotEqual(unsafe.returncode, 0)

    def test_non_github_remote_is_rejected_for_push(self):
        self.start_book_branch()
        self.git("remote", "add", "origin", "https://example.com/not-github/repo.git")
        self.assertNotEqual(self.tool(
            "push-branch", "my-book", "--confirm-remote-write"
        ).returncode, 0)


if __name__ == "__main__":
    unittest.main()
