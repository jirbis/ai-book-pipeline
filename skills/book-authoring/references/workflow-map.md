# Book pipeline workflow and authority map

The authoritative specification lives in `engine/agents/WORKFLOW.md`, `engine/agents/AGENTS.md`, and the individual agent prompts. Refer to those files instead of copying their full content into this skill.

| Phase | Lead roles | Required evidence | Gate |
| --- | --- | --- | --- |
| 0 — Import | Importer, Orchestrator | Original materials backed up, `files/import/import-report.md`, outline and PROJECT | Confirm classification and duplicates with author |
| 1 — Init | Orchestrator, Writer | `config/PROJECT.md`, `config/progress.md`, outline, style/author voice | Author agrees scope and outline |
| 2 — Draft | Researcher (non-fiction), Writer | `files/research/`, `chapter-N-draft-v1.md`, source notes and handoffs | Facts and missing chapters reviewed |
| 3 — Edit | Editor, Writer | Revision history, edit reports, `chapter-N-final.md` after copy edit | Structural, line and copy edits complete |
| 4 — Review | Critic, Author, Proofreader | `files/reviews/`, `files/proofread/`, corrected canonical finals | Author approval and completed review |
| 5 — Publish | Publisher, Orchestrator | Canonical chapter finals, exports in `files/output/` | Explicit publication authorization |

## Role references

Load the relevant document from `engine/agents/`:

- `orchestrator.md`: coordinate phases and handoffs.
- `importer.md`: import and classify existing sources while protecting originals.
- `researcher.md`: verify facts and keep source trail.
- `writer.md`: draft according to outline and author voice.
- `editor.md`: developmental, line and copy edits.
- `critic.md`: independent criticism and consistency checks.
- `proofreader.md`: final corrections without flattening author voice.
- `publisher.md`: assemble and export after gates.

When the file naming or gate rules in these notes differ from the current engine, **the current engine wins**. Never infer approval solely from passing filesystem validators.
