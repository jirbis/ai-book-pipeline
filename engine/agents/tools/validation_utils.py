#!/usr/bin/env python3
"""
Validation Utilities

Common functions used by all validators.
"""

import os
import re
import yaml
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of a validation check"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    stats: Optional[Dict] = None


def file_exists(filepath: str) -> bool:
    """Check if file exists"""
    return os.path.isfile(filepath)


def dir_exists(dirpath: str) -> bool:
    """Check if directory exists"""
    return os.path.isdir(dirpath)


def count_words(filepath: str) -> int:
    """Count words in a file"""
    if not file_exists(filepath):
        return 0

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Remove markdown formatting for accurate word count
            content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)  # Remove code blocks
            content = re.sub(r'`[^`]+`', '', content)  # Remove inline code
            content = re.sub(r'[#*_\[\]()]+', '', content)  # Remove markdown symbols
            words = content.split()
            return len(words)
    except Exception as e:
        print(f"Warning: Could not count words in {filepath}: {e}")
        return 0


def read_file(filepath: str) -> str:
    """Read file content"""
    if not file_exists(filepath):
        return ""

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Warning: Could not read {filepath}: {e}")
        return ""


def read_yaml(filepath: str) -> Dict:
    """Read YAML file"""
    if not file_exists(filepath):
        return {}

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"Warning: Could not parse YAML {filepath}: {e}")
        return {}


def extract_urls(content: str) -> List[str]:
    """Extract URLs from content"""
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    return re.findall(url_pattern, content)


def extract_markdown_links(content: str) -> List[Tuple[str, str]]:
    """Extract markdown links [text](url)"""
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    return re.findall(link_pattern, content)


def is_template_content(content: str) -> bool:
    """Check if content is still template (has placeholders)"""
    # Common template placeholders
    placeholders = [
        '[Title]', '[Name]', '[Date]', '[YYYY-MM-DD]', '[N]',
        '[description]', '[URL]', '[Author]', '[Source]',
        'TODO', 'FIXME', 'XXX', 'PLACEHOLDER',
        '[...]', '[add', '[fill', '[describe', '[explain',
    ]

    content_lower = content.lower()

    # Check for placeholder patterns
    for placeholder in placeholders:
        if placeholder.lower() in content_lower:
            return True

    # Check for empty sections (headers with no content)
    lines = content.split('\n')
    empty_sections = 0
    for i, line in enumerate(lines):
        if line.startswith('#') and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if not next_line or next_line.startswith('#'):
                empty_sections += 1

    # If more than 30% of sections are empty, likely a template
    total_headers = len([l for l in lines if l.startswith('#')])
    if total_headers > 0 and empty_sections / total_headers > 0.3:
        return True

    return False


def get_book_type(book_path: str) -> str:
    """Get book type (fiction/non-fiction) from PROJECT.md"""
    project_file = os.path.join(book_path, 'config', 'PROJECT.md')

    if not file_exists(project_file):
        return "unknown"

    content = read_file(project_file)

    # Look for type field
    type_match = re.search(r'\*\*Type\*\*\s*[|:]\s*`?([^`|\n]+)', content, re.IGNORECASE)
    if type_match:
        book_type = type_match.group(1).strip().lower()
        if 'non-fiction' in book_type or 'nonfiction' in book_type:
            return 'non-fiction'
        elif 'fiction' in book_type:
            return 'fiction'

    return "unknown"


def get_chapter_list(book_path: str) -> List[int]:
    """Get list of chapter numbers from outline.md"""
    outline_file = os.path.join(book_path, 'config', 'outline.md')

    if not file_exists(outline_file):
        return []

    content = read_file(outline_file)
    chapters = []

    # Look for chapter patterns
    # Format: "### Chapter N:" or "## Chapter N:" or "Chapter N:"
    chapter_pattern = r'(?:^|\n)#+\s*Chapter\s+(\d+)'
    matches = re.finditer(chapter_pattern, content, re.IGNORECASE)

    for match in matches:
        chapter_num = int(match.group(1))
        if chapter_num not in chapters:
            chapters.append(chapter_num)

    return sorted(chapters)


def get_total_chapters(book_path: str) -> int:
    """Get total number of chapters from outline.md or progress.md"""
    chapters = get_chapter_list(book_path)
    if chapters:
        return len(chapters)

    # Fallback: check progress.md
    progress_file = os.path.join(book_path, 'config', 'progress.md')
    if file_exists(progress_file):
        content = read_file(progress_file)
        # Look for "Chapters Complete: N / M"
        match = re.search(r'Chapters\s+Complete.*?(\d+)\s*/\s*(\d+)', content, re.IGNORECASE)
        if match:
            return int(match.group(2))

    return 0


def check_required_files(book_path: str, files: List[str]) -> List[str]:
    """Check which required files are missing"""
    missing = []
    for filepath in files:
        full_path = os.path.join(book_path, filepath)
        if not file_exists(full_path):
            missing.append(filepath)
    return missing


def check_required_dirs(book_path: str, dirs: List[str]) -> List[str]:
    """Check which required directories are missing"""
    missing = []
    for dirpath in dirs:
        full_path = os.path.join(book_path, dirpath)
        if not dir_exists(full_path):
            missing.append(dirpath)
    return missing


def format_error_list(errors: List[str], warnings: List[str]) -> str:
    """Format errors and warnings for display"""
    output = []

    if errors:
        output.append("\n❌ CRITICAL ERRORS:")
        for i, error in enumerate(errors, 1):
            output.append(f"  {i}. {error}")

    if warnings:
        output.append("\n⚠️  WARNINGS:")
        for i, warning in enumerate(warnings, 1):
            output.append(f"  {i}. {warning}")

    return "\n".join(output)


def print_validation_result(result: ValidationResult, phase_name: str = "") -> int:
    """
    Print validation result and return exit code.

    Returns:
        0 if valid
        1 if critical errors
        2 if warnings only
    """
    if result.is_valid and not result.warnings:
        print(f"✅ {phase_name} validation PASSED")
        if result.stats:
            print("\nStatistics:")
            for key, value in result.stats.items():
                print(f"  - {key}: {value}")
        return 0

    if result.is_valid and result.warnings:
        print(f"⚠️  {phase_name} validation PASSED with warnings")
        print(format_error_list([], result.warnings))
        if result.stats:
            print("\nStatistics:")
            for key, value in result.stats.items():
                print(f"  - {key}: {value}")
        return 2

    print(f"🚫 {phase_name} validation FAILED")
    print(format_error_list(result.errors, result.warnings))
    return 1


def validate_book_path(book_path: str) -> Tuple[bool, str]:
    """Validate that book_path is a valid book directory"""
    if not book_path:
        return False, "Book path not specified"

    if not dir_exists(book_path):
        return False, f"Book directory does not exist: {book_path}"

    # Check for config directory
    config_dir = os.path.join(book_path, 'config')
    if not dir_exists(config_dir):
        return False, f"Config directory not found: {config_dir}"

    # Check for PROJECT.md
    project_file = os.path.join(book_path, 'config', 'PROJECT.md')
    if not file_exists(project_file):
        return False, f"PROJECT.md not found: {project_file}"

    return True, ""


if __name__ == "__main__":
    print("Validation utilities loaded successfully")
    print(f"Version: {__version__}")
