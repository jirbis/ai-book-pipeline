# CODEX.md — Instructions for Codex

Codex must follow the same instructions defined for Claude Code. Treat `CLAUDE.md` as the primary reference; this file highlights how to mirror that guidance when running through Codex.

## Core workflow alignment
- Work **per book**: all generated content lives in `my-books/<book>/config/` and `my-books/<book>/files/`. Never write to `engine/book-templates/` or legacy `engine/files/` paths.
- Treat files in `engine/book-templates/` as **read-only templates**; copy them into `my-books/<book>/config/` before editing.
- The **canonical chapter handoff** after copy edit is `my-books/<book>/files/content/chapters/chapter-N-final.md`. Proofreader updates that same file; publisher assembles only from these finals.
- Before export, run `python engine/agents/tools/validate_final_chapters.py my-books/<book>` to block publication if any finals are missing.
- Always consult `engine/agents/WORKFLOW.md`, `engine/agents/AGENTS.md`, and the relevant agent file (writer/editor/critic/proofreader/publisher) for phase rules and naming.

## Setup and kickoff
1. Create the per-book layout (manual or via `python -m engine.cli init <book> --type fiction|non-fiction`).
2. Copy templates from `engine/book-templates/` into `my-books/<book>/config/` and fill `PROJECT.md`.
3. Read `engine/agents/WORKFLOW.md` and start orchestration from Codex with the same prompts used in Claude (initialize the project in `my-books/<book>/` per the workflow).
4. Track progress in `my-books/<book>/config/progress.md` and keep handoff notes in `files/handoff/`.

## Phase cheat sheet (must match WORKFLOW)
- **Phase 0: Import (optional)**
  - Input: `files/import/**/*.{md,txt,docx}`
  - Output: generated `config/PROJECT.md`, `config/outline.md`, sorted drafts/research/notes under `files/`, `files/import/import-report.md`.

- **Phase 1: Init**
  - Read `config/PROJECT.md`, `config/outline.md` (or template).
  - Create/update `config/progress.md`, confirm book type, and set chapter plan.

- **Phase 2: Draft**
  - Non-fiction: gather facts into `files/research/chapter-N-research.md`.
  - Draft chapter text to `files/content/chapters/chapter-N-draft-v1.md`, following `config/style-guide.md` and `config/author-voice.md`.

- **Phase 3: Edit (developmental → line → copy)**
  - Edit drafts through `chapter-N-draft-v2.md` / `chapter-N-draft-v3.md` as needed.
  - After copy edit, write `chapter-N-final.md` in `files/content/chapters/` — this is the **only** canonical file proofreader and publisher consume.
  - Update editing reports in `files/edits/` and progress status.

- **Phase 4: Review & Proofread**
  - Critic reviews `chapter-N-final.md` and writes to `files/reviews/`.
  - Proofreader reads/writes the same `chapter-N-final.md`, logging passes in `files/proofread/`. Keep author voice intact using `config/author-voice.md`.

- **Phase 5: Publish**
  - Run `python engine/agents/tools/validate_final_chapters.py my-books/<book>`; resolve missing finals before proceeding.
  - Assemble only `files/content/chapters/chapter-*-final.md` (plus front/back matter) into `files/output/` formats.

## Key files to read first
1. `engine/STRUCTURE.md` — structure overview
2. `engine/agents/WORKFLOW.md` — authoritative phase details
3. `engine/agents/AGENTS.md` — agent responsibilities
4. `engine/agents/INTEGRATION.md` — tool usage and chapter naming
5. `my-books/<book>/config/PROJECT.md` — book metadata and scope

## Sample commands (Codex)
- Initialize: `codex "Initialize book project in my-books/<book>/ according to WORKFLOW.md"`
- Write draft: `codex "Write chapter 3 per outline in my-books/<book>/config/outline.md; save to files/content/chapters/chapter-3-draft-v1.md"`
- Copy edit: `codex "Copy edit chapter-3-draft-v3.md and publish chapter-3-final.md for proofreading"`
- Validate finals before publish: `python engine/agents/tools/validate_final_chapters.py my-books/<book>`

## When problems arise
- Verify `config/` and `files/` exist for the book and that `PROJECT.md` is filled.
- Ensure chapter numbering is consistent so `chapter-N-final.md` aligns with outline and validator checks.
- Re-read `WORKFLOW.md` for the current phase rules before resuming work.

**Codex runs must stay synchronized with Claude Code by following the canonical workflow and file naming above.**
