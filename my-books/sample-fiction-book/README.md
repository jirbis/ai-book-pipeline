# Sample Fiction Book

Example structure of a fiction book with demonstration configuration.

## Purpose

This example demonstrates:
- Directory structure for a fiction book
- Configuration files (PROJECT.md, characters.md, plot.md, world.md)
- Working directories (files/)

Sample chapters can be generated based on `config/author-voice.md` when it is filled out.

## Usage

```bash
# Command to generate sample chapters based on config/author-voice.md
claude "Generate 3 sample chapters for fiction book based on config/author-voice.md"
```

## What it Demonstrates

- **Voice consistency** — all chapters written in a unified author style
- **Fiction structure** — characters, world, plot, chapters
- **Application of author-voice.md** — practical example of voice usage

## Structure

```
sample-fiction-book/
├── README.md                    # This file
│
├── config/                      # Configuration for this book
│   ├── PROJECT.md               # Project metadata
│   ├── characters.md            # Characters (fiction)
│   ├── plot.md                  # Plot (fiction)
│   ├── world.md                 # World (fiction)
│   ├── scenes.md                # Scenes (fiction)
│   ├── chapter.md               # Chapter template
│   ├── style-guide.md           # Style for this book
│   ├── progress.md              # Progress tracking
│   ├── review-checklist.md      # Review checklist
│   └── author-voice.md          # Author's voice
│
└── files/                       # Working files (created during work)
    ├── import/                  # Imported materials
    ├── content/                 # Drafts and final chapters
    │   └── chapters/
    │       ├── chapter-1-sample.md  # (generated on request)
    │       ├── chapter-2-sample.md
    │       └── chapter-3-sample.md
    ├── research/                # Research
    ├── edits/                   # Editing reports
    ├── reviews/                 # Reviews
    ├── handoff/                 # Agent handoff
    ├── proofread/               # Proofreading
    └── output/                  # Ready files (DOCX, PDF, EPUB)
```

## Using as a Base for a New Book

```bash
# 1. Copy structure
cp -r my-books/sample-fiction-book my-books/my-new-fiction-book

# 2. Update config/PROJECT.md with your data
# Edit my-books/my-new-fiction-book/config/PROJECT.md

# 3. Fill configuration files
# - config/characters.md - your characters
# - config/plot.md - your plot
# - config/world.md - your world
# - config/style-guide.md - your style

# 4. Launch workflow
claude "Initialize book project in my-books/my-new-fiction-book/"
```

## Generating Sample Chapters

Sample chapters are generated when:
- `config/author-voice.md` is filled out (≠ template)
- There are 2-3 samples of reference text
- User requests generation

```bash
# Generate sample chapters
claude "Generate 3 sample chapters for sample-fiction-book based on config/author-voice.md"

# Update when author-voice.md changes
claude "Update sample chapters for sample-fiction-book — author-voice.md has changed"
```

## More Details

See [../../engine/agents/WORKFLOW.md](../../engine/agents/WORKFLOW.md) for complete process description.
