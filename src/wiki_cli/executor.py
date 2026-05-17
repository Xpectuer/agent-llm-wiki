"""DAG-aware parallel chapter execution via ThreadPoolExecutor."""

from __future__ import annotations

import re
import threading
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .config import Config
from .convert import (
    extract_concepts,
    generate_pages,
    run_cross_references,
    update_index_and_log,
)
from .llm import call_claude_json
from .models import Chapter, ChapterResult, Plan
from .planner import _topological_levels, split_chapters
from .tracker import get_tracker

# --- Dedup prompts ---

SYSTEM_DEDUP = """你是一个知识库管理员。你的任务是检查一批新创建的 wiki 页面，
找出内容重叠或冗余的页面并建议合并。

规则：
- 输出有效的 JSON
- 只建议确实有显著内容重叠的合并
- 合并时指明源页面和目标页面
- 如果页面之间有互补关系但不重叠，不要建议合并"""

PROMPT_DEDUP = """检查以下从同一份文档创建的新 wiki 页面，找出冗余或过度重叠的页面。

**新创建的页面**:
{pages_text}

建议合并（如有）：
{{
  "merges": [
    {{
      "source": "page-to-merge-from",
      "target": "page-to-merge-into",
      "reason": "合并原因（一句话）"
    }}
  ]
}}

如果没有需要合并的页面，返回空列表。"""


def execute_plan(
    config: Config,
    plan: Plan,
    full_text: str,
    max_workers: int = 4,
) -> list[ChapterResult]:
    """Execute a Plan: split text, process chapters in DAG order, parallel within each level.

    Returns a list of ChapterResult, one per chapter.
    """
    if not plan.chapters:
        print("Plan has no chapters to execute.")
        return []

    # Split full text into per-chapter segments
    print(f"Splitting text into {len(plan.chapters)} chapter(s)...")
    chapter_texts = split_chapters(full_text, plan.chapters)
    for ch in plan.chapters:
        ch_len = len(chapter_texts.get(ch.id, ""))
        print(f"  {ch.id}: {ch_len:,} chars — {ch.title}")

    # Compute DAG levels
    levels = _topological_levels(plan.chapters)
    print(f"\nExecuting {len(levels)} DAG level(s) with max {max_workers} worker(s):")

    # Per-page locks for merge conflict safety
    page_locks: dict[str, threading.Lock] = {}
    page_locks_lock = threading.Lock()

    def get_page_lock(page_name: str) -> threading.Lock:
        with page_locks_lock:
            if page_name not in page_locks:
                page_locks[page_name] = threading.Lock()
            return page_locks[page_name]

    all_results: list[ChapterResult] = []
    chapter_map = {c.id: c for c in plan.chapters}

    for level_idx, level in enumerate(levels, 1):
        chapters_in_level = [chapter_map[cid] for cid in level]
        chapter_desc = ", ".join(f"{c.id} ({c.title})" for c in chapters_in_level)
        parallel_tag = f" [parallel x{len(level)}]" if len(level) > 1 else ""
        print(f"\n  Level {level_idx}: {chapter_desc}{parallel_tag}")

        with ThreadPoolExecutor(max_workers=min(max_workers, len(level))) as executor:
            futures = {}
            for ch in chapters_in_level:
                ch_text = chapter_texts.get(ch.id, "")
                future = executor.submit(
                    _process_chapter,
                    config,
                    ch,
                    ch_text,
                    get_page_lock,
                )
                futures[future] = ch.id

            level_results: list[ChapterResult] = []
            for future in as_completed(futures):
                ch_id = futures[future]
                try:
                    result = future.result()
                except Exception as e:
                    result = ChapterResult(
                        chapter_id=ch_id,
                        status="failed",
                        error=str(e),
                    )
                level_results.append(result)
                status_icon = "✓" if result.status == "success" else "✗"
                pages_str = ", ".join(result.pages_created) if result.pages_created else "none"
                print(f"    {status_icon} {ch_id}: {result.status} — pages: {pages_str}")
                if result.error:
                    print(f"      Error: {result.error}")

            all_results.extend(level_results)

    return all_results


def _process_chapter(
    config: Config,
    chapter: Chapter,
    chapter_text: str,
    get_page_lock: Callable[[str], threading.Lock],
) -> ChapterResult:
    """Process a single chapter through Phase 2-3 of the convert pipeline.

    Thread-safe: acquires per-page locks before writing merges.
    """
    try:
        filename = f"{chapter.id}-{chapter.title}"
        print(f"      [{chapter.id}] Extracting concepts...")

        concepts, _ = extract_concepts(config, chapter_text, filename)

        if not concepts:
            return ChapterResult(
                chapter_id=chapter.id,
                status="success",
                concepts=[],
                pages_created=[],
            )

        print(f"      [{chapter.id}] Found {len(concepts)} concept(s), generating pages...")

        # Generate pages with lock protection for merges
        created_pages: list[str] = []
        for concept in concepts:
            page_name = concept.get("name", "")
            target_page = concept.get("target_page") if concept.get("action") == "merge" else None

            lock_key = target_page or page_name
            lock = get_page_lock(lock_key)

            with lock:
                # Regenerate pages inside the lock to serialize conflicting writes
                pages = generate_pages(config, [concept], chapter_text, filename)
                for p, _ in pages:
                    slug = p.stem
                    if slug not in created_pages:
                        created_pages.append(slug)

        return ChapterResult(
            chapter_id=chapter.id,
            status="success",
            concepts=concepts,
            pages_created=created_pages,
        )

    except Exception as e:
        return ChapterResult(
            chapter_id=chapter.id,
            status="failed",
            error=str(e),
        )


def _dedup_new_pages(config: Config, new_page_slugs: list[str]) -> None:
    """Check newly created pages for redundancy and merge overlapping ones."""
    if len(new_page_slugs) < 2:
        return

    # Read new pages (content and briefs)
    pages_content: dict[str, str] = {}
    for slug in new_page_slugs:
        path = config.wiki_dir / f"{slug}.md"
        if path.exists():
            pages_content[slug] = path.read_text(encoding="utf-8")

    if len(pages_content) < 2:
        return

    pages_text = "\n\n---\n\n".join(
        f"## [[{name}]]\n{content[:1500]}" for name, content in pages_content.items()
    )

    with get_tracker().phase("execute.dedup"):
        result = call_claude_json(
            config,
            SYSTEM_DEDUP,
            PROMPT_DEDUP.format(pages_text=pages_text),
        )

    merges = result.get("merges", [])
    for m in merges:
        source = m.get("source", "")
        target = m.get("target", "")
        reason = m.get("reason", "")
        if not source or not target or source == target:
            continue

        source_path = config.wiki_dir / f"{source}.md"
        target_path = config.wiki_dir / f"{target}.md"
        if not source_path.exists() or not target_path.exists():
            continue

        print(f"  Merging [[{source}]] → [[{target}]]: {reason}")

        # Append source content to target, then remove source
        source_content = source_path.read_text(encoding="utf-8")
        target_content = target_path.read_text(encoding="utf-8")

        merged = target_content.rstrip() + "\n\n" + source_content
        # Remove duplicate frontmatter from appended source
        merged = merged.replace(source_content, _strip_frontmatter(source_content))
        target_path.write_text(merged, encoding="utf-8")

        source_path.unlink()
        new_page_slugs.remove(source)
        print(f"  Removed: {source_path}")


def _strip_frontmatter(content: str) -> str:
    """Remove YAML frontmatter from page content."""
    return re.sub(r"^---\s*\n.*?\n---\s*\n", "", content, count=1, flags=re.DOTALL)


def merge_all_results(
    config: Config,
    results: list[ChapterResult],
    plan: Plan,
) -> None:
    """Run final merge phases AFTER all chapters complete: dedup, cross-references, index, log."""
    # Collect all concepts and page paths from successful chapters
    all_concepts: list[dict] = []
    all_page_paths: list[Path] = []
    new_page_slugs: list[str] = []

    for r in results:
        if r.status == "success":
            all_concepts.extend(r.concepts)
            for page_slug in r.pages_created:
                page_path = config.wiki_dir / f"{page_slug}.md"
                if page_path.exists():
                    all_page_paths.append(page_path)
                    new_page_slugs.append(page_slug)

    # Phase 3.5: Dedup newly created pages (before cross-references)
    if len(new_page_slugs) >= 2:
        print("\n[Final] Checking new pages for redundancy...")
        _dedup_new_pages(config, new_page_slugs)
        # Refresh page paths after potential merges
        all_page_paths = [
            config.wiki_dir / f"{slug}.md"
            for slug in new_page_slugs
            if (config.wiki_dir / f"{slug}.md").exists()
        ]

    # Phase 4: Cross-references (once across all pages)
    print("\n[Final] Updating cross-references...")
    run_cross_references(config)

    # Phase 5: Index + log
    print("[Final] Updating index and log...")
    update_index_and_log(config, all_page_paths, all_concepts, plan.source_file)

    # Print summary
    success_count = sum(1 for r in results if r.status == "success")
    failed_count = sum(1 for r in results if r.status == "failed")
    total_pages = len(all_page_paths)

    print(f"\n{'='*50}")
    print(f"Execution complete: {success_count}/{len(results)} chapters succeeded"
          + (f", {failed_count} failed" if failed_count else ""))
    print(f"Pages created/updated: {total_pages}")
    print(f"Plan saved: reports/plan-*-{Path(plan.source_file).stem}.json")
