# Getting Started (One-Command Demo)

This short guide drops ready-to-screenshot outputs into the sample projects so you can record a quick walkthrough of Phase 1 → Phase 2.

![Quick demo flow](assets/getting-started-flow.svg)

## TL;DR commands

Run from the repository root.

```bash
# Fiction demo (resets sample files)
bash engine/demo.sh fiction --reset

# Non-fiction demo
bash engine/demo.sh non-fiction --reset

# Populate both in one go
bash engine/demo.sh all --reset
```

After each command, you will see ready-made files under `$BOOKS_ROOT/sample-*/files` (default root: `my-books/`):

- `files/handoff/demo-phase-log.md` — short narrative of Phase 1 → Phase 2
- `files/content/chapters/chapter-0-outline.md` — outline stub
- `files/content/chapters/chapter-1-draft-v1.md` — draft stub (fiction or non-fiction tone)
- `files/research/chapter-1-research.md` — supporting notes
- `files/output/demo-summary.md` — recap and suggested next steps

Open these files for quick screenshots or GIFs; they load instantly and keep the "Phase 1 → Phase 2" story visible.

## What the demo script does

`engine/demo.sh` copies the templates from `engine/book-templates/` into the target project, builds the `files/` tree, and seeds stub content that represents:

- **Phase 1 (Init):** outline prepared, handoff log recorded.
- **Phase 2 (Draft):** a short sample chapter plus matching research notes.

Use `--book <path>` to point at a different project directory if you want to demo against a custom folder.
