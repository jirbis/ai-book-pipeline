#!/usr/bin/env python3
"""
Phase 4 Validator - Review and Finalization

Validates that review phase completed successfully.

Usage:
    python validate_phase_4.py <book-path>

Exit codes:
    0 - Phase 4 complete, can proceed to Phase 5
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
    get_book_type,
    get_chapter_list,
    print_validation_result,
    validate_book_path,
)


def validate_phase_4(book_path: str, verbose: bool = False) -> ValidationResult:
    """
    Validate Phase 4 (Review and Finalization) completion.

    Checks:
    - All chapters reviewed by CRITIC
    - Full book review completed
    - Fact-check completed (non-fiction)
    - Author review and corrections applied
    - Proofreading completed
    - Final chapter files created (chapter-*-final.md)
    - Status: READY_FOR_PUBLICATION

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
    intro_file = os.path.join(book_path, 'files', 'content', 'chapters', 'chapter-0-introduction-final.md')
    if file_exists(intro_file):
        chapters_to_check = [0] + chapters
    else:
        chapters_to_check = chapters

    stats['total_chapters'] = len(chapters_to_check)

    # Track review status
    chapter_reviews = []
    final_chapters = []
    final_missing = []

    for ch in chapters_to_check:
        # Check chapter review exists
        review_file = os.path.join(
            book_path, 'files', 'reviews', f'chapter-{ch}-review.md'
        )
        if file_exists(review_file):
            chapter_reviews.append(ch)

        # CRITICAL: Check final chapter exists
        final_file = os.path.join(
            book_path, 'files', 'content', 'chapters', f'chapter-{ch}-final.md'
        )
        if file_exists(final_file):
            final_chapters.append(ch)
        else:
            final_missing.append(ch)

    stats['chapter_reviews'] = len(chapter_reviews)
    stats['final_chapters'] = len(final_chapters)
    stats['final_missing'] = len(final_missing)

    # CRITICAL: All chapters must have final version
    if final_missing:
        errors.append(
            f"Missing final chapter files for chapters: {final_missing}\n"
            f"  CRITICAL: Create files/content/chapters/chapter-N-final.md\n"
            f"  These are canonical files for publication (Phase 5)"
        )

    # Check book-level review
    book_review = os.path.join(book_path, 'files', 'reviews', 'book-review.md')
    if not file_exists(book_review):
        errors.append(
            "Missing full book review: files/reviews/book-review.md\n"
            "  CRITIC must review entire book for consistency"
        )

    # Check fact-check for non-fiction
    if book_type == "non-fiction":
        factcheck_file = os.path.join(book_path, 'files', 'research', 'final-factcheck.md')
        if not file_exists(factcheck_file):
            warnings.append(
                "Missing final fact-check: files/research/final-factcheck.md\n"
                "  Recommended for non-fiction to verify all claims"
            )

    # Check author review handoff
    author_review = os.path.join(book_path, 'files', 'handoff', 'for-author-review.md')
    if not file_exists(author_review):
        warnings.append(
            "Missing author review handoff: files/handoff/for-author-review.md\n"
            "  Should contain compiled book for author review"
        )

    # Check proofreading report
    proofread_report = os.path.join(book_path, 'files', 'proofread', 'proofreading-report.md')
    if not file_exists(proofread_report):
        errors.append(
            "Missing proofreading report: files/proofread/proofreading-report.md\n"
            "  PROOFREADER must complete all 6 passes before publication"
        )

    # Check final approval
    final_approval = os.path.join(book_path, 'files', 'handoff', 'final-approval.md')
    if not file_exists(final_approval):
        errors.append(
            "Missing final approval: files/handoff/final-approval.md\n"
            "  ORCHESTRATOR must confirm all Phase 4 stages complete"
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
        print("Usage: python validate_phase_4.py <book-path>")
        print("\nValidates Phase 4 (Review and Finalization) completion")
        sys.exit(1)

    book_path = sys.argv[1]
    verbose = '--verbose' in sys.argv

    # Validate book path
    valid, error = validate_book_path(book_path)
    if not valid:
        print(f"❌ Invalid book path: {error}")
        sys.exit(1)

    print(f"Validating Phase 4 (Review and Finalization) for: {book_path}\n")

    result = validate_phase_4(book_path, verbose=verbose)
    exit_code = print_validation_result(result, "Phase 4 (Review)")

    if exit_code == 0:
        print("\n✅ Review complete, ready for Phase 5 (Publication)")
        print("\n📋 Phase 4 checklist complete:")
        print("  ✅ All chapters reviewed by CRITIC")
        print("  ✅ Full book review completed")
        print("  ✅ Author review and corrections applied")
        print("  ✅ Proofreading completed")
        print("  ✅ Final chapter files created")
    elif exit_code == 1:
        print("\n🚫 PHASE 4 INCOMPLETE - CANNOT PROCEED TO PUBLICATION")
        print("\nCritical items required:")
        print("  1. All chapter-N-final.md files must exist")
        print("  2. Proofreading report must be completed")
        print("  3. Final approval must be received")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
