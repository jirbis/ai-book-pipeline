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

## Tests

Run from the repository root:

```bash
python -m unittest discover -s tests -p 'test_book_authoring_skill.py' -v
```

The adapter itself uses only Python's standard library. Existing phase validators import **PyYAML** via `engine/agents/tools/validation_utils.py`; install it with `python -m pip install PyYAML` before running `validate-phase` or the full integration test suite. GitHub Actions installs this engine dependency.

The integration tests create books only in temporary directories and do not touch `my-books/`. A dedicated GitHub Actions workflow runs them on pull requests.
