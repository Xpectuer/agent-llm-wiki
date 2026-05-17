---
doc_type: module
module_name: convert
module_path: src/wiki_cli/convert.py
generated_by: mci-phase-2
---

# Convert 格式转换与 Ingest 管线模块

> **Purpose**: 将 11 种格式的原始材料转换为纯文本，再通过 5 阶段 LLM 管线生成/合并 wiki 页面，并刷新交叉引用。
> **Path**: `src/wiki_cli/convert.py`

---

<!-- BEGIN:interface -->
## 1. Interface

### Exported Functions/Classes

- `convert_file(path)` → `str`: 格式转换器，根据文件扩展名路由到 pdftotext / pandoc / tesseract / 直接读取
- `check_tool(ext)` → `str | None`: 检查指定扩展名的外部工具是否可用，不可用时返回安装提示
- `run_convert(config, target, title)` → `list[Path]`: 标准 5 阶段 ingest 管线入口
- `extract_concepts(config, text, filename, text_limit)` → `(list[dict], list[dict])`: Phase 2 — LLM agentic 概念提取（工具调用循环）
- `generate_pages(config, concepts, text, filename, text_limit)` → `list[(Path, dict)]`: Phase 3 — LLM 页面生成/合并
- `extract_briefs(config)` → `dict[str, str]`: 从所有 wiki 页面提取 frontmatter brief
- `build_relevance_graph(config, briefs)` → `dict[str, list[str]]`: 基于 brief 构建相关性图谱（单次 LLM 调用）
- `run_cross_references(config)` → `None`: Phase 4 — 刷新所有页面的交叉引用（基于图谱 + 完整内容）
- `update_index_and_log(config, created_page_paths, concepts, filename, today)` → `None`: Phase 5 — 更新索引和日志
- `parse_frontmatter(content)` → `dict[str, str]`: 解析页面 YAML frontmatter
- `slugify(name)` → `str`: 名称→小写连字符 wiki slug

### 常量

- `SUPPORTED_EXTENSIONS`: 支持的 11 种文件扩展名集合
- `TOOL_REQUIREMENTS`: 每种格式对应的外部工具和安装命令
<!-- END:interface -->

---

<!-- BEGIN:dependency_graph -->
## 2. Dependency Graph

- **Imports from `.config`** → Config（路径、模型等）
- **Imports from `.llm`** → call_claude(), call_claude_json(), call_claude_with_tools()
- **Imports from `.tools`** → TOOLS, make_executor()（wiki 工具定义和实现）
- **Imports from `.tracker`** → get_tracker()（按阶段追踪 token 用量）
- **External**: `subprocess`（调用 pdftotext/pandoc/tesseract），`shutil`（复制/检查工具），`re`, `json`, `datetime`
- **Is depended on by**: executor（复用 extract_concepts, generate_pages, run_cross_references, update_index_and_log）
<!-- END:dependency_graph -->

---

<!-- BEGIN:state_management -->
## 3. State Management

**Type**: Stateless

所有函数都是纯数据处理和文件 I/O。LLM 调用通过 `call_claude` 等函数，不缓存结果。文件系统是唯一的状态存储——页面写入 `wiki/*.md`，报告写入 `reports/`，日志追加到 `wiki/log.md`。交叉引用阶段读取所有页面进内存但不持久化中间状态。
<!-- END:state_management -->

---

<!-- BEGIN:edge_cases -->
## 4. Edge Cases

### Hardcoded Values

- **概念提取文本限制**: `8000` 字符（传入 LLM 的文本截断长度）
- **页面生成文本限制**: `6000` 字符
- **空内容跳过**: 格式转换后文本为空时跳过整个管线
- **最少页面数**: 需要至少 2 个页面才能运行交叉引用和相关性图谱

### Error Handling

- **不支持格式**: 抛出 SystemExit 并列出支持的扩展名
- **工具缺失**: `check_tool()` 返回安装提示；`convert_file()` 在调用前检查
- **JSON 解析**: `_parse_json()` 使用 3 层策略：直接解析 → 去代码围栏 → 查找 JSON 边界（支持 DeepSeek 等会在 JSON 前后输出推理文本的模型）
- **页面已存在**: `_init_from_template()` 检查目标是否存在并跳过

### Special Cases

- **Page slug**: slugify 保留中文字符（`一-鿿` unicode 范围），移除特殊字符
- **交叉引用更新**: 通过正则替换 `## See also` 部分，不存在则追加；链接自动清理（去 `.md` 后缀、`[[` 括号）
- **相关性图谱**: 自动过滤自身引用和不存在的页面
- **raw 文件去重**: 如果目标文件已在 `raw/` 中则不重复复制
<!-- END:edge_cases -->

---

<!-- BEGIN:usage_example -->
## 5. Usage Example

```python
from wiki_cli.convert import run_convert, convert_file, parse_frontmatter
from wiki_cli.config import load_config

config = load_config()

# 完整 ingest 流程（单文件）
target = Path("raw/deep-learning.pdf")
created_pages = run_convert(config, target)
# → [Path("wiki/gradient-descent.md"), Path("wiki/backpropagation.md")]

# 仅格式转换（不调用 LLM）
text = convert_file(Path("raw/document.docx"))
print(f"Extracted {len(text)} characters")

# 解析已有页面的 frontmatter
content = Path("wiki/transformer-architecture.md").read_text()
fm = parse_frontmatter(content)
print(fm.get("brief"))  # "Transformer 架构的核心组件和工作原理"

# 手动运行各个阶段
from wiki_cli.convert import extract_concepts, generate_pages

concepts, ambiguities = extract_concepts(config, text, "document.docx")
# concepts = [{"name": "gradient-descent", "action": "create", ...}]

pages = generate_pages(config, concepts, text, "document.docx")
# pages = [(Path("wiki/gradient-descent.md"), {...}), ...]
```
<!-- END:usage_example -->
