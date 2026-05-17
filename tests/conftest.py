"""Shared fixtures for all tests."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from wiki_cli.config import Config


@pytest.fixture
def wiki_config(tmp_path: Path) -> Config:
    """Provide a Config pointing at temp directories with wiki/ created."""
    wiki = tmp_path / "wiki"
    raw = tmp_path / "raw"
    reports = tmp_path / "reports"
    templates = tmp_path / "templates"
    for d in [wiki, raw, reports, templates]:
        d.mkdir()
    return Config(
        api_key="test-key",
        model="claude-sonnet-4-6",
        base_url=None,
        wiki_dir=wiki,
        raw_dir=raw,
        reports_dir=reports,
        templates_dir=templates,
        project_root=tmp_path,
    )


@pytest.fixture
def mock_claude():
    """Mock anthropic.Anthropic().messages.create() so no real API calls fire.

    Yields the mocked ``messages.create`` so you can set
    ``mock_claude.create.return_value`` or ``side_effect`` per test.
    """
    with patch("wiki_cli.llm.anthropic.Anthropic") as mock_anthropic:
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        yield mock_client.messages
