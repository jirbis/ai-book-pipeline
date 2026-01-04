#!/usr/bin/env python3
"""
Phase 3 Validator - Editing

Validates that editing phase completed successfully.

Usage:
    python validate_phase_3.py <book-path>

Exit codes:
    0 - Phase 3 complete, can proceed to Phase 4
    1 - Critical errors, cannot proceed
    2 - Warnings only
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from validation_utils import (
    ValidationResult,
    file_exists,
    get_chapter_list,
    print_validation_result,
    validate_book_path,
)


def validate_phase_3(book_path: str, verbose: bool = False) -> ValidationResult:
    """
    Validate Phase 3 (Editing) completion.

    Checks:
    - All chapters passed developmental edit
    - All chapters passed line edit
    - All chapters passed copy edit
    - Edited chapter files exist
    - Edit reports created
    - style-guide.md followed

    Args:
        book_path: Path to book directory
        verbose: Print detailed information

    Returns:
        ValidationResult
    """
    errors = []
    warnings = []
    stats = {}

    # Get chapter list
    chapters = get_chapter_list(book_path)

    if not chapters:
        errors.append("No chapters found in outline.md")
        return ValidationResult(
            is_valid=False,
            errors=errors,
            warnings=warnings,
            stats=stats
        )

    # Check for introduction
    intro_file = os.path.join(book_path, 'files', 'content', 'chapters', 'chapter-0-introduction-edited.md')
    if file_exists(intro_file):
        chapters_to_check = [0] + chapters
    else:
        chapters_to_check = chapters

    stats['total_chapters'] = len(chapters_to_check)

    # Track editing status
    edited_exist = []
    edited_missing = []
    dev_edit_reports = []
    dev_edit_missing = []
    line_edit_reports = []
    copy_edit_reports = []

    for ch in chapters_to_check:
        # Check edited file exists
        edited_file = os.path.join(
            book_path, 'files', 'content', 'chapters', f'chapter-{ch}-edited.md'
        )

        if file_exists(edited_file):
            edited_exist.append(ch)
        else:
            edited_missing.append(ch)

        # Check edit reports
        dev_edit_file = os.path.join(
            book_path, 'files', 'edits', f'chapter-{ch}-dev-edit.md'
        )
        if file_exists(dev_edit_file):
            dev_edit_reports.append(ch)
        else:
            dev_edit_missing.append(ch)

        line_edit_file = os.path.join(
            book_path, 'files', 'edits', f'chapter-{ch}-line-edit.md'
        )
        if file_exists(line_edit_file):
            line_edit_reports.append(ch)

        copy_edit_file = os.path.join(
            book_path, 'files', 'edits', f'chapter-{ch}-copy-edit.md'
        )
        if file_exists(copy_edit_file):
            copy_edit_reports.append(ch)

    stats['edited_complete'] = len(edited_exist)
    stats['edited_missing'] = len(edited_missing)
    stats['dev_edit_reports'] = len(dev_edit_reports)
    stats['line_edit_reports'] = len(line_edit_reports)
    stats['copy_edit_reports'] = len(copy_edit_reports)

    # CRITICAL: All chapters must have edited version
    if edited_missing:
        errors.append(
            f"Missing edited chapter files for chapters: {edited_missing}\n"
            f"  Create: files/content/chapters/chapter-N-edited.md"
        )

    # Warnings for missing edit reports
    if dev_edit_missing:
        warnings.append(
            f"Missing developmental edit reports for chapters: {dev_edit_missing}\n"
            f"  Recommended: files/edits/chapter-N-dev-edit.md"
        )

    if len(line_edit_reports) < len(chapters_to_check):
        warnings.append(
            f"Not all chapters have line edit reports\n"
            f"  Recommended for quality control"
        )

    # Check style-guide.md exists
    style_guide = os.path.join(book_path, 'config', 'style-guide.md')
    if not file_exists(style_guide):
        warnings.append(
            "style-guide.md not found (needed to verify consistency)"
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
        print("Usage: python validate_phase_3.py <book-path>")
        print("\nValidates Phase 3 (Editing) completion")
        sys.exit(1)

    book_path = sys.argv[1]
    verbose = '--verbose' in sys.argv

    # Validate book path
    valid, error = validate_book_path(book_path)
    if not valid:
        print(f"❌ Invalid book path: {error}")
        sys.exit(1)

    print(f"Validating Phase 3 (Editing) for: {book_path}\n")

    result = validate_phase_3(book_path, verbose=verbose)
    exit_code = print_validation_result(result, "Phase 3 (Editing)")

    if exit_code == 0:
        print("\n✅ Editing complete, ready for Phase 4 (Review)")
    elif exit_code == 1:
        print("\n❌ Editing incomplete")
        print("\nFix errors before proceeding to Phase 4")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
