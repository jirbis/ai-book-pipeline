---
name: book-authoring
description: Guide creation, research, writing, editing, reviewing, and publication readiness of books with the ai-book-pipeline engine, including GitHub-hosted manuscripts, book branches, safe commits and PR collaboration. Use for fiction/non-fiction authoring, author-voice preservation, GitHub book workflows and publishing checks.
---

# Book authoring

Coordinate a book project with the existing `ai-book-pipeline` engine. This is a **skill and CLI adapter**, not an independent book generator. Keep the original engine documentation authoritative.

## Resolve context first

1. Locate the `ai-book-pipeline` checkout. When this skill is installed elsewhere, set `BOOK_PIPELINE_REPO` to its absolute path or pass `--repo` to the adapter.
2. Identify the book slug and an explicit `--books-root` (or `BOOKS_ROOT`). Never guess which existing book to modify.
3. Read `<repo>/engine/STRUCTURE.md`, `<repo>/engine/agents/WORKFLOW.md`, `<repo>/engine/agents/AGENTS.md`, and `<books-root>/<book>/config/PROJECT.md` when present.
4. Load only the relevant role document from `<repo>/engine/agents/{importer,researcher,writer,editor,critic,proofreader,publisher,orchestrator}.md`. Consult `references/workflow-map.md` for the short phase map.
5. Read `config/author-voice.md`, `config/style-guide.md`, `config/outline.md` and `config/progress.md` when relevant. Preserve the author's voice and existing draft versions.

## Commands

Use Python 3.10+; the adapter uses only the standard library and **delegates** to the existing engine. The engine's phase validators additionally need `PyYAML` (`python -m pip install PyYAML`). Options `--repo` and `--books-root` precede the command.

```bash
python skills/book-authoring/scripts/book.py --books-root /path/to/books status my-book
python skills/book-authoring/scripts/book.py --books-root /path/to/books phase my-book draft
python skills/book-authoring/scripts/book.py --books-root /path/to/books validate-phase my-book 2
python skills/book-authoring/scripts/book.py --books-root /path/to/books final-check my-book
# Creates a NEW book only after explicit author approval:
python skills/book-authoring/scripts/book.py --books-root /path/to/books init new-book --type non-fiction --confirm-write
```

For an externally installed skill, replace the script path with its installed path and set `BOOK_PIPELINE_REPO=/path/to/ai-book-pipeline`. See `README.md` for setup.

## GitHub manuscript workspace

Books may live under `books/<slug>/` in a **separate GitHub repository**, preferably private until the author chooses to release a manuscript. Set `BOOKS_ROOT` to that checkout's `books/` and keep `BOOK_PIPELINE_REPO` pointing to the engine. Load `references/github-workflow.md` when a user wants to **write books in GitHub**, not just locally.

Run the git helper from the local checkout when authorized:

```bash
python skills/book-authoring/scripts/github_workspace.py --checkout /path/to/manuscript-repo inspect my-book
python skills/book-authoring/scripts/github_workspace.py --checkout /path/to/manuscript-repo start my-book --confirm-write
# After the author approves writing and chapter files have changed:
python skills/book-authoring/scripts/github_workspace.py --checkout /path/to/manuscript-repo commit-book my-book --message 'Draft chapter one' --confirm-write
# Push ONLY with explicit permission:
python skills/book-authoring/scripts/github_workspace.py --checkout /path/to/manuscript-repo push-branch my-book --confirm-remote-write
```

When GitHub connector tools are present, use their authorized file operations directly on a **dedicated book branch**, read current SHA before updating any manuscript file, and open a Draft Pull Request. Do not write to the default branch or merge without approval. The local git helper does not itself create PRs or call the GitHub API.

## Workflow
- **0 Import (optional):** inventory source materials, preserve originals, clarify duplicates, build `PROJECT.md` and outline.
- **1 Init:** establish fiction/non-fiction configuration, audience, author voice, outline, review criteria; obtain author approval.
- **2 Draft:** researcher verifies sources for non-fiction; writer drafts numbered chapters without overwriting earlier revisions.
- **3 Edit:** developmental, line and copy edit; use the documented naming and handoff conventions.
- **4 Review:** critic, author approval, proofreader. The canonical text is `files/content/chapters/chapter-N-final.md`.
- **5 Publish:** check all canonical finals and review gates before any assembly/export. Publication remains an explicitly authorized action.

After each step, summarize what was done, unresolved questions, evidence, proposed next stage, and update `config/progress.md` **only if writing was authorized**.

## Safety and quality gates

- Default to reading and recommending changes. Never silently overwrite drafts, edit original imports, mutate templates, publish, commit, push, or sync external services.
- `status`, `phase`, `validate-phase` and `final-check` are inspection operations. `init` requires `--confirm-write` and refuses an existing book directory.
- `final-check` is read-only and calls the engine's existing chapter-number collectors. It reports **filename completeness**, not content quality or author approval. The underlying `validate_final_chapters.py` also writes a handoff on failure, so do not call its CLI in inspection-only workflows.
- Phase validators can return exit 2 for warnings. Do not interpret warnings as success or declare a book publishable from one validator alone.
- Preserve `author-voice.md` even during proofreading. For factual non-fiction, retain sources and unresolved verification items.
- Before any cloud model request, obtain authorization for sensitive material and apply the host's data/PII controls. This skill does not implement PII filtering.
- Final publication requires an explicit author decision. See `references/workflow-map.md` for required handoffs.

## Scope

The skill provides instructions, safe engine adapters and an opt-in GitHub workspace helper. It does not autonomously spawn LLM agents, browse sources, create GitHub PRs without host GitHub tools, convert to PDF/EPUB, upload to Amazon KDP, install orchestration infrastructure, or guarantee a finished book without the host agent and its enabled tools.
