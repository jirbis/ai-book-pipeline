# Sample Non-Fiction Book

Example structure of a non-fiction book with demonstration configuration.

## Purpose

This example demonstrates:
- Directory structure for a non-fiction book
- Configuration files (PROJECT.md, outline.md, research.md, bibliography.md)
- Working directories (files/)

Sample chapters can be generated based on `config/author-voice.md` when it is filled out.

## Usage

```bash
# Command to generate sample chapters based on config/author-voice.md
claude "Generate 3 sample chapters for non-fiction book based on config/author-voice.md"
```

## What it Demonstrates

- **Voice consistency** — all chapters written in a unified author style
- **Non-fiction structure** — outline, research, chapters, bibliography
- **Application of author-voice.md** — practical example of voice usage

## Structure

```
sample-non-fiction-book/
├── README.md                    # This file
│
├── config/                      # Configuration for this book
│   ├── PROJECT.md               # Project metadata
│   ├── outline.md               # Book outline (non-fiction)
│   ├── research.md              # Research template (non-fiction)
│   ├── bibliography.md          # Bibliography (non-fiction)
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
    ├── research/                # Research, fact-checking
    │   └── chapter-1-research.md
    ├── edits/                   # Editing reports
    ├── reviews/                 # Reviews
    ├── handoff/                 # Agent handoff
    ├── proofread/               # Proofreading
    └── output/                  # Ready files (DOCX, PDF, EPUB)
```

## Using as a Base for a New Book

```bash
# 1. Copy structure
cp -r my-books/sample-non-fiction-book my-books/my-new-book

# 2. Update config/PROJECT.md with your data
# Edit my-books/my-new-book/config/PROJECT.md

# 3. Fill configuration files
# - config/outline.md - your detailed outline
# - config/research.md - sources and research
# - config/style-guide.md - your style
# - config/bibliography.md - sources for bibliography

# 4. Launch workflow
claude "Initialize book project in my-books/my-new-book/"
```

## Generating Sample Chapters

Sample chapters are generated when:
- `config/author-voice.md` is filled out (≠ template)
- There are 2-3 samples of reference text
- User requests generation

```bash
# Generate sample chapters
claude "Generate 3 sample chapters for sample-non-fiction-book based on config/author-voice.md"

# Update when author-voice.md changes
claude "Update sample chapters for sample-non-fiction-book — author-voice.md has changed"
```

## Purpose of Samples

1. **Demonstration for author** — show how the book will sound in their voice
2. **Testing** — verify that author's voice is correctly extracted
3. **Agent training** — examples for WRITER on how to write in this style
4. **Validation** — author can review and adjust author-voice.md

## More Details

See [../../engine/agents/WORKFLOW.md](../../engine/agents/WORKFLOW.md) for complete process description.
