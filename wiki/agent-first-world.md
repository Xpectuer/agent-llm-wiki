# agent-first-world

> Source(s): raw/Harness engineering leveraging Codex in an agent-first world.md

**agent-first-world** 是一种以 AI 代理为执行主体的软件开发范式。在这种范式下，人类角色从直接编码者转变为设计者、监督者和系统构建者，而 AI 代理负责编写所有代码、测试、配置、文档和工具。

## 核心理念

agent-first-world 的核心原则是“人类指引，代理执行”（Humans steer. Agents execute.）。人类不再手动编写代码，而是专注于构建环境、明确意图、设计反馈循环，使 AI 代理能够高效、可靠地完成工程任务。

## 实践案例

在实践中，一个团队在 5 个月内用 **0 行手动编写的代码** 交付了一款内部 beta 软件产品。该产品包含约 100 万行代码，由三名工程师驱动 Codex 代理完成，平均每位工程师每天处理 3.5 个 PR。产品拥有内部日活用户和外部 alpha 测试者，能够正常发布、部署、出现故障并修复。

## 工程角色转变

在 agent-first-world 中，工程师的主要职责不再是写代码，而是：

- **设计系统与工具**：为代理创建合适的工作环境和抽象层
- **分解任务**：将高层次目标拆解为可被代理理解和执行的构建块
- **构建反馈循环**：设计可观测性系统（日志、指标、追踪），使代理能够自我验证和修复
- **治理与监督**：定义工作规范、质量标准，并在必要时介入

## 环境与工具要求

为了最大化代理效率，环境需要具备：

- **可观察性**：日志、指标和追踪对代理可见且可查询（如通过 LogQL、PromQL）
- **可测试性**：应用能够按 git 工作树独立启动，代理可驱动实例进行缺陷复现和验证
- **工具集成**：代理能直接使用标准开发工具（如 `gh`、本地脚本、仓库内嵌技能）
- **自动审查**：代理之间（agent-to-agent）完成大部分代码审查，人工审查作为可选环节

## 哲学约束

在 agent-first-world 中，团队通常会设定 **禁止手动编写代码** 的核心纪律。当代理失败时，常见对策不是“再试一次”，而是反问：“缺少了什么能力？如何让这个需求对代理更清晰、更可执行？”

## 参考

- [OpenAI 博客文章：Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/)
- [Ralph Wiggum Loop](https://ghuntley.com/loop/)

## See also
- [[codex-cli]]
- [[harness-engineering]]
- [[ralph-wiggum-loop]]
(none)