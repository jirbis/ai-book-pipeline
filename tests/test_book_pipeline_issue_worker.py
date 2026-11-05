"""No-network tests for role task creation and idempotent Copilot assignment."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "book_pipeline" / "issue_worker.py"
spec = importlib.util.spec_from_file_location("issue_worker_under_test", SCRIPT)
worker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(worker)


def decision(stage="plan", key="c" * 20):
    return {"status": "ready", "book": "demo", "next_stage": stage,
            "source_pr": 17, "idempotency_key": key}


class FakeAPI:
    def __init__(self):
        self.calls = []
        self.existing = None

    def find_task(self, marker):
        self.calls.append(("find", marker))
        return self.existing

    def create_issue(self, title, body):
        self.calls.append(("create", title, body))
        return {"number": 24, "html_url": "https://github.com/demo/books/issues/24"}

    def assign_copilot(self, number, token):
        self.calls.append(("assign", number, token))


class BookIssueTests(unittest.TestCase):
    def test_dry_run_is_offline_and_scope_limited(self):
        result = worker.dispatch(decision(), "demo/books")
        self.assertEqual(result["status"], "dry_run")
        self.assertIn("books/demo/", result["body"])
        self.assertIn("book:plan", result["body"])
        self.assertIn("DRAFT PR", result["body"])

    def test_plan_writing_and_proofread_role_contracts(self):
        for stage, phrase in (("plan", "ORCHESTRATOR"),
                              ("manuscript", "CRITIC"),
                              ("proofread", "PROOFREADER")):
            text = worker.dispatch(decision(stage), "demo/books")["body"]
            self.assertIn(phrase, text)
            self.assertIn("human", text.lower())
        text = worker.dispatch(decision("manuscript"), "demo/books")["body"]
        self.assertIn("TWO revision cycles", text)

    def test_idempotency_existing_issue_prevents_reassignment(self):
        api = FakeAPI()
        api.existing = {"number": 12, "html_url": "https://github.com/demo/books/issues/12"}
        result = worker.dispatch(decision(), "demo/books", apply=True,
                                 assign_copilot=True, copilot_token="test", api=api)
        self.assertEqual(result["status"], "already_created")
        self.assertEqual(len(api.calls), 1)

    def test_create_without_copilot_is_explicit_queue(self):
        api = FakeAPI()
        result = worker.dispatch(decision(), "demo/books", apply=True, api=api)
        self.assertEqual(result["status"], "created_for_manual_assignment")
        self.assertEqual([x[0] for x in api.calls], ["find", "create"])

    def test_copilot_requires_token_and_assignment_is_explicit(self):
        api = FakeAPI()
        with self.assertRaises(ValueError):
            worker.dispatch(decision(), "demo/books", apply=True,
                            assign_copilot=True, api=api)
        self.assertFalse(api.calls)
        result = worker.dispatch(decision(), "demo/books", apply=True,
                                 assign_copilot=True, copilot_token="test", api=api)
        self.assertEqual(result["status"], "assigned_to_copilot")
        self.assertEqual([x[0] for x in api.calls], ["find", "create", "assign"])

    def test_assign_existing_copilot_checks_bot_marker_and_issue_state(self):
        api = FakeAPI()
        marker = "<!-- book-pipeline-task:" + "c" * 20 + " -->"
        api.get_issue = lambda number: {
            "number": number, "state": "open", "body": "Task\\n" + marker,
            "user": {"login": "github-actions[bot]"}, "assignees": [],
            "html_url": "https://github.com/demo/books/issues/24",
        }
        result = worker.assign_existing_copilot_task(
            "demo/books", 24, "c" * 20, copilot_token="test", api=api)
        self.assertEqual(result["status"], "assigned_to_copilot")
        self.assertEqual(api.calls[-1][0], "assign")

    def test_assign_existing_refuses_untrusted_or_modified_issue(self):
        api = FakeAPI()
        marker = "<!-- book-pipeline-task:" + "c" * 20 + " -->"
        issue = {
            "number": 24, "state": "open", "body": marker,
            "user": {"login": "attacker"}, "assignees": [],
        }
        api.get_issue = lambda number: issue
        with self.assertRaises(ValueError):
            worker.assign_existing_copilot_task(
                "demo/books", 24, "c" * 20, copilot_token="test", api=api)
        issue["user"]["login"] = "github-actions[bot]"
        issue["body"] = "Wrong marker"
        with self.assertRaises(ValueError):
            worker.assign_existing_copilot_task(
                "demo/books", 24, "c" * 20, copilot_token="test", api=api)
        issue["body"] = marker
        issue["state"] = "closed"
        with self.assertRaises(ValueError):
            worker.assign_existing_copilot_task(
                "demo/books", 24, "c" * 20, copilot_token="test", api=api)
        self.assertFalse(api.calls)

    def test_assign_existing_requires_pat_and_valid_routing_key(self):
        api = FakeAPI()
        with self.assertRaises(ValueError):
            worker.assign_existing_copilot_task(
                "demo/books", 24, "c" * 20, copilot_token="", api=api)
        with self.assertRaises(ValueError):
            worker.assign_existing_copilot_task(
                "demo/books", 24, "wrong", copilot_token="test", api=api)
        self.assertFalse(api.calls)

    def test_invalid_plan_rejected_before_network(self):
        for invalid in (
            {**decision(), "status": "skip"},
            {**decision(), "book": "../escape"},
            {**decision(), "idempotency_key": "wrong"},
            {**decision(), "next_stage": "publish"},
        ):
            with self.assertRaises(ValueError):
                worker.dispatch(invalid, "demo/books", apply=True, api=FakeAPI())


if __name__ == "__main__":
    unittest.main()
