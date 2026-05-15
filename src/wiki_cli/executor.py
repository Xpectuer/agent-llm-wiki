"""DAG-aware parallel chapter execution via ThreadPoolExecutor."""

from __future__ import annotations

import threading
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .config import Config
from .convert import extract_concepts, generate_pages, run_cross_references, update_index_and_log
from .models import Chapter, ChapterResult, Plan
from .planner import _topological_levels, split_chapters


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


def merge_all_results(
    config: Config,
    results: list[ChapterResult],
    plan: Plan,
) -> None:
    """Run final merge phases AFTER all chapters complete: cross-references, index, log."""
    # Collect all concepts and page paths from successful chapters
    all_concepts: list[dict] = []
    all_page_paths: list[Path] = []

    for r in results:
        if r.status == "success":
            all_concepts.extend(r.concepts)
            for page_slug in r.pages_created:
                page_path = config.wiki_dir / f"{page_slug}.md"
                if page_path.exists():
                    all_page_paths.append(page_path)

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
