# WORKFLOW.md — Book Writing Workflow

> **Structure update:** Each book now has its own `my-books/<book-short-name>/` folder with configuration in `config/` (including `my-books/<book-short-name>/config/progress.md`) and working documents in `files/`. All examples below follow this per-book path layout—legacy `engine/files` snippets have been removed.

## Process Overview

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                           COMPLETE BOOK CREATION CYCLE                                │
├──────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                       │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐ │
│  │PHASE 0 │─▶│PHASE 1 │─▶│PHASE 2 │─▶│PHASE 3 │─▶│PHASE 4 │─▶│PHASE 5 │─▶│ DONE   │ │
│  │ IMPORT │  │  INIT  │  │ DRAFT  │  │  EDIT  │  │ REVIEW │  │PUBLISH │  │        │ │
│  └────────┘  └────────┘  └────────┘  └────────┘  └────────┘  └────────┘  └────────┘ │
│      │           │            │           │          │   │         │                  │
│      ▼           ▼            ▼           ▼          │   ▼         ▼                  │
│  Import     PROJECT.md   Chapter      Editing       │  Author   Ready               │
│  materials  + Outline    drafts       + revisions   │  Review   book                │
│  (optional)                                         │  Proof                         │
│                                                     └─▶Final                          │
│                                                         Checks                        │
│                                                                                       │
└──────────────────────────────────────────────────────────────────────────────────────┘

NEW: Phase 0 is optional if existing materials are available
NEW: Phase 4 expanded with final checks before publication
```

---

## PHASE 0: Import (optional)

### Purpose
Organize author's existing materials into the book-writer framework structure.

### When to Use
- Author has ready chapter drafts
- There are notes and sketches that need structuring
- Migration from other tools (Scrivener, Google Docs, etc.)
- Consolidation of scattered files

### Input Data
- Any author files in `my-books/<book-short-name>/files/import/`
- Supported formats: .md, .txt, .docx

### Steps

#### 0.1 Import Preparation
```
AUTHOR
ACTION: Gather all materials

ACTIONS:
1. Specify the target book directory name (or let IMPORTER create it using your path).
2. Place all files in my-books/<book-short-name>/files/import/ (or specify the path to your documents in the prompt, IMPORTER will copy them there):
   - Chapter drafts
   - Notes and ideas
   - Research
   - Outlines
   - Any related materials

IMPORTANT:
- No need to rename files
- No need to organize
- IMPORTER will handle everything
```

#### 0.2 Automatic Import
```
AGENT: IMPORTER
TRIGGER: Files detected in my-books/<book-short-name>/files/import/

ACTIONS:
1. Scanning:
   - Find all files (.md, .txt, .docx)
   - Read content
   - Catalog

2. Content analysis:
   - Determine type (chapter/notes/research)
   - Extract metadata (headings, dates)
   - Identify order (if numbered)
   - Discover connections between files

3. Auto-generate PROJECT.md:
   - Determine book type (from content)
   - Extract title (from headings)
   - Count volume
   - Identify key themes
   - Determine genre (for fiction)

4. Create my-books/<book-short-name>/config/outline.md:
   - Identify chapters
   - Determine logical order
   - Mark gaps in structure

5. Distribution to directories:
   CHAPTERS → my-books/<book-short-name>/files/content/chapters/
   - Rename: chapter-N-draft-v1.md
   - Add metadata
   - Save original in my-books/<book-short-name>/files/import/original/

   RESEARCH → my-books/<book-short-name>/files/research/
   - Systematize by topics
   - Create research.md files

   NOTES → my-books/<book-short-name>/files/notes/
   - Organize by categories
   - Create index

   FOR FICTION:
   - Characters → my-books/<book-short-name>/config/characters.md
   - World → my-books/<book-short-name>/config/world.md
   - Plot → my-books/<book-short-name>/config/plot.md

OUTPUT DATA:
→ my-books/<book-short-name>/config/PROJECT.md (generated)
→ my-books/<book-short-name>/config/outline.md (generated)
→ my-books/<book-short-name>/files/content/chapters/*.md (imported chapters)
→ my-books/<book-short-name>/files/research/*.md (imported research)
→ my-books/<book-short-name>/files/notes/*.md (imported notes)
→ my-books/<book-short-name>/files/import/import-report.md (report)
→ my-books/<book-short-name>/files/import/original/ (original backups)
```

#### 0.3 Import Verification
```
AGENT: ORCHESTRATOR
TRIGGER: IMPORTER completed work

ACTIONS:
1. Read import-report.md
2. Check:
   - All files processed
   - No conflicts (duplicates)
   - Book type correctly identified
   - Chapter order logical

3. Escalate to author:
   - List of discovered issues
   - Request clarifications:
     * Is chapter order correct?
     * Which version to use (for duplicates)?
     * Fill missing metadata in my-books/<book-short-name>/config/PROJECT.md

OUTPUT DATA:
→ List of questions for author
→ Updated my-books/<book-short-name>/config/progress.md
```

#### 0.4 Clarification and Correction
```
AUTHOR + ORCHESTRATOR
TRIGGER: Author answered questions

ACTIONS:
1. Resolve conflicts (choose versions)
2. Correct chapter order (if needed)
3. Fill missing fields in my-books/<book-short-name>/config/PROJECT.md
4. Check my-books/<book-short-name>/config/author-voice.md:
   - Extract characteristic phrases from imported text
   - Fill author voice template
   - Save examples of reference texts

RESULT:
→ my-books/<book-short-name>/config/PROJECT.md fully filled
→ my-books/<book-short-name>/config/outline.md corrected
→ my-books/<book-short-name>/config/author-voice.md filled based on existing text
→ Conflicts resolved
→ Readiness for Phase 1 (or directly to Phase 2 if chapters are ready)
```

### Special Cases

#### Import of Partially Completed Book
```
IF: Some chapters fully written, some are sketches

ACTION:
- Complete chapters → mark status: "draft" or "edited"
- Sketches → mark status: "outline" or "notes"
- ORCHESTRATOR creates plan: which chapters to write, which to edit
```

#### Import Without Clear Structure
```
IF: Files not divided into chapters, only continuous text

ACTION:
- IMPORTER attempts to split by headings
- If fails → save as my-books/<book-short-name>/files/import/unclassified/
- Ask author: how to split into chapters?
```

#### Duplicates and Version Conflicts
```
IF: Two files claim one chapter (chapter2.md and ch02-draft.txt)

ACTION:
- Save both versions:
  * chapter-2-draft-v1.md (from chapter2.md)
  * chapter-2-draft-v2.md (from ch02-draft.txt)
- Mark in import-report.md
- Ask author: which version to use?
```

### Phase 0 Completion Criteria
- [ ] All files from my-books/<book-short-name>/files/import/ processed
- [ ] my-books/<book-short-name>/config/PROJECT.md generated and verified by author
- [ ] my-books/<book-short-name>/config/outline.md created
- [ ] my-books/<book-short-name>/config/author-voice.md filled (based on imported text)
- [ ] Files distributed by structure
- [ ] Originals saved in my-books/<book-short-name>/files/import/original/
- [ ] import-report.md created
- [ ] Conflicts resolved
- [ ] Readiness for next phase determined

### Transition to Next Phase

```
IF: Only notes/plans imported
→ Phase 1 (Initialization — structure creation)

IF: Chapter drafts imported
→ Phase 2 (Writing — complete missing chapters)
   OR
→ Phase 3 (Editing — if all chapters present)

IF: Almost finished book imported
→ Phase 4 (Review — final check)
```

---

## PHASE 1: Initialization

### Purpose
Prepare everything necessary to begin writing.

### Input Data
- `my-books/<book-short-name>/config/PROJECT.md` — filled by user

### Steps

#### 1.1 Project Validation
```
AGENT: ORCHESTRATOR
ACTION: Check my-books/<book-short-name>/config/PROJECT.md

CHECKS:
- [ ] Book title specified
- [ ] Type (fiction/non-fiction) determined
- [ ] Target audience described
- [ ] Approximate volume specified
- [ ] Key themes listed

IF INCOMPLETE:
→ Request missing information from user

RESULT:
→ my-books/<book-short-name>/config/PROJECT.md validated
→ Record in my-books/<book-short-name>/config/progress.md
```

#### 1.2 Structure Creation
```
AGENT: ORCHESTRATOR
ACTION: Create directories and files

FOR NON-FICTION:
my-books/<book-short-name>/
├── config/
│   ├── PROJECT.md
│   ├── outline.md
│   ├── style-guide.md
│   ├── review-checklist.md
│   └── progress.md
└── files/
    ├── content/
    │   ├── front-matter/
    │   ├── chapters/
    │   └── back-matter/
    ├── research/
    ├── edits/
    ├── reviews/
    ├── handoff/
    └── output/

FOR FICTION:
my-books/<book-short-name>/
├── config/
│   ├── PROJECT.md
│   ├── plot.md
│   ├── characters.md
│   ├── world.md
│   ├── style-guide.md
│   ├── review-checklist.md
│   └── progress.md
└── files/
    ├── content/
    │   ├── chapters/
    │   └── scenes/
    ├── edits/
    ├── reviews/
    ├── handoff/
    ├── research/
    └── output/

RESULT:
→ Structure created
→ Templates copied
```

#### 1.3 Outline Generation
```
AGENT: ORCHESTRATOR → WRITER
ACTION: Create detailed outline

INPUT DATA:
- my-books/<book-short-name>/config/PROJECT.md
- Outline template (from templates)

PROCESS:
1. WRITER analyzes concept
2. WRITER proposes chapter structure
3. For each chapter determines:
   - Main idea
   - Key points
   - Approximate volume
4. ORCHESTRATOR approves plan

RESULT:
→ my-books/<book-short-name>/config/outline.md created
→ User confirmed plan
```

#### 1.4 Worldbuilding/Research Preparation
```
AGENT: RESEARCHER (non-fiction) or WRITER (fiction)

FOR NON-FICTION:
- Gather initial sources
- Compile list of research questions
- Create my-books/<book-short-name>/files/research/README.md

FOR FICTION:
- Fill my-books/<book-short-name>/config/world.md (basic)
- Fill my-books/<book-short-name>/config/characters.md (protagonist, antagonist)
- Fill my-books/<book-short-name>/config/plot.md (structure)

RESULT:
→ Basic materials ready
→ Can start writing
```

### Phase 1 Completion Criteria
- [ ] my-books/<book-short-name>/config/PROJECT.md complete and valid
- [ ] Directory structure created
- [ ] my-books/<book-short-name>/config/outline.md approved
- [ ] Basic materials ready
- [ ] my-books/<book-short-name>/config/progress.md initialized

---

## PHASE 2: Writing Drafts

### Purpose
Write first draft of all chapters.

### Input Data
- my-books/<book-short-name>/config/outline.md
- my-books/<book-short-name>/files/research/ (for non-fiction)
- my-books/<book-short-name>/config/world.md, my-books/<book-short-name>/config/characters.md, my-books/<book-short-name>/config/plot.md (for fiction)

### Main Cycle

```
┌──────────────────────────────────────────────────────────────┐
│                    CHAPTER WRITING CYCLE                      │
│                                                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐       │
│  │  RESEARCH   │───▶│   WRITE     │───▶│   SAVE      │       │
│  │  (if needed)│    │   DRAFT     │    │   PROGRESS  │       │
│  └─────────────┘    └─────────────┘    └─────────────┘       │
│         │                  │                  │               │
│         ▼                  ▼                  ▼               │
│   my-books/<book-short-name>/files/research/            my-books/<book-short-name>/files/content/          my-books/<book-short-name>/config/progress.md         │
│   chapter-N.md                                   chapter-N-v1.md                         updated            │
│                                                               │
│  REPEAT FOR EACH CHAPTER                                     │
└──────────────────────────────────────────────────────────────┘
```

#### 2.1 Chapter Research (Non-Fiction)
```
AGENT: RESEARCHER
TRIGGER: ORCHESTRATOR assigns chapter

INPUT DATA:
- my-books/<book-short-name>/config/outline.md (chapter section)
- Previous research in my-books/<book-short-name>/files/research/

ACTIONS:
1. Determine key chapter questions
2. Conduct web search
3. Gather facts and statistics
4. Find examples and cases
5. Record quotes
6. Save sources

OUTPUT DATA:
→ my-books/<book-short-name>/files/research/chapter-N-research.md

READINESS CRITERIA:
- [ ] All key questions covered
- [ ] Minimum 3 sources per chapter
- [ ] Concrete examples present
- [ ] Sources recorded for bibliography
```

#### 2.2 Draft Writing
```
AGENT: WRITER
TRIGGER: Research ready (or immediately for fiction)

INPUT DATA:
- my-books/<book-short-name>/config/outline.md (chapter section)
- my-books/<book-short-name>/files/research/chapter-N-research.md (for non-fiction)
- my-books/<book-short-name>/config/style-guide.md
- Previous chapter (for continuity)

ACTIONS:
1. Study chapter plan
2. Study research
3. Re-read end of previous chapter
4. Write draft:
   - Hook (first 300 words)
   - Main content
   - Transition to next chapter
5. Add metadata
6. Mark questionable areas

OUTPUT DATA:
→ my-books/<book-short-name>/files/content/chapters/chapter-N-draft-v1.md

READINESS CRITERIA:
- [ ] Volume within 80-120% of plan
- [ ] All sections from outline covered
- [ ] Hook at beginning
- [ ] Transition at end
- [ ] Metadata filled
```

#### 2.3 Progress Update
```
AGENT: ORCHESTRATOR
TRIGGER: WRITER completed chapter

ACTIONS:
1. Check file created
2. Count words
3. Update my-books/<book-short-name>/config/progress.md
4. Determine next chapter
5. Assign next task

UPDATES IN my-books/<book-short-name>/config/progress.md:
- Chapter status: draft
- Word count
- Update date
- Overall progress %
```

Example entry in a per-book progress file:
```
my-books/adventure/config/progress.md
phase: 2 (Draft)
status:
  chapter-1:
    state: draft
    words: 3200
    updated: 2025-02-10
  chapter-2:
    state: research
    words: 0
    updated: 2025-02-11
overall:
  percent_complete: 25
  last_updated: 2025-02-11
```

### Chapter Writing Order

```
STRATEGY 1: Sequential (recommended for fiction)
Chapter 1 → Chapter 2 → Chapter 3 → ...

STRATEGY 2: By research readiness (for non-fiction)
Research ready → write that chapter

STRATEGY 3: Key scenes first (for fiction)
Climax → Turning points → Rest
```

### Phase 2 Completion Criteria
- [ ] All chapters written
- [ ] All chapters have "draft" status
- [ ] Overall word count achieved
- [ ] No missing sections

---

## PHASE 3: Editing

### Purpose
Transform drafts into polished text.

### Input Data
- All chapter drafts
- my-books/<book-short-name>/config/style-guide.md

### Editing Levels

```
┌─────────────────────────────────────────────────────────────────┐
│                     EDITING PYRAMID                              │
│                                                                  │
│                    ┌─────────────┐                               │
│                    │  PROOFREAD  │  ← Typos, formatting         │
│                    └─────────────┘                               │
│                  ┌─────────────────┐                             │
│                  │    COPY EDIT    │  ← Grammar, consistency     │
│                  └─────────────────┘                             │
│                ┌─────────────────────┐                           │
│                │     LINE EDIT      │  ← Prose, voice, clarity   │
│                └─────────────────────┘                           │
│              ┌─────────────────────────┐                         │
│              │   DEVELOPMENTAL EDIT    │  ← Structure, logic      │
│              └─────────────────────────┘                         │
│                                                                  │
│  EDIT BOTTOM UP: structure first, then details                  │
└─────────────────────────────────────────────────────────────────┘
```

#### 3.1 Developmental Edit
```
AGENT: EDITOR
TRIGGER: All drafts ready OR chapter ready

INPUT DATA:
- Chapter draft from my-books/<book-short-name>/files/content/chapters/
- my-books/<book-short-name>/config/outline.md

FOCUS:
- Does structure match plan?
- Is argumentation/plot logical?
- Any sagging sections?
- All parts necessary?
- Correct pacing?

ACTIONS:
1. Read chapter completely
2. Compare with plan
3. Mark structural issues
4. Suggest changes in order/deletion/addition

OUTPUT DATA:
→ my-books/<book-short-name>/files/edits/chapter-N-dev-edit.md

NEXT:
→ If critical issues: WRITER rewrites
→ If minor: proceed to line edit
```

#### 3.2 Line Edit
```
AGENT: EDITOR
TRIGGER: Developmental edit completed

INPUT DATA:
- Draft (possibly updated) in my-books/<book-short-name>/files/content/chapters/
- my-books/<book-short-name>/config/style-guide.md

FOCUS:
- Sentence clarity
- Verb strength
- Rhythm and pace
- Voice and tone
- Transitions between paragraphs

ACTIONS:
1. Pass through each paragraph
2. Rewrite weak sentences
3. Remove excess
4. Strengthen key moments

OUTPUT DATA:
→ my-books/<book-short-name>/files/content/chapters/chapter-N-draft-v2.md
→ my-books/<book-short-name>/files/edits/chapter-N-line-edit.md (report)
```

#### 3.3 Copy Edit
```
AGENT: EDITOR
TRIGGER: Line edit completed

INPUT DATA:
- Edited chapter in my-books/<book-short-name>/files/content/chapters/
- my-books/<book-short-name>/config/style-guide.md
- Term glossary

FOCUS:
- Grammar
- Punctuation
- Spelling
- Term consistency
- Formatting consistency

ACTIONS:
1. Grammar check
2. Check terms against glossary
3. Check names/dates/numbers
4. Unify formatting

OUTPUT DATA:
→ my-books/<book-short-name>/files/content/chapters/chapter-N-edited.md
```

### Editing Cycle

```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│    DRAFT ──▶ DEV EDIT ──▶ LINE EDIT ──▶ COPY EDIT ──▶ DONE │
│       │          │            │                              │
│       │          ▼            ▼                              │
│       │    Rewrite?      Rewrite?                           │
│       │     (WRITER)      (WRITER)                          │
│       │          │            │                              │
│       └──────────┴────────────┘                              │
│                  ▲                                           │
│                  │                                           │
│           Repeat if needed                                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Phase 3 Completion Criteria
- [ ] All chapters passed developmental edit
- [ ] All chapters passed line edit
- [ ] All chapters passed copy edit
- [ ] All corrections applied
- [ ] my-books/<book-short-name>/config/style-guide.md followed

---

## PHASE 4: Review and Finalization

### Purpose
Critical check and final approval.

### Input Data
- All edited chapters
- my-books/<book-short-name>/config/PROJECT.md (to check compliance)

#### 4.1 Individual Chapter Review
```
AGENT: CRITIC
TRIGGER: Chapter passed editing

INPUT DATA:
- Edited chapter from my-books/<book-short-name>/files/content/chapters/
- my-books/<book-short-name>/config/review-checklist.md
- Previous chapters (context) in my-books/<book-short-name>/files/content/chapters/

CHECKS:

FOR NON-FICTION:
- [ ] Main thesis clear
- [ ] Argumentation convincing
- [ ] Examples work
- [ ] Practical conclusions useful
- [ ] No factual errors

FOR FICTION:
- [ ] Characters convincing
- [ ] Scenes work
- [ ] Tension maintained
- [ ] Dialogue natural
- [ ] World consistent

OUTPUT DATA:
→ my-books/<book-short-name>/files/reviews/chapter-N-review.md

VERDICTS:
- APPROVED: Chapter ready
- NEEDS REVISION: Return for refinement
- MAJOR ISSUES: Return to WRITER
```

#### 4.2 Through Book Review
```
AGENT: CRITIC
TRIGGER: All chapters passed individual review

INPUT DATA:
- All chapters in my-books/<book-short-name>/files/content/chapters/
- my-books/<book-short-name>/config/outline.md
- my-books/<book-short-name>/config/PROJECT.md

CHECKS:

CONSISTENCY:
- [ ] No contradictions between chapters
- [ ] Names/dates/facts aligned
- [ ] Voice uniform
- [ ] Terms used correctly

STRUCTURE:
- [ ] Book matches plan
- [ ] Development/progress present
- [ ] Beginning captivating
- [ ] Ending satisfying

INTEGRITY:
- [ ] Promise to reader fulfilled
- [ ] Theme revealed
- [ ] No excess chapters
- [ ] Nothing missing

OUTPUT DATA:
→ my-books/<book-short-name>/files/reviews/book-review.md
```

#### 4.3 Final Corrections
```
AGENT: EDITOR + WRITER
TRIGGER: Book review identified issues

ACTIONS:
1. ORCHESTRATOR prioritizes issues
2. Critical issues → WRITER
3. Minor issues → EDITOR
4. Re-review → CRITIC

EXIT CRITERIA:
- CRITIC gives APPROVED for entire book
```

#### 4.4 Fact-check (Non-Fiction)
```
AGENT: RESEARCHER
TRIGGER: Before final approval

ACTIONS:
1. Extract all statements
2. Verify each
3. Mark problematic ones
4. Correct or remove

OUTPUT DATA:
→ my-books/<book-short-name>/files/research/final-factcheck.md
```

#### 4.5 Handoff to Author for Review
```
AGENT: ORCHESTRATOR
TRIGGER: CRITIC gave APPROVED for entire book

PURPOSE:
Author checks AI work before final publication

PREPARATION:
1. Gather all chapters into one readable file
2. Create summary for author:
   - What was done
   - What changes made
   - What requires attention
3. Prepare checklist for author

OUTPUT DATA:
→ my-books/<book-short-name>/files/handoff/for-author-review.md (compiled book)
→ my-books/<book-short-name>/files/handoff/author-review-checklist.md
→ my-books/<book-short-name>/files/handoff/changes-summary.md

HANDOFF TO AUTHOR:
"Book has passed all editing and review stages by AI agents.
Please check before final publication:
1. Voice sounds like yours
2. Facts accurate
3. Tone matches intent
4. No important points missed
5. Everything reads naturally

See my-books/<book-short-name>/files/handoff/author-review-checklist.md"
```

#### 4.6 Processing Author Corrections
```
AUTHOR + ORCHESTRATOR
TRIGGER: Author returned comments

ACTIONS:
1. Read author comments
2. Classify corrections:
   - Critical (change meaning)
   - Stylistic (improve voice)
   - Factual (corrections)
   - Additions (new content)

3. Distribute to agents:
   CRITICAL → WRITER (rewrite)
   STYLISTIC → EDITOR (edit)
   FACTUAL → RESEARCHER (verify) + EDITOR (correct)
   ADDITIONS → WRITER (add) + EDITOR (integrate)

4. Apply all corrections

5. Verification:
   - EDITOR checks consistency
   - CRITIC checks corrections didn't break integrity

OUTPUT DATA:
→ Updated chapters with author corrections
→ my-books/<book-short-name>/files/handoff/author-revisions-applied.md (report)

READINESS CRITERIA:
- All author comments processed
- Author approved final version
```

#### 4.7 Final Proofreading
```
AGENT: PROOFREADER
TRIGGER: Author approved final version

PURPOSE:
Last check before publication — clean all remaining errors

PASSES:

PASS 1: Spelling and Grammar
- [ ] Typos
- [ ] Grammar errors
- [ ] Punctuation
- [ ] Capitalization
- [ ] Word breaks

PASS 2: Typography
- [ ] Quotes (« » vs " ")
- [ ] Dash vs hyphen (— vs -)
- [ ] Ellipses (… vs ...)
- [ ] Non-breaking spaces
- [ ] Hanging prepositions

PASS 3: Consistency
- [ ] Names (one spelling variant)
- [ ] Dates (uniform format)
- [ ] Numbers (digits vs words)
- [ ] Terms (uniformity)
- [ ] Abbreviations (expanded at first mention)

PASS 4: Final Fact-check
- [ ] All quotes accurate
- [ ] Links work
- [ ] Statistics current
- [ ] Person names correct
- [ ] Geographic names correct

PASS 5: Pre-publication Checklist
- [ ] Table of contents current
- [ ] Page numbers correct
- [ ] Footnotes in place
- [ ] Bibliography complete
- [ ] Index (if present) correct
- [ ] Metadata (ISBN, copyright) correct

PASS 6: Author Voice
- [ ] Check my-books/<book-short-name>/config/author-voice.md
- [ ] Author features preserved
- [ ] Intentional deviations from norms NOT corrected
- [ ] Author neologisms preserved

FEATURE:
PROOFREADER uses my-books/<book-short-name>/config/author-voice.md as reference:
- Does NOT correct what is author style
- Marks questionable areas as "requires author verification"
- Distinguishes error from author feature

OUTPUT DATA:
→ my-books/<book-short-name>/files/proofread/proofreading-report.md
→ my-books/<book-short-name>/files/proofread/errors-found.md (list of corrections)
→ my-books/<book-short-name>/files/proofread/questions-for-author.md (questionable areas)
→ my-books/<book-short-name>/files/content/chapters/chapter-*-final.md (canonical proofread chapters for publication)

READINESS CRITERIA:
- All passes completed
- Critical errors corrected
- Questionable areas marked for author (if any)
- PROOFREADER gave status: READY_FOR_PUBLICATION
```

#### 4.8 Final Approval
```
AGENT: ORCHESTRATOR
TRIGGER: PROOFREADER gave READY_FOR_PUBLICATION

ACTIONS:
1. Check all Phase 4 stages completed:
   - [ ] 4.1 Individual chapter review ✓
   - [ ] 4.2 Through book review ✓
   - [ ] 4.3 Final corrections ✓
   - [ ] 4.4 Fact-check ✓
   - [ ] 4.5 Author checked ✓
   - [ ] 4.6 Author corrections applied ✓
   - [ ] 4.7 Proofreading completed ✓

2. If questions for author from proofreading:
   - Request final clarifications
   - Wait for response
   - Apply last corrections

3. Confirm canonical proofread chapters:
   - my-books/<book-short-name>/files/content/chapters/chapter-*-final.md is up to date
   - Publisher will assemble ONLY from these files

4. Create final-approval report

OUTPUT DATA:
→ my-books/<book-short-name>/files/handoff/final-approval.md

MESSAGE TO AUTHOR:
"✅ Book ready for publication!

All stages completed:
- AI editing and review
- Your review and corrections
- Final proofreading

Statistics:
- Chapters: [N]
- Words: [N]
- Errors corrected: [N]

Proceeding to Phase 5: Publication"

NEXT STEP:
→ Phase 5: Book assembly and export
```

### Phase 4 Completion Criteria (updated)
- [ ] All chapters have APPROVED status (4.1)
- [ ] Through review passed (4.2)
- [ ] Final corrections applied (4.3)
- [ ] Fact-check completed — non-fiction (4.4)
- [ ] CRITIC approved entire book (4.3)
- [ ] **Author checked and approved book (4.5-4.6)** ← NEW
- [ ] **Proofreading completed (4.7)** ← NEW
- [ ] **Final approval received (4.8)** ← NEW
- [ ] **Status: READY_FOR_PUBLICATION** ← NEW

---

## PHASE 5: Publication

### Purpose
Assemble and export ready book.

### Input Data
- All final chapters in my-books/<book-short-name>/files/content/chapters/chapter-*-final.md
- Front matter / Back matter materials in my-books/<book-short-name>/files/content/

#### Automated Gate: Final Chapter Completeness
```
AGENT: PUBLISHER (run automatically before 5.1)
TRIGGER: Phase 4 completed, before assembly starts

TOOL:
→ engine/agents/tools/validate_final_chapters.py my-books/<book-short-name>

ACTIONS:
1. Scan my-books/<book-short-name>/files/content/chapters/ for chapter-*-*.md
2. Require chapter-N-final.md for every chapter number discovered
3. If any finals are missing:
   - STOP publication
   - Create a handoff to ORCHESTRATOR with the missing chapter numbers
   - Request PROOFREADER/EDITOR to produce the missing finals

OUTPUT DATA:
→ Validation result (pass/fail) logged in publisher report
```

#### 5.1 Front Matter Assembly
```
AGENT: PUBLISHER
TRIGGER: Phase 4 completed

CREATE:
1. Title page
   - Title
   - Subtitle
   - Author name

2. Copyright page
   - © [Year] [Author]
   - ISBN (if present)
   - Publisher
   - All rights reserved

3. Dedication (if present)

4. Table of contents
   - Auto-generate from chapter headings

5. Preface/Introduction

OUTPUT DATA:
→ my-books/<book-short-name>/files/content/front-matter/*.md
```

#### 5.2 Back Matter Assembly
```
AGENT: PUBLISHER
TRIGGER: Front matter ready

CREATE:
1. Epilogue/Conclusion

2. Appendices (if present)

3. Glossary (if present)
   - Gather all terms from chapters
   - Add definitions

4. Notes
   - Gather all footnotes
   - Format

5. Bibliography
   - Gather sources from my-books/<book-short-name>/files/research/
   - Format by chosen style

6. Acknowledgments

7. About the Author

OUTPUT DATA:
→ my-books/<book-short-name>/files/content/back-matter/*.md
```

#### 5.3 Final Assembly
```
AGENT: PUBLISHER
TRIGGER: All materials ready

ACTIONS:
1. Combine all files in order:
   - Front matter
   - Main text
   - Back matter

2. Check:
   - Page order
   - Chapter numbering
   - Links and footnotes
   - Table of contents

OUTPUT DATA:
→ my-books/<book-short-name>/files/output/book-complete.md
```

#### 5.4 Export to Formats
```
AGENT: PUBLISHER
TRIGGER: Assembly completed

FORMATS:

1. DOCX (for publishers)
   - Use docx skill
   - Apply styles
   - Add metadata

2. PDF (for review/print)
   - Via pandoc or LaTeX
   - Configure margins and fonts
   - Add page numbers

3. EPUB (for e-readers)
   - Via pandoc
   - Add cover
   - Validate

OUTPUT DATA:
→ my-books/<book-short-name>/files/output/[book-name].docx
→ my-books/<book-short-name>/files/output/[book-name].pdf
→ my-books/<book-short-name>/files/output/[book-name].epub
```

#### 5.5 Final Check
```
AGENT: PUBLISHER + CRITIC
TRIGGER: Export completed

CHECKS:
- [ ] All files created
- [ ] Files open
- [ ] Formatting correct
- [ ] No conversion artifacts
- [ ] Metadata correct

OUTPUT DATA:
→ Book ready for publication
```

### Phase 5 Completion Criteria
- [ ] Front matter assembled
- [ ] Back matter assembled
- [ ] Book assembled in single file
- [ ] Export to needed formats
- [ ] Final check passed
- [ ] Files delivered to user

---

## Automation

### Commands to Launch Workflow

```bash
# Complete cycle from scratch
claude "Launch complete book writing workflow. Start with Phase 1."

# Specific phase
claude "Launch Phase 2: Writing drafts."

# Specific chapter
claude "Write chapter 3 draft according to workflow."

# Status check
claude "Show current workflow status."

# Continue
claude "Continue workflow from where we stopped."

# Generate sample book (based on my-books/<book-short-name>/config/author-voice.md)
claude "Generate sample fiction book based on my-books/<book-short-name>/config/author-voice.md"
claude "Generate sample non-fiction book based on my-books/<book-short-name>/config/author-voice.md"
```

### Sample Book Generation (author voice demonstration)

#### Purpose

Sample books — are example chapters written in author's voice for:
- **Demonstration** — show author how book will sound
- **Validation** — verify correct voice extraction
- **Training** — examples for WRITER agent
- **Testing** — ensure my-books/<book-short-name>/config/author-voice.md works

#### Generation Conditions

```
REQUIREMENTS:
1. my-books/<book-short-name>/config/author-voice.md filled (≠ template)
2. Minimum 2-3 reference text samples
3. At least one voice section updated with real examples

IF NOT MET:
→ Tell author: "my-books/<book-short-name>/config/author-voice.md not yet filled with real examples"
→ Suggest first importing existing texts (Phase 0)
   OR
→ Write several paragraphs manually for voice extraction
```

#### Generation Process

```
COMMAND:
claude "Generate sample fiction book based on my-books/<book-short-name>/config/author-voice.md"
  OR
claude "Generate sample non-fiction book based on my-books/<book-short-name>/config/author-voice.md"

STEP 1: Validation
AGENT: ORCHESTRATOR
ACTIONS:
- Check that my-books/<book-short-name>/config/author-voice.md is filled
- Check presence of text samples
- Determine book type for sample

STEP 2: Structure Creation
AGENT: ORCHESTRATOR
ACTIONS:
- Create directory my-books/sample-[type]-book/
- Copy templates to my-books/sample-[type]-book/config/ from engine/book-templates/ (PROJECT, outline/plot, style-guide, author-voice snapshot)
- Create minimal structure under my-books/sample-[type]-book/files/ (content/, research/)

STEP 3: Chapter Generation
AGENT: WRITER
INPUT DATA:
- my-books/<book-short-name>/config/author-voice.md (complete voice analysis)
- Reference text samples from my-books/<book-short-name>/config/author-voice.md

ACTIONS:
1. Deeply study my-books/<book-short-name>/config/author-voice.md:
   - Tone and mood
   - Lexical features
   - Syntactic patterns
   - Rhythm and pace
   - Characteristic phrases
   - Stylistic devices

2. Write 3 example chapters (1000-1500 words each):
   - Chapter 1: Introduction/setup
   - Chapter 2: Development
   - Chapter 3: Turn/climax (for fiction)
            or Key concept (for non-fiction)

3. STRICTLY follow author voice:
   - Use characteristic words from list
   - Imitate sentence length
   - Apply author's stylistic devices
   - Reproduce rhythm from samples

OUTPUT DATA:
→ my-books/sample-[type]-book/files/content/chapters/chapter-1-sample.md
→ my-books/sample-[type]-book/files/content/chapters/chapter-2-sample.md
→ my-books/sample-[type]-book/files/content/chapters/chapter-3-sample.md

STEP 4: Voice Validation
AGENT: EDITOR
ACTIONS:
- Read generated chapters
- Compare with samples from my-books/<book-short-name>/config/author-voice.md
- Check compliance:
  * Tone ✓
  * Sentence length ✓
  * Characteristic phrases ✓
  * Rhythm ✓
  * Stylistic devices ✓

IF DOESN'T MATCH:
→ WRITER rewrites, strengthening characteristic features

STEP 5: Handoff to Author
AGENT: ORCHESTRATOR
ACTIONS:
- Create report for author
- Indicate what to check

OUTPUT DATA:
→ my-books/sample-[type]-book/REVIEW-CHECKLIST.md

MESSAGE TO AUTHOR:
"📚 Sample book generated in my-books/sample-[type]-book/

Check:
1. Does this sound like your voice?
2. Is sentence length typical for you?
3. Does tone match your style?
4. Are speech patterns recognizable?
5. Is rhythm natural for you?

If NO → indicate what's wrong, and we'll update my-books/<book-short-name>/config/author-voice.md
If YES → my-books/<book-short-name>/config/author-voice.md is valid, can start project"
```

#### Sample Update

```
COMMAND:
claude "Update sample [fiction/non-fiction] book — my-books/<book-short-name>/config/author-voice.md changed"

PROCESS:
1. Delete old chapters
2. Regenerate with updated my-books/<book-short-name>/config/author-voice.md
3. Show diff to author: what changed in voice
```

#### Sample Usage

**For Author**:
- Voice validation before starting project
- Correction of my-books/<book-short-name>/config/author-voice.md if voice inaccurate
- Confidence that AI understood style

**For Agents**:
- WRITER uses as reference when writing
- EDITOR cross-checks during editing
- PROOFREADER verifies voice preservation

**Storage**:
```
my-books/
├── sample-fiction-book/         # Fiction example
│   ├── README.md
│   ├── config/
│   │   ├── PROJECT.md
│   │   ├── outline.md
│   │   ├── characters.md
│   │   ├── world.md
│   │   ├── plot.md
│   │   ├── style-guide.md
│   │   └── author-voice-snapshot.md
│   └── files/
│       ├── content/chapters/
│       │   ├── chapter-1-sample.md
│       │   ├── chapter-2-sample.md
│       │   └── chapter-3-sample.md
│       └── research/
│
└── sample-non-fiction-book/     # Non-fiction example
    ├── README.md
    ├── config/
    │   ├── PROJECT.md
    │   ├── outline.md
    │   ├── bibliography.md
    │   ├── style-guide.md
    │   └── author-voice-snapshot.md
    └── files/
        ├── content/chapters/
        │   ├── chapter-1-sample.md
        │   ├── chapter-2-sample.md
        │   └── chapter-3-sample.md
        └── research/
            └── chapter-1-research.md
```

### Automatic Phase Transitions

```
PHASE 0 → PHASE 1 (or 2, or 3):
  Condition: import-report.md created + conflicts resolved
  Phase choice: depends on imported materials status

PHASE 1 → PHASE 2:
  Condition: my-books/<book-short-name>/config/PROJECT.md valid + my-books/<book-short-name>/config/outline.md approved

PHASE 2 → PHASE 3:
  Condition: All chapters have "draft" status

PHASE 3 → PHASE 4:
  Condition: All chapters have "edited" status

PHASE 4.1-4.4 → PHASE 4.5:
  Condition: CRITIC gave APPROVED for entire book + fact-check completed

PHASE 4.5 → PHASE 4.6:
  Condition: Author returned comments/approval

PHASE 4.6 → PHASE 4.7:
  Condition: Author corrections applied + author approved final version

PHASE 4.7 → PHASE 4.8:
  Condition: PROOFREADER gave READY_FOR_PUBLICATION

PHASE 4 → PHASE 5:
  Condition: Final approval (4.8) received

PHASE 5 → DONE:
  Condition: All exported files checked
```

### Error Handling

```
IF agent cannot complete task:
1. Record problem in handoff/errors.md
2. Notify ORCHESTRATOR
3. ORCHESTRATOR decides:
   - Retry with different parameters
   - Escalate to user
   - Skip and continue

IF user input needed:
1. ORCHESTRATOR formulates question
2. Save state
3. Wait for answer
4. Continue with answer
```

---

## Metrics and Reporting

### Automatic Reports

```markdown
# Daily Report

**Date**: [date]
**Phase**: [current phase]

## Completed Today
- [List of completed tasks]

## In Progress
- [List of current tasks]

## Blockers
- [List of issues]

## Statistics
- Words written: [N]
- Chapters completed: [N/total]
- Progress: [X%]

## Plan for Tomorrow
- [Next tasks]
```

### Final Report

```markdown
# Book Completion Report

**Title**: [title]
**Completed**: [date]

## Statistics
- Total words: [N]
- Chapters: [N]
- Work days: [N]
- Editing iterations: [N]

## Agents
| Agent | Tasks | Words |
|-------|-------|------|
| WRITER | [N] | [N] |
| EDITOR | [N] | - |
| RESEARCHER | [N] | - |
| CRITIC | [N] | - |

## Files
- Source: my-books/<book-short-name>/files/output/book.md
- DOCX: my-books/<book-short-name>/files/output/book.docx
- PDF: my-books/<book-short-name>/files/output/book.pdf

## Notes
[Project features, lessons]
```

---

## Project Launch Checklist

Before launching workflow ensure:

- [ ] my-books/<book-short-name>/config/PROJECT.md completely filled
- [ ] Book type selected (fiction/non-fiction)
- [ ] Approximate volume determined
- [ ] Key themes/ideas formulated
- [ ] my-books/<book-short-name>/config/style-guide.md configured for project
- [ ] Project directory created in my-books/<book-short-name>/
- [ ] Agents understand task

After this launch:

```bash
claude "Initialize book project and start workflow."
```
