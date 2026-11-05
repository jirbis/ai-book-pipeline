#!/usr/bin/env python3
"""Relocatable, dependency-free adapter for the existing ai-book-pipeline engine.

Read-only operations leave author books untouched. Creation requires an explicit
flag and refuses to initialize over an existing book directory.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path


BOOK_SLUG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")
PHASES = tuple(str(i) for i in range(6))


def locate_repo(explicit: str | None = None) -> Path:
    """Support both in-repo installation and standalone skill-folder copies."""
    configured = explicit or os.environ.get("BOOK_PIPELINE_REPO")
    candidates = [Path(configured).expanduser()] if configured else list(Path(__file__).resolve().parents)
    for candidate in candidates:
        repo = candidate.resolve()
        if (repo / "engine" / "cli.py").is_file() and (
            repo / "engine" / "agents" / "WORKFLOW.md"
        ).is_file():
            return repo
    raise ValueError(
        "Cannot find ai-book-pipeline engine; pass --repo or set BOOK_PIPELINE_REPO."
    )


def locate_books_root(repo: Path, explicit: str | None = None) -> Path:
    configured = explicit or os.environ.get("BOOKS_ROOT") or "my-books"
    root = Path(configured).expanduser()
    if not root.is_absolute():
        root = repo / root  # Match engine.cli's relative-root convention.
    return root.resolve()


def book_directory(books_root: Path, slug: str) -> Path:
    if not BOOK_SLUG.fullmatch(slug) or slug in {".", ".."}:
        raise ValueError("Book must be a single directory slug (not a path).")
    target = (books_root / slug).resolve()
    if not target.is_relative_to(books_root):
        raise ValueError("Book resolves outside the books root (symlinks are not allowed).")
    return target


def call_engine_cli(repo: Path, books_root: Path, command: str, *args: str) -> int:
    argv = [
        sys.executable, "-m", "engine.cli", command, *args,
        "--books-root", str(books_root),
    ]
    return subprocess.run(argv, cwd=repo, check=False).returncode


def validate_phase(repo: Path, book: Path, phase: str) -> int:
    if importlib.util.find_spec("yaml") is None:
        print("Phase validators require PyYAML: python -m pip install PyYAML", file=sys.stderr)
        return 2
    script = repo / "engine" / "agents" / "tools" / f"validate_phase_{phase}.py"
    if not script.is_file():
        raise ValueError(f"Missing engine validator for phase {phase}")
    return subprocess.run([sys.executable, str(script), str(book)], cwd=repo, check=False).returncode


def final_check(repo: Path, book: Path) -> int:
    """Run existing filename collection logic without its write-on-failure CLI."""
    module_file = repo / "engine" / "agents" / "tools" / "validate_final_chapters.py"
    spec = importlib.util.spec_from_file_location("book_authoring_final_validation", module_file)
    if spec is None or spec.loader is None:
        raise ValueError(f"Cannot load final chapter validator: {module_file}")
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)

    chapters = book / "files" / "content" / "chapters"
    if not chapters.is_dir():
        found, finals, missing, status = [], [], [], "error_missing_chapters_dir"
    else:
        found = sorted(validator.collect_chapter_numbers(chapters))
        finals = sorted(validator.collect_final_numbers(chapters))
        missing = sorted(set(found) - set(finals))
        status = ("error_no_chapters_found" if not found
                  else "missing_finals" if missing else "ok")

    print(json.dumps({
        "book": book.name,
        "chapters_dir": str(chapters),
        "status": status,
        "chapter_numbers_found": found,
        "final_chapters_found": finals,
        "missing_finals": missing,
        "read_only": True,
        "scope": "filename_completeness_only",
    }, indent=2))
    return 0 if status == "ok" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Safe adapter for ai-book-pipeline.")
    parser.add_argument("--repo", help="ai-book-pipeline repository path.")
    parser.add_argument("--books-root", help="Book workspace root.")
    commands = parser.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="Initialize a new book only.")
    init.add_argument("book")
    init.add_argument("--type", required=True, choices=("fiction", "non-fiction", "nonfiction"))
    init.add_argument("--confirm-write", action="store_true", help="Allow creating new book files.")

    status = commands.add_parser("status", help="Read existing book status.")
    status.add_argument("book")

    phase = commands.add_parser("phase", help="Read existing workflow guidance.")
    phase.add_argument("book")
    phase.add_argument("phase")

    check = commands.add_parser("validate-phase", help="Run an existing phase validator.")
    check.add_argument("book")
    check.add_argument("phase", choices=PHASES)

    final = commands.add_parser("final-check", help="Read-only final chapter filename check.")
    final.add_argument("book")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        repo = locate_repo(args.repo)
        books_root = locate_books_root(repo, args.books_root)
        book = book_directory(books_root, args.book)

        if args.command == "init":
            if not args.confirm_write:
                parser.error("init needs --confirm-write; no files were created.")
            if book.exists() or book.is_symlink():
                parser.error(f"Refusing to initialize existing book directory: {book}")
            return call_engine_cli(repo, books_root, "init", args.book, "--type", args.type)

        if not book.is_dir():
            parser.error(f"Book directory does not exist: {book}")
        if args.command == "status":
            return call_engine_cli(repo, books_root, "status", args.book)
        if args.command == "phase":
            return call_engine_cli(repo, books_root, "phase", args.book, args.phase)
        if args.command == "validate-phase":
            return validate_phase(repo, book, args.phase)
        if args.command == "final-check":
            return final_check(repo, book)
        parser.error(f"Unsupported command: {args.command}")
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
