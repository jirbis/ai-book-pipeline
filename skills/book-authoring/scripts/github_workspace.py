#!/usr/bin/env python3
"""Safe, explicit GitHub-backed book workspace operations.

This script uses a local Git clone. It never changes a remote repository
without --confirm-remote-write and never edits manuscript content itself.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import urlsplit

SLUG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")
BRANCH_SEGMENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")


def git(root: Path, *args: str, check: bool = True) -> str:
    command = ["git", "-C", str(root), *args]
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    if check and completed.returncode:
        raise ValueError(completed.stderr.strip() or f"Git command failed: {args[0]}")
    return completed.stdout.strip()


def checkout_root(path: str) -> Path:
    requested = Path(path).expanduser().resolve()
    if not requested.is_dir():
        raise ValueError("Checkout directory not found.")
    root = Path(git(requested, "rev-parse", "--show-toplevel")).resolve()
    if requested != root:
        raise ValueError("--checkout must be the Git working-tree root.")
    if git(root, "rev-parse", "--is-bare-repository") != "false":
        raise ValueError("A non-bare working tree is required.")
    return root


def book_path(root: Path, books_dir: str, slug: str) -> tuple[Path, str]:
    if not SLUG.fullmatch(slug) or slug in {".", ".."}:
        raise ValueError("Book must be a simple slug, not a filesystem path.")
    relative = Path(books_dir)
    if (relative.is_absolute() or not relative.parts or
            any(part in {".", "..", ".git"} for part in relative.parts)):
        raise ValueError("--books-dir must be a relative path without traversal.")
    folder = (root / relative / slug).resolve()
    if not folder.is_relative_to(root):
        raise ValueError("Book directory escapes the checkout.")
    if (root / relative / slug).is_symlink():
        raise ValueError("Book directory cannot be a symlink.")
    return folder, (relative / slug).as_posix()


def current_branch(root: Path) -> str:
    return git(root, "branch", "--show-current")


def branch_for_book(branch: str, slug: str) -> bool:
    parts = branch.split("/")
    return (len(parts) == 3 and parts[0] == "book" and
            parts[1] == slug and BRANCH_SEGMENT.fullmatch(parts[2]) is not None and
            parts[2] not in {".", ".."})


def dirty_paths(root: Path) -> list[str]:
    names = set()
    for args in (
        ("diff", "--name-only", "-z"),
        ("diff", "--cached", "--name-only", "-z"),
        ("ls-files", "--others", "--exclude-standard", "-z"),
    ):
        raw = git(root, *args)
        names.update(p for p in raw.split("\0") if p)
    return sorted(names)


def canonical_github_url(url: str) -> str:
    """Validate a Git remote URL and return a credential-free canonical URL."""
    if url.startswith("git@github.com:"):
        path = url.split(":", 1)[1]
    elif url.startswith("ssh://"):
        parsed = urlsplit(url)
        if parsed.hostname != "github.com":
            raise ValueError("Remote is not hosted on github.com.")
        path = parsed.path.lstrip("/")
    else:
        parsed = urlsplit(url)
        if parsed.scheme != "https" or parsed.hostname != "github.com":
            raise ValueError("Remote must be a github.com HTTPS or SSH URL.")
        path = parsed.path.lstrip("/")
    path = path.removesuffix(".git")
    if len(path.split("/")) != 2 or not all(SLUG.fullmatch(part) for part in path.split("/")):
        raise ValueError("Remote does not identify a GitHub owner/repository.")
    return "https://github.com/" + path


def github_remote(root: Path, *, for_push: bool = False) -> str:
    """Verify the actual push target, not only origin's fetch URL.

    Git supports remote.origin.pushurl, URL rewrite rules, and multiple push URLs.
    Git's get-url --push --all resolves these. Refuse ambiguous or redirected pushes.
    """
    fetch_url = canonical_github_url(git(root, "remote", "get-url", "origin"))
    if not for_push:
        return fetch_url
    push_urls = git(root, "remote", "get-url", "--push", "--all", "origin").splitlines()
    if len(push_urls) != 1:
        raise ValueError("origin must have exactly one push URL; refusing ambiguous push.")
    push_url = canonical_github_url(push_urls[0])
    if push_url != fetch_url:
        raise ValueError("origin push URL must match its validated GitHub fetch repository.")
    return push_url


def inspect(root: Path, path: Path, relative: str) -> int:
    try:
        remote = github_remote(root)
    except ValueError:
        remote = None
    modified = dirty_paths(root)
    own_paths = [name for name in modified if name.startswith(relative + "/")]
    print(json.dumps({
        "checkout": str(root),
        "book": relative,
        "book_exists": path.is_dir(),
        "branch": current_branch(root) or None,
        "github_repository": remote,
        "modified_paths": own_paths,
        "other_modified_paths_count": len(modified) - len(own_paths),
        "read_only": True,
    }, indent=2))
    return 0


def start_branch(root: Path, slug: str, name: str, base: str, confirm: bool) -> int:
    if not confirm:
        raise ValueError("Branch creation requires --confirm-write.")
    if not branch_for_book(name, slug):
        raise ValueError("Branch must have the form book/<book-slug>/<topic>.")
    if dirty_paths(root):
        raise ValueError("Refusing branch switch while checkout has uncommitted changes.")
    if not SLUG.fullmatch(base) or base in {".", ".."}:
        raise ValueError("Invalid local base branch name.")
    git(root, "show-ref", "--verify", "--quiet", "refs/heads/" + base)
    git(root, "switch", "-c", name, base)
    print(f"Created local branch {name} from {base}. Nothing was pushed.")
    return 0


def commit_book(root: Path, path: Path, relative: str, slug: str, message: str, confirm: bool) -> int:
    if not confirm:
        raise ValueError("Commit requires --confirm-write.")
    branch = current_branch(root)
    if not branch_for_book(branch, slug):
        raise ValueError("Commits must be on book/<book-slug>/<topic>, not main or another book.")
    if not path.is_dir():
        raise ValueError("Book directory does not exist; initialize it on this branch first.")
    if not message.strip():
        raise ValueError("Provide a non-empty commit message.")
    all_paths = dirty_paths(root)
    outside = [item for item in all_paths if not item.startswith(relative + "/")]
    if outside:
        raise ValueError("Uncommitted files outside this book: " + ", ".join(outside))
    if not all_paths:
        raise ValueError("No book changes to commit.")
    git(root, "add", "-A", "--", relative)
    staged = git(root, "diff", "--cached", "--name-only", "-z").split("\0")
    if any(item and not item.startswith(relative + "/") for item in staged):
        raise ValueError("Staged content extends outside this book; commit aborted.")
    # Untrusted repository hooks can execute arbitrary code: disable them for agent commits.
    # This also overrides a custom core.hooksPath set in the checkout.
    git(root, "-c", "core.hooksPath=/dev/null", "commit", "-m", message)
    print(f"Committed only {relative}/ on {branch}. Nothing was pushed.")
    return 0


def push_branch(root: Path, slug: str, confirm: bool) -> int:
    if not confirm:
        raise ValueError("Remote push requires --confirm-remote-write.")
    branch = current_branch(root)
    if not branch_for_book(branch, slug):
        raise ValueError("Push allowed only on this book's book/<slug>/<topic> branch.")
    remote = github_remote(root, for_push=True)
    if dirty_paths(root):
        raise ValueError("Commit or discard working-tree changes before pushing.")
    # Explicit refspec prevents push.default or remote.push from widening scope.
    # Disable mirror mode and follow-tags in case they were set in Git config.
    git(root, "-c", "remote.origin.mirror=false", "-c", "push.followTags=false",
        "push", "--no-follow-tags", "--set-upstream", "origin",
        f"refs/heads/{branch}:refs/heads/{branch}")
    print(f"Pushed {branch} to {remote}. Open a Pull Request for review; no merge was done.")
    return 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Opt-in GitHub-backed book workspace adapter.")
    p.add_argument("--checkout", default=".", help="Root of a local Git clone.")
    p.add_argument("--books-dir", default="books", help="Relative folder for books in the clone.")
    commands = p.add_subparsers(dest="action", required=True)

    show = commands.add_parser("inspect", help="Read GitHub/git workspace status.")
    show.add_argument("book")

    start = commands.add_parser("start", help="Create a local book-specific branch.")
    start.add_argument("book")
    start.add_argument("--branch", help="Default: book/<book>/draft.")
    start.add_argument("--from-branch", default="main", help="Existing local base branch.")
    start.add_argument("--confirm-write", action="store_true")

    commit = commands.add_parser("commit-book", help="Commit only this book's files.")
    commit.add_argument("book")
    commit.add_argument("--message", required=True)
    commit.add_argument("--confirm-write", action="store_true")

    push = commands.add_parser("push-branch", help="Explicitly push the current book branch to origin.")
    push.add_argument("book")
    push.add_argument("--confirm-remote-write", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    p = parser()
    args = p.parse_args(argv)
    try:
        root = checkout_root(args.checkout)
        path, relative = book_path(root, args.books_dir, args.book)
        if args.action == "inspect":
            return inspect(root, path, relative)
        if args.action == "start":
            return start_branch(root, args.book, args.branch or f"book/{args.book}/draft",
                                args.from_branch, args.confirm_write)
        if args.action == "commit-book":
            return commit_book(root, path, relative, args.book, args.message, args.confirm_write)
        if args.action == "push-branch":
            return push_branch(root, args.book, args.confirm_remote_write)
    except (OSError, ValueError) as error:
        p.error(str(error))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
