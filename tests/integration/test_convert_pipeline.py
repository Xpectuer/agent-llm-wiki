"""Phase 3: LLM-mocked pipeline integration tests."""

import json
from unittest.mock import MagicMock

from wiki_cli.convert import (
    build_relevance_graph,
    extract_concepts,
)


def _make_text_response(text: str):
    """Build a mock messages.create response with a single text block."""
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


def _make_tool_then_text_response(tool_name: str, tool_input: dict, final_text: str):
    """Build the sequence of responses for an agentic tool-calling loop:
    first response has a tool_use block, second response has final text.

    Returns a list of mock responses (one per turn).
    """
    # Turn 1: tool_use response
    turn1 = MagicMock()
    tool_block = MagicMock()
    tool_block.type = "tool_use"
    tool_block.name = tool_name
    tool_block.id = "tool_001"
    tool_block.input = tool_input
    turn1.content = [tool_block]
    turn1.usage = MagicMock(
        input_tokens=100,
        output_tokens=50,
        cache_creation_input_tokens=0,
        cache_read_input_tokens=0,
    )

    # Turn 2: final text response
    turn2 = _make_text_response(final_text)

    return [turn1, turn2]


class TestExtractConcepts:
    CONCEPT_JSON = json.dumps(
        {
            "concepts": [
                {
                    "name": "transformer",
                    "action": "create",
                    "target_page": None,
                    "summary": "Transformer architecture",
                },
                {
                    "name": "attention",
                    "action": "merge",
                    "target_page": "attention-mechanism",
                    "summary": "Attention mechanism",
                },
            ],
            "ambiguities": [
                {
                    "concept": "attention",
                    "conflict": "Overlaps with self-attention page",
                    "resolution": "Merge",
                },
            ],
        }
    )

    def test_extracts_concepts_from_tool_loop(self, wiki_config, mock_claude):
        """LLM does search_wiki → final JSON with concepts."""
        mock_claude.create.side_effect = _make_tool_then_text_response(
            tool_name="search_wiki",
            tool_input={"query": "transformer"},
            final_text=self.CONCEPT_JSON,
        )

        concepts, ambiguities = extract_concepts(
            wiki_config, "test text about transformers", "test.pdf"
        )

        assert len(concepts) == 2
        assert concepts[0]["name"] == "transformer"
        assert concepts[0]["action"] == "create"
        assert concepts[1]["name"] == "attention"
        assert concepts[1]["action"] == "merge"
        assert len(ambiguities) == 1
        assert ambiguities[0]["concept"] == "attention"

    def test_no_concepts_found(self, wiki_config, mock_claude):
        """LLM returns empty concepts list."""
        mock_claude.create.return_value = _make_text_response(
            json.dumps({"concepts": [], "ambiguities": []})
        )
        concepts, ambiguities = extract_concepts(wiki_config, "irrelevant text", "empty.pdf")
        assert concepts == []
        assert ambiguities == []

    def test_json_inside_fence(self, wiki_config, mock_claude):
        """LLM returns JSON wrapped in markdown fence."""
        mock_claude.create.return_value = _make_text_response(
            "```json\n" + self.CONCEPT_JSON + "\n```"
        )
        concepts, _ = extract_concepts(wiki_config, "test text", "test.pdf")
        assert len(concepts) == 2

    def test_deepseek_style_response(self, wiki_config, mock_claude):
        """LLM returns reasoning text + JSON (like DeepSeek)."""
        mock_claude.create.return_value = _make_text_response(
            "思考：这个文档讲的是transformer...\n" + self.CONCEPT_JSON + "\n以上就是提取结果。"
        )
        concepts, _ = extract_concepts(wiki_config, "test", "test.pdf")
        assert len(concepts) == 2

    def test_truncates_long_text(self, wiki_config, mock_claude):
        mock_claude.create.return_value = _make_text_response(
            json.dumps({"concepts": [], "ambiguities": []})
        )
        very_long_text = "test content. " * 5000  # ~65k chars, limit is 8000
        _, _ = extract_concepts(wiki_config, very_long_text, "long.pdf")
        call_args = mock_claude.create.call_args
        user_message = call_args[1]["messages"][0]["content"]
        assert len(user_message) < 12000  # should be capped at 8000 + prompt overhead


class TestBuildRelevanceGraph:
    def test_builds_graph_from_briefs(self, wiki_config, mock_claude):
        mock_claude.create.return_value = _make_text_response(
            json.dumps(
                {
                    "graph": {
                        "transformer": ["attention", "bert"],
                        "attention": ["transformer"],
                        "bert": ["transformer"],
                    }
                }
            )
        )
        briefs = {
            "transformer": "Transformer架构详解",
            "attention": "注意力机制",
            "bert": "BERT预训练模型",
        }
        graph = build_relevance_graph(wiki_config, briefs)
        assert set(graph["transformer"]) == {"attention", "bert"}
        assert graph["attention"] == ["transformer"]

    def test_filters_self_references(self, wiki_config, mock_claude):
        mock_claude.create.return_value = _make_text_response(
            json.dumps(
                {
                    "graph": {
                        "transformer": ["attention", "transformer"],  # includes self-ref
                    }
                }
            )
        )
        briefs = {"transformer": "desc", "attention": "desc"}
        graph = build_relevance_graph(wiki_config, briefs)
        assert "transformer" not in graph.get("transformer", [])

    def test_filters_nonexistent_pages(self, wiki_config, mock_claude):
        mock_claude.create.return_value = _make_text_response(
            json.dumps(
                {
                    "graph": {
                        "transformer": ["attention", "nonexistent-page"],
                    }
                }
            )
        )
        briefs = {"transformer": "desc", "attention": "desc"}
        graph = build_relevance_graph(wiki_config, briefs)
        assert "nonexistent-page" not in graph["transformer"]
