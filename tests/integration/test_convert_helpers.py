from wiki_cli.convert import (
    _append_log,
    _list_wiki_pages,
    _read_all_wiki_pages,
    _update_index,
    _update_see_also,
    _write_instruction,
)


class TestUpdateSeeAlso:
    def test_replaces_existing_section(self, wiki_config):
        page = wiki_config.wiki_dir / "a.md"
        page.write_text("# A\n\nContent.\n\n## See also\n- [[old]]\n", encoding="utf-8")
        _update_see_also(page, ["transformer", "bert"])
        content = page.read_text(encoding="utf-8")
        assert "[[transformer]]" in content
        assert "[[bert]]" in content
        assert "[[old]]" not in content

    def test_appends_when_no_see_also(self, wiki_config):
        page = wiki_config.wiki_dir / "a.md"
        page.write_text("# A\n\nContent.\n", encoding="utf-8")
        _update_see_also(page, ["rlhf"])
        content = page.read_text(encoding="utf-8")
        assert "## See also" in content
        assert "[[rlhf]]" in content

    def test_handles_wikilink_brackets_in_input(self, wiki_config):
        page = wiki_config.wiki_dir / "a.md"
        page.write_text("# A\n\n## See also\n- [[old]]\n", encoding="utf-8")
        _update_see_also(page, ["[[transformer]]", "[[bert]]"])
        content = page.read_text(encoding="utf-8")
        assert "[[transformer]]" in content
        # Should not double-wrap
        assert "[[[[transformer]]]]" not in content

    def test_handles_md_extension_in_input(self, wiki_config):
        page = wiki_config.wiki_dir / "a.md"
        page.write_text("# A\n\n## See also\n- [[old]]\n", encoding="utf-8")
        _update_see_also(page, ["transformer.md"])
        content = page.read_text(encoding="utf-8")
        assert "[[transformer]]" in content
        assert "[[transformer.md]]" not in content


class TestUpdateIndex:
    def test_adds_under_synthesis(self, wiki_config):
        index = wiki_config.wiki_dir / "index.md"
        index.write_text("# Index\n\n## Synthesis\n\n", encoding="utf-8")
        concepts = [{"name": "transformer", "summary": "Transformer architecture"}]
        _update_index(wiki_config, [wiki_config.wiki_dir / "transformer.md"], concepts)
        content = index.read_text(encoding="utf-8")
        assert "[[transformer]]" in content
        assert "Transformer architecture" in content

    def test_adds_under_concepts(self, wiki_config):
        index = wiki_config.wiki_dir / "index.md"
        index.write_text("# Index\n\n## Concepts\n\n", encoding="utf-8")
        concepts = [{"name": "rlhf", "summary": "RLHF method"}]
        _update_index(wiki_config, [wiki_config.wiki_dir / "rlhf.md"], concepts)
        content = index.read_text(encoding="utf-8")
        assert "[[rlhf]]" in content

    def test_index_not_exists(self, wiki_config):
        concepts = [{"name": "test", "summary": "test"}]
        # Should not raise
        _update_index(wiki_config, [], concepts)


class TestAppendLog:
    def test_appends_entry(self, wiki_config):
        log = wiki_config.wiki_dir / "log.md"
        log.write_text("# Log\n", encoding="utf-8")
        concepts = [{"name": "gpt"}, {"name": "bert"}]
        _append_log(wiki_config, "2026-05-18", "convert", "test.pdf", concepts)
        content = log.read_text(encoding="utf-8")
        assert "2026-05-18" in content
        assert "convert" in content
        assert "test.pdf" in content
        assert "gpt" in content

    def test_log_not_exists(self, wiki_config):
        concepts = [{"name": "test"}]
        # Should not raise
        _append_log(wiki_config, "2026-05-18", "convert", "test.pdf", concepts)


class TestWriteInstruction:
    def test_writes_instruction_file(self, wiki_config):
        concepts = [
            {"name": "transformer", "action": "create", "summary": "A model architecture"},
            {
                "name": "attention",
                "action": "merge",
                "target_page": "attention-mechanism",
                "summary": "Attention layer",
            },
        ]
        ambiguities = [
            {
                "concept": "attention",
                "conflict": "Multiple pages on attention",
                "resolution": "Dedicated page",
            },
        ]
        path = _write_instruction(wiki_config, "2026-05-18", "test.pdf", concepts, ambiguities)
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "test.pdf" in content
        assert "transformer" in content
        assert "merge" in content
        assert "attention" in content

    def test_no_ambiguities(self, wiki_config):
        concepts = [{"name": "simple", "action": "create", "summary": "Simple concept"}]
        path = _write_instruction(wiki_config, "2026-05-18", "test.pdf", concepts, [])
        assert path.exists()


class TestListWikiPages:
    def test_regular_pages(self, wiki_config):
        (wiki_config.wiki_dir / "a.md").write_text("# A")
        (wiki_config.wiki_dir / "b.md").write_text("# B")
        assert sorted(_list_wiki_pages(wiki_config)) == ["a", "b"]

    def test_excludes_index_and_log(self, wiki_config):
        (wiki_config.wiki_dir / "data.md").write_text("# D")
        (wiki_config.wiki_dir / "index.md").write_text("# I")
        (wiki_config.wiki_dir / "log.md").write_text("# L")
        assert _list_wiki_pages(wiki_config) == ["data"]


class TestReadAllWikiPages:
    def test_reads_content(self, wiki_config):
        (wiki_config.wiki_dir / "a.md").write_text("# A content")
        pages = _read_all_wiki_pages(wiki_config)
        assert pages == {"a": "# A content"}
