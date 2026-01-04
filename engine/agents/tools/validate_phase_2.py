#!/usr/bin/env python3
"""
Phase 2 Validator - Writing Drafts

Validates that draft writing phase completed successfully.
CRITICAL: For non-fiction, enforces research before writing.

Usage:
    python validate_phase_2.py <book-path>

Exit codes:
    0 - Phase 2 complete, can proceed to Phase 3
    1 - Critical errors, BLOCKED from Phase 3
    2 - Warnings only
"""

import sys
import os
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from validation_utils import (
    ValidationResult,
    file_exists,
    read_file,
    count_words,
    get_book_type,
    get_chapter_list,
    is_template_content,
    print_validation_result,
    validate_book_path,
)


def validate_phase_2(book_path: str, verbose: bool = False) -> ValidationResult:
    """
    Validate Phase 2 (Writing Drafts) completion.

    CRITICAL FOR NON-FICTION:
    - Research files must exist for ALL chapters
    - Research files must be validated (not templates)
    - Handoff logs must exist (researcher -> writer)

    FOR ALL BOOKS:
    - All chapters have draft files
    - Word counts tracked in progress.md
    - Required directories exist

    Args:
        book_path: Path to book directory
        verbose: Print detailed information

    Returns:
        ValidationResult
    """
    errors = []
    warnings = []
    stats = {}

    # Get book type and chapters
    book_type = get_book_type(book_path)
    stats['book_type'] = book_type

    # Get chapter list from outline
    chapters = get_chapter_list(book_path)

    if not chapters:
        errors.append(
            "No chapters found in outline.md"
        )
        return ValidationResult(
            is_valid=False,
            errors=errors,
            warnings=warnings,
            stats=stats
        )

    stats['total_chapters'] = len(chapters)

    # Also check for introduction (chapter 0)
    intro_file = os.path.join(book_path, 'files', 'content', 'chapters', 'chapter-0-introduction-draft-v1.md')
    if file_exists(intro_file):
        chapters_to_check = [0] + chapters
    else:
        chapters_to_check = chapters

    # Track chapter status
    drafts_exist = []
    drafts_missing = []
    research_exist = []
    research_missing = []
    research_invalid = []
    handoff_exist = []
    handoff_missing = []

    for ch in chapters_to_check:
        # Check draft exists
        draft_patterns = [
            f'chapter-{ch}-draft-v1.md',
            f'chapter-{ch}-draft.md',
        ]

        draft_found = False
        for pattern in draft_patterns:
            draft_file = os.path.join(book_path, 'files', 'content', 'chapters', pattern)
            if file_exists(draft_file):
                drafts_exist.append(ch)
                draft_found = True
                break

        if not draft_found:
            drafts_missing.append(ch)

        # For non-fiction: CRITICAL - check research
        if book_type == "non-fiction":
            research_file = os.path.join(
                book_path, 'files', 'research', f'chapter-{ch}-research.md'
            )

            if not file_exists(research_file):
                research_missing.append(ch)
            else:
                research_exist.append(ch)

                # Validate research file quality
                # Call validate_research.py as subprocess
                validator_path = os.path.join(
                    Path(__file__).parent,
                    'validate_research.py'
                )

                try:
                    result = subprocess.run(
                        [sys.executable, validator_path, research_file],
                        capture_output=True,
                        timeout=10
                    )

                    if result.returncode != 0:
                        research_invalid.append(ch)
                        if verbose:
                            print(f"\nResearch validation failed for chapter {ch}:")
                            print(result.stdout.decode())

                except Exception as e:
                    warnings.append(
                        f"Could not validate research for chapter {ch}: {e}"
                    )

            # Check handoff log exists
            handoff_file = os.path.join(
                book_path, 'files', 'handoff', f'researcher-to-writer-ch-{ch}.md'
            )

            if not file_exists(handoff_file):
                handoff_missing.append(ch)
            else:
                handoff_exist.append(ch)

    stats['drafts_complete'] = len(drafts_exist)
    stats['drafts_missing'] = len(drafts_missing)

    if book_type == "non-fiction":
        stats['research_complete'] = len(research_exist)
        stats['research_missing'] = len(research_missing)
        stats['research_invalid'] = len(research_invalid)
        stats['handoff_logs_exist'] = len(handoff_exist)
        stats['handoff_logs_missing'] = len(handoff_missing)

    # CRITICAL ERRORS for non-fiction
    if book_type == "non-fiction":
        if research_missing:
            errors.append(
                f"CRITICAL: Missing research files for chapters: {research_missing}\n"
                f"  Non-fiction requires research BEFORE writing.\n"
                f"  Create research files: files/research/chapter-N-research.md"
            )

        if research_invalid:
            errors.append(
                f"CRITICAL: Invalid research files for chapters: {research_invalid}\n"
                f"  Research files failed validation (template content, too short, or insufficient sources).\n"
                f"  Run: python engine/agents/tools/validate_research.py <file> for details"
            )

        if handoff_missing:
            warnings.append(
                f"Missing handoff logs for chapters: {handoff_missing}\n"
                f"  Create: files/handoff/researcher-to-writer-ch-N.md"
            )

    # ERRORS for all books
    if drafts_missing:
        errors.append(
            f"Missing draft files for chapters: {drafts_missing}\n"
            f"  Create: files/content/chapters/chapter-N-draft-v1.md"
        )

    # Check progress.md is updated
    progress_file = os.path.join(book_path, 'config', 'progress.md')
    if not file_exists(progress_file):
        warnings.append("progress.md not found (should track chapter progress)")
    else:
        content = read_file(progress_file)
        if is_template_content(content):
            warnings.append("progress.md appears to be template (not updated with actual progress)")

    # Check required directories exist for Phase 3
    required_dirs = ['files/edits', 'files/reviews', 'files/proofread']
    for dir_name in required_dirs:
        full_path = os.path.join(book_path, dir_name)
        if not os.path.isdir(full_path):
            errors.append(
                f"Missing directory required for Phase 3: {dir_name}\n"
                f"  Create before transitioning to Phase 3"
            )

    is_valid = len(errors) == 0

    return ValidationResult(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings,
        stats=stats
    )


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python validate_phase_2.py <book-path>")
        print("\nValidates Phase 2 (Writing Drafts) completion")
        print("\nCRITICAL: For non-fiction, validates research was done before writing")
        sys.exit(1)

    book_path = sys.argv[1]
    verbose = '--verbose' in sys.argv

    # Validate book path
    valid, error = validate_book_path(book_path)
    if not valid:
        print(f"❌ Invalid book path: {error}")
        sys.exit(1)

    print(f"Validating Phase 2 (Writing Drafts) for: {book_path}\n")

    result = validate_phase_2(book_path, verbose=verbose)
    exit_code = print_validation_result(result, "Phase 2 (Writing Drafts)")

    if exit_code == 0:
        print("\n✅ Phase 2 complete, ready for Phase 3 (Editing)")
    elif exit_code == 1:
        print("\n🚫 PHASE 2 INCOMPLETE - CANNOT PROCEED TO PHASE 3")
        print("\nFix critical errors above before proceeding")

        if result.stats.get('book_type') == 'non-fiction':
            print("\n📌 For non-fiction books:")
            print("  1. Create research files: python -m engine.cli generate-research <book> --chapter N")
            print("  2. Fill research with actual data (min 3 sources, 300 words)")
            print("  3. Validate research: python engine/agents/tools/validate_research.py <file>")
            print("  4. Create handoff logs: files/handoff/researcher-to-writer-ch-N.md")
            print("  5. Create missing directories: mkdir -p files/edits files/reviews files/proofread")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
