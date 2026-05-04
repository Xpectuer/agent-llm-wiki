# LLM Wiki

Personal knowledge base powered by LLM. Raw materials → structured wiki → queryable knowledge.

## Directory Layout

| Directory | Purpose | Mutability |
|-----------|---------|------------|
| `raw/` | Original materials (PDF, DOCX, HTML, images, notes) | **Immutable** — never edit after placing |
| `wiki/` | LLM-authored knowledge pages | Agent writes here |
| `reports/` | Query logs, lint reports, schema notes | Agent writes here |
| `templates/` | Page templates for scaffolding | Static |
| `src/wiki_cli/` | Python CLI tool | Static |

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
# Title

> Source(s): raw/source-file.pdf

Body content with [[cross-references]].

## See also
- [[related-page]]
- [[another-page]]
```

## CLI Commands

```bash
wiki init                # Initialize directory structure
wiki convert <file>      # Convert raw material to wiki pages (LLM-enhanced)
wiki convert <dir>       # Batch convert all files in directory
wiki lint [--strict]     # Check wiki structure health
wiki lint --model <name> # LLM-enhanced lint
wiki query <question>    # Ask a question against the wiki
```

## Three Core Operations

### Ingest

1. Place raw material in `raw/` with a clear filename
2. Run `wiki convert raw/<file>` — CLI handles conversion, concept extraction, merging, and cross-referencing
3. Review generated pages and instruction files in `reports/`

### Query

1. Run `wiki query "your question here"`
2. CLI finds relevant wiki pages, calls LLM for synthesis, records the answer
3. Check `reports/queries.md` for recorded queries

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

Operations: `ingest`, `query`, `lint`, `init`
