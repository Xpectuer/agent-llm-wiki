---
doc_type: module
module_name: cli
module_path: src/wiki_cli/cli.py
generated_by: mci-phase-2
---

# CLI 入口模块

> **Purpose**: Click 命令行入口，定义 4 个命令（init/convert/query/lint）及其参数，负责流程编排和配置加载。
> **Path**: `src/wiki_cli/cli.py`

---

<!-- BEGIN:interface -->
## 1. Interface

### Exported Functions/Classes

- `cli(ctx, project_root)` → Click group，所有命令的父入口，设置 `ctx.obj["root"]` 为项目根路径
- `init(ctx)` → `wiki init` 命令：创建目录结构、模板文件、CLAUDE.md
- `convert(ctx, target, title, model, large, dry_run, workers, plan_file, token_report, token_report_format, quiet)` → `wiki convert` 命令：单文件或目录的 ingest，自动检测大文档切换到 plan-and-execute
- `lint(ctx, strict, model, token_report, token_report_format, quiet)` → `wiki lint` 命令：静态 + 可选 LLM 增强检查
- `query(ctx, question, model, token_report, token_report_format, quiet)` → `wiki query` 命令：agentic 工具调用查询

### CLI 参数

- `--project-root` (全局): 项目根目录，默认 `.`
- `--model`: 覆盖 `WIKI_MODEL` 环境变量
- `--large` / `--no-large`: 强制开启/关闭 plan-and-execute 模式
- `--dry-run`: 仅规划不执行
- `--workers N`: 并行线程数
- `--plan-file`: 复用已有计划文件
- `--token-report` / `--token-report-format`: Token 用量报告
- `-q` / `--quiet`: 抑制 spinner 输出
<!-- END:interface -->

---

<!-- BEGIN:dependency_graph -->
## 2. Dependency Graph

- **Imports from `.config`** → Config 数据类和 load_config() 工厂函数
- **Imports from `.tracker`** → get_tracker() 用于 token 报告
- **Imports from `.convert`** (延迟导入) → convert_file() 和 run_convert()
- **Imports from `.planner`** (延迟导入) → plan_document(), save_plan(), load_plan()
- **Imports from `.executor`** (延迟导入) → execute_plan(), merge_all_results()
- **Imports from `.query`** (延迟导入) → run_query()
- **Imports from `.llint`** (延迟导入) → run_lint()
- **External**: `click` (CLI 框架), `pathlib.Path`, `datetime.date`
<!-- END:dependency_graph -->

---

<!-- BEGIN:state_management -->
## 3. State Management

**Type**: Stateless

模块本身无状态。通过 Click 的 `ctx.obj` 字典在命令间传递项目根路径（`ctx.obj["root"]`）。所有业务逻辑委托给下游模块。`_load_config_with_override()` 通过临时设置 `WIKI_MODEL` 环境变量实现模型覆盖，函数返回后不保留副作用。
<!-- END:state_management -->

---

<!-- BEGIN:edge_cases -->
## 4. Edge Cases

### Hardcoded Values

- **默认模型**: `claude-sonnet-4-6`（在 `config.py` 中定义，非本模块）
- **大文档阈值**: `30,000` 字符（来自 Config，可被 `WIKI_LARGE_THRESHOLD` 覆盖）

### Error Handling

- **目录模式**: 仅支持单文件 standard/plan-and-execute 切换；目录批量处理始终使用 standard 模式（每个文件独立处理）
- **空目录**: 如果目录中没有支持格式的文件，打印提示并退出
- **格式检测**: 仅处理 11 种支持的文件扩展名（`.md`, `.txt`, `.pdf`, `.docx`, `.html`, `.htm`, `.epub`, `.rtf`, `.png`, `.jpg`, `.jpeg`）

### Special Cases

- **大文档自动检测**: `large` 参数为 `None` 时，先提取文本检查长度是否超过 `config.large_threshold`
- **--plan-file 复用**: 仅在 `large=True` 时生效，跳过 LLM 规划阶段直接加载已有计划
- **init 命令**: 不需要 API key，使用 `_init_config()` 创建空配置；AGENTS.md 创建为 CLAUDE.md 的符号链接
<!-- END:edge_cases -->

---

<!-- BEGIN:usage_example -->
## 5. Usage Example

```python
# 标准单文件 ingest
wiki convert raw/document.pdf

# 大文档（自动检测或手动指定）
wiki convert --large raw/big-doc.md --workers 8

# 仅规划（dry-run）
wiki convert --dry-run raw/big-doc.md

# 复用已有计划执行
wiki convert --plan-file reports/plan-2026-05-17-big-doc.json raw/big-doc.md

# 目录批量处理
wiki convert raw/

# Agentic 查询
wiki query "what is transformer architecture?"

# 带 token 报告的查询
wiki query "explain gradient descent" --token-report --token-report-format html
```
<!-- END:usage_example -->
