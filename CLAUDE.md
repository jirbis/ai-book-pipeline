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
└── my-books/                    # User books
    ├── sample-fiction-book/     # Fiction example
    │   ├── config/              # Configuration for this book
    │   └── files/               # Working files for this book
    │
    └── sample-non-fiction-book/ # Non-fiction example
        ├── config/
        └── files/
```

## Important Principles

### 1. Book Isolation

Each book in `my-books/` has:
- **config/** - configuration for this book (PROJECT.md, style-guide.md, etc.)
- **files/** - working files for this book (content/, research/, edits/, etc.)

### 2. Templates vs Configuration

- **engine/book-templates/** contains TEMPLATES (do not change)
- **my-books/BOOK_NAME/config/** contains configuration for specific book (created from templates)

### 3. File Paths

In agent documentation, mentions of `engine/files/` should be understood as `my-books/BOOK_NAME/files/`. See [engine/STRUCTURE.md](engine/STRUCTURE.md) for details.

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

### Creating a New Book

```bash
# 1. Create structure
mkdir -p my-books/my-new-book/{config,files/{import,content,research,edits,reviews,handoff,proofread,output}}

# 2. Copy templates (fiction or non-fiction)
cp engine/book-templates/PROJECT.md my-books/my-new-book/config/
cp engine/book-templates/author-voice.md my-books/my-new-book/config/
cp engine/book-templates/progress.md my-books/my-new-book/config/
cp engine/book-templates/review-checklist.md my-books/my-new-book/config/
cp engine/book-templates/style-guide.md my-books/my-new-book/config/
cp engine/book-templates/fiction/*.md my-books/my-new-book/config/  # for fiction
# or
cp engine/book-templates/non-fiction/*.md my-books/my-new-book/config/  # for non-fiction

# 3. Fill in PROJECT.md
```

### Running Workflow

```bash
# Initialize project
claude "Initialize book project in my-books/BOOK_NAME/ according to WORKFLOW.md"

# Continue work
claude "Continue work on book in my-books/BOOK_NAME/"

# Check status
claude "Show project status for book in my-books/BOOK_NAME/"
```

### Import Existing Materials

```bash
# 1. Place files in my-books/BOOK_NAME/files/import/
# 2. Run import
claude "Run import of materials from my-books/BOOK_NAME/files/import/"
```

## Key Files to Read

When working with book-pipeline, first read:

1. **engine/STRUCTURE.md** - understanding project structure
2. **engine/agents/WORKFLOW.md** - understanding workflow
3. **engine/agents/AGENTS.md** - understanding agent roles
4. **my-books/BOOK_NAME/config/PROJECT.md** - metadata for specific book

## Author Voice

Critically important file: **config/author-voice.md**

- Contains analysis of author's unique writing style
- All agents follow this voice when generating content
- PROOFREADER protects authorial features from "correction"

After importing materials or writing first chapters, author-voice.md is automatically filled with characteristic features of the author's style.

## Sample Books

In `my-books/sample-fiction-book/` and `my-books/sample-non-fiction-book/` are examples of structure with demonstration configuration. Use them as a basis for creating new books.

## Documentation

- 📘 [engine/agents/INTEGRATION.md](engine/agents/INTEGRATION.md) - integration with Claude Code
- 🔄 [engine/agents/WORKFLOW.md](engine/agents/WORKFLOW.md) - workflow
- 🤖 [engine/agents/AGENTS.md](engine/agents/AGENTS.md) - agent descriptions
- 🏗️ [engine/STRUCTURE.md](engine/STRUCTURE.md) - project structure
- 📖 [README.md](README.md) - project overview

## Important Reminders

1. **Do not edit engine/book-templates/** - these are templates, not configuration
2. **Each book is isolated** - files in my-books/BOOK_NAME/
3. **Follow WORKFLOW** - do not skip phases
4. **Preserve author voice** - use author-voice.md
5. **Version through Git** - commit changes regularly

## When Problems Arise

1. Check book directory structure (config/ and files/ exist?)
2. Check PROJECT.md is filled correctly
3. Check book type (fiction/non-fiction) matches configuration
4. Read engine/STRUCTURE.md to understand new structure
5. Refer to WORKFLOW.md to understand current phase

---

**For Claude Code**: This project uses an agent system for automated book writing. When working with it, always consider the current workflow phase and the role of the agent that should perform the task.
