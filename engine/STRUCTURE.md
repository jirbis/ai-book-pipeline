# Book Pipeline Project Structure

## Important Structure Change (January 2026)

### Old structure (deprecated):
```
/engine/
├── files/         # REMOVED - files moved to each book
├── fiction/       # MOVED to /engine/book-templates/
└── non-fiction/   # MOVED to /engine/book-templates/
```

### New structure:
```
/engine/
├── book-templates/      # Templates for creating new books
│   ├── fiction/        # Templates for fiction literature
│   ├── non-fiction/    # Templates for non-fiction
│   ├── PROJECT.md      # Project file template
│   ├── author-voice.md # Shared template
│   ├── progress.md     # Shared template
│   ├── review-checklist.md # Shared template
│   └── style-guide.md  # Shared template
│
└── agents/             # AI agent descriptions
    ├── AGENTS.md
    ├── WORKFLOW.md
    └── *.md

$BOOKS_ROOT/ (default: /my-books/)
├── sample-fiction-book/
│   ├── config/              # Configuration for THIS book
│   │   ├── PROJECT.md       # Project metadata
│   │   ├── characters.md    # (for fiction)
│   │   ├── plot.md          # (for fiction)
│   │   ├── world.md         # (for fiction)
│   │   ├── style-guide.md   # Style for this book
│   │   ├── progress.md      # Progress for this book
│   │   └── ...
│   │
│   ├── files/               # Working files for THIS book
│   │   ├── import/          # Imported materials
│   │   ├── content/         # Drafts and final chapters
│   │   ├── research/        # Research
│   │   ├── edits/           # Editing reports
│   │   ├── reviews/         # Reviews
│   │   ├── handoff/         # Communication between agents
│   │   ├── proofread/       # Proofreading
│   │   └── output/          # Final book files
│   │
│   └── README.md
│
└── sample-non-fiction-book/
    ├── config/
    │   ├── PROJECT.md
    │   ├── outline.md       # (for non-fiction)
    │   ├── bibliography.md  # (for non-fiction)
    │   ├── research.md      # (for non-fiction)
    │   ├── style-guide.md
    │   ├── progress.md
    │   └── ...
    │
    ├── files/
    │   └── [same subdirectories as above]
    │
    └── README.md
```

## Key Principles of New Structure

### 1. Templates vs Book Configuration

**engine/book-templates/** contains TEMPLATES:
- Do not change for specific books
- Used as basis for creating config files
- Copied to config/ of each new book during initialization

**$BOOKS_ROOT/\<book-name\>/config/** (default: `my-books/<book-name>/config/`) contains BOOK CONFIGURATION:
- Unique for each book
- Created from templates or automatically during import
- Choice of fiction/non-fiction files determined by book type in PROJECT.md

### 2. Working Files Now in Each Book

**$BOOKS_ROOT/\<book-name\>/files/** (default: `my-books/<book-name>/files/`) contains ALL working files:
- `import/` - imported author materials
- `content/` - drafts and final chapters
- `research/` - research and fact-checking
- `edits/` - editing reports
- `reviews/` - reviews from critic
- `handoff/` - task handoff between agents
- `proofread/` - proofreading results
- `output/` - final files (DOCX, PDF, EPUB)

### 3. File Paths in Agent Commands

**Instead of old:**
```bash
Read engine/files/content/chapters/chapter-1.md
```

**Now use:**
```bash
Read $BOOKS_ROOT/<book-short-name>/files/content/chapters/chapter-1.md  # default root: my-books/
```

**Where `<book-short-name>`:**
- Defined from book's PROJECT.md
- Or passed as parameter when launching agent
- Or taken from current work context

### 4. Creating a New Book

```bash
# Step 1: Create directory
mkdir -p $BOOKS_ROOT/my-new-book/{config,files/{import,content,research,edits,reviews,handoff,proofread,output}}  # defaults to my-books/

# Step 2: Copy templates
# For fiction:
cp engine/book-templates/PROJECT.md $BOOKS_ROOT/my-new-book/config/
cp engine/book-templates/author-voice.md $BOOKS_ROOT/my-new-book/config/
cp engine/book-templates/progress.md $BOOKS_ROOT/my-new-book/config/
cp engine/book-templates/review-checklist.md $BOOKS_ROOT/my-new-book/config/
cp engine/book-templates/style-guide.md $BOOKS_ROOT/my-new-book/config/
cp engine/book-templates/fiction/*.md $BOOKS_ROOT/my-new-book/config/

# For non-fiction:
cp engine/book-templates/PROJECT.md $BOOKS_ROOT/my-new-book/config/
cp engine/book-templates/author-voice.md $BOOKS_ROOT/my-new-book/config/
cp engine/book-templates/progress.md $BOOKS_ROOT/my-new-book/config/
cp engine/book-templates/review-checklist.md $BOOKS_ROOT/my-new-book/config/
cp engine/book-templates/style-guide.md $BOOKS_ROOT/my-new-book/config/
cp engine/book-templates/non-fiction/*.md $BOOKS_ROOT/my-new-book/config/

# Step 3: Fill in PROJECT.md
# Edit $BOOKS_ROOT/my-new-book/config/PROJECT.md  # default: my-books/...
```

### 5. Import Existing Materials

```bash
# Step 1: Place files
cp /path/to/drafts/* $BOOKS_ROOT/my-new-book/files/import/

# Step 2: Run IMPORTER agent
claude "Import materials from $BOOKS_ROOT/my-new-book/files/import/"  # defaults to my-books/

# Agent will automatically:
# - Create config/PROJECT.md (if doesn't exist)
# - Determine book type
# - Copy needed templates to config/
# - Organize files into files/content/, files/research/, etc.
```

## Migration for Existing Documents

All mentions of `engine/files/` in AGENTS.md, WORKFLOW.md and other agent files
should be understood as `$BOOKS_ROOT/<book-short-name>/files/` (default: `my-books/<book-short-name>/files/`).

Documentation will be updated to reflect the new structure.
