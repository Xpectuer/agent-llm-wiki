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

### 1. 添加核心管线的集成测试 (影响: 高)

- **当前状态**: 0% 测试覆盖，~3000 行 Python 完全依赖手动验证
- **目标**: 为 `convert_file()`（格式转换）、`run_query()`（查询）、`run_lint()`（检查）添加集成测试，覆盖率达到 60%+
- **工作量**: 中等 (1-2 周)
- **收益**:
  - CI 中可自动验证 ingest 和 query 管线
  - LLM 调用可用 mock 替代，测试纯逻辑部分
  - 防止重构时引入回归

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
