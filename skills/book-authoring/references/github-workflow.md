# GitHub-backed book workspace

Books can be authored **inside GitHub repositories**, not only on a local disk. Choose a dedicated repository for manuscripts (private for unpublished works), or use a separate book branch in a suitable repository. The existing `engine/` does **not** need to be copied to that repository: set `BOOK_PIPELINE_REPO` to the engine checkout and set `BOOKS_ROOT` to the manuscript checkout's `books/` directory.

## Directory convention

```text
my-private-books/  # GitHub-backed working tree
  books/
    my-book/
      config/PROJECT.md
      config/author-voice.md
      config/progress.md
      files/content/chapters/chapter-1-draft-v1.md
      files/research/
      files/edits/
      files/reviews/
      files/handoff/
      files/output/
```

Never put confidential draft books into a public repository without an explicit release decision. Nothing in this skill publishes to Amazon KDP.

## Local Git mode (implemented)

Requires the `git` executable and an authenticated clone to push. The script makes no network requests for `inspect`, `start` or `commit-book`.

```bash
export BOOK_PIPELINE_REPO=/path/to/ai-book-pipeline
# A separate Git checkout, with an existing local main branch:
export BOOKS_ROOT=/path/to/my-private-books/books

# Read-only:
python skills/book-authoring/scripts/github_workspace.py --checkout /path/to/my-private-books inspect my-book

# Explicitly create a book-specific LOCAL branch from main:
python skills/book-authoring/scripts/github_workspace.py --checkout /path/to/my-private-books start my-book --confirm-write

# Only then initialize a book and write chapters, using the existing pipeline:
python skills/book-authoring/scripts/book.py --books-root "$BOOKS_ROOT" init my-book --type non-fiction --confirm-write

# Agent edits files inside books/my-book/ with author approval.
# Commit only this book's changes, never other books or the engine:
python skills/book-authoring/scripts/github_workspace.py --checkout /path/to/my-private-books commit-book my-book --message "Draft chapter one" --confirm-write

# Optional REMOTE operation (requires GitHub credentials and explicit approval):
python skills/book-authoring/scripts/github_workspace.py --checkout /path/to/my-private-books push-branch my-book --confirm-remote-write
```

The helper refuses to switch branches in a dirty checkout; commit from `main`, on an unrelated book branch, or when changed paths extend outside the selected book; and push without an approved GitHub `origin`. Before pushing, it verifies **the actual resolved push URL**, not just the fetch URL, refuses multiple push URLs and mismatched GitHub destinations, and uses a single explicit branch refspec. No automatic remote mutation or PR merge.

### Trust model for local Git clones

- `commit-book` intentionally disables Git commit hooks, including custom `core.hooksPath`, so an untrusted repository cannot execute hook scripts during an agent-created commit. Human developers can still run their usual hooks independently.
- **Do not run the helper against an untrusted checkout**: `git add` can still execute configured Git clean/smudge filters from attributes, and Git configuration can affect commands. Use a clean, authenticated clone you control, and review changes before committing.
- `inspect` lists modified paths only inside the selected book and reports the **count** of unrelated changed paths, not their names.
- Git's branch protection, credentials and permissions still apply; this is a safety wrapper, not a sandbox.


## GitHub connector mode (host-dependent)

An agent with authorized GitHub tools can work directly on GitHub, without a local clone:

1. Select the intended GitHub repository and specific book directory; identify private/public visibility.
2. Read current `config/PROJECT.md`, `author-voice.md`, `progress.md` and chapter files. Check for concurrent edits.
3. Create a dedicated `book/<slug>/<topic>` branch from the repository's current default branch, **only after explicit authorization**.
4. Create or update individual Markdown manuscript files **on that branch**, preserve revision history and never overwrite other authors' concurrent changes; use the current blob SHA for updates.
5. Review diffs and validate with the available engine. Do not silently edit `engine/` or other books.
6. Open a **Draft Pull Request** for author review. Do not merge or publish without explicit authorization.

The connector workflow is an instruction contract, not a claim that this Python script itself calls the GitHub API. Hosts without GitHub tools can use the local Git adapter above.

## Versioning and collaboration conventions

- All book work remains in `books/<slug>/`; one book change set per branch/PR.
- Keep research citations alongside drafts; preserve numbered version files and canonical `chapter-N-final.md` only after editorial checks.
- Do not push credentials, personal notes, or source material that cannot legally be redistributed.
- Treat a merged manuscript PR as source control, **not** as author approval to publish on Kindle or elsewhere.
- Require a separate author approval for any export, public release, or KDP upload.
