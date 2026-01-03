# Book Pipeline for Claude Code Agents

Pipeline for writing books with AI agents via Claude Code.

## New here?

See [docs/getting-started.md](docs/getting-started.md) for one-command demos (fiction and non-fiction) plus ready-made outputs for screenshots/GIFs.

## Project Structure

```
book-pipeline/
├── README.md                    # This file
│
├── engine/                      # Framework engine
│   ├── book-templates/          # Templates for creating new books
│   │   ├── fiction/             # Templates for fiction literature
│   │   │   ├── TEMPLATE.md      # Master structure template
│   │   │   ├── world.md         # World/setting template
│   │   │   ├── characters.md    # Characters template
│   │   │   ├── plot.md          # Plot template
│   │   │   ├── chapter.md       # Chapter template
│   │   │   └── scenes.md        # Scenes template
│   │   │
│   │   ├── non-fiction/         # Templates for non-fiction
│   │   │   ├── TEMPLATE.md      # Master structure template
│   │   │   ├── outline.md       # Book outline template
│   │   │   ├── chapter.md       # Chapter template
│   │   │   ├── research.md      # Research template
│   │   │   └── bibliography.md  # Bibliography template
│   │   │
│   │   ├── PROJECT.md           # Project file template
│   │   ├── author-voice.md      # Shared template
│   │   ├── progress.md          # Shared template
│   │   ├── review-checklist.md  # Shared template
│   │   └── style-guide.md       # Shared template
│   │
│   ├── agents/                  # Agent configurations
│   │   ├── AGENTS.md            # Description of agent roles
│   │   ├── WORKFLOW.md          # Workflow (6 phases)
│   │   ├── INTEGRATION.md       # Integration with Claude Code
│   │   ├── orchestrator.md      # Main coordinator
│   │   ├── importer.md          # Import existing materials
│   │   ├── writer.md            # Writer agent
│   │   ├── editor.md            # Editor agent
│   │   ├── researcher.md        # Researcher agent
│   │   ├── critic.md            # Critic agent
│   │   ├── proofreader.md       # Final proofreading
│   │   └── publisher.md         # Publishing
│   │
│   └── STRUCTURE.md             # Project structure description
│
└── my-books/                    # Your books
    ├── sample-fiction-book/     # Fiction example (generated)
    │   ├── config/              # Configuration for this book
    │   │   ├── PROJECT.md       # Project metadata
    │   │   ├── characters.md    # Characters (for fiction)
    │   │   ├── plot.md          # Plot (for fiction)
    │   │   ├── world.md         # World (for fiction)
    │   │   ├── style-guide.md   # Style for this book
    │   │   └── progress.md      # Progress for this book
    │   │
    │   ├── files/               # Working files for THIS book
    │   │   ├── import/          # Import materials
    │   │   ├── content/         # Chapter content
    │   │   ├── research/        # Research
    │   │   ├── edits/           # Editing reports
    │   │   ├── reviews/         # Reviews
    │   │   ├── proofread/       # Proofreading reports
    │   │   ├── handoff/         # Handoff between agents
    │   │   └── output/          # Final files (DOCX, PDF, EPUB)
    │   │
    │   └── README.md
    │
    └── sample-non-fiction-book/ # Non-fiction example (generated)
        ├── config/              # Configuration for this book
        ├── files/               # Working files for THIS book
        └── README.md
```

## Quick Start

### 1. Creating a New Project

For a fast walkthrough with pre-seeded files, run `bash engine/demo.sh fiction --reset` (or `non-fiction`) from the repo root. It will populate the matching sample project in `my-books/sample-*/files` with stub Phase 1 → Phase 2 outputs you can open immediately.

```bash
# Create directory structure for new book
mkdir -p my-books/my-new-book/{config,files/{import,content,research,edits,reviews,handoff,proofread,output}}

# Copy templates
# For fiction:
cp engine/book-templates/PROJECT.md my-books/my-new-book/config/
cp engine/book-templates/author-voice.md my-books/my-new-book/config/
cp engine/book-templates/progress.md my-books/my-new-book/config/
cp engine/book-templates/review-checklist.md my-books/my-new-book/config/
cp engine/book-templates/style-guide.md my-books/my-new-book/config/
cp engine/book-templates/fiction/*.md my-books/my-new-book/config/

# For non-fiction:
cp engine/book-templates/PROJECT.md my-books/my-new-book/config/
cp engine/book-templates/author-voice.md my-books/my-new-book/config/
cp engine/book-templates/progress.md my-books/my-new-book/config/
cp engine/book-templates/review-checklist.md my-books/my-new-book/config/
cp engine/book-templates/style-guide.md my-books/my-new-book/config/
cp engine/book-templates/non-fiction/*.md my-books/my-new-book/config/

# Fill in project metadata
# Edit my-books/my-new-book/config/PROJECT.md
```

### 2. Choose Book Type

- **Non-fiction**: Use templates from `engine/book-templates/non-fiction/`
- **Fiction**: Use templates from `engine/book-templates/fiction/`
- **Shared**: Common files from `engine/book-templates/` (style-guide, progress, etc.)

### 3. Running Agents

Agents work in the following order:
1. **Orchestrator** — plans and coordinates
2. **Researcher** — gathers information (for non-fiction)
3. **Writer** — writes content
4. **Editor** — edits and improves
5. **Critic** — final quality check

## Using with Claude Code

The framework works through the Claude Code agent system:

```
1. Create structure for new book in my-books/<book-name>/
2. Fill in config/PROJECT.md with your data
3. Read engine/agents/WORKFLOW.md to understand the process
4. Run: "Initialize book project according to WORKFLOW.md"
5. ORCHESTRATOR will create structure and launch agents
6. Agents work in phases: Research → Write → Edit → Review
7. Progress is tracked in my-books/<book-name>/config/progress.md
```

**Important**: Agents use Claude Code tools (Read, Write, Edit, Grep, WebSearch).

**Documentation**:
- 📘 `engine/agents/INTEGRATION.md` — **Start here!** Integration with Claude Code
- 🔄 `engine/agents/WORKFLOW.md` — Workflow (6 phases: Import → Init → Draft → Edit → Review → Publish)
- 🤖 `engine/agents/AGENTS.md` — Description of agents and their roles
- 🎨 `engine/book-templates/author-voice.md` — Template for describing author voice

## Command-Line Helper

You can drive common workflow steps without memorizing every path:

```bash
# Create structure and copy templates into my-books/my-new-book/config/
python -m engine.cli init my-new-book --type fiction

# Check required files and directories for a book
python -m engine.cli status my-new-book

# Show workflow guidance for a specific phase (0-5 or alias)
python -m engine.cli phase my-new-book 2     # Writing Drafts
python -m engine.cli phase my-new-book edit  # Editing

# View the sample-book generation steps tied to your author voice
python -m engine.cli samples my-new-book
```

## New Features

### 📥 Import Existing Materials (Phase 0)

If you already have drafts:

```bash
# 1. Create directory for book (if not already created)
mkdir -p my-books/my-book/files/import

# 2. Place files in my-books/my-book/files/import/
# 3. Run import
claude "Run import of materials from my-books/my-book/files/import/"

# IMPORTER will automatically:
# - Determine content type
# - Create config/PROJECT.md and other configuration files
# - Organize materials into files/content/, files/research/, etc.
# - Extract your author voice into config/author-voice.md
```

### 🎨 Author Voice

The framework preserves your unique writing style:

```bash
# After import or writing first chapters:
# - config/author-voice.md is automatically filled
# - All agents follow your voice
# - PROOFREADER protects your authorial features

# Generate examples in your style:
claude "Generate sample fiction book based on config/author-voice.md"
```

**Sample books** — these are 3 sample chapters written in your style for:
- Validating the extracted voice
- Demonstrating how the book will sound
- Training agents in your style

### ✅ Final Author Review

Before publication (Phase 4.5-4.8):
1. **Author reviews** the AI's work
2. **Edits are made** by agents
3. **PROOFREADER** final proofreading (6 passes)
4. **Publication** only after author approval

## Working Principles

1. **Incremental** — write in parts, save progress
2. **Consistency** — follow style-guide
3. **Versioning** — use Git for change history
4. **Review** — each chapter goes through editor and critic
