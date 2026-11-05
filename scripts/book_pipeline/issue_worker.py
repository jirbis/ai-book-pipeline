#!/usr/bin/env python3
"""Issue-backed role dispatch: idempotent, explicit, fail-closed.

Without --apply this only prints a proposed issue. With --apply, create at
most one task issue for a validated merged-PR decision. Optional Copilot
assignment requires an explicit user-to-server token and opt-in.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
KEY = re.compile(r"^[a-f0-9]{20}$")
SLUG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")
STAGES = ("plan", "manuscript", "proofread")

TASK_INSTRUCTIONS = {
    "plan": (
        "Act as IMPORTER + ORCHESTRATOR. Read the merged book source materials, "
        "config/PROJECT.md (if present), config/author-voice.md and the authoritative "
        "engine/agents/WORKFLOW.md. Propose config/PROJECT.md, config/outline.md "
        "(or config/plot.md for fiction), author-voice guidance, and handoffs. "
        "Preserve originals. Do not begin drafting chapters. "
        "Open a DRAFT PR scoped to this book; propose label book:plan. "
        "The author must approve and merge the plan PR before any writing starts."
    ),
    "manuscript": (
        "Use the approved plan. Work on ONE chapter only. Follow the roles "
        "RESEARCHER (if non-fiction) → WRITER → EDITOR → CRITIC. "
        "Do at most TWO revision cycles. Preserve previous draft versions and "
        "sources; never invent citations. Record Critic verdict, unresolved "
        "issues and handoffs. Open a DRAFT PR scoped to this book; propose "
        "label book:manuscript. STOP for human approval before proofreading."
    ),
    "proofread": (
        "Act as PROOFREADER on the author-approved chapter. Read author voice, "
        "style guide and latest approved chapter; preserve intentional language. "
        "Prepare proofreading report and proposed chapter finals. "
        "Open a DRAFT PR with label book:proofread. "
        "STOP: publication/export to Kindle requires separate human authorization."
    ),
}


def task_text(plan: dict, *, books_prefix: str = "books") -> tuple[str, str]:
    if plan.get("status") != "ready":
        raise ValueError("Only ready routing decisions may create tasks.")
    book = plan.get("book")
    stage = plan.get("next_stage")
    key = plan.get("idempotency_key")
    pr = plan.get("source_pr")
    if (not isinstance(book, str) or not SLUG.fullmatch(book) or book in {".", ".."}
            or stage not in STAGES or not isinstance(key, str) or not KEY.fullmatch(key)
            or not isinstance(pr, int) or isinstance(pr, bool) or pr < 1
            or not SLUG.fullmatch(books_prefix) or books_prefix in {".", ".."}):
        raise ValueError("Malformed routing decision.")
    folder = f"{books_prefix}/{book}/"
    title = f"[book-pipeline] {book}: {stage} (from PR #{pr})"
    body = f"""# Book pipeline task

<!-- book-pipeline-task:{key} -->

**Book:** {book}
**Phase:** {stage}
**Source:** merged PR #{pr}
**Scope:** `{folder}`

## Agent instructions

{TASK_INSTRUCTIONS[stage]}

Read `skills/book-authoring/SKILL.md` and `engine/agents/AGENTS.md` if installed
in this repository. If the manuscripts are in a separate repository, install
the canonical skill and provide authorized access to the engine first.

**File boundary:** edit only `{folder}`. Do not change `main` directly,
modify another book, merge PRs, expose unpublished material publicly or
publish to Amazon. Add the proposed `book:{stage}`
label before the author merges the resulting PR. The author must check it.

**Human gate:** The agent's result is a proposed Draft PR, not authorization
for a merge or public release. Stop after the Draft PR and its review report.
"""
    return title, body


class GitHubAPI:
    def __init__(self, repo: str, token: str):
        if not isinstance(repo, str) or not REPO.fullmatch(repo):
            raise ValueError("Invalid owner/repo.")
        if not token:
            raise ValueError("Missing authenticated GitHub token.")
        self.repo = repo
        self.token = token

    def request(self, method: str, path: str, payload: dict | None = None,
                token: str | None = None) -> object:
        raw = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = urllib.request.Request(
            "https://api.github.com" + path, data=raw, method=method,
            headers={
                "Authorization": "Bearer " + (token or self.token),
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                **({"Content-Type": "application/json"} if raw is not None else {}),
            },
        )
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))

    def find_task(self, marker: str) -> dict | None:
        """Scan issues INCLUDING PRs; fail closed if pagination is too large."""
        for page in range(1, 11):
            data = self.request(
                "GET",
                f"/repos/{self.repo}/issues?state=all&per_page=100&page={page}"
            )
            if not isinstance(data, list):
                raise ValueError("Invalid GitHub issues response.")
            for item in data:
                if isinstance(item, dict) and marker in (item.get("body") or ""):
                    return item
            if len(data) < 100:
                return None
        raise ValueError("Too many issues to safely establish task idempotency.")

    def create_issue(self, title: str, body: str) -> dict:
        data = self.request("POST", f"/repos/{self.repo}/issues",
                            {"title": title, "body": body})
        if not isinstance(data, dict) or not isinstance(data.get("number"), int):
            raise ValueError("Invalid GitHub issue creation response.")
        return data

    def assign_copilot(self, issue_number: int, token: str) -> object:
        """Copilot issue assignment API requires a user-to-server token."""
        return self.request(
            "POST", f"/repos/{self.repo}/issues/{issue_number}/assignees",
            {
                "assignees": ["copilot-swe-agent[bot]"],
                "agent_assignment": {
                    "target_repo": self.repo,
                    "base_branch": "main",
                    "custom_instructions": (
                        "Use the book-authoring skill; edit only the selected "
                        "book directory; stop at a Draft PR for human review."
                    ),
                },
            }, token=token,
        )


def dispatch(plan: dict, repo: str, *, apply: bool = False,
             assign_copilot: bool = False, books_prefix: str = "books",
             api: GitHubAPI | None = None, copilot_token: str = "") -> dict:
    title, body = task_text(plan, books_prefix=books_prefix)
    if not REPO.fullmatch(repo):
        raise ValueError("Invalid owner/repo.")
    if not apply:
        return {"status": "dry_run", "title": title, "body": body}
    if assign_copilot and not copilot_token:
        raise ValueError("Copilot assignment requires an explicit user-to-server token.")
    if api is None:
        api = GitHubAPI(repo, os.getenv("GH_TOKEN", ""))
    marker = f"<!-- book-pipeline-task:{plan['idempotency_key']} -->"
    existing = api.find_task(marker)
    if existing is not None:
        # Never restart an already handled (possibly completed) task.
        return {"status": "already_created", "issue": existing.get("number"),
                "url": existing.get("html_url")}
    created = api.create_issue(title, body)
    issue_no = created["number"]
    if assign_copilot:
        api.assign_copilot(issue_no, copilot_token)
        return {"status": "assigned_to_copilot", "issue": issue_no,
                "url": created.get("html_url")}
    return {"status": "created_for_manual_assignment", "issue": issue_no,
            "url": created.get("html_url")}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--decision", type=Path, required=True)
    p.add_argument("--repo", required=True)
    p.add_argument("--books-prefix", default="books")
    p.add_argument("--apply", action="store_true")
    p.add_argument("--assign-copilot", action="store_true")
    a = p.parse_args(argv)
    try:
        plan = json.loads(a.decision.read_text(encoding="utf-8"))
        if plan.get("status") != "ready":
            print(json.dumps({"status": "skipped", "reason": plan.get("reason")}))
            return 0
        result = dispatch(
            plan, a.repo, apply=a.apply, assign_copilot=a.assign_copilot,
            books_prefix=a.books_prefix,
            copilot_token=os.getenv("COPILOT_USER_TOKEN", ""),
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (ValueError, OSError, urllib.error.URLError, TypeError) as e:
        # Do not echo request headers, tokens, or raw API responses.
        print(f"Book dispatch failed closed: {type(e).__name__}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
