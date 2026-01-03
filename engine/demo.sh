#!/usr/bin/env bash

set -euo pipefail

# demo.sh — quick demo runner for the book pipeline
#
# This script bootstraps a book project from the templates in engine/book-templates/
# and drops stub content that represents Phase 1 (Init) and Phase 2 (Draft).
# It is meant for fast demos, screenshots, or GIF recordings and keeps everything
# local under my-books/.

usage() {
  cat <<'EOF'
Usage: bash engine/demo.sh [fiction|non-fiction|all] [--book <path>] [--reset]

Examples:
  bash engine/demo.sh fiction            # Populate my-books/sample-fiction-book
  bash engine/demo.sh non-fiction        # Populate my-books/sample-non-fiction-book
  bash engine/demo.sh all                # Populate both sample books
  bash engine/demo.sh fiction --book my-books/my-demo --reset

Options:
  --book <path>   Target book directory (default: sample-* paths for each type)
  --reset         Delete existing files/ directory before recreating demo output
  -h, --help      Show this help message
EOF
}

log() {
  printf "[demo] %s\n" "$1"
}

ensure_templates() {
  local book_dir="$1"
  local book_type="$2"

  mkdir -p "$book_dir/config"

  local shared_templates=(PROJECT.md author-voice.md progress.md review-checklist.md style-guide.md)
  for template in "${shared_templates[@]}"; do
    local src="engine/book-templates/${template}"
    if [[ -f "$src" ]]; then
      cp -n "$src" "$book_dir/config/"
    fi
  done

  if [[ "$book_type" == "fiction" ]]; then
    cp -n engine/book-templates/fiction/*.md "$book_dir/config/" 2>/dev/null || true
  else
    cp -n engine/book-templates/non-fiction/*.md "$book_dir/config/" 2>/dev/null || true
  fi
}

reset_files() {
  local book_dir="$1"
  if [[ -d "$book_dir/files" ]]; then
    rm -rf "$book_dir/files"
  fi
}

ensure_working_tree() {
  local book_dir="$1"
  mkdir -p "$book_dir/files/content/chapters" \
    "$book_dir/files/research" \
    "$book_dir/files/edits" \
    "$book_dir/files/reviews" \
    "$book_dir/files/handoff" \
    "$book_dir/files/proofread" \
    "$book_dir/files/output" \
    "$book_dir/files/import"
}

phase_stub_content() {
  local book_dir="$1"
  local book_type="$2"
  local book_name
  book_name="$(basename "$book_dir")"

  cat > "$book_dir/files/handoff/demo-phase-log.md" <<EOF
# Demo Phase Log — ${book_name}

**Phases covered**: Phase 1 (Init) ✅ → Phase 2 (Draft) ✅

## Phase 1 — Initialization snapshot
- Templates copied into config/
- Baseline outline locked for the first chapter
- Task handed from ORCHESTRATOR to WRITER with a tiny deliverable

## Phase 2 — Draft snapshot
- Writer produced a short sample chapter draft
- Progress markers updated for quick screenshots
- Ready to hand off to EDITOR or CRITIC in a real run
EOF

  cat > "$book_dir/files/content/chapters/chapter-0-outline.md" <<EOF
# Chapter 0 — Demo Outline (${book_type^})

## Goal
Set the tone and scope for a 2–3 chapter book sprint.

## Beats
1. Hook the reader with a promise of value.
2. Introduce the main tension or thesis.
3. Preview how the next chapter delivers on the promise.

## Notes
- Keep it under 250 words so the draft renders quickly during demos.
- Emphasize the "Phase 1 → Phase 2" handoff so screenshots show progress.
EOF

  if [[ "$book_type" == "fiction" ]]; then
    cat > "$book_dir/files/content/chapters/chapter-1-draft-v1.md" <<'EOF'
# Chapter 1 — Lanterns in the Harbor

<!-- METADATA
version: 1
status: draft
words: 245
created: demo-run
modified: demo-run
-->

Mira coasted along the docks with a lantern that flickered like a heartbeat. The harbor's brass cranes groaned in the fog, and every rusted chain sang a note she had not yet translated. Tonight she carried a sealed note from the Editor Guild—orders to find a storyteller before dawn.

She paused at Slip Seven, where an old submersible slept beneath tarps. A kid in oil-stained overalls leaned out. "You lost?" he asked.

"Looking for someone who can turn riddles into roads," Mira answered. The boy laughed and pointed to a crooked warehouse with a single light.

Inside, the Writer sorted scraps of dialogue into jars labeled *hope*, *risk*, and *twist*. "You brought the brief?" they asked.

Mira set the lantern down. "Phase Two starts now. Give me six paragraphs that prove the harbor still dreams."

The Writer grinned. "Then let's wake it up."

---

<!-- END OF CHAPTER -->
EOF

    cat > "$book_dir/files/research/chapter-1-research.md" <<'EOF'
# Research Notes — Demo Fiction Chapter

## Atmosphere cues
- Brass machinery and foghorns create an industrial fairytale mood.
- Harbor lanterns give warm/cool contrast for screenshots.

## Character fragments
- Mira: courier who translates mechanical sounds.
- Writer: collects scraps of dialogue, uses jars as props.

## Sensory anchors
- Sounds: groaning cranes, chains humming.
- Smell: sea salt mixed with hot oil from submersibles.

Use these lines to annotate GIF captions or lower-third notes.
EOF
  else
    cat > "$book_dir/files/content/chapters/chapter-1-draft-v1.md" <<'EOF'
# Chapter 1 — Sketching the Idea in 20 Minutes

<!-- METADATA
version: 1
status: draft
words: 260
created: demo-run
modified: demo-run
-->

> **Purpose:** Show how the pipeline moves from a filled-out PROJECT.md to a usable first-draft page in under half an hour.

1. **Frame the problem.** Define the reader's pain point in two sentences and link it to the book's promise.
2. **Pick a single case study.** Use a real or hypothetical team sprint and include one metric (cycle time, defects, or throughput).
3. **Note the constraint.** Mention what you are deliberately *not* covering in this short pass.
4. **Call the next step.** Suggest what Researcher should validate before editing (e.g., citation or benchmark).

This stub is intentionally short so a screen recording shows the transition from outline → draft without long waits. Replace the numbered bullets with prose once Researcher signs off.

---

<!-- END OF CHAPTER -->
EOF

    cat > "$book_dir/files/research/chapter-1-research.md" <<'EOF'
# Research Notes — Demo Non-Fiction Chapter

| Fact or Check | Source | Confidence |
|---------------|--------|------------|
| Teams that shorten feedback loops improve delivery lead time. | Accelerate (Forsgren et al.) | ⭐⭐⭐⭐ |
| Lightweight demos help align stakeholders before editing. | Internal workshop notes | ⭐⭐⭐ |
| A 20-minute outline-to-draft sprint keeps momentum high for small teams. | Process retros (sample) | ⭐⭐⭐ |

Use these bullets to mark what the Researcher signs off before the Editor polishes.
EOF
  fi

  cat > "$book_dir/files/output/demo-summary.md" <<EOF
# Demo Summary for ${book_name}

This project now contains stub outputs for the first two phases so you can record a walkthrough quickly.

## Files created
- files/handoff/demo-phase-log.md — quick narrative of Phase 1 → Phase 2
- files/content/chapters/chapter-0-outline.md — outline-sized kick-off
- files/content/chapters/chapter-1-draft-v1.md — short draft ready for screenshots
- files/research/chapter-1-research.md — supporting notes for the first chapter

## Suggested next steps
- Open config/PROJECT.md to personalize the title and scope.
- Run a screen recording while opening the outline and draft to show the transition.
- Hand off to EDITOR or CRITIC by dropping a comment in files/handoff/.
EOF
}

run_demo() {
  local mode="$1"
  local book_dir="$2"
  local reset_requested="$3"

  log "Setting up ${mode} demo in ${book_dir}"
  ensure_templates "$book_dir" "$mode"

  if [[ "$reset_requested" == "true" ]]; then
    log "Resetting files directory"
    reset_files "$book_dir"
  fi

  ensure_working_tree "$book_dir"
  phase_stub_content "$book_dir" "$mode"
  log "Demo content ready under ${book_dir}/files"
}

main() {
  if [[ $# -eq 0 ]]; then
    usage
    exit 0
  fi

  local mode="$1"
  shift || true

  local book_dir=""
  local reset_requested="false"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --book)
        book_dir="$2"
        shift 2
        ;;
      --reset)
        reset_requested="true"
        shift
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        echo "Unknown option: $1" >&2
        usage
        exit 1
        ;;
    esac
  done

  case "$mode" in
    fiction)
      : "${book_dir:="my-books/sample-fiction-book"}"
      run_demo "fiction" "$book_dir" "$reset_requested"
      ;;
    non-fiction)
      : "${book_dir:="my-books/sample-non-fiction-book"}"
      run_demo "non-fiction" "$book_dir" "$reset_requested"
      ;;
    all)
      local fiction_dir="${book_dir:-my-books/sample-fiction-book}"
      local non_fiction_dir="${book_dir:-my-books/sample-non-fiction-book}"
      run_demo "fiction" "$fiction_dir" "$reset_requested"
      run_demo "non-fiction" "$non_fiction_dir" "$reset_requested"
      ;;
    *)
      echo "Mode must be 'fiction', 'non-fiction', or 'all'." >&2
      usage
      exit 1
      ;;
  esac
}

main "$@"
