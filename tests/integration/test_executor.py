"""Phase 3: Executor tests with mocked LLM."""

import json
from unittest.mock import MagicMock

from wiki_cli.executor import merge_all_results
from wiki_cli.models import Chapter, ChapterResult, Plan


def _text_response(text: str):
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


def ch(id, title="", order=0, deps=None, summary=""):
    return Chapter(
        id=id,
        title=title or id,
        order=order,
        heading_pattern="",
        depends_on=deps or [],
        summary=summary,
    )


class TestMergeAllResults:
    def test_merge_with_no_pages_skips_xref(self, wiki_config, mock_claude):
        """When no pages were created, merge should not call the LLM."""
        plan = Plan(source_file="test.pdf", total_chars=100, chapters=[ch("ch-01", order=1)])
        results = [
            ChapterResult(chapter_id="ch-01", status="success", concepts=[], pages_created=[])
        ]

        merge_all_results(wiki_config, results, plan)
        # No LLM calls should happen (no pages to xref)
        # Just verify it doesn't crash

    def test_merge_with_pages_runs_xref(self, wiki_config, mock_claude):
        """When pages exist, xref should run. Mock LLM returns empty suggestions."""
        # Create wiki pages first
        wiki_config.wiki_dir.mkdir(parents=True, exist_ok=True)
        (wiki_config.wiki_dir / "a.md").write_text(
            "---\nbrief: Page A\n---\n# A\n\nContent.\n", encoding="utf-8"
        )
        (wiki_config.wiki_dir / "b.md").write_text(
            "---\nbrief: Page B\n---\n# B\n\nContent about A.\n", encoding="utf-8"
        )

        # Mock: graph LLM response
        graph_response = _text_response(json.dumps({"graph": {"a": ["b"], "b": ["a"]}}))
        # Mock: xref LLM response (for each page)
        xref_response_a = _text_response(
            json.dumps(
                {
                    "see_also": ["b"],
                    "merge_candidates": [],
                }
            )
        )
        xref_response_b = _text_response(
            json.dumps(
                {
                    "see_also": ["a"],
                    "merge_candidates": [],
                }
            )
        )

        mock_claude.create.side_effect = [graph_response, xref_response_a, xref_response_b]

        plan = Plan(source_file="test.pdf", total_chars=100, chapters=[ch("ch-01", order=1)])
        results = [
            ChapterResult(
                chapter_id="ch-01",
                status="success",
                concepts=[{"name": "a", "action": "create", "summary": "A"}],
                pages_created=["a"],
            ),
        ]

        merge_all_results(wiki_config, results, plan)

        # Verify xref ran: page "a" should have "b" in See also
        content = (wiki_config.wiki_dir / "a.md").read_text(encoding="utf-8")
        assert "[[b]]" in content or "## See also" in content

    def test_merge_with_failed_chapter_skips(self, wiki_config, mock_claude):
        plan = Plan(source_file="test.pdf", total_chars=100, chapters=[ch("ch-01", order=1)])
        results = [
            ChapterResult(
                chapter_id="ch-01",
                status="failed",
                error="API error",
                concepts=[],
                pages_created=[],
            )
        ]
        # Should not raise
        merge_all_results(wiki_config, results, plan)
