---
doc_type: module
module_name: config
module_path: src/wiki_cli/config.py
generated_by: mci-phase-2
---

# Config 配置模块

> **Purpose**: 从环境变量加载配置，生成不可变的 Config 数据类，驱动所有模块的路径和参数行为。
> **Path**: `src/wiki_cli/config.py`

---

<!-- BEGIN:interface -->
## 1. Interface

### Exported Functions/Classes

- `Config` (data class) → 包含所有运行时配置字段：`api_key`, `model`, `base_url`, `wiki_dir`, `raw_dir`, `reports_dir`, `templates_dir`, `project_root`, `max_workers`, `large_threshold`, `quiet`
- `load_config(project_root)` → 从环境变量读取并返回 Config 实例；未设置 `ANTHROPIC_API_KEY` 时抛出 SystemExit
- `DEFAULT_MODEL = "claude-sonnet-4-6"` → 默认 LLM 模型
- `DEFAULT_WIKI_DIR = "wiki"` 等 → 各目录的默认名称常量

### 环境变量 → 配置映射

| 环境变量 | Config 字段 | 默认值 |
|----------|-------------|--------|
| `ANTHROPIC_API_KEY` | `api_key` | 必填，否则退出 |
| `WIKI_MODEL` | `model` | `claude-sonnet-4-6` |
| `ANTHROPIC_BASE_URL` | `base_url` | `None` |
| `WIKI_DIR` | `wiki_dir` | `wiki` |
| `RAW_DIR` | `raw_dir` | `raw` |
| `REPORTS_DIR` | `reports_dir` | `reports` |
| `TEMPLATES_DIR` | `templates_dir` | `templates` |
| `WIKI_MAX_WORKERS` | `max_workers` | `4` |
| `WIKI_LARGE_THRESHOLD` | `large_threshold` | `30000` |
<!-- END:interface -->

---

<!-- BEGIN:dependency_graph -->
## 2. Dependency Graph

- **No internal dependencies** — 不导入任何项目内部模块
- **External**: `os`, `dataclasses`, `pathlib.Path`
- **Is depended on by**: 几乎所有其他模块（cli, llm, convert, planner, executor, query, llint, tools, tracker）
<!-- END:dependency_graph -->

---

<!-- BEGIN:state_management -->
## 3. State Management

**Type**: Stateless

`load_config()` 是纯函数：每次调用都从当前环境变量读取，不缓存，不修改环境。Config 实例创建后不可变（字段虽然技术上可修改，但惯例上只读）。`quiet` 字段是唯一的例外——由 CLI 层在加载后设置，而非来自环境变量。
<!-- END:state_management -->

---

<!-- BEGIN:edge_cases -->
## 4. Edge Cases

### Hardcoded Values

- **默认模型**: `claude-sonnet-4-6`
- **默认并行度**: `4` workers
- **大文档阈值**: `30,000` 字符
- **默认目录名**: `wiki`, `raw`, `reports`, `templates`

### Error Handling

- **缺失 API Key**: `ANTHROPIC_API_KEY` 未设置时，`load_config()` 直接 `SystemExit`，打印设置提示
- **类型转换**: `max_workers` 和 `large_threshold` 通过 `int()` 转换环境变量，非法值会抛出 `ValueError`

### Special Cases

- **base_url**: 为 `None` 时，Anthropic SDK 使用默认端点；为空字符串时也转为 `None`
- **路径解析**: 所有目录路径通过 `root / name` 拼接后 `resolve()`，均为绝对路径
<!-- END:edge_cases -->

---

<!-- BEGIN:usage_example -->
## 5. Usage Example

```python
from wiki_cli.config import Config, load_config

# 标准加载（从环境变量）
config = load_config()
print(config.model)          # "claude-sonnet-4-6"
print(config.max_workers)    # 4
print(config.wiki_dir)       # /absolute/path/to/project/wiki

# 指定项目根
config = load_config(project_root=Path("/other/project"))

# CLI 层覆盖模型（通过临时环境变量）
import os
os.environ["WIKI_MODEL"] = "claude-opus-4-7"
config = load_config()

# 创建自定义 Config（如 init 命令不需要 API key）
config = Config(
    api_key="",
    model="",
    base_url=None,
    wiki_dir=root / "wiki",
    raw_dir=root / "raw",
    reports_dir=root / "reports",
    templates_dir=root / "templates",
    project_root=root,
)
```
<!-- END:usage_example -->
