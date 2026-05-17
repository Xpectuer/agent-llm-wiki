"""Phase 3: Query flow tests with mocked LLM."""

from unittest.mock import MagicMock

from wiki_cli.query import _append_log, _record_query, run_query


def _text_response(text: str):
    msg = MagicMock()
    text_block = MagicMock()
    text_block.type = "text"
    text_block.text = text
    msg.content = [text_block]
    msg.usage = MagicMock(
        input_tokens=200,
        output_tokens=100,
        cache_creation_input_tokens=0,
        cache_read_input_tokens=0,
    )
    return msg


class TestRunQuery:
    def test_basic_query(self, wiki_config, mock_claude):
        answer = """**回答**: Transformer 是一种基于自注意力机制的神经网络架构。

**引用**:
- [[transformer]] — Transformer架构概述
- raw/deep-learning.pdf — 原始教材

**建议新页面**: 无"""
        mock_claude.create.return_value = _text_response(answer)

        result = run_query(wiki_config, "什么是Transformer？")
        assert "Transformer" in result
        assert "[[transformer]]" in result

    def test_query_with_tool_loop(self, wiki_config, mock_claude):
        # Simulate: search_wiki → read_page → final answer
        tool_block = MagicMock()
        tool_block.type = "tool_use"
        tool_block.name = "search_wiki"
        tool_block.id = "tool_001"
        tool_block.input = {"query": "transformer"}

        turn1 = MagicMock()
        turn1.content = [tool_block]
        turn1.usage = MagicMock(
            input_tokens=100,
            output_tokens=30,
            cache_creation_input_tokens=0,
            cache_read_input_tokens=0,
        )

        turn2 = _text_response("""**回答**: 根据wiki内容，Transformer是...

**引用**:
- [[transformer]] — 核心架构

**建议新页面**: 无""")

        mock_claude.create.side_effect = [turn1, turn2]

        result = run_query(wiki_config, "transformer是什么？")
        assert "Transformer" in result

    def test_answer_recorded_to_reports(self, wiki_config, mock_claude):
        answer = "**回答**: Short answer.\n\n**引用**:\n- [[page]]\n\n**建议新页面**: 无"
        mock_claude.create.return_value = _text_response(answer)

        run_query(wiki_config, "test question")
        queries_path = wiki_config.reports_dir / "queries.md"
        assert queries_path.exists()
        content = queries_path.read_text(encoding="utf-8")
        assert "test question" in content

    def test_log_appended(self, wiki_config, mock_claude):
        answer = "**回答**: Test.\n\n**引用**:\n- [[test]]\n\n**建议新页面**: 无"
        mock_claude.create.return_value = _text_response(answer)

        # Create log.md first
        wiki_config.wiki_dir.mkdir(parents=True, exist_ok=True)
        (wiki_config.wiki_dir / "log.md").write_text("# Log\n")

        run_query(wiki_config, "log test question")
        log_content = (wiki_config.wiki_dir / "log.md").read_text(encoding="utf-8")
        assert "log test question" in log_content


class TestRecordQuery:
    def test_creates_new_queries_file(self, wiki_config):
        _record_query(wiki_config, "Q1", "Answer 1")
        path = wiki_config.reports_dir / "queries.md"
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "Q1" in content
        assert "Answer 1" in content

    def test_appends_to_existing_file(self, wiki_config):
        path = wiki_config.reports_dir / "queries.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Queries\n\n## [2026-01-01] Old Q\n\nOld answer.\n\n---\n")

        _record_query(wiki_config, "New Q", "New answer.")
        content = path.read_text(encoding="utf-8")
        assert "Old Q" in content
        assert "New Q" in content


class TestAppendLog:
    def test_appends_log_entry(self, wiki_config):
        log = wiki_config.wiki_dir / "log.md"
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text("# Log\n")
        _append_log(wiki_config, "What is RLHF?")
        content = log.read_text(encoding="utf-8")
        assert "What is RLHF?" in content
        assert "query" in content

    def test_log_not_exists_no_error(self, wiki_config):
        _append_log(wiki_config, "Question")
        # Should not raise
