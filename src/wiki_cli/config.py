"""Configuration management for wiki CLI. Stateless — reads from env each call."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_WIKI_DIR = "wiki"
DEFAULT_RAW_DIR = "raw"
DEFAULT_REPORTS_DIR = "reports"
DEFAULT_TEMPLATES_DIR = "templates"


@dataclass
class Config:
    api_key: str
    model: str
    base_url: str | None
    wiki_dir: Path
    raw_dir: Path
    reports_dir: Path
    templates_dir: Path
    project_root: Path


def load_config(project_root: Path | None = None) -> Config:
    """Load configuration from environment variables."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise SystemExit(
            "Error: ANTHROPIC_API_KEY environment variable not set.\n"
            "  export ANTHROPIC_API_KEY=your-key-here"
        )

    root = (project_root or Path.cwd()).resolve()
    return Config(
        api_key=api_key,
        model=os.environ.get("WIKI_MODEL", DEFAULT_MODEL),
        base_url=os.environ.get("ANTHROPIC_BASE_URL") or None,
        wiki_dir=root / os.environ.get("WIKI_DIR", DEFAULT_WIKI_DIR),
        raw_dir=root / os.environ.get("RAW_DIR", DEFAULT_RAW_DIR),
        reports_dir=root / os.environ.get("REPORTS_DIR", DEFAULT_REPORTS_DIR),
        templates_dir=root / os.environ.get("TEMPLATES_DIR", DEFAULT_TEMPLATES_DIR),
        project_root=root,
    )
