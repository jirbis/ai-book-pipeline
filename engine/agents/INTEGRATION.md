# Claude Code Integration Guide

> **Structure update:** Work inside `my-books/<book-short-name>/` — configuration lives in `config/` (including `progress.md`), and all working documents live in `files/`. All examples below follow this per-book path pattern.

How to use Book Writer Framework with Claude Code.

---

## Overview

This framework works through **Claude Code agent system**. Agents are specialized AI assistants that perform specific tasks and pass results to each other.

---

## Claude Code Tools

Agents use the following tools:

### File Operations

| Tool | Purpose | Example |
|------|---------|---------|
| **Read** | Read files | `Read my-books/<book-short-name>/config/PROJECT.md` |
| **Write** | Create new files | `Write my-books/<book-short-name>/files/content/chapter-1.md` |
| **Edit** | Edit existing files | `Edit my-books/<book-short-name>/config/progress.md` |
| **Glob** | Find files by pattern | `Glob my-books/<book-short-name>/files/content/**/*.md` |
| **Grep** | Search by content | `Grep "main thesis" my-books/<book-short-name>/files/content/` |

### Research

| Tool | Purpose | Example |
|------|---------|---------|
| **WebSearch** | Search information | `WebSearch "AI agents 2025"` |
| **WebFetch** | Get URL content | `WebFetch https://example.com` |

### Coordination

| Tool | Purpose | Example |
|------|---------|---------|
| **Task** | Launch agent | `Task subagent_type="writer" prompt="Write chapter 1"` |

---

## How Agents Work

### Launching Agent via Task tool

```markdown
Task subagent_type="orchestrator"
     prompt="Read my-books/<book-short-name>/config/PROJECT.md and initialize project"
     description="Project initialization"
```

### Available Agent Types

For this framework use standard Claude Code agent:

| Type | Description |
|------|-------------|
| `general-purpose` | Universal agent for all framework tasks |

**Important**: Agents ORCHESTRATOR, WRITER, EDITOR, RESEARCHER, CRITIC work through instructions in prompts, not as separate subagent_type.

---

## Workflow

### 1. Preparation

```markdown
1. Fill my-books/<book-short-name>/config/PROJECT.md with your data
2. Read WORKFLOW.md to understand the process
3. Determine book type (fiction/non-fiction)
```

### 2. Project Initialization

**User Request:**
```
Initialize book project according to PROJECT.md and WORKFLOW.md
```

**What happens:**
1. Claude reads my-books/<book-short-name>/config/PROJECT.md
2. Determines book type
3. Creates my-books/<book-short-name>/files/ directory structure
4. Initializes my-books/<book-short-name>/config/progress.md
5. Launches Phase 1 from WORKFLOW.md

**Template sources vs destinations:**
- Read-only templates live in engine/book-templates/** (fiction, non-fiction, and shared).
- All generated configs and working files must be written to my-books/<book-short-name>/config/ and my-books/<book-short-name>/files/.
- Never write back into engine/book-templates/ or legacy engine/files/ paths.

### 3. Phase 1: Planning

**Automatic actions:**
```markdown
Read my-books/<book-short-name>/config/PROJECT.md
Read engine/book-templates/non-fiction/TEMPLATE.md  # or engine/book-templates/fiction/TEMPLATE.md (template source only)
Read engine/book-templates/non-fiction/outline.md   # template source

# Create detailed plan
Write my-books/<book-short-name>/config/outline.md  # filled from template
Write my-books/<book-short-name>/config/progress.md      # update status
```

### 4. Phase 2: Writing

**For each chapter:**
```markdown
# If non-fiction:
Read my-books/<book-short-name>/config/outline.md
Read my-books/<book-short-name>/config/style-guide.md
WebSearch [chapter topic]  # gather information
Write my-books/<book-short-name>/files/research/chapter-N-research.md

# Write draft
Write my-books/<book-short-name>/files/content/chapters/chapter-N-draft-v1.md
```

### 5. Phase 3: Editing

**For each chapter:**
```markdown
# Developmental Edit
Read my-books/<book-short-name>/files/content/chapters/chapter-N-draft-v1.md
Edit my-books/<book-short-name>/files/content/chapters/chapter-N-draft-v2.md

# Line Edit
Edit my-books/<book-short-name>/files/content/chapters/chapter-N-draft-v3.md

# Copy Edit
Edit my-books/<book-short-name>/files/content/chapters/chapter-N-edited.md
```

### 6. Phase 4: Review

```markdown
Read my-books/<book-short-name>/files/content/chapters/chapter-N-edited.md
Read my-books/<book-short-name>/config/review-checklist.md
Write my-books/<book-short-name>/files/reviews/chapter-N-review.md

# If APPROVED → next chapter
# If NEEDS_REVISION → return to editing
```

### 7. Phase 5: Publication

```markdown
# Validate final coverage (run before export)
Run: engine/agents/tools/validate_final_chapters.py my-books/<book-short-name>

# Gather all finals
Glob my-books/<book-short-name>/files/content/chapters/chapter-*-final.md

# Create front/back matter
Write my-books/<book-short-name>/files/content/front-matter/title.md
Write my-books/<book-short-name>/files/content/back-matter/bibliography.md

# Final assembly
Write my-books/<book-short-name>/files/output/book-complete.md
```

---

## Example Commands

### Start New Project

```
Hello! I want to write a book. Help me initialize the project
according to book-pipeline framework. First read my-books/<book-short-name>/config/PROJECT.md,
then engine/agents/WORKFLOW.md and start with Phase 1.
```

### Write Chapter

```
Write draft of chapter 3 according to plan in my-books/<book-short-name>/config/outline.md.
Follow instructions from WRITER agent in engine/agents/writer.md. Save
result to my-books/<book-short-name>/files/content/chapters/chapter-3-draft-v1.md.
```

### Edit Chapter

```
Edit chapter-3-draft-v1.md according to EDITOR agent instructions
from engine/agents/editor.md. Do developmental edit and create report.
```

### Check Status

```
Show current project status. Read my-books/<book-short-name>/config/progress.md and
list what's done, what's in progress, what remains.
```
Use the per-book progress file under `my-books/<book>/config/`.

---

## File Structure

### Templates (in repo)

```
engine/book-templates/PROJECT.md                 # Project template
engine/book-templates/style-guide.md      # Style template
engine/book-templates/progress.md         # Progress template
engine/book-templates/review-checklist.md # Review checklist template
engine/book-templates/non-fiction/outline.md     # Non-fiction outline template
engine/book-templates/fiction/outline.md         # Fiction outline template
```
Each book keeps its own `progress.md` inside `my-books/<book>/config/`; read or edit the file for the active book.

### Book-Specific Files

```
my-books/<book-short-name>/config/               # Configuration for one book
├── PROJECT.md                                   # Filled project file
├── outline.md                                   # Plan (non-fiction) or outline/plot (fiction)
├── style-guide.md                               # Book-specific style
├── review-checklist.md                          # Review checklist
└── progress.md                                  # Progress tracking

my-books/<book-short-name>/files/                # Working documents
├── content/
│   ├── chapters/
│   │   ├── chapter-1-draft-v1.md
│   │   ├── chapter-1-draft-v2.md
│   │   └── chapter-1-edited.md
│   ├── front-matter/
│   └── back-matter/
├── research/
│   ├── chapter-1-research.md
│   └── chapter-1-factcheck.md
├── edits/
│   ├── chapter-1-dev-edit.md
│   └── chapter-1-line-edit.md
├── reviews/
│   └── chapter-1-review.md
├── handoff/
│   ├── orchestrator-to-writer.md
│   └── writer-to-orchestrator.md
└── output/
    └── book-complete.md
```

---

## Error Handling

### Agent Cannot Find File

```markdown
# Check path
Read my-books/<book-short-name>/config/PROJECT.md  # correct path from root

# Create missing directories
Write my-books/<book-short-name>/files/content/chapters/.gitkeep
```

### Contradictory Instructions

```markdown
# Escalate to user
"Contradiction detected: my-books/<book-short-name>/config/PROJECT.md specifies genre 'thriller',
but outline.md has non-fiction structure. Which book type is correct?"
```

### Lost Context

```markdown
# Always start by reading state
Read my-books/<book-short-name>/config/progress.md
Read my-books/<book-short-name>/config/PROJECT.md

# Determine current phase
# Continue from where stopped
```

---

## Best Practices

### 1. Always read PROJECT.md at session start

```markdown
Read my-books/<book-short-name>/config/PROJECT.md
Read my-books/<book-short-name>/config/progress.md
```

### 2. Update the per-book progress.md (under `config/`) after each task

```markdown
Edit my-books/<book-short-name>/config/progress.md
# Update chapter status, word count, date
```

### 3. Use metadata in files

```markdown
<!-- METADATA
version: 2
status: draft
words: 3500
created: 2025-01-01
modified: 2025-01-02
-->
```

### 4. Document decisions

```markdown
Write my-books/<book-short-name>/files/handoff/orchestrator-notes.md
# Why chose this approach
# What alternatives considered
# What needs checking later
```

### 5. Give clear instructions

**Bad:**
```
Write chapter
```

**Good:**
```
Execute WRITER agent task:
1. Read my-books/<book-short-name>/config/outline.md (section "Chapter 3")
2. Read my-books/<book-short-name>/files/research/chapter-3-research.md
3. Read my-books/<book-short-name>/config/style-guide.md
4. Write draft 3000-5000 words
5. Write my-books/<book-short-name>/files/content/chapters/chapter-3-draft-v1.md
6. Add metadata and notes for editor
```

---

## Troubleshooting

### "File not found"

**Reason**: Wrong path or file not created

**Solution**:
```markdown
# Check existence
Glob my-books/<book-short-name>/files/content/**/*.md

# Create if missing
Write my-books/<book-short-name>/files/content/chapters/.gitkeep
```

### "Too many files"

**Reason**: Trying to read too many files

**Solution**:
```markdown
# Use Glob for list
Glob my-books/<book-short-name>/files/content/chapters/*.md

# Read one by one
Read my-books/<book-short-name>/files/content/chapters/chapter-1-edited.md
```

### "Context too long"

**Reason**: File too large or too much text

**Solution**:
```markdown
# Read in parts
Read my-books/<book-short-name>/files/content/chapters/chapter-1-edited.md offset=0 limit=500
Read my-books/<book-short-name>/files/content/chapters/chapter-1-edited.md offset=500 limit=500
```

---

## Useful Patterns

### Batch operations

```markdown
# Get file list
Glob my-books/<book-short-name>/files/content/chapters/chapter-*-edited.md

# Process each
For each file:
  Read [file]
  Process
  Write result
```

### Incremental work

```markdown
# Work one chapter at a time
Phase 2 → Chapter 1 → DONE
Phase 2 → Chapter 2 → DONE
...

# Don't try to do everything at once
```

### State management

```markdown
# Always know where we are
Read my-books/<book-short-name>/config/progress.md

# Update after each step
Edit my-books/<book-short-name>/config/progress.md

# Handoff between agents
Write my-books/<book-short-name>/files/handoff/[agent]-to-[agent].md
```

---

## FAQ

**Q: How do agents communicate with each other?**
A: Through handoff-files in `my-books/<book-short-name>/files/handoff/`. ORCHESTRATOR coordinates everyone.

**Q: Can multiple agents run in parallel?**
A: Technically yes, but better sequentially for quality control.

**Q: What to do if agent "loops"?**
A: Interrupt, read my-books/<book-short-name>/config/progress.md, continue from known state.

**Q: How to resume work after break?**
A: Read my-books/<book-short-name>/config/PROJECT.md and my-books/<book-short-name>/config/progress.md, continue from last completed task.

**Q: Do I need to manually create directories?**
A: No, agents will create on first file write.
