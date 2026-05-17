"""CLI entry point for wiki — powered by Click."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import click

from .config import Config, load_config
from .tracker import get_tracker


@click.group()
@click.option("--project-root", default=".", help="Project root directory")
@click.pass_context
def cli(ctx: click.Context, project_root: str) -> None:
    """LLM-powered personal wiki CLI."""
    ctx.ensure_object(dict)
    ctx.obj["root"] = Path(project_root).resolve()


@cli.command()
@click.pass_context
def init(ctx: click.Context) -> None:
    """Initialize wiki directory structure."""
    root = ctx.obj["root"]
    config = _init_config(root)

    # Create directories
    dirs = [config.raw_dir, config.wiki_dir, config.reports_dir, config.templates_dir]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        gitkeep = d / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.touch()
            click.echo(f"  Created {d}/")

    # Instantiate wiki files from templates
    today = date.today().isoformat()

    _init_from_template(
        config.templates_dir / "index.md",
        config.wiki_dir / "index.md",
        replacements={"{date}": today},
    )

    _init_from_template(
        config.templates_dir / "log.md",
        config.wiki_dir / "log.md",
        replacements={"{date}": today},
    )

    # Create report files
    for name in ("queries.md", "lint-report.md"):
        dest = config.reports_dir / name
        if not dest.exists():
            src = config.templates_dir / name
            if src.exists():
                _init_from_template(src, dest, replacements={"{date}": today})
            else:
                dest.write_text(f"# {Path(name).stem.title()}\n", encoding="utf-8")
                click.echo(f"  Created {dest}")

    # Create schema-note.md if not exists
    schema_note = config.reports_dir / "schema-note.md"
    if not schema_note.exists():
        schema_note.write_text(
            "# Schema Note\n\n> Explain your organizational decisions here.\n", encoding="utf-8"
        )
        click.echo(f"  Created {schema_note}")

    # Create CLAUDE.md if not exists
    claude_md = root / "CLAUDE.md"
    if not claude_md.exists():
        _create_claude_md(claude_md, today)
        click.echo(f"  Created {claude_md}")

    # Create AGENTS.md symlink to CLAUDE.md if not exists
    agents_md = root / "AGENTS.md"
    if not agents_md.exists():
        agents_md.symlink_to(claude_md.name)
        click.echo(f"  Created {agents_md} -> {claude_md.name}")

    click.echo("\nWiki initialized successfully.")


@cli.command()
@click.argument("target", type=click.Path(exists=True))
@click.option("--title", default=None, help="Override page title")
@click.option("--model", default=None, help="LLM model to use")
@click.option(
    "--large/--no-large",
    default=None,
    help="Force plan-and-execute on/off (default: auto-detect based on document size)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Plan only, do not execute (for use with plan-and-execute mode)",
)
@click.option(
    "--workers",
    default=None,
    type=int,
    help="Max parallel workers (default: 4 or WIKI_MAX_WORKERS)",
)
@click.option(
    "--plan-file",
    default=None,
    type=click.Path(exists=True),
    help="Use existing plan file (skip plan phase)",
)
@click.option(
    "--token-report",
    is_flag=True,
    default=False,
    help="Show token usage pivot report after conversion",
)
@click.option(
    "--token-report-format",
    type=click.Choice(["text", "html"]),
    default="text",
    help="Token report output format",
)
@click.option("-q", "--quiet", is_flag=True, default=False, help="Suppress spinner output")
@click.pass_context
def convert(
    ctx: click.Context,
    target: str,
    title: str | None,
    model: str | None,
    large: bool | None,
    dry_run: bool,
    workers: int | None,
    plan_file: str | None,
    token_report: bool,
    token_report_format: str,
    quiet: bool,
) -> None:
    """Convert raw material(s) to wiki pages (LLM-enhanced).

    Automatically detects large documents and switches to plan-and-execute mode.
    Use --large / --no-large to override the auto-detection.
    """
    from .convert import convert_file, run_convert

    if token_report:
        get_tracker().reset()

    config = _load_config_with_override(ctx, model, quiet=quiet)
    target_path = Path(target).resolve()

    if target_path.is_dir():
        # Directory: always single-pass per file (plan-and-execute not supported for dirs)
        files = sorted(
            f
            for f in target_path.iterdir()
            if f.is_file()
            and f.suffix.lower()
            in {
                ".md",
                ".txt",
                ".pdf",
                ".docx",
                ".html",
                ".htm",
                ".epub",
                ".rtf",
                ".png",
                ".jpg",
                ".jpeg",
            }
        )
        if not files:
            click.echo(f"No supported files found in {target_path}")
            _token_report(config, token_report, token_report_format)
            return
        click.echo(f"Processing {len(files)} file(s) from {target_path}/")
        for f in files:
            click.echo(f"\n{'=' * 50}")
            click.echo(f"File: {f.name}")
            click.echo(f"{'=' * 50}")
            run_convert(config, f, title=title)
    else:
        # Single file: determine whether to use plan-and-execute
        if large is None:
            # Auto-detect: extract text and check size
            text = convert_file(target_path)
            large = len(text) > config.large_threshold
            mode = "plan-and-execute" if large else "standard"
            click.echo(
                f"Document: {len(text):,} chars (threshold: {config.large_threshold:,}). Using {mode} mode.\n"
            )
        elif large:
            # Force plan-and-execute: extract text for the planner
            text = convert_file(target_path)

        if large:
            actual_workers = workers or config.max_workers

            if plan_file:
                from .planner import load_plan

                plan = load_plan(Path(plan_file))
            else:
                from .planner import describe_plan, plan_document, save_plan

                click.echo("[Plan] Analyzing document structure...")
                plan = plan_document(config, text, target_path.name)
                plan_path = save_plan(plan, config)
                click.echo(f"Plan saved to {plan_path}")
                click.echo(describe_plan(plan))

            if dry_run:
                _token_report(config, token_report, token_report_format)
                return

            from .executor import execute_plan, merge_all_results

            results = execute_plan(config, plan, text, max_workers=actual_workers)
            merge_all_results(config, results, plan)
        else:
            run_convert(config, target_path, title=title)

    _token_report(config, token_report, token_report_format)


@cli.command()
@click.option("--strict", is_flag=True, help="Exit with error code on any failure")
@click.option("--model", default=None, help="Enable LLM-enhanced lint with specified model")
@click.option(
    "--token-report", is_flag=True, default=False, help="Show token usage pivot report after lint"
)
@click.option(
    "--token-report-format",
    type=click.Choice(["text", "html"]),
    default="text",
    help="Token report output format",
)
@click.option("-q", "--quiet", is_flag=True, default=False, help="Suppress spinner output")
@click.pass_context
def lint(
    ctx: click.Context,
    strict: bool,
    model: str | None,
    token_report: bool,
    token_report_format: str,
    quiet: bool,
) -> None:
    """Check wiki structure health (static + optional LLM)."""
    from .llint import run_lint

    if token_report:
        get_tracker().reset()

    config = _load_config_with_override(ctx, model, quiet=quiet)
    use_llm = model is not None
    run_lint(config, use_llm=use_llm, strict=strict)

    _token_report(config, token_report, token_report_format)


@cli.command()
@click.argument("question", nargs=-1, required=True)
@click.option("--model", default=None, help="LLM model to use")
@click.option(
    "--token-report", is_flag=True, default=False, help="Show token usage pivot report after query"
)
@click.option(
    "--token-report-format",
    type=click.Choice(["text", "html"]),
    default="text",
    help="Token report output format",
)
@click.option("-q", "--quiet", is_flag=True, default=False, help="Suppress spinner output")
@click.pass_context
def query(
    ctx: click.Context,
    question: tuple[str, ...],
    model: str | None,
    token_report: bool,
    token_report_format: str,
    quiet: bool,
) -> None:
    """Ask a question against the wiki."""
    from .query import run_query

    if token_report:
        get_tracker().reset()

    config = _load_config_with_override(ctx, model, quiet=quiet)
    q = " ".join(question)
    run_query(config, q)

    _token_report(config, token_report, token_report_format)


# --- Token report helper ---


def _token_report(config: Config, enabled: bool, fmt: str = "text") -> None:
    """Print and save token usage report if enabled."""
    if not enabled:
        return
    tracker = get_tracker()
    ext = "html" if fmt == "html" else "md"
    path = tracker.save_report(str(config.reports_dir / f"token-usage.{ext}"))
    print(f"Token report saved to {path}")


# --- Helpers ---


def _init_config(root: Path) -> Config:
    """Create a config for init (doesn't require API key)."""
    return Config(
        api_key="",
        model="",
        base_url=None,
        wiki_dir=root / "wiki",
        raw_dir=root / "raw",
        reports_dir=root / "reports",
        templates_dir=root / "templates",
        project_root=root,
    )


def _load_config_with_override(
    ctx: click.Context, model: str | None, quiet: bool = False
) -> Config:
    """Load config with optional model override and quiet flag."""
    import os

    root = ctx.obj["root"]
    if model:
        os.environ["WIKI_MODEL"] = model
    config = load_config(root)
    config.quiet = quiet
    return config


def _init_from_template(src: Path, dest: Path, replacements: dict[str, str] | None = None) -> None:
    """Copy template to destination with placeholder replacements."""
    if dest.exists():
        click.echo(f"  Already exists: {dest}")
        return
    if not src.exists():
        click.echo(f"  Template not found: {src}, skipping")
        return

    content = src.read_text(encoding="utf-8")
    if replacements:
        for old, new in replacements.items():
            content = content.replace(old, new)
    dest.write_text(content, encoding="utf-8")
    click.echo(f"  Created {dest}")


def _create_claude_md(path: Path, today: str) -> None:
    """Create CLAUDE.md with the standard wiki schema."""
    path.write_text(
        """# LLM Wiki

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

All LLM commands support `--token-report` (with `--token-report-format text|html`) and `--workers N` for parallel chapter processing.

## Three Core Operations

### Ingest

1. Place raw material in `raw/` with a clear filename
2. Run `wiki convert raw/<file>` — CLI auto-detects document size and chooses standard or plan-and-execute mode
3. Review generated pages and instruction files in `reports/`
4. Keep generated pages aligned with the frontmatter + `## See also` structure

### Query

1. Run `wiki query "your question here"`
2. The CLI finds relevant wiki pages, calls LLM for synthesis, and records the answer
3. Check `reports/queries.md` for recorded queries
4. If the query generates new knowledge, the CLI creates an instruction file for a new page

### Lint

1. Run `wiki lint` for static checks (no API calls)
2. Run `wiki lint --model <name>` for LLM-enhanced content analysis
3. Review findings in `reports/lint-report.md`
4. Fix critical issues and update `wiki/log.md` (auto-updated by CLI)

## Log Entry Format

Append to `wiki/log.md`:

```
## [YYYY-MM-DD] operation | Title
- What was done
- Which pages were affected
```

Operations: `convert`, `query`, `lint`, `init`
""",
        encoding="utf-8",
    )


if __name__ == "__main__":
    cli()
