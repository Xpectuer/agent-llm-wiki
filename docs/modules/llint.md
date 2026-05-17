---
doc_type: module
module_name: llint
module_path: src/wiki_cli/llint.py
generated_by: mci-phase-2
---

# Llint 结构健康检查模块

> **Purpose**: 对 wiki 结构进行静态检查（断链、孤立页面、交叉引用密度、矛盾标记）和可选的 LLM 增强内容分析。
> **Path**: `src/wiki_cli/llint.py`

---

<!-- BEGIN:interface -->
## 1. Interface

### Exported Functions/Classes

- `run_lint(config, use_llm=False, strict=False)` → `LintResult`: 主入口——运行所有检查，输出报告
- `LintResult` (data class) → `errors: list[str]`, `warnings: list[str]`, `passes: list[str]` + `format_report()` 方法
- `REQUIRED_FILES` (constant) → 必须存在的文件列表：`wiki/index.md`, `wiki/log.md`, `reports/queries.md`, `reports/lint-report.md`, `reports/schema-note.md`

### 静态检查函数

- `check_required_files(config, result)` → 检查必要文件是否存在
- `check_broken_links(config, result)` → 检查所有 `[[wikilink]]` 是否指向存在的页面
- `check_orphan_pages(config, result)` → 检查未被任何页面引用的孤立页面
- `check_xref_density(config, result)` → 统计平均交叉引用密度，标记少于 2 个链接的页面
- `check_contradictions(config, result)` → 检查页面中是否包含 `<!-- CONTRADICTION -->` 或 `**[CONFLICT]**` 标记
- `run_llm_lint(config, result)` → LLM 增强的内容分析（矛盾/重复/缺失概念/弱结论）
<!-- END:interface -->

---

<!-- BEGIN:dependency_graph -->
## 2. Dependency Graph

- **Imports from `.config`** → Config
- **Imports from `.llm`** → call_claude_json()（LLM 增强分析）
- **Imports from `.tracker`** → get_tracker()（token 用量追踪）
- **External**: `re`, `dataclasses`, `datetime`, `pathlib`
- **Is depended on by**: cli（lint 命令）
<!-- END:dependency_graph -->

---

<!-- BEGIN:state_management -->
## 3. State Management

**Type**: Stateless

所有检查函数接收 `LintResult` 引用来追加发现。LintResult 对象生命周期限于单次 `run_lint()` 调用。报告持久化到 `reports/lint-report.md`（多轮追加模式，按 `## Round N` 组织）。
<!-- END:state_management -->

---

<!-- BEGIN:edge_cases -->
## 4. Edge Cases

### Hardcoded Values

- **低交叉引用阈值**: `< 2` 个内部链接（触发 warning）
- **LLM 内容分析截断**: `2000` 字符/页

### Error Handling

- **wiki/ 目录不存在**: `check_broken_links()` 和 `check_orphan_pages()` 提前返回 warning
- **strict 模式**: `result.errors` 非空时 `raise SystemExit(1)`
- **LLM 分析全空**: 所有类别为空数组时输出 `[LLM] No content issues found`

### Special Cases

- **多轮 lint 报告**: 追加模式，通过 `_count_rounds()` 计算已有轮次，新轮次递增编号
- **排除文件**: index.md 和 log.md 不检查孤立页面和交叉引用密度
- **日志同步**: 每次 lint 运行自动追加到 `wiki/log.md`
<!-- END:edge_cases -->

---

<!-- BEGIN:usage_example -->
## 5. Usage Example

```python
from wiki_cli.llint import run_lint, LintResult
from wiki_cli.config import load_config

config = load_config()

# 仅静态检查（不调用 LLM）
result = run_lint(config, use_llm=False)
print(result.format_report())
# === LLM Wiki Lint Report ===
# [PASS] wiki/index.md exists
# [FAIL] gradient-descent.md: [[adam]] -> wiki/adam.md not found
# [WARN] vggnet.md has only 1 internal link(s) (low connectivity)
# Errors: 1, Warnings: 1, Passes: 15

# 带 LLM 增强（消耗 API tokens）
result = run_lint(config, use_llm=True)
# [LLM] Contradiction: gradient-descent.md 和 optimization.md 对学习率的描述冲突

# strict 模式（有错误时 exit 1）
result = run_lint(config, strict=True)
```
<!-- END:usage_example -->
