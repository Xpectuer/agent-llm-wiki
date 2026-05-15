"""File format conversion and LLM-enhanced ingest workflow."""

from __future__ import annotations

import re
import shutil
import subprocess
from datetime import date
from pathlib import Path

from .config import Config
from .llm import call_claude, call_claude_json
from .tracker import get_tracker

# --- Format routing ---

SUPPORTED_EXTENSIONS = {
    ".md", ".txt", ".pdf", ".docx", ".html", ".htm",
    ".epub", ".rtf", ".png", ".jpg", ".jpeg",
}

TOOL_REQUIREMENTS = {
    ".pdf": ("pdftotext", "brew install poppler"),
    ".docx": ("pandoc", "brew install pandoc"),
    ".html": ("pandoc", "brew install pandoc"),
    ".htm": ("pandoc", "brew install pandoc"),
    ".epub": ("pandoc", "brew install pandoc"),
    ".rtf": ("pandoc", "brew install pandoc"),
    ".png": ("tesseract", "brew install tesseract"),
    ".jpg": ("tesseract", "brew install tesseract"),
    ".jpeg": ("tesseract", "brew install tesseract"),
}


def check_tool(ext: str) -> str | None:
    """Check if the required tool for a file extension is available. Returns error msg or None."""
    if ext not in TOOL_REQUIREMENTS:
        return None
    tool, install_hint = TOOL_REQUIREMENTS[ext]
    if shutil.which(tool):
        return None
    return f"Error: {tool} not found for .{ext} files. Install with: {install_hint}"


def convert_file(path: Path) -> str:
    """Convert a raw file to markdown text. Returns the extracted text content."""
    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise SystemExit(f"Error: unsupported format {ext}. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}")

    err = check_tool(ext)
    if err:
        raise SystemExit(err)

    match ext:
        case ".md" | ".txt":
            return path.read_text(encoding="utf-8", errors="replace")
        case ".pdf":
            result = subprocess.run(
                ["pdftotext", "-layout", str(path), "-"],
                capture_output=True, text=True,
            )
            return result.stdout
        case ".docx" | ".html" | ".htm" | ".epub" | ".rtf":
            result = subprocess.run(
                ["pandoc", str(path), "-t", "markdown", "--wrap=none"],
                capture_output=True, text=True,
            )
            return result.stdout
        case ".png" | ".jpg" | ".jpeg":
            result = subprocess.run(
                ["tesseract", str(path), "stdout", "-l", "eng"],
                capture_output=True, text=True,
            )
            return result.stdout
        case _:
            raise SystemExit(f"Error: unsupported format {ext}")


# --- Page naming ---

def slugify(name: str) -> str:
    """Convert a name to a lowercase-hyphenated wiki page slug."""
    return re.sub(r"[^a-z0-9一-鿿]+", "-", name.lower()).strip("-")


# --- LLM prompts ---

SYSTEM_CONCEPT_EXTRACT = """你是一个知识库管理员。你的任务是从原始材料中提取核心概念，
并判断每个概念应该如何融入现有的 wiki 知识库。

规则：
- 输出必须是有效的 JSON
- 每个概念有 name（英文小写连字符）、action（create 或 merge）、target_page 和 summary
- 如果 action 是 merge，target_page 必须是现有页面名称
- 如果 action 是 create，target_page 为 null
- 检测并报告任何歧义或概念冲突"""

PROMPT_CONCEPT_EXTRACT = """分析以下从原始材料提取的文本，以及现有的 wiki 目录结构。

**原始材料文件**: {filename}

**原始材料文本**:
{text}

**现有 wiki 目录**:
{index_content}

**现有 wiki 页面列表**:
{existing_pages}

请提取核心概念，对每个概念判断：
1. 应创建新页面（create）还是合并到已有页面（merge）？
2. 如果合并，合并到哪个页面？
3. 一句话中文摘要

同时报告任何概念歧义。

以 JSON 格式输出：
{{
  "concepts": [
    {{
      "name": "concept-name",
      "action": "create",
      "target_page": null,
      "summary": "一句话摘要"
    }}
  ],
  "ambiguities": [
    {{
      "concept": "concept-name",
      "conflict": "冲突描述",
      "resolution": "建议解决方案"
    }}
  ]
}}"""


SYSTEM_PAGE_GENERATE = """你是一个知识库编辑。根据提供的材料生成 wiki 页面。
规则：
- 使用 Markdown 格式
- 页面标题用 H1
- 在正文开头用 blockquote 标注来源：> Source(s): raw/filename
- 正文内容要完整、准确，保留原始材料的关键信息
- 在底部添加 ## See also 部分，列出相关的 wiki 页面（使用 [[page-name]] 格式）
- 如果是合并操作，将新材料自然融入已有内容，不要简单拼接"""

PROMPT_PAGE_CREATE = """请根据以下原始材料创建一个新的 wiki 页面。

**概念名称**: {concept_name}
**概念摘要**: {summary}
**原始材料文件**: {filename}
**原始材料文本**:
{text}

**现有 wiki 页面**（供交叉引用参考）:
{existing_pages_summary}

请生成完整的 wiki 页面内容（Markdown 格式）。"""

PROMPT_PAGE_MERGE = """请将以下新材料合并到已有的 wiki 页面中。

**目标页面**: {target_page}
**概念摘要**: {summary}
**新材料来源**: {filename}

**已有页面内容**:
{existing_content}

**新材料文本**:
{new_text}

请生成合并后的完整页面内容（保留已有内容并自然融入新材料）。"""


SYSTEM_XREF = """你是一个知识库助手。你的任务是为 wiki 页面建议交叉引用。
规则：
- 输出有效的 JSON
- 为每个页面建议至少 2 个相关的其他页面
- 使用 [[page-name]] 格式
- 只建议确实有内容关联的页面"""

PROMPT_XREF = """分析以下 wiki 页面，为每个页面建议相关的交叉引用。

**所有 wiki 页面**:
{all_pages}

对每个页面，输出建议的 See also 链接：
{{
  "suggestions": [
    {{
      "page": "page-name",
      "see_also": ["related-page-1", "related-page-2"]
    }}
  ]
}}"""


# --- Reusable phase primitives (also used by executor) ---

def extract_concepts(
    config: Config,
    text: str,
    filename: str,
    text_limit: int = 8000,
) -> tuple[list[dict], list[dict]]:
    """Phase 2: LLM concept extraction. Returns (concepts, ambiguities)."""
    index_content = _read_if_exists(config.wiki_dir / "index.md")
    existing_pages = _list_wiki_pages(config)
    existing_pages_str = "\n".join(f"- {p}" for p in existing_pages) or "(none)"

    with get_tracker().phase("convert.extract"):
        result = call_claude_json(
            config,
            SYSTEM_CONCEPT_EXTRACT,
            PROMPT_CONCEPT_EXTRACT.format(
                filename=filename,
                text=text[:text_limit],
                index_content=index_content or "(empty)",
                existing_pages=existing_pages_str,
            ),
        )
    return result.get("concepts", []), result.get("ambiguities", [])


def generate_pages(
    config: Config,
    concepts: list[dict],
    text: str,
    filename: str,
    text_limit: int = 6000,
) -> list[tuple[Path, dict]]:
    """Phase 3: LLM page generation. Returns list of (page_path, concept_dict)."""
    existing_pages_summary = "\n".join(f"- [[{p}]]" for p in _list_wiki_pages(config)) or "(none)"
    created_pages: list[tuple[Path, dict]] = []

    with get_tracker().phase("convert.generate"):
        for concept in concepts:
            page_name = slugify(concept["name"])
            page_path = config.wiki_dir / f"{page_name}.md"

            if concept["action"] == "merge" and concept.get("target_page"):
                target_page = concept["target_page"]
                target_path = config.wiki_dir / f"{target_page}.md"
                existing_content = _read_if_exists(target_path) or ""

                page_content = call_claude(
                    config,
                    SYSTEM_PAGE_GENERATE,
                    PROMPT_PAGE_MERGE.format(
                        target_page=target_page,
                        summary=concept.get("summary", ""),
                        filename=filename,
                        existing_content=existing_content,
                        new_text=text[:text_limit],
                    ),
                )
                page_path = target_path
            else:
                page_content = call_claude(
                    config,
                    SYSTEM_PAGE_GENERATE,
                    PROMPT_PAGE_CREATE.format(
                        concept_name=concept["name"],
                        summary=concept.get("summary", ""),
                        filename=filename,
                        text=text[:text_limit],
                        existing_pages_summary=existing_pages_summary,
                    ),
                )

            config.wiki_dir.mkdir(parents=True, exist_ok=True)
            page_path.write_text(page_content, encoding="utf-8")
            created_pages.append((page_path, concept))
            print(f"  Written: {page_path}")

    return created_pages


def run_cross_references(config: Config) -> None:
    """Phase 4: refresh cross-references across all wiki pages."""
    all_pages = _read_all_wiki_pages(config)
    if len(all_pages) >= 2:
        pages_text = "\n\n---\n\n".join(
            f"## {name}\n{content[:2000]}" for name, content in all_pages.items()
        )
        with get_tracker().phase("convert.xref"):
            xref_result = call_claude_json(
                config,
                SYSTEM_XREF,
                PROMPT_XREF.format(all_pages=pages_text),
            )
            suggestions = xref_result.get("suggestions", [])
            for sug in suggestions:
                page_name = sug["page"]
                page_path = config.wiki_dir / f"{page_name}.md"
                if page_path.exists():
                    _update_see_also(page_path, sug.get("see_also", []))
    else:
        print("  Skipped: need at least 2 pages for cross-referencing")


def update_index_and_log(
    config: Config,
    created_page_paths: list[Path],
    concepts: list[dict],
    filename: str,
    today: str | None = None,
) -> None:
    """Phase 5: update wiki/index.md and wiki/log.md."""
    if today is None:
        today = date.today().isoformat()
    _update_index(config, created_page_paths, concepts)
    _append_log(config, today, "convert", filename, concepts)


# --- Main convert workflow ---

def run_convert(
    config: Config,
    target: Path,
    title: str | None = None,
) -> list[Path]:
    """Run the full convert workflow on a single file. Returns list of created/updated page paths."""
    target = target.resolve()
    if not target.exists():
        raise SystemExit(f"Error: {target} not found")

    filename = target.name
    today = date.today().isoformat()

    # Phase 1: Format conversion
    print(f"[Phase 1] Converting {filename}...")
    text = convert_file(target)
    if not text.strip():
        print(f"  Warning: {filename} produced empty content, skipping.")
        return []

    # Copy raw file to raw/ if not already there
    raw_dest = config.raw_dir / filename
    if not raw_dest.exists():
        config.raw_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, raw_dest)
        print(f"  Copied to {raw_dest}")

    # Phase 2: Concept extraction (LLM)
    print("[Phase 2] Extracting concepts...")
    concepts, ambiguities = extract_concepts(config, text, filename)

    print(f"  Found {len(concepts)} concept(s):")
    for c in concepts:
        action_str = f"merge → {c['target_page']}" if c["action"] == "merge" else "create new"
        print(f"    - {c['name']}: {action_str} — {c.get('summary', '')}")

    if ambiguities:
        print(f"  Ambiguities ({len(ambiguities)}):")
        for a in ambiguities:
            print(f"    - {a.get('concept', '?')}: {a.get('conflict', '')}")

    # Write instruction file
    _write_instruction(config, today, filename, concepts, ambiguities)

    # Phase 3: Page generation (LLM)
    print("[Phase 3] Generating wiki pages...")
    created = generate_pages(config, concepts, text, filename)
    created_page_paths = [p for p, _ in created]

    # Phase 4: Cross-references (LLM)
    print("[Phase 4] Updating cross-references...")
    run_cross_references(config)

    # Phase 5: Update index and log
    print("[Phase 5] Finalizing...")
    update_index_and_log(config, created_page_paths, concepts, filename, today)

    print(f"\nDone. Created/updated {len(created_page_paths)} page(s).")
    return created_page_paths


# --- Helpers ---

def _read_if_exists(path: Path) -> str | None:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


def _list_wiki_pages(config: Config) -> list[str]:
    """List wiki page names (without .md extension), excluding index and log."""
    if not config.wiki_dir.exists():
        return []
    return [
        p.stem
        for p in config.wiki_dir.glob("*.md")
        if p.stem not in ("index", "log")
    ]


def _read_all_wiki_pages(config: Config) -> dict[str, str]:
    """Read all wiki pages into a dict of name -> content."""
    pages = {}
    if not config.wiki_dir.exists():
        return pages
    for p in config.wiki_dir.glob("*.md"):
        if p.stem not in ("index", "log"):
            pages[p.stem] = p.read_text(encoding="utf-8")
    return pages


def _update_see_also(page_path: Path, suggestions: list[str]) -> None:
    """Update the ## See also section of a wiki page."""
    content = page_path.read_text(encoding="utf-8")
    see_also_lines = [f"- [[{s}]]" for s in suggestions]
    new_section = "## See also\n" + "\n".join(see_also_lines) + "\n"

    # Replace existing See also section or append
    pattern = r"## See also\n(?:.*\n)*"
    if re.search(pattern, content):
        content = re.sub(pattern, new_section, content)
    else:
        content = content.rstrip() + "\n\n" + new_section

    page_path.write_text(content, encoding="utf-8")


def _update_index(config: Config, created_pages: list[Path], concepts: list[dict]) -> None:
    """Update wiki/index.md with new pages."""
    index_path = config.wiki_dir / "index.md"
    if not index_path.exists():
        return

    content = index_path.read_text(encoding="utf-8")
    today = date.today().isoformat()

    # Update the date
    content = re.sub(
        r"> Last updated:.*",
        f"> Last updated: {today}",
        content,
    )

    # Add new pages under appropriate sections
    for concept in concepts:
        page_name = slugify(concept["name"])
        summary = concept.get("summary", "")
        entry = f"- [[{page_name}]] -- {summary}"

        # Simple heuristic: add under ## Synthesis for now
        if "## Synthesis" in content:
            content = content.replace(
                "## Synthesis\n",
                f"## Synthesis\n{entry}\n",
            )
        elif "## Concepts" in content:
            content = content.replace(
                "## Concepts\n",
                f"## Concepts\n{entry}\n",
            )

    index_path.write_text(content, encoding="utf-8")


def _append_log(config: Config, today: str, operation: str, source: str, concepts: list[dict]) -> None:
    """Append an entry to wiki/log.md."""
    log_path = config.wiki_dir / "log.md"
    if not log_path.exists():
        return

    pages = ", ".join(slugify(c["name"]) for c in concepts)
    entry = (
        f"\n## [{today}] {operation} | {source}\n"
        f"- Extracted {len(concepts)} concept(s): {pages}\n"
    )
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(entry)


def _write_instruction(config: Config, today: str, filename: str, concepts: list[dict], ambiguities: list[dict]) -> Path:
    """Write a detailed instruction file for this convert operation."""
    config.reports_dir.mkdir(parents=True, exist_ok=True)
    path = config.reports_dir / f"instruction-{today}-{Path(filename).stem}.md"

    lines = [
        f"# Convert Instruction: {filename}",
        f"> Generated: {today}",
        "",
        "## Concepts Extracted",
        "",
    ]
    for c in concepts:
        action_str = f"merge → {c['target_page']}" if c["action"] == "merge" else "create"
        lines.append(f"- **{c['name']}** ({action_str}): {c.get('summary', '')}")

    if ambiguities:
        lines.append("")
        lines.append("## Ambiguities")
        lines.append("")
        for a in ambiguities:
            lines.append(f"- **{a.get('concept', '?')}**: {a.get('conflict', '')}")
            lines.append(f"  Resolution: {a.get('resolution', 'N/A')}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  Instruction: {path}")
    return path
