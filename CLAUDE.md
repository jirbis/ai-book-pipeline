# CLAUDE.md — Instructions for Claude Code

This file contains contextual information for Claude Code when working with the book-pipeline project.

## About the Project

Book Pipeline is a framework for writing books with AI agents via Claude Code. The system consists of specialized agents, each performing their role in the book creation process.

## Project Structure

```
book-pipeline/
├── engine/                      # Framework engine
│   ├── book-templates/          # Templates for creating new books
│   │   ├── fiction/             # Templates for fiction literature
│   │   ├── non-fiction/         # Templates for non-fiction
│   │   ├── PROJECT.md           # Project file template
│   │   ├── author-voice.md      # Shared template
│   │   ├── progress.md          # Shared template
│   │   ├── review-checklist.md  # Shared template
│   │   └── style-guide.md       # Shared template
│   │
│   ├── agents/                  # Agent configurations
│   │   ├── AGENTS.md            # Description of agent roles
│   │   ├── WORKFLOW.md          # Workflow (6 phases)
│   │   └── *.md                 # Individual agent descriptions
│   │
│   └── STRUCTURE.md             # Detailed structure description
│
└── $BOOKS_ROOT/ (default: my-books/)  # User books
    ├── sample-fiction-book/     # Fiction example
    │   ├── config/              # Configuration for this book
    │   └── files/               # Working files for this book
    │
    └── sample-non-fiction-book/ # Non-fiction example
        ├── config/
        └── files/
```

### Expanded tree for context

```
$BOOKS_ROOT/<book-name>/  # defaults to my-books/<book-name>/
  config/                        # PROJECT.md, author-voice.md, style-guide.md, etc.
  files/
    import/                      # Optional imported source files
    content/                     # Chapters (drafts, edited, copyedited)
      chapters/
    research/                    # Research notes and fact checks
    edits/                       # Editing reports
    reviews/                     # Critic reviews
    proofread/                   # Proofreading reports
    handoff/                     # Agent handoff logs
    output/                      # Final exports (docx/pdf/epub/markdown)
```

## Important Principles

### 1. Book Isolation

Each book in `$BOOKS_ROOT/` (default: `my-books/`) has:
- **config/** - configuration for this book (PROJECT.md, style-guide.md, etc.)
- **files/** - working files for this book (content/, research/, edits/, etc.)

### 2. Templates vs Configuration

- **engine/book-templates/** contains TEMPLATES (do not change)
- **$BOOKS_ROOT/BOOK_NAME/config/** contains configuration for specific book (created from templates; default root `my-books/`)

### 3. File Paths

In agent documentation, mentions of `engine/files/` should be understood as `$BOOKS_ROOT/BOOK_NAME/files/` (default: `my-books/BOOK_NAME/files/`). See [engine/STRUCTURE.md](engine/STRUCTURE.md) for details.

## Workflow (6 Phases)

1. **Phase 0: Import (optional)** - import existing author materials
2. **Phase 1: Init** - project initialization, structure creation
3. **Phase 2: Draft** - writing chapter drafts
4. **Phase 3: Edit** - editing (developmental → line → copy)
5. **Phase 4: Review** - review, author corrections, proofreading
6. **Phase 5: Publish** - assembly and export to formats

See [engine/agents/WORKFLOW.md](engine/agents/WORKFLOW.md) for detailed description.

## Agents

- **ORCHESTRATOR** - main project coordinator
- **IMPORTER** - import existing materials (Phase 0)
- **RESEARCHER** - information gathering, fact-checking (for non-fiction)
- **WRITER** - writing chapter drafts
- **EDITOR** - editing (developmental, line, copy)
- **CRITIC** - critical quality assessment
- **PROOFREADER** - final proofreading before publication
- **PUBLISHER** - book assembly and export

See [engine/agents/AGENTS.md](engine/agents/AGENTS.md) for detailed role descriptions.

## Typical Commands

### Creating a New Book (set `BOOKS_ROOT` to override the default `my-books/`)

```bash
# 1. Create structure
mkdir -p $BOOKS_ROOT/my-new-book/{config,files/{import,content,research,edits,reviews,handoff,proofread,output}}

# 2. Copy templates (fiction or non-fiction)
cp engine/book-templates/PROJECT.md $BOOKS_ROOT/my-new-book/config/
cp engine/book-templates/author-voice.md $BOOKS_ROOT/my-new-book/config/
cp engine/book-templates/progress.md $BOOKS_ROOT/my-new-book/config/
cp engine/book-templates/review-checklist.md $BOOKS_ROOT/my-new-book/config/
cp engine/book-templates/style-guide.md $BOOKS_ROOT/my-new-book/config/
cp engine/book-templates/fiction/*.md $BOOKS_ROOT/my-new-book/config/  # for fiction
# or
cp engine/book-templates/non-fiction/*.md $BOOKS_ROOT/my-new-book/config/  # for non-fiction

# 3. Fill in PROJECT.md
```

### Running Workflow

```bash
# Initialize project
claude "Initialize book project in $BOOKS_ROOT/BOOK_NAME/ according to WORKFLOW.md"  # defaults to my-books/BOOK_NAME/

# Continue work
claude "Continue work on book in $BOOKS_ROOT/BOOK_NAME/"

# Check status
claude "Show project status for book in $BOOKS_ROOT/BOOK_NAME/"
```

### Import Existing Materials

```bash
# 1. Place files in $BOOKS_ROOT/BOOK_NAME/files/import/  # defaults to my-books/...
# 2. Run import
claude "Run import of materials from $BOOKS_ROOT/BOOK_NAME/files/import/"
```

### Fast demos (ready-to-open files)

```bash
# Fiction demo (resets sample files)
bash engine/demo.sh fiction --reset

# Non-fiction demo
bash engine/demo.sh non-fiction --reset

# Populate both samples
bash engine/demo.sh all --reset

# Send demo output to a specific book directory (defaults to my-books/)
bash engine/demo.sh non-fiction --reset --book $BOOKS_ROOT/my-first-book
```

### Command-line helper (Python CLI)

```bash
# Create structure and copy templates
python -m engine.cli init my-new-book --type fiction  # or non-fiction

# Check required files and directories
python -m engine.cli status my-new-book

# Show workflow guidance for a specific phase (0-5 or alias)
python -m engine.cli phase my-new-book 2     # Writing Drafts
python -m engine.cli phase my-new-book edit  # Editing

# View sample-book generation steps tied to author voice
python -m engine.cli samples my-new-book
```

## Agent Flow (concise)

1. **Orchestrator** → plans and coordinates.
2. **Researcher** → gathers facts (especially for non-fiction).
3. **Writer** → drafts chapters.
4. **Editor** → developmental → line → copy edits.
5. **Critic** → quality and consistency review.
6. **Author review** → human approval/changes.
7. **Proofreader** → typography, grammar, consistency, voice protection.
8. **Publisher** → assembly and export (docx/pdf/epub/markdown).

## Key Files to Read

When working with book-pipeline, first read:

1. **engine/STRUCTURE.md** - understanding project structure
2. **engine/agents/WORKFLOW.md** - understanding workflow
3. **engine/agents/AGENTS.md** - understanding agent roles
4. **$BOOKS_ROOT/BOOK_NAME/config/PROJECT.md** (default: `my-books/BOOK_NAME/config/PROJECT.md`) - metadata for specific book

## Author Voice

Critically important file: **config/author-voice.md**

- Contains analysis of author's unique writing style
- All agents follow this voice when generating content
- PROOFREADER protects authorial features from "correction"

After importing materials or writing first chapters, author-voice.md is automatically filled with characteristic features of the author's style.

## Sample Books

In `$BOOKS_ROOT/sample-fiction-book/` and `$BOOKS_ROOT/sample-non-fiction-book/` (default root: `my-books/`) are examples of structure with demonstration configuration. Use them as a basis for creating new books.

## Documentation

- 📘 [engine/agents/INTEGRATION.md](engine/agents/INTEGRATION.md) - integration with Claude Code
- 🔄 [engine/agents/WORKFLOW.md](engine/agents/WORKFLOW.md) - workflow
- 🤖 [engine/agents/AGENTS.md](engine/agents/AGENTS.md) - agent descriptions
- 🏗️ [engine/STRUCTURE.md](engine/STRUCTURE.md) - project structure
- 📖 [README.md](README.md) - project overview

## Important Reminders

1. **Do not edit engine/book-templates/** - these are templates, not configuration
2. **Each book is isolated** - files in `$BOOKS_ROOT/BOOK_NAME/` (default: `my-books/BOOK_NAME/`)
3. **Follow WORKFLOW** - do not skip phases
4. **Preserve author voice** - use author-voice.md
5. **Version through Git** - commit changes regularly

## When Problems Arise

1. Check book directory structure (config/ and files/ exist?)
2. Check PROJECT.md is filled correctly
3. Check book type (fiction/non-fiction) matches configuration
4. Read engine/STRUCTURE.md to understand new structure
5. Refer to WORKFLOW.md to understand current phase

## Helpful reminders from prior README content

- **Import existing materials (Phase 0):** Place source files under `files/import/` and trigger the IMPORTER to classify, map, and extract author voice automatically.
- **Author voice protection:** `config/author-voice.md` is the reference for style; PROOFREADER must preserve it and flag uncertain changes.
- **Final author review:** Before publication, ensure author review, edits applied, proofreader passes complete, and only then publish.
- **Working principles:** Keep work incremental, follow the style guide, version with Git, and route every chapter through edit and review steps.

---

**For Claude Code**: This project uses an agent system for automated book writing. When working with it, always consider the current workflow phase and the role of the agent that should perform the task.
