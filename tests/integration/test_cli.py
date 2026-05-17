"""Phase 4: CLI end-to-end tests using Click CliRunner."""

import os
from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

from wiki_cli.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def with_api_key(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-123")


class TestInit:
    def test_creates_directories(self, runner, tmp_path):
        result = runner.invoke(cli, ["--project-root", str(tmp_path), "init"])
        assert result.exit_code == 0
        assert (tmp_path / "wiki").is_dir()
        assert (tmp_path / "raw").is_dir()
        assert (tmp_path / "reports").is_dir()
        assert (tmp_path / "templates").is_dir()

    def test_creates_wiki_files(self, runner, tmp_path):
        # Pre-create templates/ with index.md and log.md so _init_from_template works
        templates = tmp_path / "templates"
        templates.mkdir()
        (templates / "index.md").write_text(
            "# Index\n\n> Last updated: {date}\n\n## Synthesis\n", encoding="utf-8"
        )
        (templates / "log.md").write_text("# Log\n", encoding="utf-8")

        result = runner.invoke(cli, ["--project-root", str(tmp_path), "init"])
        assert result.exit_code == 0
        assert (tmp_path / "wiki" / "index.md").exists()
        assert (tmp_path / "wiki" / "log.md").exists()

    def test_creates_report_files(self, runner, tmp_path):
        result = runner.invoke(cli, ["--project-root", str(tmp_path), "init"])
        assert result.exit_code == 0
        assert (tmp_path / "reports" / "queries.md").exists()
        assert (tmp_path / "reports" / "lint-report.md").exists()
        assert (tmp_path / "reports" / "schema-note.md").exists()

    def test_creates_claude_md(self, runner, tmp_path):
        result = runner.invoke(cli, ["--project-root", str(tmp_path), "init"])
        assert result.exit_code == 0
        claude_md = tmp_path / "CLAUDE.md"
        assert claude_md.exists()
        content = claude_md.read_text()
        assert "LLM Wiki" in content

    def test_creates_agents_symlink(self, runner, tmp_path):
        result = runner.invoke(cli, ["--project-root", str(tmp_path), "init"])
        assert result.exit_code == 0
        agents_md = tmp_path / "AGENTS.md"
        assert agents_md.is_symlink()

    def test_output_shows_success(self, runner, tmp_path):
        result = runner.invoke(cli, ["--project-root", str(tmp_path), "init"])
        assert "Wiki initialized successfully" in result.output


class TestLintNoApi:
    def test_static_lint_no_api_key_needed(self, runner, tmp_path, monkeypatch):
        """Static lint (without --model) calls _load_config_with_override which requires API key."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        wiki = tmp_path / "wiki"
        wiki.mkdir()
        (wiki / "index.md").write_text("# Index\n\n## Synthesis\n", encoding="utf-8")
        (wiki / "log.md").write_text("# Log\n", encoding="utf-8")

        reports = tmp_path / "reports"
        reports.mkdir()

        result = runner.invoke(cli, ["--project-root", str(tmp_path), "lint"])
        # Even static lint requires API key because _load_config_with_override always calls load_config
        assert result.exit_code != 0
        assert "ANTHROPIC_API_KEY" in result.output

    def test_static_lint_with_api_key(self, runner, tmp_path, with_api_key):
        wiki = tmp_path / "wiki"
        wiki.mkdir()
        (wiki / "index.md").write_text("# Index\n\n## Synthesis\n", encoding="utf-8")
        (wiki / "log.md").write_text("# Log\n", encoding="utf-8")

        reports = tmp_path / "reports"
        reports.mkdir()

        result = runner.invoke(cli, ["--project-root", str(tmp_path), "lint"])
        assert result.exit_code == 0

    def test_lint_strict_flag(self, runner, tmp_path, with_api_key):
        wiki = tmp_path / "wiki"
        wiki.mkdir()
        (wiki / "index.md").write_text("# Index\n", encoding="utf-8")
        (wiki / "log.md").write_text("# Log\n", encoding="utf-8")

        reports = tmp_path / "reports"
        reports.mkdir()

        # Create a broken link to generate an error, then strict should fail
        (wiki / "broken.md").write_text("See [[nonexistent]].", encoding="utf-8")

        result = runner.invoke(cli, ["--project-root", str(tmp_path), "lint", "--strict"])
        # strict mode: any error → exit code 1
        assert result.exit_code != 0


class TestConvertValidation:
    def test_missing_file(self, runner, tmp_path, with_api_key):
        result = runner.invoke(cli, ["--project-root", str(tmp_path), "convert", "nonexistent.pdf"])
        assert result.exit_code != 0

    def test_requires_api_key(self, runner, tmp_path, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        # Create the file so Click's path validation passes
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        result = runner.invoke(cli, ["--project-root", str(tmp_path), "convert", str(test_file)])
        assert result.exit_code != 0
        assert "ANTHROPIC_API_KEY" in result.output

    def test_dry_run_with_txt_triggers_plan(self, runner, tmp_path, with_api_key, mock_claude):
        """Dry-run on a large text file should go through plan path."""
        txt = tmp_path / "large.txt"
        # Write a file larger than the auto-detect threshold
        txt.write_text("x" * 40000, encoding="utf-8")

        # Mock plan LLM response
        mock_claude.create.return_value = _make_text_response(
            '{"chapters": [{"id": "ch-01", "title": "All", "order": 1, "heading_pattern": "", "depends_on": [], "summary": "test"}]}'
        )

        result = runner.invoke(
            cli,
            [
                "--project-root",
                str(tmp_path),
                "convert",
                str(txt),
                "--dry-run",
                "-q",
            ],
        )
        assert result.exit_code == 0


class TestQueryValidation:
    def test_requires_question(self, runner, tmp_path, with_api_key):
        result = runner.invoke(cli, ["--project-root", str(tmp_path), "query"])
        assert result.exit_code != 0

    def test_requires_api_key(self, runner, tmp_path, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        result = runner.invoke(cli, ["--project-root", str(tmp_path), "query", "test"])
        assert result.exit_code != 0
        assert "ANTHROPIC_API_KEY" in result.output


class TestGlobalOptions:
    def test_version_or_help(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "init" in result.output
        assert "convert" in result.output
        assert "lint" in result.output
        assert "query" in result.output

    def test_default_project_root_is_cwd(self, runner, tmp_path, with_api_key):
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(cli, ["init"])
            assert result.exit_code == 0
            assert (tmp_path / "wiki").is_dir()
        finally:
            os.chdir(original_cwd)


def _make_text_response(text: str):
    msg = MagicMock()
    text_block = MagicMock()
    text_block.type = "text"
    text_block.text = text
    msg.content = [text_block]
    msg.usage = MagicMock(
        input_tokens=100,
        output_tokens=50,
        cache_creation_input_tokens=0,
        cache_read_input_tokens=0,
    )
    return msg
