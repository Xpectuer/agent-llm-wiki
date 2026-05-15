"""Document structure analysis: ToC scanning, DAG construction, chapter splitting."""

from __future__ import annotations

import json
import re
from collections import defaultdict, deque
from datetime import date
from pathlib import Path

from .config import Config
from .llm import call_claude_json
from .models import Chapter, Plan
from .tracker import get_tracker

# --- LLM prompts ---

SYSTEM_PLAN = """你是一个文档结构分析师。你的任务是分析大型文档的目录结构，
识别章节边界、顺序和依赖关系。

规则：
- 输出必须是有效的 JSON
- 每个章节必须有唯一的 id（如 ch-01）
- 每个章节必须有 heading_pattern（用于定位章节边界的正则表达式或关键词）
- depends_on 列出该章节依赖的前置章节 id（引用或需要先理解的章节）
- 依赖关系必须无环
- 为每个章节提供一句话中文摘要"""

PROMPT_PLAN = """分析以下文档的目录结构和章节组织。

**文档文件**: {filename}

**文档文本**（开头部分，用于识别目录结构）:
{text}

请识别：
1. 文档有多少个主要章节？
2. 每个章节的标题是什么？
3. 各章节之间的依赖关系（哪些章节需要先阅读其他章节才能理解）
4. 用于定位章节边界的文本模式

如果没有找到明确的章节结构，请将文本按主题自然分段。

以 JSON 格式输出：
{{
  "chapters": [
    {{
      "id": "ch-01",
      "title": "章节标题",
      "order": 1,
      "heading_pattern": "用于定位章节的正则模式或关键词",
      "depends_on": [],
      "summary": "一句话中文摘要"
    }}
  ]
}}"""


# --- DAG validation ---

def _validate_dag(chapters: list[Chapter]) -> None:
    """Check for invalid dependency references and cycles. Raises ValueError."""
    ids = {c.id for c in chapters}

    for ch in chapters:
        for dep in ch.depends_on:
            if dep not in ids:
                raise ValueError(
                    f"Chapter '{ch.id}' depends on unknown chapter '{dep}'"
                )

    # Cycle detection via DFS
    white, gray, black = set(ids), set(), set()

    def visit(node_id: str) -> None:
        if node_id in black:
            return
        if node_id in gray:
            raise ValueError(f"Cycle detected in chapter dependencies involving '{node_id}'")
        white.discard(node_id)
        gray.add(node_id)
        ch = next(c for c in chapters if c.id == node_id)
        for dep in ch.depends_on:
            visit(dep)
        gray.discard(node_id)
        black.add(node_id)

    while white:
        visit(next(iter(white)))


def _topological_levels(chapters: list[Chapter]) -> list[list[str]]:
    """Kahn's algorithm: return list of levels, each a list of chapter IDs runnable in parallel."""
    in_degree: dict[str, int] = {c.id: 0 for c in chapters}
    adj: dict[str, list[str]] = defaultdict(list)

    for ch in chapters:
        for dep in ch.depends_on:
            adj[dep].append(ch.id)
            in_degree[ch.id] += 1

    queue = deque(c.id for c in chapters if in_degree[c.id] == 0)
    levels: list[list[str]] = []
    remaining = len(chapters)

    while queue:
        level = list(queue)
        queue.clear()
        levels.append(level)
        remaining -= len(level)

        for node_id in level:
            for neighbor in adj[node_id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

    if remaining != 0:
        raise ValueError("Cycle detected: unable to resolve all chapter dependencies")

    return levels


# --- Plan phase ---

def plan_document(
    config: Config,
    text: str,
    filename: str,
    text_limit: int = 12000,
) -> Plan:
    """Analyze document structure via LLM. Returns a Plan with chapters and DAG metadata."""
    with get_tracker().phase("convert.plan"):
        result = call_claude_json(
            config,
            SYSTEM_PLAN,
            PROMPT_PLAN.format(
                filename=filename,
                text=text[:text_limit],
            ),
        )

    chapters_data = result.get("chapters", [])
    if not chapters_data:
        # Fallback: single chapter for the whole document
        return Plan(
            source_file=filename,
            total_chars=len(text),
            chapters=[
                Chapter(
                    id="ch-01",
                    title="Full Document",
                    order=1,
                    heading_pattern="",
                    depends_on=[],
                    summary="Entire document as single chapter",
                )
            ],
            metadata={"fallback": True},
        )

    chapters = [
        Chapter(
            id=ch["id"],
            title=ch["title"],
            order=ch["order"],
            heading_pattern=ch.get("heading_pattern", ""),
            depends_on=ch.get("depends_on", []),
            summary=ch.get("summary", ""),
        )
        for ch in chapters_data
    ]
    chapters.sort(key=lambda c: c.order)

    _validate_dag(chapters)

    return Plan(
        source_file=filename,
        total_chars=len(text),
        chapters=chapters,
        metadata={"model": config.model},
    )


def save_plan(plan: Plan, config: Config) -> Path:
    """Save a Plan as JSON to reports/. Returns the path."""
    config.reports_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    stem = Path(plan.source_file).stem
    path = config.reports_dir / f"plan-{today}-{stem}.json"

    data = {
        "source_file": plan.source_file,
        "total_chars": plan.total_chars,
        "chapters": [
            {
                "id": ch.id,
                "title": ch.title,
                "order": ch.order,
                "heading_pattern": ch.heading_pattern,
                "depends_on": ch.depends_on,
                "summary": ch.summary,
            }
            for ch in plan.chapters
        ],
        "metadata": plan.metadata,
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_plan(plan_path: Path) -> Plan:
    """Load a Plan from a JSON file."""
    data = json.loads(plan_path.read_text(encoding="utf-8"))
    return Plan(
        source_file=data["source_file"],
        total_chars=data["total_chars"],
        chapters=[
            Chapter(
                id=ch["id"],
                title=ch["title"],
                order=ch["order"],
                heading_pattern=ch.get("heading_pattern", ""),
                depends_on=ch.get("depends_on", []),
                summary=ch.get("summary", ""),
            )
            for ch in data["chapters"]
        ],
        metadata=data.get("metadata", {}),
    )


# --- Chapter splitting ---

def split_chapters(full_text: str, chapters: list[Chapter]) -> dict[str, str]:
    """Split full document text into per-chapter segments using heading patterns.

    Returns dict of chapter_id -> chapter_text.
    """
    if len(chapters) == 1:
        return {chapters[0].id: full_text}

    segments: dict[str, str] = {}
    sorted_chapters = sorted(chapters, key=lambda c: c.order)

    # Try regex-based splitting using heading_patterns
    positions: list[tuple[int, str, str | None]] = []  # (start, chapter_id, end_pattern)

    for i, ch in enumerate(sorted_chapters):
        pattern = ch.heading_pattern
        if pattern:
            try:
                match = re.search(pattern, full_text, re.MULTILINE | re.IGNORECASE)
                if match:
                    positions.append((match.start(), ch.id, pattern))
                    continue
            except re.error:
                pass
        # Fallback: approximate position by proportional text split
        positions.append((-1, ch.id, None))

    # Assign text segments
    text_len = len(full_text)
    for i, (pos, ch_id, _) in enumerate(positions):
        if i < len(positions) - 1:
            next_pos = positions[i + 1][0]
            if next_pos > 0:
                segments[ch_id] = full_text[pos:next_pos]
                continue

        # Last chapter or position unknown: proportional split
        if pos >= 0:
            segments[ch_id] = full_text[pos:]
        else:
            # Proportional fallback
            start_frac = i / len(chapters)
            end_frac = (i + 1) / len(chapters)
            segments[ch_id] = full_text[int(start_frac * text_len):int(end_frac * text_len)]

    return segments


def describe_plan(plan: Plan) -> str:
    """Render a human-readable summary of the plan."""
    levels = _topological_levels(plan.chapters)
    lines = [
        f"Plan: {plan.source_file} ({plan.total_chars:,} chars)",
        f"Found {len(plan.chapters)} chapter(s) in {len(levels)} DAG level(s):",
        "",
    ]
    for i, level in enumerate(levels, 1):
        level_chapters = [next(c for c in plan.chapters if c.id == cid) for cid in level]
        chapter_desc = ", ".join(
            f"{ch.id}: {ch.title} {'(depends: ' + ', '.join(ch.depends_on) + ')' if ch.depends_on else '(no deps)'}"
            for ch in level_chapters
        )
        parallel_note = f" ← {len(level)} parallel" if len(level) > 1 else ""
        lines.append(f"  Level {i}: [{chapter_desc}]{parallel_note}")

    return "\n".join(lines)
