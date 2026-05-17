---
doc_type: module
module_name: query
module_path: src/wiki_cli/query.py
generated_by: mci-phase-2
---

# Query 知识查询模块

> **Purpose**: Agentic 工具调用查询——LLM 使用 search_wiki / read_page / list_pages 工具搜索 wiki，合成回答并记录到报告。
> **Path**: `src/wiki_cli/query.py`

---

<!-- BEGIN:interface -->
## 1. Interface

### Exported Functions/Classes

- `run_query(config, question)` → `str`: 查询主入口——LLM 工具调用循环，返回回答字符串
- `SYSTEM_QUERY` (constant) → Agentic 查询的系统提示词
- `PROMPT_QUERY` (constant) → 查询的 user prompt 模板

### 查询流程

```
run_query()
  ├── call_claude_with_tools()  # LLM 使用 search/read/list 工具
  ├── 打印回答
  ├── _record_query()           # 记录到 reports/queries.md
  ├── _append_log()             # 追加到 wiki/log.md
  └── _check_new_page_suggestion()  # 检查是否需要创建新页面
```

### 内部函数

- `_record_query(config, question, answer)` → 追加到 `reports/queries.md`
- `_append_log(config, question)` → 追加到 `wiki/log.md`
- `_check_new_page_suggestion(config, answer)` → 检测 LLM 是否建议创建新页面，写入 instruction 文件
<!-- END:interface -->

---

<!-- BEGIN:dependency_graph -->
## 2. Dependency Graph

- **Imports from `.config`** → Config
- **Imports from `.llm`** → call_claude_with_tools()（agentic 工具调用循环）
- **Imports from `.tools`** → TOOLS, make_executor()（wiki 工具的 Anthropic 格式定义和执行器）
- **Imports from `.tracker`** → get_tracker()（token 用量追踪）
- **External**: `datetime`
- **Is depended on by**: cli（query 命令）
<!-- END:dependency_graph -->

---

<!-- BEGIN:state_management -->
## 3. State Management

**Type**: Stateless

查询本身无服务器状态。回答持久化到文件系统（`reports/queries.md` 和 `wiki/log.md`）。每次查询是独立的，不依赖之前的查询结果。
<!-- END:state_management -->

---

<!-- BEGIN:edge_cases -->
## 4. Edge Cases

### Hardcoded Values

- **日志截断**: `wiki/log.md` 中的查询记录截断到前 60 字符
- **最大工具轮次**: `8`（来自 `call_claude_with_tools` 默认值）

### Error Handling

- **空 wiki**: tools.py 中的 `search_wiki` 返回 `"(wiki 中没有页面)"`，LLM 据此回应
- **不完整回答**: LLM 被提示在信息不足时明确说明

### Special Cases

- **新页面建议检测**: 仅当 LLM 回答中"建议新页面"部分包含"无"时跳过；否则写入 `reports/instruction-{date}-query.md`
- **重复查询管理**: `reports/queries.md` 以追加模式记录，不会覆盖历史查询
<!-- END:edge_cases -->

---

<!-- BEGIN:usage_example -->
## 5. Usage Example

```python
from wiki_cli.query import run_query
from wiki_cli.config import load_config

config = load_config()

# Agentic 查询
answer = run_query(config, "什么是 transformer 架构？")
# LLM 会：
# 1. search_wiki("transformer")
# 2. read_page("transformer-architecture")
# 3. search_wiki("attention mechanism")
# 4. 合成回答

# 回答格式：
# **回答**: Transformer 是一种基于自注意力机制的...
#
# **引用**:
# - [[transformer-architecture]] — 核心架构说明
# - [[attention-mechanism]] — 注意力机制详解
#
# **建议新页面**: 无

print(answer)
# 同时自动记录到 reports/queries.md 和 wiki/log.md
```
<!-- END:usage_example -->
