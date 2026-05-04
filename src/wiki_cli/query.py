"""Query the wiki and generate answers with citations."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from .config import Config
from .llm import call_claude


SYSTEM_QUERY = """你是一个知识库助手。根据 wiki 页面内容回答用户的问题。

规则：
- 回答必须基于提供的 wiki 页面内容
- 标注引用的 wiki 页面（使用 [[page-name]] 格式）
- 标注引用的原始材料文件
- 如果信息不足以回答，明确说明
- 如果回答产生了新的有价值知识（如比较、总结、FAQ），建议创建新的 wiki 页面"""

PROMPT_QUERY = """**用户问题**: {question}

**相关 wiki 页面**:
{relevant_pages}

请回答问题，并标注引用来源。

格式：
**回答**: (你的回答)

**引用**:
- [[page-name]] — (引用了什么内容)
- raw/filename — (引用了什么内容)

**建议新页面**: (如果回答产生了新知识，给出建议的页面名称和内容摘要；否则写"无")"""


def run_query(config: Config, question: str) -> str:
    """Query the wiki and return the answer. Records to reports/queries.md."""
    # Find relevant pages
    relevant = _find_relevant_pages(config, question)

    pages_text = "\n\n---\n\n".join(
        f"## {name}\n{content}" for name, content in relevant.items()
    )
    if not pages_text:
        pages_text = "(wiki 中没有找到相关页面)"

    # Call LLM
    answer = call_claude(
        config,
        SYSTEM_QUERY,
        PROMPT_QUERY.format(question=question, relevant_pages=pages_text),
        max_tokens=4096,
    )

    # Print answer
    print(f"\nQ: {question}\n")
    print(answer)

    # Record to reports/queries.md
    _record_query(config, question, answer)

    # Append to log
    _append_log(config, question)

    # Check if LLM suggested a new page
    _check_new_page_suggestion(config, answer)

    return answer


def _find_relevant_pages(config: Config, question: str) -> dict[str, str]:
    """Find wiki pages relevant to the question. Sends all pages if <= 10, otherwise keyword filter."""
    relevant: dict[str, str] = {}
    if not config.wiki_dir.exists():
        return relevant

    all_pages = {
        p: (config.wiki_dir / p).with_suffix(".md")
        for p in _list_page_names(config)
    }

    # If wiki is small enough, just send all pages to LLM
    if len(all_pages) <= 10:
        for name, path in all_pages.items():
            relevant[name] = path.read_text(encoding="utf-8")
        return relevant

    # Otherwise, filter by keyword matching
    keywords = set(re.findall(r"[\w一-鿿]{2,}", question.lower()))

    for name, path in all_pages.items():
        content = path.read_text(encoding="utf-8").lower()
        matches = sum(1 for kw in keywords if kw in content)
        if matches > 0:
            relevant[name] = path.read_text(encoding="utf-8")

    # Fallback: if keyword match found nothing, send all pages
    if not relevant:
        for name, path in all_pages.items():
            relevant[name] = path.read_text(encoding="utf-8")

    return relevant


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
