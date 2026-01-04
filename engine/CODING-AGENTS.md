# CODING-AGENTS.md — Instructions for AI Coding Agents

**Audience**: AI coding agents (Codex, GitHub Copilot, Cursor, Claude Code, etc.)
**Purpose**: Universal guidelines for working with the book-pipeline project
**Version**: 1.0
**Last updated**: 2026-01-04

---

## 🎯 Quick Start

### Before You Start

1. **Read this file first** — understand the workflow system
2. **Check book type** — fiction vs. non-fiction have different requirements
3. **Identify current phase** — each phase has specific rules
4. **Validate before proceeding** — use validation tools to check compliance

### Essential Commands

```bash
# Check workflow health
python -m engine.cli health <book-name>

# Validate current phase
python engine/agents/tools/validate_phase_2.py my-books/<book-name>/

# Generate work instructions
python -m engine.cli agent-instructions <book-name> --phase 2 --chapter 4

# Fix common blockers
python -m engine.cli fix-blockers <book-name> --phase 2
```

---

## 📚 Documentation Structure

This project has layered documentation for different purposes:

```
engine/
├── CODING-AGENTS.md          ← YOU ARE HERE (universal agent guide)
├── /CLAUDE.md                ← Claude Code specific instructions
│
├── agents/
│   ├── AGENTS.md             ← Agent roles and responsibilities
│   ├── WORKFLOW.md           ← 6-phase workflow (CRITICAL - READ THIS)
│   ├── INTEGRATION.md        ← Integration with Claude Code
│   ├── ORCHESTRATOR.md       ← Coordination agent
│   ├── RESEARCHER.md         ← Research agent (non-fiction)
│   ├── WRITER.md             ← Writing agent
│   ├── EDITOR.md             ← Editing agent
│   ├── CRITIC.md             ← Review agent
│   ├── PROOFREADER.md        ← Proofreading agent
│   └── PUBLISHER.md          ← Publishing agent
│
├── STRUCTURE.md              ← Project structure explanation
└── claude-improvements-suggestions.md  ← Improvement roadmap
```

**Reading priority**:
1. ✅ This file (CODING-AGENTS.md) — universal guidelines
2. ✅ `agents/WORKFLOW.md` — understand the 6-phase process
3. ✅ `agents/AGENTS.md` — understand agent roles
4. ✅ `/CLAUDE.md` (if using Claude Code) — Claude-specific context
5. ✅ `STRUCTURE.md` — understand directory structure

---

## 🏗️ System Overview

### The Book-Pipeline Framework

This is a **workflow-driven system** for writing books with AI agents. Each agent has:
- **Specific role** (research, write, edit, review, etc.)
- **Clear inputs** (what files to read)
- **Clear outputs** (what files to create)
- **Validation requirements** (how to verify completion)
- **Handoff protocol** (how to pass work to next agent)

### The 6-Phase Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│  Phase 0: IMPORT    → Phase 1: INIT     → Phase 2: DRAFT       │
│  (optional)           (setup)              (writing)            │
│                                                                 │
│  Phase 3: EDIT      → Phase 4: REVIEW   → Phase 5: PUBLISH     │
│  (polish)             (validate)           (export)             │
└─────────────────────────────────────────────────────────────────┘
```

**⚠️ CRITICAL**: Phases must be completed in order. You **cannot** skip phases.

**📖 Details**: See `engine/agents/WORKFLOW.md` for complete phase descriptions.

---

## 🎭 Agent Roles

You will act as different agents depending on the task:

| Agent | Role | Input | Output | Phase |
|-------|------|-------|--------|-------|
| **ORCHESTRATOR** | Coordinate workflow | All files | Assignments, status | All |
| **IMPORTER** | Import existing materials | files/import/ | Organized files | 0 |
| **RESEARCHER** | Gather facts (non-fiction) | outline.md | research/*.md | 2 |
| **WRITER** | Write chapter drafts | outline, research | chapters/*.md | 2 |
| **EDITOR** | Polish text | draft chapters | edited chapters | 3 |
| **CRITIC** | Quality review | edited chapters | review reports | 4 |
| **PROOFREADER** | Final check | final chapters | proofread reports | 4 |
| **PUBLISHER** | Export to formats | all content | .docx, .pdf, .epub | 5 |

**📖 Details**: See `engine/agents/AGENTS.md` for complete role descriptions.

---

## ⚠️ Critical Rules — DO NOT SKIP

### Rule 1: Always Validate Before Proceeding

**Before starting work**:
```bash
# Check current phase status
python -m engine.cli health my-books/<book-name>

# If issues found → fix them first
```

**After completing work**:
```bash
# Validate your output
python engine/agents/tools/validate_phase_<N>.py my-books/<book-name>/

# Exit code must be 0 before marking complete
```

---

### Rule 2: Follow Phase-Specific Requirements

#### For **Fiction** Books:
- Phase 1: Create plot.md, characters.md, world.md
- Phase 2: Write sequentially (chapter order matters)
- Phase 4: Check character consistency, plot coherence

#### For **Non-Fiction** Books:
- Phase 2.1: **RESEARCH BEFORE WRITING** (mandatory!)
- Phase 2.2: Write using research files
- Phase 4: Fact-check all claims

**⚠️ CRITICAL FOR NON-FICTION**:

```bash
# Non-fiction chapters require research FIRST
# DO NOT write without research!

# Correct order:
1. RESEARCHER creates research/chapter-N-research.md
2. RESEARCHER validates research (min 3 sources)
3. RESEARCHER creates handoff log
4. WRITER reads research file
5. WRITER writes chapter using research
```

**Wrong order** (will fail validation):
```bash
❌ WRITER writes chapter without research
❌ Research file is template/empty
❌ No handoff log from RESEARCHER to WRITER
```

---

### Rule 3: Create ALL Required Files

Each phase requires specific files. **Missing files = validation failure**.

**Example for Phase 2 (non-fiction chapter)**:
```
Required files for Chapter 4:
✅ config/outline.md (chapter 4 section exists)
✅ files/research/chapter-4-research.md (≥ 300 words, ≥ 3 sources)
✅ files/content/chapters/chapter-4-draft-v1.md
✅ files/handoff/researcher-to-writer-ch-4.md
✅ config/progress.md (updated with chapter 4 status)
```

**Missing any file → Phase validation FAILS → Cannot proceed**

---

### Rule 4: Update Tracking Files

After completing work, **always update**:

1. **config/progress.md**:
   ```markdown
   | 4 | Chapter Title | 3500 | 3421 | 98% | ✅ draft | 2026-01-04 |
   ```

2. **config/phase-status.yml** (if exists):
   ```yaml
   phase_2_checklist:
     chapters_drafted: 5/19
   ```

3. **Handoff log**:
   ```markdown
   # files/handoff/researcher-to-writer-ch-4.md
   Research completed: 2026-01-04
   Status: READY_FOR_DRAFTING
   ```

---

## 📋 Phase-Specific Checklists

### Phase 0: Import (optional)

**When**: Author has existing materials to import

**Checklist**:
- [ ] Read files from `files/import/`
- [ ] Classify content type (chapters, notes, research)
- [ ] Create `config/PROJECT.md` from imported content
- [ ] Create `config/outline.md`
- [ ] Move files to correct locations
- [ ] Create `files/import/import-report.md`
- [ ] Save originals in `files/import/original/`

**Validation**: All imported files classified and organized

---

### Phase 1: Initialization

**When**: Starting a new book from scratch

**Checklist**:
- [ ] Verify `config/PROJECT.md` is filled (title, type, audience, themes)
- [ ] Create directory structure (content/, research/, edits/, reviews/, etc.)
- [ ] Create `config/outline.md` with chapter breakdown
- [ ] For fiction: Create `config/plot.md`, `config/characters.md`, `config/world.md`
- [ ] For non-fiction: Create `config/bibliography.md`
- [ ] Initialize `config/progress.md`

**Validation**: All config files exist and are filled (not templates)

---

### Phase 2: Writing Drafts

**⚠️ CRITICAL**: Different requirements for fiction vs. non-fiction!

#### For Non-Fiction (MANDATORY):

**Checklist for EACH chapter**:

```bash
# STEP 1: RESEARCH (RESEARCHER agent)
[ ] Read config/outline.md chapter section
[ ] Generate research template:
    python -m engine.cli generate-research <book> --chapter N
[ ] Conduct research (minimum 3 authoritative sources)
[ ] Fill research file:
    - Sources table (≥ 3 sources with URLs)
    - Key findings (≥ 3 findings)
    - Examples/case studies (≥ 2 examples)
    - Bibliography
[ ] Validate research:
    python engine/agents/tools/validate_research.py \
           my-books/<book>/files/research/chapter-N-research.md
[ ] Create handoff log: files/handoff/researcher-to-writer-ch-N.md
[ ] Update progress.md: chapter-N status = "research_complete"

# STEP 2: WRITE (WRITER agent)
[ ] Read research file (confirm it exists and is filled)
[ ] Read outline.md chapter section
[ ] Read style-guide.md
[ ] Read previous chapter (for continuity)
[ ] Write draft: files/content/chapters/chapter-N-draft-v1.md
    - Hook opening (first 300 words)
    - Main content (based on research)
    - Transition to next chapter
[ ] Target: 80-120% of planned word count
[ ] Update progress.md: chapter-N status = "draft", words = [COUNT]
[ ] Create handoff log: files/handoff/writer-to-editor-ch-N.md
```

**Validation command**:
```bash
python engine/agents/tools/validate_chapter.py \
       my-books/<book>/ --chapter N --phase 2
```

#### For Fiction:

**Checklist for EACH chapter**:
```bash
# STEP 1: PLAN (WRITER agent)
[ ] Read config/plot.md (story arc)
[ ] Read config/characters.md (character details)
[ ] Read config/world.md (setting/worldbuilding)
[ ] Read outline.md chapter section
[ ] Read previous chapter (for continuity)

# STEP 2: WRITE
[ ] Write draft: files/content/chapters/chapter-N-draft-v1.md
[ ] Follow character voice and motivations
[ ] Maintain world consistency
[ ] Advance plot according to plan
[ ] Update progress.md: chapter-N status = "draft", words = [COUNT]
```

**Phase 2 Completion Criteria**:
- [ ] All chapters have draft-v1.md files
- [ ] All chapters have research files (non-fiction only)
- [ ] All handoff logs created
- [ ] progress.md shows accurate status
- [ ] Total word count within 90-110% of target

**Validation command**:
```bash
python engine/agents/tools/validate_phase_2.py my-books/<book>/
```

---

### Phase 3: Editing

**Checklist**:
- [ ] Phase 2 validation passed
- [ ] For each chapter, perform 3 editing passes:

**3.1 Developmental Edit** (EDITOR agent):
- [ ] Read draft chapter
- [ ] Check structure matches outline
- [ ] Verify logical flow and pacing
- [ ] Identify sections to rewrite/reorganize
- [ ] Create `files/edits/chapter-N-dev-edit.md`
- [ ] If major issues → return to WRITER
- [ ] If minor issues → proceed to line edit

**3.2 Line Edit** (EDITOR agent):
- [ ] Improve sentence clarity and rhythm
- [ ] Strengthen weak verbs
- [ ] Remove redundancy
- [ ] Improve transitions
- [ ] Create `files/content/chapters/chapter-N-draft-v2.md`
- [ ] Create `files/edits/chapter-N-line-edit.md`

**3.3 Copy Edit** (EDITOR agent):
- [ ] Fix grammar and punctuation
- [ ] Check spelling
- [ ] Verify term consistency
- [ ] Unify formatting
- [ ] Create `files/content/chapters/chapter-N-edited.md`

**Phase 3 Completion Criteria**:
- [ ] All chapters passed all 3 editing levels
- [ ] All edit reports created
- [ ] style-guide.md followed consistently

**Validation command**:
```bash
python engine/agents/tools/validate_phase_3.py my-books/<book>/
```

---

### Phase 4: Review and Finalization

**Checklist**:

**4.1 Individual Chapter Review** (CRITIC agent):
- [ ] For each chapter, check against `config/review-checklist.md`
- [ ] Non-fiction: thesis clear, arguments convincing, facts correct
- [ ] Fiction: characters convincing, scenes work, tension maintained
- [ ] Create `files/reviews/chapter-N-review.md`
- [ ] Verdict: APPROVED / NEEDS_REVISION / MAJOR_ISSUES

**4.2 Full Book Review** (CRITIC agent):
- [ ] Check consistency across all chapters
- [ ] Verify no contradictions
- [ ] Check beginning captivating, ending satisfying
- [ ] Create `files/reviews/book-review.md`

**4.3 Fact-Check** (RESEARCHER, non-fiction only):
- [ ] Verify all factual claims
- [ ] Check all statistics and dates
- [ ] Validate sources still accessible
- [ ] Create `files/research/final-factcheck.md`

**4.4 Author Review** (ORCHESTRATOR):
- [ ] Compile book into `files/handoff/for-author-review.md`
- [ ] Create `files/handoff/author-review-checklist.md`
- [ ] Wait for author approval
- [ ] Process author corrections

**4.5 Final Proofreading** (PROOFREADER agent):
- [ ] Pass 1: Spelling and grammar
- [ ] Pass 2: Typography (quotes, dashes, ellipses)
- [ ] Pass 3: Consistency (names, dates, terms)
- [ ] Pass 4: Final fact-check
- [ ] Pass 5: Pre-publication checklist (TOC, bibliography, metadata)
- [ ] Pass 6: Author voice protection (check author-voice.md)
- [ ] Create `files/proofread/proofreading-report.md`
- [ ] Create canonical files: `chapter-*-final.md`
- [ ] Status: READY_FOR_PUBLICATION

**Phase 4 Completion Criteria**:
- [ ] CRITIC approved entire book
- [ ] Fact-check completed (non-fiction)
- [ ] Author reviewed and approved
- [ ] Author corrections applied
- [ ] Proofreading completed (all 6 passes)
- [ ] All chapter-*-final.md files created

**Validation command**:
```bash
python engine/agents/tools/validate_phase_4.py my-books/<book>/
```

---

### Phase 5: Publication

**Checklist**:

**5.1 Validate Final Chapters** (PUBLISHER agent):
- [ ] Run: `python engine/agents/tools/validate_final_chapters.py my-books/<book>/`
- [ ] Confirm chapter-N-final.md exists for ALL chapters
- [ ] If any missing → STOP, escalate to ORCHESTRATOR

**5.2 Front Matter** (PUBLISHER agent):
- [ ] Create title page
- [ ] Create copyright page
- [ ] Create table of contents (auto-generated)
- [ ] Add dedication (if provided)
- [ ] Add preface/introduction

**5.3 Back Matter** (PUBLISHER agent):
- [ ] Create epilogue/conclusion
- [ ] Create appendices (if needed)
- [ ] Create glossary (gather terms)
- [ ] Create bibliography (from research/)
- [ ] Create acknowledgments
- [ ] Create "About the Author"

**5.4 Assembly** (PUBLISHER agent):
- [ ] Combine: front matter + chapters + back matter
- [ ] Verify chapter numbering
- [ ] Check all links/footnotes work
- [ ] Create `files/output/book-complete.md`

**5.5 Export** (PUBLISHER agent):
- [ ] Export to DOCX: `files/output/<book-name>.docx`
- [ ] Export to PDF: `files/output/<book-name>.pdf`
- [ ] Export to EPUB: `files/output/<book-name>.epub`
- [ ] Validate all exports open correctly

**Phase 5 Completion Criteria**:
- [ ] All formats exported
- [ ] All files validated
- [ ] No conversion artifacts
- [ ] Metadata correct

**Validation command**:
```bash
python engine/agents/tools/validate_phase_5.py my-books/<book>/
```

---

## 🚨 Common Pitfalls & How to Avoid Them

### Pitfall 1: Skipping Research (Non-Fiction)

**Symptom**:
```bash
❌ Writing chapters without research files
❌ Research file is template (not filled)
❌ Research file has <300 words
❌ Research file has <3 sources
```

**Prevention**:
```bash
# ALWAYS validate research before writing
python engine/agents/tools/validate_research.py \
       my-books/<book>/files/research/chapter-N-research.md

# Exit code 0 → research valid → proceed to writing
# Exit code 1 → research invalid → FIX ISSUES
```

**Fix**:
```bash
# Generate research template
python -m engine.cli generate-research <book> --chapter N

# Fill with actual research
# Re-validate until passing
```

---

### Pitfall 2: Missing Handoff Logs

**Symptom**:
```bash
❌ Chapter written but no handoff log from previous agent
❌ Phase validation fails due to missing handoff/
```

**Prevention**:
```bash
# After completing agent task, ALWAYS create handoff
cat > files/handoff/<from-agent>-to-<to-agent>-ch-N.md << EOF
# <From> → <To> Handoff (Chapter N)

Completed: $(date)
Status: READY_FOR_<NEXT_STEP>

[Summary of work done]
[Key findings/notes]
[Any issues/questions]
EOF
```

---

### Pitfall 3: Incorrect Directory Structure

**Symptom**:
```bash
❌ Missing directories: edits/, reviews/, proofread/
❌ Files in wrong locations
```

**Prevention**:
```bash
# Before starting phase, ensure directories exist
# Phase 1 should create all directories

# Fix missing directories:
python -m engine.cli fix-blockers <book> --phase <N>
```

---

### Pitfall 4: Outdated progress.md

**Symptom**:
```bash
⚠️ progress.md shows 0 words but chapters exist
⚠️ Chapter statuses don't match actual files
```

**Prevention**:
```bash
# After EVERY chapter, update progress.md
# Use actual word counts (wc -w)
# Update status to match phase (outline → research_complete → draft → edited → final)
```

---

### Pitfall 5: Skipping Validation

**Symptom**:
```bash
❌ Moving to next phase without validating current phase
❌ "It looks done" but validation fails
```

**Prevention**:
```bash
# ALWAYS run validation before claiming completion
python engine/agents/tools/validate_phase_<N>.py my-books/<book>/

# If exit code ≠ 0 → NOT DONE
# Fix all errors, then re-validate
```

---

## 🔍 Validation Reference

### Validation Tools

```bash
# Phase validators (block phase transitions if incomplete)
python engine/agents/tools/validate_phase_0.py my-books/<book>/  # Import
python engine/agents/tools/validate_phase_1.py my-books/<book>/  # Init
python engine/agents/tools/validate_phase_2.py my-books/<book>/  # Draft
python engine/agents/tools/validate_phase_3.py my-books/<book>/  # Edit
python engine/agents/tools/validate_phase_4.py my-books/<book>/  # Review
python engine/agents/tools/validate_phase_5.py my-books/<book>/  # Publish

# Specific validators
python engine/agents/tools/validate_research.py <research-file>
python engine/agents/tools/validate_chapter.py my-books/<book>/ --chapter N --phase 2
python engine/agents/tools/validate_final_chapters.py my-books/<book>/

# CLI tools
python -m engine.cli health <book>              # Show workflow health
python -m engine.cli phase-status <book>        # Show phase status
python -m engine.cli fix-blockers <book>        # Fix common issues
python -m engine.cli agent-instructions <book>  # Generate instructions
```

### Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Validation PASSED | Proceed to next step |
| 1 | CRITICAL errors found | MUST fix before proceeding |
| 2 | WARNINGS found | Can proceed but review needed |

---

## 📖 Quick Reference by Book Type

### Working on Fiction Book

```bash
# Phase 1: Init
[ ] Create config/plot.md (story structure)
[ ] Create config/characters.md (character profiles)
[ ] Create config/world.md (setting/worldbuilding)
[ ] Create config/outline.md (chapter breakdown)

# Phase 2: Draft
[ ] Write chapters sequentially (order matters)
[ ] Follow plot.md story arc
[ ] Maintain character consistency (check characters.md)
[ ] Maintain world consistency (check world.md)
[ ] Update progress.md after each chapter

# Phase 3: Edit
[ ] Developmental → Line → Copy editing
[ ] Check plot coherence
[ ] Verify character arcs
[ ] Ensure world consistency

# Phase 4: Review
[ ] CRITIC checks story structure
[ ] CRITIC checks character development
[ ] Author review
[ ] PROOFREADER final polish
```

### Working on Non-Fiction Book

```bash
# Phase 1: Init
[ ] Create config/outline.md (chapter breakdown with research questions)
[ ] Create config/bibliography.md

# Phase 2: Draft (CRITICAL: Research first!)
For each chapter:
  [ ] RESEARCHER: Conduct research (min 3 sources)
  [ ] RESEARCHER: Create research/chapter-N-research.md
  [ ] RESEARCHER: Validate research
  [ ] RESEARCHER: Create handoff log
  [ ] WRITER: Read research file
  [ ] WRITER: Write chapter using research
  [ ] WRITER: Update progress.md

# Phase 3: Edit
[ ] Developmental → Line → Copy editing
[ ] Verify argumentation logic
[ ] Check fact accuracy

# Phase 4: Review
[ ] CRITIC checks thesis clarity
[ ] CRITIC checks argument strength
[ ] RESEARCHER fact-checks all claims
[ ] Author review
[ ] PROOFREADER final polish + fact verification
```

---

## 🎓 Integration Examples

### Example 1: Starting Phase 2 (Non-Fiction)

```bash
# 1. Validate Phase 1 complete
python engine/agents/tools/validate_phase_1.py my-books/my-crypto-book/
# Exit code 0 → Phase 1 complete ✅

# 2. Check workflow health
python -m engine.cli health my-crypto-book
# Shows: Phase 1 complete, ready for Phase 2

# 3. Get instructions for chapter 1
python -m engine.cli agent-instructions my-crypto-book --phase 2 --chapter 1
# Creates: /tmp/agent-instructions-my-crypto-book-phase2.md

# 4. Follow instructions (RESEARCH FIRST for non-fiction!)
# Step 1: Generate research template
python -m engine.cli generate-research my-crypto-book --chapter 1
# Creates: my-books/my-crypto-book/files/research/chapter-1-research.md

# Step 2: Fill research template with actual research
# (Edit the file, add sources, facts, examples)

# Step 3: Validate research
python engine/agents/tools/validate_research.py \
       my-books/my-crypto-book/files/research/chapter-1-research.md
# Exit code 0 → Research valid ✅

# Step 4: Create handoff log
cat > my-books/my-crypto-book/files/handoff/researcher-to-writer-ch-1.md << EOF
# Research → Writing Handoff (Chapter 1)

Research completed: 2026-01-04
Sources found: 5
Key findings:
- Crypto trader failure rate: 80-90% (source: exchange retention data)
- Average holding time: <3 months before capitulation
- Main causes: emotional trading, no risk management

Ready for drafting: YES
EOF

# Step 5: Write chapter draft
# Create: my-books/my-crypto-book/files/content/chapters/chapter-1-draft-v1.md
# Using research file as factual foundation

# Step 6: Update progress
# Edit: my-books/my-crypto-book/config/progress.md
# | 1 | Chapter Title | 3500 | 3421 | 98% | ✅ draft | 2026-01-04 |

# Step 7: Validate chapter
python engine/agents/tools/validate_chapter.py \
       my-books/my-crypto-book/ --chapter 1 --phase 2
# Exit code 0 → Chapter valid ✅
```

### Example 2: Fixing Validation Errors

```bash
# Run validation
python engine/agents/tools/validate_phase_2.py my-books/my-book/

# Output shows errors:
🚫 PHASE 2 INCOMPLETE
❌ MISSING: files/research/chapter-2-research.md
❌ MISSING: files/research/chapter-3-research.md
❌ MISSING: files/handoff/researcher-to-writer-ch-1.md

# Use fix-blockers tool
python -m engine.cli fix-blockers my-book --phase 2

# Wizard generates:
✅ Created: files/research/chapter-2-research.md (template)
✅ Created: files/research/chapter-3-research.md (template)
✅ Created: files/handoff/researcher-to-writer-ch-1.md (template)

# Fill templates with actual data
# Re-validate
python engine/agents/tools/validate_phase_2.py my-books/my-book/
# Exit code 0 → Phase 2 complete ✅
```

---

## 🔗 Additional Resources

### Core Documentation
- **WORKFLOW.md** → `engine/agents/WORKFLOW.md` (6-phase process, CRITICAL)
- **AGENTS.md** → `engine/agents/AGENTS.md` (agent roles and responsibilities)
- **STRUCTURE.md** → `engine/STRUCTURE.md` (directory structure)

### Claude Code Specific
- **CLAUDE.md** → `/CLAUDE.md` (Claude Code context and instructions)
- **INTEGRATION.md** → `engine/agents/INTEGRATION.md` (Claude Code integration)

### Improvement Roadmap
- **Improvement Plan** → `engine/claude-improvements-suggestions.md` (planned features)

### Agent Contracts (Detailed Requirements)
- `engine/agents/contracts/RESEARCHER.md` (when available)
- `engine/agents/contracts/WRITER.md` (when available)
- `engine/agents/contracts/EDITOR.md` (when available)
- `engine/agents/contracts/ORCHESTRATOR.md` (when available)

---

## ✅ Final Checklist Before Starting Work

Before beginning any task, confirm:

- [ ] Read this file (CODING-AGENTS.md)
- [ ] Read WORKFLOW.md (understand phases)
- [ ] Identified book name and location (my-books/<book-name>/)
- [ ] Checked book type (fiction vs. non-fiction)
- [ ] Identified current phase (0-5)
- [ ] Ran health check: `python -m engine.cli health <book>`
- [ ] Validated previous phase (if applicable)
- [ ] Generated agent instructions (if needed)
- [ ] Understand required inputs for current task
- [ ] Understand required outputs for current task
- [ ] Know validation command to run when done

**When in doubt**:
1. Run: `python -m engine.cli health <book>`
2. Read: `engine/agents/WORKFLOW.md` for current phase
3. Ask: User for clarification

---

## 🆘 Troubleshooting

### "I don't know what phase we're in"

```bash
python -m engine.cli phase-status <book>
# Shows current phase and status
```

### "Validation is failing but I don't know why"

```bash
# Run validation in verbose mode
python engine/agents/tools/validate_phase_<N>.py my-books/<book>/ --verbose

# Or check health dashboard
python -m engine.cli health <book>
# Shows specific blockers
```

### "I need to skip a workflow step"

**⚠️ YOU CANNOT SKIP STEPS**

The workflow is designed to ensure quality. Skipping steps will:
- Cause validation failures
- Block phase transitions
- Create issues in later phases (e.g., no research → fact-check fails)

If a step seems unnecessary, escalate to user for clarification.

### "Research seems optional, can I skip it?"

**For non-fiction: NO, research is MANDATORY**

Research is not optional for non-fiction. Skipping research:
- Violates Phase 2 requirements
- Causes Phase 4 fact-check to fail
- Results in poor quality content

**For fiction: Research is optional but recommended**
- Historical fiction needs historical accuracy
- Sci-fi may need scientific research
- Any factual claims need sources

---

## 📝 Summary

**Remember**:

1. ✅ **Read documentation first** (WORKFLOW.md, AGENTS.md)
2. ✅ **Validate before and after** (use validation tools)
3. ✅ **Follow phase order** (cannot skip phases)
4. ✅ **Research before writing** (non-fiction only, but mandatory)
5. ✅ **Create all required files** (drafts, handoffs, tracking)
6. ✅ **Update progress.md** (after every chapter)
7. ✅ **Use handoff logs** (document agent transitions)
8. ✅ **Check book type** (fiction vs. non-fiction have different rules)

**When unsure**: Run `python -m engine.cli health <book>` and read the output.

**Questions?**: Ask the user or read the detailed documentation in `engine/agents/`.

---

**Good luck! 🚀**

Remember: This is a quality-focused system. Following the workflow ensures high-quality output. Shortcuts lead to validation failures and rework.
