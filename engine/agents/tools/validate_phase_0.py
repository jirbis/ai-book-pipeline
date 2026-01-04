#!/usr/bin/env python3
"""
Phase 0 Validator - Import Completion

Validates that import phase completed successfully.

Usage:
    python validate_phase_0.py <book-path>

Exit codes:
    0 - Phase 0 complete, can proceed
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
    dir_exists,
    check_required_files,
    print_validation_result,
    validate_book_path,
)


def validate_phase_0(book_path: str, verbose: bool = False) -> ValidationResult:
    """
    Validate Phase 0 (Import) completion.

    Checks:
    - import-report.md exists
    - Original files backed up
    - PROJECT.md populated from import
    - outline.md created
    - Files distributed to correct locations

    Args:
        book_path: Path to book directory
        verbose: Print detailed information

    Returns:
        ValidationResult
    """
    errors = []
    warnings = []
    stats = {}

    # Check import report exists
    import_report = os.path.join(book_path, 'files', 'import', 'import-report.md')
    if not file_exists(import_report):
        warnings.append(
            "No import-report.md found (Phase 0 may not have been used, which is OK if starting from scratch)"
        )
        stats['import_used'] = False
        # Phase 0 is optional, so this is just a warning
        return ValidationResult(
            is_valid=True,
            errors=errors,
            warnings=warnings,
            stats=stats
        )

    stats['import_used'] = True

    # If import was used, check all requirements
    required_files = [
        'files/import/import-report.md',
        'config/PROJECT.md',
        'config/outline.md',
    ]

    missing = check_required_files(book_path, required_files)
    if missing:
        for file in missing:
            errors.append(f"Missing required file: {file}")

    # Check original files backup directory exists
    original_dir = os.path.join(book_path, 'files', 'import', 'original')
    if not dir_exists(original_dir):
        warnings.append(
            "No files/import/original/ directory (original files should be backed up)"
        )

    # Check if PROJECT.md appears to be generated (not template)
    project_file = os.path.join(book_path, 'config', 'PROJECT.md')
    if file_exists(project_file):
        with open(project_file, 'r') as f:
            content = f.read()
            if '[Book Title]' in content or '[Title]' in content:
                errors.append(
                    "PROJECT.md appears to be template (not populated from import)"
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
        print("Usage: python validate_phase_0.py <book-path>")
        print("\nValidates Phase 0 (Import) completion")
        sys.exit(1)

    book_path = sys.argv[1]
    verbose = '--verbose' in sys.argv

    # Validate book path
    valid, error = validate_book_path(book_path)
    if not valid:
        print(f"❌ Invalid book path: {error}")
        sys.exit(1)

    print(f"Validating Phase 0 (Import) for: {book_path}\n")

    result = validate_phase_0(book_path, verbose=verbose)
    exit_code = print_validation_result(result, "Phase 0 (Import)")

    if exit_code == 0:
        if result.stats.get('import_used'):
            print("\n✅ Import phase complete, ready for Phase 1")
        else:
            print("\n✅ No import used (starting from scratch), can proceed to Phase 1")
    elif exit_code == 1:
        print("\n❌ Import phase incomplete")
        print("\nFix issues above before proceeding to Phase 1")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
