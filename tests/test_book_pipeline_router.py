"""Tests for deterministic, fail-closed, event-driven book transition routing."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "book_pipeline" / "router.py"
spec = importlib.util.spec_from_file_location("book_router_under_test", SCRIPT)
router = importlib.util.module_from_spec(spec)
spec.loader.exec_module(router)
SHA = "a" * 40


def make_pr(gate="materials", *, number=7, merged=True, merged_by="User", sha=SHA):
    return {
        "number": number, "merged": merged, "base": {"ref": "main"},
        "merged_by": {"type": merged_by},
        "merge_commit_sha": sha, "labels": [{"name": f"book:{gate}"}],
    }


class BookRoutingTests(unittest.TestCase):
    def test_materials_merge_routes_to_plan(self):
        r = router.classify(make_pr(), [
            {"filename": "books/demo/files/import/notes.md"},
            {"filename": "books/demo/config/PROJECT.md"},
        ])
        self.assertEqual((r["status"], r["next_stage"], r["book"]),
                         ("ready", "plan", "demo"))
        self.assertIn("book-pipeline-task:", r["task_marker"])

    def test_plan_merge_routes_to_manuscript(self):
        r = router.classify(make_pr("plan"), [
            {"filename": "books/demo/config/outline.md"},
            {"filename": "books/demo/config/author-voice.md"},
        ])
        self.assertEqual(r["next_stage"], "manuscript")

    def test_manuscript_merge_routes_to_proofread(self):
        r = router.classify(make_pr("manuscript"),
                            ["books/demo/files/content/chapters/chapter-1-draft-v1.md"])
        self.assertEqual(r["next_stage"], "proofread")

    def test_proofread_merge_stops_before_publication(self):
        r = router.classify(make_pr("proofread"),
                            ["books/demo/files/proofread/chapter-1-report.md"])
        self.assertEqual(r["status"], "hold")
        self.assertNotIn("next_stage", r)

    def test_non_book_pr_and_unmerged_are_ignored(self):
        p = make_pr()
        p["labels"] = []
        self.assertEqual(router.classify(p, ["README.md"])["status"], "skip")
        self.assertEqual(router.classify(make_pr(merged=False),
                                         ["books/demo/files/import/file.md"])["status"], "skip")

    def test_human_merge_required(self):
        r = router.classify(make_pr(merged_by="Bot"), ["books/demo/files/import/file.md"])
        self.assertEqual(r["reason"], "human_merge_required")

    def test_single_book_only_and_no_engine_files(self):
        r = router.classify(make_pr(), ["books/demo/files/import/a.md",
                                        "books/another/files/import/b.md"])
        self.assertEqual(r["reason"], "multiple_books")
        r = router.classify(make_pr(), ["books/demo/files/import/a.md", "engine/cli.py"])
        self.assertEqual(r["status"], "blocked")

    def test_deletions_do_not_unlock_a_gate(self):
        r = router.classify(make_pr(), [
            {"filename": "books/demo/files/import/removed-note.md", "status": "removed"}
        ])
        self.assertEqual(r["reason"], "missing_active_stage_artifacts")

    def test_valid_edit_with_scoped_deletion_is_allowed(self):
        r = router.classify(make_pr(), [
            {"filename": "books/demo/files/import/old.md", "status": "removed"},
            {"filename": "books/demo/files/import/new.md", "status": "added"},
        ])
        self.assertEqual(r["status"], "ready")
        self.assertEqual(r["book"], "demo")

    def test_deletion_plus_nonessential_edit_does_not_unlock_gate(self):
        r = router.classify(make_pr("plan"), [
            {"filename": "books/demo/config/outline.md", "status": "removed"},
            {"filename": "books/demo/config/PROJECT.md", "status": "modified"},
        ])
        self.assertEqual(r["status"], "blocked")
        self.assertEqual(r["reason"], "missing_active_stage_artifacts")

    def test_rename_cannot_hide_out_of_scope_previous_path(self):
        r = router.classify(make_pr(), [{
            "filename": "books/demo/files/import/a.md",
            "previous_filename": "books/another/files/import/a.md",
            "status": "renamed"
        }])
        self.assertEqual(r["reason"], "multiple_books")

    def test_missing_required_plan_and_wrong_gate(self):
        p = router.classify(make_pr("plan"), ["books/demo/config/PROJECT.md"])
        self.assertEqual(p["status"], "blocked")
        p = make_pr()
        p["labels"].append({"name": "book:plan"})
        self.assertEqual(router.classify(p, ["books/demo/files/import/a.md"])["status"], "blocked")

    def test_rejects_traversal_unsafe_root_and_invalid_sha(self):
        for bad in ("books/demo/../files/import/a.md", "books/demo/.git/config",
                    "books/../../files/import/a.md", "books/demo/files//a.md"):
            self.assertEqual(router.classify(make_pr(), [bad])["status"], "blocked")
        self.assertEqual(router.classify(make_pr(), ["books/demo/files/import/a.md"],
                                         books_prefix="../x")["status"], "blocked")
        self.assertEqual(router.classify(make_pr(sha="bad"),
                                         ["books/demo/files/import/a.md"])["status"], "blocked")

    def test_stable_idempotency_key_and_event_cli(self):
        r1 = router.classify(make_pr(), ["books/demo/files/import/a.md"])
        r2 = router.classify(make_pr(), ["books/demo/files/import/a.md"])
        self.assertEqual(r1["idempotency_key"], r2["idempotency_key"])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "event.json").write_text(
                json.dumps({"pull_request": make_pr()}), encoding="utf-8")
            (root / "files.json").write_text(
                json.dumps([{"filename": "books/demo/files/import/a.md"}]),
                encoding="utf-8")
            p = subprocess.run([
                sys.executable, str(SCRIPT), "--event", str(root / "event.json"),
                "--files", str(root / "files.json"), "--github-output", str(root / "output")
            ], capture_output=True, text=True, check=False)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(json.loads(p.stdout)["idempotency_key"], r1["idempotency_key"])
            self.assertIn("status=ready", (root / "output").read_text())


if __name__ == "__main__":
    unittest.main()
