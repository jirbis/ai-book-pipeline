"""Integration tests for the portable book-authoring skill.

All mutable fixtures are under TemporaryDirectory, never in my-books/.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
ADAPTER = REPO / "skills" / "book-authoring" / "scripts" / "book.py"


class BookAuthoringAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="book-authoring-test-")
        self.addCleanup(self.temp.cleanup)
        self.books_root = Path(self.temp.name) / "books"

    def command(self, *parts, env=None):
        argv = [
            sys.executable, str(ADAPTER),
            "--repo", str(REPO), "--books-root", str(self.books_root), *parts,
        ]
        return subprocess.run(argv, text=True, capture_output=True, env=env, check=False)

    def test_status_does_not_create_missing_book(self):
        result = self.command("status", "missing")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not exist", result.stderr)
        self.assertFalse(self.books_root.exists())

    def test_init_requires_confirmation_and_refuses_existing_book(self):
        denied = self.command("init", "new-book", "--type", "fiction")
        self.assertNotEqual(denied.returncode, 0)
        self.assertIn("--confirm-write", denied.stderr)
        self.assertFalse(self.books_root.exists())

        created = self.command("init", "new-book", "--type", "fiction", "--confirm-write")
        self.assertEqual(created.returncode, 0, created.stderr)
        project = self.books_root / "new-book" / "config" / "PROJECT.md"
        self.assertTrue(project.is_file())
        self.assertTrue((self.books_root / "new-book" / "files" / "content" / "chapters").is_dir())
        before = project.read_bytes()

        repeated = self.command("init", "new-book", "--type", "fiction", "--confirm-write")
        self.assertNotEqual(repeated.returncode, 0)
        self.assertIn("existing book directory", repeated.stderr)
        self.assertEqual(before, project.read_bytes())

    def test_status_phase_and_phase_validator_use_existing_engine(self):
        created = self.command("init", "demo-book", "--type", "fiction", "--confirm-write")
        self.assertEqual(created.returncode, 0, created.stderr)
        project = self.books_root / "demo-book" / "config" / "PROJECT.md"
        original = project.read_text(encoding="utf-8")
        self.assertIn("`non-fiction` / `fiction`", original)
        project.write_text(original.replace("`non-fiction` / `fiction`", "`fiction`"), encoding="utf-8")

        status = self.command("status", "demo-book")
        self.assertEqual(status.returncode, 0, status.stderr)
        self.assertIn("Type: fiction", status.stdout)

        phase = self.command("phase", "demo-book", "draft")
        self.assertEqual(phase.returncode, 0, phase.stderr)
        self.assertIn("PHASE 2: Writing Drafts", phase.stdout)

        checked = self.command("validate-phase", "demo-book", "1")
        self.assertIn(checked.returncode, (0, 1, 2), checked.stderr)
        self.assertTrue(checked.stdout.strip())
        self.assertEqual("fiction", project.read_text(encoding="utf-8").split("**Type** |")[1].split("|")[0].strip().strip("`"))

    def test_rejects_paths_and_symlinks_outside_books_root(self):
        for bad in ("../escape", "/tmp/book", ".", "nested/book"):
            result = self.command("status", bad)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("single directory slug", result.stderr)

        self.books_root.mkdir()
        external = Path(self.temp.name) / "external-book"
        external.mkdir()
        (self.books_root / "redirect").symlink_to(external, target_is_directory=True)
        escaped = self.command("status", "redirect")
        self.assertNotEqual(escaped.returncode, 0)
        self.assertIn("outside the books root", escaped.stderr)

    def test_final_check_is_read_only_and_uses_engine_collectors(self):
        chapters = self.books_root / "manuscript" / "files" / "content" / "chapters"
        chapters.mkdir(parents=True)
        (chapters / "chapter-1-draft-v1.md").write_text("Draft", encoding="utf-8")
        (chapters / "chapter-2-final.md").write_text("Final", encoding="utf-8")
        original = {p.name: p.read_bytes() for p in chapters.iterdir()}

        missing = self.command("final-check", "manuscript")
        self.assertEqual(missing.returncode, 1, missing.stderr)
        report = json.loads(missing.stdout)
        self.assertEqual(report["status"], "missing_finals")
        self.assertEqual(report["missing_finals"], [1])
        self.assertTrue(report["read_only"])
        self.assertFalse((self.books_root / "manuscript" / "files" / "handoff").exists())
        self.assertEqual(original, {p.name: p.read_bytes() for p in chapters.iterdir()})

        (chapters / "chapter-1-final.md").write_text("Final", encoding="utf-8")
        complete = self.command("final-check", "manuscript")
        self.assertEqual(complete.returncode, 0, complete.stderr)
        self.assertEqual(json.loads(complete.stdout)["status"], "ok")

    def test_external_skill_can_find_repo_using_environment(self):
        env = os.environ.copy()
        env["BOOK_PIPELINE_REPO"] = str(REPO)
        cmd = [
            sys.executable, str(ADAPTER), "--books-root", str(self.books_root),
            "status", "missing",
        ]
        result = subprocess.run(cmd, env=env, text=True, capture_output=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Book directory does not exist", result.stderr)


if __name__ == "__main__":
    unittest.main()
