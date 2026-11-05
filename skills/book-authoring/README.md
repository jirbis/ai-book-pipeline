# Portable book-authoring skill

A small Agent Skills-style package for `jirbis/ai-book-pipeline`. It keeps `engine/` as the single source of truth and adds an explicit, scriptable interface for Claude Code, Codex, local orchestration, and other agents that can load `SKILL.md` and run Python.

## Install

The skill is located in `skills/book-authoring/`. Point a compatible agent at this folder, or copy the folder to that agent's supported skills directory. Keep a checkout of `ai-book-pipeline` accessible; the engine is intentionally **not** bundled.

If you install the skill outside the repository, set:

```bash
export BOOK_PIPELINE_REPO=/absolute/path/to/ai-book-pipeline
```

Use `--repo /absolute/path/to/ai-book-pipeline` instead of the environment variable if preferred.

## Examples

When working from the repo root:

```bash
python skills/book-authoring/scripts/book.py --books-root /tmp/author-books init example --type fiction --confirm-write
# Fill in example/config/PROJECT.md before using the status/phase commands.
python skills/book-authoring/scripts/book.py --books-root /tmp/author-books status example
python skills/book-authoring/scripts/book.py --books-root /tmp/author-books phase example draft
python skills/book-authoring/scripts/book.py --books-root /tmp/author-books validate-phase example 1
python skills/book-authoring/scripts/book.py --books-root /tmp/author-books final-check example
```

`--books-root` defaults to `BOOKS_ROOT` or the existing repo's `my-books/`. For safety, each book argument must be a **single slug**. Use `--books-root` to choose an external workspace. The adapter refuses `init` if that book directory already exists. It never exposes the original CLI's `--force` option.

## Adapter vs. engine

| Adapter command | Existing engine integration | Writes? |
| --- | --- | --- |
| `status` | `python -m engine.cli status` | No |
| `phase` | `python -m engine.cli phase` | No |
| `validate-phase` | `engine/agents/tools/validate_phase_{0..5}.py` | No (validator inspection) |
| `final-check` | `collect_chapter_numbers` and `collect_final_numbers` in `validate_final_chapters.py` | No |
| `init --confirm-write` | `python -m engine.cli init` | Yes, only for new slugs |

The existing publisher workflow remains unchanged. `final-check` does not run the original validator main routine because that routine creates a handoff file on failure.

## GitHub Copilot cloud-agent discovery

GitHub Copilot cloud agent discovers project skills in `.github/skills/`, `.claude/skills/`, or `.agents/skills/`, rather than automatically scanning arbitrary top-level `skills/` directories. A lightweight compatibility entrypoint lives at `.github/skills/book-authoring/SKILL.md`; it delegates to the canonical `skills/book-authoring/SKILL.md` and its existing scripts and references. Keep the canonical version authoritative.

This auto-discovery applies to the **repository containing the entrypoint**. To use Copilot in a separate private manuscript repository, install the skill into a supported skills directory of **that repository**, and give the agent access to the `ai-book-pipeline` engine checkout. Loading a skill alone does not launch a phase: the agent must be assigned a task or triggered by a workflow.

See [GitHub agent and phase execution](references/github-agents.md) for hosted execution options.

## GitHub-backed manuscripts

For books stored in a **GitHub repository**, set `BOOKS_ROOT` to the cloned repository's `books/` directory while keeping `BOOK_PIPELINE_REPO` pointed at the book pipeline engine. The [GitHub workflow guide](references/github-workflow.md) covers both an authenticated local Git clone and an agent using its GitHub connector.

The helper `scripts/github_workspace.py` supports `inspect` (read-only), `start` (opt-in local `book/<slug>/draft` branch), `commit-book` (opt-in changes **only** within `books/<slug>/`), and `push-branch` (explicitly authorized GitHub push). It never merges PRs or publishes to Amazon Kindle. It validates resolved push URLs, blocks ambiguous or redirected pushes, uses an explicit refspec, and skips local commit hooks; see the trust limitations in the GitHub workflow guide.

```bash
python skills/book-authoring/scripts/github_workspace.py --checkout /path/to/manuscript-repo inspect my-book
python skills/book-authoring/scripts/github_workspace.py --checkout /path/to/manuscript-repo start my-book --confirm-write
```

Use a private manuscript repository for unpublished books. Existing `my-books/` examples in the engine repository are not modified.

## Before enabling GitHub book automation

In the **private manuscript repository**, require the **`Book PR scope / scope`** status check for the default branch and enable **Require review from Code Owners** (or equivalent ruleset protection) for workflow and orchestration code. These protections **must be configured manually in GitHub Settings**; adding the files or merging the orchestration PR does not enable them.

See the root [deployment checklist](../../README.md#enable-event-driven-book-automation-private-repositories) and [event-driven orchestration guide](../../docs/book-event-orchestration.md). Keep `BOOK_PIPELINE_ENABLED` disabled until both protections have been verified.

## Tests

Run from the repository root:

```bash
python -m unittest discover -s tests -p 'test_*book*.py' -v
```

The adapter itself uses only Python's standard library. Existing phase validators import **PyYAML** via `engine/agents/tools/validation_utils.py`; install it with `python -m pip install PyYAML` before running `validate-phase` or the full integration test suite. GitHub Actions installs this engine dependency.

The integration tests create books only in temporary directories and do not touch `my-books/`. A dedicated GitHub Actions workflow runs them on pull requests.
