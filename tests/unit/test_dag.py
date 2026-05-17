import pytest

from wiki_cli.executor import _strip_frontmatter
from wiki_cli.models import Chapter
from wiki_cli.planner import (
    _topological_levels,
    _validate_dag,
    describe_plan,
    split_chapters,
)


def ch(id, title="", order=0, heading="", deps=None, summary=""):
    return Chapter(
        id=id,
        title=title or id,
        order=order,
        heading_pattern=heading,
        depends_on=deps or [],
        summary=summary,
    )


class TestValidateDAG:
    def test_valid_linear_chain(self):
        _validate_dag(
            [
                ch("a"),
                ch("b", deps=["a"]),
                ch("c", deps=["b"]),
            ]
        )

    def test_valid_diamond(self):
        _validate_dag(
            [
                ch("a"),
                ch("b", deps=["a"]),
                ch("c", deps=["a"]),
                ch("d", deps=["b", "c"]),
            ]
        )

    def test_valid_independent_chapters(self):
        _validate_dag(
            [
                ch("a"),
                ch("b"),
                ch("c"),
            ]
        )

    def test_empty_list(self):
        _validate_dag([])

    def test_single_chapter(self):
        _validate_dag([ch("a")])

    def test_missing_dependency_raises(self):
        with pytest.raises(ValueError, match="unknown chapter"):
            _validate_dag([ch("a", deps=["nonexistent"])])

    def test_self_dependency(self):
        with pytest.raises(ValueError, match="Cycle detected"):
            _validate_dag([ch("a", deps=["a"])])

    def test_two_node_cycle(self):
        with pytest.raises(ValueError, match="Cycle detected"):
            _validate_dag([ch("a", deps=["b"]), ch("b", deps=["a"])])

    def test_three_node_cycle(self):
        with pytest.raises(ValueError, match="Cycle detected"):
            _validate_dag(
                [
                    ch("a", deps=["c"]),
                    ch("b", deps=["a"]),
                    ch("c", deps=["b"]),
                ]
            )

    def test_multiple_missing_deps_first_only_reported(self):
        # Should report the first unknown dependency it encounters during validation
        with pytest.raises(ValueError, match="unknown chapter"):
            _validate_dag(
                [
                    ch("a", deps=["missing1", "missing2"]),
                ]
            )

    def test_depends_on_nonexistent_but_similar_name(self):
        with pytest.raises(ValueError, match="unknown chapter 'ch-1'"):
            _validate_dag([ch("ch-01", deps=["ch-1"])])


class TestTopologicalLevels:
    def test_linear_three_levels(self):
        chapters = [
            ch("a"),
            ch("b", deps=["a"]),
            ch("c", deps=["b"]),
        ]
        assert _topological_levels(chapters) == [["a"], ["b"], ["c"]]

    def test_two_parallel_in_level(self):
        chapters = [
            ch("a"),
            ch("b", deps=["a"]),
            ch("c", deps=["a"]),
        ]
        levels = _topological_levels(chapters)
        assert levels[0] == ["a"]
        assert set(levels[1]) == {"b", "c"}

    def test_diamond_dag(self):
        chapters = [
            ch("a"),
            ch("b", deps=["a"]),
            ch("c", deps=["a"]),
            ch("d", deps=["b", "c"]),
        ]
        levels = _topological_levels(chapters)
        assert levels[0] == ["a"]
        assert set(levels[1]) == {"b", "c"}
        assert levels[2] == ["d"]

    def test_single_node(self):
        assert _topological_levels([ch("a")]) == [["a"]]

    def test_empty(self):
        assert _topological_levels([]) == []

    def test_independent_nodes_all_same_level(self):
        chapters = [ch("a"), ch("b"), ch("c")]
        levels = _topological_levels(chapters)
        assert len(levels) == 1
        assert set(levels[0]) == {"a", "b", "c"}

    def test_complex_dag(self):
        # a → b → d → f
        # a → c → d
        # a → c → e
        chapters = [
            ch("a"),
            ch("b", deps=["a"]),
            ch("c", deps=["a"]),
            ch("d", deps=["b", "c"]),
            ch("e", deps=["c"]),
            ch("f", deps=["d"]),
        ]
        levels = _topological_levels(chapters)
        assert levels[0] == ["a"]
        assert set(levels[1]) == {"b", "c"}
        assert set(levels[2]) == {"d", "e"}
        assert levels[3] == ["f"]

    def test_cycle_raises(self):
        chapters = [ch("a", deps=["b"]), ch("b", deps=["a"])]
        with pytest.raises(ValueError, match="Cycle detected"):
            _topological_levels(chapters)


class TestSplitChapters:
    def test_single_chapter_returns_full_text(self):
        chapters = [ch("ch-01")]
        text = "Full document text"
        result = split_chapters(text, chapters)
        assert result == {"ch-01": "Full document text"}

    def test_empty_text(self):
        chapters = [ch("ch-01"), ch("ch-02")]
        result = split_chapters("", chapters)
        # Each chapter gets an empty segment from the proportional split
        assert all(v == "" for v in result.values())
        assert set(result.keys()) == {"ch-01", "ch-02"}

    def test_proportional_split_for_chapters_without_patterns(self):
        chapters = [ch("ch-a", order=1), ch("ch-b", order=2), ch("ch-c", order=3)]
        text = "0123456789" * 9  # 90 chars
        result = split_chapters(text, chapters)
        assert "ch-a" in result
        assert "ch-b" in result
        assert "ch-c" in result
        # Proportional: each gets ~30 chars
        assert 20 < len(result["ch-a"]) < 40

    def test_regex_split_with_matching_pattern(self):
        chapters = [
            ch("intro", order=1, heading="## Introduction"),
            ch("methods", order=2, heading="## Methods"),
            ch("results", order=3, heading="## Results"),
        ]
        text = """## Introduction
Intro text here.
## Methods
Methods text here.
## Results
Results text here."""
        result = split_chapters(text, chapters)
        assert "intro" in result
        assert "Intro text here." in result["intro"]
        assert "Methods text here." in result["methods"]


class TestDescribePlan:
    def test_basic_output(self):
        from wiki_cli.models import Plan

        plan = Plan(
            source_file="test.pdf",
            total_chars=5000,
            chapters=[
                ch("ch-01", title="Intro", order=1),
                ch("ch-02", title="Methods", order=2, deps=["ch-01"]),
            ],
        )
        desc = describe_plan(plan)
        assert "test.pdf" in desc
        assert "5,000 chars" in desc
        assert "ch-01" in desc
        assert "ch-02" in desc

    def test_shows_parallel_tag(self):
        from wiki_cli.models import Plan

        plan = Plan(
            source_file="test.pdf",
            total_chars=100,
            chapters=[
                ch("a", order=1),
                ch("b", order=2),
            ],
        )
        desc = describe_plan(plan)
        assert "parallel" in desc


class TestStripFrontmatter:
    def test_strips_frontmatter(self):
        content = """---
brief: something
---
# Title
Body text."""
        result = _strip_frontmatter(content)
        assert "---" not in result
        assert "# Title" in result

    def test_no_frontmatter_unchanged(self):
        content = "# Just a title\nBody."
        result = _strip_frontmatter(content)
        assert result == content

    def test_empty_content(self):
        assert _strip_frontmatter("") == ""
