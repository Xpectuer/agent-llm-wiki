from wiki_cli.tools import _list_page_names, list_pages, read_page, search_wiki


def create_page(wiki_dir, name: str, content: str):
    path = wiki_dir / f"{name}.md"
    path.write_text(content, encoding="utf-8")
    return path


class TestListPageNames:
    def test_empty_wiki(self, wiki_config):
        assert _list_page_names(wiki_config) == []

    def test_regular_pages(self, wiki_config):
        create_page(wiki_config.wiki_dir, "transformer", "# Transformer")
        create_page(wiki_config.wiki_dir, "bert", "# BERT")
        assert sorted(_list_page_names(wiki_config)) == ["bert", "transformer"]

    def test_excludes_index_and_log(self, wiki_config):
        create_page(wiki_config.wiki_dir, "transformer", "# T")
        create_page(wiki_config.wiki_dir, "index", "# Index")
        create_page(wiki_config.wiki_dir, "log", "# Log")
        assert _list_page_names(wiki_config) == ["transformer"]

    def test_non_md_files_ignored(self, wiki_config):
        create_page(wiki_config.wiki_dir, "readme", "# Readme")
        (wiki_config.wiki_dir / "notes.txt").write_text("not markdown")
        assert _list_page_names(wiki_config) == ["readme"]

    def test_wiki_dir_not_exists(self, tmp_path):
        from wiki_cli.config import Config

        config = Config(
            api_key="test",
            model="test",
            base_url=None,
            wiki_dir=tmp_path / "nonexistent",
            raw_dir=tmp_path / "raw",
            reports_dir=tmp_path / "reports",
            templates_dir=tmp_path / "templates",
            project_root=tmp_path,
        )
        assert _list_page_names(config) == []


class TestListPages:
    def test_empty_wiki(self, wiki_config):
        assert "wiki 中没有页面" in list_pages(wiki_config)

    def test_sorted_output(self, wiki_config):
        create_page(wiki_config.wiki_dir, "delta", "# D")
        create_page(wiki_config.wiki_dir, "alpha", "# A")
        create_page(wiki_config.wiki_dir, "charlie", "# C")
        output = list_pages(wiki_config)
        lines = output.strip().split("\n")
        assert "alpha" in lines[0]
        assert "charlie" in lines[1]
        assert "delta" in lines[2]


class TestReadPage:
    def test_existing_page(self, wiki_config):
        create_page(wiki_config.wiki_dir, "gpt", "# GPT\n\nContent here.")
        result = read_page(wiki_config, "gpt")
        assert "# GPT" in result
        assert "Content here." in result

    def test_strips_md_extension(self, wiki_config):
        create_page(wiki_config.wiki_dir, "gpt", "# GPT")
        result = read_page(wiki_config, "gpt.md")
        assert "# GPT" in result

    def test_nonexistent_page_reports_error(self, wiki_config):
        result = read_page(wiki_config, "nonexistent")
        assert "不存在" in result

    def test_whitespace_trimmed(self, wiki_config):
        create_page(wiki_config.wiki_dir, "gpt", "# GPT")
        result = read_page(wiki_config, "  gpt  ")
        assert "# GPT" in result


class TestSearchWiki:
    def test_empty_wiki(self, wiki_config):
        result = search_wiki(wiki_config, "transformer")
        assert "wiki 中没有页面" in result

    def test_exact_match(self, wiki_config):
        create_page(
            wiki_config.wiki_dir,
            "transformer",
            "# Transformer\n\nThe transformer architecture uses self-attention.",
        )
        result = search_wiki(wiki_config, "transformer")
        assert "transformer" in result

    def test_no_match(self, wiki_config):
        create_page(
            wiki_config.wiki_dir, "rlhf", "# RLHF\n\nReinforcement learning from human feedback."
        )
        result = search_wiki(wiki_config, "transformer")
        assert "未找到" in result

    def test_chinese_search(self, wiki_config):
        create_page(wiki_config.wiki_dir, "神经网络", "# 神经网络\n\n神经网络是深度学习的核心。")
        result = search_wiki(wiki_config, "神经网络")
        assert "神经网络" in result

    def test_mixed_cn_en_search(self, wiki_config):
        create_page(
            wiki_config.wiki_dir,
            "transformer",
            "# Transformer\n\nTransformer 架构使用自注意力机制。",
        )
        result = search_wiki(wiki_config, "transformer 架构")
        assert "transformer" in result

    def test_scores_ranked(self, wiki_config):
        create_page(wiki_config.wiki_dir, "page-a", "transformer transformer transformer")
        create_page(wiki_config.wiki_dir, "page-b", "transformer")
        create_page(wiki_config.wiki_dir, "page-c", "no match here")
        result = search_wiki(wiki_config, "transformer")
        # page-a should appear before page-b (higher score)
        assert result.index("page-a") < result.index("page-b")

    def test_short_token_fallback(self, wiki_config):
        create_page(wiki_config.wiki_dir, "rlhf", "# RLHF\n\nRLHF is great.")
        result = search_wiki(wiki_config, "RL")
        # "RL" is 2 chars, but regex needs 2+ — it matches
        assert "RLHF" in result

    def test_single_char_query_fallback(self, wiki_config):
        create_page(wiki_config.wiki_dir, "a", "# A\n\nJust a page about A.")
        result = search_wiki(wiki_config, "a")
        assert "Just a page about A" in result
