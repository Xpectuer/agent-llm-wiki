from wiki_cli.convert import parse_frontmatter


def test_standard_frontmatter():
    content = """---
brief: A summary
author: someone
---
# Title
Body text."""
    assert parse_frontmatter(content) == {"brief": "A summary", "author": "someone"}


def test_no_frontmatter():
    content = "# Just a title\n\nBody text."
    assert parse_frontmatter(content) == {}


def test_empty_frontmatter():
    content = """---
---
# Title"""
    assert parse_frontmatter(content) == {}


def test_no_closing_delimiter():
    content = """---
brief: unfinished
# Title"""
    assert parse_frontmatter(content) == {}


def test_multiline_frontmatter_value():
    content = """---
brief: A very long summary
tags: tag1, tag2
---
# Title"""
    fm = parse_frontmatter(content)
    assert fm["brief"] == "A very long summary"
    assert fm["tags"] == "tag1, tag2"


def test_frontmatter_only():
    content = """---
brief: standalone
---
"""
    assert parse_frontmatter(content) == {"brief": "standalone"}


def test_colon_in_yaml_value():
    content = """---
brief: Title: subtitle
url: https://example.com
---
# Content"""
    fm = parse_frontmatter(content)
    assert fm["brief"] == "Title: subtitle"
    assert fm["url"] == "https://example.com"
