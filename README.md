# Book Pipeline for Claude Code Agents

**AI-guided book creation, from idea to publication.**

**What this is:** A guided workflow where specialized AI agents help you research, draft, edit, and package a book using simple folder-based files.

**What this is not:** A single-click book generator or a replacement for your judgment as an author or editor.

## Example prompts to try early

Set `BOOKS_ROOT` to your workspace directory for books (defaults to `my-books/`).

- "Import my book materials for `$BOOKS_ROOT/my-great-book/` from `files/import` (default root: `my-books/`, so `my-books/my-great-book/`)."
- "Outline a three-chapter structure for `$BOOKS_ROOT/my-first-book` based on the notes in `config/PROJECT.md` (default: `my-books/my-first-book`)."
- "Draft chapter 1 for `$BOOKS_ROOT/sample-non-fiction-book` using the author voice in `config/author-voice.md` (default: `my-books/sample-non-fiction-book`)."
- "Review and proofread the draft in `$BOOKS_ROOT/sample-fiction-book/edits/chapter-2.md` before exporting (default: `my-books/sample-fiction-book/edits/chapter-2.md`)."

## Who this is for

- Authors of non-fiction, fiction, and expert guides
- Small publishers and editors coordinating manuscripts
- Teams experimenting with AI agent workflows for content production

## Quickstart (5–10 minutes)

1. Clone the repo: `git clone <repo-url> && cd book-pipeline`.
2. Copy the example book: `cp -r my-books/sample-non-fiction-book $BOOKS_ROOT/my-first-book` (if `BOOKS_ROOT` is unset, it defaults to `my-books/`; use the fiction sample if preferred).
3. Set the author voice: edit `$BOOKS_ROOT/my-first-book/config/author-voice.md` to reflect tone and examples you like.
4. Run the first agent step to drop in ready-to-open files: `bash engine/demo.sh non-fiction --reset --book $BOOKS_ROOT/my-first-book` (swap to `fiction` if you copied that sample; with defaults this targets `my-books/my-first-book`).

### Choose your starting mode

- **Import existing drafts and notes.** If you already have material, put it in `$BOOKS_ROOT/<book-short-name>/files/import/` (group by chapters, notes, research as needed; default root `my-books/`) and run an import prompt such as:  
  `claude "Import my book materials for $BOOKS_ROOT/my-great-book from files/import and create PROJECT.md."`  
  The importer will catalogue files, draft `PROJECT.md`, outline chapters, and prefill `config/author-voice.md` from your writing samples.

- **Start from scratch with clean configs.** If you prefer to begin fresh, create the folder `$BOOKS_ROOT/<book-short-name>/config/` (default root: `my-books/`) and write:  
  - `config/PROJECT.md` — your working title, scope, genre, audience, and goals.  
  - `config/author-voice.md` — tone, style rules, and reference snippets you want the agents to mimic.  
  - Any other helpful starters (e.g., `config/outline.md`, `config/style-guide.md`).  
  Then launch the orchestrator with a prompt like:  
  `claude "Initialize book project. Read PROJECT.md and launch ORCHESTRATOR for $BOOKS_ROOT/<book-short-name> (default root: my-books/)."`

## Pipeline roles (at a glance)

- **ORCHESTRATOR:** Coordinates the project and hands tasks to other agents.
- **RESEARCHER:** Finds facts, sources, and supporting material.
- **WRITER:** Drafts chapters that follow your outline and voice.
- **EDITOR:** Improves structure, clarity, and flow.
- **CRITIC:** Reviews for gaps, consistency, and quality issues.
- **PROOFREADER:** Catches typos and formatting issues before release.
- **PUBLISHER:** Assembles the final manuscript and exports files.

## Project structure

```
$BOOKS_ROOT/ (default: my-books/)
  example-book/
    config/
    research/
    drafts/
    edits/
    reviews/
    output/
```

## Concrete example: idea → research → first chapter → reviewed output

1. You jot down a book idea and brief outline in `config/PROJECT.md`.
2. The RESEARCHER gathers key facts and notes into `research/chapter-1-research.md`.
3. The WRITER produces a first chapter draft that matches your voice.
4. The EDITOR polishes it, the CRITIC reviews it, and you receive a clean, commented file ready for your approval.

## Learn more

- One-command demo with ready-made outputs: see `docs/getting-started.md`.
- Agent workflow details: `engine/agents/WORKFLOW.md` and `engine/agents/AGENTS.md`.
- Using an AI coding agent? Point it to `CLAUDE.md` for commands and structure guidance.

## License & attribution

MIT License

Developed and maintained by Jirbis GmbH

GitHub Pages: https://jirbis.github.io/book-pipeline
