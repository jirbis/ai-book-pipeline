# Features

This system delivers an end-to-end, file-first book pipeline with specialized AI roles, per-book workspaces, and repeatable automation. Each feature below is built from the documented workflow and agent responsibilities.

## Multi-phase workflow
- Six explicit phases cover import, initialization, drafting, editing, review, and publishing, ensuring every stage has clear inputs, outputs, and completion criteria. 【F:engine/agents/WORKFLOW.md†L5-L172】

## Role-based agent team
- Dedicated agents (Orchestrator, Researcher, Writer, Editor, Critic, Proofreader, Publisher, Importer) collaborate through defined triggers and responsibilities so each stage has an accountable owner. 【F:README.md†L44-L52】【F:engine/agents/AGENTS.md†L7-L107】

## Per-book workspace and templates
- Each book lives in its own `$BOOKS_ROOT/<book-short-name>/` directory with config, research, drafts, edits, reviews, proofread, and output folders, seeded from shared templates for fiction and non-fiction. 【F:engine/STRUCTURE.md†L13-L138】

## Import automation for existing materials
- An optional Importer scans files, auto-generates `PROJECT.md` and `outline.md`, distributes drafts and research into the workspace, and produces an import report, accelerating projects that start from existing content. 【F:engine/agents/WORKFLOW.md†L32-L172】【F:engine/agents/AGENTS.md†L520-L618】

## Research-to-draft production loop
- Researcher gathers facts, fact-checks drafts, and surfaces quotes/examples; Writer turns outlines and research into versioned chapter drafts with metadata and editor notes. 【F:engine/agents/AGENTS.md†L116-L200】【F:engine/agents/AGENTS.md†L209-L283】

## Editing, critique, and quality gates
- Editor delivers developmental, line, and copy edits; Critic runs structured reviews with verdicts and recommendations; Orchestrator advances or routes revisions based on quality status. 【F:engine/agents/AGENTS.md†L287-L360】【F:engine/agents/AGENTS.md†L380-L456】【F:engine/agents/AGENTS.md†L52-L110】

## Proofreading with author-voice preservation
- Proofreader performs multi-pass language, typography, consistency, fact-check, and publication-readiness checks while treating `author-voice.md` as authoritative to avoid eroding style. 【F:engine/agents/AGENTS.md†L623-L757】

## Structured handoffs and progress tracking
- Agents coordinate via standardized handoff files in `files/handoff/` and update per-book `config/progress.md`, keeping tasks, inputs, and decisions auditable. 【F:engine/agents/AGENTS.md†L63-L110】【F:engine/agents/AGENTS.md†L763-L803】

## One-command demo content
- `engine/demo.sh` plus the quickstart script populate sample fiction and non-fiction projects with ready-made Phase 1 → Phase 2 artifacts for fast walkthroughs and screenshots. 【F:docs/getting-started.md†L7-L39】

## GitHub-backed book authoring (portable skill)
- Store book workspaces inside a GitHub repository; keep drafts, research, reviews and author voice under version control. The optional standard-library `github_workspace.py` provides inspect, explicit book-branch creation, scoped book commits and explicitly approved pushes. Agents with GitHub connector permissions can instead create/update chapter files on a dedicated book branch and open Draft PRs for review. [Workflow and safeguards](../skills/book-authoring/references/github-workflow.md)
- GitHub collaboration does **not** automatically publish to Kindle or merge changes. The author remains in control of approval and release.

## Published-book examples
- A [book showcase](showcase.md) links to verifiable author-catalog entries, with Amazon Kindle listing URLs to be added after ASIN verification; it does not automatically attribute every book to this pipeline.
