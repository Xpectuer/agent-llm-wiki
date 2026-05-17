---
doc_type: module
module_name: planner
module_path: src/wiki_cli/planner.py
generated_by: mci-phase-2
---

# Planner 文档规划模块

> **Purpose**: 分析大文档的章节目录结构，通过 LLM 生成包含依赖关系的章节计划（Plan），构建 DAG 并计算拓扑执行层级。
> **Path**: `src/wiki_cli/planner.py`

---

<!-- BEGIN:interface -->
## 1. Interface

### Exported Functions/Classes

- `plan_document(config, text, filename, text_limit=12000)` → `Plan`: LLM 分析文档结构，返回包含 Chapter 列表和 DAG 元数据的 Plan
- `save_plan(plan, config)` → `Path`: 将 Plan 序列化为 JSON 保存到 `reports/plan-{date}-{stem}.json`
- `load_plan(plan_path)` → `Plan`: 从 JSON 文件反序列化 Plan
- `split_chapters(full_text, chapters)` → `dict[str, str]`: 按章节的 heading_pattern 拆分全文；pattern 无匹配时回退到比例拆分
- `describe_plan(plan)` → `str`: 人类可读的计划摘要（含 DAG 层级结构）
- `_validate_dag(chapters)` → `None`: 验证依赖引用有效性和无环性（异常检测）
- `_topological_levels(chapters)` → `list[list[str]]`: Kahn 算法计算拓扑层级，每层内的章节可并行执行

### 数据模型（来自 models.py）

- `Chapter(id, title, order, heading_pattern, depends_on, summary)`
- `Plan(source_file, total_chars, chapters, metadata)`
<!-- END:interface -->

---

<!-- BEGIN:dependency_graph -->
## 2. Dependency Graph

- **Imports from `.config`** → Config（API key、model 等）
- **Imports from `.llm`** → call_claude_json()（LLM 结构化输出）
- **Imports from `.models`** → Chapter, Plan 数据类
- **Imports from `.tracker`** → get_tracker()（token 用量追踪）
- **External**: `json`, `re`, `collections`（defaultdict, deque）, `datetime`, `pathlib`
- **Is depended on by**: cli（命令层调用 plan_document, load_plan）, executor（调用 _topological_levels, split_chapters）
<!-- END:dependency_graph -->

---

<!-- BEGIN:state_management -->
## 3. State Management

**Type**: Stateless

所有函数接收输入参数并返回结果，不维护全局状态。Plan 是纯数据对象。`chapter_texts` 字典（章节 ID → 文本内容）由调用者管理生命周期。
<!-- END:state_management -->

---

<!-- BEGIN:edge_cases -->
## 4. Edge Cases

### Hardcoded Values

- **规划阶段文本限制**: `12,000` 字符（传入 LLM 分析结构的文档头部长度）
- **Plan 文件名格式**: `plan-{date}-{stem}.json`

### Error Handling

- **未知依赖**: `_validate_dag()` 检测到 chapter 依赖不存在的 chapter ID 时抛出 `ValueError`
- **循环依赖**: DFS 三色标记法检测 DAG 环，发现时抛出 `ValueError`
- **剩余节点**: Kahn 算法结束后 `remaining != 0` 说明存在未解决的依赖环，抛出 `ValueError`
- **LLM 返回空章节**: 回退到单章节 Plan（整份文档作为一个 chapter，`metadata={"fallback": True}`）
- **正则错误**: `split_chapters()` 中 heading_pattern 非法时捕获 `re.error`，回退到比例拆分

### Special Cases

- **单章节文档**: 不进行比例拆分，全文分配给唯一 chapter
- **未知位置章节**: `position = -1` 时使用比例拆分（按 chapter 序号均分全文）
- **Plan 复用**: `load_plan()` 从 JSON 恢复 Plan，跳过 LLM 规划阶段，支持断点续传
<!-- END:edge_cases -->

---

<!-- BEGIN:usage_example -->
## 5. Usage Example

```python
from wiki_cli.planner import plan_document, save_plan, split_chapters
from wiki_cli.config import load_config

config = load_config()

# 分析大文档结构
text = Path("raw/big-book.md").read_text()
plan = plan_document(config, text, "big-book.md")

# 查看计划
print(f"Found {len(plan.chapters)} chapters in {len(_topological_levels(plan.chapters))} DAG levels")
# 保存计划
plan_path = save_plan(plan, config)
# → reports/plan-2026-05-17-big-book.json

# 拆分章节
from wiki_cli.planner import _topological_levels
chapter_texts = split_chapters(text, plan.chapters)
levels = _topological_levels(plan.chapters)

# 按拓扑层级执行
for level_num, level in enumerate(levels, 1):
    print(f"Level {level_num}: {level}")  # 同级可并行
    for ch_id in level:
        ch_text = chapter_texts[ch_id]
        # process chapter...
```
<!-- END:usage_example -->
