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

## Books and Amazon Kindle examples

See the [author's book showcase](docs/showcase.md), including *The Huna Guide*, *Surviving Crypto*, and *Stop Talking. Start Building*. Verified author-catalog references are provided there; direct Amazon Kindle product links will be added when ASINs are confirmed. The showcase does not claim that every title was made with this pipeline.

## Write manuscripts in GitHub

Store book folders in a GitHub repository (private for unpublished manuscripts), use dedicated `book/<slug>/<topic>` branches, and review chapter changes through Pull Requests. The portable [book-authoring skill](skills/book-authoring/SKILL.md) provides a [Git-backed workspace helper](skills/book-authoring/references/github-workflow.md) for local clones and a documented GitHub-connector workflow for agents. No automatic publishing or merging.

## Enable event-driven book automation (private repositories)

The optional GitHub workflow routes **human-merged, stage-labeled Pull Requests** to the next authoring task: materials → plan → manuscript → proofreading → **human approval before publication**. It creates an Issue by default; launching a cloud AI agent is a separate opt-in. **Do not enable automation until the following repository protections are configured.**

1. **Install the orchestration files in the private manuscript repository and merge them into its default branch.** Include `.github/workflows/book-pr-scope.yml`, `.github/workflows/book-transition-router.yml`, `.github/CODEOWNERS`, and `scripts/book_pipeline/`. Workflows in this engine repository do not monitor another repository's PRs.
2. **Require the `Book PR scope / scope` status check before merging.** In the manuscript repository, open **Settings → Rules → Rulesets** (or **Settings → Branches → Branch protection rules**), create or update protection for `main`, enable required status checks, and select `Book PR scope / scope`. The check validates changed paths for book-labeled PRs; it must be present in the default branch before GitHub can offer it as a required check.
3. **Require Code Owner reviews.** Configure `.github/CODEOWNERS` for `.github/workflows/`, `scripts/book_pipeline/` and the ownership file itself. Enable **Require review from Code Owners** (or an equivalent ruleset), require Pull Requests before merging, and restrict bypasses. **Adding CODEOWNERS alone does not turn on review enforcement.** Ensure an eligible independent reviewer can approve changes (the PR author cannot approve their own PR).
4. **Only after these protections are active**, set the Actions repository variable `BOOK_PIPELINE_ENABLED=true`. This queues next-stage Issues after eligible human merges, but does not run a language model.
5. **Before enabling automatic Copilot assignment**, create a GitHub Environment named `book-copilot-main` in the **private manuscript repository** (**Settings → Environments**). Under **Deployment branches and tags**, select **Selected branches and tags**, and allow the **`main` branch only** (no tags or wildcard branches). Add `COPILOT_USER_TOKEN` under **Environment secrets**, not Repository or Organization secrets; remove any repository/organization-scoped copy. Keep `BOOK_PIPELINE_ASSIGN_COPILOT` disabled until the environment restriction and token are verified. GitHub plan support for private-repository environments is required.
6. Only then set `BOOK_PIPELINE_ASSIGN_COPILOT=true`. The `assign_copilot` job runs from trusted `main` code and is the only job with access to the Environment secret. Test on one private sample book. Do not enable cloud inference for sensitive manuscripts without authorization.

**These branch protection/ruleset settings and token configuration are manual GitHub repository administration steps; merging this PR does not enable or enforce them.** Automatic merging, public publication, and Amazon KDP uploads are not implemented.

Scoped file deletions are allowed when the same PR also adds, modifies, or renames a required stage artifact. A deletion-only PR cannot advance a book phase; every changed path must remain inside the same book and the stage's permitted directories.

Read the [event-driven orchestration setup and security guide](docs/book-event-orchestration.md) for the complete deployment checklist.

## Documentation language

Repository documentation, setup instructions, and developer-facing Markdown are maintained in **English**. Book manuscripts and source material may use the author's chosen language.

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
