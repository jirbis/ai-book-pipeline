# Event-driven book authoring on GitHub — Draft PR #31

Status: **opt-in; not activated**. The engine/skill lives in this repository;
private books should be in a separate manuscript repository.

This PR introduces a deterministic PR merge router, an issue-backed task queue,
optional GitHub Copilot assignment, and offline tests. An agent can then work
on the issue and propose its own PR. No manuscripts are changed by this PR.

## PR merge → gate → task

| Human-merged PR label | Required changes inside one book | Next |
| --- | --- | --- |
| `book:materials` | `books/<slug>/files/import/**` | Importer + Orchestrator → draft plan PR |
| `book:plan` | `books/<slug>/config/outline.md` or `plot.md` | Researcher → Writer → Editor → Critic, one chapter, at most 2 revisions, draft PR |
| `book:manuscript` | `books/<slug>/files/content/chapters/**` | Proofreader → draft PR |
| `book:proofread` | `books/<slug>/files/proofread/**` | HOLD. Never auto-publish or export to Kindle |

GitHub Action checks the authoritative PR via GitHub API rather than guessing
from title/body. **Exactly one known label** is required. It also checks a
human merge (`merged_by.type=User`), merge SHA, target `main`, a single book,
and essential artifacts for the stage. It rejects changes outside that book,
including renamed files originating in another book, and >300 changed files.

No automatically created or merely closed PR advances the book.
**Only an actual human merge** of an appropriate labeled PR does so.

## Configure in the PRIVATE manuscript repository

1. Install the following in the manuscript repo: `scripts/book_pipeline/router.py`,
   `scripts/book_pipeline/issue_worker.py`,
   `.github/workflows/book-transition-router.yml`, and
   the `book-authoring` skill, with authorized access to engine references.
   The workflow reacts to merges **in its own repository**, not another repo.
2. Protect `main` with required reviews and passing checks. Add labels:
   `book:materials`, `book:plan`, `book:manuscript` and `book:proofread`.
3. Set GitHub Actions repository variable `BOOK_PIPELINE_ENABLED=true` to
   enable task creation. By default the workflow job is **disabled**.
4. The standard path is `books/<slug>/`. If needed set variable
   `BOOKS_PREFIX=my-books` (only a one-segment directory slug).
5. Merge a **single-book materials PR** with `book:materials`. The workflow
   creates one task Issue with an idempotency marker and precise next-role
   instructions. Without any further configuration, it remains an unassigned
   issue for manual handoff and **does not call an LLM**.
6. To actually **start Copilot automatically**, configure a paid Copilot plan,
   enable its cloud agent for this repo, set variable
   `BOOK_PIPELINE_ASSIGN_COPILOT=true`, and add secret
   `COPILOT_USER_TOKEN`. The value must be a **user-to-server GitHub token**;
   an installation token or the default Actions `GITHUB_TOKEN` alone is not
   sufficient for this preview assignment API. This token needs the GitHub
   permissions required for agent issue assignment (Actions, Contents, Issues
   and Pull Requests read/write). Test against a private sample book.
7. Copilot processes the scoped issue, and proposes a PR with the requested
   draft plan/chapter/proofreading work. The **author** must review it, ensure
   the next `book:<gate>` label is attached, and merge only if approved.
   That merged PR triggers the next stage. Release remains human-only.

All cloud inference is a deliberate opt-in: unpublished or sensitive manuscripts
must not be processed by cloud agents without the author's approval.

## Replays and failure behavior

- Deterministic identity: SHA256(book + previous gate + merge SHA).
- The issue queue searches existing open/closed issues for the exact
  `<!-- book-pipeline-task:... -->` marker. It reuses an existing task;
  it does not create or reassign it again.
- Scans a bounded 1,000 issues; if that limit is reached without confirmation,
  it **fails closed** instead of risking duplicate work.
- GitHub Actions concurrency serializes runs for each PR number.
- If issue creation succeeds but Copilot assignment fails, the issue remains
  for **manual recovery**. No silent retry or duplicate work.
- Manual replay: GitHub Actions → Book pipeline - merged PR router → Run
  workflow → existing merged PR number. It is idempotent.

## Security, scope, remaining tasks

- The router has no write/LLM capability. Only the worker can create an issue,
  and only if the repo automation variable is enabled; assignment needs another
  opt-in variable and a user token. The main workflow permissions are
  `contents: read`, `pull-requests: read`, `issues: write`.
- Book files are never modified directly by the router/worker.
- Source prompts enforce **book-scoped changes, Draft PR and human review**,
  but the actual Copilot output must still be checked. A prompt is not an
  enforceable file-system sandbox; enforce branch protection and allowed path
  checks for output PRs before merging.
- This is an initial **single-chapter** routing mechanism, not a full
  multi-book scheduler or robust cross-provider retry engine.
- For a complete production pipeline, add a durable state journal,
  output validation, chapter sequence/scheduling, strict CI path guards,
  budgets/rate limits and optional Claude/Asgard executor integrations.
- The workflow was not activated and no GitHub Copilot account or PAT was
  connected by this PR.

**Dependency resolved:** PR #30 has been merged into `main`. PR #31 now
targets `main` directly and contains only its seven orchestration files.
Review and merge PR #31 separately; this does NOT enable agents or change books.

## References

- [GitHub Actions events and merged PRs](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
- [GitHub token event-trigger exception](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow)
- [Copilot issue-assignment API](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/use-cloud-agent-via-the-api)
- [GitHub Agentic Workflows](https://github.github.com/gh-aw/)
