# AI Book Pipeline

**AI-powered, multi-agent book creation pipeline**  
Structured workflow for writing, editing, and publishing books with quality control and author voice preservation.  
**Open-source (MIT).**

Read the [feature list](./features.md) for a concise view of pipeline capabilities.

---

## What is this?

AI Book Pipeline is an open, reproducible framework for creating books using **role-based AI agents** and a **clearly defined production process**.

It is not a text generator.  
It is a **full book lifecycle pipeline** — from idea and research to reviewed, publication-ready output.

---

## What this is NOT

- ❌ Not a SaaS writing tool  
- ❌ Not a chat-based “write me a book” prompt  
- ❌ Not focused on UI or formatting

This project focuses on **process, structure, and quality**.

---

## Who is this for?

- ✍️ Authors (fiction & non-fiction) who want a clear, repeatable process  
- 📚 Experts and educators writing books as products or thought leadership  
- 🏢 Small publishers and editorial teams experimenting with AI workflows  
- 🤖 Engineers exploring real-world multi-agent orchestration

No vendor lock-in. No hidden services. Fully transparent.

---

## Kindle publishing examples

See [books by the project author](showcase.md): *The Huna Guide*, *Surviving Crypto*, and *Stop Talking. Start Building*. Titles are linked to their author-catalog entries. Direct Amazon Kindle listings are pending independent ASIN verification, and the showcase distinguishes author portfolio from documented pipeline-produced work.

## GitHub manuscript collaboration

Work on drafts and reviews **in a GitHub repository**, including private manuscripts: one book directory, a dedicated feature branch, commits scoped to that book, and a Draft Pull Request for author review. The [portable skill](../skills/book-authoring/SKILL.md) supports Git-backed local clones and explains [GitHub-connector operation](../skills/book-authoring/references/github-workflow.md). GitHub version control does not publish to Kindle.

## How it works (high level)

The pipeline models book creation as a sequence of explicit roles:

- **ORCHESTRATOR** — coordinates phases and handoffs  
- **RESEARCHER** — gathers sources and background material  
- **WRITER** — produces structured drafts  
- **EDITOR** — improves clarity, structure, and flow  
- **CRITIC** — challenges assumptions and weak spots  
- **PROOFREADER** — fixes language and consistency  
- **PUBLISHER** — validates readiness for release

Each role works on artifacts stored in a **per-book workspace**.

---

## Project structure

Each book lives in its own directory under `$BOOKS_ROOT/` (default: `my-books/`):

```text
$BOOKS_ROOT/ (default: my-books/)
  example-book/
    config/        # author voice, settings
    research/      # sources and notes
    drafts/        # raw chapters
    edits/         # edited versions
    reviews/       # critique and feedback
    output/        # final, publishable text

```

Nothing is hidden. Every step is inspectable.

Unlike black-box AI tools, this pipeline keeps **all intermediate artifacts**:
- research notes,
- drafts and revisions,
- editorial feedback,
- critique and validation results.

Each phase leaves a trace.  
Each decision is visible.  
Each output can be reviewed, adjusted, or replaced.

This makes the process:
- transparent,
- auditable,
- reproducible.

AI Book Pipeline is designed for **real production workflows**, where understanding *how* a result was created matters as much as the result itself.


## Quickstart (10 minutes)

1. Clone the repository  
2. Copy the example book folder  
3. Define your author voice  
4. Run the first agent step (research or writing)  
5. Iterate through the pipeline phases  

**Result:** a structured, reviewable chapter draft — not just generated text.

---

## Why this approach?

Most AI tools generate content.  
Very few finish work.

AI Book Pipeline is designed to:
- preserve author voice,
- enforce quality checks,
- make progress visible,
- produce results that survive editing and publishing.

This is how AI fits into real production workflows.

---

## License

This project is released under the **MIT License**.  
You are free to use it, modify it, and build on it — including for commercial work.

---

## About

Developed and maintained by **Jirbis GmbH**  
Specialists in AI-driven process automation and agent-based systems.

- GitHub Repository: [https://github.com/jirbis/ai-book-pipeline](https://github.com/jirbis/ai-book-pipeline) 
- Company: [Jirbis GmbH](https://jirbis.de)
