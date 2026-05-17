"""Shared wiki tool implementations for agentic tool-calling loops.

Used by both `wiki query` and (now) `wiki convert` / `wiki execute`.
"""

from __future__ import annotations

import re

from .config import Config

# --- Tool definitions (Anthropic API format) ---

TOOLS = [
    {
        "name": "search_wiki",
        "description": (
            "Search across all wiki pages for relevant content. "
            "Returns ranked snippets with page names and line numbers. "
            "Use this to find which pages discuss a topic."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query. Use keywords relevant to the topic.",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "read_page",
        "description": (
            "Read the full content of a specific wiki page by name. "
            "Use this after identifying relevant pages via search_wiki. "
            "Use the filename stem (without .md extension)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The page name (without .md extension), e.g. 'transformer' or 'bert'.",
                }
            },
            "required": ["name"],
        },
    },
    {
        "name": "list_pages",
        "description": (
            "List all wiki page names (without .md extension). "
            "Use this to get an overview of what pages exist in the wiki."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]


# --- Tool implementations ---


def search_wiki(config: Config, query: str) -> str:
    """Full-text search across all wiki pages. Returns ranked snippets."""
    pages = _list_page_names(config)
    if not pages:
        return "(wiki 中没有页面)"

    # Tokenize: keep alphanumeric and CJK chars of 2+ length
    tokens = list(re.findall(r"[\w一-鿿]{2,}", query.lower()))
    if not tokens:
        tokens = [query.lower().strip()]

    scored: list[tuple[int, str, list[str]]] = []

    for name in pages:
        path = config.wiki_dir / f"{name}.md"
        content = path.read_text(encoding="utf-8")
        lines = content.split("\n")
        content_lower = content.lower()

        score = 0
        seen_lines: set[int] = set()
        snippets: list[str] = []

        for token in tokens:
            score += content_lower.count(token)
            for i, line in enumerate(lines):
                if i in seen_lines:
                    continue
                if token in line.lower():
                    seen_lines.add(i)
                    start = max(0, i - 1)
                    end = min(len(lines), i + 2)
                    ctx = "\n".join(f"  L{j + 1}: {lines[j][:120]}" for j in range(start, end))
                    snippets.append(ctx)
                    if len(snippets) >= 5:
                        break
            if len(snippets) >= 5:
                break

        if score > 0:
            scored.append((score, name, snippets))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:10]

    if not top:
        return f"未找到与 '{query}' 相关的页面。"

    result_parts = [f"搜索结果 '{query}':\n"]
    for score, name, snippets in top:
        result_parts.append(f"\n## [[{name}]] (相关度: {score})")
        for s in snippets:
            result_parts.append(s)
    return "\n".join(result_parts)


def read_page(config: Config, name: str) -> str:
    """Read the full content of a wiki page."""
    clean_name = name.strip().removesuffix(".md")
    path = config.wiki_dir / f"{clean_name}.md"
    if not path.exists():
        available = ", ".join(_list_page_names(config))
        return f"Error: 页面 '{clean_name}' 不存在。可用页面: {available}"
    return path.read_text(encoding="utf-8")


def list_pages(config: Config) -> str:
    """List all wiki page names."""
    pages = _list_page_names(config)
    if not pages:
        return "(wiki 中没有页面)"
    return "\n".join(f"- [[{p}]]" for p in sorted(pages))


def _list_page_names(config: Config) -> list[str]:
    """List wiki page names (without .md extension), excluding index and log."""
    if not config.wiki_dir.exists():
        return []
    return [p.stem for p in config.wiki_dir.glob("*.md") if p.stem not in ("index", "log")]


def make_executor(config: Config):
    """Create an execute_tool callback for use with call_claude_with_tools."""

    def execute_tool(name: str, input_data: dict) -> str:
        if name == "search_wiki":
            return search_wiki(config, input_data["query"])
        elif name == "read_page":
            return read_page(config, input_data["name"])
        elif name == "list_pages":
            return list_pages(config)
        else:
            return f"Error: unknown tool '{name}'"

    return execute_tool
