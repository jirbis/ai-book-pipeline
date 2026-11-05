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
Deletions of files in the permitted scope may accompany genuine edits. A
deletion-only PR, or a PR that only removes a required stage artifact without
adding/modifying/renaming another required artifact, does not unlock the gate.

No automatically created or merely closed PR advances the book.
**Only an actual human merge** of an appropriate labeled PR does so.

## Required repository protection before activation

**Do not set `BOOK_PIPELINE_ENABLED=true` until both protections below are
configured and verified in the private manuscript repository:**

1. **Required status check:** In **Settings → Rules → Rulesets** (or **Settings →
   Branches → Branch protection rules**), require
   `Book PR scope / scope` for merges into `main`. This check runs the
   read-only path guard. The workflow must first be merged to the private
   repository's default branch so that GitHub can recognize the status name.
2. **Required Code Owner review:** Install `.github/CODEOWNERS` covering
   `.github/workflows/`, `scripts/book_pipeline/` and `.github/CODEOWNERS`
   itself. Enable **Require review from Code Owners** or equivalent ruleset,
   require Pull Requests for `main`, and limit bypass rights. The PR author
   cannot approve their own change, so arrange an independent authorized
   reviewer or an explicit administrative review policy.

**These are GitHub repository settings, not automated by this PR.**
Neither the CODEOWNERS file nor a workflow by itself enforces the policy.
Also confirm your plan and repository type support the chosen protection
rules before enabling an autonomous agent.

### Mandatory Copilot token isolation (before enabling agent assignment)

Create an Environment called **`book-copilot-main`** in the **private manuscript
repository**, through **Settings → Environments → New environment**.

1. Under **Deployment branches and tags**, select **Selected branches and tags**
   and add **only the branch `main`**. Do not choose the unrestricted option
   or broadly allow protected branches and tags.
2. Add the user-to-server token as **Environment secret `COPILOT_USER_TOKEN`**.
   Do not store this PAT in repository or organization secrets. Remove any
   existing repository/organization-scoped copies.
3. Confirm that the GitHub plan supports Environment secrets for private
   repositories. If required reviewers are available, consider enabling them
   for extra control, noting that approval pauses automatic assignment.
4. Verify the main-branch restriction, secret isolation, branch protection,
   required book-scope check and Code Owner review **before** setting
   `BOOK_PIPELINE_ASSIGN_COPILOT=true`.

The workflow now has two jobs: `route` creates an Issue without the PAT,
then `assign_copilot` accesses the protected Environment **only on
`refs/heads/main`** when assignment is explicitly enabled. It rechecks that
the Issue is open, matches the routing marker, and was created by
`github-actions[bot]` before making the assignment. A task that already
exists is not re-assigned by replay. If the Environment is missing or
unrestricted, **do not enable assignment**. The PR cannot configure
environment settings or migrate secrets itself. See
[GitHub Environment security](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments).

## Configure in the PRIVATE manuscript repository

1. Install the following in the manuscript repo: `scripts/book_pipeline/router.py`,
   `scripts/book_pipeline/issue_worker.py`,
   `.github/workflows/book-transition-router.yml`, and
   the `book-authoring` skill, with authorized access to engine references.
   The workflow reacts to merges **in its own repository**, not another repo.
   Install the separate pre-merge `.github/workflows/book-pr-scope.yml`
   and require its **Book PR scope / scope** status in branch protection.
   Apply CODEOWNERS review protection for workflow/dispatcher paths.
2. Protect `main` with required reviews and passing checks (including
   `Book PR scope / scope`). Enable **Require review from Code Owners**
   or an equivalent repository ruleset, and restrict who can bypass it.
   The included `.github/CODEOWNERS` assigns workflow, router, worker,
   and test files to `@jirbis`. A CODEOWNERS file alone does not enforce
   approval requirements; configure branch protection yourself.
   Add labels:
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
   enable its cloud agent in this repo and complete the mandatory
   `book-copilot-main` Environment configuration above. Store
   `COPILOT_USER_TOKEN` **only as an Environment secret**, restrict that
   Environment to branch `main`, and only then set
   `BOOK_PIPELINE_ASSIGN_COPILOT=true`. The token must be a user-to-server
   GitHub token with the permissions required for Copilot issue assignment;
   the default Actions `GITHUB_TOKEN` does not replace it. Test against a
   private sample book before production.
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
  for **manual recovery**. No silent retry or duplicate work. Queue creation
  and privileged assignment are separate jobs; no PAT is exposed to routing.
- Manual replay: GitHub Actions → Book pipeline - merged PR router → Run
  workflow → existing merged PR number. It is idempotent.

## Security, scope, remaining tasks

- Security fix: the privileged post-merge dispatcher uses
  `pull_request_target: closed`, and checks out **only the repository
  default branch** with persisted checkout credentials disabled. It never
  executes the PR head or PR merge-ref. An event merely provides the PR
  number; the main-branch router fetches authoritative metadata.
- A separate read-only `pull_request_target` status check
  (`Book PR scope / scope`) validates a book-labeled PR's paths before
  merge, including rename origins and deletion-only PRs (while permitting
  scoped deletions alongside valid added/modified stage artifacts).
  Protect `main` by requiring this status; otherwise it is advisory.
- The router has no write/LLM capability. The unprivileged `route` job queues
  Issues using the limited `GITHUB_TOKEN` and **never receives the Copilot PAT**.
  Only the separate `assign_copilot` Environment job can use that token,
  on the `main` execution ref, with `contents: read` and `issues: read`.
  The workflow's routing permissions include `contents: read`,
  `pull-requests: read` and `issues: write` for queue creation.
- Book files are never modified directly by the router/worker.
- An issue with a matching task marker could be planted by a writer with
  Issue permissions and suppress an automated task; review task ownership
  on unexpected `already_created` results. A fake marker cannot authorize
  publication, but it can delay work.
- Source prompts enforce **book-scoped changes, Draft PR and human review**,
  but the actual Copilot output must still be checked. A prompt is not an
  enforceable file-system sandbox; enforce branch protection and allowed path
  checks for output PRs before merging.
- This is an initial **single-chapter** routing mechanism, not a full
  multi-book scheduler or robust cross-provider retry engine.
- For a complete production pipeline, add a durable state journal,
  output validation, chapter sequence/scheduling,
  budgets/rate limits and optional Claude/Asgard executor integrations.
- The workflow was not activated and no GitHub Copilot account or PAT was
  connected by this PR.

**Dependency resolved:** PR #30 has been merged into `main`. PR #31 now
targets `main` directly. Review and merge PR #31 separately; this does NOT
activate the workflow, enable agents, or change books.

## References

- [GitHub Actions events and merged PRs](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
- [GitHub token event-trigger exception](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow)
- [Copilot issue-assignment API](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/use-cloud-agent-via-the-api)
- [GitHub Agentic Workflows](https://github.github.com/gh-aw/)
