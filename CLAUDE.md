# LLM Wiki

Personal knowledge base powered by LLM. Raw materials → structured wiki → queryable knowledge.

## Current Project State

- The Python package version is `0.1.4`.
- `AGENTS.md` is a symlink to `CLAUDE.md`; keep project instructions in this file path so both names stay aligned.
- The CLI supports single-file ingest, directory ingest, agentic querying, linting, large-document planning, and DAG-aware execution.
- Ingest now uses an agentic tool-calling loop for concept extraction: the model can search existing wiki pages, read candidate pages, and list pages before deciding whether to create or merge concepts.
- Query and ingest share the wiki tool implementations in `src/wiki_cli/tools.py`.
- Cross-reference refresh is graph-based: page `brief` frontmatter is used to build a lightweight relevance graph, then related pages are read for `## See also` updates and merge-candidate suggestions.
- Large-document execution processes chapters by topological level with parallel workers, uses per-page locks for merge safety, and runs a final new-page deduplication pass before cross-referencing.
- Token usage tracking is available across LLM commands and can save Markdown or HTML reports under `reports/`.
- The wiki currently includes both Codex/agent-system material and deep-learning pages generated from the example materials.

## Directory Layout

| Directory | Purpose | Mutability |
|-----------|---------|------------|
| `raw/` | Original materials (PDF, DOCX, HTML, images, notes) | **Immutable** — never edit after placing |
| `wiki/` | LLM-authored knowledge pages | Agent writes here |
| `reports/` | Query logs, lint reports, schema notes | Agent writes here |
| `templates/` | Page templates for scaffolding | Static |
| `examples/` | Example source documents for demos and tests | Agent may add examples when useful |
| `src/wiki_cli/` | Python CLI tool | Agent edits for CLI feature work |

## Page Naming Convention

- Lowercase, hyphenated, `.md` extension
- Example: `transformer-architecture.md`, `rlhf-explained.md`
- Filenames become wikilink targets: `[[transformer-architecture]]`

## Wikilink Convention

- Internal references use `[[page-name]]` syntax
- Always link without `.md` extension
- Every wiki page must include a `## See also` section at the bottom with relevant wikilinks

## Page Structure

Every wiki page follows this structure:

```
---
brief: One-sentence Chinese summary under 50 characters
---

# Title

> Source(s): raw/source-file.pdf

Body content with [[cross-references]].

## See also
- [[related-page]]
- [[another-page]]
```

## CLI Commands

```bash
wiki init                          # Initialize directory structure
wiki convert <file>                # Convert raw material to wiki pages (LLM-enhanced)
wiki convert <dir>                 # Batch convert all files in directory
wiki convert --large <file>        # Plan-and-execute for large documents
wiki convert --large --dry-run <f> # Plan only, no execution
wiki convert --large --plan-file <plan> <file> # Execute with an existing plan
wiki plan <file>                   # Generate conversion plan (ToC + DAG)
wiki execute <plan> --target <f>   # Execute a saved conversion plan
wiki lint [--strict]               # Check wiki structure health
wiki lint --model <name>           # LLM-enhanced lint
wiki query <question>              # Agentic tool-calling query against the wiki
```

All LLM commands show a thinking spinner with the model name during API calls. Use `-q`/`--quiet` to suppress it. All commands support `--token-report` (with `--token-report-format text|html`) to print a usage pivot after completion. `convert --large` and `execute` support `--workers N` for parallel chapter processing.

Supported ingest formats are `.md`, `.txt`, `.pdf`, `.docx`, `.html`, `.htm`, `.epub`, `.rtf`, `.png`, `.jpg`, and `.jpeg`. PDF conversion requires `pdftotext`, rich-text conversion requires `pandoc`, and image OCR requires `tesseract`.

## Three Core Operations

### Ingest

1. Place raw material in `raw/` with a clear filename
2. Run `wiki convert raw/<file>` — CLI handles conversion, tool-assisted concept extraction, merging, page generation, and cross-referencing
3. Review generated pages and instruction files in `reports/`
4. Keep generated pages aligned with the frontmatter + `## See also` structure

### Query

1. Run `wiki query "your question here"`
2. CLI uses the shared agentic tool-calling loop: LLM searches wiki pages, lists pages when useful, reads candidates, then synthesizes an answer with citations
3. Answer is recorded in `reports/queries.md` with [[page-name]] references
4. If the answer generates new knowledge, CLI may suggest creating a new wiki page

### Plan-and-Execute (Large Documents)

For documents too large for a single LLM call, use the plan-and-execute workflow:

1. **Plan phase**: LLM analyzes the document structure, builds a ToC, identifies chapter boundaries, and creates a DAG with dependencies
2. **Execute phase**: Each chapter is converted independently with parallel workers, respecting dependency order
3. **Final merge phase**: New pages are deduplicated, cross-references are refreshed, and index/log files are updated
4. Plans are saved to `reports/` and can be reused with `wiki execute`

Single command: `wiki convert --large <file>` runs both phases. Use `--workers` to control parallelism (default: 4).

### Token Usage Tracking

All commands support `--token-report` to print a usage summary after execution. Reports are saved to `reports/token-usage.md` (or `.html`). Use `--token-report-format html` for styled output. The tracker aggregates input/output/cache tokens per API call.

### Lint

1. Run `wiki lint` for static checks (no API calls)
2. Run `wiki lint --model <name>` for LLM-enhanced content analysis
3. Review findings in `reports/lint-report.md`

## Log Entry Format

Append to `wiki/log.md`:

```
## [YYYY-MM-DD] operation | Title
- What was done
- Which pages were affected
```

Operations: `ingest`, `query`, `lint`, `init`, `plan`, `execute`
