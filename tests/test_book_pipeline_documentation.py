"""Ensure operational documentation stays in English and states required gates.

Do not scan manuscripts or author source material under my-books/.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CYRILLIC = re.compile(r"[\u0400-\u052F]")


class BookDocumentationTests(unittest.TestCase):
    def test_operational_documentation_has_no_cyrillic(self):
        files = [
            REPO / "README.md",
            REPO / "CLAUDE.md",
            REPO / "CODEX.md",
            REPO / "CODEX_PLAN_REPORT.md",
        ]
        for directory in ("docs", "skills/book-authoring", "engine"):
            files.extend((REPO / directory).rglob("*.md"))
        self.assertGreater(len(files), 20)
        for path in files:
            with self.subTest(path=str(path.relative_to(REPO))):
                content = path.read_text(encoding="utf-8")
                match = CYRILLIC.search(content)
                self.assertIsNone(match, "Operational documentation must be written in English")

    def test_readme_explains_both_required_repository_settings(self):
        readme = (REPO / "README.md").read_text(encoding="utf-8")
        self.assertIn("Book PR scope / scope", readme)
        self.assertIn("Require review from Code Owners", readme)
        self.assertIn("BOOK_PIPELINE_ENABLED=true", readme)
        self.assertIn("manual GitHub repository administration steps", readme)

    def test_orchestration_guide_requires_protection_before_activation(self):
        guide = (REPO / "docs/book-event-orchestration.md").read_text(encoding="utf-8")
        self.assertIn("Do not set", guide)
        self.assertIn("Book PR scope / scope", guide)
        self.assertIn("Require review from Code Owners", guide)


if __name__ == "__main__":
    unittest.main()
