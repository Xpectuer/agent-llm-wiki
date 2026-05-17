---
doc_type: module
module_name: tracker
module_path: src/wiki_cli/tracker.py
generated_by: mci-phase-2
---

# Tracker Token 用量追踪模块

> **Purpose**: 记录每次 LLM API 调用的 token 用量，按阶段聚合，生成 Markdown 表格或 HTML 报告，并估算费用。
> **Path**: `src/wiki_cli/tracker.py`

---

<!-- BEGIN:interface -->
## 1. Interface

### Exported Functions/Classes

- `TokenTracker` (class) → 核心追踪器，线程安全
  - `record(usage, model)` → 记录一次 API 调用的 token 用量
  - `phase(name)` → Context manager，设置当前阶段名
  - `reset()` → 清空所有记录
  - `usages` (property) → 返回用量列表副本
  - `report()` → `str`: 生成 Markdown 格式的用量报告
  - `html_report()` → `str`: 生成 HTML 格式的用量报告（含 CSS 样式和可视化卡片）
  - `save_report(path)` → `Path`: 根据文件扩展名（.html/.md）保存报告
- `get_tracker()` → `TokenTracker`: 全局单例获取器
- `effective_input_tokens(usage)` → `int`: 处理非标准 API 的 input token 计算（兼容 input_tokens=0 的情况）
- `TokenUsage` (data class) → `phase, model, input_tokens, output_tokens, cache_creation_input_tokens, cache_read_input_tokens, timestamp`
- `MODEL_PRICING` (constant) → `dict[str, tuple[float, float]]`: 各模型的 (input_price, output_price) 每百万 token

### 计费模型

| 模型 | Input ($/1M) | Output ($/1M) |
|------|-------------|---------------|
| claude-sonnet-4-6 | $3.00 | $15.00 |
| claude-sonnet-4-5 | $3.00 | $15.00 |
| claude-opus-4-7 | $15.00 | $75.00 |
| claude-opus-4-6 | $15.00 | $75.00 |
| claude-haiku-4-5 | $1.00 | $5.00 |
| 默认（未知模型） | $3.00 | $15.00 |
<!-- END:interface -->

---

<!-- BEGIN:dependency_graph -->
## 2. Dependency Graph

- **No internal dependencies** — 纯基础设施模块
- **External**: `threading`, `collections.defaultdict`, `dataclasses`, `time`, `pathlib`, `contextlib`
- **Is depended on by**: llm（每次 API 调用后 record）, convert, planner, executor, query, llint（通过 get_tracker()）
<!-- END:dependency_graph -->

---

<!-- BEGIN:state_management -->
## 3. State Management

**Type**: Stateful (global singleton)

- `_tracker` 模块级全局变量，通过 `get_tracker()` 懒初始化
- TokenTracker 内部:
  - `_usages: list[TokenUsage]` — 所有记录的列表，受 `_lock` 保护
  - `_current_phase: str` — 当前阶段名，由 `phase()` context manager 管理
- 生命周期：进程级别（模块导入时初始化，`reset()` 可清空）
- 线程安全：所有写入操作通过 `threading.Lock` 保护
<!-- END:state_management -->

---

<!-- BEGIN:edge_cases -->
## 4. Edge Cases

### Hardcoded Values

- **默认定价**: `DEFAULT_PRICING = (3.0, 15.0)` — 未知模型回退到 Sonnet 价格
- **费用单位**: 每百万 token

### Error Handling

- **非标准 API cache 膨胀**: `effective_input_tokens()` 将 cache_create 和 cache_read 上限设为总 input tokens，防止非标准 API 报告不合理的 cache 数值
- **input_tokens=0**: 回退到 `cache_create + cache_read` 作为有效 input tokens

### Special Cases

- **HTML 报告**: 包含 CSS 样式、响应式网格卡片、进度条可视化（input/output 比例、cache hit rate）
- **Markdown 报告**: 使用 Unicode 框线字符（`┌─┬─┐`）绘制表格
- **报告去重**: `save_report()` 覆盖同名文件，不追加
- **空报告**: `report()` 在无记录时返回 `"No token usage recorded."`
<!-- END:edge_cases -->

---

<!-- BEGIN:usage_example -->
## 5. Usage Example

```python
from wiki_cli.tracker import get_tracker

tracker = get_tracker()

# 设置阶段并记录用量
with tracker.phase("convert.extract"):
    # API 调用自动 record（在 llm.py 内部）
    pass

with tracker.phase("convert.generate"):
    pass

# 查看报告
print(tracker.report())
# === Token Usage Report ===
# Phase-wise Breakdown:
# ┌─ ... ─┐
# │ convert.extract  │   1 │  5,230 │  1,024 │  ...
# │ convert.generate │   2 │ 12,400 │  3,500 │  ...
# │ TOTAL            │   3 │ 17,630 │  4,524 │ $0.12

# 保存 HTML 报告（含可视化）
tracker.save_report("reports/token-usage.html")

# 重置（新命令开始前）
tracker.reset()
```
<!-- END:usage_example -->
