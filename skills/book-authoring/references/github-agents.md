# Run book phases and AI agents directly on GitHub

**Yes**, but distinguish three levels of execution. A GitHub repository is versioned storage; GitHub Actions supplies an execution runner; GitHub Copilot and other configured model runtimes supply the agent's generative intelligence.

## References (official)
- [GitHub Copilot agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)
- [GitHub Agentic Workflows](https://github.github.com/gh-aw/)
- [Agentic safe outputs for Draft PRs](https://github.github.com/gh-aw/reference/safe-outputs-pull-requests/)
- [GitHub Actions trigger behavior](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow)

## 1. Existing phase commands — deterministic (already implemented)

The engine CLI `python -m engine.cli phase <book> draft` **prints the phase instructions**. It does not write the chapter. `validate-phase` checks existing files; `final-check` checks chapter filenames. These can run in GitHub Actions (including manual `workflow_dispatch`) with read-only repository permissions after the workflow is merged to the repository's default branch.

For manuscripts in a **separate private GitHub repository**, the runner needs the manuscript checkout and access to the engine. Configure explicit `BOOK_PIPELINE_REPO` and `BOOKS_ROOT`. Do not log book text or pass it to cloud services without authorization.

## 2. GitHub Copilot coding agent — interactive writing and editorial tasks

GitHub Copilot cloud agent can work from an issue or prompt, create a branch/PR, edit Markdown chapters and respond to reviews. To make the book-authoring skill discoverable, place it in a supported project skill folder such as `.github/skills/book-authoring/`. This engine repository includes a forwarding entrypoint there; copy/install the skill into each separate book repository when needed.

Example issue task:

> For book `books/my-book`, act as WRITER for Phase 2 only. Read the book-authoring skill, current `PROJECT.md`, outline, author voice and source notes. Write `chapter-1-draft-v1.md` on a dedicated branch, add a review handoff, and open a Draft PR. Do not change any other book or publish.

Repeat as separate reviewable tasks for Researcher, Writer, Editor, Critic and Proofreader. A `SKILL.md` alone does **not** run the role automatically.

## 3. GitHub Agentic Workflows — hosted, automated phase runs

GitHub Agentic Workflows can execute instructions with configured engines (`copilot`, `claude`, `codex`, `gemini`) through GitHub Actions. Source workflow: `.github/workflows/<name>.md`, compiled to `<name>.lock.yml` using the `gh aw` extension. Enable a trigger and constrained safe outputs (for example Draft PR). Configure credentials and required account access. The compiled workflow must be reviewed before running.

Suggested design (NOT yet implemented in this repository):

1. Manual workflow with `book`, `phase`, and optional `chapter` parameters, not unrestricted shell input.
2. Check out the private manuscript repository and an immutable/approved version of the engine.
3. Load the author voice, scope, previous handoffs and the selected role, and only the files needed for that chapter.
4. Run the configured LLM with appropriate data-access permissions; output proposed changes only inside `books/<slug>/`.
5. Run existing deterministic validators; report errors/warnings honestly. Require author approval for phase advancement.
6. Save output as a Draft PR; no automatic merge, public release or KDP upload.

**Security:** GitHub-hosted agents are cloud runtimes. A local Asgard model will not automatically become available in GitHub Actions; using Asgard requires a trusted self-hosted runner or a secured integration and separate networking/PII policies. Repository visibility does not itself make content private from the selected external model provider. AI usage may incur plan/API or Actions charges.

## Minimum safe sequence

- **Now:** merge the reviewed skill into `main`, then assign a single sample chapter task to the Copilot coding agent in a **private test manuscript repo**.
- **Next:** create a dedicated manual phase-validator GitHub Actions workflow with `contents: read`.
- **Then:** build a constrained Agentic Workflow for a single phase and a single book branch. Keep each phase PR reviewable before advancing.

No cloud agent activation, secrets, token creation, GitHub Action deployment, or publishing is performed by adding this documentation.
