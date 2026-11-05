---
name: book-authoring
description: Write, research, edit, review, and organize fiction and non-fiction books in a GitHub repository using the ai-book-pipeline engine, with phase gates, author-voice preservation, and Pull Request review.
---

# GitHub entrypoint for book-authoring

**Read the canonical skill instructions from `skills/book-authoring/SKILL.md` in the repository root before acting.** Also read the phase map at `skills/book-authoring/references/workflow-map.md` and GitHub guidance at `skills/book-authoring/references/github-workflow.md` as relevant. Do not duplicate or replace these instructions.

- Determine the authorized book directory and user-requested phase. Read `engine/agents/WORKFLOW.md` and the relevant role file.
- If book files are stored in a separate manuscript repository, first locate its own installed skill and accessible engine checkout. Do not assume that this repository's book directories are the intended target.
- Work on a book-specific branch or Draft Pull Request, not directly on `main`. Preserve `author-voice.md` and earlier chapter revisions.
- Treat `phase` as a **guidance lookup**, `validate-phase` as validation, and `final-check` as filename checking. They do not call a language model or write a book by themselves.
- Writing and publication are distinct approvals. **Do not merge**, push, release to Kindle/KDP, or edit existing manuscript files unless the requested operation is explicitly authorized.
- For GitHub-hosted agent orchestration, see `skills/book-authoring/references/github-agents.md`.
