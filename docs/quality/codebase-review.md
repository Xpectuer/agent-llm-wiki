---
doc_type: review
generated_by: mci-phase-4
review_date: "2026-05-17"
---

# LLM Wiki — 代码库质量评估

---

<!-- BEGIN:gap-analysis -->
## 差距分析

### 遗漏的区域

- **缺少测试目录**: 项目中完全没有 `tests/` 目录或任何测试文件。所有 11 个模块（~3000 行 Python）零测试覆盖。
- **缺少 CI/CD 配置**: 无 `.github/workflows/`、`Makefile` 或任何自动化构建/测试/发布流程。
- **空 `__init__.py`**: `src/wiki_cli/__init__.py` 仅 1 行，无任何导出的公共 API 或版本号。
- **未追踪文件**: git status 显示 `codex-harness.md`、`未命名.md` 等未追踪文件散落在项目根目录，应清理或归档到 `raw/`。
- **`src/wiki_cli.egg-info/`**: 自动生成的构建产物混在源码树中，建议加入 `.gitignore`。

### 死代码检测

- **无明显死代码**: 搜索未发现 TODO、FIXME、HACK、XXX 注释。所有导入的函数均被实际调用。
- **`_create_claude_md()`**: cli.py 中的函数仅用于 `wiki init` 命令，创建的 CLAUDE.md 内容是硬编码模板——如果项目 CLAUDE.md 已大幅修改，此函数生成的模板会明显过时。

### 结构一致性

- **模块边界清晰**: 11 个模块关注点分离良好，无循环依赖。
- **单文件过大**: `convert.py`（693 行）是唯一超过 400 行的文件，混合了格式转换、管线编排、交叉引用、frontmatter 解析、日志更新等多种职责。
- **重复函数**: `_read_all_wiki_pages()` 和 `_list_page_names()` 在 `convert.py`、`tools.py` 和 `llint.py` 中各自独立定义，存在代码重复。
<!-- END:gap-analysis -->

---

<!-- BEGIN:risk-assessment -->
## 风险评估

### 技术债务

| 区域 | 严重性 | 描述 | 建议 |
|------|--------|------|------|
| 测试覆盖 | 高 | 0% 测试覆盖率，所有功能依赖手动验证 | 为核心管线（convert、query）添加集成测试 |
| convert.py 体积 | 中 | 693 行，混合 6 种职责 | 拆分为 convert_file.py、pipeline.py、xref.py |
| 重复的工具函数 | 低 | `_read_all_wiki_pages` 在 3 个文件中重复定义 | 统一到 tools.py 并导出 |
| 硬编码 token 限制 | 中 | text_limit 分散在各处（8000/6000/12000/2000/1500），模型切换时可能截断不当 | 集中到 Config 或各调用方可配置 |
| API 无重试 | 中 | `call_claude` 无网络错误重试逻辑，大文档 ingest 中途失败会丢失进度 | 添加指数退避重试 + 断点续传 |
| JSON 解析鲁棒性 | 低 | `_parse_json` 有 3 层回退策略应对不同模型的输出格式，说明解析不够稳健 | 强化 prompt 约束输出格式，减少回退依赖 |

### 安全热点

- **API Key 管理**: `ANTHROPIC_API_KEY` 从环境变量读取，未硬编码。✅
- **Subprocess 调用**: pdftotext/pandoc/tesseract 通过 `subprocess.run` 调用，参数由文件路径构建。文件路径来自 CLI 参数（Click 校验），但未做额外消毒。⚠️ 低风险。
- **LLM 输出注入**: LLM 生成的页面内容直接写入 `.md` 文件。由于 wiki 页面仅供人类阅读（非执行环境），XSS/代码注入风险极低。✅
- **无网络暴露**: 纯 CLI 工具，无服务端口。✅
- **依赖版本**: pyproject.toml 使用 `>=` 约束而非 lock 文件，依赖解析在不同环境可能不一致。⚠️ 低风险。
<!-- END:risk-assessment -->

---

<!-- BEGIN:ai-score -->
## AI 可用性评分: 7.0/10

### 得分明细

| 标准 | 权重 | 评分 | 说明 |
|------|------|------|------|
| 代码清晰度 | 20% | 8/10 | 命名规范、函数短小、模式一致。convert.py 偏长但分段清晰 |
| 模块化 | 20% | 8/10 | 11 个模块边界清晰，无循环依赖，依赖方向合理（基础设施←业务←CLI） |
| 文档完整性 | 20% | 7/10 | CLAUDE.md + ARCHITECTURE.md + 11 模块文档覆盖全面，但缺少 API 参考和变更日志 |
| 类型安全 | 15% | 7/10 | 全面使用 type hints + `from __future__ import annotations`，但未使用 mypy 验证 |
| 测试覆盖率 | 15% | 2/10 | 零测试。这是最严重的短板 |
| 代码复杂性 | 10% | 7/10 | 11 个源文件平均 270 行，convert.py（693 行）是唯一的复杂度热点 |

**总体评价**: 代码架构清晰、模块化良好，对 AI 代理较为友好。最严重的短板是完全没有自动化测试，其次是 convert.py 的单文件体积。安全方面无明显红线。
<!-- END:ai-score -->

---

<!-- BEGIN:improvements -->
## 改进建议 (优先排序)

### 1. 添加自动化测试 — 四阶段实施方案 (影响: 高)

> **当前状态**: 0% 测试覆盖，~3000 行 Python 完全依赖手动验证。
> **总体目标**: 覆盖率达到 60%+，核心纯逻辑 90%+，CI 可自动验证。
> **总工作量**: 约 1.5 周（可分期执行，每阶段独立交付价值）。

---

#### Phase 1: 纯逻辑单元测试 (1-2 天，ROI 最高)

覆盖所有不依赖 LLM、不读写文件系统的纯函数。这些测试零外部依赖、毫秒级运行、收益最大。

**测试文件**: `tests/unit/test_slugify.py`, `tests/unit/test_parse_frontmatter.py`, `tests/unit/test_parse_json.py`, `tests/unit/test_tracker.py`, `tests/unit/test_dag.py`, `tests/unit/test_models.py`

| 被测函数 | 所在文件 | 测试要点 |
|----------|----------|----------|
| `slugify()` | convert.py | 英文/中文/混合/特殊字符/空字符串/首尾连字符 |
| `parse_frontmatter()` | convert.py | 标准格式/空内容/无 frontmatter/brief 字段/多行值 |
| `_parse_json()` | convert.py | 纯 JSON/```json fence```/散文+JSON 混合/嵌套对象/空数组/非法 JSON 报错 |
| `effective_input_tokens()` | tracker.py | 正常 input/input=0 从 cache 聚合/全零/部分字段缺失 |
| `TokenTracker.record()` | tracker.py | 单次记录/多次记录/线程安全并发写入 |
| `TokenTracker.phase()` | tracker.py | 上下文管理器切换/异常恢复/nested phase |
| `TokenTracker._aggregate()` | tracker.py | 按 phase 聚合/计数与求和正确性/成本计算 |
| `TokenTracker.report()` | tracker.py | 空记录/有数据/中文输出格式 |
| `TokenTracker.html_report()` | tracker.py | HTML 结构完整性/空记录处理 |
| `get_tracker()` | tracker.py | 单例模式/多次调用返回同一实例 |
| `_validate_dag()` | planner.py | 合法 DAG/缺失依赖报错/环路检测/空章节列表 |
| `_topological_levels()` | planner.py | 线性依赖/并行层/复杂 DAG/空图/单节点 |
| `split_chapters()` | planner.py | 正则匹配/fallback 比例切分/单章节/空文本 |
| `describe_plan()` | planner.py | 输出格式/多层级展示/依赖项展示 |
| `_strip_frontmatter()` | executor.py | 标准 frontmatter/无 frontmatter/多段内容 |
| `LintResult.pass_/fail/warn` | llint.py | 三种级别分类/format_report 格式 |
| `_count_rounds()` | llint.py | 空文件/多轮/无匹配 |

**示例**（`tests/unit/test_dag.py`）:
```python
import pytest
from wiki_cli.planner import _validate_dag, _topological_levels
from wiki_cli.models import Chapter

def make_ch(id, deps=None):
    return Chapter(id=id, title=id, order=0, heading_pattern="", depends_on=deps or [])

class TestValidateDAG:
    def test_valid_linear(self):
        _validate_dag([make_ch("a"), make_ch("b", ["a"]), make_ch("c", ["b"])])

    def test_missing_dependency_raises(self):
        with pytest.raises(ValueError, match="unknown chapter"):
            _validate_dag([make_ch("a", ["nonexistent"])])

    def test_cycle_raises(self):
        with pytest.raises(ValueError, match="Cycle detected"):
            _validate_dag([make_ch("a", ["b"]), make_ch("b", ["a"])])

class TestTopologicalLevels:
    def test_linear_three_levels(self):
        chs = [make_ch("a"), make_ch("b", ["a"]), make_ch("c", ["b"])]
        assert _topological_levels(chs) == [["a"], ["b"], ["c"]]

    def test_parallel_level(self):
        chs = [make_ch("a"), make_ch("b", ["a"]), make_ch("c", ["a"])]
        assert _topological_levels(chs) == [["a"], ["b", "c"]]

    def test_diamond_dag(self):
        chs = [make_ch("a"), make_ch("b", ["a"]), make_ch("c", ["a"]), make_ch("d", ["b", "c"])]
        levels = _topological_levels(chs)
        assert levels[0] == ["a"]
        assert set(levels[1]) == {"b", "c"}
        assert levels[2] == ["d"]
```

**示例**（`tests/unit/test_parse_json.py`）:
```python
import json
import pytest
from wiki_cli.convert import _parse_json

def test_plain_json():
    assert _parse_json('{"a": 1}') == {"a": 1}

def test_json_in_fence():
    assert _parse_json('```json\n{"a": 1}\n```') == {"a": 1}

def test_json_in_mixed_text():
    result = _parse_json('Here is my reasoning...\n{"concepts": [{"name": "test"}]}\nMore text...')
    assert result == {"concepts": [{"name": "test"}]}

def test_nested_braces():
    assert _parse_json('{"outer": {"inner": [1, 2, 3]}}') == {"outer": {"inner": [1, 2, 3]}}

def test_invalid_json_raises():
    with pytest.raises(json.JSONDecodeError):
        _parse_json("not json at all")

def test_empty_array():
    assert _parse_json('{"concepts": []}') == {"concepts": []}
```

---

#### Phase 2: 文件系统集成测试 (2-3 天)

覆盖需要读写 `wiki/`、`reports/` 目录但不需要 LLM 的函数。使用 `tmp_path` fixture。

**测试文件**: `tests/integration/test_tools.py`, `tests/integration/test_lint.py`, `tests/integration/test_convert_helpers.py`, `tests/integration/test_planner_io.py`

| 被测函数 | 文件 | 测试要点 |
|----------|------|----------|
| `_list_page_names()` | tools.py | 空目录/有页面/排除 index 和 log |
| `search_wiki()` | tools.py | 精确匹配/中文搜索/无结果/多页面排序 |
| `read_page()` | tools.py | 存在/不存在/去掉 .md 后缀 |
| `list_pages()` | tools.py | 空/有页面/排序输出 |
| `check_required_files()` | llint.py | 全部存在/全部缺失/部分缺失 |
| `check_broken_links()` | llint.py | 无断链/断链检测/跨文件引用 |
| `check_orphan_pages()` | llint.py | 无孤立/孤立页面/双向引用 |
| `check_xref_density()` | llint.py | 高密度/低密度警告/空 wiki |
| `check_contradictions()` | llint.py | 无标记/有标记检测 |
| `_read_all_wiki_pages()` | llint.py+convert.py | 空/多页面/排除规则 |
| `_update_see_also()` | convert.py | 替换已有/追加新 section |
| `_update_index()` | convert.py | Synthesis section/Concepts section |
| `_append_log()` | convert.py | 新条目追加/log 不存在 |
| `save_plan()` / `load_plan()` | planner.py | round-trip 一致性/JSON 格式 |
| `Config` 路径解析 | config.py | 环境变量覆盖/默认值/相对路径 |

**示例**（`tests/integration/test_lint.py`）:
```python
from wiki_cli.config import Config
from wiki_cli.llint import LintResult, check_broken_links, check_orphan_pages

def make_config(tmp_path):
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    return Config(api_key="test", model="test", wiki_dir=wiki, ...)

def test_no_broken_links(tmp_path):
    config = make_config(tmp_path)
    (config.wiki_dir / "a.md").write_text("See [[b]] for more.")
    (config.wiki_dir / "b.md").write_text("# B")
    result = LintResult()
    check_broken_links(config, result)
    assert "No broken internal links" in "\n".join(result.passes)

def test_broken_link_detected(tmp_path):
    config = make_config(tmp_path)
    (config.wiki_dir / "a.md").write_text("See [[nonexistent]] for more.")
    result = LintResult()
    check_broken_links(config, result)
    assert any("nonexistent" in e for e in result.errors)

def test_orphan_detection(tmp_path):
    config = make_config(tmp_path)
    (config.wiki_dir / "lonely.md").write_text("# Nobody links here")
    (config.wiki_dir / "popular.md").write_text("See [[lonely]] and more.")
    result = LintResult()
    check_orphan_pages(config, result)
    assert any("lonely" in w for w in result.warnings)
```

---

#### Phase 3: LLM Mock 集成测试 (2-3 天)

Mock Anthropic SDK 的 `messages.create()`，验证管线逻辑正确性（prompt 构建、工具调用循环、JSON 解析、错误处理）。

**测试文件**: `tests/integration/test_convert_pipeline.py`, `tests/integration/test_query.py`, `tests/integration/test_executor.py`, `tests/conftest.py`（共享 fixtures）

| 场景 | 测试要点 |
|------|----------|
| `extract_concepts()` | Mock 工具调用循环 → 验证返回的 concepts/ambiguities 结构 |
| `generate_pages()` create | Mock 单次 API 响应 → 验证页面写入和 frontmatter |
| `generate_pages()` merge | Mock 响应 → 验证合并目标路径正确 |
| `build_relevance_graph()` | Mock JSON 响应 → 验证图过滤逻辑 |
| `run_cross_references()` | Mock graph + xref 响应 → 验证 See also 更新 |
| `run_query()` | Mock 工具调用循环 → 验证答案记录到 reports |
| `execute_plan()` | Mock 每个 chapter 的 LLM 调用 → 验证 DAG 顺序和结果聚合 |
| `_dedup_new_pages()` | Mock dedup 响应 → 验证页面合并删除 |
| LLM 调用失败重试 | Mock 网络异常 → 验证错误处理不崩溃 |

**共享 fixture 示例**（`tests/conftest.py`）:
```python
import pytest
from unittest.mock import patch, MagicMock
from wiki_cli.config import Config

@pytest.fixture
def wiki_config(tmp_path):
    """Provide a Config pointing at temp directories."""
    wiki = tmp_path / "wiki"
    raw = tmp_path / "raw"
    reports = tmp_path / "reports"
    for d in [wiki, raw, reports]:
        d.mkdir()
    return Config(
        api_key="test-key",
        model="claude-sonnet-4-6",
        base_url=None,
        wiki_dir=wiki,
        raw_dir=raw,
        reports_dir=reports,
        templates_dir=tmp_path / "templates",
        project_root=tmp_path,
    )

@pytest.fixture
def mock_claude():
    """Mock anthropic.Anthropic().messages.create() to return a controlled response."""
    with patch("wiki_cli.llm.Anthropic") as mock_client:
        instance = mock_client.return_value
        yield instance.messages
```

---

#### Phase 4: CLI 端到端测试 (可选，1-2 天)

使用 Click 的 `CliRunner` 测试命令行参数解析和命令路由，无需真实 LLM。

**测试文件**: `tests/integration/test_cli.py`

```python
from click.testing import CliRunner
from wiki_cli.cli import cli

def test_init_creates_directories(tmp_path, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0
        assert (tmp_path / "wiki").is_dir()
        assert (tmp_path / "raw").is_dir()

def test_convert_requires_file():
    runner = CliRunner()
    result = runner.invoke(cli, ["convert", "nonexistent.pdf"])
    assert result.exit_code != 0

def test_lint_no_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    runner = CliRunner()
    result = runner.invoke(cli, ["lint"])
    assert result.exit_code != 0
    assert "ANTHROPIC_API_KEY" in result.output
```

---

#### 基础设施准备

1. **添加 pytest 依赖**:
```toml
# pyproject.toml
[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-cov>=5.0"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
addopts = "-v --tb=short"
```

2. **目录结构**:
```
tests/
├── conftest.py           # 共享 fixtures: wiki_config, mock_claude
├── unit/
│   ├── test_slugify.py
│   ├── test_parse_frontmatter.py
│   ├── test_parse_json.py
│   ├── test_tracker.py
│   ├── test_dag.py
│   └── test_lint_result.py
├── integration/
│   ├── test_tools.py
│   ├── test_lint_checks.py
│   ├── test_convert_helpers.py
│   ├── test_planner_io.py
│   ├── test_convert_pipeline.py
│   ├── test_query.py
│   └── test_cli.py
```

3. **运行命令**:
```bash
pytest                              # 全部测试
pytest tests/unit/                  # 仅单元测试 (~1s)
pytest --cov=wiki_cli --cov-report=term  # 带覆盖率
```

#### 分期交付计划

| 阶段 | 测试数（估算） | 覆盖模块 | 可独立交付 |
|------|---------------|----------|-----------|
| Phase 1 | ~50 | tracker, planner (DAG), convert (纯函数), llint (LintResult) | ✅ 1-2 天后即可在 CI 运行 |
| Phase 2 | ~35 | tools, llint (checks), convert (helpers), planner (IO) | ✅ 可独立运行 |
| Phase 3 | ~20 | convert pipeline, query, executor | ✅ 核心管线首次有测试保护 |
| Phase 4 | ~10 | CLI 命令 | 可选，建议和 Phase 1 一起做 |

### 2. 拆分 convert.py (693 行 → 3-4 个文件) (影响: 高)

- **当前状态**: convert.py 混合了格式转换、5 阶段管线、交叉引用、frontmatter 解析、索引更新
- **目标**: 拆分为 `convert_file.py`（格式转换）、`pipeline.py`（标准管线）、`xref.py`（交叉引用）、`frontmatter.py`（元数据）
- **工作量**: 低 (3-5 天)
- **收益**:
  - 每个模块 < 300 行，AI 代理更容易理解
  - 交叉引用逻辑可独立测试和复用
  - executor.py 可以按需导入更细粒度的模块

### 3. 统一工具函数 + 消除重复代码 (影响: 中)

- **当前状态**: `_read_all_wiki_pages()` 和 `_list_page_names()` 在 convert.py、tools.py、llint.py 中各自定义
- **目标**: 统一到 tools.py 并导出为公共函数，其他模块从 tools 导入
- **工作量**: 低 (1-2 天)
- **收益**:
  - 消除 3 处重复代码
  - 统一页面过滤逻辑（index/log 排除规则）
  - 降低未来修改的维护成本
<!-- END:improvements -->
