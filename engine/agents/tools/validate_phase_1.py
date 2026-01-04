#!/usr/bin/env python3
"""
Phase 1 Validator - Initialization

Validates that initialization phase completed successfully.

Usage:
    python validate_phase_1.py <book-path>

Exit codes:
    0 - Phase 1 complete, can proceed to Phase 2
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
    read_file,
    check_required_files,
    check_required_dirs,
    get_book_type,
    is_template_content,
    print_validation_result,
    validate_book_path,
)


def validate_phase_1(book_path: str, verbose: bool = False) -> ValidationResult:
    """
    Validate Phase 1 (Initialization) completion.

    Checks:
    - PROJECT.md complete and valid
    - Directory structure created
    - outline.md approved
    - Fiction: plot.md, characters.md, world.md
    - Non-fiction: bibliography.md
    - progress.md initialized

    Args:
        book_path: Path to book directory
        verbose: Print detailed information

    Returns:
        ValidationResult
    """
    errors = []
    warnings = []
    stats = {}

    # Get book type
    book_type = get_book_type(book_path)
    stats['book_type'] = book_type

    if book_type == "unknown":
        errors.append(
            "Book type not specified in PROJECT.md (must be 'fiction' or 'non-fiction')"
        )

    # Check required config files
    required_config = [
        'config/PROJECT.md',
        'config/outline.md',
        'config/style-guide.md',
        'config/progress.md',
    ]

    missing_config = check_required_files(book_path, required_config)
    if missing_config:
        for file in missing_config:
            errors.append(f"Missing required config file: {file}")

    # Check book-type specific files
    if book_type == "fiction":
        fiction_files = [
            'config/plot.md',
            'config/characters.md',
            'config/world.md',
        ]
        missing_fiction = check_required_files(book_path, fiction_files)
        if missing_fiction:
            for file in missing_fiction:
                errors.append(f"Missing required fiction file: {file}")

    elif book_type == "non-fiction":
        nonfiction_files = [
            'config/bibliography.md',
        ]
        missing_nonfiction = check_required_files(book_path, nonfiction_files)
        if missing_nonfiction:
            for file in missing_nonfiction:
                warnings.append(f"Missing recommended file: {file}")

    # Check required directories
    required_dirs = [
        'files/content/chapters',
        'files/research',
        'files/edits',
        'files/reviews',
        'files/handoff',
        'files/proofread',
        'files/output',
    ]

    missing_dirs = check_required_dirs(book_path, required_dirs)
    if missing_dirs:
        for dir in missing_dirs:
            errors.append(f"Missing required directory: {dir}")

    # Check PROJECT.md is filled (not template)
    project_file = os.path.join(book_path, 'config', 'PROJECT.md')
    if file_exists(project_file):
        content = read_file(project_file)
        if is_template_content(content):
            errors.append(
                "PROJECT.md appears to be template (contains placeholders)"
            )

        # Check for required fields
        if 'Title' not in content or '[Title]' in content:
            errors.append("PROJECT.md missing book title")
        if 'Target audience' not in content or '[audience]' in content:
            warnings.append("PROJECT.md missing target audience")

    # Check outline.md is filled
    outline_file = os.path.join(book_path, 'config', 'outline.md')
    if file_exists(outline_file):
        content = read_file(outline_file)
        if is_template_content(content):
            errors.append(
                "outline.md appears to be template (not filled with actual outline)"
            )

        # Check for chapters
        if 'Chapter' not in content and 'chapter' not in content:
            errors.append("outline.md contains no chapter information")

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
        print("Usage: python validate_phase_1.py <book-path>")
        print("\nValidates Phase 1 (Initialization) completion")
        sys.exit(1)

    book_path = sys.argv[1]
    verbose = '--verbose' in sys.argv

    # Validate book path
    valid, error = validate_book_path(book_path)
    if not valid:
        print(f"❌ Invalid book path: {error}")
        sys.exit(1)

    print(f"Validating Phase 1 (Initialization) for: {book_path}\n")

    result = validate_phase_1(book_path, verbose=verbose)
    exit_code = print_validation_result(result, "Phase 1 (Initialization)")

    if exit_code == 0:
        print("\n✅ Initialization complete, ready for Phase 2 (Writing Drafts)")
    elif exit_code == 1:
        print("\n❌ Initialization incomplete")
        print("\nFix critical errors before proceeding to Phase 2")
        print("\nCommon fixes:")
        print("  - Fill PROJECT.md with actual book information")
        print("  - Create outline.md with chapter breakdown")
        print("  - Create missing directories (files/content/chapters, files/research, etc.)")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
