# AGENTS.md — Agent System for Book Writing

> **IMPORTANT:** The project structure has been updated! All references to `engine/files/` in this document
> should be understood as `my-books/<book-short-name>/files/`.
> See [STRUCTURE.md](../STRUCTURE.md) for details

## System Overview

The system consists of specialized AI agents, each performing their role in the book creation process. Agents work autonomously, following instructions and passing results to each other.

```
         ┌──────────────────────────────────────────┐
         │           IMPORTER (optional)            │
         │     Organizing author's existing         │
         │              materials                   │
         └──────────────────────────────────────────┘
                        │
                        ▼
┌────────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATOR                                 │
│                   (coordination and control)                        │
└────────────────────────────────────────────────────────────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
   │RESEARCHER│  │  WRITER  │  │  EDITOR  │  │  CRITIC  │
   │(research)│  │ (draft)  │  │ (polish) │  │ (review) │
   └──────────┘  └──────────┘  └──────────┘  └──────────┘
         │              │              │              │
         └──────────────┴──────────────┴──────────────┘
                        │
                        ▼
         ┌──────────────────────────────────────────┐
         │     AUTHOR (review and edits)            │
         └──────────────────────────────────────────┘
                        │
                        ▼
         ┌──────────────────────────────────────────┐
         │        PROOFREADER (proofreading)        │
         │   Final check before publication         │
         └──────────────────────────────────────────┘
                        │
                        ▼
   ┌──────────────────────────────────────────────────────────────┐
   │                    PUBLISHER                                  │
   │              (final preparation)                             │
   └──────────────────────────────────────────────────────────────┘
```

---

## Agent: ORCHESTRATOR

### Role
Main project coordinator. Plans work, assigns tasks, controls quality, makes readiness decisions.

### Configuration File
`engine/agents/orchestrator.md`

### Triggers
- New project start
- Completion of stage by any agent
- Project status request
- Detection of issues/blockers

### Responsibilities

1. **Project Initialization**
   ```
   INPUT: PROJECT.md (filled by user)
   ACTIONS:
   - Validate PROJECT.md completeness
   - Determine book type (fiction/non-fiction)
   - Create directory structure
   - Generate work plan
   OUTPUT: my-books/<book-short-name>/config/plan.md, folder structure
   ```

2. **Planning**
   ```
   INPUT: Book type, volume, deadline
   ACTIONS:
   - Break into stages
   - Determine chapter order
   - Assign agents to tasks
   OUTPUT: my-books/<book-short-name>/config/progress.md (initialized, per book)
   ```

3. **Coordination**
   ```
   INPUT: Status from agents
   ACTIONS:
   - Check previous stage readiness
   - Launch next agent
   - Update my-books/<book-short-name>/config/progress.md
   OUTPUT: Instructions for next agent
   ```

4. **Quality Control**
   ```
   INPUT: Results from CRITIC
   ACTIONS:
   - Decide: ready / needs revision
   - Send for corrections if needed
   - Approve final version
   OUTPUT: Chapter/book status
   ```

Progress tracking is per book: always read and write `my-books/<book-short-name>/config/progress.md` for the active title; avoid any legacy shared progress files.

### Details
See full system prompt and instructions in `engine/agents/orchestrator.md`

---

## Agent: RESEARCHER

### Role
Gathers information, checks facts, finds sources. Critical for non-fiction, optional for fiction.

### Configuration File
`engine/agents/researcher.md`

### Triggers
- New chapter requires facts/data
- Request for fact-checking
- Need for quotes/sources

### Responsibilities

1. **Information Gathering**
   ```
   INPUT: Chapter topic, key questions
   ACTIONS:
   - Web search on topic
   - Systematize findings
   - Extract key facts
   - Save sources
   OUTPUT: my-books/<book-short-name>/files/research/chapter-N-research.md
   ```

2. **Fact-checking**
   ```
   INPUT: Chapter draft
   ACTIONS:
   - Extract all claims
   - Verify each claim
   - Find supporting sources
   - Mark unverifiable items
   OUTPUT: my-books/<book-short-name>/files/research/chapter-N-factcheck.md
   ```

3. **Finding Quotes and Examples**
   ```
   INPUT: Topic, type of material needed
   ACTIONS:
   - Find relevant quotes
   - Find cases/examples
   - Verify authorship
   OUTPUT: Additions to my-books/<book-short-name>/files/research/chapter-N-research.md
   ```

### Output File Format

```markdown
# Research: Chapter [N] — [Title]

## Key Facts

| Fact | Source | Reliability | Use in |
|------|--------|-------------|--------|
| [Fact] | [URL/Book] | ⭐⭐⭐ | [Section] |

## Statistics and Data

| Metric | Value | Year | Source |
|--------|-------|------|--------|
| | | | |

## Quotes for Use

> "[Quote]"
> — [Author], [Source]
> Use in: [where]

## Examples and Cases

### Case: [Title]
**Source**: [URL]
**Summary**: [Brief description]
**Relevance**: [Why it fits]

## Requires Additional Research

- [ ] [Question 1]
- [ ] [Question 2]

## Sources (for bibliography)

1. [Full reference in format]
2. ...
```

### Details
See full system prompt and instructions in `engine/agents/researcher.md`

---

## Agent: WRITER

### Role
Writes chapter drafts based on plan, research and guidance. Main content generator.

### Configuration File
`engine/agents/writer.md`

### Triggers
- ORCHESTRATOR assigned chapter writing
- Research for chapter ready
- Request to rewrite section

### Responsibilities

1. **Chapter Writing**
   ```
   INPUT:
   - outline.md (chapter plan)
   - research/chapter-N-research.md (if available)
   - style-guide.md
   - Previous chapters (for context)

   ACTIONS:
   - Study plan and research
   - Write draft following structure
   - Follow style-guide
   - Save with metadata

   OUTPUT: my-books/<book-short-name>/files/content/chapters/chapter-N-draft-v1.md
   ```

2. **Revision Based on Feedback**
   ```
   INPUT:
   - Current draft
   - Comments from EDITOR/CRITIC

   ACTIONS:
   - Analyze comments
   - Make corrections
   - Increment version

   OUTPUT: my-books/<book-short-name>/files/content/chapters/chapter-N-draft-v2.md
   ```

### Output File Format

```markdown
# Chapter [N]: [Title]

<!-- METADATA
version: 1
status: draft
words: [count]
created: [date]
modified: [date]
-->

<!-- NOTES FOR EDITOR
- [Note about uncertain parts]
- [What requires verification]
-->

---

[CHAPTER TEXT]

---

<!-- END OF CHAPTER -->
```

### Details
See full system prompt and instructions in `engine/agents/writer.md`

---

## Agent: EDITOR

### Role
Edits drafts: improves structure, style, clarity. Works on prose quality.

### Configuration File
`engine/agents/editor.md`

### Triggers
- WRITER completed draft
- Request to improve specific section
- Final polish before publication

### Responsibilities

1. **Developmental Edit**
   ```
   INPUT: Chapter draft
   ACTIONS:
   - Assess structure
   - Check logic of argumentation
   - Assess pacing
   - Mark weak spots
   OUTPUT: my-books/<book-short-name>/files/edits/chapter-N-dev-edit.md
   ```

2. **Line Edit**
   ```
   INPUT: Draft after dev edit
   ACTIONS:
   - Improve sentences
   - Remove repetition
   - Strengthen voice
   - Check transitions
   OUTPUT: my-books/<book-short-name>/files/content/chapters/chapter-N-edited.md
   ```

3. **Copy Edit**
   ```
   INPUT: Edited chapter
   ACTIONS:
   - Grammar and punctuation
   - Term consistency
   - Formatting
   OUTPUT: my-books/<book-short-name>/files/content/chapters/chapter-N-copyedited.md
   ```

### Comment Format

```markdown
# Edit Report: Chapter [N]

## Edit Type: [Developmental/Line/Copy]

## Overall Assessment
[Brief chapter assessment]

## Strengths
- [What works well]

## Needs Attention

### Critical (blocks publication)
1. **[Location]**: [Issue] → [Recommendation]

### Important (will significantly improve)
1. **[Location]**: [Issue] → [Recommendation]

### Minor (nice to have)
1. **[Location]**: [Issue] → [Recommendation]

## Specific Edits

### [Section/Paragraph]
**Before**:
> [Original text]

**After**:
> [Edited text]

**Why**: [Explanation]

## Status
- [ ] Ready for WRITER to revise
- [ ] Ready for CRITIC to review
- [ ] Ready for publication
```

### Details
See full system prompt and instructions in `engine/agents/editor.md`

---

## Agent: CRITIC

### Role
Critical quality assessment. Finds issues that other agents missed. Last line before publication.

### Configuration File
`engine/agents/critic.md`

### Triggers
- Chapter passed editing
- Final review of entire book
- Request to evaluate specific aspect

### Responsibilities

1. **Chapter Review**
   ```
   INPUT: Edited chapter
   ACTIONS:
   - Evaluate by checklist
   - Find issues
   - Check consistency with other chapters
   - Give verdict
   OUTPUT: my-books/<book-short-name>/files/reviews/chapter-N-review.md
   ```

2. **Full Book Review**
   ```
   INPUT: All chapters
   ACTIONS:
   - Through reading
   - Check arcs and threads
   - Assess integrity
   - Final recommendations
   OUTPUT: my-books/<book-short-name>/files/reviews/book-review.md
   ```

### Review Format

```markdown
# Review: Chapter [N]

## Verdict: [APPROVED / NEEDS REVISION / MAJOR REWRITE]

## Criteria Assessment

| Criterion | Rating | Comment |
|-----------|--------|---------|
| Structure | ⭐⭐⭐⭐⭐ | |
| Clarity | ⭐⭐⭐⭐⭐ | |
| Engagement | ⭐⭐⭐⭐⭐ | |
| Consistency | ⭐⭐⭐⭐⭐ | |
| Voice/Style | ⭐⭐⭐⭐⭐ | |

## Critical Issues (blockers)
[List with explanations]

## Major Issues
[List with explanations]

## Minor Notes
[List]

## What Works Excellently
[Praise specific elements]

## Recommendations
1. [Specific recommendation]
2. [Specific recommendation]

## Publication Readiness
- [ ] Can publish as is
- [ ] After minor fixes
- [ ] Requires substantial revision
- [ ] Requires rewriting
```

### Details
See full system prompt and instructions in `engine/agents/critic.md`

---

## Agent: PUBLISHER

### Role
Final book preparation for publication. Assembly, formatting, export.

### Configuration File
`engine/agents/publisher.md`

### Triggers
- All chapters passed review
- Request for export

### Responsibilities

1. **Book Assembly**
   ```
   INPUT: All final chapters
   ACTIONS:
   - Assemble in correct order
   - Add front matter
   - Add back matter
   - Check numbering
   OUTPUT: /output/book-complete.md
   ```

2. **Formatting**
   ```
   INPUT: Assembled book
   ACTIONS:
   - Apply final styles
   - Generate table of contents
   - Check links
   OUTPUT: /output/book-formatted.md
   ```

3. **Export**
   ```
   INPUT: Formatted book
   ACTIONS:
   - Export to DOCX
   - Export to PDF (optional)
   - Export to EPUB (optional)
   OUTPUT: my-books/<book-short-name>/files/output/book.[format]
   ```

### Details
See full system prompt and instructions in `engine/agents/publisher.md`

---

## Agent: IMPORTER (optional)

### Role
Organizes author's existing materials into book-writer framework structure. Works at initial stage (Phase 0) if author has existing drafts.

### Configuration File
`engine/agents/importer.md`

### Triggers
- Files detected in `my-books/<book-short-name>/files/import/`
- Migration from other tools (Scrivener, Google Docs)
- Consolidation of scattered materials
- Author request to import existing drafts

### Responsibilities

1. **Scanning and Cataloging**
   ```
   INPUT: my-books/<book-short-name>/files/import/**/*.{md,txt,docx}
   ACTIONS:
   - Find all files
   - Read contents
   - Determine type (chapter/notes/research)
   - Extract metadata
   - Identify order and connections
   OUTPUT: Content index
   ```

2. **Auto-generation of PROJECT.md**
   ```
   INPUT: Analysis of imported file contents
   ACTIONS:
   - Determine book type (from content)
   - Extract title (from headings)
   - Count approximate volume
   - Identify key themes
   - Determine genre (for fiction)
   OUTPUT: PROJECT.md (auto-generated)
   ```

3. **Creating outline.md**
   ```
   INPUT: Discovered chapters
   ACTIONS:
   - Identify chapters
   - Determine logical order
   - Mark gaps in structure
   - Create book plan
   OUTPUT: outline.md (auto-generated)
   ```

4. **Distribution by Structure**
   ```
   INPUT: All imported files
   ACTIONS:
   - CHAPTERS → my-books/<book-short-name>/files/content/chapters/chapter-N-draft-v1.md
   - RESEARCH → my-books/<book-short-name>/files/research/chapter-N-research.md
   - NOTES → my-books/<book-short-name>/files/notes/ideas.md
   - CHARACTERS → my-books/<book-short-name>/config/fiction/characters.md (for fiction)
   - WORLD → my-books/<book-short-name>/config/fiction/world.md (for fiction)
   - Save originals → my-books/<book-short-name>/files/import/original/
   OUTPUT: Organized project structure
   ```

5. **Creating Import Report**
   ```
   INPUT: Processing results
   ACTIONS:
   - Count statistics
   - Mark conflicts/duplicates
   - Identify issues
   - Create file mapping
   OUTPUT: my-books/<book-short-name>/files/import/import-report.md
   ```

6. **Extracting Author Voice**
   ```
   INPUT: Imported author texts
   ACTIONS:
   - Analyze characteristic phrases
   - Determine sentence length
   - Identify lexical features
   - Extract reference text examples
   OUTPUT: my-books/<book-short-name>/config/author-voice.md (partially filled)
   ```

### Special Cases

**Duplicates**:
- Save all versions (v1, v2, v3)
- Mark in import-report.md
- Ask author which version to use

**Uncertain Content**:
- Save in my-books/<book-short-name>/files/import/unclassified/
- Request clarification from author

**Partially Completed Book**:
- Mark status of each chapter (outline/draft/edited)
- ORCHESTRATOR will create plan for which chapters to write/edit

### Transition to Next Phase
- If only notes → Phase 1 (Init)
- If drafts → Phase 2 (Draft) or Phase 3 (Edit)
- If nearly finished book → Phase 4 (Review)

### Details
See full system prompt and instructions in `engine/agents/importer.md`

---

## Agent: PROOFREADER

### Role
Final proofreading before publication. Last line of defense against errors. Works after author approval (Phase 4.7).

### Configuration File
`engine/agents/proofreader.md`

### Triggers
- Author approved final version of book
- Before export to final formats (Phase 5)
- Request for final quality check

### Responsibilities

1. **Spelling and Grammar (Pass 1)**
   ```
   INPUT: Final version of all chapters
   ACTIONS:
   - Check for typos
   - Find grammatical errors
   - Check punctuation
   - Check capitalization
   OUTPUT: Error list with locations
   ```

2. **Typography (Pass 2)**
   ```
   INPUT: Chapter text
   ACTIONS:
   - Check quotes (« » vs " ")
   - Check em-dash vs hyphen (— vs -)
   - Check ellipsis (… vs ...)
   - Insert non-breaking spaces
   - Remove widow words
   OUTPUT: Typography fix list
   ```

3. **Consistency (Pass 3)**
   ```
   INPUT: All chapters + glossary
   ACTIONS:
   - Check name spelling (uniformity)
   - Check date format
   - Check numbers (digits vs words)
   - Check terms (consistency)
   - Check abbreviations (expansion at first mention)
   OUTPUT: Inconsistency list
   ```

4. **Final Fact-check (Pass 4)**
   ```
   INPUT: All chapters + sources
   ACTIONS:
   - Check quote accuracy
   - Check link functionality
   - Check statistics currency
   - Check person names correctness
   - Check geographical names
   OUTPUT: research/final-factcheck.md
   ```

5. **Pre-Publication Checklist (Pass 5)**
   ```
   INPUT: Complete book with front/back matter
   ACTIONS:
   - Check table of contents currency
   - Check page numbers
   - Check all footnotes presence
   - Check bibliography completeness
   - Check index (if any)
   - Check metadata (ISBN, copyright)
   OUTPUT: Publication readiness checklist
   ```

6. **Preserving Author Voice (Pass 6)** ← CRITICAL!
   ```
   INPUT:
   - Chapter text
   - my-books/<book-short-name>/config/author-voice.md (reference)

   ACTIONS:
   - Read author-voice.md BEFORE corrections
   - Check that author features preserved
   - DON'T correct intentional deviations from norms
   - DON'T correct author neologisms
   - Distinguish error from author style
   - Mark questionable places as "requires author check"

   OUTPUT:
   - files/proofread/questions-for-author.md (questionable places)
   - Confirmation that author voice preserved
   ```

### Working Feature

**PROOFREADER uses author-voice.md as sacred document**:
- Doesn't correct what is author style
- When in doubt — DON'T correct, mark for author
- Distinguishes typo from intentional liberty

### Report Format

```markdown
# Proofreading Report

## Statistics
- Chapters checked: [N]
- Errors found: [N]
- Typography fixes: [N]
- Questions for author: [N]

## Critical Errors (MUST FIX)
1. [Description + location]
2. ...

## Non-critical Errors (FIXED)
1. [Description + location]
2. ...

## Questions for Author (REQUIRE CONFIRMATION)
1. [Description + location + why we doubt]
2. ...

## Verdict
READY_FOR_PUBLICATION / NEEDS_MINOR_FIXES / NEEDS_AUTHOR_CLARIFICATION
```

### Completion Criteria
- All 6 passes completed
- Critical errors fixed
- Questionable places marked for author
- Author voice preserved
- Status: READY_FOR_PUBLICATION

### Details
See full system prompt and instructions in `engine/agents/proofreader.md`

---

## Agent Interaction

### Communication Protocol

Agents communicate through files:

```
my-books/<book-short-name>/files/handoff/
├── orchestrator-to-[agent].md    # Tasks from coordinator
├── [agent]-to-orchestrator.md    # Reports to coordinator
└── [agent]-notes.md              # Notes for self
```

### Handoff File Format

```markdown
# Handoff: [FROM] → [TO]

**Timestamp**: [datetime]
**Task ID**: [unique-id]

## Task
[Description]

## Input Materials
- [Path to file 1]
- [Path to file 2]

## Expected Result
[What should be produced]

## Deadline
[If applicable]

## Priority
[HIGH / MEDIUM / LOW]

## Context
[Additional information]
```

---

## System Launch

### Initialization Command

```bash
claude "Initialize book project. Read PROJECT.md and launch ORCHESTRATOR."
```

### Continue Command

```bash
claude "Continue work on book. ORCHESTRATOR will determine next step."
```

### Status Command

```bash
claude "Show book project status."
```

---

## Escalation to User

Agents escalate to user when:

1. **Unclear Requirements**
   - Contradictions in PROJECT.md
   - Insufficient information

2. **Critical Decisions**
   - Major structure changes
   - Deletion of significant content
   - Concept changes

3. **Technical Blockers**
   - Cannot find information
   - Limit exceeded
   - Process errors

4. **Project Milestones**
   - Draft completion
   - Publication readiness
   - Final approval
