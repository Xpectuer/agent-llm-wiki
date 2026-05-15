"""Shared dataclasses for plan-and-execute workflow."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Chapter:
    id: str
    title: str
    order: int
    heading_pattern: str
    depends_on: list[str] = field(default_factory=list)
    summary: str = ""


@dataclass
class Plan:
    source_file: str
    total_chars: int
    chapters: list[Chapter]
    metadata: dict = field(default_factory=dict)


@dataclass
class ChapterResult:
    chapter_id: str
    status: str  # "success" | "failed" | "skipped"
    concepts: list[dict] = field(default_factory=list)
    pages_created: list[str] = field(default_factory=list)
    error: str | None = None
