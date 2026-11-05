---
name: book-authoring
description: Guide the creation, import, research, drafting, editing, review, and publication readiness of fiction and non-fiction books with the existing ai-book-pipeline engine. Use for new or existing book projects, chapter reviews, author-voice preservation, and publishing checks.
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

Use Python 3.10+; the adapter uses only the standard library and **delegates** to the existing engine. Options `--repo` and `--books-root` precede the command.

```bash
python skills/book-authoring/scripts/book.py --books-root /path/to/books status my-book
python skills/book-authoring/scripts/book.py --books-root /path/to/books phase my-book draft
python skills/book-authoring/scripts/book.py --books-root /path/to/books validate-phase my-book 2
python skills/book-authoring/scripts/book.py --books-root /path/to/books final-check my-book
# Creates a NEW book only after explicit author approval:
python skills/book-authoring/scripts/book.py --books-root /path/to/books init new-book --type non-fiction --confirm-write
```

For an externally installed skill, replace the script path with its installed path and set `BOOK_PIPELINE_REPO=/path/to/ai-book-pipeline`. See `README.md` for setup.

## Workflow

- **0 Import (optional):** inventory source materials, preserve originals, clarify duplicates, build `PROJECT.md` and outline.
- **1 Init:** establish fiction/non-fiction configuration, audience, author voice, outline, review criteria; obtain author approval.
- **2 Draft:** researcher verifies sources for non-fiction; writer drafts numbered chapters without overwriting earlier revisions.
- **3 Edit:** developmental, line and copy edit; use the documented naming and handoff conventions.
- **4 Review:** critic, author approval, proofreader. The canonical text is `files/content/chapters/chapter-N-final.md`.
- **5 Publish:** check all canonical finals and review gates before any assembly/export. Publication remains an explicitly authorized action.

After each step, summarize what was done, unresolved questions, evidence, proposed next stage, and update `config/progress.md` **only if writing was authorized**.

## Safety and quality gates

- Default to reading and recommending changes. Never silently overwrite drafts, edit original imports, mutate templates, publish, commit, or sync external services.
- `status`, `phase`, `validate-phase` and `final-check` are inspection operations. `init` requires `--confirm-write` and refuses an existing book directory.
- `final-check` is read-only and calls the engine's existing chapter-number collectors. It reports **filename completeness**, not content quality or author approval. The underlying `validate_final_chapters.py` also writes a handoff on failure, so do not call its CLI in inspection-only workflows.
- Phase validators can return exit 2 for warnings. Do not interpret warnings as success or declare a book publishable from one validator alone.
- Preserve `author-voice.md` even during proofreading. For factual non-fiction, retain sources and unresolved verification items.
- Before any cloud model request, obtain authorization for sensitive material and apply the host's data/PII controls. This skill does not implement PII filtering.
- Final publication requires an explicit author decision. See `references/workflow-map.md` for required handoffs.

## Scope

The skill provides instructions and a safe entrypoint. It does not autonomously spawn LLM agents, browse sources, convert to PDF/EPUB, install orchestration infrastructure, or guarantee a finished book without the host agent and its enabled tools.
