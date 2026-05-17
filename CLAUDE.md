# LLM Wiki

Personal knowledge base powered by LLM. Raw materials → structured wiki → queryable knowledge.

## Development Constraints
- NEVER skip git pre-commit unless user allows.
- If you do not know how to verify some part of code, ALWAYS ask user.
- After every code change, run the full test suite: `uv run pytest tests/ -v --tb=short`. Do not commit if any test fails.

## Current Project State

- The Python package version is `0.1.5`.
- `AGENTS.md` is a symlink to `CLAUDE.md`; keep project instructions in this file path so both names stay aligned.
- The CLI supports single-file ingest, directory ingest, agentic querying, and linting. `convert` auto-detects large documents and switches to plan-and-execute mode with DAG-aware parallel execution.
- Ingest now uses an agentic tool-calling loop for concept extraction: the model can search existing wiki pages, read candidate pages, and list pages before deciding whether to create or merge concepts.
- Query and ingest share the wiki tool implementations in `src/wiki_cli/tools.py`.
- Cross-reference refresh is graph-based: page `brief` frontmatter is used to build a lightweight relevance graph, then related pages are read for `## See also` updates and merge-candidate suggestions.
- Large-document execution processes chapters by topological level with parallel workers, uses per-page locks for merge safety, and runs a final new-page deduplication pass before cross-referencing.
- Token usage tracking is available across LLM commands and can save Markdown or HTML reports under the configured reports dir.
- The example wiki `codex-ml` includes both Codex/agent-system material and deep-learning pages.

## Directory Layout

| Directory | Purpose | Mutability |
|-----------|---------|------------|
| `src/wiki_cli/` | Python CLI tool | Agent edits for CLI feature work |
| `examples/` | Example wikis for testing — each subdirectory is a self-contained wiki root with `wiki/`, `raw/`, `reports/`, `templates/` | Agent may add examples when useful |
| `docs/` | Project docs — drafts, procs, lessons, modules, references, quality | Agent writes here |
| `docs/dashboard.md` | Workflow status dashboard | Agent updates |

### Example Wikis

```
examples/
  codex-ml/           # Codex agents + deep learning wiki
    wiki/             # 40+ LLM-authored pages
    raw/              # Source materials (immutable)
    reports/          # Query logs, plans, token reports
    templates/        # Page templates
  large-dl-survey.md  # Standalone example source doc
  simple-ml.md        # Standalone example source doc
```

Each wiki subdirectory is a standalone wiki root. Point `WIKI_DIR`/`RAW_DIR`/etc. at `examples/<name>/` to work with it:

```bash
WIKI_DIR=examples/codex-ml/wiki RAW_DIR=examples/codex-ml/raw \
  wiki query "什么是 transformer"
```

### Docs Subdirectories

| Subdirectory | Purpose |
|-------------|---------|
| `docs/drafts/` | Design phase — intake, idea, interview, plan sessions |
| `docs/procs/` | Execution phase — tdd/progress tracking |
| `docs/lessons/` | Lessons learned from past work |
| `docs/modules/` | Module/component documentation |
| `docs/references/` | Reference documents and external resources |
| `docs/quality/` | Quality reviews and audits |

<!-- BEGIN:module-docs -->
## Architecture & Module Docs

- Architecture overview: [ARCHITECTURE.md](ARCHITECTURE.md)
- Module index: [docs/modules/index.md](docs/modules/index.md)
- CLI: [cli.md](docs/modules/cli.md) | Config: [config.md](docs/modules/config.md) | LLM: [llm.md](docs/modules/llm.md)
- Convert: [convert.md](docs/modules/convert.md) | Planner: [planner.md](docs/modules/planner.md) | Executor: [executor.md](docs/modules/executor.md)
- Query: [query.md](docs/modules/query.md) | Tools: [tools.md](docs/modules/tools.md) | Llint: [llint.md](docs/modules/llint.md)
- Tracker: [tracker.md](docs/modules/tracker.md) | Models: [models.md](docs/modules/models.md)
<!-- END:module-docs -->

## 文档优先规则

在对代码库进行任何探索、bug 修复或功能修改之前，先阅读相关文档：

1. **先读 ARCHITECTURE.md** — 建立系统全局心智模型，理解模块边界和数据流
2. **再读相关模块文档** — 根据任务涉及的模块，阅读 `docs/modules/<module>.md` 了解接口、依赖关系和边界情况
3. **参考质量报告** — 查阅 `docs/quality/codebase-review.md` 了解已知的技术债务和安全热点

**执行顺序**: `ARCHITECTURE.md` → 相关 `docs/modules/*.md` → 开始探索/修复

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
wiki convert <file>                # Convert raw material to wiki pages (auto-detects large docs)
wiki convert <dir>                 # Batch convert all files in directory
wiki convert --large <file>        # Force plan-and-execute mode
wiki convert --no-large <file>     # Force standard single-pass mode
wiki convert --dry-run <file>      # Plan only, skip execution
wiki convert --plan-file <p> <f>   # Reuse an existing plan file
wiki lint [--strict]               # Check wiki structure health
wiki lint --model <name>           # LLM-enhanced lint
wiki query <question>              # Agentic tool-calling query against the wiki
```

All LLM commands show a thinking spinner with the model name during API calls. Use `-q`/`--quiet` to suppress it. All commands support `--token-report` (with `--token-report-format text|html`) to print a usage pivot after completion. `convert` supports `--workers N` for parallel chapter processing (plan-and-execute mode).

Supported ingest formats are `.md`, `.txt`, `.pdf`, `.docx`, `.html`, `.htm`, `.epub`, `.rtf`, `.png`, `.jpg`, and `.jpeg`. PDF conversion requires `pdftotext`, rich-text conversion requires `pandoc`, and image OCR requires `tesseract`.

## Three Core Operations

### Ingest

1. Place raw material in `raw/` with a clear filename
2. Run `wiki convert raw/<file>` — CLI auto-detects document size and chooses standard or plan-and-execute mode
3. Review generated pages and instruction files in `reports/`
4. Keep generated pages aligned with the frontmatter + `## See also` structure

For large documents, `convert` automatically switches to plan-and-execute: the LLM analyzes the document structure into chapters with DAG dependencies, processes each chapter in parallel (topological order), deduplicates new pages, and refreshes cross-references. Use `--large`/`--no-large` to override auto-detection, `--dry-run` for plan-only mode, `--plan-file` to reuse an existing plan, and `--workers N` to control parallelism (default: 4, or `WIKI_MAX_WORKERS` env var). Auto-detection threshold is 30,000 chars by default (`WIKI_LARGE_THRESHOLD` env var).

### Query

1. Run `wiki query "your question here"`
2. CLI uses the shared agentic tool-calling loop: LLM searches wiki pages, lists pages when useful, reads candidates, then synthesizes an answer with citations
3. Answer is recorded in `reports/queries.md` with [[page-name]] references
4. If the answer generates new knowledge, CLI may suggest creating a new wiki page

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

Operations: `convert`, `query`, `lint`, `init`

## Commit Conventions

- Always split commits by logical concern — never bundle unrelated changes.
- One commit = one coherent change (e.g., style/tooling separate from docs).
- For each commit, bump the package version by `0.0.1` in `pyproject.toml`.
