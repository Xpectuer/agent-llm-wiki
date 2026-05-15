"""Query the wiki and generate answers with citations — agentic tool-calling flow."""

from __future__ import annotations

import re
from datetime import date

from .config import Config
from .llm import call_claude_with_tools
from .tracker import get_tracker

SYSTEM_QUERY = """你是一个知识库助手。你可以使用工具来搜索和阅读 wiki 页面内容。

规则：
- 首先使用 search_wiki 工具查找与问题相关的页面
- 尝试不同的搜索关键词，确保找到所有相关内容
- 对 search_wiki 返回的有希望的结果，使用 read_page 工具阅读完整内容
- 可以多次搜索和阅读，直到收集到足够的信息
- 在阅读了足够的页面后，合成最终答案
- 回答必须基于 wiki 页面内容，标注引用的 wiki 页面（使用 [[page-name]] 格式）
- 标注引用的原始材料文件（raw/filename）
- 如果信息不足以回答，明确说明
- 如果回答产生了新的有价值知识（如比较、总结、FAQ），建议创建新的 wiki 页面"""

PROMPT_QUERY = """**用户问题**: {question}

请使用可用的工具搜索 wiki 知识库，找到相关信息后回答问题。

格式：
**回答**: (你的回答)

**引用**:
- [[page-name]] — (引用了什么内容)
- raw/filename — (引用了什么内容)

**建议新页面**: (如果回答产生了新知识，给出建议的页面名称和内容摘要；否则写"无")"""

TOOLS = [
    {
        "name": "search_wiki",
        "description": "Search across all wiki pages for relevant content. "
                       "Returns ranked snippets with page names and line numbers. "
                       "Use this when you need to find which pages discuss a topic.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query. Use keywords relevant to the user's question."
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "read_page",
        "description": "Read the full content of a specific wiki page by name. "
                       "Use this after identifying relevant pages via search_wiki. "
                       "Use the filename stem (without .md extension).",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The page name (without .md extension), e.g. 'transformer' or 'bert'."
                }
            },
            "required": ["name"]
        }
    }
]


def run_query(config: Config, question: str) -> str:
    """Query the wiki and return the answer. Records to reports/queries.md."""

    def execute_tool(name: str, input_data: dict) -> str:
        if name == "search_wiki":
            return _search_wiki(config, input_data["query"])
        elif name == "read_page":
            return _read_page(config, input_data["name"])
        else:
            return f"Error: unknown tool '{name}'"

    with get_tracker().phase("query"):
        answer = call_claude_with_tools(
            config,
            SYSTEM_QUERY,
            PROMPT_QUERY.format(question=question),
            TOOLS,
            execute_tool=execute_tool,
        )

    print(f"\nQ: {question}\n")
    print(answer)

    _record_query(config, question, answer)
    _append_log(config, question)
    _check_new_page_suggestion(config, answer)

    return answer


def _search_wiki(config: Config, query: str) -> str:
    """Full-text search across all wiki pages. Returns ranked snippets."""
    pages = _list_page_names(config)
    if not pages:
        return "(wiki 中没有页面)"

    # Tokenize: keep alphanumeric and CJK chars of 2+ length
    tokens = [t for t in re.findall(r"[\w一-鿿]{2,}", query.lower())]
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
                    ctx = "\n".join(
                        f"  L{j+1}: {lines[j][:120]}"
                        for j in range(start, end)
                    )
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


def _read_page(config: Config, name: str) -> str:
    """Read the full content of a wiki page."""
    clean_name = name.strip().removesuffix(".md")
    path = config.wiki_dir / f"{clean_name}.md"
    if not path.exists():
        available = ", ".join(_list_page_names(config))
        return f"Error: 页面 '{clean_name}' 不存在。可用页面: {available}"
    return path.read_text(encoding="utf-8")


def _list_page_names(config: Config) -> list[str]:
    if not config.wiki_dir.exists():
        return []
    return [
        p.stem
        for p in config.wiki_dir.glob("*.md")
        if p.stem not in ("index", "log")
    ]


def _record_query(config: Config, question: str, answer: str) -> None:
    """Record the query in reports/queries.md."""
    queries_path = config.reports_dir / "queries.md"
    config.reports_dir.mkdir(parents=True, exist_ok=True)

    today = date.today().isoformat()
    entry = f"\n## [{today}] {question}\n\n{answer}\n\n---\n"

    if queries_path.exists():
        with open(queries_path, "a", encoding="utf-8") as f:
            f.write(entry)
    else:
        queries_path.write_text(f"# Queries\n{entry}", encoding="utf-8")

    print(f"\nQuery recorded to {queries_path}")


def _append_log(config: Config, question: str) -> None:
    """Append query entry to wiki/log.md."""
    log_path = config.wiki_dir / "log.md"
    if not log_path.exists():
        return

    today = date.today().isoformat()
    entry = f"\n## [{today}] query | {question[:60]}\n- Queried wiki and recorded answer.\n"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(entry)


def _check_new_page_suggestion(config: Config, answer: str) -> None:
    """Check if the answer suggests creating a new page, and write instruction file."""
    if "建议新页面" not in answer and "无" in answer.split("建议新页面")[-1][:50]:
        return

    config.reports_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    path = config.reports_dir / f"instruction-{today}-query.md"

    lines = [
        f"# Query-Generated Page Suggestion ({today})",
        "",
        answer,
        "",
        "## Action Required",
        "- Review the suggested new page above",
        "- If valuable, create the wiki page using `wiki convert` or manually",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"New page suggestion written to {path}")
