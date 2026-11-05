#!/usr/bin/env python3
"""Deterministic, read-only router for merged book PRs.

Input: GitHub's pull request JSON + paginated PR file list (never PR title).
Output: one decision JSON. No GitHub write, LLM invocation or publication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SLUG = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,99}$")
SHA = re.compile(r"^[0-9a-f]{40}$")
GATES = {
    "materials": "plan",
    "plan": "manuscript",
    "manuscript": "proofread",
    "proofread": "hold",
}
LABEL_PREFIX = "book:"


def decision(reason: str, *, status: str = "skip", **details: object) -> dict:
    return {"status": status, "reason": reason, **details}


def valid_paths(stage: str, relative: list[str]) -> bool:
    """Allow only expected deliverables; require the stage's essential artifact."""
    essentials = {
        "materials": ("files/import/",),
        "plan": ("config/outline.md", "config/plot.md"),
        "manuscript": ("files/content/chapters/",),
        "proofread": ("files/proofread/",),
    }
    permissions = {
        "materials": ("files/import/", "config/PROJECT.md", "config/author-voice.md"),
        "plan": (
            "config/PROJECT.md", "config/author-voice.md", "config/outline.md",
            "config/plot.md", "config/characters.md", "config/world.md",
            "config/style-guide.md", "config/review-checklist.md",
            "config/progress.md", "files/research/", "files/handoff/"
        ),
        "manuscript": (
            "config/progress.md", "files/content/chapters/", "files/research/",
            "files/edits/", "files/reviews/", "files/handoff/"
        ),
        "proofread": (
            "config/progress.md", "files/proofread/", "files/content/chapters/",
            "files/handoff/", "files/reviews/"
        ),
    }
    if not relative:
        return False
    allowed = permissions[stage]
    for item in relative:
        if not any(item == p or (p.endswith("/") and item.startswith(p)) for p in allowed):
            return False
    return any(any(p == item or (p.endswith("/") and item.startswith(p))
                   for p in essentials[stage]) for item in relative)


def validate_stage_scope(stage: str, changed_files: list,
                         *, books_prefix: str = "books") -> dict:
    """Shared read-only scope validator for pre-merge CI and post-merge routing."""
    if stage not in GATES:
        return decision("unknown_gate", status="blocked")
    if not isinstance(changed_files, list):
        return decision("invalid_changed_file_list", status="blocked")
    if not isinstance(books_prefix, str) or not SLUG.fullmatch(books_prefix) or books_prefix in {".", ".."}:
        return decision("invalid_books_prefix", status="blocked")
    if not changed_files or len(changed_files) > 300:
        return decision("missing_or_excessive_changes", status="blocked")

    book = None
    relative = []
    for item in changed_files:
        if isinstance(item, str):
            paths = [item]
        elif isinstance(item, dict) and isinstance(item.get("filename"), str):
            # A deletion-only merge must not launch an agent on missing source files.
            if item.get("status") == "removed":
                return decision("deleted_files_do_not_unlock_gate", status="blocked")
            paths = [item["filename"]]
            if item.get("previous_filename"):
                paths.append(item["previous_filename"])
        else:
            return decision("invalid_changed_path", status="blocked")
        for filename in paths:
            parts = filename.split("/")
            if (len(parts) < 4 or parts[0] != books_prefix or
                    not SLUG.fullmatch(parts[1]) or parts[1] in {".", ".."} or
                    any(x in {"", ".", "..", ".git"} for x in parts)):
                return decision("unscoped_or_unsafe_file", status="blocked")
            if book is not None and parts[1] != book:
                return decision("multiple_books", status="blocked")
            book = parts[1]
            relative.append("/".join(parts[2:]))

    if not valid_paths(stage, relative):
        return decision("unexpected_or_missing_stage_artifacts", status="blocked")
    return {"status": "ok", "book": book, "source_paths": sorted(set(relative))}


def preflight(pr: dict, changed_files: list, *, books_prefix: str = "books",
              target_branch: str = "main") -> dict:
    """Require a book-labeled PR to remain within one book before merge."""
    if not isinstance(pr, dict) or not isinstance(changed_files, list):
        return decision("invalid_input", status="blocked")
    labels = [item.get("name") for item in pr.get("labels", [])
              if isinstance(item, dict)]
    book_labels = [label for label in labels if isinstance(label, str) and
                   label.startswith(LABEL_PREFIX)]
    if not book_labels:
        return decision("not_a_book_gate")
    if pr.get("base", {}).get("ref") != target_branch:
        return decision("not_target_branch", status="blocked")
    if len(book_labels) != 1 or book_labels[0][len(LABEL_PREFIX):] not in GATES:
        return decision("unknown_or_multiple_gates", status="blocked")
    stage = book_labels[0][len(LABEL_PREFIX):]
    scope = validate_stage_scope(stage, changed_files, books_prefix=books_prefix)
    if scope["status"] != "ok":
        return scope
    return decision("book_pr_scope_valid", status="ok", gate=stage,
                    book=scope["book"], source_paths=scope["source_paths"])


def classify(pr: dict, changed_files: list, *, books_prefix: str = "books",
             target_branch: str = "main") -> dict:
    """Fail closed on ambiguity; never infer stage from a title or code PR."""
    if not isinstance(pr, dict) or not isinstance(changed_files, list):
        return decision("invalid_input", status="blocked")
    if pr.get("merged") is not True:
        return decision("not_merged")
    if pr.get("base", {}).get("ref") != target_branch:
        return decision("not_target_branch")
    labels = [x.get("name") for x in pr.get("labels", []) if isinstance(x, dict)]
    stage_labels = [x for x in labels if isinstance(x, str) and x.startswith(LABEL_PREFIX)]
    if not stage_labels:
        return decision("not_a_book_gate")
    if len(stage_labels) != 1 or stage_labels[0][len(LABEL_PREFIX):] not in GATES:
        return decision("unknown_or_multiple_gates", status="blocked")
    stage = stage_labels[0][len(LABEL_PREFIX):]
    # Only human-merged PRs can unlock a gate.
    if pr.get("merged_by", {}).get("type") != "User":
        return decision("human_merge_required", status="blocked")
    merge_sha = pr.get("merge_commit_sha")
    if not isinstance(merge_sha, str) or not SHA.fullmatch(merge_sha):
        return decision("invalid_merge_sha", status="blocked")
    scope = validate_stage_scope(stage, changed_files, books_prefix=books_prefix)
    if scope["status"] != "ok":
        return scope
    book = scope["book"]
    relative = scope["source_paths"]
    next_stage = GATES[stage]
    if next_stage == "hold":
        return decision("publication_requires_separate_human_authorization",
                        status="hold", book=book, gate=stage, merge_sha=merge_sha)
    source_pr = pr.get("number")
    if not isinstance(source_pr, int) or isinstance(source_pr, bool) or source_pr < 1:
        return decision("invalid_pr_number", status="blocked")
    key = hashlib.sha256(f"{book}:{stage}:{merge_sha}".encode()).hexdigest()[:20]
    return decision(
        "merged_gate_accepted", status="ready", book=book, gate=stage,
        next_stage=next_stage, source_pr=source_pr,
        merge_sha=merge_sha, idempotency_key=key,
        task_marker=f"<!-- book-pipeline-task:{key} -->",
        source_paths=sorted(set(relative)),
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event", required=True, type=Path)
    parser.add_argument("--files", required=True, type=Path)
    parser.add_argument("--books-prefix", default="books")
    parser.add_argument("--target-branch", default="main")
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args(argv)
    try:
        event = json.loads(args.event.read_text(encoding="utf-8"))
        files = json.loads(args.files.read_text(encoding="utf-8"))
        pr = event.get("pull_request", event)
        result = classify(pr, files, books_prefix=args.books_prefix,
                          target_branch=args.target_branch)
        print(json.dumps(result, indent=2, sort_keys=True))
        if args.github_output:
            fields = {
                "status": result["status"],
                "book": result.get("book", ""),
                "next_stage": result.get("next_stage", ""),
                "idempotency_key": result.get("idempotency_key", ""),
                "merge_sha": result.get("merge_sha", ""),
                "source_pr": str(result.get("source_pr", "")),
            }
            with args.github_output.open("a", encoding="utf-8") as out:
                for name, value in fields.items():
                    out.write(f"{name}={value}\n")
        return 0 if result["status"] in {"ready", "hold", "skip"} else 2
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f"router failed closed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
