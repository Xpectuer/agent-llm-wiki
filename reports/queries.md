# Queries

> Record of questions asked against the wiki with their answers and citations.

<!-- Add query records here using the format:
## [date] question
**Answer**: ...
**Citations**: [[page]] — what was cited
**Raw sources**: raw/file
-->

## [2026-05-04] Transformer和BERT有什么区别？

**回答**: 信息不足以回答。当前提供的 wiki 页面为空（没有找到相关页面），且未提供任何原始参考材料，因此无法基于现有知识库内容为您解答“Transformer和BERT有什么区别”。

**引用**:
- (无相关引用)

**建议新页面**: 
- **建议页面名称**: `[[Transformer_vs_BERT]]`
- **内容摘要**: 建议在此页面中梳理和记录 Transformer 与 BERT 的核心区别。内容可包括：1. 架构差异（Transformer 包含完整的 Encoder 和 Decoder，而 BERT 仅使用了 Transformer 的 Encoder 部分）；2. 核心机制差异（Transformer 侧重于 Seq2Seq 的自回归生成，BERT 侧重于双向掩码语言模型）；3. 预训练任务差异（BERT 使用了掩码语言模型 MLM 和下一句预测 NSP）；4. 适用场景（Transformer 常用于机器翻译等生成任务，BERT 常用于文本分类、命名实体识别等 NLU 理解任务）。

---

## [2026-05-04] Transformer和BERT有什么区别？

**回答**: 
Transformer 和 BERT 的主要区别在于它们的定位与使用的架构模块不同：
1. **整体与局部的关系**：Transformer 是一种基础的深度学习架构，由 Vaswani 等人在 2017 年提出；而 BERT 是由 Google 在 2018 年提出的一个具体的预训练语言模型，它的核心架构正是基于 Transformer 构建的。
2. **架构模块的选择**：Transformer 包含编码器和解码器两部分。BERT 仅仅使用了 Transformer 的**编码器**部分来进行模型构建。
3. **训练任务的不同**：Transformer 是一种基础架构，而 BERT 在此基础上定义了特定的预训练任务，即通过“掩码语言模型”和“下一句预测”这两个任务来学习双向的语义表示和句子级别的连贯性。

**引用**:
- [[transformer]] — 引用了 Transformer 的提出时间、基础架构定义，以及 BERT 使用了其编码器部分并采用掩码语言模型和下一句预测任务的信息。
- [[bert]] — 引用了 BERT 的提出时间、基于 Transformer 架构构建，以及仅使用 Transformer 编码器部分和特定预训练任务的详细说明。
- raw/test-transformer.txt — 引用了上述关于 Transformer 架构和 BERT 模型特性的原始记录材料。

**建议新页面**: 
建议创建新页面：【Transformer-vs-BERT】
**内容摘要**：总结和对比基础架构 Transformer 与预训练模型 BERT 之间的核心区别，包括架构层面（完整架构 vs 仅使用编码器）和应用/训练层面（基础架构 vs 包含特定预训练任务如掩码语言模型和下一句预测的下游模型）的详细对比。

---

## [2026-05-08] how to build a auto llm agent pipeline to get shits done

好的，我已经收集了足够的信息。现在让我综合回答这个问题。

---

**回答**：

构建一个自动化 LLM Agent Pipeline（让代理"搞定事情"），需要从 **架构设计哲学、核心组件、工程实践** 三个层面来规划。以下是根据知识库总结的完整方法论：

---

## 一、核心架构：三组件解耦（大脑-双手-会话）

根据 [[harness-engineering]] 和 [[managed-agents]]，一个健壮的 Agent Pipeline 应由三个虚拟化的核心组件构成：

| 组件 | 角色 | 类比 |
|------|------|------|
| **Harness（控制循环/大脑）** | 调用 LLM、路由工具调用、驱动决策循环 | 大脑 |
| **Sandbox（沙盒/双手）** | 执行代码、编辑文件、运行工具 | 双手 |
| **Session Log（会话日志）** | 仅追加的事件日志，记录所有状态 | 记忆/黑盒记录仪 |

**关键设计原则**：这三个组件必须解耦，各自独立部署、独立失败、独立替换。这是从 **"宠物 vs. 牲畜"（Pets vs. Cattle）** 架构模式中总结出来的经验。如果所有组件捆绑在一起，一旦容器宕机就会丢失所有状态；而解耦后，沙盒死了可以自动重开一个，Harness 崩溃可以通过 Session Log 恢复执行。[[pets-vs-cattle]]

---

## 二、Agent Pipeline 的具体步骤

### Step 1：定义核心 Agent Loop（Harness）

这是 Pipeline 的心脏。根据 [[harness-engineering]]，Codex Harness 中的核心 Agent Loop 包含：

1. **接收用户意图**（通过自然语言提示描述任务）
2. **推理与规划**（LLM 解析任务，决定执行步骤）
3. **工具调用与执行**（在沙盒中运行代码、编辑文件、调用 API）
4. **观察与反馈**（收集执行结果，决定是否需要迭代）
5. **循环直到完成**（自我审查、修正、最终输出）

### Step 2：构建自审查循环（Ralph Wiggum Loop）

为了让 Agent 真正"搞定事情"而不需要人类反复介入，需要建立 **代理间的自动审查循环**。[[ralph-wiggum-loop]] 描述的流程是：

- **本地审查** → Agent 审查自己的输出
- **云端审查** → Agent 请求其他代理实例做代码/结果审查
- **迭代循环** → 响应反馈，修改，重新提交，直到所有审查条件满足
- **最终合并/交付** → 自动完成

这种策略让团队实现了 **每位工程师每天 3.5 个 PR、5 个月 1500 个 PR** 的高吞吐量。

### Step 3：设置 AGENTS.md 知识引导文件

在项目的根目录放置一个 `AGENTS.md` 文件，作为代理的"入口指南"。[[agents-dot-md]] 建议它包含：
- 项目结构概览
- 技术栈和工具链
- 编码规范和格式化规则
- 工作流程和审查要求
- 指向 `docs/` 详细文档的链接

这让 Agent 一进来就知道"这个项目怎么玩"，而不是瞎猜。

### Step 4：构建反馈循环（可观测性）

代理需要能自我验证。[[harness-engineering]] 指出，关键实践包括：

- **应用可独立启动**：每个 git worktree 可独立启动一个应用实例
- **UI 可访问**：集成 Chrome DevTools Protocol，代理可捕获 DOM 快照、截图
- **本地可观测性栈**：每次任务都附带临时日志（LogQL）、指标（PromQL）和追踪
- **代理可查询**：Prompt 可以写"确保启动时间 < 800ms"或"关键路径耗时 < 2s"

### Step 5：处理上下文焦虑与状态管理

长时间运行的任务中，LLM 可能因为上下文窗口即将耗尽而提前结束任务（Context Anxiety）。[[context-anxiety]] 描述了这种现象和解决方案：
- 实现 **上下文重置（Context Reset）** 机制，清除历史记录以释放空间
- 使用 **Session Log** 作为持久化状态，即使 Harness 重启也能从最后一个事件恢复 [[session-log]]
- **重要提示**：不要将模型特定的限制假设硬编码到 Harness 中，因为模型能力会快速演进（如 Claude Opus 4.5 已不再需要 Context Reset）

---

## 三、完整的 Pipeline 流程示意

```
用户输入意图（Prompt）
       ↓
[AGENTS.md 知识引导] → Harness（大脑）理解上下文
       ↓
Harness 调用 LLM 进行推理/规划
       ↓
Harness 路由工具调用到 Sandbox（双手）
       ↓
Sandbox 执行 → 结果返回 Harness
       ↓
Harness 将事件写入 Session Log（持久化）
       ↓
Harness 判断任务是否完成？
   ├── 否 → 继续循环（可能触发 Ralph Wiggum Loop 自审查）
   └── 是 → 输出最终结果
       ↓
可观测性反馈（LogQL/PromQL 查询）→ 代理自我修正
```

---

## 四、哲学原则

构建这个 Pipeline 的核心哲学，来自 [[agent-first-world]]：

> **"人类指引，代理执行"（Humans steer. Agents execute.）**

工程师不再写代码，而是：
1. **设计系统与工具** — 为代理创造合适的工作环境
2. **分解任务** — 将大目标拆解为 Agent 可执行的构建块
3. **构建反馈循环** — 设计可观测性系统，让代理自我验证
4. **识别缺失能力** — 当代理失败时，问"缺少什么能力？如何让它对代理既清晰又可执行？"而不是"再试一次"

正如 [[harness-engineering]] 所说：**当 Agent 失败时，修复方案几乎从来不是"更努力地尝试"，而是"什么能力缺失了，怎么让它对代理可见且可强制执行？"**

---

## 五、实际效果参考

根据 [[harness-engineering]] 中 OpenAI 实验的数据：
- **团队规模**：3-7 名工程师
- **产出**：5 个月内合并约 1,500 个 PR，约 100 万行代码
- **速度**：平均每位工程师每天 3.5 个 PR
- **效率提升**：估计是传统手动编码的 **10 倍**
- **约束**：0 行手动编写的代码

---

**引用**：
- [[harness-engineering]] — 核心架构：Harness（大脑）、Sandbox（双手）、Session Log（会话）三组件解耦；Agent Loop 逻辑层；Codex App Server 通信协议；Ralph Wiggum Loop 自审查循环；可观测性反馈设计；实际效果数据
- [[agent-first-world]] — "人类指引，代理执行"哲学；工程师角色转变；环境影响设计
- [[managed-agents]] — 大脑与双手解耦架构；Session、Harness、Sandbox 三组件虚拟化
- [[pets-vs-cattle]] — 宠物 vs. 牲畜架构模式；容器解耦；故障恢复机制
- [[agents-dot-md]] — AGENTS.md 知识引导文件设计；代理工作引导策略
- [[ralph-wiggum-loop]] — 本地+云端自审查循环；代理间迭代流程
- [[session-log]] — 仅追加事件日志；故障恢复机制；状态持久化
- [[context-anxiety]] — 上下文焦虑现象；上下文重置策略；模型假设过时风险
- raw/Harness engineering leveraging Codex in an agent-first world.md — Harness Engineering 方法论原始资料
- raw/Scaling Managed Agents Decoupling the brain from the hands.md — Managed Agents 解耦架构原始资料
- raw/Unlocking the Codex harness how we built the App Server.md — Codex App Server 原始资料

---

**建议新页面**：建议创建一个名为 **"auto-llm-agent-pipeline"** 的新页面，将上述回答内容整理为结构化的中文指南，包含架构图、步骤清单和最佳实践，方便后续查阅和迭代。

---

## [2026-05-08] how to build a auto llm agent pipeline to get shits done

基于以上 wiki 信息，我来综合回答如何构建一个自动化的 LLM agent pipeline 来完成任务。

**回答**:

构建一个自动化 LLM agent pipeline 需要采用 **harness engineering** 方法论，其核心理念是"人类指引，代理执行"（Humans steer. Agents execute）。以下是基于 OpenAI Codex 和 Anthropic Managed Agents 实践经验的完整指南：

## 一、核心架构设计

### 1. 三层解耦架构（"大脑-双手-会话"）

借鉴 [[managed-agents]] 的设计，将 agent pipeline 分离为三个独立组件：

- **Session（会话）**：持久化的仅追加事件日志，记录所有交互历史
  - 特点：append-only、persistent、indivisible state
  - 作用：作为单一真实数据源，支持崩溃恢复和状态重建
  - 实现参考：[[session-log]]

- **Harness（大脑）**：控制循环和路由逻辑
  - 职责：调用 LLM、路由工具调用、管理代理循环
  - 独立性：运行在沙盒之外，可独立崩溃和重启
  - 恢复机制：通过 `wake(sessionId)` + `getSession(id)` 恢复执行

- **Sandbox（双手）**：代码执行环境
  - 特点：临时资源，可按需创建和销毁
  - 交互接口：`execute(name, input) → string`
  - 失败处理：视为"牲畜"而非"宠物"，失败即替换
  - 安全隔离：参考 [[sandbox-isolation]]

### 2. 通信层

采用 [[json-rpc-protocol]] 实现客户端与 harness 之间的双向通信：

- 支持流式进度更新
- 工具执行事件流
- 服务器发起的请求（如审批对话框）
- 向后兼容的协议演进

## 二、核心组件实现

### 1. Agent Loop（代理循环）

根据 [[harness-engineering]]，核心代理循环包含四个部分：

1. **Core Agent Loop**：编排用户、模型和工具之间的交互
2. **Thread Lifecycle & Persistence**：管理会话的创建、恢复、分支和归档
3. **Configuration & Authentication**：配置加载、认证流程管理
4. **Tool Execution & Extensions**：沙盒化工具执行、MCP 服务器集成

### 2. 工具生态系统

- **标准开发工具**：gh、本地脚本、仓库内嵌技能
- **MCP 服务器集成**：扩展能力，如数据库访问、API 调用
- **自定义技能**：项目特定的自动化任务
- **UI 交互工具**：集成 Chrome DevTools Protocol，支持 DOM 快照、截图、导航

### 3. 反馈循环设计

关键设计原则（[[harness-engineering]]）：

- **应用可读性**：让 UI、日志、指标对代理直接可读
- **可观测性**：通过 LogQL 查询日志、PromQL 查询指标
- **精确验证**：例如"启动时间 < 800ms"、"关键路径耗时 < 2s"
- **环境隔离**：每个 git worktree 独立启动应用实例

## 三、工作流程设计

### 1. 任务执行流程（基于 [[codex-cli]]）

1. **任务描述**：工程师通过自然语言提示描述任务
2. **上下文获取**：代理使用标准工具自动获取上下文（无需人工复制粘贴）
3. **代码生成**：生成代码、测试、CI 配置、文档
4. **自审查循环**：执行 [[ralph-wiggum-loop]]：
   - 本地审查：代理自审代码质量和逻辑
   - 云端审查：请求其他代理审查（结构、测试、文档）
   - 迭代改进：响应反馈并修改
   - 自动合并：满足所有条件后自动合并 PR
5. **人类监督**：可选的最终审查（大多数审查由代理完成）

### 2. Agent-to-Agent 审查（Ralph Wiggum Loop）

核心机制（[[ralph-wiggum-loop]]）：

- 完全自动化的代码审查生命周期
- 无需人类介入的迭代循环
- 基于明确审查标准的自动化验证
- 高吞吐量交付（3.5 PR/工程师/天）

## 四、关键最佳实践

### 1. 环境规范化（[[ralph-wiggum-loop]]）

- 应用按 git worktree 启动，每个变更独立运行
- 集成 Chrome DevTools Protocol 用于 UI 自动化
- 提供临时可观测性栈（日志、指标、追踪）

### 2. 假设最小化（[[harness-engineering]]）

- 避免编码模型特定的限制（如 [[context-anxiety]]）
- 模型能力快速演进，架构应支持底层实现替换
- 定期质疑和移除过时的假设

### 3. 容量扩展原则（[[pets-vs-cattle]]）

- **避免"宠物"**：不要将组件视为不可丢失的独立实例
- **采用"牲畜"**：将沙盒和 harness 视为可替换资源
- **状态外部化**：会话日志存储在外部，支持组件自由替换

### 4. 引导策略（[[agents-dot-md]]）

创建 `AGENTS.md` 作为代理知识目录：

- 项目结构概述
- 技术栈和工具链
- 编码规范
- 工作流程
- 指向详细文档的链接

## 五、实施步骤

### 阶段 1：基础架构搭建

1. 设计三层解耦架构（Session/Harness/Sandbox）
2. 实现 JSON-RPC 通信协议
3. 创建持久化会话日志系统
4. 搭建沙盒执行环境

### 阶段 2：工具和环境集成

1. 集成标准开发工具（gh、git 等）
2. 实现 MCP 服务器连接
3. 配置可观测性栈（日志、指标、追踪）
4. 创建项目特定的 AGENTS.md

### 阶段 3：反馈循环优化

1. 实现 Ralph Wiggum 自动审查循环
2. 集成 Chrome DevTools Protocol 用于 UI 测试
3. 配置 LogQL/PromQL 查询能力
4. 建立环境隔离机制（worktree）

### 阶段 4：迭代和扩展

1. 监控代理性能和瓶颈
2. 识别缺失能力并添加
3. 优化提示词和审查标准
4. 扩展到更多任务类型

## 六、关键指标

基于 [[harness-engineering]] 的实践成果：

- **吞吐量**：1500 PR/5个月（3-7人团队）
- **速度**：3.5 PR/工程师/天
- **效率提升**：约 10x 时间节省
- **代码规模**：100万行代码，零手动编写

## 七、常见挑战和解决方案

### 1. Context Anxiety（[[context-anxiety]]）

- **问题**：模型接近上下文限制时过早结束任务
- **解决方案**：在 harness 中实现 context reset（但要注意：模型升级后可能不再需要）

### 2. "宠物"问题（[[pets-vs-cattle]]）

- **问题**：组件耦合导致难以替换和恢复
- **解决方案**：解耦大脑和双手，状态外部化，组件可替换

### 3. 代理能力不足

- **问题**：代理无法完成某些任务
- **解决方案**：不要"再试一次"，而是问"缺少什么能力？如何让它对代理可读且可执行？"

---

**引用**:
- [[harness-engineering]] — 核心方法论、Codex harness 架构、关键原则和实施方法
- [[managed-agents]] — 三层解耦架构设计（Session/Harness/Sandbox）
- [[agent-first-world]] — 代理优先的软件开发范式和核心理念
- [[agents-dot-md]] — AGENTS.md 代理工作引导策略
- [[codex-cli]] — codex-cli 工作流程和工程师角色转变
- [[ralph-wiggum-loop]] — 自动化代码审查循环机制
- [[session-log]] — 会话日志的持久化和恢复机制
- [[sandbox-isolation]] — 沙盒隔离的安全设计模式
- [[json-rpc-protocol]] — JSON-RPC 双向通信协议
- [[pets-vs-cattle]] — "牲畜"vs"宠物"的基础设施管理哲学
- [[context-anxiety]] — 上下文焦虑现象及应对策略

- raw/Harness engineering leveraging Codex in an agent-first world.md — Harness engineering 核心实践和实验结果
- raw/Scaling Managed Agents Decoupling the brain from the hands.md — Managed Agents 架构设计
- raw/Unlocking the Codex harness how we built the App Server.md — Codex App Server 实现细节

**建议新页面**:

建议创建页面 **[[llm-agent-pipeline-guide]]**，内容摘要：
- 完整的 LLM agent pipeline 构建指南
- 从架构设计到实施步骤的系统化方法
- 包含代码示例、配置模板和最佳实践清单
- 常见问题和故障排除指南
- 不同规模团队的实施路径建议

---
