import json

from wiki_cli.models import Chapter, Plan
from wiki_cli.planner import load_plan, save_plan


def ch(id, title="", order=0, heading="", deps=None, summary=""):
    return Chapter(
        id=id,
        title=title or id,
        order=order,
        heading_pattern=heading,
        depends_on=deps or [],
        summary=summary,
    )


class TestPlanRoundTrip:
    def test_round_trip(self, wiki_config):
        plan = Plan(
            source_file="test.pdf",
            total_chars=5000,
            chapters=[
                ch("ch-01", title="Introduction", order=1, summary="Overview"),
                ch(
                    "ch-02",
                    title="Methods",
                    order=2,
                    deps=["ch-01"],
                    heading="## Methods",
                    summary="How we did it",
                ),
                ch("ch-03", title="Results", order=3, deps=["ch-02"], summary="Findings"),
            ],
            metadata={"model": "claude-sonnet-4-6"},
        )
        path = save_plan(plan, wiki_config)
        assert path.exists()

        loaded = load_plan(path)
        assert loaded.source_file == "test.pdf"
        assert loaded.total_chars == 5000
        assert len(loaded.chapters) == 3
        assert loaded.metadata["model"] == "claude-sonnet-4-6"

        # Verify chapter order preserved
        assert [c.id for c in loaded.chapters] == ["ch-01", "ch-02", "ch-03"]
        assert loaded.chapters[1].depends_on == ["ch-01"]
        assert loaded.chapters[1].heading_pattern == "## Methods"

    def test_single_chapter_round_trip(self, wiki_config):
        plan = Plan(
            source_file="simple.md",
            total_chars=100,
            chapters=[ch("ch-01", "All", 1)],
            metadata={"fallback": True},
        )
        path = save_plan(plan, wiki_config)
        loaded = load_plan(path)
        assert len(loaded.chapters) == 1
        assert loaded.chapters[0].depends_on == []

    def test_json_structure(self, wiki_config):
        plan = Plan(
            source_file="test.pdf",
            total_chars=200,
            chapters=[ch("ch-01", "Foo", 1, summary="A summary")],
        )
        path = save_plan(plan, wiki_config)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["source_file"] == "test.pdf"
        assert data["total_chars"] == 200
        assert len(data["chapters"]) == 1
        ch_data = data["chapters"][0]
        assert ch_data["id"] == "ch-01"
        assert ch_data["title"] == "Foo"
        assert ch_data["order"] == 1

    def test_plan_with_empty_deps(self, wiki_config):
        plan = Plan(
            source_file="test.pdf",
            total_chars=100,
            chapters=[
                ch("a", order=1),
                ch("b", order=2),
            ],
        )
        path = save_plan(plan, wiki_config)
        loaded = load_plan(path)
        assert loaded.chapters[0].depends_on == []
        assert loaded.chapters[1].depends_on == []
