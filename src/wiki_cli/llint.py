"""Wiki structure health check — static rules + optional LLM enhancement."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from .config import Config
from .llm import call_claude_json
from .tracker import get_tracker

REQUIRED_FILES = [
    "wiki/index.md",
    "wiki/log.md",
    "reports/queries.md",
    "reports/lint-report.md",
    "reports/schema-note.md",
]


@dataclass
class LintResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    passes: list[str] = field(default_factory=list)

    def pass_(self, msg: str) -> None:
        self.passes.append(msg)

    def fail(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def format_report(self) -> str:
        lines = [
            "=== LLM Wiki Lint Report ===",
            f"Date: {date.today().isoformat()}",
            "",
            "--- Missing Required Pages ---",
        ]
        for p in self.passes:
            lines.append(f"[PASS] {p}")
        for e in self.errors:
            lines.append(f"[FAIL] {e}")
        for w in self.warnings:
            lines.append(f"[WARN] {w}")
        lines.append("")
        lines.append("--- Summary ---")
        lines.append(
            f"Errors: {len(self.errors)}, Warnings: {len(self.warnings)}, Passes: {len(self.passes)}"
        )
        return "\n".join(lines)


# --- Static checks ---


def check_required_files(config: Config, result: LintResult) -> None:
    for f in REQUIRED_FILES:
        if Path(f).exists():
            result.pass_(f"{f} exists")
        else:
            result.fail(f"{f} missing")


def check_broken_links(config: Config, result: LintResult) -> None:
    if not config.wiki_dir.exists():
        result.warn("wiki/ directory does not exist")
        return

    found_broken = False
    for md_file in config.wiki_dir.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        for match in re.finditer(r"\[\[([^\]]+)\]\]", content):
            target = match.group(1)
            target_path = config.wiki_dir / f"{target}.md"
            if not target_path.exists():
                result.fail(f"{md_file.name}: [[{target}]] -> {target_path} not found")
                found_broken = True

    if not found_broken:
        result.pass_("No broken internal links")


def check_orphan_pages(config: Config, result: LintResult) -> None:
    if not config.wiki_dir.exists():
        return

    # Collect all referenced page names
    referenced: set[str] = set()
    for md_file in config.wiki_dir.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        for match in re.finditer(r"\[\[([^\]]+)\]\]", content):
            referenced.add(match.group(1))

    found_orphan = False
    for md_file in config.wiki_dir.glob("*.md"):
        if md_file.stem in ("index", "log"):
            continue
        if md_file.stem not in referenced:
            result.warn(f"{md_file} has no inbound links (orphan)")
            found_orphan = True

    if not found_orphan:
        result.pass_("No orphan pages")


def check_xref_density(config: Config, result: LintResult) -> None:
    if not config.wiki_dir.exists():
        return

    total_links = 0
    total_pages = 0
    for md_file in config.wiki_dir.glob("*.md"):
        if md_file.stem in ("index", "log"):
            continue
        content = md_file.read_text(encoding="utf-8")
        link_count = len(re.findall(r"\[\[([^\]]+)\]\]", content))
        total_links += link_count
        total_pages += 1
        if link_count < 2:
            result.warn(f"{md_file} has only {link_count} internal link(s) (low connectivity)")

    if total_pages > 0:
        avg = total_links / total_pages
        result.passes.append(
            f"Average links per page: {avg:.1f} ({total_links} links across {total_pages} pages)"
        )
    else:
        result.passes.append("No content pages to analyze (only index.md and log.md found)")


def check_contradictions(config: Config, result: LintResult) -> None:
    if not config.wiki_dir.exists():
        return

    found = False
    for md_file in config.wiki_dir.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        for i, line in enumerate(content.splitlines(), 1):
            if "<!-- CONTRADICTION" in line or "**[CONFLICT]**" in line:
                result.fail(f"{md_file.name} line {i}: {line.strip()}")
                found = True

    if not found:
        result.pass_("No contradictions flagged")


# --- LLM enhancement ---

SYSTEM_LINT_LLM = """你是一个知识库审核员。检查以下 wiki 页面是否存在以下问题：
1. 页面内容矛盾（不同页面之间的说法冲突）
2. 信息重复（多页面重复叙述同一内容）
3. 缺失但应存在的概念（基于已有内容推断）
4. 过时或证据不足的结论

输出 JSON 格式。"""

PROMPT_LINT_LLM = """检查以下 wiki 页面的内容质量。

**所有 wiki 页面**:
{all_pages}

请检查并输出：
{{
  "contradictions": ["描述矛盾1", "描述矛盾2"],
  "duplicates": ["描述重复1"],
  "missing_concepts": ["应存在但缺失的概念"],
  "weak_claims": ["证据不足的结论"]
}}

如果没有发现问题，对应字段输出空数组。"""


def run_llm_lint(config: Config, result: LintResult) -> None:
    """Run LLM-enhanced lint checks."""
    all_pages = _read_all_wiki_pages(config)
    if not all_pages:
        return

    pages_text = "\n\n---\n\n".join(
        f"## {name}\n{content[:2000]}" for name, content in all_pages.items()
    )

    with get_tracker().phase("lint"):
        llm_result = call_claude_json(
            config,
            SYSTEM_LINT_LLM,
            PROMPT_LINT_LLM.format(all_pages=pages_text),
        )

        result.passes.append("--- LLM Content Analysis ---")
        for item in llm_result.get("contradictions", []):  # type: ignore[union-attr]
            result.fail(f"[LLM] Contradiction: {item}")
        for item in llm_result.get("duplicates", []):  # type: ignore[union-attr]
            result.warn(f"[LLM] Duplicate: {item}")
        for item in llm_result.get("missing_concepts", []):  # type: ignore[union-attr]
            result.warn(f"[LLM] Missing concept: {item}")
        for item in llm_result.get("weak_claims", []):  # type: ignore[union-attr]
            result.warn(f"[LLM] Weak claim: {item}")

        if not any(llm_result.values()):  # type: ignore[union-attr]
            result.pass_("[LLM] No content issues found")


# --- Main entry ---


def run_lint(config: Config, use_llm: bool = False, strict: bool = False) -> LintResult:
    """Run all lint checks. Returns LintResult."""
    result = LintResult()

    # Static checks
    check_required_files(config, result)
    check_broken_links(config, result)
    check_orphan_pages(config, result)
    check_xref_density(config, result)
    check_contradictions(config, result)

    # LLM-enhanced checks
    if use_llm:
        print("[LLM] Running content analysis...", file=__import__("sys").stderr)
        run_llm_lint(config, result)

    # Write report
    report = result.format_report()
    print(report)

    report_path = config.reports_dir / "lint-report.md"
    if report_path.exists():
        today = date.today().isoformat()
        round_num = _count_rounds(report_path) + 1
        entry = (
            f"\n## Round {round_num} -- [{today}]\n\n"
            f"**Findings**:\n{report}\n\n"
            f"**Actions taken**: (pending review)\n"
        )
        with open(report_path, "a", encoding="utf-8") as f:
            f.write(entry)

    # Append to log
    log_path = config.wiki_dir / "log.md"
    if log_path.exists():
        today = date.today().isoformat()
        entry = f"\n## [{today}] lint | Round {_count_rounds(report_path)}\n- Errors: {len(result.errors)}, Warnings: {len(result.warnings)}\n"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(entry)

    if strict and result.errors:
        raise SystemExit(1)

    return result


# --- Helpers ---


def _read_all_wiki_pages(config: Config) -> dict[str, str]:
    pages: dict[str, str] = {}
    if not config.wiki_dir.exists():
        return pages
    for p in config.wiki_dir.glob("*.md"):
        if p.stem not in ("index", "log"):
            pages[p.stem] = p.read_text(encoding="utf-8")
    return pages


def _count_rounds(report_path: Path) -> int:
    if not report_path.exists():
        return 0
    content = report_path.read_text(encoding="utf-8")
    return len(re.findall(r"## Round \d+", content))
