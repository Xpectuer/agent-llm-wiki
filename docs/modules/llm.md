---
doc_type: module
module_name: llm
module_path: src/wiki_cli/llm.py
generated_by: mci-phase-2
---

# LLM API 封装模块

> **Purpose**: 封装 Anthropic Claude API 的三层调用接口（单次/JSON/工具循环），提供终端 spinner 和 MultiSpinner 用于并行执行时的进度显示。
> **Path**: `src/wiki_cli/llm.py`

---

<!-- BEGIN:interface -->
## 1. Interface

### Exported Functions/Classes

- `call_claude(config, system, user, max_tokens=4096)` → `str`: 单次 API 调用，返回文本响应
- `call_claude_json(config, system, user, max_tokens=4096)` → `dict | list`: 调用后解析 JSON（自动去除 markdown 代码围栏）
- `call_claude_with_tools(config, system, user, tools, execute_tool, max_turns=8, max_tokens=4096)` → `str`: Agentic 工具调用循环，LLM 可选择调用工具直到最终回答；max_turns 耗尽时追加截断提示
- `MultiSpinner` (class) → 多槽位并行 spinner，在 stderr 渲染单行动画：`⠋ [ch1] Thinking... | ⠙ [ch2] Thinking...`
- `_Spinner` (class) → 单槽 spinner，当 MultiSpinner 激活时自动代理到其槽位
- `_active_multi_spinner` (ContextVar) → 线程安全的 MultiSpinner 引用传递
- `_spinner_label` (ContextVar) → 当前线程的 spinner 标签（如 chapter ID）

### Token 用量

每次 API 调用自动通过 `get_tracker().record()` 记录 token 用量，并打印到 stderr（MultiSpinner 活跃时切换到 stdout 以避免干扰动画行）。
<!-- END:interface -->

---

<!-- BEGIN:dependency_graph -->
## 2. Dependency Graph

- **Imports from `.config`** → Config 数据类（api_key, model, base_url, quiet）
- **Imports from `.tracker`** → get_tracker() 记录 token 用量，effective_input_tokens() 处理非标准 API
- **External**: `anthropic` (Anthropic Python SDK), `threading`, `contextvars`, `json`, `sys`, `time`
- **Is depended on by**: convert, planner, executor, query, llint
<!-- END:dependency_graph -->

---

<!-- BEGIN:state_management -->
## 3. State Management

**Type**: Stateless (with thread-local context)

API 调用本身无状态。Spinner 使用以下机制：

- **_Spinner**: 自身维护 `_running` 标志和渲染线程；当检测到 `_active_multi_spinner` ContextVar 时，转为代理模式（向 MultiSpinner 注册/注销槽位）
- **MultiSpinner**: 维护 `_slots` 字典（slot_id → (label, message)），通过 threading.Lock 保护。ContextVar `_active_multi_spinner` 在 `__enter__` 时设置，`__exit__` 时重置
- **_spinner_label** ContextVar: 每个线程设置自己的标签（如 `ch-01`），在 spinner 渲染时自动使用
<!-- END:state_management -->

---

<!-- BEGIN:edge_cases -->
## 4. Edge Cases

### Hardcoded Values

- **默认 max_tokens**: `4096`
- **最大工具调用轮次**: `8`（超限时追加截断警告）
- **Spinner 帧率**: `0.1` 秒/帧（10 FPS）
- **Spinner 动画帧**: 10 帧 braille 字符

### Error Handling

- **工具调用异常**: 单个工具调用出错时返回 `{"type": "tool_result", "is_error": true}` 而非终止整个循环
- **非标准 API**: `effective_input_tokens()` 处理 `input_tokens=0` 的情况（某些兼容 API 将 token 数藏在 cache_read_input_tokens 中）
- **thiking blocks**: 工具调用循环透传 `thinking` 类型的内容块回 API（扩展思考模型需要）

### Special Cases

- **stderr vs stdout**: 在 MultiSpinner 活跃期间（`_stderr_safe()=False`），token 用量和工具调用日志切换到 stdout 以避免破坏 stderr 上的动画行
- **quiet 模式**: `config.quiet=True` 时，_Spinner 完全跳过动画渲染
- **JSON 解析**: `call_claude_json()` 自动处理 markdown 代码围栏（```json ... ```）
<!-- END:edge_cases -->

---

<!-- BEGIN:usage_example -->
## 5. Usage Example

```python
from wiki_cli.llm import call_claude, call_claude_json, call_claude_with_tools, MultiSpinner
from wiki_cli.config import Config

config = load_config()

# 1. 单次文本调用
answer = call_claude(
    config,
    system="You are a helpful assistant.",
    user="What is a transformer?",
    max_tokens=2048,
)

# 2. JSON 结构化输出
result = call_claude_json(
    config,
    system="Output valid JSON only.",
    user="List 3 colors with hex codes.",
)
# → {"colors": [{"name": "Red", "hex": "#FF0000"}, ...]}

# 3. Agentic 工具调用
def my_tool_executor(name: str, input_data: dict) -> str:
    if name == "search":
        return f"Results for: {input_data['query']}"
    raise ValueError(f"Unknown tool: {name}")

tools = [{
    "name": "search",
    "description": "Search the knowledge base",
    "input_schema": {
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"],
    },
}]

answer = call_claude_with_tools(
    config,
    system="Use search tool to find information.",
    user="Find docs about Python async.",
    tools=tools,
    execute_tool=my_tool_executor,
)

# 4. 并行执行时的 spinner
with MultiSpinner():
    # 子线程中的 _Spinner 实例自动注册到 MultiSpinner
    import threading
    def worker(ch_id):
        from wiki_cli.llm import _spinner_label
        _spinner_label.set(ch_id)
        # call_claude 内的 _Spinner 会自动显示为 [ch_id] 槽
        call_claude(config, "...", "...")

    threads = [threading.Thread(target=worker, args=(f"ch-{i:02d}",)) for i in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
```
<!-- END:usage_example -->
