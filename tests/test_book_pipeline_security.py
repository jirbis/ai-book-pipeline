"""Offline security tests for trusted execution and pre-merge book PR gates."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROUTER = REPO / "scripts" / "book_pipeline" / "router.py"
GUARD = REPO / "scripts" / "book_pipeline" / "pr_scope_guard.py"
WORKER = REPO / "scripts" / "book_pipeline" / "issue_worker.py"


def imported(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


router = imported(ROUTER, "router_security_test")
worker = imported(WORKER, "worker_security_test")


def pr(label="book:materials", base="main"):
    return {"number": 3, "merged": False, "base": {"ref": base},
            "labels": [{"name": label}], "head": {"ref": "untrusted"}}


class BookScopeSecurityTests(unittest.TestCase):
    def test_book_pr_scope_valid_before_merge(self):
        result = router.preflight(pr(), [
            {"filename": "books/demo/files/import/notes.md", "status": "added"}])
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["book"], "demo")

    def test_out_of_scope_pr_blocks_before_merge(self):
        for filename in (".github/workflows/book-transition-router.yml",
                         "scripts/book_pipeline/issue_worker.py",
                         "books/another/files/import/notes.md"):
            changed = [{"filename": "books/demo/files/import/notes.md",
                        "status": "added"},
                       {"filename": filename, "status": "modified"}]
            outcome = router.preflight(pr(), changed)
            self.assertEqual(outcome["status"], "blocked", filename)

    def test_preflight_rejects_renamed_origins_and_removed_only_materials(self):
        changed = [{"filename": "books/demo/files/import/renamed.md",
                    "status": "renamed",
                    "previous_filename": ".github/workflows/book-transition-router.yml"}]
        self.assertEqual(router.preflight(pr(), changed)["status"], "blocked")
        removed = [{"filename": "books/demo/files/import/old.md",
                    "status": "removed"}]
        self.assertEqual(router.preflight(pr(), removed)["status"], "blocked")

    def test_preflight_allows_valid_change_with_scoped_deletion(self):
        changes = [
            {"filename": "books/demo/files/import/old.md", "status": "removed"},
            {"filename": "books/demo/files/import/new.md", "status": "added"},
        ]
        self.assertEqual(router.preflight(pr(), changes)["status"], "ok")

    def test_preflight_wrong_label_and_base_fail_closed(self):
        self.assertEqual(router.preflight(pr("book:unknown"), [])["status"], "blocked")
        self.assertEqual(router.preflight(pr(base="feature"), [
            "books/demo/files/import/notes.md"])["status"], "blocked")
        normal = {"labels": [], "base": {"ref": "main"}}
        self.assertEqual(router.preflight(normal, ["README.md"])["status"], "skip")

    def test_cli_scope_guard_rejects_bad_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p, files = root / "pr.json", root / "files.json"
            p.write_text(json.dumps(pr()), encoding="utf-8")
            files.write_text(json.dumps([{"filename": "books/demo/files/import/ok.md",
                "status": "added"}]), encoding="utf-8")
            def run():
                return subprocess.run(
                    [sys.executable, str(GUARD), "--pr", str(p), "--files", str(files)],
                    text=True, capture_output=True, check=False
                )
            self.assertEqual(run().returncode, 0)
            files.write_text(json.dumps([{"filename": "scripts/book_pipeline/router.py",
                "status": "modified"}]), encoding="utf-8")
            self.assertEqual(run().returncode, 2)

    def test_worker_has_proper_markdown(self):
        task = worker.dispatch(
            {"status": "ready", "book": "demo", "next_stage": "plan",
             "source_pr": 3, "idempotency_key": "a" * 20}, "org/books")
        self.assertIn("**Scope:** `books/demo/`", task["body"])
        self.assertIn("`book:plan`", task["body"])
        self.assertNotIn(chr(92) + chr(96), task["body"])

    def test_merged_pr_workflow_runs_default_branch_only(self):
        content = (REPO / ".github/workflows/book-transition-router.yml").read_text()
        self.assertIn("pull_request_target:", content)
        self.assertNotIn("\n  pull_request:", content)
        self.assertIn("ref: ${{ github.event.repository.default_branch }}", content)
        self.assertIn("persist-credentials: false", content)
        self.assertNotIn("github.event.pull_request.head", content)
        self.assertIn("github.event.pull_request.merged == true", content)

    def test_premerge_scope_check_has_no_secrets_or_write_access(self):
        content = (REPO / ".github/workflows/book-pr-scope.yml").read_text()
        self.assertIn("pull_request_target:", content)
        self.assertIn("contents: read", content)
        self.assertIn("pull-requests: read", content)
        self.assertNotIn("issues: write", content)
        self.assertNotIn("secrets.", content)
        self.assertIn("ref: ${{ github.event.repository.default_branch }}", content)

    def test_copilot_token_only_loaded_when_enabled(self):
        workflow = (REPO / ".github/workflows/book-transition-router.yml").read_text()
        self.assertEqual(workflow.count("secrets.COPILOT_USER_TOKEN"), 1)
        self.assertIn("vars.BOOK_PIPELINE_ASSIGN_COPILOT == 'true'", workflow)
        self.assertIn("vars.BOOK_PIPELINE_ASSIGN_COPILOT != 'true'", workflow)

    def test_codeowners_covers_privileged_files(self):
        content = (REPO / ".github/CODEOWNERS").read_text()
        self.assertIn("/.github/workflows/ @jirbis", content)
        self.assertIn("/scripts/book_pipeline/ @jirbis", content)
        self.assertIn("/.github/CODEOWNERS @jirbis", content)


if __name__ == "__main__":
    unittest.main()
