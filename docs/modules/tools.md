---
doc_type: module
module_name: tools
module_path: src/wiki_cli/tools.py
generated_by: mci-phase-2
---

# Tools 共享 Wiki 工具模块

> **Purpose**: 为 agentic 工具调用循环提供共享的 wiki 工具定义和实现，被 query 和 convert（ingest）共用。
> **Path**: `src/wiki_cli/tools.py`

---

<!-- BEGIN:interface -->
## 1. Interface

### Exported Functions/Classes

- `TOOLS` (constant) → `list[dict]`: 3 个工具的 Anthropic API 格式定义（search_wiki, read_page, list_pages）
- `search_wiki(config, query)` → `str`: 全文搜索所有 wiki 页面，返回带行号的排名片段（最多 10 个结果，每页最多 5 个片段）
- `read_page(config, name)` → `str`: 读取指定 wiki 页面的完整内容
- `list_pages(config)` → `str`: 列出所有 wiki 页面名（排序后的 wikilink 格式）
- `make_executor(config)` → `Callable[[str, dict], str]`: 创建工具执行回调函数，用于 `call_claude_with_tools()`

### 工具定义

| 工具名 | 描述 | 必需参数 |
|--------|------|----------|
| `search_wiki` | 全文搜索 wiki 页面，返回排名片段 | `query` (string) |
| `read_page` | 读取指定页面的完整内容 | `name` (string, 不含 .md) |
| `list_pages` | 列出所有页面名 | 无 |

### 内部函数

- `_list_page_names(config)` → `list[str]`: 列出页面名（排除 index 和 log）
<!-- END:interface -->

---

<!-- BEGIN:dependency_graph -->
## 2. Dependency Graph

- **Imports from `.config`** → Config（wiki_dir 路径）
- **External**: `re`
- **Is depended on by**: query, convert（两者都通过 TOOLS + make_executor 使用工具）
<!-- END:dependency_graph -->

---

<!-- BEGIN:state_management -->
## 3. State Management

**Type**: Stateless

所有工具都是纯文件 I/O 操作：读取 wiki 目录中的 `.md` 文件，无缓存，无全局状态。每次搜索都重新读取所有页面。
<!-- END:state_management -->

---

<!-- BEGIN:edge_cases -->
## 4. Edge Cases

### Hardcoded Values

- **搜索结果限制**: 前 `10` 个最相关页面
- **每页片段限制**: 前 `5` 个匹配片段
- **Token 长度**: 中英文字符 `\w` 和 CJK `一-鿿`，最小 `2` 字符
- **上下文窗口**: 匹配行前后各 `1` 行
- **行内容截断**: `120` 字符

### Error Handling

- **页面不存在**: `read_page()` 返回错误消息并列出所有可用页面
- **空 wiki**: `search_wiki` 返回 `"(wiki 中没有页面)"`
- **未知工具**: `make_executor` 返回的错误处理未知工具名

### Special Cases

- **搜索算法**: 简单词频统计——每个 token 在页面内容中出现的次数累加为分数。非全文搜索引擎，但对小规模 wiki 足够
- **排除页面**: index.md 和 log.md 不参与搜索和列表
- **去重片段**: `seen_lines` 集合防止同一行出现在多个片段中
- **clean_name**: `read_page` 自动去除 `.md` 后缀和首尾空白
<!-- END:edge_cases -->

---

<!-- BEGIN:usage_example -->
## 5. Usage Example

```python
from wiki_cli.tools import TOOLS, make_executor, search_wiki, read_page, list_pages
from wiki_cli.config import load_config

config = load_config()

# 直接调用工具函数
results = search_wiki(config, "gradient descent")
# → 搜索结果 'gradient descent':
#   ## [[gradient-descent]] (相关度: 8)
#     L15: ## 梯度下降算法
#     L16: 梯度下降是最基础的优化算法...
#     L17: ### 批量梯度下降

content = read_page(config, "transformer-architecture")
# → # Transformer 架构
#   > Source(s): raw/deep-learning.pdf
#   ...

all_pages = list_pages(config)
# → - [[bert]]
#   - [[gradient-descent]]
#   - [[transformer-architecture]]
#   ...

# 在 agentic 循环中使用
from wiki_cli.llm import call_claude_with_tools

answer = call_claude_with_tools(
    config,
    system="使用工具搜索 wiki",
    user="解释 attention mechanism",
    tools=TOOLS,
    execute_tool=make_executor(config),
)
```
<!-- END:usage_example -->
