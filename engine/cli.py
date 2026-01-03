from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path
from typing import Dict, Iterable, List, Optional


REPO_ROOT = Path(__file__).resolve().parent.parent
BOOKS_ROOT = REPO_ROOT / "my-books"
ENGINE_ROOT = Path(__file__).resolve().parent
TEMPLATE_ROOT = ENGINE_ROOT / "book-templates"
WORKFLOW_PATH = ENGINE_ROOT / "agents" / "WORKFLOW.md"

PHASE_HEADINGS: Dict[str, str] = {
    "0": "PHASE 0: Import (optional)",
    "1": "PHASE 1: Initialization",
    "2": "PHASE 2: Writing Drafts",
    "3": "PHASE 3: Editing",
    "4": "PHASE 4: Review",
    "5": "PHASE 5: Publication",
}

PHASE_ALIASES: Dict[str, str] = {
    "import": "0",
    "init": "1",
    "initialize": "1",
    "draft": "2",
    "write": "2",
    "editing": "3",
    "edit": "3",
    "review": "4",
    "publish": "5",
    "publication": "5",
}

PROJECT_FIELD_PATTERN = re.compile(
    r"^\|\s*\*\*(?P<field>[^*|]+)\*\*\s*\|\s*`?(?P<value>[^|`]+)`?\s*\|", re.IGNORECASE
)


def normalize_book_type(raw: str) -> str:
    """Normalize book type strings to template directory names."""
    value = raw.strip().lower()
    if value in {"fiction", "fic"}:
        return "fiction"
    if value in {"non-fiction", "non fiction", "nonfiction", "nf"}:
        return "non-fiction"
    raise ValueError(f"Unrecognized book type '{raw}'. Expected fiction or non-fiction.")


def parse_project_fields(project_path: Path) -> Dict[str, str]:
    """Parse simple key/value pairs from the PROJECT.md table."""
    fields: Dict[str, str] = {}
    for line in project_path.read_text(encoding="utf-8").splitlines():
        match = PROJECT_FIELD_PATTERN.match(line.strip())
        if match:
            fields[match.group("field").strip().lower()] = match.group("value").strip()
    return fields


def require_project_config(book_root: Path) -> Path:
    project_path = book_root / "config" / "PROJECT.md"
    if not project_path.exists():
        raise SystemExit(f"Missing project configuration at {project_path}")
    return project_path


def resolve_book_root(book: str) -> Path:
    return BOOKS_ROOT / book


def resolve_book_type(explicit_type: Optional[str], project_fields: Dict[str, str]) -> str:
    if explicit_type:
        return normalize_book_type(explicit_type)
    configured = project_fields.get("type")
    if configured:
        return normalize_book_type(configured)
    raise SystemExit(
        "Book type is missing. Provide --type fiction|non-fiction or fill the Type field in PROJECT.md."
    )


def copy_templates(config_dir: Path, book_type: str, overwrite: bool) -> List[Path]:
    copied: List[Path] = []

    def copy_all(files: Iterable[Path]) -> None:
        for source in files:
            if not source.is_file():
                continue
            target = config_dir / source.name
            if target.exists() and not overwrite:
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(source, target)
            copied.append(target)

    copy_all(TEMPLATE_ROOT.iterdir())

    type_dir = TEMPLATE_ROOT / book_type
    if not type_dir.exists():
        raise SystemExit(f"Templates for '{book_type}' not found at {type_dir}")
    copy_all(type_dir.iterdir())
    return copied


def ensure_file_structure(book_root: Path, book_type: str) -> List[Path]:
    created: List[Path] = []
    files_root = book_root / "files"
    common_dirs = [
        "import",
        "research",
        "edits",
        "reviews",
        "handoff",
        "proofread",
        "output",
    ]

    for name in common_dirs:
        path = files_root / name
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            created.append(path)

    content_root = files_root / "content"
    if not content_root.exists():
        content_root.mkdir(parents=True, exist_ok=True)
        created.append(content_root)

    chapters_dir = content_root / "chapters"
    if not chapters_dir.exists():
        chapters_dir.mkdir(parents=True, exist_ok=True)
        created.append(chapters_dir)

    if book_type == "fiction":
        scenes_dir = content_root / "scenes"
        if not scenes_dir.exists():
            scenes_dir.mkdir(parents=True, exist_ok=True)
            created.append(scenes_dir)
    else:
        for name in ("front-matter", "back-matter"):
            path = content_root / name
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                created.append(path)

    return created


def init_project(args: argparse.Namespace) -> None:
    book_root = resolve_book_root(args.book)
    project_path = book_root / "config" / "PROJECT.md"
    book_root.mkdir(parents=True, exist_ok=True)
    project_fields: Dict[str, str] = {}
    if project_path.exists():
        project_fields = parse_project_fields(project_path)

    book_type = resolve_book_type(args.type, project_fields)

    config_dir = book_root / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    copied = copy_templates(config_dir, book_type, overwrite=args.force)
    created = ensure_file_structure(book_root, book_type)

    print(f"Initialized book at {book_root}")
    print(f"- Book type: {book_type}")
    print(f"- Templates copied ({len(copied)}):")
    for path in copied:
        print(f"  • {path.relative_to(REPO_ROOT)}")
    if created:
        print(f"- Created directories ({len(created)}):")
        for path in created:
            print(f"  • {path.relative_to(REPO_ROOT)}")
    else:
        print("- No new directories created (already present).")
    print("\nNext steps (see engine/agents/WORKFLOW.md Phase 1):")
    print("  - Fill in config/PROJECT.md")
    print("  - Update config/outline.md or config/plot.md as appropriate")
    print("  - Track progress in config/progress.md")


def extract_section(workflow_text: str, heading_text: str) -> Optional[str]:
    lines = workflow_text.splitlines()
    start_idx: Optional[int] = None
    start_level: Optional[int] = None

    for idx, raw_line in enumerate(lines):
        line = raw_line.strip()
        match = re.match(r"^(#+)\s+(.*)$", line)
        if not match:
            continue
        heading_level = len(match.group(1))
        heading = match.group(2).strip()
        if heading.lower() == heading_text.lower():
            start_idx = idx
            start_level = heading_level
            break

    if start_idx is None or start_level is None:
        return None

    section_lines: List[str] = []
    for raw_line in lines[start_idx:]:
        match = re.match(r"^(#+)\s+(.*)$", raw_line.strip())
        if match and len(section_lines) > 0 and len(match.group(1)) <= start_level:
            break
        section_lines.append(raw_line.rstrip())
    return "\n".join(section_lines).strip()


def render_workflow_section(heading_text: str) -> str:
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")
    section = extract_section(workflow_text, heading_text)
    if section:
        return section
    return f"Could not find '{heading_text}' in {WORKFLOW_PATH}"


def resolve_phase_heading(phase: str) -> str:
    normalized = phase.lower()
    if normalized in PHASE_HEADINGS:
        return PHASE_HEADINGS[normalized]
    if normalized in PHASE_ALIASES:
        return PHASE_HEADINGS[PHASE_ALIASES[normalized]]
    raise SystemExit(f"Unknown phase '{phase}'. Expected 0-5 or one of {', '.join(PHASE_ALIASES)}.")


def run_phase(args: argparse.Namespace) -> None:
    book_root = resolve_book_root(args.book)
    project_path = require_project_config(book_root)
    project_fields = parse_project_fields(project_path)
    book_type = resolve_book_type(None, project_fields)

    heading = resolve_phase_heading(args.phase)
    print(f"Book: {book_root.relative_to(REPO_ROOT)} ({book_type})")
    print(f"Workflow excerpt for {heading}:\n")
    print(render_workflow_section(heading))


def summarize_status(args: argparse.Namespace) -> None:
    book_root = resolve_book_root(args.book)
    project_path = require_project_config(book_root)
    fields = parse_project_fields(project_path)
    book_type = resolve_book_type(None, fields)

    progress_path = book_root / "config" / "progress.md"
    missing: List[str] = []
    key_files = [
        project_path,
        book_root / "config" / "style-guide.md",
        progress_path,
    ]
    for path in key_files:
        if not path.exists():
            missing.append(str(path.relative_to(REPO_ROOT)))

    print(f"Book: {book_root.relative_to(REPO_ROOT)}")
    print(f"Title: {fields.get('title', 'Unknown')} — Type: {book_type}")
    if "status" in fields:
        print(f"Status: {fields['status']}")
    print(f"Config present at: {project_path.relative_to(REPO_ROOT)}")
    print(f"Progress file: {progress_path.relative_to(REPO_ROOT)} ({'found' if progress_path.exists() else 'missing'})")

    files_root = book_root / "files"
    print("Working directories:")
    expected_dirs = [
        files_root / "content",
        files_root / "research",
        files_root / "edits",
        files_root / "reviews",
        files_root / "handoff",
        files_root / "proofread",
        files_root / "output",
    ]
    for path in expected_dirs:
        print(f"  • {path.relative_to(REPO_ROOT)} ({'ok' if path.exists() else 'missing'})")

    if missing:
        print("\nMissing recommended files:")
        for path in missing:
            print(f"  - {path}")


def generate_samples(args: argparse.Namespace) -> None:
    book_root = resolve_book_root(args.book)
    project_path = require_project_config(book_root)
    project_fields = parse_project_fields(project_path)
    book_type = resolve_book_type(None, project_fields)

    author_voice_path = book_root / "config" / "author-voice.md"
    if not author_voice_path.exists():
        raise SystemExit(f"Author voice file not found at {author_voice_path}")

    print(f"Book: {book_root.relative_to(REPO_ROOT)} ({book_type})")
    print(f"Author voice file: {author_voice_path.relative_to(REPO_ROOT)}")
    print("\nFollow the sample generation steps from WORKFLOW.md:\n")
    print(render_workflow_section("Sample Book Generation (author voice demonstration)"))
    print("\nIf you already generated samples, see also:")
    print(render_workflow_section("Sample Update"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Book pipeline helper CLI. Wraps key workflows from engine/agents/WORKFLOW.md.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser(
        "init",
        help="Create per-book directories and copy templates.",
    )
    init_parser.add_argument("book", help="Short name of the book under my-books/")
    init_parser.add_argument(
        "--type",
        choices=["fiction", "non-fiction", "nonfiction"],
        help="Book type. Required if not already set in config/PROJECT.md.",
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing template files when copying.",
    )
    init_parser.set_defaults(func=init_project)

    phase_parser = subparsers.add_parser(
        "phase",
        help="Show workflow guidance for a specific phase (0-5 or name).",
    )
    phase_parser.add_argument("book", help="Short name of the book under my-books/")
    phase_parser.add_argument("phase", help="Phase number or alias (import, init, draft, edit, review, publish).")
    phase_parser.set_defaults(func=run_phase)

    status_parser = subparsers.add_parser(
        "status",
        help="Summarize configuration and directory readiness.",
    )
    status_parser.add_argument("book", help="Short name of the book under my-books/")
    status_parser.set_defaults(func=summarize_status)

    samples_parser = subparsers.add_parser(
        "samples",
        help="Show steps for generating sample chapters based on author voice.",
    )
    samples_parser.add_argument("book", help="Short name of the book under my-books/")
    samples_parser.set_defaults(func=generate_samples)

    return parser


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
