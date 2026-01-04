#!/usr/bin/env python3
"""
Research File Validator

Validates research file completeness and quality for non-fiction chapters.

Usage:
    python validate_research.py <research-file-path>

Exit codes:
    0 - Validation passed
    1 - Critical errors found (must fix)
    2 - Warnings only (can proceed)
"""

import sys
import os
import re
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from validation_utils import (
    ValidationResult,
    file_exists,
    read_file,
    count_words,
    extract_urls,
    extract_markdown_links,
    is_template_content,
    print_validation_result,
)


def validate_research_file(research_file_path: str, verbose: bool = False) -> ValidationResult:
    """
    Validates a single research file meets minimum standards.

    Args:
        research_file_path: Path to research file
        verbose: Print detailed information

    Returns:
        ValidationResult with is_valid, errors, warnings, stats
    """
    errors = []
    warnings = []
    stats = {}

    # CRITICAL: File must exist
    if not file_exists(research_file_path):
        errors.append(f"Research file does not exist: {research_file_path}")
        return ValidationResult(
            is_valid=False,
            errors=errors,
            warnings=warnings,
            stats=None
        )

    content = read_file(research_file_path)

    if not content:
        errors.append("Research file is empty")
        return ValidationResult(
            is_valid=False,
            errors=errors,
            warnings=warnings,
            stats=None
        )

    # CRITICAL: Minimum word count
    word_count = count_words(research_file_path)
    stats['word_count'] = word_count

    if word_count < 300:
        errors.append(
            f"Research too short: {word_count} words (minimum: 300)"
        )

    # CRITICAL: Must not be template
    if is_template_content(content):
        errors.append(
            "Research file appears to be template (contains placeholders like [Title], [URL], TODO, etc.)"
        )

    # Extract sources
    sources = extract_sources(content)
    stats['source_count'] = len(sources)

    # CRITICAL: Must have sources
    if len(sources) < 3:
        errors.append(
            f"Insufficient sources: {len(sources)} found (minimum: 3)"
        )

    # Check for URLs
    urls = extract_urls(content)
    markdown_links = extract_markdown_links(content)
    total_urls = len(urls) + len(markdown_links)
    stats['url_count'] = total_urls

    # WARNING: Should have URLs for sources
    if total_urls < 2:
        warnings.append(
            f"Few URLs found: {total_urls} (recommended: 3+ for source verification)"
        )

    # Check for key findings
    findings = extract_findings(content)
    stats['findings_count'] = len(findings)

    if len(findings) < 2:
        warnings.append(
            f"Few key findings: {len(findings)} (recommended: 3+)"
        )

    # Check for examples/case studies
    examples = extract_examples(content)
    stats['examples_count'] = len(examples)

    if len(examples) < 1:
        warnings.append(
            "No examples or case studies found (recommended: 2+)"
        )

    # Check for quotes
    quotes = extract_quotes(content)
    stats['quotes_count'] = len(quotes)

    if len(quotes) == 0:
        warnings.append(
            "No quotes found (recommended: 1+ per source)"
        )

    # Check for bibliography section
    has_bibliography = check_bibliography(content)
    stats['has_bibliography'] = has_bibliography

    if not has_bibliography:
        warnings.append(
            "No bibliography section found (recommended for source tracking)"
        )

    is_valid = len(errors) == 0

    return ValidationResult(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings,
        stats=stats
    )


def extract_sources(content: str) -> list:
    """Extract sources from research file"""
    sources = []

    # Look for "Sources" section or table
    # Common patterns:
    # - "## Sources"
    # - "| # | Title | Author | URL |"
    # - "1. Author. (Year). Title."

    # Method 1: Markdown table in Sources section
    sources_section = re.search(
        r'##\s*Sources.*?\n(.*?)(?=\n##|\Z)',
        content,
        re.IGNORECASE | re.DOTALL
    )

    if sources_section:
        section_content = sources_section.group(1)
        # Count rows in table (excluding header)
        table_rows = [
            line for line in section_content.split('\n')
            if line.strip().startswith('|') and not line.strip().startswith('|---')
        ]
        # Subtract header row
        if len(table_rows) > 1:
            sources.extend(range(len(table_rows) - 1))

    # Method 2: Numbered list
    # Pattern: "1. Author. Title. URL"
    numbered_sources = re.findall(
        r'^\s*\d+\.\s+.{20,}',  # At least 20 chars after number
        content,
        re.MULTILINE
    )
    sources.extend(numbered_sources)

    # Method 3: Bibliography entries
    # Pattern: "Author. (Year). Title."
    bib_entries = re.findall(
        r'\w+\.\s*\(\d{4}\)\.\s*.+\.',
        content
    )
    sources.extend(bib_entries)

    return list(set(sources))  # Remove duplicates


def extract_findings(content: str) -> list:
    """Extract key findings from research file"""
    findings = []

    # Look for "Findings" or "Key Findings" section
    findings_section = re.search(
        r'##\s*(?:Key\s*)?Findings.*?\n(.*?)(?=\n##|\Z)',
        content,
        re.IGNORECASE | re.DOTALL
    )

    if findings_section:
        section_content = findings_section.group(1)

        # Count subsections (### Finding N:)
        finding_headers = re.findall(
            r'###\s*Finding\s+\d+',
            section_content,
            re.IGNORECASE
        )
        findings.extend(finding_headers)

        # Count bullet points
        bullet_points = re.findall(
            r'^\s*[-*]\s+.{30,}',  # At least 30 chars
            section_content,
            re.MULTILINE
        )
        findings.extend(bullet_points)

    return findings


def extract_examples(content: str) -> list:
    """Extract examples/case studies from research file"""
    examples = []

    # Look for "Examples" or "Case Studies" section
    examples_section = re.search(
        r'##\s*(?:Examples|Case\s*Studies).*?\n(.*?)(?=\n##|\Z)',
        content,
        re.IGNORECASE | re.DOTALL
    )

    if examples_section:
        section_content = examples_section.group(1)

        # Count numbered examples
        example_numbers = re.findall(
            r'^\s*\d+\.\s*\*\*(?:Example|Case)',
            section_content,
            re.MULTILINE | re.IGNORECASE
        )
        examples.extend(example_numbers)

        # Count subsections
        example_headers = re.findall(
            r'###\s*(?:Example|Case)',
            section_content,
            re.IGNORECASE
        )
        examples.extend(example_headers)

    return examples


def extract_quotes(content: str) -> list:
    """Extract quotes from research file"""
    quotes = []

    # Pattern 1: Text in quotes "..."
    double_quotes = re.findall(r'"([^"]{20,})"', content)
    quotes.extend(double_quotes)

    # Pattern 2: Markdown blockquotes
    blockquotes = re.findall(r'^>\s*(.{20,})', content, re.MULTILINE)
    quotes.extend(blockquotes)

    # Pattern 3: Key Quote field
    quote_fields = re.findall(
        r'(?:Key\s*Quote|Quote):\s*(.{20,})',
        content,
        re.IGNORECASE
    )
    quotes.extend(quote_fields)

    return quotes


def check_bibliography(content: str) -> bool:
    """Check if bibliography section exists"""
    return bool(re.search(
        r'##\s*(?:Bibliography|References|Sources)',
        content,
        re.IGNORECASE
    ))


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python validate_research.py <research-file-path>")
        print("\nValidates research file for non-fiction chapters")
        print("\nExit codes:")
        print("  0 - Validation passed")
        print("  1 - Critical errors (must fix)")
        print("  2 - Warnings only (can proceed)")
        sys.exit(1)

    research_file = sys.argv[1]
    verbose = '--verbose' in sys.argv or '-v' in sys.argv

    print(f"Validating research file: {research_file}\n")

    result = validate_research_file(research_file, verbose=verbose)
    exit_code = print_validation_result(result, "Research")

    if exit_code == 0:
        print("\n✅ Research file is ready for drafting")
    elif exit_code == 1:
        print("\n❌ Please fix critical errors before proceeding")
        print("\nCommon fixes:")
        print("  - Add more sources (minimum 3 with URLs)")
        print("  - Expand research (minimum 300 words)")
        print("  - Replace template placeholders with actual content")
        print("  - Add key findings from sources")
    else:
        print("\n⚠️  Research file passes but could be improved")
        print("  Consider addressing warnings for higher quality")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
