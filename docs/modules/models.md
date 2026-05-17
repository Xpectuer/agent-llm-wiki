---
doc_type: module
module_name: models
module_path: src/wiki_cli/models.py
generated_by: mci-phase-2
---

# Models 共享数据模型模块

> **Purpose**: 定义 plan-and-execute 工作流中的三个共享数据类（Chapter, Plan, ChapterResult）。
> **Path**: `src/wiki_cli/models.py`

---

<!-- BEGIN:interface -->
## 1. Interface

### Exported Classes

- `Chapter(id, title, order, heading_pattern, depends_on=[], summary="")` → 单个章节的元数据
  - `id`: str — 唯一标识符（如 `ch-01`）
  - `title`: str — 章节标题
  - `order`: int — 章节序号
  - `heading_pattern`: str — 用于定位章节边界的正则/关键词
  - `depends_on`: list[str] — 依赖的前置章节 ID 列表
  - `summary`: str — 一句话中文摘要（默认空）
- `Plan(source_file, total_chars, chapters, metadata={})` → 文档执行计划
  - `source_file`: str — 源文件名
  - `total_chars`: int — 文档总字符数
  - `chapters`: list[Chapter] — 章节列表
  - `metadata`: dict — 额外元数据（如 `{"model": "claude-sonnet-4-6"}`, `{"fallback": True}`）
- `ChapterResult(chapter_id, status, concepts=[], pages_created=[], error=None)` → 章节执行结果
  - `chapter_id`: str — 章节 ID
  - `status`: str — `"success"`, `"failed"`, 或 `"skipped"`
  - `concepts`: list[dict] — 提取的概念列表
  - `pages_created`: list[str] — 创建的页面 slug 列表
  - `error`: str | None — 失败时的错误信息
<!-- END:interface -->

---

<!-- BEGIN:dependency_graph -->
## 2. Dependency Graph

- **No internal dependencies** — 纯数据类模块
- **External**: `dataclasses`
- **Is depended on by**: planner（Chapter, Plan）, executor（ChapterResult, Plan）, cli（通过 planner/executor 间接使用）
<!-- END:dependency_graph -->

---

<!-- BEGIN:state_management -->
## 3. State Management

**Type**: Stateless

纯数据类，无行为逻辑。实例不可变性取决于调用者的使用方式（字段未使用 `frozen=True`）。这三个类仅用于在 planner → executor → cli 之间传递结构化数据。
<!-- END:state_management -->

---

<!-- BEGIN:edge_cases -->
## 4. Edge Cases

### Hardcoded Values

- **默认 depends_on**: `[]`（空列表，无依赖）
- **默认 summary**: `""`（空字符串）
- **默认 concepts**: `[]`
- **默认 pages_created**: `[]`
- **默认 error**: `None`
- **默认 metadata**: `{}`

### Special Cases

- **status 值域**: 约定为 `"success"`, `"failed"`, `"skipped"`，但不通过枚举强制（依赖调用者遵守约定）
- **fallback 标记**: `Plan.metadata` 中包含 `{"fallback": True}` 时表示 LLM 未能识别章节结构，使用了单章节回退方案
- **Chapter 排序**: Chapter 列表由 planner 按 `order` 字段排序，DAG 依赖可能使执行顺序与 order 不同
<!-- END:edge_cases -->

---

<!-- BEGIN:usage_example -->
## 5. Usage Example

```python
from wiki_cli.models import Chapter, Plan, ChapterResult

# 构建章节
ch1 = Chapter(
    id="ch-01",
    title="Introduction",
    order=1,
    heading_pattern=r"^# Introduction",
    depends_on=[],
    summary="深度学习的历史背景和基本概念",
)

ch2 = Chapter(
    id="ch-02",
    title="Optimization",
    order=2,
    heading_pattern=r"^# Optimization",
    depends_on=["ch-01"],
    summary="梯度下降及其变体",
)

# 创建计划
plan = Plan(
    source_file="deep-learning-book.md",
    total_chars=150000,
    chapters=[ch1, ch2],
    metadata={"model": "claude-sonnet-4-6"},
)

# 记录章节执行结果
result = ChapterResult(
    chapter_id="ch-01",
    status="success",
    concepts=[
        {"name": "gradient-descent", "action": "create", "summary": "..."},
    ],
    pages_created=["gradient-descent"],
)

failed_result = ChapterResult(
    chapter_id="ch-02",
    status="failed",
    error="LLM API timeout after 3 retries",
)
```
<!-- END:usage_example -->
