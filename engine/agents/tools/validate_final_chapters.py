#!/usr/bin/env python3
"""Validate that every chapter has a canonical final file before publication.

Outputs a machine-readable JSON summary and, when finals are missing, a Markdown
report plus a handoff file under `<books-root>/<book>/files/handoff/` for
ORCHESTRATOR.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


DEFAULT_BOOKS_DIRNAME = "my-books"
BOOKS_ROOT_ENV = "BOOKS_ROOT"
REPO_ROOT = Path(__file__).resolve().parents[2]


def collect_chapter_numbers(chapters_dir: Path) -> set[int]:
    """Collect chapter numbers from all chapter file variants."""
    pattern = re.compile(r"^chapter-(\d+)-")
    numbers: set[int] = set()

    for path in chapters_dir.glob("chapter-*-*.md"):
        match = pattern.match(path.name)
        if match:
            numbers.add(int(match.group(1)))

    return numbers


def collect_final_numbers(chapters_dir: Path) -> set[int]:
    """Collect chapter numbers that already have a final file."""
    pattern = re.compile(r"^chapter-(\d+)-final\.md$")
    numbers: set[int] = set()

    for path in chapters_dir.glob("chapter-*-final.md"):
        match = pattern.match(path.name)
        if match:
            numbers.add(int(match.group(1)))

    return numbers


def build_report(
    *,
    book_root: Path,
    chapters_dir: Path,
    chapter_numbers: Iterable[int],
    final_numbers: Iterable[int],
    missing_finals: Iterable[int],
    status: str,
    handoff_file: Path | None = None,
) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "book": book_root.name,
        "chapters_dir": str(chapters_dir),
        "generated_at": now,
        "status": status,
        "chapter_numbers_found": sorted(set(chapter_numbers)),
        "final_chapters_found": sorted(set(final_numbers)),
        "missing_finals": sorted(set(missing_finals)),
        "handoff_file": str(handoff_file) if handoff_file else None,
    }


def render_markdown_report(report: dict) -> str:
    lines = [
        f"# Final Chapter Validation — {report['book']}",
        "",
        f"- Status: {report['status']}",
        f"- Generated at: {report['generated_at']}",
        f"- Chapters directory: {report['chapters_dir']}",
        f"- Handoff file: {report['handoff_file'] or 'n/a'}",
        "",
        "## Summary",
        f"- Chapters discovered: {report['chapter_numbers_found']}",
        f"- Finals present: {report['final_chapters_found']}",
    ]

    missing = report.get("missing_finals") or []
    if missing:
        lines.append("\n## Missing finals")
        lines.append("| Chapter | Expected file |")
        lines.append("|---------|---------------|")
        for num in missing:
            lines.append(f"| {num} | chapter-{num}-final.md |")
    else:
        lines.append("\nAll chapter numbers have a chapter-N-final.md. Ready for publication.")

    return "\n".join(lines)


def write_handoff_file(book_root: Path, missing_finals: list[int], chapters_dir: Path) -> Path:
    handoff_dir = book_root / "files" / "handoff"
    handoff_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc)
    task_id = f"final-chapter-validation-{timestamp.strftime('%Y%m%dT%H%M%SZ')}"
    handoff_path = handoff_dir / "publisher-to-orchestrator-missing-final-chapters.md"

    missing_lines = "\n".join(
        f"- Chapter {num}: expected {chapters_dir / f'chapter-{num}-final.md'}" for num in missing_finals
    )

    handoff_contents = f"""# Handoff: PUBLISHER → ORCHESTRATOR

**Timestamp**: {timestamp.isoformat()}
**Task ID**: {task_id}

## Task
Missing final chapter files detected during publication validation.

## Input Materials
- Chapters directory: {chapters_dir}
- Validation tool: engine/agents/tools/validate_final_chapters.py

## Missing Finals
{missing_lines}

## Expected Result
- Add/restore chapter-N-final.md files for the missing chapter numbers.
- Re-run the validator before attempting export.

## Priority
HIGH
"""

    handoff_path.write_text(handoff_contents)
    return handoff_path


def resolve_books_root(explicit_root: str | None) -> Path:
    raw_root = explicit_root or os.getenv(BOOKS_ROOT_ENV) or DEFAULT_BOOKS_DIRNAME
    books_root = Path(raw_root).expanduser()
    if not books_root.is_absolute():
        books_root = REPO_ROOT / books_root
    return books_root


def resolve_book_root(book: str, books_root: Path) -> Path:
    candidate = Path(book)
    if candidate.is_absolute():
        return candidate
    return books_root / candidate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate that all chapters have a chapter-N-final.md. Defaults to BOOKS_ROOT or"
            f" '{DEFAULT_BOOKS_DIRNAME}' under the repo root."
        )
    )
    parser.add_argument(
        "book",
        help="Book short name (relative to the books root) or an absolute path to the book directory.",
    )
    parser.add_argument(
        "--books-root",
        help=(
            "Path to the books root. Uses $BOOKS_ROOT if set or defaults to"
            f" '{DEFAULT_BOOKS_DIRNAME}' relative to the repository."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    books_root = resolve_books_root(args.books_root)
    book_root = resolve_book_root(args.book, books_root)
    chapters_dir = book_root / "files" / "content" / "chapters"

    if not chapters_dir.is_dir():
        report = build_report(
            book_root=book_root,
            chapters_dir=chapters_dir,
            chapter_numbers=[],
            final_numbers=[],
            missing_finals=[],
            status="error_missing_chapters_dir",
        )
        print(json.dumps(report, indent=2))
        return 1

    chapter_numbers = collect_chapter_numbers(chapters_dir)
    final_numbers = collect_final_numbers(chapters_dir)

    if not chapter_numbers:
        report = build_report(
            book_root=book_root,
            chapters_dir=chapters_dir,
            chapter_numbers=[],
            final_numbers=final_numbers,
            missing_finals=[],
            status="error_no_chapters_found",
        )
        print(json.dumps(report, indent=2))
        return 1

    missing_finals = sorted(chapter_numbers - final_numbers)

    if missing_finals:
        handoff_path = write_handoff_file(book_root, missing_finals, chapters_dir)
        report = build_report(
            book_root=book_root,
            chapters_dir=chapters_dir,
            chapter_numbers=chapter_numbers,
            final_numbers=final_numbers,
            missing_finals=missing_finals,
            status="missing_finals",
            handoff_file=handoff_path,
        )
        print(json.dumps(report, indent=2))
        print("\nMarkdown report:\n")
        print(render_markdown_report(report))
        return 1

    report = build_report(
        book_root=book_root,
        chapters_dir=chapters_dir,
        chapter_numbers=chapter_numbers,
        final_numbers=final_numbers,
        missing_finals=[],
        status="ok",
    )
    print(json.dumps(report, indent=2))
    print("\nMarkdown report:\n")
    print(render_markdown_report(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
