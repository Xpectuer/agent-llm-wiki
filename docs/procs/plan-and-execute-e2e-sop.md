---
doc_type: proc
proc_type: sop
scope: plan-and-execute mode e2e verification
last_verified: 2026-05-18
---

# Plan-and-Execute E2E 验证 SOP

> 验证 `wiki convert` 的大文档 plan-and-execute 模式端到端工作正常。

---

## 1. 测试文件契约

### 最小要求

| 维度 | 要求 | 说明 |
|------|------|------|
| 字符数 | > 30,000（默认 `WIKI_LARGE_THRESHOLD`） | 低于此值触发 standard 模式，不走 plan-and-execute |
| 格式 | `.md`（无需外部工具） | 其他格式需要 pdftotext/pandoc/tesseract |
| 章节结构 | 每个章节 ≥1 个 `## Chapter N: Title` 标题 | planner 用 heading_pattern 定位章节边界 |
| 内容质量 | 每个章节够提取 2-5 个概念 | 内容太少会导致空 chapter（success 但无页面） |

### 推荐测试文件结构

```markdown
# Document Title

> A brief intro to set context.

---

## Chapter 1: Topic A

Substantive content with enough detail for concept extraction...
(每个章节至少 3000+ 字符)

## Chapter 2: Topic B

...

## Chapter N: Topic N

...
```

### 已验证的测试文件

`examples/codex-ml/raw/software-engineering-practices.md` — 30,363 字符，7 章软件工程主题。

生成脚本（可复用）：

```bash
python3 << 'PYEOF'
# 调整 chapters 列表即可生成不同主题的测试文件
# 确保总和 > 30,000 字符
PYEOF
```

---

## 2. Positive Path（正常流程）

### 2.1 运行命令

```bash
WIKI_DIR=examples/<wiki>/wiki \
RAW_DIR=examples/<wiki>/raw \
REPORTS_DIR=examples/<wiki>/reports \
TEMPLATES_DIR=examples/<wiki>/templates \
uv run wiki convert examples/<wiki>/raw/<large-file>.md -q
```

### 2.2 预期阶段

```
Document: 30,363 chars (threshold: 30,000). Using plan-and-execute mode.  ← 阶段0: 自动检测

[Plan] Analyzing document structure...                                      ← 阶段1: Planner
[LLM] N input + M output tokens
Plan saved to .../plan-YYYY-MM-DD-<file>.json
Plan: <file> (N chars)
Found X chapter(s) in Y DAG level(s):
  Level 1: [ch-01: ... (no deps), ch-02: ... (no deps)] ← 2 parallel
  Level 2: [ch-03: ... (depends: ch-01)]

Splitting text into X chapter(s)...                                         ← 阶段2: Executor
  ch-01: N chars — Title
  ...
Executing Y DAG level(s) with max 4 worker(s):
  Level 1: ... [parallel x2]
    [ch-01] Found N concept(s), generating pages...
    Written: .../wiki/page-name.md
    ✓ ch-01: success — pages: page-1, page-2
    ...
  Level 2: ...
    ✓ ch-03: success — pages: page-3, page-4

[Final] Checking new pages for redundancy...                                ← 阶段3: Merge
  Merging [[a]] → [[b]]: reason
  Removed: .../wiki/a.md

[Final] Updating cross-references...                                        ← 阶段4: Cross-ref
  Building relevance graph from briefs...
  Merge candidate: [[x]] ← [[y]]

[Final] Updating index and log...                                           ← 阶段5: Index

==================================================
Execution complete: X/Y chapters succeeded
Pages created/updated: Z
```

### 2.3 成功判据

- [ ] 输出 `Using plan-and-execute mode`（自动检测正确）
- [ ] Plan JSON 保存到 `reports/plan-*.json`
- [ ] 章节按 DAG 层级排序，同层有 `[parallel xN]` 标记
- [ ] 每个成功 chapter 输出 `✓ ch-XX: success — pages: ...`
- [ ] Dedup 阶段正确识别并合并重叠页面
- [ ] 交叉引用阶段输出 `Building relevance graph from briefs...`
- [ ] 最终输出 `Execution complete: X/Y chapters succeeded`
- [ ] 退出码为 0

---

## 3. Negative Situations & Handling

### 3.1 Chapter 执行失败：JSON 解析错误

**现象**：
```
✗ ch-01: failed — pages: none
  Error: 'list' object has no attribute 'get'
```

**根因**：`_process_chapter()` 调用 `extract_concepts()` → LLM 的 JSON 输出被 `_parse_json()` 解析为 list 而非 dict。下游 `result.get("concepts", [])` 期望 dict，对 list 调用 `.get()` 报错。

**已知触发场景**：DeepSeek 模型（通过 `ANTHROPIC_BASE_URL` 代理）偶尔在 `{...}` JSON 外层包裹推理文本，`_parse_json()` 的 3 层策略未能处理。

**处理方式**：
1. 检查 `_parse_json()` 的三层策略是否覆盖该模型的输出格式
2. 临时绕过：用 `--no-large` 降级为 standard 单次模式
3. 永久修复：增强 `_parse_json()`，在解析失败时添加更激进的 JSON 提取（如使用 `json.loads` 的 `strict=False`、处理 BOM 等）

**代码位置**：`src/wiki_cli/convert.py:_parse_json()` (line 541)、`src/wiki_cli/executor.py:_process_chapter()` (line 142)

### 3.2 Planner 章节合并

**现象**：源文档有 7 个 `## Chapter N` 标题，Planner 只识别出 3 个章节。

**根因**：Planner 只发送文档前 12,000 字符给 LLM 分析（`text_limit=12000`），无法看到所有章节。LLM 基于部分信息做了章节合并。

**处理方式**：
1. 调大 `plan_document()` 的 `text_limit` 参数（当前 12,000）
2. 使用 `--plan-file` 加载手动调整过的 plan JSON
3. 如果合并合理（内容确实相关），接受 LLM 的判断

**代码位置**：`src/wiki_cli/planner.py:plan_document()` (line 130)

### 3.3 所有 concepts merge 到同一页面

**现象**：一个 chapter 提取了 10 个 concept，全部以 `action: "merge"` 指向同一页面（如 `code-review`），生成的 10 个页面都是同一个文件。

**根因**：Wiki 中已存在同名页面，且 LLM 决定所有概念都应合并到该页面。这是合理的 agentic 行为（避免创建重复页面），但导致文件被反复覆盖。

**影响**：同一文件被写入多次，最终内容取决于最后一次生成。没有数据丢失，但有 API 浪费。

**处理方式**：
1. 检查 concept extraction 的输出，看是否真的有 10 个不同概念可以分开
2. 可考虑在 `generate_pages()` 中加去重：同一个 target_page 只 merge 一次
3. 在 agent prompt 中提示避免大量 merge 到同一页面

### 3.4 Dedup 后交叉引用残留

**现象**：Dedup 阶段将 `trunk-based-development` 合并入 `continuous-integration` 并删除源文件，但后续交叉引用阶段仍然输出：
```
Merge candidate: [[continuous-integration]] ← [[trunk-based-development]]
```

**根因**：交叉引用阶段 `run_cross_references()` 基于所有 wiki 页面（包括之前被删除的），可能有缓存或时序问题。但观察实际结果，这个 merge candidate 可能来自 brief 中仍存在的引用。

**处理方式**：
1. 检查 `merge_all_results()` 中 dedup 后的 `new_page_slugs` 是否正确移除了已删除页面
2. 交叉引用在 dedup 后运行，理论上不应看到已删除页面；如果看到则是时序 bug
3. 可接受警告（不 fatal）——merge candidate 只是建议

**代码位置**：`src/wiki_cli/executor.py:merge_all_results()` (line 260)

### 3.5 文件未达到阈值

**现象**：输出 `Using standard mode` 而非 plan-and-execute。

**处理方式**：
1. 确认字符数：`python3 -c "print(len(open('path').read()))"`
2. 确认阈值：`echo $WIKI_LARGE_THRESHOLD`（默认 30,000）
3. 用 `--large` 强制触发 plan-and-execute

### 3.6 空 Wiki（无现有页面）

**现象**：Concept extraction 的 tool-calling 循环中 `list_pages()` 返回空，`search_wiki()` 无结果。

**影响**：LLM 无法做 merge 判断，所有 concept 都是 create。这是正确的行为——新 wiki 不应有 merge。

**处理方式**：无需处理。但如果想测试 merge 路径，需要预先有一个填充好的 wiki（如 `codex-ml`）。

### 3.7 外部工具缺失

**现象**（非 `.md` 文件时）：
```
Error: pandoc not found for .docx files. Install with: brew install pandoc
```

**处理方式**：
1. 安装对应工具：`brew install pandoc` / `brew install poppler` / `brew install tesseract`
2. 或使用 `.md` 格式（无需外部工具），推荐用于纯 e2e 验证

### 3.8 API 超时或限流

**现象**：LLM 调用挂起或返回错误。

**处理方式**：
1. Plan-and-execute 有容错——单个 chapter 失败不影响其他 chapter
2. 失败的 chapter 显示 `✗ ch-XX: failed` 并携带错误信息
3. 最终统计区分 success/failed chapter
4. 可重跑（使用 `--plan-file` 跳过 plan 阶段，节省一次 API 调用）

---

## 4. E2E Test Checklist

运行前：

- [ ] `ANTHROPIC_API_KEY` 已设置
- [ ] 目标 wiki 有 `wiki/index.md` 和 `wiki/log.md`
- [ ] 测试文件 > 30,000 字符且有清晰章节标题
- [ ] 测试文件在 `examples/<name>/raw/` 中

运行中（观察）：

- [ ] 输出 `Using plan-and-execute mode`
- [ ] Planner 产出了合理的章节划分
- [ ] 每个 DAG 层级正确标记 parallel
- [ ] 失败的 chapter 有明确错误信息

运行后验证：

- [ ] `reports/plan-*.json` 存在且可读
- [ ] 新页面在 `wiki/` 中，符合 frontmatter + See also 结构
- [ ] `wiki/index.md` 有更新
- [ ] `wiki/log.md` 有新条目
- [ ] 退出码 = 0

---

## 5. 快速验证命令

```bash
# 完整 e2e（使用 codex-ml wiki）
WIKI_DIR=examples/codex-ml/wiki \
RAW_DIR=examples/codex-ml/raw \
REPORTS_DIR=examples/codex-ml/reports \
TEMPLATES_DIR=examples/codex-ml/templates \
uv run wiki convert examples/codex-ml/raw/software-engineering-practices.md -q

# 仅规划（dry-run，节省 API）
uv run wiki convert examples/codex-ml/raw/software-engineering-practices.md --dry-run -q \
  --project-root examples/codex-ml

# 强制标准模式（对比）
uv run wiki convert examples/codex-ml/raw/software-engineering-practices.md --no-large -q \
  --project-root examples/codex-ml
```
