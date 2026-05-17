from unittest.mock import MagicMock

from wiki_cli.config import Config
from wiki_cli.llint import (
    LintResult,
    _read_all_wiki_pages,
    check_briefs,
    check_broken_links,
    check_contradictions,
    check_orphan_pages,
    check_xref_density,
    fix_briefs,
)


def write_page(wiki_dir, name: str, content: str):
    (wiki_dir / f"{name}.md").write_text(content, encoding="utf-8")


class TestReadAllWikiPages:
    def test_empty(self, wiki_config):
        assert _read_all_wiki_pages(wiki_config) == {}

    def test_reads_pages(self, wiki_config):
        write_page(wiki_config.wiki_dir, "a", "# A")
        write_page(wiki_config.wiki_dir, "b", "# B")
        pages = _read_all_wiki_pages(wiki_config)
        assert pages["a"] == "# A"
        assert pages["b"] == "# B"

    def test_excludes_index_and_log(self, wiki_config):
        write_page(wiki_config.wiki_dir, "a", "# A")
        write_page(wiki_config.wiki_dir, "index", "# Index")
        write_page(wiki_config.wiki_dir, "log", "# Log")
        pages = _read_all_wiki_pages(wiki_config)
        assert list(pages.keys()) == ["a"]

    def test_wiki_dir_not_exists(self, tmp_path):
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
        assert _read_all_wiki_pages(config) == {}


class TestCheckBrokenLinks:
    def test_no_broken(self, wiki_config):
        write_page(wiki_config.wiki_dir, "a", "See [[b]] for more.")
        write_page(wiki_config.wiki_dir, "b", "# B")
        result = LintResult()
        check_broken_links(wiki_config, result)
        assert any("No broken" in p for p in result.passes)

    def test_broken_detected(self, wiki_config):
        write_page(wiki_config.wiki_dir, "a", "See [[nonexistent]] for more.")
        result = LintResult()
        check_broken_links(wiki_config, result)
        assert any("nonexistent" in e for e in result.errors)

    def test_multiple_links(self, wiki_config):
        write_page(wiki_config.wiki_dir, "a", "See [[b]] and [[c]].")
        write_page(wiki_config.wiki_dir, "b", "# B")
        result = LintResult()
        check_broken_links(wiki_config, result)
        assert any("c" in e for e in result.errors)

    def test_wiki_dir_missing(self, wiki_config):
        import shutil

        shutil.rmtree(wiki_config.wiki_dir)
        result = LintResult()
        check_broken_links(wiki_config, result)
        assert any("wiki" in w.lower() for w in result.warnings)


class TestCheckOrphanPages:
    def test_no_orphan(self, wiki_config):
        write_page(wiki_config.wiki_dir, "a", "See [[b]].")
        write_page(wiki_config.wiki_dir, "b", "See [[a]].")
        result = LintResult()
        check_orphan_pages(wiki_config, result)
        assert any("No orphan" in p for p in result.passes)

    def test_orphan_detected(self, wiki_config):
        write_page(wiki_config.wiki_dir, "lonely", "# Nobody links to me")
        write_page(wiki_config.wiki_dir, "connected", "# I exist but don't link to lonely")
        result = LintResult()
        check_orphan_pages(wiki_config, result)
        # "lonely" has no inbound links → orphan warning
        assert any("lonely" in w for w in result.warnings)

    def test_mutual_references_not_orphan(self, wiki_config):
        write_page(wiki_config.wiki_dir, "a", "See [[b]].")
        write_page(wiki_config.wiki_dir, "b", "See [[a]].")
        result = LintResult()
        check_orphan_pages(wiki_config, result)
        assert any("No orphan" in p for p in result.passes)


class TestCheckXrefDensity:
    def test_low_density_warns(self, wiki_config):
        write_page(wiki_config.wiki_dir, "a", "# A\n\nJust some text, only [[b]].")
        write_page(wiki_config.wiki_dir, "b", "# B")
        result = LintResult()
        check_xref_density(wiki_config, result)
        assert any("low connectivity" in w.lower() for w in result.warnings)

    def test_empty_wiki(self, wiki_config):
        result = LintResult()
        check_xref_density(wiki_config, result)
        assert any("No content pages" in p or "content" in p for p in result.passes)


class TestCheckContradictions:
    def test_no_contradictions(self, wiki_config):
        write_page(wiki_config.wiki_dir, "a", "# Clean page\nNo issues here.")
        result = LintResult()
        check_contradictions(wiki_config, result)
        assert any("No contradictions" in p for p in result.passes)

    def test_contradiction_comment_detected(self, wiki_config):
        write_page(wiki_config.wiki_dir, "a", "<!-- CONTRADICTION with page b -->\nSome text.")
        result = LintResult()
        check_contradictions(wiki_config, result)
        assert any("CONTRADICTION" in e for e in result.errors)

    def test_conflict_marker_detected(self, wiki_config):
        write_page(
            wiki_config.wiki_dir, "a", "Some text. **[CONFLICT]** This disagrees with page X."
        )
        result = LintResult()
        check_contradictions(wiki_config, result)
        assert any("CONFLICT" in e for e in result.errors)


class TestCheckBriefs:
    def test_all_pages_have_briefs(self, wiki_config):
        write_page(wiki_config.wiki_dir, "a", "---\nbrief: Page A\n---\n# A\n")
        result = LintResult()
        missing = check_briefs(wiki_config, result)
        assert missing == []
        assert any("All pages have briefs" in p for p in result.passes)

    def test_missing_brief_in_frontmatter(self, wiki_config):
        write_page(wiki_config.wiki_dir, "a", "---\nauthor: test\n---\n# A\n")
        result = LintResult()
        missing = check_briefs(wiki_config, result)
        assert len(missing) == 1
        assert any("missing brief" in e.lower() for e in result.errors)

    def test_missing_frontmatter_entirely(self, wiki_config):
        write_page(wiki_config.wiki_dir, "a", "# A\nNo frontmatter here.\n")
        result = LintResult()
        missing = check_briefs(wiki_config, result)
        assert len(missing) == 1
        assert any("missing frontmatter" in e.lower() for e in result.errors)

    def test_excludes_index_and_log(self, wiki_config):
        write_page(wiki_config.wiki_dir, "index", "# Index\nNo brief.")
        write_page(wiki_config.wiki_dir, "log", "# Log\nNo brief.")
        result = LintResult()
        missing = check_briefs(wiki_config, result)
        assert missing == []


class TestFixBriefs:
    def test_injects_brief_into_existing_frontmatter(self, wiki_config, mock_claude):
        write_page(wiki_config.wiki_dir, "a", "---\nauthor: test\n---\n# A\nContent.")
        mock_claude.create.return_value.usage.output_tokens = 10
        mock_claude.create.return_value.usage.input_tokens = 100
        mock_claude.create.return_value.usage.cache_read_input_tokens = 0
        mock_claude.create.return_value.usage.cache_creation_input_tokens = 0
        mock_claude.create.return_value.content = [MagicMock(type="text", text="A summary")]

        page_path = wiki_config.wiki_dir / "a.md"
        fixed = fix_briefs(wiki_config, [page_path])
        assert len(fixed) == 1
        content = page_path.read_text(encoding="utf-8")
        assert "brief: A summary" in content
        assert "author: test" in content

    def test_prepends_frontmatter_when_missing(self, wiki_config, mock_claude):
        write_page(wiki_config.wiki_dir, "a", "# A\nContent without frontmatter.")
        mock_claude.create.return_value.usage.output_tokens = 10
        mock_claude.create.return_value.usage.input_tokens = 100
        mock_claude.create.return_value.usage.cache_read_input_tokens = 0
        mock_claude.create.return_value.usage.cache_creation_input_tokens = 0
        mock_claude.create.return_value.content = [MagicMock(type="text", text="Brief text")]

        page_path = wiki_config.wiki_dir / "a.md"
        fixed = fix_briefs(wiki_config, [page_path])
        assert len(fixed) == 1
        content = page_path.read_text(encoding="utf-8")
        assert content.startswith("---\nbrief: Brief text\n---\n\n")
        assert "# A" in content
