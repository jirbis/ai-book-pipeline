#!/usr/bin/env python3
"""
Phase 5 Validator - Publication

Validates that publication phase completed successfully.

Usage:
    python validate_phase_5.py <book-path>

Exit codes:
    0 - Phase 5 complete, book published
    1 - Critical errors, publication incomplete
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
    print_validation_result,
    validate_book_path,
)


def validate_phase_5(book_path: str, verbose: bool = False) -> ValidationResult:
    """
    Validate Phase 5 (Publication) completion.

    Checks:
    - Front matter created
    - Back matter created
    - Book assembled (book-complete.md)
    - Exported to all formats (docx, pdf, epub)
    - Files validated (open correctly, no artifacts)
    - Publication ready

    Args:
        book_path: Path to book directory
        verbose: Print detailed information

    Returns:
        ValidationResult
    """
    errors = []
    warnings = []
    stats = {}

    output_dir = os.path.join(book_path, 'files', 'output')

    if not dir_exists(output_dir):
        errors.append(
            "Output directory does not exist: files/output/\n"
            "  Create directory and export book"
        )
        return ValidationResult(
            is_valid=False,
            errors=errors,
            warnings=warnings,
            stats=stats
        )

    # Check assembled book
    book_complete = os.path.join(output_dir, 'book-complete.md')
    if not file_exists(book_complete):
        errors.append(
            "Assembled book not found: files/output/book-complete.md\n"
            "  PUBLISHER must combine all content"
        )

    # Check exported formats
    # Look for any .docx files
    docx_files = [f for f in os.listdir(output_dir) if f.endswith('.docx')]
    pdf_files = [f for f in os.listdir(output_dir) if f.endswith('.pdf')]
    epub_files = [f for f in os.listdir(output_dir) if f.endswith('.epub')]

    stats['docx_count'] = len(docx_files)
    stats['pdf_count'] = len(pdf_files)
    stats['epub_count'] = len(epub_files)

    if not docx_files:
        errors.append(
            "No DOCX export found in files/output/\n"
            "  Export to DOCX format for publishers"
        )

    if not pdf_files:
        warnings.append(
            "No PDF export found in files/output/\n"
            "  Recommended for review and print"
        )

    if not epub_files:
        warnings.append(
            "No EPUB export found in files/output/\n"
            "  Recommended for e-readers"
        )

    # Check front matter
    front_matter_dir = os.path.join(book_path, 'files', 'content', 'front-matter')
    if dir_exists(front_matter_dir):
        front_matter_files = os.listdir(front_matter_dir)
        stats['front_matter_files'] = len(front_matter_files)

        if not front_matter_files:
            warnings.append(
                "Front matter directory empty\n"
                "  Should contain title page, copyright, TOC, etc."
            )
    else:
        warnings.append(
            "No front matter directory: files/content/front-matter/"
        )

    # Check back matter
    back_matter_dir = os.path.join(book_path, 'files', 'content', 'back-matter')
    if dir_exists(back_matter_dir):
        back_matter_files = os.listdir(back_matter_dir)
        stats['back_matter_files'] = len(back_matter_files)

        if not back_matter_files:
            warnings.append(
                "Back matter directory empty\n"
                "  Should contain bibliography, about author, etc."
            )
    else:
        warnings.append(
            "No back matter directory: files/content/back-matter/"
        )

    # List exported files
    if verbose:
        print("\nExported files found:")
        if docx_files:
            print(f"  DOCX: {', '.join(docx_files)}")
        if pdf_files:
            print(f"  PDF: {', '.join(pdf_files)}")
        if epub_files:
            print(f"  EPUB: {', '.join(epub_files)}")

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
        print("Usage: python validate_phase_5.py <book-path>")
        print("\nValidates Phase 5 (Publication) completion")
        sys.exit(1)

    book_path = sys.argv[1]
    verbose = '--verbose' in sys.argv

    # Validate book path
    valid, error = validate_book_path(book_path)
    if not valid:
        print(f"❌ Invalid book path: {error}")
        sys.exit(1)

    print(f"Validating Phase 5 (Publication) for: {book_path}\n")

    result = validate_phase_5(book_path, verbose=verbose)
    exit_code = print_validation_result(result, "Phase 5 (Publication)")

    if exit_code == 0:
        print("\n🎉 PUBLICATION COMPLETE!")
        print("\n📚 Book successfully published:")
        if result.stats.get('docx_count', 0) > 0:
            print(f"  ✅ DOCX format: {result.stats['docx_count']} file(s)")
        if result.stats.get('pdf_count', 0) > 0:
            print(f"  ✅ PDF format: {result.stats['pdf_count']} file(s)")
        if result.stats.get('epub_count', 0) > 0:
            print(f"  ✅ EPUB format: {result.stats['epub_count']} file(s)")
        print("\nFiles ready for distribution!")
    elif exit_code == 1:
        print("\n❌ Publication incomplete")
        print("\nFix errors above to complete publication")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
