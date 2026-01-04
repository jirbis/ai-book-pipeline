# Claude Improvements Suggestions

**Date**: 2026-01-04
**Based on**: Workflow violation analysis for sample-non-fiction-book
**Context**: Phase 2.1 (Research) was skipped during chapter writing, leading to workflow compliance issues

---

## Executive Summary

**Critical Issue Found**: External coding agents (codex, copilot) can violate WORKFLOW.md requirements because:
1. No automated validation/enforcement of phase transitions
2. No mandatory checklists that agents must complete
3. No blocking mechanisms for incomplete phases
4. Missing tooling for workflow health monitoring

**Impact**: Research phase (2.1) was completely skipped for chapters 0-3, violating non-fiction workflow requirements.

---

## Improvement Roadmap by Priority

### 🔴 Critical (P0) - Must have for workflow integrity

**Group A: Phase Validation & Gates**
- Prevents agents from skipping required workflow steps
- Blocks invalid phase transitions
- Ensures completeness before handoffs

**Group B: Research Validation for Non-Fiction**
- Enforces research requirements before writing
- Validates research quality and completeness
- Prevents fact-checking failures in Phase 4

---

### 🟠 High Priority (P1) - Significantly improves workflow compliance

**Group C: Agent Contracts & Checklists**
- Provides clear, enforceable requirements for each agent
- Makes workflow steps explicit and verifiable
- Improves handoff quality between agents

**Group D: User Tooling & Visibility**
- Enables users to monitor workflow health
- Provides actionable remediation steps
- Improves external agent integration

---

### 🟡 Medium Priority (P2) - Enhances workflow efficiency

**Group E: Automation & Orchestration**
- Reduces manual validation overhead
- Automates phase transition management
- Improves overall workflow efficiency

**Group F: Documentation & Training**
- Improves onboarding for new users
- Clarifies workflow requirements
- Provides examples and templates

---

### 🟢 Low Priority (P3) - Nice to have

**Group G: Advanced Features**
- Analytics and reporting
- Workflow optimization suggestions
- Integration with external tools

---

## Detailed Feature Groups

---

## 🔴 Group A: Phase Validation & Gates [CRITICAL - P0]

**Objective**: Prevent workflow violations through automated validation

### A.1 Phase Validators [P0 - Critical]

**Task**: Create validation scripts for each phase transition

**Implementation**:
```
engine/agents/tools/
├── validate_phase_0.py   # Import completion check
├── validate_phase_1.py   # Init & outline check
├── validate_phase_2.py   # Draft & research check ⭐ CRITICAL
├── validate_phase_3.py   # Edit completion check
├── validate_phase_4.py   # Review & approval check
└── validate_phase_5.py   # Publication readiness check
```

**Requirements for validate_phase_2.py**:
- ✅ Check all chapters have research files (non-fiction only)
- ✅ Validate research files are not templates (minimum word count, source count)
- ✅ Check all drafts exist and match outline
- ✅ Verify handoff logs exist (researcher → writer)
- ✅ Validate required directories created (edits/, reviews/, proofread/)
- ✅ Check progress.md accuracy
- ⛔ BLOCK Phase 3 if any critical check fails

**Exit codes**:
- 0: Validation passed, can proceed
- 1: Critical errors found, MUST fix before proceeding
- 2: Warnings found, can proceed but review needed

**Effort**: 2-3 days
**Dependency**: None
**Blocks**: A.2, C.1

---

### A.2 Phase Transition Enforcer [P0 - Critical]

**Task**: Automatically run validators when agents attempt phase transitions

**Implementation**:
```python
# engine/agents/tools/phase_enforcer.py

def enforce_phase_transition(book_path, from_phase, to_phase):
    """
    Enforces phase transition rules.
    Raises PhaseTransitionBlocked if validation fails.
    """
    validator = f"validate_phase_{from_phase}.py"
    result = subprocess.run([validator, book_path])

    if result.returncode != 0:
        raise PhaseTransitionBlocked(
            f"Cannot transition Phase {from_phase} → {to_phase}\n"
            f"Validation failed. See errors above."
        )

    # Update phase tracking
    update_phase_status(book_path, to_phase)
    create_phase_completion_report(book_path, from_phase)
```

**Integration points**:
- WORKFLOW.md: Add validation requirement before each phase
- AGENTS.md: Update each agent to check phase validity
- CLI: Add automatic validation to `start-phase` command

**Effort**: 1-2 days
**Dependency**: A.1
**Blocks**: E.1

---

### A.3 Phase Status Tracking [P0 - Critical]

**Task**: Create machine-readable phase status file

**Implementation**:
```yaml
# my-books/BOOK/config/phase-status.yml

current_phase: 2
last_validated: 2026-01-04T10:30:00Z

phase_history:
  - phase: 0
    started: 2026-01-04T08:00:00Z
    completed: 2026-01-04T09:00:00Z
    validation: PASSED

  - phase: 1
    started: 2026-01-04T09:00:00Z
    completed: 2026-01-04T09:30:00Z
    validation: PASSED

  - phase: 2
    started: 2026-01-04T09:30:00Z
    completed: null
    validation: FAILED
    blockers:
      critical:
        - "Missing research files for chapters: [0, 2, 3]"
        - "Missing directories: [edits, reviews]"
      warnings:
        - "Handoff logs incomplete"

phase_2_checklist:
  research_complete: 4/19      # 4 chapters have research
  drafts_written: 4/19         # 4 chapters drafted
  handoff_logs_created: 0/19   # No handoff logs
  progress_tracking: true      # progress.md updated
  directories_created: false   # Missing edits/, reviews/

can_transition_to_phase_3: false
validation_command: "python engine/agents/tools/validate_phase_2.py my-books/sample-non-fiction-book/"
```

**CLI Integration**:
```bash
python -m engine.cli phase-status my-book
# Output: Shows current phase, blockers, next steps
```

**Effort**: 1 day
**Dependency**: A.1
**Blocks**: D.1, E.2

---

## 🔴 Group B: Research Validation for Non-Fiction [CRITICAL - P0]

**Objective**: Ensure research quality before writing (non-fiction only)

### B.1 Research File Validator [P0 - Critical]

**Task**: Validate research file completeness and quality

**Implementation**:
```python
# engine/agents/tools/validate_research.py

def validate_research_file(research_file_path):
    """
    Validates a single research file meets minimum standards.
    Returns (is_valid, errors, warnings, stats)
    """
    errors = []
    warnings = []

    # CRITICAL: File must exist and not be template
    if not exists(research_file_path):
        errors.append("❌ Research file does not exist")
        return (False, errors, warnings, None)

    content = read_file(research_file_path)

    # CRITICAL: Minimum word count
    word_count = count_words(content)
    if word_count < 300:
        errors.append(f"❌ Research too short: {word_count} words (min: 300)")

    # CRITICAL: Must have sources
    sources = extract_sources(content)
    if len(sources) < 3:
        errors.append(f"❌ Insufficient sources: {len(sources)} (min: 3)")

    # CRITICAL: Must not be template
    if is_template_content(content):
        errors.append("❌ Research file is still template (not filled with real data)")

    # WARNING: Check for URLs
    urls = extract_urls(content)
    if len(urls) < 2:
        warnings.append(f"⚠️ Few URLs found: {len(urls)} (recommended: 3+)")

    # WARNING: Check for quotes
    quotes = extract_quotes(content)
    if len(quotes) == 0:
        warnings.append("⚠️ No quotes found (recommended: 1+ per source)")

    stats = {
        'word_count': word_count,
        'source_count': len(sources),
        'url_count': len(urls),
        'quote_count': len(quotes)
    }

    is_valid = len(errors) == 0
    return (is_valid, errors, warnings, stats)
```

**CLI Integration**:
```bash
python engine/agents/tools/validate_research.py \
       my-books/my-book/files/research/chapter-1-research.md

# Output:
✅ Research validation PASSED

Statistics:
- Word count: 542
- Sources: 4
- URLs: 5
- Quotes: 3

⚠️ Warnings:
- Consider adding more concrete examples
```

**Effort**: 2 days
**Dependency**: None
**Blocks**: A.1 (uses this in phase validation)

---

### B.2 Research Template Generator [P1 - High]

**Task**: Generate research file templates with chapter-specific questions

**Implementation**:
```python
# engine/agents/tools/generate_research_template.py

def generate_research_template(book_path, chapter_num):
    """
    Generates a research template pre-filled with questions
    from the outline for the specified chapter.
    """
    outline = read_outline(f"{book_path}/config/outline.md")
    chapter = outline.chapters[chapter_num]

    template = f"""# Research Notes — {chapter.title}

**Chapter number**: {chapter_num}
**Key thesis**: {chapter.thesis}
**Target word count**: {chapter.target_words}

---

## Research Questions

Based on outline, research these key questions:

"""

    # Extract questions from outline
    for i, question in enumerate(chapter.research_questions, 1):
        template += f"{i}. {question}\n"

    template += """

---

## Sources

| # | Title | Author | URL | Type | Relevance | Key Quote |
|---|-------|--------|-----|------|-----------|-----------|
| 1 | | | | article/book/study | ⭐⭐⭐⭐ | |
| 2 | | | | | | |
| 3 | | | | | | |

---

## Key Findings

### Finding 1: [Title]
- **Source**: [Source #N]
- **Fact**: [Specific fact, stat, or quote]
- **Relevance**: [Why this matters for the chapter]

### Finding 2: [Title]
- **Source**: [Source #N]
- **Fact**:
- **Relevance**:

### Finding 3: [Title]
- **Source**: [Source #N]
- **Fact**:
- **Relevance**:

---

## Examples & Case Studies

1. **Example 1**: [Title]
   - Description:
   - Source:
   - Relevance:

2. **Example 2**: [Title]
   - Description:
   - Source:
   - Relevance:

---

## Bibliography

1. [Author]. ([Year]). _[Title]_. [URL]
2.
3.

---

## Research Status

- [ ] All research questions answered
- [ ] Minimum 3 sources found
- [ ] Sources verified and URLs recorded
- [ ] Key findings extracted (3+)
- [ ] Examples/case studies found (2+)
- [ ] Ready for handoff to WRITER

**Researcher**: [Name]
**Date completed**: [YYYY-MM-DD]
"""

    output_path = f"{book_path}/files/research/chapter-{chapter_num}-research.md"
    write_file(output_path, template)
    return output_path
```

**CLI Integration**:
```bash
python -m engine.cli generate-research my-book --chapter 4

# Output:
✅ Created: my-books/my-book/files/research/chapter-4-research.md
📋 Template pre-filled with 6 research questions from outline
🎯 Next: Fill template with research findings
```

**Effort**: 1 day
**Dependency**: None
**Blocks**: None

---

### B.3 Research Checklist in WORKFLOW.md [P0 - Critical]

**Task**: Add mandatory, explicit checklists to WORKFLOW.md Phase 2.1

**Changes to**: `engine/agents/WORKFLOW.md`

**Before**:
```markdown
#### 2.1 Chapter Research (Non-Fiction)
AGENT: RESEARCHER
ACTIONS:
1. Determine key chapter questions
2. Conduct web search
...
```

**After**:
```markdown
#### 2.1 Chapter Research (Non-Fiction)

**⚠️ MANDATORY FOR NON-FICTION - CANNOT SKIP**

**AGENT**: RESEARCHER
**INPUT**: outline.md (chapter section)
**OUTPUT**: research/chapter-N-research.md + handoff log

---

**🔴 MANDATORY CHECKLIST (All items must be completed)**:

```bash
# STEP 1: Prepare research file
[ ] Read outline.md chapter section
[ ] Extract research questions from outline
[ ] Run: python -m engine.cli generate-research BOOK --chapter N
[ ] Verify template created: files/research/chapter-N-research.md

# STEP 2: Conduct research
[ ] Research minimum 3 authoritative sources per key question
[ ] Record each source: title, author, URL, publication date
[ ] Extract key facts, statistics, quotes from each source
[ ] Find 2+ concrete examples or case studies
[ ] Save all URLs for bibliography

# STEP 3: Fill research file
[ ] Complete "Sources" table (min 3 entries)
[ ] Complete "Key Findings" (min 3 findings)
[ ] Complete "Examples & Case Studies" (min 2 examples)
[ ] Complete "Bibliography" section
[ ] Check all research questions answered

# STEP 4: Validate research
[ ] Run: python engine/agents/tools/validate_research.py \
         my-books/BOOK/files/research/chapter-N-research.md
[ ] If validation FAILS → fix issues and re-validate
[ ] If validation PASSES → proceed to handoff

# STEP 5: Create handoff to WRITER
[ ] Create handoff/researcher-to-writer-ch-N.md with:
    - Research completion confirmation
    - Source count
    - Key findings summary (3-5 bullet points)
    - Status: READY_FOR_DRAFTING
[ ] Update progress.md: chapter-N status = "research_complete"

# STEP 6: Verification
[ ] All checkboxes above marked ✅
[ ] Research file ≥ 300 words
[ ] Minimum 3 sources with URLs
[ ] Handoff log created
```

---

**🛑 BLOCKING RULE**:

WRITER agent **MUST NOT** start writing chapter N until:
1. ✅ research/chapter-N-research.md exists and validated
2. ✅ handoff/researcher-to-writer-ch-N.md created
3. ✅ progress.md shows chapter-N status = "research_complete"

**Validation command**:
```bash
python engine/agents/tools/validate_research.py \
       my-books/BOOK/files/research/chapter-N-research.md
```

If exit code ≠ 0 → research incomplete, CANNOT proceed to writing.

---

**OUTPUT FILES (all must exist)**:
```
files/research/chapter-N-research.md     (≥ 300 words, ≥ 3 sources)
files/handoff/researcher-to-writer-ch-N.md
config/progress.md                       (updated with research_complete)
```
```

**Effort**: 2 hours
**Dependency**: B.1, B.2
**Blocks**: None (documentation)

---

## 🟠 Group C: Agent Contracts & Checklists [HIGH - P1]

**Objective**: Define explicit, verifiable requirements for each agent

### C.1 RESEARCHER Agent Contract [P1 - High]

**Task**: Create formal contract defining RESEARCHER responsibilities

**Implementation**:
```markdown
# engine/agents/contracts/RESEARCHER.md

## RESEARCHER Agent Contract v1.0

### Role
Gather, verify, and document factual information for non-fiction chapters.

### Activation Triggers
- ORCHESTRATOR assigns chapter for research (non-fiction books only)
- Previous phase: Outline approved for chapter
- Book type: `non-fiction` in PROJECT.md

### Pre-conditions (must verify before starting)
- [ ] my-books/BOOK/config/outline.md exists and contains chapter section
- [ ] my-books/BOOK/config/PROJECT.md has type = "non-fiction"
- [ ] my-books/BOOK/files/research/ directory exists
- [ ] Chapter not already researched (check progress.md)

### Mandatory Outputs (ALL must be created)

#### 1. Research file: `files/research/chapter-N-research.md`
**Minimum requirements**:
- ≥ 300 words total content
- ≥ 3 sources with full citations (title, author, URL, date)
- ≥ 3 key findings extracted from sources
- ≥ 2 concrete examples or case studies
- All research questions from outline answered
- Bibliography section completed

**Quality standards**:
- Sources must be authoritative (no Wikipedia as primary source)
- URLs must be working (checked at time of research)
- Quotes must be exact with proper attribution
- Facts must be verifiable from provided sources

#### 2. Handoff log: `files/handoff/researcher-to-writer-ch-N.md`
**Required content**:
```markdown
# Research → Writing Handoff (Chapter N)

**Chapter**: [Title]
**Research completed**: [YYYY-MM-DD HH:MM]
**Researcher**: [Agent name/version]

## Research Summary

**Sources found**: [N]
**Total words**: [N]
**Research questions answered**: [N/N]

## Key Findings
1. [Finding 1 - one sentence]
2. [Finding 2 - one sentence]
3. [Finding 3 - one sentence]

## Ready for Drafting
- [x] All research questions answered
- [x] Minimum 3 sources documented
- [x] Examples and case studies found
- [x] Bibliography complete

**Status**: READY_FOR_DRAFTING
**Next agent**: WRITER
```

#### 3. Progress update: `config/progress.md`
**Required changes**:
```markdown
| N | [Chapter Title] | [target] | 0 | 0% | ✅ research_complete | [DATE] |
```

### Validation Gate (MUST PASS)

Before marking task complete, RESEARCHER must:
```bash
# Validate research file
python engine/agents/tools/validate_research.py \
       my-books/BOOK/files/research/chapter-N-research.md

# Exit code must be 0 (validation passed)
```

If validation fails:
1. ❌ DO NOT create handoff log
2. ❌ DO NOT update progress.md
3. ❌ DO NOT mark task complete
4. ✅ Fix validation errors
5. ✅ Re-run validation
6. ✅ Repeat until validation passes

### Handoff Protocol

**After validation passes**:
1. Create handoff log (see template above)
2. Update progress.md with "research_complete" status
3. Notify ORCHESTRATOR: "Chapter N research complete, ready for WRITER"
4. ORCHESTRATOR validates handoff files exist
5. ORCHESTRATOR assigns chapter N to WRITER

### Error Handling

**If sources cannot be found**:
- Document issue in handoff log
- Mark status as "research_blocked"
- Escalate to ORCHESTRATOR with specific questions
- Wait for user guidance (acceptable alternative sources, scope changes, etc.)

**If research questions unclear**:
- Escalate to ORCHESTRATOR
- Request outline clarification
- Do NOT proceed with incomplete research

### Performance Metrics

**Target benchmarks**:
- Research time per chapter: 30-60 minutes
- Source quality: ≥ 80% authoritative sources
- Validation pass rate: 100% (after fixes)

### Dependencies

**Requires**:
- outline.md (chapter section with research questions)
- PROJECT.md (book metadata)
- Research directory structure

**Provides to**:
- WRITER: Factual foundation for drafting
- EDITOR: Source verification during editing
- PROOFREADER: Fact-checking references

### Contract Compliance

**This contract is enforced by**:
- validate_research.py (automated validation)
- validate_phase_2.py (phase transition blocker)
- ORCHESTRATOR handoff checks

**Non-compliance consequences**:
- Phase 2 validation fails
- Cannot transition to Phase 3
- WRITER cannot start drafting
```

**Effort**: 3 hours
**Dependency**: A.1, B.1
**Blocks**: C.2, C.3

---

### C.2 WRITER Agent Contract [P1 - High]

**Task**: Create formal contract for WRITER agent

**File**: `engine/agents/contracts/WRITER.md`

**Key sections**:
- Pre-conditions: Research complete, outline exists, style guide available
- Mandatory inputs: research file, outline section, previous chapter (for continuity)
- Mandatory outputs: chapter-N-draft-v1.md, handoff to EDITOR
- Validation: Word count within 80-120% of target, all outline sections covered
- Handoff protocol: Create writer-to-editor-ch-N.md

**Effort**: 3 hours
**Dependency**: C.1
**Blocks**: None

---

### C.3 ORCHESTRATOR Agent Contract [P1 - High]

**Task**: Create formal contract for ORCHESTRATOR coordination role

**File**: `engine/agents/contracts/ORCHESTRATOR.md`

**Key responsibilities**:
- Validate phase transitions (run validation scripts)
- Verify handoff logs exist before assigning next agent
- Maintain phase-status.yml accuracy
- Escalate blockers to user
- Coordinate multi-agent workflows

**Effort**: 3 hours
**Dependency**: C.1, C.2
**Blocks**: E.1

---

## 🟠 Group D: User Tooling & Visibility [HIGH - P1]

**Objective**: Enable users to monitor and fix workflow issues

### D.1 Workflow Health Dashboard [P1 - High]

**Task**: Create CLI command to show workflow health

**Implementation**:
```python
# engine/cli.py - add command

def cmd_health(book_name):
    """Show workflow health and blockers for a book"""

    book_path = f"my-books/{book_name}"

    # Load phase status
    phase_status = load_yaml(f"{book_path}/config/phase-status.yml")
    current_phase = phase_status['current_phase']

    # Run validation for current phase
    validator = f"engine/agents/tools/validate_phase_{current_phase}.py"
    result = subprocess.run([validator, book_path], capture_output=True)

    # Parse validation output
    errors = parse_errors(result.stderr)
    warnings = parse_warnings(result.stdout)

    # Display health dashboard
    print(f"📊 Book Workflow Health: {book_name}\n")
    print(f"Phase {current_phase} ({PHASE_NAMES[current_phase]}) - ", end="")

    if result.returncode == 0:
        print("✅ HEALTHY\n")
    else:
        print("⚠️ ISSUES FOUND\n")

    # Show detailed status
    show_research_coverage(book_path)
    show_draft_coverage(book_path)
    show_handoff_status(book_path)
    show_directory_structure(book_path)

    # Show blockers
    if errors:
        print("\n⚠️ BLOCKERS (must fix before next phase):")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")

        print("\n📌 Recommended action:")
        print(f"   python -m engine.cli fix-blockers {book_name} --phase {current_phase}")

    # Show warnings
    if warnings:
        print("\n💡 WARNINGS (can proceed but review needed):")
        for i, warning in enumerate(warnings, 1):
            print(f"  {i}. {warning}")
```

**Example output**:
```bash
$ python -m engine.cli health sample-non-fiction-book

📊 Book Workflow Health: sample-non-fiction-book

Phase 2 (Writing Drafts) - ⚠️ ISSUES FOUND

Research Coverage (non-fiction):
  ✅ Chapter 1: research complete (4 sources, 542 words)
  ❌ Chapter 0: MISSING research file
  ❌ Chapter 2: MISSING research file
  ❌ Chapter 3: MISSING research file
  ⬜ Chapters 4-18: not started

Draft Coverage:
  ✅ Chapters 0-3: drafts complete (9,122 words / 13,000 target)
  ⬜ Chapters 4-18: not started (0 / 57,000 target)

Handoff Logs:
  ❌ MISSING: researcher-to-writer logs (0/4 expected)
  ⬜ writer-to-editor: not yet required

Directory Structure:
  ✅ content/chapters/
  ✅ research/
  ✅ handoff/
  ❌ MISSING: edits/
  ❌ MISSING: reviews/
  ❌ MISSING: proofread/

⚠️ BLOCKERS (must fix before Phase 3):
  1. Create research files for chapters: 0, 2, 3
  2. Create handoff logs (researcher→writer) for chapters: 0, 1, 2, 3
  3. Create missing directories: edits/, reviews/, proofread/

📌 Recommended action:
   python -m engine.cli fix-blockers sample-non-fiction-book --phase 2
```

**Effort**: 2 days
**Dependency**: A.1, A.3
**Blocks**: D.2

---

### D.2 Fix Blockers Tool [P1 - High]

**Task**: Automated tool to fix common workflow blockers

**Implementation**:
```python
# engine/cli.py - add command

def cmd_fix_blockers(book_name, phase=None):
    """Interactively fix workflow blockers"""

    # Run validation to identify blockers
    blockers = get_blockers(book_name, phase)

    print(f"🔧 Fix Blockers Wizard: {book_name}\n")
    print(f"Found {len(blockers)} blockers to fix\n")

    for i, blocker in enumerate(blockers, 1):
        print(f"\n[{i}/{len(blockers)}] {blocker.description}")
        print(f"Type: {blocker.type}")
        print(f"Severity: {blocker.severity}")

        if blocker.type == "missing_research":
            fix_missing_research(blocker)
        elif blocker.type == "missing_handoff":
            fix_missing_handoff(blocker)
        elif blocker.type == "missing_directory":
            fix_missing_directory(blocker)
        else:
            print(f"Manual fix required:")
            print(f"  {blocker.fix_instructions}")

    # Re-validate
    print("\n♻️ Re-validating...")
    result = validate_phase(book_name, phase)

    if result.returncode == 0:
        print("✅ All blockers fixed! Phase validation PASSED")
    else:
        print("⚠️ Some blockers remain. Review output above.")

def fix_missing_research(blocker):
    """Generate research template for missing research file"""
    chapter = blocker.chapter
    book = blocker.book

    print(f"\n🔬 Generating research template for chapter {chapter}...")

    template_path = generate_research_template(book, chapter)

    print(f"✅ Created: {template_path}")
    print(f"\n⚠️ NEXT STEPS:")
    print(f"   1. Fill template with actual research")
    print(f"   2. Validate: python engine/agents/tools/validate_research.py {template_path}")
    print(f"   3. Create handoff log")

    return template_path
```

**Example usage**:
```bash
$ python -m engine.cli fix-blockers sample-non-fiction-book --phase 2

🔧 Fix Blockers Wizard: sample-non-fiction-book

Found 3 blockers to fix

[1/3] Missing research file for chapter 0
Type: missing_research
Severity: CRITICAL

🔬 Generating research template for chapter 0...
✅ Created: my-books/sample-non-fiction-book/files/research/chapter-0-research.md

⚠️ NEXT STEPS:
   1. Fill template with actual research
   2. Validate: python engine/agents/tools/validate_research.py [path]
   3. Create handoff log

[2/3] Missing directory: edits/
Type: missing_directory
Severity: HIGH

📁 Creating directory...
✅ Created: my-books/sample-non-fiction-book/files/edits/

[3/3] Missing handoff log: researcher-to-writer-ch-0.md
Type: missing_handoff
Severity: HIGH

📝 Generate handoff template? [y/N]: y
✅ Created: my-books/sample-non-fiction-book/files/handoff/researcher-to-writer-ch-0.md

⚠️ Template created - you must fill with actual handoff data

♻️ Re-validating...
⚠️ Some blockers remain. Review output above.

Manual steps required:
1. Fill research templates with actual research data
2. Complete handoff logs with real handoff information
3. Re-run: python -m engine.cli health sample-non-fiction-book
```

**Effort**: 2 days
**Dependency**: D.1, B.2
**Blocks**: None

---

### D.3 Agent Instructions Generator [P1 - High]

**Task**: Generate instructions for external coding agents

**Implementation**:
```python
# engine/cli.py - add command

def cmd_agent_instructions(book_name, phase, chapter=None):
    """Generate instructions for external coding agents (codex, copilot)"""

    book_path = f"my-books/{book_name}"
    project = load_project(f"{book_path}/config/PROJECT.md")

    instructions = f"""# Agent Instructions — {book_name}

**Generated**: {datetime.now()}
**Phase**: {phase} ({PHASE_NAMES[phase]})
**Book Type**: {project.type}
**Chapter**: {chapter if chapter else 'All'}

---

## CRITICAL REQUIREMENTS

⚠️ **You MUST follow these requirements exactly** ⚠️

"""

    if project.type == "non-fiction" and phase == 2:
        instructions += """
### Phase 2 (Writing Drafts) for NON-FICTION

**WORKFLOW RULE**: Research BEFORE Writing

For each chapter, you MUST:

1. **RESEARCH FIRST** (RESEARCHER agent role):
   ```bash
   # Generate research template
   python -m engine.cli generate-research {book} --chapter {N}

   # Fill template with:
   # - Minimum 3 authoritative sources with URLs
   # - Key facts, statistics, quotes
   # - Concrete examples/case studies

   # Validate research
   python engine/agents/tools/validate_research.py \\
          my-books/{book}/files/research/chapter-{N}-research.md

   # If validation FAILS → fix and re-validate
   # If validation PASSES → proceed to step 2
   ```

2. **CREATE HANDOFF** (RESEARCHER → WRITER):
   ```bash
   # Create handoff log
   cat > my-books/{book}/files/handoff/researcher-to-writer-ch-{N}.md << EOF
   # Research → Writing Handoff (Chapter {N})

   Research completed: $(date)
   Sources found: [COUNT]
   Key findings:
   - [FINDING 1]
   - [FINDING 2]
   - [FINDING 3]

   Ready for drafting: YES
   EOF
   ```

3. **WRITE DRAFT** (WRITER agent role):
   ```bash
   # Now write chapter using research
   # Input files:
   # - config/outline.md (chapter plan)
   # - files/research/chapter-{N}-research.md (facts)
   # - config/style-guide.md (tone)

   # Output:
   # - files/content/chapters/chapter-{N}-draft-v1.md
   ```

4. **UPDATE PROGRESS** (ORCHESTRATOR role):
   ```bash
   # Update config/progress.md:
   # - chapter-{N}: status = draft, words = [COUNT], updated = [DATE]
   ```

5. **VALIDATE CHAPTER**:
   ```bash
   python engine/agents/tools/validate_chapter.py \\
          my-books/{book}/ --chapter {N} --phase 2

   # Exit code must be 0 before marking complete
   ```

---

## VALIDATION COMMANDS

Before marking work complete, run:

```bash
# Validate current chapter
python engine/agents/tools/validate_chapter.py \\
       my-books/{book}/ --chapter {chapter} --phase {phase}

# Validate overall phase status
python -m engine.cli health {book}
```

---

## DO NOT SKIP

❌ **DO NOT** write chapters without research (non-fiction)
❌ **DO NOT** use template research files as-is
❌ **DO NOT** skip handoff logs
❌ **DO NOT** skip progress.md updates

✅ **DO** follow workflow steps in order
✅ **DO** validate before marking complete
✅ **DO** create all required files

---

## Questions?

Read full workflow: engine/agents/WORKFLOW.md Phase {phase}
Agent contracts: engine/agents/contracts/
"""

    # Write instructions file
    output = f"/tmp/agent-instructions-{book_name}-phase{phase}.md"
    write_file(output, instructions)

    print(f"✅ Instructions generated: {output}")
    print(f"\nProvide to coding agent:")
    print(f"  'Read {output} before starting work'")

    return output
```

**Usage**:
```bash
# Generate instructions for phase 2, chapter 4
python -m engine.cli agent-instructions my-book --phase 2 --chapter 4

# Output:
✅ Instructions generated: /tmp/agent-instructions-my-book-phase2.md

Provide to coding agent:
  'Read /tmp/agent-instructions-my-book-phase2.md before starting work'
```

**Effort**: 1 day
**Dependency**: None
**Blocks**: None

---

## 🟡 Group E: Automation & Orchestration [MEDIUM - P2]

### E.1 Phase Orchestrator Agent [P2 - Medium]

**Task**: Create meta-agent to manage phase transitions

**File**: `engine/agents/PHASE-ORCHESTRATOR.md`

**Responsibilities**:
- Monitor phase completion status
- Auto-run validation on phase completion signals
- Block invalid transitions
- Generate phase completion reports
- Auto-assign next tasks

**Effort**: 3 days
**Dependency**: A.1, A.2, C.3
**Blocks**: None

---

### E.2 Auto-validation Hooks [P2 - Medium]

**Task**: Integrate validation into git hooks and CLI

**Implementation**:
```bash
# .git/hooks/pre-commit (if project uses git for versioning)

# Auto-validate phase status before committing
python -m engine.cli health $BOOK_NAME --quiet

if [ $? -ne 0 ]; then
    echo "⚠️ Workflow validation failed"
    echo "Run: python -m engine.cli health $BOOK_NAME"
    echo "Commit anyway? [y/N]"
    read answer
    if [ "$answer" != "y" ]; then
        exit 1
    fi
fi
```

**Effort**: 1 day
**Dependency**: D.1
**Blocks**: None

---

## 🟡 Group F: Documentation & Training [MEDIUM - P2]

### F.1 Update WORKFLOW.md with Enforcement Sections [P2 - Medium]

**Task**: Add validation requirements to each phase in WORKFLOW.md

**Changes**: Add to each phase section:
- "Validation Gate" subsection
- "Mandatory Checklist" with explicit checkboxes
- "Blocking Rules" for transition

**Effort**: 4 hours
**Dependency**: A.1, B.3
**Blocks**: None

---

### F.2 Create INTEGRATION.md Section for External Agents [P2 - Medium]

**Task**: Document how to use book-pipeline with external coding agents

**File**: `engine/agents/INTEGRATION.md` (new section)

**Content**:
- Pre-flight checklist for external agents
- Validation workflow
- Common pitfalls and how to avoid them
- Example sessions with codex/copilot

**Effort**: 3 hours
**Dependency**: D.3
**Blocks**: None

---

### F.3 Update CLAUDE.md with Workflow Enforcement [P2 - Medium]

**Task**: Add workflow enforcement guidelines to CLAUDE.md

**Content**:
- Rules for phase validation
- How to use validation tools
- When to block/escalate
- Examples of correct workflow

**Effort**: 2 hours
**Dependency**: None
**Blocks**: None

---

## 🟢 Group G: Advanced Features [LOW - P3]

### G.1 Workflow Analytics [P3 - Low]

**Task**: Track and report workflow efficiency metrics

**Features**:
- Time spent in each phase
- Validation failure rates
- Common blocker types
- Agent efficiency metrics

**Effort**: 3 days
**Dependency**: A.3
**Blocks**: None

---

### G.2 Workflow Optimization Suggestions [P3 - Low]

**Task**: AI-powered suggestions for workflow improvements

**Features**:
- Detect bottlenecks
- Suggest parallel work opportunities
- Recommend chapter writing order

**Effort**: 4 days
**Dependency**: G.1
**Blocks**: None

---

## Implementation Roadmap

### Sprint 1 (Week 1): Critical Validation [P0] ✅ COMPLETE
**Goal**: Prevent workflow violations
**Status**: ✅ **COMPLETED** on 2026-01-04
**Actual effort**: 1 day (vs estimated 5 days)

- [x] A.1: Phase validators (validate_phase_0-5.py) - 3 days ✅ DONE
- [x] B.1: Research file validator - 2 days ✅ DONE

**Deliverables** ✅:
- ✅ validate_phase_2.py blocks Phase 3 without research
- ✅ validate_research.py ensures research quality
- ✅ Can detect current workflow violations
- ✅ **BONUS**: All 6 phase validators created (0-5)
- ✅ **BONUS**: validation_utils.py infrastructure

**Success criteria**: ✅ **ALL MET**

**Test Results** (validated on sample-non-fiction-book):
```bash
$ python engine/agents/tools/validate_phase_2.py my-books/sample-non-fiction-book/
🚫 PHASE 2 INCOMPLETE - CANNOT PROCEED TO PHASE 3

❌ CRITICAL ERRORS:
  1. CRITICAL: Missing research files for chapters: [0, 2, 3, 4, 5, ...]
  2. CRITICAL: Invalid research files for chapters: [1]
  3. Missing draft files for chapters: [0, 4, 5, 6, ...]
  4. Missing directory required for Phase 3: files/edits
  5. Missing directory required for Phase 3: files/reviews
  6. Missing directory required for Phase 3: files/proofread

⚠️  WARNINGS:
  1. Missing handoff logs for chapters: [0, 1, 2, 3, ...]
  2. progress.md appears to be template

📌 For non-fiction books:
  1. Create research files: python -m engine.cli generate-research <book> --chapter N
  2. Fill research with actual data (min 3 sources, 300 words)
  3. Validate research: python engine/agents/tools/validate_research.py <file>
  4. Create handoff logs: files/handoff/researcher-to-writer-ch-N.md
  5. Create missing directories: mkdir -p files/edits files/reviews files/proofread

$ python engine/agents/tools/validate_research.py my-books/sample-non-fiction-book/files/research/chapter-1-research.md
🚫 Research validation FAILED

❌ CRITICAL ERRORS:
  1. Research too short: 81 words (minimum: 300)
  2. Research file appears to be template
  3. Insufficient sources: 0 found (minimum: 3)
```

**Files Created**:
```
engine/agents/tools/
├── __init__.py               ← Package initialization
├── validation_utils.py       ← Common validation utilities
├── validate_research.py      ← Research quality validator ⭐
├── validate_phase_0.py       ← Import phase validator
├── validate_phase_1.py       ← Init phase validator
├── validate_phase_2.py       ← Draft phase validator ⭐ CRITICAL
├── validate_phase_3.py       ← Edit phase validator
├── validate_phase_4.py       ← Review phase validator
└── validate_phase_5.py       ← Publish phase validator
```

**Impact**:
- ✅ Workflow violations NOW DETECTED automatically
- ✅ Research requirement ENFORCED for non-fiction
- ✅ Phase transitions BLOCKED when validation fails
- ✅ Clear error messages with remediation steps
- ✅ Exit codes for automation (0=pass, 1=critical, 2=warnings)

---

### Sprint 2 (Week 2): User Tooling [P1]
**Goal**: Enable users to fix issues

- [ ] A.3: Phase status tracking (phase-status.yml) - 1 day
- [ ] D.1: Health dashboard CLI - 2 days
- [ ] D.2: Fix blockers tool - 2 days

**Deliverables**:
- ✅ `python -m engine.cli health BOOK` shows issues
- ✅ `python -m engine.cli fix-blockers BOOK` repairs common issues
- ✅ phase-status.yml tracks validation state

**Success criteria**:
```bash
$ python -m engine.cli health sample-non-fiction-book
📊 Book Workflow Health: sample-non-fiction-book
Phase 2 (Writing Drafts) - ⚠️ ISSUES FOUND
[... detailed status ...]

$ python -m engine.cli fix-blockers sample-non-fiction-book --phase 2
🔧 Fix Blockers Wizard
[... interactive fixes ...]
✅ All blockers fixed!
```

---

### Sprint 3 (Week 3): Documentation & Contracts [P1]
**Goal**: Clear requirements for agents

- [ ] B.3: Research checklist in WORKFLOW.md - 2 hours
- [ ] C.1: RESEARCHER agent contract - 3 hours
- [ ] C.2: WRITER agent contract - 3 hours
- [ ] C.3: ORCHESTRATOR agent contract - 3 hours
- [ ] D.3: Agent instructions generator - 1 day
- [ ] F.3: Update CLAUDE.md - 2 hours

**Deliverables**:
- ✅ WORKFLOW.md has mandatory checklists
- ✅ Agent contracts define requirements
- ✅ `python -m engine.cli agent-instructions` generates instructions for external agents

**Success criteria**:
- Agents have clear, verifiable requirements
- External coding agents get proper setup instructions
- CLAUDE.md has enforcement guidelines

---

### Sprint 4 (Week 4): Polish & Automation [P2]
**Goal**: Streamline workflow

- [ ] A.2: Phase transition enforcer - 2 days
- [ ] B.2: Research template generator - 1 day
- [ ] E.2: Auto-validation hooks - 1 day
- [ ] F.1: Update WORKFLOW.md validation sections - 4 hours
- [ ] F.2: INTEGRATION.md external agents section - 3 hours

**Deliverables**:
- ✅ Phase transitions auto-validated
- ✅ Research templates auto-generated from outlines
- ✅ Git hooks run validation
- ✅ Documentation complete

**Success criteria**:
- Workflow violations prevented automatically
- Users have clear guidance for all scenarios
- External agents integrate smoothly

---

## Summary Statistics

**Total Features**: 28
- 🔴 Critical (P0): 6 features
- 🟠 High (P1): 10 features
- 🟡 Medium (P2): 10 features
- 🟢 Low (P3): 2 features

**Estimated Effort**:
- Sprint 1 (Critical): 5 days
- Sprint 2 (Tooling): 5 days
- Sprint 3 (Documentation): 3 days
- Sprint 4 (Polish): 4 days
- **Total**: ~17 days (3.5 weeks)

**Dependencies**:
- 6 features have no dependencies (can start immediately)
- Most critical features (P0) have no dependencies
- User tooling (P1) depends on validators (P0)

---

## Success Metrics

### After Sprint 1 (Critical):
- ✅ 0% of workflow violations go undetected
- ✅ Phase transitions blocked when validation fails
- ✅ Research quality enforced for non-fiction

### After Sprint 2 (Tooling):
- ✅ Users can identify workflow issues in <30 seconds
- ✅ 80% of common blockers auto-fixable
- ✅ Clear visibility into workflow health

### After Sprint 3 (Documentation):
- ✅ Agents have explicit, verifiable contracts
- ✅ External coding agents have clear setup instructions
- ✅ 100% of workflow steps have validation

### After Sprint 4 (Complete):
- ✅ Workflow violations prevented automatically
- ✅ Users spend <5 min fixing validation issues
- ✅ External agents integrate without violations

---

## Next Steps

**Immediate actions (can do now)**:

1. **Create validate_phase_2.py** [P0 - Critical]
   - Blocks most critical workflow violation
   - Effort: 1 day
   - No dependencies

2. **Create validate_research.py** [P0 - Critical]
   - Enforces research quality
   - Effort: 1 day
   - No dependencies

3. **Add research checklist to WORKFLOW.md** [P0 - Critical]
   - Makes requirements explicit
   - Effort: 2 hours
   - No dependencies

**Recommended priority**:
1. Sprint 1 (Critical validators) - Week 1
2. Sprint 2 (User tooling) - Week 2
3. Sprint 3 (Documentation) - Week 3
4. Sprint 4 (Automation) - Week 4

---

## Appendix: Current Violations Found

**Book**: sample-non-fiction-book
**Phase**: 2 (Writing Drafts)
**Violations detected**: 2026-01-04

### Critical Violations:
1. ❌ Missing research files for chapters: 0, 2, 3
2. ❌ Missing handoff logs: researcher-to-writer (all chapters)
3. ❌ Missing directories: edits/, reviews/, proofread/

### Warnings:
1. ⚠️ Research file for chapter 1 is template (demo content, not real research)
2. ⚠️ Sources in outline.md unchecked for all chapters

**Estimated fix time**: 4-6 hours (manual research required)

**Prevention**: After Sprint 1, these violations would be blocked automatically.
