from pathlib import Path

from wiki_cli.config import DEFAULT_MODEL, Config, load_config


def write_missing_files(config: Config):
    """Ensure required directories exist."""
    for d in [config.wiki_dir, config.raw_dir, config.reports_dir, config.templates_dir]:
        d.mkdir(parents=True, exist_ok=True)


class TestLoadConfig:
    def test_defaults(self, monkeypatch, tmp_path):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-123")
        # Unset overrides
        for var in [
            "WIKI_MODEL",
            "ANTHROPIC_BASE_URL",
            "WIKI_DIR",
            "RAW_DIR",
            "REPORTS_DIR",
            "TEMPLATES_DIR",
            "WIKI_MAX_WORKERS",
            "WIKI_LARGE_THRESHOLD",
        ]:
            monkeypatch.delenv(var, raising=False)

        config = load_config(tmp_path)
        assert config.api_key == "test-key-123"
        assert config.model == DEFAULT_MODEL
        assert config.base_url is None
        assert config.wiki_dir == tmp_path / "wiki"
        assert config.raw_dir == tmp_path / "raw"
        assert config.max_workers == 4
        assert config.large_threshold == 30_000

    def test_env_override(self, monkeypatch, tmp_path):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "key-override")
        monkeypatch.setenv("WIKI_MODEL", "claude-opus-4-7")
        monkeypatch.setenv("ANTHROPIC_BASE_URL", "https://proxy.example.com")
        monkeypatch.setenv("WIKI_DIR", "my_wiki")
        monkeypatch.setenv("WIKI_MAX_WORKERS", "8")
        monkeypatch.setenv("WIKI_LARGE_THRESHOLD", "50000")

        config = load_config(tmp_path)
        assert config.model == "claude-opus-4-7"
        assert config.base_url == "https://proxy.example.com"
        assert config.wiki_dir == tmp_path / "my_wiki"
        assert config.max_workers == 8
        assert config.large_threshold == 50_000

    def test_missing_api_key_exits(self, monkeypatch, tmp_path):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        try:
            load_config(tmp_path)
            raise AssertionError("Should have raised SystemExit")
        except SystemExit as e:
            assert "ANTHROPIC_API_KEY" in str(e)

    def test_project_root_resolved(self, monkeypatch, tmp_path):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "key")
        config = load_config(tmp_path)
        assert config.project_root == tmp_path.resolve()

    def test_default_project_root_is_cwd(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "key")
        config = load_config()  # no explicit root
        assert config.project_root == Path.cwd().resolve()

    def test_quiet_flag_not_set_by_env(self, monkeypatch, tmp_path):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "key")
        config = load_config(tmp_path)
        assert config.quiet is False
