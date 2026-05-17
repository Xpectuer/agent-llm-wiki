---
doc_type: module
module_name: executor
module_path: src/wiki_cli/executor.py
generated_by: mci-phase-2
---

# Executor 并行执行引擎模块

> **Purpose**: 基于 DAG 拓扑层级的并行章节处理引擎，使用 ThreadPoolExecutor 在同级内并行、跨级串行，包含新页面去重和最终合并管线。
> **Path**: `src/wiki_cli/executor.py`

---

<!-- BEGIN:interface -->
## 1. Interface

### Exported Functions/Classes

- `execute_plan(config, plan, full_text, max_workers=4)` → `list[ChapterResult]`: 主入口——按 DAG 拓扑层级执行所有章节，同层并行、跨层串行
- `merge_all_results(config, results, plan)` → `None`: 所有章节完成后的最终合并：去重新页面 → 交叉引用刷新 → 索引日志更新
- `_process_chapter(config, chapter, chapter_text, get_page_lock)` → `ChapterResult`: 单个章节的处理函数（线程安全，通过 per-page 锁保护合并写入）
- `_dedup_new_pages(config, new_page_slugs)` → `None`: LLM 检查新页面之间的冗余，合并重叠页面
- `_strip_frontmatter(content)` → `str`: 去除页面 YAML frontmatter

### 执行流程

```
execute_plan()
  ├── split_chapters()           # 拆分全文
  ├── _topological_levels()      # 计算拓扑层级
  ├── for each DAG level:
  │   └── ThreadPoolExecutor     # 并行处理同层章节
  │       └── _process_chapter() # 概念提取 + 页面生成（带锁）
  └── merge_all_results()
      ├── _dedup_new_pages()     # LLM 去重
      ├── run_cross_references() # 刷新交叉引用
      └── update_index_and_log() # 更新索引
```
<!-- END:interface -->

---

<!-- BEGIN:dependency_graph -->
## 2. Dependency Graph

- **Imports from `.config`** → Config
- **Imports from `.convert`** → extract_concepts(), generate_pages(), run_cross_references(), update_index_and_log()
- **Imports from `.llm`** → MultiSpinner, _spinner_label, call_claude_json()
- **Imports from `.models`** → Chapter, ChapterResult, Plan
- **Imports from `.planner`** → _topological_levels(), split_chapters()
- **Imports from `.tracker`** → get_tracker()
- **External**: `concurrent.futures` (ThreadPoolExecutor, as_completed), `threading`, `re`, `pathlib`
- **Is depended on by**: cli（convert 命令的大文档路径）
<!-- END:dependency_graph -->

---

<!-- BEGIN:state_management -->
## 3. State Management

**Type**: Stateful (thread-safe, execution-scoped)

- **page_locks**: `dict[str, threading.Lock]` — per-page 锁字典，由 `page_locks_lock` 保护。用于防止多个线程同时写同一个目标页面（merge 操作）
- **all_results**: `list[ChapterResult]` — 跨层级累积的结果列表
- **MultiSpinner**: 通过 context manager 管理，同级并行执行时显示多槽位 spinner
- **ContextVar**: `_spinner_label` 在每个 worker 线程中设置为其 chapter ID

状态生命周期限于单次 `execute_plan()` 调用。
<!-- END:state_management -->

---

<!-- BEGIN:edge_cases -->
## 4. Edge Cases

### Hardcoded Values

- **默认 max_workers**: `4`（来自 Config，可被 `WIKI_MAX_WORKERS` 或 `--workers` 覆盖）
- **去重检查最少页面数**: `2`（少于 2 个新页面时跳过去重）

### Error Handling

- **章节处理异常**: 单个章节失败时捕获异常，生成 `ChapterResult(status="failed", error=str(e))`，不阻塞其他章节
- **空章节**: 概念提取返回空列表时，该章节标记为 success 但无创建页面
- **缺失页面路径**: `merge_all_results()` 中通过 `page_path.exists()` 过滤已不存在的页面（可能被去重移除）

### Special Cases

- **合并锁**: 写入 merge 目标页面前获取 per-page 锁，防止多个 worker 同时写入同一页面
- **去重合并**: 源页面内容去掉 frontmatter 后追加到目标页面。正则使用 `count=1` 确保只移除第一个 frontmatter
- **ThreadPoolExecutor 大小**: `min(max_workers, len(level))` —— 不创建超过当前层章节数的线程
- **失败汇总**: 最终打印成功/失败章节数统计
<!-- END:edge_cases -->

---

<!-- BEGIN:usage_example -->
## 5. Usage Example

```python
from wiki_cli.executor import execute_plan, merge_all_results
from wiki_cli.planner import plan_document
from wiki_cli.config import load_config

config = load_config()

# 大文档完整流程
text = Path("raw/big-book.md").read_text()

# 规划
plan = plan_document(config, text, "big-book.md")

# 执行（8 workers 并行）
results = execute_plan(config, plan, text, max_workers=8)
# → 按 DAG 层级顺序打印：
#   Level 1: ch-01 (Introduction) [no deps] ← 1 parallel
#     ✓ ch-01: success — pages: gradient-descent, loss-functions
#   Level 2: ch-02, ch-03 (Optimizers, Regularization) ← 2 parallel
#     ✓ ch-02: success — pages: sgd, adam
#     ✓ ch-03: success — pages: dropout, l2-regularization

# 最终合并（去重 + 交叉引用 + 索引）
merge_all_results(config, results, plan)
# → [Final] Checking new pages for redundancy...
# → [Final] Updating cross-references...
# → [Final] Updating index and log...
# → Execution complete: 3/3 chapters succeeded
# → Pages created/updated: 4
```
<!-- END:usage_example -->
