# Query-Generated Page Suggestion (2026-05-08)

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

## Action Required
- Review the suggested new page above
- If valuable, create the wiki page using `wiki convert` or manually
